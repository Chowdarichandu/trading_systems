#!/usr/bin/env python3
"""ROUND 5 WS2/WS3/WS4 cycles (freezes in nifty_engine_frozen.md Round 5).
Baseline CURRENT = the WS0 causal book (+50,618.00). Every candidate runs
the full controls gate in the same run via run_r5. Missing candles are
fetched via the expired-instruments route, then re-checked; anything
still missing is NOT_COMPUTED, named, never estimated."""
import sys, json
from pathlib import Path
from datetime import date as _d
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r5_harness import run_r5, set_current, BOOK_GEOM
from nifty_engine_r5_ws0 import causal_legs, dte0_population
from nifty_engine_r2_harness import candles_exact
import nifty_engine_r5_fetch as F

TR = Path.home() / "workspace/trading"

def set_baseline():
    c = json.loads((TR / "nifty_engine_run3r5_run3r5_ws0_causal_summary.json").read_text())
    set_current(c, "WS0 causal book (adopted book read causally) +50,618.00")
    return c

def dte(leg):
    y, m, dd = map(int, leg["date"].split("-")); ey, em, ed = map(int, leg["expiry"].split("-"))
    return (_d(ey, em, ed) - _d(y, m, dd)).days

def ensure_candles(legs, weekly=False):
    missing = []
    for l in legs:
        if not candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"]):
            missing.append(l)
    fetched = []
    for l in missing:
        r = F.fetch_one(l["strike"], l["direction"], l["date"], l["expiry"], weekly=weekly)
        fetched.append((l["date"], l["direction"], l["strike"], l["expiry"], r))
    still = [l for l in missing
             if not candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])]
    return fetched, still

def shifted(leg, pts=100):
    nl = dict(leg)
    nl["strike"] = leg["strike"] - pts if leg["direction"] == "CE" else leg["strike"] + pts
    return nl

if __name__ == "__main__":
    which = sys.argv[1]
    set_baseline()
    base = causal_legs()
    if which == "ws2":
        # Cycle 103 — ITM100 blanket
        legs = [shifted(l) for l in base]
        fetched, still = ensure_candles(legs)
        print("C103 fetches:", fetched, "| still missing:", [(l['date'], l['direction'], l['strike']) for l in still])
        run_r5("run3r5_c103_itm100", legs)
        # Cycle 104 — ITM100 expiry-scoped (DTE <= 4)
        legs2 = [shifted(l) if dte(l) <= 4 else dict(l) for l in base]
        fetched2, still2 = ensure_candles(legs2)
        print("C104 fetches:", fetched2, "| still missing:", [(l['date'], l['direction'], l['strike']) for l in still2])
        run_r5("run3r5_c104_itm100_expiry", legs2)
    elif which == "ws3":
        pop, excluded = dte0_population()
        print("WS3 population:", [(l["date"], l["direction"], l["entry_time"], l["strike"]) for l in pop], "| excluded:", excluded)
        fetched, still = ensure_candles(pop)
        print("WS3 fetches:", fetched, "| still missing:", [(l['date'], l['direction'], l['strike']) for l in still])
        popkeys = {(l["date"], l["direction"]) for l in pop}
        def with_pop(geom_fn):
            legs = [dict(l) for l in base] + [dict(l) for l in pop]
            def g(l):
                if (l["date"], l["direction"]) in popkeys: return geom_fn()
                return BOOK_GEOM
            return legs, g
        # Cycle 105 — control: population at book geometry
        legs, g = with_pop(lambda: BOOK_GEOM)
        run_r5("run3r5_c105_dte0_control", legs, geom_by_leg=g)
        # Cycle 106 — square-off 14:30 on population
        legs, g = with_pop(lambda: dict(BOOK_GEOM, sq="14:30"))
        run_r5("run3r5_c106_dte0_sq1430", legs, geom_by_leg=g)
        # Cycle 107 — square-off 15:00 on population
        legs, g = with_pop(lambda: dict(BOOK_GEOM, sq="15:00"))
        run_r5("run3r5_c107_dte0_sq1500", legs, geom_by_leg=g)
        # Cycle 108 — BE arm +40 on population
        legs, g = with_pop(lambda: dict(BOOK_GEOM, arm=40.0))
        run_r5("run3r5_c108_dte0_arm40", legs, geom_by_leg=g)
        # Cycle 109 — runner lock +40 on population
        legs, g = with_pop(lambda: dict(BOOK_GEOM, lock=40.0))
        run_r5("run3r5_c109_dte0_lock40", legs, geom_by_leg=g)
    elif which == "ws4":
        # Cycle 110 — Cell A: entry > 11:00 -> lock +40
        def gA(l): return dict(BOOK_GEOM, lock=40.0) if l["entry_time"] > "11:00" else BOOK_GEOM
        run_r5("run3r5_c110_split_late_lock40", base, geom_by_leg=gA)
        # Cycle 111 — Cell B: entry <= 11:00 -> lock +40
        def gB(l): return dict(BOOK_GEOM, lock=40.0) if l["entry_time"] <= "11:00" else BOOK_GEOM
        run_r5("run3r5_c111_split_early_lock40", base, geom_by_leg=gB)
    elif which == "ws3cont":
        # Cycle 112 (contingency) — population at sq 15:00 + arm +40
        pop, _ = dte0_population()
        ensure_candles(pop)
        popkeys = {(l["date"], l["direction"]) for l in pop}
        legs = [dict(l) for l in base] + [dict(l) for l in pop]
        def g(l):
            return dict(BOOK_GEOM, sq="15:00", arm=40.0) if (l["date"], l["direction"]) in popkeys else BOOK_GEOM
        run_r5("run3r5_c112_dte0_sq1500_arm40", legs, geom_by_leg=g)
