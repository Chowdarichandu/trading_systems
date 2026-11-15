#!/usr/bin/env python3
"""ROUND 6 fetch: contracts absent from the local store, needed by the
WS1 grid cells and WS2 solo books — same expired-instruments route as
Rounds 3–5 (browser UA, token read inside nifty_engine_r5_fetch, never
printed). The 2026-10-28 22500 PE job is the named NOT_COMPUTED leg
(weekly expiry 2026-11-03): it is attempted once through the route; if
the registry again yields nothing it stays NOT_COMPUTED, named, never
estimated. Paper only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r5_fetch import fetch_one

JOBS = [  # (strike, type, day, expiry, weekly)
    (23300, "PE", "2026-05-18", "2026-05-26", False),
    (23500, "PE", "2026-06-01", "2026-06-30", False),
    (23900, "CE", "2026-06-24", "2026-06-30", False),
    (24100, "PE", "2026-03-11", "2026-03-30", False),
    (24100, "PE", "2026-04-16", "2026-04-28", False),
    (24200, "PE", "2026-08-24", "2026-08-25", False),
    (26000, "PE", "2026-01-08", "2026-01-27", False),
    (22500, "PE", "2026-10-28", "2026-11-03", True),   # named NC leg — one route attempt
]

if __name__ == "__main__":
    for strike, typ, day, exp, wk in JOBS:
        print((strike, typ, day, exp, "weekly" if wk else "monthly"), fetch_one(strike, typ, day, exp, weekly=wk))
