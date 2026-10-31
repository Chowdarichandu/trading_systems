#!/usr/bin/env python3
"""ENGINE SAT-2 STEP 2: score frozen fix SAT-2-F4-INDUSTOWER-LONG
(F4 no longer takes LONG signals on INDUSTOWER; all else identical
incl. RF-1, AU-1/JU-1/JN-1/SAT-1 exclusions) on the full Jan-Oct
union from audited dumps. Anchor: ungated rebuild == state
(+143,386.24 / 896 tr) first. Timing: the fix only DELETES trades
from pre-audited dumps and creates none, so entry timing validity
is inherited; anchor assertion is the gate. Paper, real Rs0,
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
print("ANCHOR:", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok
ex0, top3_0 = extop3(base)
print(f"incumbent ex-top-3: {ex0} (top3 {top3_0})")

removed = [t for t in f4
           if t["stock"] == "INDUSTOWER" and t["dir"] == "LONG"]
print(f"\nremoved F4 INDUSTOWER LONG trades: {len(removed)} "
      f"net {round(sum(t['net'] for t in removed),2)} "
      f"winners {sum(1 for t in removed if t['net'] > 0)}/{len(removed)}")
for t in sorted(removed, key=lambda t: t["date"]):
    print(f"  {t['date']} {t['setup']:24} entry {t['entry_time']} "
          f"{t['exit_reason']:10} net {t['net']:9.2f}")
rm, _ = mt(removed)
print("removed by month:", rm)

new_f4 = [t for t in f4
          if not (t["stock"] == "INDUSTOWER" and t["dir"] == "LONG")]
new_book = inv + n4 + p2f + new_f4
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'state':>10} {'new':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | ex-top-3 delta "
      f"{round(ex1-ex0,2)}")

aug_delta = round(nt["2026-08"] - STATE["2026-08"], 2)
print("\n=== SATURATION GATE (frozen SAT-2) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
banked = all([ga, gb, gc])
print("BANKED (a,b,c):", banked)

# CH-2 N4-rebuild revisit accounting (August delta from the CH-2 record)
N4_AUG_DELTA = -3834.85
aug_after_n4 = round(nt["2026-08"] + N4_AUG_DELTA, 2)
shortfall = round(3834.85 - aug_delta, 2)
print(f"\nREVISIT: August thickening achieved: Rs{aug_delta} of the "
      f"Rs3,834.85 needed -> shortfall Rs{shortfall}")
print(f"REVISIT: August after hypothetical N4 re-apply: "
      f"{nt['2026-08']} {N4_AUG_DELTA:+.2f} = {aug_after_n4} "
      f"-> N4 rebuild {'ADOPTABLE' if aug_after_n4 > 0 else 'STILL BLOCKED'}")

json.dump({"anchor_ok": anchor_ok, "fix": "SAT-2-F4-INDUSTOWER-LONG",
           "removed_trades": len(removed),
           "removed_net": round(sum(t["net"] for t in removed), 2),
           "removed_months": rm,
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "august_delta": aug_delta,
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc},
           "august_after_n4_reapply": aug_after_n4,
           "august_revisit_shortfall": shortfall},
          open(f"{BASE}/stocks_engine_sat2_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat2_result.json")
