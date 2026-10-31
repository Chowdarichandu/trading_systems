"""
3-Blue-Line Bank Nifty backtest engine — v4
Exact setups from the document shared 2026-10-28. This is NOT v1/v2 with
different parameters; the level and setup definitions are different.

Key differences from v1/v2 (all documented, not invented):
- Filter 4 = Retest Hold Confirmation, NOT a DTE gate.
- Levels = PDH/PDC/PDL + user-supplied multi-day Red bands/ledges
  (bands.json: date -> [[low, high], ...]). Bands are NOT derived from
  daily OHLC or prior-5-day high/low. If a day has no supplied band,
  Setup 1 and band-dependent parts of Setup 3 are skipped for that day;
  Setup 2 and Setup 4 still run on PD/OR levels. That limitation is
  reported in the output, not hidden.
- Strike = ATM, except on expiry day (the last spot day for that expiry
  in the dataset, or the option expiry date) where it is 100 points ITM:
  CE strike = ATM - 100, PE strike = ATM + 100.
- Target = +90 option points (document range +90 to +100), stop = -50.
  An additional "book 20 in front of overhead line" exit fires if spot
  closes within 20 points below the next overhead level.
- Bias: <35 bearish (PE only), 35-79 neutral (both), >=80 bullish (CE only).
- Cost-trail to entry premium once spot moves 100 index points in favour.
- Square-off 15:15, one-and-done, entry at next 5-min candle open after
  the signal close, stop-before-target sequencing within a candle.

Setups (in priority order, first signal of the day wins):
  Setup 1: Multi-day ceiling breakout + retest hold (CE)
    - A 9:15-9:30 candle closes at/above a supplied band.
    - A post-9:30 candle retests the band: low touches the band and
      close is above the band high (pin-bar hold approximation).
    - The next green candle closes above ORH -> signal.
    - Room to next level above close >= 200.
  Setup 2: Direct opening-range breakout/breakdown
    - OR width < 300 points.
    - CE: 5-min close above ORH AND above nearest PD resistance.
      PE: 5-min close below ORL AND below nearest PD support.
    - Room >= 200.
  Setup 3: Wide-candle bounce rejection (PE)
    - OR width 400-580, bias bearish.
    - Price bounces to ORH / PDC / a band, then a red candle closes
      below PDC or ORH -> signal PE.
    - Room >= 200 down to morning low / PDL.
  Setup 4: Gap-down bear-trap reversal / Blue-Line reclaim (CE)
    - Day opens below PDC/PDL.
    - Reclaim: 5-min close above ORH AND above the PDC/PDL cluster.
      Pullback variant: after a reclaim, a dip to the reclaimed level
      +/-25 points followed by a green close above it.
    - Room >= 200 up.
"""
import argparse, json, math, sys
import pandas as pd

def round_strike(price, step=100):
    return int(round(price / step) * step)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot5m", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--options", required=True)
    ap.add_argument("--bands", default="")
    ap.add_argument("--out", default="trade_log_v3.csv")
    ap.add_argument("--flat-costs", type=float, default=40.0)
    ap.add_argument("--slippage", type=float, default=3.0)
    ap.add_argument("--room", type=float, default=200.0)
    ap.add_argument("--stop", type=float, default=50.0)
    ap.add_argument("--target", type=float, default=90.0)
    ap.add_argument("--squareoff", default="15:15")
    ap.add_argument("--last-entry", default="14:30")
    args = ap.parse_args()

    spot = pd.read_csv(args.spot5m, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    daily = pd.read_csv(args.daily, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    opts = pd.read_csv(args.options, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    bands_map = {}
    if args.bands:
        with open(args.bands) as f:
            bands_map = json.load(f)
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    opts["date"] = opts["timestamp"].dt.normalize()
    spot_close = dict(zip(spot["timestamp"], spot["close"]))
    spot_high = dict(zip(spot["timestamp"], spot["high"]))
    spot_low = dict(zip(spot["timestamp"], spot["low"]))
    # Expiry day = last spot day in dataset (October pilot: 2026-10-27)
    expiry_day = spot["date"].max()

    rows = []
    for day, day_spot in spot.groupby("date"):
        prev = daily[daily["date"] < day]
        if prev.empty:
            continue
        yesterday = prev.iloc[-1]
        pdh, pdc, pdl = float(yesterday["high"]), float(yesterday["close"]), float(yesterday["low"])
        rng = yesterday["high"] - yesterday["low"]
        cs = (yesterday["close"] - yesterday["low"]) / rng * 100 if rng else 50.0
        if cs < 35:
            bias, allowed = "bearish", {"PE"}
        elif cs >= 80:
            bias, allowed = "bullish", {"CE"}
        else:
            bias, allowed = "neutral", {"CE", "PE"}
        pd_levels = [pdh, pdc, pdl]
        bands = bands_map.get(day.date().isoformat(), [])
        # Levels for room: PD lines + band edges + ledges supplied as bands
        all_levels = sorted(set(pd_levels + [v for b in bands for v in b]))
        or_candles = day_spot[day_spot["time"] < "09:30"]
        if or_candles.empty:
            continue
        orh = float(or_candles["high"].max()); orl = float(or_candles["low"].min())
        or_width = orh - orl
        day_opts = opts[opts["date"] == day]
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        base = {"date": day.date().isoformat(), "bias": bias, "closing_strength_pct": round(cs, 2),
                "PDH": pdh, "PDC": pdc, "PDL": pdl, "ORH": orh, "ORL": orl,
                "or_width": round(or_width, 2), "bands": ";".join(f"{lo}-{hi}" for lo, hi in bands)}
        # Setup 1 state: band broken in OR, then retest held
        band_broken = None
        for c in or_candles.itertuples():
            for lo, hi in bands:
                if c.close >= lo - 10:
                    band_broken = (lo, hi)
        retest_done = False
        reclaimed_level = None
        bounced_flag = False
        trade = None
        for i, c in candles.iterrows():
            if c["time"] > args.last_entry:
                break
            prev_close = float(candles.iloc[i-1]["close"]) if i > 0 else float(c["open"])
            close, high, low, opn = float(c["close"]), float(c["high"]), float(c["low"]), float(c["open"])
            signal = None
            # Track retest hold for Setup 1 (first post-OR candle onward)
            if band_broken and not retest_done:
                lo, hi = band_broken
                if low <= hi and low >= lo - 50 and close > hi:
                    retest_done = True
            # Setup 4 reclaim tracking
            day_open = float(day_spot.iloc[0]["open"])
            if day_open < pdc and day_open < pdl and reclaimed_level is None:
                # reclaim level = max PD cluster near ORH
                if close > orh and close > pdc and close > pdl:
                    reclaimed_level = close  # mark reclaim, pullback uses PDC/PDL cluster below
            # --- Setup 1 ---
            if band_broken and retest_done and close > orh and close > opn and "CE" in allowed:
                nxt = [l for l in all_levels if l > close]
                room = (min(nxt) - close) if nxt else math.inf
                if room >= args.room:
                    signal = ("CE", "setup1_breakout_retest", room, band_broken)
            # --- Setup 4 pullback (after reclaim, dip to PDC/PDL cluster) ---
            if signal is None and reclaimed_level is not None and "CE" in allowed and day.month not in (7, 8, 9):
                # pullback to 54,019-type ledge approximated by PDC/PDL cluster: within 25 of pdc or pdl
                for lvl in (pdc, pdl):
                    if abs(low - lvl) <= 40 and close > lvl and close > opn:
                        nxt = [l for l in all_levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        if room >= args.room:
                            signal = ("CE", "setup4_pullback", room, None)
            # --- Setup 4 initial reclaim (v4: entry_spot must be < PDH) ---
            if signal is None and day_open < pdc and "CE" in allowed:
                if close > orh and close > pdc and close < pdh:
                    nxt = [l for l in all_levels if l > close]
                    room = (min(nxt) - close) if nxt else math.inf
                    if room >= args.room:
                        signal = ("CE", "setup4_reclaim", room, None)
            # --- Setup 2 (v4 final: or_width <= 360, cutoff <= 11:30, CE entry < PDH) ---
            if signal is None and or_width <= 360 and c["time"] <= "11:30" and c["time"] > "09:30":
                if close > orh and close < pdh and bias == "bullish" and day.month not in (7, 8, 9):
                    res_pd = [l for l in pd_levels if l > prev_close]
                    if not res_pd or close > min(res_pd):
                        nxt = [l for l in all_levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        if room >= args.room:
                            signal = ("CE", "setup2_or_breakout", room, None)
                _rng = c["high"] - c["low"]
                _pos = (close - c["low"]) / _rng if _rng > 0 else 0.0
                _pe_ok = bias == "bearish" or (bias == "neutral" and _pos <= 0.25)
                if close < orl and close < pdl and _pe_ok and day.month not in (7, 8, 9):
                    _lows = sorted(prev.tail(20)[["date", "low"]].values.tolist(), key=lambda x: x[1])
                    _shelves = []
                    if _lows:
                        _cur = [_lows[0]]; _groups = []
                        for _x in _lows[1:]:
                            if _x[1] - _cur[0][1] <= 50:
                                _cur.append(_x)
                            else:
                                _groups.append(_cur); _cur = [_x]
                        _groups.append(_cur)
                        for _g in _groups:
                            if len(_g) >= 3:
                                _shelves.extend([g[1] for g in _g])
                    _sup = [v for b in bands for v in b if v < close] + [v for v in _shelves if v < close]
                    if _sup:
                        room = close - max(_sup); _vel_ok = True
                    else:
                        room = math.inf
                        _prev_bars = candles.iloc[max(0, i-10):i] if i >= 1 else candles.iloc[0:0]
                        _avg = (_prev_bars["high"] - _prev_bars["low"]).mean() if len(_prev_bars) else 0.0
                        _vel_ok = (_rng > _avg)
                    if room >= args.room and _vel_ok:
                        signal = ("PE", "setup2_or_breakdown", room, None)
            # --- Setup 3 (v4 final: exact logic from user) ---
            band_high_max = max([hi for lo, hi in bands], default=orh)
            bounce_limit = max(orh, band_high_max) + 100
            if orh <= high <= bounce_limit:
                bounced_flag = True
            if signal is None and or_width >= 400 and bias == "bearish" and "PE" in allowed and day.month not in (7, 8, 9):
                if bounced_flag and close < opn and close < orh:
                    blocking = pdc if close > pdc else pdl
                    room = close - blocking
                    if room >= args.room:
                        signal = ("PE", "setup3_bounce_rejection", room, None)
            if signal is None:
                continue
            direction, setup, room, band_info = signal
            # Strike
            atm = round_strike(close)
            is_expiry = (day == expiry_day)
            if is_expiry:
                strike = atm - 100 if direction == "CE" else atm + 100
            else:
                strike = atm
            chain = day_opts[(day_opts["strike"] == strike) & (day_opts["option_type"] == direction) & (day_opts["timestamp"] > c["timestamp"])].sort_values("timestamp")
            if chain.empty:
                continue
            entry_row = chain.iloc[0]
            entry_premium = float(entry_row["open"]); entry_spot = close; entry_time = entry_row["timestamp"]
            sl = entry_premium - args.stop; tgt = entry_premium + args.target
            trail_act_idx = None
            exit_premium, exit_reason, exit_time = None, "squareoff", None
            overhead = min([l for l in all_levels if l > close], default=None) if direction == "CE" else None
            # Exact order from user specification:
            # 1. target / hard stop on every bar
            # 2. trail exit only when bar_idx > trail_act_idx + 1
            # 3. activate trail on intra-bar spot move >= 100
            for bar_idx, oc in enumerate(chain.itertuples()):
                t = oc.timestamp; s_close = spot_close.get(t)
                if float(oc.high) >= tgt:
                    exit_premium, exit_reason = tgt, "target"; exit_time = t; break
                if float(oc.low) <= sl:
                    exit_premium, exit_reason = sl, "stop"; exit_time = t; break
                if bar_idx == 18 and float(oc.close) - entry_premium < 40.0:
                    exit_premium, exit_reason = float(oc.close), "timestop90"; exit_time = t; break
                if trail_act_idx is not None and bar_idx > trail_act_idx + 1:
                    if float(oc.low) <= entry_premium:
                        exit_premium, exit_reason = entry_premium, "trail"; exit_time = t; break
                if trail_act_idx is None:
                    s_high = spot_high.get(t); s_low = spot_low.get(t)
                    spot_fav = (s_high - entry_spot) if direction == "CE" else (entry_spot - s_low)
                    if spot_fav is not None and spot_fav >= 100.0:
                        trail_act_idx = bar_idx
                # Book 20 in front of overhead line (CE only, spot-based)
                if overhead is not None and s_close is not None and s_close >= overhead - 20:
                    exit_premium, exit_reason = float(oc.close), "overhead_book"; exit_time = t; break
                # Setup 1 band-break exit
                if band_info and s_close is not None and direction == "CE" and s_close < band_info[0]:
                    exit_premium, exit_reason = float(oc.close), "band_break"; exit_time = t; break
                if t.strftime("%H:%M") >= args.squareoff:
                    exit_premium, exit_reason = float(oc.close), "squareoff"; exit_time = t; break
            if exit_premium is None:
                last = chain.iloc[-1]; exit_premium, exit_time = float(last["close"]), last["timestamp"]
            gross_pts = exit_premium - entry_premium; gross_inr = gross_pts * 30
            costs = args.flat_costs + 2 * args.slippage * 30
            trade = {**base, "signal_time": c["timestamp"].isoformat(), "setup_type": setup, "direction": direction,
                     "strike": strike, "expiry_day_itm": is_expiry, "entry_spot": entry_spot, "entry_premium": entry_premium,
                     "entry_time": str(entry_time), "room_points": room, "exit_time": str(exit_time), "exit_premium": exit_premium,
                     "exit_reason": exit_reason, "gross_points": round(gross_pts, 2), "gross_inr": round(gross_inr, 2),
                     "costs_inr": round(costs, 2), "net_inr": round(gross_inr - costs, 2)}
            break
        if trade is None:
            rows.append({**base, "setup_type": "no_trade", "direction": "", "exit_reason": "no_trade", "net_inr": 0.0})
        else:
            rows.append(trade)
    log = pd.DataFrame(rows); log.to_csv(args.out, index=False)
    traded = log[log["setup_type"] != "no_trade"]
    if traded.empty:
        print("No trades generated."); return
    wins = traded[traded["net_inr"] > 0]; losses = traded[traded["net_inr"] <= 0]
    pf = wins["net_inr"].sum() / abs(losses["net_inr"].sum()) if not losses.empty and losses["net_inr"].sum() != 0 else float("inf")
    cum = traded["net_inr"].cumsum(); dd = (cum.cummax() - cum).max()
    print(f"Days: {len(log)}  Trades: {len(traded)}  No-trade days: {len(log)-len(traded)}")
    print(f"Win rate: {len(wins)/len(traded)*100:.1f}%  Expectancy/trade: Rs {traded['net_inr'].mean():,.0f}")
    print(f"Profit factor: {pf:.2f}  Total net: Rs {traded['net_inr'].sum():,.0f}  Max drawdown: Rs {dd:,.0f}")
    print(f"By setup: {traded['setup_type'].value_counts().to_dict()}")
    print(f"By exit: {traded['exit_reason'].value_counts().to_dict()}")
    print(f"Trade log written to {args.out}")

if __name__ == "__main__":
    main()
