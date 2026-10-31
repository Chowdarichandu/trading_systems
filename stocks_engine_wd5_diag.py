#!/usr/bin/env python3
"""ENGINE SAT-3 STEP 1: verify incumbent anchor vs state (878 tr,
+143,747.36, August +878.69, October +51,364.74, headroom 1,364.74),
then a wide slice scan for parts negative in a THIN month (Aug/Jun/Apr)
AND full-period (Lessons 5/11/12/15), each candidate carrying its
October slice vs the NEW headroom (SAT-2 raised headroom from 572.02
to 1,364.74, so slices floor-blocked at SAT-2 -- e.g. F4 x UNITDSPR
SHORT, Oct +780.00 -- must be re-checked). Paper, real Rs0,
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

STATE = {"2026-01": 11378.22, "2026-02": 6130.34, "2026-03": 20269.77,
         "2026-04": 2043.12, "2026-05": 28714.75, "2026-06": 1853.72,
         "2026-07": 3196.63, "2026-08": 878.69, "2026-09": 17917.38,
         "2026-10": 51364.74}
STATE_TOTAL, STATE_TRADES = 143747.36, 878
OCT_HEADROOM = round(STATE["2026-10"] - 50000, 2)   # 1364.74

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
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")]
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
      f"| August {bt['2026-08']} | October {bt['2026-10']} headroom {OCT_HEADROOM}")
assert anchor_ok

def slice_stats(trades, keyfn, k):
    sel = [t for t in trades if keyfn(t) == k]
    out = {}
    for name, mon in [("aug", "2026-08"), ("jun", "2026-06"), ("apr", "2026-04"),
                      ("oct", "2026-10"), ("full", None)]:
        s = sel if mon is None else [t for t in sel if t["date"].startswith(mon)]
        out[name] = (len(s), round(sum(t["net"] for t in s), 2),
                     sum(1 for t in s if t["net"] > 0))
    out["months"] = {k2: round(v2, 2) for k2, v2 in mt(sel)[0].items()}
    return out

scans = {
    "comp x stock": lambda t: (t["comp"], t["stock"]),
    "comp x stock x dir": lambda t: (t["comp"], t["stock"], t["dir"]),
    "comp x dir": lambda t: (t["comp"], t["dir"]),
    "comp x setup": lambda t: (t["comp"], t.get("setup", "-")),
    "comp x setup x dir": lambda t: (t["comp"], t.get("setup", "-"), t["dir"]),
    "stock (all comps)": lambda t: t["stock"],
}
found = []
for target, tname in [("aug", "August"), ("jun", "June"), ("apr", "April")]:
    print(f"\n=== SLICE SCAN: negative in {tname} AND full-period ===")
    any_f = False
    for label, fn in scans.items():
        keys = {fn(t) for t in book}
        for k in sorted(keys, key=str):
            st = slice_stats(book, fn, k)
            if st[target][1] < 0 and st["full"][1] < 0 and st[target][0] > 0:
                any_f = True
                rec = {"target": target, "scan": label, "slice": str(k),
                       "tgt_n": st[target][0], "tgt_net": st[target][1],
                       "full_n": st["full"][0], "full_net": st["full"][1],
                       "full_win": st["full"][2],
                       "oct_n": st["oct"][0], "oct_net": st["oct"][1],
                       "aug_net": st["aug"][1], "jun_net": st["jun"][1],
                       "apr_net": st["apr"][1],
                       "oct_blocked": st["oct"][1] > OCT_HEADROOM,
                       "months": st["months"]}
                found.append(rec)
                print(f" {label:20} {str(k):46} tgt n={st[target][0]} {st[target][1]:9.2f} "
                      f"| full n={st['full'][0]} {st['full'][1]:10.2f} (w {st['full'][2]}) "
                      f"| Oct {st['oct'][1]:9.2f} | Aug {st['aug'][1]:8.2f} "
                      f"| Jun {st['jun'][1]:8.2f} | Apr {st['apr'][1]:8.2f}"
                      f"{'  <-- OCT-BLOCKED' if rec['oct_blocked'] else ''}")
    if not any_f:
        print(" none")

# explicit re-check of the SAT-2 floor-blocked names under the new headroom
print("\n=== RE-CHECK SAT-2 BLOCKED SLICES AT NEW HEADROOM 1,364.74 ===")
for comp, stock in [("F4", "UNITDSPR"), ("F4", "GLENMARK"), ("F4", "GODREJCP")]:
    for d in (None, "LONG", "SHORT"):
        fn = (lambda dd: (lambda t: (t["comp"], t["stock"], t["dir"]) if dd else (t["comp"], t["stock"])))(d)
        k = (comp, stock, d) if d else (comp, stock)
        st = slice_stats(book, fn, k)
        if st["full"][0]:
            print(f" {comp} {stock} {d or 'ALL':5} full n={st['full'][0]} {st['full'][1]:10.2f} "
                  f"| Aug {st['aug'][1]:9.2f} | Oct {st['oct'][1]:9.2f} "
                  f"| Jun {st['jun'][1]:8.2f} | Apr {st['apr'][1]:8.2f} | months {st['months']}")

# SE-1-F4R1 revisit arithmetic at current headroom
r2 = [t for t in f4 if str(t.get("round")) == "2" or t.get("leg") == "round2"]
print(f"\n=== SE-1-F4R1 REVISIT CHECK === F4 round/leg-2 trades in dump: {len(r2)} "
      f"net {round(sum(t['net'] for t in r2),2)}; months {mt(r2)[0]}")
print(f"October headroom {OCT_HEADROOM} vs recorded Oct round2 value +1,551.75 "
      f"-> {'UNLOCKED' if OCT_HEADROOM >= 1551.75 else 'STILL SHORT by ' + str(round(1551.75 - OCT_HEADROOM, 2))}")

json.dump({"anchor_ok": anchor_ok, "oct_headroom": OCT_HEADROOM,
           "surgical_candidates": found},
          open(f"{BASE}/stocks_engine_sat3_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat3_diag.json")
