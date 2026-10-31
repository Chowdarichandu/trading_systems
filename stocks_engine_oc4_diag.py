#!/usr/bin/env python3
"""ENGINE OC-4 STEP 1: F4@T150/S065 favourable-excursion diagnosis.
Rebuilds F4@T150 with the audited M2 machinery (anchor: raw rebuild
must equal stocks_engine_oc3_f4t150_trades.csv), filters to the
banked component (setup3 excluded, RF-1 weekend dropped), then for
every trade walks the day's 5-min bars to measure:
  - MFE during the hold (entry bar .. exit bar),
  - post-exit FIRST PASSAGE (diagnostic only, same day's later bars):
    target exits  -> +1.75% vs -0.65% (what T175 would have done)
    stop exits    -> +1.50% vs -0.80% (what stop -0.80 would have done)
Estimates from post-exit paths are ROUGH DIAGNOSTICS, not scores.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1, M = M2F.H1, M2F.H1.M

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5

H1.ensure_prep()
ns = M.get_ns(H1.WHICH)
days = M2F.days_of([f"2026-{i:02d}" for i in range(1, 11)])
CFG = {"band_hi": 1.0, "regime": "below50"}

M2F.TP, M2F.SP = 1.50, 0.65
a0 = dict(M2F._AUDIT)
raw = M2F.collect2(days, CFG)
audit = {"trades": M2F._AUDIT["trades"] - a0["trades"],
         "violations": M2F._AUDIT["violations"] - a0["violations"]}
with open(f"{BASE}/stocks_engine_oc3_f4t150_trades.csv") as f:
    dump = list(csv.DictReader(f))
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
anchor = sorted(key(t) for t in raw) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR F4@T150 rebuild == oc3 dump:", anchor, "| audit:", audit)

banked = [t for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
print("banked F4 trades:", len(banked),
      "| net:", round(sum(t["net"] for t in banked), 2),
      "| Oct net:", round(sum(t["net"] for t in banked if t["date"].startswith("2026-10")), 2))

def fav_adv(c, entry, sign):
    if sign == 1:
        return (c["high"] / entry - 1) * 100, (1 - c["low"] / entry) * 100
    return (1 - c["low"] / entry) * 100, (c["high"] / entry - 1) * 100

def analyse(trades):
    out = {"n": len(trades), "buckets": {"mfe>=1.25": 0, "mfe>=1.50": 0,
             "mfe>=1.75": 0, "mfe>=2.00": 0},
           "by_reason": {}, "tgt_post": {"to175": 0, "to_stop": 0, "both": 0, "neither": 0},
           "stp_post": {"to_target": 0, "deeper": 0, "both": 0, "neither": 0},
           "sq_mfe": {"[1.25,1.50)": 0, "[1.00,1.25)": 0, "[0.50,1.00)": 0, "<0.50": 0},
           "nonT_mfe>=1.50": 0, "est_T175": 0.0, "est_S080": 0.0}
    for t in trades:
        ctx = ns["DAYCTX"].get((t["symbol"], t["date"]))
        candles = ctx["candles"]
        ei = next(i for i, c in enumerate(candles) if c["time"] == t["entry_time"])
        xi = next(i for i, c in enumerate(candles) if c["time"] == t["exit_time"])
        sign = 1 if t["dir"] == "LONG" else -1
        entry = float(t["entry"])
        mfe = max(fav_adv(c, entry, sign)[0] for c in candles[ei:xi + 1])
        for b, th in [("mfe>=1.25", 1.25), ("mfe>=1.50", 1.50), ("mfe>=1.75", 1.75), ("mfe>=2.00", 2.00)]:
            if mfe >= th: out["buckets"][b] += 1
        r = t["exit_reason"]
        d = out["by_reason"].setdefault(r, {"n": 0, "net": 0.0})
        d["n"] += 1; d["net"] += t["net"]
        if r != "target" and mfe >= 1.50: out["nonT_mfe>=1.50"] += 1
        rest = candles[xi + 1:]
        if r == "target":
            res = "neither"; close_fav = None
            for c in rest:
                f, a = fav_adv(c, entry, sign)
                if f >= 1.75 and a >= 0.65: res = "both"; break
                if f >= 1.75: res = "to175"; break
                if a >= 0.65: res = "to_stop"; break
            out["tgt_post"][res] += 1
            if res == "to175": out["est_T175"] += 0.0025 * entry * 100
            elif res == "to_stop": out["est_T175"] -= 0.0215 * entry * 100
            elif res == "neither" and rest:
                cf = (rest[-1]["close"] / entry - 1) * 100 * sign
                cf = max(-0.65, min(1.75, cf))
                out["est_T175"] += (cf - 1.50) / 100 * entry * 100
        elif r == "stop":
            res = "neither"
            for c in rest:
                f, a = fav_adv(c, entry, sign)
                if f >= 1.50 and a >= 0.80: res = "both"; break
                if f >= 1.50: res = "to_target"; break
                if a >= 0.80: res = "deeper"; break
            out["stp_post"][res] += 1
            if res == "to_target": out["est_S080"] += 0.0215 * entry * 100
            elif res == "deeper": out["est_S080"] -= 0.0015 * entry * 100
            elif res == "neither" and rest:
                cf = (rest[-1]["close"] / entry - 1) * 100 * sign
                cf = max(-0.80, min(1.50, cf))
                out["est_S080"] += (cf + 0.65) / 100 * entry * 100
        elif r == "square_off":
            if mfe >= 1.25: out["sq_mfe"]["[1.25,1.50)"] += 1
            elif mfe >= 1.00: out["sq_mfe"]["[1.00,1.25)"] += 1
            elif mfe >= 0.50: out["sq_mfe"]["[0.50,1.00)"] += 1
            else: out["sq_mfe"]["<0.50"] += 1
    for d in out["by_reason"].values(): d["net"] = round(d["net"], 2)
    out["est_T175"] = round(out["est_T175"], 2); out["est_S080"] = round(out["est_S080"], 2)
    return out

full = analyse(banked)
octb = analyse([t for t in banked if t["date"].startswith("2026-10")])
for name, o in [("FULL PERIOD", full), ("OCTOBER", octb)]:
    print(f"\n=== {name} ({o['n']} trades) ===")
    print(" MFE-during-hold buckets:", o["buckets"])
    print(" by exit reason:", o["by_reason"])
    print(" non-target exits with MFE>=1.50 (gap-through):", o["nonT_mfe>=1.50"])
    print(" target exits, post-exit first passage to +1.75 vs -0.65:", o["tgt_post"],
          "| rough est. T175 swing Rs:", o["est_T175"])
    print(" stop exits, post-exit first passage to +1.50 vs -0.80:", o["stp_post"],
          "| rough est. S080 swing Rs:", o["est_S080"])
    print(" square-off MFE buckets:", o["sq_mfe"])
json.dump({"anchor": anchor, "audit": audit, "full": full, "october": octb},
          open(f"{BASE}/stocks_engine_oc4_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_oc4_diag.json")
