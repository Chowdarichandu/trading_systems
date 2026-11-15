#!/usr/bin/env python3
"""FLOOR CYCLE 3 (challenger slot) — DIAGNOSIS ONLY.
(a) P2F family: reconstruct each book trade's reaction_ret (close-to-close on
    the reaction day R; entry = R+lag trading days, lag 1 for P2F, 2 for
    P2F-R2 / R2-LOWBAND) and tabulate expectancy by |reaction_ret| bucket x
    year. Reconstruction validated against the frozen bands (P2F/P2F-R2 rows
    must sit >= 2.5%, R2-LOWBAND rows in [2.0, 2.5)).
(b) F4 x regime-cell x year table (2025 F4 is ~breakeven overall).
Runs on the banked FLOOR-C2 book.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, LABELS, _stock_data
from collections import defaultdict

b25 = load("stocks_engine_floor_c2_book2025_trades.csv")
b26 = load("stocks_engine_floor_c2_book2026_trades.csv")
LAG = {"P2F": 1, "P2F-R2": 2, "R2-LOWBAND": 2}

def reaction_ret(t):
    _, dl = _stock_data(t["stock"])
    dates = [d for d, _ in dl]
    if t["date"] not in dates: return None
    ei = dates.index(t["date"])
    ri = ei - LAG[t["comp"]]
    if ri < 1: return None
    return round((dl[ri][1] / dl[ri - 1][1] - 1) * 100, 2), dates[ri]

print("=== (a) P2F family reaction_ret reconstruction + buckets ===")
band_bad = 0; total = 0
for yr, rows in ((2025, b25), (2026, b26)):
    fam = [t for t in rows if t["comp"] in LAG]
    buckets = defaultdict(lambda: [0, 0.0])
    for t in fam:
        rr = reaction_ret(t)
        total += 1
        if rr is None: band_bad += 1; continue
        v, _ = rr
        if t["comp"] in ("P2F", "P2F-R2") and abs(v) < 2.5: band_bad += 1
        if t["comp"] == "R2-LOWBAND" and not (2.0 <= abs(v) < 2.5): band_bad += 1
        b = "2.5-4" if abs(v) < 4 else "4-6" if abs(v) < 6 else "6-8" if abs(v) < 8 else ">=8"
        buckets[b][0] += 1; buckets[b][1] += t["net"]
    print(f"{yr}: " + " | ".join(f"{k}: {v[0]} tr {v[1]:+.2f} (exp {v[1]/v[0]:+.0f})"
                                 for k, v in sorted(buckets.items())))
print(f"band-consistency violations: {band_bad} of {total} family rows")

print("\n=== (a2) pooled family, top buckets by year ===")
for lo, hi in ((6, 8), (8, 99)):
    for yr, rows in ((2025, b25), (2026, b26)):
        sel = []
        for t in rows:
            if t["comp"] in LAG:
                rr = reaction_ret(t)
                if rr and lo <= abs(rr[0]) < hi: sel.append(t)
        if sel: print(f"|ret| [{lo},{hi}) {yr}: {len(sel)} tr / {round(sum(t['net'] for t in sel), 2):+.2f}")

print("\n=== (b) F4 x cell x year ===")
for yr, rows in ((2025, b25), (2026, b26)):
    by = defaultdict(lambda: [0, 0.0])
    for t in rows:
        if t["comp"] == "F4":
            by[LABELS.get(t["date"])][0] += 1; by[LABELS.get(t["date"])][1] += t["net"]
    print(yr, {k: (v[0], round(v[1], 2)) for k, v in sorted(by.items())})
