#!/usr/bin/env python3
"""
SAPTA Design 5 — engine additions (sapta_d5_SPEC.md):
  * index PROXY series rebuilt exactly as the selection layer built
    them (sapta_owner_select.py construction: RELIANCE calendar,
    equal-weighted mean of constituents' daily close-to-close returns,
    NaN returns -> 0, cumprod from 1.0) — verified by control C-6;
  * proxy 200DMA gate codes per calendar position;
  * per-name Daily-5 gate codes: for signal day i, the gate of the
    A4 owning entity (owner of the name in the quarter containing the
    ENTRY day dates[i+1]) read on its proxy at the signal DATE;
  * the FROZEN intraday universe (each year's Q1 selection held all
    year) and frozen ownership.
The daily machine and placebo are Design 4's (sapta_d4_engine),
reused verbatim — only the gate-code arrays differ. The intraday
books reuse sapta_d3_engine verbatim (EKAM shell).
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade. Paper only.
"""
import csv, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E

BASE = E.BASE
DATA = os.path.join(BASE, 'universe_daily')
CONS = os.path.join(BASE, 'sapta_constituents')

INDICES = {
    'Nifty Bank': 'ind_niftybanklist', 'Nifty IT': 'ind_niftyitlist',
    'Nifty Pharma': 'ind_niftypharmalist', 'Nifty Auto': 'ind_niftyautolist',
    'Nifty Metal': 'ind_niftymetallist', 'Nifty FMCG': 'ind_niftyfmcglist',
    'Nifty Realty': 'ind_niftyrealtylist', 'Nifty Energy': 'ind_niftyenergylist',
    'Nifty PSU Bank': 'ind_niftypsubanklist',
    'Nifty Financial Services': 'ind_niftyfinancelist',
    'Nifty Consumer Durables': 'ind_niftyconsumerdurableslist',
    'Nifty Oil & Gas': 'ind_niftyoilgaslist',
    'Nifty Healthcare': 'ind_niftyhealthcarelist',
    'Nifty Media': 'ind_niftymedialist',
    'Nifty Infrastructure': 'ind_niftyinfralist',
}

def _read_list(fname):
    with open(os.path.join(CONS, fname + '.csv')) as fh:
        return [row['Symbol'].strip() for row in csv.DictReader(fh)]

CONSTITUENTS = {k: _read_list(v) for k, v in INDICES.items()}

# ---------------------------------------------------------------- calendar
_cal_df = pd.read_parquet(os.path.join(DATA, 'RELIANCE.parquet')).sort_values('date')
CAL_TS = pd.to_datetime(_cal_df['date']).tolist()
CAL = [d.strftime('%Y-%m-%d') for d in CAL_TS]
CAL_POS = {d: i for i, d in enumerate(CAL)}
NCAL = len(CAL)

def build_proxy_levels():
    """Owner-spec s.1.2 PROXY levels per index, construction identical
    to sapta_owner_select.py. Returns {index: np.array len NCAL}."""
    close = {}
    all_syms = sorted({s for v in CONSTITUENTS.values() for s in v})
    for s in all_syms:
        p = os.path.join(DATA, s + '.parquet')
        if not os.path.exists(p):
            continue
        df = pd.read_parquet(p).sort_values('date').drop_duplicates('date')
        dts = pd.to_datetime(df['date'])
        idx = np.array([CAL_POS.get(x.strftime('%Y-%m-%d'), -1) for x in dts])
        ok = idx >= 0
        c = np.full(NCAL, np.nan)
        c[idx[ok]] = df['close'].to_numpy(float)[ok]
        close[s] = c
    rets = {}
    for s, c in close.items():
        r = np.full(NCAL, np.nan)
        prev, cur = c[:-1], c[1:]
        m = ~np.isnan(prev) & ~np.isnan(cur) & (prev > 0)
        r[1:][m] = cur[m] / prev[m] - 1.0
        rets[s] = r
    levels = {}
    for idx_name, syms in CONSTITUENTS.items():
        avail = [s for s in syms if s in rets]
        M = np.vstack([rets[s] for s in avail]) if avail else np.empty((0, NCAL))
        with np.errstate(invalid='ignore'):
            mean_r = np.nanmean(M, axis=0) if M.shape[0] else np.full(NCAL, np.nan)
        mean_r = np.where(np.isnan(mean_r), 0.0, mean_r)
        levels[idx_name] = np.cumprod(1.0 + mean_r)
    return levels

PROXY_LEVEL = build_proxy_levels()

def proxy_gate_code(level):
    """Per-calendar-position gate code for one proxy series (SPEC s.4):
    -1 = short history (fewer than 200 proxy values up to and including
    the position), 0 = level <= its 200DMA, 1 = level > its 200DMA.
    MA200P[p] = mean(level[p-199 .. p]), causal."""
    n = len(level)
    code = np.zeros(n, dtype=np.int8)
    if n == 0:
        return code
    cs = np.concatenate([[0.0], np.cumsum(level)])
    for p in range(n):
        if p < 199:
            code[p] = -1
        else:
            ma = (cs[p + 1] - cs[p - 199]) / 200.0
            code[p] = 1 if level[p] > ma else 0
    return code

PROXY_CODE = {k: proxy_gate_code(v) for k, v in PROXY_LEVEL.items()}

def proxy_trailing_ret(level, end_pos, win=126):
    """Selection-layer replica (control C-6): trailing `win`-trading-day
    return of a level series through calendar position end_pos."""
    if end_pos - win < 0:
        return None
    return float(level[end_pos] / level[end_pos - win] - 1.0)

def last_pos_before(R_str):
    """Calendar position of the last trading day strictly before R_str
    ('YYYY-MM-DD'), as in sapta_owner_select.last_pos_before."""
    arr = np.array(CAL_TS, dtype='datetime64[ns]')
    return int(np.searchsorted(arr, np.datetime64(R_str), side='left') - 1)

# ---------------------------------------------------------------- ownership
def owner_in_quarter(pick_of, quarters, sym, qi):
    """A4 owner: highest-ranked entity (earliest in the quarter's top-7
    order) that picked sym in quarter qi; None if unpicked."""
    for ent in quarters[qi]['top7']:
        if sym in pick_of.get((ent, qi), []):
            return ent
    return None

def build_name_gate_code(d, sym, pick_of, quarters, q_ends):
    """Daily-5 per-name gate code array over the name's own daily series
    (SPEC s.4): code[i] is consulted at signal day i only when the entry
    day dates[i+1] is active; it is the proxy gate code of the owning
    entity (owner in the quarter containing the ENTRY day) at the
    calendar position of the SIGNAL date dates[i]. Days with no owner
    or no calendar position get 0 (veto) — unreachable when the entry
    day is active, by construction of the active map."""
    dates = d['dates']
    n = len(dates)
    code = np.zeros(n, dtype=np.int8)
    for i in range(n - 1):
        entry_date = dates[i + 1]
        qi = None
        for k, q in enumerate(quarters):
            if q['ranking_date'] <= entry_date < q_ends[k]:
                qi = k
                break
        if qi is None:
            continue
        owner = owner_in_quarter(pick_of, quarters, sym, qi)
        if owner is None:
            continue
        p = CAL_POS.get(dates[i])
        if p is None:
            continue
        code[i] = PROXY_CODE[owner][p]
    return code

# ---------------------------------------------------------------- frozen maps
Q1_OF_YEAR = {2025: 0, 2026: 4}

def build_frozen_maps(quarters, q_ends, pick_of, dates_between):
    """SPEC s.2: frozen active map + frozen (ent, sym) pick sets.
    A name picked in year Y's Q1 is active on every trading day of Y
    in the entries window (2025: [2025-01-01, 2026-01-01);
    2026: [2026-01-01, 2026-11-14))."""
    frozen_picks = {}
    for yr, qi in Q1_OF_YEAR.items():
        lo = f'{yr}-01-01'
        hi = '2026-01-01' if yr == 2025 else '2026-11-14'
        days = dates_between(lo, hi)
        for ent in quarters[qi]['top7']:
            for s in pick_of.get((ent, qi), []):
                frozen_picks.setdefault((ent, s), set()).update(days)
    frozen_union = {}
    for (ent, s), dset in frozen_picks.items():
        frozen_union.setdefault(s, set()).update(dset)
    return frozen_picks, frozen_union

def frozen_owner_of(pick_of, quarters, sym, date):
    """SPEC s.3 frozen ownership: the owner from the year's Q1
    selection (quarter 0 for 2025 dates, quarter 4 for 2026 dates)."""
    qi = Q1_OF_YEAR[2025] if date < '2026-01-01' else Q1_OF_YEAR[2026]
    return owner_in_quarter(pick_of, quarters, sym, qi)
