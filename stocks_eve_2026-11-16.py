#!/usr/bin/env python3
"""Stocks evening engine 2026-11-16 — SCORE-ONLY per owner settlement 2026-11-13.
Part A only: candle-verified detail for today's Stock Book trades + scorecards + shadows.
No tuning candidates (owner: 'Keep whatever is running... Let it run'; engines score-only).
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade.
"""
import csv, json, pathlib
WS = pathlib.Path.home() / "workspace/trading"
FWD = WS / "data/sarvaritu_fwd"
COST = 40.0

def bars(root, sym, day):
    out = []
    p = root / sym / "spot_5m.csv"
    if not p.exists():
        return out
    for r in csv.DictReader(open(p)):
        if r["timestamp"][:10] == day:
            out.append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                        float(r["low"]), float(r["close"])))
    return sorted(out)

def scan(bars_, entry_time, entry, stop, target, direction):
    started = False
    mfe = mae = None
    for t, o, h, l, c in bars_:
        if t == entry_time:
            started = True
            continue
        if t < entry_time or not started or t > "15:10":
            continue
        if direction == "LONG":
            fav = (h - entry) * 100; adv = (l - entry) * 100
        else:
            fav = (entry - l) * 100; adv = (entry - h) * 100
        mfe = fav if mfe is None else max(mfe, fav)
        mae = adv if mae is None else min(mae, adv)
        if direction == "LONG":
            if l <= stop: return t, stop, "stop", mfe, mae
            if h >= target: return t, target, "target", mfe, mae
        else:
            if h >= stop: return t, stop, "stop", mfe, mae
            if l <= target: return t, target, "target", mfe, mae
        if t == "15:10":
            return t, c, "square_off", mfe, mae
    return None, None, "no_exit", mfe, mae

def net_of(entry, exit_price, direction):
    if direction == "LONG":
        return round((exit_price - entry) * 100 - COST, 2)
    return round((entry - exit_price) * 100 - COST, 2)

def levels(entry, direction, stop_pct, tgt_pct):
    if direction == "LONG":
        return round(entry * (1 - stop_pct), 2), round(entry * (1 + tgt_pct), 2)
    return round(entry * (1 + stop_pct), 2), round(entry * (1 - tgt_pct), 2)

print("="*70)
TRADES = [
    ("P2F/book+scorecard T125S050", "IRCTC", "SHORT", "09:15", 456.20, 0.0050, 0.0125, 530.25),
    ("P2F/scorecard-only T125S050", "BDL", "SHORT", "09:15", 1030.00, 0.0050, 0.0125, -555.00),
]
for label, sym, d, et, entry, sp, tp, logged in TRADES:
    b = bars(FWD, sym, "2026-11-16")
    stop, tgt = levels(entry, d, sp, tp)
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    print(json.dumps({"label": label, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": net_of(entry, xp, d) if xp else None,
                      "net_logged": logged,
                      "mfe_rs": round(mfe,2) if mfe is not None else None,
                      "mae_rs": round(mae,2) if mae is not None else None,
                      "nbars": len(b)}))
    # T10 shadow
    stop10, tgt10 = levels(entry, d, sp, 0.0100)
    xt10, xp10, xr10, mfe10, mae10 = scan(b, et, entry, stop10, tgt10, d)
    print(json.dumps({"label": label+" T10", "exit_time": xt10, "exit_price": xp10, "exit_reason": xr10,
                      "net_recomputed": net_of(entry, xp10, d) if xp10 else None}))

for sym in ("IRCTC","BDL","OIL"):
    b = bars(FWD, sym, "2026-11-16")
    if b:
        print(json.dumps({sym+"_day": {"open": b[0][1], "high": max(x[2] for x in b),
                                       "low": min(x[3] for x in b),
                                       "close_1510": [x[4] for x in b if x[0]=="15:10"][0] if any(x[0]=="15:10" for x in b) else None,
                                       "nbars": len(b),
                                       "bar_0915": b[0], "bar_0925": [x for x in b if x[0]=="09:25"][:1],
                                       "bar_0945": [x for x in b if x[0]=="09:45"][:1]}}))
print("SCORE-ONLY: no Part B — no candidate gated tonight per owner settlement 2026-11-13.")
