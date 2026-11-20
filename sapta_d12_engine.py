#!/usr/bin/env python3
"""
SAPTA Design 12 — engine additions (sapta_d12_SPEC.md):

  * Daily-12 THE OCCUPANCY BASKET (SPEC s.2): no signal at all —
    enter each selected name on its first selected own-series day
    of each calendar month at the open (skipped while held), exit
    at the close of series day e+20 (last close if past the end).
    Plus its placebo: the standing daily recipe with the variant's
    own exit (the fixed horizon), drawn from the name's selected
    own-series days in the same quarter-window.
  * Intraday-12 GAP-FADE (SPEC s.3): TARANG's T25-C book imported
    frozen (tarang25_SPEC.md sS.2-S.4) into SAPTA's rotating
    construction — candidates only on the name's selected days,
    chronology key = the quarter's selection order (Amendment A4
    order), placebo name pool = the day's selected names.

The selection layer, the daily prep and the gate are Designs 1-11's
(sapta_owner_engine / sapta_d2_engine / sapta_d3_run), reused.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E
import tarang_score as T
import tarang20_score as T20
import tarang23_score as T23
import tarang24_score as T24
import tarang25_score as T25

COST = 40.0
QTY = 100
HORIZON = 20


def _dates_of(d):
    return [str(x)[:10] for x in d['dates']]


# ------------------------------------------------------------ daily-12
def basket_trades(d, active_dates):
    """SPEC s.2: the occupancy basket on one name's prepared daily
    series. active_dates: the name's selected calendar days (set of
    'YYYY-MM-DD'). Returns gate-shaped trade rows."""
    dates = _dates_of(d)
    o, c, n = d['o'], d['c'], d['n']
    trades = []
    seen_months = set()
    held_until = -1
    for i, dt in enumerate(dates):
        if dt not in active_dates:
            continue
        m = dt[:7]
        if m in seen_months:
            continue
        seen_months.add(m)          # first selected series day of month
        if i <= held_until:         # still held -> no entry this month
            continue
        if i == n - 1:              # cannot enter on the last series day
            continue
        xi = min(i + HORIZON, n - 1)
        ep, xp = float(o[i]), float(c[xi])
        kind = 'HORIZON20' if xi == i + HORIZON else 'FORCED'
        trades.append({
            'sym': d['sym'], 'date': dt, 'side': 'LONG',
            'entry_stamp': dt, 'exit_stamp': dates[xi],
            'entry_date': dt, 'exit_date': dates[xi],
            'entry_price': round(ep, 4), 'exit_price': round(xp, 4),
            'exit_reason': 'horizon20' if kind == 'HORIZON20' else 'forced',
            'exit_kind': kind, 'hold': xi - i,
            'net': round((xp - ep) * QTY - COST, 2)})
        held_until = xi
    return trades


def placebo_basket(d, active_dates, real_trades, quarter_of, seed,
                   draws=200):
    """SPEC s.2 placebo: per real trade, an entry day drawn uniformly
    from the name's selected own-series days in the same
    quarter-window (series' last day excluded); LONG; the basket's
    own exit (close at min(idx+20, n-1)). Returns (draws x 2) nets
    by the REAL trade's entry year."""
    dates = _dates_of(d)
    o, c, n = d['o'], d['c'], d['n']
    rng = np.random.default_rng(seed)
    out = np.zeros((draws, 2))
    cache = {}

    def single_net(i):
        if i not in cache:
            xi = min(i + HORIZON, n - 1)
            cache[i] = round((float(c[xi]) - float(o[i])) * QTY - COST, 2)
        return cache[i]

    spaces = {}
    items = []
    for t in real_trades:
        qi = quarter_of(t['date'])
        if qi not in spaces:
            spaces[qi] = [i for i, dt in enumerate(dates)
                          if dt in active_dates
                          and quarter_of(dt) == qi and i != n - 1]
        items.append((t, spaces[qi]))
    for dr in range(draws):
        for t, space in items:
            if not space:
                continue
            i = space[int(rng.integers(0, len(space)))]
            yr = 0 if t['date'] < '2026-01-01' else 1
            out[dr, yr] += single_net(i)
    return out


# ------------------------------------------------------------ intraday-12
def load_name_sapta(sym):
    """load_name6's post-processing, from the store found by
    sapta_owner_engine.find_5m_store (SPEC s.3e). None if no store."""
    p = E.find_5m_store(sym)
    if p is None:
        return None
    df = pd.read_csv(p)
    df['ts'] = df['timestamp'].astype(str).str.slice(0, 19)
    df['date'] = df['ts'].str.slice(0, 10)
    df['time'] = df['ts'].str.slice(11, 16)
    df = df.sort_values('ts').reset_index(drop=True)
    return df


def prep_sapta(names):
    """tarang23_score.prep's body, fed by load_name_sapta."""
    data = {}
    for sym in names:
        df = load_name_sapta(sym)
        if df is None:
            continue
        df['volume'] = df['volume'].fillna(0.0)
        o = df['open'].to_numpy(float)
        h = df['high'].to_numpy(float)
        l = df['low'].to_numpy(float)
        c = df['close'].to_numpy(float)
        v = df['volume'].to_numpy(float)
        time = df['time'].to_numpy()
        days = []
        for date, idx in df.groupby('date', sort=False).groups.items():
            ii = np.sort(np.asarray(idx))
            times = time[ii]
            sqc = np.where(times <= '15:15')[0]
            sq = int(sqc[-1]) if len(sqc) else len(ii) - 1
            days.append(dict(date=str(date), ii=ii, times=times, sq=sq))
        typ = (h + l + c) / 3.0
        vwap = np.full(len(df), np.nan)
        for d in days:
            ii = d['ii']
            cv = np.cumsum(v[ii])
            cpv = np.cumsum(typ[ii] * v[ii])
            with np.errstate(invalid='ignore', divide='ignore'):
                vwap[ii] = np.where(cv > 0, cpv / np.where(cv == 0, 1, cv),
                                    np.nan)
        data[sym] = dict(sym=sym, df=df, o=o, h=h, l=l, c=c, v=v,
                         time=time, days=days, vwap=vwap,
                         rsi2=T23.rsi2_engine(c))
    return data


def gen_candidates_sapta(data, active_map, order_maps):
    """SPEC s.3: T25-C candidates (GAP-FADE-UP-15 stream of
    tarang24_score.sig_gapw2, standalone trades by
    tarang23_score.take_trade) generated ONLY on the name's
    selected days. order_maps: {quarter_index: {sym: position}} —
    the chronology key (adaptation b)."""
    cands = []
    skipped_first_days = 0
    for sym in sorted(data):
        D = data[sym]
        active = active_map.get(sym, set())
        prev = None
        for day in D['days']:
            if prev is not None and day['date'] in active:
                ctx = T23.day_ctx(D, day, prev)
                sigs, _sk = T24.sig_gapw2(ctx)
                for (stream, sl, side, el) in sigs:
                    if stream != 'GAP-FADE-UP-15':
                        continue
                    tr = T23.take_trade(D, day, ctx, stream, sl, side, el)
                    if tr is None:
                        continue
                    tr = dict(tr)
                    gap = float(ctx['o'][0] / prev['last_close'] - 1.0)
                    tr['gap_pct'] = round(gap, 6)
                    tr['vol_ratio'] = round(
                        T25.vol_ratio_at(D, int(day['ii'][0])), 6)
                    tr['univ'] = order_maps[quarter_of(day['date'])][sym]
                    cands.append(tr)
            elif prev is None:
                skipped_first_days += 1
            if len(day['ii']):
                ii = day['ii']
                prev = dict(pdh=float(D['h'][ii].max()),
                            pdl=float(D['l'][ii].min()),
                            last_close=float(D['c'][ii[-1]]))
    return cands, skipped_first_days


def quarter_of(date):
    """Quarter index by the stored ranking dates (mirrors
    sapta_d8_run.quarter_of; imported lazily to avoid a cycle)."""
    import sapta_d3_run as D3R
    for qi, q in enumerate(D3R.QUARTERS):
        if q['ranking_date'] <= date < D3R.Q_ENDS[qi]:
            return qi
    return None


def dayinfo_sapta(data):
    """placebo25's _dayinfo over an arbitrary prepared name set."""
    info = {}
    for sym, D in data.items():
        for day in D['days']:
            ii = day['ii']
            times = day['times']
            elig = [k for k in range(len(ii))
                    if T.PLACEBO_LO <= times[k] <= T.PLACEBO_HI]
            info[(sym, day['date'])] = (
                D['o'][ii], D['h'][ii], D['l'][ii], D['c'][ii],
                ii, day['sq'], elig)
    return info


def placebo_gap(info, taken, pool_by_date, seed0, draws=200):
    """SPEC s.3c: tarang25_score.placebo25's construction with the
    name pool = the day's selected names (pool_by_date). Returns
    (draws x 2) net array by the date's year."""
    per_day_count = {}
    for tr in taken:
        per_day_count[tr['date']] = per_day_count.get(tr['date'], 0) + 1
    out = np.zeros((draws, 2))
    for d in range(draws):
        rng = np.random.default_rng(seed0 + d)
        totals = {2025: 0.0, 2026: 0.0}
        for date, want in per_day_count.items():
            year = int(date[:4])
            pool = pool_by_date.get(date, [])
            if not pool:
                continue
            placed, attempts = 0, 0
            busy, nameday = {}, {}
            while placed < want and attempts < 60 * want + 60:
                attempts += 1
                sym = pool[int(rng.integers(0, len(pool)))]
                got = info.get((sym, date))
                if got is None:
                    continue
                o, h, l, c, ii, sq, elig = got
                if not elig:
                    continue
                e_local = elig[int(rng.integers(0, len(elig)))]
                e_glob = int(ii[e_local])
                if busy.get(sym, -1) >= e_glob:
                    continue
                if nameday.get(sym, 0) >= 1:
                    continue
                side = 1 if rng.random() < 0.5 else -1
                px = float(o[e_local])
                xj, xpx, _ = T20.exit20_audit(o, h, l, c, e_local,
                                              sq, side, px)
                totals[year] += side * (xpx - px) * QTY - COST
                busy[sym] = int(ii[xj])
                nameday[sym] = 1
                placed += 1
        out[d, 0] = round(totals[2025], 2)
        out[d, 1] = round(totals[2026], 2)
    return out


def gate_row_from_tarang(tr):
    """SAPTA gate-shaped row from a TARANG-shaped taken trade."""
    return {
        'sym': tr['sym'], 'date': tr['date'], 'side': tr['side'],
        'entry_stamp': f"{tr['date']} {tr['entry_time']}",
        'exit_stamp': f"{tr['date']} {tr['exit_time']}",
        'entry_price': tr['entry_price'], 'exit_price': tr['exit_price'],
        'exit_reason': tr['exit_reason'], 'net': tr['net_inr'],
        'gap_pct': tr['gap_pct'], 'vol_ratio': tr['vol_ratio']}
