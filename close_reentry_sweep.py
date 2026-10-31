"""Close-confirmed re-entry (strict variants) + signal-quality filter
(original signal only, no rescan) + bounce-bar-close entry.
NIFTY Cluster 1 + 14 PE winners, paper only, from Upstox 5-min cache.
Reuses timing_sweep.load/day_data and bounce_sizing_sweep.scan.

IMPORTANT honesty note, stated before any result:
- The BASE single-close re-entry (first bar after the stop whose
  CLOSE is below OR low, to 11:30) was ALREADY tested in
  stop_sweep.py (replay_reentry): re-entry alone 3/8 green,
  day combined 2/8 green, -17,355. It is reproduced here ONLY as
  a reference, NOT as a new variant. The new (i) variants are
  stricter / wider-window versions of it, defined below.
- Signal distance was ALREADY tested in stop_sweep.py as a
  SCAN-FORWARD rule (skip bars until one meets the distance, so
  later signals appear). The new (ii) variants are ORIGINAL-SIGNAL-
  ONLY filters: if the original signal fails, the day is a
  no-trade, no later signal is sought. That is a different rule.

Common replay (PE): entry, stop, target=entry-2*risk; per bar
stop checked before target, square-off at 15:10 close; 100 shares,
Rs40/trade; green = net > 0; no-trade counted separately from green.
"""
import os, json, math, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
from bounce_sizing_sweep import scan

QTY, COST = 100, 40.0

def replay_pe(candles, start_idx, entry, stop, target):
    """Return dict with exit, exit_idx (candles index), net, or None if
    start_idx out of range. start_idx is first bar that can exit."""
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk",
                "exit_time": None, "exit_idx": None, "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        if hi >= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if lo <= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2)}

def orig_trade(dd, mode):
    """Return (candles, orh, orl, sig_idx, sig_dict, orig) or None."""
    day_spot, pdh, pdc, pdl, bias, scale = dd
    candles, orh, orl, sig_idx = scan(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None or sig_idx + 1 >= len(candles):
        return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx + 1]["open"])
    stop = float(sig["high"]); risk = stop - entry
    target = entry - 2 * risk
    orig = replay_pe(candles, sig_idx + 1, entry, stop, target)
    info = {"signal": sig["time"], "sig_close": float(sig["close"]), "sig_high": stop,
            "sig_low": float(sig["low"]), "sig_range": round(float(sig["high"]) - float(sig["low"]), 2),
            "entry": entry, "stop": stop, "target": round(target, 2), "risk": round(risk, 2),
            "orl": orl, "orh": orh, "or_width": round(orh - orl, 2),
            "dist_below_orl": round(orl - float(sig["close"]), 2),
            "pdl": pdl, "scale": scale,
            "close_pos": round((float(sig["close"]) - float(sig["low"])) / (float(sig["high"]) - float(sig["low"])), 3)
            if float(sig["high"]) > float(sig["low"]) else None}
    return candles, orh, orl, sig_idx, info, orig

def reentry_trade(candles, orl, pdl, scale, mode, stop_idx, variant):
    """Find re-entry signal after stop_idx (candles index of stop bar).
    Returns (re_dict, re_signal_time) or (None, None)."""
    if stop_idx is None:
        return None, None
    # window: last signal bar time <= window
    window = "15:05" if variant == "RE-EXT" else "11:30"
    # For RE-2C we need a pair of consecutive closes < orl
    prev_below = False
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]
        t = c["time"]
        if t > window:
            break
        cl = float(c["close"])
        if variant == "RE-BASE" or variant == "RE-EXT":
            if cl < orl:
                sig_idx = k; break
        elif variant == "RE-2C":
            if cl < orl:
                if prev_below:
                    sig_idx = k; break
                prev_below = True
            else:
                prev_below = False
        elif variant == "RE-PDL":
            if cl < orl and cl < pdl:
                if mode == "skill":
                    sig_idx = k; break
                levels = None  # room needs PD levels: recompute from pdl? use dist to pdl as room proxy? No:
                # Full V4 room: close to next PD level below. We do not have pdh/pdc here,
                # so caller passes room via pdl only is insufficient; handled by caller variant
                # below via reentry_trade_full. This branch is not used.
                sig_idx = k; break
        else:
            raise ValueError(variant)
    else:
        return None, None
    if k + 1 >= len(candles):
        return None, None
    entry = float(candles.iloc[k + 1]["open"])
    stop = float(candles.iloc[k]["high"]); risk = stop - entry
    target = entry - 2 * risk
    r = replay_pe(candles, k + 1, entry, stop, target)
    r.update({"re_signal": c["time"]})
    return r, c["time"]

def reentry_full(dd, mode, variant):
    """Full re-entry day: orig + one re-entry variant. Returns dict."""
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    day_spot, pdh, pdc, pdl, bias, scale = dd
    if orig is None or orig["exit"] != "stop":
        return {"info": info, "orig": orig, "re": None, "day_net": orig["net"] if orig else None}
    stop_idx = orig["exit_idx"]
    window = "15:05" if variant == "RE-EXT" else "11:30"
    sig_k = None
    prev_below = False
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > window:
            break
        cl = float(c["close"])
        if variant in ("RE-BASE", "RE-EXT"):
            if cl < orl:
                sig_k = k; break
        elif variant == "RE-2C":
            if cl < orl:
                if prev_below:
                    sig_k = k; break
                prev_below = True
            else:
                prev_below = False
        elif variant == "RE-PDL":
            if cl < orl and cl < pdl:
                if mode == "skill":
                    sig_k = k; break
                levels = sorted(set([pdh, pdc, pdl]))
                nxt = [l for l in levels if l < cl]
                room = (cl - max(nxt)) if nxt else math.inf
                if room >= 200 * scale:
                    sig_k = k; break
        else:
            raise ValueError(variant)
    if sig_k is None or sig_k + 1 >= len(candles):
        return {"info": info, "orig": orig, "re": None, "day_net": orig["net"]}
    entry = float(candles.iloc[sig_k + 1]["open"])
    stop = float(candles.iloc[sig_k]["high"]); risk = stop - entry
    target = entry - 2 * risk
    re = replay_pe(candles, sig_k + 1, entry, stop, target)
    re.update({"re_signal": candles.iloc[sig_k]["time"]})
    day_net = None
    if orig["net"] is not None and re["net"] is not None:
        day_net = round(orig["net"] + re["net"], 2)
    return {"info": info, "orig": orig, "re": re, "day_net": day_net}

def sq_filter(info, variant):
    """Original-signal-only filter: True = trade allowed."""
    d = info["dist_below_orl"]; w = info["or_width"]; cp = info["close_pos"]
    if variant == "SQ-D5": return d >= 5
    if variant == "SQ-D10": return d >= 10
    if variant == "SQ-D20": return d >= 20
    if variant == "SQ-D30": return d >= 30
    if variant == "SQ-WLE80": return w <= 80
    if variant == "SQ-WLE100": return w <= 100
    if variant == "SQ-WLE120": return w <= 120
    if variant == "SQ-WGT100": return w > 100
    if variant == "SQ-BODY33": return cp is not None and cp <= 0.33
    if variant == "SQ-COMB": return d >= 10 and w <= 120
    raise ValueError(variant)

def bc_trade(dd, mode, variant):
    """Bounce-bar-close entry. S+1 = original entry bar. Entry = close of
    S+1, only if that close < ORL, else no-trade. Replay from S+2.
    BC-A: stop = original signal high. BC-B: stop = high of S+1."""
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    if sig_idx + 1 >= len(candles):
        return None
    b = candles.iloc[sig_idx + 1]
    if float(b["close"]) >= orl:
        return {"info": info, "orig": orig, "bc": None, "reason": "bounce_close_above_orl_no_trade"}
    entry = float(b["close"])
    stop = float(info["sig_high"]) if variant == "BC-A" else float(b["high"])
    risk = stop - entry
    if risk <= 0 or sig_idx + 2 >= len(candles):
        return {"info": info, "orig": orig, "bc": None, "reason": "invalid_risk_or_no_bars"}
    target = entry - 2 * risk
    bc = replay_pe(candles, sig_idx + 2, entry, stop, target)
    bc.update({"bounce_bar": b["time"], "bounce_high": float(b["high"]), "bounce_close": entry})
    return {"info": info, "orig": orig, "bc": bc}

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
    # --- original signal diagnostics ---
    print("=== Original signals: Cluster 1 ===")
    for ds in cluster1:
        dd = day_data(spot, daily, ds)
        o = orig_trade(dd, modes1.get(ds, "v4")) if dd else None
        print(ds, o[4] if o else None, "orig_exit", o[5] if o else None)
        out.setdefault("diag_cluster1", {})[ds] = o[4] if o else None
    print("=== Original signals: Winners ===")
    for ds in win_days:
        dd = day_data(spot, daily, ds)
        o = orig_trade(dd, modesw.get(ds, "v4")) if dd else None
        print(ds, o[4] if o else None, "orig_net", o[5]["net"] if o and o[5] else None)
        out.setdefault("diag_winners", {})[ds] = o[4] if o else None

    # --- (i) re-entry variants ---
    for v in ["RE-BASE", "RE-2C", "RE-PDL", "RE-EXT"]:
        rows = []
        for ds in cluster1:
            dd = day_data(spot, daily, ds)
            r = reentry_full(dd, modes1.get(ds, "v4"), v) if dd else None
            rows.append({"date": ds, "orig_net": orig1[ds], "result": r})
        out.setdefault("reentry", {})[v] = rows
        re_green = sum(1 for x in rows if x["result"] and x["result"]["re"] and x["result"]["re"]["net"] is not None and x["result"]["re"]["net"] > 0)
        re_traded = sum(1 for x in rows if x["result"] and x["result"]["re"])
        day_green = sum(1 for x in rows if x["result"] and x["result"]["day_net"] is not None and x["result"]["day_net"] > 0)
        tot = sum(x["result"]["day_net"] for x in rows if x["result"] and x["result"]["day_net"] is not None)
        print(f"\n=== {v} Cluster1: re-alone green {re_green}/{re_traded} traded, day green {day_green}/8, day total {tot} ===")
        for x in rows:
            r = x["result"]
            print(x["date"], "orig", x["orig_net"], "re", r["re"] if r else None, "day", r["day_net"] if r else None)

    # --- (ii) signal-quality, original signal only ---
    for v in ["SQ-D5", "SQ-D10", "SQ-D20", "SQ-D30", "SQ-WLE80", "SQ-WLE100", "SQ-WLE120",
              "SQ-WGT100", "SQ-BODY33", "SQ-COMB"]:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1),
                                         ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data(spot, daily, ds)
                o = orig_trade(dd, modes.get(ds, "v4")) if dd else None
                if o is None:
                    rows.append({"date": ds, "orig_net": orig[ds], "kept": None, "trade": None})
                else:
                    kept = sq_filter(o[4], v)
                    rows.append({"date": ds, "orig_net": orig[ds], "kept": kept,
                                 "trade": o[5] if kept else None, "info": o[4]})
            out.setdefault("sq", {}).setdefault(v, {})[label] = rows
            green = sum(1 for x in rows if x["trade"] and x["trade"]["net"] is not None and x["trade"]["net"] > 0)
            nt = sum(1 for x in rows if not x["kept"])
            tot = sum(x["trade"]["net"] for x in rows if x["trade"] and x["trade"]["net"] is not None)
            print(f"\n=== {v} {label}: green {green}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                print(x["date"], "orig", x["orig_net"], "kept", x["kept"], "->", x["trade"]["net"] if x["trade"] else None, x["info"] if x["trade"] is None else "")

    # --- (iii) bounce-bar-close ---
    for v in ["BC-A", "BC-B"]:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1),
                                         ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data(spot, daily, ds)
                r = bc_trade(dd, modes.get(ds, "v4"), v) if dd else None
                rows.append({"date": ds, "orig_net": orig[ds], "result": r})
            out.setdefault("bc", {}).setdefault(v, {})[label] = rows
            green = sum(1 for x in rows if x["result"] and x["result"]["bc"] and x["result"]["bc"]["net"] is not None and x["result"]["bc"]["net"] > 0)
            nt = sum(1 for x in rows if x["result"] and x["result"]["bc"] is None)
            tot = sum(x["result"]["bc"]["net"] for x in rows if x["result"] and x["result"]["bc"] and x["result"]["bc"]["net"] is not None)
            print(f"\n=== {v} {label}: green {green}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                r = x["result"]
                print(x["date"], "orig", x["orig_net"], "bc", r["bc"] if r else None, r.get("reason") if r else None)

    with open(os.path.expanduser("~/workspace/trading/close_reentry_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
