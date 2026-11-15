#!/usr/bin/env python3
"""ROUND 7 — WS2: NE-REV AFTERNOON VARIANT (R7-04).
Construction and verdict rule EXACTLY as pre-registered in
stocks_engine_round7_2026-11-02.md: certified non-event population;
signal = close of the 13:25 bar vs prior close <= -2.00%; entry LONG
at the open of the 13:35 bar; T100/S065 via replay_plain (entry bar
checked); square-off 15:10; one trade per stock-day. Placebos:
opposite direction at the same entry bar; same direction one bar
later (13:40). Timing violations counted in code, asserted 0.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r7_lib as R7
import stocks_engine_r7_builders as B

books = R7.load_books()
COMP = "NE-REV-PM"

cert, r5set, added = B.certified_exclusions()
real, flipped, late, viol, stats = B.nerev_gen(
    signal_time="13:25", entry_time="13:35", thr=2.0, excl=cert)
assert viol == 0, viol
print(f"population stock-days (certified): {stats['population_days']}; "
      f"signal days: {stats['signal_days']}; trades: "
      f"{len(real[2025]) + len(real[2026])}")

real = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
flipped = {yr: [dict(t, comp="NE-REV-PM-S") for t in flipped[yr]]
           for yr in flipped}
late = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
var = R7.add_comp(books, COMP, real)
pl = [R7.full_total(R7.add_comp(books, "NE-REV-PM-S", flipped)),
      R7.full_total(R7.add_comp(books, COMP, late))]
out = R7.gate(books, var, pl, timing_violations=viol)
n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
sa = {str(yr): round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
R7.record(
    "R7-04",
    "NE-REV AFTERNOON (non-event reversal, signal 13:25 close "
    "<= -2.00%, entry 13:35, T100/S065)", out,
    note=f"population trades {n}; standalone {sa}; certified "
         f"population stock-days {stats['population_days']}, signal "
         f"days {stats['signal_days']}; timing audit: entry bar "
         f"(13:35) strictly after the signal bar (13:25) on every "
         f"row, violations counted = {viol}; placebos: "
         f"opposite-direction book {pl[0]}; one-bar-late book "
         f"{pl[1]}",
    extra={"standalone": sa, "population_trades": n,
           "signal_days": stats["signal_days"]})
if out["verdict"]:
    books = var
    R7.save_books(books)
    print("    -> BANKED; incumbent updated")
print("WS2 done. Incumbent Jan-Oct:",
      {yr: R7.jo(books, yr) for yr in (2025, 2026)})
