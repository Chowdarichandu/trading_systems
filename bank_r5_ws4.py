#!/usr/bin/env python3
"""Cycles 125-129 — WS4: Volrix-Bank grid on the audited pipeline.
Trigger axis at cooldown 10: -0.75% (125), -1.25% (126), -1.0% regenerated
(127, the frozen-cell reproduction with the two named exceptions), then
cooldown {5, 15} at the best trigger (128, 129). Regeneration: trigger =
prior session close-to-close <= thr, entry next session 09:20, strike ATM
at entry spot, monthly expiry in force (Round-5 sanity addendum)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r3_setups import generate as gen_setups

ref = c.aud_ref()
print(f"REF_AUD: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")
_ns1 = c.aud_inputs()[1]
gen = gen_setups()

def pooled_for(thr, cd):
    legs = c.volrix_gen_legs(thr, cd)
    comps = c.component_legs(volrix=legs)
    return c.pool_b2(comps, solo_rule="causal"), legs

cells = [(125, -0.0075, 10), (126, -0.0125, 10), (127, -0.01, 10)]
pools, legsets = {}, {}
for cyc, thr, cd in cells:
    pools[cyc], legsets[cyc] = pooled_for(thr, cd)
    print(f"C{cyc} thr={thr} cd={cd}: {len(legsets[cyc])} volrix legs, pooled {len(pools[cyc])}")
all_legs = _ns1 + c.ns3_legs(causal=True) + gen["S3A"] + gen["S3E"] + gen["S3D"]
for p in pools.values(): all_legs += p
still = c.fetch_missing(all_legs)
print("still missing:", still)
assert not still

results = {}
for cyc, thr, cd in cells:
    res = c.judge(f"C{cyc} Volrix thr={thr} cd={cd}", ref, pools[cyc], _ns1,
                  ns3_causal_form=True, ns3_filter=c.GDGU, ns3_params=c.GEO)
    results[cyc] = res["controls"]["net"]
    print("   detail:", res["detail"])
best_thr = max(((results[125], -0.0075), (results[126], -0.0125), (results[127], -0.01)))[1]
print(f"best trigger by net: {best_thr}")
for cyc, cd in ((128, 5), (129, 15)):
    pooled_v, legs = pooled_for(best_thr, cd)
    still = c.fetch_missing(pooled_v + _ns1 + c.ns3_legs(causal=True) +
                            gen["S3A"] + gen["S3E"] + gen["S3D"])
    assert not still, f"C{cyc} unfetchable {still}"
    res = c.judge(f"C{cyc} Volrix thr={best_thr} cd={cd} ({len(legs)} legs)", ref,
                  pooled_v, _ns1, ns3_causal_form=True, ns3_filter=c.GDGU,
                  ns3_params=c.GEO)
    print("   detail:", res["detail"])
