#!/usr/bin/env python3
"""ROUND 4 finalise: export the ending books (Round-2 book + R4-03's
banked sleeve; R4-07 voided, nothing else banked), independently re-sum
the exports, and print the ending per-year scorecard."""
import sys, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r4_lib as R4

books = R4.load_books()
cols = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r4_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(books[yr], key=lambda t: (t["date"], t["comp"],
                                                  t["stock"])):
            w.writerow({c: t[c] for c in cols})
    back = FL.load(f"stocks_engine_r4_book{yr}_trades.csv")
    jo_pkl = round(sum(t["net"] for t in books[yr]
                       if t["date"] <= f"{yr}-10-31"), 2)
    jo_csv = round(sum(t["net"] for t in back
                       if t["date"] <= f"{yr}-10-31"), 2)
    assert jo_pkl == jo_csv and len(back) == len(books[yr]), (jo_pkl, jo_csv)
    print(f"{yr}: export re-sum OK — JO {jo_csv}, rows {len(back)}")
    sc = FL.scorecard(books[yr], yr)
    cells, missing = FL.cells(books[yr])
    print(f"  total {sc['total']} | JO {sc['jan_oct_total']} "
          f"({round(sc['jan_oct_total']/10, 2)}/mo) | trades "
          f"{sc['trades']} | wins {sc['wins']} | ex-top3 "
          f"{sc['ex_top3_stocks']} | top3 {sc['top3_stocks']}")
    print(f"  H1(Jan-May) {sc['jan_oct_H1_jan_may']} | H2(Jun-Oct) "
          f"{sc['jan_oct_H2_jun_oct']} | cells {cells} missing {missing}")
    print(f"  months: {sc['months']}")
    print(f"  by_comp: {sc['by_comp']}")
print("finalise done")
