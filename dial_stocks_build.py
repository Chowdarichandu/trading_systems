#!/usr/bin/env python3
"""DIAL — STOCKS standalone indicator system. Spec: dial_stocks_SPEC.md (frozen 2026-11-14).
Research only. Reads data/sarvaritu_fwd/<SYM>/spot_5m.csv. Writes
dial_stocks_results.json + dial_stocks_trades.csv. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade.
"""
import csv, json, math, os, random, sys
import numpy as np
from collections import defaultdict

WS = os.path.dirname(os.path.abspath(__file__))
NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC "
         "INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD "
         "TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO").split()
COST = 40.0
SEED = 20261114
SQ_STAMP = "15:10"          # bar whose CLOSE is the 15:15 square-off price
LAST_ENTRY_STAMP = "15:10"  # entry bar stamp must be <= this

# ---------------------------------------------------------------- data loading
def load_stock(sym):
    path = os.path.join(WS, "data", "sarvaritu_fwd", sym, "spot_5m.csv")
    ts, o, h, l, c = [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            ts.append(r["timestamp"]); o.append(float(r["open"])); h.append(float(r["high"]))
            l.append(float(r["low"])); c.append(float(r["close"]))
    return ts, np.array(o), np.array(h), np.array(l), np.array(c)

def day_segments(ts):
    """date -> (start_idx, end_idx_exclusive) over the stock's continuous arrays."""
    seg, start = {}, 0
    for i in range(1, len(ts) + 1):
        if i == len(ts) or ts[i][:10] != ts[start][:10]:
            seg[ts[start][:10]] = (start, i)
            start = i
    return seg

# ---------------------------------------------------------------- indicators (all causal)
def rsi_wilder(c, p=14):
    n = len(c); out = np.full(n, np.nan)
    if n <= p: return out
    d = np.diff(c)
    g = np.where(d > 0, d, 0.0); ls = np.where(d < 0, -d, 0.0)
    ag, al = g[:p].mean(), ls[:p].mean()
    out[p] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    for i in range(p + 1, n):
        ch = d[i - 1]
        ag = (ag * (p - 1) + (ch if ch > 0 else 0.0)) / p
        al = (al * (p - 1) + (-ch if ch < 0 else 0.0)) / p
        out[i] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    return out

def ema_series(c, span=50):
    n = len(c); out = np.full(n, np.nan)
    if n < span: return out
    out[span - 1] = c[:span].mean()
    k = 2.0 / (span + 1.0)
    for i in range(span, n):
        out[i] = c[i] * k + out[i - 1] * (1.0 - k)
    return out

def bollinger_pctb(c, w=20, mult=2.0):
    n = len(c); out = np.full(n, np.nan)
    cs = np.concatenate([[0.0], np.cumsum(c)]); cs2 = np.concatenate([[0.0], np.cumsum(c * c)])
    s = cs[w:] - cs[:-w]; s2 = cs2[w:] - cs2[:-w]
    m = s / w; var = np.maximum(s2 / w - m * m, 0.0); sd = np.sqrt(var)
    up = m + mult * sd; lo = m - mult * sd
    rng = up - lo
    vals = np.where(rng > 0, (c[w - 1:] - lo) / np.where(rng > 0, rng, 1.0), np.nan)
    out[w - 1:] = vals
    return out

def supertrend_dir(h, l, c, p=7, mult=3.0):
    n = len(c); direction = np.zeros(n, dtype=int)
    if n <= p: return direction
    tr = np.empty(n); tr[0] = h[0] - l[0]
    pc = np.empty(n); pc[0] = c[0]; pc[1:] = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - pc[1:]), np.abs(l[1:] - pc[1:])))
    atr = np.full(n, np.nan); atr[p - 1] = tr[:p].mean()
    for i in range(p, n):
        atr[i] = (atr[i - 1] * (p - 1) + tr[i]) / p
    fu = fl = None; dirn = 0
    for i in range(p - 1, n):
        mid = (h[i] + l[i]) / 2.0
        bu = mid + mult * atr[i]; bl = mid - mult * atr[i]
        if fu is None:
            fu, fl = bu, bl
            dirn = 1 if c[i] >= mid else -1
        else:
            if c[i] > fu: dirn = 1
            elif c[i] < fl: dirn = -1
            fu = bu if (bu < fu or c[i - 1] > fu) else fu
            fl = bl if (bl > fl or c[i - 1] < fl) else fl
        direction[i] = dirn
    return direction

# ---------------------------------------------------------------- exit geometry
def exit_eval(o, h, l, c, entry_li, sq_li, E, side):
    """Bars are one day's local arrays. Monitor entry bar..sq bar inclusive.
    Returns exit price. Stop-first on same-bar overlap; gap-through fills at open."""
    if side == 1:   # LONG
        tgt, stp = E * 1.01, E * 0.995
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= tgt: return oj
            if oj <= stp: return oj
            th, sh = hj >= tgt, lj <= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    else:           # SHORT
        tgt, stp = E * 0.99, E * 1.005
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj <= tgt: return oj
            if oj >= stp: return oj
            th, sh = lj <= tgt, hj >= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    return c[sq_li]

def trade_net(E, exit_px, side):
    return ((exit_px - E) if side == 1 else (E - exit_px)) * 100.0 - COST

# ---------------------------------------------------------------- per-stock build
def build_stock(sym):
    ts, o, h, l, c = load_stock(sym)
    seg = day_segments(ts)
    stamps = [t[11:16] for t in ts]
    dates = [t[:10] for t in ts]
    rsi = rsi_wilder(c); ema = ema_series(c); pctb = bollinger_pctb(c)
    stdir = supertrend_dir(h, l, c)
    days = {}
    for date, (a, b) in seg.items():
        lo_o, lo_h, lo_l, lo_c = o[a:b], h[a:b], l[a:b], c[a:b]
        lo_st = stamps[a:b]
        tp = (lo_h + lo_l + lo_c) / 3.0
        vwap = np.cumsum(tp) / np.arange(1, len(tp) + 1)
        sq_li = lo_st.index(SQ_STAMP) if SQ_STAMP in lo_st else None
        tradable = sq_li is not None and (b - a) >= 30
        days[date] = dict(a=a, b=b, o=lo_o, h=lo_h, l=lo_l, c=lo_c, st=lo_st,
                          vwap=vwap, sq_li=sq_li, tradable=tradable)
    return dict(sym=sym, ts=ts, stamps=stamps, dates=dates, o=o, h=h, l=l, c=c,
                rsi=rsi, ema=ema, pctb=pctb, stdir=stdir, days=days)

def stock_signals(S):
    """Yield trades (dicts) for every tradable day in the full series."""
    trades = []
    for date, D in sorted(S["days"].items()):
        if not D["tradable"]: continue
        a = D["a"]; n = D["b"] - a
        got = {"T": False, "R": False}
        for li in range(n):
            if got["T"] and got["R"]: break
            g = a + li
            if g + 1 < 60:  # warm-up: need >=60 bars of history incl. current
                continue
            # entry bar = next present bar, same day, stamp <= 15:10
            if li + 1 >= n: continue
            if D["st"][li + 1] > LAST_ENTRY_STAMP: continue
            side = comp = None
            if not got["T"] and S["stdir"][g] != 0 and g > 0 and S["stdir"][g - 1] != 0 \
               and S["stdir"][g] != S["stdir"][g - 1]:
                if S["stdir"][g] == 1 and S["c"][g] > D["vwap"][li]: side, comp = 1, "T"
                elif S["stdir"][g] == -1 and S["c"][g] < D["vwap"][li]: side, comp = -1, "T"
            if side is None and not got["R"]:
                r, pb = S["rsi"][g], S["pctb"][g]
                if not (math.isnan(r) or math.isnan(pb) or math.isnan(S["ema"][g]) or math.isnan(S["ema"][g - 6])):
                    slope = (S["ema"][g] - S["ema"][g - 6]) / S["ema"][g - 6]
                    if r <= 30 and pb <= 0.05 and slope > -0.001: side, comp = 1, "R"
                    elif r >= 70 and pb >= 0.95 and slope < 0.001: side, comp = -1, "R"
            if side is None: continue
            eli = li + 1
            E = float(D["o"][eli])
            xp = exit_eval(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side)
            assert eli > li  # timing audit: entry strictly after signal bar
            trades.append(dict(sym=S["sym"], date=date, comp=comp, side=side,
                               signal_stamp=D["st"][li], entry_stamp=D["st"][eli],
                               entry=E, exit=float(xp), net=trade_net(E, xp, side)))
            got[comp] = True
    return trades

# ---------------------------------------------------------------- gate maths
def summarise(trades):
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    return dict(trades=len(trades), total=round(tot, 2),
                wr=round(100.0 * wins / len(trades), 2) if trades else None)

def gate_block(trades, year):
    sel = [t for t in trades if t["date"][:4] == str(year) and t["date"][5:7] in
           ("01","02","03","04","05","06","07","08","09","10")]
    months = {}
    for m in range(1, 11):
        key = f"{year}-{m:02d}"
        months[key] = round(sum(t["net"] for t in sel if t["date"][:7] == key), 2)
    tot = sum(months.values())
    h1 = sum(v for k, v in months.items() if k[5:7] in ("01","02","03","04","05"))
    h2 = tot - h1
    srt = sorted((t["net"] for t in sel), reverse=True)
    ext3 = tot - sum(srt[:3])
    red = sum(1 for v in months.values() if v < 0)
    return dict(summary=summarise(sel), months=months, total=round(tot, 2),
                h1=round(h1, 2), h2=round(h2, 2), ex_top3=round(ext3, 2),
                red_months=red, pace=round(tot / 10.0, 2), trades=sel)

def placebo_pct(stocks_days, year, count, rng):
    """Percentile of the real total among 200 random-entry draws (same count/year)."""
    universe = []
    for S in stocks_days:
        for date, D in S["days"].items():
            if date[:4] == str(year) and date[5:7] in ("01","02","03","04","05","06","07","08","09","10") and D["tradable"]:
                entries = [li for li, s in enumerate(D["st"]) if "09:20" <= s <= LAST_ENTRY_STAMP]
                if entries: universe.append((S["sym"], D, entries))
    cache = {}
    def one():
        sym, D, entries = universe[rng.randrange(len(universe))]
        eli = entries[rng.randrange(len(entries))]
        side = 1 if rng.random() < 0.5 else -1
        key = (sym, id(D), eli, side)
        if key not in cache:
            E = float(D["o"][eli])
            xp = exit_eval(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side)
            cache[key] = trade_net(E, xp, side)
        return cache[key]
    draws = []
    for _ in range(200):
        draws.append(sum(one() for _ in range(count)))
    return draws

def pass_verdict(block, pct, year):
    pace_bar = 7500.0 if year == 2026 else 5000.0
    fails = []
    if pct is None or pct < 95.0: fails.append(f"placebo {pct} < 95th pct")
    if not (block["h1"] > 0 and block["h2"] > 0): fails.append(f"halves H1 {block['h1']} / H2 {block['h2']} not both positive")
    if not block["ex_top3"] > 0: fails.append(f"ex-top-3 {block['ex_top3']} <= 0")
    if block["pace"] < pace_bar: fails.append(f"pace {block['pace']} < {pace_bar}")
    if block["red_months"] > 4: fails.append(f"red months {block['red_months']} > 4")
    return ("PASS" if not fails else "FAIL"), fails

# ---------------------------------------------------------------- main
def main():
    stocks = [build_stock(s) for s in NAMES]
    all_trades = []
    for S in stocks:
        all_trades.extend(stock_signals(S))
    # coverage / NC
    cov = {}
    for yr in (2025, 2026):
        sd = nc = 0
        for S in stocks:
            for date, D in S["days"].items():
                if date[:4] == str(yr) and date[5:7] in ("01","02","03","04","05","06","07","08","09","10"):
                    sd += 1
                    if not D["tradable"]: nc += 1
        cov[yr] = dict(stock_days=sd, nc_stock_days=nc)
    nov_dates = ["2026-11-02","2026-11-03","2026-11-04","2026-11-05","2026-11-06",
                 "2026-11-09","2026-11-11","2026-11-12","2026-11-13"]
    nov_nc = sum(1 for S in stocks for d, D in S["days"].items()
                 if d == "2026-11-08" and not D["tradable"])
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only",
               "coverage": cov, "nov_nc_stub_stock_days": nov_nc, "series": {}}
    rng = random.Random(SEED)
    for comp, sel_all in (("T", [t for t in all_trades if t["comp"] == "T"]),
                          ("R", [t for t in all_trades if t["comp"] == "R"]),
                          ("COMBINED", all_trades)):
        results["series"][comp] = {}
        for yr in (2025, 2026):
            blk = gate_block(sel_all, yr)
            draws = placebo_pct(stocks, yr, len(blk["trades"]), rng) if blk["trades"] else []
            real = blk["total"]
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            verdict, fails = pass_verdict(blk, pct, yr)
            results["series"][comp][yr] = dict(
                trades=blk["summary"]["trades"], total=blk["total"], wr=blk["summary"]["wr"],
                months=blk["months"], h1=blk["h1"], h2=blk["h2"], ex_top3=blk["ex_top3"],
                red_months=blk["red_months"], pace=blk["pace"], placebo_pct=pct,
                verdict=verdict, failing_legs=fails,
                placebo_draws_summary=dict(min=round(min(draws), 2), median=round(sorted(draws)[100], 2),
                                           max=round(max(draws), 2)) if draws else None)
    # November CF
    nov = {}
    for comp, sel_all in (("T", [t for t in all_trades if t["comp"] == "T"]),
                          ("R", [t for t in all_trades if t["comp"] == "R"]),
                          ("COMBINED", all_trades)):
        sel = [t for t in sel_all if t["date"] in nov_dates]
        by_day = {d: round(sum(t["net"] for t in sel if t["date"] == d), 2) for d in nov_dates}
        nov[comp] = dict(trades=len(sel), total=round(sum(t["net"] for t in sel), 2),
                         wr=summarise(sel)["wr"], by_day=by_day,
                         trade_list=[{k: t[k] for k in ("sym","date","side","signal_stamp","entry_stamp","entry","exit","net")} for t in sel])
    results["november_cf"] = nov
    results["stock_book_nov_actual"] = 7517.94
    with open(os.path.join(WS, "dial_stocks_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(WS, "dial_stocks_trades.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sym","date","comp","side","signal_stamp","entry_stamp","entry","exit","net"])
        for t in sorted(all_trades, key=lambda x: (x["date"], x["sym"], x["comp"])):
            w.writerow([t["sym"], t["date"], t["comp"], t["side"], t["signal_stamp"], t["entry_stamp"],
                        t["entry"], t["exit"], round(t["net"], 2)])
    print(json.dumps({k: results[k] for k in ("coverage", "nov_nc_stub_stock_days")}, indent=1))
    for comp in ("T", "R", "COMBINED"):
        for yr in (2025, 2026):
            r = results["series"][comp][yr]
            print(comp, yr, "trades", r["trades"], "total", r["total"], "WR", r["wr"],
                  "pace", r["pace"], "pct", r["placebo_pct"], r["verdict"], r["failing_legs"])
    for comp in ("T", "R", "COMBINED"):
        print("NOV", comp, results["november_cf"][comp]["trades"], results["november_cf"][comp]["total"])

if __name__ == "__main__":
    main()
