#!/usr/bin/env python3
"""HUNT-1 — invented intraday STOCK strategy (equity cash, NOT options).
Spec: stocks_hunt1_frozen.md. Paper only, no orders. Per 100 shares
provisional, Rs40/trade. Rolling day-so-far breakout, trail exit,
re-entry hunt up to chain cap."""
import csv, json, os, sys
from collections import defaultdict
from datetime import date, timedelta

BASE = "/home/hatch/workspace/trading/data/progressive"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
QTY, COST = 100, 40.0
LO, HI = "2026-01-01", "2026-10-28"
SQ = "15:10"          # square-off candle (start time)
LAST_ENTRY = "15:05"  # last trigger candle (start time)
TRIG_FROM = "09:45"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{BASE}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{BASE}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]),
                "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d] = sorted(spot[d], key=lambda x: x["time"])
    return spot, daily

stocks = {s: load_stock(s) for s in SYMBOLS}
_, nifty_daily = load_stock("NIFTY")
DAYS = sorted(d["date"] for d in nifty_daily if LO <= d["date"] <= HI)
DAYSET = set(DAYS)

def build_windows(sym):
    _, daily = stocks[sym]
    tdays = [d["date"] for d in daily]; idx = {d: i for i, d in enumerate(tdays)}
    windows = set()
    with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            if r["stock"] != sym: continue
            ev = date.fromisoformat(r["event_date"][:10]) if r["event_date"] else None
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            if ev is None: continue
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            if ev.isoformat() not in idx or eff.isoformat() not in idx: continue
            a = max(0, idx[ev.isoformat()] - 7); b = min(len(tdays) - 1, idx[eff.isoformat()] + 7)
            windows.update(tdays[a:b + 1])
    return windows
WINDOWS = {s: build_windows(s) for s in SYMBOLS}

def adr_ok(sym, day):
    _, daily = stocks[sym]
    rows = [d for d in daily if d["date"] < day][-10:]
    if len(rows) < 10: return False
    return sum((d["high"] - d["low"]) / d["close"] for d in rows) / 10 >= 0.02

ADR = {(s, d): adr_ok(s, d) for s in SYMBOLS for d in DAYS}

# ---------- exit machinery ----------
def exit_trail(bars, ei, sign, entry, sq_i, act=0.005, dist=0.0035, istop=0.005):
    """Return (exit_price, exit_idx, reason). Bars after entry only."""
    stop = entry * (1 - istop * sign)
    best = entry; active = False
    for j in range(ei + 1, sq_i + 1):
        b = bars[j]
        if sign > 0:
            if b["low"] <= stop:
                return (b["open"] if b["open"] < stop else stop), j, ("trail_stop" if active else "stop")
            best = max(best, b["high"])
            if best >= entry * (1 + act):
                active = True; stop = max(stop, best * (1 - dist))
        else:
            if b["high"] >= stop:
                return (b["open"] if b["open"] > stop else stop), j, ("trail_stop" if active else "stop")
            best = min(best, b["low"])
            if best <= entry * (1 - act):
                active = True; stop = min(stop, best * (1 + dist))
        if j == sq_i:
            return b["close"], j, "squareoff"
    b = bars[sq_i]; return b["close"], sq_i, "squareoff"

def exit_fixed(bars, ei, sign, entry, sq_i, tgt_pct, stop_pct=0.005):
    target = entry * (1 + tgt_pct * sign); stop = entry * (1 - stop_pct * sign)
    for j in range(ei + 1, sq_i + 1):
        b = bars[j]
        if sign > 0:
            if b["low"] <= stop: return (b["open"] if b["open"] < stop else stop), j, "stop"
            if b["high"] >= target: return (b["open"] if b["open"] > target else target), j, "target"
        else:
            if b["high"] >= stop: return (b["open"] if b["open"] > stop else stop), j, "stop"
            if b["low"] <= target: return (b["open"] if b["open"] < target else target), j, "target"
        if j == sq_i:
            return b["close"], j, "squareoff"
    b = bars[sq_i]; return b["close"], sq_i, "squareoff"

# ---------- one stock-day ----------
def simulate(bars, cfg):
    """cfg keys: trigger A|B, exit trail|fixed, target, cap (None=uncapped),
    stopout bool, late bool (no entries >=14:30), reclaim bool."""
    n = len(bars)
    sq_i = next((i for i, b in enumerate(bars) if b["time"] == SQ), n - 1)
    if sq_i < 8: return []
    # running extremes BEFORE each bar
    ext_hi, ext_lo = [], []
    h, l = -1e18, 1e18
    for b in bars:
        ext_hi.append(h); ext_lo.append(l)
        h = max(h, b["high"]); l = min(l, b["low"])
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    consec_stop = 0
    last = None  # last exit info for reclaim: dict(dir, exit_price, level, exit_i, dip, used)
    while i <= sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cfg.get("late") and b["time"] >= "14:30": break
        if cfg["cap"] is not None and len(trades) >= cfg["cap"]: break
        # trigger level for this bar
        if cfg["trigger"] == "A":
            lev_hi, lev_lo = ext_hi[i], ext_lo[i]
            if lev_hi <= -1e17: i += 1; continue
        else:  # B: trailing 12 completed bars
            if b["time"] < "10:15" or i < 12: i += 1; continue
            lev_hi = max(x["high"] for x in bars[i - 12:i]); lev_lo = min(x["low"] for x in bars[i - 12:i])
        direction = None; level = None; kind = "breakout"
        clr = cfg.get("clearance", 0.0)
        if b["close"] > lev_hi * (1 + clr): direction, level = 1, lev_hi
        elif b["close"] < lev_lo * (1 - clr): direction, level = -1, lev_lo
        elif cfg.get("reclaim") and last is not None and not last["used"]:
            # dip tracking uses bars strictly after exit and before i
            if not last["dip"]:
                for k in range(last["exit_i"] + 1, i):
                    if last["dir"] > 0 and bars[k]["low"] <= last["exit_price"] * 0.995: last["dip"] = True
                    if last["dir"] < 0 and bars[k]["high"] >= last["exit_price"] * 1.005: last["dip"] = True
            if last["dip"]:
                if last["dir"] > 0 and b["close"] > last["level"]: direction, level, kind = 1, last["level"], "reclaim"
                if last["dir"] < 0 and b["close"] < last["level"]: direction, level, kind = -1, last["level"], "reclaim"
                if direction: last["used"] = True
        if direction is None:
            i += 1; continue
        entry = b["close"]; sign = direction
        if cfg["exit"] == "trail":
            xp, xi, reason = exit_trail(bars, i, sign, entry, sq_i,
                                        cfg.get("trail_act", 0.005), cfg.get("trail_dist", 0.0035))
        else:
            xp, xi, reason = exit_fixed(bars, i, sign, entry, sq_i, cfg["target"])
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_i": i, "entry_time": b["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1, "kind": kind,
            "level": round(level, 2)})
        last = {"dir": sign, "exit_price": xp, "level": level, "exit_i": xi, "dip": False, "used": False}
        if reason == "stop":
            consec_stop += 1
            if cfg.get("stopout") and consec_stop >= 2: break
        else:
            consec_stop = 0
        i = xi + 1
    return trades

FAMILIES = {
    "F0":  {"trigger": "A", "exit": "trail", "cap": 4},
    "F1":  {"trigger": "A", "exit": "fixed", "target": 0.010, "cap": 4},
    "F2":  {"trigger": "A", "exit": "fixed", "target": 0.005, "cap": 4},
    "F3":  {"trigger": "B", "exit": "trail", "cap": 4},
    "F4":  {"trigger": "A", "exit": "trail", "cap": None},
    "F5":  {"trigger": "A", "exit": "trail", "cap": 4, "stopout": True},
    "F6":  {"trigger": "A", "exit": "trail", "cap": 4, "adr": True},
    "F7":  {"trigger": "A", "exit": "trail", "cap": 4, "late": True},
    "F8":  {"trigger": "A", "exit": "trail", "cap": 4, "reclaim": True},
    "F9":  {"trigger": "A", "exit": "trail", "cap": 4, "clearance": 0.001},
    "F10": {"trigger": "A", "exit": "trail", "cap": 4, "trail_act": 0.0075, "trail_dist": 0.005},
}

def run_family(fid, cfg, extra=None):
    cfg = dict(cfg); cfg.update(extra or {})
    all_trades = []
    for sym in SYMBOLS:
        spot, _ = stocks[sym]
        for day in DAYS:
            bars = spot.get(day)
            if not bars or len(bars) < 40: continue
            if cfg.get("adr") and not ADR[(sym, day)]: continue
            ts = simulate(bars, cfg)
            for t in ts:
                t.update({"symbol": sym, "date": day, "family": fid,
                          "event": "event" if day in WINDOWS[sym] else "no_event"})
                all_trades.append(t)
    return all_trades

def metrics(ts):
    if not ts: return {"trades": 0, "net": 0.0, "win_pct": 0.0, "exp": 0.0}
    net = sum(t["net"] for t in ts); wins = sum(1 for t in ts if t["net"] > 0)
    return {"trades": len(ts), "net": round(net, 2), "win_pct": round(100 * wins / len(ts), 1),
            "exp": round(net / len(ts), 2)}

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
         "no_event": metrics([t for t in ts if t["event"] == "no_event"]),
         "morning": metrics([t for t in ts if t["entry_time"] < "12:00"]),
         "afternoon": metrics([t for t in ts if t["entry_time"] >= "12:00"])}
    by_stock = defaultdict(list)
    for t in ts: by_stock[t["symbol"]].append(t)
    sm = sorted(((metrics(v)["net"], k, metrics(v)["trades"]) for k, v in by_stock.items()), reverse=True)
    s["top_stocks"] = sm[:5]; s["bottom_stocks"] = sm[-5:]
    tot = s["all"]["net"]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": 25,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None}
    return s

def save_trades(fid, ts):
    if not ts: return
    cols = ["family", "symbol", "date", "round", "kind", "dir", "entry_time", "entry",
            "level", "exit_time", "exit", "exit_reason", "net", "event"]
    with open(f"{OUT}/hunt1_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(ts, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t[c] for c in cols})

if __name__ == "__main__":
    fams = sys.argv[1].split(",") if len(sys.argv) > 1 else list(FAMILIES)
    results = {}
    if os.path.exists(f"{OUT}/hunt1_results.json"):
        results = json.load(open(f"{OUT}/hunt1_results.json"))
    for fid in fams:
        if fid in FAMILIES:
            cfg = FAMILIES[fid]; label = fid
        else:  # extra family spec passed as JSON in env HUNT_EXTRA: {"FX": {...}}
            cfg = json.loads(os.environ["HUNT_EXTRA"])[fid]; label = fid
        ts = run_family(label, cfg)
        save_trades(label, ts)
        results[label] = summarize(label, ts)
        print(label, json.dumps(results[label]["all"]), "JM", json.dumps(results[label]["jan_may"]),
              "JO", json.dumps(results[label]["jun_oct"]), "OCT", json.dumps(results[label]["october"]),
              "per_day", results[label]["per_day"], flush=True)
    json.dump(results, open(f"{OUT}/hunt1_results.json", "w"), indent=1)
