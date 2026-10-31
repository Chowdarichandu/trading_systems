#!/usr/bin/env python3
"""ENGINE SAT-2 STEP 1: verify current incumbent anchor vs state
(896 tr, +143,386.24, August +185.69 / 32 tr), then diagnose
August's drags: component/stock/day/dir/exit splits + a wide slice
scan for parts negative in August AND full-period (Lessons 5/11),
each candidate carrying its October / June / April slices
(Lesson 12: judged net of the secured floors; October headroom is
only Rs572.02). For any floor-blocked comp x stock slice, print the
DIRECTION split automatically (Lesson 15). Paper, real Rs0,
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

STATE = {"2026-01": 11378.22, "2026-02": 6130.34, "2026-03": 20825.94,
         "2026-04": 1284.36, "2026-05": 28673.22, "2026-06": 1853.72,
         "2026-07": 3196.63, "2026-08": 185.69, "2026-09": 19286.10,
         "2026-10": 50572.02}
STATE_TOTAL, STATE_TRADES = 143386.24, 896
OCT_HEADROOM = round(STATE["2026-10"] - 50000, 2)   # 572.02

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
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")]
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
      f"| August {bt['2026-08']} / {bc['2026-08']} trades "
      f"| October {bt['2026-10']} headroom {OCT_HEADROOM}")
assert anchor_ok

aug = [t for t in book if t["date"].startswith("2026-08")]

def agg(label, trades, keyfn):
    g = defaultdict(lambda: [0, 0.0])
    for t in trades:
        k = keyfn(t); g[k][0] += 1; g[k][1] += t["net"]
    print(f"\n--- August by {label} (n, net) ---")
    for k, v in sorted(g.items(), key=lambda kv: kv[1][1]):
        print(f" {str(k):28} n={v[0]:3} net={v[1]:10.2f}")
    return g

agg("component", aug, lambda t: t["comp"])
agg("stock", aug, lambda t: t["stock"])
agg("day", aug, lambda t: t["date"])
agg("dir", aug, lambda t: t["dir"])
agg("exit_reason", aug, lambda t: t["exit_reason"])
agg("comp x exit", aug, lambda t: (t["comp"], t["exit_reason"]))
agg("comp x dir", aug, lambda t: (t["comp"], t["dir"]))

nets = sorted((t["net"] for t in aug), reverse=True)
atot = round(sum(nets), 2)
print(f"\n=== AUGUST CONCENTRATION === August net {atot} | top1 {nets[0]:.2f} "
      f"| top3 {sum(nets[:3]):.2f} | ex-top3 {atot - sum(nets[:3]):.2f} "
      f"| winners {sum(1 for n in nets if n > 0)}/{len(nets)}")

def slice_stats(trades, keyfn, k):
    sel = [t for t in trades if keyfn(t) == k]
    out = {}
    for name, pred in [("aug", lambda t: t["date"].startswith("2026-08")),
                       ("full", lambda t: True),
                       ("oct", lambda t: t["date"].startswith("2026-10")),
                       ("jun", lambda t: t["date"].startswith("2026-06")),
                       ("apr", lambda t: t["date"].startswith("2026-04"))]:
        s = [t for t in sel if pred(t)]
        out[name] = (len(s), round(sum(t["net"] for t in s), 2),
                     sum(1 for t in s if t["net"] > 0))
    return out

print("\n=== SLICE SCAN: negative in August AND full-period ===")
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
    keys = {fn(t) for t in book}
    keys.discard(None)
    for k in sorted(keys, key=str):
        st = slice_stats(book, fn, k)
        if st["aug"][1] < 0 and st["full"][1] < 0 and st["aug"][0] > 0:
            rec = {"scan": label, "slice": str(k),
                   "aug_n": st["aug"][0], "aug_net": st["aug"][1],
                   "aug_win": st["aug"][2],
                   "full_n": st["full"][0], "full_net": st["full"][1],
                   "full_win": st["full"][2],
                   "oct_n": st["oct"][0], "oct_net": st["oct"][1],
                   "jun_net": st["jun"][1], "apr_net": st["apr"][1],
                   "oct_blocked": st["oct"][1] > OCT_HEADROOM}
            found.append(rec)
            print(f" {label:20} {str(k):44} Aug n={st['aug'][0]} {st['aug'][1]:9.2f} "
                  f"(w {st['aug'][2]}) | full n={st['full'][0]} {st['full'][1]:10.2f} "
                  f"(w {st['full'][2]}) | Oct {st['oct'][1]:9.2f} "
                  f"| Jun {st['jun'][1]:8.2f} | Apr {st['apr'][1]:8.2f}"
                  f"{'  <-- OCT-BLOCKED' if rec['oct_blocked'] else ''}")
if not found:
    print(" none")

print("\n=== DIRECTION SPLITS of floor-blocked / large comp x stock slices "
      "(Lesson 15) ===")
fn2 = lambda t: (t["comp"], t["stock"])
seen = set()
for rec in found:
    if rec["scan"] != "comp x stock":
        continue
    comp, stock = eval(rec["slice"])
    for d in ("LONG", "SHORT"):
        st = slice_stats(book, lambda t: (t["comp"], t["stock"], t["dir"]),
                         (comp, stock, d))
        if st["full"][0] == 0:
            continue
        key = (comp, stock, d)
        if key in seen:
            continue
        seen.add(key)
        print(f" {comp:8} {stock:12} {d:5} Aug n={st['aug'][0]} {st['aug'][1]:9.2f} "
              f"| full n={st['full'][0]} {st['full'][1]:10.2f} (w {st['full'][2]}) "
              f"| Oct {st['oct'][1]:9.2f} | Jun {st['jun'][1]:8.2f} "
              f"| Apr {st['apr'][1]:8.2f}")

print("\n=== AUGUST WORST DAYS / TRADES ===")
for t in sorted(aug, key=lambda t: t["net"])[:14]:
    print(f" {t['date']} {t['comp']:8} {t['stock']:12} {t['dir']:5} "
          f"{str(t.get('setup','-')):24} {t['exit_reason']:10} net {t['net']:9.2f}")

json.dump({"anchor_ok": anchor_ok, "august_trades": len(aug),
           "august_net": atot, "oct_headroom": OCT_HEADROOM,
           "surgical_candidates": found},
          open(f"{BASE}/stocks_engine_sat2_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat2_diag.json")
