#!/usr/bin/env python3
"""ROUND 6 WS1 — Cycles 137-140: NS3 on CAUSAL times.
Census first (all NS3 candidate legs at signal+5 by subleg), then:
  C137 admission retest: ALL sublegs @ GEO (lock65/tgt2 175) — does the
       Round-4 FLAT exclusion still hold causally? (Round-4's verdict was
       measured on mis-timed entries and is NOT evidence here.)
  C138 GD+GU @ stop50/trig90/lock50/tgt2 175
  C139 GD+GU @ stop50/trig90/lock65/tgt2 150
  C140 GD+GU @ stop50/trig90/lock50/tgt2 150
(Incumbent cell GD+GU @ lock65/tgt2 175 == v20, reproduced in sanity.)
Causality certificate: NS3 legs enter at signal+5 (bank_r5_core.ns3_legs
causal form); admission inputs (gap class, subleg) are properties of the
signal bar, known before entry; pooling/states consume the same times."""
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r6_core as c
from bank_r6_core import judge6, v20_inputs, v20_ref, GDGU, GEO

ref = v20_ref()
print(f"v20 ref: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")
pooled, ns1 = v20_inputs()

all_ns3 = c5.ns3_legs(causal=True)
cen = Counter(c5.enrich(l)["_subleg"] for l in all_ns3)
print(f"NS3 causal census: {len(all_ns3)} legs by subleg: {dict(cen)}")
still = c5.fetch_missing(pooled + ns1 + all_ns3)
print("still missing:", still)
assert not still

def P(lock, tgt2):
    return dict(stop=50.0, trig=90.0, lock=lock, tgt2=tgt2)

cells = [
    (137, "ALL sublegs @ L65/G175", None, P(65.0, 175.0)),
    (138, "GDGU @ L50/G175", GDGU, P(50.0, 175.0)),
    (139, "GDGU @ L65/G150", GDGU, P(65.0, 150.0)),
    (140, "GDGU @ L50/G150", GDGU, P(50.0, 150.0)),
]
for cyc, name, filt, params in cells:
    res = judge6(f"C{cyc} NS3 {name}", ref, pooled, ns1,
                 ns3_causal_form=True, ns3_filter=filt, ns3_params=params)
    print("   detail:", [d for d in res["detail"] if d["family"] == "NS3"])
