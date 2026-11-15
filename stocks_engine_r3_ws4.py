#!/usr/bin/env python3
"""ROUND 3 — WS4 NEW MECHANISM CLASSES (frozen constructions).

R3-05 GAP-FOLLOW / R3-06 GAP-FADE: overnight gap |gap| >= 1.5% (day open
vs prior daily close) on the 25; entry at the 09:20 bar open; exits
T125/S050 via the event-family replay (entry bar unchecked, square-off
15:10) — the P2F open-entry convention. One trade per stock-day.
Direction diagnostic pre-registered: H1 (Jan-Jun, both years pooled) and
H2 (Jul-Oct, both years pooled) standalone expectancy per direction;
BOTH directions are then gated as separate candidates regardless.
Placebos per candidate: the opposite direction's book; the same
direction entered one bar later (09:25 open).

R3-07 ORB-STOCK: opening range = 09:15-09:30 bars' high/low; first
5-min bar at/after 09:30 closing beyond the range (signal bar start
<= 11:25) sets direction; entry next bar open (<= 11:30); exits
T125/S050 via replay_plain (entry bar checked — the F4/N4 signal-bar
convention). One trade per stock-day. Placebos: flipped (fade) book;
entry one further bar late.

Universal filters only for the new sleeves: weekend bars excluded.
No component law sets apply (new families). Disclosure: the closed
lesson-2 lines (price-derived events / R2 follow-through & gaps, old
LH/RH S/R constructions) are different constructions; these sleeves are
tried once each under the brief's order and judged by the gate alone.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r3_lib as R3
import stocks_engine_floor_lib as FL

g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay, replay_plain = g["STOCKS_E"], g["replay"], g["replay_plain"]
SYMBOLS = g["SYMBOLS"]
books = R3.load_books()
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def book_total(bk):
    return round(sum(sum(t["net"] for t in bk[yr]
                         if t["date"] <= f"{yr}-10-31")
                     for yr in (2025, 2026)), 2)

# ------------------------------------------------------------ GAP sleeve --
def gap_rows(mode, entry_bar=1):
    """mode: 'follow' or 'fade'. Returns split book rows (comp GAP-*)."""
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
            if abs(gap) < 1.5:
                continue
            natural = "LONG" if gap > 0 else "SHORT"
            direction = natural if mode == "follow" else (
                "SHORT" if natural == "LONG" else "LONG")
            entry = bars[entry_bar]["open"]
            r = replay(bars, entry_bar, entry, direction, 1.25, 0.5)
            if r is None:
                continue
            er, ep, et = r
            comp = "GAP-FOLLOW" if mode == "follow" else "GAP-FADE"
            out.append(R.norm(comp, day, sym, direction,
                              bars[entry_bar]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

follow = gap_rows("follow")
fade = gap_rows("fade")
follow_late = gap_rows("follow", entry_bar=2)
fade_late = gap_rows("fade", entry_bar=2)

def expectancy(rows_by_yr):
    out = {}
    for half, months in (("H1", range(1, 7)), ("H2", range(7, 11))):
        sel = [t for yr in (2025, 2026) for t in rows_by_yr[yr]
               if int(t["date"][5:7]) in months]
        out[half] = (len(sel), round(sum(t["net"] for t in sel) / len(sel), 2)
                     if sel else None,
                     round(sum(t["net"] for t in sel), 2))
    return out

diag = {"GAP-FOLLOW": expectancy(follow), "GAP-FADE": expectancy(fade)}
print("GAP diagnostic (n, expectancy/trade, total) per half, both years pooled:")
for k, v in diag.items():
    print(f"  {k}: H1 {v['H1']}  H2 {v['H2']}")
print("GAP standalone Jan-Oct totals:",
      {c: {str(yr): round(sum(t['net'] for t in rows[yr]
                              if t['date'] <= f'{yr}-10-31'), 2)
           for yr in (2025, 2026)}
       for c, rows in (("FOLLOW", follow), ("FADE", fade))})

for cyc, mode, rows, late in (("R3-05", "follow", follow, follow_late),
                              ("R3-06", "fade", fade, fade_late)):
    comp = "GAP-FOLLOW" if mode == "follow" else "GAP-FADE"
    other = fade if mode == "follow" else follow
    other_comp = "GAP-FADE" if mode == "follow" else "GAP-FOLLOW"
    var_books = R3.add_comp(books, comp, rows)
    pl_other = R3.add_comp(books, other_comp, other)
    pl_late = R3.add_comp(books, comp, late)
    pl = [book_total(pl_other), book_total(pl_late)]
    out = R3.gate(books, var_books, pl)
    R3.record(cyc, f"NEW SLEEVE {comp} (gap >=1.5%, entry 09:20 open, "
                   f"T125/S050)", out,
              note=f"diagnostic H1/H2 expectancy {diag[comp]}; placebos: "
                   f"opposite-direction book {pl[0]}; one-bar-late entry "
                   f"book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var_books
        R3.save_books(books)
        print("    -> BANKED")

# ------------------------------------------------------------ ORB sleeve --
def orb_rows(flip=False, late=False):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            bars = spot.get(day, [])
            or_bars = [c for c in bars if c["time"] in ("09:15", "09:20", "09:25")]
            if len(or_bars) < 3:
                continue
            or_high = max(c["high"] for c in or_bars)
            or_low = min(c["low"] for c in or_bars)
            sig = None
            for j, c in enumerate(bars):
                if c["time"] <= "09:25" or c["time"] > "11:25":
                    continue
                if c["close"] > or_high:
                    sig = (j, "LONG")
                    break
                if c["close"] < or_low:
                    sig = (j, "SHORT")
                    break
            if sig is None:
                continue
            j, direction = sig
            ei = j + 1 + (1 if late else 0)
            if ei >= len(bars) or bars[ei]["time"] > "11:30":
                continue
            if flip:
                direction = "SHORT" if direction == "LONG" else "LONG"
            entry = float(bars[ei]["open"])
            sign = 1 if direction == "LONG" else -1
            er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry, 1.25, 0.5)
            out.append(R.norm("ORB-STOCK", day, sym, direction,
                              bars[ei]["time"], round(gross - COST, 2)))
    return R.split_years(out)

orb = orb_rows()
orb_flip = orb_rows(flip=True)
orb_late = orb_rows(late=True)
print("ORB standalone Jan-Oct totals:",
      {str(yr): round(sum(t['net'] for t in orb[yr]
                          if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)},
      "trades:", {str(yr): len(orb[yr]) for yr in orb})
var_books = R3.add_comp(books, "ORB-STOCK", orb)
pl = [book_total(R3.add_comp(books, "ORB-STOCK", orb_flip)),
      book_total(R3.add_comp(books, "ORB-STOCK", orb_late))]
out = R3.gate(books, var_books, pl)
R3.record("R3-07", "NEW SLEEVE ORB-STOCK (09:15-09:30 range break close, "
                   "entry next bar open <=11:30, T125/S050)", out,
          note=f"placebos: flipped (fade) book {pl[0]}; one-bar-later "
               f"entry book {pl[1]}",
          extra={"standalone": {str(yr): round(sum(t['net'] for t in orb[yr]), 2)
                                for yr in orb}})
if out["verdict"]:
    books = var_books
    R3.save_books(books)
    print("    -> BANKED")
print("WS4 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
