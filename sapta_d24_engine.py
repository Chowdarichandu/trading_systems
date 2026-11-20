#!/usr/bin/env python3
"""
SAPTA Design 24 — engine (sapta_d24_SPEC.md s.2/s.4).

RS63: cross-sectional relative strength inside the rotating
SAPTA universe. Monthly rebalance (first trading day of the
month, RELIANCE calendar); rank the pool by trailing
63-trading-day return on the name's own daily closes
(closes strictly before the rebalance date); hold the
entry band ranks 1-7, exit when rank decays past the hold
band 1-14, the name leaves the pool, or it goes
unrankable. LONG only, 100 shares, executions at the
rebalance date's daily close. NO intraday signal.

Daily data: universe_daily/<SYM>.parquet (full-NSE daily
dump, 2019-01-01 -> 2026-11-13).
Costs (SPEC s.2, per the design brief): Rs 40 on EVERY
entry AND every exit = Rs 80 per completed trade.
Basis: equity cash, PROVISIONAL per 100 shares.
Paper only, real money Rs 0.
"""
import bisect
import os
import numpy as np
import pandas as pd

BASE = os.path.expanduser('~/workspace/trading')
COST_SIDE = 40.0
COST_RT = 80.0
QTY = 100
LOOKBACK = 63
ENTRY_BAND = 7
HOLD_BAND = 14
MAX_HOLD = 7
WIN_START = '2025-01-01'
WIN_END = '2026-11-13'


# ------------------------------------------------------------ daily data
def load_daily(sym):
    """(dates list[str], closes np.array) from the parquet
    dump, or None if the name has no file."""
    p = os.path.join(BASE, 'universe_daily', f'{sym}.parquet')
    if not os.path.exists(p):
        return None
    df = pd.read_parquet(p)
    dates = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return (dates.tolist(), df['close'].to_numpy(float))


def calendar():
    """RELIANCE parquet dates inside the window (the
    trading calendar for rebalances and hold lengths)."""
    got = load_daily('RELIANCE')
    dates, _c = got
    return [d for d in dates if WIN_START <= d <= WIN_END]


def rebalance_dates(cal):
    """First trading day of each calendar month."""
    out = []
    seen = set()
    for d in cal:
        ym = d[:7]
        if ym not in seen:
            seen.add(ym)
            out.append(d)
    return out


class Series:
    """One name's daily closes with bisect helpers."""

    def __init__(self, dates, closes):
        self.dates = dates
        self.closes = closes

    def n_before(self, date):
        """Number of closes strictly before `date`."""
        return bisect.bisect_left(self.dates, date)

    def close_on(self, date):
        """Close exactly on `date`, or None."""
        i = bisect.bisect_left(self.dates, date)
        if i < len(self.dates) and self.dates[i] == date:
            return float(self.closes[i])
        return None

    def close_on_or_before(self, date):
        """(date_used, close) of the last close <= date."""
        i = bisect.bisect_right(self.dates, date) - 1
        if i < 0:
            return None, None
        return self.dates[i], float(self.closes[i])

    def trailing_ret(self, date):
        """SPEC s.2 rank key: c_m / c_{m-63} - 1 over the
        closes strictly before `date`; None if unrankable
        (fewer than 64 such closes)."""
        m = self.n_before(date)
        if m < LOOKBACK + 1:
            return None
        return float(self.closes[m - 1] / self.closes[m - 1 - LOOKBACK]
                     - 1.0)


def rank_pool(series, pool, date):
    """{sym: (rank, ret63)} for rankable pool names at
    `date`; ranks 1-based, descending ret, ties by sym ASC.
    Also returns the unrankable pool names."""
    rets = {}
    unrank = []
    for sym in pool:
        s = series.get(sym)
        if s is None:
            unrank.append(sym)
            continue
        r = s.trailing_ret(date)
        if r is None:
            unrank.append(sym)
        else:
            rets[sym] = r
    ordered = sorted(rets, key=lambda s: (-rets[s], s))
    ranks = {sym: (i + 1, rets[sym]) for i, sym in enumerate(ordered)}
    return ranks, unrank


# ------------------------------------------------------------ the book
def run_rs63(series, pool_of, rebalances, cal_index):
    """The frozen RS63 book. `pool_of(date) -> iterable of
    pool names on that date`. Returns (trades, counters).
    Trade dicts carry the owner-gate keys ('date', 'net',
    'entry_stamp', 'exit_stamp') plus reporting fields."""
    trades = []
    counters = {'rebalances': 0, 'entries': 0,
                'exit_rank_decay': 0, 'exit_universe_exit': 0,
                'exit_unrankable': 0, 'exit_window_end': 0,
                'entry_skip_no_close': 0,
                'exit_close_fallback': 0,
                'unrankable_pool_names': 0,
                'holdings_after_rebalance': []}
    holdings = {}   # sym -> position dict

    def close_position(sym, pos, exit_date, reason):
        s = series[sym]
        px = s.close_on(exit_date)
        used = exit_date
        if px is None:
            used, px = s.close_on_or_before(exit_date)
            counters['exit_close_fallback'] += 1
        gross = (px - pos['entry_price']) * QTY
        trades.append(dict(
            sym=sym, date=pos['entry_date'], year=int(pos['entry_date'][:4]),
            side=1, entry_date=pos['entry_date'],
            entry_stamp=f"{pos['entry_date']} 15:30",
            entry_price=round(pos['entry_price'], 2),
            entry_rank=pos['entry_rank'],
            entry_ret63=round(pos['entry_ret63'], 6),
            exit_date=exit_date, exit_date_used=used,
            exit_stamp=f"{exit_date} 15:30",
            exit_price=round(px, 2), exit_reason=reason,
            hold_trading_days=(cal_index.get(exit_date, 0)
                               - cal_index.get(pos['entry_date'], 0)),
            gross_inr=round(gross, 2),
            net_inr=round(gross - COST_RT, 2),
            net=round(gross - COST_RT, 2)))
        counters[f'exit_{reason}'] += 1

    for R in rebalances:
        counters['rebalances'] += 1
        pool = set(pool_of(R))
        ranks, unrank = rank_pool(series, pool, R)
        counters['unrankable_pool_names'] += len(unrank)
        # ---- exits first (SPEC s.2 procedure step 2)
        for sym in sorted(list(holdings)):
            if sym not in pool:
                close_position(sym, holdings.pop(sym), R,
                               'universe_exit')
            elif sym not in ranks:
                close_position(sym, holdings.pop(sym), R,
                               'unrankable')
            elif ranks[sym][0] > HOLD_BAND:
                close_position(sym, holdings.pop(sym), R,
                               'rank_decay')
        # ---- entries (step 3): entry band, rank order
        cands = sorted((rk, sym) for sym, (rk, _r) in ranks.items()
                       if rk <= ENTRY_BAND and sym not in holdings)
        for rk, sym in cands:
            if len(holdings) >= MAX_HOLD:
                break
            px = series[sym].close_on(R)
            if px is None:
                counters['entry_skip_no_close'] += 1
                continue
            holdings[sym] = {'entry_date': R, 'entry_price': px,
                             'entry_rank': rk,
                             'entry_ret63': ranks[sym][1]}
            counters['entries'] += 1
        counters['holdings_after_rebalance'].append(len(holdings))
    # ---- window end: force-close what is still open
    for sym in sorted(list(holdings)):
        close_position(sym, holdings.pop(sym), WIN_END, 'window_end')
    trades.sort(key=lambda t: (t['entry_date'], t['sym']))
    return trades, counters


# ------------------------------------------------------------ placebo
def placebo_rs63(trades, pool_by_date, series, draws=200):
    """SPEC s.4: random selection, the book's own holding
    schedule. pool_by_date: {entry_date: [pool names]}.
    Returns (draws x 2) net array by entry year + the
    skipped-placement count."""
    by_date = {}
    for t in trades:
        by_date.setdefault(t['entry_date'], []).append(t)
    ordered = []
    for date in sorted(by_date):
        ordered.extend(sorted(by_date[date], key=lambda t: t['sym']))
    out = np.zeros((draws, 2))
    skipped = 0
    for d in range(draws):
        rng = np.random.default_rng(24000 + d)
        open_pos = []   # (sym, entry_date, exit_date) of this draw
        for t in ordered:
            pool = [s for s in pool_by_date.get(t['entry_date'], [])
                    if s in series]
            placed = False
            for _att in range(200):
                if not pool:
                    break
                sym = pool[int(rng.integers(0, len(pool)))]
                overlap = any(
                    s2 == sym and e2 <= t['exit_date']
                    and x2 >= t['entry_date']
                    for (s2, e2, x2) in open_pos)
                if overlap:
                    continue
                s = series[sym]
                _du, epx = s.close_on_or_before(t['entry_date'])
                if epx is None:
                    continue
                _du2, xpx = s.close_on_or_before(t['exit_date'])
                if xpx is None:
                    continue
                yr = 0 if t['entry_date'] < '2026-01-01' else 1
                out[d, yr] += (xpx - epx) * QTY - COST_RT
                open_pos.append((sym, t['entry_date'], t['exit_date']))
                placed = True
                break
            if not placed:
                skipped += 1
    return out, skipped


# ------------------------------------------------------------ summaries
def month_table(trades):
    m = {}
    for t in trades:
        k = t['entry_date'][:7]
        m[k] = round(m.get(k, 0.0) + t['net_inr'], 2)
    return m


def slice_net(trades, lo, hi):
    sel = [t for t in trades if lo <= t['entry_date'] <= hi]
    return {'trades': len(sel),
            'net_inr': round(sum(t['net_inr'] for t in sel), 2)}


def summarise(trades):
    out = {}
    for yr in (2025, 2026):
        sel = [t for t in trades if t['year'] == yr]
        n = len(sel)
        gross = sum(t['gross_inr'] for t in sel)
        out[str(yr)] = dict(
            trades=n, gross_inr=round(gross, 2),
            net_inr=round(sum(t['net_inr'] for t in sel), 2),
            win_rate=(round(100.0 * sum(1 for t in sel
                                        if t['net_inr'] > 0) / n, 1)
                      if n else None),
            avg_hold_days=(round(float(np.mean(
                [t['hold_trading_days'] for t in sel])), 1) if n else None))
    out['month_table_entry_month'] = month_table(trades)
    out['november_2026'] = slice_net(trades, '2026-11-01', '2026-11-13')
    out['october_2025'] = slice_net(trades, '2025-10-01', '2025-10-31')
    out['october_2026'] = slice_net(trades, '2026-10-01', '2026-10-31')
    return out
