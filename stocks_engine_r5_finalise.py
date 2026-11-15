#!/usr/bin/env python3
"""ROUND 5 finalise: (1) WS6 — zero Round-5 bankings exist, so there is
nothing to combine; as decision support only (the R4-WS4 disposition),
the round's two one/two-leg near-misses are gated in combination —
R5-03's thr-1.25 sleeve swap + R5-07's NE-REV-LONG sleeve — with
force_no_bank set: the engine does not adopt what it did not bank.
The two row sets are rebuilt here and ANCHORED against their recorded
single-variant variant totals before the combination is scored.
(2) Export the ending books and re-sum independently. (3) Print the
ending per-year scorecard.
"""
import sys, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r5_lib as R5
import stocks_engine_floor_lib as FL

books = R5.load_books()
LABELS = R.LABELS
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay, replay_plain = (g["STOCKS_E"], g["replay"],
                                  g["replay_plain"])
SYMBOLS = g["SYMBOLS"]
rc = g["reaction_candidates"]
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def gap_rows(mode, thr, entry_bar, tgt, stp, only_dir, cells):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            if cells is not None and LABELS.get(day) not in cells:
                continue
            bars = spot.get(day, [])
            if len(bars) <= entry_bar:
                continue
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            gap = (bars[0]["open"] / prev_close - 1) * 100
            if abs(gap) < thr:
                continue
            natural = "LONG" if gap > 0 else "SHORT"
            direction = natural if mode == "follow" else (
                "SHORT" if natural == "LONG" else "LONG")
            if only_dir and direction != only_dir:
                continue
            entry = bars[entry_bar]["open"]
            r = replay(bars, entry_bar, entry, direction, tgt, stp)
            if r is None:
                continue
            er, ep, et = r
            comp = "GAP-FOLLOW" if mode == "follow" else "GAP-FADE"
            out.append(R.norm(comp, day, sym, direction,
                              bars[entry_bar]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

# NE-REV population (identical construction to stocks_engine_r5_ws3.py)
contaminated = set()
for cal, lo, hi in [(f"{WS}/stock_event_calendar_2025.csv",
                     "2025-01-01", "2025-12-31"),
                    (f"{WS}/stock_event_calendar_jan_oct_2026.csv",
                     "2026-01-01", "2026-12-31")]:
    for c in rc(cal, lo, hi):
        daily = STOCKS_E[c["symbol"]][1]
        for j in (0, 1, 2):
            if c["ri"] + j < len(daily):
                contaminated.add((c["symbol"], daily[c["ri"] + j]["date"]))

def nerev(direction, entry_time_want, flip=False):
    rows = []
    trade_dir = direction
    if flip:
        trade_dir = "SHORT" if direction == "LONG" else "LONG"
    sign = 1 if trade_dir == "LONG" else -1
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day) or (sym, day) in contaminated:
                continue
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "10:25" not in idx or entry_time_want not in idx:
                continue
            si, ei = idx["10:25"], idx[entry_time_want]
            if ei <= si:
                continue
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            move = (bars[si]["close"] / prev_close - 1) * 100
            if direction == "LONG" and move > -2.0:
                continue
            if direction == "SHORT" and move < 2.0:
                continue
            entry = float(bars[ei]["open"])
            er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry,
                                                 1.00, 0.65)
            rows.append(R.norm("NE-REV-LONG", day, sym, trade_dir,
                               bars[ei]["time"], round(gross - COST, 2)))
    return R.split_years(rows)

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

# ---- anchors: each near-miss alone must reproduce its recorded totals
sleeve125 = gap_rows("fade", 1.25, 1, 1.25, 0.5, "LONG",
                     {"DOWN", "FLAT"})
v03 = R5.swap(books, "GAP-FADE", sleeve125)
assert (jo(v03, 2025), jo(v03, 2026)) == (88401.23, 226071.55), \
    (jo(v03, 2025), jo(v03, 2026))
nerev_long = nerev("LONG", "10:35")
v07 = R5.add_comp(books, "NE-REV-LONG", nerev_long)
assert (jo(v07, 2025), jo(v07, 2026)) == (90121.11, 247599.9), \
    (jo(v07, 2025), jo(v07, 2026))
print("anchors OK: R5-03 and R5-07 single-variant totals reproduced")

# ---- R5-15: the combination, decision support only
combo = R5.add_comp(v03, "NE-REV-LONG", nerev_long)
base_wo = {yr: [t for t in books[yr] if t["comp"] != "GAP-FADE"]
           for yr in (2025, 2026)}
late = R5.add_comp(R5.swap(base_wo, "GAP-FADE",
                           gap_rows("fade", 1.25, 2, 1.25, 0.5, "LONG",
                                    {"DOWN", "FLAT"})),
                   "NE-REV-LONG", nerev("LONG", "10:40"))
mirr = R5.add_comp(R5.swap(base_wo, "GAP-FADE",
                           gap_rows("follow", 1.25, 1, 1.25, 0.5,
                                    "SHORT", {"DOWN", "FLAT"})),
                   "NE-REV-LONG", nerev("LONG", "10:35", flip=True))
pl = [R5.full_total(late), R5.full_total(mirr)]
out = R5.gate(books, combo, pl, timing_violations=0)
R5.record("R5-15", "DECISION SUPPORT: R5-03 sleeve (thr 1.25) + R5-07 "
                   "NE-REV-LONG, combined", out,
          note=f"WS6: no Round-5 bankings exist to combine; this is "
               f"the R4-WS4 disposition applied to the round's two "
               f"near-misses, gated whole and recorded UNBANKED "
               f"regardless of verdict (adoption is Chandu's). "
               f"Anchors reproduced first (R5-03: 88401.23/226071.55; "
               f"R5-07: 90121.11/247599.90). Timing: gap entries bar 1 "
               f"after the bar-0 print; NE-REV entries 10:35 after the "
               f"10:25 signal bar -> 0 violations. Placebos: both "
               f"sleeves one bar late {pl[0]}; both mirrors {pl[1]}.",
          force_no_bank=True)

# ------------------------------------------------------------- export --
cols = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r5_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(books[yr], key=lambda t: (t["date"], t["comp"],
                                                  t["stock"])):
            w.writerow({c: t[c] for c in cols})
    back = FL.load(f"stocks_engine_r5_book{yr}_trades.csv")
    jo_pkl = jo(books, yr)
    jo_csv = round(sum(t["net"] for t in back
                       if t["date"] <= f"{yr}-10-31"), 2)
    assert jo_pkl == jo_csv and len(back) == len(books[yr]), (jo_pkl,
                                                              jo_csv)
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
