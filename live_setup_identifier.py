"""Live setup identifier: v4 signal detection only, no option fills, no orders.
Usage: python3 live_setup_identifier.py --spot5m <csv> --daily <csv> --bands <json> [--date YYYY-MM-DD]
Prints the first v4 signal for each day (or one day), with signal time, setup,
direction, ATM strike, entry spot and room. Bands are user-supplied; without
bands, Setup 1 is skipped and other setups run on PD/OR only, as in v4.
This is paper / identification only. It places no orders.
"""
import argparse, json, math
import pandas as pd

def round_strike(price, step=100):
    return int(round(price / step) * step)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot5m", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--bands", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--room", type=float, default=200.0)
    args = ap.parse_args()
    spot = pd.read_csv(args.spot5m, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    daily = pd.read_csv(args.daily, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    bands_map = json.load(open(args.bands)) if args.bands else {}
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    for day, day_spot in spot.groupby("date"):
        ds = day.date().isoformat()
        if args.date and ds != args.date:
            continue
        prev = daily[daily["date"] < day]
        if prev.empty:
            continue
        y = prev.iloc[-1]
        pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
        rng = y["high"] - y["low"]
        cs = (y["close"] - y["low"]) / rng * 100 if rng else 50.0
        bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
        allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
        bands = bands_map.get(ds, [])
        all_levels = sorted(set([pdh, pdc, pdl] + [v for b in bands for v in b]))
        or_c = day_spot[day_spot["time"] < "09:30"]
        if or_c.empty:
            continue
        orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
        or_width = orh - orl
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        band_broken = None
        for c in or_c.itertuples():
            for lo, hi in bands:
                if c.close >= lo - 10:
                    band_broken = (lo, hi)
        retest_done = False
        reclaimed = None
        bounced = False
        signal = None
        for i, c in candles.iterrows():
            if c["time"] > "14:30":
                break
            prev_close = float(candles.iloc[i-1]["close"]) if i > 0 else float(c["open"])
            close, high, low, opn = float(c["close"]), float(c["high"]), float(c["low"]), float(c["open"])
            if band_broken and not retest_done:
                lo, hi = band_broken
                if low <= hi and low >= lo - 50 and close > hi:
                    retest_done = True
            day_open = float(day_spot.iloc[0]["open"])
            if day_open < pdc and day_open < pdl and reclaimed is None:
                if close > orh and close > pdc and close > pdl:
                    reclaimed = close
            if band_broken and retest_done and close > orh and close > opn and "CE" in allowed:
                nxt = [l for l in all_levels if l > close]
                room = (min(nxt) - close) if nxt else math.inf
                if room >= args.room:
                    signal = ("CE", "setup1_breakout_retest", room); break
            if reclaimed is not None and "CE" in allowed:
                for lvl in (pdc, pdl):
                    if abs(low - lvl) <= 40 and close > lvl and close > opn:
                        nxt = [l for l in all_levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        if room >= args.room:
                            signal = ("CE", "setup4_pullback", room)
                if signal: break
            if day_open < pdc and "CE" in allowed and close > orh and close > pdc and close < pdh:
                nxt = [l for l in all_levels if l > close]
                room = (min(nxt) - close) if nxt else math.inf
                if room >= args.room:
                    signal = ("CE", "setup4_reclaim", room); break
            if or_width <= 360 and c["time"] <= "11:30":
                if close > orh and close < pdh and "CE" in allowed:
                    res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                    if not res or close > min(res):
                        nxt = [l for l in all_levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        if room >= args.room:
                            signal = ("CE", "setup2_or_breakout", room); break
                if close < orl and close < pdl and "PE" in allowed:
                    nxt = [l for l in all_levels if l < close]
                    room = (close - max(nxt)) if nxt else math.inf
                    if room >= args.room:
                        signal = ("PE", "setup2_or_breakdown", room); break
            band_high_max = max([hi for lo, hi in bands], default=orh)
            if orh <= high <= max(orh, band_high_max) + 100:
                bounced = True
            if or_width >= 400 and bias == "bearish" and "PE" in allowed:
                if bounced and close < opn and close < orh:
                    blocking = pdc if close > pdc else pdl
                    room = close - blocking
                    if room >= args.room:
                        signal = ("PE", "setup3_bounce_rejection", room); break
        if signal:
            d, s, room = signal
            print(f"{ds} bias={bias} OR={orh:.2f}/{orl:.2f} w={or_width:.2f} signal={c['timestamp']} {s} {d} ATM={round_strike(close)} entry_spot={close:.2f} room={room:.2f}")
        else:
            print(f"{ds} bias={bias} OR={orh:.2f}/{orl:.2f} w={or_width:.2f} signal=no_trade")

if __name__ == "__main__":
    main()
