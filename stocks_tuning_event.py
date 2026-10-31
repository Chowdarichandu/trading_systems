#!/usr/bin/env python3
"""Tuning loop LINE 3 — the EVENT BOOK (N4-V3 + P2F), families V1..V6.
Spec frozen FIRST in stocks_tuning_event_frozen.md.
EQUITY CASH intraday (except V3a, NON-INTRADAY, labelled). LONG/SHORT.
Paper only, real Rs0. Per 100 shares provisional, Rs40/trade flat."""
import csv, json, re
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

# NIFTY daily for V6
nifty = []
with open(f"{BASE}/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        nifty.append({"date": r["date"][:10], "close": float(r["close"])})
nifty.sort(key=lambda x: x["date"])
nifty_dates = [d["date"] for d in nifty]

def inv1_met(day):
    """INV1 condition ex-ante for trade date `day`: prev close <= 50DMA
    (mean of 50 closes ending at prev bar). None if not computable."""
    prev_idx = None
    for i, d in enumerate(nifty_dates):
        if d < day: prev_idx = i
        else: break
    if prev_idx is None or prev_idx < 49: return None
    closes = [nifty[j]["close"] for j in range(prev_idx - 49, prev_idx + 1)]
    return nifty[prev_idx]["close"] <= sum(closes) / 50.0

# ---------- exit engine: round-5 N4, verbatim logic ----------
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

# ---------- P2F candidates, regenerated exactly per frozen spec ----------
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

p2f_candidates = []   # every candidate event with reaction data, before band filter
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

p2f_base_cands = [c for c in p2f_candidates if abs(c["reaction_ret_pct"]) >= 2.0]
p2f_trades = [t for t in (score_p2f_t125(c) for c in p2f_base_cands) if t]

# ---------- N4-V3 trades from the published round-5 file ----------
n4_trades = []
with open(f"{OUT}/eq_n4deep_v3_trades_T125_janoct.csv") as f:
    for r in csv.DictReader(f):
        n4_trades.append({"symbol": r["stock"], "date": r["date"], "direction": r["direction"],
                          "entry_time": r["entry_time"], "entry": float(r["entry"]),
                          "exit_reason": r["exit_reason"], "exit_price": float(r["exit_price"]),
                          "exit_time": r["exit_time"], "net_rs": float(r["net_rs_provisional_per100"]),
                          "note": r["note"]})

# ---------- metrics ----------
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

results = {}

# ---------- ANCHORS ----------
anch = {"N4V3": block(n4_trades), "P2F": block(p2f_trades)}
results["anchors"] = anch
print("ANCHOR N4-V3 T125 (expect 56 / +7990.43 / +5155.13 / +2835.30):",
      anch["N4V3"]["all"], anch["N4V3"]["H1"]["net_rs"], anch["N4V3"]["H2"]["net_rs"])
print("ANCHOR P2F   T125 (expect 48 / +12835.88 / +3498.10 / +9337.78 / breadth 14):",
      anch["P2F"]["all"], anch["P2F"]["H1"]["net_rs"], anch["P2F"]["H2"]["net_rs"],
      "breadth", anch["P2F"]["breadth_net_positive_stocks"])
p2f_long = [t for t in p2f_trades if t["direction"] == "LONG"]
p2f_short = [t for t in p2f_trades if t["direction"] == "SHORT"]
print("ANCHOR P2F dir split (expect SHORT +13109.45 / LONG -273.57):",
      round(sum(t["net_rs"] for t in p2f_short), 2), round(sum(t["net_rs"] for t in p2f_long), 2))
assert anch["N4V3"]["all"]["trades"] == 56 and abs(anch["N4V3"]["all"]["net_rs"] - 7990.43) < 0.01
assert anch["P2F"]["all"]["trades"] == 48 and abs(anch["P2F"]["all"]["net_rs"] - 12835.88) < 0.01

# ---------- V1 COMBINED BOOK ----------
combined = ([dict(t, leg="N4V3") for t in n4_trades] + [dict(t, leg="P2F") for t in p2f_trades])
combined.sort(key=lambda t: (t["date"], t["symbol"], t["leg"]))
v1 = block(combined)
# overlap (a): both-fire events — N4 trade date == P2F reaction date R, same stock
n4_by_key = {}
for t in n4_trades: n4_by_key.setdefault((t["symbol"], t["date"]), []).append(t)
both_fire = []
for t in p2f_trades:
    for n4t in n4_by_key.get((t["symbol"], t["R"]), []):
        both_fire.append({"symbol": t["symbol"], "R": t["R"], "p2f_date": t["date"],
                          "n4": n4t, "p2f": t})
# overlap (b): same stock + same trade date in both legs
p2f_dates = {(t["symbol"], t["date"]) for t in p2f_trades}
same_day = [(t["symbol"], t["date"]) for t in n4_trades if (t["symbol"], t["date"]) in p2f_dates]
results["V1"] = {"book": v1, "both_fire_events": len(both_fire), "same_stock_same_day": same_day}
print("V1 COMBINED:", v1["all"], "H1", v1["H1"]["net_rs"], "H2", v1["H2"]["net_rs"],
      "both+", v1["both_halves_positive"], "breadth", v1["breadth_net_positive_stocks"],
      "both-fire", len(both_fire), "same-day overlaps", same_day)

# ---------- V2 REACTION BANDS ----------
results["V2"] = {}
band_trades = {}
for band in (2.5, 3.0, 4.0):
    cands = [c for c in p2f_candidates if abs(c["reaction_ret_pct"]) >= band]
    tr = [t for t in (score_p2f_t125(c) for c in cands) if t]
    band_trades[band] = tr
    results["V2"][f"band_{band}"] = block(tr)
    print(f"V2 band >={band}%:", results["V2"][f'band_{band}']["all"],
          "H1", results["V2"][f'band_{band}']["H1"]["net_rs"],
          "H2", results["V2"][f'band_{band}']["H2"]["net_rs"],
          "breadth", results["V2"][f'band_{band}']["breadth_net_positive_stocks"])

# ---------- V3 HOLD VARIANTS (V3a NON-INTRADAY) ----------
def score_v3a(cand):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    ti = didx[cand["trade_date"]]
    if ti + 1 >= len(daily): return None, "no R+2 in data"
    r2 = daily[ti + 1]["date"]
    bars2 = spot.get(r2, [])
    if not bars2: return None, "no R+2 bars"
    entry, direction = cand["entry"], cand["direction"]
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * 1.25 / 100); stop = entry * (1 - sign * 0.5 / 100)
    r = replay(spot[cand["trade_date"]], 0, entry, direction, 1.25, 0.5)
    if r is not None and r[0] in ("stop", "target"):
        er, ep, et = r
        return {"symbol": sym, "date": cand["trade_date"], "direction": direction,
                "entry_time": "09:15", "entry": round(entry, 2), "exit_reason": er,
                "exit_price": round(ep, 2), "exit_time": f"{cand['trade_date']} {et}",
                "net_rs": net_of(direction, entry, ep), "R": cand["R"],
                "reaction_ret_pct": cand["reaction_ret_pct"], "hold_days": 1,
                "note": f"V3a reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}% exited day 1"}, None
    # held overnight -> R+2
    o = bars2[0]["open"]
    if sign == 1:
        if o <= stop: er, ep = "gap_stop", o
        elif o >= target: er, ep = "gap_target", o
        else: er, ep = None, None
    else:
        if o >= stop: er, ep = "gap_stop", o
        elif o <= target: er, ep = "gap_target", o
        else: er, ep = None, None
    if er is not None:
        et = bars2[0]["time"]
    else:
        r2res = replay(bars2, -1, entry, direction, 1.25, 0.5)  # scan from bar 0 of R+2
        if r2res is None: return None, "R+2 replay failed"
        er, ep, et = r2res
    return {"symbol": sym, "date": cand["trade_date"], "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2), "exit_reason": er,
            "exit_price": round(ep, 2), "exit_time": f"{r2} {et}",
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"], "hold_days": 2,
            "note": f"V3a NON-INTRADAY reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}% held overnight, exit {r2}"}, None

def score_v3b(cand):
    spot, _ = stocks[cand["symbol"]]
    bars = spot[cand["trade_date"]]
    last = None
    for c in bars:
        if c["time"] > "15:10": break
        last = c
        if c["time"] == "15:10": break
    if last is None: return None
    ep = last["close"]
    return {"symbol": cand["symbol"], "date": cand["trade_date"], "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(cand["entry"], 2), "exit_reason": "close_exit",
            "exit_price": round(ep, 2), "exit_time": last["time"],
            "net_rs": net_of(cand["direction"], cand["entry"], ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"V3b control reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

v3a_trades, v3a_dropped = [], []
for c in p2f_base_cands:
    t, why = score_v3a(c)
    if t: v3a_trades.append(t)
    else: v3a_dropped.append({"symbol": c["symbol"], "R": c["R"], "trade_date": c["trade_date"], "why": why})
v3b_trades = [t for t in (score_v3b(c) for c in p2f_base_cands) if t]
results["V3a_NONINTRADAY"] = {"book": block(v3a_trades), "dropped_no_R2": v3a_dropped,
                             "exited_day1": sum(1 for t in v3a_trades if t["hold_days"] == 1),
                             "held_overnight": sum(1 for t in v3a_trades if t["hold_days"] == 2)}
results["V3b"] = {"book": block(v3b_trades)}
b = results["V3a_NONINTRADAY"]["book"]
print("V3a TWO-DAY HOLD (NON-INTRADAY):", b["all"], "H1", b["H1"]["net_rs"], "H2", b["H2"]["net_rs"],
      "breadth", b["breadth_net_positive_stocks"], "overnight", results["V3a_NONINTRADAY"]["held_overnight"],
      "dropped", len(v3a_dropped))
b = results["V3b"]["book"]
print("V3b CLOSE-EXIT CONTROL:", b["all"], "H1", b["H1"]["net_rs"], "H2", b["H2"]["net_rs"],
      "breadth", b["breadth_net_positive_stocks"])

# ---------- V4 DIRECTION SPLIT ----------
results["V4"] = {"SHORT_only": block(p2f_short), "LONG_only": block(p2f_long)}
for k, v in results["V4"].items():
    print(f"V4 {k}:", v["all"], "H1", v["H1"]["net_rs"], "H2", v["H2"]["net_rs"],
          "breadth", v["breadth_net_positive_stocks"])

# ---------- V5 CHAIN ACCOUNTING ----------
chains = []
for bf in both_fire:
    n4t, p2t = bf["n4"], bf["p2f"]
    chains.append({"symbol": bf["symbol"], "R": bf["R"],
                   "n4_date": n4t["date"], "n4_direction": n4t["direction"], "n4_net_rs": n4t["net_rs"],
                   "p2f_date": p2t["date"], "p2f_direction": p2t["direction"], "p2f_net_rs": p2t["net_rs"],
                   "directions_agree": n4t["direction"] == p2t["direction"],
                   "chain_net_rs": round(n4t["net_rs"] + p2t["net_rs"], 2)})
chain_nets = [c["chain_net_rs"] for c in chains]
results["V5"] = {"chains": chains,
                 "chain_count": len(chains),
                 "chain_net_total": round(sum(chain_nets), 2),
                 "chain_win_pct": round(100 * sum(1 for x in chain_nets if x > 0) / len(chain_nets), 1) if chains else 0.0,
                 "chain_expectancy": round(sum(chain_nets) / len(chain_nets), 2) if chains else 0.0,
                 "n4_leg_expectancy_on_chain_events": round(sum(c["n4_net_rs"] for c in chains) / len(chains), 2) if chains else 0.0,
                 "p2f_leg_expectancy_on_chain_events": round(sum(c["p2f_net_rs"] for c in chains) / len(chains), 2) if chains else 0.0,
                 "directions_agree_count": sum(1 for c in chains if c["directions_agree"])}
print("V5 CHAINS:", results["V5"]["chain_count"], "chain net", results["V5"]["chain_net_total"],
      "chain exp", results["V5"]["chain_expectancy"], "agree", results["V5"]["directions_agree_count"])

# ---------- V6 COMBINED BOOK x INV1 CONDITION ----------
tagged = []
unclass = 0
for t in combined:
    m = inv1_met(t["date"])
    if m is None: unclass += 1
    tagged.append(dict(t, inv1_met=m))
met = [t for t in tagged if t["inv1_met"] is True]
notmet = [t for t in tagged if t["inv1_met"] is False]
results["V6"] = {"MET": block(met), "NOT_MET": block(notmet), "unclassifiable": unclass,
                 "MET_N4V3": block([t for t in met if t["leg"] == "N4V3"]),
                 "MET_P2F": block([t for t in met if t["leg"] == "P2F"]),
                 "NOTMET_N4V3": block([t for t in notmet if t["leg"] == "N4V3"]),
                 "NOTMET_P2F": block([t for t in notmet if t["leg"] == "P2F"])}
for k in ("MET", "NOT_MET"):
    v = results["V6"][k]
    print(f"V6 {k}:", v["all"], "H1", v["H1"]["net_rs"], "H2", v["H2"]["net_rs"])

# ---------- SUPPLEMENTARY composition check (NOT a frozen family) ----------
# V1's book with its P2F leg at the V2 2.5% band. Run AFTER V1 and V2
# were scored; disclosed in the report as a composition check, not a
# pre-declared family, and NOT the frozen candidate on its own.
combo25 = ([dict(t, leg="N4V3") for t in n4_trades] +
           [dict(t, leg="P2F@2.5") for t in band_trades[2.5]])
results["SUPP_combined_P2F_band25"] = block(combo25)
s = results["SUPP_combined_P2F_band25"]
print("SUPP combined w/ P2F@2.5:", s["all"], "H1", s["H1"]["net_rs"], "H2", s["H2"]["net_rs"],
      "breadth", s["breadth_net_positive_stocks"])

# ---------- write outputs ----------
def wcsv(fn, dicts, fields):
    with open(f"{OUT}/{fn}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for d in dicts: w.writerow(d)

tf = ["leg","symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","R","reaction_ret_pct","note"]
wcsv("stocks_tuning_event_V1_combined_trades.csv", combined, tf)
wcsv("stocks_tuning_event_V3a_NONINTRADAY_trades.csv", v3a_trades,
     ["symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","R","reaction_ret_pct","hold_days","note"])
wcsv("stocks_tuning_event_V3b_trades.csv", v3b_trades,
     ["symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","R","reaction_ret_pct","note"])
wcsv("stocks_tuning_event_V5_chains.csv", chains,
     ["symbol","R","n4_date","n4_direction","n4_net_rs","p2f_date","p2f_direction","p2f_net_rs","directions_agree","chain_net_rs"])
with open(f"{OUT}/stocks_tuning_event_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE stocks_tuning_event_results.json + CSVs")
