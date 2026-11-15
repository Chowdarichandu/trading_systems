#!/usr/bin/env python3
"""ROUND 4 WS3 (Cycles 89+): Setup-3 completion cells S3-F..S3-J.
Standalone first (v17 + cell as the only add-on family); any cell whose
family net is positive is then gated inside the flagged stack (admitted
after S3-D). Gate vs v17; in-stack also reported vs the flagged stack."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import gate
from bank_r4_core import judge_stack, stack_ref
from bank_r4_setups import generate_r4

TR = Path.home() / "workspace/trading"

def main():
    gen = generate_r4()
    sref = stack_ref()
    results = {}
    cyc = 89
    positives = []
    for cell in ("S3F", "S3G", "S3H", "S3I", "S3J"):
        legs = gen[cell]
        r = judge_stack(f"Cycle {cyc} WS3 {cell} standalone (v17+{cell})",
                        ns3_filter=lambda l: False, include_s3=False,
                        extra_families=[legs])
        fam = [d for d in r["detail"] if d["family"] == "EXTRA0"]
        results[f"{cell}_standalone"] = dict(cycle=cyc, **r)
        if fam and fam[0]["net"] > 0:
            positives.append((cell, legs, fam[0]["net"]))
        cyc += 1
    for cell, legs, fnet in positives:
        r = judge_stack(f"Cycle {cyc} WS3 {cell} in flagged stack (family net standalone {fnet:+,.2f})",
                        extra_families=[legs])
        ok_s, why_s = gate(r["controls"], sref)
        r["gate_vs_stack"] = dict(passed=ok_s, failed=why_s)
        print(f"   -> vs flagged stack: pass={ok_s} why={why_s}")
        results[f"{cell}_instack"] = dict(cycle=cyc, **r)
        cyc += 1
    (TR / "bank_r4_ws3_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r4_ws3_results.json; positives:", [p[0] for p in positives])

if __name__ == "__main__":
    main()
