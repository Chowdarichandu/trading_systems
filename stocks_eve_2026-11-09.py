#!/usr/bin/env python3
"""Stocks evening engine 2026-11-09.
Part A: candle-verified detail for today's (2026-11-09) SarvaRitu book trades
(4) + scorecard trades (N4-V3 HINDALCO SHORT stop; P2F shadow GLENMARK target /
ASTRAL stop) + TUNED SHADOW v1 scoring.
Part B: STOCKS-EVE-15 - INV-ABOVE stop widened S050 -> S080 (T125 kept),
rescanned from data/full_hist; scanner must first reproduce stored nets.
Part C: STOCKS-EVE-16 - INV-ABOVE: drop entries whose stock already traded a
P2F-family leg (P2F / P2F-R2 / R2-LOWBAND) the same day in the same book dump
(cross-component same-stock stacking filter; pure drop filter, both years).
Part D: STOCKS-EVE-17 - INV-ABOVE: registry deletion of GLENMARK only
(FLOOR-4-style single-name deletion; pure drop filter, both years).
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade.
"""
import csv, json, pathlib, collections
WS = pathlib.Path.home() / "workspace/trading"
FWD = WS / "data/sarvaritu_fwd"
FULL = WS / "data/full_hist"
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

def scan(bars_, entry_time, entry, stop, target, direction, include_entry=False):
    started = include_entry
    mfe = mae = None
    for t, o, h, l, c in bars_:
        if t == entry_time and not include_entry:
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
            if l <= stop:
                return t, stop, "stop", mfe, mae
            if h >= target:
                return t, target, "target", mfe, mae
        else:
            if h >= stop:
                return t, stop, "stop", mfe, mae
            if l <= target:
                return t, target, "target", mfe, mae
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

def summ(rows, col="net"):
    return {"n": len(rows), "net": round(sum(float(r[col]) for r in rows), 2)}
def halves(rows, col="net"):
    h1 = [r for r in rows if r["date"][5:7] in ("01", "02", "03", "04", "05")]
    h2 = [r for r in rows if r["date"][5:7] in ("06", "07", "08", "09", "10", "11", "12")]
    return summ(h1, col), summ(h2, col)
def months(rows, col="net"):
    m = collections.defaultdict(float)
    for r in rows:
        m[r["date"][:7]] += float(r[col])
    return {k: round(v, 2) for k, v in sorted(m.items())}
def ex_top3(rows, col="net"):
    s = sorted((float(r[col]) for r in rows), reverse=True)
    return round(sum(s[3:]), 2) if len(s) > 3 else None
def flips(base_rows, var_rows, col="net"):
    bm, vm = months(base_rows, col), months(var_rows, col)
    return [m for m in bm if bm[m] > 0 and vm.get(m, 0.0) < 0]

# ---------------- Part A ----------------
print("=" * 70)
print("PART A - today 2026-11-09, candle-verified (fwd root, 75 bars/symbol)")
# Book trades: (comp, stock, dir, entry_time, entry, logged_net, logged_exit)
BOOK = [
    ("P2F-R2", "GLENMARK", "LONG", "09:15", 2590.00, 3197.50, 2622.38),
    ("INV-ABOVE", "GLENMARK", "LONG", "09:35", 2658.00, -1369.00, 2644.71),
    ("INV-ABOVE", "GLENMARK", "LONG", "09:40", 2650.80, -1365.40, 2637.55),
]
GEOM = {"P2F-R2": (0.0050, 0.0125), "INV-ABOVE": (0.0050, 0.0125)}
for comp, sym, d, et, entry, logged, logged_exit in BOOK:
    b = bars(FWD, sym, "2026-11-09")
    sp, tp = GEOM[comp]
    stop, tgt = levels(entry, d, sp, tp)
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    print(json.dumps({"comp": comp, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": net_of(entry, xp, d) if xp else None,
                      "net_logged_book": logged, "exit_logged_book": logged_exit,
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None,
                      "nbars": len(b)}))
# GLENMARK continuation after the INV stops (exit-tuning evidence)
b = bars(FWD, "GLENMARK", "2026-11-09")
print(json.dumps({"GLENMARK_day": {"open": b[0][1], "high": max(x[2] for x in b),
                                   "low": min(x[3] for x in b), "close_1510": [x[4] for x in b if x[0] == "15:10"][0]}}))
# Book N4-V3 TATASTEEL: entry = 09:30 close per n4_raw (entry_time labelled 09:35),
# trigger vs fwd-daily prev close (2026-11-08 Muhurat close 190.20) = -1.225% SHORT;
# scorecard construction (ex-Muhurat, prev regular close 186.30) = +0.843% no-trigger.
b = bars(FWD, "TATASTEEL", "2026-11-09")
stop, tgt = levels(187.47, "SHORT", 0.0080, 0.0150)
xt, xp, xr, mfe, mae = scan(b, "09:35", 187.47, stop, tgt, "SHORT", include_entry=True)
print(json.dumps({"comp": "N4-V3-BOOK", "stock": "TATASTEEL", "dir": "SHORT",
                  "entry_time": "09:35", "entry_0930close": 187.47, "stop": stop,
                  "target": tgt, "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                  "net_recomputed": net_of(187.47, xp, "SHORT"), "net_logged_book": 241.20,
                  "mfe_rs": round(mfe, 2), "mae_rs": round(mae, 2)}))
# Scorecards today
b = bars(FWD, "HINDALCO", "2026-11-09")
stop, tgt = levels(936.40, "SHORT", 0.0050, 0.0125)
xt, xp, xr, mfe, mae = scan(b, "09:35", 936.40, stop, tgt, "SHORT", include_entry=True)
print(json.dumps({"comp": "N4-V3-SCORECARD", "stock": "HINDALCO", "entry": 936.40,
                  "stop": stop, "target": tgt, "exit_time": xt, "exit_price": xp,
                  "exit_reason": xr, "net_recomputed": net_of(936.40, xp, "SHORT"),
                  "net_logged_scorecard": -508.20,
                  "mfe_rs": round(mfe, 2), "mae_rs": round(mae, 2)}))
b = bars(FWD, "ASTRAL", "2026-11-09")
stop, tgt = levels(1261.60, "SHORT", 0.0050, 0.0125)
xt, xp, xr, mfe, mae = scan(b, "09:15", 1261.60, stop, tgt, "SHORT")
print(json.dumps({"comp": "P2F-SHADOW", "stock": "ASTRAL", "entry": 1261.60,
                  "stop": stop, "target": tgt, "exit_time": xt, "exit_price": xp,
                  "exit_reason": xr, "net_recomputed": net_of(1261.60, xp, "SHORT"),
                  "net_logged_shadow": -670.80,
                  "mfe_rs": round(mfe, 2) if mfe is not None else None,
                  "mae_rs": round(mae, 2) if mae is not None else None}))
# Live-shadow-only rows today (not in the frozen book log): NHPC P2F-R2, PFC R2-LOWBAND
for sym, entry in (("NHPC", 81.30), ("PFC", 332.05)):
    bb = bars(FWD, sym, "2026-11-09")
    s2, t2 = levels(entry, "LONG", 0.0050, 0.0125)
    xt, xp, xr, mfe, mae = scan(bb, "09:15", entry, s2, t2, "LONG")
    print(json.dumps({"comp": "LIVE-SHADOW-ONLY", "stock": sym, "entry": entry,
                      "stop": s2, "target": t2, "exit_time": xt, "exit_price": xp,
                      "exit_reason": xr, "net_recomputed": net_of(entry, xp, "LONG")}))

# ---------------- Parts B/C/D universes ----------------
def load_book(yr):
    rows = list(csv.DictReader(open(WS / f"stocks_engine_v2_c24_book{yr}_trades.csv")))
    for r in rows:
        r["net"] = float(r["net"])
    return rows
BOOKS = {yr: load_book(yr) for yr in ("2025", "2026")}
INV = {yr: sorted([r for r in BOOKS[yr] if r["comp"] == "INV-ABOVE"],
                  key=lambda r: (r["date"], r["entry_time"])) for yr in BOOKS}
ALL = INV["2025"] + INV["2026"]
print("INV-ABOVE universe:", {y: summ(INV[y]) for y in INV}, "combined", summ(ALL))

def gate_drop(name, drop_pred, placebo_mode="chrono"):
    kept = [r for r in ALL if not drop_pred(r)]
    dropped = [r for r in ALL if drop_pred(r)]
    if placebo_mode == "chrono":
        plac = ALL[len(dropped):]
    else:  # mirror: drop the LAST same-count entries chronologically
        plac = ALL[:len(ALL) - len(dropped)] if dropped else ALL
    res = {"candidate": name, "base": summ(ALL), "variant": summ(kept),
           "dropped": summ(dropped), "placebo_chrono": summ(plac),
           "halves_base": halves(ALL), "halves_variant": halves(kept),
           "ex_top3_base": ex_top3(ALL), "ex_top3_variant": ex_top3(kept),
           "month_flips": flips(ALL, kept),
           "month_table_base": months(ALL), "month_table_variant": months(kept)}
    for yr in ("2025", "2026"):
        ky = [r for r in INV[yr] if not drop_pred(r)]
        dy = [r for r in INV[yr] if drop_pred(r)]
        py = INV[yr][len(dy):]
        res[f"yr_{yr}"] = {"base": summ(INV[yr]), "variant": summ(ky),
                           "dropped": summ(dy), "placebo_chrono": summ(py),
                           "flips": flips(INV[yr], ky)}
    print(json.dumps(res))
    return res

print("=" * 70)
print("PART B - STOCKS-EVE-15: INV-ABOVE stop S050 -> S080 (T125 kept), full_hist rescan")
def entry_open(sym, day, et):
    for t, o, h, l, c in bars(FULL, sym, day):
        if t == et:
            return o
    return None
repro_exact = repro_close = missing = 0
base_scan, var_scan = [], []
for r in ALL:
    e = entry_open(r["stock"], r["date"], r["entry_time"])
    if e is None:
        missing += 1
        continue
    bb = bars(FULL, r["stock"], r["date"])
    for sp, acc in ((0.0050, base_scan), (0.0080, var_scan)):
        s2, t2 = levels(e, "LONG", sp, 0.0125)
        xt, xp, xr, mfe, mae = scan(bb, r["entry_time"], e, s2, t2, "LONG")
        if xp is None:
            continue
        acc.append({"date": r["date"], "stock": r["stock"], "net": net_of(e, xp, "LONG"),
                    "exit_reason": xr})
    if base_scan and base_scan[-1]["date"] == r["date"] and base_scan[-1]["stock"] == r["stock"]:
        dn = abs(base_scan[-1]["net"] - r["net"])
        if dn <= 0.51:
            repro_exact += 1
        if dn <= 5.0:
            repro_close += 1
print(json.dumps({"population": len(ALL), "missing_candles": missing,
                  "repro_within_0.51": repro_exact, "repro_within_5": repro_close,
                  "stored_base": summ(ALL), "rescan_base_S050": summ(base_scan),
                  "variant_S080": summ(var_scan),
                  "halves_base_scan": halves(base_scan), "halves_variant": halves(var_scan),
                  "ex_top3_base_scan": ex_top3(base_scan), "ex_top3_variant": ex_top3(var_scan),
                  "month_flips_scan": flips(base_scan, var_scan),
                  "month_table_base_scan": months(base_scan),
                  "month_table_variant": months(var_scan),
                  "stops_base": sum(1 for x in base_scan if x["exit_reason"] == "stop"),
                  "stops_variant": sum(1 for x in var_scan if x["exit_reason"] == "stop"),
                  "targets_base": sum(1 for x in base_scan if x["exit_reason"] == "target"),
                  "targets_variant": sum(1 for x in var_scan if x["exit_reason"] == "target")}))

print("=" * 70)
print("PART C - STOCKS-EVE-16: drop INV-ABOVE rows whose stock had a P2F-family leg same day")
fam_days = {}
for yr in BOOKS:
    s = set()
    for r in BOOKS[yr]:
        if r["comp"] in ("P2F", "P2F-R2", "R2-LOWBAND"):
            s.add((r["date"], r["stock"]))
    fam_days[yr] = s
# tag each INV row with its year via date prefix
for r in ALL:
    r["_yr"] = r["date"][:4]
gate_drop("EVE-16_drop_INV_if_P2Ffamily_same_stock_day",
          lambda r: (r["date"], r["stock"]) in fam_days[r["_yr"]])

print("=" * 70)
print("PART D - STOCKS-EVE-17: INV-ABOVE registry deletion of GLENMARK only")
gate_drop("EVE-17_drop_INV Glenmark".replace(" ", "_"),
          lambda r: r["stock"] == "GLENMARK")
