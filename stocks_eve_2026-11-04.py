#!/usr/bin/env python3
"""Stocks evening engine 2026-11-04.
Part A: candle-verified detail (entry/exit/MFE/MAE) for today's SarvaRitu book
trades + P2F scorecard identity check, from data/sarvaritu_fwd candles.
Part B: STOCKS-EVE-06 (INV-ABOVE rupee-stop cap: skip entry price >= 1500) and
STOCKS-EVE-07 (INV-ABOVE late-entry cut: skip entry_time >= 10:00) gated on the
c24 whole-book dumps (2025 + 2026 INV-ABOVE populations; entry prices for EVE-06
from data/full_hist 5m bar opens at entry_time).
Part C: STOCKS-EVE-08 (P2F family target T125 -> T100, stops unchanged per file)
rescanned from data/full_hist candles; scanner must first reproduce the stored
87-trade baseline (+27,293.58) before the variant is scored.
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

# ---------------- Part A ----------------
print("=" * 70)
print("PART A — today 2026-11-04, candle-verified (fwd root)")
TRADES = [
    # comp, stock, dir, entry_time, entry, stop, target, logged_net
    ("P2F", "ITC", "LONG", "09:15", 272.90, 271.54, 276.31, 301.12),
    ("P2F", "NATIONALUM", "SHORT", "09:15", 317.55, 319.14, 313.58, -198.77),
    ("R2-LOWBAND", "NTPC", "LONG", "09:15", 320.00, 318.40, 324.00, -200.00),
    ("INV-ABOVE", "HINDCOPPER", "LONG", "09:35", 400.10, 398.10, 405.10, 460.12),
    ("INV-ABOVE", "GLENMARK", "LONG", "10:10", 2418.20, 2406.11, 2448.43, -1249.10),
    ("INV-ABOVE", "HINDCOPPER", "LONG", "10:20", 404.55, 402.53, 409.61, 465.69),
]
for comp, sym, d, et, entry, stop, tgt, logged in TRADES:
    b = bars(FWD, sym, "2026-11-04")
    xt, xp, xr, mfe, mae = scan(b, et, entry, stop, tgt, d)
    n = net_of(entry, xp, d) if xp is not None else None
    print(json.dumps({"comp": comp, "stock": sym, "dir": d, "entry_time": et,
                      "entry": entry, "stop": stop, "target": tgt,
                      "exit_time": xt, "exit_price": xp, "exit_reason": xr,
                      "net_recomputed": n, "net_logged": logged,
                      "match": (n is not None and abs(n - logged) <= 1.0),
                      "mfe_rs": round(mfe, 2) if mfe is not None else None,
                      "mae_rs": round(mae, 2) if mae is not None else None}))
# NATIONALUM T10 shadow check (target 314.37 = entry -1.0%)
b = bars(FWD, "NATIONALUM", "2026-11-04")
xt, xp, xr, mfe, mae = scan(b, "09:15", 317.55, 319.14, 314.37, "SHORT")
print("NATIONALUM T10 shadow rescan:", xt, xp, xr, net_of(317.55, xp, "SHORT"),
      "(scorecard logged +277.55)")
# Nifty context: prior close vs 50DMA from fwd daily
daily = [(r["date"], float(r["close"])) for r in csv.DictReader(open(FWD / "NIFTY" / "spot_daily.csv"))]
daily.sort()
idx = [i for i, (d, _) in enumerate(daily) if d == "2026-11-04"][0]
prev_close = daily[idx - 1][1]
ma50 = sum(c for _, c in daily[idx - 50:idx]) / 50
print(json.dumps({"nifty_2026-11-03_close": prev_close, "nifty_50dma_at_11-04": round(ma50, 2),
                  "prior_close_vs_50dma": "above" if prev_close > ma50 else "below/at"}))

# ---------------- Part B ----------------
print("=" * 70)
print("PART B — INV-ABOVE candidates on c24 dumps")
def load_book(yr):
    return list(csv.DictReader(open(WS / f"stocks_engine_v2_c24_book{yr}_trades.csv")))
_open_cache = {}
def entry_open(sym, day, et):
    key = (sym, day)
    if key not in _open_cache:
        _open_cache[key] = {t: o for t, o, h, l, c in bars(FULL, sym, day)}
    return _open_cache[key].get(et)

def summ(rows):
    return {"n": len(rows), "net": round(sum(float(r["net"]) for r in rows), 2)}
def halves(rows):
    h1 = [r for r in rows if r["date"][5:7] in ("01", "02", "03", "04", "05")]
    h2 = [r for r in rows if r["date"][5:7] in ("06", "07", "08", "09", "10")]
    return summ(h1), summ(h2)
def months(rows):
    m = collections.defaultdict(float)
    for r in rows:
        m[r["date"][:7]] += float(r["net"])
    return {k: round(v, 2) for k, v in sorted(m.items())}
def ex_top3(rows):
    s = sorted((float(r["net"]) for r in rows), reverse=True)
    return round(sum(s[3:]), 2) if len(s) > 3 else None
def chrono_skip(rows, k):
    return summ(rows[k:])

for cand, drop_fn, label in [
    ("STOCKS-EVE-06", lambda r, price: price is not None and price >= 1500.0,
     "skip INV-ABOVE entries with entry price >= Rs1,500 (rupee stop >= Rs750/100sh)"),
    ("STOCKS-EVE-07", lambda r, price: r["entry_time"] >= "10:00",
     "skip INV-ABOVE entries at/after 10:00"),
]:
    print("-" * 60)
    print(cand, "—", label)
    for yr in ("2025", "2026"):
        book = load_book(yr)
        inv = [r for r in book if r["comp"] == "INV-ABOVE"]
        priced, missing = [], 0
        for r in inv:
            p = entry_open(r["stock"], r["date"], r["entry_time"])
            if p is None:
                missing += 1
            priced.append((r, p))
        dropped = [r for r, p in priced if drop_fn(r, p)]
        kept = [r for r, p in priced if not drop_fn(r, p)]
        base_m, kept_m = months(inv), months(kept)
        flips = [m for m in base_m if base_m[m] > 0 and kept_m.get(m, 0.0) < 0]
        book_base = summ(book); book_var = summ([r for r in book if r not in dropped]) \
            if dropped else book_base
        print(json.dumps({"year": yr, "inv_base": summ(inv), "inv_variant": summ(kept),
                          "dropped": summ(dropped), "price_missing": missing,
                          "halves_base": halves(inv), "halves_variant": halves(kept),
                          "ex_top3_base": ex_top3(inv), "ex_top3_variant": ex_top3(kept),
                          "month_flips_green_to_red": flips,
                          "placebo_chrono_skip_same_n": chrono_skip(inv, len(dropped)),
                          "book_base": book_base, "book_variant": book_var}))

# ---------------- Part C ----------------
print("=" * 70)
print("PART C — STOCKS-EVE-08 P2F family T125 -> T100 rescan")
FAMILY = [("stocks_engine_ch1_p2fprofile_trades.csv", "net", 0.0065),
          ("stocks_engine_sat13_p2fr2_trades.csv", "net_rs", 0.0050),
          ("stocks_engine_sat33_r2lowband_trades.csv", "net_rs", 0.0050)]
fam = []
for f, col, stop_pct in FAMILY:
    for r in csv.DictReader(open(WS / f)):
        fam.append({"file": f, "stock": r["symbol"], "date": r["date"],
                    "dir": r["direction"], "entry_time": r["entry_time"],
                    "entry": float(r["entry"]), "net": float(r[col]),
                    "exit_reason": r["exit_reason"], "stop_pct": stop_pct})
fam.sort(key=lambda r: (r["date"], r["entry_time"], r["stock"]))
print("family n:", len(fam), "stored net:", round(sum(r["net"] for r in fam), 2),
      "(target +27,293.58)")
def rescan(r, target_pct):
    b = bars(FULL, r["stock"], r["date"])
    if not b:
        return None
    e = r["entry"]
    if r["dir"] == "LONG":
        stop = round(e * (1 - r["stop_pct"]), 2); tgt = round(e * (1 + target_pct), 2)
    else:
        stop = round(e * (1 + r["stop_pct"]), 2); tgt = round(e * (1 - target_pct), 2)
    xt, xp, xr, mfe, mae = scan(b, r["entry_time"], e, stop, tgt, r["dir"])
    if xp is None:
        return None
    return net_of(e, xp, r["dir"]), xr
repro, repro_ok = [], 0
for r in fam:
    out = rescan(r, 0.0125)
    if out and abs(out[0] - r["net"]) <= 1.0:
        repro_ok += 1
    repro.append(out[0] if out else None)
print("baseline reproduction: matched", repro_ok, "of", len(fam),
      "| rescan net:", round(sum(x for x in repro if x is not None), 2))
var, var_reasons = [], collections.Counter()
for r in fam:
    out = rescan(r, 0.0100)
    var.append(out[0] if out else None)
    if out:
        var_reasons[out[1]] += 1
base_reasons = collections.Counter(r["exit_reason"] for r in fam)
print("variant T100 net:", round(sum(x for x in var if x is not None), 2),
      "| exit mix base:", dict(base_reasons), "variant:", dict(var_reasons))
paired = [(r, repro[i], var[i]) for i, r in enumerate(fam) if repro[i] is not None and var[i] is not None]
def vsumm(pairs, idx):
    return {"n": len(pairs), "net": round(sum(p[idx] for p in pairs), 2)}
def vhalves(pairs, idx):
    h1 = [p for p in pairs if p[0]["date"][5:7] in ("01", "02", "03", "04", "05")]
    h2 = [p for p in pairs if p[0]["date"][5:7] in ("06", "07", "08", "09", "10")]
    return vsumm(h1, idx), vsumm(h2, idx)
def vmonths(pairs, idx):
    m = collections.defaultdict(float)
    for p in pairs:
        m[p[0]["date"][:7]] += p[idx]
    return {k: round(v, 2) for k, v in sorted(m.items())}
def vex3(pairs, idx):
    s = sorted((p[idx] for p in pairs), reverse=True)
    return round(sum(s[3:]), 2)
bm, vm = vmonths(paired, 1), vmonths(paired, 2)
flips = [m for m in bm if bm[m] > 0 and vm.get(m, 0.0) < 0]
print(json.dumps({"paired_n": len(paired), "base": vsumm(paired, 1), "variant": vsumm(paired, 2),
                  "halves_base": vhalves(paired, 1), "halves_variant": vhalves(paired, 2),
                  "ex_top3_base": vex3(paired, 1), "ex_top3_variant": vex3(paired, 2),
                  "month_flips_green_to_red": flips, "months_base": bm, "months_variant": vm}))
print("DONE")
