#!/usr/bin/env python3
"""ROUND 5 — WS1 (GAP-FADE SHORT, UP-cell mirror) + WS2 (banked-sleeve
micro-grid).

WS1: the R4-03 banked phenomenon was fade-LONG restricted to DOWN+FLAT
cells. The mirror — fade gap-UPS (SHORT) restricted to UP cells — was
never gated (R3's diagnostic scored the UNRESTRICTED short side:
-49/-9 per trade in the pooled halves). Cells:
  R5-01 fade SHORT >=1.5%, UP cells only      (09:20, T125/S050)
  R5-02 fade SHORT >=1.5%, UP+FLAT cells      (09:20, T125/S050)
Added as a separate component GAP-FADE-SHORT so the banked LONG sleeve
is never touched; if R5-01 banks, R5-02 swaps it.

WS2: neighbours of the banked R4-03 cell (DOWN+FLAT, LONG, 09:20) that
Round 4 did NOT test — R4's threshold swaps were scored on the
UNRESTRICTED sleeve; the restricted form's own neighbours are open:
  R5-03 threshold 1.25% (DOWN+FLAT, T125/S050)
  R5-04 threshold 1.75% (DOWN+FLAT, T125/S050)
  R5-05 exits T100/S065  (thr 1.5, DOWN+FLAT)
  R5-06 exits T150/S065  (thr 1.5, DOWN+FLAT)
Each is a swap of the GAP-FADE component, gated against the incumbent.

Placebos per cell (pre-registered, R4 pattern): the mirror population
(follow, opposite only_dir) under the cell's identical parameters, and
the same cell entered one bar later — each scored as a whole book with
the target sleeve removed and the placebo sleeve added.

Timing: the gap signal is complete at bar 0's open print; every real
and placebo entry here is at bar >= 1 — strictly after the signal
print. timing_violations = 0 BY CONSTRUCTION, derived, not defaulted.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r5_lib as R5

books = R5.load_books()
LABELS = R.LABELS
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
SYMBOLS = g["SYMBOLS"]
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None,
             cells=None, comp_name=None):
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
            comp = comp_name or ("GAP-FOLLOW" if mode == "follow"
                                 else "GAP-FADE")
            out.append(R.norm(comp, day, sym, direction,
                              bars[entry_bar]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

def without(books_, comp):
    return {yr: [t for t in books_[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

def run_add_cell(cyc, label, comp, rows, mirror_rows, late_rows):
    global books
    present = any(t["comp"] == comp for yr in (2025, 2026)
                  for t in books[yr])
    var = (R5.swap(books, comp, rows) if present
           else R5.add_comp(books, comp, rows))
    base_wo = without(books, comp)
    pl = [R5.full_total(R5.add_comp(base_wo, "GAP-FOLLOW", mirror_rows)),
          R5.full_total(R5.add_comp(base_wo, comp, late_rows))]
    out = R5.gate(books, var, pl, timing_violations=0)
    n = {str(yr): len(rows[yr]) for yr in (2025, 2026)}
    R5.record(cyc, label, out,
              note=f"sleeve trades {n}; timing: entries at bar 1, signal "
                   f"complete at bar-0 open print -> 0 violations by "
                   f"construction; placebos: mirror-follow book {pl[0]}; "
                   f"one-bar-late book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var
        R5.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

def run_swap_cell(cyc, label, thr, tgt, stp, cells):
    global books
    rows = gap_rows("fade", thr, 1, tgt, stp, only_dir="LONG",
                    cells=cells)
    mirror = gap_rows("follow", thr, 1, tgt, stp, only_dir="SHORT",
                      cells=cells)
    late = gap_rows("fade", thr, 2, tgt, stp, only_dir="LONG",
                    cells=cells)
    var = R5.swap(books, "GAP-FADE", rows)
    base_wo = without(books, "GAP-FADE")
    pl = [R5.full_total(R5.add_comp(base_wo, "GAP-FOLLOW", mirror)),
          R5.full_total(R5.add_comp(base_wo, "GAP-FADE", late))]
    out = R5.gate(books, var, pl, timing_violations=0)
    n = {str(yr): len(rows[yr]) for yr in (2025, 2026)}
    R5.record(cyc, label, out,
              note=f"sleeve trades {n}; timing: entries at bar 1, signal "
                   f"complete at bar-0 open print -> 0 violations by "
                   f"construction; placebos: mirror-follow book {pl[0]}; "
                   f"one-bar-late book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var
        R5.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

# ------------------------------------------------------------- WS1 -----
rows_up = gap_rows("fade", 1.5, 1, 1.25, 0.5, only_dir="SHORT",
                   cells={"UP"}, comp_name="GAP-FADE-SHORT")
mir_up = gap_rows("follow", 1.5, 1, 1.25, 0.5, only_dir="LONG",
                  cells={"UP"})
late_up = gap_rows("fade", 1.5, 2, 1.25, 0.5, only_dir="SHORT",
                   cells={"UP"}, comp_name="GAP-FADE-SHORT")
run_add_cell("R5-01", "GAP-FADE SHORT >=1.5%, UP-cell days only "
                      "(09:20, T125/S050)", "GAP-FADE-SHORT",
             rows_up, mir_up, late_up)

rows_uf = gap_rows("fade", 1.5, 1, 1.25, 0.5, only_dir="SHORT",
                   cells={"UP", "FLAT"}, comp_name="GAP-FADE-SHORT")
mir_uf = gap_rows("follow", 1.5, 1, 1.25, 0.5, only_dir="LONG",
                  cells={"UP", "FLAT"})
late_uf = gap_rows("fade", 1.5, 2, 1.25, 0.5, only_dir="SHORT",
                   cells={"UP", "FLAT"}, comp_name="GAP-FADE-SHORT")
run_add_cell("R5-02", "GAP-FADE SHORT >=1.5%, UP+FLAT-cell days "
                      "(09:20, T125/S050)", "GAP-FADE-SHORT",
             rows_uf, mir_uf, late_uf)

# ------------------------------------------------------------- WS2 -----
run_swap_cell("R5-03", "GAP-FADE LONG >=1.25% swap (DOWN+FLAT, 09:20, "
                       "T125/S050)", 1.25, 1.25, 0.5, {"DOWN", "FLAT"})
run_swap_cell("R5-04", "GAP-FADE LONG >=1.75% swap (DOWN+FLAT, 09:20, "
                       "T125/S050)", 1.75, 1.25, 0.5, {"DOWN", "FLAT"})
run_swap_cell("R5-05", "GAP-FADE LONG exits T100/S065 swap (thr 1.5, "
                       "DOWN+FLAT, 09:20)", 1.5, 1.00, 0.65,
              {"DOWN", "FLAT"})
run_swap_cell("R5-06", "GAP-FADE LONG exits T150/S065 swap (thr 1.5, "
                       "DOWN+FLAT, 09:20)", 1.5, 1.50, 0.65,
              {"DOWN", "FLAT"})

print("WS1+WS2 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)},
      "trades:", {yr: len(books[yr]) for yr in (2025, 2026)})
