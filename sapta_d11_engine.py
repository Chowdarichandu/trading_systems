#!/usr/bin/env python3
"""
SAPTA Design 11 — engine additions (sapta_d11_SPEC.md):
  * horizon_trade: the fixed-horizon transform of one native base
    trade (SPEC s.2) — entry kept exactly (same day, same open);
    exit at the close of series day e+20 (entry day = day 0), or the
    last series close when e+20 runs past the series end (FORCED);
  * placebo_daily_horizon11: the standing daily placebo recipe with
    the variant's own exit rule — the fixed horizon (SPEC s.2).
The intraday shells, the gate and the base daily machine are Designs
3/8's and sapta_owner_engine's, reused verbatim.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade. Paper only.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E

COST = 40.0
HORIZON = 20


def horizon_trade(d, base_trade):
    """Fixed-horizon form of one native base trade (sim4c_gated dict
    shape). Returns (sim-shaped trade dict, entry_index, exit_index).
    Entry price is asserted against the prepared series open at the
    entry-date index by the caller (control C-17a)."""
    dates, o, c, n = d['dates'], d['o'], d['c'], d['n']
    pos = {dt: i for i, dt in enumerate(dates)}
    e = pos[base_trade['entry_date']]
    xi = min(e + HORIZON, n - 1)
    xp = float(c[xi])
    Ep = float(base_trade['entry'])
    kind = 'HORIZON20' if xi == e + HORIZON else 'FORCED'
    tr = dict(
        sym=d['sym'], comps=base_trade['comps'],
        signal_date=base_trade['signal_date'],
        entry_date=base_trade['entry_date'],
        exit_date=dates[xi], entry=Ep, exit=xp,
        net=round((xp - Ep) * 100.0 - COST, 2), hold=xi - e,
        exit_kind=kind, forced=(kind == 'FORCED'),
        upgraded=False, upgrade_date=None, upgrade_offset=None,
        counted_upgrade=False)
    return tr, e, xi


def placebo_daily_horizon11(d, real_trades, windows, draws=200,
                            seed=E.SEED, single_cache=None):
    """SPEC s.2 daily placebo = the standing recipe (Design 8 s.4
    construction) with the variant's own exit — the fixed horizon:
    per real trade, an entry day drawn uniformly from the name's
    selected days in the same quarter-window whose prior day carries
    a non-empty firing set (BB or RSI or MACD) and which is not the
    series' last day; the placebo net is that day's horizon net
    (close at min(idx+20, n-1) - open) x 100 - 40; an empty sample
    space contributes 0. Returns (draws x 2) nets by the REAL
    trade's entry year."""
    rng = np.random.default_rng(seed)
    out = np.zeros((draws, 2))
    pos = {dt: i for i, dt in enumerate(d['dates'])}
    last_date = d['dates'][-1]
    n = d['n']
    cache = single_cache if single_cache is not None else {}

    def single_net(D_):
        key = (d['sym'], 'H11', D_)
        if key not in cache:
            i = pos[D_]
            xi = min(i + HORIZON, n - 1)
            cache[key] = round((float(d['c'][xi]) - float(d['o'][i]))
                               * 100.0 - COST, 2)
        return cache[key]

    items = []
    for t in real_trades:
        days = windows.get(t['date'], [])
        space = []
        for D_ in days:
            pi = pos.get(D_)
            if pi is None or pi == 0 or D_ == last_date:
                continue
            if (d['sig_in']['BB'][pi - 1] or d['sig_in']['RSI'][pi - 1]
                    or d['sig_in']['MACD'][pi - 1]):
                space.append(D_)
        items.append((t, space))
    for dr in range(draws):
        for t, space in items:
            if not space:
                continue
            D_ = space[rng.integers(0, len(space))]
            yr = 0 if t['date'] < '2026-01-01' else 1
            out[dr, yr] += single_net(D_)
    return out
