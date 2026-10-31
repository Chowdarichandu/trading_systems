#!/usr/bin/env python3
"""LINE T2 — EVENT-AXIS DEEPENING (P2F extensions).
Spec frozen FIRST in stocks_T2_frozen.md. EQUITY CASH, LONG/SHORT.
Paper only, real Rs0. Per 100 shares provisional, Rs40/trade flat.
Cells: T2-A magnitude curve R+1 (3.0/4.0), T2-B entry R+2 (2.0/2.5),
T2-C two-day stop-only hold at 2.5% (NON-INTRADAY, labelled)."""
import csv, json, os
from datetime import date, timedelta

OUT = "/home/hatch/workspace/trading"
HOME_BASE = f"{OUT}/data/progressive"
EXT_BASE = f"{OUT}/data/progressive_ext"
HOME_SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
EXT_SYMBOLS = sorted(d for d in os.listdir(EXT_BASE)
                     if os.path.isdir(f"{EXT_BASE}/{d}") and d != "NIFTY")
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
H1_HI = "2026-05-31"

def load_stock(base, sym):
    spot, daily = {}, []
    with open(f"{base}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{base}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]), "high": float(r["high"]),
                          "low": float(r["low"]), "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

UNIV = {
    "HOME": {"base": HOME_BASE, "symbols": HOME_SYMBOLS,
             "calendar": f"{OUT}/stock_event_calendar_jan_oct_2026.csv", "stocks": {}},
    "EXT":  {"base": EXT_BASE, "symbols": EXT_SYMBOLS,
             "calendar": f"{OUT}/stock_event_calendar_ext_jan_oct_2026.csv", "stocks": {}},
}
for u in UNIV.values():
    for s in u["symbols"]:
        u["stocks"][s] = load_stock(u["base"], s)

# ---------- exit engine: round-5 N4, verbatim from stocks_tuning_event.py ----------
def replay(candles, ei, entry, direction, tgt_pct, stp_pct):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + 1, len(candles)):
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

# ---------- P2F candidates, verbatim construction (per universe) ----------
def build_candidates(u):
    spot_all, events = u["stocks"], []
    with open(u["calendar"]) as f:
        for r in csv.DictReader(f):
            if r["event_type"] != "results" or r["stock"] not in u["symbols"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if ALL_LO <= ds <= ALL_HI:
                events.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
    events.sort(key=lambda e: (e["symbol"], e["R"]))
    cands = []
    for e in events:
        sym, R = e["symbol"], e["R"]
        spot, daily = spot_all[sym]
        didx = {d["date"]: i for i, d in enumerate(daily)}
        if R not in didx: continue
        ri = didx[R]
        if ri == 0 or ri + 1 >= len(daily): continue
        reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
        nd = daily[ri + 1]["date"]
        if nd > ALL_HI: continue
        bars = spot.get(nd, [])
        if not bars: continue
        cands.append({"symbol": sym, "announce": e["announce"], "R": R,
                      "reaction_ret_pct": reaction_ret, "trade_date": nd,
                      "direction": "LONG" if reaction_ret > 0 else "SHORT",
                      "entry": bars[0]["open"], "ri": ri})
    return cands

CANDS = {name: build_candidates(u) for name, u in UNIV.items()}

# ---------- scorers ----------
def score_r1(u, cand):
    spot, _ = u["stocks"][cand["symbol"]]
    r = replay(spot[cand["trade_date"]], 0, cand["entry"], cand["direction"], 1.25, 0.5)
    if r is None: return None
    er, ep, et = r
    return {"symbol": cand["symbol"], "date": cand["trade_date"], "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(cand["entry"], 2), "exit_reason": er,
            "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(cand["direction"], cand["entry"], ep),
            "R": cand["R"], "reaction_ret_pct": cand["reaction_ret_pct"]}

def score_r2(u, cand):
    """Entry R+2 09:15 open. Returns (trade|None, drop_reason|None)."""
    spot, daily = u["stocks"][cand["symbol"]]
    ri = cand["ri"]
    if ri + 2 >= len(daily): return None, "no R+2 in data"
    d2 = daily[ri + 2]["date"]
    if d2 > ALL_HI: return None, "R+2 after window"
    bars = spot.get(d2, [])
    if not bars: return None, "no R+2 bars"
    entry = bars[0]["open"]
    r = replay(bars, 0, entry, cand["direction"], 1.25, 0.5)
    if r is None: return None, "replay none"
    er, ep, et = r
    return {"symbol": cand["symbol"], "date": d2, "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(entry, 2), "exit_reason": er,
            "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(cand["direction"], entry, ep),
            "R": cand["R"], "reaction_ret_pct": cand["reaction_ret_pct"]}, None

def score_hold(u, cand):
    """T2-C NON-INTRADAY: stop-only (-0.5%) across R+1 and R+2; exit R+2 15:10 close."""
    spot, daily = u["stocks"][cand["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    ti = didx[cand["trade_date"]]
    if ti + 1 >= len(daily): return None, "no R+2 in data"
    r2 = daily[ti + 1]["date"]
    bars2 = spot.get(r2, [])
    if not bars2: return None, "no R+2 bars"
    entry, direction = cand["entry"], cand["direction"]
    sign = 1 if direction == "LONG" else -1
    stop = entry * (1 - sign * 0.5 / 100)
    def stop_hit(c):
        return c["low"] <= stop if sign == 1 else c["high"] >= stop
    def mk(er, ep, et, hold_days):
        return {"symbol": cand["symbol"], "date": cand["trade_date"], "direction": direction,
                "entry_time": "09:15", "entry": round(entry, 2), "exit_reason": er,
                "exit_price": round(ep, 2), "exit_time": et,
                "net_rs": net_of(direction, entry, ep),
                "R": cand["R"], "reaction_ret_pct": cand["reaction_ret_pct"],
                "hold_days": hold_days}, None
    # Day R+1: scan bars after entry bar, times <= 15:10
    held = True
    for c in spot[cand["trade_date"]][1:]:
        if c["time"] > "15:10": break
        if stop_hit(c): return mk("stop", stop, f"{cand['trade_date']} {c['time']}", 1)
        if c["time"] == "15:10": break
    # Overnight -> R+2 open gap check
    o = bars2[0]["open"]
    if (sign == 1 and o <= stop) or (sign == -1 and o >= stop):
        return mk("gap_stop", o, f"{r2} 09:15", 2)
    # Day R+2: scan all bars, times <= 15:10
    last = None
    for c in bars2:
        if c["time"] > "15:10": break
        last = c
        if stop_hit(c): return mk("stop", stop, f"{r2} {c['time']}", 2)
        if c["time"] == "15:10": return mk("square_off", c["close"], f"{r2} {c['time']}", 2)
    if last is not None: return mk("square_off", last["close"], f"{r2} {last['time']}", 2)
    return None, "no R+2 bars usable"

# ---------- metrics ----------
def metrics(trades):
    if not trades:
        return {"trades": 0, "win_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0}
    net = round(sum(t["net_rs"] for t in trades), 2)
    return {"trades": len(trades),
            "win_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "net_rs": net, "expectancy_rs": round(net / len(trades), 2)}

def block(trades, universe_size):
    h1 = [t for t in trades if t["date"] <= H1_HI]; h2 = [t for t in trades if t["date"] > H1_HI]
    oct_ = [t for t in trades if t["date"][:7] == "2026-10"]
    pst = {}
    for t in trades: pst[t["symbol"]] = round(pst.get(t["symbol"], 0.0) + t["net_rs"], 2)
    m = metrics(trades)
    pos = sorted((v for v in pst.values() if v > 0), reverse=True)
    top3 = round(sum(pos[:3]) / m["net_rs"] * 100, 1) if m["net_rs"] > 0 and pos else None
    longs = [t for t in trades if t["direction"] == "LONG"]; shorts = [t for t in trades if t["direction"] == "SHORT"]
    return {"all": m, "H1": metrics(h1), "H2": metrics(h2), "october": metrics(oct_),
            "both_halves_positive": bool(h1 and h2 and metrics(h1)["net_rs"] > 0 and metrics(h2)["net_rs"] > 0),
            "october_positive": bool(oct_ and metrics(oct_)["net_rs"] > 0),
            "breadth_net_positive_stocks": sum(1 for v in pst.values() if v > 0),
            "breadth_of": universe_size, "stocks_traded": len(pst),
            "top3_share_pct": top3,
            "LONG": metrics(longs), "SHORT": metrics(shorts),
            "per_stock_net": dict(sorted(pst.items(), key=lambda kv: -kv[1]))}

def audit(trades, threshold):
    """Timing + construction audit over every trade of a cell."""
    v = 0; bad = []
    for t in trades:
        ok = (t["date"] > t["R"] and t["entry_time"] == "09:15"
              and t["direction"] == ("LONG" if t["reaction_ret_pct"] > 0 else "SHORT")
              and abs(t["reaction_ret_pct"]) >= threshold - 1e-9)
        if not ok: v += 1; bad.append(t)
    return v, bad

def gate(b, is_home):
    g = {"both_halves_positive": b["both_halves_positive"],
         "october_positive": b["october_positive"]}
    if is_home: g["expectancy_ge_397.16"] = b["all"]["expectancy_rs"] >= 397.16
    g["pass"] = all(g.values())
    return g

results = {"anchors": {}, "audit": {}, "cells": {}}

# ---------- ANCHORS (HOME) ----------
home_u = UNIV["HOME"]
for band, exp_n, exp_net in ((2.0, 48, 12835.88), (2.5, 39, 15489.08)):
    tr = [t for c in CANDS["HOME"] if abs(c["reaction_ret_pct"]) >= band
          for t in [score_r1(home_u, c)] if t]
    b = block(tr, 25)
    results["anchors"][f"P2F_{band}"] = b
    print(f"ANCHOR HOME P2F {band}% (expect {exp_n} / +{exp_net}):", b["all"],
          "H1", b["H1"]["net_rs"], "H2", b["H2"]["net_rs"], "breadth", b["breadth_net_positive_stocks"])
    assert b["all"]["trades"] == exp_n and abs(b["all"]["net_rs"] - exp_net) < 0.01, f"ANCHOR FAIL {band}"

# ---------- CELLS ----------
CELLS = [
    ("T2-A_3.0", "T2-A", 3.0, "r1"),
    ("T2-A_4.0", "T2-A", 4.0, "r1"),
    ("T2-B_2.0", "T2-B", 2.0, "r2"),
    ("T2-B_2.5", "T2-B", 2.5, "r2"),
    ("T2-C_2.5", "T2-C", 2.5, "hold"),
]
all_audit_violations = 0
for cell_id, family, band, kind in CELLS:
    per_univ_trades = {}
    drops = {}
    for uname, u in UNIV.items():
        trs = []
        dropped = 0
        for c in CANDS[uname]:
            if abs(c["reaction_ret_pct"]) < band: continue
            if kind == "r1":
                t = score_r1(u, c)
                if t: trs.append(dict(t, universe=uname))
            elif kind == "r2":
                t, why = score_r2(u, c)
                if t: trs.append(dict(t, universe=uname))
                else: dropped += 1
            else:
                t, why = score_hold(u, c)
                if t: trs.append(dict(t, universe=uname))
                else: dropped += 1
        per_univ_trades[uname] = trs
        drops[uname] = dropped
    pooled = per_univ_trades["HOME"] + per_univ_trades["EXT"]
    pooled.sort(key=lambda t: (t["date"], t["symbol"]))
    v, bad = audit(pooled, band)
    all_audit_violations += v
    results["audit"][cell_id] = {"violations": v}
    bh = block(per_univ_trades["HOME"], 25)
    bp = block(pooled, 50)
    gh = gate(bh, True); gp = gate(bp, False)
    gh["audit_clean"] = gp["audit_clean"] = (v == 0)
    gh["pass"] = gh["pass"] and v == 0; gp["pass"] = gp["pass"] and v == 0
    results["cells"][cell_id] = {"family": family, "band": band, "kind": kind,
                                 "drops": drops, "HOME": bh, "POOLED": bp,
                                 "gate_HOME": gh, "gate_POOLED": gp}
    print(f"{cell_id}: audit_violations={v} drops={drops}")
    print(f"  HOME   {bh['all']} H1 {bh['H1']['net_rs']}({bh['H1']['trades']}) H2 {bh['H2']['net_rs']}({bh['H2']['trades']}) "
          f"OCT {bh['october']['net_rs']}({bh['october']['trades']}) breadth {bh['breadth_net_positive_stocks']}/25 top3 {bh['top3_share_pct']} gate {gh}")
    print(f"  POOLED {bp['all']} H1 {bp['H1']['net_rs']}({bp['H1']['trades']}) H2 {bp['H2']['net_rs']}({bp['H2']['trades']}) "
          f"OCT {bp['october']['net_rs']}({bp['october']['trades']}) breadth {bp['breadth_net_positive_stocks']}/50 top3 {bp['top3_share_pct']} gate {gp}")
    # dump pooled trades (universe column marks membership)
    cols = ["universe","leg","symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","R","reaction_ret_pct","hold_days"]
    with open(f"{OUT}/stocks_T2_{cell_id}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in pooled:
            w.writerow({"universe": t["universe"], "leg": family, "symbol": t["symbol"], "date": t["date"],
                        "direction": t["direction"], "entry_time": t["entry_time"], "entry": t["entry"],
                        "exit_reason": t["exit_reason"], "exit_price": t["exit_price"], "exit_time": t["exit_time"],
                        "net_rs": t["net_rs"], "R": t["R"], "reaction_ret_pct": t["reaction_ret_pct"],
                        "hold_days": t.get("hold_days", 1)})

results["audit"]["TOTAL_VIOLATIONS"] = all_audit_violations
json.dump(results, open(f"{OUT}/stocks_T2_results.json", "w"), indent=1)
print("TOTAL AUDIT VIOLATIONS:", all_audit_violations)
print("DONE")
