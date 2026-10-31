"""Parametrized stock-system engine for the S2/S3/S4/S5 continuation.
Paper only, no orders, cash intraday only, NO options.
Base = S1 (see new_stock_system_s1.py). Parameters are the ONLY differences
between versions; each version's frozen spec file states its parameters
before scoring. No timing gates, no OR-high stop, no bounce-bar stops,
no target-shrink: target is always entry +/- 2*risk, stop is always the
structural OR-boundary stop, give-back exit is always 50 at 1R / rest to BE.
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import replay, nifty_day_map

STOCKS = [s for s in SYMBOLS if s not in ("NIFTY", "BANKNIFTY")]
QTY, COST = 100, 40.0
RANK_SETUP = {"setup4_reclaim": 3, "setup4_pullback": 3, "setup3_bounce_rejection": 2,
              "setup2_or_breakout": 1, "setup2_or_breakdown": 1}
S1_ZERO = ["HDFCBANK","HINDCOPPER","HINDUNILVR","IRCTC","ITC","KALYANKJIL",
           "NATIONALUM","NHPC","NTPC","PFC","RECLTD","TATASTEEL","WIPRO","OIL"]

def run_version(room_min=1.5, nifty_mode="bias_only", cap_rank="target",
                year=2026, months=range(1, 11)):
    """nifty_mode: 'or_side' (S1), 'bias_only' (S2),
    'bias_relaxed_room2' (S3 candidate: opposed direction allowed only if room>=2*risk).
    cap_rank: 'target' (S1/S2) or 'room' (later candidate: room_ratio first)."""
    nmap = nifty_day_map()
    # Nifty daily bias per date, from daily data
    _, nifty_daily = load("NIFTY")
    ndl = nifty_daily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0:
            continue
        b, _ = bias_of(ndl[i-1])
        nbias[y["date"].date().isoformat()] = b
    funnel = {"scanned": 0, "or_pass": 0, "signal": 0, "second_close": 0,
              "room": 0, "nifty": 0, "target_ge500": 0, "uncapped": 0}
    weeks = set()
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
            weeks.add(d.isocalendar()[:2])
            prev = dl[i-1]
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
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            sig_idx = None
            for j, c in enumerate(candles):
                if str(c["timestamp"]) == str(sig["timestamp"]):
                    sig_idx = j; break
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
            buf = 0.001 * pdc
            stop = (orl - buf) if direction == "CE" else (orh + buf)
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
            if room < room_min * risk:
                continue
            funnel["room"] += 1
            room_ratio = room / risk
            # Nifty confirmation
            nm = nmap.get(d.date().isoformat())
            if nm is None:
                continue
            if nifty_mode == "or_side":
                ncloses = [cl for (tt, cl) in nm["candles"] if tt <= conf["time"]]
                if not ncloses:
                    continue
                nlast = ncloses[-1]
                if direction == "CE" and not (nlast > nm["orh"]):
                    continue
                if direction == "PE" and not (nlast < nm["orl"]):
                    continue
                nconfirm = nlast
            elif nifty_mode == "bias_only":
                nb = nbias.get(d.date().isoformat())
                if nb is None:
                    continue
                if direction == "CE" and nb == "bearish":
                    continue
                if direction == "PE" and nb == "bullish":
                    continue
                nconfirm = nb
            elif nifty_mode == "bias_relaxed_room2":
                nb = nbias.get(d.date().isoformat())
                if nb is None:
                    continue
                opposed = (direction == "CE" and nb == "bearish") or (direction == "PE" and nb == "bullish")
                if opposed and room_ratio < 2.0:
                    continue
                nconfirm = nb
            else:
                raise ValueError(nifty_mode)
            funnel["nifty"] += 1
            tnet = round(2 * risk * QTY - COST, 2)
            if tnet < 500:
                continue
            funnel["target_ge500"] += 1
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
            out = replay(crecs, sig_idx + 2, entry, stop, target, direction)
            wk = d.isocalendar()[:2]; week = f"{wk[0]}-W{wk[1]:02d}"
            cands.append({
                "symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                "setup": setup, "direction": direction, "bias": bias,
                "signal_time": str(sig["timestamp"]), "confirm_time": str(conf["timestamp"]),
                "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
                "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room_ratio, 3),
                "target_net_rs": tnet, "orh": orh, "orl": orl,
                "nifty_confirm": nconfirm, "nifty_bias": nbias.get(d.date().isoformat()),
                **out,
            })
    funnel["uncapped"] = len(cands)
    return cands, funnel, len(weeks)

def cap_select(cands, cap_rank="target"):
    if cap_rank == "target":
        key = lambda t: (-t["target_net_rs"], -t["room_ratio"], -RANK_SETUP.get(t["setup"], 0), t["date"], t["symbol"])
    else:  # room first
        key = lambda t: (-t["room_ratio"], -t["target_net_rs"], -RANK_SETUP.get(t["setup"], 0), t["date"], t["symbol"])
    ranked = sorted(cands, key=key)
    picked, week_cnt, sym_week = [], {}, set()
    for t in ranked:
        if week_cnt.get(t["week"], 0) >= 3:
            continue
        if (t["symbol"], t["week"]) in sym_week:
            continue
        picked.append(t); week_cnt[t["week"]] = week_cnt.get(t["week"], 0) + 1; sym_week.add((t["symbol"], t["week"]))
    return picked

def metrics(trades):
    if not trades:
        return {"trades": 0, "wins_net_pos": 0, "win_rate_pct": 0.0, "full_targets": 0, "full_target_rate_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0}
    wins = sum(1 for t in trades if t["net_rs"] > 0)
    ft = sum(1 for t in trades if t.get("full_target"))
    net = round(sum(t["net_rs"] for t in trades), 2)
    return {"trades": len(trades), "wins_net_pos": wins, "win_rate_pct": round(wins/len(trades)*100, 1),
            "full_targets": ft, "full_target_rate_pct": round(ft/len(trades)*100, 1),
            "net_rs": net, "expectancy_rs": round(net/len(trades), 2)}

def summarise(name, capped, nweeks):
    m = metrics(capped)
    cum, months = 0.0, {}
    for mo in range(1, 11):
        mt = [t for t in capped if t["month"] == mo]
        mm = metrics(mt); cum = round(cum + mm["net_rs"], 2); months[mo] = {**mm, "cumulative_rs": cum}
    per_stock = {}
    for s in STOCKS:
        per_stock[s] = metrics([t for t in capped if t["symbol"] == s])
    ex_mar = round(sum(t["net_rs"] for t in capped if t["month"] != 3), 2)
    ex_oct = round(sum(t["net_rs"] for t in capped if t["month"] != 10), 2)
    ce = sum(1 for t in capped if t["direction"] == "CE")
    pe = sum(1 for t in capped if t["direction"] == "PE")
    setups = {}
    for t in capped:
        setups[t["setup"]] = setups.get(t["setup"], 0) + 1
    zero_stock_trades = sum(1 for t in capped if t["symbol"] in S1_ZERO)
    return {"version": name, "total": m, "freq_per_week": round(m["trades"]/nweeks, 2) if nweeks else 0,
            "nweeks": nweeks, "months": months, "per_stock": per_stock,
            "ex_march_net_rs": ex_mar, "ex_october_net_rs": ex_oct,
            "direction": {"CE": ce, "PE": pe}, "setups": setups,
            "s1_zero_stock_trades": zero_stock_trades,
            "s1_zero_stock_symbols_traded": sorted(set(t["symbol"] for t in capped if t["symbol"] in S1_ZERO))}

if __name__ == "__main__":
    import csv
    name = sys.argv[1]; room = float(sys.argv[2]); nmode = sys.argv[3]; crank = sys.argv[4]
    uncapped, funnel, nweeks = run_version(room_min=room, nifty_mode=nmode, cap_rank=crank)
    capped = cap_select(uncapped, cap_rank=crank)
    summ = summarise(name, capped, nweeks)
    print(json.dumps({"funnel": funnel, "summary": summ}, indent=2, default=str))
    slug = name.lower()
    with open(os.path.expanduser(f"~/workspace/trading/{slug}_trades_jan_oct_2026.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(capped[0].keys()) if capped else []); w.writeheader(); w.writerows(capped)
    with open(os.path.expanduser(f"~/workspace/trading/{slug}_uncapped_jan_oct_2026.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(uncapped[0].keys()) if uncapped else []); w.writeheader(); w.writerows(uncapped)
    with open(os.path.expanduser(f"~/workspace/trading/data/progressive/{slug}_summary_2026-jan-oct.json"), "w") as f:
        json.dump({"funnel": funnel, "summary": summ, "capped": capped}, f, indent=2, default=str)
