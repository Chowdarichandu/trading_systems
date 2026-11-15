#!/usr/bin/env python3
"""EKAM-INTRADAY — NIFTY (spec: ekam_intraday_nifty_SPEC.md, frozen before scoring).
Standard indicators clubbed by votes; intraday 5-min. Research only.
Reads persisted stores; writes ekam_intraday_nifty_results.json + ekam_intraday_nifty_trades.csv.
"""
import json, random, re
from pathlib import Path
from datetime import date
from collections import Counter
import pandas as pd
import numpy as np

TR = Path.home() / "workspace" / "trading"
LOT = 65
COST = 220.0
random.seed(20261114)

# ---------------------------------------------------------------- spot + indicators
spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv", parse_dates=["timestamp"])
spot = spot.sort_values("timestamp").reset_index(drop=True)
spot["date"] = spot["timestamp"].dt.date
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")

c = spot["close"].values.astype(float); h = spot["high"].values.astype(float); l = spot["low"].values.astype(float)
n = len(spot)

# Wilder ATR(7) + Supertrend(7,3) — identical construction to dial_nifty_build.py
trv = np.zeros(n)
trv[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
atr = np.full(n, np.nan)
if n > 7:
    atr[7] = trv[1:8].mean()
    for i in range(8, n):
        atr[i] = (atr[i-1] * 6 + trv[i]) / 7.0
hl2 = (h + l) / 2.0
ub = hl2 + 3 * atr; lb = hl2 - 3 * atr
fub = np.full(n, np.nan); flb = np.full(n, np.nan); stdir = np.zeros(n, dtype=int)
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

# Wilder RSI(14) — identical to dial_nifty_build.py
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
rsi = np.where(al == 0, 100.0, 100 - 100 / (1 + np.where(al == 0, np.inf, ag / np.where(al == 0, np.nan, al))))

# EMAs (seeded at first close, continuous — same convention as DIAL EMA50)
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

# Wilder ADX(14)
dh = np.zeros(n); dl_ = np.zeros(n)
dh[1:] = h[1:] - h[:-1]; dl_[1:] = l[:-1] - l[1:]
pdm = np.where((dh > dl_) & (dh > 0), dh, 0.0); mdm = np.where((dl_ > dh) & (dl_ > 0), dl_, 0.0)
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
dx = np.where((dip + dim) > 0, 100 * np.abs(dip - dim) / np.where((dip + dim) == 0, np.nan, dip + dim), 0.0)
adx = np.full(n, np.nan)
if n > 27:
    adx[27] = np.nanmean(dx[14:28])
    for i in range(28, n):
        adx[i] = (adx[i-1] * 13 + dx[i]) / 14.0

# ---------------------------------------------------------------- futures VWAP (DIAL code)
fut_by_exp = {}
for fn in (TR / "phase3_buildup_data/futures").glob("FUT7_NIFTY_*.json"):
    m = re.match(r"FUT7_NIFTY_(\d{4}-\d{2}-\d{2})_", fn.name)
    if not m: continue
    exp = m.group(1)
    d = json.load(open(fn))["data"]["candles"]
    dd = fut_by_exp.setdefault(exp, {})
    for ts, o_, h_, l_, c_, v_, oi_ in d:
        dd.setdefault(ts[:10], {})[ts[11:16]] = ((h_ + l_ + c_) / 3.0, v_, c_)
fut_exps = sorted(fut_by_exp)
_vw_cache = {}
def vwap_series(day):
    key = day.isoformat()
    if key in _vw_cache: return _vw_cache[key]
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

# ---------------------------------------------------------------- votes
lv5 = np.zeros(n, dtype=int); sv5 = np.zeros(n, dtype=int)
# directional votes 2-5 (EMA, ST, MACD, RSI) vectorised
lv5 += np.where(ema9 > ema21, 1, 0); sv5 += np.where(ema9 < ema21, 1, 0)
lv5 += np.where(stdir == 1, 1, 0);  sv5 += np.where(stdir == -1, 1, 0)
lv5 += np.where(macd > macd_sig, 1, 0); sv5 += np.where(macd < macd_sig, 1, 0)
lv5 += np.where((rsi >= 50) & (rsi < 70), 1, 0); sv5 += np.where((rsi > 30) & (rsi < 50), 1, 0)
# vote 1 (VWAP, basis-consistent futures close vs futures VWAP) per bar
dates_arr = spot["date"].values; times_arr = spot["time"].values
for day in pd.unique(dates_arr):
    vw = vwap_series(day)
    if not vw: continue
    idxs = np.where(dates_arr == day)[0]
    for i in idxs:
        v = vw.get(times_arr[i])
        if v is None or v[0] is None: continue
        if v[1] > v[0]: lv5[i] += 1
        elif v[1] < v[0]: sv5[i] += 1
# vote 6 (ADX to the leading side)
lv = lv5.copy(); sv = sv5.copy()
lead_l = (~np.isnan(adx)) & (adx >= 20) & (lv5 > sv5)
lead_s = (~np.isnan(adx)) & (adx >= 20) & (sv5 > lv5)
lv += np.where(lead_l, 1, 0); sv += np.where(lead_s, 1, 0)
spot["lv"] = lv; spot["sv"] = sv

# per-day structures
day_rows = {}
for i, d in enumerate(dates_arr):
    day_rows.setdefault(d, []).append(i)
votes_by_day = {d.isoformat(): {times_arr[i]: (int(lv[i]), int(sv[i])) for i in idxs}
                for d, idxs in day_rows.items()}

# ---------------------------------------------------------------- option store (DIAL code)
OI = TR / "oi_buildup_data"
expiry_cal = sorted({re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name).group(1)
                     for fn in OI.glob("candles_NIFTY_*.json") if re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name)})
_file_cache = {}
def contract_bars(day, strike, typ, exp):
    key = (day, strike, typ, exp)
    if key in _file_cache: return _file_cache[key]
    fn = OI / f"candles_NIFTY_{strike}{typ}_{exp}_{day}.json"
    out = None
    if fn.exists():
        raw = json.load(open(fn))["data"]["candles"]
        bars = {}
        for ts, o_, h_, l_, c_, v_, oi_ in raw:
            bars[ts[11:16]] = (o_, h_, l_, c_)
        out = bars
    _file_cache[key] = out
    return out

BAR_TIMES = [f"{9 + (15 + 5*i)//60:02d}:{(15 + 5*i) % 60:02d}" for i in range(75)]  # 09:15..15:25
BT_IDX = {t: j for j, t in enumerate(BAR_TIMES)}
def scorable_window(bars, entry_t):
    if bars is None: return False
    i0 = BT_IDX[entry_t]
    return all(BAR_TIMES[j] in bars for j in range(i0, BT_IDX["15:20"] + 1))

def simulate_x1(bars, entry_t):
    ep = bars[entry_t][0]
    stop, tgt = ep - 50.0, ep + 90.0
    for t in BAR_TIMES[BT_IDX[entry_t]: BT_IDX["15:15"] + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "stop"
        if h_ >= tgt: return ep, tgt, "target"
    return ep, bars["15:20"][0], "sq1520"

def simulate_x2(bars, entry_t, day_str, direction):
    ep = bars[entry_t][0]
    stop = ep - 60.0
    day_votes = votes_by_day.get(day_str, {})
    for t in BAR_TIMES[BT_IDX[entry_t]: BT_IDX["15:15"] + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "stop60"
        v = day_votes.get(t)
        if v is not None:
            own = v[0] if direction == 1 else v[1]
            if own <= 2:
                nxt = BAR_TIMES[BT_IDX[t] + 1]
                return ep, bars[nxt][0], "decay"
    return ep, bars["15:20"][0], "sq1520"

def weekly_expiry(day):
    ds = day.isoformat()
    return next((e for e in expiry_cal if e >= ds), None)

# ---------------------------------------------------------------- signals + scoring
def gen_signal(day, T):
    """First bar (time <= 15:10) with lv >= T (long) or sv >= T (short). Returns (direction, global_idx) or None."""
    for i in day_rows.get(day, []):
        t = times_arr[i]
        if t > "15:10": break
        if t not in BT_IDX: continue
        if lv[i] >= T: return 1, i
        if sv[i] >= T: return -1, i
    return None

def score_signal(day, direction, i, X):
    sig_t = times_arr[i]
    j = BT_IDX[sig_t]
    if j + 1 >= len(BAR_TIMES): return None, "no_entry_bar"
    entry_t = BAR_TIMES[j + 1]
    if entry_t > "15:15": return None, "late"
    strike = int(round(float(c[i]) / 50.0) * 50)
    typ = "CE" if direction == 1 else "PE"
    exp = weekly_expiry(day)
    bars = contract_bars(day.isoformat(), strike, typ, exp)
    if bars is None: return None, "nc_no_file"
    if not scorable_window(bars, entry_t): return None, "nc_partial"
    if X == "X1":
        ep, xp, reason = simulate_x1(bars, entry_t)
    else:
        ep, xp, reason = simulate_x2(bars, entry_t, day.isoformat(), direction)
    net = (xp - ep) * LOT - COST
    return {
        "date": day.isoformat(), "signal_time": sig_t, "entry_time": entry_t,
        "direction": typ, "strike": strike, "expiry": exp,
        "lv": int(lv[i]), "sv": int(sv[i]),
        "entry": ep, "exit": xp, "exit_reason": reason, "net": round(net, 2),
    }, "scored"

def metrics(trades):
    if not trades:
        return {"trades": 0, "total": 0.0, "wr": 0.0, "trade_days": 0, "rs_per_td": 0.0}
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    tdays = len({t["date"] for t in trades})
    return {"trades": len(trades), "total": round(tot, 2), "wr": round(100 * wins / len(trades), 1),
            "trade_days": tdays, "rs_per_td": round(tot / tdays, 2) if tdays else 0.0}

def run_window(d0, d1, T, X):
    days = sorted(d for d in day_rows if d0 <= d <= d1)
    trades, nc, sig_count, no_sig = [], {}, 0, 0
    for day in days:
        s = gen_signal(day, T)
        if s is None:
            no_sig += 1; continue
        sig_count += 1
        tr, status = score_signal(day, s[0], s[1], X)
        if tr: trades.append(tr)
        else: nc[status] = nc.get(status, 0) + 1
    return days, trades, nc, sig_count, no_sig

# ---------------------------------------------------------------- main run
D0, D1 = date(2026, 1, 1), date(2026, 10, 31)
all_days = sorted(d for d in day_rows if D0 <= d <= D1)

# daily max vote distribution over signal-evaluable bars (time <= 15:10)
max_lv_dist, max_sv_dist = Counter(), Counter()
for day in all_days:
    ml = ms = 0
    for i in day_rows[day]:
        if times_arr[i] > "15:10": break
        ml = max(ml, int(lv[i])); ms = max(ms, int(sv[i]))
    max_lv_dist[ml] += 1; max_sv_dist[ms] += 1

rows_out = {}
all_trades = {}
for T in (4, 5):
    for X in ("X1", "X2"):
        row = f"T{T}-{X}"
        days, trades, nc, nsig, no_sig = run_window(D0, D1, T, X)
        jan_jun = [t for t in trades if t["date"] < "2026-07-01"]
        jul_oct = [t for t in trades if t["date"] >= "2026-07-01"]
        pairs = Counter(f'{t["lv"]},{t["sv"]}' for t in trades)
        rows_out[row] = {
            "signals": nsig, "nc": nc, "no_signal_days": no_sig,
            "jan_jun": metrics(jan_jun), "jul_oct": metrics(jul_oct), "full": metrics(trades),
            "signal_vote_pairs_scored": dict(sorted(pairs.items())),
        }
        all_trades[row] = trades

best_row = max(rows_out, key=lambda r: rows_out[r]["full"]["total"])
best_trades = all_trades[best_row]
bT, bX = int(best_row[1]), best_row[3:]

# timing audit: every scored trade in every row
audit_ok = True
audit_checked = 0
for row, trades in all_trades.items():
    for t in trades:
        bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
        audit_checked += 1
        if bars[t["entry_time"]][0] != t["entry"] or BT_IDX[t["entry_time"]] != BT_IDX[t["signal_time"]] + 1:
            audit_ok = False

# independent recompute at first scored signal bar of the best row
def audit_recompute():
    if not best_trades: return {"checked": False}
    tr = best_trades[0]
    i = next(i for i in day_rows[date.fromisoformat(tr["date"])] if times_arr[i] == tr["signal_time"])
    closes = c[:i+1]
    # RSI by explicit Wilder loop
    g = l_ = 0.0
    for x in range(1, 15):
        d = closes[x] - closes[x-1]; g += max(d, 0); l_ += max(-d, 0)
    g /= 14; l_ /= 14
    for x in range(15, len(closes)):
        d = closes[x] - closes[x-1]
        g = (g * 13 + max(d, 0)) / 14; l_ = (l_ * 13 + max(-d, 0)) / 14
    rsi2 = 100.0 if l_ == 0 else 100 - 100 / (1 + g / l_)
    def ema_loop(x, p):
        e = x[0]; kk = 2 / (p + 1)
        for v in x[1:]: e = v * kk + e * (1 - kk)
        return e
    e9, e21 = ema_loop(closes, 9), ema_loop(closes, 21)
    m12, m26 = ema_loop(closes, 12), ema_loop(closes, 26)
    # MACD signal: EMA9 over the MACD line, rebuilt bar by bar
    e12 = e26 = closes[0]; macd_line = []
    k12, k26, k9 = 2/13, 2/27, 2/10
    for x, v in enumerate(closes):
        if x > 0:
            e12 = v * k12 + e12 * (1 - k12); e26 = v * k26 + e26 * (1 - k26)
        macd_line.append(e12 - e26)
    msig = macd_line[0]
    for v in macd_line[1:]: msig = v * k9 + msig * (1 - k9)
    # Supertrend direction via ewm-ATR second implementation
    trs = pd.Series(trv[:i+1])
    atr2 = trs.ewm(alpha=1/7, adjust=False).mean().values
    hl2_ = (h[:i+1] + l[:i+1]) / 2.0
    ub2 = hl2_ + 3 * atr2; lb2 = hl2_ - 3 * atr2
    fub2 = np.zeros(i+1); flb2 = np.zeros(i+1); d2 = np.zeros(i+1, dtype=int)
    cc = closes
    for x in range(i+1):
        if x == 0:
            fub2[x], flb2[x] = ub2[x], lb2[x]
        else:
            fub2[x] = ub2[x] if (ub2[x] < fub2[x-1] or cc[x-1] > fub2[x-1]) else fub2[x-1]
            flb2[x] = lb2[x] if (lb2[x] > flb2[x-1] or cc[x-1] < flb2[x-1]) else flb2[x-1]
        if x == 0:
            d2[x] = -1 if cc[x] <= flb2[x] else (1 if cc[x] >= fub2[x] else -1)
        elif d2[x-1] == 1:
            d2[x] = -1 if cc[x] < flb2[x] else 1
        else:
            d2[x] = 1 if cc[x] > fub2[x] else -1
    return {"checked": True, "date": tr["date"], "signal_time": tr["signal_time"],
            "rsi_main": round(float(rsi[i]), 3), "rsi_indep": round(float(rsi2), 3),
            "rsi_match": abs(float(rsi[i]) - rsi2) < 0.6,
            "ema9_main": round(float(ema9[i]), 2), "ema9_indep": round(float(e9), 2),
            "ema21_main": round(float(ema21[i]), 2), "ema21_indep": round(float(e21), 2),
            "ema_match": abs(float(ema9[i]) - e9) < 1.0 and abs(float(ema21[i]) - e21) < 1.0,
            "macd_main": round(float(macd[i]), 3), "macd_indep": round(float(macd_line[-1]), 3),
            "macdsig_main": round(float(macd_sig[i]), 3), "macdsig_indep": round(float(msig), 3),
            "macd_match": abs(float(macd[i]) - macd_line[-1]) < 0.6,
            "st_main": int(stdir[i]), "st_indep": int(d2[i]), "st_match": int(stdir[i]) == int(d2[i])}
audit_re = audit_recompute()

# random-entry placebo on the best full-year row (1,000 iterations)
universe = []
for fn in OI.glob("candles_NIFTY_*.json"):
    m = re.match(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", fn.name)
    if not m: continue
    strike, typ, exp, day = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if not ("2026-01-01" <= day <= "2026-10-31"): continue
    if day not in votes_by_day: continue
    bars = contract_bars(day, strike, typ, exp)
    feas = [BAR_TIMES[j] for j in range(0, BT_IDX["15:15"] + 1) if scorable_window(bars, BAR_TIMES[j])]
    if feas: universe.append((bars, feas, day, 1 if typ == "CE" else -1))
cnt_best = rows_out[best_row]["full"]["trades"]
placebo_totals = []
for _ in range(1000):
    tot = 0.0
    for _ in range(cnt_best):
        bars, feas, day, direction = universe[random.randrange(len(universe))]
        et = feas[random.randrange(len(feas))]
        if bX == "X1":
            ep, xp, _r = simulate_x1(bars, et)
        else:
            ep, xp, _r = simulate_x2(bars, et, day, direction)
        tot += (xp - ep) * LOT - COST
    placebo_totals.append(round(tot, 2))
real_best = rows_out[best_row]["full"]["total"]
pct = sum(1 for v in placebo_totals if v <= real_best) / len(placebo_totals) if cnt_best else 0.0
placebo = {"best_row": best_row, "iterations": 1000, "trades_per_iter": cnt_best,
           "percentile": round(pct, 4), "mean_total": round(float(np.mean(placebo_totals)), 2),
           "p95_total": round(float(np.percentile(placebo_totals, 95)), 2),
           "universe_files": len(universe)}

# November CF (all rows, descriptive)
nov_out = {}
for T in (4, 5):
    for X in ("X1", "X2"):
        row = f"T{T}-{X}"
        days, trades, nc, nsig, no_sig = run_window(date(2026, 11, 2), date(2026, 11, 13), T, X)
        nov_out[row] = {"signals": nsig, "nc": nc, "metrics": metrics(trades), "trades_detail": trades}

results = {
    "book": "EKAM-INTRADAY-NIFTY v1 (vote-clubbed standard indicators)",
    "window": "2026-01-01..2026-10-31", "trading_days": len(all_days),
    "rows": rows_out,
    "daily_max_vote_distribution": {"long": {str(k): v for k, v in sorted(max_lv_dist.items())},
                                    "short": {str(k): v for k, v in sorted(max_sv_dist.items())}},
    "timing_audit_ok": audit_ok, "timing_audit_checked": audit_checked,
    "audit_recompute_best_row_first_signal": audit_re,
    "random_placebo": placebo,
    "november_cf": nov_out,
    "trades": all_trades,
}
json.dump(results, open(TR / "ekam_intraday_nifty_results.json", "w"), indent=1,
          default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
flat = []
for row, trades in all_trades.items():
    for t in trades:
        flat.append({"row": row, **t})
pd.DataFrame(flat).to_csv(TR / "ekam_intraday_nifty_trades.csv", index=False)
print(json.dumps({"trading_days": len(all_days), "rows": rows_out, "best_row": best_row,
                  "timing_audit_ok": audit_ok, "checked": audit_checked,
                  "audit_recompute": audit_re, "placebo": placebo,
                  "daily_max": results["daily_max_vote_distribution"],
                  "november": {r: {"signals": v["signals"], "nc": v["nc"], "metrics": v["metrics"]}
                               for r, v in nov_out.items()}}, indent=1, default=str))
