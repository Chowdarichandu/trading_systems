#!/usr/bin/env python3
"""Stocks EQUITY exploration round 4 — STOCK-NATIVE signals.
Spec: stocks_equity_native4_frozen.md (frozen before scoring).
EQUITY CASH intraday only. LONG/SHORT. Paper only.
Per 100 shares provisional, Rs40/trade. UNCAPPED portfolio view.
Families: N1 gap continuation (a: |gap|>=1%, b: >=2%), N2 gap fade (a/b),
N3 stock ORB (OR width<=1.5%, prior-10d ADR>=2%), N4 results-reaction
momentum (+ N4b single-news). Exit T10 primary (tgt 1.0/stop 0.5),
T125 secondary (tgt 1.25/stop 0.5). Stop-first tie. 15:10 square-off."""
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

def adr10(sym, day, dmap, daily):
    i = dmap.get(day)
    if i is None or i < 5: return None
    prior = daily[max(0, i-10):i]
    if len(prior) < 5: return None
    vals = [(d["high"]-d["low"])/d["close"]*100 for d in prior if d["close"]]
    return round(sum(vals)/len(vals), 3) if vals else None

# ---- reaction days from the event calendar ----
SINGLE_NEWS = {"management_change","large_order","fda_approval","block_deal",
               "sector_policy","pricing","corporate_action"}
def reaction_days(want_results):
    """stock -> set of effective reaction dates inside window."""
    out = {s: set() for s in SYMBOLS}
    with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in out: continue
            et = r["event_type"]
            if want_results and et != "results": continue
            if not want_results and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if ALL_LO <= ds <= ALL_HI: out[sym].add(ds)
    return out
RESULTS_DAYS = reaction_days(True)
NEWS_DAYS = reaction_days(False)

# ---- exit replay: entry at close of bar index `ei`; scan from ei+1 ----
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
    return None  # no bar after entry -> cannot trade

SIGNALS = {"N1a": [], "N1b": [], "N2a": [], "N2b": [], "N3": [], "N4": [], "N4b": []}
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
        day_open = raw[0]["open"]
        # ---- N1 / N2: gap families ----
        b0920 = by_time.get("09:20")
        gap_pct = (day_open / prev_close - 1) * 100
        if b0920 is not None:
            ei = idx_of[b0920["timestamp"]]
            for thr, suf in ((1.0, "a"), (2.0, "b")):
                if gap_pct >= thr:
                    if b0920["close"] > day_open:
                        add("N1" + suf, sym, day, "LONG", ei, b0920["close"], "09:20",
                            f"gap {gap_pct:+.2f}%")
                    add("N2" + suf, sym, day, "SHORT", ei, b0920["close"], "09:20",
                        f"gap {gap_pct:+.2f}% fade")
                elif gap_pct <= -thr:
                    if b0920["close"] < day_open:
                        add("N1" + suf, sym, day, "SHORT", ei, b0920["close"], "09:20",
                            f"gap {gap_pct:+.2f}%")
                    add("N2" + suf, sym, day, "LONG", ei, b0920["close"], "09:20",
                        f"gap {gap_pct:+.2f}% fade")
        # ---- N3: stock ORB ----
        or_bars = [by_time.get(t) for t in ("09:15", "09:20", "09:25")]
        if all(or_bars):
            orh = max(c["high"] for c in or_bars); orl = min(c["low"] for c in or_bars)
            width_pct = (orh - orl) / day_open * 100 if day_open else 999.0
            adr = adr10(sym, day, dmap, daily)
            if width_pct <= 1.5 and adr is not None and adr >= 2.0:
                for c in raw:
                    if c["time"] < "09:30" or c["time"] > "15:05": continue
                    if c["close"] > orh:
                        add("N3", sym, day, "LONG", idx_of[c["timestamp"]], c["close"],
                            c["time"], f"OR width {width_pct:.2f}% ADR {adr:.2f}%")
                        break
                    if c["close"] < orl:
                        add("N3", sym, day, "SHORT", idx_of[c["timestamp"]], c["close"],
                            c["time"], f"OR width {width_pct:.2f}% ADR {adr:.2f}%")
                        break
        # ---- N4 / N4b: reaction-day momentum ----
        for fam, dayset in (("N4", RESULTS_DAYS), ("N4b", NEWS_DAYS)):
            if day not in dayset[sym]: continue
            b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
            if b0925 is None or b0930 is None: continue
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= 1.0:
                add(fam, sym, day, "LONG" if move_pct > 0 else "SHORT",
                    idx_of[b0930["timestamp"]], b0930["close"], "09:35",
                    f"reaction move by 09:30 {move_pct:+.2f}%")

EXITS = {"T10": (1.0, 0.5), "T125": (1.25, 0.5)}
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
                    "jun_oct": len(DAYS_H2), "oct": len(DAYS_OCT)}, "families": {}}
for fam in SIGNALS:
    results["families"][fam] = {ex: fam_metrics(TRADES[fam][ex]) for ex in EXITS}
    m = results["families"][fam]["T10"]
    results["families"][fam]["survivor_T10"] = (
        m["jan_may"]["net_rs"] > 0 and m["jun_oct"]["net_rs"] > 0
        and not (fam == "N4b" and m["all"]["trades"] < 10))

survivors = [f for f in SIGNALS if results["families"][f]["survivor_T10"]]
results["survivors_T10"] = survivors

# ---- union of survivors (dedup stock+date+direction, earliest entry) ----
union_trades = []
if len(survivors) >= 2:
    pool = [t for f in survivors for t in TRADES[f]["T10"]]
    pool.sort(key=lambda t: (t["date"], t["symbol"], t["direction"], t["entry_time"]))
    seen = set()
    for t in pool:
        k = (t["symbol"], t["date"], t["direction"])
        if k in seen: continue
        seen.add(k); union_trades.append(t)
    results["union_T10"] = fam_metrics(union_trades)
else:
    results["union_T10"] = None

def write_trades(fn, trades, combo):
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "stock", "direction", "family", "entry_time", "entry", "stop",
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
        files.append(write_trades(f"{OUT}/eq_native4_{fam.lower()}_trades_{ex}_janoct.csv",
                                  TRADES[fam][ex], ex))
if union_trades:
    files.append(write_trades(f"{OUT}/eq_native4_union_trades_T10_janoct.csv", union_trades, "UNION_T10"))
    # October slices for survivors (trade-by-trade in the report source)
    for f in survivors:
        oct_t = [t for t in TRADES[f]["T10"] if t["date"] >= OCT_LO]
        files.append(write_trades(f"{OUT}/eq_native4_{f.lower()}_trades_T10_october.csv", oct_t, "T10_OCT"))
results["files"] = files
with open(f"{OUT}/stocks_equity_native4_results.json", "w") as f:
    json.dump(results, f, indent=1)

def line(name, m):
    a, h1, h2, o = m["all"], m["jan_may"], m["jun_oct"], m["oct"]
    print(f"{name:6s} ALL n={a['trades']:5d} win={a['win_pct']:5.1f} tgt={a['target_pct']:5.1f} net={a['net_rs']:12.2f} exp={a['expectancy_rs']:8.2f} tpd={a['trades_per_day']:5.2f} | H1 n={h1['trades']:5d} net={h1['net_rs']:12.2f} exp={h1['expectancy_rs']:8.2f} | H2 n={h2['trades']:5d} net={h2['net_rs']:12.2f} exp={h2['expectancy_rs']:8.2f} | OCT n={o['trades']:4d} net={o['net_rs']:11.2f} win={o['win_pct']:5.1f}")
print(f"DAYS all={len(ALL_DAYS)} jan-may={len(DAYS_H1)} jun-oct={len(DAYS_H2)} oct={len(DAYS_OCT)}")
for fam in SIGNALS:
    for ex in EXITS:
        line(f"{fam}/{ex}", results["families"][fam][ex])
    print(f"   survivor_T10={results['families'][fam]['survivor_T10']}")
print("SURVIVORS:", survivors)
if results["union_T10"]: line("UNION", results["union_T10"])
print("FILES", len(files))
