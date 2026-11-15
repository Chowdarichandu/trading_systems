#!/usr/bin/env python3
"""PREMIUM-TAPE NIFTY ROUND 3 — THE FADE TURN (spec: premium_tape_nifty_r3_SPEC.md).
Data/contract/indicator machinery copied from premium_tape_nifty_build.py (Round 1)
and premium_tape_nifty_r2_build.py (Round 2). Control first: P1-X1 must reproduce
168 trades / -Rs75,995.75 exactly, else abort before scoring the turn.
Research only; writes premium_tape_nifty_r3_results.json + premium_tape_nifty_r3_trades.csv.
"""
import json, re, random, sys
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd

TR = Path.home() / "workspace" / "trading"
OI = TR / "oi_buildup_data"
LOT, COST = 65, 220.0
random.seed(20261114)
np.random.seed(20261114)

BAR_TIMES = [f"{9 + (15 + 5 * i) // 60:02d}:{(15 + 5 * i) % 60:02d}" for i in range(75)]
def ti(t): return BAR_TIMES.index(t)
I_OR_END = ti("09:40")
I_SIG0 = ti("09:45")
I_SIG1 = ti("15:10")
I_ENTRY_MAX = ti("15:15")
I_SQ = ti("15:20")
I_SPIKE_MAX = ti("14:30")   # last spike bar (entry by 14:35)

# ---------------------------------------------------------------- spot (strike selection only)
spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv", parse_dates=["timestamp"])
spot = spot.sort_values("timestamp").reset_index(drop=True)
spot["date"] = spot["timestamp"].dt.date
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
spot_by_day = {}
for d, g in spot.groupby("date"):
    spot_by_day[d] = dict(zip(g["time"], g["close"]))

# ---------------------------------------------------------------- premium store
expiry_cal = sorted({re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name).group(1)
                     for fn in OI.glob("candles_NIFTY_*.json")
                     if re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name)})
def weekly_expiry(day):
    ds = day.isoformat()
    return next((e for e in expiry_cal if e >= ds), None)

_cache = {}
def contract_bars(day_s, strike, typ, exp):
    key = (day_s, strike, typ, exp)
    if key in _cache: return _cache[key]
    fn = OI / f"candles_NIFTY_{strike}{typ}_{exp}_{day_s}.json"
    out = None
    if fn.exists():
        raw = json.load(open(fn))["data"]["candles"]
        out = {}
        for ts, o_, h_, l_, c_, v_, oi_ in raw:
            out[ts[11:16]] = (float(o_), float(h_), float(l_), float(c_), float(v_))
    _cache[key] = out
    return out

def available(bars):
    return bars is not None and all(BAR_TIMES[j] in bars for j in range(0, I_SQ + 1))

class ContractDay:
    def __init__(self, bars):
        idx = [j for j in range(75) if BAR_TIMES[j] in bars]
        self.o = np.array([bars[BAR_TIMES[j]][0] for j in idx])
        self.h = np.array([bars[BAR_TIMES[j]][1] for j in idx])
        self.l = np.array([bars[BAR_TIMES[j]][2] for j in idx])
        self.c = np.array([bars[BAR_TIMES[j]][3] for j in idx])
        self.v = np.array([bars[BAR_TIMES[j]][4] for j in idx])
        self.times = [BAR_TIMES[j] for j in idx]
        tp = (self.h + self.l + self.c) / 3.0
        if self.v.sum() > 0:
            self.vwap = np.cumsum(tp * self.v) / np.cumsum(self.v)
            self.vwap_proxy = False
        else:
            self.vwap = np.cumsum(tp) / np.arange(1, len(tp) + 1)
            self.vwap_proxy = True
        self.or_high = float(self.h[:I_OR_END + 1].max())
        self.or_low = float(self.l[:I_OR_END + 1].min())
        # Wilder RSI(14) within the day (identical to Round 1)
        n = len(self.c)
        self.rsi = np.full(n, np.nan)
        if n > 14:
            d = np.diff(self.c)
            gains = np.where(d > 0, d, 0.0); losses = np.where(d < 0, -d, 0.0)
            ag = gains[:14].mean(); al = losses[:14].mean()
            self.rsi[14] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
            for i in range(15, n):
                ag = (ag * 13 + gains[i - 1]) / 14
                al = (al * 13 + losses[i - 1]) / 14
                self.rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

    def p1_event(self):
        """Round-1 P1 first trigger (control): first bar close > OR high AND close > VWAP."""
        n = len(self.c)
        for i in range(I_SIG0, I_SIG1 + 1):
            if i >= n: break
            if self.c[i] > self.or_high and self.c[i] > self.vwap[i]:
                size = (self.c[i] - self.or_high) / self.or_high if self.or_high else 0.0
                return i, size
        return None

    def spike(self):
        """P-FADE spike: first bar 09:45..14:30 with close > OR high AND premium RSI(14) >= 70."""
        n = len(self.c)
        for i in range(I_SIG0, I_SPIKE_MAX + 1):
            if i >= n: break
            if np.isnan(self.rsi[i]):
                continue
            if self.c[i] > self.or_high and self.rsi[i] >= 70.0:
                size = (self.c[i] - self.or_high) / self.or_high if self.or_high else 0.0
                return i, size, float(self.rsi[i])
        return None

def simulate(cd, entry_i, exit_kind):
    ep = float(cd.o[entry_i])
    if exit_kind == "X1":
        stop, tgt = ep - 50.0, ep + 90.0
        for j in range(entry_i, I_ENTRY_MAX + 1):
            if cd.l[j] <= stop: return ep, stop, "stop"
            if cd.h[j] >= tgt: return ep, tgt, "target"
        return ep, float(cd.o[I_SQ]), "sq1520"
    else:
        stop = ep - 60.0
        for j in range(entry_i, I_ENTRY_MAX + 1):
            if cd.l[j] <= stop: return ep, stop, "hardstop"
            if cd.c[j] < cd.vwap[j]: return ep, float(cd.c[j]), "vwap_exit"
        return ep, float(cd.o[I_SQ]), "sq1520"

def metrics(trades):
    if not trades:
        return {"trades": 0, "total": 0.0, "wr": 0.0, "trade_days": 0, "rs_per_td": 0.0}
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    tdays = len({t["date"] for t in trades})
    return {"trades": len(trades), "total": round(tot, 2), "wr": round(100 * wins / len(trades), 1),
            "trade_days": tdays, "rs_per_td": round(tot / tdays, 2) if tdays else 0.0}

OPP = {"CE": "PE", "PE": "CE"}

def run_window(d0, d1):
    days = sorted(d for d in spot_by_day if d0 <= d <= d1)
    ctrl_trades, fade_trades, nc, skipped = [], [], {}, 0
    stats = {"contract_day_spikes": 0, "spike_days": 0, "trades_taken": 0,
             "spike_blocked_opposite_nc": 0}
    day_side_avail = {}
    for day in days:
        ds = day.isoformat()
        sday = spot_by_day[day]
        if "09:15" not in sday:
            skipped += 1
            continue
        strike = int(round(sday["09:15"] / 50.0) * 50)
        exp = weekly_expiry(day)
        cds = {}
        p1_events = []   # (bar_i, -size, side_order, side, cd)
        spikes = []      # (bar_i, -size, side_order, spike_side, cd, rsi)
        for s_order, side in enumerate(("CE", "PE")):
            bars = contract_bars(ds, strike, side, exp)
            if bars is None:
                nc["nc_no_file"] = nc.get("nc_no_file", 0) + 1
                continue
            if not available(bars):
                nc["nc_partial"] = nc.get("nc_partial", 0) + 1
                continue
            cd = ContractDay(bars)
            cds[side] = cd
            day_side_avail[(ds, side)] = cd
            if cd.vwap_proxy:
                nc["vwap_proxy_dayside"] = nc.get("vwap_proxy_dayside", 0) + 1
            p1 = cd.p1_event()
            if p1 is not None:
                p1_events.append((p1[0], -p1[1], s_order, side, cd))
            sp = cd.spike()
            if sp is not None:
                stats["contract_day_spikes"] += 1
                spikes.append((sp[0], -sp[1], s_order, side, cd, sp[2]))
        # CONTROL: Round-1 P1 book, X1 only
        if p1_events:
            bi, _ns, _so, side, cd = min(p1_events, key=lambda e: (e[0], e[1], e[2]))
            ep, xp, reason = simulate(cd, bi + 1, "X1")
            ctrl_trades.append({"date": ds, "side": side, "strike": strike, "expiry": exp,
                                "signal_time": BAR_TIMES[bi], "entry_time": BAR_TIMES[bi + 1],
                                "entry": ep, "exit_price": xp, "exit_reason": reason,
                                "net": round((xp - ep) * LOT - COST, 2)})
        # P-FADE day trade: first spike across contracts -> buy the opposite contract
        if spikes:
            stats["spike_days"] += 1
            si, _ns, _so, spike_side, _scd, srsi = min(spikes, key=lambda e: (e[0], e[1], e[2]))
            bought_side = OPP[spike_side]
            bcd = cds.get(bought_side)
            if bcd is None:
                stats["spike_blocked_opposite_nc"] += 1
            else:
                stats["trades_taken"] += 1
                for xk in ("X1", "X2"):
                    ep, xp, reason = simulate(bcd, si + 1, xk)
                    fade_trades.append({"exit": xk, "date": ds, "spike_side": spike_side,
                                        "bought_side": bought_side, "strike": strike,
                                        "expiry": exp, "spike_time": BAR_TIMES[si],
                                        "entry_time": BAR_TIMES[si + 1],
                                        "spike_rsi": round(srsi, 2),
                                        "entry": ep, "exit_price": xp, "exit_reason": reason,
                                        "net": round((xp - ep) * LOT - COST, 2),
                                        "_spike_idx": si, "_entry_idx": si + 1})
    return days, ctrl_trades, fade_trades, nc, skipped, stats, day_side_avail

# ---------------------------------------------------------------- gate run
g_days, g_ctrl, g_fade, g_nc, g_skip, g_stats, avail = run_window(date(2026, 1, 1), date(2026, 10, 31))
ctrl_full = metrics(g_ctrl)
print("CONTROL P1-X1:", ctrl_full)
if not (ctrl_full["trades"] == 168 and abs(ctrl_full["total"] - (-75995.75)) < 0.01):
    print("CONTROL MISMATCH — aborting before scoring the turn.")
    sys.exit(1)
print("CONTROL OK — P1-X1 reproduced exactly (168 trades, -Rs75,995.75).")

def fade_tables(trades):
    out = {}
    for xk in ("X1", "X2"):
        sel = [t for t in trades if t["exit"] == xk]
        out[f"P-FADE-{xk}"] = {
            "jan_jun": metrics([t for t in sel if t["date"] <= "2026-06-30"]),
            "jul_oct": metrics([t for t in sel if t["date"] >= "2026-07-01"]),
            "full": metrics(sel),
        }
    return out

tables = fade_tables(g_fade)
best_key = max(tables, key=lambda k: tables[k]["full"]["total"])
best_exit = best_key.split("-")[-1]
best_trades = [t for t in g_fade if t["exit"] == best_exit]

# timing audit: entry = spike bar + 1 & stored open of the BOUGHT contract;
# independent VWAP/RSI recompute at sampled spike bars on the SPIKING contract
audit = {"entry_alignment_ok": True, "entry_price_ok": True, "recompute_checked": 0,
         "recompute_ok": True, "max_vwap_diff": 0.0, "max_rsi_diff": 0.0}
for t in g_fade:
    if t["_entry_idx"] != t["_spike_idx"] + 1:
        audit["entry_alignment_ok"] = False
for t in best_trades[:25]:
    ds = t["date"]
    # entry price check on the bought contract from the raw file
    fnb = OI / f"candles_NIFTY_{t['strike']}{t['bought_side']}_{t['expiry']}_{ds}.json"
    rawb = {r[0][11:16]: r for r in json.load(open(fnb))["data"]["candles"]}
    if abs(float(rawb[t["entry_time"]][1]) - t["entry"]) > 1e-9:
        audit["entry_price_ok"] = False
    # VWAP + RSI recompute on the spiking contract up to the spike bar
    bi = t["_spike_idx"]
    fns = OI / f"candles_NIFTY_{t['strike']}{t['spike_side']}_{t['expiry']}_{ds}.json"
    raw = sorted(json.load(open(fns))["data"]["candles"], key=lambda r: r[0])
    rows = [r for r in raw if r[0][11:16] <= BAR_TIMES[bi]]
    tpv = [((r[2] + r[3] + r[4]) / 3.0) * r[5] for r in rows]
    vv = [r[5] for r in rows]
    vwap2 = sum(tpv) / sum(vv) if sum(vv) > 0 else sum((r[2] + r[3] + r[4]) / 3.0 for r in rows) / len(rows)
    closes = [r[4] for r in rows]
    g_ = l_ = 0.0
    for x in range(1, 15):
        d = closes[x] - closes[x - 1]; g_ += max(d, 0); l_ += max(-d, 0)
    g_ /= 14; l_ /= 14
    for x in range(15, len(closes)):
        d = closes[x] - closes[x - 1]
        g_ = (g_ * 13 + max(d, 0)) / 14; l_ = (l_ * 13 + max(-d, 0)) / 14
    rsi2 = 100.0 if l_ == 0 else 100 - 100 / (1 + g_ / l_)
    cd = avail.get((ds, t["spike_side"]))
    if cd is None: continue
    audit["max_vwap_diff"] = max(audit["max_vwap_diff"], abs(float(cd.vwap[bi]) - vwap2))
    if not np.isnan(cd.rsi[bi]):
        audit["max_rsi_diff"] = max(audit["max_rsi_diff"], abs(float(cd.rsi[bi]) - rsi2))
    audit["recompute_checked"] += 1
audit["recompute_ok"] = audit["max_vwap_diff"] < 0.01 and audit["max_rsi_diff"] < 0.6

# random-entry placebo on the best exit row (random day, randomly chosen one of its contracts)
avail_list = list(avail.values())
cnt = len(best_trades)
draws = []
for _ in range(1000):
    tot = 0.0
    for _ in range(cnt):
        cd = avail_list[random.randrange(len(avail_list))]
        ei = random.randrange(1, I_ENTRY_MAX + 1)
        ep, xp, _r = simulate(cd, ei, best_exit)
        tot += (xp - ep) * LOT - COST
    draws.append(round(tot, 2))
real_tot = tables[best_key]["full"]["total"]
pct = sum(1 for v in draws if v <= real_tot) / len(draws) if cnt else 0.0
placebo = {"book": best_key, "iterations": 1000, "trades_per_draw": cnt,
           "percentile": round(pct, 4), "mean_total": round(float(np.mean(draws)), 2),
           "p95_total": round(float(np.percentile(draws, 95)), 2)}

# ---------------------------------------------------------------- November CF
n_days, _nc_ctrl, n_fade, n_nc, n_skip, n_stats, _na = run_window(date(2026, 11, 2), date(2026, 11, 13))
nov = {"days": len(n_days), "nc": n_nc, "skipped_no_spot0915": n_skip,
       "spike_stats": n_stats, "tables": fade_tables(n_fade)}

results = {
    "book": "PREMIUM-TAPE NIFTY R3 (P-FADE)",
    "basis": "paper, buying only, 1 lot (65), Rs220/trade",
    "control_p1_x1_full": ctrl_full,
    "gate_days": len(g_days), "gate_nc": g_nc, "gate_skipped_no_spot0915": g_skip,
    "spike_stats_gate": g_stats,
    "tables": tables, "best_full_year": best_key,
    "timing_audit": audit, "placebo": placebo,
    "november_cf": nov,
    "trades": [{k: v for k, v in t.items() if not k.startswith("_")} for t in g_fade],
    "november_trades": [{k: v for k, v in t.items() if not k.startswith("_")} for t in n_fade],
}
json.dump(results, open(TR / "premium_tape_nifty_r3_results.json", "w"), indent=1)
pd.DataFrame([{k: v for k, v in t.items() if not k.startswith("_")} for t in g_fade]).to_csv(
    TR / "premium_tape_nifty_r3_trades.csv", index=False)
print(json.dumps({"gate_days": len(g_days), "gate_nc": g_nc, "skipped": g_skip,
                  "spike_stats": g_stats, "tables": tables, "best": best_key,
                  "audit": audit, "placebo": placebo, "november": nov}, indent=1))
