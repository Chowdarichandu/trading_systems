#!/usr/bin/env python3
"""
SAPTA Design 16 — engine additions (sapta_d16_SPEC.md):

  * Union candidate generation (SPEC s.2): Design 12/15's
    candidate machinery (day context, take_trade with the
    frozen exit20, gap/vol_ratio keys, the chronology key from
    the quarterly A4 order maps) with the kept stream replaced
    by the UNION of the two frozen streams GAP-FADE-UP-15 and
    GAP-FADE-20, resolved per the SPEC's frozen rule: one
    candidate per qualifying name-day — SHORT for gap >= +1.5%
    (UP-15; the >= +2.0% overlap where FADE-20 co-fires
    prescribes the same SHORT), LONG for gap <= -2.0%
    (FADE-20 only). Each candidate records which stream(s)
    fired in 'union_src' ('UP15' / 'FADE20' / 'BOTH').

The allocation (tarang25_score.allocate25), the TRAIL re-exit,
the TRAIL placebo and the gate are Designs 12/13's
(sapta_d12_engine / sapta_d13_engine / sapta_owner_engine),
reused.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_d12_engine as D12
import tarang23_score as T23
import tarang24_score as T24
import tarang25_score as T25

COST = 40.0
QTY = 100

UP15 = 'GAP-FADE-UP-15'
FADE20 = 'GAP-FADE-20'


def gen_candidates_sapta_union(data, active_map, order_maps):
    """SPEC s.2 union candidates. Candidates are generated ONLY
    on the name's active days; the chronology key is
    order_maps[quarter_of(date)][sym] (the rotating quarterly A4
    order, as Designs 12-15). Returns (cands, skipped_first_days,
    side_conflicts) — side_conflicts counts name-days where the
    two streams fired with different sides (must be 0 by the
    frozen construction; counted, not assumed)."""
    cands = []
    skipped_first_days = 0
    side_conflicts = 0
    for sym in sorted(data):
        D = data[sym]
        active = active_map.get(sym, set())
        prev = None
        for day in D['days']:
            if prev is not None and day['date'] in active:
                ctx = T23.day_ctx(D, day, prev)
                sigs, _sk = T24.sig_gapw2(ctx)
                by_stream = {s[0]: s for s in sigs}
                fire = [k for k in (UP15, FADE20) if k in by_stream]
                if fire:
                    sides = {by_stream[k][2] for k in fire}
                    if len(sides) > 1:
                        side_conflicts += 1
                    else:
                        sname, sl, side, el = by_stream[fire[0]]
                        tr = T23.take_trade(D, day, ctx, 'GAP-FADE-UNION',
                                            sl, side, el)
                        if tr is not None:
                            tr = dict(tr)
                            gap = float(ctx['o'][0] / prev['last_close']
                                        - 1.0)
                            tr['gap_pct'] = round(gap, 6)
                            tr['vol_ratio'] = round(
                                T25.vol_ratio_at(D, int(day['ii'][0])), 6)
                            tr['univ'] = order_maps[
                                D12.quarter_of(day['date'])][sym]
                            tr['union_src'] = ('BOTH' if len(fire) == 2
                                               else 'UP15' if fire[0] == UP15
                                               else 'FADE20')
                            cands.append(tr)
            elif prev is None:
                skipped_first_days += 1
            if len(day['ii']):
                ii = day['ii']
                prev = dict(pdh=float(D['h'][ii].max()),
                            pdl=float(D['l'][ii].min()),
                            last_close=float(D['c'][ii[-1]]))
    return cands, skipped_first_days, side_conflicts
