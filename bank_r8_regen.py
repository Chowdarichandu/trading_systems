#!/usr/bin/env python3
"""ROUND 8 Cycle 167 — regeneration verification of the Round-8 December
freeze (bank_engine_frozen.md, ROUND 8 block). The frozen specification's
construction is re-run through the audited causal pipeline
(bank_r7_core.v21_ref / assemble6 at the frozen parameters: causal-solo
B2 pool with Volrix regenerated -1.0%/cd15, NS1 regenerated at the frozen
cell room 1.5 / window 14:30, NS3 GD+GU @ stop -50/trig +90/lock +50/
tgt2 +150, S3 sequential admission, square-off 15:20) and the resulting
trades are written out and compared LEG-FOR-LEG against the trades of
record (bank_engine_r6_v21_trades.csv), with the full controls gate in
the same run (timing audit, delay-6 placebo, halves, month table,
ex-top-3, NOT_COMPUTED) and an independent re-sum from the written file.
Any mismatch is reported, never patched."""
import sys, csv, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r7_core import v21_ref, _V21
from bank_r2_core import write_trades

TR = Path.home() / "workspace/trading"
ref = v21_ref()
rows = _V21["rows"]
resum = write_trades(rows, str(TR / "bank_engine_r8_v21_regen_trades.csv"))

def load(name):
    return list(csv.DictReader(open(TR / name)))

old = load("bank_engine_r6_v21_trades.csv")
new = load("bank_engine_r8_v21_regen_trades.csv")
assert len(old) == len(new), f"leg count differs: record {len(old)} vs regen {len(new)}"
mism = []
for i, (a, b) in enumerate(zip(old, new)):
    for k in a:
        va, vb = a[k], b[k]
        try:
            same = abs(float(va) - float(vb)) < 0.005
        except ValueError:
            same = va == vb
        if not same:
            mism.append((i, a["date"], a["direction"], k, va, vb))
print(f"leg-for-leg: {len(old)} legs compared, mismatches = {len(mism)}")
for m in mism[:10]:
    print("  MISMATCH:", m)
print(f"controls: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']} "
      f"freq={ref['per_week_raw']} placebo={ref['placebo']['net']:+,.2f} "
      f"halves={ref['halves']} ex_top3={ref['ex_top3_total']:+,.2f} "
      f"NC={ref['not_computed']} timing_violations={len(ref['timing_violations'])}")
print(f"independent re-sum of written file: {resum}")
ok = (not mism and abs(ref["net"] - 83650.50) < 0.005 and ref["n"] == 99
      and ref["not_computed"] == 0 and len(ref["timing_violations"]) == 0
      and resum["n"] == 99 and abs(resum["net"] - 83650.50) < 0.005)
print("REGENERATION VERIFICATION:", "PASS" if ok else "FAIL")
(TR / "bank_r8_regen.json").write_text(json.dumps(
    dict(passed=ok, mismatches=mism, controls=ref, resum=resum), indent=1, default=str))
