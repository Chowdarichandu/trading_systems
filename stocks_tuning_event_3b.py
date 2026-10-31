#!/usr/bin/env python3
"""Tuning loop LINE 3b — stress-test of the EVENT BOOK candidate.
Spec frozen FIRST in stocks_tuning_event_frozen.md (Line 3b section).
W1 concentration stress (base book @2.0%), W2 v2.1 verification,
W3 spec-only (no scoring), W4 month table for v2.1.
EQUITY CASH intraday. LONG/SHORT. Paper only, real Rs0.
Per 100 shares provisional, Rs40/trade flat."""
import csv, json
from datetime import date, timedelta

BASE = "/home/hatch/workspace/trading/data/progressive"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
H1_HI = "2026-05-31"
OCT_LO = "2026-10-01"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{BASE}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{BASE}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]), "high": float(r["high"]),
                          "low": float(r["low"]), "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

stocks = {s: load_stock(s) for s in SYMBOLS}

def replay(candles, ei, entry, direction, tgt_pct, stp_pct):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + 1, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
    if last is not None:
        return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * QTY - COST, 2)

# ---------- P2F candidates (exact frozen definitions, as Line 3) ----------
events = []
with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
    for r in csv.DictReader(f):
        if r["event_type"] != "results" or r["stock"] not in SYMBOLS: continue
        ev = date.fromisoformat(r["event_date"][:10])
        react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
        ds = eff.isoformat()
        if ALL_LO <= ds <= ALL_HI:
            events.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
events.sort(key=lambda e: (e["symbol"], e["R"]))

p2f_candidates = []
for e in events:
    sym, R = e["symbol"], e["R"]
    spot, daily = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if R not in didx: continue
    ri = didx[R]
    if ri == 0 or ri + 1 >= len(daily): continue
    reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
    nd = daily[ri + 1]["date"]
    if nd > ALL_HI: continue
    bars = spot.get(nd, [])
    if not bars: continue
    p2f_candidates.append({"symbol": sym, "announce": e["announce"], "R": R,
                           "reaction_ret_pct": reaction_ret, "trade_date": nd,
                           "direction": "LONG" if reaction_ret > 0 else "SHORT",
                           "entry": bars[0]["open"], "ri": ri})

def score_p2f_t125(cand):
    spot, _ = stocks[cand["symbol"]]
    r = replay(spot[cand["trade_date"]], 0, cand["entry"], cand["direction"], 1.25, 0.5)
    if r is None: return None
    er, ep, et = r
    return {"symbol": cand["symbol"], "date": cand["trade_date"], "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(cand["entry"], 2), "exit_reason": er,
            "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(cand["direction"], cand["entry"], ep),
            "R": cand["R"], "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"P2F reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

def p2f_at(band):
    cands = [c for c in p2f_candidates if abs(c["reaction_ret_pct"]) >= band]
    return [t for t in (score_p2f_t125(c) for c in cands) if t]

p2f20 = p2f_at(2.0)
p2f25 = p2f_at(2.5)

# ---------- N4-V3 trades (published round-5 file, as Line 3) ----------
n4_trades = []
with open(f"{OUT}/eq_n4deep_v3_trades_T125_janoct.csv") as f:
    for r in csv.DictReader(f):
        n4_trades.append({"symbol": r["stock"], "date": r["date"], "direction": r["direction"],
                          "entry_time": r["entry_time"], "entry": float(r["entry"]),
                          "exit_reason": r["exit_reason"], "exit_price": float(r["exit_price"]),
                          "exit_time": r["exit_time"], "net_rs": float(r["net_rs_provisional_per100"]),
                          "note": r["note"]})

# ---------- metrics (identical to Line 3) ----------
def metrics(trades):
    if not trades:
        return {"trades": 0, "win_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0, "gross_expectancy_rs": 0.0}
    net = round(sum(t["net_rs"] for t in trades), 2)
    return {"trades": len(trades),
            "win_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "net_rs": net,
            "expectancy_rs": round(net / len(trades), 2),
            "gross_expectancy_rs": round((net + COST * len(trades)) / len(trades), 2)}

def block(trades):
    h1 = [t for t in trades if t["date"] <= H1_HI]; h2 = [t for t in trades if t["date"] > H1_HI]
    pst = {}
    for t in trades: pst[t["symbol"]] = round(pst.get(t["symbol"], 0.0) + t["net_rs"], 2)
    m1, m2 = metrics(h1), metrics(h2)
    return {"all": metrics(trades), "H1": m1, "H2": m2,
            "both_halves_positive": bool(h1 and h2 and m1["net_rs"] > 0 and m2["net_rs"] > 0),
            "breadth_net_positive_stocks": sum(1 for v in pst.values() if v > 0),
            "stocks_traded": len(pst),
            "per_stock_net": dict(sorted(pst.items(), key=lambda kv: -kv[1]))}

def gate(b):
    return bool(b["both_halves_positive"] and b["all"]["expectancy_rs"] > 0
                and b["breadth_net_positive_stocks"] >= 10)

results = {}

# ---------- ANCHORS ----------
combined20 = ([dict(t, leg="N4V3") for t in n4_trades] + [dict(t, leg="P2F") for t in p2f20])
combined20.sort(key=lambda t: (t["date"], t["symbol"], t["leg"]))
v1 = block(combined20)
print("ANCHOR V1 (expect 104 / +20826.31 / +8653.23 / +12173.08 / breadth 13):",
      v1["all"], v1["H1"]["net_rs"], v1["H2"]["net_rs"], v1["breadth_net_positive_stocks"])
assert v1["all"]["trades"] == 104 and abs(v1["all"]["net_rs"] - 20826.31) < 0.01
assert abs(v1["H1"]["net_rs"] - 8653.23) < 0.01 and abs(v1["H2"]["net_rs"] - 12173.08) < 0.01
assert v1["breadth_net_positive_stocks"] == 13
results["anchor_V1"] = v1

# ---------- W1 CONCENTRATION STRESS ----------
pst = v1["per_stock_net"]
top3 = [s for s, _ in list(pst.items())[:3]]
print("V1 per-stock top5:", list(pst.items())[:5])
print("Top-3 payers dropped in W1b:", top3, [pst[s] for s in top3])

w1a_trades = [t for t in combined20 if t["symbol"] != "GLENMARK"]
w1a = block(w1a_trades)
w1b_trades = [t for t in combined20 if t["symbol"] not in top3]
w1b = block(w1b_trades)

# W1c winsorised: per stock per half, cap positive contribution at +2000
def winsorised(trades, cap=2000.0):
    halves = {"H1": {}, "H2": {}}
    for t in trades:
        h = "H1" if t["date"] <= H1_HI else "H2"
        halves[h][t["symbol"]] = round(halves[h].get(t["symbol"], 0.0) + t["net_rs"], 2)
    out = {}
    capped_total_by_stock = {}
    for h, d in halves.items():
        capped = {s: (min(v, cap) if v > 0 else v) for s, v in d.items()}
        out[h] = {"net_rs": round(sum(capped.values()), 2),
                  "capped_stocks": {s: [d[s], capped[s]] for s in d if capped[s] != d[s]}}
        for s, v in capped.items():
            capped_total_by_stock[s] = round(capped_total_by_stock.get(s, 0.0) + v, 2)
    tot = round(out["H1"]["net_rs"] + out["H2"]["net_rs"], 2)
    return {"H1_net_rs": out["H1"]["net_rs"], "H2_net_rs": out["H2"]["net_rs"],
            "net_rs": tot, "expectancy_rs": round(tot / len(trades), 2) if trades else 0.0,
            "both_halves_positive": out["H1"]["net_rs"] > 0 and out["H2"]["net_rs"] > 0,
            "breadth_net_positive_stocks": sum(1 for v in capped_total_by_stock.values() if v > 0),
            "capped_detail": {"H1": out["H1"]["capped_stocks"], "H2": out["H2"]["capped_stocks"]},
            "trades": len(trades)}

w1c = winsorised(combined20)
w1c_gate = bool(w1c["both_halves_positive"] and w1c["expectancy_rs"] > 0
                and w1c["breadth_net_positive_stocks"] >= 10)
results["W1"] = {"top3_dropped": top3,
                 "W1a_ex_GLENMARK": w1a, "W1a_gate_pass": gate(w1a),
                 "W1b_ex_top3": w1b, "W1b_gate_pass": gate(w1b),
                 "W1c_winsorised_2000": w1c, "W1c_gate_pass": w1c_gate}
for k in ("W1a_ex_GLENMARK", "W1b_ex_top3"):
    b = results["W1"][k]
    print(k, b["all"], "H1", b["H1"]["net_rs"], "H2", b["H2"]["net_rs"],
          "breadth", b["breadth_net_positive_stocks"], "gate", results["W1"][k.replace("W1a","W1a").replace("W1b","W1b") + "_gate_pass"] if False else "")
print("W1a gate:", gate(w1a), "| W1b gate:", gate(w1b))
print("W1c winsorised:", w1c["net_rs"], "H1", w1c["H1_net_rs"], "H2", w1c["H2_net_rs"],
      "breadth", w1c["breadth_net_positive_stocks"], "gate", w1c_gate, "capped:", w1c["capped_detail"])

if gate(w1a) and gate(w1b) and w1c_gate: verdict = "STANDS"
elif not gate(w1a) or not w1c["both_halves_positive"]: verdict = "FALLS"
elif gate(w1a) and w1c_gate and not gate(w1b): verdict = "STANDS WEAKENED"
else: verdict = "STANDS WEAKENED (mixed — see report)"
results["W1"]["candidate_verdict"] = verdict
print("W1 candidate verdict:", verdict)

# ---------- W2 v2.1 VERIFICATION ----------
combined21 = ([dict(t, leg="N4V3") for t in n4_trades] + [dict(t, leg="P2F@2.5") for t in p2f25])
combined21.sort(key=lambda t: (t["date"], t["symbol"], t["leg"]))
v21 = block(combined21)
expect = {"trades": 95, "net_rs": 23479.51, "H1": 11857.97, "H2": 11621.54, "breadth": 13}
got = {"trades": v21["all"]["trades"], "net_rs": v21["all"]["net_rs"],
       "H1": v21["H1"]["net_rs"], "H2": v21["H2"]["net_rs"],
       "breadth": v21["breadth_net_positive_stocks"]}
match = all(abs(got[k] - expect[k]) < 0.01 if isinstance(expect[k], float) else got[k] == expect[k] for k in expect)
print("W2 v2.1 verify: expect", expect, "| got", got, "| MATCH" if match else "| DISCREPANCY")
glen21 = v21["per_stock_net"].get("GLENMARK", 0.0)
glen21_share = round(100 * glen21 / v21["all"]["net_rs"], 1) if v21["all"]["net_rs"] else 0.0
oct21 = [t for t in combined21 if t["date"] >= OCT_LO]
oct21_block = block(oct21)
p25_short = [t for t in p2f25 if t["direction"] == "SHORT"]
p25_long = [t for t in p2f25 if t["direction"] == "LONG"]
# overlap for 2.5% leg: both-fire events (N4 date == P2F R, same stock)
n4_by_key = {}
for t in n4_trades: n4_by_key.setdefault((t["symbol"], t["date"]), []).append(t)
both_fire25 = sum(1 for t in p2f25 if (t["symbol"], t["R"]) in n4_by_key)
results["W2"] = {"book": v21, "verification": {"expected": expect, "got": got, "exact_match": match},
                 "glenmark_net_v21": glen21, "glenmark_share_pct": glen21_share,
                 "october_slice": oct21_block,
                 "p2f25_direction": {"SHORT": block(p25_short), "LONG": block(p25_long)},
                 "p2f25_trades": len(p2f25), "both_fire_events_25": both_fire25}
print("v2.1 GLENMARK:", glen21, f"({glen21_share}% of net)",
      "| Oct slice:", oct21_block["all"], "| both-fire @2.5:", both_fire25)
print("P2F@2.5 SHORT:", results["W2"]["p2f25_direction"]["SHORT"]["all"],
      "LONG:", results["W2"]["p2f25_direction"]["LONG"]["all"])

# ---------- W4 MONTH TABLE (v2.1) ----------
months = {}
for t in combined21:
    m = t["date"][:7]
    months.setdefault(m, []).append(t)
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
for m in ALL_MONTHS: months.setdefault(m, [])
mtab, cum = [], 0.0
for m in ALL_MONTHS:
    tr = months[m]
    n = round(sum(t["net_rs"] for t in tr), 2)
    cum = round(cum + n, 2)
    mtab.append({"month": m, "trades": len(tr), "net_rs": n, "cumulative_rs": cum,
                 "share_of_total_pct": round(100 * n / v21["all"]["net_rs"], 1) if v21["all"]["net_rs"] else 0.0})
results["W4"] = {"months": mtab,
                 "negative_months": [r["month"] for r in mtab if r["net_rs"] < 0],
                 "months_worse_than_-3000": [r for r in mtab if r["net_rs"] < -3000]}
for r in mtab: print("W4", r)

# ---------- outputs ----------
def wcsv(fn, dicts, fields):
    with open(f"{OUT}/{fn}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for d in dicts: w.writerow(d)

tf = ["leg","symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","R","reaction_ret_pct","note"]
wcsv("stocks_tuning_event_v21_combined_trades.csv", combined21, tf)
with open(f"{OUT}/stocks_tuning_event_3b_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE stocks_tuning_event_3b_results.json + v21 trades CSV")
