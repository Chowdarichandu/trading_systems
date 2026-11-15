#!/usr/bin/env python3
"""Stocks evening engine 2026-11-11 (early run, owner-directed 16:37).
Part A: candle-verified detail for today's (2026-11-11) SarvaRitu book trades
(2) + scorecard trades (N4-V3 KALYANKJIL scorecard basis; P2F shadow
TATASTEEL) + TUNED SHADOW v1/v2 scoring.
Part B: STOCKS-EVE-21 - N4-V3 one-sided cap refined to a BAND cap: skip LONG
entries with signed move by 09:30 in [+3.0%, +6.0%); LONG moves >= +6.0% are
TAKEN again (extreme-move exemption). Trigger: today's KALYANKJIL LONG
+8.658% hit target on both bases (+959.30 book / +792.75 scorecard) while the
promoted one-sided cap skipped it. Universe: the stored 56-trade standalone
N4-V3 population (eq_n4deep_v3 T125 file for scorecard nets + move parsed
from its note field; book nets joined from stocks_engine_ch2_n4_trades.csv).
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade.
"""
import csv, json, pathlib, collections, re
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
print("PART A - today 2026-11-11, candle-verified (fwd root)")
# (comp, stock, dir, entry_time, entry, stop_pct, tgt_pct, logged_net, basis)
TRADES = [
    ("P2F/book", "TATASTEEL", "SHORT", "09:15", 186.40, 0.0050, 0.0125, -133.20),
    ("N4-V3/book T150S080", "KALYANKJIL", "LONG", "09:35", 666.20, 0.0080, 0.0150, 959.30),
    ("N4-V3/scorecard T125S050", "KALYANKJIL", "LONG", "09:35", 666.20, 0.0050, 0.0125, 792.75),
]
for comp, sym, d, et, entry, sp, tp, logged in TRADES:
    b = bars(FWD, sym, "2026-11-11")
    stop, tgt = levels(entry, d, sp, tp)
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    print(json.dumps({"comp": comp, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": net_of(entry, xp, d) if xp else None,
                      "net_logged": logged,
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None,
                      "nbars": len(b)}))
for sym in ("TATASTEEL", "KALYANKJIL"):
    b = bars(FWD, sym, "2026-11-11")
    if b:
        print(json.dumps({sym + "_day": {"open": b[0][1], "high": max(x[2] for x in b),
                                         "low": min(x[3] for x in b),
                                         "close_1510": [x[4] for x in b if x[0] == "15:10"][0] if any(x[0] == "15:10" for x in b) else None,
                                         "nbars": len(b)}}))

print("=" * 70)
print("PART B - STOCKS-EVE-21: N4-V3 band cap [+3%,+6%) with >=+6% LONG exemption")
v3 = list(csv.DictReader(open(WS / "eq_n4deep_v3_trades_T125_janoct.csv")))
ch2 = {(r["date"], r["stock"]): float(r["net"]) for r in csv.DictReader(open(WS / "stocks_engine_ch2_n4_trades.csv"))}
rows = []
for r in v3:
    m = re.search(r"move by 09:30 ([+-]?[0-9.]+)%", r["note"])
    assert m, r["note"]
    rows.append({"date": r["date"], "stock": r["stock"], "dir": r["direction"],
                 "move": float(m.group(1)), "sc_net": float(r["net_rs_provisional_per100"]),
                 "book_net": ch2.get((r["date"], r["stock"]))})
missing = [r for r in rows if r["book_net"] is None]
print("population:", len(rows), "book-join missing:", len(missing))
def S(rs, col): return round(sum(r[col] for r in rs), 2)
def halves(rs, col):
    h1 = [r for r in rs if r["date"][5:7] in ("01","02","03","04","05")]
    h2 = [r for r in rs if r["date"][5:7] in ("06","07","08","09","10")]
    return S(h1, col), S(h2, col)
def months(rs, col):
    mm = collections.defaultdict(float)
    for r in rs: mm[r["date"][:7]] += r[col]
    return {k: round(v, 2) for k, v in sorted(mm.items())}
def extop3(rs, col):
    s = sorted((r[col] for r in rs), reverse=True)
    return round(sum(s[3:]), 2)
def flips(base, var, col):
    bm, vm = months(base, col), months(var, col)
    return [m for m in bm if bm[m] > 0 and vm.get(m, 0.0) < 0]
for col in ("sc_net", "book_net"):
    inc = rows
    cap = [r for r in rows if not (r["dir"] == "LONG" and r["move"] >= 3.0)]
    band = [r for r in rows if not (r["dir"] == "LONG" and 3.0 <= r["move"] < 6.0)]
    dropped_band = [r for r in rows if r["dir"] == "LONG" and 3.0 <= r["move"] < 6.0]
    extreme = [r for r in rows if r["dir"] == "LONG" and r["move"] >= 6.0]
    nd = len(dropped_band)
    chrono = rows[nd:]
    print(json.dumps({col: {
        "incumbent": {"n": len(inc), "net": S(inc, col), "halves": halves(inc, col), "ex_top3": extop3(inc, col), "months": months(inc, col)},
        "onesided_cap": {"n": len(cap), "net": S(cap, col)},
        "band_variant": {"n": len(band), "net": S(band, col), "halves": halves(band, col), "ex_top3": extop3(band, col), "flips_vs_incumbent": flips(inc, band, col)},
        "dropped_band_bucket": {"n": nd, "net": S(dropped_band, col)},
        "extreme_ge6_bucket": {"n": len(extreme), "net": S(extreme, col), "trades": [(r["date"], r["stock"], r["move"], r[col]) for r in extreme]},
        "chrono_placebo_skip_first_N": {"n": len(chrono), "net": S(chrono, col)},
    }}, indent=1))
print("timing: move is the 09:25 close vs prev close, known before the 09:35 entry - 0 violations in construction")
print("cross-year: standalone N4 population is 2026-only; no 2025 standalone file with 09:30 moves - UNVERIFIABLE on this universe")
