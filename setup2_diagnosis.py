"""Setup2 raw-signal diagnosis, Jan-Oct 2026, 25 stocks, cache only.
For each OR-pass stock-day, scan candles 09:30-11:30 and record, per direction:
- raw cross: close beyond OR (CE: close>orh and close<pdh; PE: close<orl and close<pdl)
- each gate that would block that cross: bias-allowed, OR width <=360*scale,
  room >=200*scale from the cross close, CE prev-close-resistance condition
  (no PD level above prev_close, or close > min(res))
- whether find_signal returned an EARLIER setup that day (precedence masking):
  find_signal setup + its signal time vs first setup2-pass candle time
Paper only, no orders.
"""
import sys, json, math
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of

STOCKS = [s for s in SYMBOLS if s not in ("NIFTY", "BANKNIFTY")]

def diagnose():
    totals = {
        "stock_days_or_pass": 0,
        "ce_cross_days": 0, "pe_cross_days": 0, "any_cross_days": 0,
        "ce_pass_all_gates_days": 0, "pe_pass_all_gates_days": 0, "any_pass_all_gates_days": 0,
        "blocked_or_width_only": 0, "blocked_room_only": 0, "blocked_res_only": 0,
        "blocked_bias_only": 0, "blocked_multiple": 0,
        "pass_but_masked_by_earlier_setup": 0, "pass_and_returned_by_find_signal": 0,
        "pass_but_no_find_signal_return": 0,
        "find_signal_setup2_days": 0, "find_signal_other_setup_days": 0,
        "find_signal_none_days": 0,
    }
    masked_examples, pass_no_return_examples = [], []
    per_stock = {}
    for sym in STOCKS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        ps = {k: 0 for k in totals}
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != 2026 or d.month not in range(1, 11) or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, _ = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            or_c = day_spot[day_spot["time"] < "09:30"]
            if or_c.empty:
                continue
            orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
            if not (0.0025 <= (orh - orl) / pdc <= 0.030 if pdc else False):
                continue
            totals["stock_days_or_pass"] += 1; ps["stock_days_or_pass"] += 1
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            levels = sorted(set([pdh, pdc, pdl]))
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            or_width_ok = (orh - orl) <= 360 * scale
            # first setup2-pass candle per direction, and first raw cross per direction
            first_pass, first_cross = {}, {}
            blocked = {"or_width": 0, "room": 0, "res": 0, "bias": 0}
            for j, c in enumerate(candles):
                t = c["time"]
                if t > "11:30":
                    break
                close = float(c["close"])
                prev_close = float(candles[j - 1]["close"]) if j > 0 else float(c["open"])
                for direction, cross in (("CE", close > orh and close < pdh),
                                        ("PE", close < orl and close < pdl)):
                    if not cross:
                        continue
                    if direction not in first_cross:
                        first_cross[direction] = t
                    fails = []
                    if direction not in allowed:
                        fails.append("bias")
                    if not or_width_ok:
                        fails.append("or_width")
                    if direction == "CE":
                        nxt = [l for l in levels if l > close]
                        room = (min(nxt) - close) if nxt else math.inf
                        res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                        if res and not (close > min(res)):
                            fails.append("res")
                    else:
                        nxt = [l for l in levels if l < close]
                        room = (close - max(nxt)) if nxt else math.inf
                    if room < 200 * scale:
                        fails.append("room")
                    for f in set(fails):
                        blocked[f] += 1
                    if not fails and direction not in first_pass:
                        first_pass[direction] = t
            if first_cross:
                totals["any_cross_days"] += 1; ps["any_cross_days"] += 1
            if "CE" in first_cross:
                totals["ce_cross_days"] += 1; ps["ce_cross_days"] += 1
            if "PE" in first_cross:
                totals["pe_cross_days"] += 1; ps["pe_cross_days"] += 1
            if first_pass:
                totals["any_pass_all_gates_days"] += 1; ps["any_pass_all_gates_days"] += 1
                if "CE" in first_pass:
                    totals["ce_pass_all_gates_days"] += 1; ps["ce_pass_all_gates_days"] += 1
                if "PE" in first_pass:
                    totals["pe_pass_all_gates_days"] += 1; ps["pe_pass_all_gates_days"] += 1
                # precedence: what did find_signal return that day?
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                sig_time = str(sig["timestamp"])[11:16] if sig is not None else None
                earliest_pass = min(first_pass.values())
                if setup and setup.startswith("setup2"):
                    totals["pass_and_returned_by_find_signal"] += 1; ps["pass_and_returned_by_find_signal"] += 1
                    totals["find_signal_setup2_days"] += 1; ps["find_signal_setup2_days"] += 1
                elif setup and sig_time is not None and sig_time < earliest_pass:
                    totals["pass_but_masked_by_earlier_setup"] += 1; ps["pass_but_masked_by_earlier_setup"] += 1
                    if len(masked_examples) < 15:
                        masked_examples.append({"symbol": sym, "date": d.date().isoformat(),
                            "find_signal": setup, "find_signal_time": sig_time,
                            "first_setup2_pass_time": earliest_pass, "first_pass": first_pass})
                    totals["find_signal_other_setup_days"] += 1; ps["find_signal_other_setup_days"] += 1
                elif setup:
                    # find_signal returned something at/after the setup2 pass (same-candle
                    # setup4 precedence, or a later setup) - count as other, not earlier-mask
                    totals["find_signal_other_setup_days"] += 1; ps["find_signal_other_setup_days"] += 1
                    if len(pass_no_return_examples) < 15:
                        pass_no_return_examples.append({"symbol": sym, "date": d.date().isoformat(),
                            "find_signal": setup, "find_signal_time": sig_time,
                            "first_setup2_pass_time": earliest_pass, "first_pass": first_pass})
                else:
                    totals["pass_but_no_find_signal_return"] += 1; ps["pass_but_no_find_signal_return"] += 1
                    totals["find_signal_none_days"] += 1; ps["find_signal_none_days"] += 1
            else:
                # no pass: classify blocking (per day, from first-cross fails - approximate
                # by re-checking: use blocked counters at day level via first cross only)
                pass
            # day-level block classification for cross-but-no-pass days
            if first_cross and not first_pass:
                # recompute fails for the first cross candle of each direction, take union
                fails_union = set()
                for j, c in enumerate(candles):
                    t = c["time"]
                    if t > "11:30":
                        break
                    close = float(c["close"])
                    prev_close = float(candles[j - 1]["close"]) if j > 0 else float(c["open"])
                    for direction, cross in (("CE", close > orh and close < pdh),
                                            ("PE", close < orl and close < pdl)):
                        if not cross:
                            continue
                        if direction not in allowed:
                            fails_union.add("bias")
                        if not or_width_ok:
                            fails_union.add("or_width")
                        if direction == "CE":
                            nxt = [l for l in levels if l > close]
                            room = (min(nxt) - close) if nxt else math.inf
                            res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                            if res and not (close > min(res)):
                                fails_union.add("res")
                        else:
                            nxt = [l for l in levels if l < close]
                            room = (close - max(nxt)) if nxt else math.inf
                        if room < 200 * scale:
                            fails_union.add("room")
                        break
                    if fails_union:
                        break
                if len(fails_union) == 1:
                    only = next(iter(fails_union))
                    totals[f"blocked_{only}_only"] += 1; ps[f"blocked_{only}_only"] += 1
                elif len(fails_union) > 1:
                    totals["blocked_multiple"] += 1; ps["blocked_multiple"] += 1
        per_stock[sym] = ps
    return {"totals": totals, "per_stock": per_stock,
            "masked_examples": masked_examples, "pass_not_returned_examples": pass_no_return_examples}

if __name__ == "__main__":
    out = diagnose()
    with open("/home/hatch/workspace/trading/setup2_diagnosis_jan_oct_2026.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(json.dumps(out["totals"], indent=2))
    print("masked examples:", len(out["masked_examples"]))
    for e in out["masked_examples"][:10]:
        print(e)
    print("pass-not-returned examples:", len(out["pass_not_returned_examples"]))
    for e in out["pass_not_returned_examples"][:10]:
        print(e)
