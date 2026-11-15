#!/usr/bin/env python3
"""ROUND 3 — WS4 completion + WS5.
R3-08 GAP-FADE @ >=2.5% and R3-09 GAP-FOLLOW @ >=2.5% complete the
pre-declared {follow, fade} x {1.5%, 2.5%} sleeve grid. Placebos: the
opposite direction at the same threshold; the same direction one bar
late. Then the fade sign-split diagnostic (fade-LONG = faded gap-downs;
fade-SHORT = faded gap-ups) on the 1.5% population: if exactly one side
has positive expectancy in BOTH halves, that sub-sleeve is gated as
R3-10; otherwise R3-10 is GAP-FADE @1.5% with the reaction families'
other exit geometry (T150/S080). WS5 runs only if something banked.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r3_lib as R3

g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
SYMBOLS = g["SYMBOLS"]
books = R3.load_books()
COST = 40.0
banked_any = False

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def book_total(bk):
    return round(sum(sum(t["net"] for t in bk[yr]
                         if t["date"] <= f"{yr}-10-31")
                     for yr in (2025, 2026)), 2)

def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
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

def expectancy_halves(rows_by_yr):
    out = {}
    for half, months in (("H1", range(1, 7)), ("H2", range(7, 11))):
        sel = [t for yr in (2025, 2026) for t in rows_by_yr[yr]
               if int(t["date"][5:7]) in months]
        out[half] = (len(sel),
                     round(sum(t["net"] for t in sel) / len(sel), 2)
                     if sel else None)
    return out

def run_sleeve(cyc, label, comp, rows, other_comp, other_rows, late_rows,
               note_extra=""):
    global books, banked_any
    var_books = R3.add_comp(books, comp, rows)
    pl = [book_total(R3.add_comp(books, other_comp, other_rows)),
          book_total(R3.add_comp(books, comp, late_rows))]
    out = R3.gate(books, var_books, pl)
    R3.record(cyc, label, out,
              note=f"placebos: opposite-direction book {pl[0]}; "
                   f"one-bar-late book {pl[1]}. {note_extra}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var_books
        R3.save_books(books)
        banked_any = True
        print("    -> BANKED")
    return out

fade25 = gap_rows("fade", 2.5)
follow25 = gap_rows("follow", 2.5)
fade25_late = gap_rows("fade", 2.5, entry_bar=2)
follow25_late = gap_rows("follow", 2.5, entry_bar=2)
print("fade@2.5 standalone JO:", {str(yr): round(sum(t['net'] for t in fade25[yr]
      if t['date'] <= f'{yr}-10-31'), 2) for yr in fade25},
      "diag:", expectancy_halves(fade25))
run_sleeve("R3-08", "NEW SLEEVE GAP-FADE @ >=2.5% (entry 09:20 open, "
                    "T125/S050)", "GAP-FADE", fade25,
           "GAP-FOLLOW", follow25, fade25_late)
run_sleeve("R3-09", "NEW SLEEVE GAP-FOLLOW @ >=2.5% (entry 09:20 open, "
                    "T125/S050)", "GAP-FOLLOW", follow25,
           "GAP-FADE", fade25, follow25_late)

# ---- fade sign-split diagnostic on the 1.5% population ------------------
fade_long = gap_rows("fade", 1.5, only_dir="LONG")
fade_short = gap_rows("fade", 1.5, only_dir="SHORT")
d_long, d_short = expectancy_halves(fade_long), expectancy_halves(fade_short)
print(f"fade sign-split: fade-LONG (gap-down fades) H1 {d_long['H1']} "
      f"H2 {d_long['H2']}; fade-SHORT (gap-up fades) H1 {d_short['H1']} "
      f"H2 {d_short['H2']}")
def both_pos(d):
    return all(v[1] is not None and v[1] > 0 for v in d.values())
if both_pos(d_long) != both_pos(d_short):
    side = "LONG" if both_pos(d_long) else "SHORT"
    rows = fade_long if side == "LONG" else fade_short
    late = gap_rows("fade", 1.5, entry_bar=2, only_dir=side)
    opp = gap_rows("follow", 1.5, only_dir=("SHORT" if side == "LONG" else "LONG"))
    run_sleeve("R3-10", f"GAP-FADE {side}-only sub-sleeve @ >=1.5% "
                        f"(diagnosis-led sign split, T125/S050)",
               "GAP-FADE", rows, "GAP-FOLLOW", opp, late,
               note_extra=f"sign-split diagnostic: LONG {d_long}, SHORT {d_short}")
else:
    rows = gap_rows("fade", 1.5, tgt=1.50, stp=0.80)
    late = gap_rows("fade", 1.5, entry_bar=2, tgt=1.50, stp=0.80)
    opp = gap_rows("follow", 1.5, tgt=1.50, stp=0.80)
    run_sleeve("R3-10", "GAP-FADE @ >=1.5% with T150/S080 exits (the "
                        "reaction families' other geometry)", "GAP-FADE",
               rows, "GAP-FOLLOW", opp, late,
               note_extra=f"sign-split diagnostic inconclusive: LONG "
                          f"{d_long}, SHORT {d_short}; exit-geometry cell run")

print("WS5:", "combination re-gate required" if banked_any else
      "vacuous — no Round-3 bankings exist to combine; the ending book is "
      "the Round-2 ending book unchanged.")
print("Final incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)},
      "trades:", {yr: len(books[yr]) for yr in (2025, 2026)})
