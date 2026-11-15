#!/usr/bin/env python3
"""ROUND 4 WS2 (Cycles 82-88): NS3 admission refinement. Seven frozen
subsets (bank_engine_frozen.md ROUND 4 appendix), one axis at a time,
applied to NS3 candidates BEFORE admission; each gated as a full stack
variant vs v17, and also reported vs the flagged stack's controls."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import gate
from bank_r4_core import judge_stack, stack_ref

TR = Path.home() / "workspace/trading"
SUBSETS = [
    ("premium<400", lambda l: l["_ep"] is not None and l["_ep"] < 400.0),
    ("premium>=550", lambda l: l["_ep"] is not None and l["_ep"] >= 550.0),
    ("DTE>=1", lambda l: l["_dte"] >= 1),
    ("DTE<=7", lambda l: l["_dte"] <= 7),
    ("DTE>7", lambda l: l["_dte"] > 7),
    ("source GD only", lambda l: l["_subleg"] == "NS3-GD"),
    ("source GD+GU", lambda l: l["_subleg"] in ("NS3-GD", "NS3-GU")),
]

def main():
    sref = stack_ref()
    results = {}
    cyc = 82
    for name, pred in SUBSETS:
        r = judge_stack(f"Cycle {cyc} WS2 NS3 subset [{name}] stack", ns3_filter=pred)
        ok_s, why_s = gate(r["controls"], sref)
        r["gate_vs_stack"] = dict(passed=ok_s, failed=why_s)
        print(f"   -> vs flagged stack: pass={ok_s} why={why_s}")
        results[name] = dict(cycle=cyc, **r)
        cyc += 1
    (TR / "bank_r4_ws2_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r4_ws2_results.json")

if __name__ == "__main__":
    main()
