#!/usr/bin/env python3
"""ENGINE SAT-2 STEP 1c: F4 stop-excursion diagnosis on the CURRENT
component (T150/S080, setup3 + GODREJCP-SHORT + weekend filtered;
anchor: union == state 896 tr / +143,386.24 asserted in diag 1).
For every F4 STOP exit, walk the day's later 5-min bars (OC-4
method): first passage to +1.50% (rescue under a wider stop) vs
-0.95% / -1.10% (the wider stop's extra cost), or neither -> day
close. Rough swing estimates for S095 and S110, split August /
October / full period. Post-exit paths are DIAGNOSTICS, not scores.
Paper, real Rs0, per 100 sh, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
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
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

H1.ensure_prep()
ns = M.get_ns(H1.WHICH)

f4 = [r for r in rd("stocks_engine_oc4_f4s080_trades.csv")
      if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
      and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")]
print(f"current F4 component: {len(f4)} trades, "
      f"net {round(sum(float(r['net']) for r in f4), 2)}")

def fav_adv(c, entry, sign):
    if sign == 1:
        return (c["high"] / entry - 1) * 100, (1 - c["low"] / entry) * 100
    return (1 - c["low"] / entry) * 100, (c["high"] / entry - 1) * 100

def passage(trades, wide):
    """first passage after a stop exit: target vs -wide% vs neither"""
    out = {"n": 0, "to_target": 0, "deeper": 0, "neither": 0, "est": 0.0,
           "detail": []}
    for t in trades:
        ctx = ns["DAYCTX"].get((t["symbol"], t["date"]))
        candles = ctx["candles"]
        ei = next(i for i, c in enumerate(candles) if c["time"] == t["entry_time"])
        xi = next(i for i, c in enumerate(candles) if c["time"] == t["exit_time"])
        sign = 1 if t["dir"] == "LONG" else -1
        entry = float(t["entry"])
        rest = candles[xi + 1:]
        res = "neither"; swing = 0.0
        for c in rest:
            f, a = fav_adv(c, entry, sign)
            if f >= 1.50 and a >= wide: res = "both"; break
            if f >= 1.50: res = "to_target"; break
            if a >= wide: res = "deeper"; break
        if res == "to_target":
            swing = (1.50 + 0.80) / 100 * entry * 100
        elif res == "deeper":
            swing = -(wide - 0.80) / 100 * entry * 100
        elif res == "both":
            swing = -(wide - 0.80) / 100 * entry * 100  # conservative
        elif rest:
            cf = (rest[-1]["close"] / entry - 1) * 100 * sign
            cf = max(-wide, min(1.50, cf))
            swing = (cf + 0.80) / 100 * entry * 100
        out["n"] += 1; out[res if res != "both" else "deeper"] += 1
        out["est"] += swing
        out["detail"].append({"date": t["date"], "stock": t["symbol"],
                              "dir": t["dir"], "net": float(t["net"]),
                              "res": res, "swing": round(swing, 2)})
    out["est"] = round(out["est"], 2)
    return out

stops = [t for t in f4 if t["exit_reason"] == "stop"]
groups = {"AUGUST": [t for t in stops if t["date"].startswith("2026-08")],
          "OCTOBER": [t for t in stops if t["date"].startswith("2026-10")],
          "FULL": stops}
result = {}
for gname, gtrades in groups.items():
    result[gname] = {}
    for wide in (0.95, 1.10):
        o = passage(gtrades, wide)
        result[gname][str(wide)] = o
        print(f"\n=== {gname} stop exits (n={o['n']}) at candidate stop -{wide}% ===")
        print(f" to_target(rescue) {o['to_target']} | deeper {o['deeper']} "
              f"| neither {o['neither']} | rough swing est Rs{o['est']}")
        if gname == "AUGUST":
            for d in sorted(o["detail"], key=lambda d: d["swing"]):
                print(f"   {d['date']} {d['stock']:12} {d['dir']:5} "
                      f"net {d['net']:9.2f} -> {d['res']:9} swing {d['swing']:9.2f}")

# context: exit structure of current F4 by month for Aug/Oct
for mname in ("2026-08", "2026-10"):
    sub = [t for t in f4 if t["date"].startswith(mname)]
    by = defaultdict(lambda: [0, 0.0])
    for t in sub: by[t["exit_reason"]][0] += 1; by[t["exit_reason"]][1] += float(t["net"])
    print(f"\nF4 {mname}: " + " | ".join(
        f"{k} n={v[0]} {round(v[1],2)}" for k, v in sorted(by.items())))

json.dump(result, open(f"{BASE}/stocks_engine_sat2_diag3.json", "w"), indent=1)
print("\nwrote stocks_engine_sat2_diag3.json")
