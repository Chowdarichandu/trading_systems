#!/usr/bin/env python3
"""TRIO-IND — does EKAM-style vote agreement at entry raise TRIO's
accuracy? Spec: trio_ind_SPEC.md (frozen 2026-11-15 before scoring).
Research only: reads stored legs + stores, writes
trio_ind_results.json + trio_ind_2026-11-15.md. Changes nothing.
Paper only, real money Rs0. Buying only.
"""
import bisect, csv, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))

# =====================================================================
# LEGS — the repaired TRIO lead lines (stored)
# =====================================================================
def bank_legs():
    legs = []
    with open(TR / "november_books_fix_repair_bank_legs.csv") as f:
        for r in csv.DictReader(f):
            if r["stood_down"].strip():
                continue
            legs.append(dict(line="BANK", date=r["date"], side=r["side"],
                             entry_time=r["entry_time"],
                             net=float(r["net_inr"]), window="janoct"))
    # November: shadow stack legs with the frozen B-FIX-1 stand-down
    import bank_bfix1_score as bf
    with open(TR / "november_shadow_stack_bank_log.csv") as f:
        for r in csv.DictReader(f):
            if not r["net_inr"]:
                continue
            g = bf.gap_pct(r["date"])
            prem = float(r["entry_premium"])
            if (r["direction"] == "PE" and g is not None and g < 0
                    and 500.0 <= prem <= 800.0):
                continue  # stood down by B-FIX-1
            legs.append(dict(line="BANK", date=r["date"],
                             side=r["direction"], entry_time=r["entry_time"],
                             net=float(r["net_inr"]), window="nov"))
    return legs

def nifty_legs():
    legs = []
    with open(TR / "november_books_fix_repair_nifty_legs.csv") as f:
        for r in csv.DictReader(f):
            if r["stood_down"].strip():
                continue
            legs.append(dict(line="NIFTY", date=r["date"], side=r["side"],
                             entry_time=r["entry_time"],
                             net=float(r["net_inr"]), window="janoct"))
    import nifty_nfix1_score as nf
    for day in nf.NOV_DAYS:
        g = nf.gap_pct(day)
        for r in nf.v1_legs(day):
            if r["direction"] == "CE" and g is not None and g > 0:
                continue  # stood down by N-FIX-1
            legs.append(dict(line="NIFTY", date=day, side=r["direction"],
                             entry_time=r["entry_time"],
                             net=float(r["net_inr"]), window="nov"))
    return legs

def stock_trades():
    out = []
    with open(TR / "stocks_engine_adoptedC_book2025_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["date"] > "2025-10-31":
                continue  # Nov-Dec 2025 outside the adopted window
            out.append(dict(line="STOCKS", year="2025", date=r["date"],
                            sym=r["stock"], side=r["dir"],
                            entry_time=r["entry_time"],
                            net=float(r["net"]), window="janoct"))
    with open(TR / "stocks_engine_adoptedC_book2026_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["date"] > "2026-10-31":
                continue
            out.append(dict(line="STOCKS", year="2026", date=r["date"],
                            sym=r["stock"], side=r["dir"],
                            entry_time=r["entry_time"],
                            net=float(r["net"]), window="janoct"))
    with open(TR / "stocks_sarvaritu_paper_log.csv") as f:
        for r in csv.DictReader(f):
            out.append(dict(line="STOCKS", year="2026", date=r["date"],
                            sym=r["stock"], side=r["dir"],
                            entry_time=r["entry_time"],
                            net=float(r["net"]), window="nov"))
    return out

# =====================================================================
# BANK VOTES — ekam_intraday_bank_build.py replicated verbatim
# =====================================================================
def bank_votes():
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
    EXP = {}
    with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
        for r in csv.DictReader(f):
            EXP[r["date"]] = r["expiry"]
    for d in NOV_DAYS:
        EXP[d] = "2026-11-23"
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
    # indicators (house implementations, verbatim)
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
            tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]),
                        abs(l[i] - c[i - 1]))
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
    EMA9 = ema_series(C, 9); EMA21 = ema_series(C, 21)
    ST_DIR = supertrend(H, L, C, 7, 3.0)
    MACD_LINE, MACD_SIG = macd_from(C, 12, 26, 9)
    RSI = rsi_wilder(C, 14)
    ADX = adx_wilder(H, L, C, 14)
    LV = [0] * N; SV = [0] * N
    for day in GATE_DAYS + NOV_DAYS:
        vw = day_vwap(day)
        for gi in day_idx[day]:
            t = TIMES[gi]
            v = vw.get(t) if vw else None
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
    return {d: {TIMES[gi]: (LV[gi], SV[gi]) for gi in idxs}
            for d, idxs in day_idx.items()}


# =====================================================================
# NIFTY VOTES — ekam_intraday_nifty_build.py replicated verbatim
# =====================================================================
def nifty_votes():
    import re
    spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv",
                       parse_dates=["timestamp"])
    spot = spot.sort_values("timestamp").reset_index(drop=True)
    spot["date"] = spot["timestamp"].dt.date
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    c = spot["close"].values.astype(float)
    h = spot["high"].values.astype(float)
    l = spot["low"].values.astype(float)
    n = len(spot)
    trv = np.zeros(n)
    trv[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]),
                                                   np.abs(l[1:] - c[:-1])))
    atr = np.full(n, np.nan)
    if n > 7:
        atr[7] = trv[1:8].mean()
        for i in range(8, n):
            atr[i] = (atr[i-1] * 6 + trv[i]) / 7.0
    hl2 = (h + l) / 2.0
    ub = hl2 + 3 * atr; lb = hl2 - 3 * atr
    fub = np.full(n, np.nan); flb = np.full(n, np.nan)
    stdir = np.zeros(n, dtype=int)
    for i in range(n):
        if np.isnan(atr[i]):
            continue
        if i == 0 or np.isnan(fub[i-1]):
            fub[i], flb[i] = ub[i], lb[i]
        else:
            fub[i] = ub[i] if (ub[i] < fub[i-1] or c[i-1] > fub[i-1]) else fub[i-1]
            flb[i] = lb[i] if (lb[i] > flb[i-1] or c[i-1] < flb[i-1]) else flb[i-1]
        if i == 0 or stdir[i-1] == 0:
            stdir[i] = -1 if c[i] <= flb[i] else (1 if c[i] >= fub[i] else -1)
        elif stdir[i-1] == 1:
            stdir[i] = -1 if c[i] < flb[i] else 1
        else:
            stdir[i] = 1 if c[i] > fub[i] else -1
    delta = np.diff(c, prepend=c[0])
    gain = np.where(delta > 0, delta, 0.0); loss = np.where(delta < 0, -delta, 0.0)
    def wilder(x, p):
        out = np.full(n, np.nan)
        if n > p:
            out[p] = x[1:p+1].mean()
            for i in range(p+1, n):
                out[i] = (out[i-1] * (p-1) + x[i]) / p
        return out
    ag, al = wilder(gain, 14), wilder(loss, 14)
    rsi = np.where(al == 0, 100.0, 100 - 100 / (1 + np.where(
        al == 0, np.inf, ag / np.where(al == 0, np.nan, al))))
    def ema_series(x, p):
        out = np.full(len(x), np.nan); k = 2 / (p + 1)
        e = x[0]
        for i in range(len(x)):
            e = x[i] * k + e * (1 - k) if i > 0 else x[0]
            out[i] = e
        return out
    ema9 = ema_series(c, 9); ema21 = ema_series(c, 21)
    ema12 = ema_series(c, 12); ema26 = ema_series(c, 26)
    macd = ema12 - ema26
    macd_sig = ema_series(macd, 9)
    dh = np.zeros(n); dl_ = np.zeros(n)
    dh[1:] = h[1:] - h[:-1]; dl_[1:] = l[:-1] - l[1:]
    pdm = np.where((dh > dl_) & (dh > 0), dh, 0.0)
    mdm = np.where((dl_ > dh) & (dl_ > 0), dl_, 0.0)
    def wilder_sum(x, p):
        out = np.full(n, np.nan)
        if n > p:
            out[p] = x[1:p+1].sum()
            for i in range(p+1, n):
                out[i] = out[i-1] - out[i-1] / p + x[i]
        return out
    sTR, sP, sM = wilder_sum(trv, 14), wilder_sum(pdm, 14), wilder_sum(mdm, 14)
    dip = np.where(sTR > 0, 100 * sP / np.where(sTR == 0, np.nan, sTR), 0.0)
    dim = np.where(sTR > 0, 100 * sM / np.where(sTR == 0, np.nan, sTR), 0.0)
    dx = np.where((dip + dim) > 0, 100 * np.abs(dip - dim) /
                  np.where((dip + dim) == 0, np.nan, dip + dim), 0.0)
    adx = np.full(n, np.nan)
    if n > 27:
        adx[27] = np.nanmean(dx[14:28])
        for i in range(28, n):
            adx[i] = (adx[i-1] * 13 + dx[i]) / 14.0
    fut_by_exp = {}
    for fn in (TR / "phase3_buildup_data/futures").glob("FUT7_NIFTY_*.json"):
        m = re.match(r"FUT7_NIFTY_(\d{4}-\d{2}-\d{2})_", fn.name)
        if not m:
            continue
        exp = m.group(1)
        d = json.load(open(fn))["data"]["candles"]
        dd = fut_by_exp.setdefault(exp, {})
        for ts, o_, h_, l_, c_, v_, oi_ in d:
            dd.setdefault(ts[:10], {})[ts[11:16]] = ((h_ + l_ + c_) / 3.0, v_, c_)
    fut_exps = sorted(fut_by_exp)
    _vw_cache = {}
    def vwap_series(day):
        key = day.isoformat()
        if key in _vw_cache:
            return _vw_cache[key]
        exp = next((e for e in fut_exps if e >= key), None)
        out = {}
        if exp is not None:
            bars = fut_by_exp[exp].get(key, {})
            pv, vv, last = 0.0, 0.0, None
            for t in sorted(bars):
                tp, v_, fc = bars[t]
                pv += tp * v_; vv += v_
                last = pv / vv if vv > 0 else last
                out[t] = (last, fc)
        _vw_cache[key] = out
        return out
    lv5 = np.zeros(n, dtype=int); sv5 = np.zeros(n, dtype=int)
    lv5 += np.where(ema9 > ema21, 1, 0); sv5 += np.where(ema9 < ema21, 1, 0)
    lv5 += np.where(stdir == 1, 1, 0);  sv5 += np.where(stdir == -1, 1, 0)
    lv5 += np.where(macd > macd_sig, 1, 0); sv5 += np.where(macd < macd_sig, 1, 0)
    lv5 += np.where((rsi >= 50) & (rsi < 70), 1, 0)
    sv5 += np.where((rsi > 30) & (rsi < 50), 1, 0)
    dates_arr = spot["date"].values; times_arr = spot["time"].values
    for day in pd.unique(dates_arr):
        vw = vwap_series(day)
        if not vw:
            continue
        idxs = np.where(dates_arr == day)[0]
        for i in idxs:
            v = vw.get(times_arr[i])
            if v is None or v[0] is None:
                continue
            if v[1] > v[0]:
                lv5[i] += 1
            elif v[1] < v[0]:
                sv5[i] += 1
    lv = lv5.copy(); sv = sv5.copy()
    lead_l = (~np.isnan(adx)) & (adx >= 20) & (lv5 > sv5)
    lead_s = (~np.isnan(adx)) & (adx >= 20) & (sv5 > lv5)
    lv += np.where(lead_l, 1, 0); sv += np.where(lead_s, 1, 0)
    votes_by_day = {}
    day_rows = {}
    for i, d in enumerate(dates_arr):
        day_rows.setdefault(d, []).append(i)
    for d, idxs in day_rows.items():
        votes_by_day[d.isoformat()] = {
            times_arr[i]: (int(lv[i]), int(sv[i])) for i in idxs}
    return votes_by_day

# =====================================================================
# STOCKS VOTES — ekam_intraday_stocks_build.build_stock (its own code)
# =====================================================================
def stock_day_votes(sym, cache={}):
    if sym not in cache:
        import ekam_intraday_stocks_build as eb
        cache[sym] = eb.build_stock(sym)
    return cache[sym]

def stock_vote_at(sym, date, entry_time):
    """(L, S) at the bar just before entry, or None (NC)."""
    S = stock_day_votes(sym)
    D = S["days"].get(date)
    if D is None:
        return None
    stamps = list(D["st"])
    if entry_time not in stamps:
        return None
    li = stamps.index(entry_time)
    if li == 0:
        return None
    lv, sv = D["LV"][li - 1], D["SV"][li - 1]
    if lv is None or sv is None:
        return None
    return (lv, sv)

# =====================================================================
# VOTE LOOKUP (indices): bar just before entry
# =====================================================================
def index_vote_at(votes_by_day, date, entry_time):
    day = votes_by_day.get(date)
    if not day:
        return None
    times = sorted(day)
    prior = [t for t in times if t < entry_time]
    if not prior:
        return None
    return day[prior[-1]]

# =====================================================================
# VALIDATION — recomputed votes vs the EKAM builds' stored trades
# =====================================================================
def validate_bank(vbd):
    d = json.load(open(TR / "ekam_intraday_bank_results.json"))
    ok = bad = 0
    for row in d["rows"].values():
        for t in row["trades"]:
            v = vbd.get(t["date"], {}).get(t["signal_time"])
            if v is None:
                bad += 1
                continue
            own = v[0] if t["side"] == "up" else v[1]
            if own == t["signal_votes"]:
                ok += 1
            else:
                bad += 1
    nov = d.get("november", {})
    for row in (nov.get("rows", {}) or {}).values():
        for t in row.get("trades", []):
            v = vbd.get(t["date"], {}).get(t["signal_time"])
            if v is None:
                bad += 1
                continue
            own = v[0] if t["side"] == "up" else v[1]
            if own == t["signal_votes"]:
                ok += 1
            else:
                bad += 1
    return ok, bad

def validate_nifty(vbd):
    ok = bad = 0
    seen = set()
    with open(TR / "ekam_intraday_nifty_trades.csv") as f:
        for r in csv.DictReader(f):
            key = (r["date"], r["signal_time"])
            if key in seen:
                continue
            seen.add(key)
            v = vbd.get(r["date"], {}).get(r["signal_time"])
            if v is None:
                bad += 1
                continue
            if v == (int(r["lv"]), int(r["sv"])):
                ok += 1
            else:
                bad += 1
    return ok, bad

def validate_stocks():
    ok = bad = 0
    seen = set()
    with open(TR / "ekam_intraday_stocks_trades.csv") as f:
        for r in csv.DictReader(f):
            key = (r["sym"], r["date"], r["signal_stamp"], r["entry_stamp"])
            if key in seen:
                continue
            seen.add(key)
            S = stock_day_votes(r["sym"])
            D = S["days"].get(r["date"])
            if D is None or r["signal_stamp"] not in list(D["st"]):
                bad += 1
                continue
            li = list(D["st"]).index(r["signal_stamp"])
            lv, sv = D["LV"][li], D["SV"][li]
            if lv is None:
                bad += 1
                continue
            own = lv if int(r["side"]) == 1 else sv
            if own == int(r["votes"]):
                ok += 1
            else:
                bad += 1
    return ok, bad

# =====================================================================
# ROW SCORING
# =====================================================================
def row_stats(legs):
    if not legs:
        return dict(legs=0, net=0.0, wr=None, per_trade=None,
                    trade_days=0, per_td=None)
    net = round(sum(x["net"] for x in legs), 2)
    wins = sum(1 for x in legs if x["net"] > 0)
    days = len({x["date"] for x in legs})
    return dict(legs=len(legs), net=net,
                wr=round(100.0 * wins / len(legs), 1),
                per_trade=round(net / len(legs), 2),
                trade_days=days, per_td=round(net / days, 2))

def half_stats(legs):
    h1 = [x for x in legs if x["date"][5:7] in ("01", "02", "03", "04", "05", "06")]
    h2 = [x for x in legs if x["date"][5:7] in ("07", "08", "09", "10")]
    def s(ls):
        if not ls:
            return dict(legs=0, net=0.0, wr=None)
        return dict(legs=len(ls), net=round(sum(x["net"] for x in ls), 2),
                    wr=round(100.0 * sum(1 for x in ls if x["net"] > 0) / len(ls), 1))
    return dict(jan_jun=s(h1), jul_oct=s(h2))

def score_rows(legs):
    """legs carry own/opp vote counts or None."""
    scored = [x for x in legs if x.get("own") is not None]
    nc = len(legs) - len(scored)
    rows = {}
    rows["ALL"] = row_stats(legs)
    rows["AGREE>=4"] = row_stats([x for x in scored if x["own"] >= 4])
    rows["AGREE>=5"] = row_stats([x for x in scored if x["own"] >= 5])
    rows["DISAGREE>=4"] = row_stats([x for x in scored if x["opp"] >= 4])
    halves = {}
    for nm, sel in (("ALL", legs),
                    ("AGREE>=4", [x for x in scored if x["own"] >= 4]),
                    ("AGREE>=5", [x for x in scored if x["own"] >= 5]),
                    ("DISAGREE>=4", [x for x in scored if x["opp"] >= 4])):
        halves[nm] = half_stats(sel)
    return rows, halves, nc

def verdict_for(rows_by_window):
    """rows_by_window: list of (ALL, AGREE row) stat pairs that must
    ALL pass (stocks: both years). Returns (helps, best_row_name)."""
    best = None
    for cand in ("AGREE>=4", "AGREE>=5"):
        ok_all = True
        for rows in rows_by_window:
            a, r = rows["ALL"], rows[cand]
            if (r["legs"] == 0 or r["wr"] is None or a["wr"] is None
                    or not (r["wr"] > a["wr"] and r["net"] >= 0.8 * a["net"])):
                ok_all = False
                break
        if ok_all:
            best = cand
            break
    return best

def main():
    results = {"spec": "trio_ind_SPEC.md",
               "basis": "paper only, real money Rs0; indices per 1 lot, "
                        "stocks per 100 shares PROVISIONAL"}
    # ---------------- BANK ----------------
    bv = bank_votes()
    ok, bad = validate_bank(bv)
    results["validation"] = {"bank": {"match": ok, "mismatch": bad}}
    blegs = bank_legs()
    for x in blegs:
        v = index_vote_at(bv, x["date"], x["entry_time"])
        if v is None:
            x["own"] = x["opp"] = None
        elif x["side"] == "CE":
            x["own"], x["opp"] = v
        else:
            x["opp"], x["own"] = v
    b_jo = [x for x in blegs if x["window"] == "janoct"]
    b_nov = [x for x in blegs if x["window"] == "nov"]
    assert round(sum(x["net"] for x in b_jo), 2) == 131510.00, \
        sum(x["net"] for x in b_jo)
    assert round(sum(x["net"] for x in b_nov), 2) == -3440.00, \
        sum(x["net"] for x in b_nov)
    brows, bhalves, bnc = score_rows(b_jo)
    brows_nov, _, bnc_nov = score_rows(b_nov)
    results["bank"] = {"control_check": "Jan-Oct +131,510.00 EXACT; "
                                        "Nov -3,440.00 EXACT",
                       "janoct": brows, "janoct_halves": bhalves,
                       "nov": brows_nov, "nc_janoct": bnc, "nc_nov": bnc_nov}
    # ---------------- NIFTY ----------------
    nv = nifty_votes()
    ok, bad = validate_nifty(nv)
    results["validation"]["nifty"] = {"match": ok, "mismatch": bad}
    nlegs = nifty_legs()
    for x in nlegs:
        v = index_vote_at(nv, x["date"], x["entry_time"])
        if v is None:
            x["own"] = x["opp"] = None
        elif x["side"] == "CE":
            x["own"], x["opp"] = v
        else:
            x["opp"], x["own"] = v
    n_jo = [x for x in nlegs if x["window"] == "janoct"]
    n_nov = [x for x in nlegs if x["window"] == "nov"]
    assert round(sum(x["net"] for x in n_jo), 2) == 117170.00, \
        sum(x["net"] for x in n_jo)
    assert round(sum(x["net"] for x in n_nov), 2) == 0.00
    nrows, nhalves, nnc = score_rows(n_jo)
    nrows_nov, _, nnc_nov = score_rows(n_nov)
    results["nifty"] = {"control_check": "Jan-Oct +117,170.00 EXACT; "
                                         "Nov 0 legs / Rs0 EXACT",
                        "janoct": nrows, "janoct_halves": nhalves,
                        "nov": nrows_nov, "nc_janoct": nnc, "nc_nov": nnc_nov}
    # ---------------- STOCKS ----------------
    ok, bad = validate_stocks()
    results["validation"]["stocks"] = {"match": ok, "mismatch": bad}
    strades = stock_trades()
    for x in strades:
        v = stock_vote_at(x["sym"], x["date"], x["entry_time"])
        if v is None:
            x["own"] = x["opp"] = None
        elif x["side"] == "LONG":
            x["own"], x["opp"] = v
        else:
            x["opp"], x["own"] = v
    sres = {}
    for yr, ctrl_net, ctrl_n in (("2025", 119813.44, 1064),
                                 ("2026", 247178.79, 1363)):
        ys = [x for x in strades if x["year"] == yr and x["window"] == "janoct"]
        assert round(sum(x["net"] for x in ys), 2) == ctrl_net, \
            (yr, sum(x["net"] for x in ys))
        assert len(ys) == ctrl_n, (yr, len(ys))
        r, hh, nc = score_rows(ys)
        sres[yr] = {"janoct": r, "janoct_halves": hh, "nc_janoct": nc}
    snov = [x for x in strades if x["window"] == "nov"]
    assert round(sum(x["net"] for x in snov), 2) == 7517.94
    assert len(snov) == 32
    r_nov, _, nc_nov = score_rows(snov)
    sres["nov"] = {"rows": r_nov, "nc": nc_nov}
    sres["control_check"] = ("2025 +119,813.44 / 1,064 EXACT; 2026 "
                             "+247,178.79 / 1,363 EXACT; Nov +7,517.94 "
                             "/ 32 EXACT")
    results["stocks"] = sres
    # ---------------- verdicts ----------------
    def best_agree(rows):
        cands = [(nm, rows[nm]) for nm in ("AGREE>=4", "AGREE>=5")
                 if rows[nm]["legs"] > 0]
        if not cands:
            return None, None
        return max(cands, key=lambda kv: (kv[1]["wr"], kv[1]["net"]))
    verdicts = {}
    for line, rows in (("bank", brows), ("nifty", nrows)):
        bn, br = best_agree(rows)
        passed = verdict_for([rows])
        verdicts[line] = {"best_agreement_row": bn,
                          "helps": passed is not None,
                          "passing_row": passed}
    s_passed = verdict_for([sres["2025"]["janoct"], sres["2026"]["janoct"]])
    bn25, br25 = best_agree(sres["2025"]["janoct"])
    bn26, br26 = best_agree(sres["2026"]["janoct"])
    verdicts["stocks"] = {"best_agreement_row_2025": bn25,
                          "best_agreement_row_2026": bn26,
                          "helps": s_passed is not None,
                          "passing_row": s_passed}
    results["verdicts"] = verdicts
    (TR / "trio_ind_results.json").write_text(json.dumps(results, indent=1))
    # ---------------- markdown ----------------
    def fmt_row(nm, s):
        wr = f"{s['wr']:.1f}%" if s["wr"] is not None else "—"
        pt = f"{s['per_trade']:+,.2f}" if s["per_trade"] is not None else "—"
        ptd = f"{s['per_td']:+,.2f}" if s["per_td"] is not None else "—"
        return (f"| {nm} | {s['legs']} | {s['net']:+,.2f} | {wr} | {pt} | "
                f"{s['trade_days']} | {ptd} |")
    def fmt_half(nm, hh):
        def g(k):
            s = hh[nm][k]
            wr = f"{s['wr']:.1f}%" if s["wr"] is not None else "—"
            return f"{s['net']:+,.2f} ({s['legs']}, {wr})"
        return f"| {nm} | {g('jan_jun')} | {g('jul_oct')} |"
    L = []
    L.append("# TRIO-IND — does EKAM-style vote agreement at entry raise "
             "TRIO's accuracy? (2026-11-15)")
    L.append("")
    L.append("Spec: trio_ind_SPEC.md (frozen before scoring). Research "
             "only; nothing armed. Paper only, real money Rs0. Indices: "
             "option premiums per 1 lot. Stocks: equity cash, per 100 "
             "shares PROVISIONAL, Rs40/trade inside stored nets.")
    L.append("")
    L.append("## Prior measured context (why this test exists)")
    L.append("")
    L.append("- Indicator conditioning on these books has mostly FAILED: "
             "Phase-3 buildup / volume / speculation surfaces all "
             "gate-failed on the Bank stack and on Nifty TUNED v1, in "
             "both directions.")
    L.append("- The one success was the Bank CONFIDENCE score (a "
             "composite, not indicator agreement): stack WR 59.5% -> "
             "62.5% keeping 96.1% of profit; on forward shadow, "
             "adoption at the Nov 30 verdicts. It FAILED on Nifty "
             "and on Stocks.")
    L.append("- In SOLID-60, agreement was BACKWARDS: more systems "
             "agreeing = LOWER win rate. Hence the DISAGREE>=4 row "
             "below, reported on its own.")
    L.append("- This build tests the remaining version: EKAM's frozen "
             "6-vote agreement read at the bar just before each TRIO "
             "leg's entry.")
    L.append("")
    val = results["validation"]
    L.append("## Vote validation (recomputed vs EKAM builds' stored trades)")
    L.append("")
    for k in ("bank", "nifty", "stocks"):
        L.append(f"- {k}: {val[k]['match']} match / "
                 f"{val[k]['mismatch']} mismatch")
    L.append("")
    for title, blk, ctrl in (
            ("BANK — TUNED STACK v2 + B-FIX-1 (repaired lead)", results["bank"], None),
            ("NIFTY — TUNED v1 + N-FIX-1 (repaired lead)", results["nifty"], None)):
        L.append(f"## {title}")
        L.append("")
        L.append(f"Control check: {blk['control_check']}. "
                 f"NC legs (no pre-entry vote): Jan-Oct {blk['nc_janoct']}, "
                 f"Nov {blk['nc_nov']} — counted, never estimated.")
        L.append("")
        L.append("Jan-Oct 2026:")
        L.append("")
        L.append("| Row | Legs | Net (Rs) | WR | Rs/trade | Trade-days | Rs/trade-day |")
        L.append("|---|---|---|---|---|---|---|")
        for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
            L.append(fmt_row(nm, blk["janoct"][nm]))
        L.append("")
        L.append("Halves (net (legs, WR)):")
        L.append("")
        L.append("| Row | Jan-Jun | Jul-Oct |")
        L.append("|---|---|---|")
        for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
            L.append(fmt_half(nm, blk["janoct_halves"]))
        L.append("")
        L.append("November (descriptive):")
        L.append("")
        L.append("| Row | Legs | Net (Rs) | WR | Rs/trade | Trade-days | Rs/trade-day |")
        L.append("|---|---|---|---|---|---|---|")
        for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
            L.append(fmt_row(nm, blk["nov"][nm]))
        L.append("")
    sb = results["stocks"]
    L.append("## STOCKS — raw Stock Book (TRIO's stocks line)")
    L.append("")
    L.append(f"Control check: {sb['control_check']}. Vote state "
             "recomputed with the EKAM-intraday stocks build's own "
             "frozen code (build_stock / votes_at) on the same stores — "
             "that build persists votes only for its own trades; Stock "
             "Book trades whose pre-entry vote is undefined are NC, "
             "counted, never estimated.")
    L.append("")
    for yr in ("2025", "2026"):
        blk = sb[yr]
        L.append(f"### {yr} (Jan-Oct) — NC legs: {blk['nc_janoct']}")
        L.append("")
        L.append("| Row | Trades | Net (Rs) | WR | Rs/trade | Trade-days | Rs/trade-day |")
        L.append("|---|---|---|---|---|---|---|")
        for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
            L.append(fmt_row(nm, blk["janoct"][nm]))
        L.append("")
        L.append("| Row | Jan-Jun | Jul-Oct |")
        L.append("|---|---|---|")
        for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
            L.append(fmt_half(nm, blk["janoct_halves"]))
        L.append("")
    L.append(f"### November 2026 (descriptive) — NC trades: {sb['nov']['nc']}")
    L.append("")
    L.append("| Row | Trades | Net (Rs) | WR | Rs/trade | Trade-days | Rs/trade-day |")
    L.append("|---|---|---|---|---|---|---|")
    for nm in ("ALL", "AGREE>=4", "AGREE>=5", "DISAGREE>=4"):
        L.append(fmt_row(nm, sb["nov"]["rows"][nm]))
    L.append("")
    L.append("## Verdicts (frozen rule: WR above control AND >=80% of "
             "control profit kept; stocks must pass in both years)")
    L.append("")
    vd = results["verdicts"]
    def vline(name, rows, vkey):
        a = rows["ALL"]
        bn, br = best_agree(rows)
        if bn is None:
            return (f"- **{name}:** control WR {a['wr']:.1f}% / net "
                    f"{a['net']:+,.2f}; no agreement row has any legs — "
                    f"**NONE**.")
        return (f"- **{name}:** control WR {a['wr']:.1f}% / net "
                f"{a['net']:+,.2f}; best agreement row {bn} WR "
                f"{br['wr']:.1f}% / net {br['net']:+,.2f} "
                f"({br['legs']} legs) — "
                f"**{'HELPS (' + str(vkey) + ')' if vkey else 'NONE'}.**")
    L.append(vline("Bank", brows, vd["bank"]["passing_row"]))
    L.append(vline("Nifty", nrows, vd["nifty"]["passing_row"]))
    a25, a26 = sres["2025"]["janoct"]["ALL"], sres["2026"]["janoct"]["ALL"]
    L.append(f"- **Stocks:** control WR {a25['wr']:.1f}% / net "
             f"{a25['net']:+,.2f} (2025), WR {a26['wr']:.1f}% / net "
             f"{a26['net']:+,.2f} (2026); best agreement rows "
             f"{bn25} (2025: WR {br25['wr']:.1f}% / {br25['net']:+,.2f}), "
             f"{bn26} (2026: WR {br26['wr']:.1f}% / {br26['net']:+,.2f}) — "
             f"**{'HELPS (' + str(vd['stocks']['passing_row']) + ')' if vd['stocks']['passing_row'] else 'NONE'}.**")
    L.append("")
    (TR / "trio_ind_2026-11-15.md").write_text("\n".join(L) + "\n")
    # ---------------- final message ----------------
    def brief(name, rows, vkey):
        a = rows["ALL"]
        bn, br = best_agree(rows)
        if bn is None:
            print(f"{name}: control WR {a['wr']:.1f}% / net "
                  f"{a['net']:+,.2f} ({a['legs']} legs); no agreement "
                  f"legs; verdict NONE.")
        else:
            print(f"{name}: control WR {a['wr']:.1f}% / net "
                  f"{a['net']:+,.2f} ({a['legs']} legs); best agreement "
                  f"row {bn} WR {br['wr']:.1f}% / net {br['net']:+,.2f} "
                  f"({br['legs']} legs); verdict "
                  f"{'HELPS via ' + str(vkey) if vkey else 'NONE'}.")
    brief("BANK", brows, vd["bank"]["passing_row"])
    brief("NIFTY", nrows, vd["nifty"]["passing_row"])
    print(f"STOCKS: control WR {a25['wr']:.1f}% / {a25['net']:+,.2f} "
          f"(2025), WR {a26['wr']:.1f}% / {a26['net']:+,.2f} (2026); "
          f"best agreement {bn25} WR {br25['wr']:.1f}% / "
          f"{br25['net']:+,.2f} (2025), {bn26} WR {br26['wr']:.1f}% / "
          f"{br26['net']:+,.2f} (2026); verdict "
          f"{'HELPS via ' + str(vd['stocks']['passing_row']) if vd['stocks']['passing_row'] else 'NONE'}.")

if __name__ == "__main__":
    main()
