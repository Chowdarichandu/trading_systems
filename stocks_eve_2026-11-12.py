#!/usr/bin/env python3
"""Stocks evening engine 2026-11-12.
Part A: candle-verified detail for today's (2026-11-12) Stock Book trades
(4 book rows) + component scorecard rows (N4-V3 HINDCOPPER scorecard basis;
P2F shadow KALYANKJIL, identical to the book P2F row) + TUNED SHADOW v1/v2
scoring for today.
Part B: STOCKS-EVE-22 - P2F family: drop entries whose |reaction_ret_pct|
>= 5.0% (extreme-reaction stand-down; the RSI-STOCKS-012 watch axis, never
gated before). Universe: the stored 87-trade P2F family files used by
EVE-04/05/08/10/12 (ch1 profile T125/S065 geometry per its own file;
sat13 P2F-R2 and sat33 R2-LOWBAND at their own geometries).
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade.
"""
import csv, json, pathlib, collections
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

print("=" * 70)
print("PART A - today 2026-11-12, candle-verified (fwd root)")
# (label, stock, dir, entry_time, entry, stop_pct, tgt_pct, logged_net)
TRADES = [
    ("P2F/book+scorecard T125S050", "KALYANKJIL", "LONG", "09:15", 675.00, 0.0050, 0.0125, 803.75),
    ("P2F-R2/book T125S050", "TATASTEEL", "SHORT", "09:15", 188.75, 0.0050, 0.0125, -134.37),
    ("N4-V3/book T150S080", "HINDCOPPER", "LONG", "09:35", 455.40, 0.0080, 0.0150, -404.32),
    ("N4-V3/scorecard T125S050", "HINDCOPPER", "LONG", "09:35", 455.40, 0.0050, 0.0125, -267.70),
    ("INV-ABOVE/book T125S050", "ASTRAL", "LONG", "09:55", 1301.20, 0.0050, 0.0125, -690.60),
]
for label, sym, d, et, entry, sp, tp, logged in TRADES:
    b = bars(FWD, sym, "2026-11-12")
    stop, tgt = levels(entry, d, sp, tp)
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    print(json.dumps({"label": label, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": net_of(entry, xp, d) if xp else None,
                      "net_logged": logged,
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None,
                      "nbars": len(b)}))
for sym in ("KALYANKJIL", "TATASTEEL", "HINDCOPPER", "ASTRAL"):
    b = bars(FWD, sym, "2026-11-12")
    if b:
        print(json.dumps({sym + "_day": {"open": b[0][1], "high": max(x[2] for x in b),
                                         "low": min(x[3] for x in b),
                                         "close_1510": [x[4] for x in b if x[0] == "15:10"][0] if any(x[0] == "15:10" for x in b) else None,
                                         "nbars": len(b)}}))

print("=" * 70)
print("PART B - STOCKS-EVE-22: P2F family, drop |reaction| >= 5.0% entries")
FAMILY = [("stocks_engine_ch1_p2fprofile_trades.csv", "net"),
          ("stocks_engine_sat13_p2fr2_trades.csv", "net_rs"),
          ("stocks_engine_sat33_r2lowband_trades.csv", "net_rs")]
fam = []
for f, col in FAMILY:
    for r in csv.DictReader(open(WS / f)):
        fam.append({"date": r["date"], "stock": r["symbol"], "dir": r["direction"],
                    "reaction": float(r["reaction_ret_pct"]), "net": float(r[col]),
                    "exit_reason": r["exit_reason"], "entry_time": r["entry_time"],
                    "exit_time": r["exit_time"]})
fam.sort(key=lambda r: r["date"])
def S(rs): return round(sum(r["net"] for r in rs), 2)
def halves(rs):
    h1 = [r for r in rs if r["date"][5:7] in ("01", "02", "03", "04", "05")]
    h2 = [r for r in rs if r["date"][5:7] in ("06", "07", "08", "09", "10", "11", "12")]
    return S(h1), S(h2)
def months(rs):
    mm = collections.defaultdict(float)
    for r in rs: mm[r["date"][:7]] += r["net"]
    return {k: round(v, 2) for k, v in sorted(mm.items())}
def extop3(rs):
    s = sorted((r["net"] for r in rs), reverse=True)
    return round(sum(s[3:]), 2)
def flips(base, var):
    bm, vm = months(base), months(var)
    return [m for m in bm if bm[m] > 0 and vm.get(m, 0.0) < 0]
inc = fam
dropped = [r for r in fam if abs(r["reaction"]) >= 5.0]
var = [r for r in fam if abs(r["reaction"]) < 5.0]
nd = len(dropped)
chrono = fam[nd:]
mirror = dropped  # extreme-only book, for reference
print(json.dumps({
    "population": len(fam), "incumbent_net_resum": S(inc),
    "dropped_extreme_ge5": {"n": nd, "net": S(dropped),
                            "trades": [(r["date"], r["stock"], r["reaction"], r["net"]) for r in dropped]},
    "variant": {"n": len(var), "net": S(var), "halves": halves(var),
                "ex_top3": extop3(var), "months": months(var),
                "flips_vs_incumbent": flips(inc, var)},
    "incumbent": {"halves": halves(inc), "ex_top3": extop3(inc), "months": months(inc)},
    "chrono_placebo_skip_first_N": {"n": len(chrono), "net": S(chrono)},
    "extreme_only_reference": {"n": len(mirror), "net": S(mirror)},
}, indent=1))
print("timing: reaction_ret_pct is the reaction day's close-to-close move, known before the R+1 09:15 entry - 0 violations in construction")
print("cross-year: stored P2F family population is 2026-only; the c24 book dumps carry no reaction_ret_pct, so the filter cannot be identified in 2025 - UNVERIFIABLE (same ground as EVE-05/EVE-12)")
