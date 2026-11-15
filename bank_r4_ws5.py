#!/usr/bin/env python3
"""ROUND 4 WS5 (Cycles 98-101): entry-state features on the flagged stack.
Frozen definitions (bank_engine_frozen.md ROUND 4 appendix): range30 =
spot high-low over bars with time < 09:45; trailMed = median of range30
over the prior 20 trading days (>=10 required); gap% = (open - prev
close)/prev close; tercile cuts T1 <= -0.210%, T3 > +0.139% (asserted
against the computed distribution). Legs entering before 09:45 are exempt
from the range condition; undefined features admit unconditionally."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import gate
from bank_r4_core import judge_stack, stack_ref
from bank_r3_setups import SPOT, DAILY, DAYS

TR = Path.home() / "workspace/trading"

R30 = {}
for d in DAYS:
    b = SPOT[(SPOT["date"] == d) & (SPOT["time"] < "09:45")]
    R30[d] = float(b["high"].max() - b["low"].min()) if len(b) else None
TMED, GAP = {}, {}
for i, d in enumerate(DAYS):
    prior = [R30[x] for x in DAYS[max(0, i - 20):i] if R30[x] is not None]
    TMED[d] = float(np.median(prior)) if len(prior) >= 10 else None
    if i >= 1:
        pc = float(DAILY[DAYS[i - 1]]["close"])
        GAP[d] = (float(DAILY[d]["open"]) - pc) / pc * 100.0
gaps = sorted(GAP.values())
q1, q2 = float(np.quantile(gaps, 1 / 3)), float(np.quantile(gaps, 2 / 3))
print(f"gap terciles computed: T1 <= {q1:+.3f}%  T3 > {q2:+.3f}%  (frozen: -0.210 / +0.139)")
assert abs(q1 - (-0.210)) < 0.02 and abs(q2 - 0.139) < 0.02, "tercile cuts do not match the frozen diagnosis"

def f_range_le(row):
    d = row["date"]
    if row["entry_time"] < "09:45" or R30.get(d) is None or TMED.get(d) is None: return True
    return R30[d] <= TMED[d]

def f_range_gt(row):
    d = row["date"]
    if row["entry_time"] < "09:45" or R30.get(d) is None or TMED.get(d) is None: return True
    return R30[d] > TMED[d]

def f_no_gap_t3(row):
    g = GAP.get(row["date"])
    return True if g is None else g <= q2

def f_no_gap_t1(row):
    g = GAP.get(row["date"])
    return True if g is None else g > q1

VARIANTS = [
    ("range30<=trailMed only", f_range_le),
    ("range30>trailMed only", f_range_gt),
    ("drop gap-T3 dates", f_no_gap_t3),
    ("drop gap-T1 dates", f_no_gap_t1),
]

def main():
    sref = stack_ref()
    results = {}
    cyc = 98
    for name, pred in VARIANTS:
        r = judge_stack(f"Cycle {cyc} WS5 stack filter [{name}]", stack_filter=pred)
        ok_s, why_s = gate(r["controls"], sref)
        r["gate_vs_stack"] = dict(passed=ok_s, failed=why_s)
        print(f"   -> vs flagged stack: pass={ok_s} why={why_s}")
        results[name] = dict(cycle=cyc, **r)
        cyc += 1
    (TR / "bank_r4_ws5_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r4_ws5_results.json")

if __name__ == "__main__":
    main()
