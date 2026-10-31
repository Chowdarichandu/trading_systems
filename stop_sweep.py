"""Stop-placement / distance / re-entry sweeps for NIFTY Cluster 1.
Paper only. Replays bar-by-bar from Upstox 5-min cache, same signal
scan as timing_sweep.py: V4 setup2 PE breakdown (close<OR low, close<PDL,
room>=200*scale, OR width<=360*scale, signal<=11:30), except 2026-04-02
Skill (close<OR low, close<PDL, no width/room cap). Entry = next bar open.
Stop checked before target on each bar including entry bar, square-off 15:10.
100 shares, Rs40/trade. PE net = -(exit-entry)*100-40.
Variants are kept separate; no cherry-picking across variants.
"""
import pandas as pd, json, math, os
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

def day_data(spot, daily, datestr):
    d = pd.Timestamp(datestr)
    day_spot = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day_spot.empty or prev.empty: return None
    y = prev.iloc[-1]
    pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    return day_spot, pdh, pdc, pdl, bias, scale

def find_signal(day_spot, pdh, pdc, pdl, scale, mode="v4", min_dist=None, start_idx=0):
    or_c = day_spot[day_spot["time"] < "09:30"]
    if or_c.empty: return None, None, None
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i in range(start_idx, len(candles)):
        c = candles.iloc[i]; t = c["time"]
        if t > "11:30": continue
        close = float(c["close"])
        if close < orl and close < pdl:
            if min_dist is not None and (orl - close) < min_dist: continue
            if mode == "skill":
                return i, candles, (orl, orh)
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if (orh - orl) <= 360 * scale and room >= 200 * scale:
                return i, candles, (orl, orh)
    return None, candles, (orl, orh)

def run_from(candles, sig_idx, orl, orh, stop_mode, stop_param=None, orig_risk=None):
    """stop_mode: 'signal_high' | 'buffer' | 'or_high' | 'close_orl'
    Returns dict or None. For close_orl, exit is on a bar CLOSE above OR low,
    at that close price; target checked first on that bar (low<=target)."""
    if sig_idx is None or sig_idx + 1 >= len(candles): return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx+1]["open"])
    sig_high = float(sig["high"])
    if stop_mode == "signal_high":
        stop = sig_high; risk = stop - entry; target = entry - 2*risk
    elif stop_mode == "buffer":
        stop = sig_high + stop_param; risk = stop - entry; target = entry - 2*risk
    elif stop_mode == "or_high":
        stop = orh; risk = stop - entry
        target = entry - 2*risk if stop_param == "recomputed" else entry - 2*orig_risk
    elif stop_mode == "close_orl":
        stop = orl  # trigger level, not a touch stop
        risk = sig_high - entry  # target kept on original risk (see report: recomputed variant is degenerate)
        target = entry - 2*risk
    else: raise ValueError(stop_mode)
    if stop_mode != "close_orl" and risk <= 0:
        return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
    for j in range(sig_idx+1, len(candles)):
        c = candles.iloc[j]
        if stop_mode == "close_orl":
            if float(c["low"]) <= target:
                return finish(sig, entry, stop, target, risk, "target", target, c["time"])
            if float(c["close"]) > orl:
                return finish(sig, entry, stop, target, risk, "close_above_orl", float(c["close"]), c["time"])
            if c["time"] == "15:10":
                return finish(sig, entry, stop, target, risk, "square_off", float(c["close"]), c["time"])
        else:
            if float(c["high"]) >= stop:
                return finish(sig, entry, stop, target, risk, "stop", stop, c["time"])
            if float(c["low"]) <= target:
                return finish(sig, entry, stop, target, risk, "target", target, c["time"])
            if c["time"] == "15:10":
                return finish(sig, entry, stop, target, risk, "square_off", float(c["close"]), c["time"])
    c = candles.iloc[-1]
    return finish(sig, entry, stop, target, risk, "square_off", float(c["close"]), c["time"])

def finish(sig, entry, stop, target, risk, exit_reason, exit_price, exit_time):
    return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2),
            "risk": round(risk,2), "exit": exit_reason, "exit_time": exit_time,
            "exit_price": exit_price, "net": round(-(exit_price-entry)*QTY-COST,2)}

def trade(day, mode, stop_mode, stop_param=None, min_dist=None):
    dd = day[0] if isinstance(day, tuple) else None
    return None

def replay_one(spot, daily, ds, mode, stop_mode, stop_param=None, min_dist=None):
    dd = day_data(spot, daily, ds)
    if not dd: return None
    day_spot, pdh, pdc, pdl, bias, scale = dd
    sig_idx, candles, (orl, orh) = find_signal(day_spot, pdh, pdc, pdl, scale, mode, min_dist)
    if sig_idx is None: return None
    # orig risk for or_high uncapped variant
    sig = candles.iloc[sig_idx]; entry = float(candles.iloc[sig_idx+1]["open"]) if sig_idx+1 < len(candles) else None
    orig_risk = float(sig["high"]) - entry if entry is not None else None
    r = run_from(candles, sig_idx, orl, orh, stop_mode, stop_param, orig_risk)
    if r: r.update({"orl": orl, "orh": orh})
    return r

def replay_reentry(spot, daily, ds, mode):
    """Original trade, then ONE re-entry: first bar after the stop bar whose
    close is back below OR low becomes the re-entry signal; entry next open,
    stop = that bar's high, target = entry-2*risk. Returns (orig, reentry)."""
    dd = day_data(spot, daily, ds)
    if not dd: return None, None
    day_spot, pdh, pdc, pdl, bias, scale = dd
    sig_idx, candles, (orl, orh) = find_signal(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None: return None, None
    orig = run_from(candles, sig_idx, orl, orh, "signal_high")
    if orig is None or orig["exit"] != "stop": return orig, None
    # stop bar index: find bar with time == exit_time at/after entry
    stop_bar = None
    for j in range(sig_idx+1, len(candles)):
        if candles.iloc[j]["time"] == orig["exit_time"]:
            stop_bar = j; break
    if stop_bar is None: return orig, None
    # scan for close below OR low after stop bar; that bar is re-entry signal
    for k in range(stop_bar+1, len(candles)):
        if candles.iloc[k]["time"] > "11:30": break
        if float(candles.iloc[k]["close"]) < orl:
            # re-entry signal must also be below PDL? Keep it simple and stated:
            # re-entry is defined in the task as close back below OR low only.
            re = run_from(candles, k, orl, orh, "signal_high")
            if re: re.update({"orl": orl, "orh": orh, "reentry_signal": candles.iloc[k]["time"]})
            return orig, re
    return orig, None

if __name__ == "__main__":
    spot, daily = load()
    cluster1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    orig_nets = {"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,
                 "2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
    modes = {"2026-04-02": "skill"}
    win_days = {"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,
                "2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,
                "2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,
                "2026-10-08":5440,"2026-10-23":11390}
    win_modes = {"2026-03-23": "skill"}
    out = {}
    def summarise(rows):
        traded = [r for r in rows if r["trade"] is not None and r["trade"].get("net") is not None]
        green = sum(1 for r in traded if r["trade"]["net"] > 0)
        nt = sum(1 for r in rows if r["trade"] is None or r["trade"].get("net") is None)
        loss = sum(1 for r in traded if r["trade"]["net"] <= 0)
        total = round(sum(r["trade"]["net"] for r in traded),2)
        return {"green": green, "no_trade": nt, "still_loss": loss, "traded_total": total, "n_traded": len(traded)}
    variants = [
        ("stop_buffer_10", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "buffer", 10)),
        ("stop_buffer_20", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "buffer", 20)),
        ("stop_or_high_recomputed", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "or_high", "recomputed")),
        ("stop_or_high_orig_target", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "or_high", "orig")),
        ("stop_close_orl_orig_target", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "close_orl")),
        ("distance_10", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "signal_high", None, 10)),
        ("distance_20", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "signal_high", None, 20)),
        ("distance_30", lambda ds: replay_one(spot, daily, ds, modes.get(ds,"v4"), "signal_high", None, 30)),
    ]
    for name, fn in variants:
        rows = [{"date": ds, "orig_net": orig_nets[ds], "trade": fn(ds)} for ds in cluster1]
        out[name] = {"cluster1": rows, "summary": summarise(rows)}
        print(f"\n=== {name} Cluster1 {out[name]['summary']} ===")
        for r in rows: print(r["date"], r["orig_net"], "->", r["trade"])
        # winning PE impact
        wrows = []
        for ds, onet in win_days.items():
            # winning replay needs same variant: reuse fn logic but with win mode
            if name.startswith("stop_buffer"):
                buf = 10 if "10" in name else 20
                t = replay_one(spot, daily, ds, win_modes.get(ds,"v4"), "buffer", buf)
            elif name.startswith("stop_or_high"):
                t = replay_one(spot, daily, ds, win_modes.get(ds,"v4"), "or_high", "recomputed" if "recomputed" in name else "orig")
            elif name.startswith("stop_close"):
                t = replay_one(spot, daily, ds, win_modes.get(ds,"v4"), "close_orl")
            else:
                d = 10 if name=="distance_10" else 20 if name=="distance_20" else 30
                t = replay_one(spot, daily, ds, win_modes.get(ds,"v4"), "signal_high", None, d)
            wrows.append({"date": ds, "orig_net": onet, "trade": t})
        out[name]["winning_pe"] = wrows
        out[name]["winning_summary"] = summarise(wrows)
        print(f"--- {name} Winning PE {out[name]['winning_summary']} ---")
        for r in wrows: print(r["date"], r["orig_net"], "->", r["trade"])
    # Re-entry family
    rows = []
    for ds in cluster1:
        orig, re = replay_reentry(spot, daily, ds, modes.get(ds,"v4"))
        rows.append({"date": ds, "orig_net": orig_nets[ds], "orig": orig, "reentry": re,
                     "reentry_net": re["net"] if re else None,
                     "combined_net": round(orig["net"]+re["net"],2) if (orig and re and re.get("net") is not None) else (orig["net"] if orig else None)})
    out["reentry"] = {"cluster1": rows}
    print("\n=== REENTRY Cluster1 ===")
    for r in rows: print(r["date"], "orig", r["orig"], "reentry", r["reentry"], "combined", r["combined_net"])
    # winning re-entry not applicable (winners did not stop) - skip
    with open(os.path.expanduser("~/workspace/trading/stop_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
