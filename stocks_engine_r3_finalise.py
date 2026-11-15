#!/usr/bin/env python3
"""ROUND 3 finalisation: insert the R3-02 audit record, export the ending
books, append log + lessons, update state, write the round report."""
import sys, json, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r3_lib as R3
import stocks_engine_floor_lib as FL

books = R3.load_books()

# ---- R3-02 audit record into r3_results.json (kept in cycle order) ------
data = json.load(open(f"{WS}/r3_results.json"))
if not any(r["cycle"] == "R3-02" for r in data):
    audit = {"cycle": "R3-02", "type": "audit_no_candidate",
             "label": "WS2 event-layer audit: 2025 population completeness",
             "banked": False,
             "finding": ("2025 calendar COMPLETE: 100 results rows (4/stock), "
                         "0 with missing/out-of-window reaction_date; reaction "
                         "candidates 100 vs 2026's 80; band>=2.5% candidates "
                         "33 vs 39; N4 signal-days 91 vs 77. Nothing missing "
                         "to rebuild. The 16 out-of-window rows in the 2026 "
                         "file are 15 Nov-2025 events (placeholder reaction "
                         "2026-01-01; valid Nov-2025 dates sourceable from "
                         "results_events_v1.csv but outside the judged "
                         "window either way) + UNITDSPR 2026-10-28 (reaction "
                         "date unsourceable; incumbent treats announcement "
                         "day as R). 2025 family weakness is expectancy "
                         "(P2F-R2 -390.06 on 21 tr vs 2026 +15,149.33 on 32) "
                         "and band mix, not coverage."),
             "note": "no candidate gated: no hole exists in the judged window"}
    data.insert(1, audit)
    json.dump(data, open(f"{WS}/r3_results.json", "w"), indent=1)

# ---- export ending books -------------------------------------------------
for yr in (2025, 2026):
    rows = sorted(books[yr], key=lambda t: (t["date"], t["comp"], t["stock"]))
    with open(f"{WS}/stocks_engine_r3_book{yr}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "comp", "stock", "dir",
                                          "entry_time", "net"])
        w.writeheader()
        w.writerows(rows)

sc = {yr: FL.scorecard(books[yr], yr) for yr in (2025, 2026)}
cells = {yr: FL.cells(books[yr]) for yr in (2025, 2026)}
print(json.dumps({str(yr): {"jan_oct": sc[yr]["jan_oct_total"],
                            "months": sc[yr]["months"],
                            "per_comp": sc[yr]["by_comp"],
                            "cells": cells[yr][0]} for yr in sc}, indent=1))
print("finalised exports")
