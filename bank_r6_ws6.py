#!/usr/bin/env python3
"""ROUND 6 WS6 — Cycle 149: combination / final re-gate.
The round's only banking axis is NS3 geometry (C138/C139/C140 are
mutually exclusive cells of one axis; C140 dominates). WS3/WS4/WS5
banked nothing, so the combination is the best banked variant —
v20 with NS3(GD+GU) @ stop50/trig90/lock50/tgt2 150 — re-gated
whole-book vs v20 with independent re-sum, and chained vs the C138
and C139 controls (Round-5 WS6 hygiene)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r6_core as c
from bank_r6_core import assemble6, v20_inputs, v20_ref, GDGU, GEO
from bank_r2_core import controls, gate, write_trades

ref = v20_ref()
pooled, ns1 = v20_inputs()

def full(params):
    rows, nc, lbk, detail, plan = assemble6(pooled, ns1, delay=0,
                                            ns3_causal_form=True,
                                            ns3_filter=GDGU, ns3_params=params)
    prows, pnc, _pl, _pd, _p2 = assemble6(pooled, ns1, delay=6,
                                          ns3_causal_form=True,
                                          ns3_filter=GDGU, ns3_params=params,
                                          plan=plan)
    return controls(rows, nc, lbk, prows, pnc), rows, detail

def P(lock, tgt2):
    return dict(stop=50.0, trig=90.0, lock=lock, tgt2=tgt2)

c138, _r, _d = full(P(50.0, 175.0))
c139, _r, _d = full(P(65.0, 150.0))
rows, nc, lbk, detail, plan = assemble6(pooled, ns1, delay=0,
                                        ns3_causal_form=True,
                                        ns3_filter=GDGU, ns3_params=P(50.0, 150.0))
prows, pnc, _pl, _pd, _p2 = assemble6(pooled, ns1, delay=6,
                                      ns3_causal_form=True,
                                      ns3_filter=GDGU, ns3_params=P(50.0, 150.0),
                                      plan=plan)
ctrl = controls(rows, nc, lbk, prows, pnc)
resum = write_trades(rows, "bank_engine_r6_v21_trades.csv")
ctrl["independent_resum"] = resum
ctrl["resum_matches"] = (resum["n"] == ctrl["n"]
                         and abs(resum["net"] - ctrl["net"]) < 0.005)
ok_v20, why_v20 = gate(ctrl, ref, resum=resum)
ok_139, why_139 = gate(ctrl, c139, resum=resum)
ok_138, why_138 = gate(ctrl, c138, resum=resum)
print(f"C138 controls: net={c138['net']:+,.2f} n={c138['n']} FT90={c138['ft90_pct']}")
print(f"C139 controls: net={c139['net']:+,.2f} n={c139['n']} FT90={c139['ft90_pct']}")
print(f"C149 v21 = v20 x NS3@L50/G150: gate vs v20={ok_v20} {why_v20}; "
      f"vs C139={ok_139} {why_139}; vs C138={ok_138} {why_138}")
print("detail:", detail)
print(json.dumps(ctrl, indent=1, default=str))
json.dump(ctrl, open("bank_r6_v21_freeze.json", "w"), indent=1, default=str)
