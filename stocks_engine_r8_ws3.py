#!/usr/bin/env python3
"""ROUND 8 — WS3: R7-03 GEOMETRY NEIGHBOUR (R8-07).

REXP-SHORT restricted to DOWN regime cells, verbatim R7-03
population (anchored first at the frozen geometry T125/S050:
standalone must reproduce +14,870.39 / -8,399.33, 41/86 trades),
rescored at the single pre-registered neighbour cell T100/S065.
Gated whole-book as an addition. Placebos: opposite direction
(LONG, DOWN cells, T100/S065); same direction one bar late
(10:25, T100/S065). Frozen disposition: passes ALL legs -> banks;
either way the flagged list afterwards carries the T100/S065
form as the preferred REXP-DOWN flag with both prices stated.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r8_builders as B8
import stocks_engine_r8_lib as R8

books = R8.load_books()

def standalone(rows):
    return {yr: round(sum(t["net"] for t in rows[yr]), 2)
            for yr in (2025, 2026)}

# anchor at the frozen geometry via the parameterised builder
a_real, _, _, a_viol = B8.rexp_geo("SHORT", cells={"DOWN"},
                                   tgt=1.25, stp=0.50)
assert a_viol == 0, a_viol
sa_a = standalone(a_real)
assert sa_a == {2025: 14870.39, 2026: -8399.33}, sa_a
assert (len(a_real[2025]), len(a_real[2026])) == (41, 86)
print("R7-03 population anchor OK via rexp_geo at T125/S050 "
      "(+14,870.39 / -8,399.33; 41/86 rows)")

real, flipped, late, viol = B8.rexp_geo("SHORT", cells={"DOWN"},
                                        tgt=1.00, stp=0.65)
assert viol == 0, viol
sa = standalone(real)
assert (len(real[2025]), len(real[2026])) == (41, 86)
COMP = "REXP-SHORT"
var = R8.add_comp(books, COMP, real)
pl = [R8.full_total(R8.add_comp(books, COMP, flipped)),
      R8.full_total(R8.add_comp(books, COMP, late))]
out = R8.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R8.record(
    "R8-07",
    "REXP-SHORT DOWN-only at T100/S065 (geometry neighbour of "
    "the flagged R7-03 T125/S050 form)", out,
    note=f"population re-anchored exactly at the frozen geometry "
         f"first (T125/S050 standalone +14,870.39 / -8,399.33; "
         f"41/86 trades). At T100/S065: standalone {sa[2025]} "
         f"(2025) / {sa[2026]} (2026), same 41/86 trades. Timing "
         f"audit: entry bar (10:20) strictly after the 10:10 "
         f"signal bar on every row, violations counted = {viol}. "
         f"Placebos: opposite-direction (LONG, DOWN, T100/S065) "
         f"book {pl[0]}; one-bar-late book {pl[1]}. Failed legs: "
         f"{failed}. Frozen disposition: if banked, it displaces "
         f"the T125/S050 form as the live REXP-DOWN sleeve; if "
         f"not, the flagged list carries this T100/S065 form as "
         f"the preferred REXP-DOWN flag with both prices stated.",
    extra={"standalone": {str(k): v for k, v in sa.items()},
           "standalone_T125S050": {str(k): v for k, v in sa_a.items()},
           "population_trades": {"2025": 41, "2026": 86}})
print("WS3 done.")
