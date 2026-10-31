#!/usr/bin/env python3
"""ENGINE JU-1 STEP 1: verify current book anchor vs state, then
diagnose July (target month): component/stock/day splits,
concentration, inactive components, and a slice scan for parts
negative in July AND full-period (Lessons 5/11 surgical pattern).
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
STATE_TOTAL, STATE_TRADES = 134850.34, 930

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"]) and t["stock"] != "ASTRAL"]
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
      f"| July {bt['2026-07']} / {bc['2026-07']} trades")
assert anchor_ok

jul = sorted([t for t in book if t["date"].startswith("2026-07")],
             key=lambda t: (t["date"], t["entry_time"]))
print(f"\n=== JULY TRADES ({len(jul)}) ===")
for t in jul:
    print(f" {t['date']} {t['comp']:8} {t['stock']:12} {t['dir']:5} "
          f"{t.get('setup','-'):24} entry {t['entry_time']} "
          f"{t['exit_reason']:10} net {t['net']:9.2f}")

def agg(label, trades, keyfn):
    g = defaultdict(lambda: [0, 0.0])
    for t in trades:
        k = keyfn(t); g[k][0] += 1; g[k][1] += t["net"]
    print(f"\n--- July by {label} (n, net) ---")
    for k, v in sorted(g.items(), key=lambda kv: kv[1][1]):
        print(f" {str(k):28} n={v[0]:3} net={v[1]:10.2f}")
    return g

agg("component", jul, lambda t: t["comp"])
allcomps = {"INV-LONG", "N4-V3", "P2F", "F4"}
active = {t["comp"] for t in jul}
print("inactive components in July:", sorted(allcomps - active) or "none")
agg("stock", jul, lambda t: t["stock"])
agg("day", jul, lambda t: t["date"])
agg("dir", jul, lambda t: t["dir"])
agg("exit_reason", jul, lambda t: t["exit_reason"])

nets = sorted((t["net"] for t in jul), reverse=True)
jtot = round(sum(nets), 2)
print(f"\n=== JULY CONCENTRATION ===")
print(f" July net {jtot} | top1 {nets[0]:.2f} ({100*nets[0]/jtot:.1f}%) "
      f"| top3 {sum(nets[:3]):.2f} ({100*sum(nets[:3])/jtot:.1f}%) "
      f"| ex-top3 {jtot - sum(nets[:3]):.2f}")
print(f" winners {sum(1 for n in nets if n > 0)}/{len(nets)} "
      f"| gross wins {sum(n for n in nets if n > 0):.2f} "
      f"| gross losses {sum(n for n in nets if n < 0):.2f}")

print("\n=== SLICE SCAN: negative in July AND full-period ===")
def slices(trades, keyfn):
    gj = defaultdict(lambda: [0, 0.0]); gf = defaultdict(lambda: [0, 0.0])
    for t in book:
        k = keyfn(t); gf[k][0] += 1; gf[k][1] += t["net"]
        if t["date"].startswith("2026-07"):
            gj[k][0] += 1; gj[k][1] += t["net"]
    return gj, gf
scans = {
    "comp x stock": lambda t: (t["comp"], t["stock"]),
    "comp x dir": lambda t: (t["comp"], t["dir"]),
    "comp x setup": lambda t: (t["comp"], t.get("setup", "-")),
    "F4 x leg": lambda t: ("F4", t.get("leg", "-")) if t["comp"] == "F4" else None,
    "F4 x band": lambda t: ("F4", "[0.5,0.75)" if t.get("premove_pct", 0) < 0.75 else "[0.75,1.0)") if t["comp"] == "F4" else None,
    "F4 x event": lambda t: ("F4", t.get("event", "-")) if t["comp"] == "F4" else None,
}
found = []
for label, fn in scans.items():
    gj, gf = slices(book, fn)
    for k, (nj, vj) in gj.items():
        if k is None or (isinstance(k, tuple) and None in k): continue
        nf, vf = gf[k]
        if vj < 0 and vf < 0:
            found.append({"scan": label, "slice": str(k), "jul_n": nj,
                          "jul_net": round(vj, 2), "full_n": nf,
                          "full_net": round(vf, 2)})
            print(f" {label:14} {str(k):42} Jul n={nj} net={vj:9.2f} "
                  f"| full n={nf} net={vf:10.2f}")
if not found:
    print(" none")
json.dump({"anchor_ok": anchor_ok, "july_trades": len(jul),
           "july_net": jtot,
           "top1": round(nets[0], 2), "top3": round(sum(nets[:3]), 2),
           "ex_top3": round(jtot - sum(nets[:3]), 2),
           "inactive": sorted(allcomps - active),
           "surgical_candidates": found},
          open(f"{BASE}/stocks_engine_ju1_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_ju1_diag.json")
