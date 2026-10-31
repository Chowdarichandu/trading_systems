#!/usr/bin/env python3
"""ENGINE SAT-14 DIAGNOSIS (re-derivation only — no scoring, no banking).
Rebuild the CURRENT book (813 tr / +166,176.00, FIVE components incl.
P2F-R2), anchor-assert against stocks_engine_state.json, then re-derive
the qualifying (comp x stock x dir) slices at THIS book: August slice
negative AND full-period negative. For each, compute the removal
arithmetic: August gain (-Aug slice), October after (51,107.02 - Oct
slice), whether every month stays green, and the new total. The
N4-rebuild revisit needs August >= 4,020.54, i.e. an August gain
>= 449.11, with October slice <= 1,107.02 (headroom). Selection rule
(pre-registered): among feasible slices prefer LEAST SURGERY = fewest
trades removed, tie-break smallest |full net|. Paper, real Rs0,
per 100 shares, Rs40/trade."""
import csv, sys, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
from datetime import date

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 18656.70, "2026-02": 12689.65, "2026-03": 18739.16,
         "2026-04": 7602.73, "2026-05": 32207.10, "2026-06": 2036.67,
         "2026-07": 2022.79, "2026-08": 3571.43, "2026-09": 17542.75,
         "2026-10": 51107.02}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 166176.00, 813, 51853.86
HEADROOM = 1107.02
AUG_NOW, AUG_NEED = 3571.43, 4020.54
AUG_GAIN_MIN = round(AUG_NEED - AUG_NOW, 2)   # 449.11

# ---------- current book: identical construction to sat13_score + R2 ----------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4 = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
       "dir": t["dir"], "net": t["net"]}
      for t in M1.load_n4()
      if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT")}
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")]
book = inv + n4 + p2f + f4 + r2

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

bt, _ = mt(book)
ex0, top3_0 = extop3(book)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
             and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR: current book == state: {anchor_ok} | trades {len(book)} "
      f"total {round(sum(t['net'] for t in book),2)} ex-top-3 {ex0} "
      f"(top3 {top3_0})")
for comp, rows in (("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f),
                   ("F4", f4), ("P2F-R2", r2)):
    print(f"  {comp}: {len(rows)} tr / {round(sum(t['net'] for t in rows),2)}")
assert anchor_ok, "ANCHOR FAILED — do not proceed"

# ---------- slice scan at the CURRENT book ----------
slices = defaultdict(lambda: {"trades": [], "months": defaultdict(float)})
for t in book:
    s = slices[(t["comp"], t["stock"], t["dir"])]
    s["trades"].append(t)
    s["months"][t["date"][:7]] += t["net"]

rows = []
for (comp, stock, d), s in sorted(slices.items()):
    full = round(sum(t["net"] for t in s["trades"]), 2)
    aug = round(s["months"].get("2026-08", 0.0), 2)
    if not (aug < 0 and full < 0):
        continue
    oct_slice = round(s["months"].get("2026-10", 0.0), 2)
    # removal arithmetic
    after = dict(STATE)
    for m, v in s["months"].items():
        after[m] = round(after[m] - v, 2)
    rows.append({
        "comp": comp, "stock": stock, "dir": d,
        "n": len(s["trades"]),
        "win": sum(1 for t in s["trades"] if t["net"] > 0),
        "full_net": full, "aug_net": aug, "oct_slice": oct_slice,
        "aug_gain": round(-aug, 2),
        "aug_after": after["2026-08"], "oct_after": after["2026-10"],
        "total_after": round(STATE_TOTAL - full, 2),
        "all_green_after": all(v > 0 for v in after.values()),
        "min_month_after": min(after.values()),
        "months": {k: round(v, 2) for k, v in sorted(s["months"].items())},
        "trade_keys": sorted((t["date"], t["net"]) for t in s["trades"]),
    })

feasible = [r for r in rows
            if r["aug_gain"] >= AUG_GAIN_MIN
            and r["oct_slice"] <= HEADROOM
            and r["all_green_after"]]
feasible.sort(key=lambda r: (r["n"], abs(r["full_net"])))
print(f"\nAUGUST SLICE SCAN (Aug<0 AND full<0 at current book): "
      f"{len(rows)} slices; feasible (gain >= {AUG_GAIN_MIN}, Oct slice "
      f"<= {HEADROOM}, all-green after): {len(feasible)}")
for r in sorted(rows, key=lambda r: r["aug_net"]):
    print(f"  {r['comp']:8} {r['stock']:12} {r['dir']:5} n={r['n']:>2} "
          f"win {r['win']} | full {r['full_net']:>9.2f} | Aug "
          f"{r['aug_net']:>9.2f} | Oct slice {r['oct_slice']:>8.2f} | "
          f"Aug after {r['aug_after']:>9.2f} | green-after "
          f"{r['all_green_after']}")
if feasible:
    c = feasible[0]
    print(f"\nSELECTED (least surgery): {c['comp']} x {c['stock']} x "
          f"{c['dir']} — {c['n']} tr, full {c['full_net']}, Aug "
          f"{c['aug_net']} (gain {c['aug_gain']} >= {AUG_GAIN_MIN}), Oct "
          f"slice {c['oct_slice']} (<= {HEADROOM}); Aug after "
          f"{c['aug_after']} (>= {AUG_NEED}: {c['aug_after'] >= AUG_NEED}); "
          f"total after {c['total_after']}; min month after "
          f"{c['min_month_after']}")
    print(f"  deleted set: {c['trade_keys']}")
    print(f"  slice months: {c['months']}")

json.dump({"anchor_ok": anchor_ok, "rows": rows,
           "feasible_ranked": feasible,
           "selected": feasible[0] if feasible else None},
          open(f"{BASE}/stocks_engine_sat14_diag.json", "w"), indent=1,
          default=str)
print("\nwrote stocks_engine_sat14_diag.json")
