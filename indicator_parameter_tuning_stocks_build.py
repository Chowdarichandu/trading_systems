#!/usr/bin/env python3
"""INDICATOR PARAMETER ATLAS — STOCKS. Spec: indicator_parameter_tuning_stocks_SPEC.md
(frozen 2026-11-14 before scoring). Research only; changes no book/ledger/job.
Basis: equity cash, frozen 25 names, per 100 shares PROVISIONAL, Rs40/trade, paper only.
Part A: 5-min parameter grid with frequency discipline + discovery/validation robustness.
Part B: daily swing systems x exit overlays. Judged per year, never pooled.
"""
import csv, json, math, os, random, sys
import numpy as np
from collections import defaultdict

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
from dial_stocks_build import load_stock, day_segments, rsi_wilder, ema_series  # Round 1 constructions

NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC "
         "INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD "
         "TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO").split()
COST = 40.0
SQ_STAMP = "15:10"
SEED_PLACEBO = 20261115

# ---------------------------------------------------------------- indicators (extra)
def supertrend_full(h, l, c, p, mult):
    n = len(c); direction = np.zeros(n, dtype=int); line = np.full(n, np.nan)
    if n <= p: return direction, line
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
            fu, fl = bu, bl; dirn = 1 if c[i] >= mid else -1
        else:
            if c[i] > fu: dirn = 1
            elif c[i] < fl: dirn = -1
            fu = bu if (bu < fu or c[i - 1] > fu) else fu
            fl = bl if (bl > fl or c[i - 1] < fl) else fl
        direction[i] = dirn
        line[i] = fl if dirn == 1 else (fu if dirn == -1 else np.nan)
    return direction, line

def bollinger_bands(c, w):
    n = len(c); mid = np.full(n, np.nan); sd = np.full(n, np.nan)
    cs = np.concatenate([[0.0], np.cumsum(c)]); cs2 = np.concatenate([[0.0], np.cumsum(c * c)])
    s = cs[w:] - cs[:-w]; s2 = cs2[w:] - cs2[:-w]
    m = s / w; var = np.maximum(s2 / w - m * m, 0.0)
    mid[w - 1:] = m; sd[w - 1:] = np.sqrt(var)
    return mid, sd

def macd_series(c, f, s, sig):
    ef = ema_series(c, f); es = ema_series(c, s)
    m = ef - es
    # signal = SMA-seeded EMA of MACD over its defined region
    n = len(c); sgn = np.full(n, np.nan)
    idx = np.where(~np.isnan(m))[0]
    if len(idx) > sig:
        st = idx[0]; seg = m[st:]
        out = np.full(len(seg), np.nan)
        out[sig - 1] = np.nanmean(seg[:sig])
        k = 2.0 / (sig + 1.0)
        for i in range(sig, len(seg)):
            out[i] = seg[i] * k + out[i - 1] * (1.0 - k)
        sgn[st:] = out
    return m, sgn

def adx_wilder(h, l, c, p=14):
    n = len(c); out = np.full(n, np.nan)
    if n <= 2 * p: return out
    tr = np.empty(n); up = np.empty(n); dn = np.empty(n)
    tr[0] = h[0] - l[0]; up[0] = dn[0] = 0.0
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        u = h[i] - h[i - 1]; d = l[i - 1] - l[i]
        up[i] = u if (u > d and u > 0) else 0.0
        dn[i] = d if (d > u and d > 0) else 0.0
    str_ = tr[1:p + 1].sum(); sup = up[1:p + 1].sum(); sdn = dn[1:p + 1].sum()
    dxs = []
    def dx_of(su, sd_, st_):
        if st_ == 0: return 0.0
        pdi = 100.0 * su / st_; mdi = 100.0 * sd_ / st_
        return 0.0 if (pdi + mdi) == 0 else 100.0 * abs(pdi - mdi) / (pdi + mdi)
    dxs.append(dx_of(sup, sdn, str_))
    for i in range(p + 1, n):
        str_ = str_ - str_ / p + tr[i]; sup = sup - sup / p + up[i]; sdn = sdn - sdn / p + dn[i]
        dxs.append(dx_of(sup, sdn, str_))
    # dxs[k] corresponds to bar index p + k; ADX = Wilder average of DX, first at index 2p-1
    if len(dxs) >= p:
        adx = np.full(n, np.nan)
        val = float(np.mean(dxs[:p])); adx[2 * p - 1] = val
        for k in range(p, len(dxs)):
            val = (val * (p - 1) + dxs[k]) / p
            adx[p + k] = val
        return adx
    return out

def donchian_prior(h, l, p):
    n = len(h); ph = np.full(n, np.nan); pl = np.full(n, np.nan)
    for i in range(p, n):
        ph[i] = h[i - p:i].max(); pl[i] = l[i - p:i].min()
    return ph, pl

def atr_wilder(h, l, c, p=14):
    n = len(c); out = np.full(n, np.nan)
    if n <= p: return out
    tr = np.empty(n); tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out[p - 1] = tr[:p].mean()
    for i in range(p, n):
        out[i] = (out[i - 1] * (p - 1) + tr[i]) / p
    return out

# ---------------------------------------------------------------- exits (Part A)
def exit_fixed(o, h, l, c, eli, sq, E, side, tgt_pct, stp_pct):
    if side == 1:
        tgt, stp = E * (1 + tgt_pct), E * (1 - stp_pct)
        for j in range(eli, sq + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= tgt: return oj
            if oj <= stp: return oj
            th, sh = hj >= tgt, lj <= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    else:
        tgt, stp = E * (1 - tgt_pct), E * (1 + stp_pct)
        for j in range(eli, sq + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj <= tgt: return oj
            if oj >= stp: return oj
            th, sh = lj <= tgt, hj >= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    return c[sq]

def exit_flip(o, h, l, c, eli, sq, E, side, flip_bars):
    """flip_bars: sorted local indices (incl. signal bars) where opposite signal fires.
    Hard stop -0.75% monitored bar by bar; stop beats a same-bar flip."""
    stp = E * (1 - 0.0075) if side == 1 else E * (1 + 0.0075)
    fset = set(flip_bars)
    for j in range(eli, sq + 1):
        oj, hj, lj = o[j], h[j], l[j]
        if side == 1:
            if oj <= stp: return oj
            if lj <= stp: return stp
        else:
            if oj >= stp: return oj
            if hj >= stp: return stp
        if j in fset: return c[j]
    return c[sq]

def net_of(E, xp, side):
    return ((xp - E) if side == 1 else (E - xp)) * 100.0 - COST

EXITS = [("X1", 0.008, 0.004), ("X2", 0.010, 0.005), ("X3", 0.015, 0.0075), ("FLIP", None, None)]

# ---------------------------------------------------------------- Part A prep
def prep_stock_a(sym):
    ts, o, h, l, c = load_stock(sym)
    seg = day_segments(ts)
    stamps = [t[11:16] for t in ts]; dates = [t[:10] for t in ts]
    days = {}
    for date, (a, b) in seg.items():
        lo_st = stamps[a:b]
        tp = (h[a:b] + l[a:b] + c[a:b]) / 3.0
        vwap = np.cumsum(tp) / np.arange(1, b - a + 1)
        sq = lo_st.index(SQ_STAMP) if SQ_STAMP in lo_st else None
        days[date] = dict(a=a, b=b, st=lo_st, vwap=vwap, sq=sq,
                          tradable=(sq is not None and (b - a) >= 30))
    ind = {}
    for span in (8, 9, 13, 19, 20, 21, 26, 34, 39, 50):
        ind[f"ema{span}"] = ema_series(c, span)
    for p in (7, 14, 21):
        ind[f"rsi{p}"] = rsi_wilder(c, p)
    for (p, m) in [(7, 2), (7, 3), (7, 4), (10, 2), (10, 3), (10, 4), (14, 2), (14, 3), (14, 4)]:
        d, ln = supertrend_full(h, l, c, p, float(m)); ind[f"st{p}_{m}"] = (d, ln)
    for (f, s, sg) in [(8, 21, 5), (12, 26, 9), (19, 39, 9)]:
        ind[f"macd{f}_{s}_{sg}"] = macd_series(c, f, s, sg)
    for w in (14, 20, 30):
        ind[f"bb{w}"] = bollinger_bands(c, w)
    for p in (10, 20, 55):
        ind[f"dc{p}"] = donchian_prior(h, l, p)
    ind["adx"] = adx_wilder(h, l, c, 14)
    return dict(sym=sym, ts=ts, stamps=stamps, dates=dates, o=o, h=h, l=l, c=c,
                days=days, ind=ind)

# Event: (local_idx, side, extremity, adx_value)
def gen_events(S, famkey):
    """Return dict date -> list of events (bar order) for one family-params set."""
    o, h, l, c, ind = S["o"], S["h"], S["l"], S["c"], S["ind"]
    adx = ind["adx"]
    ev = defaultdict(list)
    fam = famkey[0]
    for date, D in S["days"].items():
        if not D["tradable"]: continue
        a, b, sq = D["a"], D["b"], D["sq"]
        # excursion trackers for reversion families (reset per day is WRONG for state,
        # but excursion state is tracked on the continuous series below instead)
        for li in range(b - a):
            g = a + li
            if g < 60 or g == 0: continue
            side = ext = None
            if fam == "EMA-X":
                _, f, s = famkey
                ef, es = ind[f"ema{f}"], ind[f"ema{s}"]
                if np.isnan(ef[g]) or np.isnan(es[g]) or np.isnan(ef[g - 1]) or np.isnan(es[g - 1]): continue
                vw = D["vwap"][li]
                if ef[g - 1] <= es[g - 1] and ef[g] > es[g] and c[g] > vw:
                    side, ext = 1, abs(ef[g] - es[g]) / c[g]
                elif ef[g - 1] >= es[g - 1] and ef[g] < es[g] and c[g] < vw:
                    side, ext = -1, abs(ef[g] - es[g]) / c[g]
            elif fam == "ST":
                _, p, m = famkey
                d, ln = ind[f"st{p}_{m}"]
                if d[g] != 0 and d[g - 1] != 0 and d[g] != d[g - 1] and not np.isnan(ln[g]):
                    side, ext = int(d[g]), abs(c[g] - ln[g]) / c[g]
            elif fam == "RSI-M":
                _, p = famkey
                r = ind[f"rsi{p}"]
                if np.isnan(r[g]) or np.isnan(r[g - 1]): continue
                if r[g - 1] <= 50 < r[g]: side, ext = 1, r[g] - 50
                elif r[g - 1] >= 50 > r[g]: side, ext = -1, 50 - r[g]
            elif fam == "MACD":
                _, f, s, sg = famkey
                mm, ss = ind[f"macd{f}_{s}_{sg}"]
                if np.isnan(mm[g]) or np.isnan(ss[g]) or np.isnan(mm[g - 1]) or np.isnan(ss[g - 1]): continue
                if mm[g - 1] <= ss[g - 1] and mm[g] > ss[g]: side, ext = 1, abs(mm[g] - ss[g]) / c[g]
                elif mm[g - 1] >= ss[g - 1] and mm[g] < ss[g]: side, ext = -1, abs(mm[g] - ss[g]) / c[g]
            elif fam == "BB-BO":
                _, w, k = famkey
                mid, sd = ind[f"bb{w}"]
                if np.isnan(mid[g]) or np.isnan(sd[g]) or np.isnan(mid[g - 1]) or np.isnan(sd[g - 1]): continue
                up, lo_ = mid[g] + k * sd[g], mid[g] - k * sd[g]
                upp, lop = mid[g - 1] + k * sd[g - 1], mid[g - 1] - k * sd[g - 1]
                if c[g - 1] <= upp and c[g] > up: side, ext = 1, (c[g] - up) / c[g]
                elif c[g - 1] >= lop and c[g] < lo_: side, ext = -1, (lo_ - c[g]) / c[g]
            elif fam == "DC":
                _, p = famkey
                ph, pl = ind[f"dc{p}"]
                if np.isnan(ph[g]) or np.isnan(pl[g]): continue
                if c[g] > ph[g]: side, ext = 1, (c[g] - ph[g]) / c[g]
                elif c[g] < pl[g]: side, ext = -1, (pl[g] - c[g]) / c[g]
            if side is not None:
                ev[date].append((li, side, float(ext), float(adx[g]) if not np.isnan(adx[g]) else None))
    return ev

def gen_events_reversion(S, famkey):
    """RSI-R / BB-R need excursion state on the continuous series — separate generator."""
    o, h, l, c, ind = S["o"], S["h"], S["l"], S["c"], S["ind"]
    adx = ind["adx"]
    ev = defaultdict(list)
    day_of = {}
    for date, D in S["days"].items():
        for li in range(D["b"] - D["a"]):
            day_of[D["a"] + li] = (date, li, D)
    n = len(c)
    if famkey[0] == "RSI-R":
        _, p, lo_t, hi_t = famkey
        r = ind[f"rsi{p}"]
        state = 0; exc = 0.0  # state -1 = below-lo excursion, +1 = above-hi
        for g in range(1, n):
            if np.isnan(r[g]) or np.isnan(r[g - 1]): state = 0; continue
            if state == 0:
                if r[g] <= lo_t: state, exc = -1, lo_t - r[g]
                elif r[g] >= hi_t: state, exc = 1, r[g] - hi_t
            elif state == -1:
                exc = max(exc, lo_t - r[g])
                if r[g - 1] <= lo_t < r[g]:
                    if g in day_of and g >= 60:
                        date, li, D = day_of[g]
                        if D["tradable"]:
                            ev[date].append((li, 1, float(exc), float(adx[g]) if not np.isnan(adx[g]) else None))
                    state = 0
                elif r[g] >= hi_t: state, exc = 1, r[g] - hi_t
            elif state == 1:
                exc = max(exc, r[g] - hi_t)
                if r[g - 1] >= hi_t > r[g]:
                    if g in day_of and g >= 60:
                        date, li, D = day_of[g]
                        if D["tradable"]:
                            ev[date].append((li, -1, float(exc), float(adx[g]) if not np.isnan(adx[g]) else None))
                    state = 0
                elif r[g] <= lo_t: state, exc = -1, lo_t - r[g]
    else:  # BB-R
        _, w, k = famkey
        mid, sd = ind[f"bb{w}"]
        state = 0; exc = 0.0
        for g in range(1, n):
            if np.isnan(mid[g]) or np.isnan(sd[g]) or np.isnan(mid[g - 1]) or np.isnan(sd[g - 1]):
                state = 0; continue
            up, lo_ = mid[g] + k * sd[g], mid[g] - k * sd[g]
            upp, lop = mid[g - 1] + k * sd[g - 1], mid[g - 1] - k * sd[g - 1]
            if state == 0:
                if c[g] < lo_: state, exc = -1, (lo_ - c[g]) / c[g]
                elif c[g] > up: state, exc = 1, (c[g] - up) / c[g]
            elif state == -1:
                if c[g] < lo_: exc = max(exc, (lo_ - c[g]) / c[g])
                if c[g - 1] < lop and c[g] >= lo_:
                    if g in day_of and g >= 60:
                        date, li, D = day_of[g]
                        if D["tradable"]:
                            ev[date].append((li, 1, float(exc), float(adx[g]) if not np.isnan(adx[g]) else None))
                    state = 0
                elif c[g] > up: state, exc = 1, (c[g] - up) / c[g]
            elif state == 1:
                if c[g] > up: exc = max(exc, (c[g] - up) / c[g])
                if c[g - 1] > upp and c[g] <= up:
                    if g in day_of and g >= 60:
                        date, li, D = day_of[g]
                        if D["tradable"]:
                            ev[date].append((li, -1, float(exc), float(adx[g]) if not np.isnan(adx[g]) else None))
                    state = 0
                elif c[g] < lo_: state, exc = -1, (lo_ - c[g]) / c[g]
    return ev

def exit_ride(o, h, l, c, eli, sq, E, side):
    """Placebo geometry for FLIP configs: -0.75% hard stop, else ride to sq close."""
    stp = E * (1 - 0.0075) if side == 1 else E * (1 + 0.0075)
    for j in range(eli, sq + 1):
        oj, hj, lj = o[j], h[j], l[j]
        if side == 1:
            if oj <= stp: return oj
            if lj <= stp: return stp
        else:
            if oj >= stp: return oj
            if hj >= stp: return stp
    return c[sq]

# ---------------------------------------------------------------- Part A configs
# family -> (combos list, coord axes sizes, is_trend)
FAMILIES = {
    "EMA-X":  dict(combos=[("EMA-X", 9, 21), ("EMA-X", 13, 34), ("EMA-X", 20, 50)], axes=[3], trend=True),
    "ST":     dict(combos=[("ST", p, m) for p in (7, 10, 14) for m in (2, 3, 4)], axes=[3, 3], trend=True),
    "RSI-M":  dict(combos=[("RSI-M", p) for p in (7, 14, 21)], axes=[3], trend=True),
    "MACD":   dict(combos=[("MACD", 8, 21, 5), ("MACD", 12, 26, 9), ("MACD", 19, 39, 9)], axes=[3], trend=True),
    "BB-BO":  dict(combos=[("BB-BO", w, k) for w in (14, 20, 30) for k in (1.5, 2, 2.5)], axes=[3, 3], trend=True),
    "DC":     dict(combos=[("DC", p) for p in (10, 20, 55)], axes=[3], trend=True),
    "RSI-R":  dict(combos=[("RSI-R", p, lo, hi) for p in (7, 14, 21)
                           for (lo, hi) in ((25, 75), (30, 70), (35, 65))], axes=[3, 3], trend=False),
    "BB-R":   dict(combos=[("BB-R", w, k) for w in (14, 20, 30) for k in (1.5, 2, 2.5)], axes=[3, 3], trend=False),
}
ADX_LEVELS = [None, 20, 25]
NOV_DATES = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
             "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]

def combo_coord(fam, combo_idx):
    """combo index -> coordinate tuple per the family's axes."""
    axes = FAMILIES[fam]["axes"]
    if len(axes) == 1: return (combo_idx,)
    return (combo_idx // axes[1], combo_idx % axes[1])

def coord_combo(fam, coord):
    axes = FAMILIES[fam]["axes"]
    if len(axes) == 1: return coord[0]
    return coord[0] * axes[1] + coord[1]

def run_config(stocks, events_by_stock, fam, combo, adx_level, exit_idx, dates_wanted=None):
    """events_by_stock: {sym: {date: [events]}}. Returns trade list."""
    ex_name, tgt, stp = EXITS[exit_idx]
    by_date = defaultdict(list)
    for S in stocks:
        ev = events_by_stock[S["sym"]]
        for date, evs in ev.items():
            if dates_wanted is not None and date not in dates_wanted: continue
            filt = [e for e in evs if adx_level is None or (e[3] is not None and e[3] >= adx_level)]
            if not filt: continue
            li, side, ext, _ = filt[0]
            by_date[date].append((S, li, side, ext, filt))
    trades = []
    for date, cands in by_date.items():
        cands.sort(key=lambda x: (-x[3], x[0]["days"][date]["st"][x[1]], x[0]["sym"]))
        for (S, li, side, ext, filt) in cands[:5]:
            D = S["days"][date]; a = D["a"]
            eli = li + 1
            if eli > D["sq"]: continue
            o = S["o"][a:D["b"]]; h = S["h"][a:D["b"]]; l = S["l"][a:D["b"]]; c = S["c"][a:D["b"]]
            E = float(o[eli])
            assert eli > li
            if ex_name == "FLIP":
                flips = [e[0] for e in filt if e[1] == -side and e[0] >= eli]
                xp = exit_flip(o, h, l, c, eli, D["sq"], E, side, flips)
            else:
                xp = exit_fixed(o, h, l, c, eli, D["sq"], E, side, tgt, stp)
            trades.append(dict(sym=S["sym"], date=date, side=side, entry=E,
                               exit=float(xp), net=net_of(E, float(xp), side)))
    return trades

def window_stats(trades, year, months):
    sel = [t for t in trades if t["date"][:4] == str(year) and int(t["date"][5:7]) in months]
    tot = sum(t["net"] for t in sel)
    wins = sum(1 for t in sel if t["net"] > 0)
    mstat = {}
    for m in months:
        key = f"{year}-{m:02d}"
        mstat[key] = round(sum(t["net"] for t in sel if t["date"][:7] == key), 2)
    srt = sorted((t["net"] for t in sel), reverse=True)
    return dict(trades=len(sel), total=round(tot, 2),
                wr=round(100.0 * wins / len(sel), 2) if sel else None,
                months=mstat, ex_top3=round(tot - sum(srt[:3]), 2),
                red_months=sum(1 for v in mstat.values() if v < 0), _sel=sel)

# placebo net cache: (sym, date, exit_name) -> {side: (entry_lis, nets array)}
_placebo_cache = {}
def placebo_day_nets(S, date, exit_name):
    key = (S["sym"], date, exit_name)
    if key in _placebo_cache: return _placebo_cache[key]
    D = S["days"][date]; a = D["a"]
    o = S["o"][a:D["b"]]; h = S["h"][a:D["b"]]; l = S["l"][a:D["b"]]; c = S["c"][a:D["b"]]
    lis = [li for li, s in enumerate(D["st"]) if "09:20" <= s <= SQ_STAMP]
    out = {}
    for side in (1, -1):
        nets = []
        for eli in lis:
            E = float(o[eli])
            if exit_name == "FLIP":
                xp = exit_ride(o, h, l, c, eli, D["sq"], E, side)
            else:
                _, tgt, stp = next(e for e in EXITS if e[0] == exit_name)
                xp = exit_fixed(o, h, l, c, eli, D["sq"], E, side, tgt, stp)
            nets.append(net_of(E, float(xp), side))
        out[side] = nets
    res = (lis, out)
    _placebo_cache[key] = res
    return res

def placebo_pct(stocks, year, exit_name, count, rng):
    universe = []
    for S in stocks:
        for date, D in S["days"].items():
            if date[:4] == str(year) and int(date[5:7]) in (7, 8, 9, 10) and D["tradable"]:
                if any("09:20" <= s <= SQ_STAMP for s in D["st"]):
                    universe.append((S, date))
    if not universe or count == 0: return None
    draws = []
    for _ in range(200):
        tot = 0.0
        for _ in range(count):
            S, date = universe[rng.randrange(len(universe))]
            lis, nets = placebo_day_nets(S, date, exit_name)
            k = rng.randrange(len(lis)); side = 1 if rng.random() < 0.5 else -1
            tot += nets[side][k]
        draws.append(tot)
    return draws

# ---------------------------------------------------------------- Part B
def load_daily(sym):
    path = os.path.join(WS, "data", "sarvaritu_fwd", sym, "spot_daily.csv")
    dates, o, h, l, c = [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            dates.append(r["date"]); o.append(float(r["open"])); h.append(float(r["high"]))
            l.append(float(r["low"])); c.append(float(r["close"]))
    return dates, np.array(o), np.array(h), np.array(l), np.array(c)

def run_swing(dates, o, h, l, c, entry_sig, exit_sig, overlay, atr=None, cap_pct=None):
    n = len(dates); trades = []; pos = None; i = 0
    k_trail = {"TRAIL2": 2.0, "TRAIL3": 3.0}.get(overlay)
    while i < n:
        if pos is None:
            if entry_sig[i] and i + 1 < n:
                pos = dict(e=i + 1, E=float(o[i + 1])); i += 1; continue
            i += 1; continue
        e, E = pos["e"], pos["E"]
        done = None
        if overlay == "TIME60" and i - e >= 60 and i > e:
            done = (i, float(o[i]), "TIME")
        elif k_trail and i > e and atr is not None and not np.isnan(atr[i - 1]):
            stop = float(np.max(c[e:i])) - k_trail * float(atr[i - 1])
            if o[i] <= stop: done = (i, float(o[i]), "TRAIL")
            elif l[i] <= stop: done = (i, stop, "TRAIL")
        if done is None and cap_pct is not None and i >= e:
            lvl = E * (1 + cap_pct)
            if h[i] >= lvl:
                done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
        if done is None and exit_sig[i]:
            if i + 1 < n: done = (i + 1, float(o[i + 1]), "SIGNAL")
            else: done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            trades.append(dict(entry_date=dates[e], exit_date=dates[xi], entry=E, exit=xp,
                               net=round((xp - E) * 100.0 - COST, 2), hold=xi - e,
                               exit_kind=why, forced=(why == "FORCED")))
            pos = None; i = xi; continue
        i += 1
    if pos is not None:
        e, E = pos["e"], pos["E"]
        xp = float(c[n - 1])
        trades.append(dict(entry_date=dates[e], exit_date=dates[n - 1], entry=E, exit=xp,
                           net=round((xp - E) * 100.0 - COST, 2), hold=n - 1 - e,
                           exit_kind="FORCED", forced=True))
    return trades

def part_b():
    systems = {}
    rows = []
    all_trades = {}
    for sym in NAMES:
        dates, o, h, l, c = load_daily(sym)
        n = len(dates)
        e50 = ema_series(c, 50); e100 = ema_series(c, 100); e200 = ema_series(c, 200)
        r14 = rsi_wilder(c, 14)
        mm, ss = macd_series(c, 12, 26, 9)
        stdir, _ln = supertrend_full(h, l, c, 10, 3.0)
        mid, sdv = bollinger_bands(c, 20); lower = mid - 2 * sdv
        atr = atr_wilder(h, l, c, 14)
        def cross_up(a, b):
            out = np.zeros(n, dtype=bool)
            ok = ~np.isnan(a) & ~np.isnan(b)
            out[1:] = ok[1:] & ok[:-1] & (a[:-1] <= b[:-1]) & (a[1:] > b[1:])
            return out
        def cross_dn(a, b):
            out = np.zeros(n, dtype=bool)
            ok = ~np.isnan(a) & ~np.isnan(b)
            out[1:] = ok[1:] & ok[:-1] & (a[:-1] >= b[:-1]) & (a[1:] < b[1:])
            return out
        fifty = np.full(n, 50.0)
        sys_defs = {
            "EMA50-X":  (cross_up(c, e50), cross_dn(c, e50), None),
            "EMA100-X": (cross_up(c, e100), cross_dn(c, e100), None),
            "EMA200-X": (cross_up(c, e200), cross_dn(c, e200), None),
            "GCROSS":   (cross_up(e50, e200), cross_dn(e50, e200), None),
            "RSI50":    (cross_up(r14, fifty), cross_dn(r14, fifty), None),
            "RSI-REV":  (cross_up(r14, np.full(n, 30.0)),
                         np.where(~np.isnan(r14), r14 >= 70, False), 0.10),
            "MACD-D":   (cross_up(mm, ss), cross_dn(mm, ss), None),
            "ST-D":     (np.concatenate([[False], (stdir[1:] == 1) & (stdir[:-1] == -1)]),
                         np.concatenate([[False], (stdir[1:] == -1) & (stdir[:-1] == 1)]), None),
            "BB-REV-D": (np.concatenate([[False], (c[:-1] < lower[:-1]) & (c[1:] >= lower[1:]) & ~np.isnan(lower[1:])]),
                         np.where(~np.isnan(mid), c >= mid, False), None),
        }
        for sname, (es, xs, cap) in sys_defs.items():
            for overlay in ("BASE", "TRAIL2", "TRAIL3", "TIME60"):
                tr = run_swing(dates, o, h, l, c, es, xs, overlay, atr=atr, cap_pct=cap)
                for t in tr: t["sym"] = sym
                all_trades.setdefault((sname, overlay), []).extend(tr)
    for (sname, overlay), tr in sorted(all_trades.items()):
        row = dict(system=sname, overlay=overlay, years={})
        curve = sorted(tr, key=lambda t: t["exit_date"])
        eq = 0.0; peak = 0.0; mdd = 0.0
        for t in curve:
            eq += t["net"]; peak = max(peak, eq); mdd = min(mdd, eq - peak)
        row["max_drawdown_rs"] = round(mdd, 2)
        for yr in (2025, 2026):
            sel = [t for t in tr if t["entry_date"][:4] == str(yr)
                   and int(t["entry_date"][5:7]) in range(1, 11)]
            tot = sum(t["net"] for t in sel)
            wins = sum(1 for t in sel if t["net"] > 0)
            row["years"][yr] = dict(
                trades=len(sel), total=round(tot, 2),
                wr=round(100.0 * wins / len(sel), 2) if sel else None,
                avg_hold=round(sum(t["hold"] for t in sel) / len(sel), 1) if sel else None,
                worst=round(min((t["net"] for t in sel), default=0.0), 2),
                forced=sum(1 for t in sel if t["forced"]))
        y25, y26 = row["years"][2025], row["years"][2026]
        row["counted"] = bool(y25["total"] > 0 and y26["total"] > 0
                              and y25["trades"] >= 10 and y26["trades"] >= 10)
        rows.append(row)
    return rows, all_trades

# ---------------------------------------------------------------- main
def main():
    print("prep Part A stocks...", flush=True)
    stocks = [prep_stock_a(s) for s in NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    # events per family-combo per stock
    events = {}   # (fam, combo_idx) -> {sym: {date: [events]}}
    for fam, fd in FAMILIES.items():
        for ci, combo in enumerate(fd["combos"]):
            per = {}
            gen = gen_events_reversion if fam in ("RSI-R", "BB-R") else gen_events
            for S in stocks:
                per[S["sym"]] = gen(S, combo)
            events[(fam, ci)] = per
        print("events done:", fam, flush=True)
    rng = random.Random(SEED_PLACEBO)
    rows = []            # per config
    val_total = {}       # (fam, coord, adx_idx, exit_idx, year) -> val total
    config_trades = {}   # key -> trades (kept for robust/CF use)
    for fam, fd in FAMILIES.items():
        exits_n = 4 if fd["trend"] else 3
        adx_list = [0, 1, 2] if fd["trend"] else [None]
        for ci, combo in enumerate(fd["combos"]):
            coord = combo_coord(fam, ci)
            for adx_idx in adx_list:
                adx_level = ADX_LEVELS[adx_idx] if adx_idx is not None else None
                for exit_idx in range(exits_n):
                    trades = run_config(stocks, events[(fam, ci)], fam, combo, adx_level, exit_idx)
                    key = (fam, ci, adx_idx, exit_idx)
                    config_trades[key] = trades
                    row = dict(family=fam, combo=list(combo[1:]), combo_idx=ci,
                               adx=adx_level, exit=EXITS[exit_idx][0], years={})
                    for yr in (2025, 2026):
                        disc = window_stats(trades, yr, (1, 2, 3, 4, 5, 6))
                        val = window_stats(trades, yr, (7, 8, 9, 10))
                        draws = placebo_pct(stocks, yr, EXITS[exit_idx][0], val["trades"], rng) \
                            if val["trades"] else None
                        pct = round(100.0 * sum(1 for d in draws if d < val["total"]) / len(draws), 1) \
                            if draws else None
                        row["years"][yr] = dict(
                            disc_total=disc["total"], disc_trades=disc["trades"],
                            val_total=val["total"], val_trades=val["trades"], val_wr=val["wr"],
                            val_months=val["months"], val_ex_top3=val["ex_top3"],
                            val_red_months=val["red_months"], val_pace=round(val["total"] / 4.0, 2),
                            val_placebo_pct=pct)
                        val_total[(fam, coord, adx_idx, exit_idx, yr)] = val["total"]
                    rows.append((key, row))
        print("configs done:", fam, flush=True)
    # robustness (neighbours need all val totals first)
    out_rows = []
    fam_summary = {}
    pass_keys = []
    for (key, row) in rows:
        fam, ci, adx_idx, exit_idx = key
        fd = FAMILIES[fam]
        coord = combo_coord(fam, ci)
        full_coord = list(coord) + ([adx_idx] if fd["trend"] else []) + [exit_idx]
        domains = list(fd["axes"]) + ([3] if fd["trend"] else []) + [4 if fd["trend"] else 3]
        robust = {}
        for yr in (2025, 2026):
            y = row["years"][yr]
            npos = 0
            for pos_i, dom in enumerate(domains):
                for delta in (-1, 1):
                    nc = list(full_coord); nc[pos_i] += delta
                    if nc[pos_i] < 0 or nc[pos_i] >= dom: continue
                    ncoord = tuple(nc[:len(coord)])
                    nci = coord_combo(fam, ncoord)
                    rest = nc[len(coord):]
                    nadx = rest[0] if fd["trend"] else None
                    nexit = rest[-1]
                    vt = val_total.get((fam, ncoord, nadx, nexit, yr))
                    if vt is not None and vt > 0: npos += 1
            pace_bar = 7500.0 if yr == 2026 else 5000.0
            fails = []
            if not y["disc_total"] > 0: fails.append("discovery<=0")
            if not y["val_total"] > 0: fails.append("validation<=0")
            if npos < 2: fails.append(f"neighbours {npos}<2")
            if not y["val_ex_top3"] > 0: fails.append("val ex-top-3<=0")
            if y["val_placebo_pct"] is None or y["val_placebo_pct"] < 95.0:
                fails.append(f"placebo {y['val_placebo_pct']}")
            if y["val_pace"] < pace_bar: fails.append(f"pace {y['val_pace']}<{pace_bar}")
            if y["val_red_months"] > 1: fails.append(f"red months {y['val_red_months']}>1")
            robust[yr] = dict(robust=not fails, neighbours_pos=npos, fails=fails)
        row["robust"] = robust
        row["pass"] = bool(robust[2025]["robust"] and robust[2026]["robust"])
        if row["pass"]: pass_keys.append(key)
        out_rows.append(row)
        fs = fam_summary.setdefault(fam, dict(configs=0, robust_2025=0, robust_2026=0, passed=0, best_raw=None))
        fs["configs"] += 1
        fs["robust_2025"] += 1 if robust[2025]["robust"] else 0
        fs["robust_2026"] += 1 if robust[2026]["robust"] else 0
        fs["passed"] += 1 if row["pass"] else 0
        score = row["years"][2025]["val_total"] + row["years"][2026]["val_total"]
        if fs["best_raw"] is None or score > fs["best_raw"]["_score"]:
            fs["best_raw"] = dict(combo=row["combo"], adx=row["adx"], exit=row["exit"],
                                  val_2025=row["years"][2025]["val_total"],
                                  val_2026=row["years"][2026]["val_total"],
                                  robust_2025=robust[2025]["robust"], robust_2026=robust[2026]["robust"],
                                  _score=score)
    # November CF for PASS configs only
    nov_cf = []
    for key in pass_keys:
        fam, ci, adx_idx, exit_idx = key
        combo = FAMILIES[fam]["combos"][ci]
        adx_level = ADX_LEVELS[adx_idx] if adx_idx is not None else None
        tr = run_config(stocks, events[(fam, ci)], fam, combo, adx_level, exit_idx,
                        dates_wanted=set(NOV_DATES))
        nov_cf.append(dict(family=fam, combo=list(combo[1:]), adx=adx_level,
                           exit=EXITS[exit_idx][0], trades=len(tr),
                           total=round(sum(t["net"] for t in tr), 2)))
    print("Part A done. PASS configs:", len(pass_keys), flush=True)
    print("running Part B...", flush=True)
    b_rows, b_trades = part_b()
    print("Part B done.", flush=True)
    results = dict(
        basis="equity cash, frozen 25 names, per 100 shares PROVISIONAL, Rs40/trade, paper only, real money Rs0",
        partA=dict(families=fam_summary, configs=out_rows, november_cf=nov_cf),
        partB=dict(rows=b_rows))
    with open(os.path.join(WS, "indicator_parameter_tuning_stocks_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(WS, "indicator_parameter_tuning_stocks_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part", "family_or_system", "combo", "adx_or_overlay", "exit",
                    "sym", "date", "side_or_hold", "entry", "exit_px", "net"])
        for (key, row) in rows:
            if row["robust"][2025]["robust"] or row["robust"][2026]["robust"]:
                fam, ci, adx_idx, exit_idx = key
                for t in config_trades[key]:
                    w.writerow(["A", fam, row["combo"], row["adx"], row["exit"], t["sym"],
                                t["date"], t["side"], t["entry"], t["exit"], round(t["net"], 2)])
        for key in pass_keys:
            fam, ci, adx_idx, exit_idx = key
            combo = FAMILIES[fam]["combos"][ci]
            adx_level = ADX_LEVELS[adx_idx] if adx_idx is not None else None
            tr = run_config(stocks, events[(fam, ci)], fam, combo, adx_level, exit_idx,
                            dates_wanted=set(NOV_DATES))
            for t in tr:
                w.writerow(["A-NOV", fam, list(combo[1:]), adx_level, EXITS[exit_idx][0],
                            t["sym"], t["date"], t["side"], t["entry"], t["exit"], round(t["net"], 2)])
        for (sname, overlay), tr in sorted(b_trades.items()):
            for t in tr:
                w.writerow(["B", sname, "", overlay, t["exit_kind"], t["sym"], t["entry_date"],
                            t["hold"], t["entry"], t["exit"], t["net"]])
    # ---- console summary
    for fam, fs in fam_summary.items():
        br = fs["best_raw"]
        print(f"A {fam}: configs {fs['configs']} robust25 {fs['robust_2025']} robust26 {fs['robust_2026']} "
              f"PASS {fs['passed']} | best raw {br['combo']} adx {br['adx']} {br['exit']} "
              f"val25 {br['val_2025']} val26 {br['val_2026']}")
    for pc in nov_cf:
        print("NOV CF:", pc)
    for r in b_rows:
        print(f"B {r['system']} {r['overlay']}: 2025 {r['years'][2025]['trades']}t {r['years'][2025]['total']} "
              f"WR {r['years'][2025]['wr']} hold {r['years'][2025]['avg_hold']} | "
              f"2026 {r['years'][2026]['trades']}t {r['years'][2026]['total']} WR {r['years'][2026]['wr']} "
              f"hold {r['years'][2026]['avg_hold']} | DD {r['max_drawdown_rs']} COUNTED {r['counted']}")

if __name__ == "__main__":
    main()
