"""Extra variants for bounce_sizing_sweep.py, run 2026-10-29.
BS-CAP: bounce-range delayed entry with Rb capped at original risk.
T-RATCHET: profit-lock trail with locks stepping up (0.5x->0.25x lock,
1.0x->0.5x lock, 1.5x->1.0x lock); lock checked on the bar that sets it,
as in bounce_sizing_sweep.py (stop wins if a bar's high reaches stop).
Paper only; same scan, square-off 15:10, 100 shares, 40/trade.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
from bounce_sizing_sweep import scan, replay_generic, QTY, COST

def replay_ratchet(candles, start_idx, entry, stop, target):
    risk = stop - entry; lock = None
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        fav = entry - lo; newlock = None
        if fav >= 1.5 * risk: newlock = entry - 1.0 * risk
        elif fav >= 1.0 * risk: newlock = entry - 0.5 * risk
        elif fav >= 0.5 * risk: newlock = entry - 0.25 * risk
        if newlock is not None and (lock is None or newlock < lock): lock = newlock
        if lock is not None:
            if hi >= lock and hi < stop:
                return {"exit": "ratchet_lock", "exit_time": c["time"], "exit_price": lock,
                        "net": round((entry - lock) * QTY - COST, 2)}
            if hi >= stop:
                return {"exit": "stop", "exit_time": c["time"], "exit_price": stop,
                        "net": round(-risk * QTY - COST, 2)}
        else:
            if hi >= stop:
                return {"exit": "stop", "exit_time": c["time"], "exit_price": stop,
                        "net": round(-risk * QTY - COST, 2)}
        if lo <= target:
            return {"exit": "target", "exit_time": c["time"], "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2)}
        if c["time"] == "15:10":
            return {"exit": "square_off", "exit_time": c["time"], "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2)}
    return None

def run(dd, mode, variant):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    candles, orh, orl, sig_idx = scan(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None: return None
    sig = candles.iloc[sig_idx]
    if variant == "BS-CAP":
        if sig_idx + 2 >= len(candles): return None
        B = candles.iloc[sig_idx + 1]; Rb = float(B["high"]) - float(B["low"])
        orig_entry = float(candles.iloc[sig_idx + 1]["open"]); orig_risk = float(sig["high"]) - orig_entry
        Rb_eff = min(Rb, orig_risk)
        entry = float(candles.iloc[sig_idx + 2]["open"]); stop = entry + Rb_eff; target = entry - 2 * Rb_eff
        r = replay_generic(candles, sig_idx + 2, entry, stop, target)
        if r: r.update({"signal": sig["time"], "bounce_range": round(Rb, 2), "Rb_eff": round(Rb_eff, 2)})
        return r
    entry = float(candles.iloc[sig_idx + 1]["open"]); stop = float(sig["high"]); risk = stop - entry
    target = entry - 2 * risk
    r = replay_ratchet(candles, sig_idx + 1, entry, stop, target)
    if r: r.update({"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target, 2)})
    return r

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
    out = {}
    for v in ["BS-CAP", "T-RATCHET"]:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1),
                                         ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data(spot, daily, ds)
                r = run(dd, modes.get(ds, "v4"), v) if dd else None
                rows.append({"date": ds, "orig_net": orig[ds], "trade": r})
            out.setdefault(v, {})[label] = rows
            green = sum(1 for x in rows if x["trade"] and x["trade"]["net"] is not None and x["trade"]["net"] > 0)
            tot = sum(x["trade"]["net"] for x in rows if x["trade"] and x["trade"]["net"] is not None)
            print(f"=== {v} {label}: green {green}/{len(rows)} total {tot} ===")
    with open(os.path.expanduser("~/workspace/trading/bounce_sizing_extra_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
