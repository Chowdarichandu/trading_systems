#!/usr/bin/env python3
"""
SAPTA Design 14 — engine additions (sapta_d14_SPEC.md):

  * Daily-14 (SPEC s.3): Design 13's basket x native frame with
    the entry schedule moved inside the window —
      MID  : first selected own-series day of the month with
             day-of-month >= 15;
      DOWN : first selected own-series day of the month whose
             close < open; if none, the month's last selected
             own-series day.
    Exits are Design 13's frozen native-exit simulator
    (sapta_d13_engine.native_exit), reused verbatim. The placebo
    is Design 13's (sapta_d13_engine.placebo_basket_native) —
    the standing daily recipe with the variant's own exits.
  * Intraday-14 (SPEC s.2) needs no new engine code: Design 12's
    candidate generation and Design 13's TRAIL re-exit run on
    Design 5's frozen maps (sapta_d5_engine.build_frozen_maps).

Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_d13_engine as D13

COST = 40.0
QTY = 100

_KIND2REASON = D13._KIND2REASON


def _month_candidates(d, active_dates, rule):
    """SPEC s.3: per (name, calendar month), the single candidate
    series index under `rule` ('MID' or 'DOWN'), chosen from the
    name's selected own-series days in that month. Returns a list
    of series indices in chronological order."""
    dates = D13._dates_of(d)
    o, c = d['o'], d['c']
    by_month = {}
    for i, dt in enumerate(dates):
        if dt in active_dates:
            by_month.setdefault(dt[:7], []).append(i)
    out = []
    for m in sorted(by_month):
        idxs = by_month[m]
        if rule == 'MID':
            cand = None
            for i in idxs:
                if int(dates[i][8:10]) >= 15:
                    cand = i
                    break
            if cand is not None:
                out.append(cand)
        elif rule == 'DOWN':
            cand = None
            for i in idxs:
                if float(c[i]) < float(o[i]):
                    cand = i
                    break
            if cand is None:
                cand = idxs[-1]
            out.append(cand)
        else:
            raise ValueError(f'unknown rule {rule}')
    return out


def basket_timed_trades(d, active_dates, rule):
    """SPEC s.3: enter each month's candidate at its open unless
    the name already holds a position under this book's own
    exits (skipped, not deferred; the month is consumed); the
    last series day cannot be an entry. Exits by D13.native_exit."""
    dates = D13._dates_of(d)
    o, n = d['o'], d['n']
    trades = []
    held_until = -1
    for i in _month_candidates(d, active_dates, rule):
        if i <= held_until:         # still held -> skip this month
            continue
        if i == n - 1:              # cannot enter on the last series day
            continue
        xi, xp, kind = D13.native_exit(d, i)
        ep = float(o[i])
        trades.append({
            'sym': d['sym'], 'date': dates[i], 'side': 'LONG',
            'entry_stamp': dates[i], 'exit_stamp': dates[xi],
            'entry_date': dates[i], 'exit_date': dates[xi],
            'entry_price': round(ep, 4), 'exit_price': round(xp, 4),
            'exit_reason': _KIND2REASON[kind], 'exit_kind': kind,
            'hold': xi - i,
            'net': round((xp - ep) * QTY - COST, 2)})
        held_until = xi
    return trades
