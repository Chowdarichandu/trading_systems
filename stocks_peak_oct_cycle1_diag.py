#!/usr/bin/env python3
"""PEAK LAB CYCLE 1 - DIAGNOSIS at the current (peak/state) basis.
Verifies the incumbent book (INV-LONG + N4-V3 + P2F 2.5% + F4-minus
-setup3 @ T150/S080, RF-1 book-wide) == peak state table, splits
October by component, and profiles F4 October excursions at
T150/S080 to choose between lever (a) T175 and lever (b) S095.
Candidate (c) P2F-3.0 HOME leg: pre-checked - all 33 HOME rows are
already inside the P2F 2.5% book (nested subset) = double-count,
barred; its home October is -315.00 (already in the book).
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
PEAK = {"2026-01": 12433.74, "2026-02": 4173.49, "2026-03": 20322.06,
        "2026-04": 50.73, "2026-05": 27844.38, "2026-06": -1233.49,
        "2026-07": 2096.63, "2026-08": -1484.26, "2026-09": 17413.79,
        "2026-10": 50029.72}

H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)

def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"] - a0["trades"],
             "violations": M2F._AUDIT["violations"] - a0["violations"]}
    return raw, audit

key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])

raw, aud = build_f4(1.50, 0.80)
dump = rd("stocks_engine_oc4_f4s080_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S080 rebuild == oc4 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
def filt_f4(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"]),
             "dir": t["dir"], "setup": t["setup"], "entry": float(t["entry"]),
             "entry_time": t["entry_time"], "exit_time": t["exit_time"],
             "exit_reason": t["exit_reason"], "round": int(t["round"])}
            for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
f4 = filt_f4(raw)
book = inv + n4 + p2f + f4
mt_ = defaultdict(float)
for t in book: mt_[t["date"][:7]] += t["net"]
mt_ = {k: round(v, 2) for k, v in sorted(mt_.items())}
tot = round(sum(t["net"] for t in book), 2)
print("ANCHOR B: union == peak state table:", mt_ == PEAK, "| trades:", len(book), "| total:", tot)

print("\n=== OCTOBER by component ===")
for comp, rows in [("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4", f4)]:
    o = [t for t in rows if t["date"].startswith("2026-10")]
    los = [t for t in o if t["net"] < 0]
    print(f"{comp:9} Oct {len(o):3} tr net {round(sum(t['net'] for t in o),2):>10.2f} "
          f"| losers {len(los):2} net {round(sum(t['net'] for t in los),2):>10.2f}")

print("\n=== F4 OCTOBER excursion profile @ T150/S080 ===")
ns = H1.M.get_ns(H1.WHICH)
oct_f4 = [t for t in f4 if t["date"].startswith("2026-10")]
stats = {"target": 0, "stop": 0, "square_off": 0}
reach175_hold = reach200_hold = 0
post175 = post200 = 0
stop_band = stop_deep = stop_recover = 0
for t in oct_f4:
    ctx = ns["DAYCTX"].get((t["stock"], t["date"]))
    candles = ctx["candles"]
    ei = next(i for i, c in enumerate(candles) if c["time"] == t["entry_time"])
    xi = next(i for i, c in enumerate(candles) if c["time"] == t["exit_time"])
    sgn = 1 if t["dir"] == "LONG" else -1
    e = t["entry"]
    def fav(c): return sgn * ((c["high"] if sgn > 0 else c["low"]) - e) / e * 100 if sgn > 0 else (e - c["low"]) / e * 100
    def adv(c): return (e - c["low"]) / e * 100 if sgn > 0 else (c["high"] - e) / e * 100
    hold = candles[ei:xi + 1]
    mfe = max(fav(c) for c in hold)
    stats[t["exit_reason"]] = stats.get(t["exit_reason"], 0) + 1
    if mfe >= 1.75: reach175_hold += 1
    if mfe >= 2.00: reach200_hold += 1
    rest = candles[xi + 1:]
    if rest:
        pmfe = max(fav(c) for c in rest)
        if pmfe >= 1.75: post175 += 1
        if pmfe >= 2.00: post200 += 1
    if t["exit_reason"] == "stop":
        mae_day = max(adv(c) for c in candles[ei:])
        if mae_day >= 0.95: stop_deep += 1
        else:
            stop_band += 1
            if rest and max(fav(c) for c in rest) >= 1.50: stop_recover += 1
print(f"F4 October trades: {len(oct_f4)} | exits: {stats}")
print(f"reached +1.75% WITHIN holding window: {reach175_hold} | +2.00%: {reach200_hold}")
print(f"reached +1.75% only AFTER exit (diagnostic, flatters T175): {post175} | +2.00%: {post200}")
print(f"stop-outs whose full-day adverse excursion stayed < 0.95% (would survive S095): {stop_band}, "
      f"of which later reached +1.50% same day (diagnostic): {stop_recover}")
print(f"stop-outs that fell through -0.95% anyway (S095 only loses more): {stop_deep}")
print(f"F4 October net: {round(sum(t['net'] for t in oct_f4),2)} | losers: "
      f"{sum(1 for t in oct_f4 if t['net']<0)} net {round(sum(t['net'] for t in oct_f4 if t['net']<0),2)}")
json.dump({"anchorA": a_ok, "anchorB": mt_ == PEAK, "total": tot,
           "exc": {"reach175_hold": reach175_hold, "reach200_hold": reach200_hold,
                   "post175": post175, "post200": post200, "stop_band": stop_band,
                   "stop_recover": stop_recover, "stop_deep": stop_deep,
                   "exits": stats, "oct_f4_trades": len(oct_f4)}},
          open(f"{BASE}/stocks_peak_oct_cycle1_diag.json", "w"), indent=1)
print("wrote stocks_peak_oct_cycle1_diag.json")
