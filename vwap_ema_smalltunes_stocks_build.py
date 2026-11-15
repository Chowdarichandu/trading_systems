#!/usr/bin/env python3
"""SMALL TUNES — VWAP x EMA CROSSOVER, Stocks intraday.
Spec: vwap_ema_smalltunes_stocks_SPEC.md (frozen 2026-11-14, before scoring).
Research only. Reads data/sarvaritu_fwd/<SYM>/spot_5m.csv. Writes
vwap_ema_smalltunes_stocks_results.json. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade.
VWAP = equal-weighted typical-price proxy (stores carry no volume) — disclosed in spec.
"""
import csv, json, math, os, random
import numpy as np
from collections import defaultdict

WS = os.path.dirname(os.path.abspath(__file__))
NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC "
         "INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD "
         "TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO").split()
COST = 40.0
SEED = 20261114
SQ_STAMP = "15:10"
LAST_ENTRY_STAMP = "15:10"
PAIRS = [(5, 20), (9, 21), (13, 34), (20, 50)]
SPANS = sorted({s for p in PAIRS for s in p})
BUFFERS = [0.0, 0.0005, 0.0010]
HOLDS = [0, 1]
EXITS = ["X1", "X2", "X3", "X4"]
JAN_OCT = ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")
NOV_DATES = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
             "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]

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

def ema_series(c, span):
    """DIAL-Stocks construction: SMA seed of first `span` closes, continuous series."""
    n = len(c); out = np.full(n, np.nan)
    if n < span: return out
    out[span - 1] = c[:span].mean()
    k = 2.0 / (span + 1.0)
    for i in range(span, n):
        out[i] = c[i] * k + out[i - 1] * (1.0 - k)
    return out

# ---------------------------------------------------------------- exits
def exit_tp_sl(o, h, l, c, entry_li, sq_li, E, side, tgt_m, stp_m):
    """X1/X2 geometry. Stop-first on same-bar overlap; gap-through fills at open (DIAL)."""
    if side == 1:
        tgt, stp = E * tgt_m, E * stp_m
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= tgt: return oj
            if oj <= stp: return oj
            th, sh = hj >= tgt, lj <= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    else:
        tgt, stp = E * (2.0 - tgt_m), E * (2.0 - stp_m)
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj <= tgt: return oj
            if oj >= stp: return oj
            th, sh = lj <= tgt, hj >= stp
            if sh and th: return stp
            if th: return tgt
            if sh: return stp
    return c[sq_li]

def _hard_stop_hit(o, h, l, j, E, side):
    """X3/X4 hard stop -0.75%: returns fill price if hit on bar j, else None."""
    if side == 1:
        stp = E * 0.9925
        if o[j] <= stp: return o[j]
        if l[j] <= stp: return stp
    else:
        stp = E * 1.0075
        if o[j] >= stp: return o[j]
        if h[j] >= stp: return stp
    return None

def exit_x3(o, h, l, c, vwap, entry_li, sq_li, E, side):
    for j in range(entry_li, sq_li + 1):
        hs = _hard_stop_hit(o, h, l, j, E, side)
        if hs is not None: return hs
        if side == 1 and c[j] < vwap[j]: return c[j]
        if side == -1 and c[j] > vwap[j]: return c[j]
    return c[sq_li]

def exit_x4(o, h, l, c, opp_cross, a, entry_li, sq_li, E, side):
    """opp_cross = global bool array of crosses AGAINST the position's direction."""
    for j in range(entry_li, sq_li + 1):
        hs = _hard_stop_hit(o, h, l, j, E, side)
        if hs is not None: return hs
        if opp_cross[a + j]: return c[j]
    return c[sq_li]

def trade_net(E, exit_px, side):
    return ((exit_px - E) if side == 1 else (E - exit_px)) * 100.0 - COST

# ---------------------------------------------------------------- per-stock build
def build_stock(sym):
    ts, o, h, l, c = load_stock(sym)
    seg = day_segments(ts)
    stamps = [t[11:16] for t in ts]
    emas = {s: ema_series(c, s) for s in SPANS}
    pair_arrays = {}
    for (f, s) in PAIRS:
        fa, sa = emas[f], emas[s]
        valid = ~np.isnan(fa) & ~np.isnan(sa)
        xup = np.zeros(len(c), dtype=bool); xdn = np.zeros(len(c), dtype=bool)
        if len(c) > 1:
            up = valid[1:] & valid[:-1] & (fa[:-1] <= sa[:-1]) & (fa[1:] > sa[1:])
            dn = valid[1:] & valid[:-1] & (fa[:-1] >= sa[:-1]) & (fa[1:] < sa[1:])
            xup[1:] = up; xdn[1:] = dn
        pair_arrays[(f, s)] = dict(xup=xup, xdn=xdn, align_up=np.where(valid, fa > sa, False))
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
    return dict(sym=sym, ts=ts, stamps=stamps, o=o, h=h, l=l, c=c,
                pair_arrays=pair_arrays, days=days)

# ---------------------------------------------------------------- candidates
def _entry_ok(D, entry_li):
    return entry_li < len(D["st"]) and D["st"][entry_li] <= LAST_ENTRY_STAMP

def cand_a(S, D, hold, buf):
    """Rule A (and C2's cross engine): first VWAP cross whose hold confirmation passes."""
    c, vwap, st = D["c"], D["vwap"], D["st"]
    vup, vdn = vwap * (1.0 + buf), vwap * (1.0 - buf)
    n = len(st)
    for li in range(1, n):
        if D["a"] + li < 59:  # warm-up: >=60 bars of history incl. signal bar
            continue
        side = 0
        if c[li - 1] <= vup[li - 1] and c[li] > vup[li]: side = 1
        elif c[li - 1] >= vdn[li - 1] and c[li] < vdn[li]: side = -1
        if side == 0: continue
        ok = True
        for k in range(1, hold + 1):
            j = li + k
            if j >= n: ok = False; break
            if side == 1 and not c[j] > vup[j]: ok = False; break
            if side == -1 and not c[j] < vdn[j]: ok = False; break
        if not ok: continue
        eli = li + hold + 1
        if not _entry_ok(D, eli): return None
        return dict(date=None, side=side, signal_li=li, entry_li=eli,
                    signal_stamp=st[li], entry_stamp=st[eli])
    return None

def cand_c2(S, D, pair, hold, buf):
    """Rule C2: Rule A cross + EMA pair already aligned at the cross bar."""
    c, vwap, st = D["c"], D["vwap"], D["st"]
    vup, vdn = vwap * (1.0 + buf), vwap * (1.0 - buf)
    align = S["pair_arrays"][pair]["align_up"]
    # alignment needs the pair's slow EMA valid at the bar; align_up False when NaN —
    # but fast>slow False also when fast<slow; distinguish via a validity check:
    n = len(st)
    for li in range(1, n):
        g = D["a"] + li
        if g < 59: continue
        side = 0
        if c[li - 1] <= vup[li - 1] and c[li] > vup[li]: side = 1
        elif c[li - 1] >= vdn[li - 1] and c[li] < vdn[li]: side = -1
        if side == 0: continue
        # EMA validity at g: both EMAs non-NaN — approximate via slow span warm-up index
        if g < pair[1] - 1: continue
        if side == 1 and not align[g]: continue
        if side == -1 and align[g]: continue
        if side == -1:
            # align_up False could mean fast<slow (good) — fast==slow impossible in floats
            pass
        ok = True
        for k in range(1, hold + 1):
            j = li + k
            if j >= n: ok = False; break
            if side == 1 and not c[j] > vup[j]: ok = False; break
            if side == -1 and not c[j] < vdn[j]: ok = False; break
        if not ok: continue
        eli = li + hold + 1
        if not _entry_ok(D, eli): return None
        return dict(date=None, side=side, signal_li=li, entry_li=eli,
                    signal_stamp=st[li], entry_stamp=st[eli])
    return None

def cand_b(S, D, pair):
    """Rule B: first EMA cross of the day (continuous series)."""
    pa = S["pair_arrays"][pair]
    st = D["st"]; n = len(st)
    for li in range(n):
        g = D["a"] + li
        if g < 59: continue
        side = 1 if pa["xup"][g] else (-1 if pa["xdn"][g] else 0)
        if side == 0: continue
        eli = li + 1
        if not _entry_ok(D, eli): return None
        return dict(date=None, side=side, signal_li=li, entry_li=eli,
                    signal_stamp=st[li], entry_stamp=st[eli])
    return None

def cand_c(S, D, pair, buf):
    """Rule C: EMA cross whose bar closes beyond the buffered VWAP on the matching side."""
    pa = S["pair_arrays"][pair]
    c, vwap, st = D["c"], D["vwap"], D["st"]
    vup, vdn = vwap * (1.0 + buf), vwap * (1.0 - buf)
    n = len(st)
    for li in range(n):
        g = D["a"] + li
        if g < 59: continue
        if pa["xup"][g] and c[li] > vup[li]: side = 1
        elif pa["xdn"][g] and c[li] < vdn[li]: side = -1
        else: continue
        eli = li + 1
        if not _entry_ok(D, eli): return None
        return dict(date=None, side=side, signal_li=li, entry_li=eli,
                    signal_stamp=st[li], entry_stamp=st[eli])
    return None

BASES = []  # (rule, pair, hold, buffer, finder-key)
for hold in HOLDS:
    for buf in BUFFERS:
        BASES.append(("A", None, hold, buf))
for pair in PAIRS:
    BASES.append(("B", pair, None, None))
for pair in PAIRS:
    for buf in BUFFERS:
        BASES.append(("C", pair, None, buf))
for pair in PAIRS:
    for hold in HOLDS:
        for buf in BUFFERS:
            BASES.append(("C2", pair, hold, buf))

def find_candidates(S, base):
    """All per-stock-day candidates for one base config across the full store."""
    rule, pair, hold, buf = base
    out = []
    for date, D in sorted(S["days"].items()):
        if not D["tradable"]: continue
        if rule == "A": cd = cand_a(S, D, hold, buf)
        elif rule == "B": cd = cand_b(S, D, pair)
        elif rule == "C": cd = cand_c(S, D, pair, buf)
        else: cd = cand_c2(S, D, pair, hold, buf)
        if cd is not None:
            cd["date"] = date; cd["sym"] = S["sym"]
            out.append(cd)
    return out

def apply_daily_cap(cands):
    """<=1/stock/day already true by construction; cap <=5/day, earliest signals first."""
    by_date = defaultdict(list)
    for cd in cands: by_date[cd["date"]].append(cd)
    kept = []
    for date, lst in by_date.items():
        lst.sort(key=lambda x: (x["signal_stamp"], x["entry_stamp"], x["sym"]))
        kept.extend(lst[:5])
    return kept

# ---------------------------------------------------------------- exit dispatch
_exit_cache = {}
def eval_exit(S, D, entry_li, side, exit_id, pair):
    key = (S["sym"], D["a"], entry_li, side, exit_id, pair)
    if key in _exit_cache: return _exit_cache[key]
    o, h, l, c = D["o"], D["h"], D["l"], D["c"]
    E = float(o[entry_li]); sq = D["sq_li"]
    if exit_id == "X1": xp = exit_tp_sl(o, h, l, c, entry_li, sq, E, side, 1.008, 0.996)
    elif exit_id == "X2": xp = exit_tp_sl(o, h, l, c, entry_li, sq, E, side, 1.010, 0.995)
    elif exit_id == "X3": xp = exit_x3(o, h, l, c, D["vwap"], entry_li, sq, E, side)
    else:
        pa = S["pair_arrays"][pair]
        opp = pa["xdn"] if side == 1 else pa["xup"]
        xp = exit_x4(o, h, l, c, opp, D["a"], entry_li, sq, E, side)
    xp = float(xp)
    _exit_cache[key] = xp
    return xp

def x4_pair_for(rule, pair):
    return pair if pair is not None else (9, 21)

# ---------------------------------------------------------------- summarising
def summarise(trades):
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    return dict(trades=len(trades), net=round(tot, 2),
                wr=round(100.0 * wins / len(trades), 2) if trades else None)

def window_block(trades, year):
    def sel(months):
        return [t for t in trades if t["date"][:4] == str(year) and t["date"][5:7] in months]
    return dict(jan_jun=summarise(sel(("01", "02", "03", "04", "05", "06"))),
                jul_oct=summarise(sel(("07", "08", "09", "10"))),
                full=summarise(sel(JAN_OCT)))

# ---------------------------------------------------------------- placebo
def placebo_pct(stocks_by_sym, year, count, exit_id, pair, rng):
    universe = []
    for S in stocks_by_sym:
        for date, D in S["days"].items():
            if date[:4] == str(year) and date[5:7] in JAN_OCT and D["tradable"]:
                entries = [li for li, s in enumerate(D["st"]) if "09:20" <= s <= LAST_ENTRY_STAMP]
                if entries: universe.append((S, D, entries))
    draws = []
    for _ in range(200):
        tot = 0.0
        for _ in range(count):
            S, D, entries = universe[rng.randrange(len(universe))]
            eli = entries[rng.randrange(len(entries))]
            side = 1 if rng.random() < 0.5 else -1
            E = float(D["o"][eli])
            xp = eval_exit(S, D, eli, side, exit_id, pair)
            tot += trade_net(E, xp, side)
        draws.append(tot)
    return draws

# ---------------------------------------------------------------- main
def main():
    stocks = [build_stock(s) for s in NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    # coverage check (mirror DIAL-Stocks: 2025 5200 stock-days / 25 NC; 2026 5125 / 0 NC)
    cov = {}
    for yr in (2025, 2026):
        sd = nc = 0
        for S in stocks:
            for date, D in S["days"].items():
                if date[:4] == str(yr) and date[5:7] in JAN_OCT:
                    sd += 1
                    if not D["tradable"]: nc += 1
        cov[yr] = dict(stock_days=sd, nc_stock_days=nc)
    print("coverage:", cov, flush=True)

    rows = []          # one entry per (base, exit) row
    audit_checked = 0
    for base in BASES:
        rule, pair, hold, buf = base
        cands = []
        for S in stocks:
            cands.extend(find_candidates(S, base))
        kept = apply_daily_cap(cands)
        for cd in kept:
            assert cd["entry_stamp"] > cd["signal_stamp"]
            audit_checked += 1
        for exit_id in EXITS:
            xp_pair = x4_pair_for(rule, pair)
            trades = []
            for cd in kept:
                S = by_sym[cd["sym"]]; D = S["days"][cd["date"]]
                E = float(D["o"][cd["entry_li"]])
                xp = eval_exit(S, D, cd["entry_li"], cd["side"], exit_id, xp_pair)
                trades.append(dict(sym=cd["sym"], date=cd["date"], side=cd["side"],
                                   signal_stamp=cd["signal_stamp"], entry_stamp=cd["entry_stamp"],
                                   entry=E, exit=xp, net=trade_net(E, xp, cd["side"])))
            row = dict(rule=rule, pair=list(pair) if pair else None, hold=hold,
                       buffer=buf, exit=exit_id, trades_all=trades,
                       years={yr: window_block(trades, yr) for yr in (2025, 2026)})
            rows.append(row)
        print("base done:", base, "kept candidates:", len(kept), flush=True)

    # best row per rule per year (full Jan-Oct net; ties: WR, then grid order)
    best = {}
    for rule in ("A", "B", "C", "C2"):
        best[rule] = {}
        for yr in (2025, 2026):
            cand_rows = [r for r in rows if r["rule"] == rule]
            def keyf(r):
                f = r["years"][yr]["full"]
                return (f["net"], f["wr"] if f["wr"] is not None else -1.0)
            br = max(cand_rows, key=keyf)
            best[rule][yr] = br
    # placebo on best rows only
    rng = random.Random(SEED)
    placebo = {}
    for rule in ("A", "B", "C", "C2"):
        placebo[rule] = {}
        for yr in (2025, 2026):
            br = best[rule][yr]
            cnt = br["years"][yr]["full"]["trades"]
            real = br["years"][yr]["full"]["net"]
            if cnt == 0:
                placebo[rule][yr] = dict(percentile=None, real=real, count=0)
                continue
            draws = placebo_pct(stocks, yr, cnt, br["exit"],
                                x4_pair_for(rule, br["pair"] and tuple(br["pair"])), rng)
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1)
            placebo[rule][yr] = dict(percentile=pct, real=real, count=cnt,
                                     draws_min=round(min(draws), 2),
                                     draws_median=round(sorted(draws)[100], 2),
                                     draws_max=round(max(draws), 2))
            print("placebo:", rule, yr, "pct", pct, "real", real, "count", cnt, flush=True)
    # November CF: each rule's best row (selected on 2026) over the 9 book days
    nov_cf = {}
    for rule in ("A", "B", "C", "C2"):
        br = best[rule][2026]
        sel = [t for t in br["trades_all"] if t["date"] in NOV_DATES]
        by_day = {d: round(sum(t["net"] for t in sel if t["date"] == d), 2) for d in NOV_DATES}
        nov_cf[rule] = dict(row=dict(pair=br["pair"], hold=br["hold"], buffer=br["buffer"],
                                     exit=br["exit"]),
                            summary=summarise(sel), by_day=by_day,
                            trade_list=[{k: t[k] for k in ("sym", "date", "side", "signal_stamp",
                                                            "entry_stamp", "entry", "exit", "net")} for t in sel])
    out = dict(
        basis="equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
              "VWAP = equal-weighted typical-price proxy (stores carry no volume)",
        spec="vwap_ema_smalltunes_stocks_SPEC.md",
        coverage=cov, timing_audit_assertions=audit_checked,
        rows=[dict(rule=r["rule"], pair=r["pair"], hold=r["hold"], buffer=r["buffer"],
                   exit=r["exit"], years=r["years"]) for r in rows],
        best={rule: {str(yr): dict(pair=best[rule][yr]["pair"], hold=best[rule][yr]["hold"],
                                   buffer=best[rule][yr]["buffer"], exit=best[rule][yr]["exit"],
                                   full=best[rule][yr]["years"][yr]["full"],
                                   jan_jun=best[rule][yr]["years"][yr]["jan_jun"],
                                   jul_oct=best[rule][yr]["years"][yr]["jul_oct"])
                     for yr in (2025, 2026)} for rule in best},
        placebo={rule: {str(yr): placebo[rule][yr] for yr in (2025, 2026)} for rule in placebo},
        november_cf=nov_cf,
        stock_book_nov_actual=7517.94)
    with open(os.path.join(WS, "vwap_ema_smalltunes_stocks_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE vwap_ema_smalltunes_stocks_results.json")
    for rule in ("A", "B", "C", "C2"):
        for yr in (2025, 2026):
            b = best[rule][yr]
            print(rule, yr, "BEST pair", b["pair"], "hold", b["hold"], "buf", b["buffer"],
                  "exit", b["exit"], "full", b["years"][yr]["full"],
                  "placebo_pct", placebo[rule][yr]["percentile"])
    for rule in ("A", "B", "C", "C2"):
        print("NOV CF", rule, nov_cf[rule]["summary"], "row", nov_cf[rule]["row"])

if __name__ == "__main__":
    main()
