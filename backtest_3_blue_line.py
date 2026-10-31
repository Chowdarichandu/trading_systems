"""
3-Blue-Line Bank Nifty backtest engine — v2
Implements the spec in 3-blue-line-bank-nifty-backtest-spec.md.

v2 fix (2026-10-28): breakout/breakdown trigger uses only the 3 Blue Lines
(PDH/PDC/PDL) for the level-crossing test, not the far prior-5-day high/low.
In v1, a day that opened already above PDH could never trigger a breakout,
because the "next resistance" became the prior-5-day high (e.g. 55,883.70 on
2026-10-27). In v2, if price is already above all PD levels, a close above
the opening range high is itself the breakout; likewise below all PD levels
for a breakdown. Prior-5-day levels are still used for the clear-room
measurement. Levels already broken by an opening gap are seeded into the
broken sets, so a retest of a gapped-over PD level can trigger.

Inputs (CSV, IST timestamps):
  spot_5m.csv:    timestamp, open, high, low, close
  spot_daily.csv: date, open, high, low, close
  option_5m.csv:  timestamp, strike, option_type, expiry, open, high, low, close
                  option_type is CE or PE. One row per strike per 5-min candle.

Outputs:
  trade_log.csv with one row per trading day (including no-trade days)
  Summary printed to stdout.

This is a research tool, not a trading recommendation. It must be fed
REAL historical option premiums. Do not substitute spot prices with a
fixed delta — that will produce a misleading result.

Usage:
  python3 backtest_3_blue_line.py --spot5m spot_5m.csv --daily spot_daily.csv \
      --options option_5m.csv --out trade_log.csv \
      --flat-costs 40 --slippage 3
"""

import argparse
import math
import sys

import pandas as pd


def round_strike(price, step=100):
    return int(round(price / step) * step)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot5m", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--options", required=True)
    ap.add_argument("--out", default="trade_log.csv")
    ap.add_argument("--flat-costs", type=float, default=40.0,
                    help="Flat charges per round trip in INR (brokerage+taxes). Replace with broker actuals.")
    ap.add_argument("--slippage", type=float, default=3.0,
                    help="Slippage in option points per leg.")
    ap.add_argument("--room", type=float, default=200.0)
    ap.add_argument("--stop", type=float, default=50.0)
    ap.add_argument("--target", type=float, default=100.0)
    ap.add_argument("--last-entry", default="14:30")
    ap.add_argument("--squareoff", default="15:15")
    ap.add_argument("--no-trail", action="store_true", help="Disable the cost-trail rule.")
    ap.add_argument("--min-dte", type=int, default=0,
                    help="Only trade when at least this many trading days remain in the dataset after today (DTE gate). 0 = off.")
    ap.add_argument("--no-bounce", action="store_true", help="Exclude bounce setups.")
    ap.add_argument("--no-bias", action="store_true", help="Ignore the closing-strength bias filter.")
    args = ap.parse_args()

    spot = pd.read_csv(args.spot5m, parse_dates=["timestamp"])
    daily = pd.read_csv(args.daily, parse_dates=["date"])
    opts = pd.read_csv(args.options, parse_dates=["timestamp"])

    spot = spot.sort_values("timestamp").reset_index(drop=True)
    daily = daily.sort_values("date").reset_index(drop=True)
    opts = opts.sort_values("timestamp").reset_index(drop=True)

    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    opts["date"] = opts["timestamp"].dt.normalize()

    # Spot close lookup by timestamp, for the cost-trail trigger.
    spot_close = dict(zip(spot["timestamp"], spot["close"]))
    spot_dates = sorted(spot["date"].unique())

    rows = []

    for day, day_spot in spot.groupby("date"):
        prev = daily[daily["date"] < day]
        if prev.empty:
            continue
        yesterday = prev.iloc[-1]
        pdh, pdc, pdl = float(yesterday["high"]), float(yesterday["close"]), float(yesterday["low"])
        prior5 = prev.tail(5)
        p5_high = float(prior5["high"].max())
        p5_low = float(prior5["low"].min())

        # Closing strength and bias (spec section 4.3).
        rng = yesterday["high"] - yesterday["low"]
        cs = (yesterday["close"] - yesterday["low"]) / rng * 100 if rng else 50.0
        if cs < 35:
            bias, allowed = "bearish", {"PE"}
        elif cs > 80:
            bias, allowed = "bullish", {"CE"}
        else:
            bias, allowed = "neutral", {"CE", "PE"}
        if args.no_bias:
            allowed = {"CE", "PE"}

        levels = sorted({pdh, pdc, pdl, p5_high, p5_low})

        # Opening range: 9:15-9:30 candles.
        or_candles = day_spot[day_spot["time"] < "09:30"]
        if or_candles.empty:
            continue
        orh = float(or_candles["high"].max())
        orl = float(or_candles["low"].min())

        day_opts = opts[opts["date"] == day]
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)

        base = {
            "date": day.date().isoformat(), "bias": bias,
            "closing_strength_pct": round(cs, 2), "PDH": pdh, "PDC": pdc, "PDL": pdl,
            "prior_5d_high": p5_high, "prior_5d_low": p5_low,
            "ORH": orh, "ORL": orl,
        }

        # DTE gate: trading days remaining in this dataset after today.
        if args.min_dte > 0:
            remaining = sum(1 for d in spot_dates if d > day)
            if remaining < args.min_dte:
                rows.append({**base, "setup_type": "no_trade", "direction": "",
                             "exit_reason": "no_trade_dte_gate", "net_inr": 0.0})
                continue

        pd_levels = [pdh, pdc, pdl]
        # Seed levels already broken by an opening gap (e.g. open above PDH).
        day_open = float(day_spot.iloc[0]["open"]) if not day_spot.empty else None
        broken_res = {lvl for lvl in levels if day_open is not None and day_open > lvl}
        broken_sup = {lvl for lvl in levels if day_open is not None and day_open < lvl}
        trade = None

        for i, c in candles.iterrows():
            if c["time"] > args.last_entry:
                break
            prev_close = float(candles.iloc[i - 1]["close"]) if i > 0 else float(c["open"])
            close, high, low = float(c["close"]), float(c["high"]), float(c["low"])

            # Track broken levels for retest entries.
            for lvl in levels:
                if prev_close <= lvl < close:
                    broken_res.add(lvl)
                if prev_close >= lvl > close:
                    broken_sup.add(lvl)

            signal = None  # (direction, setup, room)

            # --- Breakout CE (v2: PD levels only for the crossing test) ---
            res_pd_above_prev = [l for l in pd_levels if l > prev_close]
            if close > orh and (not res_pd_above_prev or close > min(res_pd_above_prev)) and "CE" in allowed:
                nxt = [l for l in levels if l > close]
                room = (min(nxt) - close) if nxt else math.inf
                if room >= args.room:
                    signal = ("CE", "breakout", room)
            # --- Breakdown PE (v2: PD levels only for the crossing test) ---
            if signal is None:
                sup_pd_below_prev = [l for l in pd_levels if l < prev_close]
                if close < orl and (not sup_pd_below_prev or close < max(sup_pd_below_prev)) and "PE" in allowed:
                    nxt = [l for l in levels if l < close]
                    room = (close - max(nxt)) if nxt else math.inf
                    if room >= args.room:
                        signal = ("PE", "breakdown", room)
            # --- Retest ---
            if signal is None:
                for lvl in broken_res:
                    if abs(close - lvl) <= 25 and close > lvl and "CE" in allowed:
                        nxt = [l for l in levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        if room >= args.room:
                            signal = ("CE", "retest", room)
                for lvl in broken_sup:
                    if abs(close - lvl) <= 25 and close < lvl and "PE" in allowed:
                        nxt = [l for l in levels if l < close]
                        room = (close - max(nxt)) if nxt else math.inf
                        if room >= args.room:
                            signal = ("PE", "retest", room)
            # --- Bounce ---
            if signal is None and not args.no_bounce:
                body = abs(close - float(c["open"]))
                for lvl in levels:
                    if low < lvl <= high and close < lvl and close < float(c["open"]) and "PE" in allowed:
                        wick = high - max(float(c["open"]), close)
                        if body > 0 and wick >= 1.5 * body:
                            nxt = [l for l in levels if l < close]
                            room = (close - max(nxt)) if nxt else math.inf
                            if room >= args.room:
                                signal = ("PE", "bounce", room)
                    if low <= lvl < high and close > lvl and close > float(c["open"]) and "CE" in allowed:
                        wick = min(float(c["open"]), close) - low
                        if body > 0 and wick >= 1.5 * body:
                            nxt = [l for l in levels if l > close]
                            room = (min(nxt) - close) if nxt else math.inf
                            if room >= args.room:
                                signal = ("CE", "bounce", room)

            if signal is None:
                continue

            direction, setup, room = signal
            strike = round_strike(close)
            chain = day_opts[
                (day_opts["strike"] == strike)
                & (day_opts["option_type"] == direction)
                & (day_opts["timestamp"] > c["timestamp"])
            ].sort_values("timestamp")
            if chain.empty:
                continue  # No option data for this signal: skip, do not invent a price.

            entry_row = chain.iloc[0]
            entry_premium = float(entry_row["open"])
            entry_spot = close
            entry_time = entry_row["timestamp"]
            sl = entry_premium - args.stop
            tgt = entry_premium + args.target
            trail_sl = entry_premium
            trail_on = False
            exit_premium, exit_reason, exit_time = None, "squareoff", None

            for _, oc in chain.iterrows():
                t = oc["timestamp"]
                s_close = spot_close.get(t)
                if s_close is not None and not args.no_trail:
                    if direction == "CE" and s_close - entry_spot >= 100:
                        trail_on = True
                    if direction == "PE" and entry_spot - s_close >= 100:
                        trail_on = True
                eff_sl = trail_sl if trail_on else sl
                # Conservative sequencing: stop before target in the same candle.
                if float(oc["low"]) <= eff_sl:
                    exit_premium, exit_reason = eff_sl, ("trail" if trail_on else "stop")
                    exit_time = t
                    break
                if float(oc["high"]) >= tgt:
                    exit_premium, exit_reason = tgt, "target"
                    exit_time = t
                    break
                if oc["timestamp"].strftime("%H:%M") >= args.squareoff:
                    exit_premium, exit_reason = float(oc["close"]), "squareoff"
                    exit_time = t
                    break
            if exit_premium is None:
                last = chain.iloc[-1]
                exit_premium, exit_time = float(last["close"]), last["timestamp"]

            gross_pts = exit_premium - entry_premium
            gross_inr = gross_pts * 30
            costs = args.flat_costs + 2 * args.slippage * 30
            trade = {
                **base, "signal_time": c["timestamp"].isoformat(),
                "setup_type": setup, "direction": direction, "strike": strike,
                "entry_spot": entry_spot, "entry_premium": entry_premium,
                "entry_time": str(entry_time), "room_points": room,
                "exit_time": str(exit_time), "exit_premium": exit_premium,
                "exit_reason": exit_reason, "gross_points": round(gross_pts, 2),
                "gross_inr": round(gross_inr, 2), "costs_inr": round(costs, 2),
                "net_inr": round(gross_inr - costs, 2),
            }
            break  # One-and-done.

        if trade is None:
            rows.append({**base, "setup_type": "no_trade", "direction": "",
                         "exit_reason": "no_trade", "net_inr": 0.0})
        else:
            rows.append(trade)

    log = pd.DataFrame(rows)
    log.to_csv(args.out, index=False)

    traded = log[log["setup_type"] != "no_trade"]
    if traded.empty:
        print("No trades generated. Check that option data covers the ATM strikes on signal days.")
        return
    wins = traded[traded["net_inr"] > 0]
    losses = traded[traded["net_inr"] <= 0]
    win_rate = len(wins) / len(traded) * 100
    expectancy = traded["net_inr"].mean()
    pf = (wins["net_inr"].sum() / abs(losses["net_inr"].sum())) if not losses.empty and losses["net_inr"].sum() != 0 else float("inf")
    cum = traded["net_inr"].cumsum()
    dd = (cum.cummax() - cum).max()
    print(f"Days: {len(log)}  Trades: {len(traded)}  No-trade days: {len(log) - len(traded)}")
    print(f"Win rate: {win_rate:.1f}%  Expectancy/trade: Rs {expectancy:,.0f}")
    print(f"Profit factor: {pf:.2f}  Total net: Rs {traded['net_inr'].sum():,.0f}  Max drawdown: Rs {dd:,.0f}")
    print(f"By exit: {traded['exit_reason'].value_counts().to_dict()}")
    print(f"Trade log written to {args.out}")


if __name__ == "__main__":
    main()
