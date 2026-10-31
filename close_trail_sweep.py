"""Close-based profit-lock trail + pre-signal sizing sweep, NIFTY Cluster 1 + winners.
Paper only. Replays bar by bar from Upstox 5-min cache, same signal scan
as timing_sweep.py / bounce_sizing_sweep.py (V4 setup2 PE breakdown;
Skill mode for 2026-04-02 / 2026-03-23). Entry = next bar open after
signal, original stop = signal high (PE), original target = entry - 2*risk,
stop checked before target on each bar including entry bar, square-off
15:10, 100 shares, 40/trade. Green = net > 0. No-trade separate from green.

Ordering per bar (documented, conservative):
  1. intraday high >= original stop -> stop (stop wins over a close-lock)
  2. intraday low <= target -> target
  3. at bar close: update arm/lock from the CLOSE (not the low/high),
     then if a lock is armed from an EARLIER bar and this close >= lock
     level -> exit at this close. A lock armed on bar k cannot exit on
     bar k itself (its close is by construction below the lock level for
     distance-triggered locks; for level-armed locks the exit check
     starts on the next bar, so a wobble close that arms the lock cannot
     instantly exit at a loss).
  4. square-off at 15:10 close if nothing fired earlier.

Family (a) CLOSE-based trail, trigger/exit on closes only:
  CT-05:            close fav >= 0.5*risk -> lock 0.25*risk
  CT-10:            close fav >= 1.0*risk -> lock 0.50*risk
  CT-RATCHET-CLOSE: stepped on closes: fav >=0.5 -> lock 0.25;
                    fav >=1.0 -> lock 0.50; fav >=1.5 -> lock 1.00
                    (lock only ever moves in the trade's favour)
Family (b) lock arms ONLY after a CLOSE below a level, original stop
kept throughout (lock is an additional exit, not a stop replacement):
  CT-ARM-SIG:        arm when a bar closes below the SIGNAL bar's low;
                     then lock 0.25*risk, exit on a later close >= lock
  CT-ARM-SIG-RATCHET: same arm, stepped locks 0.25/0.50/1.00 by close fav
Family (c) sizing from a PRE-SIGNAL bar, knowable at entry (no delay):
  S-ORAVG:     risk_unit = mean range (high-low) of the 3 OR bars
               (09:15, 09:20, 09:25); stop = entry + risk_unit,
               target = entry - 2*risk_unit
  S-PD10:      risk_unit = 0.10 * previous-day range (high-low)
  S-ORAVG-CAP: risk_unit = min(mean OR bar range, original risk)
"""
import os, json, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
from bounce_sizing_sweep import scan
QTY, COST = 100, 40.0

def lock_from_close_fav(fav, risk, mode):
    """Return lock distance (points below entry) or None, from close fav."""
    if mode == "CT-05":
        return 0.25 * risk if fav >= 0.5 * risk else None
    if mode == "CT-10":
        return 0.50 * risk if fav >= 1.0 * risk else None
    if mode == "CT-RATCHET-CLOSE":
        if fav >= 1.5 * risk: return 1.00 * risk
        if fav >= 1.0 * risk: return 0.50 * risk
        if fav >= 0.5 * risk: return 0.25 * risk
        return None
    return None

def replay_close_trail(candles, start_idx, entry, stop, target, sig_low, mode):
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk", "net": None}
    lock = None  # lock distance below entry, or None
    armed = False
    is_arm = mode.startswith("CT-ARM")
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        if hi >= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "stop", "exit_time": c["time"], "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2)}
        if lo <= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "target", "exit_time": c["time"], "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2)}
        # close-based update / exit. OLD-lock check FIRST: if a lock armed
        # on an earlier bar is breached by this close, exit at this close
        # (close-only execution cannot exit at the lock price itself).
        fav_close = entry - cl
        if is_arm:
            if armed and lock is not None and cl >= entry - lock:
                return {"entry": entry, "stop": stop, "target": round(target, 2),
                        "exit": "close_lock", "exit_time": c["time"], "exit_price": cl,
                        "net": round((entry - cl) * QTY - COST, 2)}
            if not armed and cl < sig_low:
                armed = True
                if mode == "CT-ARM-SIG":
                    lock = 0.25 * risk
                else:
                    lock = lock_from_close_fav(fav_close, risk, "CT-RATCHET-CLOSE")
                    if lock is None:
                        lock = 0.25 * risk  # armed, but fav below first step: floor at 0.25
                continue  # exit check starts next bar
            if armed and mode == "CT-ARM-SIG-RATCHET":
                nl = lock_from_close_fav(fav_close, risk, "CT-RATCHET-CLOSE")
                if nl is not None and nl > lock:
                    lock = nl
        else:
            if lock is not None and cl >= entry - lock:
                return {"entry": entry, "stop": stop, "target": round(target, 2),
                        "exit": "close_lock", "exit_time": c["time"], "exit_price": cl,
                        "net": round((entry - cl) * QTY - COST, 2)}
            nl = lock_from_close_fav(fav_close, risk, mode)
            if nl is not None and (lock is None or nl > lock):
                lock = nl
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "square_off", "exit_time": c["time"], "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2),
            "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2)}

def replay_generic_simple(candles, start_idx, entry, stop, target):
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk", "net": None}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        if hi >= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "stop", "exit_time": c["time"], "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2)}
        if lo <= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2),
                    "exit": "target", "exit_time": c["time"], "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2)}
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
    if sig_idx + 1 >= len(candles):
        return None
    entry = float(candles.iloc[sig_idx + 1]["open"])
    stop = float(sig["high"]); risk = stop - entry
    target = entry - 2 * risk
    extra = {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target, 2),
             "risk": round(risk, 2), "sig_low": float(sig["low"]), "orl": orl}
    if variant.startswith("CT-"):
        r = replay_close_trail(candles, sig_idx + 1, entry, stop, target, float(sig["low"]), variant)
        return dict(r, **extra) if r else None
    if variant.startswith("S-"):
        or_bars = day_spot[day_spot["time"] < "09:30"]
        or_ranges = [float(r["high"]) - float(r["low"]) for _, r in or_bars.iterrows()]
        or_avg = sum(or_ranges) / len(or_ranges) if or_ranges else risk
        pd_range = pdh - pdl
        if variant == "S-ORAVG":
            ru = or_avg
        elif variant == "S-PD10":
            ru = 0.10 * pd_range
        elif variant == "S-ORAVG-CAP":
            ru = min(or_avg, risk)
        else:
            raise ValueError(variant)
        stop2 = entry + ru; target2 = entry - 2 * ru
        r = replay_generic_simple(candles, sig_idx + 1, entry, stop2, target2)
        if not r:
            return None
        out = dict(extra)
        out.update(r)  # r's stop/target are the sized stop2/target2
        out.update({"risk_unit": round(ru, 2), "or_avg_range": round(or_avg, 2),
                    "pd_range": round(pd_range, 2), "stop_orig": stop,
                    "target_orig": round(target, 2)})
        return out
    raise ValueError(variant)

def close_fav_before_stop(dd, mode):
    """Diagnostic ceiling: max (entry-close) in x original risk, on bars
    before the stop bar, for a Cluster 1 day. No close-trail with a
    trigger above this can ever arm on that day."""
    day_spot, pdh, pdc, pdl, bias, scale = dd
    candles, orh, orl, sig_idx = scan(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None:
        return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx + 1]["open"]); stop = float(sig["high"]); risk = stop - entry
    best = 0.0; best_time = None
    for j in range(sig_idx + 1, len(candles)):
        c = candles.iloc[j]
        if float(c["high"]) >= stop:
            break
        fav = entry - float(c["close"])
        if fav > best:
            best = fav; best_time = c["time"]
    return {"entry": entry, "stop": stop, "risk": round(risk, 2),
            "max_close_fav_pts": round(best, 2), "max_close_fav_xrisk": round(best / risk, 3) if risk else None,
            "at": best_time, "sig_low": float(sig["low"])}

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
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    print("=== Close-favourable ceiling, Cluster 1 (before stop bar) ===")
    ceil = {}
    for ds in cluster1:
        dd = day_data(spot, daily, ds)
        ceil[ds] = close_fav_before_stop(dd, modes1.get(ds, "v4")) if dd else None
        print(ds, ceil[ds])
    variants = ["CT-05", "CT-10", "CT-RATCHET-CLOSE", "CT-ARM-SIG", "CT-ARM-SIG-RATCHET",
                "S-ORAVG", "S-PD10", "S-ORAVG-CAP"]
    out = {"close_fav_ceiling": ceil}
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
            nt = sum(1 for x in rows if x["trade"] is None)
            tot = sum(x["trade"]["net"] for x in rows if x["trade"] and x["trade"]["net"] is not None)
            print(f"\n=== {v} {label}: green {green}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                print(x["date"], "orig", x["orig_net"], "->", x["trade"])
    with open(os.path.expanduser("~/workspace/trading/close_trail_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
