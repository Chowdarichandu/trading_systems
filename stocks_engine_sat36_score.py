#!/usr/bin/env python3
"""ENGINE SAT-36 SCORE: F4 x GLENMARK x SHORT exclusion, frozen in
stocks_engine_frozen.md (SAT-36 section) AFTER the diagnosis
(sat36_diag) and BEFORE this ran. Anchors: (A) incumbent union
(SIX components) == state (663 tr / +197,607.74 / month table /
ex-top-3 72,518.25), per book law; (B) the deleted set == the
diagnosis 20-trade set exactly; (C) deletion-only on audited dumps
(timing inherited).
JUDGED ON TWO STANDARDS, BOTH REQUIRED TO BANK (frozen SAT-36):
(1) the arithmetic saturation gate -- (a) total rises; (b) all ten
months > 0 AND August >= 100; (c) October >= 50,000; (d) ex-top-3
not worse; (e) anchors pass.
(2) the standing quality bar (Lesson 5 rot-everywhere registry
standard): slice full-period net <= -500 at the current book.
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

STATE = {"2026-01": 28536.25, "2026-02": 18419.86, "2026-03": 20584.41,
         "2026-04": 9895.49, "2026-05": 34880.86, "2026-06": 3823.22,
         "2026-07": 6965.93, "2026-08": 666.78, "2026-09": 19562.51,
         "2026-10": 54272.43}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 197607.74, 663, 72518.25
EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
            ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
            ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
            ("PFC", "SHORT"), ("RECLTD", "SHORT")}

inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"
       and t["stock"] != "VEDL" and t["stock"] != "HINDZINC"
       and t["stock"] != "INDUSTOWER" and t["stock"] != "KALYANKJIL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"
      and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")
      and not (r["stock"] == "OIL" and r["direction"] == "LONG")]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL_DIR:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
      if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
r2low = [{"date": r["date"], "stock": r["symbol"], "comp": "R2-LOWBAND",
          "dir": r["direction"], "net": float(r["net_rs"])}
         for r in rd("stocks_engine_sat33_r2lowband_trades.csv")]
book = inv + n4 + p2f + f4 + r2 + r2low

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
print(f"ANCHOR A: incumbent == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

diag = json.load(open(f"{BASE}/stocks_engine_sat36_diag.json"))
FROZEN_SET = [tuple(x) for x in diag["slice"]["deleted_set"]]
deleted = [t for t in book
           if t["comp"] == "F4" and t["stock"] == "GLENMARK"
           and t["dir"] == "SHORT"]
dset = sorted((t["date"], t["stock"], t["dir"], t["net"]) for t in deleted)
b_ok = dset == sorted(FROZEN_SET)
s_net = round(sum(x[3] for x in dset), 2)
print(f"ANCHOR B: deleted set == frozen diagnosis set: {b_ok} | "
      f"{len(dset)} trades, net {s_net}")
assert b_ok, "ANCHOR B FAILED -- do not judge"

new_book = [t for t in book
            if not (t["comp"] == "F4" and t["stock"] == "GLENMARK"
                    and t["dir"] == "SHORT")]
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
ex1, top3_1 = extop3(new_book)
print(f"\n{'month':8} {'incumbent':>10} {'union':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt[k]:>10.2f} "
          f"{round(nt[k]-STATE[k],2):>10.2f} {nc[k]:>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
print(f"ex-top-3: {ex0} -> {ex1} (top3 before {top3_0}, after {top3_1})")
print(f"August union {nt['2026-08']} | October union {nt['2026-10']} "
      f"| headroom {round(nt['2026-10']-50000,2)}")

print("\n=== STANDARD 1: ARITHMETIC SATURATION GATE (frozen SAT-36) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values()) and nt["2026-08"] >= 100
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten green + August >= 100: {gb} "
      f"(min {min(nt.values())} in {min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors pass: A {a_ok}, B {b_ok} -> {ge}")
gate = all([ga, gb, gc, gd, ge])
print("GATE (standard 1):", gate)

print("\n=== STANDARD 2: QUALITY BAR (Lesson 5, registry standard) ===")
bar = s_net <= -500
print(f"slice full-period net {s_net} <= -500 -> {bar}")
print(f"supporting facts (diagnosis): 20 tr / 10 w / expectancy "
      f"{round(s_net/len(dset),2)} / net ex-August "
      f"{diag['slice']['net_ex_august']} / ex-carrier "
      f"{diag['slice']['ex_carrier']} / halves H1 {diag['slice']['h1']} "
      f"H2 {diag['slice']['h2']}")

banked = gate and bar
print(f"\nBANKED (requires BOTH standards): {banked}")
if not banked:
    print("REFUSED -- principled no-beat: the gate arithmetic passes but "
          "the quality bar fails; the bar is not lowered at the finish "
          "line. no_beat_cycles 2 -> 3: THE RUN IS SATURATED.")

json.dump({"anchors": {"A": a_ok, "B": b_ok},
           "fix": "SAT-36-F4-GLENMARK-SHORT (F4 excludes GLENMARK SHORT "
                  "signals; stock x mechanism x DIRECTION exclusion "
                  "-- F4 keeps GLENMARK LONG)",
           "fix_id": "SAT-36-F4-GLENMARK-SHORT",
           "slice": diag["slice"],
           "quality_bar": {"standard": "full-period <= -500",
                           "slice_net": s_net, "passes": bar},
           "gate_legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                         "d_extop3": gd, "e_anchors": ge},
           "gate_passes": gate,
           "union_month_table": nt, "union_total": tot_new,
           "union_trades": len(new_book),
           "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_before": top3_0, "top3_after": top3_1,
           "oct_headroom_union": round(nt["2026-10"] - 50000, 2),
           "banked": banked,
           "verdict": "PRINCIPLED NO-BEAT -- gate passes, quality bar "
                      "fails; run SATURATED (no_beat_cycles 3)"
                      if (gate and not bar) else
                      ("BANKED" if banked else "REJECTED")},
          open(f"{BASE}/stocks_engine_sat36_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat36_result.json")
