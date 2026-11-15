#!/usr/bin/env python3
"""Cycle 135 — WS6: final whole-book re-gate of the best banked variant.
Banked in WS4: C127 (Volrix regen -1.0%/cd10), C128 (cd5), C129 (cd15) —
one axis, mutually exclusive; WS5 banked nothing, so the combination is
the best single variant (C129 by net) re-gated vs REF_AUD with full
controls + independent re-sum, and chained vs C127."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r2_core import controls, gate, write_trades
from bank_r3_setups import generate as gen_setups

ref = c.aud_ref()
_ns1 = c.aud_inputs()[1]
gen = gen_setups()

def build(thr, cd):
    comps = c.component_legs(volrix=c.volrix_gen_legs(thr, cd))
    return c.pool_b2(comps, solo_rule="causal")

def full(pooled, write=None):
    rows, nc, lbk, detail, plan = c._assemble(pooled, _ns1, delay=0,
                                              ns3_causal_form=True,
                                              ns3_filter=c.GDGU, ns3_params=c.GEO)
    prows, pnc, _pl, _pd, _p2 = c._assemble(pooled, _ns1, delay=6,
                                            ns3_causal_form=True,
                                            ns3_filter=c.GDGU, ns3_params=c.GEO,
                                            plan=plan)
    ctrl = controls(rows, nc, lbk, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        ctrl["independent_resum"] = resum
        ctrl["resum_matches"] = (resum["n"] == ctrl["n"]
                                 and abs(resum["net"] - ctrl["net"]) < 0.005)
    return ctrl, detail

p127 = build(-0.01, 10)
p129 = build(-0.01, 15)
still = c.fetch_missing(p127 + p129 + _ns1 + c.ns3_legs(causal=True) +
                        gen["S3A"] + gen["S3E"] + gen["S3D"])
assert not still
c127, _d1 = full(p127)
c129, det129 = full(p129, write="bank_engine_r5_v20_trades.csv")
ok_aud, why_aud = gate(c129, ref, resum=c129.get("independent_resum"))
ok_127, why_127 = gate(c129, c127, resum=c129.get("independent_resum"))
print(f"C127 controls: net={c127['net']:+,.2f} n={c127['n']} FT90={c127['ft90_pct']}")
print(f"C135 v20 (Volrix -1.0%/cd15 on causal rebuild): gate vs REF_AUD={ok_aud} {why_aud}; "
      f"gate vs C127={ok_127} {why_127}")
print("detail:", det129)
print(json.dumps(c129, indent=1, default=str))
json.dump(c129, open("bank_r5_v20_freeze.json", "w"), indent=1, default=str)
