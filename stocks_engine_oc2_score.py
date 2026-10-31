#!/usr/bin/env python3
"""ENGINE OC-2 STEP 3: score union with the frozen fix (F4 excludes
setup3_bounce_rejection). Component dumps already audited upstream;
anchors re-verified here. Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, datetime, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("M1", "/home/hatch/workspace/trading/stocks_M1.py")
M1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M1)
BASE = "/home/hatch/workspace/trading"
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
f4_all, f4_fix = [], []
for r in rd("stocks_M2_F4_trades.csv"):
    if wk(r["date"]): continue
    tr = {"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
    f4_all.append(tr)
    if r["setup"] != "setup3_bounce_rejection": f4_fix.append(tr)

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}

base_book = inv + n4 + p2f + f4_all
new_book = inv + n4 + p2f + f4_fix
old_t, _ = mt(base_book); new_t, new_c = mt(new_book)
STATE = {"2026-01": 15850.19, "2026-02": -2759.77, "2026-03": 9953.85, "2026-04": -7708.27,
         "2026-05": 21766.53, "2026-06": -2096.96, "2026-07": 2151.71, "2026-08": 1144.98,
         "2026-09": 16260.35, "2026-10": 43011.62}
print("pre-fix anchor month table == state table:", old_t == STATE,
      "| trades:", len(base_book), "| total:", round(sum(t['net'] for t in base_book), 2))
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
tot_old = tot_new = 0.0
for k in sorted(STATE):
    d = round(new_t.get(k, 0.0) - STATE[k], 2)
    tot_old += STATE[k]; tot_new += new_t.get(k, 0.0)
    print(f"{k:8} {STATE[k]:>10.2f} {new_t.get(k,0.0):>10.2f} {d:>10.2f} {new_c.get(k,0):>7}")
print(f"{'TOTAL':8} {round(tot_old,2):>10.2f} {round(tot_new,2):>10.2f} {round(tot_new-tot_old,2):>10.2f} {len(new_book):>7}")
print("\n=== ACCEPTANCE LEGS ===")
print("1 October rises:", new_t["2026-10"], "> 43011.62 ->", new_t["2026-10"] > 43011.62,
      "| reaches 50000 ->", new_t["2026-10"] >= 50000, "| residual gap:", round(50000 - new_t["2026-10"], 2))
print("2 total does not fall:", round(tot_new, 2), ">= 97574.23 ->", tot_new >= 97574.23)
print("3 no month < -12000 ->", all(v >= -12000 for v in new_t.values()), "| min:", min(new_t.values()))
bad4 = {k: round(new_t.get(k,0.0)-v,2) for k, v in STATE.items() if v > 0 and new_t.get(k,0.0)-v < -5000}
print("4 positive months losing >5000:", bad4 or "none", "->", not bad4)
bad5 = {k: round(new_t.get(k,0.0)-STATE[k],2) for k in ["2026-02","2026-04","2026-06"] if new_t.get(k,0.0)-STATE[k] < -2000}
print("5 red months deepened >2000:", bad5 or "none", "->", not bad5)
s3 = [t for t in f4_all if t not in f4_fix]
print("\nsetup3 trades removed:", len(f4_all) - len(f4_fix), "net removed:", round(sum(t['net'] for t in f4_all) - sum(t['net'] for t in f4_fix), 2))
json.dump({"new_month_table": new_t, "new_total": round(tot_new, 2), "new_trades": len(new_book)},
          open(f"{BASE}/stocks_engine_oc2_result.json", "w"), indent=1)
print("wrote stocks_engine_oc2_result.json")
