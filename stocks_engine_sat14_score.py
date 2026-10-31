#!/usr/bin/env python3
"""ENGINE SAT-14 SCORE: P2F excludes HINDALCO LONG (frozen in
stocks_engine_frozen.md, SAT-14 section, AFTER the diagnosis and
BEFORE this ran). Deletion-only fix on audited component dumps.
Anchors: (A) current book == state (813 tr / +166,176.00 / month
table / ex-top-3 51,853.86); (B) deleted set == the frozen 1-trade
set exactly. Saturation gate: (a) total rises; (b) all ten months
> 0; (c) October >= 50,000; (d) ex-top-3 not worse; (e) anchors.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
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
FROZEN_DELETED = [("2026-08-10", "HINDALCO", "LONG", -572.50)]
AUG_NEED = 4020.54

# ---------- current book (identical construction to sat14_diag) ----------
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
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: current book == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
assert a_ok, "ANCHOR A FAILED — do not judge"

# ---------- the frozen fix ----------
deleted = [t for t in book if t["comp"] == "P2F"
           and t["stock"] == "HINDALCO" and t["dir"] == "LONG"]
del_set = sorted((t["date"], t["stock"], t["dir"], t["net"]) for t in deleted)
b_ok = del_set == sorted(FROZEN_DELETED)
print(f"ANCHOR B: deleted set == frozen set: {b_ok} | {del_set}")
assert b_ok, "ANCHOR B FAILED — deleted set does not match the freeze"

new_book = [t for t in book if not (t["comp"] == "P2F"
            and t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
ex1, top3_1 = extop3(new_book)
print(f"\n{'month':8} {'current':>10} {'SAT-14':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")
aug_after = nt["2026-08"]
print(f"August after: Rs{aug_after} | N4-revisit required >= Rs{AUG_NEED} "
      f"| August leg MET: {aug_after >= AUG_NEED} "
      f"(margin Rs{round(aug_after - AUG_NEED, 2)})")
print(f"October after: Rs{nt['2026-10']} | headroom "
      f"Rs{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-14) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors pass: -> {ge} (A {a_ok}, B {b_ok})")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

json.dump({"anchors": {"A": a_ok, "B": b_ok},
           "fix": "SAT-14-P2F-HINDALCO-LONG-exclusion (P2F does not "
                  "take HINDALCO LONG signals; mechanism x direction "
                  "scoped)",
           "fix_id": "SAT-14-P2F-HINDALCO-LONG",
           "deleted_set": del_set,
           "deleted_detail": {"date": "2026-08-10", "stock": "HINDALCO",
                              "dir": "LONG", "net": -572.50,
                              "exit_reason": "stop", "R": "2026-08-07",
                              "reaction_ret_pct": 3.17},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_anchors": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": aug_after,
           "n4_revisit": {"august_required": AUG_NEED,
                          "august_leg_met": aug_after >= AUG_NEED,
                          "august_margin": round(aug_after - AUG_NEED, 2),
                          "note": "August leg only, at THIS book. The "
                                  "rebuild's own deltas (CH-2: August "
                                  "-3,834.85, June flip) are stale and "
                                  "must be re-measured in SAT-15 "
                                  "(Lesson 16) before any re-apply."}},
          open(f"{BASE}/stocks_engine_sat14_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat14_result.json")
