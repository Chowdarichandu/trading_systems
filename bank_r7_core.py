#!/usr/bin/env python3
"""ROUND 7 core (BANKNIFTY ONLY). Baseline = book v21 (Round 6 freeze):
v20 inputs assembled with NS3(GD+GU) @ stop -50 / trig +90 / lock +50 /
tgt2 +150, square-off 15:20 (bank_r5_core.SQ). judge7 = the Round-5/6
pipeline (bank_r6_core.assemble6, delay-0 book + delay-6 placebo twin
sharing the admission plan) under bank_r2_core.controls/gate PLUS the
protocol's ex-top-3 >= 0 leg enforced explicitly (the brief's banking
gate: net + FT90 + frequency together, no green month flips red,
halves >= 0, placebo beaten, ex-top-3 >= 0, NC 0, timing clean,
independent re-sum when written).

Causality certification (written, per lessons 46/52/64-71/72-77): all
legs enter at their true causal bars — component legs at their own
system's signal+5 (or 09:20 on a prior-day trigger), NS1 regenerated at
crossing+1, NS3 at signal+5. Round-7 variant legs carry their own
certificates in their WS scripts. Rounds 1-4 magnitudes are NOT
evidence; only constructions re-tested on causal times count."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r6_core as c6
from bank_r6_core import assemble6, v20_inputs, GDGU
from bank_r2_core import controls, gate, write_trades

P21 = dict(stop=50.0, trig=90.0, lock=50.0, tgt2=150.0)

_V21 = {}
def v21_ref():
    if "ref" not in _V21:
        pooled, ns1 = v20_inputs()
        rows, nc, lbk, detail, plan = assemble6(
            pooled, ns1, delay=0, ns3_causal_form=True,
            ns3_filter=GDGU, ns3_params=P21)
        prows, pnc, _pl, _pd, _p2 = assemble6(
            pooled, ns1, delay=6, ns3_causal_form=True,
            ns3_filter=GDGU, ns3_params=P21, plan=plan)
        _V21["ref"] = controls(rows, nc, lbk, prows, pnc)
        _V21["rows"] = rows
        _V21["detail"] = detail
    return _V21["ref"]

def judge7(label, ref, pooled, ns1, write=None, **book_kw):
    book_kw.setdefault("ns3_causal_form", True)
    book_kw.setdefault("ns3_filter", GDGU)
    book_kw.setdefault("ns3_params", P21)
    rows, nc, lbk, detail, plan = assemble6(pooled, ns1, delay=0, **book_kw)
    prows, pnc, _plbk, _pd, _p2 = assemble6(pooled, ns1, delay=6,
                                            plan=plan, **book_kw)
    ctrl = controls(rows, nc, lbk, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        ctrl["independent_resum"] = resum
        ctrl["resum_matches"] = (resum["n"] == ctrl["n"]
                                 and abs(resum["net"] - ctrl["net"]) < 0.005)
    ok, why = gate(ctrl, ref, resum=resum)
    if ctrl["ex_top3_total"] < 0:
        ok = False
        why = list(why) + [f"ex-top-3 {ctrl['ex_top3_total']} < 0"]
    print(f"{label}: net={ctrl['net']:+,.2f} n={ctrl['n']} FT90={ctrl['ft90_pct']} "
          f"freq={ctrl['per_week_raw']} placebo={ctrl['placebo']['net']:+,.2f} "
          f"ex_top3={ctrl['ex_top3_total']:+,.2f} nc={nc}/{pnc} banked={ok} why={why}")
    return dict(label=label, controls=ctrl, banked=ok, gate_why=why,
                detail=detail, rows=rows)
