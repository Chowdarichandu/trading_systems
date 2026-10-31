#!/usr/bin/env python3
"""ENGINE SAT-1 STEP 1: verify current incumbent anchor vs state
(906 tr, +138,631.32, June +172.76), then diagnose June's drags:
component/stock/day/dir/exit splits + a wide slice scan for parts
negative in June AND full-period (Lessons 5/11), each candidate
also carrying its October / August / April slices (Lesson 12:
a fix is judged net of the secured floors). Paper, real Rs0,
per 100 sh, Rs40/tr."""
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

STATE = {"2026-01": 11378.22, "2026-02": 5125.86, "2026-03": 19116.26,
         "2026-04": 1464.36, "2026-05": 29377.98, "2026-06": 172.76,
         "2026-07": 3196.63, "2026-08": 185.69, "2026-09": 18041.54,
         "2026-10": 50572.02}
STATE_TOTAL, STATE_TRADES = 138631.32, 906

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "round": r["round"], "entry_time": r["entry_time"],
        "exit_reason": r["exit_reason"], "net": float(r["net"]),
        "premove_pct": float(r["premove_pct"]), "event": r["event"]}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

bt, bc = mt(book)
tot = round(sum(t["net"] for t in book), 2)
anchor_ok = bt == STATE and tot == STATE_TOTAL and len(book) == STATE_TRADES
print(f"ANCHOR: {anchor_ok} | trades {len(book)} total {tot} "
      f"| June {bt['2026-06']} / {bc['2026-06']} trades")
assert anchor_ok

jun = [t for t in book if t["date"].startswith("2026-06")]

def agg(label, trades, keyfn):
    g = defaultdict(lambda: [0, 0.0])
    for t in trades:
        k = keyfn(t); g[k][0] += 1; g[k][1] += t["net"]
    print(f"\n--- June by {label} (n, net) ---")
    for k, v in sorted(g.items(), key=lambda kv: kv[1][1]):
        print(f" {str(k):28} n={v[0]:3} net={v[1]:10.2f}")
    return g

agg("component", jun, lambda t: t["comp"])
agg("stock", jun, lambda t: t["stock"])
agg("day", jun, lambda t: t["date"])
agg("dir", jun, lambda t: t["dir"])
agg("exit_reason", jun, lambda t: t["exit_reason"])
agg("comp x exit", jun, lambda t: (t["comp"], t["exit_reason"]))

nets = sorted((t["net"] for t in jun), reverse=True)
jtot = round(sum(nets), 2)
print(f"\n=== JUNE CONCENTRATION === June net {jtot} | top1 {nets[0]:.2f} "
      f"| top3 {sum(nets[:3]):.2f} | ex-top3 {jtot - sum(nets[:3]):.2f} "
      f"| winners {sum(1 for n in nets if n > 0)}/{len(nets)}")

print("\n=== SLICE SCAN: negative in June AND full-period ===")
def month_net(trades, k, keyfn, month):
    return round(sum(t["net"] for t in trades
                     if keyfn(t) == k and t["date"].startswith(month)), 2)
def month_n(trades, k, keyfn, month):
    return sum(1 for t in trades
               if keyfn(t) == k and t["date"].startswith(month))

scans = {
    "comp x stock": lambda t: (t["comp"], t["stock"]),
    "comp x stock x dir": lambda t: (t["comp"], t["stock"], t["dir"]),
    "comp x dir": lambda t: (t["comp"], t["dir"]),
    "comp x setup": lambda t: (t["comp"], t.get("setup", "-")),
    "stock (all comps)": lambda t: t["stock"],
    "F4 x leg": lambda t: ("F4", t.get("leg", "-")) if t["comp"] == "F4" else None,
    "F4 x band": lambda t: ("F4", "[0.5,0.75)" if t.get("premove_pct", 0) < 0.75 else "[0.75,1.0)") if t["comp"] == "F4" else None,
    "F4 x event": lambda t: ("F4", t.get("event", "-")) if t["comp"] == "F4" else None,
    "F4 x stock x band": lambda t: ("F4", t["stock"], "[0.5,0.75)" if t.get("premove_pct", 0) < 0.75 else "[0.75,1.0)") if t["comp"] == "F4" else None,
}
found = []
for label, fn in scans.items():
    gj = defaultdict(lambda: [0, 0.0]); gf = defaultdict(lambda: [0, 0.0])
    for t in book:
        k = fn(t)
        if k is None or (isinstance(k, tuple) and None in k): continue
        gf[k][0] += 1; gf[k][1] += t["net"]
        if t["date"].startswith("2026-06"):
            gj[k][0] += 1; gj[k][1] += t["net"]
    for k, (nj, vj) in sorted(gj.items(), key=lambda kv: kv[1][1]):
        nf, vf = gf[k]
        if vj < 0 and vf < 0:
            rec = {"scan": label, "slice": str(k), "jun_n": nj,
                   "jun_net": round(vj, 2), "full_n": nf,
                   "full_net": round(vf, 2),
                   "oct_net": month_net(book, k, fn, "2026-10"),
                   "aug_net": month_net(book, k, fn, "2026-08"),
                   "apr_net": month_net(book, k, fn, "2026-04")}
            found.append(rec)
            print(f" {label:20} {str(k):44} Jun n={nj} {vj:9.2f} "
                  f"| full n={nf} {vf:10.2f} | Oct {rec['oct_net']:9.2f} "
                  f"| Aug {rec['aug_net']:8.2f} | Apr {rec['apr_net']:8.2f}")
if not found:
    print(" none")

print("\n=== JUNE WORST DAYS / TRADES ===")
gd = agg("day (repeat)", jun, lambda t: t["date"])
for t in sorted(jun, key=lambda t: t["net"])[:12]:
    print(f" {t['date']} {t['comp']:8} {t['stock']:12} {t['dir']:5} "
          f"{str(t.get('setup','-')):24} {t['exit_reason']:10} net {t['net']:9.2f}")

json.dump({"anchor_ok": anchor_ok, "june_trades": len(jun),
           "june_net": jtot, "surgical_candidates": found},
          open(f"{BASE}/stocks_engine_sat1_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat1_diag.json")
