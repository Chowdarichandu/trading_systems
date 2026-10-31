#!/usr/bin/env python3
"""Stocks EQUITY exploration round 3. Spec: stocks_equity_explore3_frozen.md
(frozen before scoring). EQUITY CASH intraday only. LONG/SHORT. Paper only.
Per 100 shares provisional, Rs40/trade. UNCAPPED portfolio view.
Tests selection layers (F1 vol/room, F2 Nifty regime, F3 timing, F4 direction,
F5 event, F6 stack) on the V5 and Skill entry pools, Jan-Oct 2026."""
import csv, json, sys, math
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
        "skill_or_breakout":0,"skill_or_breakdown":0}
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
H1_HI, H2_LO = "2026-05-31", "2026-06-01"

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
DAYS_H1 = [d for d in ALL_DAYS if d <= H1_HI]
DAYS_H2 = [d for d in ALL_DAYS if d >= H2_LO]
NDMAP = {d["date"]: i for i, d in enumerate(nifty_daily)}

def nifty_bias(day):
    i = NDMAP.get(day)
    if i is None or i == 0: return "neutral"
    b, _ = bias_of(nifty_daily[i-1])
    return b
NIFTY_BIAS = {d: nifty_bias(d) for d in ALL_DAYS}

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

def adr10(sym, day):
    _, daily = stocks[sym]
    idx = {d["date"]: i for i, d in enumerate(daily)}
    i = idx.get(day)
    if i is None or i < 5: return None
    prior = daily[max(0, i-10):i]
    if len(prior) < 5: return None
    vals = [(d["high"]-d["low"])/d["close"]*100 for d in prior if d["close"]]
    return round(sum(vals)/len(vals), 3) if vals else None

# ---- signal generation (V5 logic copied from stocks_equity_v5_deep.py;
# ---- Skill-full logic copied from stocks_equity_systems_oct.py) ----
DAY_CANDLES = {}
signals = {"V5": [], "SKILL": []}
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
        DAY_CANDLES[(sym, day)] = candles
        orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
        ev_status = "no_event" if day not in WINDOWS[sym] else "event_window"
        adr = adr10(sym, day); nbias = NIFTY_BIAS[day]
        # V5 pool
        v4 = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, V4P)
        skor = tuning_find_signal(candles, orh, orl, orh-orl, raw[0]["open"], pdh, pdc, pdl, bias, SKP)
        pool = []
        for st in (v4, skor):
            if st[0] is not None:
                setup, dirc, sig = st
                idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
                if idx is not None and idx+1 < len(candles): pool.append((setup, dirc, sig, idx))
        if pool:
            def pool_key(p):
                setup, dirc, sig, idx = p
                entry_px = candles[idx+1]["open"]
                return (-RANK.get(setup,0), -(0.01*entry_px*QTY - COST), sig["time"])
            setup, dirc, sig, idx = sorted(pool, key=pool_key)[0]
            signals["V5"].append({"system":"V5","symbol":sym,"date":day,"setup":setup,
                "direction":"LONG" if dirc=="CE" else "SHORT","entry_idx":idx+1,
                "entry":float(candles[idx+1]["open"]),"entry_time":candles[idx+1]["time"],
                "signal_time":sig["time"],"event_status":ev_status,"adr10_pct":adr,"nifty_bias":nbias})
        # Skill full pool
        raw_str = [dict(c) for c in raw]
        sk_setup, sk_dir, sk_sig = find_skill_signal(raw_str, ("or","flag","oversold"))
        if sk_setup is not None:
            idx = next((i for i,c in enumerate(candles) if c["timestamp"] == sk_sig["timestamp"]), None)
            if idx is not None and idx+1 < len(candles):
                signals["SKILL"].append({"system":"SKILL","symbol":sym,"date":day,"setup":sk_setup,
                    "direction":"LONG" if sk_dir=="CE" else "SHORT","entry_idx":idx+1,
                    "entry":float(candles[idx+1]["open"]),"entry_time":candles[idx+1]["time"],
                    "signal_time":sk_sig["time"],"event_status":ev_status,"adr10_pct":adr,"nifty_bias":nbias})

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

EXITS = {"T10": (1.0, 0.5), "T125": (1.25, 0.5)}
TRADES = {pool: {ex: score(signals[pool], *EXITS[ex]) for ex in EXITS} for pool in signals}

def metrics(trades, days):
    n_days = len(days)
    if not trades:
        return {"trades":0,"win_pct":0.0,"target_pct":0.0,"net_rs":0.0,"expectancy_rs":0.0,"trades_per_day":0.0}
    net = sum(t["net_rs"] for t in trades)
    return {"trades": len(trades),
            "win_pct": round(100*sum(1 for t in trades if t["net_rs"]>0)/len(trades),1),
            "target_pct": round(100*sum(1 for t in trades if t["exit_reason"]=="target")/len(trades),1),
            "net_rs": round(net,2), "expectancy_rs": round(net/len(trades),2),
            "trades_per_day": round(len(trades)/n_days,2) if n_days else 0.0}

def fam_metrics(trades):
    return {"all": metrics(trades, ALL_DAYS),
            "jan_may": metrics([t for t in trades if t["date"] <= H1_HI], DAYS_H1),
            "jun_oct": metrics([t for t in trades if t["date"] >= H2_LO], DAYS_H2)}

def regime_ok(t):
    return (t["direction"]=="LONG" and t["nifty_bias"]=="bullish") or \
           (t["direction"]=="SHORT" and t["nifty_bias"]=="bearish")

FAMILIES = {
  "BASE": lambda t: True,
  "F1a_adr2": lambda t: t["adr10_pct"] is not None and t["adr10_pct"] >= 2.0,
  "F1b_adr3": lambda t: t["adr10_pct"] is not None and t["adr10_pct"] >= 3.0,
  "F2_regime": regime_ok,
  "F3_morning": lambda t: "09:15" <= t["entry_time"] < "11:00",
  "F3_afternoon": lambda t: "11:00" <= t["entry_time"] <= "15:10",
  "F4_long": lambda t: t["direction"]=="LONG",
  "F4_short": lambda t: t["direction"]=="SHORT",
  "F5_noevent": lambda t: t["event_status"]=="no_event",
  "F5_F1a_noevent": lambda t: t["event_status"]=="no_event" and t["adr10_pct"] is not None and t["adr10_pct"] >= 2.0,
  "F5_F1b_noevent": lambda t: t["event_status"]=="no_event" and t["adr10_pct"] is not None and t["adr10_pct"] >= 3.0,
  "F6_stack": lambda t: t["event_status"]=="no_event" and t["adr10_pct"] is not None and t["adr10_pct"] >= 2.0 and regime_ok(t),
}

results = {"days": {"all": len(ALL_DAYS), "jan_may": len(DAYS_H1), "jun_oct": len(DAYS_H2)},
           "pools": {}, "families": {}}
for pool in ("V5","SKILL"):
    results["pools"][pool] = {ex: fam_metrics(TRADES[pool][ex]) for ex in EXITS}
    results["families"][pool] = {}
    for ex in EXITS:
        results["families"][pool][ex] = {}
        for fam, fn in FAMILIES.items():
            sel = [t for t in TRADES[pool][ex] if fn(t)]
            results["families"][pool][ex][fam] = fam_metrics(sel)

# ---- persistence: V5 pool, T10, per-stock half nets ----
v5t10 = TRADES["V5"]["T10"]
persist_rows = []
for sym in SYMBOLS:
    st = [t for t in v5t10 if t["symbol"]==sym]
    h1 = [t for t in st if t["date"] <= H1_HI]; h2 = [t for t in st if t["date"] >= H2_LO]
    persist_rows.append({"stock": sym,
        "trades_h1": len(h1), "net_h1_rs": round(sum(t["net_rs"] for t in h1),2),
        "trades_h2": len(h2), "net_h2_rs": round(sum(t["net_rs"] for t in h2),2),
        "net_total_rs": round(sum(t["net_rs"] for t in st),2)})
xs = [r["net_h1_rs"] for r in persist_rows]; ys = [r["net_h2_rs"] for r in persist_rows]
mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
cov = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
sx = math.sqrt(sum((x-mx)**2 for x in xs)); sy = math.sqrt(sum((y-my)**2 for y in ys))
corr = round(cov/(sx*sy), 3) if sx and sy else None
both_pos = [r["stock"] for r in persist_rows if r["net_h1_rs"]>0 and r["net_h2_rs"]>0]
both_neg = [r["stock"] for r in persist_rows if r["net_h1_rs"]<=0 and r["net_h2_rs"]<=0]
mixed = [r["stock"] for r in persist_rows if (r["net_h1_rs"]>0) != (r["net_h2_rs"]>0)]
results["persistence_v5_t10"] = {"pearson_r": corr, "both_positive": both_pos,
    "both_negative": both_neg, "mixed_sign": mixed, "rows": persist_rows}

# ---- CSVs ----
def write_trades(fn, trades, combo_label):
    with open(fn,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","stock","direction","setup","system","entry_time","entry","stop","target",
                    "exit_reason","exit_price","exit_time","net_rs_provisional_per100","pct_captured",
                    "event_status","adr10_pct","nifty_bias","combo"])
        for t in sorted(trades, key=lambda x:(x["date"],x["entry_time"],x["symbol"])):
            w.writerow([t["date"],t["symbol"],t["direction"],t["setup"],t["system"],t["entry_time"],
                        round(t["entry"],2),t["stop"],t["target"],t["exit_reason"],t["exit_price"],
                        t["exit_time"],t["net_rs"],t["pct_captured"],t["event_status"],t["adr10_pct"],
                        t["nifty_bias"],combo_label])
    return fn
files = []
files.append(write_trades(f"{OUT}/eq_explore3_v5_trades_T10_janoct.csv", TRADES["V5"]["T10"], "T10"))
files.append(write_trades(f"{OUT}/eq_explore3_v5_trades_T125_janoct.csv", TRADES["V5"]["T125"], "T125"))
files.append(write_trades(f"{OUT}/eq_explore3_skill_trades_T10_janoct.csv", TRADES["SKILL"]["T10"], "T10"))
files.append(write_trades(f"{OUT}/eq_explore3_skill_trades_T125_janoct.csv", TRADES["SKILL"]["T125"], "T125"))
for pool in ("V5","SKILL"):
    sel = [t for t in TRADES[pool]["T10"] if FAMILIES["F6_stack"](t)]
    files.append(write_trades(f"{OUT}/eq_explore3_{pool.lower()}_f6_trades_T10_janoct.csv", sel, "F6_T10"))
with open(f"{OUT}/eq_explore3_persistence_v5_t10.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["stock","trades_h1","net_h1_rs","trades_h2","net_h2_rs","net_total_rs"])
    w.writeheader(); w.writerows(persist_rows)
files.append(f"{OUT}/eq_explore3_persistence_v5_t10.csv")
results["files"] = files
with open(f"{OUT}/stocks_equity_explore3_results.json","w") as f:
    json.dump(results, f, indent=1)

# ---- console summary ----
def line(name, m):
    a,h1,h2 = m["all"], m["jan_may"], m["jun_oct"]
    print(f"{name:28s} ALL n={a['trades']:5d} win={a['win_pct']:5.1f} tgt={a['target_pct']:5.1f} net={a['net_rs']:12.2f} exp={a['expectancy_rs']:8.2f} tpd={a['trades_per_day']:5.2f} | H1 n={h1['trades']:5d} net={h1['net_rs']:12.2f} exp={h1['expectancy_rs']:8.2f} | H2 n={h2['trades']:5d} net={h2['net_rs']:12.2f} exp={h2['expectancy_rs']:8.2f}")
print(f"DAYS all={len(ALL_DAYS)} jan-may={len(DAYS_H1)} jun-oct={len(DAYS_H2)}")
for pool in ("V5","SKILL"):
    for ex in EXITS:
        print(f"--- {pool} x {ex} ---")
        for fam in FAMILIES: line(fam, results["families"][pool][ex][fam])
print("PERSISTENCE pearson r:", corr, "| both+:", both_pos, "| both-:", both_neg, "| mixed:", mixed)
for r in sorted(persist_rows, key=lambda r:-r["net_total_rs"]):
    print(f"  {r['stock']:12s} H1 n={r['trades_h1']:4d} net={r['net_h1_rs']:11.2f} | H2 n={r['trades_h2']:4d} net={r['net_h2_rs']:11.2f} | TOT {r['net_total_rs']:11.2f}")
print("FILES", files)
