#!/usr/bin/env python3
"""DIAL — BANK NIFTY indicator parameter tuning atlas.
Spec: indicator_parameter_tuning_bank_SPEC.md (frozen 2026-11-14
before this run). Local stores only — NO API calls. Research only:
reads stores; writes indicator_parameter_tuning_bank_results.json
+ indicator_parameter_tuning_bank_grid.csv."""
import csv, json, math, random, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
LOT, COST, STEP = 30, 220.0, 100
SEED = 20261114
SQ = "15:20"

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
ALL_DAYS = sorted(day_idx)
DISC_DAYS = [d for d in ALL_DAYS if d <= "2026-06-30"]
VAL_DAYS = [d for d in ALL_DAYS if "2026-07-01" <= d <= "2026-10-31"]
NOV_DAYS = [d for d in ALL_DAYS if "2026-11-02" <= d <= "2026-11-13"]
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

import bisect
def day_vwap(day):
    fd = fut_day(EXP[day], day)
    if not fd:
        return None
    cum_pv, cum_v, raw = 0.0, 0.0, {}
    for t in sorted(fd):
        o, h, l, c, v = fd[t]
        tp = (h + l + c) / 3.0
        cum_pv += tp * v; cum_v += v
        raw[t] = cum_pv / cum_v if cum_v > 0 else None
    ftimes = sorted(raw)
    out = {}
    for gi in day_idx[day]:
        t = TIMES[gi]
        j = bisect.bisect_right(ftimes, t) - 1
        out[t] = raw[ftimes[j]] if j >= 0 else None
    return out

VWAP = {d: day_vwap(d) for d in ALL_DAYS}

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

# ---------------- indicators (causal, continuous series) ----------------
def ema_series(c, period):
    n = len(c); out = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(c[:period]) / period
    for i in range(period, n):
        out[i] = c[i] * k + out[i - 1] * (1 - k)
    return out

def wilder_atr(h, l, c, period):
    n = len(c); tr = [None] * n; atr = [None] * n
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    if n > period:
        atr[period] = sum(tr[1:period + 1]) / period
        for i in range(period + 1, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def supertrend(h, l, c, period, mult):
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

def rsi_wilder(c, period):
    n = len(c); out = [None] * n
    if n <= period:
        return out
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
    ag = sum(gains[:period]) / period; al = sum(losses[:period]) / period
    def _r(a, b):
        return 100.0 if b == 0 else 100.0 - 100.0 / (1.0 + a / b)
    out[period] = _r(ag, al)
    for i in range(period + 1, n):
        ag = (ag * (period - 1) + gains[i - 1]) / period
        al = (al * (period - 1) + losses[i - 1]) / period
        out[i] = _r(ag, al)
    return out

def bollinger_bands(c, period, mult):
    n = len(c); up = [None] * n; lo = [None] * n
    for i in range(period - 1, n):
        w = c[i - period + 1:i + 1]
        m = sum(w) / period
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / period)
        up[i] = m + mult * sd; lo[i] = m - mult * sd
    return up, lo

def donchian(h, l, n_bars):
    n = len(h); up = [None] * n; lo = [None] * n
    for i in range(n_bars, n):
        up[i] = max(h[i - n_bars:i]); lo[i] = min(l[i - n_bars:i])
    return up, lo

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

EMA = {p: ema_series(C, p) for p in (8, 9, 12, 13, 19, 20, 21, 26, 34, 39, 50)}
RSI_S = {p: rsi_wilder(C, p) for p in (7, 14, 21)}
ADX14 = adx_wilder(H, L, C, 14)
ST_S = {(p, m): supertrend(H, L, C, p, float(m))
        for p in (7, 10, 14) for m in (2, 3, 4)}
BB_S = {(p, s): bollinger_bands(C, p, s)
        for p in (14, 20, 30) for s in (1.5, 2.0, 2.5)}
DON_S = {n_: donchian(H, L, n_) for n_ in (10, 20, 55)}

def macd_series(fast, slow, sig):
    ef, es = EMA[fast], EMA[slow]
    n = len(C); line = [None] * n
    for i in range(n):
        if ef[i] is not None and es[i] is not None:
            line[i] = ef[i] - es[i]
    start = next(i for i in range(n) if line[i] is not None)
    vals = [line[i] for i in range(start, n) if line[i] is not None]
    sigv = ema_series(vals, sig)
    signal = [None] * n
    for j, i in enumerate(range(start, n)):
        signal[i] = sigv[j]
    return line, signal

MACD_S = {(8, 21, 5): macd_series(8, 21, 5),
          (12, 26, 9): macd_series(12, 26, 9),
          (19, 39, 9): macd_series(19, 39, 9)}

# ---------------- raw direction-event series (no filters) ----------------
def ev_cross(a, b):
    ev = [None] * N
    for i in range(1, N):
        if None in (a[i], b[i], a[i - 1], b[i - 1]):
            continue
        if a[i - 1] <= b[i - 1] and a[i] > b[i]:
            ev[i] = "up"
        elif a[i - 1] >= b[i - 1] and a[i] < b[i]:
            ev[i] = "down"
    return ev

EV = {}
for pair in ((9, 21), (13, 34), (20, 50)):
    EV[("EMA", pair)] = ev_cross(EMA[pair[0]], EMA[pair[1]])
for key, direc in ST_S.items():
    ev = [None] * N
    for i in range(1, N):
        if direc[i] is not None and direc[i - 1] is not None and \
                direc[i] != direc[i - 1]:
            ev[i] = direc[i]
    EV[("ST", key)] = ev
for p in (7, 14, 21):
    r = RSI_S[p]; ev = [None] * N
    for i in range(1, N):
        if r[i] is None or r[i - 1] is None:
            continue
        if r[i - 1] <= 50 and r[i] > 50:
            ev[i] = "up"
        elif r[i - 1] >= 50 and r[i] < 50:
            ev[i] = "down"
    EV[("RSIM", p)] = ev
for p in (7, 14, 21):
    for os_ in (25, 30, 35):
        ob_ = 100 - os_; r = RSI_S[p]; ev = [None] * N
        mode = None; ext = None; fired = False
        for i in range(1, N):
            if r[i] is None or r[i - 1] is None:
                continue
            if r[i - 1] >= 50 and r[i] < 50:
                mode, ext, fired = "long", r[i], False
            elif r[i - 1] <= 50 and r[i] > 50:
                mode, ext, fired = "short", r[i], False
            if mode == "long":
                ext = min(ext, r[i])
                if not fired and ext <= os_ and r[i] > r[i - 1] and r[i] <= 50:
                    ev[i] = "up"; fired = True
            elif mode == "short":
                ext = max(ext, r[i])
                if not fired and ext >= ob_ and r[i] < r[i - 1] and r[i] >= 50:
                    ev[i] = "down"; fired = True
        EV[("RSIR", (p, os_))] = ev
for key, (line, signal) in MACD_S.items():
    ev = [None] * N
    for i in range(1, N):
        if None in (line[i], signal[i], line[i - 1], signal[i - 1]):
            continue
        if line[i - 1] <= signal[i - 1] and line[i] > signal[i]:
            ev[i] = "up"
        elif line[i - 1] >= signal[i - 1] and line[i] < signal[i]:
            ev[i] = "down"
    EV[("MACD", key)] = ev
for key, (up, lo) in BB_S.items():
    evb = [None] * N; evr = [None] * N
    arm = None; arm_i = -1
    for i in range(N):
        if up[i] is None:
            continue
        if C[i] > up[i]:
            evb[i] = "up"
        elif C[i] < lo[i]:
            evb[i] = "down"
        if C[i] >= up[i]:
            arm, arm_i = "short", i
        elif C[i] <= lo[i]:
            arm, arm_i = "long", i
        elif arm is not None:
            if i - arm_i > 30:
                arm = None
            elif arm == "short" and C[i] < up[i]:
                evr[i] = "down"; arm = None
            elif arm == "long" and C[i] > lo[i]:
                evr[i] = "up"; arm = None
    EV[("BBB", key)] = evb
    EV[("BBR", key)] = evr
for n_, (up, lo) in DON_S.items():
    ev = [None] * N
    for i in range(N):
        if up[i] is None:
            continue
        if C[i] > up[i]:
            ev[i] = "up"
        elif C[i] < lo[i]:
            ev[i] = "down"
    EV[("DON", n_)] = ev

# per-day raw events (for E4 exits): {(family,sigkey): {day: [(pos, side)]}}
DAY_EV = {}
for k, ev in EV.items():
    byd = {}
    for d, idxs in day_idx.items():
        lst = [(POS[gi], ev[gi]) for gi in idxs if ev[gi] is not None]
        if lst:
            byd[d] = lst
    DAY_EV[k] = byd

# ---------------- signal scan per variant ----------------
def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

def scan_signals(family, sigkey, adx_level, days):
    """First qualifying signal per day. Returns (signals, counts)
    signals = [{date, gi, side}]."""
    ev = EV[(family, sigkey)]
    sigs = []; cnt = dict(sig=0, late=0, nc_filter=0)
    for day in days:
        idxs = day_idx[day]
        vw = VWAP[day]
        for pos, gi in enumerate(idxs):
            t = TIMES[gi]
            if t > "15:10":
                break
            s = ev[gi]
            if s is None:
                continue
            # filters are evaluated at this bar; a failed filter does
            # NOT consume the day's first-signal slot.
            if adx_level is not None:
                a = ADX14[gi]
                if a is None or a < adx_level:
                    continue
            if family == "EMA":
                v = vw.get(t) if vw else None
                if v is None:
                    continue
                if s == "up" and not C[gi] > v:
                    continue
                if s == "down" and not C[gi] < v:
                    continue
            if pos >= len(idxs) - 1:
                cnt["late"] += 1
                break
            sigs.append(dict(date=day, gi=gi, side=s,
                             signal_time=t))
            cnt["sig"] += 1
            break
    return sigs, cnt

# ---------------- trade scoring ----------------
EXIT_SL = {"E1": (40.0, 70.0), "E2": (50.0, 90.0), "E3": (60.0, 120.0)}

def score_trade(day, entry_time, side, ref_close, exit_set, ev_key=None):
    strike = int(math.floor(ref_close / STEP + 0.5)) * STEP
    typ = "CE" if side == "up" else "PE"
    exp = EXP[day]
    prem = prem_store(exp, strike, typ, day)
    if not prem or entry_time not in prem:
        return None
    entry_px = prem[entry_time][0]
    exit_px = reason = xt = None
    if exit_set in EXIT_SL:
        stop, tgt = EXIT_SL[exit_set]
        m = tmin(entry_time)
        while m <= tmin(SQ):
            t = tstr(m)
            bar = prem.get(t)
            if bar is None:
                return None
            o, h, l, c = bar
            if l <= entry_px - stop:
                exit_px, reason, xt = entry_px - stop, "stop", t; break
            if h >= entry_px + tgt:
                exit_px, reason, xt = entry_px + tgt, "target", t; break
            if t == SQ:
                exit_px, reason, xt = c, "squareoff", t; break
            m += 5
    else:  # E4 flip exit, hard stop -60
        stop = 60.0
        idxs = day_idx[day]
        pos_of = {TIMES[gi]: POS[gi] for gi in idxs}
        entry_pos = pos_of[entry_time]
        opp = [q for (q, s) in DAY_EV[ev_key].get(day, []) if s != side]
        opp_after = [q for q in opp if q >= entry_pos]
        flip_bar = (min(opp_after) + 1) if opp_after else None
        m = tmin(entry_time)
        while m <= tmin(SQ):
            t = tstr(m)
            bar = prem.get(t)
            if bar is None:
                return None
            o, h, l, c = bar
            p = pos_of[t]
            if flip_bar is not None and p >= flip_bar:
                exit_px, reason, xt = o, "flip", t; break
            if l <= entry_px - stop:
                exit_px, reason, xt = entry_px - stop, "stop", t; break
            if t == SQ:
                exit_px, reason, xt = c, "squareoff", t; break
            m += 5
    if exit_px is None:
        return None
    return dict(date=day, side=side, strike=strike, typ=typ, expiry=exp,
                entry_time=entry_time, entry_px=entry_px, exit_time=xt,
                exit_px=exit_px, exit_reason=reason,
                net=(exit_px - entry_px) * LOT - COST)

def score_signals(sigs, exit_set, ev_key=None):
    trades, nc = [], 0
    for s in sigs:
        idxs = day_idx[s["date"]]
        entry_gi = idxs[POS[s["gi"]] + 1]
        tr = score_trade(s["date"], TIMES[entry_gi], s["side"], C[s["gi"]],
                         exit_set, ev_key)
        if tr is None:
            nc += 1
        else:
            tr["signal_time"] = s["signal_time"]
            trades.append(tr)
    return trades, nc

def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = sum(t["net"] for t in trades)
    months = {}
    for t in trades:
        months[t["date"][:7]] = months.get(t["date"][:7], 0.0) + t["net"]
    top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                total=round(total, 2),
                trade_days=len(set(t["date"] for t in trades)),
                months={k: round(v, 2) for k, v in sorted(months.items())},
                ex_top3=round(total - sum(top3), 2))

# ---------------- grid definition ----------------
import itertools
ADX_LEVELS = [None, 20, 25]
EXIT_TREND = ["E1", "E2", "E3", "E4"]
EXIT_BASE = ["E1", "E2", "E3"]
GATE_DAYS = sorted(DISC_DAYS + VAL_DAYS)

FAMS = [
    dict(name="EMA", card="EMA cross", trend=True,
         axes=[[(9, 21), (13, 34), (20, 50)]],
         sigkey=lambda av: av[0],
         label=lambda av: f"EMA {av[0][0]}/{av[0][1]}"),
    dict(name="ST", card="Supertrend", trend=True,
         axes=[[7, 10, 14], [2, 3, 4]],
         sigkey=lambda av: (av[0], av[1]),
         label=lambda av: f"ST period {av[0]} x mult {av[1]}"),
    dict(name="RSIM", card="RSI momentum", trend=False,
         axes=[[7, 14, 21]],
         sigkey=lambda av: av[0],
         label=lambda av: f"RSI({av[0]}) 50-cross"),
    dict(name="RSIR", card="RSI reversion", trend=False,
         axes=[[7, 14, 21], [25, 30, 35]],
         sigkey=lambda av: (av[0], av[1]),
         label=lambda av: f"RSI({av[0]}) rev {av[1]}/{100 - av[1]}"),
    dict(name="MACD", card="MACD", trend=True,
         axes=[[(8, 21, 5), (12, 26, 9), (19, 39, 9)]],
         sigkey=lambda av: av[0],
         label=lambda av: f"MACD {av[0][0]},{av[0][1]},{av[0][2]}"),
    dict(name="BBB", card="Bollinger breakout", trend=False,
         axes=[[14, 20, 30], [1.5, 2.0, 2.5]],
         sigkey=lambda av: (av[0], av[1]),
         label=lambda av: f"BB {av[0]}/{av[1]} breakout"),
    dict(name="BBR", card="Bollinger reversion", trend=False,
         axes=[[14, 20, 30], [1.5, 2.0, 2.5]],
         sigkey=lambda av: (av[0], av[1]),
         label=lambda av: f"BB {av[0]}/{av[1]} reversion"),
    dict(name="DON", card="Donchian breakout", trend=True,
         axes=[[10, 20, 55]],
         sigkey=lambda av: av[0],
         label=lambda av: f"DON {av[0]}"),
]

ROWS = {}          # key -> row dict
SIGS = {}          # (fam, sigkey, adx_level) -> gate signals
AUDIT_BARS = {}    # (fam, sigkey) -> [gi,...]

for fam in FAMS:
    exits = EXIT_TREND if fam["trend"] else EXIT_BASE
    adx_list = ADX_LEVELS if fam["trend"] else [None]
    for idx_tuple in itertools.product(*[range(len(a)) for a in fam["axes"]]):
        axis_vals = tuple(fam["axes"][k][idx_tuple[k]]
                          for k in range(len(fam["axes"])))
        sigkey = fam["sigkey"](axis_vals)
        ev_key = (fam["name"], sigkey)
        for adx_idx, adx_level in enumerate(adx_list):
            skey = (fam["name"], sigkey, adx_level)
            sigs, cnt = scan_signals(fam["name"], sigkey, adx_level,
                                     GATE_DAYS)
            SIGS[skey] = sigs
            if adx_level is None:
                ab = AUDIT_BARS.setdefault((fam["name"], sigkey), [])
                for s in sigs:
                    if len(ab) < 5:
                        ab.append(s["gi"])
            for exit_idx, exit_set in enumerate(exits):
                trades, nc = score_signals(sigs, exit_set, ev_key)
                disc = stats([t for t in trades if t["date"] <= "2026-06-30"])
                val = stats([t for t in trades if t["date"] >= "2026-07-01"])
                key = (fam["name"], idx_tuple,
                       adx_idx if fam["trend"] else -1, exit_idx)
                ROWS[key] = dict(
                    family=fam["name"], card=fam["card"],
                    label=fam["label"](axis_vals),
                    axis_vals=[list(x) if isinstance(x, tuple) else x
                               for x in axis_vals],
                    idx_tuple=list(idx_tuple),
                    adx=(adx_level if fam["trend"] else None),
                    adx_idx=(adx_idx if fam["trend"] else -1),
                    exit=exit_set, exit_idx=exit_idx,
                    ev_key=[ev_key[0], ev_key[1] if not isinstance(
                        ev_key[1], tuple) else list(ev_key[1])],
                    sigkey=(sigkey if not isinstance(sigkey, tuple)
                            else list(sigkey)),
                    signals=len(sigs), late=cnt["late"], nc=nc,
                    disc=disc, val=val,
                    val_sides=[t["side"] for t in trades
                               if t["date"] >= "2026-07-01"])

print(f"grid rows: {len(ROWS)}")

# ---------------- timing audit (truncated recomputation) ----------------
def audit_family(fam_name, sigkey, gi):
    """Recompute the family's defining indicator values at bar gi
    from the series truncated at gi; compare with full-series."""
    h, l, c = H[:gi + 1], L[:gi + 1], C[:gi + 1]
    if fam_name == "EMA":
        f_, s_ = sigkey
        return (abs(ema_series(c, f_)[-1] - EMA[f_][gi]) < 1e-6 and
                abs(ema_series(c, s_)[-1] - EMA[s_][gi]) < 1e-6)
    if fam_name == "ST":
        p, m = sigkey
        return supertrend(h, l, c, p, float(m))[-1] == ST_S[sigkey][gi]
    if fam_name in ("RSIM", "RSIR"):
        p = sigkey if fam_name == "RSIM" else sigkey[0]
        a, b = rsi_wilder(c, p)[-1], RSI_S[p][gi]
        return (a is None and b is None) or abs(a - b) < 1e-9
    if fam_name == "MACD":
        f_, s_, g_ = sigkey
        ef = ema_series(c, f_); es = ema_series(c, s_)
        line = [None if (ef[i] is None or es[i] is None)
                else ef[i] - es[i] for i in range(len(c))]
        start = next(i for i in range(len(c)) if line[i] is not None)
        sigv = ema_series([line[i] for i in range(start, len(c))], g_)
        lt, st_ = MACD_S[sigkey]
        return (sigv[-1] is not None and
                abs(line[-1] - lt[gi]) < 1e-6 and
                abs(sigv[-1] - st_[gi]) < 1e-6)
    if fam_name in ("BBB", "BBR"):
        p, sd = sigkey
        up, lo = bollinger_bands(c, p, sd)
        fu, fl = BB_S[sigkey]
        return abs(up[-1] - fu[gi]) < 1e-6 and abs(lo[-1] - fl[gi]) < 1e-6
    if fam_name == "DON":
        up, lo = donchian(h, l, sigkey)
        fu, fl = DON_S[sigkey]
        return (up[-1] == fu[gi]) and (lo[-1] == fl[gi])
    return False

audit_checked, audit_bad = 0, []
for fam in FAMS:
    seen = set()
    for (fn, sigkey), bars in AUDIT_BARS.items():
        if fn != fam["name"] or str(sigkey) in seen:
            continue
        seen.add(str(sigkey))
        for gi in bars:
            audit_checked += 1
            if not audit_family(fn, sigkey, gi):
                audit_bad.append((fn, str(sigkey), gi))
if audit_bad:
    print("TIMING AUDIT FAILED:", audit_bad[:5])
    sys.exit(1)
print(f"timing audit: PASS ({audit_checked} fired signal bars recomputed "
      f"from truncated series)")

# ---------------- neighbours + robustness ----------------
def neighbours(key):
    fam_name, idx_tuple, adx_idx, exit_idx = key
    fam = next(f for f in FAMS if f["name"] == fam_name)
    out = []
    for k in range(len(idx_tuple)):
        for dlt in (-1, 1):
            nt = list(idx_tuple); nt[k] += dlt
            if 0 <= nt[k] < len(fam["axes"][k]):
                out.append((fam_name, tuple(nt), adx_idx, exit_idx))
    if fam["trend"]:
        for dlt in (-1, 1):
            na = adx_idx + dlt
            if 0 <= na < len(ADX_LEVELS):
                out.append((fam_name, idx_tuple, na, exit_idx))
    exits = EXIT_TREND if fam["trend"] else EXIT_BASE
    for dlt in (-1, 1):
        ne = exit_idx + dlt
        if 0 <= ne < len(exits):
            out.append((fam_name, idx_tuple, adx_idx, ne))
    return [k for k in out if k in ROWS]

VAL_MONTHS = ["2026-07", "2026-08", "2026-09", "2026-10"]

def placebo_val(sides, exit_set, ev_key, real_total):
    rng = random.Random(SEED)
    totals, drops = [], 0
    for _ in range(500):
        tot = 0.0
        for side in sides:
            tr = None
            for _a in range(51):
                d = rng.choice(VAL_DAYS)
                idxs = day_idx[d]
                cand = [gi for gi in idxs if "09:20" <= TIMES[gi] <= "15:15"]
                ei = rng.choice(cand)
                tr = score_trade(d, TIMES[ei], side,
                                 C[idxs[POS[ei] - 1]], exit_set, ev_key)
                if tr:
                    break
            if tr:
                tot += tr["net"]
            else:
                drops += 1
        totals.append(tot)
    totals.sort()
    pct = round(100.0 * sum(1 for x in totals if x < real_total) /
                len(totals), 1)
    return dict(percentile=pct, drops=drops, p50=totals[250],
                p95=totals[474], max=totals[-1])

for key, row in ROWS.items():
    nb = neighbours(key)
    row["neighbours"] = len(nb)
    row["neighbours_val_positive"] = sum(
        1 for k in nb if ROWS[k]["val"]["total"] > 0)
    val = row["val"]
    row["val_red_months"] = sum(
        1 for m in VAL_MONTHS if val["months"].get(m, 0.0) < 0)
    row["val_pace"] = round(val["total"] / 4.0, 2)
    legs = dict(
        disc_val_positive=bool(row["disc"]["total"] > 0 and
                               val["total"] > 0),
        plateau=bool(row["neighbours_val_positive"] >= 2),
        ex_top3=bool(val["ex_top3"] > 0),
        pace_red=bool(row["val_pace"] >= 7500 and
                      row["val_red_months"] <= 1),
        placebo=None)
    row["legs_pre_placebo"] = legs
    row["robust"] = False

candidates = [k for k, r in ROWS.items()
              if r["legs_pre_placebo"]["disc_val_positive"] and
              r["legs_pre_placebo"]["plateau"] and
              r["legs_pre_placebo"]["ex_top3"] and
              r["legs_pre_placebo"]["pace_red"]]
print(f"placebo candidates: {len(candidates)}")
for key in candidates:
    row = ROWS[key]
    ev_key = (row["ev_key"][0],
              tuple(row["ev_key"][1]) if isinstance(row["ev_key"][1], list)
              else row["ev_key"][1])
    pl = placebo_val(row["val_sides"], row["exit"], ev_key,
                     row["val"]["total"])
    row["placebo"] = pl
    row["legs_pre_placebo"]["placebo"] = bool(pl["percentile"] >= 95.0)
    row["robust"] = bool(row["legs_pre_placebo"]["placebo"])

robust_rows = [r for r in ROWS.values() if r["robust"]]
print(f"robust rows: {len(robust_rows)}")

# best raw row (highest validation total)
best_key = max(ROWS, key=lambda k: ROWS[k]["val"]["total"])
best_row = ROWS[best_key]
print(f"best raw row: {best_row['label']} adx={best_row['adx']} "
      f"exit={best_row['exit']} val={best_row['val']['total']} "
      f"robust={best_row['robust']}")

# ---------------- November CF (AFTER robust set frozen) ----------------
def november_cf(row):
    fam_name = row["family"]
    sigkey = tuple(row["sigkey"]) if isinstance(row["sigkey"], list) \
        else row["sigkey"]
    ev_key = (fam_name, sigkey)
    sigs, cnt = scan_signals(fam_name, sigkey, row["adx"], NOV_DAYS)
    trades, nc = score_signals(sigs, row["exit"], ev_key)
    return dict(stats=stats(trades), signals=len(sigs), nc=nc,
                late=cnt["late"],
                trades=[dict(date=t["date"], side=t["side"],
                             entry_time=t["entry_time"],
                             net=t["net"], exit_reason=t["exit_reason"])
                        for t in trades])

nov_cf = {}
for r in robust_rows:
    nov_cf[f"{r['label']}|adx={r['adx']}|{r['exit']}"] = november_cf(r)
nov_cf_best = november_cf(best_row)
print("november CF computed for robust rows + best raw row")

# ---------------- long-term annex (daily spot signal study) ----------------
daily = pd.read_csv(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv")
dD = daily["date"].tolist()
dH = daily["high"].to_numpy(float); dL = daily["low"].to_numpy(float)
dC = daily["close"].to_numpy(float)
dn = len(dC)

def annex_events(name):
    evs = []
    if name in ("EMA(20,50)", "EMA(50,200)"):
        f_, s_ = (20, 50) if name == "EMA(20,50)" else (50, 200)
        ef = ema_series(dC, f_); es = ema_series(dC, s_)
        for i in range(1, dn):
            if None in (ef[i], es[i], ef[i - 1], es[i - 1]):
                continue
            if ef[i - 1] <= es[i - 1] and ef[i] > es[i]:
                evs.append((i, "up"))
            elif ef[i - 1] >= es[i - 1] and ef[i] < es[i]:
                evs.append((i, "down"))
    elif name == "RSI(14) 50-cross":
        r = rsi_wilder(dC, 14)
        for i in range(1, dn):
            if r[i] is None or r[i - 1] is None:
                continue
            if r[i - 1] <= 50 and r[i] > 50:
                evs.append((i, "up"))
            elif r[i - 1] >= 50 and r[i] < 50:
                evs.append((i, "down"))
    elif name == "MACD(12,26,9)":
        ef = ema_series(dC, 12); es = ema_series(dC, 26)
        line = [None if (ef[i] is None or es[i] is None)
                else ef[i] - es[i] for i in range(dn)]
        start = next(i for i in range(dn) if line[i] is not None)
        sigv = ema_series([line[i] for i in range(start, dn)], 9)
        signal = [None] * dn
        for j, i in enumerate(range(start, dn)):
            signal[i] = sigv[j]
        for i in range(1, dn):
            if None in (line[i], signal[i], line[i - 1], signal[i - 1]):
                continue
            if line[i - 1] <= signal[i - 1] and line[i] > signal[i]:
                evs.append((i, "up"))
            elif line[i - 1] >= signal[i - 1] and line[i] < signal[i]:
                evs.append((i, "down"))
    elif name == "Supertrend(10,3)":
        direc = supertrend(dH, dL, dC, 10, 3.0)
        for i in range(1, dn):
            if direc[i] is not None and direc[i - 1] is not None and \
                    direc[i] != direc[i - 1]:
                evs.append((i, direc[i]))
    return evs

ANNEX = {}
for nm in ("EMA(20,50)", "EMA(50,200)", "RSI(14) 50-cross",
           "MACD(12,26,9)", "Supertrend(10,3)"):
    evs = annex_events(nm)
    rec = dict(events=len(evs), horizons={})
    for hz in (5, 10, 20):
        moves = []
        for i, side in evs:
            if i + hz < dn:
                mv = (dC[i + hz] / dC[i] - 1.0) * 100.0
                moves.append(mv if side == "up" else -mv)
        if moves:
            rec["horizons"][hz] = dict(
                n=len(moves),
                avg_pct=round(sum(moves) / len(moves), 3),
                win_pct=round(100.0 * sum(1 for m in moves if m > 0) /
                              len(moves), 1))
    ANNEX[nm] = rec
    print(f"annex {nm}: {rec}")

# ---------------- outputs ----------------
def row_out(r):
    o = {k: r[k] for k in ("family", "card", "label", "adx", "exit",
                           "signals", "late", "nc", "disc", "val",
                           "neighbours", "neighbours_val_positive",
                           "val_red_months", "val_pace", "robust")}
    o["legs"] = r["legs_pre_placebo"]
    if "placebo" in r:
        o["placebo"] = r["placebo"]
    return o

fam_verdicts = {}
for fam in FAMS:
    frows = [r for r in ROWS.values() if r["family"] == fam["name"]]
    rob = [r for r in frows if r["robust"]]
    rob_wr = [r for r in rob if r["val"]["wr"] >= 60.0]
    if rob_wr:
        pick = max(rob_wr, key=lambda r: r["val"]["total"])
        verdict = "PASS"
    elif rob:
        pick = max(rob, key=lambda r: r["val"]["total"])
        verdict = "ROBUST BUT NO PASS (validation WR < 60%)"
    else:
        pick = None
        verdict = "NONE ROBUST"
    fam_verdicts[fam["name"]] = dict(
        card=fam["card"], verdict=verdict,
        robust_rows=len(rob),
        pick=({k: pick[k] for k in ("label", "adx", "exit", "disc", "val")}
              if pick else None))

out = dict(
    spec="indicator_parameter_tuning_bank_SPEC.md",
    basis="paper, buying only, 1 lot (30), Rs220/trade",
    gate_days=dict(discovery=len(DISC_DAYS), validation=len(VAL_DAYS)),
    timing_audit=f"PASS ({audit_checked} bars)",
    rows=[row_out(r) for r in ROWS.values()],
    family_verdicts=fam_verdicts,
    robust_rows=[row_out(r) for r in robust_rows],
    best_raw_row=dict(row=row_out(best_row), november_cf=nov_cf_best,
                      robust=best_row["robust"]),
    november_cf_robust=nov_cf,
    annex=dict(source="volrix_banknifty/banknifty_daily_2019_2026.csv",
               bars=dn, from_date=dD[0], to_date=dD[-1], signals=ANNEX))
json.dump(out, open(TR / "indicator_parameter_tuning_bank_results.json",
                    "w"), indent=1)

with open(TR / "indicator_parameter_tuning_bank_grid.csv", "w",
          newline="") as f:
    w = csv.writer(f)
    w.writerow(["family", "params", "adx", "exit", "signals", "nc",
                "disc_trades", "disc_total", "disc_wr",
                "val_trades", "val_total", "val_wr", "val_ex_top3",
                "val_pace", "val_red_months", "neighbours",
                "neighbours_val_positive", "placebo_pct", "robust"])
    for r in ROWS.values():
        w.writerow([r["family"], r["label"], r["adx"], r["exit"],
                    r["signals"], r["nc"], r["disc"]["trades"],
                    r["disc"]["total"], r["disc"]["wr"],
                    r["val"]["trades"], r["val"]["total"], r["val"]["wr"],
                    r["val"]["ex_top3"], r["val_pace"],
                    r["val_red_months"], r["neighbours"],
                    r["neighbours_val_positive"],
                    (r["placebo"]["percentile"] if "placebo" in r else ""),
                    r["robust"]])

print(json.dumps(fam_verdicts, indent=1))
print("DONE")
