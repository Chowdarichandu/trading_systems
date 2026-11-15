#!/usr/bin/env python3
"""Stocks evening engine 2026-11-06.
Part A: candle-verified detail for today's (2026-11-06) SarvaRitu book trades
(4 book trades, all winners) + today's scorecard trades (N4-V3 ASTRAL SHORT,
P2F shadow NHPC/PFC) + TUNED SHADOW v1 scoring (ASTRAL SHORT uncapped -> taken).
Part B: STOCKS-EVE-12 - P2F family: tighten stop to 0.35% (T125 kept),
rescanned from data/full_hist; the registered follow-up to EVE-10's mirror
control observation (+Rs30,744.00). Scanner must first reproduce the stored
87-trade baseline (+Rs27,293.58).
Part C: STOCKS-EVE-13 - INV-ABOVE: drop 2nd+ same-stock same-day entries
(c24 dumps, both years; pure drop filter on stored nets).
Part D: STOCKS-EVE-14 - INV-ABOVE: skip entries whose stock traded INV-ABOVE
on the prior trading day (follow-through exhaustion, Lesson RSI-STOCKS-008;
c24 dumps, both years).
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
    h2 = [r for r in rows if r["date"][5:7] in ("06", "07", "08", "09", "10")]
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
print("PART A - today 2026-11-06, candle-verified (fwd root)")
# Book INV-ABOVE entries are the entry bar's open (verified identity:
# net = (target - open)*100 - 40 for all three target exits).
BOOK = [
    ("P2F", "NHPC", "LONG", "09:15", 80.60, 60.75),
    ("INV-ABOVE", "GLENMARK", "LONG", "09:35", 2486.60, 3068.25),
    ("INV-ABOVE", "RECLTD", "LONG", "09:35", 296.25, 330.31),
    ("INV-ABOVE", "GLENMARK", "LONG", "09:55", 2526.70, 3118.37),
]
for comp, sym, d, et, entry, logged in BOOK:
    b = bars(FWD, sym, "2026-11-06")
    stop, tgt = levels(entry, d, 0.0050, 0.0125)
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    n = net_of(entry, xp, d) if xp is not None else None
    print(json.dumps({"comp": comp, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": n, "net_logged_book": logged,
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None}))
# Day continuation past the GLENMARK exits (give-back / exit-tuning evidence)
for sym, et, entry in (("GLENMARK", "09:35", 2486.60), ("GLENMARK", "09:55", 2526.70),
                       ("RECLTD", "09:35", 296.25), ("NHPC", "09:15", 80.60)):
    b = bars(FWD, sym, "2026-11-06")
    day_hi = max(h for _, _, h, _, _ in b)
    print(json.dumps({"continuation": sym, "day_high": day_hi,
                      "beyond_entry_rs": round((day_hi - entry) * 100, 2)}))
# Scorecard trades today
print("-- scorecards --")
# P2F shadow PFC stop (from stocks_p2f_november_shadow_log.csv)
b = bars(FWD, "PFC", "2026-11-06")
stop, tgt = levels(328.50, "LONG", 0.0050, 0.0125)
xt, xp, xr, mfe, mae = scan(b, "09:15", 328.50, stop, tgt, "LONG")
print(json.dumps({"comp": "P2F-SHADOW", "stock": "PFC", "entry": 328.50, "stop": stop,
                  "target": tgt, "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                  "net_recomputed": net_of(328.50, xp, "LONG"),
                  "mfe_rs": round(mfe, 2), "mae_rs": round(mae, 2)}))
# N4-V3 scorecard ASTRAL SHORT: entry = 09:25 close 1249.20 recorded 09:35;
# the frozen log scans FROM the 09:35 bar (stop-first). Scorecard T125/S050
# result is the log's own (+1521.50); book geometry T150/S080 computed here
# for the TUNED SHADOW v1 book-basis line (SHORT uncapped -> taken).
b = bars(FWD, "ASTRAL", "2026-11-06")
for gname, sp, tp in (("scorecard", 0.0050, 0.0125), ("book", 0.0080, 0.0150)):
    stop, tgt = levels(1249.20, "SHORT", sp, tp)
    xt, xp, xr, mfe, mae = scan(b, "09:35", 1249.20, stop, tgt, "SHORT", include_entry=True)
    print(json.dumps({"comp": "N4-V3", "stock": "ASTRAL", "geom": gname, "entry": 1249.20,
                      "stop": stop, "target": tgt, "exit_time": xt, "exit_price": xp,
                      "exit_reason": xr, "net_recomputed": net_of(1249.20, xp, "SHORT"),
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None}))
# Regime: prior close (2026-11-05) vs 50DMA
daily = sorted([(r["date"], float(r["close"])) for r in csv.DictReader(open(FWD / "NIFTY" / "spot_daily.csv"))])
idx = [i for i, (d, _) in enumerate(daily) if d == "2026-11-06"][0]
prev_close = daily[idx - 1][1]
ma50 = sum(c for _, c in daily[idx - 50:idx]) / 50
print(json.dumps({"nifty_2026-11-05_close": prev_close, "nifty_50dma_at_11-06": round(ma50, 2),
                  "regime": "FLAT/above" if prev_close > ma50 else "DOWN"}))

# ---------------- Part B: EVE-12 ----------------
print("=" * 70)
print("PART B - STOCKS-EVE-12: P2F family stop tightened to 0.35% (T125 kept), rescan")
FAM_RAW = [("stocks_engine_ch1_p2fprofile_trades.csv", "net", 0.0065),
           ("stocks_engine_sat13_p2fr2_trades.csv", "net_rs", 0.0050),
           ("stocks_engine_sat33_r2lowband_trades.csv", "net_rs", 0.0050)]
raw = []
for f, col, sp in FAM_RAW:
    for r in csv.DictReader(open(WS / f)):
        raw.append({"date": r["date"], "stock": r["symbol"], "dir": r["direction"],
                    "entry_time": r["entry_time"], "entry": float(r["entry"]),
                    "stored_net": float(r[col]), "stop_pct": sp})
print("stored baseline re-sum:", summ([{"net": r["stored_net"]} for r in raw], "net"))
def rescan_family(stop_override=None):
    out, missing = [], 0
    for r in raw:
        b = bars(FULL, r["stock"], r["date"])
        if not b:
            missing += 1
            continue
        sp = stop_override if stop_override is not None else r["stop_pct"]
        stop, tgt = levels(r["entry"], r["dir"], sp, 0.0125)
        xt, xp, xr, mfe, mae = scan(b, r["entry_time"], r["entry"], stop, tgt, r["dir"])
        if xp is None:
            missing += 1
            continue
        out.append({"date": r["date"], "net": net_of(r["entry"], xp, r["dir"]),
                    "exit_reason": xr, "exit_time": xt})
    return out, missing
base_scan, miss0 = rescan_family()
var_scan, miss1 = rescan_family(stop_override=0.0035)
print(json.dumps({"rescan_baseline": summ(base_scan), "missing": miss0,
                  "variant_S035": summ(var_scan), "missing_v": miss1,
                  "halves_base": halves(base_scan), "halves_variant": halves(var_scan),
                  "ex_top3_base": ex_top3(base_scan), "ex_top3_variant": ex_top3(var_scan),
                  "month_table_base": months(base_scan), "month_table_variant": months(var_scan),
                  "month_flips": flips(base_scan, var_scan),
                  "stops_base": sum(1 for r in base_scan if r["exit_reason"] == "stop"),
                  "stops_variant": sum(1 for r in var_scan if r["exit_reason"] == "stop"),
                  "targets_base": sum(1 for r in base_scan if r["exit_reason"] == "target"),
                  "targets_variant": sum(1 for r in var_scan if r["exit_reason"] == "target")}))

# ---------------- Parts C/D: INV-ABOVE c24 drop filters ----------------
def load_inv():
    out = {}
    for yr in ("2025", "2026"):
        rows = [r for r in csv.DictReader(open(WS / f"stocks_engine_v2_c24_book{yr}_trades.csv"))
                if r["comp"] == "INV-ABOVE"]
        rows.sort(key=lambda r: (r["date"], r["entry_time"]))
        for r in rows:
            r["net"] = float(r["net"])
        out[yr] = rows
    return out
INV = load_inv()
ALL = INV["2025"] + INV["2026"]
print("INV-ABOVE universe:", {y: summ(INV[y]) for y in INV}, "combined", summ(ALL))

print("=" * 70)
print("PART C - STOCKS-EVE-13: drop 2nd+ same-stock same-day INV-ABOVE entries")
def gate_drop(name, drop_pred, placebo_pred):
    kept = [r for r in ALL if not drop_pred(r)]
    dropped = [r for r in ALL if drop_pred(r)]
    plac = [r for r in ALL if not placebo_pred(r)]
    res = {"candidate": name, "base": summ(ALL), "variant": summ(kept),
           "dropped": summ(dropped), "placebo_variant": summ(plac),
           "halves_base": halves(ALL), "halves_variant": halves(kept),
           "ex_top3_base": ex_top3(ALL), "ex_top3_variant": ex_top3(kept),
           "month_flips": flips(ALL, kept),
           "month_table_base": months(ALL), "month_table_variant": months(kept)}
    for yr in ("2025", "2026"):
        ky = [r for r in INV[yr] if not drop_pred(r)]
        dy = [r for r in INV[yr] if drop_pred(r)]
        res[f"yr_{yr}"] = {"base": summ(INV[yr]), "variant": summ(ky), "dropped": summ(dy),
                           "flips": flips(INV[yr], ky)}
    print(json.dumps(res))
    return res

repeat_flags, first_of_repeat_flags = {}, {}
for yr in ("2025", "2026"):
    c = collections.Counter()
    for r in INV[yr]:
        key = (r["date"], r["stock"])
        c[key] += 1
        repeat_flags[id(r)] = c[key] >= 2
    day_counts = collections.Counter((r["date"], r["stock"]) for r in INV[yr])
    c2 = collections.Counter()
    for r in INV[yr]:
        key = (r["date"], r["stock"])
        c2[key] += 1
        # mirror placebo: drop the FIRST entry of each stock-day that has repeats
        first_of_repeat_flags[id(r)] = c2[key] == 1 and day_counts[key] >= 2
gate_drop("EVE-13_drop_repeat_same_day",
          lambda r: repeat_flags[id(r)],
          lambda r: first_of_repeat_flags[id(r)])
# NOTE placebo = drop the FIRST entry of each repeated stock-day (mirror)

print("=" * 70)
print("PART D - STOCKS-EVE-14: skip INV-ABOVE if same stock traded INV-ABOVE prior trading day")
for yr in ("2025", "2026"):
    days = sorted({r["date"] for r in INV[yr]})
    prev_day = {days[i]: days[i - 1] for i in range(1, len(days))}
    traded = collections.defaultdict(set)
    for r in INV[yr]:
        traded[r["date"]].add(r["stock"])
    for r in INV[yr]:
        pd_ = prev_day.get(r["date"])
        r["_exhaust"] = bool(pd_ and r["stock"] in traded.get(pd_, set()))
gate_drop("EVE-14_skip_after_prior_day_trade",
          lambda r: r.get("_exhaust", False),
          lambda r: False)  # placebo replaced below by chrono skip
# Chronological placebo for EVE-14: skip the same NUMBER of earliest entries overall
n_drop14 = sum(1 for r in ALL if r.get("_exhaust"))
chrono_kept = ALL[n_drop14:]
print(json.dumps({"EVE-14_placebo_chrono_skip_first_N": summ(chrono_kept), "n_dropped": n_drop14}))
