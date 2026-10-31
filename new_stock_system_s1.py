"""S1 — NEW intraday STOCK system, provisional, FROZEN before scoring.
Paper only, no orders, cash intraday only, NO options.
Leverages old V4 levels/setups; addresses known V4 issues with specific rules.
See new_stock_system_s1.md for the frozen rule list and issue mapping.

Rules (frozen, 2026-10-29, before any S1 scoring):
- Universe: 25 stocks only. NIFTY is used ONLY as index-confirmation, never traded here.
- Base signal: old V4 find_signal (setups 2 OR breakout/breakdown, 3 bounce
  rejection, 4 reclaim/pullback). Setup 1 skipped (no Red bands for stocks).
  Bias filter as old (bearish->PE only, bullish->CE only, neutral->both).
- OR filter (new): OR width / prev close must be in [0.25%, 3.0%]; else no-trade.
  Addresses thin/wide OR noise.
- Confirmation (new, re-test with caveat): the candle immediately after the
  signal candle must close FURTHER in signal direction than the signal close
  (CE: conf_close > sig_close; PE: conf_close < sig_close). Entry = open of
  the candle after confirmation. If not, no trade that day (no rescan, no
  re-entry). Caveat: second-close was weak on Nifty Cluster 1 PE alone
  (day-1 loss halved, not turned green); re-tested here because stock ORs
  are price-scaled differently and confirmation here is paired with a
  structural stop and Nifty confirmation, not used alone.
- Structural stop (new, replaces signal-candle stop): CE stop = OR low
  minus 0.1% of prev close; PE stop = OR high plus 0.1% of prev close.
  Stop is at/just outside the OR boundary, NOT at the signal candle's
  inside-OR extreme. Risk = |entry - stop|; invalid if risk <= 0.
- Room filter (new, fixes infinite-room artefact): room to the NEXT PD
  level in direction (PDH/PDC/PDL) must be finite AND >= 2*risk.
  If no PD level lies beyond entry, room is NOT treated as infinite pass —
  it fails. Target = entry +/- 2*risk.
- Index confirmation (new): at confirmation time, Nifty's last closed 5-min
  candle must be on the same OR side as the stock direction
  (CE: Nifty close > Nifty OR high; PE: Nifty close < Nifty OR low).
  Nifty inside its OR = no trade.
- Give-back exit (new): at 1.0x risk, book 50 shares (partial). Remaining
  50 shares' stop trails to breakeven (entry). Remaining target stays 2x
  risk; square-off 15:10. Bar order: stop first, then partial, then target
  (stop-after-partial = breakeven stop). Caveat: partial50_trailBE
  collapsed Nifty winners when applied to mornings in sweep (o); here it
  is 50% only, with a structural stop and room filter, and is reported
  with partial vs full-target splits so any winner-tax is visible.
- No re-entry (new): one signal, one trade per stock/day; no second trade
  after a stop. Addresses (lA) re-entry losses.
- Convicted cap (new, fixes cap crowding): max 3 stock trades/week,
  max 1/stock/week, prospective full-target net >= Rs 500
  (2*risk*100 - 40 >= 500 => risk >= Rs 2.70/share). Ranking for cap is
  by prospective target net DESCENDING, then room_ratio, then setup_rank
  (NOT setup_rank first — setup_rank-first crowding dropped Rs 49,925 of
  Skill trades in the dual merge).
- Costs/size: 100 shares, Rs 40/trade, square-off 15:10, short paper-only.
  Win (primary) = net > 0. Full-target rate is also reported, because old
  V4 win rate = targets/trades and a partial-BE win is not a full target.
"""
import sys, os, json, math
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
STOCKS = [s for s in SYMBOLS if s not in ("NIFTY", "BANKNIFTY")]
QTY, COST = 100, 40.0

def nifty_day_map():
    spot, daily = load("NIFTY")
    out = {}
    for date, grp in spot.groupby("date"):
        g = grp.sort_values("timestamp")
        or_c = g[g["time"] < "09:30"]
        if or_c.empty:
            continue
        out[date.date().isoformat()] = {
            "orh": float(or_c["high"].max()), "orl": float(or_c["low"].min()),
            "candles": [(c["time"], float(c["close"])) for c in g.to_dict("records")],
        }
    return out

def replay(candles, start_idx, entry, stop, target, direction):
    """candles: list of dicts with time/high/low/close. Returns exit dict.
    Partial at 1R on 50 shares, remaining 50 trail to BE."""
    d = 1 if direction == "CE" else -1
    risk = abs(entry - stop)
    plevel = entry + d * risk
    partial = False
    for i in range(start_idx, len(candles)):
        c = candles[i]; t = c["time"]; hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        cur_stop = entry if partial else stop
        # stop first (conservative)
        if direction == "CE" and lo <= cur_stop:
            if partial:
                net = round(50 * risk - COST, 2)
                return {"exit_reason": "stop_after_partial_BE", "exit_price": cur_stop, "exit_time": t, "net_rs": net, "full_target": False}
            return {"exit_reason": "stop", "exit_price": stop, "exit_time": t, "net_rs": round(-risk * QTY - COST, 2), "full_target": False}
        if direction == "PE" and hi >= cur_stop:
            if partial:
                net = round(50 * risk - COST, 2)
                return {"exit_reason": "stop_after_partial_BE", "exit_price": cur_stop, "exit_time": t, "net_rs": net, "full_target": False}
            return {"exit_reason": "stop", "exit_price": stop, "exit_time": t, "net_rs": round(-risk * QTY - COST, 2), "full_target": False}
        # partial touch
        if not partial:
            if (direction == "CE" and hi >= plevel) or (direction == "PE" and lo <= plevel):
                partial = True
                # target same bar?
                if (direction == "CE" and hi >= target) or (direction == "PE" and lo <= target):
                    net = round(50 * risk + 50 * 2 * risk - COST, 2)
                    return {"exit_reason": "target_after_partial", "exit_price": target, "exit_time": t, "net_rs": net, "full_target": True}
                # else continue with BE trail
        else:
            if (direction == "CE" and hi >= target) or (direction == "PE" and lo <= target):
                net = round(50 * risk + 50 * 2 * risk - COST, 2)
                return {"exit_reason": "target_after_partial", "exit_price": target, "exit_time": t, "net_rs": net, "full_target": True}
        if t == "15:10":
            if partial:
                rem = d * (cl - entry) * 50
                return {"exit_reason": "square_off_after_partial", "exit_price": cl, "exit_time": t, "net_rs": round(50 * risk + rem - COST, 2), "full_target": False}
            return {"exit_reason": "square_off", "exit_price": cl, "exit_time": t, "net_rs": round(d * (cl - entry) * QTY - COST, 2), "full_target": False}
    c = candles[-1]
    if partial:
        rem = d * (float(c["close"]) - entry) * 50
        return {"exit_reason": "square_off_after_partial", "exit_price": float(c["close"]), "exit_time": c["time"], "net_rs": round(50 * risk + rem - COST, 2), "full_target": False}
    return {"exit_reason": "square_off", "exit_price": float(c["close"]), "exit_time": c["time"], "net_rs": round(d * (float(c["close"]) - entry) * QTY - COST, 2), "full_target": False}

def s1_candidates(year=2026, months=range(1, 11)):
    nmap = nifty_day_map()
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
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            or_c = day_spot[day_spot["time"] < "09:30"]
            if or_c.empty:
                continue
            orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
            orw = orh - orl
            or_pct = orw / pdc if pdc else 0
            if or_pct < 0.0025 or or_pct > 0.030:
                continue
            setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
            if setup is None or sig is None:
                continue
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
            entry_candle = candles[sig_idx + 2]
            entry = float(entry_candle["open"])
            entry_time = entry_candle["time"]
            # structural stop
            buf = 0.001 * pdc
            stop = (orl - buf) if direction == "CE" else (orh + buf)
            risk = abs(entry - stop)
            if risk <= 0:
                continue
            target = entry + (2 * risk if direction == "CE" else -2 * risk)
            # room: next PD level, finite and >= 2*risk
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
            if room < 2 * risk:
                continue
            room_ratio = room / risk
            # Nifty confirmation at confirmation time
            nm = nmap.get(d.date().isoformat())
            if nm is None:
                continue
            ncloses = [cl for (tt, cl) in nm["candles"] if tt <= conf["time"]]
            if not ncloses:
                continue
            nlast = ncloses[-1]
            if direction == "CE" and not (nlast > nm["orh"]):
                continue
            if direction == "PE" and not (nlast < nm["orl"]):
                continue
            tnet = round(2 * risk * QTY - COST, 2)
            if tnet < 500:
                continue
            # replay from entry candle
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
            out = replay(crecs, sig_idx + 2, entry, stop, target, direction)
            wk = d.isocalendar()[:2]; week = f"{wk[0]}-W{wk[1]:02d}"
            cands.append({
                "symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                "setup": setup, "direction": direction, "bias": bias,
                "signal_time": str(sig["timestamp"]), "confirm_time": str(conf["timestamp"]),
                "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
                "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room_ratio, 3),
                "target_net_rs": tnet, "orh": orh, "orl": orl, "or_pct": round(or_pct * 100, 3),
                "nifty_confirm_close": nlast, "nifty_orh": nm["orh"], "nifty_orl": nm["orl"],
                **out,
            })
    return cands

def cap_select(cands):
    """max 3 stock/week, max 1/stock/week. Rank: target_net desc, room_ratio, setup_rank."""
    rank_setup = {"setup4_reclaim": 3, "setup4_pullback": 3, "setup3_bounce_rejection": 2, "setup2_or_breakout": 1, "setup2_or_breakdown": 1}
    ranked = sorted(cands, key=lambda t: (-t["target_net_rs"], -t["room_ratio"], -rank_setup.get(t["setup"], 0), t["date"], t["symbol"]))
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
    return {"trades": len(trades), "wins_net_pos": wins, "win_rate_pct": round(wins / len(trades) * 100, 1),
            "full_targets": ft, "full_target_rate_pct": round(ft / len(trades) * 100, 1),
            "net_rs": net, "expectancy_rs": round(net / len(trades), 2)}

if __name__ == "__main__":
    uncapped = s1_candidates()
    capped = cap_select(uncapped)
    print(f"uncapped={len(uncapped)} capped={len(capped)}")
    print("capped total:", metrics(capped))
    print("uncapped total:", metrics(uncapped))
    import collections
    for m in range(1, 11):
        mt = [t for t in capped if t["month"] == m]
        print(f"month {m:02d}:", metrics(mt))
    with open(os.path.expanduser("~/workspace/trading/s1_trades_jan_oct_2026.csv"), "w", newline="") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(capped[0].keys()) if capped else []); w.writeheader(); w.writerows(capped)
    with open(os.path.expanduser("~/workspace/trading/s1_uncapped_jan_oct_2026.csv"), "w", newline="") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(uncapped[0].keys()) if uncapped else []); w.writeheader(); w.writerows(uncapped)
    print("wrote s1_trades_jan_oct_2026.csv / s1_uncapped_jan_oct_2026.csv")
