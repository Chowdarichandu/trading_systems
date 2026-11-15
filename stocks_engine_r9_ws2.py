#!/usr/bin/env python3
"""ROUND 9 — WS2 (R9-05): ATH-PROXIMITY MOMENTUM SLEEVE.

Frozen construction (Round-9 pre-registration): close within
2% of the trailing 252-session high -> LONG next session at the
09:35 open, T125/S050, square-off 15:10; NO event exclusion.
Gated whole-book per year as a new comp (bankable). Placebos:
opposite direction and one-bar-late whole books on the identical
population. Timing audit: entry session strictly after the
trigger session by series construction — violations counted in
the builder (asserted 0).
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING
import stocks_engine_r9_builders as B9

ing = ING.build_all()
books = ing["books"]

real, flipped, late, viol, stats = B9.ath_rows()
assert viol == 0, viol
sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
print(f"ATH population: triggers {stats['trigger_days']}, trades "
      f"{stats['trades']} ({len(real[2025])} in 2025, "
      f"{len(real[2026])} in 2026); standalone {sa}; skips: "
      f"no-next {stats['no_next_session']}, weekend "
      f"{stats['weekend_entry']}, no-0935 {stats['no_0935_bar']}, "
      f"no-0940 {stats['no_0940_bar']}")

COMP = "ATH-PROX"
real_r = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
flip_r = {yr: [dict(t, comp=COMP) for t in flipped[yr]]
          for yr in flipped}
late_r = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
var = R9.add_comp(books, COMP, real_r)
pl = [R9.full_total(R9.add_comp(books, COMP, flip_r)),
      R9.full_total(R9.add_comp(books, COMP, late_r))]
out = R9.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R9.record(
    "R9-05",
    "ATH-PROXIMITY MOMENTUM (close within 2% of trailing "
    "252-session high -> LONG next session 09:35, T125/S050, "
    "no event exclusion)", out,
    note=f"population: {stats['trigger_days']} trigger days -> "
         f"{stats['trades']} trades ({len(real[2025])} in 2025, "
         f"{len(real[2026])} in 2026 — the 252-session history "
         f"requirement means the 2025 population only exists "
         f"once a full trailing year is on file). Standalone: "
         f"{sa[2025]} (2025) / {sa[2026]} (2026). Skips counted: "
         f"no next session {stats['no_next_session']}, weekend "
         f"entry {stats['weekend_entry']}, missing 09:35 bar "
         f"{stats['no_0935_bar']}, missing 09:40 bar (late "
         f"placebo only) {stats['no_0940_bar']}. Timing audit: "
         f"every input (252-session high, trigger close) is "
         f"known at the trigger session's close; every entry "
         f"is the NEXT session's 09:35 open — violations "
         f"counted in code = {viol}. Placebos: "
         f"opposite-direction book {pl[0]}; one-bar-late book "
         f"{pl[1]}. Failed legs: {failed}.",
    extra={"standalone": {str(k): v for k, v in sa.items()},
           "population_trades": {"2025": len(real[2025]),
                                 "2026": len(real[2026])},
           "trigger_days": stats["trigger_days"]})
print("WS2 done.")
