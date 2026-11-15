#!/usr/bin/env python3
"""ROUND 8 shared builders — pre-registered in
stocks_engine_round8_2026-11-02.md before any scoring.

- nifty_bars()/nifty_prior_close(): NIFTY 5-min closes and prior-day
  closes (full_hist, sarvaritu_fwd supplement — the FL convention).
- drive_rows(sign_mode): WS1 drive-continuation. sign_mode=+1 builds
  the LONG form (10:25-bar move >= +thr% -> LONG at 10:35 open);
  sign_mode=-1 builds the frozen SHORT twin (move <= -thr% ->
  SHORT). T125/S050 via replay_plain. Population: the certified
  non-event set (Round-7 definition, unchanged).
- rexp_geo(direction, cells, tgt, stp): the REXP construction
  verbatim from stocks_engine_r7_builders.rexp_rows with the exit
  geometry parameterised (Round 7 hardcoded T125/S050). At
  (SHORT, {DOWN}, 1.25, 0.50) it must reproduce R7-03 exactly.
All entries are strictly after every input is knowable; violations
are counted per construction and returned, never defaulted.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade.
"""
import sys, csv
from statistics import median
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
FH = f"{WS}/data/full_hist"
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B
import stocks_engine_r7_builders as B7

COST = 40.0

def machinery():
    return B.machinery()

# ------------------------------------------------------------ NIFTY ----
_nifty = None

def nifty_data():
    """Returns (bars, prior_close): bars[day] = {time: close};
    prior_close[day] = previous trading day's NIFTY close."""
    global _nifty
    if _nifty is not None:
        return _nifty
    bars = {}
    with open(f"{FH}/NIFTY/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            day = r["timestamp"][:10]
            bars.setdefault(day, {})[r["timestamp"][11:16]] = \
                float(r["close"])
    daily = {}
    with open(f"{FH}/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily[r["date"][:10]] = float(r["close"])
    with open(f"{WS}/data/sarvaritu_fwd/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.setdefault(r["date"][:10], float(r["close"]))
    days = sorted(daily)
    prior = {days[i]: daily[days[i - 1]] for i in range(1, len(days))}
    _nifty = (bars, prior)
    return _nifty

def nifty_move(day, bar_time):
    """NIFTY % move of the close of the bar timestamped `bar_time`
    vs the prior trading day's close; None when either input is
    missing (state unknown — never guessed)."""
    bars, prior = nifty_data()
    pc = prior.get(day)
    day_bars = bars.get(day, {})
    if pc is None or bar_time not in day_bars or not pc:
        return None
    return (day_bars[bar_time] / pc - 1) * 100

# ------------------------------------------------------------ DRIVE ----
def drive_rows(sign_mode=+1, thr=2.0, excl=None):
    """WS1: follow the morning drive on certified non-event days.
    sign_mode=+1: move by the 10:25 bar close >= +thr% -> LONG at
    the open of the 10:35 bar. sign_mode=-1 (frozen twin): move
    <= -thr% -> SHORT at 10:35. T125/S050 via replay_plain (entry
    bar checked). Returns (real, flipped, late, violations, stats);
    flipped = opposite direction on the same population/entry;
    late = same direction one bar after the entry bar."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    if excl is None:
        excl = B7.certified_exclusions()[0]
    direction = "LONG" if sign_mode > 0 else "SHORT"

    def score(bars, ei, s):
        entry = float(bars[ei]["open"])
        er, ep, et, xi, gross = replay_plain(bars, ei, s, entry,
                                             1.25, 0.50)
        return round(gross - COST, 2)

    real, flipped, late = [], [], []
    violations = 0
    stats = {"population_days": 0, "signal_days": 0}
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day) or (sym, day) in excl:
                continue
            stats["population_days"] += 1
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "10:25" not in idx or "10:35" not in idx:
                continue
            si, ei = idx["10:25"], idx["10:35"]
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            move = (bars[si]["close"] / prev_close - 1) * 100
            if sign_mode > 0 and move < thr:
                continue
            if sign_mode < 0 and move > -thr:
                continue
            stats["signal_days"] += 1
            if ei <= si:
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("DRIVE", day, sym, direction, etime,
                               score(bars, ei, sign_mode)))
            flipped.append(R.norm(
                "DRIVE", day, sym,
                "SHORT" if direction == "LONG" else "LONG", etime,
                score(bars, ei, -sign_mode)))
            if ei + 1 < len(bars):
                li = ei + 1
                late.append(R.norm("DRIVE", day, sym, direction,
                                   bars[li]["time"],
                                   score(bars, li, sign_mode)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations, stats)

# ------------------------------------------------------------- REXP ----
FH_TIMES = B7.FH_TIMES

def rexp_geo(direction, cells=None, tgt=1.25, stp=0.50):
    """REXP construction verbatim (Round-7 builder) with exit
    geometry parameterised. Returns (real, flipped, late,
    violations), each split by year."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    sign = 1 if direction == "LONG" else -1
    LABELS = B7.LABELS

    def score(bars, ei, s):
        entry = float(bars[ei]["open"])
        er, ep, et, xi, gross = replay_plain(bars, ei, s, entry,
                                             tgt, stp)
        return round(gross - COST, 2)

    real, flipped, late = [], [], []
    violations = 0
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        fh = []
        for d in daily:
            day = d["date"]
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if all(t in idx for t in FH_TIMES):
                seg = [bars[idx[t]] for t in FH_TIMES]
                rng = (max(b["high"] for b in seg)
                       - min(b["low"] for b in seg))
                fh.append((day, rng, bars, idx))
            else:
                fh.append((day, None, bars, idx))
        ranges = [r for _, r, _, _ in fh if r is not None]
        seen = 0
        for day, rng, bars, idx in fh:
            if rng is None:
                continue
            pos_in_ranges = seen
            seen += 1
            if R._wk(day) or pos_in_ranges < 20 or rng <= 0:
                continue
            window = ranges[pos_in_ranges - 20:pos_in_ranges]
            med = median(window)
            if not med or rng / med < 2.0:
                continue
            seg = [bars[idx[t]] for t in FH_TIMES]
            hi = max(b["high"] for b in seg)
            lo = min(b["low"] for b in seg)
            if hi <= lo:
                continue
            pos = (seg[-1]["close"] - lo) / (hi - lo)
            if direction == "LONG" and pos < 0.75:
                continue
            if direction == "SHORT" and pos > 0.25:
                continue
            if cells is not None and LABELS.get(day) not in cells:
                continue
            if "10:20" not in idx:
                continue
            si, ei = idx["10:10"], idx["10:20"]
            if ei <= si:
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("REXP", day, sym, direction, etime,
                               score(bars, ei, sign)))
            flipped.append(R.norm(
                "REXP", day, sym,
                "SHORT" if direction == "LONG" else "LONG", etime,
                score(bars, ei, -sign)))
            if "10:25" in idx and idx["10:25"] > ei:
                li = idx["10:25"]
                late.append(R.norm("REXP", day, sym, direction,
                                   bars[li]["time"],
                                   score(bars, li, sign)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations)
