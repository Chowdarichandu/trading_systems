#!/usr/bin/env python3
"""ENGINE SAT-6: RE-MEASUREMENT + BANKING TEST of SE-1-F4R1 at the
CURRENT book (post SAT-5). Frozen in stocks_engine_frozen.md (SAT-6
section) BEFORE this ran. Anchor: current-book rebuild == state
(869 tr / +146,411.36 / Oct +52,681.54) first. The re-test only
DELETES F4 leg=='round2' trades from the pre-audited dump, so
timing validity is inherited; the anchor assertion is the gate.
Lesson 16: SAT-5 intervened on the same component (F4 x HINDUNILVR
x SHORT, 9 trades) — this run verifies that slice's leg composition
and re-derives the round2 set from scratch. Paper, real Rs0, per
100 shares, Rs40/trade, home 25."""
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

STATE = {"2026-01": 13282.30, "2026-02": 6130.34, "2026-03": 20269.77,
         "2026-04": 1516.24, "2026-05": 28714.75, "2026-06": 2893.72,
         "2026-07": 3196.63, "2026-08": 878.69, "2026-09": 16847.38,
         "2026-10": 52681.54}
STATE_TOTAL, STATE_TRADES = 146411.36, 869

# SAT-3 measurement (stocks_engine_sat3_result.json) at the post-SAT-2
# book: round2 = 70 tr / net -11.83; month nets below (net OF the legs;
# dropping them moves the union by -net). October: 8 tr / +1,551.75.
SAT3_R2_MONTHS = {"2026-01": 1261.27, "2026-02": 3641.69,
                  "2026-03": -2022.02, "2026-04": -1720.02,
                  "2026-05": 876.14, "2026-06": -1393.79,
                  "2026-08": 775.25, "2026-09": -2982.10,
                  "2026-10": 1551.75}
SAT3_R2_NET, SAT3_R2_N = -11.83, 70

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
RAW = rd("stocks_engine_oc4_f4s080_trades.csv")
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "round": r["round"], "entry_time": r["entry_time"],
        "exit_reason": r["exit_reason"], "net": float(r["net"]),
        "premove_pct": float(r["premove_pct"]), "event": r["event"]}
       for r in RAW
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
       and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")]

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

base = inv + n4 + p2f + f4
bt, _ = mt(base)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in base), 2) == STATE_TOTAL
             and len(base) == STATE_TRADES)
print("ANCHOR (current book == state):", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok, "ANCHOR FAILED"
ex0, top3_0 = extop3(base)
print(f"incumbent ex-top-3: {ex0} (top3 {top3_0})")

# Lesson-16 check INSIDE the run: leg composition of the SAT-5 frozen
# slice (F4 x HINDUNILVR x SHORT, in the book's filter space).
s5 = [r for r in RAW
      if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
      and r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT"]
s5_legs = defaultdict(int)
for r in s5: s5_legs[r["leg"]] += 1
print(f"\nSAT-5 slice leg composition: {dict(s5_legs)} "
      f"({len(s5)} trades, net {round(sum(float(r['net']) for r in s5),2)})"
      f" -> round2 legs touched by SAT-5: {s5_legs.get('round2', 0)}")

r2 = [t for t in f4 if t["leg"] == "round2"]
r2m, r2c = mt(r2)
r2net = round(sum(t["net"] for t in r2), 2)
print(f"\nF4 round2 legs AT THE CURRENT BOOK: {len(r2)} trades, "
      f"net {r2net} (winners {sum(1 for t in r2 if t['net'] > 0)}/{len(r2)})")
print("round2 net by month:", r2m)
print("round2 count by month:", r2c)
print(f"vs SAT-3: {SAT3_R2_N} trades / net {SAT3_R2_NET} / months "
      f"{SAT3_R2_MONTHS} -> IDENTICAL: "
      f"{len(r2) == SAT3_R2_N and r2net == SAT3_R2_NET and r2m == SAT3_R2_MONTHS}")
for t in sorted((t for t in r2 if t["date"].startswith("2026-10")),
                key=lambda t: t["date"]):
    print(f"  OCT {t['date']} {t['stock']:12} {t['dir']:5} "
          f"{t['setup']:24} entry {t['entry_time']} "
          f"{t['exit_reason']:10} net {t['net']:9.2f}")

new_f4 = [t for t in f4 if t["leg"] != "round2"]
new_book = inv + n4 + p2f + new_f4
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'current':>10} {'F4R1-now':>10} {'delta-now':>10}"
      f" {'trades':>7}")
for k in sorted(STATE):
    d_now = round(nt.get(k, 0.0) - STATE[k], 2)
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} {d_now:>10.2f}"
          f" {nc.get(k,0):>7}")
d_tot = round(tot_new - STATE_TOTAL, 2)
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} {d_tot:>10.2f}"
      f" {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")

oct_cost_now = round(STATE["2026-10"] - nt["2026-10"], 2)
print(f"\nF4R1 October cost NOW: Rs{oct_cost_now} | October under F4R1: "
      f"Rs{nt['2026-10']} | headroom after: Rs{round(nt['2026-10']-50000,2)}"
      f" (before: Rs2,681.54)")
aug_after = nt["2026-08"]
n4_shortfall = round(4020.54 - aug_after, 2)
print(f"August under F4R1: Rs{aug_after} | N4-revisit August shortfall "
      f"(needs >= Rs4,020.54): Rs{n4_shortfall} (was Rs3,141.85)")

print("\n=== SATURATION GATE (frozen SAT-6) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
banked = all([ga, gb, gc])
print("BANKED:", banked)

json.dump({"anchor_ok": anchor_ok, "fix": "SAT-6-SE1-F4R1-BANK",
           "sat5_slice_legs": dict(s5_legs),
           "round2_trades_now": len(r2), "round2_net_now": r2net,
           "round2_months_now": r2m,
           "round2_identical_to_sat3":
               bool(len(r2) == SAT3_R2_N and r2net == SAT3_R2_NET
                    and r2m == SAT3_R2_MONTHS),
           "oct_cost_now": oct_cost_now,
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas_now": {k: round(nt.get(k, 0.0) - STATE[k], 2)
                          for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": aug_after,
           "n4_revisit_august_shortfall_after": n4_shortfall},
          open(f"{BASE}/stocks_engine_sat6_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat6_result.json")
