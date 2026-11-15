#!/usr/bin/env python3
"""Stocks evening engine 2026-11-05.
Part A: candle-verified detail for today's (2026-11-05) SarvaRitu book trades
from data/sarvaritu_fwd candles, both geometries where they diverge
(N4-V3: book T150/S080 vs scorecard T125/S050), plus TUNED SHADOW v1 scoring.
Part B: STOCKS-EVE-09 — P2F family: drop all R+2 legs (P2F-R2 + R2-LOWBAND),
tested on the stored 87-trade family files AND cross-year on the c24 dumps.
Part C: STOCKS-EVE-10 — P2F family: widen stop to 0.80% (target T125 kept),
rescanned from data/full_hist candles; scanner must first reproduce the
stored 87-trade baseline (+Rs27,293.58). Mirror control: stop 0.35%.
Part D: STOCKS-EVE-11 — N4-V3 standalone: T125 target with S080 stop (the
geometry PFC proved today), rescanned from full_hist on the 56-trade ch2
population; scanner validated against the file's src T125/S050 nets.
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

def scan(bars_, entry_time, entry, stop, target, direction):
    """Frozen convention: scan from the bar AFTER the entry bar; stop before
    target if both touched in one bar; square-off 15:10 close."""
    started = False
    mfe = mae = None
    for t, o, h, l, c in bars_:
        if t == entry_time:
            started = True
            continue
        if not started or t > "15:10":
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

# ---------------- Part A ----------------
print("=" * 70)
print("PART A - today 2026-11-05, candle-verified (fwd root)")
# comp, stock, dir, entry_time, entry, logged_book_net
BOOK = [
    ("P2F-R2", "ITC", "LONG", "09:15", 283.10, -181.55),
    ("P2F-R2", "NATIONALUM", "SHORT", "09:15", 328.80, -204.40),
    ("N4-V3", "NHPC", "LONG", "09:35", 81.29, -105.03),
    ("N4-V3", "PFC", "LONG", "09:35", 325.85, 448.77),
]
for comp, sym, d, et, entry, logged in BOOK:
    b = bars(FWD, sym, "2026-11-05")
    geoms = [("book", 0.0080, 0.0150)] if comp == "N4-V3" else [("family", 0.0050, 0.0125)]
    if comp == "N4-V3":
        geoms.append(("scorecard", 0.0050, 0.0125))
    for gname, sp, tp in geoms:
        stop, tgt = levels(entry, d, sp, tp)
        xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
        n = net_of(entry, xp, d) if xp is not None else None
        print(json.dumps({"comp": comp, "stock": sym, "dir": d, "geom": gname,
                          "entry_time": et, "entry": entry, "stop": stop, "target": tgt,
                          "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                          "net_recomputed": n, "net_logged_book": logged if gname in ("book", "family") else None,
                          "mfe_rs": round(mfe, 2) if mfe is not None else None,
                          "mae_rs": round(mae, 2) if mae is not None else None}))
# HINDCOPPER INV-ABOVE: derive entry from the 10:25 bar open in fwd candles
b = bars(FWD, "HINDCOPPER", "2026-11-05")
opens = {t: o for t, o, h, l, c in b}
entry_hc = opens.get("10:25")
print("HINDCOPPER 10:25 bar open:", entry_hc, "| book logged exit 431.98 net -257.07")
if entry_hc:
    for cand_entry in (entry_hc, round(431.98 / 0.995, 2)):
        stop, tgt = levels(cand_entry, "LONG", 0.0050, 0.0125)
        xt, xp, xr, mfe, mae = scan(b, "10:25", cand_entry, stop, tgt, "LONG")
        print(json.dumps({"comp": "INV-ABOVE", "stock": "HINDCOPPER", "entry_try": cand_entry,
                          "stop": stop, "target": tgt, "exit_time": xt, "exit_price": xp,
                          "exit_reason": xr, "net_recomputed": net_of(cand_entry, xp, "LONG") if xp else None,
                          "mfe_rs": round(mfe, 2) if mfe is not None else None,
                          "mae_rs": round(mae, 2) if mae is not None else None}))
# Nifty regime context for today: prior close (2026-11-04) vs 50DMA
daily = sorted([(r["date"], float(r["close"])) for r in csv.DictReader(open(FWD / "NIFTY" / "spot_daily.csv"))])
idx = [i for i, (d, _) in enumerate(daily) if d == "2026-11-05"][0]
prev_close = daily[idx - 1][1]
ma50 = sum(c for _, c in daily[idx - 50:idx]) / 50
print(json.dumps({"nifty_2026-11-04_close": prev_close, "nifty_50dma_at_11-05": round(ma50, 2),
                  "regime": "FLAT/above" if prev_close > ma50 else "DOWN"}))

# ---------------- shared summaries ----------------
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

# ---------------- Part B: EVE-09 ----------------
print("=" * 70)
print("PART B - STOCKS-EVE-09: drop R+2 legs (P2F-R2 + R2-LOWBAND) from P2F family")
FAMILY_FILES = [("stocks_engine_ch1_p2fprofile_trades.csv", "net", "P2F"),
                ("stocks_engine_sat13_p2fr2_trades.csv", "net_rs", "P2F-R2"),
                ("stocks_engine_sat33_r2lowband_trades.csv", "net_rs", "R2-LOWBAND")]
fam = []
for f, col, leg in FAMILY_FILES:
    for r in csv.DictReader(open(WS / f)):
        fam.append({"date": r["date"], "stock": r.get("symbol"), "leg": leg,
                    "net": float(r[col]), "exit_reason": r["exit_reason"],
                    "exit_time": r["exit_time"], "entry_time": r["entry_time"]})
fam.sort(key=lambda r: r["date"])
kept9 = [r for r in fam if r["leg"] == "P2F"]
dropped9 = [r for r in fam if r["leg"] != "P2F"]
print(json.dumps({"family_base": summ(fam), "variant_R1_only": summ(kept9),
                  "dropped_R2_legs": summ(dropped9),
                  "halves_base": halves(fam), "halves_variant": halves(kept9),
                  "ex_top3_base": ex_top3(fam), "ex_top3_variant": ex_top3(kept9),
                  "month_flips": flips(fam, kept9),
                  "placebo_chrono_skip_same_n": summ(fam[len(dropped9):]),
                  "quick_stops_base": sum(1 for r in fam if r["exit_reason"] == "stop" and r["exit_time"] <= "09:30"),
                  "quick_stops_variant": sum(1 for r in kept9 if r["exit_reason"] == "stop" and r["exit_time"] <= "09:30")}))
for yr in ("2025", "2026"):
    book = list(csv.DictReader(open(WS / f"stocks_engine_v2_c24_book{yr}_trades.csv")))
    fam_y = [r for r in book if r["comp"] in ("P2F", "P2F-R2", "R2-LOWBAND")]
    kept_y = [r for r in fam_y if r["comp"] == "P2F"]
    drop_y = [r for r in fam_y if r["comp"] != "P2F"]
    print(json.dumps({"cross_year": yr, "family_base": summ(fam_y), "variant": summ(kept_y),
                      "dropped": summ(drop_y)}))

# ---------------- Part C: EVE-10 ----------------
print("=" * 70)
print("PART C - STOCKS-EVE-10: P2F family stop -> 0.80% (T125 kept), candle rescan")
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
def rescan_family(stop_override=None, mirror=None):
    out, missing = [], 0
    for r in raw:
        b = bars(FULL, r["stock"], r["date"])
        if not b:
            missing += 1
            continue
        sp = mirror if mirror is not None else (stop_override if stop_override is not None else r["stop_pct"])
        stop, tgt = levels(r["entry"], r["dir"], sp, 0.0125)
        xt, xp, xr, mfe, mae = scan(b, r["entry_time"], r["entry"], stop, tgt, r["dir"])
        if xp is None:
            missing += 1
            continue
        out.append({"date": r["date"], "net": net_of(r["entry"], xp, r["dir"]),
                    "exit_reason": xr, "exit_time": xt})
    return out, missing
base_scan, miss0 = rescan_family()
var_scan, miss1 = rescan_family(stop_override=0.0080)
mir_scan, miss2 = rescan_family(mirror=0.0035)
print(json.dumps({"rescan_baseline": summ(base_scan), "missing": miss0,
                  "variant_S080": summ(var_scan), "missing_v": miss1,
                  "mirror_S035_placebo": summ(mir_scan),
                  "halves_base": halves(base_scan), "halves_variant": halves(var_scan),
                  "ex_top3_base": ex_top3(base_scan), "ex_top3_variant": ex_top3(var_scan),
                  "month_flips": flips(base_scan, var_scan),
                  "stops_base": sum(1 for r in base_scan if r["exit_reason"] == "stop"),
                  "stops_variant": sum(1 for r in var_scan if r["exit_reason"] == "stop")}))

# ---------------- Part D: EVE-11 ----------------
print("=" * 70)
print("PART D - STOCKS-EVE-11: N4-V3 standalone T125 with stop S050 -> S080, candle rescan")
n4 = []
for r in csv.DictReader(open(WS / "stocks_engine_ch2_n4_trades.csv")):
    n4.append({"date": r["date"], "stock": r["stock"], "dir": r["direction"],
               "entry_time": r["entry_time"], "entry": float(r["entry"]),
               "src_T125S050": float(r["src_net_T125S050"]), "book_net": float(r["net"])})
print("ch2 sums:", json.dumps({"book_T150S080_stored": round(sum(r["book_net"] for r in n4), 2),
                              "src_T125S050_stored": round(sum(r["src_T125S050"] for r in n4), 2)}))
def rescan_n4(sp, tp):
    out, missing = [], 0
    for r in n4:
        b = bars(FULL, r["stock"], r["date"])
        if not b:
            missing += 1
            continue
        stop, tgt = levels(r["entry"], r["dir"], sp, tp)
        xt, xp, xr, mfe, mae = scan(b, r["entry_time"], r["entry"], stop, tgt, r["dir"])
        if xp is None:
            missing += 1
            continue
        out.append({"date": r["date"], "net": net_of(r["entry"], xp, r["dir"]), "exit_reason": xr})
    return out, missing
chk, m_chk = rescan_n4(0.0050, 0.0125)
var11, m_var = rescan_n4(0.0080, 0.0125)
mir11, m_mir = rescan_n4(0.0035, 0.0125)
bookchk, m_bk = rescan_n4(0.0080, 0.0150)
print(json.dumps({"scanner_check_T125S050_rescan": summ(chk), "missing": m_chk,
                  "book_geom_T150S080_rescan": summ(bookchk),
                  "variant_T125S080": summ(var11), "mirror_T125S035_placebo": summ(mir11),
                  "halves_check": halves(chk), "halves_variant": halves(var11),
                  "ex_top3_check": ex_top3(chk), "ex_top3_variant": ex_top3(var11),
                  "month_flips_vs_T125S050": flips(chk, var11)}))
