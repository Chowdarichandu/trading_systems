#!/usr/bin/env python3
"""DIAL PARAMETER ATLAS — NIFTY (spec: indicator_parameter_tuning_nifty_SPEC.md, frozen).
Research only. Reads persisted stores; writes indicator_parameter_tuning_nifty_results.json,
indicator_parameter_tuning_nifty_heatmap.csv and per-config trade detail is kept in-memory
for the report builder section at the end (November CF). Change nothing running.
"""
import json, math, random, re, sys
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

TR = Path.home() / "workspace" / "trading"
LOT = 65
COST = 220.0
random.seed(20261114)
np.seterr(all="ignore")

# ------------------------------------------------------------------ spot + bars
spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv", parse_dates=["timestamp"])
spot = spot.sort_values("timestamp").reset_index(drop=True)
spot["date"] = spot["timestamp"].dt.date
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
c = spot["close"].values.astype(float); h = spot["high"].values.astype(float)
l = spot["low"].values.astype(float); o = spot["open"].values.astype(float)
n = len(spot)
BAR_TIMES = [f"{9 + (15 + 5*i)//60:02d}:{(15 + 5*i) % 60:02d}" for i in range(75)]  # 09:15..15:25
TIDX = {t: i for i, t in enumerate(BAR_TIMES)}
day_bars = {}
for i, d in enumerate(spot["date"]):
    day_bars.setdefault(d, []).append(i)
ALL_DATES = sorted(day_bars)
JAN_OCT = [d for d in ALL_DATES if date(2026, 1, 1) <= d <= date(2026, 10, 31)]
DISC_DATES = [d for d in JAN_OCT if d <= date(2026, 6, 30)]
VAL_DATES = [d for d in JAN_OCT if d >= date(2026, 7, 1)]
NOV_DATES = [d for d in ALL_DATES if date(2026, 11, 2) <= d <= date(2026, 11, 13)]

def ema_series(x, p):
    out = np.full(len(x), np.nan); k = 2.0 / (p + 1)
    e = x[0]; out[0] = e
    for i in range(1, len(x)):
        e = x[i] * k + e * (1 - k); out[i] = e
    return out

def wilder_smooth(x, p):
    out = np.full(len(x), np.nan)
    if len(x) > p:
        out[p] = np.nansum(x[1:p + 1]) / p
        for i in range(p + 1, len(x)):
            out[i] = (out[i - 1] * (p - 1) + x[i]) / p
    return out

def rsi_series(p):
    delta = np.diff(c, prepend=c[0])
    gain = np.where(delta > 0, delta, 0.0); loss = np.where(delta < 0, -delta, 0.0)
    ag, al = wilder_smooth(gain, p), wilder_smooth(loss, p)
    rs = np.where(al == 0, np.inf, ag / np.where(al == 0, np.nan, al))
    return np.where(al == 0, 100.0, 100 - 100 / (1 + rs))

def supertrend_dir(p, mult):
    trv = np.zeros(n)
    trv[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    atr = wilder_smooth(trv, p)
    hl2 = (h + l) / 2.0
    ub = hl2 + mult * atr; lb = hl2 - mult * atr
    fub = np.full(n, np.nan); flb = np.full(n, np.nan); d = np.zeros(n, dtype=int)
    for i in range(n):
        if np.isnan(atr[i]): continue
        if i == 0 or np.isnan(fub[i - 1]):
            fub[i], flb[i] = ub[i], lb[i]
        else:
            fub[i] = ub[i] if (ub[i] < fub[i - 1] or c[i - 1] > fub[i - 1]) else fub[i - 1]
            flb[i] = lb[i] if (lb[i] > flb[i - 1] or c[i - 1] < flb[i - 1]) else flb[i - 1]
        if i == 0 or d[i - 1] == 0:
            d[i] = -1 if c[i] <= flb[i] else (1 if c[i] >= fub[i] else -1)
        elif d[i - 1] == 1:
            d[i] = -1 if c[i] < flb[i] else 1
        else:
            d[i] = 1 if c[i] > fub[i] else -1
    return d

def adx_series(p=14):
    up = h[1:] - h[:-1]; dn = l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    trv = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    PDM = np.concatenate([[0.0], pdm]); NDM = np.concatenate([[0.0], ndm]); TRV = np.concatenate([[0.0], trv])
    sTR = wilder_smooth(TRV, p); sP = wilder_smooth(PDM, p); sN = wilder_smooth(NDM, p)
    pdi = 100 * sP / sTR; ndi = 100 * sN / sTR
    dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    adx = np.full(n, np.nan)
    seed_i = 2 * p
    if n > seed_i:
        adx[seed_i] = np.nanmean(dx[p:seed_i])
        for i in range(seed_i + 1, n):
            adx[i] = (adx[i - 1] * (p - 1) + dx[i]) / p if not np.isnan(dx[i]) else adx[i - 1]
    return adx

# ------------------------------------------------------------------ futures VWAP side
fut_by_exp = {}
for fn in (TR / "phase3_buildup_data/futures").glob("FUT7_NIFTY_*.json"):
    m = re.match(r"FUT7_NIFTY_(\d{4}-\d{2}-\d{2})_", fn.name)
    if not m: continue
    exp = m.group(1)
    dd = fut_by_exp.setdefault(exp, {})
    for ts, o_, h_, l_, c_, v_, oi_ in json.load(open(fn))["data"]["candles"]:
        dd.setdefault(ts[:10], {})[ts[11:16]] = ((h_ + l_ + c_) / 3.0, v_, c_)
fut_exps = sorted(fut_by_exp)
def vwap_day(day):
    exp = next((e for e in fut_exps if e >= day.isoformat()), None)
    if exp is None: return {}
    bars = fut_by_exp[exp].get(day.isoformat(), {})
    out, pv, vv, last = {}, 0.0, 0.0, None
    for t in sorted(bars):
        tp, v_, fc = bars[t]
        pv += tp * v_; vv += v_
        last = pv / vv if vv > 0 else last
        out[t] = (last, fc)
    return out
# per-global-bar VWAP side flags (basis-consistent: futures close vs futures VWAP)
vwap_up = np.zeros(n, dtype=bool); vwap_dn = np.zeros(n, dtype=bool)
for day in JAN_OCT + NOV_DATES:
    vw = vwap_day(day)
    for i in day_bars[day]:
        v = vw.get(spot.at[i, "time"])
        if v is not None and v[0] is not None:
            if v[1] > v[0]: vwap_up[i] = True
            elif v[1] < v[0]: vwap_dn[i] = True

# ------------------------------------------------------------------ indicators
EMA = {p: ema_series(c, p) for p in (8, 9, 12, 13, 19, 20, 21, 26, 34, 39, 50)}
RSI = {p: rsi_series(p) for p in (7, 14, 21)}
ST = {(p, m): supertrend_dir(p, m) for p in (7, 10, 14) for m in (2, 3, 4)}
ADX14 = adx_series(14)
cs = pd.Series(c)
BB = {}
for p in (14, 20, 30):
    ma = cs.rolling(p).mean().values; sd = cs.rolling(p).std(ddof=1).values
    for s_ in (1.5, 2.0, 2.5):
        BB[(p, s_)] = (ma + s_ * sd, ma - s_ * sd)
DON = {}
for p in (10, 20, 55):
    DON[p] = (pd.Series(h).rolling(p).max().shift(1).values,
              pd.Series(l).rolling(p).min().shift(1).values)
MACD = {}
for (f_, s_, g_) in ((8, 21, 5), (12, 26, 9), (19, 39, 9)):
    line = EMA[f_] - EMA[s_]
    MACD[(f_, s_, g_)] = (line, ema_series(line, g_))

def cross_up(a, b):
    return (a[1:] > b[1:]) & (a[:-1] <= b[:-1])
def cross_dn(a, b):
    return (a[1:] < b[1:]) & (a[:-1] >= b[:-1])
def pad1(x):
    return np.concatenate([[False], x])

# ------------------------------------------------------------------ signal streams
# stream: dict(family, mode, params_label, key_dims(dict for neighbour steps), raw_up, raw_dn,
#              qual_up, qual_dn, exits list, trend bool)
streams = []
def add_stream(family, mode, label, dims, raw_up, raw_dn, qual_up=None, qual_dn=None, trend=False):
    streams.append({"family": family, "mode": mode, "label": label, "dims": dims,
                    "raw_up": raw_up, "raw_dn": raw_dn,
                    "qual_up": raw_up if qual_up is None else qual_up,
                    "qual_dn": raw_dn if qual_dn is None else qual_dn,
                    "trend": trend})
# EMA cross (qualifying = cross AND VWAP side)
for idx, (f_, s_) in enumerate(((9, 21), (13, 34), (20, 50))):
    ru = pad1(cross_up(EMA[f_], EMA[s_])); rd = pad1(cross_dn(EMA[f_], EMA[s_]))
    add_stream("EMA", "cross", f"EMA({f_},{s_})", {"pair": idx}, ru, rd,
               ru & vwap_up, rd & vwap_dn, trend=True)
# Supertrend flips
for p in (7, 10, 14):
    for m_ in (2, 3, 4):
        d = ST[(p, m_)]
        ru = np.zeros(n, dtype=bool); rd = np.zeros(n, dtype=bool)
        fl = (d[1:] != d[:-1]) & (d[1:] != 0) & (d[:-1] != 0)
        ru[1:] = fl & (d[1:] == 1); rd[1:] = fl & (d[1:] == -1)
        add_stream("Supertrend", "flip", f"ST({p},{m_})", {"period": p, "mult": m_}, ru, rd, trend=True)
# RSI momentum
for p in (7, 14, 21):
    r = RSI[p]
    ru = pad1((r[1:] > 50) & (r[:-1] <= 50)); rd = pad1((r[1:] < 50) & (r[:-1] >= 50))
    add_stream("RSI", "momentum", f"RSI({p}) mom50", {"period": p}, ru, rd)
# RSI reversion
for p in (7, 14, 21):
    r = RSI[p]
    for bi, (lo_, hi_) in enumerate(((25, 75), (30, 70), (35, 65))):
        ru = pad1((r[1:] > lo_) & (r[:-1] <= lo_)); rd = pad1((r[1:] < hi_) & (r[:-1] >= hi_))
        add_stream("RSI", "reversion", f"RSI({p}) rev{lo_}/{hi_}", {"period": p, "band": bi}, ru, rd)
# MACD
for idx, (f_, s_, g_) in enumerate(((8, 21, 5), (12, 26, 9), (19, 39, 9))):
    line, sig = MACD[(f_, s_, g_)]
    ru = pad1(cross_up(line, sig)); rd = pad1(cross_dn(line, sig))
    add_stream("MACD", "signal", f"MACD({f_},{s_},{g_})", {"triple": idx}, ru, rd, trend=True)
# Bollinger
for p in (14, 20, 30):
    for s_ in (1.5, 2.0, 2.5):
        up_b, lo_b = BB[(p, s_)]
        bu = pad1((c[1:] > up_b[1:]) & (c[:-1] <= up_b[:-1]))
        bd = pad1((c[1:] < lo_b[1:]) & (c[:-1] >= lo_b[:-1]))
        add_stream("Bollinger", "breakout", f"BB({p},{s_}) bo", {"period": p, "sd": s_}, bu, bd)
        ru2 = pad1((c[1:] >= lo_b[1:]) & (c[:-1] < lo_b[:-1]))
        rd2 = pad1((c[1:] <= up_b[1:]) & (c[:-1] > up_b[:-1]))
        add_stream("Bollinger", "reversion", f"BB({p},{s_}) rev", {"period": p, "sd": s_}, ru2, rd2)
# Donchian
for p in (10, 20, 55):
    top, bot = DON[p]
    bu = np.zeros(n, dtype=bool); bd = np.zeros(n, dtype=bool)
    ok = ~np.isnan(top)
    bu[ok] = (c[ok] > top[ok]) & (np.concatenate([[0.0], c[:-1]])[ok] <= top[ok])
    bd[ok] = (c[ok] < bot[ok]) & (np.concatenate([[0.0], c[:-1]])[ok] >= bot[ok])
    add_stream("Donchian", "breakout", f"DON({p})", {"channel": p}, bu, bd, trend=True)

ADX_LEVELS = [None, 20, 25]
EXITS_TREND = ["E1", "E2", "E3", "E4"]
EXITS_PLAIN = ["E1", "E2", "E3"]
EXIT_GEO = {"E1": (40.0, 70.0), "E2": (50.0, 90.0), "E3": (60.0, 120.0)}

# ------------------------------------------------------------------ option store
OI = TR / "oi_buildup_data"
expiry_cal = sorted({re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name).group(1)
                     for fn in OI.glob("candles_NIFTY_*.json")
                     if re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name)})
_file_cache = {}
def contract_bars(day_iso, strike, typ, exp):
    key = (day_iso, strike, typ, exp)
    if key in _file_cache: return _file_cache[key]
    fn = OI / f"candles_NIFTY_{strike}{typ}_{exp}_{day_iso}.json"
    out = None
    if fn.exists():
        bars = {}
        for ts, o_, h_, l_, c_, v_, oi_ in json.load(open(fn))["data"]["candles"]:
            bars[ts[11:16]] = (o_, h_, l_, c_)
        out = bars
    _file_cache[key] = out
    return out
def weekly_expiry(day):
    ds = day.isoformat()
    return next((e for e in expiry_cal if e >= ds), None)
def scorable_window(bars, entry_t):
    if bars is None: return False
    i0 = TIDX[entry_t]
    return all(BAR_TIMES[j] in bars for j in range(i0, TIDX["15:20"] + 1))

_sim_cache = {}
def simulate(bars, entry_t, exit_id, flip_bar_idx=None, day_idx_list=None):
    """Returns (entry, exit, reason, exit_bar_time_idx) or None. Cached for E1-E3."""
    if exit_id != "E4":
        key = (id(bars), entry_t, exit_id)
        if key in _sim_cache: return _sim_cache[key]
    ep = bars[entry_t][0]
    i0 = TIDX[entry_t]
    res = None
    if exit_id in EXIT_GEO:
        stop_pts, tgt_pts = EXIT_GEO[exit_id]
        stop, tgt = ep - stop_pts, ep + tgt_pts
        for j in range(i0, TIDX["15:15"] + 1):
            t = BAR_TIMES[j]; b = bars[t]
            if b[2] <= stop: res = (ep, stop, "stop", j); break
            if b[1] >= tgt: res = (ep, tgt, "target", j); break
        if res is None: res = (ep, bars["15:20"][0], "sq1520", TIDX["15:20"])
    else:  # E4 flip exit, hard stop -60
        stop = ep - 60.0
        exit_j, exit_px, reason = TIDX["15:20"], bars["15:20"][0], "sq1520"
        last_scan = TIDX["15:15"]
        if flip_bar_idx is not None:
            last_scan = flip_bar_idx
            exit_j = flip_bar_idx + 1
            exit_px = bars[BAR_TIMES[exit_j]][0]; reason = "flip"
        stopped = None
        for j in range(i0, last_scan + 1):
            if bars[BAR_TIMES[j]][2] <= stop:
                stopped = (ep, stop, "stop", j); break
        res = stopped if stopped else (ep, exit_px, reason, exit_j)
    if exit_id != "E4": _sim_cache[key] = res
    return res

# ------------------------------------------------------------------ signal extraction
def first_signals(stream, adx_level, dates):
    """Per day: (day, dir, global_idx) of first qualifying signal, or none."""
    qu, qd = stream["qual_up"], stream["qual_dn"]
    out = []
    for day in dates:
        for i in day_bars[day]:
            if spot.at[i, "time"] > "15:10": break
            up, dn = qu[i], qd[i]
            if not (up or dn): continue
            if adx_level is not None and not (ADX14[i] >= adx_level): continue
            out.append((day, 1 if up else -1, i))
            break
    return out

def opp_flip_idx(stream, day, entry_bar_pos):
    """First raw opposite-direction event bar position (index into BAR_TIMES) in the day
    at/after entry bar position, <= 15:15 position; direction of the ENTRY is implied by caller."""
    return None  # replaced by per-signal logic below

def score_signal(stream, day, direction, gi, exit_id):
    """Score one signal under one exit. Returns trade dict or (None, nc_reason)."""
    sig_t = spot.at[gi, "time"]
    j = TIDX[sig_t]
    if j + 1 >= len(BAR_TIMES): return None, "late"
    entry_t = BAR_TIMES[j + 1]
    if entry_t > "15:15": return None, "late"
    strike = int(round(spot.at[gi, "close"] / 50.0) * 50)
    typ = "CE" if direction == 1 else "PE"
    exp = weekly_expiry(day)
    bars = contract_bars(day.isoformat(), strike, typ, exp)
    if bars is None: return None, "nc_no_file"
    if not scorable_window(bars, entry_t): return None, "nc_partial"
    flip_pos = None
    if exit_id == "E4":
        # first raw opposite event bar in same day at/after entry bar, time <= 15:15
        opp = stream["raw_dn"] if direction == 1 else stream["raw_up"]
        for i2 in day_bars[day]:
            t2 = spot.at[i2, "time"]
            if t2 < entry_t: continue
            if t2 > "15:15": break
            if opp[i2]:
                flip_pos = TIDX[t2]; break
    ep, xp, reason, exit_j = simulate(bars, entry_t, exit_id, flip_pos)
    net = (xp - ep) * LOT - COST
    return {"date": day.isoformat(), "signal_time": sig_t, "entry_time": entry_t,
            "direction": typ, "strike": strike, "expiry": exp, "entry": ep, "exit": xp,
            "exit_reason": reason, "exit_bar_pos": exit_j, "entry_bar_pos": TIDX[entry_t],
            "net": round(net, 2)}, "scored"

def metrics(trades):
    if not trades:
        return {"trades": 0, "total": 0.0, "wr": 0.0, "trade_days": 0}
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    return {"trades": len(trades), "total": round(tot, 2),
            "wr": round(100 * wins / len(trades), 1),
            "trade_days": len({t["date"] for t in trades})}

def month_table(trades, months):
    return {m: round(sum(t["net"] for t in trades if t["date"][:7] == m), 2) for m in months}

DISC_MONTHS = [f"2026-{m:02d}" for m in range(1, 7)]
VAL_MONTHS = [f"2026-{m:02d}" for m in range(7, 11)]

print(f"streams: {len(streams)}", flush=True)

# ------------------------------------------------------------------ config assembly
GRID_LENS = {"EMA": (3,), "Supertrend": (3, 3), "RSI_mom": (3,), "RSI_rev": (3, 3),
             "MACD": (3,), "Bollinger": (3, 3), "Donchian": (3,)}
def stream_group_coords(st):
    fam, mode, d = st["family"], st["mode"], st["dims"]
    if fam == "EMA": return ("EMA", (d["pair"],))
    if fam == "Supertrend": return ("Supertrend", ([7, 10, 14].index(d["period"]), [2, 3, 4].index(d["mult"])))
    if fam == "RSI" and mode == "momentum": return ("RSI_mom", ([7, 14, 21].index(d["period"]),))
    if fam == "RSI" and mode == "reversion": return ("RSI_rev", ([7, 14, 21].index(d["period"]), d["band"]))
    if fam == "MACD": return ("MACD", (d["triple"],))
    if fam == "Bollinger": return ("Bollinger", ([14, 20, 30].index(d["period"]), [1.5, 2.0, 2.5].index(d["sd"])))
    if fam == "Donchian": return ("Donchian", ([10, 20, 55].index(d["channel"]),))
    raise ValueError(fam)

configs = {}   # key -> record
fam_nc = {}    # (family, mode, window) -> dict(signals, scored, nc reasons)
for si, st in enumerate(streams):
    group, coords = stream_group_coords(st)
    exits = EXITS_TREND if st["trend"] else EXITS_PLAIN
    adx_opts = ADX_LEVELS if st["trend"] else [None]
    for adx_level in adx_opts:
        adx_idx = ADX_LEVELS.index(adx_level) if st["trend"] else -1
        sigs = first_signals(st, adx_level, JAN_OCT)
        # score each signal under all exits at once
        per_exit = {e: [] for e in exits}
        nc_reasons = {}
        scored_signals = 0
        for (day, direction, gi) in sigs:
            first = True
            for e in exits:
                tr, status = score_signal(st, day, direction, gi, e)
                if tr is not None:
                    per_exit[e].append(tr)
                elif first:
                    nc_reasons[status] = nc_reasons.get(status, 0) + 1
                first = False
            if per_exit[exits[0]] and per_exit[exits[0]][-1]["date"] == day.isoformat():
                scored_signals += 1
        win = "disc" if True else None
        for wname, wdates in (("disc", DISC_DATES), ("val", VAL_DATES)):
            wset = {d.isoformat() for d in wdates}
            wsigs = [s for s in sigs if s[0].isoformat() in wset]
            key = (st["family"], st["mode"], wname)
            agg = fam_nc.setdefault(key, {"signals": 0, "scored": 0, "nc": {}})
            agg["signals"] += len(wsigs)
        # NC split per window approximated by re-deriving from trade dates: NC reasons are
        # window-agnostic in the loop above; record per signal-set totals and split by date below.
        for e in exits:
            trades = per_exit[e]
            d_tr = [t for t in trades if t["date"] <= "2026-06-30"]
            v_tr = [t for t in trades if t["date"] >= "2026-07-01"]
            key = (group, st["mode"], coords, adx_idx, e)
            configs[key] = {
                "group": group, "coords": coords, "adx_idx": adx_idx,
                "adx": adx_level, "exit": e, "stream_idx": si,
                "family": st["family"], "mode": st["mode"], "label": st["label"],
                "trend": st["trend"],
                "disc": metrics(d_tr), "val": metrics(v_tr),
                "disc_months": month_table(d_tr, DISC_MONTHS),
                "val_months": month_table(v_tr, VAL_MONTHS),
                "val_trades": v_tr, "disc_trades": d_tr,
                "signals_total": len(sigs),
            }
    # per-family NC accounting at signal-set level (window split by signal date)
    # recompute NC per window honestly: rerun the scorability probe per window
    for adx_level in adx_opts:
        sigs = first_signals(st, adx_level, JAN_OCT)
        for (day, direction, gi) in sigs:
            wname = "disc" if day <= date(2026, 6, 30) else "val"
            _tr, status = score_signal(st, day, direction, gi, "E2")
            key = (st["family"], st["mode"], wname)
            agg = fam_nc[key]
            if status == "scored":
                agg["scored"] += 1
            else:
                agg["nc"][status] = agg["nc"].get(status, 0) + 1
print(f"configs: {len(configs)}", flush=True)

def val_ex_top3(rec):
    nets = sorted((t["net"] for t in rec["val_trades"]), reverse=True)
    return round(rec["val"]["total"] - sum(nets[:3]), 2) if nets else 0.0

def neighbours(key):
    group, mode, coords, adx_idx, exit_id = key
    out = []
    lens = GRID_LENS[group]
    for pos in range(len(coords)):
        for delta in (-1, 1):
            nc_ = list(coords); nc_[pos] += delta
            if 0 <= nc_[pos] < lens[pos]:
                k2 = (group, mode, tuple(nc_), adx_idx, exit_id)
                if k2 in configs: out.append(k2)
    if adx_idx >= 0:
        for delta in (-1, 1):
            a2 = adx_idx + delta
            if 0 <= a2 < 3:
                k2 = (group, mode, coords, a2, exit_id)
                if k2 in configs: out.append(k2)
    chain = ["E1", "E2", "E3"]
    if exit_id in chain:
        i = chain.index(exit_id)
        for delta in (-1, 1):
            j = i + delta
            if 0 <= j < 3:
                k2 = (group, mode, coords, adx_idx, chain[j])
                if k2 in configs: out.append(k2)
    return out

# ---------------------------------------------------------- screening legs 1,2,3,5,6,7
for key, rec in configs.items():
    rec["val_ex_top3"] = val_ex_top3(rec)
    rec["val_red_months"] = sum(1 for v in rec["val_months"].values() if v < 0)
    nb = neighbours(key)
    rec["n_neighbours"] = len(nb)
    rec["n_neighbours_val_positive"] = sum(1 for k2 in nb if configs[k2]["val"]["total"] > 0)
    rec["legs"] = {
        "L1_disc_val_positive": rec["disc"]["total"] > 0 and rec["val"]["total"] > 0,
        "L2_neighbours": rec["n_neighbours_val_positive"] >= 2,
        "L3_val_ex_top3": rec["val_ex_top3"] > 0,
        "L5_val_pace": rec["val"]["total"] / 4.0 >= 7500.0,
        "L6_red_months": rec["val_red_months"] <= 1,
        "L7_val_wr60": rec["val"]["wr"] >= 60.0,
    }
    rec["screen_pass"] = all(rec["legs"].values())
survivors = [k for k, r in configs.items() if r["screen_pass"]]
print(f"screen survivors (legs 1,2,3,5,6,7): {len(survivors)}", flush=True)
for k in survivors:
    r = configs[k]
    print("  SURVIVOR:", r["family"], r["mode"], r["label"], "adx", r["adx"], r["exit"],
          "disc", r["disc"]["total"], "val", r["val"]["total"], "wr", r["val"]["wr"], flush=True)

# ---------------------------------------------------------- validation placebo universe
val_universe = []
for fn in OI.glob("candles_NIFTY_*.json"):
    m = re.match(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", fn.name)
    if not m: continue
    strike, typ, exp, day = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if not ("2026-07-01" <= day <= "2026-10-31"): continue
    bars = contract_bars(day, strike, typ, exp)
    feas = [BAR_TIMES[j] for j in range(0, TIDX["15:15"] + 1) if scorable_window(bars, BAR_TIMES[j])]
    if feas: val_universe.append((bars, feas))
print(f"validation placebo universe: {len(val_universe)} contract-days", flush=True)

def placebo_pct(rec, iters):
    cnt = rec["val"]["trades"]
    if cnt == 0: return None
    holds = [t["exit_bar_pos"] - t["entry_bar_pos"] for t in rec["val_trades"]]
    real = rec["val"]["total"]
    totals = []
    for _ in range(iters):
        tot = 0.0
        for k in range(cnt):
            bars, feas = val_universe[random.randrange(len(val_universe))]
            et = feas[random.randrange(len(feas))]
            if rec["exit"] in EXIT_GEO:
                ep_, xp_, _r, _j = simulate(bars, et, rec["exit"])
                tot += (xp_ - ep_) * LOT - COST
            else:
                ep_ = bars[et][0]; i0 = TIDX[et]
                exit_pos = min(i0 + holds[k], TIDX["15:20"])
                stop = ep_ - 60.0; xp_ = bars[BAR_TIMES[exit_pos]][0]
                for j in range(i0, exit_pos):
                    if bars[BAR_TIMES[j]][2] <= stop:
                        xp_ = stop; break
                tot += (xp_ - ep_) * LOT - COST
        totals.append(round(tot, 2))
    return round(sum(1 for v in totals if v <= real) / len(totals), 4), round(float(np.percentile(totals, 95)), 2), round(float(np.mean(totals)), 2)

for key in survivors:
    rec = configs[key]
    iters = 1000 if len(survivors) <= 12 else 300
    out = placebo_pct(rec, iters)
    rec["placebo"] = {"iterations": iters, "percentile": out[0], "p95_total": out[1], "mean_total": out[2]}
    rec["legs"]["L4_placebo"] = out[0] >= 0.95
    print("  PLACEBO:", rec["label"], rec["exit"], "pct", out[0], flush=True)
if len(survivors) > 12:
    for key in survivors:
        rec = configs[key]
        if rec["placebo"]["percentile"] >= 0.90:
            out = placebo_pct(rec, 1000)
            rec["placebo"] = {"iterations": 1000, "percentile": out[0], "p95_total": out[1], "mean_total": out[2]}
            rec["legs"]["L4_placebo"] = out[0] >= 0.95
for key, rec in configs.items():
    rec["robust"] = bool(rec.get("screen_pass") and rec["legs"].get("L4_placebo"))

# ---------------------------------------------------------- cards + best raw
GROUP_FAMILY = {"EMA": ("EMA", "cross"), "Supertrend": ("Supertrend", "flip"),
                "RSI_mom": ("RSI", "momentum"), "RSI_rev": ("RSI", "reversion"),
                "MACD": ("MACD", "signal"), "Bollinger": None, "Donchian": ("Donchian", "breakout")}
cards = {}
for group in ("EMA", "Supertrend", "RSI_mom", "RSI_rev", "MACD", "Donchian"):
    fam, mode = GROUP_FAMILY[group]
    members = [(k, r) for k, r in configs.items() if r["group"] == group]
    robust_members = [(k, r) for k, r in members if r["robust"]]
    robust_members.sort(key=lambda kr: (-kr[1]["val"]["total"], -kr[1]["val"]["wr"]))
    raw_sorted = sorted(members, key=lambda kr: -kr[1]["val"]["total"])
    cards[f"{fam}|{mode}"] = {
        "family": fam, "mode": mode, "n_configs": len(members),
        "best_robust_key": str(robust_members[0][0]) if robust_members else None,
        "best_robust": robust_members[0][1] if robust_members else None,
        "n_robust": len(robust_members),
        "best_raw_in_family": raw_sorted[0][1] if raw_sorted else None,
        "verdict": "PASS" if robust_members else "FAIL — NONE ROBUST",
    }
for mode in ("breakout", "reversion"):
    members = [(k, r) for k, r in configs.items() if r["group"] == "Bollinger" and r["mode"] == mode]
    robust_members = [(k, r) for k, r in members if r["robust"]]
    robust_members.sort(key=lambda kr: (-kr[1]["val"]["total"], -kr[1]["val"]["wr"]))
    raw_sorted = sorted(members, key=lambda kr: -kr[1]["val"]["total"])
    cards[f"Bollinger|{mode}"] = {
        "family": "Bollinger", "mode": mode, "n_configs": len(members),
        "best_robust_key": str(robust_members[0][0]) if robust_members else None,
        "best_robust": robust_members[0][1] if robust_members else None,
        "n_robust": len(robust_members),
        "best_raw_in_family": raw_sorted[0][1] if raw_sorted else None,
        "verdict": "PASS" if robust_members else "FAIL — NONE ROBUST",
    }
best_raw_key, best_raw = max(configs.items(), key=lambda kr: kr[1]["val"]["total"])
print("best raw:", best_raw["family"], best_raw["mode"], best_raw["label"], "adx", best_raw["adx"],
      best_raw["exit"], "val", best_raw["val"]["total"], "robust", best_raw["robust"], flush=True)

# ---------------------------------------------------------- November CF (post-freeze, descriptive)
def nov_cf_for(rec):
    st = streams[rec["stream_idx"]]
    sigs = first_signals(st, rec["adx"], NOV_DATES)
    trades, nc = [], {}
    for (day, direction, gi) in sigs:
        tr, status = score_signal(st, day, direction, gi, rec["exit"])
        if tr: trades.append(tr)
        else: nc[status] = nc.get(status, 0) + 1
    return {"signals": len(sigs), "nc": nc, "metrics": metrics(trades), "trades": trades}
nov_cf = {}
cf_targets = {}
for cname, card in cards.items():
    if card["best_robust"] is not None:
        cf_targets[f"card:{cname}"] = card["best_robust"]
cf_targets["best_raw_overall"] = best_raw
for name, rec in cf_targets.items():
    nov_cf[name] = nov_cf_for(rec)
    print("NOV CF", name, nov_cf[name]["metrics"], flush=True)

# ---------------------------------------------------------- timing audit (sampled, explicit)
import random as _rnd
_rnd.seed(99)
all_trades = []
for rec in configs.values():
    all_trades.extend(rec["val_trades"]); all_trades.extend(rec["disc_trades"])
sample = _rnd.sample(all_trades, min(600, len(all_trades)))
audit_ok = True
for t in sample:
    bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
    if bars[t["entry_time"]][0] != t["entry"] or t["entry_bar_pos"] != TIDX[t["signal_time"]] + 1:
        audit_ok = False
# independent RSI(14) recompute at one 2026 bar (separate code path)
gi_chk = next(i for i in range(n) if spot.at[i, "date"] == date(2026, 3, 2) and spot.at[i, "time"] == "11:00")
closes = c[:gi_chk + 1]
g_ = l_ = 0.0
for x in range(1, 15):
    dd = closes[x] - closes[x - 1]; g_ += max(dd, 0); l_ += max(-dd, 0)
g_ /= 14; l_ /= 14
for x in range(15, len(closes)):
    dd = closes[x] - closes[x - 1]
    g_ = (g_ * 13 + max(dd, 0)) / 14; l_ = (l_ * 13 + max(-dd, 0)) / 14
rsi_indep = 100.0 if l_ == 0 else 100 - 100 / (1 + g_ / l_)
rsi_main = float(RSI[14][gi_chk])
print("timing audit ok:", audit_ok, "| RSI14 main", round(rsi_main, 3), "indep", round(rsi_indep, 3), flush=True)

# ---------------------------------------------------------- long-term annex (daily spot)
daily = pd.read_csv(TR / "data/progressive/NIFTY/spot_daily.csv", parse_dates=["date"])
daily = daily.sort_values("date").reset_index(drop=True)
dc = daily["close"].values.astype(float); dh = daily["high"].values.astype(float)
dl = daily["low"].values.astype(float); dn_ = len(daily)
def ema_d(x, p):
    out = np.full(len(x), np.nan); k = 2.0 / (p + 1); e = x[0]; out[0] = e
    for i in range(1, len(x)):
        e = x[i] * k + e * (1 - k); out[i] = e
    return out
def rsi_d(p):
    delta = np.diff(dc, prepend=dc[0])
    gain = np.where(delta > 0, delta, 0.0); loss = np.where(delta < 0, -delta, 0.0)
    def wsm(x):
        out = np.full(dn_, np.nan)
        out[p] = x[1:p + 1].mean()
        for i in range(p + 1, dn_): out[i] = (out[i - 1] * (p - 1) + x[i]) / p
        return out
    ag, al = wsm(gain), wsm(loss)
    return np.where(al == 0, 100.0, 100 - 100 / (1 + np.where(al == 0, np.inf, ag / np.where(al == 0, np.nan, al))))
def st_d(p, mult):
    trv = np.zeros(dn_)
    trv[1:] = np.maximum(dh[1:] - dl[1:], np.maximum(np.abs(dh[1:] - dc[:-1]), np.abs(dl[1:] - dc[:-1])))
    atr = np.full(dn_, np.nan)
    atr[p] = trv[1:p + 1].mean()
    for i in range(p + 1, dn_): atr[i] = (atr[i - 1] * (p - 1) + trv[i]) / p
    hl2 = (dh + dl) / 2.0
    ub = hl2 + mult * atr; lb = hl2 - mult * atr
    fub = np.full(dn_, np.nan); flb = np.full(dn_, np.nan); d = np.zeros(dn_, dtype=int)
    for i in range(dn_):
        if np.isnan(atr[i]): continue
        if i == 0 or np.isnan(fub[i - 1]): fub[i], flb[i] = ub[i], lb[i]
        else:
            fub[i] = ub[i] if (ub[i] < fub[i - 1] or dc[i - 1] > fub[i - 1]) else fub[i - 1]
            flb[i] = lb[i] if (lb[i] > flb[i - 1] or dc[i - 1] < flb[i - 1]) else flb[i - 1]
        if i == 0 or d[i - 1] == 0: d[i] = -1 if dc[i] <= flb[i] else (1 if dc[i] >= fub[i] else -1)
        elif d[i - 1] == 1: d[i] = -1 if dc[i] < flb[i] else 1
        else: d[i] = 1 if dc[i] > fub[i] else -1
    return d
ANNEX_FROM = pd.Timestamp("2025-07-01")
def annex_events(name, up_ev, dn_ev):
    ev = []
    for i in range(1, dn_):
        if daily.at[i, "date"] < ANNEX_FROM: continue
        if up_ev[i]: ev.append((i, 1))
        elif dn_ev[i]: ev.append((i, -1))
    out = {"signal": name, "events": len(ev),
           "long_events": sum(1 for _, s in ev if s == 1), "short_events": sum(1 for _, s in ev if s == -1)}
    for k in (5, 10, 20):
        rets = [s * (dc[i + k] / dc[i] - 1) * 100 for (i, s) in ev if i + k < dn_]
        out[f"h{k}"] = {"n": len(rets),
                        "mean_pct": round(float(np.mean(rets)), 3) if rets else None,
                        "wr": round(100 * sum(1 for r in rets if r > 0) / len(rets), 1) if rets else None}
    return out
e20, e50, e200 = ema_d(dc, 20), ema_d(dc, 50), ema_d(dc, 200)
annex = []
annex.append(annex_events("EMA(20,50) cross",
             np.concatenate([[False], (e20[1:] > e50[1:]) & (e20[:-1] <= e50[:-1])]),
             np.concatenate([[False], (e20[1:] < e50[1:]) & (e20[:-1] >= e50[:-1])])))
annex.append(annex_events("EMA(50,200) cross",
             np.concatenate([[False], (e50[1:] > e200[1:]) & (e50[:-1] <= e200[:-1])]),
             np.concatenate([[False], (e50[1:] < e200[1:]) & (e50[:-1] >= e200[:-1])])))
r14d = rsi_d(14)
annex.append(annex_events("RSI(14) 50-cross",
             np.concatenate([[False], (r14d[1:] > 50) & (r14d[:-1] <= 50)]),
             np.concatenate([[False], (r14d[1:] < 50) & (r14d[:-1] >= 50)])))
mline = ema_d(dc, 12) - ema_d(dc, 26); msig = ema_d(mline, 9)
annex.append(annex_events("MACD(12,26,9) signal cross",
             np.concatenate([[False], (mline[1:] > msig[1:]) & (mline[:-1] <= msig[:-1])]),
             np.concatenate([[False], (mline[1:] < msig[1:]) & (mline[:-1] >= msig[:-1])])))
std_ = st_d(10, 3)
annex.append(annex_events("Supertrend(10,3) flip",
             np.concatenate([[False], (std_[1:] == 1) & (std_[:-1] == -1)]),
             np.concatenate([[False], (std_[1:] == -1) & (std_[:-1] == 1)])))
for a in annex: print("ANNEX", a, flush=True)

# ---------------------------------------------------------- outputs
def clean_rec(rec):
    return {"family": rec["family"], "mode": rec["mode"], "label": rec["label"],
            "adx": rec["adx"], "exit": rec["exit"],
            "disc": rec["disc"], "val": rec["val"],
            "disc_months": rec["disc_months"], "val_months": rec["val_months"],
            "val_ex_top3": rec["val_ex_top3"], "val_red_months": rec["val_red_months"],
            "n_neighbours": rec["n_neighbours"],
            "n_neighbours_val_positive": rec["n_neighbours_val_positive"],
            "legs": rec["legs"], "screen_pass": rec["screen_pass"],
            "placebo": rec.get("placebo"), "robust": rec["robust"],
            "signals_jan_oct": rec["signals_total"]}
results = {
    "programme": "DIAL PARAMETER ATLAS — NIFTY",
    "spec": "indicator_parameter_tuning_nifty_SPEC.md",
    "windows": {"discovery": "2026-01-01..2026-06-30", "validation": "2026-07-01..2026-10-31"},
    "n_configs": len(configs),
    "timing_audit_ok": bool(audit_ok),
    "rsi14_spotcheck": {"main": round(rsi_main, 3), "independent": round(rsi_indep, 3),
                        "match": abs(rsi_main - rsi_indep) < 0.6},
    "family_nc": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in fam_nc.items()},
    "cards": {name: {"family": cd["family"], "mode": cd["mode"], "n_configs": cd["n_configs"],
                     "n_robust": cd["n_robust"], "verdict": cd["verdict"],
                     "best_robust": clean_rec(cd["best_robust"]) if cd["best_robust"] else None,
                     "best_raw_in_family": clean_rec(cd["best_raw_in_family"]) if cd["best_raw_in_family"] else None}
              for name, cd in cards.items()},
    "best_raw_overall": clean_rec(best_raw) | {"robust": bool(best_raw["robust"])},
    "november_cf": {name: {"signals": v["signals"], "nc": v["nc"], "metrics": v["metrics"],
                           "trades": v["trades"]} for name, v in nov_cf.items()},
    "annex_long_term": annex,
    "configs": [clean_rec(r) for r in configs.values()],
}
json.dump(results, open(TR / "indicator_parameter_tuning_nifty_results.json", "w"), indent=1,
          default=lambda oo: bool(oo) if isinstance(oo, np.bool_) else (float(oo) if isinstance(oo, (np.floating, np.integer)) else str(oo)))
rows = []
for r in configs.values():
    rows.append({"family": r["family"], "mode": r["mode"], "label": r["label"], "adx": r["adx"],
                 "exit": r["exit"], "signals_jan_oct": r["signals_total"],
                 "disc_trades": r["disc"]["trades"], "disc_total": r["disc"]["total"], "disc_wr": r["disc"]["wr"],
                 "val_trades": r["val"]["trades"], "val_total": r["val"]["total"], "val_wr": r["val"]["wr"],
                 "val_ex_top3": r["val_ex_top3"], "val_red_months": r["val_red_months"],
                 "neighbours_val_positive": r["n_neighbours_val_positive"],
                 "placebo_pct": (r.get("placebo") or {}).get("percentile"),
                 "screen_pass": r["screen_pass"], "robust": r["robust"]})
pd.DataFrame(rows).to_csv(TR / "indicator_parameter_tuning_nifty_heatmap.csv", index=False)
print("DONE. robust configs:", sum(1 for r in configs.values() if r["robust"]), flush=True)
