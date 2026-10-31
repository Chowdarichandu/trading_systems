#!/usr/bin/env python3
"""ENGINE JU-1 STEP 2: score frozen fix JU-1-P2F-HINDUNILVR (P2F 2.5%
no longer trades HINDUNILVR; all else identical incl. AU-1 ASTRAL
exclusion) on the full Jan-Oct union from audited dumps. Anchor:
ungated rebuild == state (+134,850.34 / 930 tr) first.
Paper, real Rs0, per 100 sh, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 12433.74, "2026-02": 4173.49, "2026-03": 20322.06,
         "2026-04": 50.73, "2026-05": 29377.98, "2026-06": -1233.49,
         "2026-07": 2096.63, "2026-08": 185.69, "2026-09": 17413.79,
         "2026-10": 50029.72}

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"]) and t["stock"] != "ASTRAL"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "net": float(r["net"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

base = inv + n4 + p2f + f4
bt, _ = mt(base)
anchor_ok = bt == STATE and round(sum(t["net"] for t in base), 2) == 134850.34 and len(base) == 930
print("ANCHOR:", anchor_ok, f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok

removed = [t for t in p2f if t["stock"] == "HINDUNILVR"]
print(f"removed P2F HINDUNILVR trades: {len(removed)} "
      f"net {round(sum(t['net'] for t in removed),2)} "
      f"-> {[(t['date'], t['net']) for t in removed]}")
new_book = inv + n4 + [t for t in p2f if t["stock"] != "HINDUNILVR"] + f4
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {134850.34:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-134850.34,2):>10.2f} {len(new_book):>7}")

print("\n=== ACCEPTANCE LEGS (frozen JU-1) ===")
l1 = nt["2026-07"] > STATE["2026-07"]
l2 = nt["2026-10"] >= 50000
l3 = nt["2026-09"] > 0 and nt["2026-08"] > 0
l4 = tot_new >= 134850.34
bad5 = {k: round(nt.get(k,0.0)-v,2) for k, v in STATE.items()
        if v > 0 and nt.get(k,0.0)-v < -5000}
l5 = not bad5
l6 = nt["2026-06"] - STATE["2026-06"] >= -2000
print("1 July rises:", nt["2026-07"], "> 2096.63 ->", l1, "| July > 0 ->", nt["2026-07"] > 0)
print("2 OCTOBER HARD FLOOR:", nt["2026-10"], ">= 50000 ->", l2)
print("3 Sep + Aug stay positive:", nt["2026-09"], nt["2026-08"], "->", l3)
print("4 total does not fall:", tot_new, ">= 134850.34 ->", l4)
print("5 positive months losing >5000:", bad5 or "none", "->", l5)
print("6 June deepens >2000:", round(nt["2026-06"]-STATE["2026-06"],2), "->", l6)
banked = all([l1, l2, l3, l4, l5, l6])
print("BANKED:", banked)

json.dump({"anchor_ok": anchor_ok, "fix": "JU-1-P2F-HINDUNILVR",
           "removed_trades": len(removed),
           "removed_net": round(sum(t["net"] for t in removed), 2),
           "removed_detail": [(t["date"], t["net"]) for t in removed],
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "legs": {"l1_jul_rises": l1, "l2_oct_floor": l2, "l3_sep_aug": l3,
                    "l4_total": l4, "l5_pos_months": l5, "l6_june": l6}},
          open(f"{BASE}/stocks_engine_ju1_result.json", "w"), indent=1)
print("wrote stocks_engine_ju1_result.json")
