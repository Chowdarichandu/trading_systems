#!/usr/bin/env python3
"""Stocks EQUITY — V5 validation (Jan-Sep) + target/stop grid tuning.
Spec: stocks_equity_v5_deep_frozen.md (frozen before scoring).
EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders.
Per 100 shares provisional, Rs40/trade. NO portfolio cap (user rule 19:33 IST):
uncapped per-stock view is primary; max 1 trade/stock/day by construction."""
import csv, json, sys
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
from daytrader_cash_tuning import find_signal as tuning_find_signal, bias_of

BASE = "/home/hatch/workspace/trading/data/progressive"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
V4P = {"entry_mode":"v4","room_pct":0.0036,"bias_on":True,"signal_end":"baseline","target_ratio":2.0,"stop_scale":1.0}
SKP = {"entry_mode":"skill_or","room_pct":0.0036,"bias_on":True,"signal_end":"baseline","target_ratio":2.0,"stop_scale":1.0}
RANK = {"setup4_pullback":3,"setup4_reclaim":3,"setup3_bounce_rejection":2,
        "setup2_or_breakout":1,"setup2_or_breakdown":1,
        "skill_or_breakout":0,"skill_or_breakdown":0}
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"

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
nifty_spot, nifty_daily = load_stock("NIFTY")
ALL_DAYS = sorted(d["date"] for d in nifty_daily if ALL_LO <= d["date"] <= ALL_HI)
JANSEP_DAYS = [d for d in ALL_DAYS if d <= "2026-09-30"]
OCT_DAYS = [d for d in ALL_DAYS if d >= "2026-10-01"]

from datetime import date, timedelta
def build_windows(sym):
    _, daily = stocks[sym]
    tdays = [d["date"] for d in daily]; idx = {d:i for i,d in enumerate(tdays)}
    windows = set()
    with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            if r["stock"] != sym: continue
            ev = date.fromisoformat(r["event_date"][:10]) if r["event_date"] else None
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            if ev is None: continue
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            if ev.isoformat() not in idx or eff.isoformat() not in idx: continue
            a = max(0, idx[ev.isoformat()]-7); b = min(len(tdays)-1, idx[eff.isoformat()]+7)
            windows.update(tdays[a:b+1])
    return windows
WINDOWS = {s: build_windows(s) for s in SYMBOLS}

def nifty_break(day):
    raw = nifty_spot.get(day, [])
    or_c = [c for c in raw if c["time"] < "09:30"]; candles = [c for c in raw if c["time"] >= "09:30"]
    if not or_c or not candles: return None, None
    orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
    for c in candles:
        if c["time"] > "11:30": break
        if c["close"] > orh: return "LONG", c["time"]
        if c["close"] < orl: return "SHORT", c["time"]
    return None, None
NIFTY_BREAK = {d: nifty_break(d) for d in ALL_DAYS}

# ---- generate signals once: entries with candle refs kept in memory ----
DAY_CANDLES = {}  # (sym, day) -> candles >=09:30
signals = {"V5": [], "LA": []}   # each: dict with entry info
for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    for day in ALL_DAYS:
        if day not in dmap or dmap[day] == 0: continue
        raw = spot.get(day, [])
        if not raw: continue
        prev = daily[dmap[day]-1]
        pdh, pdc, pdl = prev["high"], prev["close"], prev["low"]
        bias, _ = bias_of(prev)
        candles = [c for c in raw if c["time"] >= "09:30"]
        or_c = [c for c in raw if c["time"] < "09:30"]
        if not candles or not or_c: continue
        orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
        v4 = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, V4P)
        skor = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, SKP)
        pool = []
        for st in (v4, skor):
            if st[0] is not None:
                setup, dirc, sig = st
                idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
                if idx is not None and idx+1 < len(candles): pool.append((setup, dirc, sig, idx))
        if not pool: continue
        DAY_CANDLES[(sym, day)] = candles
        ev_status = "no_event" if day not in WINDOWS[sym] else "event_window"
        def pool_key(p):
            setup, dirc, sig, idx = p
            entry_px = candles[idx+1]["open"]
            return (-RANK.get(setup,0), -(0.01*entry_px*QTY - COST), sig["time"])
        pool_sorted = sorted(pool, key=pool_key)
        setup, dirc, sig, idx = pool_sorted[0]
        signals["V5"].append({"system":"V5","symbol":sym,"date":day,"setup":setup,
            "direction":"LONG" if dirc=="CE" else "SHORT","entry_idx":idx+1,
            "entry":float(candles[idx+1]["open"]),"entry_time":candles[idx+1]["time"],
            "signal_time":sig["time"],"event_status":ev_status})
        nb_dir, nb_time = NIFTY_BREAK.get(day, (None, None))
        if nb_dir:
            cand = [p for p in pool if p[2]["time"] >= nb_time and p[2]["time"] <= "11:30"
                    and ("LONG" if p[1]=="CE" else "SHORT") == nb_dir]
            if cand:
                cand.sort(key=lambda p: p[2]["time"])
                setup, dirc, sig, idx = cand[0]
                signals["LA"].append({"system":"LA","symbol":sym,"date":day,"setup":setup+" (lA-confirmed)",
                    "direction":nb_dir,"entry_idx":idx+1,"entry":float(candles[idx+1]["open"]),
                    "entry_time":candles[idx+1]["time"],"signal_time":sig["time"],"event_status":ev_status})

def replay(sig, tgt_pct, stp_pct):
    candles = DAY_CANDLES[(sig["symbol"], sig["date"])]
    entry = sig["entry"]; sign = 1 if sig["direction"]=="LONG" else -1
    target = entry*(1+sign*tgt_pct/100); stop = entry*(1-sign*stp_pct/100)
    for j in range(sig["entry_idx"], len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop: er, ep = "stop", stop
            elif c["high"] >= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        else:
            if c["high"] >= stop: er, ep = "stop", stop
            elif c["low"] <= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        return er, ep, c["time"], round(stop,2), round(target,2)
    c = candles[-1]
    return "square_off", c["close"], c["time"], round(stop,2), round(target,2)

def score(sig_list, tgt_pct, stp_pct):
    out = []
    for s in sig_list:
        er, ep, et, stp, tgt = replay(s, tgt_pct, stp_pct)
        sign = 1 if s["direction"]=="LONG" else -1
        out.append({**s, "stop":stp, "target":tgt, "exit_reason":er, "exit_price":round(ep,2), "exit_time":et,
                    "net_rs": round(sign*(ep-s["entry"])*QTY - COST, 2),
                    "pct_captured": round(sign*(ep-s["entry"])/s["entry"]*100, 3)})
        out[-1].pop("entry_idx", None)
    return out

def metrics(trades, period_days):
    if not trades:
        return {"trades":0,"win_pct":0.0,"target_pct":0.0,"net_rs":0.0,"expectancy_rs":0.0,
                "maxdd_rs":0.0,"avg_pct":0.0,"mean_per_day":0.0,"days0":len(period_days),"days1":0,"days2plus":0}
    net = sum(t["net_rs"] for t in trades)
    by_day = defaultdict(float); cnt = defaultdict(int)
    for t in trades: by_day[t["date"]] += t["net_rs"]; cnt[t["date"]] += 1
    cum, peak, dd = 0.0, 0.0, 0.0
    for d in period_days:
        cum += by_day.get(d, 0.0); peak = max(peak, cum); dd = min(dd, cum-peak)
    dist = [cnt.get(d,0) for d in period_days]
    return {"trades": len(trades),
            "win_pct": round(100*sum(1 for t in trades if t["net_rs"]>0)/len(trades),1),
            "target_pct": round(100*sum(1 for t in trades if t["exit_reason"]=="target")/len(trades),1),
            "net_rs": round(net,2), "expectancy_rs": round(net/len(trades),2),
            "maxdd_rs": round(dd,2),
            "avg_pct": round(sum(t["pct_captured"] for t in trades)/len(trades),3),
            "mean_per_day": round(len(trades)/len(period_days),2),
            "days0": sum(1 for x in dist if x==0), "days1": sum(1 for x in dist if x==1),
            "days2plus": sum(1 for x in dist if x>=2)}

def split_metrics(trades, days):
    return {"all": metrics(trades, days),
            "no_event": metrics([t for t in trades if t["event_status"]=="no_event"], days),
            "event_window": metrics([t for t in trades if t["event_status"]=="event_window"], days)}

results = {}
# --- T10 trades: V5 and LA, Jan-Sep and Oct ---
v5_t10_all = score(signals["V5"], 1.0, 0.5)
la_t10_all = score(signals["LA"], 1.0, 0.5)
def in_period(ts, lo, hi): return [t for t in ts if lo <= t["date"] <= hi]
v5_t10_js, v5_t10_oct = in_period(v5_t10_all,"2026-01-01","2026-09-30"), in_period(v5_t10_all,"2026-10-01","2026-10-28")
la_t10_js = in_period(la_t10_all,"2026-01-01","2026-09-30")
results["repro_oct_v5_t10"] = split_metrics(v5_t10_oct, OCT_DAYS)
results["v5_t10_jansep"] = split_metrics(v5_t10_js, JANSEP_DAYS)
results["v5_t10_oct"] = results["repro_oct_v5_t10"]
results["la_t10_jansep"] = split_metrics(la_t10_js, JANSEP_DAYS)
# per month Jan-Sep (V5 T10)
months = {}
for m in range(1,10):
    mdays = [d for d in JANSEP_DAYS if int(d[5:7])==m]
    mt = [t for t in v5_t10_js if int(t["date"][5:7])==m]
    months[f"2026-{m:02d}"] = split_metrics(mt, mdays)
results["v5_t10_jansep_bymonth"] = months

# --- grid on V5: Oct + Jan-Sep, all + no_event ---
grid = {}
for tgt in (0.75, 1.0, 1.25):
    for stp in (0.4, 0.5, 0.75):
        key = f"T{tgt}_S{stp}"
        tr = score(signals["V5"], tgt, stp)
        js, oc = in_period(tr,"2026-01-01","2026-09-30"), in_period(tr,"2026-10-01","2026-10-28")
        grid[key] = {"target_pct":tgt,"stop_pct":stp,
                     "jansep": split_metrics(js, JANSEP_DAYS), "oct": split_metrics(oc, OCT_DAYS),
                     "janoct_noevent_net": round(sum(t["net_rs"] for t in tr if t["event_status"]=="no_event"),2)}
results["grid_v5"] = grid
# best combo: rank by jan-sep no-event net + oct no-event net (both must be reported; pick max sum, tie -> T10 order)
best_key, best_sum = None, None
for k, g in grid.items():
    s = g["jansep"]["no_event"]["net_rs"] + g["oct"]["no_event"]["net_rs"]
    if best_sum is None or s > best_sum: best_key, best_sum = k, s
results["best_combo_key"] = best_key
bg = grid[best_key]
best_trades = score(signals["V5"], bg["target_pct"], bg["stop_pct"])
results["best_combo_janoct"] = split_metrics(best_trades, ALL_DAYS)

# per-stock table (best combo, Jan-Oct)
per_stock = {}
for sym in SYMBOLS:
    st = [t for t in best_trades if t["symbol"]==sym]
    per_stock[sym] = {"trades": len(st),
        "win_pct": round(100*sum(1 for t in st if t["net_rs"]>0)/len(st),1) if st else 0.0,
        "net_rs": round(sum(t["net_rs"] for t in st),2),
        "noevent_net_rs": round(sum(t["net_rs"] for t in st if t["event_status"]=="no_event"),2)}
results["best_per_stock_janoct"] = per_stock
# timing + direction diagnostics (best combo, Jan-Oct)
def diag(trades, keyfn):
    out = {}
    for t in trades: out.setdefault(keyfn(t), []).append(t)
    return {k: {"trades": len(v), "win_pct": round(100*sum(1 for t in v if t["net_rs"]>0)/len(v),1),
                "net_rs": round(sum(t["net_rs"] for t in v),2)} for k,v in sorted(out.items())}
results["best_diag_timing"] = diag(best_trades, lambda t: "before_1100" if t["entry_time"] < "11:00" else "from_1100")
results["best_diag_direction"] = diag(best_trades, lambda t: t["direction"])
results["t10_diag_direction_jansep"] = diag(v5_t10_js, lambda t: t["direction"])
results["t10_diag_timing_jansep"] = diag(v5_t10_js, lambda t: "before_1100" if t["entry_time"] < "11:00" else "from_1100")

# --- CSVs ---
def write_trades(fn, trades, combo_label):
    with open(fn,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","stock","direction","setup","system","entry_time","entry","stop","target","exit_reason","exit_price","exit_time","net_rs_provisional_per100","pct_captured","event_status","combo"])
        for t in sorted(trades, key=lambda x:(x["date"],x["entry_time"],x["symbol"])):
            w.writerow([t["date"],t["symbol"],t["direction"],t["setup"],t["system"],t["entry_time"],round(t["entry"],2),t["stop"],t["target"],t["exit_reason"],t["exit_price"],t["exit_time"],t["net_rs"],t["pct_captured"],t["event_status"],combo_label])
    return fn
files = [write_trades(f"{OUT}/eq_v5_jansep_trades_T10.csv", v5_t10_js, "T10"),
         write_trades(f"{OUT}/eq_v5_oct_trades_T10_repro.csv", v5_t10_oct, "T10"),
         write_trades(f"{OUT}/eq_v5_bestcombo_janoct_trades.csv", best_trades, best_key),
         write_trades(f"{OUT}/eq_la_jansep_trades_T10.csv", la_t10_js, "T10")]
results["files"] = files
with open(f"{OUT}/stocks_equity_v5_grid_results.json","w") as f:
    json.dump(results, f, indent=1)
print(json.dumps({k: results[k] for k in ("repro_oct_v5_t10","v5_t10_jansep","la_t10_jansep","best_combo_key")}, indent=1))
print("GRID (jansep no_event net | oct no_event net | jansep all net | oct all net):")
for k,g in grid.items():
    print(k, g["jansep"]["no_event"]["net_rs"], "|", g["oct"]["no_event"]["net_rs"], "|", g["jansep"]["all"]["net_rs"], "|", g["oct"]["all"]["net_rs"])
print("BEST per-stock:", json.dumps(per_stock))
print("BEST diag timing:", results["best_diag_timing"], "direction:", results["best_diag_direction"])
print("FILES", files)
