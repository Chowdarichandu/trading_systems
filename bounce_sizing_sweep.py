"""Bounce-bar sizing + new morning-exit sweeps, NIFTY Cluster 1 + winners.
Paper only. Replays bar by bar from Upstox 5-min cache, same signal scan
as timing_sweep.py (V4 setup2 PE breakdown; Skill mode for 2026-04-02 /
2026-03-23). Entry = next bar open unless a variant says otherwise.
Stop checked before target on each bar including entry bar, square-off
15:10, 100 shares equivalent, 40/trade unless a sizing variant says so.
Green = net > 0. No-trade counted separately from green throughout.

Family 1 - sizing by the BOUNCE bar's range:
  Bounce bar B = the bar immediately after the signal bar (the original
  entry bar). Its range Rb = high - low is known only after B closes,
  so a bounce-sized trade CANNOT be entered at the original entry open.
  The live version is therefore a DELAYED entry at the open after B.
  BS-A : delayed entry, stop = entry + Rb, target = entry - 2*Rb,
         no condition on B's close (unconditional delayed entry).
  BS-A2: same as BS-A, but only if B's close is still below OR low
         (breakdown still intact); otherwise no-trade.
  BS-S : diagnostic only, NOT live at original entry: original trade
         prices, shares scaled to Rb: shares = round(100 * orig_risk / Rb).
         Sign cannot change (same exit prices), so this can only change
         total magnitude, never green count. Cost kept at 40 flat.
Family 2 - NEW morning exits (not buffer/OR-high/close-exit/partial/stall):
  Stall (prior sweep) = exit at close after N bars WITHOUT a new
  favourable extreme; its counter RESETS on every new low (PE).
  The variants below do NOT reset, and are not partials:
  T-A : profit-lock trail, full position: trigger at 0.5x risk
        favourable (low <= entry - 0.5*risk); once triggered, exit
        at lock = entry - 0.25*risk on first high >= lock. No partial
        booking, no move to breakeven.
  T-B : same, trigger at 1.0x risk, lock at 0.5x risk.
  T-C6: ABSOLUTE time exit, distinct from stall: if by the close of
        the 6th bar after the entry bar the trade has not reached
        0.5x risk favourable AT ANY POINT (new lows do NOT reset
        this clock), exit at that bar's close. Stop/target checked
        before the time exit on every bar.
  T-C3: same, clock = 3rd bar after the entry bar.
  T-D : OR-low TOUCH exit (distinct from prior close-exit Z, which
        waited for a 5-min CLOSE above OR low): exit at OR low on the
        first bar whose high >= OR low, before the original stop.
        Original target kept.
"""
import os, json, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data

QTY, COST = 100, 40.0

def scan(day_spot, pdh, pdc, pdl, scale, mode="v4"):
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    import math
    levels = sorted(set([pdh, pdc, pdl]))
    for i, (_, c) in enumerate(candles.iterrows()):
        t = c["time"]
        if t > "11:30":
            continue
        close = float(c["close"])
        if close < orl and close < pdl:
            if mode == "skill":
                return candles, orh, orl, i
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                return candles, orh, orl, i
    return candles, orh, orl, None

def replay_generic(candles, start_idx, entry, stop, target, orl=None,
                   trail=None, time_exit=None, orlow_touch=False):
    """PE trade. trail=(trigger_dist, lock_dist) in points below entry.
    time_exit=(n_bars_after_entry, need_dist): exit at close of that bar
    if max favourable so far < need_dist. Returns dict or None."""
    if start_idx >= len(candles):
        return None
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk", "net": None}
    triggered = False
    max_fav = 0.0
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        fav = entry - lo
        if fav > max_fav:
            max_fav = fav
        # trail trigger check (on this bar, before lock/stop handling below)
        if trail and not triggered and lo <= entry - trail[0]:
            triggered = True
        if trail and triggered:
            lock = entry - trail[1]
            if hi >= lock and hi < stop:
                return {"entry": entry, "stop": stop, "target": round(target, 2),
                        "exit": "trail_lock", "exit_time": c["time"], "exit_price": lock,
                        "net": round((entry - lock) * QTY - COST, 2)}
            if hi >= stop:
                return {"entry": entry, "stop": stop, "target": round(target, 2),
                        "exit": "stop", "exit_time": c["time"], "exit_price": stop,
                        "net": round(-risk * QTY - COST, 2)}
        elif orlow_touch and orl is not None and hi >= orl:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "orlow_touch", "exit_time": c["time"], "exit_price": orl,
                    "net": round(-(orl - entry) * QTY - COST, 2)}
        else:
            if hi >= stop:
                return {"entry": entry, "stop": stop, "target": round(target, 2),
                        "exit": "stop", "exit_time": c["time"], "exit_price": stop,
                        "net": round(-risk * QTY - COST, 2)}
        if lo <= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "target", "exit_time": c["time"], "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2)}
        if time_exit and j == start_idx + time_exit[0] and max_fav < time_exit[1]:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "time_exit", "exit_time": c["time"], "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2)}
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "square_off", "exit_time": c["time"], "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2),
            "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2)}

def run_day(dd, mode, variant):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    candles, orh, orl, sig_idx = scan(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None:
        return None
    sig = candles.iloc[sig_idx]
    if variant in ("BS-A", "BS-A2"):
        if sig_idx + 2 >= len(candles):
            return None
        B = candles.iloc[sig_idx + 1]
        if variant == "BS-A2" and float(B["close"]) >= orl:
            return None
        Rb = float(B["high"]) - float(B["low"])
        entry = float(candles.iloc[sig_idx + 2]["open"])
        stop = entry + Rb
        target = entry - 2 * Rb
        r = replay_generic(candles, sig_idx + 2, entry, stop, target)
        if r:
            r.update({"signal": sig["time"], "bounce_range": round(Rb, 2),
                      "bounce_close": float(B["close"]), "orl": orl})
        return r
    # original entry/stop/target for Family 2 and BS-S
    if sig_idx + 1 >= len(candles):
        return None
    entry = float(candles.iloc[sig_idx + 1]["open"])
    stop = float(sig["high"]); risk = stop - entry
    target = entry - 2 * risk
    if variant == "BS-S":
        B = candles.iloc[sig_idx + 1]
        Rb = float(B["high"]) - float(B["low"])
        r = replay_generic(candles, sig_idx + 1, entry, stop, target)
        if r and r["net"] is not None and Rb > 0:
            shares = round(QTY * risk / Rb)
            # recompute net with scaled shares, flat 40 cost
            if r["exit"] == "stop":
                net = round(-risk * shares - COST, 2)
            elif r["exit"] == "target":
                net = round(2 * risk * shares - COST, 2)
            else:
                net = round((entry - r["exit_price"]) * shares - COST, 2)
            r = dict(r, net=net, shares=shares, bounce_range=round(Rb, 2))
        return r
    if variant == "T-A":
        return dict(replay_generic(candles, sig_idx + 1, entry, stop, target,
                     trail=(0.5 * risk, 0.25 * risk)), signal=sig["time"])
    if variant == "T-B":
        return dict(replay_generic(candles, sig_idx + 1, entry, stop, target,
                     trail=(1.0 * risk, 0.5 * risk)), signal=sig["time"])
    if variant == "T-C6":
        return dict(replay_generic(candles, sig_idx + 1, entry, stop, target,
                     time_exit=(6, 0.5 * risk)), signal=sig["time"])
    if variant == "T-C3":
        return dict(replay_generic(candles, sig_idx + 1, entry, stop, target,
                     time_exit=(3, 0.5 * risk)), signal=sig["time"])
    if variant == "T-D":
        return dict(replay_generic(candles, sig_idx + 1, entry, stop, target,
                     orl=orl, orlow_touch=True), signal=sig["time"])
    raise ValueError(variant)

if __name__ == "__main__":
    spot, daily = load()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02",
                "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    orig1 = {"2026-01-09": -3745, "2026-02-06": -2275, "2026-03-30": -2055, "2026-04-02": -2115,
             "2026-05-13": -5075, "2026-06-29": -4740, "2026-07-08": -1985, "2026-08-19": -2300}
    win_days = {"2026-01-21": 9280, "2026-02-24": 7350, "2026-03-16": 8940, "2026-03-13": 5400,
                "2026-03-23": 7260, "2026-04-24": 8820, "2026-05-05": 5040, "2026-07-22": 6320,
                "2026-08-12": 6250, "2026-08-27": 3000, "2026-09-29": 3790, "2026-09-07": 2990,
                "2026-10-08": 5440, "2026-10-23": 11390}
    modes1 = {"2026-04-02": "skill"}
    modesw = {"2026-03-23": "skill"}
    variants = ["BS-A", "BS-A2", "BS-S", "T-A", "T-B", "T-C6", "T-C3", "T-D"]
    out = {}
    for v in variants:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1),
                                         ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data(spot, daily, ds)
                r = run_day(dd, modes.get(ds, "v4"), v) if dd else None
                rows.append({"date": ds, "orig_net": orig[ds], "trade": r})
            out.setdefault(v, {})[label] = rows
            green = sum(1 for x in rows if x["trade"] and x["trade"]["net"] is not None and x["trade"]["net"] > 0)
            nt = sum(1 for x in rows if x["trade"] is None or (x["trade"] and x["trade"]["net"] is None))
            tot = sum(x["trade"]["net"] for x in rows if x["trade"] and x["trade"]["net"] is not None)
            print(f"\n=== {v} {label}: green {green}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                print(x["date"], "orig", x["orig_net"], "->", x["trade"])
    with open(os.path.expanduser("~/workspace/trading/bounce_sizing_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
