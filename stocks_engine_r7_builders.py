#!/usr/bin/env python3
"""ROUND 7 shared builders — pre-registered in
stocks_engine_round7_2026-11-02.md before any scoring.

- certified_exclusions(): the R6-11-strengthened non-event set (the
  frozen R5 reaction-window set UNION every calendar event day, any
  event_type, with its reaction window; blanket window when the
  reaction date is unsourceable).
- rexp_rows(direction, cells): R6-09/R6-10's construction verbatim
  (stocks_engine_r6_ws3.build) plus the pre-registered regime-cell
  restriction. At (SHORT, cells=None) it must reproduce R6-10 exactly.
- nerev_gen(...): the NE-REV construction generalised only in its
  pre-registered parameters (signal/entry bar times, exclusion set,
  optional quiet-name filter). At (10:25 -> 10:35, thr 2.0, R5 set,
  no quiet filter) it must reproduce R5-07 exactly (asserted via
  stocks_engine_r6_builders.nerev_rows in the workstreams).
- disloc_rows(): the two-day dislocation reversal (WS3).
All entries are strictly after every input is knowable; violations
are counted per construction and returned, never defaulted.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade.
"""
import sys, csv
from statistics import median
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B
import stocks_engine_floor_lib as FL

LABELS = FL.LABELS
COST = 40.0
CALS = [f"{WS}/stock_event_calendar_2025.csv",
        f"{WS}/stock_event_calendar_jan_oct_2026.csv"]

def machinery():
    return B.machinery()

# ------------------------------------------------- certified non-event
_cert = None

def certified_exclusions():
    """Returns (certified_set, r5_set, added_set) of (sym, date)."""
    global _cert
    if _cert is not None:
        return _cert
    r5 = B.contaminated_set()
    g = machinery()
    STOCKS_E = g["STOCKS_E"]
    added = set()
    n_rows = 0
    for cal in CALS:
        for r in csv.DictReader(open(cal)):
            sym = r["stock"]
            if sym not in STOCKS_E:
                continue
            n_rows += 1
            daily = STOCKS_E[sym][1]
            didx = {d["date"]: i for i, d in enumerate(daily)}
            ev = r["event_date"][:10]
            added.add((sym, ev))
            rd = (r["reaction_date"] or "")[:10]
            if rd and rd in didx:
                j = didx[rd]
                added.add((sym, rd))
                for k in (1, 2):
                    if j + k < len(daily):
                        added.add((sym, daily[j + k]["date"]))
            elif ev in didx:
                j = didx[ev]
                for k in (1, 2, 3):
                    if j + k < len(daily):
                        added.add((sym, daily[j + k]["date"]))
    cert = r5 | added
    print(f"certified set: calendar rows used {n_rows}; R5 set "
          f"{len(r5)}; event-day additions {len(added - r5)}; "
          f"certified total {len(cert)} stock-days excluded")
    _cert = (cert, r5, added)
    return _cert

# ------------------------------------------------------------- REXP ----
FH_TIMES = ["09:15", "09:20", "09:25", "09:30", "09:35", "09:40",
            "09:45", "09:50", "09:55", "10:00", "10:05", "10:10"]

def _score_plain(replay_plain, bars, ei, sign, tgt, stp):
    entry = float(bars[ei]["open"])
    er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry,
                                         tgt, stp)
    return round(gross - COST, 2)

def rexp_rows(direction, cells=None):
    """Verbatim R6 WS3 build + optional regime-cell restriction.
    Returns (real, flipped, late, violations), each split by year."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    sign = 1 if direction == "LONG" else -1

    def score(bars, ei, s):
        return _score_plain(replay_plain, bars, ei, s, 1.25, 0.50)

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

# ------------------------------------------------------------ NE-REV ---
def nerev_gen(signal_time="10:25", entry_time="10:35", thr=2.0,
              excl=None, cells=None, quiet=False):
    """LONG fade of a >= thr% fall by the signal bar's close on
    certified non-event stock-days; entry at the open of the
    entry_time bar; T100/S065 via replay_plain (entry bar checked).
    Returns (real, flipped, late, violations, stats). late = same
    direction one bar after the entry bar (by bar index, the engine
    convention)."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    if excl is None:
        excl = certified_exclusions()[0]
    qmap = quiet_map() if quiet else None

    def score(bars, ei, s):
        return _score_plain(replay_plain, bars, ei, s, 1.00, 0.65)

    real, flipped, late = [], [], []
    violations = 0
    stats = {"population_days": 0, "signal_days": 0,
             "quiet_rejected": 0}
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day) or (sym, day) in excl:
                continue
            if cells is not None and LABELS.get(day) not in cells:
                continue
            stats["population_days"] += 1
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if signal_time not in idx or entry_time not in idx:
                continue
            si, ei = idx[signal_time], idx[entry_time]
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            move = (bars[si]["close"] / prev_close - 1) * 100
            if move > -thr:
                continue
            stats["signal_days"] += 1
            if quiet and not qmap.get((sym, day), False):
                stats["quiet_rejected"] += 1
                continue
            if ei <= si:
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("NE-REV", day, sym, "LONG", etime,
                               score(bars, ei, 1)))
            flipped.append(R.norm("NE-REV", day, sym, "SHORT", etime,
                                  score(bars, ei, -1)))
            if ei + 1 < len(bars):
                li = ei + 1
                late.append(R.norm("NE-REV", day, sym, "LONG",
                                   bars[li]["time"],
                                   score(bars, li, 1)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations, stats)

# ------------------------------------------------------- quiet filter --
_qmap = None

def quiet_map():
    """(sym, day) -> True if the name's trailing-20-session median
    daily range% is strictly below that day's watchlist median.
    Trailing data only: sessions strictly before the trade day."""
    global _qmap
    if _qmap is not None:
        return _qmap
    g = machinery()
    STOCKS_E = g["STOCKS_E"]
    char = {}
    for sym, (spot, daily) in STOCKS_E.items():
        rngs = [((d["high"] - d["low"]) / d["close"] * 100
                 if d["close"] else None) for d in daily]
        for i in range(20, len(daily)):
            vals = [v for v in rngs[i - 20:i] if v is not None]
            if len(vals) == 20:
                char[(sym, daily[i]["date"])] = median(vals)
    by_day = {}
    for (sym, day), v in char.items():
        by_day.setdefault(day, []).append(v)
    day_med = {day: median(vs) for day, vs in by_day.items()}
    _qmap = {k: v < day_med[k[1]] for k, v in char.items()}
    return _qmap

# ------------------------------------------------------------ DISLOC ---
def disloc_rows(excl=None):
    """Two-day dislocation reversal (WS3, pre-registered): cumulative
    move close[D-1]/close[D-3] - 1 <= -3.00%; D, D-1, D-2 all
    certified non-event; LONG at the open of D's 09:20 bar;
    T125/S050 via replay_plain. Returns (real, flipped, late,
    violations, stats)."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    if excl is None:
        excl = certified_exclusions()[0]

    def score(bars, ei, s):
        return _score_plain(replay_plain, bars, ei, s, 1.25, 0.50)

    real, flipped, late = [], [], []
    violations = 0
    stats = {"signal_days": 0, "skipped_no_0920": 0}
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(3, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            if ((sym, day) in excl
                    or (sym, daily[i - 1]["date"]) in excl
                    or (sym, daily[i - 2]["date"]) in excl):
                continue
            c1, c3 = daily[i - 1]["close"], daily[i - 3]["close"]
            if not c3:
                continue
            move = (c1 / c3 - 1) * 100
            if move > -3.0:
                continue
            stats["signal_days"] += 1
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "09:20" not in idx:
                stats["skipped_no_0920"] += 1
                continue
            ei = idx["09:20"]
            if bars[ei]["time"] != "09:20":
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("DISLOC-2D", day, sym, "LONG", etime,
                               score(bars, ei, 1)))
            flipped.append(R.norm("DISLOC-2D", day, sym, "SHORT",
                                  etime, score(bars, ei, -1)))
            if "09:25" in idx and idx["09:25"] > ei:
                li = idx["09:25"]
                late.append(R.norm("DISLOC-2D", day, sym, "LONG",
                                   bars[li]["time"],
                                   score(bars, li, 1)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations, stats)
