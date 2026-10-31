#!/usr/bin/env python3
"""Stocks EQUITY small-target run, Oct 2026. Spec: stocks_equity_smalltarget_frozen.md
EQUITY CASH intraday only. LONG/SHORT language. Paper only, no orders.
Per 100 shares provisional, Rs40/trade. Systems: V5-stock, Skill, (lA)-stock, Volrix-stock.
Exits: T05 (tgt .5/stop .5), T10 (tgt 1/stop .5), TSYS (tgt 1, signal stop capped 1%)."""
import csv, json, os, sys
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
from daytrader_cash_tuning import find_signal as tuning_find_signal, bias_of
from daytrader_skill_run import find_skill_signal

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
        "skill_or_breakout":0,"skill_or_breakdown":0,
        "or_breakout":2,"or_breakdown":2,"flag_breakout":1,"flag_breakdown":1,"oversold_bounce":0}
QTY, COST = 100, 40.0
LO, HI = "2026-10-01", "2026-10-28"

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
OCT_DAYS = sorted(d["date"] for d in nifty_daily if LO <= d["date"] <= HI)

# ---- event windows (same code as stocks_v2_versions_oct30.py) ----
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
NIFTY_BREAK = {d: nifty_break(d) for d in OCT_DAYS}

# ---- exit replay ----
def replay(candles, start_idx, sign, entry, stop, target):
    """candles >=09:30 (or >=09:15 for volrix when start at 0 of full list). Stop first on ties."""
    for j in range(start_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10": return "square_off", c["close"], c["time"]
    c = candles[-1]
    return "square_off", c["close"], c["time"]

def make_trade(system, sym, day, setup, direction, candles, sig_idx, sig, entry_idx, drop_pct=None):
    if entry_idx >= len(candles): return None
    entry = float(candles[entry_idx]["open"])
    sign = 1 if direction == "LONG" else -1
    sys_stop = None
    if sig is not None:
        sys_stop = float(sig["low"]) if sign == 1 else float(sig["high"])
    out = {"system": system, "symbol": sym, "date": day, "setup": setup, "direction": direction,
           "entry_time": candles[entry_idx]["time"], "entry": round(entry,2),
           "signal_time": sig["time"] if sig is not None else "09:15",
           "event_status": "no_event" if day not in WINDOWS[sym] else "event_window",
           "setup_rank": RANK.get(setup, -1), "prev_day_drop_pct": drop_pct}
    for variant in ("T05","T10","TSYS"):
        if variant == "T05": tgt, stp = entry*(1+sign*0.005), entry*(1-sign*0.005)
        elif variant == "T10": tgt, stp = entry*(1+sign*0.01), entry*(1-sign*0.005)
        else:
            if sys_stop is None: continue
            if sign == 1:
                if sys_stop >= entry: continue
                stp = max(sys_stop, entry*0.99)
            else:
                if sys_stop <= entry: continue
                stp = min(sys_stop, entry*1.01)
            tgt = entry*(1+sign*0.01)
        er, ep, et = replay(candles, entry_idx, sign, entry, stp, tgt)
        net = round(sign*(ep-entry)*QTY - COST, 2)
        out[variant] = {"stop": round(stp,2), "target": round(tgt,2), "exit_reason": er,
                        "exit_price": round(ep,2), "exit_time": et, "net_rs": net,
                        "pct_captured": round(sign*(ep-entry)/entry*100, 3)}
    return out if any(v in out for v in ("T05","T10","TSYS")) else None

# ---- signal generation ----
signals = defaultdict(list)  # system -> raw candidate dicts (with candles refs resolved to trades)
trades = defaultdict(list)
for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    # Volrix cooldown state across full history
    last_volrix_i = -100
    volrix_days = {}
    for i in range(2, len(daily)):
        prev, prev2 = daily[i-1], daily[i-2]
        pct = (prev["close"]-prev2["close"])/prev2["close"]*100
        if pct <= -2.0 and i - last_volrix_i > 10:
            volrix_days[daily[i]["date"]] = round(pct,2); last_volrix_i = i
    for day in OCT_DAYS:
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
        # V4 + SkillOR signals (tuning engine)
        v4 = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, V4P)
        skor = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, SKP)
        def to_trade(system, sig_tuple):
            if sig_tuple[0] is None: return None
            setup, dirc, sig = sig_tuple
            idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
            if idx is None: return None
            direction = "LONG" if dirc == "CE" else "SHORT"
            return make_trade(system, sym, day, setup, direction, candles, idx, sig, idx+1), (setup, direction, sig, idx)
        # Skill full (own entries)
        raw_str = [dict(c) for c in raw]
        sk_setup, sk_dir, sk_sig = find_skill_signal(raw_str, ("or","flag","oversold"))
        sk_trade = None
        if sk_setup is not None:
            idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sk_sig["timestamp"]), None)
            if idx is not None:
                sk_trade = make_trade("SKILL", sym, day, sk_setup, "LONG" if sk_dir=="CE" else "SHORT", candles, idx, sk_sig, idx+1)
                if sk_trade: trades["SKILL"].append(sk_trade)
        # V5 pool: dedup v4 vs skillOR
        pool = []
        for src, st in (("v4", v4), ("skor", skor)):
            if st[0] is not None:
                setup, dirc, sig = st
                idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
                if idx is not None: pool.append((setup, dirc, sig, idx))
        if pool:
            def pool_key(p):
                setup, dirc, sig, idx = p
                entry_px = candles[idx+1]["open"] if idx+1 < len(candles) else sig["close"]
                prosp = 0.01*entry_px*QTY - COST
                return (-RANK.get(setup,0), -prosp, sig["time"])
            pool.sort(key=pool_key)
            setup, dirc, sig, idx = pool[0]
            t = make_trade("V5", sym, day, setup, "LONG" if dirc=="CE" else "SHORT", candles, idx, sig, idx+1)
            if t: trades["V5"].append(t)
        # (lA): pooled signal at/after Nifty break, <=11:30, same direction
        nb_dir, nb_time = NIFTY_BREAK.get(day, (None, None))
        if nb_dir and pool:
            cand = [p for p in pool if p[2]["time"] >= nb_time and p[2]["time"] <= "11:30"
                    and ("LONG" if p[1]=="CE" else "SHORT") == nb_dir]
            if cand:
                cand.sort(key=lambda p: p[2]["time"])
                setup, dirc, sig, idx = cand[0]
                t = make_trade("LA", sym, day, setup+" (lA-confirmed)", nb_dir, candles, idx, sig, idx+1)
                if t: trades["LA"].append(t)
        # standalone V4/SkillOR kept only via V5/SKILL; Volrix:
        if day in volrix_days:
            full = raw  # entry at 09:15 open = first candle
            t = make_trade("VOLRIX", sym, day, "volrix_rebound", "LONG", full, 0, None, 0, drop_pct=volrix_days[day])
            # Volrix has no signal candle: TSYS not applicable (no sys stop) -> T05/T10 only; replay from candle 0 of >=09:15 list
            if t: trades["VOLRIX"].append(t)

# Volrix TSYS: no signal stop exists -> remove TSYS key (make_trade skipped it since sig None) OK.

def metrics(trade_list, variant, days=18):
    ts = [t for t in trade_list if variant in t]
    if not ts: return {"trades":0,"win_pct":0.0,"target_pct":0.0,"net_rs":0.0,"expectancy_rs":0.0,"avg_pct":0.0,"per_week":0.0}
    net = sum(t[variant]["net_rs"] for t in ts)
    return {"trades": len(ts),
            "win_pct": round(100*sum(1 for t in ts if t[variant]["net_rs"]>0)/len(ts),1),
            "target_pct": round(100*sum(1 for t in ts if t[variant]["exit_reason"]=="target")/len(ts),1),
            "net_rs": round(net,2), "expectancy_rs": round(net/len(ts),2),
            "avg_pct": round(sum(t[variant]["pct_captured"] for t in ts)/len(ts),3),
            "per_week": round(len(ts)/(days/5),2),
            "gross_rs": round(sum(t[variant]["net_rs"]+COST for t in ts),2)}

def cap_one_per_day(trade_list, variant, volrix_rank=False):
    by_day = defaultdict(list)
    for t in trade_list:
        if variant in t: by_day[t["date"]].append(t)
    picked = []
    for day, ts in by_day.items():
        if volrix_rank:
            ts.sort(key=lambda t: -abs(t.get("prev_day_drop_pct") or 0))
        else:
            ts.sort(key=lambda t: (-t["setup_rank"], -(0.01*t["entry"]*QTY-COST), t["entry_time"]))
        picked.append(ts[0])
    return sorted(picked, key=lambda t: t["date"])

results = {}
for system in ("V5","SKILL","LA","VOLRIX"):
    results[system] = {}
    for variant in ("T05","T10","TSYS"):
        unc = metrics(trades[system], variant)
        cap = metrics(cap_one_per_day(trades[system], variant, volrix_rank=(system=="VOLRIX")), variant)
        results[system][variant] = {"uncapped": unc, "capped1day": cap}

# Unified: dedup stock+day+direction earliest entry across V5/SKILL/LA/VOLRIX
uni_map = {}
for system in ("V5","SKILL","LA","VOLRIX"):
    for t in trades[system]:
        k = (t["symbol"], t["date"], t["direction"])
        if k not in uni_map or t["entry_time"] < uni_map[k]["entry_time"]:
            keep = dict(t); keep["systems"] = [system]
            if k in uni_map: keep["systems"] = sorted(set(uni_map[k].get("systems",[])+[system]))
            uni_map[k] = keep
        else:
            uni_map[k]["systems"] = sorted(set(uni_map[k].get("systems",[])+[system]))
unified = list(uni_map.values())
results["UNIFIED"] = {}
for variant in ("T05","T10","TSYS"):
    results["UNIFIED"][variant] = {"uncapped": metrics(unified, variant),
                                   "capped1day": metrics(cap_one_per_day(unified, variant), variant)}
# no-event subset of unified (all variants, both views)
results["UNIFIED_NOEVENT"] = {}
for variant in ("T05","T10","TSYS"):
    ne = [t for t in unified if t["event_status"]=="no_event"]
    results["UNIFIED_NOEVENT"][variant] = {"uncapped": metrics(ne, variant),
                                           "capped1day": metrics(cap_one_per_day(ne, variant), variant)}

# write CSVs: one per system per variant (uncapped view), plus unified best candidates all variants
def write_csv(system, trade_list, variant):
    rows = [t for t in trade_list if variant in t]
    if not rows: return None
    fn = f"{OUT}/eq_{system.lower()}_oct_trades_{variant}.csv"
    with open(fn,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","stock","direction","setup","system(s)","entry_time","entry","stop","target","exit_reason","exit_price","exit_time","net_rs_provisional_per100","pct_captured","event_status"])
        for t in sorted(rows, key=lambda x:(x["date"],x["entry_time"])):
            v = t[variant]
            w.writerow([t["date"],t["symbol"],t["direction"],t["setup"],"+".join(t.get("systems",[t["system"]])),t["entry_time"],t["entry"],v["stop"],v["target"],v["exit_reason"],v["exit_price"],v["exit_time"],v["net_rs"],v["pct_captured"],t["event_status"]])
    return fn
files = []
for system in ("V5","SKILL","LA","VOLRIX"):
    for variant in ("T05","T10","TSYS"):
        fn = write_csv(system, trades[system], variant)
        if fn: files.append(fn)
for variant in ("T05","T10","TSYS"):
    fn = write_csv("UNIFIED", unified, variant)
    if fn: files.append(fn)

with open(f"{OUT}/stocks_equity_oct_results.json","w") as f:
    json.dump({"window_days":18,"results":results,"files":files,
               "nifty_break_days":{d:v for d,v in NIFTY_BREAK.items()}}, f, indent=1)
print(json.dumps(results, indent=1))
print("FILES", files)
