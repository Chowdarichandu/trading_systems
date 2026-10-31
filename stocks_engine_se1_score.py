#!/usr/bin/env python3
"""ENGINE SE-1 STEP 3: score the frozen fix SE-1-F4R1 (F4 takes
only the first qualifying signal per stock-day; round-2 legs
dropped) on the full Jan-Oct union. Anchor: the ungated rebuild
from the same dumps must == state (+131,646.79 / 934 tr) first.
F4 round-1 trades are built identically with or without round-2,
so dropping leg=='round2' from the audited S080 dump is exactly
the gated F4 book. Paper, real Rs0, per 100 shares, Rs40/tr."""
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
         "2026-04": 50.73, "2026-05": 27844.38, "2026-06": -1233.49,
         "2026-07": 2096.63, "2026-08": -1484.26, "2026-09": 17413.79,
         "2026-10": 50029.72}

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
f4_all = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
           "net": float(r["net"]), "leg": r["leg"]}
          for r in rd("stocks_engine_oc4_f4s080_trades.csv")
          if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
f4_fix = [t for t in f4_all if t["leg"] != "round2"]
base3 = inv + n4 + p2f

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

base_book = base3 + f4_all
bt, _ = mt(base_book)
anchor_ok = bt == STATE and round(sum(t["net"] for t in base_book), 2) == 131646.79 \
    and len(base_book) == 934
print("ANCHOR: ungated rebuild == state table:", anchor_ok,
      f"| trades {len(base_book)} | total {round(sum(t['net'] for t in base_book), 2)}")
assert anchor_ok, "ANCHOR FAILED"

new_book = base3 + f4_fix
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k, 0.0):>10.2f} "
          f"{round(nt.get(k, 0.0) - STATE[k], 2):>10.2f} {nc.get(k, 0):>7}")
print(f"{'TOTAL':8} {131646.79:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new - 131646.79, 2):>10.2f} {len(new_book):>7}")

print("\n=== ACCEPTANCE LEGS (frozen SE-1) ===")
l1 = nt["2026-09"] > STATE["2026-09"]
l2 = nt["2026-10"] >= 50000
l3 = tot_new >= 131646.79
bad4 = {k: round(nt.get(k, 0.0) - v, 2) for k, v in STATE.items()
        if v > 0 and nt.get(k, 0.0) - v < -5000}
l4 = not bad4
bad5 = {k: round(nt.get(k, 0.0) - STATE[k], 2)
        for k in ["2026-06", "2026-08"] if nt.get(k, 0.0) - STATE[k] < -2000}
l5 = not bad5
print("1 September rises:", nt["2026-09"], "> 17413.79 ->", l1)
print("2 OCTOBER HARD FLOOR >= 50000:", nt["2026-10"], "->", l2)
print("3 total does not fall:", tot_new, ">= 131646.79 ->", l3)
print("4 positive months losing >5000:", bad4 or "none", "->", l4)
print("5 Jun/Aug deepened >2000:", bad5 or "none", "->", l5)
banked = all([l1, l2, l3, l4, l5])
print("BANKED:", banked,
      "| REJECTED on the October hard floor" if not l2 else "")

json.dump({"anchor_ok": anchor_ok, "fix": "SE-1-F4R1",
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "legs": {"l1_sep_rises": l1, "l2_oct_floor": l2,
                    "l3_total": l3, "l4_pos_months": l4, "l5_jun_aug": l5}},
          open(f"{BASE}/stocks_engine_se1_result.json", "w"), indent=1)
print("wrote stocks_engine_se1_result.json")
