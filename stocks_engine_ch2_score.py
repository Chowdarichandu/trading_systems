#!/usr/bin/env python3
"""ENGINE CH-2: challenger N4-V3 exit rebuild T150/S080 vs incumbent.
Spec frozen in stocks_engine_frozen.md (section CH-2, incl. the
12:10 IST supersession restoring the adoption gate).
Steps: (1) incumbent rebuild anchor == state (138,631.32 / 906);
(2) N4 replay anchor at T125/S050 must reproduce the source dump
nets per trade (bar convention determined empirically, asserted);
(3) N4 rebuilt at T150/S080 with identical entries (audit), ASTRAL
+ RF-1 filters applied; (4) assembly swap + adoption gate:
(a) all months > 0, (b) total > incumbent, (c) Oct >= 50,000,
(d) ex-top-3 not worse than incumbent.
Paper only, real Rs0, per 100 shares provisional, Rs40/trade."""
import csv, json, sys
from collections import defaultdict
from datetime import date
import importlib.util

BASE = "/home/hatch/workspace/trading"
sys.path.insert(0, BASE)
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

QTY, COST = 100, 40.0
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
STATE_MONTHS = {"2026-01": 11378.22, "2026-02": 5125.86, "2026-03": 19116.26,
                "2026-04": 1464.36, "2026-05": 29377.98, "2026-06": 172.76,
                "2026-07": 3196.63, "2026-08": 185.69, "2026-09": 18041.54,
                "2026-10": 50572.02}

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
def month_table(trades):
    m = {k: 0.0 for k in MONTHS}
    for t in trades: m[t["date"][:7]] = round(m.get(t["date"][:7], 0.0) + t["net"], 2)
    return m
def per_stock(trades):
    ps = defaultdict(float)
    for t in trades: ps[t["stock"]] += t["net"]
    return {k: round(v, 2) for k, v in ps.items()}
def ex_top3(trades):
    ps = per_stock(trades)
    tot = round(sum(ps.values()), 2)
    top = sorted(((v, k) for k, v in ps.items() if v > 0), reverse=True)[:3]
    return {"total": tot, "ex_top3": round(tot - sum(v for v, _ in top), 2),
            "top3": [(k, v) for v, k in top]}

# ---------- (1) incumbent anchor ----------
inv = [t for t in M1.load_inv_long() if not wk(t["date"]) and t["stock"] != "BDL"]
n4_old = [t for t in M1.load_n4() if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f25 = [t for t in M1.load_p2f(2.5) if not wk(t["date"])
         and t["stock"] != "ASTRAL" and t["stock"] != "HINDUNILVR"]
f4 = [{"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
      for r in rd("stocks_engine_oc4_f4s080_trades.csv")
      if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
incumbent = inv + n4_old + p2f25 + f4
im = month_table(incumbent)
inc_tot = round(sum(t["net"] for t in incumbent), 2)
anchor_inc = (im == STATE_MONTHS and inc_tot == 138631.32 and len(incumbent) == 906)
print("INCUMBENT ANCHOR:", anchor_inc, f"| trades {len(incumbent)} total {inc_tot}")
assert anchor_inc, f"incumbent anchor FAIL: {im} {inc_tot} {len(incumbent)}"
inc_x3 = ex_top3(incumbent)
print("incumbent ex-top3:", inc_x3)

# ---------- candle store ----------
def load_candles(sym):
    days = {}
    with open(f"{BASE}/data/progressive/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            days.setdefault(d, []).append({"time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"])})
    for d in days: days[d].sort(key=lambda c: c["time"])
    return days
CAND = {}
def candles_for(sym, day):
    if sym not in CAND: CAND[sym] = load_candles(sym)
    return CAND[sym].get(day, [])

def replay(candles, ei, entry, direction, tgt_pct, stp_pct, start_offset):
    """start_offset 0 = evaluate from the entry bar itself, 1 = next bar.
    Stop checked before target within a bar; square-off at 15:10 close."""
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + start_offset, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10": return "square_off", c["close"], c["time"]
    if last is not None: return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * QTY - COST, 2)

# ---------- (2) N4 replay anchor ----------
raw = rd("eq_n4deep_v3_trades_T125_janoct.csv")
def replay_all(tgt, stp, offset):
    out, bad = [], 0
    for r in raw:
        candles = candles_for(r["stock"], r["date"])
        ei = next(i for i, c in enumerate(candles) if c["time"] == r["entry_time"])
        res = replay(candles, ei, float(r["entry"]), r["direction"], tgt, stp, offset)
        if res is None: bad += 1; continue
        er, ep, et = res
        out.append({"date": r["date"], "stock": r["stock"], "direction": r["direction"],
                    "entry_time": r["entry_time"], "entry": float(r["entry"]),
                    "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
                    "net": net_of(r["direction"], float(r["entry"]), ep),
                    "src_net": float(r["net_rs_provisional_per100"]), "src_reason": r["exit_reason"]})
    return out, bad
conv = None
for offset in (0, 1):
    out, bad = replay_all(1.25, 0.50, offset)
    match = sum(1 for t in out if abs(t["net"] - t["src_net"]) < 0.011 and t["exit_reason"] == t["src_reason"])
    print(f"replay convention offset={offset}: {match}/{len(raw)} trades match (bad={bad})")
    if match == len(raw) and bad == 0: conv = offset
assert conv is not None, "N4 REPLAY ANCHOR FAIL — no convention reproduces the dump"
print("N4 REPLAY ANCHOR OK with start_offset =", conv)

# ---------- (3) rebuild at T150/S080 ----------
new_all, _ = replay_all(1.50, 0.80, conv)
audit_v = 0
same_bar = 0
for t, r in zip(new_all, raw):
    # entries must be identical to the anchor trades; exits may occur
    # inside the entry bar itself (the source engine's own convention —
    # 13 of 56 source trades exit at 09:35), so exit_time >= entry_time.
    if not (t["date"] == r["date"] and t["stock"] == r["stock"] and t["direction"] == r["direction"]
            and t["entry_time"] == "09:35" and abs(t["entry"] - float(r["entry"])) < 0.001
            and t["exit_time"] >= t["entry_time"]):
        audit_v += 1
    if t["exit_time"] == t["entry_time"]: same_bar += 1
print("timing/entry audit violations:", audit_v, "| same-bar exits (entry-bar convention):", same_bar)
assert audit_v == 0
n4_new = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
           "dir": t["direction"], "net": t["net"]}
          for t in new_all if not wk(t["date"]) and t["stock"] != "ASTRAL"]
n4_new_net = round(sum(t["net"] for t in n4_new), 2)
n4_old_net = round(sum(t["net"] for t in n4_old), 2)
print(f"N4 component: old {len(n4_old)} tr / {n4_old_net} -> new {len(n4_new)} tr / {n4_new_net} "
      f"(delta {round(n4_new_net - n4_old_net, 2)})")

# ---------- (4) assembly + gate ----------
challenger = inv + n4_new + p2f25 + f4
cm = month_table(challenger)
c_tot = round(sum(t["net"] for t in challenger), 2)
chal_x3 = ex_top3(challenger)
gate = {"a_all_months_green": all(v > 0 for v in cm.values()),
        "b_total_higher": c_tot > 138631.32,
        "c_october_floor": cm["2026-10"] >= 50000,
        "d_ex_top3_not_worse": chal_x3["ex_top3"] >= inc_x3["ex_top3"]}
adopted = all(gate.values())
print("\nINCUMBENT months:", im)
print("CHALLENGER months:", cm)
print("challenger total:", c_tot, "trades:", len(challenger))
print("challenger ex-top3:", chal_x3, "| incumbent:", inc_x3)
print("GATE:", gate, "=> ADOPTED" if adopted else "=> REJECTED")

with open(f"{BASE}/stocks_engine_ch2_n4_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "stock", "direction", "entry_time", "entry",
                                      "exit_reason", "exit_price", "exit_time", "net",
                                      "src_net_T125S050", "src_reason"])
    w.writeheader()
    for t in sorted(new_all, key=lambda x: (x["date"], x["stock"])):
        w.writerow({**{k: t[k] for k in ("date", "stock", "direction", "entry_time", "entry",
                                          "exit_reason", "exit_price", "exit_time", "net")},
                    "src_net_T125S050": t["src_net"], "src_reason": t["src_reason"]})
json.dump({"diagnosis_choice": "B (N4 exit rebuild); A not scored",
           "incumbent_anchor_ok": True, "replay_convention_offset": conv,
           "audit_violations": audit_v,
           "n4_old": {"trades": len(n4_old), "net": n4_old_net},
           "n4_new": {"trades": len(n4_new), "net": n4_new_net},
           "incumbent_months": im, "incumbent_ex_top3": inc_x3,
           "challenger_months": cm, "challenger_total": c_tot,
           "challenger_trades": len(challenger), "challenger_ex_top3": chal_x3,
           "gate": gate, "adopted": adopted},
          open(f"{BASE}/stocks_engine_ch2_result.json", "w"), indent=1)
print("wrote stocks_engine_ch2_result.json + stocks_engine_ch2_n4_trades.csv")
