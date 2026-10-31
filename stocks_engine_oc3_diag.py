#!/usr/bin/env python3
"""ENGINE OC-3 STEP 1: diagnose the residual October gap (Rs4,418.02).
Rebuilds the CURRENT working book from audited dumps (INV-LONG + N4-V3 +
P2F 2.5% + F4-minus-setup3, RF-1 book-wide) and asserts the state anchor
(986 tr, +107,227.76, Oct +45,581.98) BEFORE any diagnosis number is used.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, datetime, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("M1", "/home/hatch/workspace/trading/stocks_M1.py")
M1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M1)
BASE = "/home/hatch/workspace/trading"
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
f4 = []
for r in rd("stocks_M2_F4_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection": continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"]),
               "dir": r["dir"], "setup": r["setup"], "leg": r["leg"], "round": r["round"],
               "entry_time": r["entry_time"], "exit_time": r["exit_time"],
               "entry": float(r["entry"]), "exit": float(r["exit"]),
               "exit_reason": r["exit_reason"], "premove_pct": float(r["premove_pct"]),
               "event": r["event"]})
book = inv + n4 + p2f + f4

STATE = {"2026-01": 14489.91, "2026-02": -1813.21, "2026-03": 13422.38, "2026-04": -7042.44,
         "2026-05": 26188.71, "2026-06": -2270.04, "2026-07": 2151.71, "2026-08": 864.98,
         "2026-09": 15653.78, "2026-10": 45581.98}
def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}
bt, bc = mt(book)
print("ANCHOR month table == state:", bt == STATE, "| trades:", len(book),
      "| total:", round(sum(t['net'] for t in book), 2), "(expect 986 / 107227.76)")

oct_all = [t for t in book if t["date"].startswith("2026-10")]
print("\n=== OCTOBER BY COMPONENT ===")
for comp, rows in (("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4-s3", f4)):
    o = [t for t in rows if t["date"].startswith("2026-10")]
    los = [t for t in o if t["net"] < 0]
    print(f"{comp}: {len(o)} tr net={round(sum(t['net'] for t in o),2)} | losers {len(los)} net={round(sum(t['net'] for t in los),2)}")

def agg(rows, key, label):
    d = defaultdict(lambda: [0, 0.0, 0])
    for x in rows:
        k = key(x); d[k][0] += 1; d[k][1] += x["net"]; d[k][2] += 1 if x["net"] > 0 else 0
    print(f"  [{label}]")
    for k, (n, v, w) in sorted(d.items(), key=lambda kv: kv[1][1]):
        print(f"    {k}: n={n} net={round(v,2)} win={w}/{n}")

inv_o = [t for t in inv if t["date"].startswith("2026-10")]
inv_o_los = [t for t in inv_o if t["net"] < 0]
print(f"\n=== INV-LONG OCTOBER: {len(inv_o)} tr, losers {len(inv_o_los)} net={round(sum(t['net'] for t in inv_o_los),2)} ===")
agg(inv_o_los, lambda x: x["setup"], "losers by setup")
agg(inv_o, lambda x: x["setup"], "ALL Oct by setup")
agg(inv_o_los, lambda x: x["stock"], "losers by stock")
agg(inv_o_los, lambda x: x["date"], "losers by date")
agg(inv_o_los, lambda x: x["exit_reason"], "losers by exit")
agg(inv_o_los, lambda x: x["event_status"], "losers by event")
agg(inv_o_los, lambda x: "before10" if x["entry_time"] < "10:00" else ("10-12" if x["entry_time"] < "12:00" else "after12"), "losers by entry bucket")
agg(inv_o_los, lambda x: f"round{x['round']}", "losers by round")
# INV-LONG full period by setup (for gate justification)
print("\n=== INV-LONG FULL PERIOD by setup ===")
agg(inv, lambda x: x["setup"], "full by setup")
agg(inv, lambda x: "before10" if x["entry_time"] < "10:00" else ("10-12" if x["entry_time"] < "12:00" else "after12"), "full by entry bucket")
agg(inv, lambda x: x["event_status"], "full by event")

print("\n=== N4-V3 OCTOBER trades (all) ===")
for t in sorted([t for t in n4 if t["date"].startswith("2026-10")], key=lambda x: x["date"]):
    print(f"  {t['date']} {t['stock']} {t['dir']} net={t['net']} exit={t['exit_reason']}")
print("N4 FULL PERIOD net:", round(sum(t['net'] for t in n4), 2), "trades:", len(n4))
n4m, _ = mt(n4); print("N4 by month:", n4m)
print("\n=== P2F OCTOBER trades (all) ===")
for t in sorted([t for t in p2f if t["date"].startswith("2026-10")], key=lambda x: x["date"]):
    print(f"  {t['date']} {t['stock']} {t['dir']} net={t['net']} exit={t['exit_reason']} R={t['R']} react={t['reaction_ret_pct']}")
print("P2F FULL PERIOD net:", round(sum(t['net'] for t in p2f), 2), "trades:", len(p2f))
p2fm, _ = mt(p2f); print("P2F by month:", p2fm)

f4_o = [t for t in f4 if t["date"].startswith("2026-10")]
f4_o_los = [t for t in f4_o if t["net"] < 0]
print(f"\n=== F4-s3 OCTOBER: {len(f4_o)} tr net={round(sum(t['net'] for t in f4_o),2)}; losers {len(f4_o_los)} net={round(sum(t['net'] for t in f4_o_los),2)} ===")
agg(f4_o, lambda x: x["exit_reason"], "Oct ALL by exit_reason")
agg(f4_o_los, lambda x: x["exit_reason"], "Oct losers by exit_reason")
def band(x):
    p = abs(x["premove_pct"])
    return "[0.5,0.75)" if p < 0.75 else "[0.75,1.0)"
agg(f4_o, band, "Oct ALL by premove band")
agg(f4_o_los, band, "Oct losers by premove band")
agg(f4_o, lambda x: x["dir"], "Oct ALL by dir")
agg(f4_o_los, lambda x: x["dir"], "Oct losers by dir")
agg(f4_o, lambda x: x["entry_time"][:2] + ":00", "Oct ALL by entry hour")
agg(f4_o_los, lambda x: x["entry_time"][:2] + ":00", "Oct losers by entry hour")
agg(f4_o, lambda x: x["setup"], "Oct ALL by setup")
agg(f4_o, lambda x: x["leg"], "Oct ALL by leg")
agg(f4_o, lambda x: f"round{x['round']}", "Oct ALL by round")
agg(f4_o_los, lambda x: x["stock"], "Oct losers by stock")

def progress(x):
    # fraction of the +1.25% target distance travelled by the realised exit
    s = 1 if x["dir"] == "LONG" else -1
    return s * (x["exit"] - x["entry"]) / x["entry"] / 0.0125
print("\n--- F4-s3 October exit-progress (fraction of target distance at exit) ---")
for reason in sorted({t["exit_reason"] for t in f4_o}):
    rows = [t for t in f4_o if t["exit_reason"] == reason]
    ps = sorted(progress(t) for t in rows)
    near = [p for p in ps if 0.6 <= p < 1.0]
    print(f"  {reason}: n={len(rows)} net={round(sum(t['net'] for t in rows),2)} "
          f"progress min/med/max={ps[0]:.2f}/{ps[len(ps)//2]:.2f}/{ps[-1]:.2f} | 0.6<=p<1.0 count={len(near)}")

print("\n=== F4-s3 FULL PERIOD structure ===")
agg(f4, lambda x: x["exit_reason"], "full by exit_reason")
agg(f4, lambda x: x["entry_time"][:2] + ":00", "full by entry hour")
agg(f4, lambda x: "entry>=12:00" if x["entry_time"] >= "12:00" else "entry<12:00", "full by 12:00 cutoff")
f4late_o = [t for t in f4_o if t["entry_time"] >= "12:00"]
print(f"  F4 Oct entries>=12:00: {len(f4late_o)} tr net={round(sum(t['net'] for t in f4late_o),2)}")
agg(f4, band, "full by premove band")
agg(f4, lambda x: x["setup"], "full by setup")
agg(f4, lambda x: x["leg"], "full by leg")
agg(f4, lambda x: f"round{x['round']}", "full by round")
agg(f4, lambda x: x["dir"], "full by dir")
# full-period exit progress for non-target exits
print("--- F4-s3 FULL exit-progress for non-target exits ---")
for reason in sorted({t["exit_reason"] for t in f4}):
    if reason == "target": continue
    rows = [t for t in f4 if t["exit_reason"] == reason]
    ps = [progress(t) for t in rows]
    near = [p for p in ps if 0.6 <= p < 1.0]
    print(f"  {reason}: n={len(rows)} net={round(sum(t['net'] for t in rows),2)} | 0.6<=p<1.0 count={len(near)}")
# union October by stock / by day (weakest)
print("\n=== UNION OCTOBER ===")
agg(oct_all, lambda x: x["stock"], "union Oct by stock")
agg(oct_all, lambda x: x["date"], "union Oct by date")
json.dump({"anchor_ok": bt == STATE}, open(f"{BASE}/stocks_engine_oc3_diag.json", "w"))
print("\nDONE diag")
