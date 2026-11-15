#!/usr/bin/env python3
"""FLOOR CYCLE 4 — DIAGNOSIS ONLY. Registry re-derivation at the banked
FLOOR-C2 book with the GATE-ACCURATE bar: a slice banks under the session
gate iff its net is < 0 in one year and <= 0 in the other (removal then
raises one year and cannot lower the other), combined <= -500 (Lesson 5
quality bar). The C2 diagnostic used the stricter both-years-negative bar
(the v2 bar) and found 0; v3's own banks were mostly of this one-sided
class, so the registry is re-derived under the correct bar here.
Axes: (comp x stock x dir) and (comp x regime-cell).
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, LABELS
from collections import defaultdict

b25 = load("stocks_engine_floor_c2_book2025_trades.csv")
b26 = load("stocks_engine_floor_c2_book2026_trades.csv")

def scan(rows25, rows26, keyfn, label):
    def agg(rows):
        out = defaultdict(lambda: [0, 0.0, defaultdict(float)])
        for t in rows:
            k = keyfn(t)
            out[k][0] += 1; out[k][1] += t["net"]; out[k][2][t["date"][:7]] += t["net"]
        return out
    a25, a26 = agg(rows25), agg(rows26)
    qual = []
    for k in set(a25) | set(a26):
        n25, v25, _ = a25.get(k, [0, 0.0, {}]); n26, v26, _ = a26.get(k, [0, 0.0, {}])
        if (v25 < 0 and v26 <= 0) or (v26 < 0 and v25 <= 0):
            if v25 + v26 <= -500:
                qual.append((round(v25 + v26, 2), k, (n25, round(v25, 2)), (n26, round(v26, 2))))
    print(f"=== {label}: {len(qual)} qualifying rows ===")
    for row in sorted(qual)[:15]: print(row)
    return qual

q1 = scan(b25, b26, lambda t: (t["comp"], t["stock"], t["dir"]), "(comp x stock x dir)")
q2 = scan(b25, b26, lambda t: (t["comp"], LABELS.get(t["date"])), "(comp x regime-cell)")

if q1:
    top = sorted(q1)[0][1]
    print("\n=== leader month detail ===")
    for yr, rows in ((2025, b25), (2026, b26)):
        mo = defaultdict(float)
        for t in rows:
            if (t["comp"], t["stock"], t["dir"]) == top: mo[t["date"][:7]] += t["net"]
        print(top, yr, {k: round(v, 2) for k, v in sorted(mo.items())})
