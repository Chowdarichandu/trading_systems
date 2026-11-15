#!/usr/bin/env python3
"""ROUND 4 — WS2: GAP-FADE LONG REFINEMENT (attack the cross-year leg).

Base form = R3-10: fade LONG-only, |gap| >= 1.5%, entry 09:20 open
(entry_bar 1), T125/S050. One axis at a time, gated per cell, in the
brief's order: regime restriction first, then threshold, then entry,
then exits. A cell passing ALL legs (incl. cross-year + leg x) BANKS.

Cells:
  R4-02 regime DOWN only          R4-06 threshold 3.0
  R4-03 regime DOWN+FLAT          R4-07 entry 09:15 (bar 0)
  R4-04 threshold 2.0              R4-08 entry 09:35 (bar 4)
  R4-05 threshold 2.5              R4-09 exits T150/S080
Placebos per cell (pre-registered): the mirror population (GAP-FOLLOW
SHORT-only on the same gap-down days) under the cell's identical
parameters, and the same cell entered one bar later.
If a cell banks, later cells refine the banked sleeve via swap (never a
second copy of the sleeve).
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r4_lib as R4

books = R4.load_books()
LABELS = R.LABELS
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
SYMBOLS = g["SYMBOLS"]
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None,
             cells=None):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            if cells is not None and LABELS.get(day) not in cells:
                continue
            bars = spot.get(day, [])
            if len(bars) <= entry_bar:
                continue
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            gap = (bars[0]["open"] / prev_close - 1) * 100
            if abs(gap) < thr:
                continue
            natural = "LONG" if gap > 0 else "SHORT"
            direction = natural if mode == "follow" else (
                "SHORT" if natural == "LONG" else "LONG")
            if only_dir and direction != only_dir:
                continue
            entry = bars[entry_bar]["open"]
            r = replay(bars, entry_bar, entry, direction, tgt, stp)
            if r is None:
                continue
            er, ep, et = r
            comp = "GAP-FOLLOW" if mode == "follow" else "GAP-FADE"
            out.append(R.norm(comp, day, sym, direction,
                              bars[entry_bar]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

def apply_sleeve(base_books, rows):
    present = any(t["comp"] == "GAP-FADE" for yr in (2025, 2026)
                  for t in base_books[yr])
    return (R4.swap(base_books, "GAP-FADE", rows) if present
            else R4.add_comp(base_books, "GAP-FADE", rows))

def run_cell(cyc, label, thr=1.5, entry_bar=1, tgt=1.25, stp=0.5,
             cells=None):
    global books
    rows = gap_rows("fade", thr, entry_bar, tgt, stp, only_dir="LONG",
                    cells=cells)
    mirror = gap_rows("follow", thr, entry_bar, tgt, stp,
                      only_dir="SHORT", cells=cells)
    late = gap_rows("fade", thr, entry_bar + 1, tgt, stp,
                    only_dir="LONG", cells=cells)
    var = apply_sleeve(books, rows)
    # placebos: the current base with the sleeve removed and the placebo
    # population added instead (identical handling to the variant):
    base_no_sleeve = {yr: [t for t in books[yr]
                           if t["comp"] != "GAP-FADE"] for yr in (2025, 2026)}
    pl = [R4.full_total(R4.add_comp(base_no_sleeve, "GAP-FOLLOW", mirror)),
          R4.full_total(R4.add_comp(base_no_sleeve, "GAP-FADE", late))]
    out = R4.gate(books, var, pl)
    n = {str(yr): len(rows[yr]) for yr in (2025, 2026)}
    R4.record(cyc, label, out,
              note=f"sleeve trades {n}; placebos: mirror-follow book "
                   f"{pl[0]}; one-bar-late book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var
        R4.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

run_cell("R4-02", "GAP-FADE LONG >=1.5%, DOWN-cell days only "
                  "(09:20, T125/S050)", cells={"DOWN"})
run_cell("R4-03", "GAP-FADE LONG >=1.5%, DOWN+FLAT-cell days "
                  "(09:20, T125/S050)", cells={"DOWN", "FLAT"})
run_cell("R4-04", "GAP-FADE LONG >=2.0% (09:20, T125/S050)", thr=2.0)
run_cell("R4-05", "GAP-FADE LONG >=2.5% (09:20, T125/S050)", thr=2.5)
run_cell("R4-06", "GAP-FADE LONG >=3.0% (09:20, T125/S050)", thr=3.0)
run_cell("R4-07", "GAP-FADE LONG >=1.5%, entry 09:15 open "
                  "(T125/S050)", entry_bar=0)
run_cell("R4-08", "GAP-FADE LONG >=1.5%, entry 09:35 open "
                  "(T125/S050)", entry_bar=4)
run_cell("R4-09", "GAP-FADE LONG >=1.5%, exits T150/S080 (09:20)",
         tgt=1.50, stp=0.80)

print("WS2 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)},
      "trades:", {yr: len(books[yr]) for yr in (2025, 2026)})
