#!/usr/bin/env python3
"""FLOOR CYCLE 5 — DIAGNOSIS ONLY. Registry re-derivation at the FLOOR-C4
book, gate-accurate bar (< 0 in one year, <= 0 in the other, combined
<= -500), on THREE axes: (comp x stock x dir), (comp x stock),
(comp x regime-cell).
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, LABELS
from collections import defaultdict

b25 = load("stocks_engine_floor_c4_book2025_trades.csv")
b26 = load("stocks_engine_floor_c4_book2026_trades.csv")

def scan(rows25, rows26, keyfn, label):
    def agg(rows):
        out = defaultdict(lambda: [0, 0.0])
        for t in rows:
            k = keyfn(t); out[k][0] += 1; out[k][1] += t["net"]
        return out
    a25, a26 = agg(rows25), agg(rows26)
    qual = []
    for k in set(a25) | set(a26):
        n25, v25 = a25.get(k, [0, 0.0]); n26, v26 = a26.get(k, [0, 0.0])
        if ((v25 < 0 and v26 <= 0) or (v26 < 0 and v25 <= 0)) and v25 + v26 <= -500:
            qual.append((round(v25 + v26, 2), k, (n25, round(v25, 2)), (n26, round(v26, 2))))
    print(f"=== {label}: {len(qual)} qualifying ===")
    for row in sorted(qual)[:12]: print(row)
    return qual

scan(b25, b26, lambda t: (t["comp"], t["stock"], t["dir"]), "(comp x stock x dir)")
scan(b25, b26, lambda t: (t["comp"], t["stock"]), "(comp x stock)")
scan(b25, b26, lambda t: (t["comp"], LABELS.get(t["date"])), "(comp x regime-cell)")
