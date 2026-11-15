#!/usr/bin/env python3
"""ROUND 6 — WS1: NE-REV REPAIRS (R6-02..R6-05) + (d) AUDIT (R6-06).

Population, signal and exits exactly as pre-registered (R5-07's frozen
non-event population; 10:25-bar signal; T100/S065; one trade per
stock-day). Cells:
  R6-02  threshold 2.25%, entry 10:35, all cells
  R6-03  threshold 2.50%, entry 10:35, all cells
  R6-04  threshold 2.00%, entry 10:35, DOWN+FLAT cells only
  R6-05  threshold 2.00%, entry 11:05, all cells
Placebos per cell (whole books, identical population): opposite
direction at the same entry bar; same direction one bar later.
Timing violations are COUNTED by the builder (entry bar vs the 10:25
signal bar) and asserted 0 before gating — never defaulted.
A repair passing all legs banks as NE-REV-LONG; later cells then swap
that component (the R5 run_add_cell discipline).
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r6_lib as R6
import stocks_engine_r6_builders as B

books = R6.load_books()
COMP = "NE-REV-LONG"

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

def run_cell(cyc, label, thr, entry_time, cells):
    global books
    real, flipped, late, viol = B.nerev_rows(thr, entry_time, cells)
    assert viol == 0, (cyc, viol)
    real = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
    flipped = {yr: [dict(t, comp="NE-REV-SHORT") for t in flipped[yr]]
               for yr in flipped}
    late = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
    present = any(t["comp"] == COMP for yr in (2025, 2026)
                  for t in books[yr])
    var = (R6.swap(books, COMP, real) if present
           else R6.add_comp(books, COMP, real))
    base_wo = without(books, COMP)
    pl = [R6.full_total(R6.add_comp(base_wo, "NE-REV-SHORT", flipped)),
          R6.full_total(R6.add_comp(base_wo, COMP, late))]
    out = R6.gate(books, var, pl, timing_violations=viol)
    n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
    R6.record(cyc, label, out,
              note=f"population trades {n}; timing audit: entry bar "
                   f"({entry_time}) strictly after the 10:25 signal bar "
                   f"on every row, violations counted = {viol}; "
                   f"placebos: opposite-direction book {pl[0]}; "
                   f"one-bar-late book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in real[yr]), 2) for yr in real},
                  "population_trades": n})
    if out["verdict"]:
        books = var
        R6.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

run_cell("R6-02", "NE-REV LONG thr 2.25% (non-event, entry 10:35, "
                  "T100/S065)", 2.25, "10:35", None)
run_cell("R6-03", "NE-REV LONG thr 2.50% (non-event, entry 10:35, "
                  "T100/S065)", 2.50, "10:35", None)
run_cell("R6-04", "NE-REV LONG thr 2.00%, DOWN+FLAT cells only "
                  "(non-event, entry 10:35, T100/S065)", 2.0, "10:35",
         {"DOWN", "FLAT"})
run_cell("R6-05", "NE-REV LONG thr 2.00%, entry 11:05 (non-event, "
                  "T100/S065)", 2.0, "11:05", None)

# R6-06 — (d) carrier exclusion: the pre-registered skip ------------------
R6.record_audit(
    "R6-06",
    "NE-REV repair (d) carrier exclusion — SKIPPED, no causal ranking",
    "Pre-registered condition not met. The variant needs the book's "
    "top-3 earner names ranked on the PRIOR year's book for BOTH "
    "judging years. For 2026 rows the completed 2025 book exists "
    "(top-3: OBEROIRLTY Rs30,432.17, ASTRAL Rs14,260.02, GODREJCP "
    "Rs7,970.91) and that ranking is causal. For 2025 rows the prior "
    "year is 2024: no SarvaRitu book exists for 2024 in this workspace "
    "— the machinery's event calendars and component populations cover "
    "2025 and Jan-Oct 2026 only — and ranking 2025 rows on the 2026 "
    "book would be look-ahead (refused). The both-years condition "
    "therefore fails, so (d) is skipped with no substitute ranking "
    "invented, exactly as pre-registered. No candidate was gated.",
    extra={"skipped": True,
           "causal_ranking_available_for": ["2026 (on the 2025 book)"],
           "causal_ranking_unavailable_for": ["2025 (no 2024 book)"]})

print("WS1 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
