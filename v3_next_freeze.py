#!/usr/bin/env python3
"""V3 freeze helper: extract a slice's exact rows from the CURRENT v3
book and write its freeze JSON (the machine-readable twin of the
frozen-file entry, which is always written BEFORE the scorer runs).
Usage: v3_next_freeze.py <cycle> <comp> <stock> <dir> <label>
Prints the frozen set for the frozen-file entry. Read-only on the book.
"""
import csv, json, sys
WS = "/home/hatch/workspace/trading"
n, comp, stock, direc, label = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
rows = {}
for yr in ("2025", "2026"):
    rs = [t for t in csv.DictReader(open(f"{WS}/{state['book_files'][yr]}"))
          if t["comp"] == comp and t["stock"] == stock and t["dir"] == direc]
    rows[yr] = sorted([t["date"], t["entry_time"], float(t["net"])] for t in rs)
fz = {"cycle": int(n), "label": label, "slice": [comp, stock, direc], "rows": rows}
json.dump(fz, open(f"{WS}/v3_out/freeze_c{n}.json", "w"), indent=1)
tot = {yr: round(sum(r[2] for r in rows[yr]), 2) for yr in rows}
print(f"freeze c{n}: {comp} x {stock} x {direc} | 2025 {len(rows['2025'])} tr ({tot['2025']}) "
      f"| 2026 {len(rows['2026'])} tr ({tot['2026']})")
for yr in rows:
    for r in rows[yr]:
        print(f"   {yr}: {r[0]} {r[1]} {r[2]}")
