#!/usr/bin/env python3
"""PART 2 — VOLUME AXIS. Spec: stocks_new_strategy_frozen.md (Part 2 section).
Equity cash intraday, LONG/SHORT, paper only. Per 100 shares provisional,
Rs40/trade. Volume ratios are rolling same-day medians of prior 20 bars."""
import csv, json, math, os, statistics, sys
from collections import defaultdict

VOLBASE = "/home/hatch/workspace/trading/data/progressive_vol"
OHLCBASE = "/home/hatch/workspace/trading/data/progressive"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
QTY, COST = 100, 40.0
LO, HI = "2026-01-01", "2026-10-28"
SQ, LAST_ENTRY, TRIG_FROM = "15:10", "15:05", "09:45"

import importlib.util
spec = importlib.util.spec_from_file_location("hunt1", f"{OUT}/stocks_hunt1.py")
H = importlib.util.module_from_spec(spec)
sys.argv = ["hunt1"]  # avoid hunt1 main
# hunt1 executes load at import: it defines stocks, DAYS, WINDOWS, exits
spec.loader.exec_module(H)
DAYS = H.DAYS; WINDOWS = H.WINDOWS
exit_trail, exit_fixed = H.exit_trail, H.exit_fixed

def load_vol(sym):
    days = {}
    path = f"{VOLBASE}/{sym}/spot_5m_vol.csv"
    if not os.path.exists(path): return days
    with open(path) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            if not (LO <= d <= HI): continue
            days.setdefault(d, []).append({"time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"]),
                "volume": float(r["volume"])})
    for d in days: days[d] = sorted(days[d], key=lambda x: x["time"])
    return days

VOLDATA = {s: load_vol(s) for s in SYMBOLS}

def vr(bars, i):
    if i < 20: return None
    med = statistics.median(b["volume"] for b in bars[i-20:i])
    if med <= 0: return None
    return bars[i]["volume"] / med

def sq_index(bars):
    return next((i for i, b in enumerate(bars) if b["time"] == SQ), len(bars) - 1)

# ---------- V1: hunt + volume gate (adapted from hunt1.simulate trigger A) ----------
def sim_v1(bars, vol_mult, cap=4):
    n = len(bars); sq_i = sq_index(bars)
    if sq_i < 8: return []
    ext_hi, ext_lo = [], []; h, l = -1e18, 1e18
    for b in bars:
        ext_hi.append(h); ext_lo.append(l)
        h = max(h, b["high"]); l = min(l, b["low"])
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i <= sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        lev_hi, lev_lo = ext_hi[i], ext_lo[i]
        direction = level = None
        if lev_hi > -1e17:
            if b["close"] > lev_hi: direction, level = 1, lev_hi
            elif b["close"] < lev_lo: direction, level = -1, lev_lo
        if direction is not None:
            r = vr(bars, i)
            if r is None or r < vol_mult:
                direction = None  # volume gate blocks this candle only
        if direction is None:
            i += 1; continue
        entry = b["close"]
        xp, xi, reason = exit_trail(bars, i, direction, entry, sq_i)
        net = (xp - entry) * direction * QTY - COST
        trades.append({"entry_time": b["time"], "dir": "LONG" if direction > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "vol_hunt", "level": round(level, 2), "vr": round(r, 2)})
        i = xi + 1
    return trades

# ---------- V2: volume surge follow ----------
def sim_v2(bars, exit_mode, cap=None):
    n = len(bars); sq_i = sq_index(bars)
    if sq_i < 8: return []
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i < sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        r = vr(bars, i)
        sign = 0
        if r is not None and r >= 3.0 and b["high"] > b["low"]:
            rng = (b["high"] - b["low"]) / b["close"]
            pos = (b["close"] - b["low"]) / (b["high"] - b["low"])
            if rng >= 0.004:
                if pos >= 0.75: sign = 1
                elif pos <= 0.25: sign = -1
        if sign == 0:
            i += 1; continue
        ei = i + 1
        if ei > sq_i: break
        entry = bars[ei]["open"]
        if exit_mode == "trail":
            xp, xi, reason = exit_trail(bars, ei, sign, entry, sq_i)
        else:
            xp, xi, reason = exit_fixed(bars, ei, sign, entry, sq_i, 0.010)
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_time": bars[ei]["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "surge", "level": "", "vr": round(r, 2)})
        i = xi + 1
    return trades

# ---------- V3: ladder L-c + volume gate (adapted from stocks_new_strategy.sim_ladder2 "wide") ----------
STEP = 0.004
def band(price, anchor):
    return math.floor(math.log(price / anchor) / math.log(1 + STEP))

def sim_v3(bars, vol_mult=1.5, cap=6):
    n = len(bars); sq_i = sq_index(bars)
    if sq_i < 8: return []
    anchor = bars[0]["open"]
    seed = [b for b in bars if b["time"] < TRIG_FROM] or bars[:6]
    if not seed: return []
    bhi = max(band(b["close"], anchor) for b in seed)
    blo = min(band(b["close"], anchor) for b in seed)
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i <= sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        cb = band(b["close"], anchor)
        sign = 0; eband = None
        if cb > bhi: sign, eband = 1, cb
        elif cb < blo: sign, eband = -1, cb
        bhi = max(bhi, cb); blo = min(blo, cb)
        if sign == 0:
            i += 1; continue
        r = vr(bars, i)
        if r is None or r < vol_mult:
            i += 1; continue
        entry = b["close"]
        stop = entry * (1 - 0.010 * sign); xp = xi = reason = None
        for j in range(i + 1, sq_i + 1):
            bj = bars[j]
            if sign > 0 and bj["low"] <= stop:
                xp, xi, reason = (bj["open"] if bj["open"] < stop else stop), j, "stop"; break
            if sign < 0 and bj["high"] >= stop:
                xp, xi, reason = (bj["open"] if bj["open"] > stop else stop), j, "stop"; break
            if j == sq_i: xp, xi, reason = bj["close"], j, "squareoff"
        if xp is None: xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_time": b["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "ladder_vol", "level": eband, "vr": round(r, 2)})
        i = xi + 1
        upto = [x for x in bars[:i]]
        if upto:
            bhi = max(bhi, max(band(x["close"], anchor) for x in upto))
            blo = min(blo, min(band(x["close"], anchor) for x in upto))
    return trades

# ---------- run / summarize ----------
def metrics(ts):
    if not ts: return {"trades": 0, "net": 0.0, "win_pct": 0.0, "exp": 0.0, "gross_exp": 0.0}
    net = sum(t["net"] for t in ts); wins = sum(1 for t in ts if t["net"] > 0)
    return {"trades": len(ts), "net": round(net, 2), "win_pct": round(100 * wins / len(ts), 1),
            "exp": round(net / len(ts), 2), "gross_exp": round(net / len(ts) + COST, 2)}

def split(ts, a, b): return [t for t in ts if a <= t["date"] <= b]

def summarize(fid, ts):
    s = {"family": fid, "all": metrics(ts),
         "jan_may": metrics(split(ts, "2026-01-01", "2026-05-31")),
         "jun_oct": metrics(split(ts, "2026-06-01", "2026-10-28")),
         "october": metrics(split(ts, "2026-10-01", "2026-10-28")),
         "per_day": round(len(ts) / len(DAYS), 2),
         "rounds": {str(r): metrics([t for t in ts if t["round"] == r]) for r in (1, 2, 3, 4)},
         "rounds5p": metrics([t for t in ts if t["round"] >= 5]),
         "long": metrics([t for t in ts if t["dir"] == "LONG"]),
         "short": metrics([t for t in ts if t["dir"] == "SHORT"]),
         "event": metrics([t for t in ts if t["event"] == "event"]),
         "no_event": metrics([t for t in ts if t["event"] == "no_event"])}
    by_stock = defaultdict(list)
    for t in ts: by_stock[t["symbol"]].append(t)
    sm = sorted(((metrics(v)["net"], k, metrics(v)["trades"]) for k, v in by_stock.items()), reverse=True)
    s["top_stocks"] = sm[:5]; s["bottom_stocks"] = sm[-5:]
    tot = s["all"]["net"]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": 25,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None,
                    "per_stock": {k: metrics(v)["net"] for k, v in by_stock.items()}}
    return s

def save_trades(fid, ts):
    if not ts: return
    cols = ["family", "symbol", "date", "round", "kind", "dir", "entry_time", "entry",
            "level", "vr", "exit_time", "exit", "exit_reason", "net", "event"]
    with open(f"{OUT}/newstratvol_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(ts, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t.get(c, "") for c in cols})

FAMILIES = {
    "V1a": lambda bars: sim_v1(bars, 1.5),
    "V1b": lambda bars: sim_v1(bars, 2.0),
    "V2trail": lambda bars: sim_v2(bars, "trail"),
    "V2T10": lambda bars: sim_v2(bars, "fixed"),
    "V2cap4": lambda bars: sim_v2(bars, "trail", cap=4),
    "V3": lambda bars: sim_v3(bars, 1.5),
}

def run_family(fid):
    fn = FAMILIES[fid]; all_trades = []
    for sym in SYMBOLS:
        for day in DAYS:
            bars = VOLDATA[sym].get(day)
            if not bars or len(bars) < 40: continue
            for t in fn(bars):
                t.update({"symbol": sym, "date": day, "family": fid,
                          "event": "event" if day in WINDOWS[sym] else "no_event"})
                all_trades.append(t)
    return all_trades

if __name__ == "__main__":
    fams = sys.argv[1].split(",") if len(sys.argv) > 1 else list(FAMILIES)
    results = {}
    if os.path.exists(f"{OUT}/newstratvol_results.json"):
        results = json.load(open(f"{OUT}/newstratvol_results.json"))
    for fid in fams:
        ts = run_family(fid)
        save_trades(fid, ts)
        results[fid] = summarize(fid, ts)
        r = results[fid]
        print(fid, "ALL", json.dumps(r["all"]), "JM", json.dumps(r["jan_may"]),
              "JO", json.dumps(r["jun_oct"]), "OCT", json.dumps(r["october"]),
              "per_day", r["per_day"], "breadth", r["breadth"]["stocks_positive"], flush=True)
    json.dump(results, open(f"{OUT}/newstratvol_results.json", "w"), indent=1)
