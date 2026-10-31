#!/usr/bin/env python3
"""ENGINE SAT-32 DIAGNOSIS: P2F-LOWBAND candidate build -- the reaction
band's lower complement [2.0%, 2.5%), entered at the R+1 open in the
reaction direction, exits T125/S050 (the book's P2F exits), RF-1,
P2F's mechanism-scoped exclusions (ASTRAL, HINDUNILVR whole-name;
HINDALCO LONG). Machinery = the SAT-13/SAT-16 event machinery
(verbatim), lag +1.
CONSTRUCTION ANCHOR (before any lowband number is believed): the same
machinery at the incumbent band (>=2.5%, lag +1) must reproduce the
tuning dump's P2F leg (stocks_tuning_event_V1_combined_trades.csv)
per-trade; the replay start-offset convention is determined
empirically (offsets 0 and 1 both tried, the reproducing one used).
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
import csv, sys, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
from datetime import date, timedelta

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

DATA = f"{BASE}/data/progressive"
SYMBOLS = M1.HOME25
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{DATA}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append(
                {"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                 "open": float(r["open"]), "high": float(r["high"]),
                 "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{DATA}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]),
                          "high": float(r["high"]), "low": float(r["low"]),
                          "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

stocks = {s: load_stock(s) for s in SYMBOLS}

def replay(candles, entry, direction, tgt_pct, stp_pct, start):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(start, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
    if last is not None:
        return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * QTY - COST, 2)

# ---------- candidate set (verbatim SAT-16 event logic) ----------
events = []
with open(f"{BASE}/stock_event_calendar_jan_oct_2026.csv") as f:
    for r in csv.DictReader(f):
        if r["event_type"] != "results" or r["stock"] not in SYMBOLS: continue
        ev = date.fromisoformat(r["event_date"][:10])
        react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
        ds = eff.isoformat()
        if ALL_LO <= ds <= ALL_HI:
            events.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
events.sort(key=lambda e: (e["symbol"], e["R"]))

cands_ge25, cands_low = [], []
for e in events:
    sym, R = e["symbol"], e["R"]
    spot, daily = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if R not in didx: continue
    ri = didx[R]
    if ri == 0 or ri + 1 >= len(daily): continue
    reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
    nd = daily[ri + 1]["date"]
    if nd > ALL_HI: continue
    if not spot.get(nd): continue
    c = {"symbol": sym, "announce": e["announce"], "R": R,
         "reaction_ret_pct": reaction_ret, "ri": ri,
         "direction": "LONG" if reaction_ret > 0 else "SHORT"}
    if abs(reaction_ret) >= 2.5: cands_ge25.append(c)
    elif abs(reaction_ret) >= 2.0: cands_low.append(c)
print(f"candidates: >=2.5% band {len(cands_ge25)} (SAT-16 record: 39) | "
      f"[2.0,2.5) lowband {len(cands_low)}")

def score_lag1(cand, start, flip=False):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    d1 = daily[cand["ri"] + 1]["date"]
    bars = spot.get(d1, [])
    if not bars: return None
    direction = cand["direction"]
    if flip: direction = "SHORT" if direction == "LONG" else "LONG"
    entry = bars[0]["open"]
    r = replay(bars, entry, direction, 1.25, 0.5, start)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d1, "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"P2F-LOWBAND reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

# ---------- construction anchor vs the tuning dump's P2F leg ----------
# The dump's P2F leg holds 48 rows: 39 at >=2.5% + exactly 9 in
# [2.0%, 2.5%). The machinery must reproduce BOTH slices per-trade --
# the lowband slice itself is thereby verified against the audited
# tuning dump, not just its >=2.5% sibling.
dump = {}
for r in rd("stocks_tuning_event_V1_combined_trades.csv"):
    if r["leg"] == "P2F":
        dump[(r["date"], r["symbol"], r["direction"])] = (
            round(float(r["net_rs"]), 2), r["exit_reason"])

def matches(built):
    return sum(1 for t in built
               if dump.get((t["date"], t["symbol"], t["direction"]),
                           (None, None))[0] is not None
               and abs(dump[(t["date"], t["symbol"], t["direction"])][0]
                       - t["net_rs"]) < 0.011
               and dump[(t["date"], t["symbol"], t["direction"])][1]
               == t["exit_reason"])

conv = None
for start in (1, 0):
    b25 = [t for t in (score_lag1(c, start) for c in cands_ge25) if t]
    blow = [t for t in (score_lag1(c, start) for c in cands_low) if t]
    m25, mlow = matches(b25), matches(blow)
    print(f"construction anchor, replay start={start}: >=2.5% {m25}/"
          f"{len(b25)} | lowband {mlow}/{len(blow)} (dump P2F rows "
          f"{len(dump)})")
    if m25 == len(b25) == 39 and mlow == len(blow) == 9: conv = start
assert conv is not None, "CONSTRUCTION ANCHOR FAILED -- machinery unverified"
print(f"CONSTRUCTION ANCHOR OK: machinery reproduces the tuning dump's "
      f"P2F leg exactly on BOTH band slices (start={conv})")

# ---------- lowband build (follow + placebo), frozen filters ----------
def build(cands, flip=False):
    raw = [t for t in (score_lag1(c, conv, flip=flip) for c in cands) if t]
    kept = [t for t in raw
            if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]
    return raw, kept

low_raw, low = build(cands_low)
pl_raw, pl = build(cands_low, flip=True)
print(f"lowband: raw {len(low_raw)} -> frozen {len(low)} | placebo raw "
      f"{len(pl_raw)} -> frozen {len(pl)}")

def stats(trades):
    months = defaultdict(float)
    for t in trades: months[t["date"][:7]] += t["net_rs"]
    per = defaultdict(float)
    for t in trades: per[t["symbol"]] += t["net_rs"]
    tot = round(sum(t["net_rs"] for t in trades), 2)
    return {"trades": len(trades), "net": tot,
            "exp": round(tot / len(trades), 2) if trades else None,
            "win": sum(1 for t in trades if t["net_rs"] > 0),
            "breadth": sum(1 for v in per.values() if v > 0),
            "h1": round(sum(t["net_rs"] for t in trades
                            if t["date"] <= "2026-05-31"), 2),
            "h2": round(sum(t["net_rs"] for t in trades
                            if t["date"] > "2026-05-31"), 2),
            "months": {k: round(months.get(k, 0.0), 2)
                       for k in sorted({f"2026-{i:02d}" for i in range(1, 11)})},
            "per_stock": {k: round(v, 2) for k, v in
                          sorted(per.items(), key=lambda kv: -kv[1])}}

sl, spl = stats(low), stats(pl)
print(f"\nLOWBAND (frozen): {sl}")
print(f"PLACEBO (frozen): {spl}")

# timing audit: every entry date must be exactly R+1 in the daily series
bad = []
for t in low + pl:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 1 >= len(daily) or daily[didx[t["R"]] + 1]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
print(f"timing audit violations: {len(bad)}")

json.dump({"construction_anchor": {"start_offset": conv,
                                   "ge25_candidates": len(cands_ge25),
                                   "dump_p2f_rows": len(dump)},
           "lowband_candidates": len(cands_low),
           "lowband_raw": len(low_raw), "placebo_raw": len(pl_raw),
           "lowband_trades": sorted(low, key=lambda x: (x["date"], x["symbol"])),
           "placebo_trades": sorted(pl, key=lambda x: (x["date"], x["symbol"])),
           "lowband_stats": sl, "placebo_stats": spl,
           "timing_violations": len(bad)},
          open(f"{BASE}/stocks_engine_sat32_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat32_diag.json")
