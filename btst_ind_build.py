#!/usr/bin/env python3
"""BTST-IND — BTST decided by intraday indicators.
Spec: btst_ind_SPEC.md (frozen 2026-11-15 before scoring). Research only.
Reads persisted stores only; writes btst_ind_results.json +
btst_ind_2026-11-15.md + btst_ind_trades.csv. Changes no book/ledger/job.
"""
import bisect, csv, json, math, random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

TR = Path.home() / "workspace" / "trading"
sys.path.insert(0, str(TR))
import ekam_intraday_stocks_build as EKS

SEED = 20261115
VOTE_STAMP, FILL_STAMP = "15:00", "15:15"
IDX_COST = 220.0

def stats(trades, datekey="date"):
    if not trades:
        return dict(trades=0, net=0.0, wr=None, worst=None,
                    h1=dict(trades=0, net=0.0), h2=dict(trades=0, net=0.0))
    net = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    def half(lo, hi):
        sel = [t for t in trades if lo <= t[datekey][5:7] <= hi]
        return dict(trades=len(sel), net=round(sum(t["net"] for t in sel), 2))
    return dict(trades=len(trades), net=round(net, 2),
                wr=round(100.0 * wins / len(trades), 1),
                worst=round(min(t["net"] for t in trades), 2),
                h1=half("01", "06"), h2=half("07", "10"))

# ======================================================================
# STOCKS ARM (EKAM-Stocks vote machinery, imported frozen build)
# ======================================================================
STOCK_ROWS = [("L5", 1, 5), ("L4", 1, 4), ("S5", -1, 5)]

def run_stocks():
    stocks = {sym: EKS.build_stock(sym) for sym in EKS.NAMES}
    counts = defaultdict(int)
    trades_by_row = defaultdict(list)   # "L5-X0920" -> trades
    pool = defaultdict(list)            # (year, exit_kind) -> [(sym, date, entry, exit_px)]
    for year in (2025, 2026):
        lo, hi = f"{year}-01-01", f"{year}-10-31"
        for rowname, side, T in STOCK_ROWS:
            by_day = defaultdict(list)
            for sym, S in stocks.items():
                days_sorted = sorted(S["days"].keys())
                pos = {d: i for i, d in enumerate(days_sorted)}
                for date in days_sorted:
                    if not (lo <= date <= hi):
                        continue
                    D = S["days"][date]
                    if rowname == "L5":
                        if D["b"] - D["a"] < 30:
                            counts["day_lt30bars"] += 1
                            continue
                        if VOTE_STAMP not in D["st"] or FILL_STAMP not in D["st"]:
                            counts["day_missing_stamps"] += 1
                            continue
                    if D["b"] - D["a"] < 30 or VOTE_STAMP not in D["st"] \
                            or FILL_STAMP not in D["st"]:
                        continue
                    vi = D["st"].index(VOTE_STAMP)
                    lv, sv = D["LV"][vi], D["SV"][vi]
                    if lv is None:
                        if rowname == "L5":
                            counts["votes_undefined_1500"] += 1
                        continue
                    own = lv if side == 1 else sv
                    if own < T:
                        continue
                    arr = D["LV"] if side == 1 else D["SV"]
                    fh = next(D["st"][j] for j, v in enumerate(arr)
                              if v is not None and v >= T)
                    nd = days_sorted[pos[date] + 1] \
                        if pos[date] + 1 < len(days_sorted) else None
                    by_day[date].append(dict(
                        sym=sym, date=date, side=side, votes=int(own),
                        first_hit=fh,
                        entry=float(D["c"][D["st"].index(FILL_STAMP)]),
                        next_day=nd))
            for date, cands in sorted(by_day.items()):
                cands.sort(key=lambda x: (x["first_hit"], x["sym"]))
                counts[f"{rowname}_{year}_candidates"] += len(cands)
                counts[f"{rowname}_{year}_capped_out"] += max(0, len(cands) - 5)
                for cd in cands[:5]:
                    S = stocks[cd["sym"]]
                    nd = cd["next_day"]
                    for xname in ("X0920", "XCLOSE"):
                        rn = f"{rowname}-{xname}"
                        if nd is None or nd not in S["days"]:
                            counts[f"{rn}_nc_no_next_day"] += 1
                            continue
                        ND = S["days"][nd]
                        if xname == "X0920":
                            if "09:15" not in ND["st"]:
                                counts[f"{rn}_nc_no_0915"] += 1
                                continue
                            xp = float(ND["c"][ND["st"].index("09:15")])
                        else:
                            if ND["b"] - ND["a"] < 1:
                                counts[f"{rn}_nc_empty_next"] += 1
                                continue
                            xp = float(ND["c"][-1])
                        net = ((xp - cd["entry"]) if side == 1
                               else (cd["entry"] - xp)) * 100.0 - 40.0
                        assert FILL_STAMP > VOTE_STAMP
                        trades_by_row[rn].append(dict(
                            arm="stocks", row=rn, sym=cd["sym"], date=date,
                            side=("LONG" if side == 1 else "SHORT"),
                            votes=cd["votes"], entry=cd["entry"], exit=xp,
                            next_day=nd, net=round(net, 2), year=year))
        # placebo pool for this year (scoreable stock-days, votes not needed)
        for sym, S in stocks.items():
            days_sorted = sorted(S["days"].keys())
            pos = {d: i for i, d in enumerate(days_sorted)}
            for date in days_sorted:
                if not (lo <= date <= hi):
                    continue
                D = S["days"][date]
                if D["b"] - D["a"] < 30 or FILL_STAMP not in D["st"]:
                    continue
                if pos[date] + 1 >= len(days_sorted):
                    continue
                ND = S["days"][days_sorted[pos[date] + 1]]
                entry = float(D["c"][D["st"].index(FILL_STAMP)])
                if "09:15" in ND["st"]:
                    pool[(year, "X0920")].append(
                        (entry, float(ND["c"][ND["st"].index("09:15")])))
                if ND["b"] - ND["a"] >= 1:
                    pool[(year, "XCLOSE")].append((entry, float(ND["c"][-1])))
    return stocks, trades_by_row, counts, pool

def stocks_placebo(trades_by_row, pool):
    totals = {}
    for rn, trs in trades_by_row.items():
        totals[rn] = sum(t["net"] for t in trs if t["year"] == 2025) + \
                     sum(t["net"] for t in trs if t["year"] == 2026)
    best = max(totals, key=totals.get)
    rowname, xname = best.split("-")
    side = 1 if rowname in ("L5", "L4") else -1
    rng = random.Random(SEED)
    out = dict(row=best, combined_net=round(totals[best], 2), years={})
    for year in (2025, 2026):
        real = [t for t in trades_by_row[best] if t["year"] == year]
        real_net = sum(t["net"] for t in real)
        pl = pool[(year, xname)]
        draws = []
        for _ in range(200):
            tot = 0.0
            for _ in range(len(real)):
                e, x = pl[rng.randrange(len(pl))]
                tot += ((x - e) if side == 1 else (e - x)) * 100.0 - 40.0
            draws.append(tot)
        pct = 100.0 * sum(1 for d in draws if d < real_net) / len(draws) \
            if draws else None
        out["years"][str(year)] = dict(real_trades=len(real),
                                       real_net=round(real_net, 2),
                                       placebo_pct=round(pct, 1) if pct is not None else None)
    return out

def audit_stocks(stocks, trades_by_row):
    seen, keys = [], set()
    for rn in sorted(trades_by_row):
        for t in trades_by_row[rn]:
            k = (t["sym"], t["date"])
            if k not in keys:
                keys.add(k)
                seen.append(k)
    checked, ok = 0, True
    for idx, (sym, date) in enumerate(sorted(seen)):
        if idx % 37 != 0:
            continue
        S = stocks[sym]
        D = S["days"][date]
        vi = D["st"].index(VOTE_STAMP)
        g = D["a"] + vi
        ind = EKS.compute_indicators(S["o"][:g + 1], S["h"][:g + 1],
                                     S["l"][:g + 1], S["c"][:g + 1])
        tp = (D["h"][:vi + 1] + D["l"][:vi + 1] + D["c"][:vi + 1]) / 3.0
        vwap = float(np.cumsum(tp)[-1] / (vi + 1))
        lv, sv = EKS.votes_at(float(D["c"][vi]), vwap, ind, g)
        checked += 1
        if (lv, sv) != (D["LV"][vi], D["SV"][vi]):
            ok = False
    return ok, checked

# ======================================================================
# INDEX MACHINERY — BANK (copied from ekam_intraday_bank_build.py, frozen)
# ======================================================================
def bank_ctx():
    spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    spot = spot[(spot["timestamp"] >= "2026-01-01") &
                (spot["timestamp"] <= "2026-11-13")].sort_values("timestamp")
    spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    O = spot["open"].to_numpy(float); H = spot["high"].to_numpy(float)
    L = spot["low"].to_numpy(float);  C = spot["close"].to_numpy(float)
    DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
    day_idx = {}
    for i, d in enumerate(DATES):
        day_idx.setdefault(d, []).append(i)
    EXP = {}
    with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
        for r in csv.DictReader(f):
            EXP[r["date"]] = r["expiry"]
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
    def compute_ind(O_, H_, L_, C_):
        ml, ms = macd_from(list(C_))
        return dict(e9=ema_series(list(C_), 9), e21=ema_series(list(C_), 21),
                    st=supertrend(list(H_), list(L_), list(C_), 7, 3.0),
                    ml=ml, ms=ms, rsi=rsi_wilder(list(C_)),
                    adx=adx_wilder(list(H_), list(L_), list(C_)))
    IND = compute_ind(O, H, L, C)
    VWAP_BY_DAY = {d: day_vwap(d) for d in day_idx if d in EXP}
    def votes_at_bar(gi, ind, vwap_val):
        ld = sd = 0
        if vwap_val is not None:
            if C[gi] > vwap_val: ld += 1
            elif C[gi] < vwap_val: sd += 1
        e9, e21 = ind["e9"][gi], ind["e21"][gi]
        if e9 is not None and e21 is not None:
            if e9 > e21: ld += 1
            elif e9 < e21: sd += 1
        if ind["st"][gi] == "up": ld += 1
        elif ind["st"][gi] == "down": sd += 1
        ml, ms = ind["ml"][gi], ind["ms"][gi]
        if ml is not None and ms is not None:
            if ml > ms: ld += 1
            elif ml < ms: sd += 1
        r = ind["rsi"][gi]
        if r is not None:
            if 50 <= r < 70: ld += 1
            if 30 < r <= 50: sd += 1
        a = ind["adx"][gi]
        L_, S_ = ld, sd
        if a is not None and a >= 20:
            if ld > sd: L_ = ld + 1
            elif sd > ld: S_ = sd + 1
        return L_, S_
    LV = [0] * len(C); SV = [0] * len(C)
    for d, idxs in day_idx.items():
        vw = VWAP_BY_DAY.get(d)
        for gi in idxs:
            v = vw.get(TIMES[gi]) if vw else None
            LV[gi], SV[gi] = votes_at_bar(gi, IND, v)
    all_exps = sorted(set(EXP.values()))
    def expiry_fn(day):
        e = EXP.get(day)
        if e is not None and e > day:
            return e
        nxt = [x for x in all_exps if x > day]
        return nxt[0] if nxt else None
    return dict(kind="BANK", step=100, lot=30, days=sorted(day_idx),
                day_idx=day_idx, TIMES=TIMES, C=C, O=O, H=H, L=L,
                LV=LV, SV=SV, prem=prem_store, expiry_fn=expiry_fn,
                _ind=IND, _compute_ind=compute_ind, _votes_at_bar=votes_at_bar,
                _vwap_by_day=VWAP_BY_DAY)

# ======================================================================
# INDEX MACHINERY — NIFTY (copied from ekam_intraday_nifty_build.py, frozen)
# ======================================================================
import re as _re
def nifty_ctx():
    spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv",
                       parse_dates=["timestamp"])
    spot = spot.sort_values("timestamp").reset_index(drop=True)
    spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    O = spot["open"].to_numpy(float); H = spot["high"].to_numpy(float)
    L = spot["low"].to_numpy(float);  C = spot["close"].to_numpy(float)
    DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
    day_idx = {}
    for i, d in enumerate(DATES):
        day_idx.setdefault(d, []).append(i)
    # futures VWAP store (DIAL/EKAM-Nifty basis)
    fut_by_exp = {}
    for fn in (TR / "phase3_buildup_data/futures").glob("FUT7_NIFTY_*.json"):
        m = _re.match(r"FUT7_NIFTY_(\d{4}-\d{2}-\d{2})_", fn.name)
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
        if day in _vw_cache:
            return _vw_cache[day]
        exp = next((e for e in fut_exps if e >= day), None)
        out = {}
        if exp is not None:
            bars = fut_by_exp[exp].get(day, {})
            pv, vv, last = 0.0, 0.0, None
            for t in sorted(bars):
                tp, v_, fc = bars[t]
                pv += tp * v_; vv += v_
                last = pv / vv if vv > 0 else last
                out[t] = (last, fc)
        _vw_cache[day] = out
        return out
    def compute_votes(O_, H_, L_, C_, DATES_, TIMES_):
        n = len(C_)
        trv = np.zeros(n)
        trv[1:] = np.maximum(H_[1:] - L_[1:], np.maximum(
            np.abs(H_[1:] - C_[:-1]), np.abs(L_[1:] - C_[:-1])))
        atr = np.full(n, np.nan)
        if n > 7:
            atr[7] = trv[1:8].mean()
            for i in range(8, n):
                atr[i] = (atr[i - 1] * 6 + trv[i]) / 7.0
        hl2 = (H_ + L_) / 2.0
        ub = hl2 + 3 * atr; lb = hl2 - 3 * atr
        fub = np.full(n, np.nan); flb = np.full(n, np.nan)
        stdir = np.zeros(n, dtype=int)
        for i in range(n):
            if np.isnan(atr[i]):
                continue
            if i == 0 or np.isnan(fub[i - 1]):
                fub[i], flb[i] = ub[i], lb[i]
            else:
                fub[i] = ub[i] if (ub[i] < fub[i - 1] or C_[i - 1] > fub[i - 1]) else fub[i - 1]
                flb[i] = lb[i] if (lb[i] > flb[i - 1] or C_[i - 1] < flb[i - 1]) else flb[i - 1]
            if i == 0 or stdir[i - 1] == 0:
                stdir[i] = -1 if C_[i] <= flb[i] else (1 if C_[i] >= fub[i] else -1)
            elif stdir[i - 1] == 1:
                stdir[i] = -1 if C_[i] < flb[i] else 1
            else:
                stdir[i] = 1 if C_[i] > fub[i] else -1
        delta = np.diff(C_, prepend=C_[0])
        gain = np.where(delta > 0, delta, 0.0); loss = np.where(delta < 0, -delta, 0.0)
        def wilder(x, p):
            out = np.full(n, np.nan)
            if n > p:
                out[p] = x[1:p + 1].mean()
                for i in range(p + 1, n):
                    out[i] = (out[i - 1] * (p - 1) + x[i]) / p
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
        ema9 = ema_series(C_, 9); ema21 = ema_series(C_, 21)
        ema12 = ema_series(C_, 12); ema26 = ema_series(C_, 26)
        macd = ema12 - ema26
        macd_sig = ema_series(macd, 9)
        dh = np.zeros(n); dl_ = np.zeros(n)
        dh[1:] = H_[1:] - H_[:-1]; dl_[1:] = L_[:-1] - L_[1:]
        pdm = np.where((dh > dl_) & (dh > 0), dh, 0.0)
        mdm = np.where((dl_ > dh) & (dl_ > 0), dl_, 0.0)
        def wilder_sum(x, p):
            out = np.full(n, np.nan)
            if n > p:
                out[p] = x[1:p + 1].sum()
                for i in range(p + 1, n):
                    out[i] = out[i - 1] - out[i - 1] / p + x[i]
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
                adx[i] = (adx[i - 1] * 13 + dx[i]) / 14.0
        lv5 = np.zeros(n, dtype=int); sv5 = np.zeros(n, dtype=int)
        lv5 += np.where(ema9 > ema21, 1, 0); sv5 += np.where(ema9 < ema21, 1, 0)
        lv5 += np.where(stdir == 1, 1, 0);  sv5 += np.where(stdir == -1, 1, 0)
        lv5 += np.where(macd > macd_sig, 1, 0); sv5 += np.where(macd < macd_sig, 1, 0)
        lv5 += np.where((rsi >= 50) & (rsi < 70), 1, 0)
        sv5 += np.where((rsi > 30) & (rsi < 50), 1, 0)
        dates_arr = np.array(DATES_); times_arr = np.array(TIMES_)
        for day in pd.unique(dates_arr):
            vw = vwap_series(str(day))
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
        return lv, sv
    LV, SV = compute_votes(O, H, L, C, DATES, TIMES)
    OI = TR / "oi_buildup_data"
    expiry_cal = sorted({m.group(1) for fn in OI.glob("candles_NIFTY_*.json")
                         for m in [_re.match(
                             r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_",
                             fn.name)] if m})
    _file_cache = {}
    def contract_bars(day, strike, typ, exp):
        key = (day, strike, typ, exp)
        if key in _file_cache:
            return _file_cache[key]
        fn = OI / f"candles_NIFTY_{strike}{typ}_{exp}_{day}.json"
        out = None
        if fn.exists():
            raw = json.load(open(fn))["data"]["candles"]
            out = {}
            for ts, o_, h_, l_, c_, v_, oi_ in raw:
                out[ts[11:16]] = (o_, h_, l_, c_)
        _file_cache[key] = out
        return out
    def prem(exp, strike, typ, day):
        return contract_bars(day, strike, typ, exp)
    def expiry_fn(day):
        nxt = [e for e in expiry_cal if e >= day]
        if not nxt:
            return None
        if nxt[0] > day:
            return nxt[0]
        later = [e for e in expiry_cal if e > day]
        return later[0] if later else None
    return dict(kind="NIFTY", step=50, lot=65, days=sorted(day_idx),
                day_idx=day_idx, TIMES=TIMES, C=C, O=O, H=H, L=L,
                DATES=DATES, LV=LV, SV=SV, prem=prem, expiry_fn=expiry_fn,
                _compute_votes=compute_votes)

# ======================================================================
# INDEX ARM — scoring
# ======================================================================
def book_signals():
    books = {"BANK": defaultdict(lambda: dict(sides=set(), first=None)),
             "NIFTY": defaultdict(lambda: dict(sides=set(), first=None))}
    earliest = {}
    with open(TR / "november_books_fix_anatomy_legs.csv") as f:
        for r in csv.DictReader(f):
            kind = {"BANK_STACK": "BANK", "NIFTY_TUNED_V1": "NIFTY"}.get(r["book"])
            if kind is None:
                continue
            d = books[kind][r["date"]]
            d["sides"].add(r["side"])
            key = (kind, r["date"])
            if key not in earliest or r["entry_time"] < earliest[key]:
                earliest[key] = r["entry_time"]
                d["first"] = r["side"]
    return books

def nearest_step(x, step):
    return int(step * math.floor(x / step + 0.5))

def run_index(ctx, book):
    kind = ctx["kind"]
    counts = defaultdict(int)
    trades = defaultdict(list)
    days = ctx["days"]
    pos = {d: i for i, d in enumerate(days)}
    entry_days = [d for d in days if "2026-01-01" <= d <= "2026-10-31"]
    def bar_close(day, stamp):
        idxs = ctx["day_idx"][day]
        for gi in idxs:
            if ctx["TIMES"][gi] == stamp:
                return float(ctx["C"][gi]), gi
        return None, None
    def try_trade(D, side, rowname):
        # side: +1 CE / -1 PE
        ref, _ = bar_close(D, "15:10")
        if ref is None:
            counts[f"{rowname}_nc_no_1510"] += 1
            return
        strike = nearest_step(ref, ctx["step"])
        typ = "CE" if side == 1 else "PE"
        exp = ctx["expiry_fn"](D)
        if exp is None:
            counts[f"{rowname}_nc_no_expiry"] += 1
            return
        nd = days[pos[D] + 1] if pos[D] + 1 < len(days) else None
        if nd is None:
            counts[f"{rowname}_nc_no_next_day"] += 1
            return
        be = ctx["prem"](exp, strike, typ, D)
        if not be or FILL_STAMP not in be:
            counts[f"{rowname}_nc_no_entry_bar"] += 1
            return
        entry = float(be[FILL_STAMP][3])
        bx = ctx["prem"](exp, strike, typ, nd)
        if not bx or "09:30" not in bx:
            counts[f"{rowname}_nc_no_exit_bar"] += 1
            return
        xp = float(bx["09:30"][3])
        net = (xp - entry) * ctx["lot"] - IDX_COST
        assert FILL_STAMP > VOTE_STAMP
        trades[rowname].append(dict(
            arm=kind.lower(), row=rowname, date=D, side=typ, strike=strike,
            expiry=exp, entry=round(entry, 2), exit=round(xp, 2),
            next_day=nd, net=round(net, 2)))
    for D in entry_days:
        idxs = ctx["day_idx"][D]
        vgi = next((gi for gi in idxs if ctx["TIMES"][gi] == VOTE_STAMP), None)
        if vgi is None:
            counts["day_no_1500_bar"] += 1
            continue
        lv, sv = int(ctx["LV"][vgi]), int(ctx["SV"][vgi])
        vote_side = 1 if lv >= 5 else (-1 if sv >= 5 else 0)
        sig = book.get(D)
        if vote_side != 0:
            try_trade(D, vote_side, "VOTES")
            if sig and (("CE" if vote_side == 1 else "PE") in sig["sides"]):
                try_trade(D, vote_side, "BOTH")
        if sig:
            try_trade(D, 1 if sig["first"] == "CE" else -1, "SIGNAL")
    return trades, counts

def index_placebo(ctx, trades):
    best = max(trades, key=lambda rn: sum(t["net"] for t in trades[rn]))
    real = trades[best]
    real_net = sum(t["net"] for t in real)
    days = ctx["days"]
    pos = {d: i for i, d in enumerate(days)}
    pool = [d for d in days if "2026-01-01" <= d <= "2026-10-31"
            and pos[d] + 1 < len(days)]
    rng = random.Random(SEED)
    def draw_trade(side):
        for _ in range(50):
            D = pool[rng.randrange(len(pool))]
            idxs = ctx["day_idx"][D]
            ref = next((float(ctx["C"][gi]) for gi in idxs
                        if ctx["TIMES"][gi] == "15:10"), None)
            if ref is None:
                continue
            strike = nearest_step(ref, ctx["step"])
            typ = "CE" if side == 1 else "PE"
            exp = ctx["expiry_fn"](D)
            if exp is None:
                continue
            be = ctx["prem"](exp, strike, typ, D)
            if not be or FILL_STAMP not in be:
                continue
            bx = ctx["prem"](exp, strike, typ, days[pos[D] + 1])
            if not bx or "09:30" not in bx:
                continue
            return (float(bx["09:30"][3]) - float(be[FILL_STAMP][3])) * ctx["lot"] - IDX_COST
        return None
    totals, drops = [], 0
    for _ in range(500):
        tot, ok = 0.0, True
        for t in real:
            v = draw_trade(1 if t["side"] == "CE" else -1)
            if v is None:
                drops += 1
                ok = False
                break
            tot += v
        if ok:
            totals.append(tot)
    pct = 100.0 * sum(1 for x in totals if x < real_net) / len(totals) \
        if totals else None
    return dict(row=best, real_trades=len(real), real_net=round(real_net, 2),
                placebo_pct=round(pct, 1) if pct is not None else None,
                iterations=len(totals), dropped_iterations=drops)

def audit_index(ctx, trades):
    seen, keys = [], set()
    for rn in sorted(trades):
        for t in trades[rn]:
            k = (t["date"], t["side"])
            if k not in keys:
                keys.add(k)
                seen.append(t["date"])
    checked, ok = 0, True
    for idx, D in enumerate(sorted(set(seen))):
        if idx % 37 != 0:
            continue
        idxs = ctx["day_idx"][D]
        vgi = next(gi for gi in idxs if ctx["TIMES"][gi] == VOTE_STAMP)
        if ctx["kind"] == "BANK":
            ind = ctx["_compute_ind"](ctx["O"][:vgi + 1], ctx["H"][:vgi + 1],
                                      ctx["L"][:vgi + 1], ctx["C"][:vgi + 1])
            vw = ctx["_vwap_by_day"].get(D)
            v = vw.get(VOTE_STAMP) if vw else None
            lv, sv = ctx["_votes_at_bar"](vgi, ind, v)
            # votes_at_bar reads full-series C for the close — same index/value
            if (lv, sv) != (int(ctx["LV"][vgi]), int(ctx["SV"][vgi])):
                ok = False
        else:
            lv2, sv2 = ctx["_compute_votes"](ctx["O"][:vgi + 1], ctx["H"][:vgi + 1],
                                             ctx["L"][:vgi + 1], ctx["C"][:vgi + 1],
                                             ctx["DATES"][:vgi + 1], ctx["TIMES"][:vgi + 1])
            if (int(lv2[vgi]), int(sv2[vgi])) != (int(ctx["LV"][vgi]), int(ctx["SV"][vgi])):
                ok = False
        checked += 1
    return ok, checked

# ======================================================================
# MAIN + REPORT
# ======================================================================
def row_block(trades):
    return stats(trades)

def main():
    books = book_signals()
    # ---- stocks
    stocks, s_trades, s_counts, pool = run_stocks()
    s_placebo = stocks_placebo(s_trades, pool)
    s_audit_ok, s_audit_n = audit_stocks(stocks, s_trades)
    all_trades = []
    results = {"spec": "btst_ind_SPEC.md", "seed": SEED, "arms": {}}
    s_out = {}
    for rn in ("L5-X0920", "L5-XCLOSE", "L4-X0920", "L4-XCLOSE",
               "S5-X0920", "S5-XCLOSE"):
        trs = s_trades.get(rn, [])
        all_trades += trs
        s_out[rn] = {str(y): row_block([t for t in trs if t["year"] == y])
                     for y in (2025, 2026)}
    results["arms"]["stocks"] = dict(rows=s_out, counts=dict(s_counts),
                                     placebo=s_placebo,
                                     audit=dict(ok=s_audit_ok, checked=s_audit_n))
    # ---- indices
    idx_out = {}
    for kind, ctxf, bookkey in (("BANK", bank_ctx, "BANK"),
                                ("NIFTY", nifty_ctx, "NIFTY")):
        ctx = ctxf()
        trades, counts = run_index(ctx, books[bookkey])
        pl = index_placebo(ctx, trades) if any(trades.values()) else None
        a_ok, a_n = audit_index(ctx, trades)
        rows = {}
        for rn in ("BOTH", "VOTES", "SIGNAL"):
            trs = trades.get(rn, [])
            all_trades += trs
            rows[rn] = row_block(trs)
        idx_out[kind] = dict(rows=rows, counts=dict(counts), placebo=pl,
                             audit=dict(ok=a_ok, checked=a_n))
    results["arms"]["bank"] = idx_out["BANK"]
    results["arms"]["nifty"] = idx_out["NIFTY"]
    worst_all = min((t["net"] for t in all_trades), default=None)
    results["worst_trade_overall"] = worst_all
    (TR / "btst_ind_results.json").write_text(json.dumps(results, indent=1, default=str))
    with open(TR / "btst_ind_trades.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "row", "date", "sym", "side", "votes", "strike",
                    "expiry", "entry", "exit", "next_day", "net"])
        for t in all_trades:
            w.writerow([t["arm"], t["row"], t["date"], t.get("sym", ""),
                        t["side"], t.get("votes", ""), t.get("strike", ""),
                        t.get("expiry", ""), t["entry"], t["exit"],
                        t["next_day"], t["net"]])
    # ---- report
    def fmt(s):
        if s["trades"] == 0:
            return "0 | 0.00 | – | – | 0 / 0.00 | 0 / 0.00"
        return (f"{s['trades']} | {s['net']:+,.2f} | {s['wr']} | {s['worst']:+,.2f} | "
                f"{s['h1']['trades']} / {s['h1']['net']:+,.2f} | "
                f"{s['h2']['trades']} / {s['h2']['net']:+,.2f}")
    L = []
    L.append("# BTST-IND — BTST decided by intraday indicators (2026-11-15)")
    L.append("")
    L.append("Spec: btst_ind_SPEC.md (frozen before scoring). Research only; arms nothing.")
    L.append("**Overnight gap risk:** an overnight hold carries unhedgeable gap risk — "
             "the worst single night in the CLOSED BTST programme was **−Rs17,125.50 "
             "on 1 Bank lot (2026-03-18 → 19)**. Read every worst trade below against it.")
    L.append(f"Worst single overnight trade in this run: **Rs{worst_all:+,.2f}**." if worst_all is not None else "")
    L.append("")
    L.append("Decision: EKAM 6-vote state at the 15:00 bar · fill: close of the 15:15 bar · "
             "stocks exit next day at the first bar's close (09:20) or the day's close · "
             "index exit next day at the 09:30 premium bar close.")
    L.append("")
    L.append("## Stocks arm (equity cash, per 100 shares PROVISIONAL, Rs40/position; S5 = cash SHORT, labelled)")
    L.append("")
    L.append("| Row | Year | Trades | Net (Rs) | WR % | Worst (Rs) | H1 Jan–Jun (n / Rs) | H2 Jul–Oct (n / Rs) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for rn in ("L5-X0920", "L5-XCLOSE", "L4-X0920", "L4-XCLOSE", "S5-X0920", "S5-XCLOSE"):
        for y in (2025, 2026):
            L.append(f"| {rn} | {y} | {fmt(s_out[rn][str(y)])} |")
    sp = s_placebo
    L.append("")
    L.append(f"Placebo (best stocks row **{sp['row']}**, combined net Rs{sp['combined_net']:+,.2f}; "
             f"200 draws, random entry days, same counts/side): " +
             " · ".join(f"{y}: real Rs{v['real_net']:+,.2f} on {v['real_trades']} trades, "
                        f"placebo percentile {v['placebo_pct']}" for y, v in sp["years"].items()))
    L.append(f"Timing audit (truncated-series vote recompute, every 37th scored trade): "
             f"{'PASS' if s_audit_ok else 'FAIL'} ({s_audit_n} checked).")
    L.append(f"Counts: {dict(s_counts)}")
    L.append("")
    for kind, label in (("bank", "Bank Nifty"), ("nifty", "Nifty")):
        a = results["arms"][kind]
        L.append(f"## Index arm — {label} (bought options, 1 lot, Rs220/trade; Jan–Oct 2026, index premium stores' window)")
        L.append("")
        L.append("SIGNAL = control row approximating the closed programme's V2 (book-direction overnight).")
        L.append("")
        L.append("| Row | Trades | Net (Rs) | WR % | Worst (Rs) | H1 Jan–Jun (n / Rs) | H2 Jul–Oct (n / Rs) |")
        L.append("|---|---|---|---|---|---|---|")
        for rn in ("BOTH", "VOTES", "SIGNAL"):
            L.append(f"| {rn} | {fmt(a['rows'][rn])} |")
        pl = a["placebo"]
        if pl:
            L.append("")
            L.append(f"Placebo (best row **{pl['row']}**: real Rs{pl['real_net']:+,.2f} on "
                     f"{pl['real_trades']} trades; 500 iterations, random entry days): "
                     f"percentile {pl['placebo_pct']} ({pl['iterations']} completed, "
                     f"{pl['dropped_iterations']} dropped on NC).")
        L.append(f"Timing audit: {'PASS' if a['audit']['ok'] else 'FAIL'} ({a['audit']['checked']} checked).")
        L.append(f"Counts: {a['counts']}")
        L.append("")
    (TR / "btst_ind_2026-11-15.md").write_text("\n".join(L))
    print(json.dumps({"stocks_placebo": s_placebo,
                      "bank_placebo": idx_out["BANK"]["placebo"],
                      "nifty_placebo": idx_out["NIFTY"]["placebo"],
                      "worst_overall": worst_all}, indent=1, default=str))

if __name__ == "__main__":
    main()
