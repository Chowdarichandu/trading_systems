#!/usr/bin/env python3
"""ENGINE SAT-8 DIAG: re-derive F4 x HINDCOPPER x SHORT at the CURRENT
(post-SAT-7) book. Lesson 16: never trust the previous cycle's numbers.
Anchor: current-book rebuild == state (791 tr / +148,270.20 / month
table) asserted first. Deletion-only slices from the pre-audited F4
dump inherit timing validity. Paper, real Rs0, per 100 shares,
Rs40/trade, home 25."""
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

STATE = {"2026-01": 12021.03, "2026-02": 3611.69, "2026-03": 22623.60,
         "2026-04": 3736.26, "2026-05": 27838.61, "2026-06": 4287.51,
         "2026-07": 3196.63, "2026-08": 775.60, "2026-09": 19829.48,
         "2026-10": 50349.79}
STATE_TOTAL, STATE_TRADES = 148270.20, 791

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "net": float(r["net"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and r["leg"] != "round2"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
       and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")
       and not (r["symbol"] == "UNITDSPR" and r["dir"] == "SHORT")]

def mt(trades):
    m = defaultdict(float)
    for t in trades: m[t["date"][:7]] += t["net"]
    return {k: round(m[k], 2) for k in sorted(m)}

base = inv + n4 + p2f + f4
bt = mt(base)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in base), 2) == STATE_TOTAL
             and len(base) == STATE_TRADES)
print("ANCHOR (current book == state):", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok, "ANCHOR FAILED"

hc_all = [t for t in f4 if t["stock"] == "HINDCOPPER"]
hc_short = [t for t in hc_all if t["dir"] == "SHORT"]
hc_long = [t for t in hc_all if t["dir"] == "LONG"]
def summarise(ts, label):
    net = round(sum(t["net"] for t in ts), 2)
    w = sum(1 for t in ts if t["net"] > 0)
    mn = mt(ts)
    print(f"\n{label}: {len(ts)} trades, net {net}, winners {w}")
    for k in sorted(mn): print(f"   {k}: {mn[k]:>10.2f}")
    return net, mn
net_short, mn_short = summarise(hc_short, "F4 x HINDCOPPER x SHORT (re-derived, current book)")
net_long, _ = summarise(hc_long, "F4 x HINDCOPPER x LONG (kept half)")
for t in sorted(hc_short, key=lambda t: t["date"]):
    print(f"  SHORT {t['date']} {t['setup']:22} leg {t['leg']:8} net {t['net']:9.2f}")

aug_slice = mn_short.get("2026-08", 0.0)
oct_slice = mn_short.get("2026-10", 0.0)
print(f"\nAugust slice: {aug_slice} | October slice: {oct_slice} "
      f"(October headroom Rs349.79)")
print("\n=== COMPARE vs SAT-7 DIAG RECORD ===")
print("record: 12 tr / full -1,094.95 / 4 w / Aug -959.56 / Oct 0.00")
match = (len(hc_short) == 12 and net_short == -1094.95
         and aug_slice == -959.56 and oct_slice == 0.00
         and sum(1 for t in hc_short if t["net"] > 0) == 4)
print("MATCHES SAT-7 RECORD:", match)

json.dump({"anchor_ok": anchor_ok,
           "slice": {"trades": len(hc_short), "net": net_short,
                     "winners": sum(1 for t in hc_short if t["net"] > 0),
                     "month_nets": mn_short,
                     "august": aug_slice, "october": oct_slice},
           "long_half_net": net_long,
           "matches_sat7_record": match},
          open(f"{BASE}/stocks_engine_sat8_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat8_diag.json")
