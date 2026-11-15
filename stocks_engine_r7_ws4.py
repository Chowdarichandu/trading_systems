#!/usr/bin/env python3
"""ROUND 7 — WS4: QUIET-NAME NE-REV (R7-06).
Construction and verdict rule EXACTLY as pre-registered in
stocks_engine_round7_2026-11-02.md. Order of operations (frozen):
(1) re-anchor the unreconstructed R5-07 builder to its recorded
standalone; (2) rebuild the morning NE-REV on the CERTIFIED
population and report the population delta vs R5-07 BEFORE the
verdict is read; (3) apply the quiet-name filter (trailing-20-session
median daily range% strictly below the day's watchlist median —
trailing daily data only) and gate whole-book.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r6_builders as B6
import stocks_engine_r7_lib as R7
import stocks_engine_r7_builders as B

books = R7.load_books()
COMP = "NE-REV-Q"

# ------------------------------------------------------------ anchor -
a_real, a_flip, a_late, a_viol = B6.nerev_rows(2.0, "10:35", None)
assert a_viol == 0, a_viol
sa = {yr: round(sum(t["net"] for t in a_real[yr]), 2)
      for yr in (2025, 2026)}
assert sa == {2025: 12209.45, 2026: 24306.56}, sa
assert (len(a_real[2025]), len(a_real[2026])) == (303, 388)
print("R5-07 anchor OK (standalone +12,209.45 / +24,306.56; "
      "303/388 rows)")

# ------------------------------------------- certified-population NE-REV
cert, r5set, added = B.certified_exclusions()
c_real, _, _, c_viol, c_stats = B.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.0, excl=cert)
assert c_viol == 0, c_viol
keys_a = {(t["date"], t["stock"]) for yr in (2025, 2026)
          for t in a_real[yr]}
keys_c = {(t["date"], t["stock"]) for yr in (2025, 2026)
          for t in c_real[yr]}
removed = keys_a - keys_c
csa = {yr: round(sum(t["net"] for t in c_real[yr]), 2)
       for yr in (2025, 2026)}
print(f"certified-population morning NE-REV: standalone {csa}; "
      f"rows {len(c_real[2025]) + len(c_real[2026])} vs R5-07's "
      f"691; population rows removed by the R6-11 strengthening: "
      f"{len(removed)} {sorted(removed)}")

# ------------------------------------------------------------- quiet -
real, flipped, late, viol, stats = B.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.0, excl=cert,
    quiet=True)
assert viol == 0, viol
print(f"quiet filter: signal days {stats['signal_days']}, rejected "
      f"as not-quiet {stats['quiet_rejected']}, trades "
      f"{len(real[2025]) + len(real[2026])}")

real = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
flipped = {yr: [dict(t, comp="NE-REV-Q-S") for t in flipped[yr]]
           for yr in flipped}
late = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
var = R7.add_comp(books, COMP, real)
pl = [R7.full_total(R7.add_comp(books, "NE-REV-Q-S", flipped)),
      R7.full_total(R7.add_comp(books, COMP, late))]
out = R7.gate(books, var, pl, timing_violations=viol)
n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
saq = {str(yr): round(sum(t["net"] for t in real[yr]), 2)
       for yr in (2025, 2026)}
R7.record(
    "R7-06",
    "QUIET-NAME NE-REV (morning NE-REV on the certified population, "
    "names with trailing-20-session median daily range% strictly "
    "below the day's watchlist median)", out,
    note=f"population trades {n}; standalone {saq}. Anchors first: "
         f"R5-07 reproduced exactly (+12,209.45 / +24,306.56; "
         f"303/388 rows). Certified-population morning NE-REV "
         f"standalone {csa} on {len(c_real[2025]) + len(c_real[2026])} "
         f"rows — the R6-11 strengthening removed {len(removed)} "
         f"population rows {sorted(removed)}. Quiet filter rejected "
         f"{stats['quiet_rejected']} of {stats['signal_days']} "
         f"signal days. Timing audit: entry bar (10:35) strictly "
         f"after the signal bar (10:25) on every row, violations "
         f"counted = {viol}; quiet characteristic uses trailing "
         f"daily bars strictly before the trade day. Placebos: "
         f"opposite-direction book {pl[0]}; one-bar-late book "
         f"{pl[1]}",
    extra={"standalone": saq, "population_trades": n,
           "certified_population_standalone": {str(k): v for k, v
                                               in csa.items()},
           "removed_population_rows": [list(k) for k in
                                       sorted(removed)],
           "quiet_rejected": stats["quiet_rejected"],
           "signal_days": stats["signal_days"]})
if out["verdict"]:
    books = var
    R7.save_books(books)
    print("    -> BANKED; incumbent updated")
print("WS4 done. Incumbent Jan-Oct:",
      {yr: R7.jo(books, yr) for yr in (2025, 2026)})
