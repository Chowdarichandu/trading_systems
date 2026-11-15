#!/usr/bin/env python3
"""ROUND 8 — WS1: DRIVE-CONTINUATION SLEEVE (R8-03; twin R8-04).

R8-03: certified non-event days, 10:25-bar close >= +2.00% vs prior
close -> LONG at the 10:35 open, T125/S050 (the follow twin of
NE-REV, never gated as its own sleeve). Placebos: opposite
direction on the same population; same direction one bar late.
R8-04 (frozen twin rule): the symmetric follow twin (10:25-bar
move <= -2.00% -> SHORT at 10:35, T125/S050) is gated ONLY IF the
LONG standalone net is positive in BOTH years; otherwise the
non-trigger is recorded as an audit entry and no twin is scored.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r7_builders as B7
import stocks_engine_r8_builders as B8
import stocks_engine_r8_lib as R8

books = R8.load_books()
cert_set = B7.certified_exclusions()[0]

def standalone(rows):
    return {yr: round(sum(t["net"] for t in rows[yr]), 2)
            for yr in (2025, 2026)}

def renamed(rows, comp):
    return {yr: [dict(t, comp=comp) for t in rows[yr]] for yr in rows}

# ------------------------------------------------------------- R8-03 -
real, flipped, late, viol, stats = B8.drive_rows(+1, 2.0,
                                                 excl=cert_set)
assert viol == 0, viol
sa = standalone(real)
print(f"DRIVE LONG standalone: {sa}; rows "
      f"{len(real[2025])}/{len(real[2026])}; population days "
      f"{stats['population_days']}, signal days "
      f"{stats['signal_days']}")
COMP = "DRIVE-CONT"
var = R8.add_comp(books, COMP, renamed(real, COMP))
pl = [R8.full_total(R8.add_comp(books, COMP, renamed(flipped, COMP))),
      R8.full_total(R8.add_comp(books, COMP, renamed(late, COMP)))]
out = R8.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R8.record(
    "R8-03",
    "DRIVE-CONTINUATION LONG (certified non-event, 10:25 move "
    ">= +2.00%, entry 10:35, T125/S050)", out,
    note=f"population stock-days {stats['population_days']}, "
         f"signal days {stats['signal_days']}; standalone "
         f"{sa[2025]} (2025) / {sa[2026]} (2026) on "
         f"{len(real[2025])}/{len(real[2026])} trades. Timing "
         f"audit: entry bar (10:35) strictly after the 10:25 "
         f"signal bar on every row, violations counted = {viol}. "
         f"Placebos: opposite-direction book {pl[0]}; one-bar-late "
         f"book {pl[1]}. Failed legs: {failed}.",
    extra={"standalone": {str(k): v for k, v in sa.items()},
           "population_trades": {"2025": len(real[2025]),
                                 "2026": len(real[2026])}})

# ------------------------------------------------------------- R8-04 -
if sa[2025] > 0 and sa[2026] > 0:
    real2, flipped2, late2, viol2, stats2 = B8.drive_rows(
        -1, 2.0, excl=cert_set)
    assert viol2 == 0, viol2
    sa2 = standalone(real2)
    COMP2 = "DRIVE-CONT-S"
    var2 = R8.add_comp(books, COMP2, renamed(real2, COMP2))
    pl2 = [R8.full_total(R8.add_comp(books, COMP2,
                                     renamed(flipped2, COMP2))),
           R8.full_total(R8.add_comp(books, COMP2,
                                     renamed(late2, COMP2)))]
    out2 = R8.gate(books, var2, pl2, timing_violations=viol2)
    failed2 = [k for k, v in out2["legs"].items()
               if isinstance(v, bool) and not v]
    R8.record(
        "R8-04",
        "DRIVE-CONTINUATION SHORT twin (certified non-event, "
        "10:25 move <= -2.00%, entry 10:35, T125/S050) — gated "
        "under the frozen twin rule", out2,
        note=f"twin rule triggered (R8-03 LONG standalone positive "
             f"in both years: {sa[2025]} / {sa[2026]}). Population "
             f"signal days {stats2['signal_days']}; standalone "
             f"{sa2[2025]} (2025) / {sa2[2026]} (2026) on "
             f"{len(real2[2025])}/{len(real2[2026])} trades. "
             f"Timing violations counted = {viol2}. Placebos: "
             f"opposite-direction book {pl2[0]}; one-bar-late book "
             f"{pl2[1]}. Failed legs: {failed2}. NOTE: this "
             f"population is NE-REV's signal population traded in "
             f"the follow direction; it is gated here as its own "
             f"sleeve against the starting book.",
        extra={"standalone": {str(k): v for k, v in sa2.items()},
               "population_trades": {"2025": len(real2[2025]),
                                     "2026": len(real2[2026])}})
else:
    R8.record_audit(
        "R8-04",
        "DRIVE SHORT twin — NOT SCORED (frozen twin rule not "
        "triggered)",
        f"the frozen rule gates the SHORT follow twin only if the "
        f"R8-03 LONG standalone is positive in BOTH years; actual "
        f"LONG standalone: 2025 {sa[2025]}, 2026 {sa[2026]}. Rule "
        f"not triggered; no twin construction was scored.")
print("WS1 done.")
