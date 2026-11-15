"""Independent re-sum for BANK v22 PHASE 2: reads ONLY the written CSVs
and the frozen phase-1 trades file, recomputes every headline, and
compares with bank_v22_phase2_results.json."""
import json, csv
from collections import defaultdict

TR = "/home/hatch/workspace/trading"
res = json.load(open(f"{TR}/bank_v22_phase2_results.json"))
ok = True

def check(name, got, want):
    global ok
    good = abs(got - want) < 0.01
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {name}: file {got:.2f} vs json {want:.2f}")

inc = list(csv.DictReader(open(f"{TR}/bank_v22_phase2_increments.csv")))
sets = defaultdict(list)
for r in inc:
    sets[r["set"]].append(float(r["net_inr"]))

for setname, bookname in [("A_reentry", "A"), ("A_shift60", "A_shift60"),
                          ("B_sleeve", "B_standalone"),
                          ("B_sleeve_combined", "B_combined_set"),
                          ("B_flip", "B_flip")]:
    check(f"{bookname} total", sum(sets[setname]), res["books"][bookname]["total"])
    check(f"{bookname} legs", len(sets[setname]), res["books"][bookname]["legs"])

base = list(csv.DictReader(open(f"{TR}/bank_v22_phase1_trades.csv")))
base_tot = sum(float(r["net_inr"]) for r in base)
check("base total", base_tot, res["books"]["base"]["total"])
check("base+A total", base_tot + sum(sets["A_reentry"]),
      res["books"]["base+A"]["total"])
comb_file = list(csv.DictReader(open(f"{TR}/bank_v22_phase2_trades.csv")))
comb_tot = sum(float(r["net_inr"]) for r in comb_file)
check("combined (trades.csv) total", comb_tot, res["books"]["combined"]["total"])
check("combined legs", len(comb_file), res["books"]["combined"]["legs"])
check("combined = base+A+B_comb", base_tot + sum(sets["A_reentry"]) + sum(sets["B_sleeve_combined"]),
      res["books"]["combined"]["total"])
months = defaultdict(float)
for r in comb_file:
    months[r["date"][:7]] += float(r["net_inr"])
for m, v in sorted(months.items()):
    check(f"combined month {m}", round(v, 2), res["books"]["combined"]["months"][m])
# A decomposition: stops + targets + square-offs must equal the A total
a_rows = [r for r in inc if r["set"] == "A_reentry"]
by_reason = defaultdict(float)
for r in a_rows:
    by_reason[r["exit_reason"]] += float(r["net_inr"])
check("A stop sum", by_reason["stop"], -8600.0)
check("A target sum", by_reason["target"], 14880.0)
print("A exit-reason sums:", dict(by_reason))
print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
