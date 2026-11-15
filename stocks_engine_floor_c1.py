#!/usr/bin/env python3
"""FLOOR CYCLE 1 — N4-V3 |move by 09:30| >= 3.0% cap at whole-book level.
Frozen in stocks_engine_frozen.md BEFORE this run (2026-11-02).
Incumbent: v3 C16 book. Full session gate in the same run.
"""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, scorecard, cells, n4_move, gate_eval

WS = "/home/hatch/workspace/trading"
b25 = load("stocks_engine_v3_c16_book2025_trades.csv")
b26 = load("stocks_engine_v3_c16_book2026_trades.csv")
base = {2025: scorecard(b25, 2025), 2026: scorecard(b26, 2026)}
base_cells = {2025: cells(b25)[0], 2026: cells(b26)[0]}

# attach moves to every N4-V3 row; timing audit: entries must be 09:35
def attach(rows):
    out, missing, timing_bad = [], 0, 0
    for t in rows:
        if t["comp"] != "N4-V3":
            out.append(t); continue
        if t["entry_time"] != "09:35": timing_bad += 1
        mv = n4_move(t["stock"], t["date"])
        if mv is None: missing += 1
        out.append({**t, "move": mv})
    return out, missing, timing_bad

a25, miss25, tb25 = attach(b25)
a26, miss26, tb26 = attach(b26)
print(f"moves attached: 2025 missing {miss25}, 2026 missing {miss26}; timing violations {tb25 + tb26}")
assert miss25 == 0 and miss26 == 0, "DATA GAP: an N4 row has no computable move — stop, do not guess"

def n4_rows(rows): return [t for t in rows if t["comp"] == "N4-V3"]

for yr, rows in ((2025, a25), (2026, a26)):
    buckets = {}
    for lo, hi, name in ((1, 2, "1-2%"), (2, 3, "2-3%"), (3, 99, ">=3%")):
        sel = [t for t in n4_rows(rows) if lo <= abs(t["move"]) < hi]
        buckets[name] = (len(sel), round(sum(t["net"] for t in sel), 2))
    print(f"{yr} N4 buckets (in-book): {buckets}; N4 total {len(n4_rows(rows))} tr / "
          f"{round(sum(t['net'] for t in n4_rows(rows)), 2):+.2f}")

def drop(rows, pred):
    kept = [t for t in rows if not (t["comp"] == "N4-V3" and pred(t))]
    dropped = [t for t in rows if t["comp"] == "N4-V3" and pred(t)]
    return kept, dropped

v25, d25 = drop(a25, lambda t: abs(t["move"]) >= 3.0)
v26, d26 = drop(a26, lambda t: abs(t["move"]) >= 3.0)
print(f"cap drops: 2025 {len(d25)} tr / {round(sum(t['net'] for t in d25), 2):+.2f} | "
      f"2026 {len(d26)} tr / {round(sum(t['net'] for t in d26), 2):+.2f}")

var = {2025: scorecard(v25, 2025), 2026: scorecard(v26, 2026)}
var_cells = {2025: cells(v25)[0], 2026: cells(v26)[0]}
# independent re-sum: variant == baseline - dropped, per year
for yr, varr, basec, dropped in ((2025, v25, base[2025], d25), (2026, v26, base[2026], d26)):
    direct = round(sum(t["net"] for t in varr), 2)
    via = round(basec["total"] - sum(t["net"] for t in dropped), 2)
    assert direct == via, f"re-sum mismatch {yr}: {direct} vs {via}"
print("RE-SUM: variant totals exact both ways, both years.")

# placebos: (A) skip 1<=|move|<2 bucket; (B) chronological first-N skip per year
pA25, _ = drop(a25, lambda t: 1 <= abs(t["move"]) < 2)
pA26, _ = drop(a26, lambda t: 1 <= abs(t["move"]) < 2)
def chrono_skip(rows, n):
    n4 = sorted([t for t in rows if t["comp"] == "N4-V3"], key=lambda t: (t["date"], t["stock"]))
    kill = {(t["date"], t["stock"], t["dir"], t["entry_time"]) for t in n4[:n]}
    return [t for t in rows if not (t["comp"] == "N4-V3" and (t["date"], t["stock"], t["dir"], t["entry_time"]) in kill)]
pB25 = chrono_skip(a25, len(d25)); pB26 = chrono_skip(a26, len(d26))
pA_comb = round(sum(t["net"] for t in pA25) + sum(t["net"] for t in pA26), 2)
pB_comb = round(sum(t["net"] for t in pB25) + sum(t["net"] for t in pB26), 2)
print(f"placebos combined: A (skip 1-2% bucket) {pA_comb:+.2f} | B (chrono first-N) {pB_comb:+.2f}")

verdict, legs, sums = gate_eval(base, var, base_cells, var_cells, [pA_comb, pB_comb], tb25 + tb26)
print("GATE:", json.dumps(legs, indent=1))
print(f"combined {sums['base_combined']:+.2f} -> {sums['variant_combined']:+.2f}")
for yr in (2025, 2026):
    print(f"{yr}: total {base[yr]['total']:+.2f} -> {var[yr]['total']:+.2f} | Jan-Oct "
          f"{base[yr]['jan_oct_total']:+.2f} -> {var[yr]['jan_oct_total']:+.2f} | ex-top3 "
          f"{base[yr]['ex_top3_stocks']:+.2f} -> {var[yr]['ex_top3_stocks']:+.2f} | cells {base_cells[yr]} -> {var_cells[yr]}")
print("VERDICT:", "BANK" if verdict else "REJECT")

res = {"cycle": "FLOOR-1", "fix": "N4-V3 |move by 09:30| >= 3.0% cap, whole-book (C16 incumbent)",
       "dropped": {"2025": [(t["date"], t["stock"], t["dir"], t["move"], t["net"]) for t in d25],
                   "2026": [(t["date"], t["stock"], t["dir"], t["move"], t["net"]) for t in d26]},
       "base": base, "variant": var, "base_cells": base_cells, "variant_cells": var_cells,
       "placebos_combined": {"A_skip_1_2_bucket": pA_comb, "B_chrono_firstN": pB_comb},
       "legs": legs, "sums": sums, "verdict": "BANK" if verdict else "REJECT"}
json.dump(res, open(f"{WS}/stocks_engine_floor_c1_result.json", "w"), indent=1)
if verdict:
    import csv as _csv
    for yr, rows in ((2025, v25), (2026, v26)):
        with open(f"{WS}/stocks_engine_floor_c1_book{yr}_trades.csv", "w", newline="") as f:
            w = _csv.writer(f); w.writerow(["comp", "date", "stock", "dir", "entry_time", "net"])
            for t in rows: w.writerow([t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"], f"{t['net']:.2f}"])
    print("WROTE banked book dumps stocks_engine_floor_c1_book{2025,2026}_trades.csv")
