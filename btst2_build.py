#!/usr/bin/env python3
"""BTST-2 — the HOLD programme's entries at the two shortest holds (H1, H2).
Spec: btst2_SPEC.md (frozen 2026-11-15 before scoring). Research only;
changes no book/ledger/job. Machinery imported verbatim from
hold_programme_build.py — nothing re-implemented. Basis: equity cash,
LONG only, frozen 25 names, per 100 shares PROVISIONAL, Rs40 per
completed position, paper only.
"""
import json, os, sys
from collections import defaultdict

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import hold_programme_build as HB

NAMES, YEARS = HB.NAMES, HB.YEARS
TRIGGERS = ["E0", "E1", "E2", "E3"]
HOLDS = [1, 2]

# Published HOLD R1 E0-H3 stats (hold_programme_2026-11-15.md) — the reuse
# check must reproduce these exactly before any H1/H2 scoring.
CHECK = {2025: dict(trades=1050, net=79560.0, wr=50.5, avg_pct=0.31, worst=-18860.0),
         2026: dict(trades=1050, net=-154371.0, wr=45.1, avg_pct=-0.17, worst=-45165.0)}

def main():
    data = {sym: HB.prep(sym) for sym in NAMES}

    # ---- verification: reproduce HOLD R1 E0-H3 through the imported machinery
    for y in YEARS:
        tr = []
        for sym in NAMES:
            tr.extend(HB.score_year(HB.sim(data[sym], "E0", 3), data[sym], y))
        s = HB.stats(tr)
        for k, v in CHECK[y].items():
            got = round(s[k], 2) if k == "avg_pct" else s[k]  # report shows avg % at 2dp
            assert got == v, f"REUSE CHECK FAIL E0-H3 {y} {k}: got {s[k]}, published {v}"
    print("REUSE CHECK PASS: E0-H3 reproduces HOLD R1 exactly (both years).")

    results = {"spec": "btst2_SPEC.md",
               "basis": "per 100 shares PROVISIONAL, Rs40/position",
               "reuse_check": "E0-H3 reproduces hold_programme_2026-11-15.md exactly",
               "cells": {}, "placebo": {}}
    scored = {}
    for trig in TRIGGERS:
        for H in HOLDS:
            per_year = {y: [] for y in YEARS}
            for sym in NAMES:
                tr = HB.sim(data[sym], trig, H)
                for y in YEARS:
                    per_year[y].extend(HB.score_year(tr, data[sym], y))
            scored[(trig, H)] = per_year
            cell, comb = {}, 0.0
            for y in YEARS:
                s = HB.stats(per_year[y])
                cell[str(y)] = s
                comb += s["net"]
            cell["combined_net"] = round(comb, 2)
            results["cells"][f"{trig}-H{H}"] = cell

    # ---- placebo for the best cell of each trigger (two-year combined net)
    for trig in TRIGGERS:
        cands = [(H, results["cells"][f"{trig}-H{H}"]["combined_net"]) for H in HOLDS]
        bH, bnet = max(cands, key=lambda x: x[1])
        counts = defaultdict(int)
        for y in YEARS:
            for t in scored[(trig, bH)][y]:
                counts[t["sym"]] += 1
        draws = HB.placebo(data, dict(counts), bH)
        import numpy as np
        results["placebo"][trig] = dict(
            cell=f"{trig}-H{bH}", combined_net=bnet,
            percentile=round(100.0 * float(np.mean(draws <= bnet)), 1),
            placebo_median=round(float(np.median(draws)), 2))

    with open(os.path.join(WS, "btst2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main()
