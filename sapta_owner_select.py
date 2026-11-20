#!/usr/bin/env python3
"""
SAPTA (owner spec) — universe construction. Frozen spec: sapta_owner_SPEC.md.
Quarterly causal ranking: index PROXY (equal-weighted constituent daily returns)
trailing 126d -> TOP 7 indices; per index, top-3 stocks by trailing 126d return
with membership / liquidity / Rs 2,000 / history constraints.
All ranking inputs use data strictly before the ranking date R.
Output: sapta_owner_selections.json
Basis: equity cash, PROVISIONAL per 100 shares. Paper only.
"""
import csv, json, os
import numpy as np
import pandas as pd

BASE = os.path.expanduser('~/workspace/trading')
DATA = os.path.join(BASE, 'universe_daily')
CONS = os.path.join(BASE, 'sapta_constituents')
RET_WIN = 126
LIQ_WIN = 60
LIQ_MIN = 5e7            # Rs 5 crore
CAP_PRICE = 2000.0

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
MEMBER_FILES = ['ind_nifty100list', 'ind_niftymidcap150list']  # Amendment A2: Nifty 50 is a subset of Nifty 100

def read_list(fname):
    syms = []
    with open(os.path.join(CONS, fname + '.csv')) as fh:
        for row in csv.DictReader(fh):
            syms.append(row['Symbol'].strip())
    return syms

constituents = {k: read_list(v) for k, v in INDICES.items()}
members = set()
for f in MEMBER_FILES:
    members |= set(read_list(f))

FNO = set(json.load(open(os.path.join(CONS, 'nse_fno_symbols.json')))['symbols'])
ALL = sorted({s for v in constituents.values() for s in v})
print(f'candidate indices: {len(INDICES)}, union constituents: {len(ALL)}, member-universe: {len(members)}')

# ---- load daily closes/volumes into a wide frame on the RELIANCE calendar ----
cal_df = pd.read_parquet(os.path.join(DATA, 'RELIANCE.parquet')).sort_values('date')
CAL = pd.to_datetime(cal_df['date']).tolist()
cal_pos = {d: i for i, d in enumerate(CAL)}
NCAL = len(CAL)

close = {}   # sym -> np array len NCAL (nan where no bar)
vol = {}
missing_files = []
for s in ALL:
    p = os.path.join(DATA, s + '.parquet')
    if not os.path.exists(p):
        missing_files.append(s)
        continue
    df = pd.read_parquet(p).sort_values('date').drop_duplicates('date')
    d = pd.to_datetime(df['date'])
    idx = np.array([cal_pos.get(x, -1) for x in d])
    ok = idx >= 0
    c = np.full(NCAL, np.nan); v = np.full(NCAL, np.nan)
    c[idx[ok]] = df['close'].to_numpy(float)[ok]
    v[idx[ok]] = df['volume'].to_numpy(float)[ok]
    close[s] = c; vol[s] = v
print(f'loaded {len(close)} names; missing parquet: {missing_files}')

# per-name daily returns (only where both consecutive calendar closes exist)
rets = {}
for s, c in close.items():
    r = np.full(NCAL, np.nan)
    prev = c[:-1]; cur = c[1:]
    m = ~np.isnan(prev) & ~np.isnan(cur) & (prev > 0)
    r[1:][m] = cur[m] / prev[m] - 1.0
    rets[s] = r

# ---- index proxy levels: equal-weight mean of constituent daily returns ----
proxy_level = {}
for idx_name, syms in constituents.items():
    avail = [s for s in syms if s in rets]
    M = np.vstack([rets[s] for s in avail]) if avail else np.empty((0, NCAL))
    with np.errstate(invalid='ignore'):
        mean_r = np.nanmean(M, axis=0) if M.shape[0] else np.full(NCAL, np.nan)
    mean_r = np.where(np.isnan(mean_r), 0.0, mean_r)
    lvl = np.cumprod(1.0 + mean_r)
    proxy_level[idx_name] = lvl

def last_pos_before(R):
    """position in CAL of the last trading day strictly before R."""
    i = np.searchsorted(np.array(CAL, dtype='datetime64[ns]'), np.datetime64(R), side='left') - 1
    return int(i)

def trailing_ret(level, end_pos, win=RET_WIN):
    if end_pos - win < 0:
        return None
    return level[end_pos] / level[end_pos - win] - 1.0

def stock_trailing(s, end_pos, win=RET_WIN):
    c = close[s]
    # use the stock's own bars: positions <= end_pos with non-nan close
    pos = np.where(~np.isnan(c[:end_pos + 1]))[0]
    if len(pos) < win + 1:
        return None, None, 0
    p_end = pos[-1]; p_start = pos[-1 - win]
    return c[p_end] / c[p_start] - 1.0, c[p_end], len(pos)

def liquidity(s, end_pos, win=LIQ_WIN):
    c = close[s][:end_pos + 1]; v = vol[s][:end_pos + 1]
    tv = c * v
    tv = tv[~np.isnan(tv)]
    if len(tv) < win // 2:
        return None
    return float(np.median(tv[-win:]))

quarters = []
for y in (2025, 2026):
    for m in (1, 4, 7, 10):
        R = pd.Timestamp(y, m, 1)
        # first trading day >= R
        i = np.searchsorted(np.array(CAL, dtype='datetime64[ns]'), np.datetime64(R), side='left')
        quarters.append(CAL[int(i)])

out = {'spec': 'sapta_owner_SPEC.md', 'ranking_rule': 'inputs strictly before R',
       'member_source': MEMBER_FILES, 'fno_source': 'nse_fo_mktlots_2026-11-17.csv (Amendment A2)', 'quarters': []}
for R in quarters:
    ep = last_pos_before(R)
    idx_ret = {}
    for idx_name in INDICES:
        r = trailing_ret(proxy_level[idx_name], ep)
        if r is not None:
            idx_ret[idx_name] = r
    ranked = sorted(idx_ret.items(), key=lambda kv: -kv[1])
    top7 = [k for k, _ in ranked[:7]]
    q = {'ranking_date': str(R.date()), 'data_through': str(CAL[ep].date()),
         'index_returns_126d': {k: round(v, 6) for k, v in ranked},
         'top7': top7, 'entities': {}}
    for idx_name in top7:
        rows = []
        for s in constituents[idx_name]:
            if s not in close:
                rows.append({'sym': s, 'status': 'no_parquet'})
                continue
            r, px_last, nbars = stock_trailing(s, ep)
            if r is None:
                rows.append({'sym': s, 'status': 'insufficient_history', 'bars': int(nbars)})
                continue
            liq = liquidity(s, ep)
            rows.append({'sym': s, 'ret126': r, 'last_close': px_last, 'liq_med60': liq,
                         'member': s in members, 'fno': s in FNO, 'bars': int(nbars), 'status': 'ok'})
        ok_rows = [x for x in rows if x['status'] == 'ok']
        ok_rows.sort(key=lambda x: -x['ret126'])
        picks, excluded = [], []
        for x in ok_rows:
            why = []
            if not x['member']:
                why.append('not_in_nifty100_midcap150')
            if not x['fno']:
                why.append('not_in_fno')
            if x['liq_med60'] is None or x['liq_med60'] < LIQ_MIN:
                why.append('liquidity_below_5cr')
            if x['last_close'] > CAP_PRICE:
                why.append('price_above_2000')
            if not why and len(picks) < 3:
                picks.append(x['sym'])
            elif why:
                excluded.append({'sym': x['sym'], 'ret126': round(x['ret126'], 6),
                                 'last_close': x['last_close'], 'why': why,
                                 'would_rank': len(picks) + len([e for e in excluded]) + 1})
        # full ranked eligible list (for replacements): constraint-passing, in rank order
        eligible = [x['sym'] for x in ok_rows
                    if x['member'] and x['fno'] and x['liq_med60'] is not None and x['liq_med60'] >= LIQ_MIN
                    and x['last_close'] <= CAP_PRICE]
        q['entities'][idx_name] = {
            'picks': picks, 'eligible_ranked': eligible,
            'excluded': excluded,
            'no_data': [x['sym'] for x in rows if x['status'] != 'ok'],
            'pick_stats': {x['sym']: {'ret126': round(x['ret126'], 6),
                                      'last_close': x['last_close'],
                                      'liq_med60': x['liq_med60']} for x in ok_rows if x['sym'] in picks},
        }
    out['quarters'].append(q)
    print(R.date(), 'top7:', top7)
    for idx_name in top7:
        print('   ', idx_name, '->', q['entities'][idx_name]['picks'])

with open(os.path.join(BASE, 'sapta_owner_selections.json'), 'w') as fh:
    json.dump(out, fh, indent=1)
print('wrote sapta_owner_selections.json')
