#!/usr/bin/env python3
"""ROUND 2 — STAGE 1: POPULATION CAPTURE (cached to r2_cache.pkl).
- F4: parameterised build2 copy (lo/hi/meas), anchored against collect2.
  Captures: @10:00 exits (1.50,0.95) [incumbent], (1.25,0.65), (1.75,0.95),
  (1.50,0.80); @09:45 exits (1.50,0.95). Full signal population (lo=0).
- INV: full run_chain population both years with ADR attached.
- EVENTS: reaction candidates + score_lag at lag 1/2, both directions.
- N4: event-day signal superset (|move| >= 0.5) for variant scoring.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import sys, pickle
from collections import Counter
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L

g = L.load_machinery(L.FULLHIST, "2026-10-28")
DAYCTX = g["DAYCTX"]
below50, pick, replay_plain = g["below50"], g["pick"], g["replay_plain"]
wk = g["wk"]
days25 = sorted({d for (s, d) in DAYCTX if d.startswith("2025")})
days26 = sorted({d for (s, d) in DAYCTX if d.startswith("2026")})
ALLDAYS = days25 + days26
COST = 40.0

AUDIT = {"trades": 0, "violations": 0}

def premove_m(candles, meas):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < meas]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

def build2_p(sym, day, lo, hi, meas, TP, SP):
    """Verbatim copy of validation build2 with (lo, hi, meas) parameterised.
    lo/hi are fractions (hi=None means no upper edge)."""
    ctx = DAYCTX.get((sym, day))
    if ctx is None:
        return []
    if not below50(day):
        return []
    candles = ctx["candles"]
    pm = premove_m(candles, meas)
    if pm is None or pm == 0 or abs(pm) < lo:
        return []
    if hi is not None and abs(pm) >= hi:
        return []
    want = 1 if pm > 0 else -1
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= meas), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = pick(sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = replay_plain(candles, ei, sign, entry, TP, SP)
        AUDIT["trades"] += 1
        if candles[ei]["time"] < meas or candles[idx]["time"] < meas or ei <= idx:
            AUDIT["violations"] += 1
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 6), "meas_time": meas})
        start = xi
    return trades

def collect_p(days, lo, hi, meas, TP, SP):
    out = []
    for sym in g["SYMBOLS"]:
        for day in days:
            out.extend(build2_p(sym, day, lo, hi, meas, TP, SP))
    return out

# ---- F4 anchor: build2_p at frozen settings == collect2 raw ----------------
raw_ref = g["collect2"](ALLDAYS, g["F4_CFG"], 1.50, 0.95)
raw_mine = collect_p(ALLDAYS, 0.005, 0.01, "10:00", 1.50, 0.95)
k = lambda t: (t["date"], t["symbol"], t["dir"], t["entry_time"], round(t["net"], 2))
assert Counter(map(k, raw_ref)) == Counter(map(k, raw_mine)), "F4 build2_p anchor FAILED"
print(f"F4 anchor OK: {len(raw_mine)} raw trades reproduce collect2 exactly; "
      f"audit violations so far: {AUDIT['violations']}")

cache = {}
# ---- F4 populations ---------------------------------------------------------
configs = {
    "f4_1000_T150S095": ("10:00", 1.50, 0.95),
    "f4_1000_T125S065": ("10:00", 1.25, 0.65),
    "f4_1000_T175S095": ("10:00", 1.75, 0.95),
    "f4_1000_T150S080": ("10:00", 1.50, 0.80),
    "f4_0945_T150S095": ("09:45", 1.50, 0.95),
}
for name, (meas, TP, SP) in configs.items():
    rows = collect_p(ALLDAYS, 0.0, None, meas, TP, SP)
    cache[name] = rows
    print(f"{name}: {len(rows)} raw trades (direct "
          f"{sum(1 for t in rows if t['leg'] == 'direct')})")

# ---- INV chain population ---------------------------------------------------
rows = []
for sym in g["SYMBOLS"]:
    for day in ALLDAYS:
        rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
        for r in rs:
            r["adr"] = g["ADR"].get((sym, day))
        rows.extend(rs)
cache["inv_pop"] = [{kk: r[kk] for kk in ("date", "stock", "direction", "setup",
                                          "round", "entry_time", "entry",
                                          "exit_price", "net", "adr",
                                          "event_status")} for r in rows]
print(f"inv_pop: {len(rows)} chain rows")

# ---- EVENTS: reaction candidates + lag scores, both directions --------------
CAL25 = f"{WS}/stock_event_calendar_2025.csv"
CAL26 = f"{WS}/stock_event_calendar_jan_oct_2026.csv"
ev = {}
for yr, cal, lo, hi in ((2025, CAL25, "2025-01-01", "2025-12-31"),
                        (2026, CAL26, "2026-01-01", "2026-10-28")):
    cands = g["reaction_candidates"](cal, lo, hi)
    scored = {}
    for lag in (1, 2):
        for flip in (False, True):
            out = []
            for c in cands:
                cc = dict(c)
                if flip:
                    cc["direction"] = "SHORT" if c["direction"] == "LONG" else "LONG"
                t = g["score_lag"](cc, lag)
                if t:
                    out.append(t)
            scored[(lag, flip)] = out
    ev[yr] = {"cands": cands, "scored": scored}
    print(f"events {yr}: {len(cands)} candidates; lag1 {len(scored[(1, False)])}, "
          f"lag2 {len(scored[(2, False)])}")
cache["events"] = ev

# ---- N4 signal superset ------------------------------------------------------
STOCKS_E = g["STOCKS_E"]
NIFTY_DAILY_E = g["NIFTY_DAILY_E"]
SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
               "block_deal", "sector_policy", "pricing", "corporate_action"}
import csv as _csv
def n4_signals(cal_path, lo, hi):
    combined = {s: set() for s in g["SYMBOLS"]}
    with open(cal_path) as f:
        for r in _csv.DictReader(f):
            sym = r["stock"]
            if sym not in combined: continue
            et = r["event_type"]
            if et != "results" and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            evd = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and evd <= react <= evd + timedelta(days=7)) else evd
            ds = eff.isoformat()
            if lo <= ds <= hi: combined[sym].add(ds)
    all_days = sorted(d["date"] for d in NIFTY_DAILY_E if lo <= d["date"] <= hi)
    out = []
    for sym in g["SYMBOLS"]:
        spot, daily = STOCKS_E[sym]
        dmap = {d["date"]: i for i, d in enumerate(daily)}
        for day in all_days:
            if day not in combined[sym]: continue
            if day not in dmap or dmap[day] == 0: continue
            raw = spot.get(day, [])
            if not raw: continue
            prev_close = daily[dmap[day] - 1]["close"]
            if not prev_close: continue
            by_time = {c["time"]: c for c in raw}
            b0925 = by_time.get("09:25")
            if b0925 is None: continue
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= 0.5:
                out.append({"symbol": sym, "date": day,
                            "move_pct": round(move_pct, 4),
                            "direction": "LONG" if move_pct > 0 else "SHORT"})
    return out

cache["n4_signals"] = {2025: n4_signals(CAL25, "2025-01-01", "2025-12-31"),
                       2026: n4_signals(CAL26, "2026-01-01", "2026-10-28")}
print(f"n4 signals: 2025 {len(cache['n4_signals'][2025])}, "
      f"2026 {len(cache['n4_signals'][2026])} (|move|>=0.5 superset)")

with open(f"{WS}/r2_cache.pkl", "wb") as f:
    pickle.dump(cache, f)
print("cache written: r2_cache.pkl; total audit violations:", AUDIT["violations"])
