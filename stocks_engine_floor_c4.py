#!/usr/bin/env python3
"""FLOOR CYCLE 4 — deletion of N4-V3 x HDFCBANK x LONG (3 tr, 2025, -836.12).
Frozen before scoring. Incumbent: FLOOR-C2 book. Full session gate same run.
"""
import json, sys, csv as _csv
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, scorecard, cells, n4_move, gate_eval

WS = "/home/hatch/workspace/trading"
b25 = load("stocks_engine_floor_c2_book2025_trades.csv")
b26 = load("stocks_engine_floor_c2_book2026_trades.csv")
base = {2025: scorecard(b25, 2025), 2026: scorecard(b26, 2026)}
base_cells = {2025: cells(b25)[0], 2026: cells(b26)[0]}

def is_slice(t): return t["comp"] == "N4-V3" and t["stock"] == "HDFCBANK" and t["dir"] == "LONG"
v25 = [t for t in b25 if not is_slice(t)]
d25 = [t for t in b25 if is_slice(t)]
v26 = list(b26)
print(f"slice: {len(d25)} tr / {round(sum(t['net'] for t in d25), 2):+.2f} "
      f"({[(t['date'], t['net']) for t in d25]})")
timing_bad = sum(1 for t in d25 if t["entry_time"] != "09:35")

var = {2025: scorecard(v25, 2025), 2026: scorecard(v26, 2026)}
var_cells = {2025: cells(v25)[0], 2026: cells(v26)[0]}
assert round(sum(t["net"] for t in v25), 2) == round(base[2025]["total"] - sum(t["net"] for t in d25), 2)
print("RE-SUM exact.")

n4_25 = sorted([t for t in b25 if t["comp"] == "N4-V3"], key=lambda t: (t["date"], t["stock"]))
killA = {(t["date"], t["stock"], t["dir"], t["entry_time"]) for t in n4_25[:3]}
pA = [t for t in b25 if (t["date"], t["stock"], t["dir"], t["entry_time"]) not in killA]
by_move = sorted(n4_25, key=lambda t: -abs(n4_move(t["stock"], t["date"])))[:3]
killB = {(t["date"], t["stock"], t["dir"], t["entry_time"]) for t in by_move}
pB = [t for t in b25 if (t["date"], t["stock"], t["dir"], t["entry_time"]) not in killB]
base26_tot = base[2026]["total"]
pA_comb = round(sum(t["net"] for t in pA) + base26_tot, 2)
pB_comb = round(sum(t["net"] for t in pB) + base26_tot, 2)
print(f"placebos combined: A (chrono first-3 N4-2025) {pA_comb:+.2f} | B (largest-|move| 3) {pB_comb:+.2f}")

verdict, legs, sums = gate_eval(base, var, base_cells, var_cells, [pA_comb, pB_comb], timing_bad)
print("GATE:", json.dumps(legs, indent=1))
print(f"combined {sums['base_combined']:+.2f} -> {sums['variant_combined']:+.2f}")
for yr in (2025, 2026):
    print(f"{yr}: total {base[yr]['total']:+.2f} -> {var[yr]['total']:+.2f} | Jan-Oct "
          f"{base[yr]['jan_oct_total']:+.2f} -> {var[yr]['jan_oct_total']:+.2f} | ex-top3 "
          f"{base[yr]['ex_top3_stocks']:+.2f} -> {var[yr]['ex_top3_stocks']:+.2f} | cells {base_cells[yr]} -> {var_cells[yr]}")
print("Jul 2025:", base[2025]["months"].get("2025-07"), "->", var[2025]["months"].get("2025-07"))
print("VERDICT:", "BANK" if verdict else "REJECT")

res = {"cycle": "FLOOR-4", "fix": "Delete N4-V3 x HDFCBANK x LONG (3 tr, 2025)",
       "dropped": [(t["date"], t["stock"], t["dir"], t["net"]) for t in d25],
       "base": base, "variant": var, "base_cells": base_cells, "variant_cells": var_cells,
       "placebos_combined": {"A_chrono_first3": pA_comb, "B_largest_move3": pB_comb},
       "legs": legs, "sums": sums, "verdict": "BANK" if verdict else "REJECT"}
json.dump(res, open(f"{WS}/stocks_engine_floor_c4_result.json", "w"), indent=1)
if verdict:
    for yr, rows in ((2025, v25), (2026, v26)):
        with open(f"{WS}/stocks_engine_floor_c4_book{yr}_trades.csv", "w", newline="") as f:
            w = _csv.writer(f); w.writerow(["comp", "date", "stock", "dir", "entry_time", "net"])
            for t in rows: w.writerow([t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"], f"{t['net']:.2f}"])
    print("WROTE banked book dumps stocks_engine_floor_c4_book{2025,2026}_trades.csv")
