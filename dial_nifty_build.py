#!/usr/bin/env python3
"""DIAL-NIFTY standalone indicator system — gate run (spec: dial_nifty_SPEC.md, frozen).
Research only. Reads persisted stores; writes dial_nifty_results.json + dial_nifty_trades.csv.
"""
import json, math, random, re, sys
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

TR = Path.home() / "workspace" / "trading"
LOT = 65
COST = 220.0
STOP_PTS, TGT_PTS = 50.0, 90.0
random.seed(20261114)

# ---------------------------------------------------------------- spot + indicators
spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv", parse_dates=["timestamp"])
spot = spot.sort_values("timestamp").reset_index(drop=True)
spot["date"] = spot["timestamp"].dt.date
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")

c = spot["close"].values; h = spot["high"].values; l = spot["low"].values
n = len(spot)

# Wilder ATR(7) + Supertrend(7,3)
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
spot["st_dir"] = stdir

# Wilder RSI(14)
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
spot["rsi"] = rsi

# Bollinger %B (20, 2, ddof=1)
s = pd.Series(c)
ma20 = s.rolling(20).mean().values; sd20 = s.rolling(20).std(ddof=1).values
upper = ma20 + 2 * sd20; lower = ma20 - 2 * sd20
pctb = np.where((upper - lower) > 0, (c - lower) / np.where((upper - lower) == 0, np.nan, upper - lower), 0.5)
spot["pctb"] = pctb

# EMA50 + 6-bar slope %
ema = np.full(n, np.nan); k = 2 / 51
e = c[0]
for i in range(n):
    e = c[i] * k + e * (1 - k) if i > 0 else c[0]
    ema[i] = e
slope = np.full(n, np.nan)
slope[6:] = (ema[6:] - ema[:-6]) / ema[:-6] * 100
spot["ema50"] = ema; spot["ema_slope6"] = slope

# ---------------------------------------------------------------- futures VWAP
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
def vwap_series(day):
    """date -> {time: (cumulative session VWAP, futures close)} from near-month futures.
    VWAP-side test is basis-consistent (futures close vs futures VWAP) — see SPEC correction."""
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

# ---------------------------------------------------------------- option store
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
def t_idx(t): return BAR_TIMES.index(t)
def scorable_window(bars, entry_t):
    """bars dict must cover entry_t..15:20 contiguously."""
    if bars is None: return False
    i0 = t_idx(entry_t)
    return all(BAR_TIMES[j] in bars for j in range(i0, t_idx("15:20") + 1))

def simulate(bars, entry_t):
    """Entry at open of entry_t bar; stop/target scanned entry..15:15; SQ = open of 15:20 bar.
    Returns (entry_premium, exit_premium, exit_reason) or None."""
    ep = bars[entry_t][0]
    stop, tgt = ep - STOP_PTS, ep + TGT_PTS
    for t in BAR_TIMES[t_idx(entry_t): t_idx("15:15") + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "stop"
        if h_ >= tgt: return ep, tgt, "target"
    return ep, bars["15:20"][0], "sq1520"

def weekly_expiry(day):
    ds = day.isoformat()
    return next((e for e in expiry_cal if e >= ds), None)

# ---------------------------------------------------------------- signals
def gen_signals(day):
    """Returns list of (component, direction, signal_bar_global_idx) for the day."""
    idxs = spot.index[spot["date"] == day].tolist()
    if not idxs: return []
    vw = vwap_series(day)
    out = []
    got_t = got_r = False
    prev_i = idxs[0] - 1
    for pos, i in enumerate(idxs):
        if got_t and got_r: break
        t = spot.at[i, "time"]
        if t > "15:10": break  # entry bar would start after 15:15
        # DIAL-T: flip at this bar's close vs previous bar (continuous series)
        if not got_t and prev_i >= 0 and stdir[i] != 0 and stdir[prev_i] != 0 and stdir[i] != stdir[prev_i]:
            v = vw.get(t)
            if v is not None and v[0] is not None:
                vwap_v, fut_close = v
                if (stdir[i] == 1 and fut_close > vwap_v) or (stdir[i] == -1 and fut_close < vwap_v):
                    out.append(("T", stdir[i], i)); got_t = True
        # DIAL-R: state at this bar's close
        if not got_r and not np.isnan(rsi[i]) and not np.isnan(pctb[i]) and not np.isnan(slope[i]):
            if rsi[i] <= 30 and pctb[i] <= 0.05 and slope[i] > -0.1:
                out.append(("R", 1, i)); got_r = True
            elif rsi[i] >= 70 and pctb[i] >= 0.95 and slope[i] < 0.1:
                out.append(("R", -1, i)); got_r = True
        prev_i = i
    return out

def score_signal(day, comp, direction, i):
    sig_t = spot.at[i, "time"]
    j = t_idx(sig_t)
    if j + 1 >= len(BAR_TIMES): return None, "no_entry_bar"
    entry_t = BAR_TIMES[j + 1]
    if entry_t > "15:15": return None, "late"
    strike = int(round(spot.at[i, "close"] / 50.0) * 50)
    typ = "CE" if direction == 1 else "PE"
    exp = weekly_expiry(day)
    bars = contract_bars(day.isoformat(), strike, typ, exp)
    if bars is None: return None, "nc_no_file"
    if not scorable_window(bars, entry_t): return None, "nc_partial"
    ep, xp, reason = simulate(bars, entry_t)
    net = (xp - ep) * LOT - COST
    return {
        "component": comp, "date": day.isoformat(), "signal_time": sig_t, "entry_time": entry_t,
        "direction": "CE" if direction == 1 else "PE", "strike": strike, "expiry": exp,
        "entry": ep, "exit": xp, "exit_reason": reason, "net": round(net, 2),
    }, "scored"

def run_window(d0, d1):
    days = sorted(d for d in spot["date"].unique() if d0 <= d <= d1)
    trades, nc = [], {}
    sig_count = 0
    for day in days:
        for comp, direction, i in gen_signals(day):
            sig_count += 1
            tr, status = score_signal(day, comp, direction, i)
            if tr: trades.append(tr)
            else: nc[status] = nc.get(status, 0) + 1
    return days, trades, nc, sig_count

def metrics(trades):
    if not trades:
        return {"trades": 0, "total": 0.0, "wr": 0.0, "trade_days": 0, "rs_per_td": 0.0}
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    tdays = len({t["date"] for t in trades})
    return {"trades": len(trades), "total": round(tot, 2), "wr": round(100 * wins / len(trades), 1),
            "trade_days": tdays, "rs_per_td": round(tot / tdays, 2) if tdays else 0.0}

def month_table(trades, months):
    out = {}
    for m in months:
        sel = [t for t in trades if t["date"][:7] == m]
        out[m] = round(sum(t["net"] for t in sel), 2)
    return out

# ---------------------------------------------------------------- main Jan-Oct run
D0, D1 = date(2026, 1, 1), date(2026, 10, 31)
days, trades, nc, nsig = run_window(D0, D1)
months = [f"2026-{m:02d}" for m in range(1, 11)]
comb = metrics(trades)
comp_m = {cp: metrics([t for t in trades if t["component"] == cp]) for cp in ("T", "R")}
mt = month_table(trades, months)
red_months = sum(1 for v in mt.values() if v < 0)
h1 = sum(t["net"] for t in trades if t["date"] < "2026-06-01")
h2 = sum(t["net"] for t in trades if t["date"] >= "2026-06-01")
top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
ex_top3 = round(comb["total"] - sum(top3), 2) if trades else 0.0
pace = round(comb["total"] / 10, 2)

# timing audit: entry bar == signal bar + 5 min and entry premium == stored open
audit_ok = True
for t in trades:
    bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
    if bars[t["entry_time"]][0] != t["entry"] or t_idx(t["entry_time"]) != t_idx(t["signal_time"]) + 1:
        audit_ok = False

# independent recompute (separate code path) at first scored signal bar of each component
def audit_recompute(comp):
    tr = next((t for t in trades if t["component"] == comp), None)
    if tr is None: return {"component": comp, "checked": False}
    i = spot.index[(spot["date"].astype(str) == tr["date"]) & (spot["time"] == tr["signal_time"])][0]
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
    # EMA50 by direct loop
    e = closes[0]; kk = 2 / 51
    for x in range(1, len(closes)): e = closes[x] * kk + e * (1 - kk)
    return {"component": comp, "checked": True, "rsi_main": round(float(rsi[i]), 3),
            "rsi_indep": round(float(rsi2), 3), "rsi_match": abs(float(rsi[i]) - rsi2) < 0.6,
            "ema_main": round(float(ema[i]), 2), "ema_indep": round(float(e), 2),
            "ema_match": abs(float(ema[i]) - e) < 1.0, "st_dir": int(stdir[i])}
audit_re = [audit_recompute("T"), audit_recompute("R")]

# +30-min shift placebo (deterministic)
shift_trades, shift_dropped = [], 0
for t in trades:
    bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
    j = t_idx(t["entry_time"]) + 6
    if j > t_idx("15:15") or not scorable_window(bars, BAR_TIMES[j]):
        shift_dropped += 1; continue
    ep, xp, reason = simulate(bars, BAR_TIMES[j])
    shift_trades.append({"net": round((xp - ep) * LOT - COST, 2)})
shift_total = round(sum(t["net"] for t in shift_trades), 2)

# random-entry placebo (1000 iterations)
universe = []
for fn in OI.glob("candles_NIFTY_*.json"):
    m = re.match(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", fn.name)
    if not m: continue
    strike, typ, exp, day = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if not ("2026-01-01" <= day <= "2026-10-31"): continue
    bars = contract_bars(day, strike, typ, exp)
    feas = [BAR_TIMES[j] for j in range(0, t_idx("15:15") + 1) if scorable_window(bars, BAR_TIMES[j])]
    if feas: universe.append((bars, feas))
cnt = {"T": comp_m["T"]["trades"], "R": comp_m["R"]["trades"]}
placebo_totals = []
for _ in range(1000):
    tot = 0.0
    for cp in ("T", "R"):
        for _ in range(cnt[cp]):
            bars, feas = universe[random.randrange(len(universe))]
            et = feas[random.randrange(len(feas))]
            ep, xp, _r = simulate(bars, et)
            tot += (xp - ep) * LOT - COST
    placebo_totals.append(round(tot, 2))
pct = sum(1 for v in placebo_totals if v <= comb["total"]) / len(placebo_totals) if trades else 0.0

# November CF
ndays, ntrades, nnc, nnsig = run_window(date(2026, 11, 2), date(2026, 11, 13))
nov = {"days": len(ndays), "signals": nnsig, "trades": ntrades, "nc": nnc,
       "metrics": metrics(ntrades),
       "per_component": {cp: metrics([t for t in ntrades if t["component"] == cp]) for cp in ("T", "R")}}

results = {
    "book": "DIAL-NIFTY (standalone)", "window": "2026-01-01..2026-10-31",
    "trading_days": len(days), "signals": nsig, "nc": nc,
    "combined": comb, "components": comp_m, "month_table": mt, "red_months": red_months,
    "halves": {"H1": round(h1, 2), "H2": round(h2, 2)}, "ex_top3": ex_top3,
    "monthly_pace": pace, "top3": top3,
    "timing_audit_ok": audit_ok, "audit_recompute": audit_re,
    "shift_placebo": {"total": shift_total, "trades": len(shift_trades), "dropped": shift_dropped,
                      "real_beats_shift": comb["total"] > shift_total},
    "random_placebo": {"iterations": 1000, "percentile": round(pct, 4),
                       "p95_total": round(float(np.percentile(placebo_totals, 95)), 2),
                       "mean_total": round(float(np.mean(placebo_totals)), 2)},
    "november_cf": nov,
    "trades": trades,
}
json.dump(results, open(TR / "dial_nifty_results.json", "w"), indent=1,
          default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
pd.DataFrame(trades).to_csv(TR / "dial_nifty_trades.csv", index=False)
print(json.dumps({k: results[k] for k in ("trading_days", "signals", "nc", "combined", "components",
      "month_table", "red_months", "halves", "ex_top3", "monthly_pace", "timing_audit_ok",
      "audit_recompute", "shift_placebo", "random_placebo")}, indent=1, default=str))
print("NOV:", json.dumps(nov, indent=1, default=str))
