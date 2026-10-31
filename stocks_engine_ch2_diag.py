#!/usr/bin/env python3
"""ENGINE CH-2 STEP 1: two-direction DIAGNOSIS (not scoring).
(A) F4-MIRROR population on above50 days: qualifying stock-days
    (10:00 premove in [0.5%,1.0%)), October above50 count, and the
    fade-direction drift expectancy 10:00 -> 15:10 (gross, rough Rs).
(B) N4-V3 excursion profile at its current T125/S050 on the
    INCUMBENT N4 set (load_n4 minus weekends minus ASTRAL):
    MFE during hold, exit-reason split, post-exit first passage
    (OC-4 method) -> rough T150/S080 swing estimate.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5

_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1, M = M2F.H1, M2F.M
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

# ---------------- (B) N4 excursion profile ----------------
n4_raw = list(csv.DictReader(open(f"{BASE}/eq_n4deep_v3_trades_T125_janoct.csv")))
inc_n4 = [r for r in n4_raw if not wk(r["date"]) and r["stock"] != "ASTRAL"]
print(f"N4 raw {len(n4_raw)} -> incumbent N4 {len(inc_n4)} "
      f"(net {round(sum(float(r['net_rs_provisional_per100']) for r in inc_n4),2)})")

def load_candles(sym, day):
    out = []
    with open(f"{BASE}/data/progressive/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            if r["timestamp"][:10] == day:
                out.append({"time": r["timestamp"][11:16], "open": float(r["open"]),
                            "high": float(r["high"]), "low": float(r["low"]),
                            "close": float(r["close"])})
    out.sort(key=lambda c: c["time"])
    return out

CACHE = {}
def candles_for(sym, day):
    if (sym, day) not in CACHE: CACHE[(sym, day)] = load_candles(sym, day)
    return CACHE[(sym, day)]

def fav_adv(c, entry, sign):
    if sign == 1: return (c["high"] / entry - 1) * 100, (1 - c["low"] / entry) * 100
    return (1 - c["low"] / entry) * 100, (c["high"] / entry - 1) * 100

B = {"n": len(inc_n4), "by_reason": {}, "buckets": {"mfe>=1.25": 0, "mfe>=1.50": 0,
     "mfe>=1.75": 0, "mfe>=2.00": 0},
     "tgt_post": {"to150": 0, "to_stop080": 0, "both": 0, "neither": 0},
     "stp_post": {"to125": 0, "to150": 0, "deeper080": 0, "neither": 0},
     "est_T150": 0.0, "est_S080": 0.0, "missing": 0}
for r in inc_n4:
    candles = candles_for(r["stock"], r["date"])
    entry = float(r["entry"]); sign = 1 if r["direction"] == "LONG" else -1
    try:
        ei = next(i for i, c in enumerate(candles) if c["time"] == r["entry_time"])
        xi = next(i for i, c in enumerate(candles) if c["time"] == r["exit_time"])
    except StopIteration:
        B["missing"] += 1; continue
    mfe = max(fav_adv(c, entry, sign)[0] for c in candles[ei:xi + 1])
    for b, th in [("mfe>=1.25", 1.25), ("mfe>=1.50", 1.50), ("mfe>=1.75", 1.75), ("mfe>=2.00", 2.00)]:
        if mfe >= th: B["buckets"][b] += 1
    reason = r["exit_reason"]
    d = B["by_reason"].setdefault(reason, {"n": 0, "net": 0.0})
    d["n"] += 1; d["net"] += float(r["net_rs_provisional_per100"])
    rest = candles[xi + 1:]
    if reason == "target":  # banked +1.25; T150 keeps holding: first passage +1.50 vs -0.80
        res = "neither"
        for c in rest:
            f, a = fav_adv(c, entry, sign)
            if f >= 1.50 and a >= 0.80: res = "both"; break
            if f >= 1.50: res = "to150"; break
            if a >= 0.80: res = "to_stop080"; break
        B["tgt_post"][res] += 1
        if res == "to150": B["est_T150"] += 0.0025 * entry * 100
        elif res == "to_stop080": B["est_T150"] -= 0.0230 * entry * 100
        elif res == "neither" and rest:
            cf = (rest[-1]["close"] / entry - 1) * 100 * sign
            cf = max(-0.80, min(1.50, cf)); B["est_T150"] += (cf - 1.25) / 100 * entry * 100
    elif reason == "stop":  # stopped at -0.50; S080 keeps holding: first passage +1.25 vs -0.80
        res = "neither"
        for c in rest:
            f, a = fav_adv(c, entry, sign)
            if f >= 1.25: res = "to125"; break
            if a >= 0.80: res = "deeper080"; break
        B["stp_post"][res] += 1
        if res == "to125": B["est_S080"] += 0.0175 * entry * 100
        elif res == "deeper080": B["est_S080"] -= 0.0030 * entry * 100
        elif res == "neither" and rest:
            cf = (rest[-1]["close"] / entry - 1) * 100 * sign
            cf = max(-0.80, min(1.25, cf)); B["est_S080"] += (cf + 0.50) / 100 * entry * 100
for d in B["by_reason"].values(): d["net"] = round(d["net"], 2)
B["est_T150"] = round(B["est_T150"], 2); B["est_S080"] = round(B["est_S080"], 2)
print("\n=== (B) N4-V3 excursions @T125/S050 ===")
print(" by_reason:", B["by_reason"]); print(" MFE buckets:", B["buckets"])
print(" target exits post-passage (+1.50 vs -0.80):", B["tgt_post"], "| rough T150 swing Rs:", B["est_T150"])
print(" stop exits post-passage (+1.25 vs -0.80):", B["stp_post"], "| rough S080 swing Rs:", B["est_S080"])
print(" rough combined T150/S080 swing Rs:", round(B["est_T150"] + B["est_S080"], 2), "| missing bars:", B["missing"])

# ---------------- (A) mirror population ----------------
H1.ensure_prep()
ns = M.get_ns(H1.WHICH)
all_days = M2F.days_of([f"2026-{i:02d}" for i in range(1, 11)])
above_days = [d for d in all_days if not H1.below50(d)]
oct_days = [d for d in all_days if d.startswith("2026-10")]
oct_above = [d for d in oct_days if not H1.below50(d)]
print(f"\n=== (A) F4-MIRROR population ===")
print(f" trading days {len(all_days)} | above50 days {len(above_days)} | October days {len(oct_days)} | October above50 {len(oct_above)}")

qual = []
for sym in ns["SYMBOLS"]:
    for day in above_days:
        ctx = ns["DAYCTX"].get((sym, day))
        if ctx is None: continue
        candles = ctx["candles"]
        pm = M.premove(candles, "10:00")
        if pm is None or abs(pm) < 0.005 or abs(pm) >= 0.010: continue
        start = next((i for i, c in enumerate(candles) if c["time"] >= "10:00"), None)
        if start is None or start + 1 >= len(candles): continue
        ref = float(candles[start]["open"])
        last = candles[-1]
        fade_sign = -1 if pm > 0 else 1
        drift_pct = fade_sign * (float(last["close"]) / ref - 1) * 100
        qual.append({"sym": sym, "day": day, "pm_pct": round(100 * pm, 3),
                     "drift_pct": round(drift_pct, 3),
                     "rough_rs": round(drift_pct / 100 * ref * 100 - 40, 2)})
n = len(qual)
pos = sum(1 for q in qual if q["drift_pct"] > 0)
print(f" qualifying capped-band stock-days on above50 days: {n}")
if n:
    print(f" fade-drift: mean {round(sum(q['drift_pct'] for q in qual)/n, 3)}% | positive {pos}/{n} "
          f"| rough Rs expectancy/trade {round(sum(q['rough_rs'] for q in qual)/n, 2)} "
          f"| rough total {round(sum(q['rough_rs'] for q in qual), 2)}")
    bym = {}
    for q in qual: bym[q["day"][:7]] = round(bym.get(q["day"][:7], 0.0) + q["rough_rs"], 2)
    print(" rough Rs by month:", bym)

json.dump({"B_n4_excursions": B, "A_mirror": {"above_days": len(above_days),
           "oct_above": len(oct_above), "qualifying": n,
           "drift_mean_pct": round(sum(q['drift_pct'] for q in qual)/n, 3) if n else None,
           "rough_rs_total": round(sum(q['rough_rs'] for q in qual), 2) if n else 0.0}},
          open(f"{BASE}/stocks_engine_ch2_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_ch2_diag.json")
