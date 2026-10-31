"""Tuning grid for the clubbed Day Trader + v4 CASH engine, Bank Nifty spot.

NOT a live system, NOT options. Cash price engine only, 100 shares provisional,
Rs 40/trade assumed cost. This script exists because the 25 stocks could not
be fetched (Upstox 401 on 2026-10-29); Bank Nifty Jan-Oct spot data is held
locally, so the tuning surface is measured on Bank Nifty cash and must be
re-validated on stocks once their data is available. Do NOT carry a tuned
Bank Nifty cash result to stocks as proof.

PRE-STATED DESIGN (before results are read):
- Tune period: trade dates 2026-01-01 to 2026-06-30.
- Validate period: trade dates 2026-07-01 to 2026-10-27 (different period).
- October alone is NEVER a tuning period.
- Candidate selection rule: highest Jan-Jun net among the 27 grid combos,
  provided trades >= 15. No other combo is promoted to candidate.
- Target X is NOT defined by Chandu. This script reports the surface
  (net / win rate / trades-per-week / drawdown vs each variable) and
  leaves X open; it does not invent a target return.

Variables:
- target_ratio: target distance = ratio * stop distance.
- stop_scale: stop distance = scale * signal-candle distance
  (entry - signal low for longs, signal high - entry for shorts).
- room_pct: minimum room to the next PD level, as a fraction of price.
  Baseline 0.0036 (= 200 points on ~55,000, the v4 room rule, scaled).
- bias_on: v4 bias gating (bearish <35% PE/short only, bullish >=80% CE/long only).
- signal_end: 'baseline' (Setup 2 <= 11:30, others <= 14:30), '1130', '1430'.
- entry_mode: 'v4' (Setups 2/3/4, Setup 1 skipped, no bands) or
  'skill_or' (Day Trader skill's own entry: first 5-min close beyond ORH/ORL
  after 09:30 up to 11:30, no bias, no room, no PD cross check).
  Flags / oversold-bounce entries are NOT tested: the skill doc gives them
  no fixed definition to implement without inventing one.
"""
import glob, math, os
import pandas as pd

QTY, COST = 100, 40.0


def load_data():
    spot_frames, daily_frames = [], []
    base = os.path.expanduser("~/workspace/trading/data")
    spot_files = sorted(glob.glob(base + "/banknifty-2026-*/spot_5m.csv"))
    daily_files = sorted(glob.glob(base + "/banknifty-2026-*/spot_daily.csv"))
    for f in spot_files:
        if "jul-oct" in f or "jan-oct" in f:
            continue
        spot_frames.append(pd.read_csv(f, parse_dates=["timestamp"]))
    for f in daily_files:
        if "jul-oct" in f or "jan-oct" in f:
            continue
        daily_frames.append(pd.read_csv(f, parse_dates=["date"]))
    spot = pd.concat(spot_frames).drop_duplicates("timestamp").sort_values("timestamp")
    daily = pd.concat(daily_frames).drop_duplicates("date").sort_values("date")
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    days = {}
    daily_list = daily.to_dict("records")
    for i, y in enumerate(daily_list):
        d = y["date"]
        day_spot = spot[spot["date"] == d]
        if day_spot.empty or i == 0:
            continue
        prev = daily_list[i - 1]
        # Only count a day if its previous daily row is the previous trading day in the file
        # (all files here are trading-day sequences, so this is the v4 prior-day rule).
        days[d.date().isoformat()] = (prev, day_spot.to_dict("records"))
    return days


def bias_of(prev):
    rng = prev["high"] - prev["low"]
    cs = (prev["close"] - prev["low"]) / rng * 100 if rng else 50.0
    return ("bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"), cs


def find_signal(candles, orh, orl, or_width, day_open, pdh, pdc, pdl, bias, p):
    allowed = {"PE"} if (p["bias_on"] and bias == "bearish") else \
              {"CE"} if (p["bias_on"] and bias == "bullish") else {"CE", "PE"}
    scale = pdc / 55000.0
    room_thr = lambda close: p["room_pct"] * close
    if p["entry_mode"] == "skill_or":
        for c in candles:
            if c["time"] > "11:30":
                break
            if c["close"] > orh:
                return "skill_or_breakout", "CE", c
            if c["close"] < orl:
                return "skill_or_breakdown", "PE", c
        return None, None, None
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
        if reclaimed is not None and "CE" in allowed and t <= end_other:
            for lvl in (pdc, pdl):
                if abs(low - lvl) <= 40 * scale and close > lvl and close > opn:
                    nxt = [l for l in levels if l > close]
                    if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                        return "setup4_pullback", "CE", c
        if day_open < pdc and "CE" in allowed and t <= end_other and close > orh and close > pdc and close < pdh:
            nxt = [l for l in levels if l > close]
            if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                return "setup4_reclaim", "CE", c
        if or_width <= 360 * scale and t <= end2:
            if close > orh and close < pdh and "CE" in allowed:
                res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                if not res or close > min(res):
                    nxt = [l for l in levels if l > close]
                    if ((min(nxt) - close) if nxt else math.inf) >= room_thr(close):
                        return "setup2_or_breakout", "CE", c
            if close < orl and close < pdl and "PE" in allowed:
                nxt = [l for l in levels if l < close]
                if ((close - max(nxt)) if nxt else math.inf) >= room_thr(close):
                    return "setup2_or_breakdown", "PE", c
        if t <= end_other:
            if orh <= high <= orh + 100 * scale:
                bounced = True
            if or_width >= 400 * scale and bias == "bearish" and "PE" in allowed:
                if bounced and close < opn and close < orh:
                    blocking = pdc if close > pdc else pdl
                    if close - blocking >= room_thr(close):
                        return "setup3_bounce_rejection", "PE", c
    return None, None, None


def run(days, p, date_lo, date_hi):
    trades = []
    ndays = 0
    for ds in sorted(days):
        if not (date_lo <= ds <= date_hi):
            continue
        prev, raw = days[ds]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev)
        candles = [c for c in raw if c["time"] >= "09:30"]
        or_c = [c for c in raw if c["time"] < "09:30"]
        if not or_c or not candles:
            continue
        ndays += 1
        orh = max(c["high"] for c in or_c)
        orl = min(c["low"] for c in or_c)
        or_width = orh - orl
        day_open = raw[0]["open"]
        setup, direction, sig = find_signal(candles, orh, orl, or_width, day_open, pdh, pdc, pdl, bias, p)
        if setup is None:
            continue
        sig_idx = next(i for i, c in enumerate(candles) if c["timestamp"] == sig["timestamp"])
        if sig_idx + 1 >= len(candles):
            continue
        entry = float(candles[sig_idx + 1]["open"])
        if direction == "CE":
            base_stop = entry - float(sig["low"])
            stop = entry - p["stop_scale"] * base_stop
            target = entry + p["target_ratio"] * (entry - stop)
        else:
            base_stop = float(sig["high"]) - entry
            stop = entry + p["stop_scale"] * base_stop
            target = entry - p["target_ratio"] * (stop - entry)
        if (entry - stop) == 0:
            continue
        exit_reason, exit_price, exit_time = None, None, None
        for c in candles[sig_idx + 1:]:
            high, low, close, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
            if direction == "CE":
                if low <= stop:
                    exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
                if high >= target:
                    exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
            else:
                if high >= stop:
                    exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
                if low <= target:
                    exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
            if t == "15:10":
                exit_reason, exit_price, exit_time = "square_off", close, c["timestamp"]; break
        if exit_reason is None:
            c = candles[-1]
            exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["timestamp"]
        d = 1 if direction == "CE" else -1
        net = d * (exit_price - entry) * QTY - COST
        trades.append({"date": ds, "setup": setup, "direction": direction, "bias": bias,
                       "entry": entry, "stop": stop, "target": target,
                       "exit_reason": exit_reason, "exit_price": exit_price, "net_rs": net})
    return ndays, trades


def metrics(ndays, trades):
    if not trades:
        return {"days": ndays, "trades": 0, "targets": 0, "stops": 0, "square_offs": 0,
                "win_rate_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0,
                "max_drawdown_rs": 0.0, "trades_per_week": 0.0}
    net = sum(t["net_rs"] for t in trades)
    cum, peak, dd = 0.0, 0.0, 0.0
    for t in trades:
        cum += t["net_rs"]
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    return {"days": ndays, "trades": len(trades),
            "targets": sum(1 for t in trades if t["exit_reason"] == "target"),
            "stops": sum(1 for t in trades if t["exit_reason"] == "stop"),
            "square_offs": sum(1 for t in trades if t["exit_reason"] == "square_off"),
            "win_rate_pct": round(100 * sum(1 for t in trades if t["exit_reason"] == "target") / len(trades), 1),
            "net_rs": round(net, 2), "expectancy_rs": round(net / len(trades), 2),
            "max_drawdown_rs": round(dd, 2),
            "trades_per_week": round(len(trades) / (ndays / 5) if ndays else 0, 2)}


BASE = {"entry_mode": "v4", "room_pct": 0.0036, "bias_on": True, "signal_end": "baseline",
        "target_ratio": 2.0, "stop_scale": 1.0}


def main():
    days = load_data()
    print(f"Loaded {len(days)} trading days: {min(days)} to {max(days)}")
    outdir = os.path.expanduser("~/workspace/trading")
    periods = {"Jan-Jun (tune)": ("2026-01-01", "2026-06-30"),
               "Jul-Oct (validate)": ("2026-07-01", "2026-10-27"),
               "Jan-Oct": ("2026-01-01", "2026-10-27"),
               "Oct only (context, never tune)": ("2026-10-01", "2026-10-27")}
    summary = []
    def record(label, p, lo, hi, trades_out=None):
        ndays, trades = run(days, p, lo, hi)
        m = metrics(ndays, trades)
        summary.append({"variant": label, "period": lo + " to " + hi, **p, **m})
        if trades_out:
            pd.DataFrame(trades).to_csv(trades_out, index=False)
        print(f"{label} | {lo}..{hi} | days={ndays} trades={m['trades']} "
              f"T={m['targets']} S={m['stops']} SQ={m['square_offs']} win={m['win_rate_pct']}% "
              f"net={m['net_rs']} exp={m['expectancy_rs']} DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
        return trades
    # Baseline and skill-own entry, all periods.
    for label, p in [("baseline v4 cash", BASE),
                     ("skill_or entry", {**BASE, "entry_mode": "skill_or"})]:
        for plabel, (lo, hi) in periods.items():
            record(f"{label} [{plabel}]", p, lo, hi)
    # Grid on tune period only.
    grid = []
    for ratio in (1.0, 2.0, 3.0):
        for ss in (0.5, 1.0, 1.5):
            for room in (0.0, 0.0036, 0.0072):
                p = {**BASE, "target_ratio": ratio, "stop_scale": ss, "room_pct": room}
                ndays, trades = run(days, p, "2026-01-01", "2026-06-30")
                m = metrics(ndays, trades)
                grid.append({**p, **m})
                print(f"GRID ratio={ratio} stop_scale={ss} room={room} | trades={m['trades']} "
                      f"net={m['net_rs']} win={m['win_rate_pct']}% DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
    pd.DataFrame(grid).to_csv(f"{outdir}/daytrader_cash_tuning_grid_janjun.csv", index=False)
    cand = max((g for g in grid if g["trades"] >= 15), key=lambda g: g["net_rs"])
    print(f"CANDIDATE (pre-stated rule, Jan-Jun net, trades>=15): {cand}", flush=True)
    cp = {**BASE, "target_ratio": cand["target_ratio"], "stop_scale": cand["stop_scale"], "room_pct": cand["room_pct"]}
    for plabel, (lo, hi) in periods.items():
        record(f"tuned candidate [{plabel}]", cp, lo, hi)
    # One-at-a-time sensitivity on tune period.
    sens = []
    for label, p in [("bias off", {**BASE, "bias_on": False}),
                     ("signal end 11:30 all", {**BASE, "signal_end": "1130"}),
                     ("signal end 14:30 all", {**BASE, "signal_end": "1430"})]:
        ndays, trades = run(days, p, "2026-01-01", "2026-06-30")
        m = metrics(ndays, trades)
        sens.append({"variant": label, **p, **m})
        print(f"SENS {label}: trades={m['trades']} net={m['net_rs']} win={m['win_rate_pct']}% "
              f"DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
    pd.DataFrame(sens).to_csv(f"{outdir}/daytrader_cash_tuning_sensitivity.csv", index=False)
    pd.DataFrame(summary).to_csv(f"{outdir}/daytrader_cash_tuning_summary.csv", index=False)
    with open(f"{outdir}/daytrader_cash_tuning_candidate.txt", "w") as f:
        f.write(f"{cand}\nparams={cp}\n")


if __name__ == "__main__":
    main()
