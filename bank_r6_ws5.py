#!/usr/bin/env python3
"""ROUND 6 WS5 — Cycles 145-148: Volrix completion on the causal book.
One axis at a time from the Round-5 banked cell (-1.0%, cd15), NS3 held
at the v20 incumbent geometry (GEO) so each delta is the Volrix axis
alone, gated vs v20:
  C145 cooldown 12 @ -1.0%   C146 cooldown 20 @ -1.0%
  C147 trigger -0.9% @ cd15  C148 trigger -1.1% @ cd15
(The -0.75%/-1.25% extremes were closed in Round 5.)
Causality certificate: Volrix legs are prior-day-triggered 09:20
entries; regeneration consumes only stored daily closes up to the
trigger day; pooling/states consume the same timestamps."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r6_core as c
from bank_r6_core import judge6, v20_ref, GDGU, GEO
from bank_r3_setups import generate as gen_setups

ref = v20_ref()
print(f"v20 ref: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")
gen = gen_setups()
cells = [(145, -0.01, 12), (146, -0.01, 20), (147, -0.009, 15), (148, -0.011, 15)]
pools = {}
for cyc, thr, cd in cells:
    legs = c5.volrix_gen_legs(thr, cd)
    pools[cyc] = c5.pool_b2(c5.component_legs(volrix=legs), solo_rule="causal")
    print(f"C{cyc} thr={thr} cd={cd}: {len(legs)} volrix legs")
all_legs = []
for p in pools.values(): all_legs += p
all_legs += c5.ns3_legs(causal=True) + gen["S3A"] + gen["S3E"] + gen["S3D"]
still = c5.fetch_missing(all_legs)
print("still missing:", still)
assert not still
ns1 = c.aud_inputs()[1]
for cyc, thr, cd in cells:
    judge6(f"C{cyc} Volrix thr={thr} cd={cd}", ref, pools[cyc], ns1,
           ns3_causal_form=True, ns3_filter=GDGU, ns3_params=GEO)
