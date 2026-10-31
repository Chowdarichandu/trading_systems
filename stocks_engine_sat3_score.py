#!/usr/bin/env python3
"""ENGINE SAT-3: RE-MEASUREMENT of SE-1-F4R1 at the CURRENT book
(post SAT-1/SAT-2). Frozen in stocks_engine_frozen.md (SAT-3
section) BEFORE this ran. Anchor: current-book rebuild == state
(878 tr / +143,747.36 / Oct +51,364.74) first. The re-test only
DELETES F4 leg=='round2' trades from the pre-audited dump, so
timing validity is inherited; the anchor assertion is the gate.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
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

# SE-1 measurement (stocks_engine_se1_result.json, verified): the same
# deletion at the SE-1 book (+131,646.79 / 934 tr). Deltas = effect of
# dropping round2 legs at that book.
SE1_STATE = {"2026-01": 12433.74, "2026-02": 4173.49, "2026-03": 20322.06,
             "2026-04": 50.73, "2026-05": 27844.38, "2026-06": -1233.49,
             "2026-07": 2096.63, "2026-08": -1484.26, "2026-09": 17413.79,
             "2026-10": 50029.72}
SE1_NEW = {"2026-01": 11172.47, "2026-02": 531.80, "2026-03": 22344.08,
           "2026-04": 1770.75, "2026-05": 27973.88, "2026-06": 160.30,
           "2026-07": 2096.63, "2026-08": -1913.83, "2026-09": 19885.32,
           "2026-10": 48477.97}
SE1_DELTA = {k: round(SE1_NEW[k] - SE1_STATE[k], 2) for k in SE1_STATE}

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

r2 = [t for t in f4 if t["leg"] == "round2"]
r2m, r2c = mt(r2)
print(f"\nF4 round2 legs AT THE CURRENT BOOK: {len(r2)} trades, "
      f"net {round(sum(t['net'] for t in r2),2)} "
      f"(winners {sum(1 for t in r2 if t['net'] > 0)}/{len(r2)})")
print("round2 net by month:", r2m)
print("round2 count by month:", r2c)
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
      f" {'delta-SE1':>10} {'trades':>7}")
for k in sorted(STATE):
    d_now = round(nt.get(k, 0.0) - STATE[k], 2)
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} {d_now:>10.2f}"
          f" {SE1_DELTA[k]:>10.2f} {nc.get(k,0):>7}")
d_tot = round(tot_new - STATE_TOTAL, 2)
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} {d_tot:>10.2f}"
      f" {852.58:>10.2f} {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")

oct_cost_now = round(STATE["2026-10"] - nt["2026-10"], 2)
print(f"\nF4R1 October cost: SE-1 measured Rs1,551.75 -> NOW "
      f"Rs{oct_cost_now} | October headroom now Rs1,364.74")

print("\n=== SATURATION GATE (frozen SAT-3) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
within250 = (not gc) and nt["2026-10"] >= 49750
shortfall = round(50000 - nt["2026-10"], 2) if not gc else 0.0
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"within-Rs250-below-floor (record shortfall, no bank): {within250}"
      f" | shortfall Rs{shortfall}")
banked = all([ga, gb, gc])
print("BANKED:", banked)

json.dump({"anchor_ok": anchor_ok, "fix": "SAT-3-F4R1-REMEASURE",
           "round2_trades_now": len(r2),
           "round2_net_now": round(sum(t["net"] for t in r2), 2),
           "round2_months_now": r2m,
           "oct_cost_se1": 1551.75, "oct_cost_now": oct_cost_now,
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas_now": {k: round(nt.get(k, 0.0) - STATE[k], 2)
                          for k in STATE},
           "deltas_se1": SE1_DELTA,
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc},
           "oct_within_250_below_floor": within250,
           "oct_floor_shortfall": shortfall},
          open(f"{BASE}/stocks_engine_sat3_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat3_result.json")
