"""S6 stock system — frozen spec in new_stock_system_s6_frozen.md.
Paper only, no orders, cash intraday only, NO options.
Structural change vs S1-S5: stop = signal/confirmation extreme
(CE: min(sig low, conf low); PE: max(sig high, conf high)) instead of the
OR-boundary stop. Everything else: S2 rules (room >=1.5x new risk, Nifty
bias-only, give-back 50 at 1R / rest to BE, target entry +/-2R, prospective
>=Rs 500), except cap = max 1 stock trade per DAY, 1/stock/week retained.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import replay, nifty_day_map

STOCKS = [s for s in SYMBOLS if s not in ("NIFTY", "BANKNIFTY")]
QTY, COST = 100, 40.0
RANK_SETUP = {"setup4_reclaim": 3, "setup4_pullback": 3, "setup3_bounce_rejection": 2,
              "setup2_or_breakout": 1, "setup2_or_breakdown": 1}
S1_ZERO = ["HDFCBANK", "HINDCOPPER", "HINDUNILVR", "IRCTC", "ITC", "KALYANKJIL",
           "NATIONALUM", "NHPC", "NTPC", "PFC", "RECLTD", "TATASTEEL", "WIPRO", "OIL"]
ROOM_MIN = 1.5


def run_s6(year=2026, months=range(1, 11)):
    nmap = nifty_day_map()
    _, nifty_daily = load("NIFTY")
    ndl = nifty_daily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0:
            continue
        b, _ = bias_of(ndl[i - 1])
        nbias[y["date"].date().isoformat()] = b
    funnel = {"scanned": 0, "or_pass": 0, "signal": 0, "second_close": 0,
              "room": 0, "nifty": 0, "target_ge500": 0, "uncapped": 0}
    # per-stage counts by setup/direction (at signal stage and at uncapped stage)
    signal_by = {}
    uncapped_by = {}
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
            or_pct = (orh - orl) / pdc if pdc else 0
            if or_pct < 0.0025 or or_pct > 0.030:
                continue
            funnel["or_pass"] += 1
            setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
            if setup is None or sig is None:
                continue
            funnel["signal"] += 1
            signal_by[(setup, direction)] = signal_by.get((setup, direction), 0) + 1
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            sig_idx = None
            for j, c in enumerate(candles):
                if str(c["timestamp"]) == str(sig["timestamp"]):
                    sig_idx = j
                    break
            if sig_idx is None or sig_idx + 2 >= len(candles):
                continue
            sig_close = float(sig["close"])
            conf = candles[sig_idx + 1]
            conf_close = float(conf["close"])
            if direction == "CE" and not (conf_close > sig_close):
                continue
            if direction == "PE" and not (conf_close < sig_close):
                continue
            funnel["second_close"] += 1
            entry_candle = candles[sig_idx + 2]
            entry = float(entry_candle["open"])
            # S6 stop: retest-hold extreme over signal + confirmation candles
            if direction == "CE":
                stop = min(float(sig["low"]), float(conf["low"]))
            else:
                stop = max(float(sig["high"]), float(conf["high"]))
            risk = abs(entry - stop)
            if risk <= 0:
                continue
            target = entry + (2 * risk if direction == "CE" else -2 * risk)
            levels = sorted(set([pdh, pdc, pdl]))
            if direction == "CE":
                nxt = [l for l in levels if l > entry]
                if not nxt:
                    continue
                room = min(nxt) - entry
            else:
                nxt = [l for l in levels if l < entry]
                if not nxt:
                    continue
                room = entry - max(nxt)
            if room < ROOM_MIN * risk:
                continue
            funnel["room"] += 1
            room_ratio = room / risk
            nm = nmap.get(d.date().isoformat())
            if nm is None:
                continue
            nb = nbias.get(d.date().isoformat())
            if nb is None:
                continue
            if direction == "CE" and nb == "bearish":
                continue
            if direction == "PE" and nb == "bullish":
                continue
            funnel["nifty"] += 1
            tnet = round(2 * risk * QTY - COST, 2)
            if tnet < 500:
                continue
            funnel["target_ge500"] += 1
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]),
                      "close": float(c["close"])} for c in candles]
            out = replay(crecs, sig_idx + 2, entry, stop, target, direction)
            wk = d.isocalendar()[:2]
            week = f"{wk[0]}-W{wk[1]:02d}"
            uncapped_by[(setup, direction)] = uncapped_by.get((setup, direction), 0) + 1
            cands.append({
                "symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                "setup": setup, "direction": direction, "bias": bias,
                "signal_time": str(sig["timestamp"]), "confirm_time": str(conf["timestamp"]),
                "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
                "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room_ratio, 3),
                "target_net_rs": tnet, "orh": orh, "orl": orl,
                "nifty_bias": nb, **out,
            })
    funnel["uncapped"] = len(cands)
    return cands, funnel, trading_days, signal_by, uncapped_by


def cap_select_daily(cands):
    """Max 1 stock trade per day, max 1/stock/week.
    Ranking: prospective target net DESC, room ratio DESC, setup rank DESC."""
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
    return {"total": m, "trading_days": len(trading_days),
            "days_traded": len(days_traded),
            "days_no_valuable_setup": len(trading_days) - len(days_with_cand),
            "days_with_candidate_but_capped_out": len(days_with_cand) - len(days_traded),
            "freq_per_trading_day": round(m["trades"] / len(trading_days), 3) if trading_days else 0,
            "freq_per_week": round(m["trades"] / 44, 2),
            "months": months, "per_stock": per_stock,
            "ex_march_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 3), 2),
            "ex_october_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 10), 2),
            "direction": {"CE": sum(1 for t in capped if t["direction"] == "CE"),
                          "PE": sum(1 for t in capped if t["direction"] == "PE")},
            "setups": {k: sum(1 for t in capped if t["setup"] == k) for k in sorted(set(t["setup"] for t in capped))},
            "s1_zero_stock_trades": sum(1 for t in capped if t["symbol"] in S1_ZERO),
            "s1_zero_stock_symbols_traded": sorted(set(t["symbol"] for t in capped if t["symbol"] in S1_ZERO)),
            "zero_trade_stocks": sorted(s for s in STOCKS if per_stock[s]["trades"] == 0)}


if __name__ == "__main__":
    uncapped, funnel, tdays, signal_by, uncapped_by = run_s6()
    capped, capped_out = cap_select_daily(uncapped)
    summ = summarise(capped, tdays, uncapped)
    print(json.dumps({"funnel": funnel, "capped_out": capped_out,
                      "signal_by": {f"{k[0]}/{k[1]}": v for k, v in signal_by.items()},
                      "uncapped_by": {f"{k[0]}/{k[1]}": v for k, v in uncapped_by.items()},
                      "summary": summ}, indent=2, default=str))
    with open(os.path.expanduser("~/workspace/trading/s6_trades_jan_oct_2026.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(capped[0].keys()) if capped else [])
        w.writeheader(); w.writerows(capped)
    with open(os.path.expanduser("~/workspace/trading/s6_uncapped_jan_oct_2026.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(uncapped[0].keys()) if uncapped else [])
        w.writeheader(); w.writerows(uncapped)
    with open(os.path.expanduser("~/workspace/trading/data/progressive/s6_summary_2026-jan-oct.json"), "w") as f:
        json.dump({"funnel": funnel, "capped_out": capped_out, "summary": summ, "capped": capped}, f, indent=2, default=str)
