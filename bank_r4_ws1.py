#!/usr/bin/env python3
"""ROUND 4 WS1 (Cycles 64-81): NS3's own exit geometry. 18 cells:
trig {75,90} x lock {40,50,65} x tgt2 {130,150,175}, stop -50, SQ 15:20,
uniform over every admitted NS3 leg. Assembly (a) v17+NS3@cell alone,
assembly (b) full stack with NS3@cell. Gate vs v17; (b) also gated vs the
flagged stack's controls for the report."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import gate
from bank_r4_core import judge_stack, stack_ref, REF17

TR = Path.home() / "workspace/trading"

def main():
    sref = stack_ref()
    results = {}
    cyc = 64
    for trig in (75.0, 90.0):
        for lock in (40.0, 50.0, 65.0):
            for tgt2 in (130.0, 150.0, 175.0):
                p = dict(stop=50.0, trig=trig, lock=lock, tgt2=tgt2)
                tag = f"T{int(trig)}L{int(lock)}G{int(tgt2)}"
                ra = judge_stack(f"Cycle {cyc} WS1 {tag} (a) v17+NS3@cell",
                                 ns3_params=p, include_s3=False)
                rb = judge_stack(f"Cycle {cyc} WS1 {tag} (b) stack+NS3@cell",
                                 ns3_params=p)
                ok_b_stack, why_b_stack = gate(rb["controls"], sref)
                rb["gate_vs_stack"] = dict(passed=ok_b_stack, failed=why_b_stack)
                print(f"   -> (b) vs flagged stack: pass={ok_b_stack} why={why_b_stack}")
                results[tag] = dict(cycle=cyc, params=p, assembly_a=ra, assembly_b=rb)
                cyc += 1
    (TR / "bank_r4_ws1_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r4_ws1_results.json")
    banked = [(t, r) for t, r in results.items()
              if r["assembly_a"]["banked"] or r["assembly_b"]["banked"]]
    print("BANKED cells:", [(t, r["assembly_b"]["controls"]["net"], r["assembly_b"]["controls"]["ft90_pct"]) for t, r in banked])

if __name__ == "__main__":
    main()
