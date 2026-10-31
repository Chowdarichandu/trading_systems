#!/usr/bin/env python3
"""ENGINE SAT-10 SCORE: F4 stop -0.80% -> -0.95% (T150 unchanged),
frozen in stocks_engine_frozen.md (SAT-10 section) AFTER the
excursion diagnosis (sat10_diag) and BEFORE this ran. Anchors:
(A) rebuild at T150/S080 == oc4 dump per-trade; (B) filtered S080
union == state (779 tr / +149,365.15); (C) audit 0 violations both
builds; (D) S095 entry set == S080 entry set after filtering.
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
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1 = M2F.H1

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
STATE = {"2026-01": 12497.27, "2026-02": 3611.69, "2026-03": 22321.47,
         "2026-04": 3671.26, "2026-05": 28317.69, "2026-06": 3941.51,
         "2026-07": 3196.63, "2026-08": 1735.16, "2026-09": 19722.68,
         "2026-10": 50349.79}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 149365.15, 779, 30773.31

H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)

def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"] - a0["trades"],
             "violations": M2F._AUDIT["violations"] - a0["violations"]}
    return raw, audit

EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT")}
def keep(t):
    return (not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"
            and t["leg"] != "round2"
            and (t["symbol"], t["dir"]) not in EXCL)
def filt(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4",
             "net": float(t["net"])} for t in raw if keep(t)]

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

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]

# --- Anchor A + B + C(S080) ---
raw080, aud080 = build_f4(1.50, 0.80)
dump = rd("stocks_engine_oc4_f4s080_trades.csv")
key = lambda t: (t["date"], t["symbol"], int(t["round"]),
                 float(t["net"]), t["entry_time"])
a_ok = sorted(key(t) for t in raw080) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]),
     r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S080 rebuild == oc4 dump:", a_ok,
      f"| rebuild {len(raw080)} tr vs dump {len(dump)} tr | audit: {aud080}")
f4_080 = filt(raw080)
base_book = inv + n4 + p2f + f4_080
bt, _ = mt(base_book)
b_ok = (bt == STATE
        and round(sum(t["net"] for t in base_book), 2) == STATE_TOTAL
        and len(base_book) == STATE_TRADES)
print("ANCHOR B: filtered S080 union == state:", b_ok,
      f"| trades {len(base_book)} total "
      f"{round(sum(t['net'] for t in base_book),2)}")
ex0, top3_0 = extop3(base_book)
print(f"incumbent ex-top-3: {ex0} (top3 {top3_0}) == state "
      f"{STATE_EXTOP3}: {ex0 == STATE_EXTOP3}")
assert a_ok and b_ok, "ANCHOR FAILED — do not judge the fix"

# --- Score the frozen step ---
raw095, aud095 = build_f4(1.50, 0.95)
f4_095 = filt(raw095)
es080 = sorted((t["date"], t["symbol"], t["entry_time"])
               for t in raw080 if keep(t))
es095 = sorted((t["date"], t["symbol"], t["entry_time"])
               for t in raw095 if keep(t))
d_ok = es080 == es095
print("ANCHOR D: S095 entry set == S080 entry set:", d_ok,
      f"| {len(es095)} entries | audit S095: {aud095}")

new_book = inv + n4 + p2f + f4_095
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\nF4 component: S080 {len(f4_080)} tr "
      f"{round(sum(t['net'] for t in f4_080),2)} -> S095 {len(f4_095)} tr "
      f"{round(sum(t['net'] for t in f4_095),2)}")
print(f"\n{'month':8} {'current':>10} {'SAT-10':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")
aug_after = nt["2026-08"]
n4_shortfall = round(4020.54 - aug_after, 2)
print(f"August after: Rs{aug_after} | N4-revisit shortfall: Rs{n4_shortfall}")
print(f"October after: Rs{nt['2026-10']} | headroom "
      f"Rs{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-10) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok and d_ok and aud080["violations"] == 0 \
    and aud095["violations"] == 0
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors + audit clean: -> {ge} "
      f"(A {a_ok}, B {b_ok}, D {d_ok}, audits {aud080}/{aud095})")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

if banked:
    with open(f"{BASE}/stocks_engine_sat10_f4s095_trades.csv", "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(raw095[0].keys()))
        w.writeheader()
        for t in sorted(raw095, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(t)
    print("wrote stocks_engine_sat10_f4s095_trades.csv (new F4 dump)")

json.dump({"anchors": {"A": a_ok, "B": b_ok, "D": d_ok},
           "audit080": aud080, "audit095": aud095,
           "fix": "SAT-10-F4-S095 (stop -0.80% -> -0.95%, T150 unchanged)",
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in STATE},
           "f4_before": round(sum(t["net"] for t in f4_080), 2),
           "f4_after": round(sum(t["net"] for t in f4_095), 2),
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_anchors_audit": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": aug_after,
           "n4_revisit_august_shortfall_after": n4_shortfall},
          open(f"{BASE}/stocks_engine_sat10_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat10_result.json")
