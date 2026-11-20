#!/usr/bin/env python3
"""
SAPTA Design 9 — engine additions (sapta_d9_SPEC.md):
  * the FROZEN pool map: Design 5's freeze construction applied to
    Design 8's pool-restricted picks (sapta_d8_engine.pool_picks) —
    each year's Q1 selection (Q0 for 2025, Q4 for 2026) held all year;
  * frozen ownership under the pool picks (Design 5's owner_in_quarter
    with the year's Q1 quarter);
  * the Daily-9 HOME active map: every frozen-25 name active on every
    one of its own series days inside the entries window.
The intraday shell, the daily stepper and both placebos are Designs
3/5/8's, reused verbatim (sapta_d3_engine, sapta_d8_engine).
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade. Paper only.
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E
import sapta_d5_engine as D5
import sapta_d8_engine as D8

BASE = E.BASE
FROZEN25 = D8.FROZEN25
Q1_OF_YEAR = D5.Q1_OF_YEAR          # {2025: 0, 2026: 4}
WIN_LO, WIN_HI = '2025-01-01', '2026-11-14'

def build_frozen_pool_maps(quarters, pick_of8, dates_between):
    """SPEC s.4: frozen (ent, sym) pick sets + union active map from
    the D8 pool picks at each year's Q1 quarter. A name picked in year
    Y's Q1 selection is active on every trading day of Y in the
    entries window (2025: [2025-01-01, 2026-01-01); 2026:
    [2026-01-01, 2026-11-14))."""
    frozen_picks = {}
    for yr, qi in Q1_OF_YEAR.items():
        lo = f'{yr}-01-01'
        hi = '2026-01-01' if yr == 2025 else '2026-11-14'
        days = dates_between(lo, hi)
        for ent in quarters[qi]['top7']:
            for s in pick_of8.get((ent, qi), []):
                frozen_picks.setdefault((ent, s), set()).update(days)
    frozen_union = {}
    for (ent, s), dset in frozen_picks.items():
        frozen_union.setdefault(s, set()).update(dset)
    return frozen_picks, frozen_union

def frozen_pool_owner_of(pick_of8, quarters, sym, date):
    """SPEC s.4 frozen ownership under the POOL picks: the owner from
    the year's Q1 selection (quarter 0 for 2025 dates, quarter 4 for
    2026 dates), highest-ranked entity first (D5.owner_in_quarter)."""
    qi = Q1_OF_YEAR[2025] if date < '2026-01-01' else Q1_OF_YEAR[2026]
    return D5.owner_in_quarter(pick_of8, quarters, sym, qi)

def build_home_active(PD):
    """SPEC s.3: the Daily-9 active map — for each frozen-25 name,
    every date of its own daily series inside the entries window
    [2025-01-01, 2026-11-13]."""
    out = {}
    for s in FROZEN25:
        if s not in PD:
            continue
        out[s] = {d for d in PD[s]['dates'] if WIN_LO <= d < WIN_HI}
    return out
