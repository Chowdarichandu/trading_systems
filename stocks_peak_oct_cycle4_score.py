#!/usr/bin/env python3
"""PEAK LAB CYCLE 4 - SCORE the frozen lever: INV-LONG stop -0.50% -> -0.65%
(target +1.25% unchanged, one exit parameter only), full Jan-Oct union
rebuild. Anchors: (A) F4 T150/S125 rebuild == cycle3 dump and union ==
cycle3 peak table; (B) INV machinery inv_rows("T125_S050") LONG ==
M1.load_inv_long() dump to the paisa. Timing invariants asserted on
the new INV leg. Paper, real Rs0, per 100 shares, Rs40/tr."""
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
TI = load_mod("TI", f"{BASE}/stocks_tuning_inv.py")
from stocks_tuning_inv_families import inv_rows
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":9173.84,"2026-02":4939.87,"2026-03":21673.47,"2026-04":-632.4,
        "2026-05":26032.03,"2026-06":-817.99,"2026-07":1962.07,"2026-08":739.35,
        "2026-09":14970.43,"2026-10":53290.52}
PREV_TOTAL = 131331.19
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

# ---- Anchor A: F4 basis + old union
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw_f4, aud_f4 = build_f4(1.50, 1.25)
dump = rd("stocks_peak_oct_cycle3_f4s125_trades.csv")
a1 = sorted(key(t) for t in raw_f4) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
inv_old = [t for t in M1.load_inv_long() if not wk(t["date"])]
bt, _ = mt(inv_old + n4 + p2f + filt_f4(raw_f4))
a2 = bt == PEAK
print("ANCHOR A1 (F4 rebuild == cycle3 dump):", a1, "| ANCHOR A2 (union == cycle3 peak):", a2, "| F4 audit:", aud_f4)
assert a1 and a2 and aud_f4["violations"] == 0

# ---- Anchor B: INV audited machinery reproduces the incumbent dump
def inv_leg(label):
    rows = [r for r in inv_rows(label) if r["direction"] == "LONG" and not wk(r["date"])]
    return [{"date": r["date"], "stock": r["stock"], "comp": "INV-LONG", "net": float(r["net"]),
             "dir": "LONG", "setup": r["setup"], "round": r["round"],
             "entry_time": r["entry_time"], "exit_reason": r["exit_reason"],
             "event_status": r["event_status"], "adr_pct": r["adr"], "day_gap_pct": r["gap_pct"],
             "entry": r["entry"], "exit_time": r["exit_time"]} for r in rows]
inv_mach050 = inv_leg("T125_S050")
ikey = lambda t: (t["date"], t["stock"], int(t["round"]), float(t["net"]), t["entry_time"])
b_ok = sorted(ikey(t) for t in inv_mach050) == sorted(ikey(t) for t in inv_old)
print(f"ANCHOR B: inv_rows(T125_S050) LONG == M1 dump: {b_ok} | machinery {len(inv_mach050)} tr vs dump {len(inv_old)} tr")
assert b_ok

# ---- Frozen lever: INV-LONG @ T125/S065, invariants asserted
inv_new = inv_leg("T125_S065")
bad_cond = [r for r in inv_rows("T125_S065") if not TI.cond_inv1(r)]
bad_pool = [t for t in inv_new if int(t["round"]) > 2 or t["entry_time"] >= "10:30" or (t["adr_pct"] or 0) < 3.0]
bad_wk = [t for t in inv_new if wk(t["date"])]
print(f"INV S065 leg: {len(inv_new)} tr | cond_inv1 violations={len(bad_cond)} | pool violations={len(bad_pool)} | weekend={len(bad_wk)}")
assert not bad_cond and not bad_pool and not bad_wk

f4 = filt_f4(raw_f4)
book_new = inv_new + n4 + p2f + f4
nt, nc = mt(book_new)
tot_new = round(sum(t["net"] for t in book_new), 2)
inv_old_oct = round(sum(t["net"] for t in inv_old if t["date"].startswith("2026-10")), 2)
inv_new_oct = round(sum(t["net"] for t in inv_new if t["date"].startswith("2026-10")), 2)
print(f"INV-LONG: S050 {len(inv_old)} tr Oct={inv_old_oct} -> S065 {len(inv_new)} tr Oct={inv_new_oct}")
print(f"\n{'month':8} {'prev':>10} {'new':>10} {'delta':>10} {'trades':>7}")
for k in sorted(PEAK):
    print(f"{k:8} {PEAK[k]:>10.2f} {nt.get(k,0.0):>10.2f} {round(nt.get(k,0.0)-PEAK[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {PREV_TOTAL:>10.2f} {tot_new:>10.2f} {round(tot_new-PREV_TOTAL,2):>10.2f} {len(book_new):>7}")
d_oct = round(nt["2026-10"] - PEAK["2026-10"], 2)
progress = d_oct >= 250
print(f"\nOctober delta: {d_oct} | progress (>= +250): {progress}")
with open(f"{BASE}/stocks_peak_oct_cycle4_inv_s065_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date","stock","direction","setup","round","entry_time","entry",
                                      "exit_reason","exit_time","exit_price","gross","net","event_status","adr","gap_pct"])
    w.writeheader()
    for r in sorted(inv_rows("T125_S065"), key=lambda x: (x["date"], x["stock"], x["round"])):
        w.writerow({k: r.get(k) for k in w.fieldnames})
json.dump({"anchorA1_ok": a1, "anchorA2_ok": a2, "anchorB_ok": b_ok, "month_table": nt, "total": tot_new,
           "trades": len(book_new), "october": nt["2026-10"], "oct_delta": d_oct,
           "inv_oct_before": inv_old_oct, "inv_oct_after": inv_new_oct,
           "inv_trades_before": len(inv_old), "inv_trades_after": len(inv_new),
           "inv_invariants": {"cond_viol": len(bad_cond), "pool_viol": len(bad_pool), "weekend": len(bad_wk)},
           "f4_audit": aud_f4, "progress": progress},
          open(f"{BASE}/stocks_peak_oct_cycle4_result.json", "w"), indent=1)
print("wrote stocks_peak_oct_cycle4_result.json + stocks_peak_oct_cycle4_inv_s065_trades.csv")
