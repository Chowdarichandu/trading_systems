#!/usr/bin/env python3
"""ENGINE SAT-10 STEP 1: F4 stop-excursion diagnosis on the CURRENT
book's F4 component (T150/S080, first-signal-only, setup3 excluded,
all five direction exclusions, RF-1 weekend drop; anchor: union ==
state 779 tr / +149,365.15 asserted in-script). For every F4 STOP
exit, walk the day's later 5-min bars (OC-4 / SAT-2 diag3 method):
first passage to +1.50% (rescue under a wider stop) vs -0.95% (the
wider stop's extra cost) vs neither -> day close (clamped). Rough
swing estimate for ONE step S080 -> S095, per month + August /
October / full splits. Post-exit paths are DIAGNOSTICS, not scores.
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
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1, M = M2F.H1, M2F.H1.M

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 12497.27, "2026-02": 3611.69, "2026-03": 22321.47,
         "2026-04": 3671.26, "2026-05": 28317.69, "2026-06": 3941.51,
         "2026-07": 3196.63, "2026-08": 1735.16, "2026-09": 19722.68,
         "2026-10": 50349.79}
STATE_TOTAL, STATE_TRADES = 149365.15, 779

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4rows = [r for r in rd("stocks_engine_oc4_f4s080_trades.csv")
          if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
          and r["leg"] != "round2"
          and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
          and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
          and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")
          and not (r["symbol"] == "UNITDSPR" and r["dir"] == "SHORT")
          and not (r["symbol"] == "HINDCOPPER" and r["dir"] == "SHORT")]
f4 = [{"date": r["date"], "stock": r["symbol"], "net": float(r["net"])}
      for r in f4rows]
base = inv + n4 + p2f + f4
m = defaultdict(float)
for t in base: m[t["date"][:7]] += t["net"]
bt = {k: round(m[k], 2) for k in sorted(m)}
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in base), 2) == STATE_TOTAL
             and len(base) == STATE_TRADES)
print("ANCHOR (current book == state):", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok, "ANCHOR FAILED"
print(f"current F4 component: {len(f4rows)} trades, "
      f"net {round(sum(float(r['net']) for r in f4rows), 2)}")
by_exit = defaultdict(lambda: [0, 0.0])
for r in f4rows:
    by_exit[r["exit_reason"]][0] += 1
    by_exit[r["exit_reason"]][1] += float(r["net"])
print("F4 exits: " + " | ".join(
    f"{k} n={v[0]} {round(v[1],2)}" for k, v in sorted(by_exit.items())))

H1.ensure_prep()
ns = M.get_ns(H1.WHICH)

def fav_adv(c, entry, sign):
    if sign == 1:
        return (c["high"] / entry - 1) * 100, (1 - c["low"] / entry) * 100
    return (1 - c["low"] / entry) * 100, (c["high"] / entry - 1) * 100

WIDE = 0.95
def passage(trades):
    out = {"n": 0, "to_target": 0, "deeper": 0, "neither": 0,
           "neither_flatplus": 0, "est": 0.0, "detail": []}
    for t in trades:
        ctx = ns["DAYCTX"].get((t["symbol"], t["date"]))
        candles = ctx["candles"]
        ei = next(i for i, c in enumerate(candles) if c["time"] == t["entry_time"])
        xi = next(i for i, c in enumerate(candles) if c["time"] == t["exit_time"])
        sign = 1 if t["dir"] == "LONG" else -1
        entry = float(t["entry"])
        rest = candles[xi + 1:]
        res = "neither"; swing = 0.0; close_fav = None
        for c in rest:
            f, a = fav_adv(c, entry, sign)
            if f >= 1.50 and a >= WIDE: res = "both"; break
            if f >= 1.50: res = "to_target"; break
            if a >= WIDE: res = "deeper"; break
        if res == "to_target":
            swing = (1.50 + 0.80) / 100 * entry * 100
        elif res in ("deeper", "both"):
            swing = -(WIDE - 0.80) / 100 * entry * 100
        elif rest:
            cf = (rest[-1]["close"] / entry - 1) * 100 * sign
            close_fav = cf
            cf = max(-WIDE, min(1.50, cf))
            swing = (cf + 0.80) / 100 * entry * 100
        out["n"] += 1
        out[res if res != "both" else "deeper"] += 1
        if res == "neither" and close_fav is not None and close_fav >= 0:
            out["neither_flatplus"] += 1
        out["est"] += swing
        out["detail"].append({"date": t["date"], "stock": t["symbol"],
                              "dir": t["dir"], "net": float(t["net"]),
                              "res": res, "swing": round(swing, 2)})
    out["est"] = round(out["est"], 2)
    return out

stops = [t for t in f4rows if t["exit_reason"] == "stop"]
print(f"\nF4 stop exits in current book: {len(stops)} "
      f"(net {round(sum(float(t['net']) for t in stops), 2)})")

result = {"anchor_ok": anchor_ok, "wide": WIDE, "groups": {}, "months": {}}
for gname, gtrades in (("FULL", stops),
                       ("AUGUST", [t for t in stops if t["date"].startswith("2026-08")]),
                       ("OCTOBER", [t for t in stops if t["date"].startswith("2026-10")])):
    o = passage(gtrades)
    result["groups"][gname] = {k: v for k, v in o.items() if k != "detail"}
    print(f"\n=== {gname} stop exits (n={o['n']}) at candidate stop -{WIDE}% ===")
    print(f" to_target(rescue) {o['to_target']} | deeper {o['deeper']} "
          f"| neither {o['neither']} (of which closed >= flat: "
          f"{o['neither_flatplus']}) | rough swing est Rs{o['est']}")

print(f"\n{'month':8} {'stops':>5} {'est_swing':>10} {'state':>10} {'predicted':>10}")
pred = {}
for mk in sorted(STATE):
    sub = [t for t in stops if t["date"].startswith(mk)]
    o = passage(sub)
    pred[mk] = round(STATE[mk] + o["est"], 2)
    result["months"][mk] = {"stops": o["n"], "to_target": o["to_target"],
                            "deeper": o["deeper"], "neither": o["neither"],
                            "est_swing": o["est"], "predicted": pred[mk]}
    print(f"{mk:8} {o['n']:>5} {o['est']:>10.2f} {STATE[mk]:>10.2f} {pred[mk]:>10.2f}")
pred_total = round(STATE_TOTAL + result["groups"]["FULL"]["est"], 2)
print(f"{'TOTAL':8} {len(stops):>5} {result['groups']['FULL']['est']:>10.2f} "
      f"{STATE_TOTAL:>10.2f} {pred_total:>10.2f}")
result["predicted_total"] = pred_total
result["predicted_all_green"] = all(v > 0 for v in pred.values())
result["predicted_october"] = pred["2026-10"]
print(f"\nPREDICTED (rough): total {pred_total} | all green "
      f"{result['predicted_all_green']} | October {pred['2026-10']} "
      f"| August {pred['2026-08']}")
print("SUPPORTS FREEZING S095 (est total up AND predicted all-green "
      "AND predicted Oct >= 50,000):",
      pred_total > STATE_TOTAL and result["predicted_all_green"]
      and pred["2026-10"] >= 50000)

json.dump(result, open(f"{BASE}/stocks_engine_sat10_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat10_diag.json")
