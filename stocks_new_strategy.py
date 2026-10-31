#!/usr/bin/env python3
"""Mechanisms 2 (LADDER) and 3 (SNAP) — invented stock strategies.
Spec: stocks_new_strategy_frozen.md. Equity cash, paper only.
Per 100 shares provisional, Rs40/trade."""
import csv, json, math, os, sys
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import stocks_hunt1 as H

OUT = H.OUT; SYMBOLS = H.SYMBOLS; DAYS = H.DAYS
QTY, COST = H.QTY, H.COST
SQ, LAST_ENTRY, TRIG_FROM = H.SQ, H.LAST_ENTRY, H.TRIG_FROM

def breadth(ts):
    by = defaultdict(list)
    for t in ts: by[t["symbol"]].append(t)
    sm = sorted(((H.metrics(v)["net"], k, H.metrics(v)["trades"]) for k, v in by.items()), reverse=True)
    tot = H.metrics(ts)["net"]
    return {"top": sm[:5], "bottom": sm[-5:],
            "pos": sum(1 for x in sm if x[0] > 0),
            "top3_share": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None}

def summarize(fid, ts):
    s = {"family": fid, "all": H.metrics(ts),
         "jan_may": H.metrics(H.split(ts, "2026-01-01", "2026-05-31")),
         "jun_oct": H.metrics(H.split(ts, "2026-06-01", "2026-10-28")),
         "october": H.metrics(H.split(ts, "2026-10-01", "2026-10-28")),
         "per_day": round(len(ts) / len(DAYS), 2),
         "rounds": {str(r): H.metrics([t for t in ts if t["round"] == r]) for r in (1, 2, 3, 4)},
         "long": H.metrics([t for t in ts if t["dir"] == "LONG"]),
         "short": H.metrics([t for t in ts if t["dir"] == "SHORT"]),
         "event": H.metrics([t for t in ts if t["event"] == "event"]),
         "no_event": H.metrics([t for t in ts if t["event"] == "no_event"]),
         "breadth": breadth(ts)}
    return s

def save(fid, ts):
    if not ts: return
    cols = ["family", "symbol", "date", "round", "kind", "dir", "entry_time", "entry",
            "level", "exit_time", "exit", "exit_reason", "net", "event"]
    with open(f"{OUT}/newstrat_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(ts, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t.get(c, "") for c in cols})

# ---------------- LADDER ----------------
STEP = 0.004
def band(price, anchor):
    return math.floor(math.log(price / anchor) / math.log(1 + STEP))

def sim_ladder(bars, cap, exit_mode):
    n = len(bars)
    sq_i = next((i for i, b in enumerate(bars) if b["time"] == SQ), n - 1)
    if sq_i < 8: return []
    anchor = bars[0]["open"]
    bhi = max(band(b["close"], anchor) for b in bars if b["time"] < TRIG_FROM)
    blo = min(band(b["close"], anchor) for b in bars if b["time"] < TRIG_FROM)
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i <= sq_i:
        b = bars[i]
        cb = band(b["close"], anchor)
        if cb > bhi: bhi = cb
        if cb < blo: blo = cb
        if b["time"] > LAST_ENTRY or (cap is not None and len(trades) >= cap): break
        # entry check uses band extremes BEFORE this bar: recompute from bhi/blo history is
        # handled by checking against previous extremes stored before update -> use prev vars
        i += 1
    # NOTE: the loop above only tracks extremes; entries handled in sim_ladder2
    return trades

def sim_ladder2(bars, cap, exit_mode):
    n = len(bars)
    sq_i = next((i for i, b in enumerate(bars) if b["time"] == SQ), n - 1)
    if sq_i < 8: return []
    anchor = bars[0]["open"]
    seed = [b for b in bars if b["time"] < TRIG_FROM] or bars[:6]
    if not seed: return []
    bhi = max(band(b["close"], anchor) for b in seed)
    blo = min(band(b["close"], anchor) for b in seed)
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i <= sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        cb = band(b["close"], anchor)
        sign = 0; eband = None
        if cb > bhi: sign, eband = 1, cb
        elif cb < blo: sign, eband = -1, cb
        # update day band extremes with this close regardless
        bhi = max(bhi, cb); blo = min(blo, cb)
        if sign == 0:
            i += 1; continue
        entry = b["close"]
        if exit_mode == "trail":
            xp, xi, reason = H.exit_trail(bars, i, sign, entry, sq_i)
        elif exit_mode in ("wide", "widetrail"):
            if exit_mode == "widetrail":
                xp, xi, reason = H.exit_trail(bars, i, sign, entry, sq_i, act=0.010, dist=0.005, istop=0.010)
            else:
                stop = entry * (1 - 0.010 * sign); xp = xi = reason = None
                for j in range(i + 1, sq_i + 1):
                    bj = bars[j]
                    if sign > 0 and bj["low"] <= stop:
                        xp, xi, reason = (bj["open"] if bj["open"] < stop else stop), j, "stop"; break
                    if sign < 0 and bj["high"] >= stop:
                        xp, xi, reason = (bj["open"] if bj["open"] > stop else stop), j, "stop"; break
                    if j == sq_i: xp, xi, reason = bj["close"], j, "squareoff"
                if xp is None: xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        else:  # grid retrace + hard stop -0.6%
            stop = entry * (1 - 0.006 * sign); xp = xi = reason = None
            for j in range(i + 1, sq_i + 1):
                bj = bars[j]
                if sign > 0 and bj["low"] <= stop:
                    xp, xi, reason = (bj["open"] if bj["open"] < stop else stop), j, "stop"; break
                if sign < 0 and bj["high"] >= stop:
                    xp, xi, reason = (bj["open"] if bj["open"] > stop else stop), j, "stop"; break
                bj_band = band(bj["close"], anchor)
                if sign > 0 and bj_band <= eband - 2:
                    xp, xi, reason = bj["close"], j, "grid_retrace"; break
                if sign < 0 and bj_band >= eband + 2:
                    xp, xi, reason = bj["close"], j, "grid_retrace"; break
                if j == sq_i:
                    xp, xi, reason = bj["close"], j, "squareoff"
            if xp is None:
                xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_time": b["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "ladder", "level": eband})
        # extremes continue from exit bar onward (closes after exit update in main loop)
        i = xi + 1
        # refresh extremes with closes of bars we skipped during the position
        for k in range(i, min(i + 0, n)): pass
        # recompute extremes up to current bar from all closes so far today
        upto = [x for x in bars[:i] if x["time"] >= "09:15"]
        if upto:
            bhi = max(bhi, max(band(x["close"], anchor) for x in upto))
            blo = min(blo, min(band(x["close"], anchor) for x in upto))
    return trades

# ---------------- SNAP ----------------
def sim_snap(bars, cap, mode):
    n = len(bars)
    sq_i = next((i for i, b in enumerate(bars) if b["time"] == SQ), n - 1)
    if sq_i < 10: return []
    trades = []
    start = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), 6)
    i = max(start, 6)
    while i <= sq_i:
        if bars[i]["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        prior = bars[:i]
        sap = sum((x["high"] + x["low"] + x["close"]) / 3 for x in prior) / len(prior)
        rng = sum(x["high"] - x["low"] for x in prior) / len(prior)
        b = bars[i]
        stretch = 0; extreme = None
        if b["high"] >= sap * 1.012 and (b["high"] - b["low"]) >= 1.5 * rng:
            stretch, extreme = 1, b["high"]
        elif b["low"] <= sap * 0.988 and (b["high"] - b["low"]) >= 1.5 * rng:
            stretch, extreme = -1, b["low"]
        if stretch == 0:
            i += 1; continue
        # confirmation: fade = first later bar closing back toward the average;
        # follow (mode f) = first later bar closing beyond the stretch close, in-direction
        j = i + 1; entry = None
        while j <= sq_i and bars[j]["time"] <= "14:30":
            bj = bars[j]
            if mode == "f":
                if stretch > 0 and bj["close"] > bj["open"] and bj["close"] > b["close"]:
                    entry = (j, bj["close"]); break
                if stretch < 0 and bj["close"] < bj["open"] and bj["close"] < b["close"]:
                    entry = (j, bj["close"]); break
            else:
                if stretch > 0 and bj["close"] < bj["open"] and bj["close"] < b["close"]:
                    entry = (j, bj["close"]); break
                if stretch < 0 and bj["close"] > bj["open"] and bj["close"] > b["close"]:
                    entry = (j, bj["close"]); break
            j += 1
        if entry is None:
            i += 1; continue
        ei, ep = entry
        sign = stretch if mode == "f" else -stretch  # follow the surge, or fade it
        if mode == "f":
            xp, xi, reason = H.exit_trail(bars, ei, sign, ep, sq_i)
            net = (xp - ep) * sign * QTY - COST
            trades.append({"entry_time": bars[ei]["time"], "dir": "LONG" if sign > 0 else "SHORT",
                "entry": round(ep, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
                "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
                "kind": "surge_follow", "level": round(extreme, 2)})
            i = xi + 1; continue
        prior_e = bars[:ei]
        sap_e = sum((x["high"] + x["low"] + x["close"]) / 3 for x in prior_e) / len(prior_e)
        stop = extreme * (1 + 0.003 * sign * -1) if sign < 0 else extreme * (1 - 0.003)
        # for SHORT (sign<0): stop above extreme; for LONG: below extreme
        stop = extreme * 1.003 if sign < 0 else extreme * 0.997
        if mode == "a":
            target = ep * (1 + 0.0075 * sign)
        else:
            target = ep - 0.5 * (ep - sap_e) if sign < 0 else ep + 0.5 * (sap_e - ep)
            if abs(target - ep) / ep < 0.004:
                i = ei + 1; continue
        xp = xi = reason = None
        for k in range(ei + 1, sq_i + 1):
            bk = bars[k]
            if sign < 0:
                if bk["high"] >= stop: xp, xi, reason = (bk["open"] if bk["open"] > stop else stop), k, "stop"; break
                if bk["low"] <= target: xp, xi, reason = (bk["open"] if bk["open"] < target else target), k, "target"; break
            else:
                if bk["low"] <= stop: xp, xi, reason = (bk["open"] if bk["open"] < stop else stop), k, "stop"; break
                if bk["high"] >= target: xp, xi, reason = (bk["open"] if bk["open"] > target else target), k, "target"; break
            if k == sq_i: xp, xi, reason = bk["close"], k, "squareoff"
        if xp is None: xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        net = (xp - ep) * sign * QTY - COST
        trades.append({"entry_time": bars[ei]["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(ep, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "snap", "level": round(extreme, 2)})
        i = xi + 1
    return trades

FAMS = {
    "L-a": ("ladder", 6, "grid"), "L-b": ("ladder", 4, "grid"), "L-trail": ("ladder", 6, "trail"),
    "L-c": ("ladder", 6, "wide"), "L-d": ("ladder", 6, "widetrail"),
    "S-a": ("snap", 2, "a"), "S-b": ("snap", 2, "b"), "S-cap4": ("snap", 4, "a"),
    "S-f": ("snap", 2, "f"),
}

def run(fid):
    mech, cap, mode = FAMS[fid]
    ts = []
    for sym in SYMBOLS:
        spot, _ = H.stocks[sym]
        for day in DAYS:
            bars = spot.get(day)
            if not bars or len(bars) < 40: continue
            rows = sim_ladder2(bars, cap, mode) if mech == "ladder" else sim_snap(bars, cap, mode)
            for t in rows:
                t.update({"symbol": sym, "date": day, "family": fid,
                          "event": "event" if day in H.WINDOWS[sym] else "no_event"})
                ts.append(t)
    return ts

if __name__ == "__main__":
    fams = sys.argv[1].split(",")
    results = {}
    if os.path.exists(f"{OUT}/newstrat_results.json"):
        results = json.load(open(f"{OUT}/newstrat_results.json"))
    for fid in fams:
        ts = run(fid); save(fid, ts)
        results[fid] = summarize(fid, ts)
        r = results[fid]
        print(fid, json.dumps(r["all"]), "JM", json.dumps(r["jan_may"]), "JO", json.dumps(r["jun_oct"]),
              "OCT", json.dumps(r["october"]), "per_day", r["per_day"], "breadth_pos", r["breadth"]["pos"], flush=True)
    json.dump(results, open(f"{OUT}/newstrat_results.json", "w"), indent=1)
