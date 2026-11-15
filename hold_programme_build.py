#!/usr/bin/env python3
"""HOLD PROGRAMME — buy today, sell after a fixed number of days.
Spec: hold_programme_SPEC.md (frozen 2026-11-15 before scoring). Research only;
changes no book/ledger/job. Basis: equity cash, LONG only, frozen 25 names,
per 100 shares PROVISIONAL, Rs40 per completed position, paper only.
"""
import csv, json, os, sys
from collections import defaultdict
from datetime import date
import numpy as np

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import indicator_parameter_tuning_stocks_build as ATLAS

NAMES = ATLAS.NAMES
COST = ATLAS.COST  # 40.0
HOLDS = [3, 5, 10, 15, 20]
TRIGGERS = ["E0", "E1", "E2", "E3"]
YEARS = [2025, 2026]
SEED_PLACEBO = 20261115
N_DRAWS = 1000

# ---------------------------------------------------------------- data + signals
def prep(sym):
    dates, o, h, l, c = ATLAS.load_daily(sym)
    n = len(dates)
    mid, sdv = ATLAS.bollinger_bands(c, 20)
    lower = mid - 2 * sdv
    r14 = ATLAS.rsi_wilder(c, 14)

    e1 = np.zeros(n, dtype=bool)
    ok = ~np.isnan(r14)
    e1[1:] = ok[1:] & ok[:-1] & (r14[:-1] < 35.0) & (r14[1:] >= 35.0)

    e2 = np.zeros(n, dtype=bool)
    okl = ~np.isnan(lower)
    e2[1:] = okl[1:] & okl[:-1] & (c[:-1] < lower[:-1]) & (c[1:] >= lower[1:])

    e3 = np.zeros(n, dtype=bool)
    okm = ~np.isnan(mid)
    e3[1:] = okm[1:] & okm[:-1] & (c[:-1] <= mid[:-1]) & (c[1:] > mid[1:])

    # E0: index t is the first bar of its ISO week (in this stock's series)
    iso = [date.fromisoformat(d).isocalendar()[:2] for d in dates]
    first_week = np.zeros(n, dtype=bool)
    first_week[0] = True
    for i in range(1, n):
        first_week[i] = iso[i] != iso[i - 1]

    return dict(sym=sym, dates=dates, o=o, h=h, l=l, c=c, n=n,
                sig={"E1": e1, "E2": e2, "E3": e3}, first_week=first_week)

# ---------------------------------------------------------------- engine
def sim(d, trig, H):
    """One state machine over the full series. Returns true trades
    (exit at close of entry+H, or FORCED at the last close)."""
    dates, o, c, n = d["dates"], d["o"], d["c"], d["n"]
    trades = []
    pos = None  # entry index
    i = 0
    while i < n:
        if pos is None:
            if trig == "E0":
                if d["first_week"][i]:
                    pos = i  # enter at this bar's open
                    continue  # do not advance; exit check happens via loop below
                i += 1
                continue
            else:
                if d["sig"][trig][i] and i + 1 < n:
                    pos = i + 1
                    i = pos
                    continue
                i += 1
                continue
        # in position: exit at close of pos+H (or last close)
        xi = min(pos + H, n - 1)
        kind = "HOLD" if pos + H <= n - 1 else "FORCED"
        trades.append(dict(sym=d["sym"], entry_idx=pos, exit_idx=xi,
                           entry_date=dates[pos], exit_date=dates[xi],
                           entry=float(o[pos]), exit=float(c[xi]),
                           net=round((float(c[xi]) - float(o[pos])) * 100.0 - COST, 2),
                           pct=round((float(c[xi]) / float(o[pos]) - 1.0) * 100.0, 4),
                           hold=xi - pos, kind=kind))
        pos = None
        i = xi  # resume scanning at the exit day's close
        if trig == "E0":
            i = xi + 1  # E0 entries are week-open bars strictly after exit day
    return trades

# ---------------------------------------------------------------- scoring
def window_end_idx(dates, year):
    w = None
    for i, dt in enumerate(dates):
        if dt <= f"{year}-10-31":
            w = i
        else:
            break
    return w

def score_year(trades, d, year):
    """Select trades by entry date in the year window; re-mark exits past
    the window end at the window-end close (WMARK)."""
    w = window_end_idx(d["dates"], year)
    out = []
    for t in trades:
        if not (f"{year}-01-01" <= t["entry_date"] <= f"{year}-10-31"):
            continue
        t2 = dict(t)
        if t["exit_idx"] > w:
            xp = float(d["c"][w])
            t2.update(exit_idx=w, exit_date=d["dates"][w], exit=xp,
                      net=round((xp - t["entry"]) * 100.0 - COST, 2),
                      pct=round((xp / t["entry"] - 1.0) * 100.0, 4),
                      hold=w - t["entry_idx"], kind="WMARK")
        out.append(t2)
    return out

def stats(trades):
    if not trades:
        return dict(trades=0, net=0.0, wr=0.0, avg_pct=0.0, worst=0.0,
                    max_dd=0.0, wmark=0, forced=0)
    net = round(sum(t["net"] for t in trades), 2)
    wr = round(100.0 * sum(1 for t in trades if t["net"] > 0) / len(trades), 1)
    avg_pct = round(sum(t["pct"] for t in trades) / len(trades), 3)
    worst = min(t["net"] for t in trades)
    ordered = sorted(trades, key=lambda t: (t["exit_date"], t["entry_date"], t["sym"]))
    eq = 0.0; peak = 0.0; dd = 0.0
    for t in ordered:
        eq += t["net"]; peak = max(peak, eq); dd = min(dd, eq - peak)
    return dict(trades=len(trades), net=net, wr=wr, avg_pct=avg_pct,
                worst=round(worst, 2), max_dd=round(dd, 2),
                wmark=sum(1 for t in trades if t["kind"] == "WMARK"),
                forced=sum(1 for t in trades if t["kind"] == "FORCED"))

# ---------------------------------------------------------------- placebo
def placebo(data, cell_trades_by_sym, H):
    """cell_trades_by_sym: sym -> scored trade count (both windows combined)."""
    rng = np.random.default_rng(SEED_PLACEBO)
    real = None  # filled by caller
    draws = []
    for _ in range(N_DRAWS):
        tot = 0.0
        for sym, k in cell_trades_by_sym.items():
            if k == 0:
                continue
            d = data[sym]
            hi = d["n"] - 1 - H
            idx = rng.integers(0, hi + 1, size=k)
            for j in idx:
                tot += (float(d["c"][j + H]) - float(d["o"][j])) * 100.0 - COST
        draws.append(tot)
    return np.array(draws)

# ---------------------------------------------------------------- main
def main():
    data = {sym: prep(sym) for sym in NAMES}
    # sanity: BB signal count vs EKAM construction (same formula) — report only
    results = {"spec": "hold_programme_SPEC.md", "basis": "per 100 shares PROVISIONAL, Rs40/position",
               "cells": {}, "placebo": {}, "best_overall": None}
    all_trades = {}  # (trig,H) -> {sym: [true trades]}
    scored = {}      # (trig,H) -> {year: [scored trades]}
    for trig in TRIGGERS:
        for H in HOLDS:
            per_sym_true = {}
            per_year = {y: [] for y in YEARS}
            for sym in NAMES:
                tr = sim(data[sym], trig, H)
                per_sym_true[sym] = tr
                for y in YEARS:
                    per_year[y].extend(score_year(tr, data[sym], y))
            all_trades[(trig, H)] = per_sym_true
            scored[(trig, H)] = per_year
            cell = {}
            comb = 0.0
            for y in YEARS:
                s = stats(per_year[y])
                cell[str(y)] = s
                comb += s["net"]
            cell["combined_net"] = round(comb, 2)
            results["cells"][f"{trig}-H{H}"] = cell

    # best cell per trigger + placebo; best overall
    best_overall = None
    for trig in TRIGGERS:
        cands = [(H, results["cells"][f"{trig}-H{H}"]["combined_net"]) for H in HOLDS]
        bH, bnet = max(cands, key=lambda x: x[1])
        counts = defaultdict(int)
        for y in YEARS:
            for t in scored[(trig, bH)][y]:
                counts[t["sym"]] += 1
        draws = placebo(data, dict(counts), bH)
        pct = round(100.0 * float(np.mean(draws <= bnet)), 1)
        results["placebo"][trig] = dict(cell=f"{trig}-H{bH}", combined_net=bnet,
                                        percentile=pct,
                                        placebo_median=round(float(np.median(draws)), 2))
        if best_overall is None or bnet > best_overall[2]:
            best_overall = (trig, bH, bnet)
    results["best_overall"] = dict(trigger=best_overall[0], hold=best_overall[1],
                                   combined_net=best_overall[2])

    # best overall: full scored trade list + November trades
    trig, H = best_overall[0], best_overall[1]
    best_rows = []
    for y in YEARS:
        for t in scored[(trig, H)][y]:
            r = dict(t); r["window"] = str(y); best_rows.append(r)
    nov_rows = []
    for sym in NAMES:
        for t in all_trades[(trig, H)][sym]:
            if "2026-11-02" <= t["entry_date"] <= "2026-11-13":
                r = dict(t); r["window"] = "NOV"; nov_rows.append(r)
    best_rows.sort(key=lambda t: (t["entry_date"], t["sym"]))
    nov_rows.sort(key=lambda t: (t["entry_date"], t["sym"]))
    results["best_cell_november"] = [dict(sym=t["sym"], entry_date=t["entry_date"],
                                          exit_date=t["exit_date"], entry=t["entry"],
                                          exit=t["exit"], net=t["net"], kind=t["kind"])
                                     for t in nov_rows]
    with open(os.path.join(WS, "hold_programme_best_cell_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["window", "sym", "entry_date", "exit_date", "entry", "exit",
                    "pct_move", "net_inr", "hold_days", "exit_kind"])
        for t in best_rows + nov_rows:
            w.writerow([t["window"], t["sym"], t["entry_date"], t["exit_date"],
                        t["entry"], t["exit"], t["pct"], t["net"], t["hold"], t["kind"]])

    with open(os.path.join(WS, "hold_programme_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
