#!/usr/bin/env python3
"""ROUND 6 shared builders — the exact Round-3/4/5 constructions,
generalised only where Round 6's pre-registration names a parameter.

gap_rows: verbatim from stocks_engine_r5_ws1_ws2.py (Sarvaritu `replay`,
entry by bar position; gap = bar-0 open / prior close - 1). Adds two
optional, pre-registered parameters used only by WS2: `band` (fade-LONG
rows with gap in [-hi, -lo) instead of gap <= -thr) and `entry_time`
(select the entry bar by its time label instead of position).

nerev_rows: verbatim population from stocks_engine_r5_ws3.py (non-event
contamination set, 10:25-bar signal, replay_plain T100/S065), with the
pre-registered Round-6 parameters: threshold, entry bar time, optional
regime-cell restriction. At (thr=2.0, entry "10:35", cells=None) it must
reproduce R5-07 exactly — the workstreams assert that anchor.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R

LABELS = R.LABELS
COST = 40.0

_g = None
def machinery():
    global _g
    if _g is None:
        _g = L.load_machinery(L.FULLHIST, "2026-10-28")
    return _g

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

# ------------------------------------------------------------ gap sleeve
def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None,
             cells=None, comp_name=None, band=None, entry_time=None):
    """band=(lo, hi): keep fade rows with -hi < gap <= -lo (the WS2
    increment). entry_time: pick the entry bar by time label; returns
    rows whose day lacks that bar are dropped (counted by caller via
    the population builder if needed)."""
    g = machinery()
    STOCKS_E, replay = g["STOCKS_E"], g["replay"]
    SYMBOLS = g["SYMBOLS"]
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
            if entry_time is not None:
                idx = {b["time"]: k for k, b in enumerate(bars)}
                if entry_time not in idx:
                    continue
                eb = idx[entry_time]
            else:
                eb = entry_bar
            if len(bars) <= eb:
                continue
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            gap = (bars[0]["open"] / prev_close - 1) * 100
            if band is not None:
                lo, hi = band
                if not (-hi < gap <= -lo):
                    continue
            elif abs(gap) < thr:
                continue
            natural = "LONG" if gap > 0 else "SHORT"
            direction = natural if mode == "follow" else (
                "SHORT" if natural == "LONG" else "LONG")
            if only_dir and direction != only_dir:
                continue
            entry = bars[eb]["open"]
            r = replay(bars, eb, entry, direction, tgt, stp)
            if r is None:
                continue
            er, ep, et = r
            comp = comp_name or ("GAP-FOLLOW" if mode == "follow"
                                 else "GAP-FADE")
            out.append(R.norm(comp, day, sym, direction,
                              bars[eb]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

# ------------------------------------------------------------- NE-REV ----
_CALS = [(f"{WS}/stock_event_calendar_2025.csv", "2025-01-01", "2025-12-31"),
         (f"{WS}/stock_event_calendar_jan_oct_2026.csv", "2026-01-01",
          "2026-12-31")]
_contaminated = None

def contaminated_set():
    global _contaminated
    if _contaminated is not None:
        return _contaminated
    g = machinery()
    STOCKS_E = g["STOCKS_E"]
    rc = g["reaction_candidates"]
    contaminated = set()
    n_events = 0
    for cal, lo, hi in _CALS:
        for c in rc(cal, lo, hi):
            n_events += 1
            sym, ri = c["symbol"], c["ri"]
            daily = STOCKS_E[sym][1]
            for j in (0, 1, 2):
                if ri + j < len(daily):
                    contaminated.add((sym, daily[ri + j]["date"]))
    print(f"reaction candidates pooled: {n_events}; contaminated "
          f"stock-days: {len(contaminated)}")
    _contaminated = contaminated
    return contaminated

def nerev_rows(thr=2.0, entry_time="10:35", cells=None):
    """Returns (real, flipped, late, violations): LONG rows fading a
    >= thr% fall by the 10:25 bar close on non-event stock-days, entry
    at the open of the `entry_time` bar; flipped = SHORT on the same
    population/entry; late = LONG one bar after the entry bar.
    violations counts rows whose entry bar is not strictly after the
    10:25 signal bar (derived, never defaulted)."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    contaminated = contaminated_set()
    real, flipped, late = [], [], []
    violations = 0

    def score(bars, ei, sign):
        entry = float(bars[ei]["open"])
        er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry,
                                             1.00, 0.65)
        return round(gross - COST, 2)

    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day) or (sym, day) in contaminated:
                continue
            if cells is not None and LABELS.get(day) not in cells:
                continue
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "10:25" not in idx or entry_time not in idx:
                continue
            si, ei = idx["10:25"], idx[entry_time]
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            move = (bars[si]["close"] / prev_close - 1) * 100
            if move > -thr:
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
                                   bars[li]["time"], score(bars, li, 1)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations)
