"""Clubbed Day Trader skill + 3-Blue-Line strategy, CASH intraday backtest.

Paper / historical replay only. No orders. No live data.

Signal logic is adapted from ~/workspace/trading/live_setup_identifier.py (v4),
with Bank Nifty point thresholds scaled by (prev_close / 55000) so the same
relative rules apply to a Rs 259 stock and a Rs 4,239 stock. This scaling is
PROVISIONAL and documented, not Chandu's rule.

Differences from the Bank Nifty options engine, all documented:
- No Red Bands/ledges are supplied for stocks, so Setup 1 is SKIPPED
  (as instructed). Other setups run on PD/OR only.
- No option premium. Entry is in the share price itself.
- PROVISIONAL cash exit (NOT Chandu's rule): entry at the next 5-min open
  after the signal close. Stop = signal candle low (long) / high (short).
  Risk = abs(entry - stop). Target = entry +/- 2 * risk.
  If risk is 0 (entry == stop level) the trade is skipped as invalid.
  Exit is checked bar by bar after entry; if a candle hits both stop and
  target, stop takes priority (conservative). Square-off at the 15:10
  candle close if neither stop nor target has hit (flat before 15:15).
- PROVISIONAL size: 100 shares per trade for every stock, solely to convert
  price points to rupees for comparison. NOT Chandu's size, NOT capital-based.
  Capital was not shared, so no risk % is computed.
- PROVISIONAL cost: Rs 40 flat per trade, assumed, NOT actual brokerage.
  Net = direction * (exit - entry) * 100 - 40.

Usage:
  python3 daytrader_cash_backtest.py --symbol ITC --spot5m spot_5m.csv \
      --daily spot_daily.csv --out trade_log_cash.csv
Input spot_5m: timestamp,open,high,low,close (IST, 5-min bars).
Input daily: date,open,high,low,close (one row per trading day, derived
from the same 5-min bars if needed; the first day in the file is the
prior day for the second day, so at least one prior day is required).
"""
import argparse
import math
import pandas as pd


def bias_of(prev):
    rng = prev["high"] - prev["low"]
    cs = (prev["close"] - prev["low"]) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    return bias, cs


def find_signal(day_spot, pdh, pdc, pdl, bias, scale):
    """Return (setup, direction, signal_candle) or None. Mirrors v4 identifier."""
    allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
    or_c = day_spot[day_spot["time"] < "09:30"]
    if or_c.empty:
        return None, None, None
    orh = float(or_c["high"].max())
    orl = float(or_c["low"].min())
    or_width = orh - orl
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    all_levels = sorted(set([pdh, pdc, pdl]))
    day_open = float(day_spot.iloc[0]["open"])
    reclaimed = None
    bounced = False
    for i, c in candles.iterrows():
        t = c["time"]
        if t > "14:30":
            break
        close, high, low, opn = float(c["close"]), float(c["high"]), float(c["low"]), float(c["open"])
        prev_close = float(candles.iloc[i - 1]["close"]) if i > 0 else opn
        # Setup 4 reclaim flag: gap-down day reclaiming above OR/PD levels.
        if day_open < pdc and day_open < pdl and reclaimed is None:
            if close > orh and close > pdc and close > pdl:
                reclaimed = close
        # Setup 4 pullback: after a reclaim, dip to PDC/PDL (within tolerance) and close up.
        if reclaimed is not None and "CE" in allowed:
            for lvl in (pdc, pdl):
                if abs(low - lvl) <= 40 * scale and close > lvl and close > opn:
                    nxt = [l for l in all_levels if l > close]
                    room = (min(nxt) - close) if nxt else math.inf
                    if room >= 200 * scale:
                        return "setup4_pullback", "CE", c
        # Setup 4 reclaim: direct reclaim close.
        if day_open < pdc and "CE" in allowed and close > orh and close > pdc and close < pdh:
            nxt = [l for l in all_levels if l > close]
            room = (min(nxt) - close) if nxt else math.inf
            if room >= 200 * scale:
                return "setup4_reclaim", "CE", c
        # Setup 2 OR breakout / breakdown, OR width cap scaled, up to 11:30.
        if or_width <= 360 * scale and t <= "11:30":
            if close > orh and close < pdh and "CE" in allowed:
                res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                if not res or close > min(res):
                    nxt = [l for l in all_levels if l > close]
                    room = (min(nxt) - close) if nxt else math.inf
                    if room >= 200 * scale:
                        return "setup2_or_breakout", "CE", c
            if close < orl and close < pdl and "PE" in allowed:
                nxt = [l for l in all_levels if l < close]
                room = (close - max(nxt)) if nxt else math.inf
                if room >= 200 * scale:
                    return "setup2_or_breakdown", "PE", c
        # Setup 3 bounce rejection: wide OR, bearish bias, bounce into ORH area then red close below ORH.
        if orh <= high <= orh + 100 * scale:
            bounced = True
        if or_width >= 400 * scale and bias == "bearish" and "PE" in allowed:
            if bounced and close < opn and close < orh:
                blocking = pdc if close > pdc else pdl
                room = close - blocking
                if room >= 200 * scale:
                    return "setup3_bounce_rejection", "PE", c
    return None, None, None


def run_day(day_spot, pdh, pdc, pdl, bias, scale, qty, cost):
    """Run one day. Returns a dict for the trade log (trade or no_trade)."""
    setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
    base = {"setup": setup or "no_trade", "direction": direction or "",
            "signal_time": sig["timestamp"] if sig is not None else "",
            "entry_price": "", "stop_price": "", "target_price": "",
            "exit_reason": "no_trade", "exit_price": "", "exit_time": "",
            "gross_per_share": 0.0, "net_rs": 0.0}
    if setup is None:
        return base
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    sig_idx = None
    for i, c in candles.iterrows():
        if c["timestamp"] == sig["timestamp"]:
            sig_idx = i
            break
    if sig_idx is None or sig_idx + 1 >= len(candles):
        return base
    entry_candle = candles.iloc[sig_idx + 1]
    entry = float(entry_candle["open"])
    if direction == "CE":  # long
        stop = float(sig["low"])
        risk = entry - stop
        if risk <= 0:
            base["setup"] = setup + "_invalid_risk0"
            return base
        target = entry + 2 * risk
    else:  # short (PE setup mapped to short in cash)
        stop = float(sig["high"])
        risk = stop - entry
        if risk <= 0:
            base["setup"] = setup + "_invalid_risk0"
            return base
        target = entry - 2 * risk
    base.update({"entry_price": entry, "stop_price": stop, "target_price": target})
    # Exit bar by bar from the entry candle onwards.
    for i in range(sig_idx + 1, len(candles)):
        c = candles.iloc[i]
        t, high, low, close = c["time"], float(c["high"]), float(c["low"]), float(c["close"])
        if direction == "CE":
            if low <= stop:
                base.update({"exit_reason": "stop", "exit_price": stop, "exit_time": c["timestamp"]})
                break
            if high >= target:
                base.update({"exit_reason": "target", "exit_price": target, "exit_time": c["timestamp"]})
                break
        else:
            if high >= stop:
                base.update({"exit_reason": "stop", "exit_price": stop, "exit_time": c["timestamp"]})
                break
            if low <= target:
                base.update({"exit_reason": "target", "exit_price": target, "exit_time": c["timestamp"]})
                break
        if t == "15:10":
            base.update({"exit_reason": "square_off", "exit_price": close, "exit_time": c["timestamp"]})
            break
    else:
        # No exit hit and no 15:10 candle seen: square off at last candle close.
        c = candles.iloc[-1]
        base.update({"exit_reason": "square_off", "exit_price": float(c["close"]), "exit_time": c["timestamp"]})
    if base["exit_reason"] in ("target", "stop", "square_off"):
        d = 1 if direction == "CE" else -1
        gross = d * (float(base["exit_price"]) - entry) * qty
        base["gross_per_share"] = d * (float(base["exit_price"]) - entry)
        base["net_rs"] = gross - cost
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--spot5m", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--qty", type=int, default=100)
    ap.add_argument("--cost", type=float, default=40.0)
    args = ap.parse_args()
    spot = pd.read_csv(args.spot5m, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    daily = pd.read_csv(args.daily, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    # Normalise both sides to tz-naive calendar dates (Upstox files carry +05:30).
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    rows = []
    for day, day_spot in spot.groupby("date"):
        ds = day.date().isoformat()
        prev = daily[daily["date"] < day]
        if prev.empty:
            continue
        y = prev.iloc[-1]
        pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
        bias, cs = bias_of(y)
        scale = pdc / 55000.0 if pdc else 1.0
        r = run_day(day_spot, pdh, pdc, pdl, bias, scale, args.qty, args.cost)
        or_c = day_spot[day_spot["time"] < "09:30"]
        rows.append({"symbol": args.symbol, "date": ds, "bias": bias, "closing_strength_pct": round(cs, 2),
                     "PDH": pdh, "PDC": pdc, "PDL": pdl,
                     "ORH": float(or_c["high"].max()) if not or_c.empty else "",
                     "ORL": float(or_c["low"].min()) if not or_c.empty else "",
                     **r})
    pd.DataFrame(rows).to_csv(args.out, index=False)
    trades = [r for r in rows if r["exit_reason"] in ("target", "stop", "square_off")]
    print(f"{args.symbol}: days={len(rows)} trades={len(trades)} "
          f"net={sum(r['net_rs'] for r in trades):.2f} -> {args.out}")


if __name__ == "__main__":
    main()
