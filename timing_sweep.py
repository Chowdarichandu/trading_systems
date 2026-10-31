"""Timing sweep for NIFTY Cluster 1 (OR-breakdown PE bear-trap).
Paper only. Replays each day bar-by-bar from the Upstox 5-min cache,
using the same exit logic as daytrader_cash_backtest.run_day:
entry = next bar open after signal, stop = signal high (PE),
target = entry - 2*(stop-entry), stop checked before target on each
bar including the entry bar, square-off 15:10.

Gate definition (documented, because 5-min bars are labelled by start):
- A signal bar labelled HH:MM covers HH:MM-HH:MM+5 in real time.
- Gate G means: only signal bars with label >= G are eligible.
  X: G=09:35, Y: G=09:40, Z: G=09:45, plus 09:50, 10:00, 10:30, 11:30.
  An intermediate gate of 09:34 is identical to G=09:35 and 09:39 to
  G=09:40, because there is no 09:34/09:39 5-min bar close.
- Second-close variant: after the first qualifying bar >= G, require
  the NEXT bar to also close below OR low; entry is the open after
  that second bar, stop = second bar high, target recomputed.
- V4 setup2 breakdown conditions (from find_signal): close < OR low,
  close < PDL, room >= 200*scale to next PD level below, OR width
  <= 360*scale, signal bar <= 11:30. Skill Apr-02 is an OR breakdown
  (close < OR low); it also satisfies close < PDL on its day, so the
  same scan covers it (verified in output).
"""
import pandas as pd, json, math, os, sys
BASE = os.path.expanduser("~/workspace/trading/data/progressive/NIFTY")
QTY, COST = 100, 40.0

def load():
    spot = pd.read_csv(os.path.join(BASE, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def replay(day_spot, pdh, pdc, pdl, bias, scale, gate, second_close=False, mode="v4"):
    """Return trade dict or None (no qualifying signal). Only PE breakdown.
    mode v4: setup2 conditions (OR width cap, room>=200*scale, close<PDL).
    mode skill: OR breakdown conditions (close<OR low, close<PDL, no width cap),
    as used for 2026-04-02 and 2026-03-23 Skill trades."""
    or_c = day_spot[day_spot["time"] < "09:30"]
    if or_c.empty:
        return None
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    sig_idx = None
    for i, (_, c) in enumerate(candles.iterrows()):
        t = c["time"]
        if t > "11:30" or t < gate:
            continue
        close = float(c["close"])
        if close < orl and close < pdl:
            if mode == "skill":
                sig_idx = i; break
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                sig_idx = i; break
    if sig_idx is None:
        return None
    if second_close:
        # need next bar also close below OR low
        if sig_idx + 1 >= len(candles) or float(candles.iloc[sig_idx+1]["close"]) >= orl:
            return None
        sig_idx = sig_idx + 1
    if sig_idx + 1 >= len(candles):
        return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx+1]["open"])
    stop = float(sig["high"]); risk = stop - entry
    if risk <= 0:
        return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None,
                "exit": "invalid_risk", "net": None}
    target = entry - 2 * risk
    exit_reason = exit_price = exit_time = None
    for j in range(sig_idx+1, len(candles)):
        c = candles.iloc[j]
        if float(c["high"]) >= stop:
            exit_reason, exit_price, exit_time = "stop", stop, c["time"]; break
        if float(c["low"]) <= target:
            exit_reason, exit_price, exit_time = "target", target, c["time"]; break
        if c["time"] == "15:10":
            exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["time"]; break
    if exit_reason is None:
        c = candles.iloc[-1]
        exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["time"]
    net = round(-(exit_price - entry) * QTY - COST, 2)  # PE: profit = entry-exit
    return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2),
            "risk": round(risk,2), "exit": exit_reason, "exit_time": exit_time,
            "exit_price": exit_price, "net": net,
            "orl": orl, "orh": orh}

def day_data(spot, daily, datestr):
    d = pd.Timestamp(datestr)
    day_spot = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day_spot.empty or prev.empty:
        return None
    y = prev.iloc[-1]
    pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    return day_spot, pdh, pdc, pdl, bias, scale

if __name__ == "__main__":
    spot, daily = load()
    cluster1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02",
                "2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    orig_nets = {"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,
                 "2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
    gates = ["09:30","09:35","09:40","09:45","09:50","10:00","10:30"]
    modes = {"2026-04-02": "skill"}
    out = {"cluster1": {}, "cluster1_second_close": {}, "winning_pe": {}}
    for gate in gates:
        rows = []
        for ds in cluster1:
            dd = day_data(spot, daily, ds)
            r = replay(*dd, gate=gate, mode=modes.get(ds, "v4")) if dd else None
            rows.append({"date": ds, "orig_net": orig_nets[ds], "gate": gate, "trade": r})
        out["cluster1"][gate] = rows
        print(f"\n=== GATE {gate} Cluster1 ===")
        for row in rows:
            print(row["date"], "orig", row["orig_net"], "->", row["trade"])
    for gate in ["09:35","09:40","09:45"]:
        rows = []
        for ds in cluster1:
            dd = day_data(spot, daily, ds)
            r = replay(*dd, gate=gate, second_close=True, mode=modes.get(ds, "v4")) if dd else None
            rows.append({"date": ds, "orig_net": orig_nets[ds], "gate": gate, "trade": r})
        out["cluster1_second_close"][gate] = rows
        print(f"\n=== GATE {gate} + second-close Cluster1 ===")
        for row in rows:
            print(row["date"], "orig", row["orig_net"], "->", row["trade"])
    # Winning PE breakdown days (V5 Nifty targets, PE direction)
    win_days = {"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,
                "2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,
                "2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,
                "2026-10-08":5440,"2026-10-23":11390}
    win_modes = {"2026-03-23": "skill"}
    for gate in gates:
        rows = []
        for ds, onet in win_days.items():
            dd = day_data(spot, daily, ds)
            r = replay(*dd, gate=gate, mode=win_modes.get(ds, "v4")) if dd else None
            rows.append({"date": ds, "orig_net": onet, "gate": gate, "trade": r})
        out["winning_pe"][gate] = rows
        print(f"\n=== GATE {gate} Winning PE ===")
        for row in rows:
            print(row["date"], "orig", row["orig_net"], "->", row["trade"])
    with open(os.path.expanduser("~/workspace/trading/timing_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
