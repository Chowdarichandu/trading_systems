#!/usr/bin/env python3
"""PEAK LAB CYCLE 6 - DIAGNOSIS at Cycle-3 banked basis (F4 @ T150/S125, T=10:00).
Anchors: T150/S125 rebuild == cycle3 dump; union == peak table.
Plus: F4 direction split (LONG vs SHORT) at current S125 basis, October + full.
NO 09:45 build in this script - diagnosis only, before freeze.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1 = M2F.H1
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":9173.84,"2026-02":4939.87,"2026-03":21673.47,"2026-04":-632.4,
        "2026-05":26032.03,"2026-06":-817.99,"2026-07":1962.07,"2026-08":739.35,
        "2026-09":14970.43,"2026-10":53290.52}
assert M2F.T == "10:00", M2F.T
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw, aud = build_f4(1.50, 1.25)
dump = rd("stocks_peak_oct_cycle3_f4s125_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S125 @10:00 rebuild == cycle3 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")
inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
def filt(raw_):
    return [t for t in raw_ if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
f4 = filt(raw)
def mt(trades):
    m=defaultdict(float)
    for t in trades: m[t["date"][:7]]+=float(t["net"])
    return {k: round(v,2) for k,v in sorted(m.items())}
bt = mt(inv+n4+p2f+f4)
b_ok = bt == PEAK
tot = round(sum(float(t['net']) for t in inv+n4+p2f+f4),2)
print("ANCHOR B: union == peak table:", b_ok, "| trades", len(inv)+len(n4)+len(p2f)+len(f4), "| total", tot)
assert a_ok and b_ok and aud["violations"]==0

print("\n=== F4 direction split @ S125 basis (filtered book: non-weekend, minus setup3) ===")
split={}
for d in ["LONG","SHORT"]:
    all_=[t for t in f4 if t["dir"]==d]; oct_=[t for t in all_ if t["date"].startswith("2026-10")]
    def agg(rows):
        return {"n":len(rows),"net":round(sum(float(t['net']) for t in rows),2),
                "losers":sum(1 for t in rows if float(t['net'])<0),
                "loser_net":round(sum(float(t['net']) for t in rows if float(t['net'])<0),2),
                "winners":sum(1 for t in rows if float(t['net'])>=0)}
    split[d]={"full":agg(all_),"oct":agg(oct_)}
    mm=defaultdict(float)
    for t in all_: mm[t["date"][:7]]+=float(t["net"])
    split[d]["months"]={k:round(v,2) for k,v in sorted(mm.items())}
    print(f"{d}: full {split[d]['full']} | Oct {split[d]['oct']}")
    print(f"   months: {split[d]['months']}")
# also raw (incl setup3) direction split for completeness
split_raw={}
for d in ["LONG","SHORT"]:
    all_=[t for t in raw if t["dir"]==d]; oct_=[t for t in all_ if t["date"].startswith("2026-10")]
    split_raw[d]={"full_n":len(all_),"full_net":round(sum(float(t['net']) for t in all_),2),
                  "oct_n":len(oct_),"oct_net":round(sum(float(t['net']) for t in oct_),2)}
print("raw (incl setup3, pre-filter):", split_raw)
json.dump({"anchorA":a_ok,"anchorB":b_ok,"audit":aud,"total":tot,
           "f4_filtered_trades":len(f4),"dir_split_filtered":split,"dir_split_raw":split_raw},
          open(f"{BASE}/stocks_peak_oct_cycle6_diag.json","w"), indent=1)
print("\nwrote stocks_peak_oct_cycle6_diag.json")
