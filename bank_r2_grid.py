#!/usr/bin/env python3
"""ROUND 2 Family 1 (Cycles 28-30): EXIT-GEOMETRY GRID on the fixed v14 legs.
stop {40,50,60} x trigger {75,90,105} x lock {none,50,75,90}; T2 frozen per
segment (330 lt400 / 180 ge400). Modes: A = lt400 only; B = ge400 (warm runner
params + cold S/T plain); AB = all segments. Every cell gets full controls
(placebo, timing audit, halves, month table, ex-top-3) and the banking gate
vs book v14. Results -> bank_r2_grid_results.json."""
import sys, json, copy
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import (build_fixed, controls, gate, rescore_keys, V14,
                          book_v4_legs)
from bank_engine_run2_cycle14 import stream_keys
from bank_engine_run2_cycle18 import anchored_states

legs = book_v4_legs()
lbk = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
keys = {0: stream_keys(delay=0), 6: stream_keys(delay=6)}
states = {0: anchored_states(delay=0), 6: anchored_states(delay=6)}

ref_rows, ref_nc = rescore_keys(keys[0], lbk, states[0], V14, delay=0)
ref_prows, ref_pnc = rescore_keys(keys[6], lbk, states[6], V14, delay=6)
REF = controls(ref_rows, ref_nc, lbk, ref_prows, ref_pnc)
assert REF["net"] == 104567.00 and REF["n"] == 82, REF["net"]
print(f"REF v14: net={REF['net']} ft90={REF['ft90_pct']} placebo={REF['placebo']['net']}")

LOCKS = [None, 50.0, 75.0, 90.0]
results = []
for mode in ("A", "B", "AB"):
    for S in (40.0, 50.0, 60.0):
        for T in (75.0, 90.0, 105.0):
            for L in LOCKS:
                p = copy.deepcopy(V14)
                cell_lt = dict(stop=S, trig=T, lock=L, tgt2=330.0)
                cell_gw = dict(stop=S, trig=T, lock=L, tgt2=180.0)
                cell_gc = dict(stop=S, trig=T, lock=None, tgt2=None)
                if mode in ("A", "AB"): p["lt400"] = cell_lt
                if mode in ("B", "AB"): p["ge400_warm"] = cell_gw; p["ge400_cold"] = cell_gc
                rows, nc = rescore_keys(keys[0], lbk, states[0], p, delay=0)
                prows, pnc = rescore_keys(keys[6], lbk, states[6], p, delay=6)
                c = controls(rows, nc, lbk, prows, pnc)
                ok, failed = gate(c, REF)  # re-sum leg runs only for banked cells below
                results.append(dict(mode=mode, stop=S, trig=T, lock=L,
                                    n=c["n"], net=c["net"], ft=c["ft_pct"], ft90=c["ft90_pct"],
                                    per_week=c["per_week_raw"], halves=c["halves"],
                                    jun=c["months"]["06"], jul=c["months"]["07"],
                                    placebo=c["placebo"]["net"], ex_top3=c["ex_top3_total"],
                                    reds=c["red_month_ends"], nc=c["not_computed"],
                                    viol=len(c["timing_violations"]),
                                    gate_pass=ok, gate_failed=failed))
passes = [r for r in results if r["gate_pass"]]
print(f"cells scored: {len(results)} | gate passes (pre-resum): {len(passes)}")
for r in sorted(results, key=lambda x: -x["net"])[:12]:
    print(f"  {r['mode']} S={r['stop']:.0f} T={r['trig']:.0f} L={r['lock']} net={r['net']} "
          f"ft90={r['ft90']} pl={r['placebo']} ex3={r['ex_top3']} pass={r['gate_pass']} "
          f"fail={r['gate_failed'][:2]}")
json.dump(dict(ref={k: REF[k] for k in ("n", "net", "ft_pct", "ft90_pct", "months",
                                        "halves", "placebo", "ex_top3_total")},
               cells=results),
          open("/home/hatch/workspace/trading/bank_r2_grid_results.json", "w"), indent=1)
print("saved bank_r2_grid_results.json")
