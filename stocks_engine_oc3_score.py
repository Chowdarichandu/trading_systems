#!/usr/bin/env python3
"""ENGINE OC-3 STEP 3: score the frozen fix OC-3-F4T150 (F4 target
1.25% -> 1.50%, stop -0.65% unchanged) on the full Jan-Oct union.
Anchors: (A) M2 machinery rebuild at T125/S065 must reproduce
stocks_M2_F4_trades.csv exactly; (B) filtered T125 union must equal
the state month table (+107,227.76 / Oct +45,581.98) before the fix
is judged. Paper, real Rs0, per 100 shares, Rs40/tr."""
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

def build_f4(tp):
    M2F.TP, M2F.SP = tp, 0.65
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"] - a0["trades"],
             "violations": M2F._AUDIT["violations"] - a0["violations"]}
    return raw, audit

def filt_f4(raw):
    out = []
    for t in raw:
        if wk(t["date"]) or t["setup"] == "setup3_bounce_rejection": continue
        out.append({"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"])})
    return out

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}

# --- Anchor A: T125 rebuild == published dump ---
raw125, aud125 = build_f4(1.25)
dump = rd("stocks_M2_F4_trades.csv")
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
rebuild_keys = sorted(key(t) for t in raw125)
dump_keys = sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T125 rebuild == dump:", rebuild_keys == dump_keys,
      f"| rebuild {len(raw125)} tr / {round(sum(t['net'] for t in raw125),2)} vs dump {len(dump)} tr / "
      f"{round(sum(float(r['net']) for r in dump),2)} | audit: {aud125}")

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
STATE = {"2026-01": 14489.91, "2026-02": -1813.21, "2026-03": 13422.38, "2026-04": -7042.44,
         "2026-05": 26188.71, "2026-06": -2270.04, "2026-07": 2151.71, "2026-08": 864.98,
         "2026-09": 15653.78, "2026-10": 45581.98}
f4_125 = filt_f4(raw125)
base_book = inv + n4 + p2f + f4_125
bt, _ = mt(base_book)
print("ANCHOR B: filtered T125 union == state table:", bt == STATE,
      "| trades:", len(base_book), "| total:", round(sum(t['net'] for t in base_book), 2))

# --- Score the fix ---
raw150, aud150 = build_f4(1.50)
f4_150 = filt_f4(raw150)
new_book = inv + n4 + p2f + f4_150
nt, nc = mt(new_book)
tot_new = round(sum(t['net'] for t in new_book), 2)
f4_150_oct = round(sum(t['net'] for t in f4_150 if t["date"].startswith("2026-10")), 2)
f4_125_oct = round(sum(t['net'] for t in f4_125 if t["date"].startswith("2026-10")), 2)
print(f"\nF4 component: T125 {len(f4_125)} tr Oct={f4_125_oct} -> T150 {len(f4_150)} tr Oct={f4_150_oct} | audit T150: {aud150}")
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
tot_old = 0.0
for k in sorted(STATE):
    d = round(nt.get(k, 0.0) - STATE[k], 2); tot_old += STATE[k]
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} {d:>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {round(tot_old,2):>10.2f} {tot_new:>10.2f} {round(tot_new-tot_old,2):>10.2f} {len(new_book):>7}")

print("\n=== ACCEPTANCE LEGS (frozen) ===")
l1 = nt["2026-10"] > 45581.98
l2 = tot_new >= 107227.76
l3 = all(v >= -12000 for v in nt.values())
bad4 = {k: round(nt.get(k, 0.0) - v, 2) for k, v in STATE.items() if v > 0 and nt.get(k, 0.0) - v < -5000}
l4 = not bad4
bad5 = {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in ["2026-02", "2026-04", "2026-06"] if nt.get(k, 0.0) - STATE[k] < -2000}
l5 = not bad5
print("1 October rises:", nt["2026-10"], "> 45581.98 ->", l1, "| >= 50000 ->", nt["2026-10"] >= 50000,
      "| residual gap:", round(50000 - nt["2026-10"], 2))
print("2 total does not fall:", tot_new, ">= 107227.76 ->", l2)
print("3 no month < -12000 ->", l3, "| min:", min(nt.values()))
print("4 positive months losing >5000:", bad4 or "none", "->", l4)
print("5 red targets deepened >2000:", bad5 or "none", "->", l5)
print("AUDIT clean (both builds):", aud125["violations"] == 0 and aud150["violations"] == 0)
banked = all([l1, l2, l3, l4, l5, aud125["violations"] == 0, aud150["violations"] == 0])
print("BANKED:", banked)

with open(f"{BASE}/stocks_engine_oc3_f4t150_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(raw150[0].keys())); w.writeheader()
    for t in sorted(raw150, key=lambda x: (x["date"], x["symbol"])): w.writerow(t)
json.dump({"anchorA_ok": rebuild_keys == dump_keys, "anchorB_ok": bt == STATE,
           "new_month_table": nt, "new_total": tot_new, "new_trades": len(new_book),
           "f4_150_oct": f4_150_oct, "banked": banked,
           "legs": {"l1_oct_rises": l1, "l2_total": l2, "l3_floor": l3, "l4_pos_months": l4, "l5_red": l5},
           "audit125": aud125, "audit150": aud150},
          open(f"{BASE}/stocks_engine_oc3_result.json", "w"), indent=1)
print("wrote stocks_engine_oc3_result.json + stocks_engine_oc3_f4t150_trades.csv")
