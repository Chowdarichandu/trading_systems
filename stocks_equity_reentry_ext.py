#!/usr/bin/env python3
"""Stocks EQUITY RE-ENTRY re-run. Spec: stocks_equity_reentry_frozen.md
(frozen before scoring). EQUITY CASH intraday only. LONG/SHORT. Paper only.
Per 100 shares provisional, Rs40/trade. NO portfolio cap, NO per-stock/day
cap: after a trade exits, the next fresh signal on the same stock the same
day may enter again (one open position per stock at a time per system).
Systems: V5-stock, Skill, (lA)-stock. Volrix skipped (one-shot by
construction: prev-day trigger, 09:15 entry, 10-session cooldown).
Exits: T05 (+0.5/-0.5), T10 (+1.0/-0.5), T125 (+1.25/-0.5)."""
import csv, json, sys, math
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
from daytrader_cash_tuning import bias_of
from daytrader_skill_run import rsi_wilder

BASE = "/home/hatch/workspace/trading/data/progressive_ext"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["RELIANCE","TCS","ICICIBANK","INFY","BHARTIARTL","SBIN","LT",
           "AXISBANK","KOTAKBANK","BAJFINANCE","HCLTECH","MARUTI","SUNPHARMA",
           "TITAN","M&M","ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","COALINDIA",
           "JSWSTEEL","GRASIM","CIPLA","DRREDDY","EICHERMOT"]
V4P = {"entry_mode":"v4","room_pct":0.0036,"bias_on":True,"signal_end":"baseline","target_ratio":2.0,"stop_scale":1.0}
SKP = {"entry_mode":"skill_or","room_pct":0.0036,"bias_on":True,"signal_end":"baseline","target_ratio":2.0,"stop_scale":1.0}
RANK = {"setup4_pullback":3,"setup4_reclaim":3,"setup3_bounce_rejection":2,
        "setup2_or_breakout":1,"setup2_or_breakdown":1,
        "skill_or_breakout":0,"skill_or_breakdown":0}
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
H1_HI, H2_LO, OCT_LO = "2026-05-31", "2026-06-01", "2026-10-01"
EXITS = {"T05": (0.5, 0.5), "T10": (1.0, 0.5), "T125": (1.25, 0.5)}

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
DAYS = {"all": ALL_DAYS,
        "jan_may": [d for d in ALL_DAYS if d <= H1_HI],
        "jun_oct": [d for d in ALL_DAYS if d >= H2_LO],
        "october": [d for d in ALL_DAYS if d >= OCT_LO]}

from datetime import date, timedelta
def build_windows(sym):
    _, daily = stocks[sym]
    tdays = [d["date"] for d in daily]; idx = {d:i for i,d in enumerate(tdays)}
    windows = set()
    with open(f"{OUT}/stock_event_calendar_ext_jan_oct_2026.csv") as f:
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

# ---------- streaming detectors (verbatim conditions of the originals) ----------
def find_v4_from(candles, orh, orl, or_width, day_open, pdh, pdc, pdl, bias, p, start):
    """daytrader_cash_tuning.find_signal (entry_mode='v4') verbatim, but returns
    the first signal whose candle index >= start; day state is built from the
    day open exactly as the original. Returns (setup, dirc, candle, idx)."""
    allowed = {"PE"} if (p["bias_on"] and bias == "bearish") else \
              {"CE"} if (p["bias_on"] and bias == "bullish") else {"CE", "PE"}
    scale = pdc / 55000.0
    room_thr = lambda close: p["room_pct"] * close
    end2 = "11:30" if p["signal_end"] in ("baseline", "1130") else "14:30"
    end_other = "14:30" if p["signal_end"] in ("baseline", "1430") else "11:30"
    reclaimed = None
    bounced = False
    levels = sorted(set([pdh, pdc, pdl]))
    for i, c in enumerate(candles):
        t, close, high, low, opn = c["time"], c["close"], c["high"], c["low"], c["open"]
        prev_close = candles[i - 1]["close"] if i > 0 else opn
        if day_open < pdc and day_open < pdl and reclaimed is None:
            if close > orh and close > pdc and close > pdl:
                reclaimed = close
        if i >= start:
            if reclaimed is not None and "CE" in allowed and t <= end_other:
                for lvl in (pdc, pdl):
                    if abs(low - lvl) <= 40 * scale and close > lvl and close > opn:
                        nxt = [l for l in levels if l > close]
                        if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                            return "setup4_pullback", "CE", c, i
            if day_open < pdc and "CE" in allowed and t <= end_other and close > orh and close > pdc and close < pdh:
                nxt = [l for l in levels if l > close]
                if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                    return "setup4_reclaim", "CE", c, i
            if or_width <= 360 * scale and t <= end2:
                if close > orh and close < pdh and "CE" in allowed:
                    res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                    if not res or close > min(res):
                        nxt = [l for l in levels if l > close]
                        if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                            return "setup2_or_breakout", "CE", c, i
                if close < orl and close < pdl and "PE" in allowed:
                    nxt = [l for l in levels if l < close]
                    if ((close - max(nxt)) if nxt else math.inf) >= room_thr(close):
                        return "setup2_or_breakdown", "PE", c, i
        if t <= end_other:
            if orh <= high <= orh + 100 * scale:
                bounced = True
            if i >= start and or_width >= 400 * scale and bias == "bearish" and "PE" in allowed:
                if bounced and close < opn and close < orh:
                    blocking = pdc if close > pdc else pdl
                    if close - blocking >= room_thr(close):
                        return "setup3_bounce_rejection", "PE", c, i
    return None, None, None, None

def find_skor_from(candles, orh, orl, start):
    """find_signal entry_mode='skill_or' verbatim, first signal at index >= start."""
    for i, c in enumerate(candles):
        if c["time"] > "11:30":
            break
        if i < start:
            continue
        if c["close"] > orh:
            return "skill_or_breakout", "CE", c, i
        if c["close"] < orl:
            return "skill_or_breakdown", "PE", c, i
    return None, None, None, None

def find_skill_from(raw, start):
    """daytrader_skill_run.find_skill_signal(raw, ('or','flag','oversold'))
    verbatim priority, first signal whose candle index (in the >=09:30 list)
    >= start. Returns (setup, dirc, candle, idx_in_candles)."""
    or_c = [c for c in raw if c["time"] < "09:30"]
    if not or_c:
        return None, None, None, None
    orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
    candles = [c for c in raw if c["time"] >= "09:30"]
    closes = [c["close"] for c in raw]
    rsis = rsi_wilder(closes)
    raw_index = {id(c): i for i, c in enumerate(raw)}
    if True:  # "or" in patterns
        for i, c in enumerate(candles):
            if c["time"] > "11:30":
                break
            if i < start:
                continue
            if c["close"] > orh:
                return "or_breakout", "CE", c, i
            if c["close"] < orl:
                return "or_breakdown", "PE", c, i
    for i, c in enumerate(candles):
        if c["time"] > "14:30":
            break
        if i < start:
            continue
        if i >= 3:  # "flag" in patterns
            w = candles[i - 3:i]
            if all((x["high"] - x["low"]) <= 0.0030 * x["close"] for x in w) and \
               (max(x["high"] for x in w) - min(x["low"] for x in w)) <= 0.0050 * c["close"]:
                fh, fl = max(x["high"] for x in w), min(x["low"] for x in w)
                if c["close"] > fh:
                    return "flag_breakout", "CE", c, i
                if c["close"] < fl:
                    return "flag_breakdown", "PE", c, i
        if i >= 1:  # "oversold" in patterns
            ri = raw_index[id(c)]
            if ri >= 1 and rsis[ri - 1] is not None and rsis[ri - 1] < 30 and c["close"] > candles[i - 1]["high"]:
                return "oversold_bounce", "CE", c, i
    return None, None, None, None

# ---------- exit replay ----------
def replay(candles, entry_idx, sign, entry, tgt_pct, stp_pct):
    target = entry * (1 + sign * tgt_pct / 100); stop = entry * (1 - sign * stp_pct / 100)
    for j in range(entry_idx, len(candles)):
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
        return er, ep, c["time"], j, round(stop, 2), round(target, 2)
    c = candles[-1]
    return "square_off", c["close"], c["time"], len(candles) - 1, round(stop, 2), round(target, 2)

# ---------- per-day context ----------
DAYCTX = {}
for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    for day in ALL_DAYS:
        if day not in dmap or dmap[day] == 0: continue
        raw = spot.get(day, [])
        if not raw: continue
        prev = daily[dmap[day] - 1]
        candles = [c for c in raw if c["time"] >= "09:30"]
        or_c = [c for c in raw if c["time"] < "09:30"]
        if not candles or not or_c: continue
        orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
        bias, _ = bias_of(prev)
        DAYCTX[(sym, day)] = {"raw": raw, "candles": candles, "orh": orh, "orl": orl,
            "or_width": orh - orl, "day_open": raw[0]["open"],
            "pdh": prev["high"], "pdc": prev["close"], "pdl": prev["low"], "bias": bias,
            "event_status": "no_event" if day not in WINDOWS[sym] else "event_window"}

def v4_head(ctx, start):
    return find_v4_from(ctx["candles"], ctx["orh"], ctx["orl"], ctx["or_width"], ctx["day_open"],
                        ctx["pdh"], ctx["pdc"], ctx["pdl"], ctx["bias"], V4P, start)
def skor_head(ctx, start):
    return find_skor_from(ctx["candles"], ctx["orh"], ctx["orl"], start)

def pool_pick(ctx, v4, skor):
    """Frozen V5 dedup: rank desc, prospective T10 net desc, earlier signal."""
    candles = ctx["candles"]
    pool = []
    for st in (v4, skor):
        if st[0] is not None and st[3] + 1 < len(candles):
            pool.append(st)
    if not pool: return None
    def key(p):
        setup, dirc, sig, idx = p
        entry_px = candles[idx + 1]["open"]
        return (-RANK.get(setup, 0), -(0.01 * entry_px * QTY - COST), sig["time"])
    return sorted(pool, key=key)[0]

def la_pick(ctx, day, starts):
    """Earliest pooled candidate >= Nifty break time, <=11:30, same direction
    as Nifty's break. starts = per-source scan starts (advanced past rejected
    heads). Returns (chosen, new_starts) or (None, starts)."""
    nb_dir, nb_time = NIFTY_BREAK.get(day, (None, None))
    if not nb_dir: return None, starts
    starts = dict(starts)
    order = {"v4": 0, "skor": 1}
    while True:
        heads = {}
        v = find_v4_from(ctx["candles"], ctx["orh"], ctx["orl"], ctx["or_width"], ctx["day_open"],
                         ctx["pdh"], ctx["pdc"], ctx["pdl"], ctx["bias"], V4P, starts["v4"])
        if v[0] is not None: heads["v4"] = v
        s = skor_head(ctx, starts["skor"])
        if s[0] is not None: heads["skor"] = s
        if not heads: return None, starts
        def qualifies(h):
            setup, dirc, sig, idx = h
            return sig["time"] >= nb_time and sig["time"] <= "11:30" and \
                   ("LONG" if dirc == "CE" else "SHORT") == nb_dir and idx + 1 < len(ctx["candles"])
        qual = [(src, h) for src, h in heads.items() if qualifies(h)]
        if qual:
            qual.sort(key=lambda sh: (sh[1][2]["time"], order[sh[0]]))
            return qual[0][1], starts
        # advance the earliest non-qualifying head
        src, h = sorted(heads.items(), key=lambda sh: (sh[1][2]["time"], order[sh[0]]))[0]
        starts[src] = h[3] + 1

def run_sequence(system, sym, day, tgt_pct, stp_pct, reentry):
    ctx = DAYCTX.get((sym, day))
    if ctx is None: return []
    candles = ctx["candles"]
    trades = []
    start = 0
    la_starts = {"v4": 0, "skor": 0}
    while True:
        if system == "V5":
            chosen = pool_pick(ctx, v4_head(ctx, start), skor_head(ctx, start))
        elif system == "SKILL":
            s = find_skill_from(ctx["raw"], start)
            chosen = s if s[0] is not None else None
        elif system == "LA":
            chosen, la_starts = la_pick(ctx, day, la_starts)
        if chosen is None: break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles): break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        er, ep, et, exit_idx, stp, tgt = replay(candles, entry_idx, sign, entry, tgt_pct, stp_pct)
        trades.append({"system": system, "symbol": sym, "date": day, "setup": setup,
            "direction": direction, "signal_time": sig["time"], "entry_time": candles[entry_idx]["time"],
            "entry": round(entry, 2), "stop": stp, "target": tgt, "exit_reason": er,
            "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": round(sign * (ep - entry) * QTY - COST, 2),
            "pct_captured": round(sign * (ep - entry) / entry * 100, 3),
            "event_status": ctx["event_status"], "round": len(trades) + 1})
        if not reentry: break
        start = exit_idx
        if system == "LA":
            # next LA round must scan after this trade's signal candle
            la_starts = {"v4": max(la_starts["v4"], idx + 1), "skor": max(la_starts["skor"], idx + 1)}
            # but candidates between exit and next signal are found by la_pick's
            # own filter loop; the binding constraint is signal >= exit candle:
            la_starts = {"v4": max(la_starts["v4"], exit_idx), "skor": max(la_starts["skor"], exit_idx)}
    return trades

# ---------- score both modes ----------
SYSTEMS = ("V5", "SKILL", "LA")
TRADES = {mode: {sys_: {ex: [] for ex in EXITS} for sys_ in SYSTEMS} for mode in ("reentry", "off")}
for sym in SYMBOLS:
    for day in ALL_DAYS:
        if (sym, day) not in DAYCTX: continue
        for sys_ in SYSTEMS:
            for ex, (tp, sp) in EXITS.items():
                TRADES["reentry"][sys_][ex].extend(run_sequence(sys_, sym, day, tp, sp, True))
                TRADES["off"][sys_][ex].extend(run_sequence(sys_, sym, day, tp, sp, False))

def metrics(trades, days):
    n = len(days)
    if not trades:
        return {"trades": 0, "win_pct": 0.0, "target_pct": 0.0, "net_rs": 0.0,
                "expectancy_rs": 0.0, "entries_per_day": 0.0}
    net = sum(t["net_rs"] for t in trades)
    return {"trades": len(trades),
            "win_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "target_pct": round(100 * sum(1 for t in trades if t["exit_reason"] == "target") / len(trades), 1),
            "net_rs": round(net, 2), "expectancy_rs": round(net / len(trades), 2),
            "entries_per_day": round(len(trades) / n, 2) if n else 0.0}

def period_metrics(trades):
    return {p: metrics([t for t in trades if t["date"] in set(DAYS[p])], DAYS[p])
            for p in ("all", "jan_may", "jun_oct", "october")}

def distribution(trades):
    per_day = defaultdict(int); per_sd = defaultdict(int)
    for t in trades:
        per_day[t["date"]] += 1; per_sd[(t["date"], t["symbol"])] += 1
    counts = [per_day.get(d, 0) for d in ALL_DAYS]
    sd = list(per_sd.values())
    return {"mean_entries_per_day": round(sum(counts) / len(counts), 2) if counts else 0.0,
            "max_entries_one_day": max(counts) if counts else 0,
            "days_with_30plus": sum(1 for c in counts if c >= 30),
            "days_with_any": sum(1 for c in counts if c > 0),
            "max_entries_one_stock_day": max(sd) if sd else 0,
            "mean_entries_per_traded_stock_day": round(sum(sd) / len(sd), 2) if sd else 0.0}

results = {"days": {p: len(DAYS[p]) for p in DAYS}, "systems": {}, "validation_gate": {}}
for sys_ in SYSTEMS:
    results["systems"][sys_] = {}
    for ex in EXITS:
        re_t = TRADES["reentry"][sys_][ex]; off_t = TRADES["off"][sys_][ex]
        re_ne = [t for t in re_t if t["event_status"] == "no_event"]
        off_ne = [t for t in off_t if t["event_status"] == "no_event"]
        results["systems"][sys_][ex] = {
            "reentry": {"all_days": period_metrics(re_t), "no_event": period_metrics(re_ne),
                        "distribution": distribution(re_t)},
            "off": {"all_days": period_metrics(off_t), "no_event": period_metrics(off_ne)}}

GATE = {("V5", "T10"): -172092.42, ("V5", "T125"): -155642.34,
        ("SKILL", "T10"): -356884.60, ("SKILL", "T125"): -348883.23}
GATE_N = {("V5", "T10"): 4111, ("V5", "T125"): 4111, ("SKILL", "T10"): 5064, ("SKILL", "T125"): 5064}
for (sys_, ex), expect in GATE.items():
    got = results["systems"][sys_][ex]["off"]["all_days"]["all"]
    ok = abs(got["net_rs"] - expect) < 0.01 and got["trades"] == GATE_N[(sys_, ex)]
    results["validation_gate"][f"{sys_}x{ex}"] = {"expected_net_rs": expect, "got_net_rs": got["net_rs"],
                                                  "expected_trades": GATE_N[(sys_, ex)], "got_trades": got["trades"], "pass": ok}
results["gate_all_pass"] = all(v["pass"] for v in results["validation_gate"].values())

def write_csv(fn, trades, combo):
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","stock","direction","setup","system","round","signal_time","entry_time","entry",
                    "stop","target","exit_reason","exit_price","exit_time","net_rs_provisional_per100",
                    "pct_captured","event_status","combo"])
        for t in sorted(trades, key=lambda x: (x["date"], x["entry_time"], x["symbol"])):
            w.writerow([t["date"], t["symbol"], t["direction"], t["setup"], t["system"], t["round"],
                        t["signal_time"], t["entry_time"], t["entry"], t["stop"], t["target"],
                        t["exit_reason"], t["exit_price"], t["exit_time"], t["net_rs"],
                        t["pct_captured"], t["event_status"], combo])
    return fn

files = []
for sys_ in SYSTEMS:
    for ex in EXITS:
        files.append(write_csv(f"{OUT}/eq_reentry_{sys_.lower()}_trades_{ex}_janoct.csv",
                               TRADES["reentry"][sys_][ex], f"REENTRY_{ex}"))
for sys_ in ("V5", "SKILL"):
    for ex in ("T10", "T125"):
        files.append(write_csv(f"{OUT}/eq_reentry_off_{sys_.lower()}_trades_{ex}_janoct.csv",
                               TRADES["off"][sys_][ex], f"OFF_{ex}"))
results["files"] = files
with open(f"{OUT}/stocks_equity_reentry_results.json", "w") as f:
    json.dump(results, f, indent=1)

print("VALIDATION GATE:", json.dumps(results["validation_gate"]), "ALL PASS:", results["gate_all_pass"])
for sys_ in SYSTEMS:
    for ex in EXITS:
        r = results["systems"][sys_][ex]
        a = r["reentry"]["all_days"]; o = r["off"]["all_days"]
        d = r["reentry"]["distribution"]
        print(f"{sys_:6s} {ex:5s} RE  all n={a['all']['trades']:6d} net={a['all']['net_rs']:13.2f} exp={a['all']['expectancy_rs']:8.2f} "
              f"H1={a['jan_may']['net_rs']:13.2f}({a['jan_may']['trades']}) H2={a['jun_oct']['net_rs']:13.2f}({a['jun_oct']['trades']}) OCT={a['october']['net_rs']:12.2f}({a['october']['trades']}) "
              f"| OFF all n={o['all']['trades']:6d} net={o['all']['net_rs']:13.2f} exp={o['all']['expectancy_rs']:8.2f} "
              f"| dist mean/d={d['mean_entries_per_day']} max={d['max_entries_one_day']} d30+={d['days_with_30plus']} maxSD={d['max_entries_one_stock_day']}")
        ne = r["reentry"]["no_event"]; no = r["off"]["no_event"]
        print(f"       NOEVT RE  n={ne['all']['trades']:6d} net={ne['all']['net_rs']:13.2f} exp={ne['all']['expectancy_rs']:8.2f} H1={ne['jan_may']['net_rs']:13.2f} H2={ne['jun_oct']['net_rs']:13.2f} OCT={ne['october']['net_rs']:12.2f} "
              f"| OFF n={no['all']['trades']:6d} net={no['all']['net_rs']:13.2f} exp={no['all']['expectancy_rs']:8.2f} H1={no['jan_may']['net_rs']:13.2f} H2={no['jun_oct']['net_rs']:13.2f}")
print("FILES", files)
