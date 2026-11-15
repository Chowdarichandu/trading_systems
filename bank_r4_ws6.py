#!/usr/bin/env python3
"""ROUND 4 WS6 (Cycles 102+): combinations of the round's passing
variants and best ingredients, re-gated as whole books vs v17, reported
vs the flagged stack, and displacement-tested vs the current best book
v18 (+128,048.00 / 106 / FT90 53.8). Combinations declared before scoring:
C102 v18 x WS1 best geometry (T90L65G175 on NS3); C103 v18 x WS4
transform (DTE>=14 stop -65); C104 GD+GU & premium<400; C105 GD+GU &
DTE<=7; C106 GD & premium<400; C107-109 WS3 positive cells (S3F/G/J) on
v18; C110 premium<400 & DTE<=7; C111 GD+GU & premium<400 & DTE<=7."""
import datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import controls, gate
from bank_r2_ns1 import V15
from bank_r4_core import build_stack, judge_stack, score_leg, stack_ref, REF17
from bank_r4_setups import generate_r4

TR = Path.home() / "workspace/trading"
GDGU = lambda l: l["_subleg"] in ("NS3-GD", "NS3-GU")
GEO = dict(stop=50.0, trig=90.0, lock=65.0, tgt2=175.0)

# v18 reference controls (asserted against the freeze)
_v18rows, _v18nc, _v18lbk, _d = build_stack(ns3_filter=GDGU)
_v18prows, _v18pnc, _p, _pd = build_stack(delay=6, ns3_filter=GDGU)
V18REF = controls(_v18rows, _v18nc, _v18lbk, _v18prows, _v18pnc)
assert V18REF["n"] == 106 and abs(V18REF["net"] - 128048.00) < 0.005 and V18REF["ft90_pct"] == 53.8
print(f"v18 ref asserted: {V18REF['net']:+,.2f} / {V18REF['n']} / FT90 {V18REF['ft90_pct']}")

def own_params(row, leg):
    if leg["date"] == leg["expiry"]:
        return dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
    return dict(V15[row["segment"]])

def judge_transform(label, **kw):
    """Flagged-stack-family build (kw) + the WS4 DTE>=14 stop-65 transform,
    with the own-assembly exactness pre-check on both builds."""
    outs = []
    for delay in (0, 6):
        rows, nc, lbk, detail = build_stack(delay=delay, **kw)
        mism = 0
        for i, r in enumerate(rows):
            leg = lbk[r["leg_key"]]
            dte = (dt.date.fromisoformat(leg["expiry"]) - dt.date.fromisoformat(leg["date"])).days
            if dte < 14: continue
            p0 = own_params(r, leg)
            chk = score_leg(leg, p0, delay=delay)
            assert chk is not None
            if abs(chk["net"] - r["net"]) > 0.005 or chk.get("ft90", 0) != r.get("ft90", 0):
                mism += 1; continue
            nr = score_leg(leg, dict(p0, stop=65.0), delay=delay)
            assert nr is not None
            rows[i] = {**r, **nr}
        assert mism == 0, f"{label} delay={delay}: {mism} exactness mismatches"
        outs.append((rows, nc, lbk))
    (rows, nc, lbk), (prows, pnc, _pl) = outs
    c = controls(rows, nc, lbk, prows, pnc)
    ok, why = gate(c, REF17)
    import math
    res = dict(label=label, controls=c, banked=ok, gate_why=why,
               ft90_legs=int(round(c["ft90_pct"] / 100.0 * c["n"])) if c["n"] else 0,
               ft90_needed=math.ceil(REF17["ft90_pct"] / 100.0 * c["n"] - 1e-9) if c["n"] else 0)
    print(f"{label}: net={c['net']:+,.2f} n={c['n']} FT90={c['ft90_pct']} "
          f"placebo={c['placebo']['net']:+,.2f} banked={ok} why={why}")
    return res

def report(res, sref):
    ok_s, why_s = gate(res["controls"], sref)
    ok_18, why_18 = gate(res["controls"], V18REF)
    res["gate_vs_stack"] = dict(passed=ok_s, failed=why_s)
    res["gate_vs_v18"] = dict(passed=ok_18, failed=why_18)
    print(f"   -> vs flagged stack: pass={ok_s} {why_s}; vs v18 (displacement): pass={ok_18} {why_18}")
    return res

def main():
    sref = stack_ref()
    gen = generate_r4()
    results = {}
    results["C102"] = report(judge_stack("Cycle 102 WS6 v18 x NS3 geometry T90L65G175",
                                         ns3_filter=GDGU, ns3_params=GEO), sref)
    results["C103"] = report(judge_transform("Cycle 103 WS6 v18 x WS4 transform (DTE>=14 stop-65)",
                                             ns3_filter=GDGU), sref)
    results["C104"] = report(judge_stack("Cycle 104 WS6 NS3 GD+GU & premium<400 stack",
                                         ns3_filter=lambda l: GDGU(l) and l["_ep"] is not None and l["_ep"] < 400.0), sref)
    results["C105"] = report(judge_stack("Cycle 105 WS6 NS3 GD+GU & DTE<=7 stack",
                                         ns3_filter=lambda l: GDGU(l) and l["_dte"] <= 7), sref)
    results["C106"] = report(judge_stack("Cycle 106 WS6 NS3 GD & premium<400 stack",
                                         ns3_filter=lambda l: l["_subleg"] == "NS3-GD" and l["_ep"] is not None and l["_ep"] < 400.0), sref)
    cyc = 107
    for cell in ("S3F", "S3G", "S3J"):
        results[f"C{cyc}"] = report(judge_stack(f"Cycle {cyc} WS6 v18 + {cell}",
                                                ns3_filter=GDGU, extra_families=[gen[cell]]), sref)
        cyc += 1
    results["C110"] = report(judge_stack("Cycle 110 WS6 NS3 premium<400 & DTE<=7 stack",
                                         ns3_filter=lambda l: l["_ep"] is not None and l["_ep"] < 400.0 and l["_dte"] <= 7), sref)
    results["C111"] = report(judge_stack("Cycle 111 WS6 NS3 GD+GU & premium<400 & DTE<=7 stack",
                                         ns3_filter=lambda l: GDGU(l) and l["_ep"] is not None and l["_ep"] < 400.0 and l["_dte"] <= 7), sref)
    (TR / "bank_r4_ws6_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r4_ws6_results.json")

if __name__ == "__main__":
    main()
