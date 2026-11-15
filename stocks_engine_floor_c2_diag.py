#!/usr/bin/env python3
"""FLOOR CYCLE 2 — DIAGNOSIS ONLY (no fix scored here).
Scans at the incumbent C16 book:
 (i)   N4-V3 >=3% bucket split by direction x year (Cycle 1 follow-up);
 (ii)  (comp x stock x dir) slices negative in BOTH years (v2 registry bar);
 (iii) (comp x regime-cell) pairs negative in BOTH years (C23/C24 bar);
 (iv)  component x year table for the record.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_floor_lib import load, LABELS, n4_move
from collections import defaultdict

b25 = load("stocks_engine_v3_c16_book2025_trades.csv")
b26 = load("stocks_engine_v3_c16_book2026_trades.csv")

print("=== (i) N4-V3 |move|>=3% bucket, direction x year ===")
for yr, rows in ((2025, b25), (2026, b26)):
    for dr in ("LONG", "SHORT"):
        sel = []
        for t in rows:
            if t["comp"] == "N4-V3" and t["dir"] == dr:
                mv = n4_move(t["stock"], t["date"])
                if mv is not None and abs(mv) >= 3.0: sel.append(t)
        print(f"{yr} {dr}: {len(sel)} tr / {round(sum(t['net'] for t in sel), 2):+.2f} "
              f"(wins {sum(1 for t in sel if t['net'] > 0)})")

print("\n=== (ii) (comp x stock x dir) negative in BOTH years, combined <= -500 ===")
def slices(rows):
    out = defaultdict(lambda: [0, 0.0])
    for t in rows:
        k = (t["comp"], t["stock"], t["dir"])
        out[k][0] += 1; out[k][1] += t["net"]
    return out
s25, s26 = slices(b25), slices(b26)
qual = []
for k in set(s25) | set(s26):
    n25, v25 = s25.get(k, [0, 0.0]); n26, v26 = s26.get(k, [0, 0.0])
    if v25 < 0 and v26 < 0 and v25 + v26 <= -500:
        qual.append((round(v25 + v26, 2), k, (n25, round(v25, 2)), (n26, round(v26, 2))))
for row in sorted(qual): print(row)
print(f"qualifying rows: {len(qual)}")

print("\n=== (iii) (comp x regime-cell) negative in BOTH years, combined <= -500 ===")
def cslices(rows):
    out = defaultdict(lambda: [0, 0.0])
    for t in rows:
        k = (t["comp"], LABELS.get(t["date"]))
        out[k][0] += 1; out[k][1] += t["net"]
    return out
c25, c26 = cslices(b25), cslices(b26)
qual2 = []
for k in set(c25) | set(c26):
    n25, v25 = c25.get(k, [0, 0.0]); n26, v26 = c26.get(k, [0, 0.0])
    if v25 < 0 and v26 < 0 and v25 + v26 <= -500:
        qual2.append((round(v25 + v26, 2), k, (n25, round(v25, 2)), (n26, round(v26, 2))))
for row in sorted(qual2): print(row)
print(f"qualifying rows: {len(qual2)}")

print("\n=== (iv) component x year ===")
for yr, rows in ((2025, b25), (2026, b26)):
    by = defaultdict(lambda: [0, 0.0])
    for t in rows: by[t["comp"]][0] += 1; by[t["comp"]][1] += t["net"]
    print(yr, {k: (v[0], round(v[1], 2)) for k, v in sorted(by.items())})

print("\n=== (v) 2025 weak months anatomy (C16) ===")
mo = defaultdict(float); moc = defaultdict(lambda: defaultdict(float))
for t in b25:
    mo[t["date"][:7]] += t["net"]; moc[t["date"][:7]][t["comp"]] += t["net"]
for m in sorted(mo):
    print(m, round(mo[m], 2), {k: round(v, 2) for k, v in sorted(moc[m].items()) if abs(v) >= 500})
