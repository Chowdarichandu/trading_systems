#!/usr/bin/env python3
"""FLOOR CYCLE 2 — N4-V3 signed-move >= +3.0% skip (LONG over-extension cap).
Frozen in stocks_engine_frozen.md BEFORE this run. Incumbent: v3 C16 book
(Cycle 1 rejected; book unchanged). Full session gate in the same run.
"""
import json, sys, csv as _csv
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, scorecard, cells, n4_move, gate_eval

WS = "/home/hatch/workspace/trading"
b25 = load("stocks_engine_v3_c16_book2025_trades.csv")
b26 = load("stocks_engine_v3_c16_book2026_trades.csv")
base = {2025: scorecard(b25, 2025), 2026: scorecard(b26, 2026)}
base_cells = {2025: cells(b25)[0], 2026: cells(b26)[0]}

def attach(rows):
    out, timing_bad = [], 0
    for t in rows:
        if t["comp"] != "N4-V3": out.append(t); continue
        if t["entry_time"] != "09:35": timing_bad += 1
        out.append({**t, "move": n4_move(t["stock"], t["date"])})
    return out, timing_bad

a25, tb25 = attach(b25); a26, tb26 = attach(b26)
assert all(t.get("move") is not None for t in a25 + a26 if t["comp"] == "N4-V3")

def drop(rows, pred):
    kept = [t for t in rows if not (t["comp"] == "N4-V3" and pred(t))]
    dropped = [t for t in rows if t["comp"] == "N4-V3" and pred(t)]
    return kept, dropped

v25, d25 = drop(a25, lambda t: t["move"] >= 3.0)
v26, d26 = drop(a26, lambda t: t["move"] >= 3.0)
print(f"cap drops: 2025 {len(d25)} tr / {round(sum(t['net'] for t in d25), 2):+.2f} | "
      f"2026 {len(d26)} tr / {round(sum(t['net'] for t in d26), 2):+.2f}")
assert all(t["dir"] == "LONG" for t in d25 + d26), "signed >= +3.0% must be LONG-only"

var = {2025: scorecard(v25, 2025), 2026: scorecard(v26, 2026)}
var_cells = {2025: cells(v25)[0], 2026: cells(v26)[0]}
for yr, varr, dropped in ((2025, v25, d25), (2026, v26, d26)):
    direct = round(sum(t["net"] for t in varr), 2)
    via = round(base[yr]["total"] - sum(t["net"] for t in dropped), 2)
    assert direct == via, f"re-sum mismatch {yr}"
print("RE-SUM exact both ways, both years.")

pA25, _ = drop(a25, lambda t: t["move"] <= -3.0)
pA26, _ = drop(a26, lambda t: t["move"] <= -3.0)
def chrono_skip(rows, n):
    n4 = sorted([t for t in rows if t["comp"] == "N4-V3"], key=lambda t: (t["date"], t["stock"]))
    kill = {(t["date"], t["stock"], t["dir"], t["entry_time"]) for t in n4[:n]}
    return [t for t in rows if not (t["comp"] == "N4-V3" and (t["date"], t["stock"], t["dir"], t["entry_time"]) in kill)]
pB25 = chrono_skip(a25, len(d25)); pB26 = chrono_skip(a26, len(d26))
pA_comb = round(sum(t["net"] for t in pA25) + sum(t["net"] for t in pA26), 2)
pB_comb = round(sum(t["net"] for t in pB25) + sum(t["net"] for t in pB26), 2)
print(f"placebos combined: A (mirror, skip SHORT >=3%) {pA_comb:+.2f} | B (chrono first-N) {pB_comb:+.2f}")

verdict, legs, sums = gate_eval(base, var, base_cells, var_cells, [pA_comb, pB_comb], tb25 + tb26)
print("GATE:", json.dumps(legs, indent=1))
print(f"combined {sums['base_combined']:+.2f} -> {sums['variant_combined']:+.2f}")
for yr in (2025, 2026):
    print(f"{yr}: total {base[yr]['total']:+.2f} -> {var[yr]['total']:+.2f} | Jan-Oct "
          f"{base[yr]['jan_oct_total']:+.2f} -> {var[yr]['jan_oct_total']:+.2f} | ex-top3 "
          f"{base[yr]['ex_top3_stocks']:+.2f} -> {var[yr]['ex_top3_stocks']:+.2f} | cells {base_cells[yr]} -> {var_cells[yr]}")
print("VERDICT:", "BANK" if verdict else "REJECT")

res = {"cycle": "FLOOR-2", "fix": "N4-V3 skip signed move by 09:30 >= +3.0% (LONG over-extension cap)",
       "dropped": {"2025": [(t["date"], t["stock"], t["dir"], t["move"], t["net"]) for t in d25],
                   "2026": [(t["date"], t["stock"], t["dir"], t["move"], t["net"]) for t in d26]},
       "base": base, "variant": var, "base_cells": base_cells, "variant_cells": var_cells,
       "placebos_combined": {"A_mirror_skip_short": pA_comb, "B_chrono_firstN": pB_comb},
       "legs": legs, "sums": sums, "verdict": "BANK" if verdict else "REJECT"}
json.dump(res, open(f"{WS}/stocks_engine_floor_c2_result.json", "w"), indent=1)
if verdict:
    for yr, rows in ((2025, v25), (2026, v26)):
        with open(f"{WS}/stocks_engine_floor_c2_book{yr}_trades.csv", "w", newline="") as f:
            w = _csv.writer(f); w.writerow(["comp", "date", "stock", "dir", "entry_time", "net"])
            for t in rows: w.writerow([t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"], f"{t['net']:.2f}"])
    print("WROTE banked book dumps stocks_engine_floor_c2_book{2025,2026}_trades.csv")
