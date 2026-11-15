#!/usr/bin/env python3
"""EKAM-INTRADAY — BANK NIFTY vote-clubbed intraday indicator system,
Jan-Oct 2026 + Nov 2-13 CF. Spec: ekam_intraday_bank_SPEC.md (frozen
2026-11-14 before this run). Local stores only — NO API calls.
Research only: reads stores, writes ekam_intraday_bank_results.json
+ ekam_intraday_bank_2026-11-14.md only."""
import bisect, csv, json, math, random, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
LOT, COST, SQ = 30, 220.0, "15:20"
X1_STOP, X1_TARGET = 50.0, 90.0
X2_HARDSTOP = 60.0
STEP = 100
SEED = 20261114
ROWS = [(4, "X1"), (4, "X2"), (5, "X1"), (5, "X2")]
ROWNAME = {(4, "X1"): "T4-X1", (4, "X2"): "T4-X2",
           (5, "X1"): "T5-X1", (5, "X2"): "T5-X2"}

# ---------------- spot (continuous series) ----------------
spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot = spot[(spot["timestamp"] >= "2026-01-01") &
            (spot["timestamp"] <= "2026-11-13")].sort_values("timestamp")
spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
O = spot["open"].to_numpy(float); H = spot["high"].to_numpy(float)
L = spot["low"].to_numpy(float);  C = spot["close"].to_numpy(float)
DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
N = len(C)
day_idx = {}
for i, d in enumerate(DATES):
    day_idx.setdefault(d, []).append(i)
GATE_DAYS = sorted(d for d in day_idx if d <= "2026-10-31")
NOV_DAYS = sorted(d for d in day_idx if "2026-11-02" <= d <= "2026-11-13")
POS = {}
for d, idxs in day_idx.items():
    for p, gi in enumerate(idxs):
        POS[gi] = p

# ---------------- expiry map ----------------
EXP = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        EXP[r["date"]] = r["expiry"]
for d in NOV_DAYS:
    EXP[d] = "2026-11-23"

# ---------------- futures session VWAP ----------------
_fut = {}
def fut_day(exp, day):
    if exp not in _fut:
        fn = TR / f"round5_history/FUT7_{exp}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]),
                                                  float(r[6]))
        _fut[exp] = byd
    return _fut[exp].get(day)

def vwap_series(day):
    fd = fut_day(EXP[day], day)
    if not fd:
        return None
    out, cum_pv, cum_v = {}, 0.0, 0.0
    for t in sorted(fd):
        o, h, l, c, v = fd[t]
        tp = (h + l + c) / 3.0
        cum_pv += tp * v; cum_v += v
        out[t] = cum_pv / cum_v if cum_v > 0 else None
    return out

def day_vwap(day):
    raw = vwap_series(day)
    if raw is None:
        return None
    ftimes = sorted(raw)
    out = {}
    for gi in day_idx[day]:
        t = TIMES[gi]
        j = bisect.bisect_right(ftimes, t) - 1
        out[t] = raw[ftimes[j]] if j >= 0 else None
    return out

# ---------------- premium stores (house resolution order) ----------------
_c5 = {}
def prem_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = TR / f"round5_history/C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]))
        _c5[ck] = byd
    return _c5[ck].get(day)

PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
_prem_cache = {}
def prem_store(exp, strike, typ, day):
    ck = (exp, strike, typ, day)
    if ck in _prem_cache:
        return _prem_cache[ck]
    res = prem_c5(exp, strike, typ, day)
    if not res:
        cd = PREM_B.get(f"{exp}|{int(strike)}|{typ}", {}).get(day)
        if cd:
            res = {t: tuple(float(x) for x in v) for t, v in cd.items()}
    if not res:
        for folder in ("btst_data", "november_shadow_data",
                       "nifty_weekly_expiry_chain", "oi_buildup_data"):
            fn = TR / folder / f"candles_BANKNIFTY_{int(strike)}{typ}_{exp}_{day}.json"
            if fn.exists():
                body = json.loads(fn.read_text())
                rows = [c for c in ((body.get("data") or {}).get("candles")
                                    or []) if c[0][:10] == day]
                if rows:
                    res = {c[0][11:16]: (float(c[1]), float(c[2]),
                                         float(c[3]), float(c[4]))
                           for c in rows}
                    break
    _prem_cache[ck] = res
    return res

# ---------------- indicators (house implementations) ----------------
def ema_series(c, period):
    n = len(c); out = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(c[:period]) / period
    for i in range(period, n):
        out[i] = c[i] * k + out[i - 1] * (1 - k)
    return out

def wilder_atr(h, l, c, period=7):
    n = len(c); tr = [None] * n; atr = [None] * n
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    if n > period:
        atr[period] = sum(tr[1:period + 1]) / period
        for i in range(period + 1, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def supertrend(h, l, c, period=7, mult=3.0):
    n = len(c); atr = wilder_atr(h, l, c, period)
    direc = [None] * n; fu = [None] * n; fl = [None] * n
    for i in range(n):
        if atr[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2.0
        bu = hl2 + mult * atr[i]; bl = hl2 - mult * atr[i]
        if fu[i - 1] is None:
            fu[i], fl[i] = bu, bl
            direc[i] = "up" if c[i] >= hl2 else "down"
            continue
        fu[i] = bu if (bu < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = bl if (bl > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        if direc[i - 1] == "up":
            direc[i] = "down" if c[i] < fl[i] else "up"
        else:
            direc[i] = "up" if c[i] > fu[i] else "down"
    return direc

def rsi_wilder(c, period=14):
    n = len(c); out = [None] * n
    if n <= period:
        return out
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
    ag = sum(gains[:period]) / period; al = sum(losses[:period]) / period
    def _r(ag_, al_):
        return 100.0 if al_ == 0 else 100.0 - 100.0 / (1.0 + ag_ / al_)
    out[period] = _r(ag, al)
    for i in range(period + 1, n):
        ag = (ag * (period - 1) + gains[i - 1]) / period
        al = (al * (period - 1) + losses[i - 1]) / period
        out[i] = _r(ag, al)
    return out

def macd_from(c, fast=12, slow=26, sig=9):
    ef, es = ema_series(c, fast), ema_series(c, slow)
    n = len(c); line = [None] * n
    for i in range(n):
        if ef[i] is not None and es[i] is not None:
            line[i] = ef[i] - es[i]
    start = next(i for i in range(n) if line[i] is not None)
    vals = [line[i] for i in range(start, n)]
    sigv = ema_series(vals, sig)
    signal = [None] * n
    for j, i in enumerate(range(start, n)):
        signal[i] = sigv[j]
    return line, signal

def adx_wilder(h, l, c, period=14):
    n = len(c)
    tr = [0.0] * n; pdm = [0.0] * n; ndm = [0.0] * n
    for i in range(1, n):
        up_move = h[i] - h[i - 1]; dn_move = l[i - 1] - l[i]
        pdm[i] = up_move if (up_move > dn_move and up_move > 0) else 0.0
        ndm[i] = dn_move if (dn_move > up_move and dn_move > 0) else 0.0
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    dx = [None] * n
    if n > period:
        str_ = sum(tr[1:period + 1]); sp = sum(pdm[1:period + 1])
        sn = sum(ndm[1:period + 1])
        for i in range(period, n):
            if i > period:
                str_ = str_ - str_ / period + tr[i]
                sp = sp - sp / period + pdm[i]
                sn = sn - sn / period + ndm[i]
            if str_ > 0:
                dip = 100.0 * sp / str_; din = 100.0 * sn / str_
                dx[i] = 0.0 if (dip + din) == 0 else \
                    100.0 * abs(dip - din) / (dip + din)
    out = [None] * n
    first = 2 * period - 1
    if n > first and all(dx[j] is not None for j in range(period, first + 1)):
        out[first] = sum(dx[period:first + 1]) / period
        for i in range(first + 1, n):
            if dx[i] is not None and out[i - 1] is not None:
                out[i] = (out[i - 1] * (period - 1) + dx[i]) / period
    return out

EMA9 = ema_series(C, 9)
EMA21 = ema_series(C, 21)
ST_DIR = supertrend(H, L, C, 7, 3.0)
MACD_LINE, MACD_SIG = macd_from(C, 12, 26, 9)
RSI = rsi_wilder(C, 14)
ADX = adx_wilder(H, L, C, 14)

# ---------------- votes ----------------
VWAP_BY_DAY = {}
LV = [0] * N; SV = [0] * N
vwap_unavail_bars = 0
for day in GATE_DAYS + NOV_DAYS:
    vw = day_vwap(day)
    VWAP_BY_DAY[day] = vw
    for gi in day_idx[day]:
        t = TIMES[gi]
        v = vw.get(t) if vw else None
        if v is None:
            vwap_unavail_bars += 1
        ld = sd = 0
        if v is not None:
            if C[gi] > v: ld += 1
            elif C[gi] < v: sd += 1
        e9, e21 = EMA9[gi], EMA21[gi]
        if e9 is not None and e21 is not None:
            if e9 > e21: ld += 1
            elif e9 < e21: sd += 1
        if ST_DIR[gi] == "up": ld += 1
        elif ST_DIR[gi] == "down": sd += 1
        ml, ms = MACD_LINE[gi], MACD_SIG[gi]
        if ml is not None and ms is not None:
            if ml > ms: ld += 1
            elif ml < ms: sd += 1
        r = RSI[gi]
        if r is not None:
            if 50 <= r < 70: ld += 1
            if 30 < r <= 50: sd += 1
        a = ADX[gi]
        L_, S_ = ld, sd
        if a is not None and a >= 20:
            if ld > sd: L_ = ld + 1
            elif sd > ld: S_ = sd + 1
        LV[gi] = L_; SV[gi] = S_

# per-day vote dicts (time -> (L, S)) for the X2 decay walk
DAY_VOTES = {d: {TIMES[gi]: (LV[gi], SV[gi]) for gi in day_idx[d]}
             for d in GATE_DAYS + NOV_DAYS}

# vote-count distribution (gate window)
dist = {m: 0 for m in range(7)}
for day in GATE_DAYS:
    M = max(max(LV[gi], SV[gi]) for gi in day_idx[day])
    dist[M] += 1

# ---------------- helpers ----------------
def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

def scan_signal(day, T):
    """First bar of the day reaching T votes. Returns (gi, side),
    'LATE', or None."""
    idxs = day_idx[day]
    for pos, gi in enumerate(idxs):
        L_, S_ = LV[gi], SV[gi]
        if L_ >= T or S_ >= T:
            side = "up" if L_ >= S_ else "down"
            if TIMES[gi] <= "15:10" and pos < len(idxs) - 1:
                return (gi, side)
            return "LATE"
    return None

def _open_trade(day, entry_gi, ref_close, side):
    strike = int(math.floor(ref_close / STEP + 0.5)) * STEP
    typ = "CE" if side == "up" else "PE"
    exp = EXP[day]
    prem = prem_store(exp, strike, typ, day)
    if not prem:
        return None
    et = TIMES[entry_gi]
    if et not in prem:
        return None
    return strike, typ, exp, prem, et, prem[et][0]

def score_x1(day, entry_gi, ref_close, side):
    got = _open_trade(day, entry_gi, ref_close, side)
    if got is None:
        return None
    strike, typ, exp, prem, et, entry_px = got
    exit_px = reason = xt = None
    m = tmin(et)
    while m <= tmin(SQ):
        t = tstr(m)
        bar = prem.get(t)
        if bar is None:
            return None
        o, h, l, c = bar
        if l <= entry_px - X1_STOP:
            exit_px, reason, xt = entry_px - X1_STOP, "stop", t
            break
        if h >= entry_px + X1_TARGET:
            exit_px, reason, xt = entry_px + X1_TARGET, "target", t
            break
        if t == SQ:
            exit_px, reason, xt = c, "squareoff", t
            break
        m += 5
    if exit_px is None:
        return None
    return dict(date=day, side=side, strike=strike, typ=typ, expiry=exp,
                entry_time=et, entry_px=entry_px, exit_time=xt,
                exit_px=exit_px, exit_reason=reason,
                net=(exit_px - entry_px) * LOT - COST)

def score_x2(day, entry_gi, ref_close, side):
    got = _open_trade(day, entry_gi, ref_close, side)
    if got is None:
        return None
    strike, typ, exp, prem, et, entry_px = got
    votes = DAY_VOTES[day]
    exit_px = reason = xt = None
    m = tmin(et)
    while m <= tmin(SQ):
        t = tstr(m)
        bar = prem.get(t)
        if bar is None:
            return None
        o, h, l, c = bar
        if l <= entry_px - X2_HARDSTOP:
            exit_px, reason, xt = entry_px - X2_HARDSTOP, "hard_stop", t
            break
        if t == SQ:
            exit_px, reason, xt = c, "squareoff", t
            break
        vt = votes.get(t)
        if vt is not None:
            own = vt[0] if side == "up" else vt[1]
            if own <= 2:
                exit_px, reason, xt = c, "vote_decay", t
                break
        m += 5
    if exit_px is None:
        return None
    return dict(date=day, side=side, strike=strike, typ=typ, expiry=exp,
                entry_time=et, entry_px=entry_px, exit_time=xt,
                exit_px=exit_px, exit_reason=reason,
                net=(exit_px - entry_px) * LOT - COST)

SCORERS = {"X1": score_x1, "X2": score_x2}

def run_row(days, T, exit_rule):
    trades, audit_bars = [], []
    cnt = dict(signals=0, late=0, nc=0)
    for day in days:
        s = scan_signal(day, T)
        if s is None:
            continue
        if s == "LATE":
            cnt["late"] += 1
            continue
        gi, side = s
        cnt["signals"] += 1
        audit_bars.append(gi)
        idxs = day_idx[day]
        entry_gi = idxs[POS[gi] + 1]
        tr = SCORERS[exit_rule](day, entry_gi, C[gi], side)
        if tr is None:
            cnt["nc"] += 1
        else:
            tr["signal_time"] = TIMES[gi]
            tr["signal_votes"] = LV[gi] if side == "up" else SV[gi]
            trades.append(tr)
    return trades, cnt, audit_bars

def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = sum(t["net"] for t in trades)
    tdays = len(set(t["date"] for t in trades))
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                total=round(total, 2), trade_days=tdays,
                per_td=round(total / tdays, 2) if tdays else 0.0)

def window_stats(trades):
    w1 = [t for t in trades if t["date"][:7] <= "2026-06"]
    w2 = [t for t in trades if t["date"][:7] >= "2026-07"]
    return dict(jan_jun=stats(w1), jul_oct=stats(w2), full=stats(trades))

# ---------------- run the four rows ----------------
results = {}
audit_all = []
for (T, xr) in ROWS:
    name = ROWNAME[(T, xr)]
    g_trades, g_cnt, g_audit = run_row(GATE_DAYS, T, xr)
    n_trades, n_cnt, n_audit = run_row(NOV_DAYS, T, xr)
    audit_all += g_audit + n_audit
    results[name] = dict(T=T, exit=xr, counts=g_cnt,
                         windows=window_stats(g_trades),
                         trades=g_trades,
                         nov_counts=n_cnt, nov_stats=stats(n_trades),
                         nov_trades=n_trades)
    print(name, "gate:", results[name]["windows"], "counts:", g_cnt,
          "| nov:", results[name]["nov_stats"], n_cnt)

# ---------------- timing audit (truncated recomputation) ----------------
def _close(a, b, tol):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(a - b) < tol

bad = []
for i in sorted(set(audit_all)):
    e9 = ema_series(C[:i + 1], 9)[-1]
    e21 = ema_series(C[:i + 1], 21)[-1]
    st = supertrend(H[:i + 1], L[:i + 1], C[:i + 1])[-1]
    ml, ms = macd_from(C[:i + 1], 12, 26, 9)
    rs = rsi_wilder(C[:i + 1])[-1]
    ax = adx_wilder(H[:i + 1], L[:i + 1], C[:i + 1])[-1]
    ok = (_close(e9, EMA9[i], 1e-6) and _close(e21, EMA21[i], 1e-6) and
          st == ST_DIR[i] and
          _close(ml[-1], MACD_LINE[i], 1e-6) and
          _close(ms[-1], MACD_SIG[i], 1e-6) and
          _close(rs, RSI[i], 1e-9) and _close(ax, ADX[i], 1e-6))
    if not ok:
        bad.append(i)
if bad:
    print("TIMING AUDIT FAILED at bars:", bad[:5])
    sys.exit(1)
n_audit = len(set(audit_all))
print(f"timing audit: PASS ({n_audit} signal bars recomputed from truncated series)")

# ---------------- placebo on the best full-year row ----------------
best_name = max((ROWNAME[k] for k in ROWS),
                key=lambda nm: results[nm]["windows"]["full"]["total"])
best = results[best_name]
best_trades = best["trades"]
scorer = SCORERS[best["exit"]]
rng = random.Random(SEED)
placebo_totals, placebo_drops = [], 0
for _ in range(500):
    tot = 0.0
    for rt in best_trades:
        tr = None
        for _a in range(51):
            d = rng.choice(GATE_DAYS)
            idxs = day_idx[d]
            cand = [gi for gi in idxs if "09:20" <= TIMES[gi] <= "15:15"]
            ei = rng.choice(cand)
            tr = scorer(d, ei, C[idxs[POS[ei] - 1]], rt["side"])
            if tr:
                break
        if tr:
            tot += tr["net"]
        else:
            placebo_drops += 1
    placebo_totals.append(tot)
placebo_totals.sort()
real_total = best["windows"]["full"]["total"]
pct = round(100.0 * sum(1 for x in placebo_totals if x < real_total) /
            len(placebo_totals), 1)
print(f"placebo best row {best_name}: real {real_total} percentile {pct} "
      f"drops {placebo_drops}")

# ---------------- outputs ----------------
out = dict(
    spec="ekam_intraday_bank_SPEC.md",
    basis="paper, 1 lot (30), Rs220/trade, buying only",
    gate_days=len(GATE_DAYS), nov_days=len(NOV_DAYS),
    timing_audit=f"PASS ({n_audit} signal bars)",
    vwap_unavailable_bars=vwap_unavail_bars,
    vote_distribution={str(k): v for k, v in dist.items()},
    rows={nm: dict(T=r["T"], exit=r["exit"], counts=r["counts"],
                   windows=r["windows"], trades=r["trades"],
                   nov_counts=r["nov_counts"], nov_stats=r["nov_stats"],
                   nov_trades=r["nov_trades"])
          for nm, r in results.items()},
    best_row=best_name,
    placebo=dict(row=best_name, percentile=pct, drops=placebo_drops,
                 p50=placebo_totals[250], p95=placebo_totals[474],
                 max=placebo_totals[-1], real_total=real_total))
json.dump(out, open(TR / "ekam_intraday_bank_results.json", "w"), indent=1)

def _row_line(nm):
    w = results[nm]["windows"]
    f, a, b = w["full"], w["jan_jun"], w["jul_oct"]
    return (f"| {nm} | {a['trades']} | {a['total']:.2f} | {a['wr']} | "
            f"{b['trades']} | {b['total']:.2f} | {b['wr']} | "
            f"{f['trades']} | {f['total']:.2f} | {f['wr']} | {f['per_td']:.2f} |")

lines = []
lines.append("# EKAM-INTRADAY — BANK NIFTY · RESULTS · 2026-11-14")
lines.append("")
lines.append("Spec: ekam_intraday_bank_SPEC.md (frozen before scoring). "
             "Basis: paper, buying only, 1 lot (30), Rs220/trade.")
lines.append(f"Gate days: {len(GATE_DAYS)} (Jan-Oct 2026). "
             f"Timing audit: PASS ({n_audit} signal bars recomputed "
             "from truncated series).")
lines.append(f"VWAP-unavailable bars (gate + November): {vwap_unavail_bars}.")
lines.append("")
lines.append("## Rows — windows")
lines.append("")
lines.append("| Row | Jan-Jun trades | Jan-Jun net | Jan-Jun WR | "
             "Jul-Oct trades | Jul-Oct net | Jul-Oct WR | Full trades | "
             "Full net | Full WR | Full Rs/trade-day |")
lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
for (T, xr) in ROWS:
    lines.append(_row_line(ROWNAME[(T, xr)]))
lines.append("")
lines.append("## Counts (gate window)")
lines.append("")
lines.append("| Row | Signals | Late | NC |")
lines.append("|---|---|---|---|")
for (T, xr) in ROWS:
    nm = ROWNAME[(T, xr)]
    c = results[nm]["counts"]
    lines.append(f"| {nm} | {c['signals']} | {c['late']} | {c['nc']} |")
lines.append("")
lines.append("## Vote-count distribution (gate days by the day's max final vote count)")
lines.append("")
lines.append("| Max votes M | 0 | 1 | 2 | 3 | 4 | 5 | 6 |")
lines.append("|---|---|---|---|---|---|---|---|")
lines.append("| Days | " + " | ".join(str(dist[m]) for m in range(7)) + " |")
lines.append("")
lines.append("## Placebo (best full-year row)")
lines.append("")
lines.append(f"Best row: {best_name} (full net Rs{real_total:.2f}). "
             f"Random-entry placebo (500 iterations, same count/geometry): "
             f"percentile {pct}; median Rs{placebo_totals[250]:.2f}; "
             f"p95 Rs{placebo_totals[474]:.2f}; max Rs{placebo_totals[-1]:.2f}; "
             f"dropped draws {placebo_drops}.")
lines.append("")
lines.append("## November CF (Nov 2-13, descriptive)")
lines.append("")
lines.append("| Row | Trades | Net | WR | Signals | Late | NC |")
lines.append("|---|---|---|---|---|---|---|")
for (T, xr) in ROWS:
    nm = ROWNAME[(T, xr)]
    s, c = results[nm]["nov_stats"], results[nm]["nov_counts"]
    lines.append(f"| {nm} | {s['trades']} | {s['total']:.2f} | {s['wr']} | "
                 f"{c['signals']} | {c['late']} | {c['nc']} |")
lines.append("")
(TR / "ekam_intraday_bank_2026-11-14.md").write_text("\n".join(lines))
print("written: ekam_intraday_bank_results.json + ekam_intraday_bank_2026-11-14.md")
