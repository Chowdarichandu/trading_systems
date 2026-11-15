#!/usr/bin/env python3
"""Bank Scalp Engine — CHARTER v2 runner.
Variants: fixed-target ladder (spec ('F', tgt, stp)) and trailing
(spec ('T', act, trail, stp)). Flat-only re-entry, cap 8/day/mechanism.
Full controls per variant incl. day-level stats. Genuine 1-min data only."""
import sys, json, csv, random
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_core as C

CAP = 8

# ---------------- exit replay with spec ----------------
def replay_spec(bars, e, spec):
    o, h, l = bars["o"], bars["h"], bars["l"]
    if e < 0 or e + 5 > C.NB - 1: return None
    entry = o[e]
    if not np.isfinite(entry): return None
    if spec[0] == "F":
        _, tgt, stp = spec
        for b in range(e, e + 5):
            lo, hi = l[b], h[b]
            if not (np.isfinite(lo) and np.isfinite(hi)): return None
            if lo <= entry - stp: return (entry, entry - stp, b, "stop")
            if hi >= entry + tgt: return (entry, entry + tgt, b, "target")
        xp = o[e + 5]
        return (entry, xp, e + 5, "time") if np.isfinite(xp) else None
    else:  # trailing: ('T', act, trail, stp)
        _, act, trail, stp = spec
        stop_cur = entry - stp; peak = None; activated = False
        for b in range(e, e + 5):
            lo, hi = l[b], h[b]
            if not (np.isfinite(lo) and np.isfinite(hi)): return None
            if lo <= stop_cur:
                return (entry, stop_cur, b, "trail_stop" if activated else "stop")
            peak = hi if peak is None else max(peak, hi)
            if peak >= entry + act:
                activated = True
                stop_cur = max(stop_cur, peak - trail)
        xp = o[e + 5]
        return (entry, xp, e + 5, "time") if np.isfinite(xp) else None

def score(day, sig_end, direction, spec, lag=0):
    spot = C.load_spot()[day]
    e = sig_end + lag
    if e - 1 < 0 or e + 5 > C.NB - 1: return None
    ref = spot["c"][e - 1]
    if not np.isfinite(ref): return None
    strike = C.atm(ref); exp = C.exp_for(day)
    bars = C.opt_day(exp, strike, direction, day)
    if bars is None: return None
    r = replay_spec(bars, e, spec)
    if r is None: return None
    entry, xp, xb, reason = r
    return {"date": day, "direction": direction, "strike": strike, "expiry": exp,
            "entry_bar": e, "entry_premium": round(entry, 2), "exit_bar": xb,
            "exit_premium": round(xp, 2), "exit_reason": reason,
            "net_inr": round((xp - entry) * C.LOT - C.COST, 2)}

# ---------------- signal generators ----------------
def or_signals_1m(day, spot):
    h, l, c = spot["h"], spot["l"], spot["c"]
    orh, orl = np.nanmax(h[:15]), np.nanmin(l[:15])
    out = []
    for i in range(15, 256):
        if not (np.isfinite(c[i]) and np.isfinite(c[i-1])): continue
        if c[i] > orh and c[i-1] <= orh: out.append((i + 1, "CE"))
        elif c[i] < orl and c[i-1] >= orl: out.append((i + 1, "PE"))
    return out  # (sig_end, direction)

def agg3(spot):
    o, h, l, c = spot["o"], spot["h"], spot["l"], spot["c"]
    bars = []
    for k in range(125):
        idx = range(3*k, 3*k + 3)
        bars.append((o[3*k], np.nanmax([h[j] for j in idx]), np.nanmin([l[j] for j in idx]), c[3*k + 2]))
    return bars

def or_signals_3m(day, spot):
    bars = agg3(spot)
    orh = max(b[1] for b in bars[:5]); orl = min(b[2] for b in bars[:5])
    out = []
    for k in range(5, 86):  # 3-min bars starting 09:30 .. 13:30
        pc, cc = bars[k-1][3], bars[k][3]
        if not (np.isfinite(pc) and np.isfinite(cc)): continue
        if cc > orh and pc <= orh: out.append((3*k + 3, "CE"))
        elif cc < orl and pc >= orl: out.append((3*k + 3, "PE"))
    return out

_LEVELS = None
def levels_for(day):
    """PDH/PDL/PDC from prior day + Red bands/ledges where they exist (>=2026-07-02)."""
    global _LEVELS
    ds = C.days(); spot = C.load_spot()
    i = ds.index(day)
    lv = []
    if i > 0:
        prev = spot[ds[i-1]]
        lv += [("PDH", float(np.nanmax(prev["h"])), "R"),
               ("PDL", float(np.nanmin(prev["l"])), "S"),
               ("PDC", float(prev["c"][374]), "B")]
    if _LEVELS is None:
        try:
            _LEVELS = json.load(open("/home/hatch/workspace/trading/data/banknifty-2026-jul-oct/red_bands_v2.json"))["per_date"]
        except Exception:
            _LEVELS = {}
    for b in _LEVELS.get(day, {}).get("master_bands", []) + _LEVELS.get(day, {}).get("tactical_ledges", []):
        lv.append((f"BAND{b['low']:.0f}-{b['high']:.0f}", float(b["high"]), "R"))
        lv.append((f"BAND{b['low']:.0f}-{b['high']:.0f}", float(b["low"]), "S"))
    return lv

def _reject(direction_side, hi, lo, cc, pc, L):
    if direction_side == "R":  # resistance -> PE
        return hi > L and pc <= L and cc <= L + (hi - L) / 2
    return lo < L and pc >= L and cc >= L - (L - lo) / 2

def lr_signals_1m(day, spot):
    c = spot["c"]; out = []; last = {}
    for i in range(20, 341):
        pc = c[i-1]
        if not np.isfinite(pc) or not np.isfinite(c[i]): continue
        for name, L, side in levels_for(day):
            if name in last and i - last[name] < 60: continue
            if _reject(side, spot["h"][i], spot["l"][i], c[i], pc, L):
                out.append((i + 1, "PE" if side == "R" else "CE")); last[name] = i
    return out

def lr_signals_3m(day, spot):
    bars = agg3(spot); out = []; last = {}
    for k in range(7, 114):  # 3-min bars starting 09:36..14:57
        pc, cc = bars[k-1][3], bars[k][3]
        if not (np.isfinite(pc) and np.isfinite(cc)): continue
        for name, L, side in levels_for(day):
            if name in last and (3*k) - last[name] < 60: continue
            if _reject(side, bars[k][1], bars[k][2], cc, pc, L):
                out.append((3*k + 3, "PE" if side == "R" else "CE")); last[name] = 3*k
    return out

# ---------------- variant runner + controls ----------------
def run_variant(label, sigfn, spec):
    spot = C.load_spot(); trades, sig_ends, nc, busy = [], [], 0, 0
    for day in C.days():
        taken, busy_until = 0, -1
        for sig_end, direction in sigfn(day, spot[day]):
            if taken >= CAP: break
            if sig_end <= busy_until: busy += 1; continue
            t = score(day, sig_end, direction, spec)
            if t is None: nc += 1; continue
            t["mech"] = label; trades.append(t); sig_ends.append(sig_end)
            taken += 1; busy_until = t["exit_bar"]
    path = f"/home/hatch/workspace/trading/bank_scalp_engine_{label}_trades.csv"
    resum = C.write_trades(trades, path)
    s = summarise_charter(trades, sig_ends, spec, label)
    s.update({"not_computed": nc, "busy_skips": busy, "resum_inr": resum,
              "resum_match": bool(abs(resum - s["total_inr"]) < 0.01)})
    return s

def summarise_charter(trades, sig_ends, spec, label):
    ds = C.days(); half = len(ds) // 2; h1d = set(ds[:half])
    tot = round(sum(t["net_inr"] for t in trades), 2)
    h1 = round(sum(t["net_inr"] for t in trades if t["date"] in h1d), 2)
    months = {}
    for t in trades: months[t["date"][:7]] = round(months.get(t["date"][:7], 0.0) + t["net_inr"], 2)
    daynet = {}
    for t in trades: daynet[t["date"]] = daynet.get(t["date"], 0.0) + t["net_inr"]
    dv = sorted(daynet.values())
    days_green = round(sum(1 for v in dv if v > 0) / len(dv), 4) if dv else 0.0
    lag_tr = []
    for t, se in zip(trades, sig_ends):
        lt = score(t["date"], se, t["direction"], spec, lag=1)
        if lt is not None: lag_tr.append(lt)
    rp = random_placebo_spec(len(trades), spec) if trades else {"mean": 0.0, "min": 0.0, "max": 0.0}
    wins = sum(1 for t in trades if t["net_inr"] > 0)
    top3 = sorted((t["net_inr"] for t in trades), reverse=True)[:3]
    audit_v = sum(1 for t, se in zip(trades, sig_ends)
                  if t["entry_bar"] != se or not (0 <= t["exit_bar"] - t["entry_bar"] <= 5))
    return {"label": label, "trades": len(trades), "total_inr": tot, "h1_inr": h1,
            "h2_inr": round(tot - h1, 2), "months": months,
            "win_rate": round(wins / len(trades), 4) if trades else 0.0,
            "expectancy_inr": round(tot / len(trades), 2) if trades else 0.0,
            "gross_inr": round(tot + len(trades) * C.COST, 2),
            "ex_top3_inr": round(tot - sum(top3), 2), "audit_violations": audit_v,
            "lag_placebo_inr": round(sum(t["net_inr"] for t in lag_tr), 2),
            "random_placebo": rp,
            "days_traded": len(dv), "days_green_pct": days_green,
            "median_day_inr": round(float(np.median(dv)), 2) if dv else 0.0,
            "worst_day_inr": round(min(dv), 2) if dv else 0.0,
            "best_day_inr": round(max(dv), 2) if dv else 0.0}

def random_placebo_spec(n, spec, seed=42, draws=20):
    rng = random.Random(seed); ds = C.days(); spot = C.load_spot()
    totals = []
    for _ in range(draws):
        tot = 0.0; got = 0; tries = 0
        while got < n and tries < n * 30:
            tries += 1
            d = ds[rng.randrange(len(ds))]; e = rng.randrange(15, 351)
            direction = rng.choice(("CE", "PE"))
            ref = spot[d]["c"][e - 1]
            if not np.isfinite(ref): continue
            bars = C.opt_day(C.exp_for(d), C.atm(ref), direction, d)
            if bars is None: continue
            r = replay_spec(bars, e, spec)
            if r is None: continue
            tot += (r[1] - r[0]) * C.LOT - C.COST; got += 1
        totals.append(round(tot, 2))
    return {"mean": round(sum(totals) / len(totals), 2), "min": min(totals), "max": max(totals)}
