#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS. Spec: ekam_intraday_stocks_SPEC.md (frozen 2026-11-14).
Research only. Reads data/sarvaritu_fwd/<SYM>/spot_5m.csv. Writes
ekam_intraday_stocks_results.json + ekam_intraday_stocks_trades.csv.
Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
VWAP = equal-weighted typical-price proxy (stores carry no volume).
"""
import csv, json, math, os, random
import numpy as np

WS = os.path.dirname(os.path.abspath(__file__))
NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC "
         "INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD "
         "TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO").split()
COST = 40.0
SEED = 20261114
SQ_STAMP = "15:10"
LAST_ENTRY_STAMP = "15:10"
DAY_CAP = 5
THRESHOLDS = (4, 5)

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
    seg, start = {}, 0
    for i in range(1, len(ts) + 1):
        if i == len(ts) or ts[i][:10] != ts[start][:10]:
            seg[ts[start][:10]] = (start, i)
            start = i
    return seg

# ---------------------------------------------------------------- indicators (all causal)
def ema_series(c, span):
    n = len(c); out = np.full(n, np.nan)
    if n < span: return out
    out[span - 1] = c[:span].mean()
    k = 2.0 / (span + 1.0)
    for i in range(span, n):
        out[i] = c[i] * k + out[i - 1] * (1.0 - k)
    return out

def ema_over(x, span, start):
    """EMA over x where x is first defined at index `start`; SMA seed of first span values."""
    n = len(x); out = np.full(n, np.nan)
    if n < start + span: return out
    out[start + span - 1] = np.nanmean(x[start:start + span])
    k = 2.0 / (span + 1.0)
    for i in range(start + span, n):
        out[i] = x[i] * k + out[i - 1] * (1.0 - k)
    return out

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

def adx_wilder(h, l, c, p=14):
    n = len(c); out = np.full(n, np.nan)
    if n <= 2 * p: return out
    tr = np.empty(n); tr[0] = h[0] - l[0]
    pc = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - pc), np.abs(l[1:] - pc)))
    up = np.zeros(n); dn = np.zeros(n)
    up[1:] = h[1:] - h[:-1]; dn[1:] = l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    str_ = np.full(n, np.nan); sp = np.full(n, np.nan); sm = np.full(n, np.nan)
    str_[p] = tr[1:p + 1].sum(); sp[p] = pdm[1:p + 1].sum(); sm[p] = mdm[1:p + 1].sum()
    for i in range(p + 1, n):
        str_[i] = str_[i - 1] - str_[i - 1] / p + tr[i]
        sp[i] = sp[i - 1] - sp[i - 1] / p + pdm[i]
        sm[i] = sm[i - 1] - sm[i - 1] / p + mdm[i]
    with np.errstate(invalid="ignore", divide="ignore"):
        pdi = np.where(str_ > 0, 100.0 * sp / str_, 0.0)
        mdi = np.where(str_ > 0, 100.0 * sm / str_, 0.0)
        denom = pdi + mdi
        dx = np.where(denom > 0, 100.0 * np.abs(pdi - mdi) / denom, 0.0)
    dx[:p] = np.nan
    first = 2 * p - 1  # index 27: SMA of DX[14..27]
    if n <= first: return out
    out[first] = np.nanmean(dx[p:first + 1])
    for i in range(first + 1, n):
        out[i] = (out[i - 1] * (p - 1) + dx[i]) / p
    return out

def compute_indicators(o, h, l, c):
    e9 = ema_series(c, 9); e21 = ema_series(c, 21)
    e12 = ema_series(c, 12); e26 = ema_series(c, 26)
    macd = e12 - e26
    sig = ema_over(macd, 9, 25)
    return dict(e9=e9, e21=e21, macd=macd, sig=sig,
                rsi=rsi_wilder(c), stdir=supertrend_dir(h, l, c), adx=adx_wilder(h, l, c))

def votes_at(close, vwap, ind, g):
    """(LV, SV) at global bar g, or (None, None) if anything undefined / warm-up."""
    if g + 1 < 60: return None, None
    e9, e21, macd, sig, rsi, adx = ind["e9"][g], ind["e21"][g], ind["macd"][g], ind["sig"][g], ind["rsi"][g], ind["adx"][g]
    if any(math.isnan(v) for v in (e9, e21, macd, sig, rsi, adx)): return None, None
    sd = ind["stdir"][g]
    L = [close > vwap, e9 > e21, sd == 1, macd > sig, 50.0 <= rsi < 70.0]
    S = [close < vwap, e9 < e21, sd == -1, macd < sig, 30.0 < rsi <= 50.0]
    L5, S5 = sum(L), sum(S)
    LV, SV = L5, S5
    if adx >= 20.0:
        if L5 > S5: LV += 1
        elif S5 > L5: SV += 1
    return LV, SV

# ---------------------------------------------------------------- exits
def exit_x1(o, h, l, c, entry_li, sq_li, E, side):
    """Fixed +1.0% / -0.5%. Stop-first on overlap; gap-through fills at open; else 15:10 close."""
    if side == 1:
        tgt, stp = E * 1.01, E * 0.995
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= tgt: return oj
            if oj <= stp: return oj
            th, sh = hj >= tgt, lj <= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    else:
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

def exit_x2(o, h, l, c, entry_li, sq_li, E, side, own_votes):
    """Vote-decay: hard stop -0.75% (checked first each bar); exit at a bar's close when
    own-direction votes at that bar <= 2; else square-off at 15:10 close."""
    stp = E * 0.9925 if side == 1 else E * 1.0075
    for j in range(entry_li, sq_li + 1):
        oj, hj, lj = o[j], h[j], l[j]
        if side == 1:
            if oj <= stp: return oj
            if lj <= stp: return stp
        else:
            if oj >= stp: return oj
            if hj >= stp: return stp
        v = own_votes[j]
        if v is not None and not (isinstance(v, float) and math.isnan(v)) and v <= 2:
            return c[j]
    return c[sq_li]

def trade_net(E, exit_px, side):
    return ((exit_px - E) if side == 1 else (E - exit_px)) * 100.0 - COST

# ---------------------------------------------------------------- per-stock build
def build_stock(sym):
    ts, o, h, l, c = load_stock(sym)
    seg = day_segments(ts)
    stamps = [t[11:16] for t in ts]
    ind = compute_indicators(o, h, l, c)
    days = {}
    for date, (a, b) in seg.items():
        lo_o, lo_h, lo_l, lo_c = o[a:b], h[a:b], l[a:b], c[a:b]
        lo_st = stamps[a:b]
        tp = (lo_h + lo_l + lo_c) / 3.0
        vwap = np.cumsum(tp) / np.arange(1, len(tp) + 1)
        LV = [None] * (b - a); SV = [None] * (b - a)
        for li in range(b - a):
            lv, sv = votes_at(lo_c[li], vwap[li], ind, a + li)
            LV[li], SV[li] = lv, sv
        sq_li = lo_st.index(SQ_STAMP) if SQ_STAMP in lo_st else None
        tradable = sq_li is not None and (b - a) >= 30
        days[date] = dict(a=a, b=b, o=lo_o, h=lo_h, l=lo_l, c=lo_c, st=lo_st,
                          vwap=vwap, LV=LV, SV=SV, sq_li=sq_li, tradable=tradable)
    return dict(sym=sym, ts=ts, stamps=stamps, o=o, h=h, l=l, c=c, ind=ind, days=days)

def day_candidates(S, date, T):
    """The stock's first qualifying signal of the day at threshold T, or None."""
    D = S["days"][date]
    if not D["tradable"]: return None
    n = D["b"] - D["a"]
    for li in range(n):
        lv, sv = D["LV"][li], D["SV"][li]
        if lv is None: continue
        if lv < T and sv < T: continue
        if lv == sv: continue  # exact tie: no signal, keep scanning
        if li + 1 >= n: return None  # no entry bar left today
        if D["st"][li + 1] > LAST_ENTRY_STAMP: return None
        side = 1 if lv > sv else -1
        return dict(sym=S["sym"], date=date, side=side, votes=(lv if side == 1 else sv),
                    signal_li=li, signal_stamp=D["st"][li], entry_li=li + 1,
                    entry_stamp=D["st"][li + 1])
    return None

def make_trade(S, cand):
    D = S["days"][cand["date"]]
    eli = cand["entry_li"]
    E = float(D["o"][eli])
    assert cand["entry_stamp"] > cand["signal_stamp"]  # timing audit
    xp1 = exit_x1(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, cand["side"])
    own = D["LV"] if cand["side"] == 1 else D["SV"]
    xp2 = exit_x2(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, cand["side"], own)
    base = dict(sym=cand["sym"], date=cand["date"], side=cand["side"], votes=cand["votes"],
                signal_stamp=cand["signal_stamp"], entry_stamp=cand["entry_stamp"], entry=E)
    return dict(base, exit_x1=float(xp1), net_x1=trade_net(E, xp1, cand["side"]),
                exit_x2=float(xp2), net_x2=trade_net(E, xp2, cand["side"]))

# ---------------------------------------------------------------- summaries
def summarise(trades, netkey):
    tot = sum(t[netkey] for t in trades)
    wins = sum(1 for t in trades if t[netkey] > 0)
    return dict(trades=len(trades), total=round(tot, 2),
                wr=round(100.0 * wins / len(trades), 2) if trades else None)

def window_block(trades, netkey, year):
    def sel(lo, hi):
        return [t for t in trades if lo <= t["date"] <= hi]
    return dict(
        jan_jun=summarise(sel(f"{year}-01-01", f"{year}-06-30"), netkey),
        jul_oct=summarise(sel(f"{year}-07-01", f"{year}-10-31"), netkey),
        jan_oct=summarise(sel(f"{year}-01-01", f"{year}-10-31"), netkey))

# ---------------------------------------------------------------- placebo
def placebo_pct(stocks, year, count, exit_kind, rng):
    universe = []
    for S in stocks:
        for date, D in S["days"].items():
            if date[:4] == str(year) and "01" <= date[5:7] <= "10" and D["tradable"]:
                entries = [li for li, s in enumerate(D["st"]) if "09:20" <= s <= LAST_ENTRY_STAMP]
                if entries: universe.append((S, D, entries))
    cache = {}
    def one():
        S, D, entries = universe[rng.randrange(len(universe))]
        eli = entries[rng.randrange(len(entries))]
        side = 1 if rng.random() < 0.5 else -1
        key = (S["sym"], id(D), eli, side, exit_kind)
        if key not in cache:
            E = float(D["o"][eli])
            if exit_kind == "X1":
                xp = exit_x1(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side)
            else:
                own = D["LV"] if side == 1 else D["SV"]
                xp = exit_x2(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side, own)
            cache[key] = trade_net(E, xp, side)
        return cache[key]
    draws = [sum(one() for _ in range(count)) for _ in range(200)]
    return draws

# ---------------------------------------------------------------- timing audit (truncated recompute)
def audit_sample(stocks, sample):
    """Recompute votes from bars <= t only for sampled (stock, date, li); compare."""
    mism = 0; checked = 0
    for S, date, li in sample:
        D = S["days"][date]; g = D["a"] + li
        ind_t = compute_indicators(S["o"][:g + 1], S["h"][:g + 1], S["l"][:g + 1], S["c"][:g + 1])
        a = D["a"]
        tp = (S["h"][a:g + 1] + S["l"][a:g + 1] + S["c"][a:g + 1]) / 3.0
        vwap_t = tp.mean()  # cumulative mean of typical price through bar li = mean of the day's TPs so far
        # note: truncated-series ADX/EMA seedings are computed on the same prefix, so they
        # coincide with the full-series values at g by causality.
        lv, sv = votes_at(S["c"][g], vwap_t, ind_t, g)
        checked += 1
        if lv != D["LV"][li] or sv != D["SV"][li]: mism += 1
    return checked, mism

# ---------------------------------------------------------------- main
def main():
    stocks = [build_stock(s) for s in NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    all_dates = sorted({d for S in stocks for d in S["days"]})
    # candidates per threshold, with the 5-per-day cap
    cand_all = {T: [] for T in THRESHOLDS}   # pre-cap, for the audit sample
    trades = {T: [] for T in THRESHOLDS}     # post-cap trade records (both exits inside)
    for date in all_dates:
        for T in THRESHOLDS:
            cands = []
            for S in stocks:
                cd = day_candidates(S, date, T)
                if cd: cands.append(cd)
            cand_all[T].extend(cands)
            cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))
            for cd in cands[:DAY_CAP]:
                trades[T].append(make_trade(by_sym[cd["sym"]], cd))
    # timing audit: every 37th pre-cap candidate across the run
    sample = []
    flat = sorted(cand_all[4] + cand_all[5], key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    for i, cd in enumerate(flat):
        if i % 37 == 0:
            S = by_sym[cd["sym"]]
            sample.append((S, cd["date"], cd["signal_li"]))
    checked, mism = audit_sample(stocks, sample)
    # coverage / NC
    cov = {}
    for yr in (2025, 2026):
        sd = nc = 0
        for S in stocks:
            for date, D in S["days"].items():
                if date[:4] == str(yr) and "01" <= date[5:7] <= "10":
                    sd += 1
                    if not D["tradable"]: nc += 1
        cov[yr] = dict(stock_days=sd, nc_stock_days=nc)
    nov_dates = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
                 "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
    nov_nc = sum(1 for S in stocks for d, D in S["days"].items()
                 if d == "2026-11-08" and not D["tradable"])
    rows = {}
    for T in THRESHOLDS:
        for X, netkey in (("X1", "net_x1"), ("X2", "net_x2")):
            row = f"T{T}-{X}"
            rows[row] = {}
            for yr in (2025, 2026):
                rows[row][yr] = window_block(trades[T], netkey, yr)
            nov = [t for t in trades[T] if t["date"] in nov_dates]
            rows[row]["november_cf"] = dict(
                summarise(nov, netkey),
                by_day={d: round(sum(t[netkey] for t in nov if t["date"] == d), 2) for d in nov_dates})
    # placebo on the best full-year row per year
    rng = random.Random(SEED)
    placebo = {}
    for yr in (2025, 2026):
        best_row, best_tot = None, None
        for row in rows:
            tot = rows[row][yr]["jan_oct"]["total"]
            if best_tot is None or tot > best_tot: best_row, best_tot = row, tot
        T = int(best_row[1]); X = best_row[3:]
        count = rows[best_row][yr]["jan_oct"]["trades"]
        draws = placebo_pct(stocks, yr, count, X, rng) if count else []
        pct = round(100.0 * sum(1 for d in draws if d < best_tot) / len(draws), 1) if draws else None
        placebo[yr] = dict(row=best_row, trades=count, total=best_tot, placebo_pct=pct,
                           draws_summary=dict(min=round(min(draws), 2),
                                              median=round(sorted(draws)[100], 2),
                                              max=round(max(draws), 2)) if draws else None)
        rows[best_row][yr]["placebo_pct"] = pct
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_SPEC.md (frozen 2026-11-14)",
               "coverage": cov, "nov_nc_stub_stock_days": nov_nc,
               "timing_audit": dict(entry_after_signal_asserted_on_all_trades=True,
                                    truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "rows": rows, "placebo_best_row_per_year": placebo}
    with open(os.path.join(WS, "ekam_intraday_stocks_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(WS, "ekam_intraday_stocks_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sym", "date", "threshold", "side", "votes", "signal_stamp", "entry_stamp",
                    "entry", "exit_x1", "net_x1", "exit_x2", "net_x2"])
        for T in THRESHOLDS:
            for t in sorted(trades[T], key=lambda x: (x["date"], x["signal_stamp"], x["sym"])):
                w.writerow([t["sym"], t["date"], T, t["side"], t["votes"], t["signal_stamp"],
                            t["entry_stamp"], t["entry"], t["exit_x1"], round(t["net_x1"], 2),
                            t["exit_x2"], round(t["net_x2"], 2)])
    print(json.dumps({"coverage": cov, "nov_nc": nov_nc,
                      "audit": results["timing_audit"]}, indent=1))
    for row in ("T4-X1", "T4-X2", "T5-X1", "T5-X2"):
        for yr in (2025, 2026):
            b = rows[row][yr]
            print(row, yr, "JanJun", b["jan_jun"], "JulOct", b["jul_oct"], "Full", b["jan_oct"],
                  "placebo" , b.get("placebo_pct"))
        print(row, "NOV", rows[row]["november_cf"])
    print("PLACEBO", json.dumps(placebo, indent=1))

if __name__ == "__main__":
    main()
