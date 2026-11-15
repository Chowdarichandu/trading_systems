#!/usr/bin/env python3
"""Stocks evening engine 2026-11-13 — SCORE-ONLY per owner settlement 2026-11-13.
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

# First: discover ASTRAL book entry = 09:40 bar open in fwd candles
for sym in ("IRCTC","ASTRAL","BDL","HINDCOPPER","OIL"):
    b = bars(FWD, sym, "2026-11-13")
    print(json.dumps({sym+"_bars": len(b), sym+"_first": b[0] if b else None,
                      sym+"_0940": [x for x in b if x[0]=="09:40"][:1],
                      sym+"_0935": [x for x in b if x[0]=="09:35"][:1]}))

print("="*70)
TRADES = [
    ("N4-V3/book T150S080", "IRCTC", "SHORT", "09:35", 460.40, 0.0080, 0.0150, 230.00),
    ("N4-V3/scorecard T125S050", "IRCTC", "SHORT", "09:35", 460.40, 0.0050, 0.0125, -270.20),
    ("N4-V3/scorecard T125S050", "BDL", "SHORT", "09:35", 1044.80, 0.0050, 0.0125, -562.40),
    ("P2F/scorecard T125S050", "HINDCOPPER", "LONG", "09:15", 443.90, 0.0050, 0.0125, -262.00),
]
for label, sym, d, et, entry, sp, tp, logged in TRADES:
    b = bars(FWD, sym, "2026-11-13")
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

# ASTRAL INV-ABOVE: entry = 09:40 open from fwd; geometry T125/S050, logged net -677.80, logged exit 1269.22
b = bars(FWD, "ASTRAL", "2026-11-13")
if b:
    e940 = [x for x in b if x[0]=="09:40"]
    if e940:
        entry = e940[0][1]
        stop, tgt = levels(entry, "LONG", 0.0050, 0.0125)
        xt, xp, xr, mfe, mae = scan(b, "09:40", entry, stop, tgt, "LONG")
        print(json.dumps({"label":"INV-ABOVE/book T125S050","stock":"ASTRAL","dir":"LONG","entry_time":"09:40",
                          "entry":entry,"stop":stop,"target":tgt,"exit_time":xt,"exit_price":xp,"exit_reason":xr,
                          "net_recomputed": net_of(entry, xp, "LONG") if xp else None,"net_logged":-677.80,
                          "mfe_rs": round(mfe,2) if mfe is not None else None,
                          "mae_rs": round(mae,2) if mae is not None else None,"nbars":len(b)}))
for sym in ("IRCTC","ASTRAL","BDL","HINDCOPPER","OIL"):
    b = bars(FWD, sym, "2026-11-13")
    if b:
        print(json.dumps({sym+"_day": {"open": b[0][1], "high": max(x[2] for x in b),
                                       "low": min(x[3] for x in b),
                                       "close_1510": [x[4] for x in b if x[0]=="15:10"][0] if any(x[0]=="15:10" for x in b) else None,
                                       "nbars": len(b)}}))
print("SCORE-ONLY: no Part B — no candidate gated tonight per owner settlement 2026-11-13.")
