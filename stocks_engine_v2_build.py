#!/usr/bin/env python3
"""STOCKS ENGINE v2 BUILD — incumbent construction under the cross-year charter.

Runs the FROZEN v1 book VERBATIM on BOTH windows with all six components:
  2026 Jan-Oct (control: must reproduce the +Rs197,607.74 / 663 plateau)
  2025 Jan-Dec (full book, now runnable: the 2025 event calendar exists)

F4 + INV-LONG machinery: stocks_engine_2025_validation.py sections 2-8
exec'd verbatim, data root swapped from the (ephemeral) /tmp shadow to the
persistent rebuild data/full_hist (progressive cache copy + Upstox fills;
the main cache is never written). Event machinery (N4-V3 / P2F / P2F-R2 /
R2-LOWBAND): generalised from stocks_equity_n4deep.py / stocks_tuning_event.py
/ stocks_engine_sat13_score.py / stocks_engine_sat33_score.py, parameterised
by (calendar file, window, data root). Every generalised builder is anchored
per-trade against its frozen 2026 dump BEFORE any 2025 number is read.

Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0, square-off 15:10, RF-1 weekend stand-aside.
"""
import csv, json, os, sys, urllib.parse
from collections import defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
FULLHIST = f"{WS}/data/full_hist"
SHADOW = FULLHIST          # name the validation machinery expects
RAW = f"{WS}/data/full_hist"
OUTD = f"{WS}/v2_out"
os.makedirs(OUTD, exist_ok=True)
sys.path.insert(0, WS)

SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
GAP = ["ASTRAL", "BDL", "HINDUNILVR", "OIL"]
COST = 40.0
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)

# ---------------------------------------------------------------------
# Validation machinery, sections 2-8, verbatim (data root = full_hist)
# ---------------------------------------------------------------------
_vsrc = open(f"{WS}/stocks_engine_2025_validation.py").read()
_i2 = _vsrc.index("# 2. REENTRY HEAD"); _i2 = _vsrc.rfind("\n# =", 0, _i2)
_i8 = _vsrc.index("# 8. HELPERS");     _i8 = _vsrc.rfind("\n# =", 0, _i8)
_i9 = _vsrc.index("# 9. 2026 CONTROL"); _i9 = _vsrc.rfind("\n# =", 0, _i9)
exec(compile(_vsrc[_i2:_i8], "validation_sections_2_7", "exec"), globals())
exec(compile(_vsrc[_i8:_i9], "validation_section_8_helpers", "exec"), globals())
log("machinery loaded: collect2/build_inv/f4_keep/wk/EXCL_DIR/helpers OK")

MONTHS26 = [f"2026-{i:02d}" for i in range(1, 11)]
MONTHS25 = [f"2025-{i:02d}" for i in range(1, 13)]
STATE = {"2026-01": 28536.25, "2026-02": 18419.86, "2026-03": 20584.41,
         "2026-04": 9895.49, "2026-05": 34880.86, "2026-06": 3823.22,
         "2026-07": 6965.93, "2026-08": 666.78, "2026-09": 19562.51,
         "2026-10": 54272.43}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 197607.74, 663, 72518.25
RESULTS = {"controls": {}}

# ---------------------------------------------------------------------
# CONTROL A — SAT-36 dump assembly == plateau (validation 9a verbatim)
# ---------------------------------------------------------------------
inv_d = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
          "dir": "LONG", "net": float(t["net_rs_provisional_per100"]),
          "entry_time": t["entry_time"]}
         for t in rd("tuning_inv_T1_T125_S050_trades.csv")
         if t["direction"] == "LONG"
         and not wk(t["date"]) and t["stock"] != "BDL"
         and t["stock"] != "VEDL" and t["stock"] != "HINDZINC"
         and t["stock"] != "INDUSTOWER" and t["stock"] != "KALYANKJIL"]
n4_d = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
         "dir": r["direction"], "net": float(r["net"]), "entry_time": r["entry_time"]}
        for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
        if not wk(r["date"]) and r["stock"] != "ASTRAL"
        and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")
        and not (r["stock"] == "OIL" and r["direction"] == "LONG")]
p2f_d = [{"date": t["date"], "stock": t["symbol"], "comp": "P2F",
          "dir": t["direction"], "net": float(t["net_rs"]),
          "entry_time": t["entry_time"]}
         for t in rd("stocks_tuning_event_V1_combined_trades.csv")
         if t["leg"] == "P2F" and abs(float(t["reaction_ret_pct"])) >= 2.5
         and not wk(t["date"]) and t["symbol"] != "ASTRAL"
         and t["symbol"] != "HINDUNILVR"
         and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]
f4_d = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL_DIR:
        continue
    f4_d.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
                 "dir": r["dir"], "net": float(r["net"]),
                 "entry_time": r["entry_time"]})
r2_d = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
         "dir": r["direction"], "net": float(r["net_rs"]),
         "entry_time": r["entry_time"]}
        for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
        if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
r2low_d = [{"date": r["date"], "stock": r["symbol"], "comp": "R2-LOWBAND",
            "dir": r["direction"], "net": float(r["net_rs"]),
            "entry_time": r["entry_time"]}
           for r in rd("stocks_engine_sat33_r2lowband_trades.csv")]
book26_dumps = inv_d + n4_d + p2f_d + f4_d + r2_d + r2low_d
bt, _ = month_table(book26_dumps, MONTHS26)
ex0, top3_0 = extop3(book26_dumps)
ctrl_a = (bt == STATE and round(sum(t["net"] for t in book26_dumps), 2) == STATE_TOTAL
          and len(book26_dumps) == STATE_TRADES and ex0 == STATE_EXTOP3)
RESULTS["controls"]["A_dump_assembly"] = {
    "pass": ctrl_a, "trades": len(book26_dumps),
    "total": round(sum(t["net"] for t in book26_dumps), 2),
    "per_comp": {c: (len([t for t in book26_dumps if t["comp"] == c]),
                     round(sum(t["net"] for t in book26_dumps if t["comp"] == c), 2))
                 for c in ("INV-LONG", "N4-V3", "P2F", "F4", "P2F-R2", "R2-LOWBAND")}}
log("CONTROL A (dump assembly == plateau):", ctrl_a,
    len(book26_dumps), "tr", round(sum(t['net'] for t in book26_dumps), 2))

# ---------------------------------------------------------------------
# Generalised event machinery (data root = full_hist)
# ---------------------------------------------------------------------
def load_stock(sym):
    spot, daily = {}, []
    with open(f"{FULLHIST}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19],
                "time": r["timestamp"][11:16], "open": float(r["open"]),
                "high": float(r["high"]), "low": float(r["low"]),
                "close": float(r["close"])})
    with open(f"{FULLHIST}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]),
                          "high": float(r["high"]), "low": float(r["low"]),
                          "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

STOCKS_E = {s: load_stock(s) for s in SYMBOLS}
_, NIFTY_DAILY_E = load_stock("NIFTY")

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
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def results_events(cal_path, lo, hi):
    evs = []
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            if r["event_type"] != "results" or r["stock"] not in SYMBOLS: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                evs.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
    evs.sort(key=lambda e: (e["symbol"], e["R"]))
    return evs

def reaction_candidates(cal_path, lo, hi):
    """tuning_event / sat13 / sat33 candidate loop, verbatim logic."""
    cands = []
    for e in results_events(cal_path, lo, hi):
        sym, R = e["symbol"], e["R"]
        spot, daily = STOCKS_E[sym]
        didx = {d["date"]: i for i, d in enumerate(daily)}
        if R not in didx: continue
        ri = didx[R]
        if ri == 0 or ri + 1 >= len(daily): continue
        reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
        nd = daily[ri + 1]["date"]
        if nd > hi: continue
        if not spot.get(nd): continue
        cands.append({"symbol": sym, "announce": e["announce"], "R": R,
                      "reaction_ret_pct": reaction_ret, "ri": ri,
                      "direction": "LONG" if reaction_ret > 0 else "SHORT"})
    return cands

def score_lag(cand, lag):
    """P2F lag=1 / P2F-R2 & R2-LOWBAND lag=2. Entry = first bar open of the
    lag day, replay T125/S050 from bar 0 (sat13/sat33 verbatim)."""
    sym = cand["symbol"]; spot, daily = STOCKS_E[sym]
    ri = cand["ri"]
    if ri + lag >= len(daily): return None
    d = daily[ri + lag]["date"]
    bars = spot.get(d, [])
    if not bars: return None
    entry = bars[0]["open"]
    r = replay(bars, 0, entry, cand["direction"], 1.25, 0.5)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d, "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(cand["direction"], entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"]}

def p2f_book(cands, lo_band=2.5):
    raw = [t for t in (score_lag(c, 1) for c in cands
                       if abs(c["reaction_ret_pct"]) >= lo_band) if t]
    return [{"date": t["date"], "stock": t["symbol"], "comp": "P2F",
             "dir": t["direction"], "net": t["net_rs"],
             "entry_time": t["entry_time"], "R": t["R"],
             "reaction_ret_pct": t["reaction_ret_pct"]}
            for t in raw
            if not wk(t["date"]) and t["symbol"] != "ASTRAL"
            and t["symbol"] != "HINDUNILVR"
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

def p2fr2_sets(cands):
    ge = [c for c in cands if abs(c["reaction_ret_pct"]) >= 2.5]
    raw = [t for t in (score_lag(c, 2) for c in ge) if t]
    frozen = [t for t in raw if not wk(t["date"])
              and t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
    book = [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-R2",
             "dir": t["direction"], "net": t["net_rs"],
             "entry_time": t["entry_time"], "R": t["R"],
             "reaction_ret_pct": t["reaction_ret_pct"]}
            for t in frozen
            if not (t["symbol"] == "TVSMOTOR" and t["direction"] == "LONG")]
    return ge, frozen, book

def r2lowband_book(cands):
    low_c = [c for c in cands if 2.0 <= abs(c["reaction_ret_pct"]) < 2.5]
    raw = [t for t in (score_lag(c, 2) for c in low_c) if t]
    frozen = [t for t in raw if not wk(t["date"])
              and t["symbol"] not in ("ASTRAL", "HINDUNILVR")
              and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]
    book = [{"date": t["date"], "stock": t["symbol"], "comp": "R2-LOWBAND",
             "dir": t["direction"], "net": t["net_rs"],
             "entry_time": t["entry_time"], "R": t["R"],
             "reaction_ret_pct": t["reaction_ret_pct"]} for t in frozen]
    return low_c, book

SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
               "block_deal", "sector_policy", "pricing", "corporate_action"}
def n4_raw(cal_path, lo, hi):
    """n4deep V3 signals verbatim, rescored T150/S080 (SAT-15 exits)."""
    combined = {s: set() for s in SYMBOLS}
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in combined: continue
            et = r["event_type"]
            if et != "results" and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi: combined[sym].add(ds)
    all_days = sorted(d["date"] for d in NIFTY_DAILY_E if lo <= d["date"] <= hi)
    out = []
    for sym in SYMBOLS:
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
            idx_of = {c["timestamp"]: i for i, c in enumerate(raw)}
            b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
            if b0925 is None or b0930 is None: continue
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= 1.0:
                direction = "LONG" if move_pct > 0 else "SHORT"
                ei = idx_of[b0930["timestamp"]]
                entry = b0930["close"]
                r = replay(raw, ei, entry, direction, 1.50, 0.80)
                if r is None: continue
                er, ep, et = r
                sign = 1 if direction == "LONG" else -1
                out.append({"symbol": sym, "date": day, "direction": direction,
                            "entry_time": "09:35", "entry": round(entry, 2),
                            "exit_reason": er, "exit_price": round(ep, 2),
                            "exit_time": et,
                            "net": round(sign * (ep - entry) * 100 - COST, 2)})
    return out

def n4_book(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "N4-V3",
             "dir": t["direction"], "net": t["net"], "entry_time": t["entry_time"]}
            for t in raw
            if not wk(t["date"]) and t["symbol"] != "ASTRAL"
            and not (t["symbol"] == "TVSMOTOR" and t["direction"] == "LONG")
            and not (t["symbol"] == "OIL" and t["direction"] == "LONG")]

def sametrades(a, b, ka, kb):
    """per-trade set equality on (date, stock, dir, entry_time, net)."""
    sa = sorted((t[ka[0]], t[ka[1]], t[ka[2]], t[ka[3]], round(float(t[ka[4]]), 2)) for t in a)
    sb = sorted((t[kb[0]], t[kb[1]], t[kb[2]], t[kb[3]], round(float(t[kb[4]]), 2)) for t in b)
    return sa == sb

CAL26 = f"{WS}/stock_event_calendar_jan_oct_2026.csv"
CAL25 = f"{WS}/stock_event_calendar_2025.csv"
LO26, HI26 = "2026-01-01", "2026-10-28"
LO25, HI25 = "2025-01-01", "2025-12-31"

# ---------------------------------------------------------------------
# CONTROLS B/C — F4 + INV machinery rebuilds over 2026 (validation 9b/9c)
# ---------------------------------------------------------------------
days26 = sorted({d for (s, d) in DAYCTX if d.startswith("2026")})
days25 = sorted({d for (s, d) in DAYCTX if d.startswith("2025")})
a0 = dict(_AUDIT)
raw080 = collect2(days26, F4_CFG, 1.50, 0.80)
aud080 = {"trades": _AUDIT["trades"] - a0["trades"],
          "violations": _AUDIT["violations"] - a0["violations"]}
oc4 = rd("stocks_engine_oc4_f4s080_trades.csv")
key5 = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
ctrl_b1 = sorted(key5(t) for t in raw080) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in oc4)
a0 = dict(_AUDIT)
raw095 = collect2(days26, F4_CFG, 1.50, 0.95)
aud095 = {"trades": _AUDIT["trades"] - a0["trades"],
          "violations": _AUDIT["violations"] - a0["violations"]}
f4_mine26 = [t for t in raw095 if f4_keep(t)]
f4key = lambda t: (t["date"], t["stock"], t["dir"], t["net"], t["entry_time"])
ctrl_b2 = sorted(f4key({"date": t["date"], "stock": t["symbol"], "dir": t["dir"],
                        "net": t["net"], "entry_time": t["entry_time"]}) for t in f4_mine26) == \
          sorted(f4key(t) for t in f4_d)
inv_mine26, inv_stages26 = build_inv(days26)
invkey = lambda t: (t["date"], t["stock"], t["entry_time"], t["net"])
ctrl_c = sorted(invkey(t) for t in inv_mine26) == sorted(invkey(t) for t in inv_d)
RESULTS["controls"]["B1_f4_oc4"] = ctrl_b1
RESULTS["controls"]["B2_f4_frozen_set"] = ctrl_b2
RESULTS["controls"]["C_inv_frozen_set"] = ctrl_c
RESULTS["controls"]["f4_audit"] = {"s080": aud080, "s095": aud095}
log("CONTROL B1 (F4 T150/S080 == oc4):", ctrl_b1, "| B2 (F4 S095 == frozen set):",
    ctrl_b2, "| C (INV == frozen set):", ctrl_c, "| audits:", aud080, aud095)

# ---------------------------------------------------------------------
# EVENT ANCHORS 2026 — generalised builders vs frozen dumps
# ---------------------------------------------------------------------
cands26 = reaction_candidates(CAL26, LO26, HI26)
p2f20 = [t for t in (score_lag(c, 1) for c in cands26
                     if abs(c["reaction_ret_pct"]) >= 2.0) if t]
anch_p2f20 = (len(p2f20) == 48
              and round(sum(t["net_rs"] for t in p2f20), 2) == 12835.88)
p2f_mine26 = p2f_book(cands26)
anch_p2f = sametrades(p2f_mine26, p2f_d,
                      ("date", "stock", "dir", "entry_time", "net"),
                      ("date", "stock", "dir", "entry_time", "net"))
ge26, frozen26, r2_mine26 = p2fr2_sets(cands26)
sat13_dump = rd("stocks_engine_sat13_p2fr2_trades.csv")
anch_r2_cands = len(ge26) == 39
anch_r2_frozen = sametrades(
    [{"date": t["date"], "stock": t["symbol"], "dir": t["direction"],
      "net": t["net_rs"], "entry_time": t["entry_time"]} for t in frozen26],
    sat13_dump, ("date", "stock", "dir", "entry_time", "net"),
    ("date", "symbol", "direction", "entry_time", "net_rs"))
anch_r2_book = sametrades(r2_mine26, r2_d,
                          ("date", "stock", "dir", "entry_time", "net"),
                          ("date", "stock", "dir", "entry_time", "net"))
lowc26, low_mine26 = r2lowband_book(cands26)
sat33_dump = rd("stocks_engine_sat33_r2lowband_trades.csv")
anch_low_cands = len(lowc26) == 9
anch_low = sametrades(low_mine26, sat33_dump,
                      ("date", "stock", "dir", "entry_time", "net"),
                      ("date", "symbol", "direction", "entry_time", "net_rs"))
n4raw26 = n4_raw(CAL26, LO26, HI26)
sat15_dump = rd("stocks_engine_sat15_n4_t150s080_trades.csv")
anch_n4_raw = sametrades(
    [{"date": t["date"], "stock": t["symbol"], "dir": t["direction"],
      "net": t["net"], "entry_time": t["entry_time"]} for t in n4raw26],
    sat15_dump, ("date", "stock", "dir", "entry_time", "net"),
    ("date", "stock", "direction", "entry_time", "net"))
n4_mine26 = n4_book(n4raw26)
anch_n4_book = sametrades(n4_mine26, n4_d,
                          ("date", "stock", "dir", "entry_time", "net"),
                          ("date", "stock", "dir", "entry_time", "net"))
RESULTS["controls"]["event_anchors"] = {
    "p2f_band20_anchor_48_12835.88": anch_p2f20, "p2f_book": anch_p2f,
    "p2fr2_candidates_39": anch_r2_cands, "p2fr2_frozen_dump": anch_r2_frozen,
    "p2fr2_book": anch_r2_book, "r2lowband_candidates_9": anch_low_cands,
    "r2lowband_dump": anch_low, "n4_raw_dump": anch_n4_raw, "n4_book": anch_n4_book}
log("EVENT ANCHORS 2026:", RESULTS["controls"]["event_anchors"])

# ---------------------------------------------------------------------
# 2025 ANCHORS — F4 + INV on full_hist == validation numbers
# ---------------------------------------------------------------------
a0 = dict(_AUDIT)
raw25 = collect2(days25, F4_CFG, 1.50, 0.95)
aud25 = {"trades": _AUDIT["trades"] - a0["trades"],
         "violations": _AUDIT["violations"] - a0["violations"]}
f4_mine25 = [t for t in raw25 if f4_keep(t)]
inv_mine25, inv_stages25 = build_inv(days25)
f4_25_net = round(sum(t["net"] for t in f4_mine25), 2)
inv_25_net = round(sum(t["net"] for t in inv_mine25), 2)
anch25_f4 = len(f4_mine25) == 261 and f4_25_net == -5093.75
anch25_inv = len(inv_mine25) == 245 and inv_25_net == 7642.52
RESULTS["controls"]["anchors_2025"] = {
    "f4_261_-5093.75": anch25_f4, "inv_245_+7642.52": anch25_inv,
    "f4_audit": aud25}
log("2025 ANCHORS: F4", len(f4_mine25), f4_25_net, anch25_f4,
    "| INV", len(inv_mine25), inv_25_net, anch25_inv, "| audit", aud25)

ALL_CTRL = all([ctrl_a, ctrl_b1, ctrl_b2, ctrl_c, anch_p2f20, anch_p2f,
                anch_r2_cands, anch_r2_frozen, anch_r2_book, anch_low_cands,
                anch_low, anch_n4_raw, anch_n4_book, anch25_f4, anch25_inv,
                aud080["violations"] == 0, aud095["violations"] == 0,
                aud25["violations"] == 0])
RESULTS["controls"]["ALL_PASS"] = ALL_CTRL
log("ALL CONTROLS PASS:", ALL_CTRL)
if not ALL_CTRL:
    json.dump(RESULTS, open(f"{OUTD}/v2_build_results.json", "w"), indent=1)
    log("CONTROL FAILURE — stopping before incumbent assembly.")
    sys.exit(2)

# ---------------------------------------------------------------------
# INCUMBENT ASSEMBLY — both years, all six components, machinery-built
# ---------------------------------------------------------------------
def norm_f4(raw, comp="F4"):
    return [{"date": t["date"], "stock": t["symbol"], "comp": comp,
             "dir": t["dir"], "entry_time": t["entry_time"], "net": t["net"],
             "setup": t["setup"], "round": t["round"]} for t in raw]
def norm_inv(raw):
    return [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
             "dir": "LONG", "entry_time": t["entry_time"], "net": t["net"],
             "setup": t["setup"], "round": t["round"]} for t in raw]

f4_26 = norm_f4(f4_mine26); inv_26 = norm_inv(inv_mine26)
book26 = f4_26 + inv_26 + n4_mine26 + p2f_mine26 + r2_mine26 + low_mine26

cands25 = reaction_candidates(CAL25, LO25, HI25)
p2f_mine25 = p2f_book(cands25)
ge25, frozen25, r2_mine25 = p2fr2_sets(cands25)
lowc25, low_mine25 = r2lowband_book(cands25)
n4raw25 = n4_raw(CAL25, LO25, HI25)
n4_mine25 = n4_book(n4raw25)
f4_25 = norm_f4(f4_mine25); inv_25 = norm_inv(inv_mine25)
book25 = f4_25 + inv_25 + n4_mine25 + p2f_mine25 + r2_mine25 + low_mine25

COMPS = ("F4", "INV-LONG", "N4-V3", "P2F", "P2F-R2", "R2-LOWBAND")
def comp_table(book):
    return {c: {"trades": len([t for t in book if t["comp"] == c]),
                "net": round(sum(t["net"] for t in book if t["comp"] == c), 2)}
            for c in COMPS}
s26 = stats_block(book26, MONTHS26)
s25 = stats_block(book25, MONTHS25)
assert round(s26["total"], 2) == STATE_TOTAL and len(book26) == STATE_TRADES, \
    "machinery 2026 book != plateau"
comb_total = round(s25["total"] + s26["total"], 2)
RESULTS["incumbent"] = {
    "y2025": {"stats": s25, "per_comp": comp_table(book25),
              "candidates": {"reaction_cands": len(cands25),
                             "ge25": len(ge25), "lowband": len(lowc25),
                             "n4_raw": len(n4raw25)}},
    "y2026": {"stats": s26, "per_comp": comp_table(book26)},
    "combined_total": comb_total,
    "combined_trades": len(book25) + len(book26),
    "monthly_avg_22mo": round(comb_total / 22, 2),
    "avg_2025_per_month": round(s25["total"] / 12, 2),
    "avg_2026_per_month": round(s26["total"] / 10, 2),
    "goal_per_month": 75000}
log("2025 FULL BOOK:", s25["trades"], "tr, total", s25["total"],
    "| per-comp", RESULTS["incumbent"]["y2025"]["per_comp"])
log("2025 months:", s25["months"], "| red:", s25["red_months"],
    "| ex-top3:", s25["ex_top3"], "| maxDD:", s25["max_drawdown"])
log("2026 BOOK (machinery):", s26["trades"], "tr, total", s26["total"],
    "| per-comp", RESULTS["incumbent"]["y2026"]["per_comp"])
log("COMBINED:", comb_total, "| 22-mo avg:", RESULTS["incumbent"]["monthly_avg_22mo"],
    "| 2025/mo:", RESULTS["incumbent"]["avg_2025_per_month"],
    "| 2026/mo:", RESULTS["incumbent"]["avg_2026_per_month"])

def wtrades(fn, book):
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
        for t in sorted(book, key=lambda x: (x["date"], x["entry_time"], x["stock"], x["comp"])):
            w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                        t["entry_time"], t["net"]])
wtrades(f"{WS}/stocks_engine_v2_book2025_trades.csv", book25)
wtrades(f"{WS}/stocks_engine_v2_book2026_trades.csv", book26)
json.dump(RESULTS, open(f"{OUTD}/v2_build_results.json", "w"), indent=1)
log("wrote v2 book trade CSVs + v2_out/v2_build_results.json")
print("\n".join(LOG))
