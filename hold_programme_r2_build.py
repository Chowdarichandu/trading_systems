#!/usr/bin/env python3
"""HOLD PROGRAMME ROUND 2 — tune around the RSI-dip + 3-week cell.
Spec: hold_programme_r2_SPEC.md (frozen 2026-11-15 before scoring).
Reuses Round 1's engine/scoring/stats verbatim (hold_programme_build.py);
only the E1 signal level is parameterised. Research only; arms nothing.
Basis: equity cash, LONG only, frozen 25 names, per 100 shares PROVISIONAL,
Rs40 per completed position, paper only.
"""
import csv, json, os, sys
from collections import defaultdict
import numpy as np

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import indicator_parameter_tuning_stocks_build as ATLAS
import hold_programme_build as R1

NAMES = ATLAS.NAMES
COST = ATLAS.COST
YEARS = R1.YEARS
LEVELS = [30, 35, 40]
HOLDS = [10, 15, 20]
CONTROL = (35, 15)

def prep_r2(sym):
    """Round 1 prep, plus E1 signal arrays at each level."""
    d = R1.prep(sym)
    c = d["c"]
    r14 = ATLAS.rsi_wilder(c, 14)
    ok = ~np.isnan(r14)
    sig = {}
    for L in LEVELS:
        e = np.zeros(d["n"], dtype=bool)
        e[1:] = ok[1:] & ok[:-1] & (r14[:-1] < float(L)) & (r14[1:] >= float(L))
        sig[L] = e
    d["sig_r2"] = sig
    return d

def sim_r2(d, L, H):
    """Round 1 sim() with the level-parameterised signal array.
    Mirrors R1.sim for non-E0 triggers exactly."""
    dates, o, c, n = d["dates"], d["o"], d["c"], d["n"]
    sig = d["sig_r2"][L]
    trades = []
    pos = None
    i = 0
    while i < n:
        if pos is None:
            if sig[i] and i + 1 < n:
                pos = i + 1
                i = pos
                continue
            i += 1
            continue
        xi = min(pos + H, n - 1)
        kind = "HOLD" if pos + H <= n - 1 else "FORCED"
        trades.append(dict(sym=d["sym"], entry_idx=pos, exit_idx=xi,
                           entry_date=dates[pos], exit_date=dates[xi],
                           entry=float(o[pos]), exit=float(c[xi]),
                           net=round((float(c[xi]) - float(o[pos])) * 100.0 - COST, 2),
                           pct=round((float(c[xi]) / float(o[pos]) - 1.0) * 100.0, 4),
                           hold=xi - pos, kind=kind))
        pos = None
        i = xi
    return trades

def main():
    data = {sym: prep_r2(sym) for sym in NAMES}

    # --- control verification against Round 1's published E1-H15 lines
    r1 = json.load(open(os.path.join(WS, "hold_programme_results.json")))
    r1_cell = r1["cells"]["E1-H15"]
    scored = {}   # (L,H) -> {year: [scored trades]}
    true_tr = {}  # (L,H) -> {sym: [true trades]}
    results = {"spec": "hold_programme_r2_SPEC.md",
               "basis": "per 100 shares PROVISIONAL, Rs40/position",
               "cells": {}, "control_check": None}
    for L in LEVELS:
        for H in HOLDS:
            per_year = {y: [] for y in YEARS}
            per_sym = {}
            for sym in NAMES:
                tr = sim_r2(data[sym], L, H)
                per_sym[sym] = tr
                for y in YEARS:
                    per_year[y].extend(R1.score_year(tr, data[sym], y))
            scored[(L, H)] = per_year
            true_tr[(L, H)] = per_sym
            cell = {}
            comb = 0.0
            for y in YEARS:
                s = R1.stats(per_year[y])
                cell[str(y)] = s
                comb += s["net"]
            cell["combined_net"] = round(comb, 2)
            results["cells"][f"L{L}-H{H}"] = cell

    cc = results["cells"]["L35-H15"]
    ok = (cc["2025"]["trades"] == r1_cell["2025"]["trades"] == 83
          and cc["2025"]["net"] == r1_cell["2025"]["net"] == 42163.0
          and cc["2026"]["trades"] == r1_cell["2026"]["trades"] == 103
          and cc["2026"]["net"] == r1_cell["2026"]["net"] == 83963.0)
    results["control_check"] = dict(
        reproduced=bool(ok),
        r2=dict(t2025=cc["2025"]["trades"], n2025=cc["2025"]["net"],
                t2026=cc["2026"]["trades"], n2026=cc["2026"]["net"]),
        r1=dict(t2025=r1_cell["2025"]["trades"], n2025=r1_cell["2025"]["net"],
                t2026=r1_cell["2026"]["trades"], n2026=r1_cell["2026"]["net"]))
    print("CONTROL CHECK:", results["control_check"])
    assert ok, "control did not reproduce Round 1 E1-H15"

    # --- best cell by the frozen rule
    pos_cells = [(L, H) for L in LEVELS for H in HOLDS
                 if results["cells"][f"L{L}-H{H}"]["2025"]["net"] > 0
                 and results["cells"][f"L{L}-H{H}"]["2026"]["net"] > 0]
    if pos_cells:
        bL, bH = max(pos_cells,
                     key=lambda lh: results["cells"][f"L{lh[0]}-H{lh[1]}"]["combined_net"])
    else:
        bL, bH = CONTROL
    bnet = results["cells"][f"L{bL}-H{bH}"]["combined_net"]
    results["best_cell"] = dict(level=bL, hold=bH, combined_net=bnet,
                                positive_both_years=bool(pos_cells))

    # beats control in both years?
    ctrl = results["cells"]["L35-H15"]
    beats = [f"L{L}-H{H}" for L in LEVELS for H in HOLDS if not (L, H) == CONTROL
             and results["cells"][f"L{L}-H{H}"]["2025"]["net"] > ctrl["2025"]["net"]
             and results["cells"][f"L{L}-H{H}"]["2026"]["net"] > ctrl["2026"]["net"]]
    results["cells_beating_control_both_years"] = beats

    # --- placebo for best cell (Round 1 construction)
    counts = defaultdict(int)
    for y in YEARS:
        for t in scored[(bL, bH)][y]:
            counts[t["sym"]] += 1
    draws = R1.placebo(data, dict(counts), bH)
    results["placebo"] = dict(cell=f"L{bL}-H{bH}", combined_net=bnet,
                              percentile=round(100.0 * float(np.mean(draws <= bnet)), 1),
                              placebo_median=round(float(np.median(draws)), 2))

    # --- ex-top-3 + month table for best cell
    extop, months = {}, {}
    for y in YEARS:
        tr = scored[(bL, bH)][y]
        top3 = sorted((t["net"] for t in tr), reverse=True)[:3]
        extop[str(y)] = round(sum(t["net"] for t in tr) - sum(top3), 2)
        mt = defaultdict(lambda: [0, 0.0])
        for t in tr:
            mt[t["entry_date"][:7]][0] += 1
            mt[t["entry_date"][:7]][1] += t["net"]
        months[str(y)] = {m: dict(trades=v[0], net=round(v[1], 2))
                          for m, v in sorted(mt.items())}
    results["best_cell_ex_top3"] = extop
    results["best_cell_months"] = months

    # --- best cell November trades (true exits; FORCED = open/marked)
    nov = []
    for sym in NAMES:
        for t in true_tr[(bL, bH)][sym]:
            if "2026-11-02" <= t["entry_date"] <= "2026-11-13":
                r = dict(t)
                r["label"] = "OPEN/MARKED" if t["kind"] == "FORCED" else "CLOSED"
                nov.append(r)
    nov.sort(key=lambda t: (t["entry_date"], t["sym"]))
    results["best_cell_november"] = [
        dict(sym=t["sym"], entry_date=t["entry_date"], exit_date=t["exit_date"],
             entry=t["entry"], exit=t["exit"], net=t["net"], kind=t["kind"],
             label=t["label"]) for t in nov]
    results["best_cell_november_total"] = round(sum(t["net"] for t in nov), 2)

    # --- best-cell full scored trade list CSV
    rows = []
    for y in YEARS:
        for t in scored[(bL, bH)][y]:
            r = dict(t); r["window"] = str(y); rows.append(r)
    rows.sort(key=lambda t: (t["entry_date"], t["sym"]))
    with open(os.path.join(WS, "hold_programme_r2_best_cell_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["window", "sym", "entry_date", "exit_date", "entry", "exit",
                    "pct_move", "net_inr", "hold_days", "exit_kind"])
        for t in rows:
            w.writerow([t["window"], t["sym"], t["entry_date"], t["exit_date"],
                        t["entry"], t["exit"], t["pct"], t["net"], t["hold"], t["kind"]])
        for t in nov:
            w.writerow(["NOV", t["sym"], t["entry_date"], t["exit_date"],
                        t["entry"], t["exit"], t["pct"], t["net"], t["hold"],
                        t["kind"] + (" (OPEN/MARKED)" if t["kind"] == "FORCED" else "")])

    with open(os.path.join(WS, "hold_programme_r2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
