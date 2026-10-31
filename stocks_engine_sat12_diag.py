#!/usr/bin/env python3
"""ENGINE SAT-12 STEP 1: F4 target-excursion diagnosis on the CURRENT
book's F4 component (T150/S095, first-signal-only, setup3 excluded,
all five direction exclusions, RF-1 weekend drop; anchor: union ==
state 779 tr / +153,263.52 asserted in-script). For every F4 TARGET
exit, walk the day's later 5-min bars up to the 15:10 square-off
(SAT-10 diag method, mirrored to the winner side): first passage to
+1.65% (the stepped target) vs -0.95% (the incumbent stop) vs
neither -> square-off close (clamped). Rough swing of ONE step
T150 -> T165, counted honestly on both sides: reach165 gains
+0.15 x entry; stop-first LOSES the banked +1.50 AND takes the stop
(swing -2.45 x entry); neither exits at close (swing close_fav-1.50).
Same-candle both-touch counts as stop-first (conservative, as in
SAT-10). Per month + August / October / full splits. Post-exit paths
are DIAGNOSTICS, not scores. Paper, real Rs0, per 100 sh, Rs40/tr."""
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

STATE = {"2026-01": 14722.77, "2026-02": 7816.34, "2026-03": 18739.16,
         "2026-04": 7744.23, "2026-05": 27400.76, "2026-06": 4105.67,
         "2026-07": 3092.38, "2026-08": 1182.43, "2026-09": 17542.75,
         "2026-10": 50917.03}
STATE_TOTAL, STATE_TRADES = 153263.52, 779

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT")}
f4rows = [r for r in rd("stocks_engine_sat10_f4s095_trades.csv")
          if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
          and r["leg"] != "round2"
          and (r["symbol"], r["dir"]) not in EXCL]
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

OLD_TP, NEW_TP, STOP = 1.50, 1.65, 0.95
def passage(trades):
    out = {"n": 0, "reach165": 0, "stop_first": 0, "neither": 0,
           "no_bars": 0, "est": 0.0, "detail": []}
    for t in trades:
        ctx = ns["DAYCTX"].get((t["symbol"], t["date"]))
        candles = ctx["candles"]
        xi = next(i for i, c in enumerate(candles)
                  if c["time"] == t["exit_time"])
        sign = 1 if t["dir"] == "LONG" else -1
        entry = float(t["entry"])
        rest = [c for c in candles[xi + 1:] if c["time"] <= "15:10"]
        res = "neither"; swing = 0.0
        for c in rest:
            f, a = fav_adv(c, entry, sign)
            if f >= NEW_TP and a >= STOP: res = "stop_first"; break
            if f >= NEW_TP: res = "reach165"; break
            if a >= STOP: res = "stop_first"; break
        if res == "reach165":
            swing = (NEW_TP - OLD_TP) * entry          # +0.15 x entry
        elif res == "stop_first":
            swing = -(STOP + OLD_TP) * entry           # -2.45 x entry
        elif rest:
            cf = (rest[-1]["close"] / entry - 1) * 100 * sign
            cf = max(-STOP, min(NEW_TP, cf))
            swing = (cf - OLD_TP) * entry
        else:
            out["no_bars"] += 1
        out["n"] += 1
        out[res] += 1
        out["est"] += swing
        out["detail"].append({"date": t["date"], "stock": t["symbol"],
                              "dir": t["dir"], "net": float(t["net"]),
                              "res": res, "swing": round(swing, 2)})
    out["est"] = round(out["est"], 2)
    return out

targets = [t for t in f4rows if t["exit_reason"] == "target"]
print(f"\nF4 target exits in current book: {len(targets)} "
      f"(net {round(sum(float(t['net']) for t in targets), 2)})")

result = {"anchor_ok": anchor_ok, "new_tp": NEW_TP, "stop": STOP,
          "groups": {}, "months": {}}
for gname, gtrades in (("FULL", targets),
                       ("AUGUST", [t for t in targets
                                   if t["date"].startswith("2026-08")]),
                       ("OCTOBER", [t for t in targets
                                    if t["date"].startswith("2026-10")])):
    o = passage(gtrades)
    result["groups"][gname] = {k: v for k, v in o.items() if k != "detail"}
    print(f"\n=== {gname} target exits (n={o['n']}) at candidate "
          f"target +{NEW_TP}% (stop -{STOP}%) ===")
    print(f" reach165 {o['reach165']} | stop_first {o['stop_first']} "
          f"| neither {o['neither']} (no_bars {o['no_bars']}) "
          f"| rough swing est Rs{o['est']}")

print(f"\n{'month':8} {'tgts':>5} {'est_swing':>10} {'state':>10} {'predicted':>10}")
pred = {}
for mk in sorted(STATE):
    sub = [t for t in targets if t["date"].startswith(mk)]
    o = passage(sub)
    pred[mk] = round(STATE[mk] + o["est"], 2)
    result["months"][mk] = {"targets": o["n"], "reach165": o["reach165"],
                            "stop_first": o["stop_first"],
                            "neither": o["neither"],
                            "est_swing": o["est"], "predicted": pred[mk]}
    print(f"{mk:8} {o['n']:>5} {o['est']:>10.2f} {STATE[mk]:>10.2f} {pred[mk]:>10.2f}")
pred_total = round(STATE_TOTAL + result["groups"]["FULL"]["est"], 2)
print(f"{'TOTAL':8} {len(targets):>5} {result['groups']['FULL']['est']:>10.2f} "
      f"{STATE_TOTAL:>10.2f} {pred_total:>10.2f}")
result["predicted_total"] = pred_total
result["predicted_all_green"] = all(v > 0 for v in pred.values())
result["predicted_october"] = pred["2026-10"]
result["predicted_october_headroom"] = round(pred["2026-10"] - 50000, 2)
result["predicted_august"] = pred["2026-08"]
support = (pred_total > STATE_TOTAL and result["predicted_all_green"]
           and pred["2026-10"] >= 50000)
result["support_test_pass"] = support
print(f"\nPREDICTED (rough): total {pred_total} | all green "
      f"{result['predicted_all_green']} | October {pred['2026-10']} "
      f"(headroom {result['predicted_october_headroom']}) "
      f"| August {pred['2026-08']}")
print("SUPPORTS FREEZING T165 (est total up AND predicted all-green "
      "AND predicted Oct >= 50,000):", support)

json.dump(result, open(f"{BASE}/stocks_engine_sat12_diag.json", "w"),
          indent=1)
print("\nwrote stocks_engine_sat12_diag.json")
