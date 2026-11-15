#!/usr/bin/env python3
"""ROUND 7 sanity (pre-cycle, unnumbered): reproduce v20 and v21 exactly
through bank_r6_core/bank_r7_core before any Round-7 candidate is scored.
Certification: every figure is produced by the audited causal pipeline
(causal-solo B2 pool, NS1 regenerated at causal entries, NS3 signal+5);
no Round 1-4 magnitude is cited."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r6_core as c6
from bank_r6_core import v20_ref
from bank_r7_core import v21_ref
from bank_r2_core import gate

r20 = v20_ref()
print(f"v20 reproduced: net={r20['net']:+,.2f} n={r20['n']} FT90={r20['ft90_pct']} "
      f"placebo={r20['placebo']['net']:+,.2f} nc={r20['not_computed']}")
assert abs(r20["net"] - 78250.50) < 0.005 and r20["n"] == 99, "v20 mismatch"

r21 = v21_ref()
print(f"v21 reproduced: net={r21['net']:+,.2f} n={r21['n']} FT90={r21['ft90_pct']} "
      f"freq={r21['per_week_raw']} placebo={r21['placebo']['net']:+,.2f} "
      f"ex_top3={r21['ex_top3_total']:+,.2f} nc={r21['not_computed']} "
      f"viol={len(r21['timing_violations'])}")
assert abs(r21["net"] - 83650.50) < 0.005 and r21["n"] == 99, "v21 mismatch"
ok, why = gate(r21, r20)
print(f"v21 gate vs v20: {ok} {why}")
assert ok and r21["ex_top3_total"] >= 0
print("SANITY PASS — v21 baseline certified for Round 7.")
