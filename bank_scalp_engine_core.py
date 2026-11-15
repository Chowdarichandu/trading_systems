#!/usr/bin/env python3
"""Bank Scalp Engine — core data + replay + controls.
Genuine 1-min data only (scalp_1min_data/). See bank_scalp_engine_protocol.md.
Conventions: bar index = minutes since 09:15 (0..374). Entry = open of the bar
at index e. Exit replay checks bars e..e+4 (stop before target within a bar);
residual exit at open of bar e+5. Net = (exit-entry)*30 - 220."""
import csv, json, math, random
from pathlib import Path
import numpy as np

TR = Path.home() / "workspace/trading"
SD = TR / "scalp_1min_data"
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]
LOT = 30; COST = 220.0
NB = 375  # bars per day 09:15..15:29

def _midx(ts):
    return (int(ts[11:13]) - 9) * 60 + int(ts[14:16]) - 15

def exp_for(day): return next(e for e in EXPIRIES if e >= day)

# ---------------- spot ----------------
_spot = {}
def load_spot():
    if _spot: return _spot
    for m in range(1, 11):
        p = SD / f"spot_1m_2026-{m:02d}.csv"
        if not p.exists(): continue
        for r in csv.DictReader(open(p)):
            d = r["timestamp"][:10]; i = _midx(r["timestamp"])
            if d not in _spot:
                _spot[d] = {k: np.full(NB, np.nan) for k in "ohlc"}
            for k, col in zip("ohlc", ("open","high","low","close")):
                _spot[d][k][i] = float(r[col])
    return _spot

def days(): return sorted(load_spot())

# ---------------- options (lazy) ----------------
_opt = {}
def opt_day(exp, strike, typ, day):
    """Return dict of arrays for (exp,strike,typ,day) or None if series absent."""
    key = (exp, strike, typ)
    if key not in _opt:
        p = SD / "options" / exp / f"opt_{strike}{typ}.csv"
        series = {}
        if p.exists():
            for r in csv.DictReader(open(p)):
                d = r["timestamp"][:10]; i = _midx(r["timestamp"])
                if i < 0 or i >= NB: continue  # ignore pre/post-session bars (e.g. 15:30-15:39 tail prints)
                if d not in series:
                    series[d] = {k: np.full(NB, np.nan) for k in "ohlc"}
                for k, col in zip("ohlc", ("open","high","low","close")):
                    series[d][k][i] = float(r[col])
        _opt[key] = series
    return _opt[key].get(day)

def atm(spot_close):
    return int(round(spot_close / 100.0) * 100)

# ---------------- exit replay ----------------
def replay(bars, e, tgt, stp):
    """bars: dict o/h/l/c arrays. Entry at open of bar e. Returns
    (entry_px, exit_px, exit_bar, reason) or None if any needed bar missing."""
    o, h, l = bars["o"], bars["h"], bars["l"]
    if e < 0 or e + 5 > NB - 1: return None
    entry = o[e]
    if not np.isfinite(entry): return None
    for b in range(e, e + 5):
        lo, hi = l[b], h[b]
        if not (np.isfinite(lo) and np.isfinite(hi)): return None
        if lo <= entry - stp: return (entry, entry - stp, b, "stop")
        if hi >= entry + tgt: return (entry, entry + tgt, b, "target")
    xp = o[e + 5]
    if not np.isfinite(xp): return None
    return (entry, xp, e + 5, "time")

def score_signal(day, sig_end, direction, tgt, stp, lag=0):
    """sig_end = index of first bar after signal closes (= entry bar index).
    lag=1 shifts entry one bar later (placebo). Returns trade dict or None."""
    spot = load_spot()[day]
    e = sig_end + lag
    if e - 1 < 0 or e + 5 > NB - 1: return None
    ref_close = spot["c"][e - 1]
    if not np.isfinite(ref_close): return None
    strike = atm(ref_close); exp = exp_for(day)
    bars = opt_day(exp, strike, direction, day)
    if bars is None: return None
    r = replay(bars, e, tgt, stp)
    if r is None: return None
    entry, xp, xb, reason = r
    return {"date": day, "direction": direction, "strike": strike, "expiry": exp,
            "entry_bar": e, "entry_premium": round(entry, 2), "exit_bar": xb,
            "exit_premium": round(xp, 2), "exit_reason": reason,
            "net_inr": round((xp - entry) * LOT - COST, 2)}

# ---------------- controls ----------------
def audit(trades, sig_ends):
    """sig_ends: parallel list of signal-end indices. 0 violations required."""
    v = 0
    for t, se in zip(trades, sig_ends):
        if t["entry_bar"] != se: v += 1
        if not (0 <= t["exit_bar"] - t["entry_bar"] <= 5): v += 1
    return v

def random_placebo(n, tgt, stp, seed=42, draws=20):
    rng = random.Random(seed)
    ds = days(); spot = load_spot()
    totals = []
    for _ in range(draws):
        tot = 0.0; got = 0; tries = 0
        while got < n and tries < n * 30:
            tries += 1
            d = ds[rng.randrange(len(ds))]
            e = rng.randrange(15, 351)
            direction = rng.choice(("CE", "PE"))
            ref = spot[d]["c"][e - 1]
            if not np.isfinite(ref): continue
            strike = atm(ref); exp = exp_for(d)
            bars = opt_day(exp, strike, direction, d)
            if bars is None: continue
            r = replay(bars, e, tgt, stp)
            if r is None: continue
            tot += (r[1] - r[0]) * LOT - COST; got += 1
        totals.append(round(tot, 2))
    return {"mean": round(sum(totals) / len(totals), 2), "min": min(totals), "max": max(totals)}

def summarise(trades, sig_ends, tgt, stp, label):
    ds = days(); half = len(ds) // 2
    h1d = set(ds[:half])
    tot = round(sum(t["net_inr"] for t in trades), 2)
    h1 = round(sum(t["net_inr"] for t in trades if t["date"] in h1d), 2)
    h2 = round(tot - h1, 2)
    months = {}
    for t in trades: months[t["date"][:7]] = round(months.get(t["date"][:7], 0.0) + t["net_inr"], 2)
    top3 = sorted((t["net_inr"] for t in trades), reverse=True)[:3]
    lag_tr = []
    for t, se in zip(trades, sig_ends):
        lt = score_signal(t["date"], se, t["direction"], tgt, stp, lag=1)
        if lt is not None: lag_tr.append(lt)
    lag_tot = round(sum(t["net_inr"] for t in lag_tr), 2)
    rp = random_placebo(len(trades), tgt, stp) if trades else {"mean": 0.0, "min": 0.0, "max": 0.0}
    wins = sum(1 for t in trades if t["net_inr"] > 0)
    return {"label": label, "trades": len(trades), "total_inr": tot, "h1_inr": h1, "h2_inr": h2,
            "months": months, "win_rate": round(wins / len(trades), 4) if trades else 0.0,
            "expectancy_inr": round(tot / len(trades), 2) if trades else 0.0,
            "ex_top3_inr": round(tot - sum(top3), 2), "audit_violations": audit(trades, sig_ends),
            "lag_placebo_inr": lag_tot, "lag_placebo_n": len(lag_tr), "random_placebo": rp}

def write_trades(trades, path):
    cols = ["date","direction","strike","expiry","entry_bar","entry_premium","exit_bar","exit_premium","exit_reason","net_inr"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for t in trades: w.writerow({c: t[c] for c in cols})
    # independent re-sum
    back = list(csv.DictReader(open(path)))
    return round(sum(float(r["net_inr"]) for r in back), 2)
