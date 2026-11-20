#!/usr/bin/env python3
"""
SAPTA Design 15 — engine additions (sapta_d15_SPEC.md):

  * Semi-annual selection layer (SPEC s.2): windows W0..W3
    ranked at the stored ranking dates of quarters Q0/Q2/Q4/Q6;
    a window's picks (the ranking quarter's stored picks) are
    active on every trading day of the window. Order maps per
    calendar quarter point at the window's ranking quarter
    (Design 14's pattern). Window ownership mirrors Amendment A4
    with the window's ranking quarter.
  * Stream-parameterised candidate generation (SPEC s.2/s.3):
    sapta_d12_engine.gen_candidates_sapta's body with the kept
    stream as a parameter ('GAP-FADE-UP-15' for Book A,
    'GAP-FADE-20' for Book B). Everything else — day context,
    take_trade (frozen exit), gap/vol_ratio keys, the
    chronology key from order_maps — is Design 12's, unchanged.

The TRAIL re-exit, the TRAIL placebo and the gate are Designs
13's (sapta_d13_engine / sapta_owner_engine), reused.
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

# window w -> ranking quarter index (stored layer)
WINDOW_Q = (0, 2, 4, 6)


def build_semi_maps(QUARTERS, Q_ENDS, PICK_OF, dates_between):
    """SPEC s.2: semi-annual active maps + order maps.
    Returns (semi_picks, semi_union, order_maps, windows) where
    semi_picks[(ent, sym)] = set of active dates, semi_union[sym]
    likewise, order_maps[qi] = the window ranking quarter's A4
    order for every calendar quarter qi, and windows is a list of
    dicts {window, ranking_quarter, ranking_date, start, end,
    top7}."""
    semi_picks = {}
    windows = []
    for w, qw in enumerate(WINDOW_Q):
        start = QUARTERS[qw]['ranking_date']
        end = Q_ENDS[qw + 1]
        days = dates_between(start, end)
        for ent in QUARTERS[qw]['top7']:
            for s in PICK_OF.get((ent, qw), []):
                semi_picks.setdefault((ent, s), set()).update(days)
        windows.append({'window': w, 'ranking_quarter': qw,
                        'ranking_date': start, 'start': start,
                        'end': end, 'top7': list(QUARTERS[qw]['top7'])})
    semi_union = {}
    for (_ent, s), dset in semi_picks.items():
        semi_union.setdefault(s, set()).update(dset)
    order_maps = {}
    for qi in range(len(QUARTERS)):
        src = WINDOW_Q[qi // 2]
        om = {}
        for ent in QUARTERS[src]['top7']:
            for sym in PICK_OF.get((ent, src), []):
                if sym not in om:
                    om[sym] = len(om)
        order_maps[qi] = om
    return semi_picks, semi_union, order_maps, windows


def semi_window_of(windows, date):
    """Window index containing date (windows are [start, end))."""
    for w in windows:
        if w['start'] <= date < w['end']:
            return w['window']
    return None


def semi_owner_of(PICK_OF, QUARTERS, windows, sym, date):
    """SPEC s.2 sleeve ownership: the highest-ranked entity in
    the window's top-7 that picked sym in the ranking quarter."""
    wi = semi_window_of(windows, date)
    if wi is None:
        return None
    qw = WINDOW_Q[wi]
    for ent in QUARTERS[qw]['top7']:
        if sym in PICK_OF.get((ent, qw), []):
            return ent
    return None


def gen_candidates_sapta_stream(data, active_map, order_maps, stream):
    """Design 12's gen_candidates_sapta with the kept stream as a
    parameter (SPEC s.2/s.3). Candidates are generated ONLY on
    the name's active days; the chronology key is
    order_maps[quarter_of(date)][sym] — for Book A the order maps
    already point at the window's ranking quarter."""
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
                for (sname, sl, side, el) in sigs:
                    if sname != stream:
                        continue
                    tr = T23.take_trade(D, day, ctx, sname, sl, side, el)
                    if tr is None:
                        continue
                    tr = dict(tr)
                    gap = float(ctx['o'][0] / prev['last_close'] - 1.0)
                    tr['gap_pct'] = round(gap, 6)
                    tr['vol_ratio'] = round(
                        T25.vol_ratio_at(D, int(day['ii'][0])), 6)
                    tr['univ'] = order_maps[D12.quarter_of(day['date'])][sym]
                    cands.append(tr)
            elif prev is None:
                skipped_first_days += 1
            if len(day['ii']):
                ii = day['ii']
                prev = dict(pdh=float(D['h'][ii].max()),
                            pdl=float(D['l'][ii].min()),
                            last_close=float(D['c'][ii[-1]]))
    return cands, skipped_first_days
