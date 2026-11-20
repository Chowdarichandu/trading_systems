#!/usr/bin/env python3
"""
SAPTA Design 13 — engine additions (sapta_d13_SPEC.md):

  * Daily-13 BASKET x NATIVE (SPEC s.2): Design 12's no-signal
    monthly entry schedule, exits by the base machine's native
    governed exit set (TIME 60 -> CAP +10% -> BAND, in
    sim2c_gated's own check order, evaluated from the entry day).
    Plus its placebo: the standing daily recipe with the
    variant's own (native) exits.
  * Intraday-13 GAP-FADE + TRAIL (SPEC s.3): Design 12's
    candidates and allocation unchanged; each taken trade
    re-exited by TARANG Design 26's TRAIL exit
    (tarang26_score.exit26_trail_engine, with the audit-form
    exit run alongside on every trade as a parity check).
    Plus its placebo: D12's construction with the TRAIL exit.

The selection layer, the daily prep and the gate are Designs
1-12's (sapta_owner_engine / sapta_d2_engine / sapta_d3_run /
sapta_d12_engine), reused.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_d12_engine as D12
import tarang_score as T
import tarang26_score as T26

COST = 40.0
QTY = 100
TIME_DAYS = 60
CAP_MULT = 1.10


def _dates_of(d):
    return [str(x)[:10] for x in d['dates']]


# ------------------------------------------------------------ daily-13
def native_exit(d, e):
    """SPEC s.2 exit simulator: the governed exit set of
    sim2c_gated (TIME -> CAP -> BAND, its own check order),
    evaluated from the entry day e itself. Entry fill E = o[e].
    Returns (exit_index, exit_price, exit_kind)."""
    o, h, c, mid, n = d['o'], d['h'], d['c'], d['mid'], d['n']
    E = float(o[e])
    lvl = E * CAP_MULT
    for i in range(e, n):
        if i - e >= TIME_DAYS and i > e:
            return i, float(o[i]), 'TIME'
        if h[i] >= lvl:
            return i, (float(o[i]) if o[i] >= lvl else lvl), 'CAP'
        if not np.isnan(mid[i]) and c[i] >= mid[i]:
            if i + 1 < n:
                return i + 1, float(o[i + 1]), 'SIGNAL-BB'
            return i, float(c[i]), 'FORCED'
    return n - 1, float(c[n - 1]), 'FORCED'


_KIND2REASON = {'TIME': 'time', 'CAP': 'cap', 'SIGNAL-BB': 'signal',
                'FORCED': 'forced'}


def basket_native_trades(d, active_dates):
    """SPEC s.2: Design 12's entry schedule (first selected
    own-series day of each calendar month, at the open, skipped
    while held) with held measured by THIS design's exit index;
    exits by native_exit."""
    dates = _dates_of(d)
    o, n = d['o'], d['n']
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
        xi, xp, kind = native_exit(d, i)
        ep = float(o[i])
        trades.append({
            'sym': d['sym'], 'date': dt, 'side': 'LONG',
            'entry_stamp': dt, 'exit_stamp': dates[xi],
            'entry_date': dt, 'exit_date': dates[xi],
            'entry_price': round(ep, 4), 'exit_price': round(xp, 4),
            'exit_reason': _KIND2REASON[kind], 'exit_kind': kind,
            'hold': xi - i,
            'net': round((xp - ep) * QTY - COST, 2)})
        held_until = xi
    return trades


def placebo_basket_native(d, active_dates, real_trades, quarter_of,
                          seed, draws=200):
    """SPEC s.2 placebo: per real trade, an entry day drawn
    uniformly from the name's selected own-series days in the
    same quarter-window (series' last day excluded); LONG; exit
    by the variant's own rules (native_exit). Returns (draws x 2)
    nets by the REAL trade's entry year."""
    dates = _dates_of(d)
    o, n = d['o'], d['n']
    rng = np.random.default_rng(seed)
    out = np.zeros((draws, 2))
    cache = {}

    def single_net(i):
        if i not in cache:
            _xi, xp, _k = native_exit(d, i)
            cache[i] = round((xp - float(o[i])) * QTY - COST, 2)
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


# ------------------------------------------------------------ intraday-13
def day_maps_sapta(data):
    """(sym, date) -> (day_index, day) over a prep_sapta dataset,
    plus prev-close lookup (previous store day's last close)."""
    by_key = {}
    for sym, D in data.items():
        for di, day in enumerate(D['days']):
            by_key[(sym, day['date'])] = (di, day)
    return by_key


def prev_close_sapta(data, by_key, sym, date):
    di, _day = by_key[(sym, date)]
    if di == 0:
        return None
    pii = data[sym]['days'][di - 1]['ii']
    return float(data[sym]['c'][pii[-1]])


def retrail_taken(data, by_key, taken):
    """SPEC s.3: re-exit Design 12's taken trades (tarang-shaped)
    under the TRAIL exit. The engine form computes the exit; the
    audit form re-derives it on every trade (parity counters).
    Returns (new_trades, counters)."""
    eng, aud_fn = T26.EXIT26['trail']
    v = {'exit_parity_mismatch': 0, 'entry_mismatch': 0,
         'half_level_mismatch': 0, 'net_mismatch': 0}
    out = []
    for tr in taken:
        di, day = by_key[(tr['sym'], tr['date'])]
        ii = day['ii']
        D = data[tr['sym']]
        o, h, l, c = D['o'][ii], D['h'][ii], D['l'][ii], D['c'][ii]
        pc = prev_close_sapta(data, by_key, tr['sym'], tr['date'])
        px = float(tr['entry_price'])
        if pc is None or abs(px - float(o[0])) > 1e-9:
            v['entry_mismatch'] += 1
            continue
        tgt = (px + pc) / 2.0
        tgt2 = (float(o[0]) + pc) / 2.0
        if abs(tgt - tgt2) > 1e-12:
            v['half_level_mismatch'] += 1
        e = int(tr['entry_local'])
        side = int(tr['side'])
        xj, xpx, reason = eng(o, h, l, c, e, day['sq'], side, px, tgt)
        aj, apx, areason = aud_fn(o, h, l, c, e, day['sq'], side,
                                  px, tgt)
        if aj != xj or abs(apx - xpx) > 1e-9 or areason != reason:
            v['exit_parity_mismatch'] += 1
        gross = (xpx - px) * side * QTY
        nt = dict(tr)
        nt['exit_time'] = str(day['times'][xj])
        nt['exit_price'] = float(xpx)
        nt['exit_reason'] = reason
        nt['exit_local'] = int(xj)
        nt['gross_inr'] = round(gross, 2)
        nt['net_inr'] = round(gross - COST, 2)
        if abs(nt['net_inr'] - (gross - COST)) > 0.011:
            v['net_mismatch'] += 1
        out.append(nt)
    v['total_violations'] = int(sum(v.values()))
    return out, v


def dayinfo_sapta_trail(data, by_key):
    """D12's dayinfo extended with prev_close (SPEC s.3 placebo):
    (sym, date) -> (o, h, l, c, ii, sq, elig, pc) day-sliced."""
    info = {}
    for sym, D in data.items():
        for di, day in enumerate(D['days']):
            ii = day['ii']
            times = day['times']
            elig = [k for k in range(len(ii))
                    if T.PLACEBO_LO <= times[k] <= T.PLACEBO_HI]
            pc = None
            if di > 0:
                pii = D['days'][di - 1]['ii']
                pc = float(D['c'][pii[-1]])
            info[(sym, day['date'])] = (
                D['o'][ii], D['h'][ii], D['l'][ii], D['c'][ii],
                ii, day['sq'], elig, pc)
    return info


def placebo_gap_trail(info, taken, pool_by_date, seed0, draws=200):
    """SPEC s.3: D12's placebo_gap construction with the book's
    own exit replaced by TRAIL (audit form; half level per the
    family convention; a drawn name-day with no previous day is
    skipped). Returns (draws x 2) net array by the date's year."""
    _eng, aud_fn = T26.EXIT26['trail']
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
                o, h, l, c, ii, sq, elig, pc = got
                if not elig or pc is None:
                    continue
                e_local = elig[int(rng.integers(0, len(elig)))]
                e_glob = int(ii[e_local])
                if busy.get(sym, -1) >= e_glob:
                    continue
                if nameday.get(sym, 0) >= 1:
                    continue
                side = 1 if rng.random() < 0.5 else -1
                px = float(o[e_local])
                tgt = px + side * 0.5 * abs(px - pc)
                xj, xpx, _ = aud_fn(o, h, l, c, e_local, sq, side,
                                    px, tgt)
                totals[year] += side * (xpx - px) * QTY - COST
                busy[sym] = int(ii[xj])
                nameday[sym] = 1
                placed += 1
        out[d, 0] = round(totals[2025], 2)
        out[d, 1] = round(totals[2026], 2)
    return out
