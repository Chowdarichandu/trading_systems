#!/usr/bin/env python3
"""ROUND 6 — WS2: R5-03 INCREMENT CONDITIONING (R6-07, R6-08).

The >=1.25% DOWN+FLAT sleeve decomposes into the banked >=1.5% sleeve
plus the [1.25%, 1.5%) increment (identical construction). The
decomposition is VERIFIED before scoring: row-key set difference and
standalone sums must reproduce the recorded R5-03 deltas
(2025 +10,594.66 / 2026 +2,778.21 full-year = Jan-Oct here).
Only the increment is conditioned; the banked sleeve is never touched:
  R6-07  increment, DOWN-cell days only, entry bar 1 (09:20)
  R6-08  increment, DOWN+FLAT days, entry at the 09:40 bar (first bar
         open strictly after 09:35, selected by time lookup)
Placebos per cell: mirror increment (follow-SHORT, identical band /
cells / entry bar) and the same increment one bar later, as whole
books. Timing: gap signal complete at bar 0's open print; every entry
is strictly after it — violations counted (rows entering at 09:15)
and asserted 0.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r6_lib as R6
import stocks_engine_r6_builders as B

books = R6.load_books()
COMP = "GAP-FADE-INC"
DF = {"DOWN", "FLAT"}

def keys(rows):
    return {(t["date"], t["stock"]) for yr in (2025, 2026)
            for t in rows[yr]}

def standalone(rows):
    return {yr: round(sum(t["net"] for t in rows[yr]), 2)
            for yr in (2025, 2026)}

# ------------------------------------------------- verify decomposition
s15 = B.gap_rows("fade", 1.5, 1, 1.25, 0.5, only_dir="LONG", cells=DF)
s125 = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG", cells=DF)
inc = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG", cells=DF,
                 band=(1.25, 1.5))
book_fade = {yr: round(sum(t["net"] for t in books[yr]
                           if t["comp"] == "GAP-FADE"), 2)
             for yr in (2025, 2026)}
assert standalone(s15) == book_fade == {2025: 21470.27, 2026: 1492.21}, \
    (standalone(s15), book_fade)
assert keys(s15) | keys(inc) == keys(s125)
assert not (keys(s15) & keys(inc))
d = {yr: round(standalone(s125)[yr] - standalone(s15)[yr], 2)
     for yr in (2025, 2026)}
assert standalone(inc) == d == {2025: 10594.66, 2026: 2778.21}, \
    (standalone(inc), d)
print("decomposition verified: S1.25 = S1.5 (banked) + increment "
      f"{standalone(inc)}; row sets disjoint and exhaustive")

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

def run_inc(cyc, label, rows, mirror_rows, late_rows, note_extra):
    global books
    viol = sum(1 for yr in (2025, 2026) for t in rows[yr]
               if t["entry_time"] == "09:15")
    assert viol == 0, (cyc, viol)
    present = any(t["comp"] == COMP for yr in (2025, 2026)
                  for t in books[yr])
    var = (R6.swap(books, COMP, rows) if present
           else R6.add_comp(books, COMP, rows))
    base_wo = without(books, COMP)
    pl = [R6.full_total(R6.add_comp(base_wo, "GAP-FOLLOW", mirror_rows)),
          R6.full_total(R6.add_comp(base_wo, COMP, late_rows))]
    out = R6.gate(books, var, pl, timing_violations=viol)
    n = {str(yr): len(rows[yr]) for yr in (2025, 2026)}
    R6.record(cyc, label, out,
              note=f"increment trades {n}; timing: signal complete at "
                   f"the bar-0 open print, all entries strictly after "
                   f"(09:15 entries counted = {viol}); placebos: "
                   f"mirror-increment book {pl[0]}; one-bar-late book "
                   f"{pl[1]}. {note_extra}",
              extra={"standalone": standalone(rows)})
    if out["verdict"]:
        books = var
        R6.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

# R6-07 — increment, DOWN cells only, bar 1 --------------------------------
inc_down = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                      cells={"DOWN"}, band=(1.25, 1.5), comp_name=COMP)
mir_down = B.gap_rows("follow", 1.25, 1, 1.25, 0.5, only_dir="SHORT",
                      cells={"DOWN"}, band=(1.25, 1.5))
late_down = B.gap_rows("fade", 1.25, 2, 1.25, 0.5, only_dir="LONG",
                       cells={"DOWN"}, band=(1.25, 1.5), comp_name=COMP)
run_inc("R6-07", "GAP-FADE increment [1.25%,1.5%), DOWN-cell days only "
                 "(09:20, T125/S050) — conditioning of the R5-03 "
                 "increment; banked sleeve untouched",
        inc_down, mir_down, late_down,
        "Population: the increment's DOWN-cell subset only.")

# R6-08 — increment, DOWN+FLAT, entry 09:40 (by time lookup) --------------
inc_late = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                      cells=DF, band=(1.25, 1.5), comp_name=COMP,
                      entry_time="09:40")
mir_late = B.gap_rows("follow", 1.25, 1, 1.25, 0.5, only_dir="SHORT",
                      cells=DF, band=(1.25, 1.5), entry_time="09:40")
late_late = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                       cells=DF, band=(1.25, 1.5), comp_name=COMP,
                       entry_time="09:45")
assert all(t["entry_time"] == "09:40" for yr in (2025, 2026)
           for t in inc_late[yr])
dropped = len(keys(inc)) - len(keys(inc_late))
run_inc("R6-08", "GAP-FADE increment [1.25%,1.5%), DOWN+FLAT, entries "
                 "after 09:35 (09:40 open, T125/S050) — conditioning of "
                 "the R5-03 increment; banked sleeve untouched",
        inc_late, mir_late, late_late,
        f"Population: the full DOWN+FLAT increment entered at 09:40; "
        f"{dropped} increment stock-days dropped (no 09:40 bar).")

print("WS2 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
