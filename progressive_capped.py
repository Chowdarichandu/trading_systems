"""Capped progressive backtest: V4 + Day Trader skill, portfolio-capped.
Paper only, no orders. Provisional cash rules (NOT Chandu's rules):
100 shares, Rs 40/trade, stop = signal-candle low/high, target = 2x stop
distance, square-off 15:10, one trade/instrument/day, thresholds scaled by
prev-close, Setup 1 skipped, short signals paper-only.
CAP (Chandu correction 2026-10-29 08:28 IST):
- Skill pool is OR-only (flag/oversold dropped as entries: earlier ablation
  showed flag adds losing trades, oversold never fired first).
- Skill OR trades pass ONLY if V4-style filters pass: bias-aligned
  (bearish->PE only, bullish->CE only, neutral->both) AND room >= 200*scale
  to the next PD level in direction AND PD bound (CE close < PDH,
  PE close < PDL).
- V4 trades already carry those filters in find_signal.
- Ranking uses ONLY signal-time information, never trade outcome:
  setup quality (setup4=3, setup3=2, setup2=1, skill OR=0), then room ratio,
  then bias-strong (non-neutral), then results-gate pass.
  Results gate is NEUTRAL (0) for Jan-Mar 2025: the v1 patterns are derived
  from Sep 2025-Jun 2026 quarters, which are in the FUTURE relative to
  Jan-Mar 2025, so using them there would be look-ahead. The gate can only
  apply after the pattern quarters are known.
- Portfolio cap: max 3 trades per ISO week TOTAL per series, and max 1
  trade per symbol per week. Series: capped-V4, capped-Skill, unified
  (best of both, deduplicated by symbol+date).
Reads ~/workspace/trading/data/progressive/<SYMBOL>/spot_5m.csv + spot_daily.csv
"""
import sys, os, json, math
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
QTY, COST = 100, 40.0
SYMBOLS = ["NIFTY","BANKNIFTY","GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY","NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO","NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL","ASTRAL","BDL","OIL","HINDUNILVR"]
SETUP_RANK = {"setup4_pullback":3, "setup4_reclaim":3, "setup3_bounce_rejection":2,
              "setup2_or_breakout":1, "setup2_or_breakdown":1, "or_breakout":0, "or_breakdown":0}

def load(symbol):
    spot = pd.read_csv(os.path.join(BASE, symbol, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, symbol, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def room_ratio(sig_close, direction, pdh, pdc, pdl, scale):
    levels = sorted(set([pdh, pdc, pdl]))
    if direction == "CE":
        nxt = [l for l in levels if l > sig_close]
        room = (min(nxt) - sig_close) if nxt else float("inf")
    else:
        nxt = [l for l in levels if l < sig_close]
        room = (sig_close - max(nxt)) if nxt else float("inf")
    return room / (200 * scale) if scale else 0.0, room

def skill_or_outcome(raw, sig, direction):
    # raw: list of dicts with timestamp as str, time, open/high/low/close
    candles = [c for c in raw if c["time"] >= "09:30"]
    sig_idx = next((i for i, c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
    if sig_idx is None or sig_idx + 1 >= len(candles):
        return None
    entry = float(candles[sig_idx + 1]["open"])
    if direction == "CE":
        stop = entry - 1.0 * (entry - float(sig["low"])); target = entry + 2.0 * (entry - stop)
    else:
        stop = entry + 1.0 * (float(sig["high"]) - entry); target = entry - 2.0 * (stop - entry)
    if entry == stop:
        return None
    exit_reason = exit_price = exit_time = None
    for c in candles[sig_idx + 1:]:
        if direction == "CE":
            if float(c["low"]) <= stop: exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
            if float(c["high"]) >= target: exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
        else:
            if float(c["high"]) >= stop: exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
            if float(c["low"]) <= target: exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
        if c["time"] == "15:10": exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["timestamp"]; break
    if exit_reason is None:
        c = candles[-1]; exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["timestamp"]
    d = 1 if direction == "CE" else -1
    return {"entry": entry, "stop": stop, "target": target, "exit_reason": exit_reason,
            "exit_price": exit_price, "exit_time": exit_time, "net_rs": round(d * (exit_price - entry) * QTY - COST, 2)}

def candidates_for_month(year, month):
    """Return (days, v4_cands, skill_raw_count, skill_filtered_cands)."""
    v4, skill_filt = [], []
    skill_raw = 0
    ndays = None
    for sym in SYMBOLS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        days = 0
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != year or d.month != month or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            days += 1
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            week = d.isocalendar()[:2]  # (year, week)
            # V4 candidate
            r = run_day(day_spot, pdh, pdc, pdl, bias, scale, QTY, COST)
            if r["exit_reason"] in ("target", "stop", "square_off"):
                # signal candle for room: re-find
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                sig_close = float(sig["close"]) if sig is not None else float(r["entry_price"])
                rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
                v4.append({"method": "V4", "symbol": sym, "date": d.date().isoformat(), "week": f"{week[0]}-W{week[1]:02d}",
                           "setup": setup, "direction": direction, "exit_reason": r["exit_reason"],
                           "net_rs": round(float(r["net_rs"]), 2), "setup_rank": SETUP_RANK.get(setup, 0),
                           "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                           "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
            # Skill OR-only candidate
            raw = day_spot.to_dict("records")
            for c in raw:
                c["timestamp"] = str(c["timestamp"])
            setup, direction, sig = find_skill_signal(raw, ("or",))
            if setup is None:
                continue
            skill_raw += 1
            if direction not in allowed:
                continue
            sig_close = float(sig["close"])
            # PD bound, V4-style
            if direction == "CE" and not (sig_close < pdh):
                continue
            if direction == "PE" and not (sig_close < pdl):
                continue
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            if rr < 1.0:
                continue
            out = skill_or_outcome(raw, sig, direction)
            if out is None:
                continue
            skill_filt.append({"method": "Skill", "symbol": sym, "date": d.date().isoformat(), "week": f"{week[0]}-W{week[1]:02d}",
                               "setup": setup, "direction": direction, "exit_reason": out["exit_reason"],
                               "net_rs": out["net_rs"], "setup_rank": 0,
                               "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                               "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
        if ndays is None:
            ndays = days
    return ndays, v4, skill_raw, skill_filt

def cap_select(cands, cap_per_week=3):
    """Rank by setup_rank, room_ratio, bias_strong, results_pass (signal-time only),
    then date/symbol for determinism. Apply 3/week total + 1/symbol/week."""
    ranked = sorted(cands, key=lambda t: (-t["setup_rank"], -t["room_ratio"], -t["bias_strong"], -t["results_pass"], t["date"], t["symbol"]))
    picked, week_count, sym_week = [], {}, set()
    for t in ranked:
        w = t["week"]
        if week_count.get(w, 0) >= cap_per_week:
            continue
        if (t["symbol"], w) in sym_week:
            continue
        picked.append(t); week_count[w] = week_count.get(w, 0) + 1; sym_week.add((t["symbol"], w))
    return picked, ranked

def metrics(trades, ndays, nweeks):
    if not trades:
        return {"trades": 0, "targets": 0, "stops": 0, "square_offs": 0, "win_rate_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0, "max_drawdown_rs": 0.0, "trades_per_week": 0.0}
    net = sum(t["net_rs"] for t in trades); cum = peak = dd = 0.0
    for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
        cum += t["net_rs"]; peak = max(peak, cum); dd = max(dd, peak - cum)
    return {"trades": len(trades), "targets": sum(1 for t in trades if t["exit_reason"] == "target"),
            "stops": sum(1 for t in trades if t["exit_reason"] == "stop"),
            "square_offs": sum(1 for t in trades if t["exit_reason"] == "square_off"),
            "win_rate_pct": round(100 * sum(1 for t in trades if t["exit_reason"] == "target") / len(trades), 1),
            "net_rs": round(net, 2), "expectancy_rs": round(net / len(trades), 2), "max_drawdown_rs": round(dd, 2),
            "trades_per_week": round(len(trades) / nweeks, 2) if nweeks else 0.0}

def split_net(trades):
    idx = sum(t["net_rs"] for t in trades if t["symbol"] in ("NIFTY", "BANKNIFTY"))
    stk = sum(t["net_rs"] for t in trades if t["symbol"] not in ("NIFTY", "BANKNIFTY"))
    return round(idx, 2), round(stk, 2)

def run_capped_month(year, month):
    ndays, v4, skill_raw, skill_filt = candidates_for_month(year, month)
    weeks = sorted(set(t["week"] for t in v4 + skill_filt))
    nweeks = len(weeks)
    v4_cap, _ = cap_select(v4)
    sk_cap, _ = cap_select(skill_filt)
    # Unified: pool, dedup by symbol+date keeping higher setup_rank (V4 first)
    pool = {}
    for t in v4 + skill_filt:
        k = (t["symbol"], t["date"])
        if k not in pool or t["setup_rank"] > pool[k]["setup_rank"]:
            pool[k] = t
    uni_cap, _ = cap_select(list(pool.values()))
    return {"year": year, "month": month, "days": ndays, "weeks": nweeks,
            "raw_v4": len(v4), "raw_skill_or": skill_raw, "filtered_skill": len(skill_filt),
            "v4_capped": metrics(v4_cap, ndays, nweeks), "skill_capped": metrics(sk_cap, ndays, nweeks),
            "unified_capped": metrics(uni_cap, ndays, nweeks),
            "v4_capped_trades": v4_cap, "skill_capped_trades": sk_cap, "unified_capped_trades": uni_cap,
            "v4_split": split_net(v4_cap), "skill_split": split_net(sk_cap), "unified_split": split_net(uni_cap)}

if __name__ == "__main__":
    y, m = int(sys.argv[1]), int(sys.argv[2])
    out = run_capped_month(y, m)
    print(f"{y}-{m:02d} days={out['days']} weeks={out['weeks']} raw_v4={out['raw_v4']} raw_skill_OR={out['raw_skill_or']} filtered_skill={out['filtered_skill']}")
    for k in ("v4_capped", "skill_capped", "unified_capped"):
        print(k, out[k], "split idx/stk:", out[k.replace("_capped", "_split") if k != "unified_capped" else "unified_split"])
    with open(f"/home/hatch/workspace/trading/data/progressive/capped_summary_{y}-{m:02d}.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
