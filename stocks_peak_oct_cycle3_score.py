#!/usr/bin/env python3
"""PEAK LAB CYCLE 3 - SCORE the frozen lever: F4 stop -1.10% -> -1.25%
(target +1.50% unchanged), full Jan-Oct union rebuild. Anchors: the
T150/S110 rebuild must first reproduce the cycle2 dump and the cycle2
peak table exactly. Timing audit asserted on the new build.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1 = M2F.H1
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":10605.83,"2026-02":6441.5,"2026-03":24862.22,"2026-04":-3577.04,
        "2026-05":25950.59,"2026-06":-1070.86,"2026-07":2002.22,"2026-08":-2949.53,
        "2026-09":17074.58,"2026-10":52428.5}
PREV_TOTAL = 131768.01
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
def filt_f4(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"])}
            for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k],2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
raw0, aud0 = build_f4(1.50, 1.10)
dump = rd("stocks_peak_oct_cycle2_f4s110_trades.csv")
a_ok = sorted(key(t) for t in raw0) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
bt, _ = mt(inv + n4 + p2f + filt_f4(raw0))
b_ok = bt == PEAK
print("ANCHOR A (rebuild == cycle2 dump):", a_ok, "| ANCHOR B (union == cycle2 peak table):", b_ok, "| audit base:", aud0)
assert a_ok and b_ok and aud0["violations"] == 0
raw_new, aud_new = build_f4(1.50, 1.25)
assert aud_new["violations"] == 0, f"TIMING AUDIT FAILED on new build: {aud_new}"
f4_new = filt_f4(raw_new)
book_new = inv + n4 + p2f + f4_new
nt, nc = mt(book_new)
tot_new = round(sum(t["net"] for t in book_new), 2)
f4_old_oct = round(sum(t["net"] for t in filt_f4(raw0) if t["date"].startswith("2026-10")), 2)
f4_new_oct = round(sum(t["net"] for t in f4_new if t["date"].startswith("2026-10")), 2)
print(f"F4: S110 {len(filt_f4(raw0))} tr Oct={f4_old_oct} -> S125 {len(f4_new)} tr Oct={f4_new_oct} | audit new: {aud_new}")
print(f"\n{'month':8} {'prev':>10} {'S125':>10} {'delta':>10} {'trades':>7}")
for k in sorted(PEAK):
    print(f"{k:8} {PEAK[k]:>10.2f} {nt.get(k,0.0):>10.2f} {round(nt.get(k,0.0)-PEAK[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {PREV_TOTAL:>10.2f} {tot_new:>10.2f} {round(tot_new-PREV_TOTAL,2):>10.2f} {len(book_new):>7}")
d_oct = round(nt["2026-10"] - PEAK["2026-10"], 2)
progress = d_oct >= 250 and aud_new["violations"] == 0 and a_ok and b_ok
print(f"\nOctober delta: {d_oct} | progress (>= +250, audit clean): {progress}")
with open(f"{BASE}/stocks_peak_oct_cycle3_f4s125_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(raw_new[0].keys())); w.writeheader()
    for t in sorted(raw_new, key=lambda x: (x["date"], x["symbol"])): w.writerow(t)
json.dump({"anchorA_ok": a_ok, "anchorB_ok": b_ok, "month_table": nt, "total": tot_new,
           "trades": len(book_new), "october": nt["2026-10"], "oct_delta": d_oct,
           "f4_oct_before": f4_old_oct, "f4_oct_after": f4_new_oct,
           "audit_new": aud_new, "progress": progress},
          open(f"{BASE}/stocks_peak_oct_cycle3_result.json", "w"), indent=1)
print("wrote stocks_peak_oct_cycle3_result.json + stocks_peak_oct_cycle3_f4s125_trades.csv")
