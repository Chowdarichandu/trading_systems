#!/usr/bin/env python3
"""Stocks EQUITY round 5 — N4-deep (event-reaction).
Spec: stocks_equity_n4deep_frozen.md (frozen BEFORE scoring; T125 PRIMARY,
declared in the spec because round-4 N4 was both-halves positive only at T125).
EQUITY CASH intraday only. LONG/SHORT. Paper only.
Per 100 shares provisional, Rs40/trade. UNCAPPED portfolio view.
Variants: BASE (round-4 N4 anchor), V1a thr>=0.5%, V1b thr>=1.5%,
V2 entry 10:05 (same >=1% trigger), V3 combined results+single-news >=1%,
V4 day+1 follow-through (results, day-1 close in trigger direction).
Exits: T125 primary (tgt 1.25/stop 0.5), T10 secondary (tgt 1.0/stop 0.5).
Stop-first tie. Exit scan from bar after entry bar. 15:10 square-off."""
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
H1_HI, H2_LO = "2026-05-31", "2026-06-01"
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
_, nifty_daily = load_stock("NIFTY")
ALL_DAYS = sorted(d["date"] for d in nifty_daily if ALL_LO <= d["date"] <= ALL_HI)
DAYS_H1 = [d for d in ALL_DAYS if d <= H1_HI]
DAYS_H2 = [d for d in ALL_DAYS if d >= H2_LO]
DAYS_OCT = [d for d in ALL_DAYS if d >= OCT_LO]
DAY_IDX = {d: i for i, d in enumerate(ALL_DAYS)}

SINGLE_NEWS = {"management_change","large_order","fda_approval","block_deal",
               "sector_policy","pricing","corporate_action"}
def reaction_days(kind):
    """kind: 'results' | 'news' | 'combined' -> stock -> set of reaction dates."""
    out = {s: set() for s in SYMBOLS}
    with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in out: continue
            et = r["event_type"]
            if kind == "results" and et != "results": continue
            if kind == "news" and et not in SINGLE_NEWS: continue
            if kind == "combined" and et != "results" and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if ALL_LO <= ds <= ALL_HI: out[sym].add(ds)
    return out
RESULTS_DAYS = reaction_days("results")
COMBINED_DAYS = reaction_days("combined")

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

SIGNALS = {"BASE": [], "V1a": [], "V1b": [], "V2": [], "V3": [], "V4": []}
def add(fam, sym, day, direction, ei, entry, entry_time, note):
    SIGNALS[fam].append({"family": fam, "symbol": sym, "date": day,
        "direction": direction, "entry_idx": ei, "entry": entry,
        "entry_time": entry_time, "note": note})

for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    for day in ALL_DAYS:
        if day not in dmap or dmap[day] == 0: continue
        raw = spot.get(day, [])
        if not raw: continue
        prev_close = daily[dmap[day] - 1]["close"]
        if not prev_close: continue
        by_time = {c["time"]: c for c in raw}
        idx_of = {c["timestamp"]: i for i, c in enumerate(raw)}
        b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
        # ---- results reaction variants (BASE / V1a / V1b / V2) ----
        if day in RESULTS_DAYS[sym] and b0925 is not None and b0930 is not None:
            move_pct = (b0925["close"] / prev_close - 1) * 100
            direction = "LONG" if move_pct > 0 else "SHORT"
            ei930 = idx_of[b0930["timestamp"]]
            note = f"reaction move by 09:30 {move_pct:+.2f}%"
            if abs(move_pct) >= 1.0:
                add("BASE", sym, day, direction, ei930, b0930["close"], "09:35", note)
                b1000 = by_time.get("10:00")
                if b1000 is not None:
                    add("V2", sym, day, direction, idx_of[b1000["timestamp"]],
                        b1000["close"], "10:05", note + " | entry 10:05")
                # ---- V4: day+1 follow-through ----
                day_close = daily[dmap[day]]["close"]
                closed_dir = (day_close > prev_close) if direction == "LONG" else (day_close < prev_close)
                if closed_dir and DAY_IDX.get(day) is not None and DAY_IDX[day] + 1 < len(ALL_DAYS):
                    nd = ALL_DAYS[DAY_IDX[day] + 1]
                    if nd in dmap and spot.get(nd):
                        nraw = spot[nd]
                        nb = {c["time"]: c for c in nraw}
                        nb0930 = nb.get("09:30")
                        if nb0930 is not None:
                            nei = {c["timestamp"]: i for i, c in enumerate(nraw)}[nb0930["timestamp"]]
                            add("V4", sym, nd, direction, nei, nb0930["close"], "09:35",
                                f"day+1 follow-through of {day} reaction {move_pct:+.2f}%, day-1 close confirmed")
            if abs(move_pct) >= 0.5:
                add("V1a", sym, day, direction, ei930, b0930["close"], "09:35", note)
            if abs(move_pct) >= 1.5:
                add("V1b", sym, day, direction, ei930, b0930["close"], "09:35", note)
        # ---- V3: combined results + single-news reaction ----
        if day in COMBINED_DAYS[sym] and b0925 is not None and b0930 is not None:
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= 1.0:
                src = "results" if day in RESULTS_DAYS[sym] else "single-news"
                add("V3", sym, day, "LONG" if move_pct > 0 else "SHORT",
                    idx_of[b0930["timestamp"]], b0930["close"], "09:35",
                    f"combined ({src}) reaction move by 09:30 {move_pct:+.2f}%")

EXITS = {"T125": (1.25, 0.5), "T10": (1.0, 0.5)}  # T125 PRIMARY (frozen spec)
def score(sig_list, tgt_pct, stp_pct):
    out = []
    for s in sig_list:
        spot, _ = stocks[s["symbol"]]
        candles = spot[s["date"]]
        r = replay(candles, s["entry_idx"], s["entry"], s["direction"], tgt_pct, stp_pct)
        if r is None: continue
        er, ep, et = r
        sign = 1 if s["direction"] == "LONG" else -1
        out.append({"family": s["family"], "symbol": s["symbol"], "date": s["date"],
            "direction": s["direction"], "entry_time": s["entry_time"],
            "entry": round(s["entry"], 2),
            "stop": round(s["entry"] * (1 - sign * stp_pct / 100), 2),
            "target": round(s["entry"] * (1 + sign * tgt_pct / 100), 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": round(sign * (ep - s["entry"]) * QTY - COST, 2),
            "pct_captured": round(sign * (ep - s["entry"]) / s["entry"] * 100, 3),
            "note": s["note"]})
    return out

TRADES = {fam: {ex: score(SIGNALS[fam], *EXITS[ex]) for ex in EXITS} for fam in SIGNALS}

def metrics(trades, days):
    if not trades:
        return {"trades": 0, "win_pct": 0.0, "target_pct": 0.0, "net_rs": 0.0,
                "expectancy_rs": 0.0, "trades_per_day": 0.0}
    net = sum(t["net_rs"] for t in trades)
    return {"trades": len(trades),
            "win_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "target_pct": round(100 * sum(1 for t in trades if t["exit_reason"] == "target") / len(trades), 1),
            "net_rs": round(net, 2), "expectancy_rs": round(net / len(trades), 2),
            "trades_per_day": round(len(trades) / len(days), 2) if days else 0.0}

def fam_metrics(trades):
    return {"all": metrics(trades, ALL_DAYS),
            "jan_may": metrics([t for t in trades if t["date"] <= H1_HI], DAYS_H1),
            "jun_oct": metrics([t for t in trades if t["date"] >= H2_LO], DAYS_H2),
            "oct": metrics([t for t in trades if t["date"] >= OCT_LO], DAYS_OCT)}

results = {"days": {"all": len(ALL_DAYS), "jan_may": len(DAYS_H1),
                    "jun_oct": len(DAYS_H2), "oct": len(DAYS_OCT)},
           "primary_exit": "T125", "variants": {}}
for fam in SIGNALS:
    results["variants"][fam] = {ex: fam_metrics(TRADES[fam][ex]) for ex in EXITS}
    p = results["variants"][fam]["T125"]
    adequate = p["all"]["trades"] >= 10 and p["jan_may"]["trades"] >= 3 and p["jun_oct"]["trades"] >= 3
    results["variants"][fam]["graduates_T125"] = bool(
        p["jan_may"]["net_rs"] > 0 and p["jun_oct"]["net_rs"] > 0 and adequate)
    results["variants"][fam]["both_halves_positive_T125"] = bool(
        p["jan_may"]["net_rs"] > 0 and p["jun_oct"]["net_rs"] > 0)
    s10 = results["variants"][fam]["T10"]
    results["variants"][fam]["both_halves_positive_T10"] = bool(
        s10["jan_may"]["net_rs"] > 0 and s10["jun_oct"]["net_rs"] > 0)

grads = [f for f in SIGNALS if results["variants"][f]["graduates_T125"] and f != "V4"]
if "V4" in grads: grads.remove("V4")
v4_grad = results["variants"]["V4"]["graduates_T125"]
results["graduates_T125"] = grads
results["v4_graduates_T125"] = bool(v4_grad)
# November primary per frozen rule: highest Jan-Oct T125 net among graduates (excl V4);
# tie -> simpler (order BASE, V1a, V1b, V2, V3). Else BASE.
order = ["BASE", "V1a", "V1b", "V2", "V3"]
if grads:
    best = max(grads, key=lambda f: (results["variants"][f]["T125"]["all"]["net_rs"],
                                     -order.index(f)))
else:
    best = "BASE"
results["november_primary_variant"] = best

def write_trades(fn, trades, combo):
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "stock", "direction", "variant", "entry_time", "entry", "stop",
                    "target", "exit_reason", "exit_price", "exit_time",
                    "net_rs_provisional_per100", "pct_captured", "note", "combo"])
        for t in sorted(trades, key=lambda x: (x["date"], x["entry_time"], x["symbol"])):
            w.writerow([t["date"], t["symbol"], t["direction"], t["family"], t["entry_time"],
                        t["entry"], t["stop"], t["target"], t["exit_reason"], t["exit_price"],
                        t["exit_time"], t["net_rs"], t["pct_captured"], t["note"], combo])
    return fn

files = []
for fam in SIGNALS:
    for ex in EXITS:
        files.append(write_trades(f"{OUT}/eq_n4deep_{fam.lower()}_trades_{ex}_janoct.csv",
                                  TRADES[fam][ex], ex))
results["files"] = files
with open(f"{OUT}/stocks_equity_n4deep_results.json", "w") as f:
    json.dump(results, f, indent=1)

def line(name, m):
    a, h1, h2, o = m["all"], m["jan_may"], m["jun_oct"], m["oct"]
    print(f"{name:10s} ALL n={a['trades']:4d} win={a['win_pct']:5.1f} tgt={a['target_pct']:5.1f} net={a['net_rs']:11.2f} exp={a['expectancy_rs']:8.2f} tpd={a['trades_per_day']:5.2f} | H1 n={h1['trades']:3d} net={h1['net_rs']:11.2f} exp={h1['expectancy_rs']:8.2f} | H2 n={h2['trades']:3d} net={h2['net_rs']:11.2f} exp={h2['expectancy_rs']:8.2f} | OCT n={o['trades']:3d} net={o['net_rs']:10.2f} win={o['win_pct']:5.1f}")
print(f"DAYS all={len(ALL_DAYS)} jan-may={len(DAYS_H1)} jun-oct={len(DAYS_H2)} oct={len(DAYS_OCT)}")
for fam in SIGNALS:
    for ex in ("T125", "T10"):
        line(f"{fam}/{ex}", results["variants"][fam][ex])
    print(f"   both+ T125={results['variants'][fam]['both_halves_positive_T125']} graduates_T125={results['variants'][fam]['graduates_T125']} both+ T10={results['variants'][fam]['both_halves_positive_T10']}")
print("GRADUATES (excl V4):", grads, "| V4 graduates:", v4_grad)
print("NOVEMBER PRIMARY:", best)
print("ANCHOR CHECK: BASE/T10 all net should be 4319.24, BASE/T125 all net 2924.79")
print("FILES", len(files))
