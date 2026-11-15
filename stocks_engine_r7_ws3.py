#!/usr/bin/env python3
"""ROUND 7 — WS3: TWO-DAY DISLOCATION REVERSAL (R7-05).
Construction and verdict rule EXACTLY as pre-registered in
stocks_engine_round7_2026-11-02.md: cumulative two-session move
close[D-1]/close[D-3] - 1 <= -3.00%; D, D-1, D-2 all certified
non-event; entry LONG at the open of D's 09:20 bar; T125/S050 via
replay_plain (entry bar checked); square-off 15:10; intraday only.
Placebos: opposite direction at the same entry bar; same direction
one bar later (09:25). Timing violations counted, asserted 0.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r7_lib as R7
import stocks_engine_r7_builders as B

books = R7.load_books()
COMP = "DISLOC-2D"

cert, r5set, added = B.certified_exclusions()
real, flipped, late, viol, stats = B.disloc_rows(excl=cert)
assert viol == 0, viol
print(f"signal days: {stats['signal_days']}; skipped (no 09:20 "
      f"bar): {stats['skipped_no_0920']}; trades: "
      f"{len(real[2025]) + len(real[2026])}")

real = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
flipped = {yr: [dict(t, comp="DISLOC-2D-S") for t in flipped[yr]]
           for yr in flipped}
late = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
var = R7.add_comp(books, COMP, real)
pl = [R7.full_total(R7.add_comp(books, "DISLOC-2D-S", flipped)),
      R7.full_total(R7.add_comp(books, COMP, late))]
out = R7.gate(books, var, pl, timing_violations=viol)
n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
sa = {str(yr): round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
R7.record(
    "R7-05",
    "TWO-DAY DISLOCATION REVERSAL (2-session fall >= 3.00%, "
    "certified non-event sessions, entry 09:20, T125/S050)", out,
    note=f"population trades {n}; standalone {sa}; signal days "
         f"{stats['signal_days']}, skipped for a missing 09:20 bar "
         f"{stats['skipped_no_0920']}; timing audit: the signal uses "
         f"only closes of sessions strictly before the trade day and "
         f"every entry is at the 09:20 bar, violations counted = "
         f"{viol}; placebos: opposite-direction book {pl[0]}; "
         f"one-bar-late book {pl[1]}",
    extra={"standalone": sa, "population_trades": n,
           "signal_days": stats["signal_days"],
           "skipped_no_0920": stats["skipped_no_0920"]})
if out["verdict"]:
    books = var
    R7.save_books(books)
    print("    -> BANKED; incumbent updated")
print("WS3 done. Incumbent Jan-Oct:",
      {yr: R7.jo(books, yr) for yr in (2025, 2026)})
