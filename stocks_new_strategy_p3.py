#!/usr/bin/env python3
"""PART 3 — EX-ANTE ADAPTATION vs the drift flip.
Spec: stocks_new_strategy_frozen.md (Part 3 section, frozen before scoring).
Equity cash intraday, LONG/SHORT, paper only. Per 100 shares provisional,
Rs40/trade. No calendar-month logic anywhere: drift uses trailing daily
windows ending the previous trading day; RS uses same-day data up to the
ranking bar only.

D1/D1b = post-filter gate on the frozen Part 2 V3 trade set (direction must
match the sign of the stock's trailing-N-day intraday drift).
D2     = in-stream drift-follow ladder: V3's sim re-run with entries
         generated only in the drift_20 direction (blocked signals never
         consume a position slot, unlike the D1 post-filter).
X1     = cross-sectional relative strength (10:30 / 13:00 rankings).
X2     = X1 + volume-pace >= 1.0x gate.
"""
import csv, json, math, os, statistics, sys
from collections import defaultdict

OUT = "/home/hatch/workspace/trading"
sys.path.insert(0, OUT)
import stocks_new_strategy_vol as V   # loads hunt1 (DAYS/WINDOWS), VOLDATA, vr
import stocks_hunt1 as H

SYMBOLS = V.SYMBOLS; DAYS = V.DAYS; WINDOWS = V.WINDOWS; VOLDATA = V.VOLDATA
QTY, COST = 100, 40.0
SQ, LAST_ENTRY, TRIG_FROM = V.SQ, V.LAST_ENTRY, V.TRIG_FROM
vr = V.vr

# ---------------- trailing intraday drift ----------------
DAILY = {s: H.stocks[s][1] for s in SYMBOLS}          # sorted daily rows, all dates in file
DIDX = {s: {d["date"]: i for i, d in enumerate(DAILY[s])} for s in SYMBOLS}

def drift(sym, day, n):
    """Mean (close-open)/open over the n trading days of sym before `day`.
    None if day unknown for sym or fewer than n prior days."""
    i = DIDX[sym].get(day)
    if i is None or i < n: return None
    rows = DAILY[sym][i - n:i]
    return sum((d["close"] - d["open"]) / d["open"] for d in rows) / n

def drift_sign(sym, day, n):
    d = drift(sym, day, n)
    if d is None or d == 0: return 0
    return 1 if d > 0 else -1

# ---------------- D2: in-stream drift-follow ladder (V3 sim + direction rule) ----------------
STEP = 0.004
def band(price, anchor):
    return math.floor(math.log(price / anchor) / math.log(1 + STEP))

def sim_ladder_drift(bars, dsign, vol_mult=1.5, cap=6):
    """Verbatim copy of Part 2 sim_v3, plus: if dsign is not None, an entry is
    taken only when its sign == dsign (dsign 0 -> no entries). Gate-off
    (dsign None) must reproduce V3 exactly."""
    sq_i = V.sq_index(bars)
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
        bhi = max(bhi, cb); blo = min(blo, cb)
        if sign == 0:
            i += 1; continue
        if dsign is not None and sign != dsign:
            i += 1; continue
        r = vr(bars, i)
        if r is None or r < vol_mult:
            i += 1; continue
        entry = b["close"]
        stop = entry * (1 - 0.010 * sign); xp = xi = reason = None
        for j in range(i + 1, sq_i + 1):
            bj = bars[j]
            if sign > 0 and bj["low"] <= stop:
                xp, xi, reason = (bj["open"] if bj["open"] < stop else stop), j, "stop"; break
            if sign < 0 and bj["high"] >= stop:
                xp, xi, reason = (bj["open"] if bj["open"] > stop else stop), j, "stop"; break
            if j == sq_i: xp, xi, reason = bj["close"], j, "squareoff"
        if xp is None: xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_time": b["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "ladder_drift", "level": eband, "vr": round(r, 2)})
        i = xi + 1
        upto = [x for x in bars[:i]]
        if upto:
            bhi = max(bhi, max(band(x["close"], anchor) for x in upto))
            blo = min(blo, min(band(x["close"], anchor) for x in upto))
    return trades

def run_ladder(fid, dsign_fn):
    all_trades = []
    for sym in SYMBOLS:
        for day in DAYS:
            bars = VOLDATA[sym].get(day)
            if not bars or len(bars) < 40: continue
            ds = dsign_fn(sym, day)
            for t in sim_ladder_drift(bars, ds):
                t.update({"symbol": sym, "date": day, "family": fid,
                          "event": "event" if day in WINDOWS[sym] else "no_event"})
                all_trades.append(t)
    return all_trades

# ---------------- D1: post-filter on frozen V3 trades ----------------
def load_v3_trades():
    ts = []
    with open(f"{OUT}/newstratvol_V3_trades.csv") as f:
        for r in csv.DictReader(f):
            ts.append({"symbol": r["symbol"], "date": r["date"], "round": int(r["round"]),
                       "kind": r["kind"], "dir": r["dir"], "entry_time": r["entry_time"],
                       "entry": float(r["entry"]), "level": r["level"], "vr": r["vr"],
                       "exit_time": r["exit_time"], "exit": float(r["exit"]),
                       "exit_reason": r["exit_reason"], "net": float(r["net"]),
                       "event": r["event"]})
    return ts

def d1_filter(n):
    kept, dropped = [], []
    for t in load_v3_trades():
        ds = drift_sign(t["symbol"], t["date"], n)
        want = 1 if t["dir"] == "LONG" else -1
        t2 = dict(t); t2["drift"] = drift(t["symbol"], t["date"], n)
        (kept if ds == want else dropped).append(t2)
    return kept, dropped

# ---------------- X1 / X2: cross-sectional relative strength ----------------
def bar_at(bars, time):
    for i, b in enumerate(bars):
        if b["time"] == time: return i
    return None

# volume pace: cumulative volume 09:15..ranking bar (inclusive), per stock-day
PACE_CACHE = {}
def cumvol_series(sym):
    if sym in PACE_CACHE: return PACE_CACHE[sym]
    days_sorted = sorted(VOLDATA[sym].keys())
    out = {}
    for d in days_sorted:
        bars = VOLDATA[sym][d]
        c10 = sum(b["volume"] for b in bars if b["time"] <= "10:30")
        c13 = sum(b["volume"] for b in bars if b["time"] <= "13:00")
        out[d] = (c10, c13)
    res = (days_sorted, out)
    PACE_CACHE[sym] = res
    return res

def pace(sym, day, which):
    """which 0 -> through 10:30 bar; 1 -> through 13:00 bar.
    Ratio vs mean of same window over prior 20 volume days. None if <20 prior."""
    days_sorted, out = cumvol_series(sym)
    if day not in out: return None
    k = days_sorted.index(day)
    if k < 20: return None
    prior = [out[days_sorted[j]][which] for j in range(k - 20, k)]
    m = sum(prior) / 20
    if m <= 0: return None
    return out[day][which] / m

def exit_x(bars, ei, sign, entry, sq_i, mode):
    if mode == "T10":
        stop = entry * (1 - 0.005 * sign); target = entry * (1 + 0.010 * sign)
        for j in range(ei, sq_i + 1):
            b = bars[j]
            if sign > 0:
                if b["low"] <= stop: return (b["open"] if (j > ei and b["open"] < stop) else stop), j, "stop"
                if b["high"] >= target: return (b["open"] if (j > ei and b["open"] > target) else target), j, "target"
            else:
                if b["high"] >= stop: return (b["open"] if (j > ei and b["open"] > stop) else stop), j, "stop"
                if b["low"] <= target: return (b["open"] if (j > ei and b["open"] < target) else target), j, "target"
            if j == sq_i: return b["close"], j, "squareoff"
    else:  # HOLD: -1.0% disaster stop, else 15:10 close
        stop = entry * (1 - 0.010 * sign)
        for j in range(ei, sq_i + 1):
            b = bars[j]
            if sign > 0 and b["low"] <= stop:
                return (b["open"] if (j > ei and b["open"] < stop) else stop), j, "stop"
            if sign < 0 and b["high"] >= stop:
                return (b["open"] if (j > ei and b["open"] > stop) else stop), j, "stop"
            if j == sq_i: return b["close"], j, "squareoff"
    b = bars[sq_i]; return b["close"], sq_i, "squareoff"

def run_x(mode, use_pace):
    """mode in {T10, HOLD}; use_pace True -> X2. Returns trade list."""
    all_trades = []
    for day in DAYS:
        traded = set()
        for setno, (rank_t, entry_t, which) in enumerate(
                [("10:30", "10:35", 0), ("13:00", "13:05", 1)], start=1):
            cands = []
            for sym in SYMBOLS:
                if sym in traded: continue
                bars = VOLDATA[sym].get(day)
                if not bars or len(bars) < 40: continue
                ri = bar_at(bars, rank_t); ei = bar_at(bars, entry_t)
                oi = bar_at(bars, "09:15")
                if ri is None or ei is None or oi is None: continue
                r = bars[ri]["close"] / bars[oi]["open"] - 1
                cands.append((r, sym, bars, ei))
            if not cands: continue
            cands.sort(key=lambda x: x[0])
            picks = [(c, 1) for c in cands[-3:] if c[0] >= 0.005] + \
                    [(c, -1) for c in cands[:3] if c[0] <= -0.005]
            sq_cache = {}
            for (r, sym, bars, ei), sign in picks:
                p = None
                if use_pace:
                    p = pace(sym, day, which)
                    if p is None or p < 1.0: continue
                sq_i = V.sq_index(bars)
                entry = bars[ei]["open"]
                xp, xi, reason = exit_x(bars, ei, sign, entry, sq_i, mode)
                net = (xp - entry) * sign * QTY - COST
                all_trades.append({"symbol": sym, "date": day,
                    "family": ("X2" if use_pace else "X1") + mode,
                    "round": setno, "kind": "rs_vol" if use_pace else "rs",
                    "dir": "LONG" if sign > 0 else "SHORT",
                    "entry_time": bars[ei]["time"], "entry": round(entry, 2),
                    "level": round(r * 100, 3), "exit_time": bars[xi]["time"],
                    "exit": round(xp, 2), "exit_reason": reason, "net": round(net, 2),
                    "event": "event" if day in WINDOWS[sym] else "no_event",
                    "pace": (round(p, 3) if p is not None else "")})
                traded.add(sym)
    return all_trades

# ---------------- metrics / summarize ----------------
def metrics(ts):
    if not ts: return {"trades": 0, "net": 0.0, "win_pct": 0.0, "exp": 0.0, "gross_exp": 0.0}
    net = sum(t["net"] for t in ts); wins = sum(1 for t in ts if t["net"] > 0)
    return {"trades": len(ts), "net": round(net, 2), "win_pct": round(100 * wins / len(ts), 1),
            "exp": round(net / len(ts), 2), "gross_exp": round(net / len(ts) + COST, 2)}

def split(ts, a, b): return [t for t in ts if a <= t["date"] <= b]
JM = ("2026-01-01", "2026-05-31"); JO = ("2026-06-01", "2026-10-28"); OCT = ("2026-10-01", "2026-10-28")

def summarize(fid, ts):
    s = {"family": fid, "all": metrics(ts),
         "jan_may": metrics(split(ts, *JM)), "jun_oct": metrics(split(ts, *JO)),
         "october": metrics(split(ts, *OCT)),
         "per_day": round(len(ts) / len(DAYS), 2),
         "long_jm": metrics([t for t in split(ts, *JM) if t["dir"] == "LONG"]),
         "long_jo": metrics([t for t in split(ts, *JO) if t["dir"] == "LONG"]),
         "short_jm": metrics([t for t in split(ts, *JM) if t["dir"] == "SHORT"]),
         "short_jo": metrics([t for t in split(ts, *JO) if t["dir"] == "SHORT"]),
         "long": metrics([t for t in ts if t["dir"] == "LONG"]),
         "short": metrics([t for t in ts if t["dir"] == "SHORT"]),
         "event": metrics([t for t in ts if t["event"] == "event"]),
         "no_event": metrics([t for t in ts if t["event"] == "no_event"]),
         "set1": metrics([t for t in ts if t.get("round") == 1]),
         "set2": metrics([t for t in ts if t.get("round") == 2]),
         "rounds": {str(r): metrics([t for t in ts if t.get("round") == r]) for r in (1, 2, 3, 4)}}
    by_stock = defaultdict(list)
    for t in ts: by_stock[t["symbol"]].append(t)
    sm = sorted(((metrics(v)["net"], k, metrics(v)["trades"]) for k, v in by_stock.items()), reverse=True)
    tot = s["all"]["net"]
    s["top_stocks"] = sm[:5]; s["bottom_stocks"] = sm[-5:]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": 25,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None,
                    "per_stock": {k: metrics(v)["net"] for k, v in by_stock.items()}}
    return s

def save_trades(fid, ts):
    if not ts: return
    cols = ["family", "symbol", "date", "round", "kind", "dir", "entry_time", "entry",
            "level", "vr", "exit_time", "exit", "exit_reason", "net", "event", "drift", "pace"]
    with open(f"{OUT}/newstratp3_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(ts, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t.get(c, "") for c in cols})

if __name__ == "__main__":
    results = {}
    if os.path.exists(f"{OUT}/newstratp3_results.json"):
        results = json.load(open(f"{OUT}/newstratp3_results.json"))
    which = sys.argv[1].split(",") if len(sys.argv) > 1 else \
        ["VALIDATE", "D1", "D1b", "D2", "X1T10", "X1HOLD", "X2T10", "X2HOLD"]
    for fid in which:
        if fid == "VALIDATE":
            ts = run_ladder("V3R", lambda s, d: None)
            m = metrics(ts)
            print("VALIDATE gate-off reproduction of V3:", json.dumps(m),
                  "expected: trades 3275, net -16284.0", flush=True)
            results["VALIDATE"] = {"reproduction": m,
                                   "expected": {"trades": 3275, "net": -16284.0}}
        elif fid in ("D1", "D1b"):
            n = 20 if fid == "D1" else 10
            kept, dropped = d1_filter(n)
            for t in kept + dropped: t["family"] = fid
            save_trades(fid, kept)
            results[fid] = summarize(fid, kept)
            results[fid + "_dropped"] = summarize(fid + "_dropped", dropped)
            r = results[fid]
            print(fid, "KEPT", json.dumps(r["all"]), "JM", json.dumps(r["jan_may"]),
                  "JO", json.dumps(r["jun_oct"]), "OCT", json.dumps(r["october"]),
                  "breadth", r["breadth"]["stocks_positive"],
                  "| DROPPED JM", json.dumps(results[fid + "_dropped"]["jan_may"]),
                  "JO", json.dumps(results[fid + "_dropped"]["jun_oct"]), flush=True)
        elif fid == "D2":
            ts = run_ladder("D2", lambda s, d: drift_sign(s, d, 20))
            save_trades("D2", ts)
            results["D2"] = summarize("D2", ts)
            r = results["D2"]
            print("D2", json.dumps(r["all"]), "JM", json.dumps(r["jan_may"]),
                  "JO", json.dumps(r["jun_oct"]), "OCT", json.dumps(r["october"]),
                  "breadth", r["breadth"]["stocks_positive"], flush=True)
        elif fid.startswith("X"):
            mode = "T10" if fid.endswith("T10") else "HOLD"
            ts = run_x(mode, fid.startswith("X2"))
            save_trades(fid, ts)
            results[fid] = summarize(fid, ts)
            r = results[fid]
            print(fid, json.dumps(r["all"]), "JM", json.dumps(r["jan_may"]),
                  "JO", json.dumps(r["jun_oct"]), "OCT", json.dumps(r["october"]),
                  "per_day", r["per_day"], "breadth", r["breadth"]["stocks_positive"], flush=True)
    json.dump(results, open(f"{OUT}/newstratp3_results.json", "w"), indent=1)
