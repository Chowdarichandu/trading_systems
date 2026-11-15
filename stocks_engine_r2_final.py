#!/usr/bin/env python3
"""ROUND 2 — FINAL: export the ending book CSVs, independently re-sum them,
and print the controlled scorecard of the ending book vs FLOOR-C4.
"""
import sys, csv, pickle
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL

books = pickle.load(open(f"{WS}/r2_books.pkl", "rb"))
c4 = {}
for yr in (2025, 2026):
    with open(f"{WS}/stocks_engine_floor_c4_book{yr}_trades.csv") as f:
        c4[yr] = [{"comp": r["comp"], "date": r["date"], "stock": r["stock"],
                   "dir": r["dir"], "entry_time": r["entry_time"],
                   "net": float(r["net"])} for r in csv.DictReader(f)]

FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    rows = sorted(books[yr], key=lambda t: (t["date"], t["entry_time"],
                                            t["stock"], t["comp"]))
    with open(f"{WS}/stocks_engine_r2_book{yr}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in rows:
            w.writerow({k: t[k] for k in FIELDS})
    # independent re-sum from the written file
    with open(f"{WS}/stocks_engine_r2_book{yr}_trades.csv") as f:
        back = list(csv.DictReader(f))
    s_file = round(sum(float(r["net"]) for r in back), 2)
    s_mem = round(sum(float(t["net"]) for t in books[yr]), 2)
    assert s_file == s_mem and len(back) == len(books[yr]), f"re-sum failed {yr}"
    print(f"{yr}: exported {len(back)} trades, re-sum exact ({s_file})")

def card(rows, yr):
    jo = [t for t in rows if t["date"] <= f"{yr}-10-31"]
    tot = round(sum(t["net"] for t in rows), 2)
    jos = round(sum(t["net"] for t in jo), 2)
    months = defaultdict(float)
    for t in jo:
        months[t["date"][:7]] += float(t["net"])
    h1 = round(sum(t["net"] for t in jo if t["date"] <= f"{yr}-05-31"), 2)
    h2 = round(jos - h1, 2)
    top3 = sorted((float(t["net"]) for t in jo), reverse=True)[:3]
    ext = round(jos - sum(top3), 2)
    cells = defaultdict(float)
    for t in jo:
        cells[FL.LABELS.get(t["date"], "?")] += float(t["net"])
    comps = defaultdict(lambda: [0, 0.0])
    for t in jo:
        comps[t["comp"]][0] += 1
        comps[t["comp"]][1] += float(t["net"])
    return {"total": tot, "jan_oct": jos, "trades": len(jo), "h1": h1,
            "h2": h2, "ex_top3": ext,
            "months": {m: round(months.get(f"{yr}-{m:02d}", 0.0), 2)
                       for m in range(1, 11)},
            "cells": {k: round(v, 2) for k, v in sorted(cells.items())},
            "comps": {k: (v[0], round(v[1], 2))
                      for k, v in sorted(comps.items())}}

for yr in (2025, 2026):
    a, b = card(c4[yr], yr), card(books[yr], yr)
    print(f"\n=== {yr}: FLOOR-C4 -> ROUND-2 END ===")
    print(f"  Jan-Oct {a['jan_oct']} ({a['trades']} tr) -> {b['jan_oct']} "
          f"({b['trades']} tr) | delta {round(b['jan_oct']-a['jan_oct'],2)}")
    print(f"  total {a['total']} -> {b['total']} | halves {a['h1']}/{a['h2']} "
          f"-> {b['h1']}/{b['h2']} | ex-top3 {a['ex_top3']} -> {b['ex_top3']}")
    print(f"  cells C4 {a['cells']}")
    print(f"  cells R2 {b['cells']}")
    print(f"  months C4 {[a['months'][m] for m in range(1,11)]}")
    print(f"  months R2 {[b['months'][m] for m in range(1,11)]}")
    print(f"  comps R2 {b['comps']}")
    print(f"  pace R2 {round(b['jan_oct']/10, 2)}/month; floor gap "
          f"{round(150000 - b['jan_oct'], 2)}")
