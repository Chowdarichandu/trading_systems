#!/usr/bin/env python3
"""
SAPTA Design 20 — engine additions (sapta_d20_SPEC.md):

  * allocate20 (SPEC s.2.2): the two gated streams' candidate
    pools — Design 16's intraday union (INTRA) and Design 19's
    GF-FILL3 (FILL3) — merged and allocated chronologically
    under ONE shared rule: one position per name across both
    streams (carried positions and same-day takes both block),
    a shared cap of 10 open positions at each day's allocation
    instant (carried + taken today), and the Designs 12-19
    ranking key (-|gap_pct|, -vol_ratio, univ ASC) with the
    pre-registered final tie-break INTRA before FILL3.
  * placebo_d20 (SPEC s.4): the programme's book placebo
    extended across the two streams — per-date taken counts
    split by stream, INTRA placements exited by the TRAIL
    audit form (Design 13's recipe), FILL3 placements by
    Design 19's generalised multi-day scan, both sharing one
    open-position state under the s.2.2 rule.

The candidate generators, the TRAIL re-exit, the selection
layer and the gate are Designs 12-19's (sapta_d16_engine /
sapta_d19_engine / sapta_d13_engine / sapta_owner_engine),
reused frozen.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_d19_engine as D19
import tarang26_score as T26

COST = 40.0
QTY = 100
DAY_CAP = 10
STREAM_RANK = {'INTRA': 0, 'FILL3': 1}


# ------------------------------------------------------------ allocation
def merge_pools(intra_cands, fill3_cands):
    """Tag both frozen pools with xstream; INTRA candidates get
    exit_date = entry date (same-day TRAIL exit by
    construction). Returns the merged candidate list."""
    merged = []
    for c in intra_cands:
        c = dict(c)
        c['xstream'] = 'INTRA'
        c['exit_date'] = c['date']
        merged.append(c)
    for c in fill3_cands:
        c = dict(c)
        c['xstream'] = 'FILL3'
        merged.append(c)
    return merged


def allocate20(merged):
    """SPEC s.2.2 shared allocation. Returns (taken, stats).
    Taken INTRA candidates still carry their frozen exit20
    exits — the caller re-exits them with TRAIL (Design 16's
    order: allocation first, retrail after)."""
    by_day = defaultdict(list)
    for c in merged:
        by_day[c['date']].append(c)
    taken = []
    open_pos = []          # taken positions from earlier days
    stats = {'skip_name_busy': 0, 'skip_cap_full': 0,
             'skip_name_busy_INTRA': 0, 'skip_name_busy_FILL3': 0,
             'skip_cap_full_INTRA': 0, 'skip_cap_full_FILL3': 0,
             'cap_bound_days': 0, 'days_with_candidates': 0,
             'max_concurrent_open': 0, 'entries_per_day_max': 0,
             'dual_fire_name_days': 0, 'dual_taken_INTRA': 0,
             'dual_taken_FILL3': 0, 'dual_taken_none': 0,
             'candidates_INTRA': 0, 'candidates_FILL3': 0,
             'taken_INTRA': 0, 'taken_FILL3': 0}
    for c in merged:
        stats[f"candidates_{c['xstream']}"] += 1
    for date in sorted(by_day):
        cs = by_day[date]
        stats['days_with_candidates'] += 1
        dual = ({c['sym'] for c in cs if c['xstream'] == 'INTRA'}
                & {c['sym'] for c in cs if c['xstream'] == 'FILL3'})
        stats['dual_fire_name_days'] += len(dual)
        carried = [p for p in open_pos if p['exit_date'] >= date]
        busy = {p['sym'] for p in carried}
        ranked = sorted(
            cs, key=lambda c: (-abs(c['gap_pct']), -c['vol_ratio'],
                               c['univ'], STREAM_RANK[c['xstream']]))
        taken_today = 0
        cap_skip_today = False
        taken_syms_today = {}
        for c in ranked:
            if c['sym'] in busy:
                stats['skip_name_busy'] += 1
                stats[f"skip_name_busy_{c['xstream']}"] += 1
                continue
            if len(carried) + taken_today >= DAY_CAP:
                stats['skip_cap_full'] += 1
                stats[f"skip_cap_full_{c['xstream']}"] += 1
                cap_skip_today = True
                continue
            taken.append(c)
            open_pos.append(c)
            busy.add(c['sym'])
            taken_today += 1
            taken_syms_today[c['sym']] = c['xstream']
            stats[f"taken_{c['xstream']}"] += 1
            stats['max_concurrent_open'] = max(
                stats['max_concurrent_open'],
                len(carried) + taken_today)
        for s in dual:
            w = taken_syms_today.get(s)
            if w == 'INTRA':
                stats['dual_taken_INTRA'] += 1
            elif w == 'FILL3':
                stats['dual_taken_FILL3'] += 1
            else:
                stats['dual_taken_none'] += 1
        stats['entries_per_day_max'] = max(
            stats['entries_per_day_max'], taken_today)
        if cap_skip_today:
            stats['cap_bound_days'] += 1
    taken.sort(key=lambda c: (c['date'], c['univ'],
                              STREAM_RANK[c['xstream']]))
    return taken, stats


# ------------------------------------------------------------ placebo
def placebo_d20(trail_info, info19, day_list19, taken, pool_by_date,
                seed0, draws=200):
    """SPEC s.4 combined placebo. `taken` rows need 'date' and
    'xstream'. trail_info: sapta_d13_engine.dayinfo_sapta_trail
    output; info19/day_list19: sapta_d19_engine.dayinfo_d19
    output. Returns (draws x 2) net array by entry year."""
    _eng, aud_fn = T26.EXIT26['trail']
    counts = {}
    for tr in taken:
        counts.setdefault(tr['date'], {'INTRA': 0, 'FILL3': 0})
        counts[tr['date']][tr['xstream']] += 1
    out = np.zeros((draws, 2))
    for d in range(draws):
        rng = np.random.default_rng(seed0 + d)
        totals = {2025: 0.0, 2026: 0.0}
        open_pos = []      # (sym, exit_date) of this draw
        for date in sorted(counts):
            year = int(date[:4])
            pool = pool_by_date.get(date, [])
            if not pool:
                continue
            open_now = [p for p in open_pos if p[1] >= date]
            open_names = {p[0] for p in open_now}
            placed_names = set()
            placed_today = 0
            for stream in ('INTRA', 'FILL3'):
                want = counts[date][stream]
                placed, attempts = 0, 0
                while placed < want and attempts < 60 * want + 60:
                    attempts += 1
                    if len(open_now) + placed_today >= DAY_CAP:
                        break
                    sym = pool[int(rng.integers(0, len(pool)))]
                    if sym in placed_names or sym in open_names:
                        continue
                    if stream == 'INTRA':
                        got = trail_info.get((sym, date))
                        if got is None:
                            continue
                        o, h, l, c, ii, sq, elig, pc = got
                        if not elig or pc is None:
                            continue
                        e_local = elig[int(rng.integers(0, len(elig)))]
                        side = 1 if rng.random() < 0.5 else -1
                        px = float(o[e_local])
                        tgt = px + side * 0.5 * abs(px - pc)
                        xj, xpx, _r = aud_fn(o, h, l, c, e_local, sq,
                                             side, px, tgt)
                        totals[year] += side * (xpx - px) * QTY - COST
                        open_pos.append((sym, date))
                    else:
                        got = info19.get((sym, date))
                        if got is None:
                            continue
                        di, o, h, l, c, elig, pc = got
                        if not elig or pc is None:
                            continue
                        e_local = elig[int(rng.integers(0, len(elig)))]
                        side = 1 if rng.random() < 0.5 else -1
                        px = float(o[e_local])
                        hlev = (px + pc) / 2.0
                        res = D19._scan_placebo(day_list19[sym], di,
                                                e_local, side, px, 3,
                                                hlev)
                        if res is None:
                            continue
                        _xs, xpx, _r, xdt = res
                        totals[year] += side * (xpx - px) * QTY - COST
                        open_pos.append((sym, xdt))
                    placed_names.add(sym)
                    placed += 1
                    placed_today += 1
        out[d, 0] = round(totals[2025], 2)
        out[d, 1] = round(totals[2026], 2)
    return out
