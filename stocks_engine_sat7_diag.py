#!/usr/bin/env python3
"""ENGINE SAT-7 DIAGNOSIS: AUGUST at the CURRENT book (post SAT-6,
F4 first-signal-only). Anchor: rebuild == state (799 tr /
+146,423.19 / Oct +51,129.79) asserted first. Deletion analysis
only, so timing validity is inherited. Paper, real Rs0, per 100
shares, Rs40/trade, home 25."""
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

STATE = {"2026-01": 12021.03, "2026-02": 2488.65, "2026-03": 22291.79,
         "2026-04": 3236.26, "2026-05": 27838.61, "2026-06": 4287.51,
         "2026-07": 3196.63, "2026-08": 103.44, "2026-09": 19829.48,
         "2026-10": 51129.79}
STATE_TOTAL, STATE_TRADES = 146423.19, 799

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
       and r["leg"] != "round2"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
       and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")]
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(float)
    for t in trades: m[t["date"][:7]] += t["net"]
    return {k: round(m[k], 2) for k in sorted(m)}

def sm(trades):
    return (len(trades), round(sum(t["net"] for t in trades), 2),
            sum(1 for t in trades if t["net"] > 0))

bt = mt(book)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
             and len(book) == STATE_TRADES)
print("ANCHOR (current book == state):", anchor_ok,
      f"| trades {len(book)} total {round(sum(t['net'] for t in book),2)}")
assert anchor_ok, "ANCHOR FAILED"

AUG = [t for t in book if t["date"].startswith("2026-08")]
print(f"\n=== AUGUST AT CURRENT BOOK: {len(AUG)} trades, "
      f"net {round(sum(t['net'] for t in AUG),2)} ===")
byc = defaultdict(list)
for t in AUG: byc[t["comp"]].append(t)
for c in sorted(byc):
    n, net, w = sm(byc[c])
    print(f"  {c:9} {n:3} tr net {net:10.2f} winners {w}/{n}")
print("\n  all August trades:")
for t in sorted(AUG, key=lambda t: (t["date"], t["comp"])):
    print(f"   {t['date']} {t['comp']:9} {t['stock']:12} {t['dir']:5} "
          f"{str(t.get('setup','')):22} {t['entry_time']:5} "
          f"{t['exit_reason']:10} net {t['net']:9.2f}")

def slice_report(keyfn, label, min_n_aug=1):
    """Slices negative in BOTH August and full period."""
    full, aug = defaultdict(list), defaultdict(list)
    for t in book: full[keyfn(t)].append(t)
    for t in AUG: aug[keyfn(t)].append(t)
    print(f"\n--- {label}: slices negative in August AND full-period ---")
    rows = []
    for k in sorted(set(full) | set(aug)):
        fn, fnet, fw = sm(full.get(k, []))
        an, anet, aw = sm(aug.get(k, []))
        if an >= min_n_aug:
            flag = " <== NEG BOTH" if (anet < 0 and fnet < 0) else ""
            rows.append((k, an, anet, aw, fn, fnet, fw, flag))
    for k, an, anet, aw, fn, fnet, fw, flag in rows:
        print(f"  {str(k):38} Aug {an:3} tr {anet:10.2f} (w {aw}) | "
              f"Full {fn:3} tr {fnet:11.2f} (w {fw}){flag}")
    return rows

slice_report(lambda t: t["comp"], "component")
slice_report(lambda t: (t["comp"], t["dir"]), "component x direction")
slice_report(lambda t: (t["comp"], t["stock"]), "component x stock")
slice_report(lambda t: (t["comp"], t["stock"], t["dir"]),
             "component x stock x direction")
slice_report(lambda t: (t["comp"], t.get("setup", "-")),
             "component x setup")
slice_report(lambda t: (t["comp"], t["stock"]), "comp x stock (dup guard)")

# October slice of every comp x stock x dir slice negative in Aug
print("\n--- October slices of Aug-negative comp x stock x dir slices "
      "(floor check: headroom 1,129.79) ---")
octbook = [t for t in book if t["date"].startswith("2026-10")]
def key3(t): return (t["comp"], t["stock"], t["dir"])
for k in sorted({key3(t) for t in AUG}):
    a = [t for t in AUG if key3(t) == k]
    if sum(t["net"] for t in a) < 0:
        o = [t for t in octbook if key3(t) == k]
        f = [t for t in book if key3(t) == k]
        print(f"  {str(k):38} Aug {sm(a)[0]:2} tr {sm(a)[1]:9.2f} | "
              f"Oct {sm(o)[0]:2} tr {sm(o)[1]:9.2f} | Full {sm(f)[1]:10.2f}")

# ---- WINNERS SIDE: what earned in August, and in what ex-ante state?
print("\n=== AUGUST WINNERS vs LOSERS — shared ex-ante states ===")
winA = [t for t in AUG if t["net"] > 0]; losA = [t for t in AUG if t["net"] <= 0]
print(f"winners {len(winA)} (+{round(sum(t['net'] for t in winA),2)}) | "
      f"losers {len(losA)} ({round(sum(t['net'] for t in losA),2)})")
f4a = [t for t in AUG if t["comp"] == "F4"]
print("\nF4 August by premove sub-band:")
for lo, hi in [(0.5, 0.65), (0.65, 0.8), (0.8, 1.0)]:
    s = [t for t in f4a if lo <= abs(t["premove_pct"]) < hi]
    sf = [t for t in f4 if lo <= abs(t["premove_pct"]) < hi]
    if s:
        print(f"  |premove| [{lo},{hi}): Aug {sm(s)} | Full {sm(sf)}")
print("\nF4 August by entry hour:")
for h in ["10", "11", "12", "13", "14", "15"]:
    s = [t for t in f4a if t["entry_time"].startswith(h)]
    sf = [t for t in f4 if t["entry_time"].startswith(h)]
    if s:
        print(f"  {h}:xx  Aug {sm(s)} | Full {sm(sf)}")
print("\nF4 August by setup x direction:")
for k in sorted({(t["setup"], t["dir"]) for t in f4a}):
    s = [t for t in f4a if (t["setup"], t["dir"]) == k]
    sf = [t for t in f4 if (t["setup"], t["dir"]) == k]
    print(f"  {str(k):38} Aug {sm(s)} | Full {sm(sf)}")
print("\nF4 August by exit reason:")
for k in sorted({t["exit_reason"] for t in f4a}):
    s = [t for t in f4a if t["exit_reason"] == k]
    print(f"  {k:10} Aug {sm(s)}")
print("\nEvent systems August by direction:")
for c in ["N4-V3", "P2F"]:
    for d in ["LONG", "SHORT"]:
        s = [t for t in AUG if t["comp"] == c and t["dir"] == d]
        if s: print(f"  {c} {d}: Aug {sm(s)}")
print("\nAugust by week (Mon-Fri blocks):")
for wkstart in ["2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24",
                "2026-08-31"]:
    s = [t for t in AUG
         if wkstart <= t["date"] <= wkstart[:8] + "31"
         and (datetime.date.fromisoformat(t["date"])
              - datetime.date.fromisoformat(wkstart)).days < 5]
    if s: print(f"  week of {wkstart}: {sm(s)}")
json.dump({"anchor_ok": anchor_ok,
           "august_by_comp": {c: sm(byc[c]) for c in byc}},
          open(f"{BASE}/stocks_engine_sat7_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat7_diag.json")
