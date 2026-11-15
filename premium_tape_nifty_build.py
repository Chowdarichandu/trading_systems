#!/usr/bin/env python3
"""PREMIUM-TAPE — NIFTY (spec: premium_tape_nifty_SPEC.md, frozen before scoring).
Signals off the option premium's own chart. Research only; reads persisted stores;
writes premium_tape_nifty_results.json + premium_tape_nifty_trades.csv.
"""
import json, re, random
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd

TR = Path.home() / "workspace" / "trading"
OI = TR / "oi_buildup_data"
LOT, COST = 65, 220.0
random.seed(20261114)
np.random.seed(20261114)

BAR_TIMES = [f"{9 + (15 + 5 * i) // 60:02d}:{(15 + 5 * i) % 60:02d}" for i in range(75)]  # 09:15..15:25
def ti(t): return BAR_TIMES.index(t)
I_OR_END = ti("09:40")      # OR = bars 09:15..09:40
I_SIG0 = ti("09:45")        # first signal bar
I_SIG1 = ti("15:10")        # last signal bar
I_ENTRY_MAX = ti("15:15")   # last entry bar
I_SQ = ti("15:20")          # square-off bar (open)

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
    """Premium series + trailing indicators for one contract on one day."""
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
        # Wilder RSI(14) within the day
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
        self.mom3 = np.full(n, np.nan)
        if n > 3: self.mom3[3:] = self.c[3:] - self.c[:-3]

    def events(self):
        """All P1/P2 first triggers for this contract. Times are global bar indices 0..74
        (availability guarantees bars 0..73; series may extend to 74)."""
        out = []
        n = len(self.c)
        p1 = None
        for i in range(I_SIG0, I_SIG1 + 1):
            if i >= n: break
            if self.c[i] > self.or_high and self.c[i] > self.vwap[i]:
                p1 = (i, (self.c[i] - self.or_high) / self.or_high if self.or_high else 0.0)
                break
        if p1: out.append(("P1", p1[0], p1[1]))
        p2 = None
        for i in range(max(I_SIG0, 14), I_SIG1 + 1):
            if i >= n: break
            if np.isnan(self.rsi[i]) or np.isnan(self.rsi[i - 1]) or np.isnan(self.mom3[i]): continue
            if self.c[i] > self.vwap[i] and self.mom3[i] > 0 and self.rsi[i - 1] <= 50 < self.rsi[i]:
                p2 = (i, self.mom3[i] / self.c[i] if self.c[i] else 0.0)
                break
        if p2: out.append(("P2", p2[0], p2[1]))
        return out

def simulate(cd: ContractDay, entry_i, exit_kind):
    ep = float(cd.o[entry_i])
    if exit_kind == "X1":
        stop, tgt = ep - 50.0, ep + 90.0
        for j in range(entry_i, I_ENTRY_MAX + 1):
            if cd.l[j] <= stop: return ep, stop, "stop"
            if cd.h[j] >= tgt: return ep, tgt, "target"
        return ep, float(cd.o[I_SQ]), "sq1520"
    else:  # X2
        stop = ep - 60.0
        for j in range(entry_i, I_ENTRY_MAX + 1):
            if cd.l[j] <= stop: return ep, stop, "hardstop"
            if cd.c[j] < cd.vwap[j]: return ep, float(cd.c[j]), "vwap_exit"
        return ep, float(cd.o[I_SQ]), "sq1520"

BOOKS = ("P1", "P2", "COMB")
EXITS = ("X1", "X2")

def run_window(d0, d1):
    days = sorted(d for d in spot_by_day if d0 <= d <= d1)
    trades, nc, skipped = [], {}, 0
    day_side_avail = {}   # (day_s, side) -> ContractDay, for the placebo
    for day in days:
        ds = day.isoformat()
        sday = spot_by_day[day]
        if "09:15" not in sday:
            skipped += 1
            continue
        strike = int(round(sday["09:15"] / 50.0) * 50)
        exp = weekly_expiry(day)
        events = []  # (bar_i, rule_prio, -size, side_order, side, rule)
        for s_order, side in enumerate(("CE", "PE")):
            bars = contract_bars(ds, strike, side, exp)
            if bars is None:
                nc["nc_no_file"] = nc.get("nc_no_file", 0) + 1
                continue
            if not available(bars):
                nc["nc_partial"] = nc.get("nc_partial", 0) + 1
                continue
            cd = ContractDay(bars)
            day_side_avail[(ds, side)] = cd
            if cd.vwap_proxy:
                nc["vwap_proxy_dayside"] = nc.get("vwap_proxy_dayside", 0) + 1
            for rule, bi, size in cd.events():
                events.append((bi, 0 if rule == "P1" else 1, -size, s_order, side, rule, cd))
        if not events:
            continue
        p1_ev = min((e for e in events if e[5] == "P1"), key=lambda e: (e[0], e[2], e[3]), default=None)
        p2_ev = min((e for e in events if e[5] == "P2"), key=lambda e: (e[0], e[2], e[3]), default=None)
        comb_ev = min(events, key=lambda e: (e[0], e[1], e[2], e[3]))
        chosen = {"P1": p1_ev, "P2": p2_ev, "COMB": comb_ev}
        for book, ev in chosen.items():
            if ev is None: continue
            bi, _prio, _ns, _so, side, rule, cd = ev
            entry_i = bi + 1
            for xk in EXITS:
                ep, xp, reason = simulate(cd, entry_i, xk)
                trades.append({
                    "book": book, "exit": xk, "rule": rule, "date": ds,
                    "signal_time": BAR_TIMES[bi], "entry_time": BAR_TIMES[entry_i],
                    "side": side, "strike": strike, "expiry": exp,
                    "entry": ep, "exit_price": xp, "exit_reason": reason,
                    "net": round((xp - ep) * LOT - COST, 2),
                    "_signal_idx": bi, "_entry_idx": entry_i,
                })
    return days, trades, nc, skipped, day_side_avail

def metrics(trades):
    if not trades:
        return {"trades": 0, "total": 0.0, "wr": 0.0, "trade_days": 0, "rs_per_td": 0.0}
    tot = sum(t["net"] for t in trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    tdays = len({t["date"] for t in trades})
    return {"trades": len(trades), "total": round(tot, 2), "wr": round(100 * wins / len(trades), 1),
            "trade_days": tdays, "rs_per_td": round(tot / tdays, 2) if tdays else 0.0}

def book_tables(trades):
    out = {}
    for book in BOOKS:
        for xk in EXITS:
            sel = [t for t in trades if t["book"] == book and t["exit"] == xk]
            out[f"{book}-{xk}"] = {
                "jan_jun": metrics([t for t in sel if t["date"] <= "2026-06-30"]),
                "jul_oct": metrics([t for t in sel if t["date"] >= "2026-07-01"]),
                "full": metrics(sel),
            }
    return out

# ---------------------------------------------------------------- gate run
g_days, g_trades, g_nc, g_skip, avail = run_window(date(2026, 1, 1), date(2026, 10, 31))
tables = book_tables(g_trades)

# best full-year book (by total)
best_key = max(tables, key=lambda k: tables[k]["full"]["total"])
best_book, best_exit = best_key.split("-")
best_trades = [t for t in g_trades if t["book"] == best_book and t["exit"] == best_exit]

# timing audit: entry = signal + 1 bar & stored open; independent VWAP/RSI recompute at sampled signals
audit = {"entry_alignment_ok": True, "recompute_checked": 0, "recompute_ok": True, "max_vwap_diff": 0.0, "max_rsi_diff": 0.0}
for t in g_trades:
    if t["_entry_idx"] != t["_signal_idx"] + 1:
        audit["entry_alignment_ok"] = False
sample = best_trades[:25] if best_trades else g_trades[:25]
for t in sample:
    ds, side, bi = t["date"], t["side"], t["_signal_idx"]
    fn = OI / f"candles_NIFTY_{t['strike']}{side}_{t['expiry']}_{ds}.json"
    raw = sorted(json.load(open(fn))["data"]["candles"], key=lambda r: r[0])
    rows = [r for r in raw if r[0][11:16] <= BAR_TIMES[bi]]
    # raw candle layout: [ts, open, high, low, close, volume, oi]
    tpv = [((r[2] + r[3] + r[4]) / 3.0) * r[5] for r in rows]
    vv = [r[5] for r in rows]
    vwap2 = sum(tpv) / sum(vv) if sum(vv) > 0 else sum((r[2] + r[3] + r[4]) / 3.0 for r in rows) / len(rows)
    closes = [r[4] for r in rows]
    g = l_ = 0.0
    for x in range(1, 15):
        d = closes[x] - closes[x - 1]; g += max(d, 0); l_ += max(-d, 0)
    g /= 14; l_ /= 14
    for x in range(15, len(closes)):
        d = closes[x] - closes[x - 1]
        g = (g * 13 + max(d, 0)) / 14; l_ = (l_ * 13 + max(-d, 0)) / 14
    rsi2 = 100.0 if l_ == 0 else 100 - 100 / (1 + g / l_)
    cd = avail.get((ds, side))
    if cd is None: continue
    audit["max_vwap_diff"] = max(audit["max_vwap_diff"], abs(float(cd.vwap[bi]) - vwap2))
    if not np.isnan(cd.rsi[bi]):
        audit["max_rsi_diff"] = max(audit["max_rsi_diff"], abs(float(cd.rsi[bi]) - rsi2))
    audit["recompute_checked"] += 1
audit["recompute_ok"] = audit["max_vwap_diff"] < 0.01 and audit["max_rsi_diff"] < 0.6

# random-entry placebo on the best book
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
n_days, n_trades, n_nc, n_skip, _na = run_window(date(2026, 11, 2), date(2026, 11, 13))
nov = {"days": len(n_days), "nc": n_nc, "skipped_no_spot0915": n_skip, "tables": book_tables(n_trades)}

results = {
    "book": "PREMIUM-TAPE NIFTY", "basis": "paper, buying only, 1 lot (65), Rs220/trade",
    "gate_days": len(g_days), "gate_nc": g_nc, "gate_skipped_no_spot0915": g_skip,
    "tables": tables, "best_full_year": best_key,
    "timing_audit": audit, "placebo": placebo,
    "november_cf": nov,
    "trades": [{k: v for k, v in t.items() if not k.startswith("_")} for t in g_trades],
    "november_trades": [{k: v for k, v in t.items() if not k.startswith("_")} for t in n_trades],
}
json.dump(results, open(TR / "premium_tape_nifty_results.json", "w"), indent=1)
pd.DataFrame(results["trades"]).to_csv(TR / "premium_tape_nifty_trades.csv", index=False)
print(json.dumps({"gate_days": len(g_days), "gate_nc": g_nc, "skipped": g_skip,
                  "tables": tables, "best": best_key, "audit": audit, "placebo": placebo,
                  "november": {k: nov[k] for k in ("days", "nc")},
                  "nov_tables": nov["tables"]}, indent=1))
