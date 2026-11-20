#!/usr/bin/env python3
"""
SAPTA Design 17 — engine additions (sapta_d17_SPEC.md):

  * The FOCUS restriction (SPEC s.2): the focus sleeve set
    F = {Nifty Bank, Nifty Healthcare, Nifty Realty}; a
    name-day is focus-eligible iff the name is active that day
    under the rotating stored selections AND its Amendment-A4
    owning entity for that quarter (sapta_d8_run.owner_of, on
    the stored picks) is in F. build_focus_active() turns the
    rotating active map into the focus active map.
  * Candidate generation is Design 16's union generator
    (sapta_d16_engine.gen_candidates_sapta_union) run on the
    focus active map — the union condition, gap/vol_ratio keys
    and chronology keys are byte-identical to Design 16; only
    the days it may fire on change.

The allocation (tarang25_score.allocate25), the TRAIL re-exit,
the TRAIL placebo and the gate are Designs 12/13/16's
(sapta_d12_engine / sapta_d13_engine / sapta_d16_engine /
sapta_owner_engine), reused.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade.
Paper only, real money Rs 0.
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_d8_run as D8R
import sapta_d16_engine as D16

COST = 40.0
QTY = 100

FOCUS_ENTITIES = ('Nifty Bank', 'Nifty Healthcare', 'Nifty Realty')
FOCUS_SET = frozenset(FOCUS_ENTITIES)


def build_focus_active(active_union):
    """SPEC s.2: {sym: set(dates)} restricted to focus-eligible
    name-days — active under the rotating selections with an
    A4 owner in F. Names with no focus-eligible day are dropped."""
    out = {}
    for sym, days in active_union.items():
        keep = {d for d in days if D8R.owner_of(sym, d) in FOCUS_SET}
        if keep:
            out[sym] = keep
    return out


def gen_candidates_sapta_focus(data, focus_active, order_maps):
    """SPEC s.2 candidates: Design 16's union generator on the
    focus active map. Returns (cands, skipped_first_days,
    side_conflicts) exactly as the D16 generator does."""
    active_i = {s: focus_active[s] for s in data if s in focus_active}
    return D16.gen_candidates_sapta_union(data, active_i, order_maps)
