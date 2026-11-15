#!/usr/bin/env python3
"""DIAL-NIFTY ROUND 2 — the R-PE seed (spec: dial_nifty_r2_SPEC.md, frozen).
The indicator/signal/scoring code below is Round 1's own code path, copied
verbatim from dial_nifty_build.py so the regenerated set is the control.
Research only. Writes dial_nifty_r2_results.json + dial_nifty_r2_trades.csv.
Round 1 artifacts are read-only inputs and are never written.
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
    if bars is None: return False
    i0 = t_idx(entry_t)
    return all(BAR_TIMES[j] in bars for j in range(i0, t_idx("15:20") + 1))

def simulate(bars, entry_t):
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
    idxs = spot.index[spot["date"] == day].tolist()
    if not idxs: return []
    vw = vwap_series(day)
    out = []
    got_t = got_r = False
    prev_i = idxs[0] - 1
    for pos, i in enumerate(idxs):
        if got_t and got_r: break
        t = spot.at[i, "time"]
        if t > "15:10": break
        if not got_t and prev_i >= 0 and stdir[i] != 0 and stdir[prev_i] != 0 and stdir[i] != stdir[prev_i]:
            v = vw.get(t)
            if v is not None and v[0] is not None:
                vwap_v, fut_close = v
                if (stdir[i] == 1 and fut_close > vwap_v) or (stdir[i] == -1 and fut_close < vwap_v):
                    out.append(("T", stdir[i], i)); got_t = True
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

# ================================================================ ROUND 2 MAIN
D0, D1 = date(2026, 1, 1), date(2026, 10, 31)
days, trades, nc, nsig = run_window(D0, D1)

def line(sel):
    m = metrics(sel)
    return {"n": m["trades"], "total": m["total"],
            "wins": sum(1 for t in sel if t["net"] > 0), "wr": m["wr"],
            "trade_days": m["trade_days"]}

comb = line(trades)
tline = line([t for t in trades if t["component"] == "T"])
rline = line([t for t in trades if t["component"] == "R"])
rce = line([t for t in trades if t["component"] == "R" and t["direction"] == "CE"])
seed = [t for t in trades if t["component"] == "R" and t["direction"] == "PE"]
sline = line(seed)

ANCHORS = {
    "combined": {"n": 205, "total": -89487.20},
    "T": {"n": 112, "total": -51821.70},
    "R": {"n": 93, "total": -37665.50},
    "R_CE": {"n": 47, "total": -70179.00},
    "R_PE_seed": {"n": 46, "total": 32513.50, "wins": 22, "wr": 47.8},
}
control = {}
for name, got in (("combined", comb), ("T", tline), ("R", rline), ("R_CE", rce), ("R_PE_seed", sline)):
    a = ANCHORS[name]
    ok = got["n"] == a["n"] and got["total"] == a["total"] and \
         ("wins" not in a or (got["wins"] == a["wins"] and got["wr"] == a["wr"]))
    control[name] = {"got": got, "anchor": a, "match": bool(ok)}
control_ok = all(v["match"] for v in control.values())
print("CONTROL:", json.dumps(control, indent=1))
if not control_ok:
    print("CONTROL MISMATCH — stopping before the gate, per spec.")
    json.dump({"control": control, "control_ok": False}, open(TR / "dial_nifty_r2_results.json", "w"), indent=1)
    sys.exit(1)

# ---- seed metrics
months = [f"2026-{m:02d}" for m in range(1, 11)]
sm = metrics(seed)
mt = month_table(seed, months)
red_months = sum(1 for v in mt.values() if v < 0)
h1 = round(sum(t["net"] for t in seed if t["date"] < "2026-06-01"), 2)
h2 = round(sum(t["net"] for t in seed if t["date"] >= "2026-06-01"), 2)
top3 = sorted((t["net"] for t in seed), reverse=True)[:3]
ex_top3 = round(sm["total"] - sum(top3), 2)
pace = round(sm["total"] / 10, 2)

# timing audit on seed trades
audit_ok = True
for t in seed:
    bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
    if bars[t["entry_time"]][0] != t["entry"] or t_idx(t["entry_time"]) != t_idx(t["signal_time"]) + 1:
        audit_ok = False

# +30-min shift placebo on the seed
shift_trades, shift_dropped = [], 0
for t in seed:
    bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
    j = t_idx(t["entry_time"]) + 6
    if j > t_idx("15:15") or not scorable_window(bars, BAR_TIMES[j]):
        shift_dropped += 1; continue
    ep, xp, reason = simulate(bars, BAR_TIMES[j])
    shift_trades.append({"net": round((xp - ep) * LOT - COST, 2)})
shift_total = round(sum(t["net"] for t in shift_trades), 2)

# random-entry placebo — PE-only universe, same count and geometry
universe = []
for fn in sorted(OI.glob("candles_NIFTY_*PE_*.json")):
    m = re.match(r"candles_NIFTY_(\d+)(PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", fn.name)
    if not m: continue
    strike, typ, exp, day = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if not ("2026-01-01" <= day <= "2026-10-31"): continue
    bars = contract_bars(day, strike, typ, exp)
    feas = [BAR_TIMES[j] for j in range(0, t_idx("15:15") + 1) if scorable_window(bars, BAR_TIMES[j])]
    if feas: universe.append((bars, feas))
placebo_totals = []
for _ in range(1000):
    tot = 0.0
    for _ in range(len(seed)):
        bars, feas = universe[random.randrange(len(universe))]
        et = feas[random.randrange(len(feas))]
        ep, xp, _r = simulate(bars, et)
        tot += (xp - ep) * LOT - COST
    placebo_totals.append(round(tot, 2))
pct = sum(1 for v in placebo_totals if v <= sm["total"]) / len(placebo_totals)

# ---- November CF: FULL seed signal set (scored + NC with reasons)
nov_detail = []
ndays = sorted(d for d in spot["date"].unique() if date(2026, 11, 2) <= d <= date(2026, 11, 13))
for day in ndays:
    for comp, direction, i in gen_signals(day):
        if comp != "R" or direction != -1: continue
        tr, status = score_signal(day, comp, direction, i)
        rec = {"date": day.isoformat(), "signal_time": spot.at[i, "time"],
               "strike": int(round(spot.at[i, "close"] / 50.0) * 50),
               "expiry": weekly_expiry(day), "status": status}
        if tr: rec.update({k: tr[k] for k in ("entry_time", "entry", "exit", "exit_reason", "net")})
        nov_detail.append(rec)
nov_scored = [r for r in nov_detail if r["status"] == "scored"]
nov_net = round(sum(r["net"] for r in nov_scored), 2)

gate = {
    "placebo_pct_ge_0.95": {"value": round(pct, 4), "pass": bool(pct >= 0.95)},
    "beats_shift": {"value": shift_total, "pass": bool(sm["total"] > shift_total)},
    "halves_positive": {"H1": h1, "H2": h2, "pass": bool(h1 > 0 and h2 > 0)},
    "ex_top3_positive": {"value": ex_top3, "pass": bool(ex_top3 > 0)},
    "rs_per_td_ge_900": {"value": sm["rs_per_td"], "pass": bool(sm["rs_per_td"] >= 900)},
    "wr_ge_60": {"value": sm["wr"], "pass": bool(sm["wr"] >= 60)},
    "pace_ge_7500": {"value": pace, "pass": bool(pace >= 7500)},
    "red_months_le_2": {"value": red_months, "pass": bool(red_months <= 2)},
}
verdict = all(g["pass"] for g in gate.values())

results = {
    "book": "DIAL-NIFTY ROUND 2 — R-PE seed (SHORT-reversion put-buying only)",
    "window": "2026-01-01..2026-10-31",
    "control": control, "control_ok": bool(control_ok),
    "seed": sm, "month_table": mt, "red_months": red_months,
    "halves": {"H1": h1, "H2": h2}, "ex_top3": ex_top3, "top3": top3,
    "monthly_pace": pace, "timing_audit_ok": bool(audit_ok),
    "shift_placebo": {"total": shift_total, "trades": len(shift_trades), "dropped": shift_dropped,
                      "real_beats_shift": bool(sm["total"] > shift_total)},
    "random_placebo": {"iterations": 1000, "universe_pe_files": len(universe),
                       "percentile": round(pct, 4),
                       "p95_total": round(float(np.percentile(placebo_totals, 95)), 2),
                       "mean_total": round(float(np.mean(placebo_totals)), 2)},
    "gate": gate, "verdict_pass": bool(verdict),
    "november_cf": {"signals": nov_detail, "scored": len(nov_scored),
                    "nc": len(nov_detail) - len(nov_scored), "net": nov_net},
    "seed_trades": seed,
}
json.dump(results, open(TR / "dial_nifty_r2_results.json", "w"), indent=1,
          default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
pd.DataFrame(seed).to_csv(TR / "dial_nifty_r2_trades.csv", index=False)
print("SEED:", json.dumps(sm, indent=1))
print("MONTHS:", json.dumps(mt), "red:", red_months)
print("HALVES:", h1, h2, "| EX-TOP3:", ex_top3, "| PACE:", pace, "| AUDIT:", audit_ok)
print("SHIFT:", shift_total, "trades:", len(shift_trades), "dropped:", shift_dropped)
print("PLACEBO: pct", round(pct, 4), "p95", round(float(np.percentile(placebo_totals, 95)), 2),
      "mean", round(float(np.mean(placebo_totals)), 2), "universe", len(universe))
print("GATE:", json.dumps(gate, indent=1), "VERDICT PASS:", verdict)
print("NOV SEED SET:", json.dumps(nov_detail, indent=1), "net:", nov_net)
