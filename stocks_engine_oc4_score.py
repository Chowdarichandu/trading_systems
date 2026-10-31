#!/usr/bin/env python3
"""ENGINE OC-4 STEP 3: score the frozen fix OC-4-F4S080 (F4 stop
-0.65% -> -0.80%, target +1.50% unchanged) on the full Jan-Oct
union. Anchors: (A) T150/S065 rebuild == stocks_engine_oc3_f4t150
_trades.csv exactly; (B) filtered T150/S065 union == current state
table (+112,101.53 / Oct +48,138.22) before the fix is judged.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, datetime, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py")
sys.argv = _argv
H1 = M2F.H1

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]

H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)

def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"] - a0["trades"],
             "violations": M2F._AUDIT["violations"] - a0["violations"]}
    return raw, audit

def filt_f4(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"])}
            for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}

key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])

# --- Anchor A: T150/S065 rebuild == oc3 dump ---
raw150, aud150 = build_f4(1.50, 0.65)
dump = rd("stocks_engine_oc3_f4t150_trades.csv")
a_ok = sorted(key(t) for t in raw150) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S065 rebuild == oc3 dump:", a_ok,
      f"| rebuild {len(raw150)} tr vs dump {len(dump)} tr | audit: {aud150}")

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
STATE = {"2026-01": 13665.48, "2026-02": -1660.11, "2026-03": 9281.57, "2026-04": -3324.69,
         "2026-05": 28938.33, "2026-06": -473.22, "2026-07": 2141.15, "2026-08": 382.10,
         "2026-09": 15012.70, "2026-10": 48138.22}
f4_150 = filt_f4(raw150)
base_book = inv + n4 + p2f + f4_150
bt, _ = mt(base_book)
b_ok = bt == STATE and round(sum(t["net"] for t in base_book), 2) == 112101.53
print("ANCHOR B: filtered T150/S065 union == state table:", b_ok,
      "| trades:", len(base_book), "| total:", round(sum(t['net'] for t in base_book), 2))

# --- Score the fix ---
raw_new, aud_new = build_f4(1.50, 0.80)
f4_new = filt_f4(raw_new)
new_book = inv + n4 + p2f + f4_new
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
f4n_oct = round(sum(t["net"] for t in f4_new if t["date"].startswith("2026-10")), 2)
f4o_oct = round(sum(t["net"] for t in f4_150 if t["date"].startswith("2026-10")), 2)
print(f"\nF4 component: S065 {len(f4_150)} tr Oct={f4o_oct} -> S080 {len(f4_new)} tr Oct={f4n_oct} | audit S080: {aud_new}")
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} {round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {112101.53:>10.2f} {tot_new:>10.2f} {round(tot_new-112101.53,2):>10.2f} {len(new_book):>7}")

print("\n=== ACCEPTANCE LEGS (frozen) ===")
l1 = nt["2026-10"] > 48138.22
l2 = tot_new >= 112101.53
l3 = all(v >= -12000 for v in nt.values())
bad4 = {k: round(nt.get(k, 0.0) - v, 2) for k, v in STATE.items() if v > 0 and nt.get(k, 0.0) - v < -5000}
l4 = not bad4
bad5 = {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in ["2026-02", "2026-04", "2026-06"] if nt.get(k, 0.0) - STATE[k] < -2000}
l5 = not bad5
l6 = aud_new["violations"] == 0
print("1 October rises:", nt["2026-10"], "> 48138.22 ->", l1, "| >= 50000 ->", nt["2026-10"] >= 50000,
      "| residual gap:", round(50000 - nt["2026-10"], 2))
print("2 total does not fall:", tot_new, ">= 112101.53 ->", l2)
print("3 no month < -12000 ->", l3, "| min:", min(nt.values()))
print("4 positive months losing >5000:", bad4 or "none", "->", l4)
print("5 red months deepened >2000:", bad5 or "none", "->", l5)
print("6 audit clean on new build ->", l6, aud_new)
banked = all([a_ok, b_ok, l1, l2, l3, l4, l5, l6])
print("BANKED:", banked)

with open(f"{BASE}/stocks_engine_oc4_f4s080_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(raw_new[0].keys())); w.writeheader()
    for t in sorted(raw_new, key=lambda x: (x["date"], x["symbol"])): w.writerow(t)
json.dump({"anchorA_ok": a_ok, "anchorB_ok": b_ok, "new_month_table": nt,
           "new_total": tot_new, "new_trades": len(new_book), "f4_s080_oct": f4n_oct,
           "banked": banked, "legs": {"l1_oct_rises": l1, "l2_total": l2, "l3_floor": l3,
           "l4_pos_months": l4, "l5_red": l5, "l6_audit": l6},
           "audit150": aud150, "audit_new": aud_new},
          open(f"{BASE}/stocks_engine_oc4_result.json", "w"), indent=1)
print("wrote stocks_engine_oc4_result.json + stocks_engine_oc4_f4s080_trades.csv")
