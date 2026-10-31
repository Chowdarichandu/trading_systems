#!/usr/bin/env python3
"""ENGINE SAT-20 SCORE: INV-LONG x HINDZINC exclusion, frozen in
stocks_engine_frozen.md (SAT-20 section) AFTER the diagnosis
(sat20_diag) and BEFORE this ran. Anchors: (A) incumbent union ==
state (780 tr / +184,555.23 / month table / ex-top-3 61,445.64),
N4 anchored on the SAT-15 T150/S080 dump MINUS the SAT-17
TVSMOTOR-LONG exclusion, F4 minus the SAT-18 OIL-SHORT exclusion,
INV-LONG minus BDL + the SAT-19 VEDL exclusion (book law --
M1.load_n4() is the stale T125/S050 dump and is NOT used);
(B) the deleted set == the frozen 9-trade set exactly;
(C) deletion-only on audited dumps (timing inherited).
Saturation gate: (a) total rises; (b) all ten months > 0 AND
razors Aug/Jul/Jun keep >= Rs100; (c) October >= 50,000;
(d) ex-top-3 not worse; (e) anchors pass.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
import csv, sys, json
from collections import defaultdict
from datetime import date
import importlib.util

BASE = "/home/hatch/workspace/trading"
sys.path.insert(0, BASE)
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 26611.46, "2026-02": 18112.44, "2026-03": 20093.11,
         "2026-04": 7917.43, "2026-05": 34456.21, "2026-06": 1532.01,
         "2026-07": 4448.29, "2026-08": 309.08, "2026-09": 18043.55,
         "2026-10": 53031.65}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 184555.23, 780, 61445.64
FROZEN_SLICE = ("INV-LONG", "HINDZINC", "LONG")
FROZEN_SET = [("2026-01-13", "HINDZINC", "LONG", -358.3),
              ("2026-01-21", "HINDZINC", "LONG", -388.2),
              ("2026-01-21", "HINDZINC", "LONG", -388.45),
              ("2026-02-02", "HINDZINC", "LONG", -335.57),
              ("2026-03-20", "HINDZINC", "LONG", -302.75),
              ("2026-04-07", "HINDZINC", "LONG", 620.44),
              ("2026-04-09", "HINDZINC", "LONG", -320.75),
              ("2026-05-04", "HINDZINC", "LONG", -343.48),
              ("2026-06-11", "HINDZINC", "LONG", -314.77)]

# ---------- incumbent book (post-SAT-19 construction) -------------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"
       and t["stock"] != "VEDL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"
      and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT"), ("OIL", "SHORT")}
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
    return ({k: round(m.get(k, 0.0), 2) for k in sorted(STATE)},
            {k: c[k] for k in sorted(c)})

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [(k, round(v, 2)) for k, v in top3])

bt, _ = mt(book)
ex0, top3_0 = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: incumbent union == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- the frozen deletion ----------
deleted = [t for t in book
           if (t["comp"], t["stock"], t["dir"]) == FROZEN_SLICE]
dset = sorted((t["date"], t["stock"], t["dir"], t["net"]) for t in deleted)
b_ok = dset == sorted(FROZEN_SET)
print(f"ANCHOR B: deleted set == frozen set: {b_ok} | {len(dset)} trades, "
      f"net {round(sum(x[3] for x in dset),2)}")
assert b_ok, f"ANCHOR B FAILED -- do not judge: {dset}"

new_book = [t for t in book
            if (t["comp"], t["stock"], t["dir"]) != FROZEN_SLICE]
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
ex1, top3_1 = extop3(new_book)
print(f"\n{'month':8} {'current':>10} {'SAT-20':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt[k]:>10.2f} "
          f"{round(nt[k]-STATE[k],2):>10.2f} {nc[k]:>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
print(f"ex-top-3: {ex0} -> {ex1} (top3 before {top3_0}, after {top3_1})")
print(f"razors after: Aug {nt['2026-08']} / Jul {nt['2026-07']} / "
      f"Jun {nt['2026-06']} | October headroom "
      f"{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-20) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values()) and nt["2026-08"] >= 100 \
    and nt["2026-07"] >= 100 and nt["2026-06"] >= 100
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten green + razors >= 100: {gb} "
      f"(min {min(nt.values())} in {min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors pass: A {a_ok}, B {b_ok} -> {ge}")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

json.dump({"anchors": {"A": a_ok, "B": b_ok},
           "fix": "SAT-20-INV-HINDZINC (INV-LONG excludes HINDZINC; "
                  "stock x mechanism exclusion)",
           "fix_id": "SAT-20-INV-HINDZINC",
           "slice": {"trades": len(deleted),
                     "net": round(sum(x[3] for x in dset), 2),
                     "win": sum(1 for x in dset if x[3] > 0),
                     "deleted_set": dset,
                     "jun_slice": -314.77, "oct_slice": 0.0,
                     "aug_slice": 0.0, "apr_slice": 299.69},
           "registry": {"slices_total": 145, "qualifying": 11},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_before": top3_0, "top3_after": top3_1,
           "legs": {"a_total": ga, "b_all_green_razors": gb,
                    "c_oct": gc, "d_extop3": gd, "e_anchors": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "razors_after": {"2026-08": nt["2026-08"],
                            "2026-07": nt["2026-07"],
                            "2026-06": nt["2026-06"]}},
          open(f"{BASE}/stocks_engine_sat20_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat20_result.json")
