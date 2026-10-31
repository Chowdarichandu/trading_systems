#!/usr/bin/env python3
"""ENGINE SAT-2 STEP 1b: richer August cuts after the first scan
found no single comp x stock slice big enough. August is an F4
problem (-7,286.99; 11 stops -10,393.92) dominated by
skill_or_breakdown SHORT stops (GLENMARK x2, UNITDSPR, BDL,
HINDALCO, HINDCOPPER x2, RECLTD). Cut by comp x setup, F4 x setup
x dir, F4 x dir, F4 x stock x setup, F4 x stock (both dirs),
F4 x stock x dir for the August-heavy names, and F4 by day-cluster
structure (round/leg). Every candidate reports Aug / full / Oct /
Jun / Apr. Removal value for August = -(Aug net). Paper, real Rs0.
"""
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
assert len(book) == 896 and round(sum(t["net"] for t in book), 2) == 143386.24

def stats(trades, keyfn, k):
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

def show(label, keyfn, min_aug_loss=0.0, only_neg_both=True):
    print(f"\n=== {label} ===")
    keys = {keyfn(t) for t in book}
    keys.discard(None)
    rows = []
    for k in keys:
        st = stats(book, keyfn, k)
        if st["aug"][0] == 0:
            continue
        if only_neg_both and not (st["aug"][1] < -min_aug_loss
                                  and st["full"][1] < 0):
            continue
        rows.append((st["aug"][1], k, st))
    for _, k, st in sorted(rows):
        print(f" {str(k):46} Aug n={st['aug'][0]:2} {st['aug'][1]:9.2f} (w {st['aug'][2]}) "
              f"| full n={st['full'][0]:3} {st['full'][1]:10.2f} (w {st['full'][2]}) "
              f"| Oct {st['oct'][1]:9.2f} | Jun {st['jun'][1]:8.2f} | Apr {st['apr'][1]:8.2f}")

show("comp x setup (neg Aug & full)",
     lambda t: (t["comp"], t.get("setup", "-")))
show("F4 x setup x dir (neg Aug & full)",
     lambda t: ("F4", t.get("setup", "-"), t["dir"]) if t["comp"] == "F4" else None)
show("F4 x dir (ALL, context)",
     lambda t: ("F4", t["dir"]) if t["comp"] == "F4" else None,
     only_neg_both=False)
show("F4 x stock (neg Aug & full)",
     lambda t: ("F4", t["stock"]) if t["comp"] == "F4" else None)
show("F4 x stock x dir (neg Aug & full, Aug loss > 500)",
     lambda t: ("F4", t["stock"], t["dir"]) if t["comp"] == "F4" else None,
     min_aug_loss=500.0)
show("F4 x leg / round (neg Aug & full)",
     lambda t: ("F4", t.get("leg", "-"), str(t.get("round", "-"))) if t["comp"] == "F4" else None)
show("comp x setup x dir (neg Aug & full)",
     lambda t: (t["comp"], t.get("setup", "-"), t["dir"]))

# F4 August stops: what were they, in full?
print("\n=== ALL F4 AUGUST TRADES ===")
for t in sorted([t for t in f4 if t["date"].startswith("2026-08")],
                key=lambda t: t["net"]):
    print(f" {t['date']} {t['stock']:12} {t['dir']:5} {t['setup']:24} "
          f"leg {t['leg']:7} pm {t['premove_pct']:+.2f} {t['exit_reason']:10} "
          f"net {t['net']:9.2f}")
