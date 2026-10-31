"""S8 stock system — frozen spec in new_stock_system_s8_frozen.md.
Paper only, no orders, cash intraday only, NO options.
CE leg: setup4 pullback ONLY, S8 arming = ANY reclaim close above OR high
(regardless of day open vs PDC), dip to OR high within
40*scale + green close above OR high, second close on pullback,
entry next open, stop = pullback low, room >=1.5x to next PD above).
PE leg: S6 exactly (find_signal PE, second close, retest-hold stop
max(sig high, conf high), room >=1.5x to next PD below).
Cap: max 1 stock trade/day, 1/stock/week, ranking target net -> room -> setup rank.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import replay, nifty_day_map

STOCKS = [s for s in SYMBOLS if s not in ("NIFTY", "BANKNIFTY")]
QTY, COST = 100, 40.0
RANK_SETUP = {"setup4_pullback": 3, "setup3_bounce_rejection": 2, "setup2_or_breakdown": 1}
S1_ZERO = ["HDFCBANK", "HINDCOPPER", "HINDUNILVR", "IRCTC", "ITC", "KALYANKJIL",
           "NATIONALUM", "NHPC", "NTPC", "PFC", "RECLTD", "TATASTEEL", "WIPRO", "OIL"]
ROOM_MIN = 1.5
CE_STAGE = {"armed": 0, "pullback": 0, "second_close": 0}


def _pe_candidate(day_spot, candles, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d):
    """S6 PE path. Returns candidate dict or None. candles = post-09:30 records."""
    setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
    if setup is None or sig is None or direction != "PE":
        return None
    sig_idx = None
    for j, c in enumerate(candles):
        if str(c["timestamp"]) == str(sig["timestamp"]):
            sig_idx = j
            break
    if sig_idx is None or sig_idx + 2 >= len(candles):
        return None
    conf = candles[sig_idx + 1]
    if not (float(conf["close"]) < float(sig["close"])):
        return None
    entry_candle = candles[sig_idx + 2]
    entry = float(entry_candle["open"])
    stop = max(float(sig["high"]), float(conf["high"]))
    risk = stop - entry
    if risk <= 0:
        return None
    target = entry - 2 * risk
    levels = sorted(set([pdh, pdc, pdl]))
    nxt = [l for l in levels if l < entry]
    if not nxt:
        return None
    room = entry - max(nxt)
    if room < ROOM_MIN * risk:
        return None
    if nb == "bullish":  # Nifty bias-only: PE blocked on bullish Nifty days
        return None
    tnet = round(2 * risk * QTY - COST, 2)
    if tnet < 500:
        return None
    crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]),
              "close": float(c["close"])} for c in candles]
    out = replay(crecs, sig_idx + 2, entry, stop, target, "PE")
    return {"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
            "setup": setup, "direction": "PE", "bias": bias,
            "signal_time": str(sig["timestamp"]), "confirm_time": str(conf["timestamp"]),
            "entry_time": entry_candle["time"],
            "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
            "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room / risk, 3),
            "target_net_rs": tnet, "orh": orh, "orl": orl, "nifty_bias": nb, **out}


def _ce_pullback_candidate(candles, day_open, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d):
    """S7 CE pullback path. Returns candidate dict or None."""
    if "CE" not in ({"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}):
        return None
    if nb == "bearish":  # Nifty bias-only: CE blocked on bearish Nifty days
        return None
    levels = sorted(set([pdh, pdc, pdl]))
    # 1. Arming reclaim close
    arm_idx = None
    for j, c in enumerate(candles):
        if c["time"] > "14:30":
            break
        close = float(c["close"])
        if close > orh and close > pdc and close < pdh:
            nxt = [l for l in levels if l > close]
            room = (min(nxt) - close) if nxt else float("inf")
            if room >= 200 * scale:
                arm_idx = j
                CE_STAGE["armed"] += 1
                break
    if arm_idx is None:
        return None
    # 2. First pullback candle after arming
    pb_idx = None
    for j in range(arm_idx + 1, len(candles)):
        c = candles[j]
        if c["time"] > "14:30":
            break
        low, close, opn = float(c["low"]), float(c["close"]), float(c["open"])
        if abs(low - orh) <= 40 * scale and close > orh and close > opn:
            pb_idx = j
            CE_STAGE["pullback"] += 1
            break
    if pb_idx is None or pb_idx + 2 >= len(candles):
        return None
    # 3. Second close on the pullback candle
    pb = candles[pb_idx]
    conf = candles[pb_idx + 1]
    if not (float(conf["close"]) > float(pb["close"])):
        return None
    CE_STAGE["second_close"] += 1
    entry_candle = candles[pb_idx + 2]
    entry = float(entry_candle["open"])
    stop = float(pb["low"])
    risk = entry - stop
    if risk <= 0:
        return None
    target = entry + 2 * risk
    nxt = [l for l in levels if l > entry]
    if not nxt:
        return None
    room = min(nxt) - entry
    if room < ROOM_MIN * risk:
        return None
    tnet = round(2 * risk * QTY - COST, 2)
    if tnet < 500:
        return None
    crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]),
              "close": float(c["close"])} for c in candles]
    out = replay(crecs, pb_idx + 2, entry, stop, target, "CE")
    return {"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
            "setup": "setup4_pullback", "direction": "CE", "bias": bias,
            "signal_time": str(pb["timestamp"]), "confirm_time": str(conf["timestamp"]),
            "entry_time": entry_candle["time"], "arm_time": candles[arm_idx]["time"],
            "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
            "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room / risk, 3),
            "target_net_rs": tnet, "orh": orh, "orl": orl, "nifty_bias": nb, **out}


def run_s8(year=2026, months=range(1, 11)):
    nmap = nifty_day_map()
    _, nifty_daily = load("NIFTY")
    ndl = nifty_daily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0:
            continue
        b, _ = bias_of(ndl[i - 1])
        nbias[y["date"].date().isoformat()] = b
    funnel = {"scanned": 0, "or_pass": 0, "pe_signal": 0, "ce_armed": 0,
              "ce_pullback": 0, "ce_second_close": 0, "uncapped": 0}
    trading_days = set()
    cands = []
    for sym in STOCKS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != year or d.month not in months or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            funnel["scanned"] += 1
            trading_days.add(d.date().isoformat())
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            or_c = day_spot[day_spot["time"] < "09:30"]
            if or_c.empty:
                continue
            orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
            if not (0.0025 <= (orh - orl) / pdc <= 0.030 if pdc else False):
                continue
            funnel["or_pass"] += 1
            nb = nbias.get(d.date().isoformat())
            if nb is None:
                continue
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            wk = d.isocalendar()[:2]
            week = f"{wk[0]}-W{wk[1]:02d}"
            day_open = float(day_spot.iloc[0]["open"])
            day_cands = []
            pe = _pe_candidate(day_spot, candles, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d)
            if pe is not None:
                day_cands.append(pe)
            # funnel counters for CE path stages (diagnostic, independent of PE)
            ce = _ce_pullback_candidate(candles, day_open, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d)
            if ce is not None:
                day_cands.append(ce)
            if not day_cands:
                continue
            # one candidate per stock-day: earliest entry, tie -> higher target net
            day_cands.sort(key=lambda t: (t["entry_time"], -t["target_net_rs"]))
            cands.append(day_cands[0])
    funnel["uncapped"] = len(cands)
    funnel["ce_armed"] = CE_STAGE["armed"]
    funnel["ce_pullback"] = CE_STAGE["pullback"]
    funnel["ce_second_close"] = CE_STAGE["second_close"]
    return cands, funnel, trading_days


def cap_select_daily(cands):
    key = lambda t: (-t["target_net_rs"], -t["room_ratio"], -RANK_SETUP.get(t["setup"], 0),
                     t["date"], t["symbol"])
    ranked = sorted(cands, key=key)
    picked, days, sym_week = [], set(), set()
    capped_out = 0
    for t in ranked:
        if t["date"] in days or (t["symbol"], t["week"]) in sym_week:
            capped_out += 1
            continue
        picked.append(t)
        days.add(t["date"])
        sym_week.add((t["symbol"], t["week"]))
    return picked, capped_out


def metrics(trades):
    if not trades:
        return {"trades": 0, "wins_net_pos": 0, "win_rate_pct": 0.0, "full_targets": 0,
                "full_target_rate_pct": 0.0, "partial_be_wins": 0, "net_rs": 0.0, "expectancy_rs": 0.0}
    wins = sum(1 for t in trades if t["net_rs"] > 0)
    ft = sum(1 for t in trades if t.get("full_target"))
    pb = sum(1 for t in trades if t.get("exit_reason") == "stop_after_partial_BE")
    net = round(sum(t["net_rs"] for t in trades), 2)
    return {"trades": len(trades), "wins_net_pos": wins, "win_rate_pct": round(wins / len(trades) * 100, 1),
            "full_targets": ft, "full_target_rate_pct": round(ft / len(trades) * 100, 1),
            "partial_be_wins": pb, "net_rs": net, "expectancy_rs": round(net / len(trades), 2)}


def summarise(capped, trading_days, uncapped):
    m = metrics(capped)
    cum, months = 0.0, {}
    for mo in range(1, 11):
        mt = [t for t in capped if t["month"] == mo]
        mm = metrics(mt)
        cum = round(cum + mm["net_rs"], 2)
        months[mo] = {**mm, "cumulative_rs": cum}
    per_stock = {s: metrics([t for t in capped if t["symbol"] == s]) for s in STOCKS}
    days_traded = sorted(set(t["date"] for t in capped))
    days_with_cand = sorted(set(t["date"] for t in uncapped))
    ce = [t for t in capped if t["direction"] == "CE"]
    pe = [t for t in capped if t["direction"] == "PE"]
    return {"total": m, "trading_days": len(trading_days),
            "days_traded": len(days_traded),
            "days_no_valuable_setup": len(trading_days) - len(days_with_cand),
            "days_with_candidate_but_capped_out": len(days_with_cand) - len(days_traded),
            "freq_per_trading_day": round(m["trades"] / len(trading_days), 3) if trading_days else 0,
            "freq_per_week": round(m["trades"] / 44, 2),
            "months": months, "per_stock": per_stock,
            "ex_march_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 3), 2),
            "ex_october_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 10), 2),
            "direction": {"CE": len(ce), "PE": len(pe)},
            "setups": {k: sum(1 for t in capped if t["setup"] == k) for k in sorted(set(t["setup"] for t in capped))},
            "ce_leg": metrics(ce), "pe_leg": metrics(pe),
            "s1_zero_stock_trades": sum(1 for t in capped if t["symbol"] in S1_ZERO),
            "s1_zero_stock_symbols_traded": sorted(set(t["symbol"] for t in capped if t["symbol"] in S1_ZERO)),
            "zero_trade_stocks": sorted(s for s in STOCKS if per_stock[s]["trades"] == 0)}


if __name__ == "__main__":
    uncapped, funnel, tdays = run_s8()
    capped, capped_out = cap_select_daily(uncapped)
    summ = summarise(capped, tdays, uncapped)
    print(json.dumps({"funnel": funnel, "capped_out": capped_out, "summary": summ}, indent=2, default=str))
    with open(os.path.expanduser("~/workspace/trading/s8_trades_jan_oct_2026.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(capped[0].keys()) if capped else [])
        w.writeheader(); w.writerows(capped)
    with open(os.path.expanduser("~/workspace/trading/s8_uncapped_jan_oct_2026.csv"), "w", newline="") as f:
        _fields = []
        for _r in uncapped:
            for _k in _r.keys():
                if _k not in _fields:
                    _fields.append(_k)
        w = csv.DictWriter(f, fieldnames=_fields)
        w.writeheader(); w.writerows(uncapped)
    with open(os.path.expanduser("~/workspace/trading/data/progressive/s8_summary_2026-jan-oct.json"), "w") as f:
        json.dump({"funnel": funnel, "capped_out": capped_out, "summary": summ, "capped": capped}, f, indent=2, default=str)
