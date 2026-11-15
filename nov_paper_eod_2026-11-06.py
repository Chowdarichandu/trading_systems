#!/usr/bin/env python3
"""EOD frozen construction for 2026-11-06 November paper (primary+control).
Uses live_signal_producer functions (same as Nov 2-5 construction) with API bars.
Paper only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from datetime import date
import live_signal_producer as P

day = date(2026,11,6)
out = {}
for sym in ("BANKNIFTY","NIFTY"):
    own = P.fetch_intraday(sym)
    conf = P.fetch_intraday("NIFTY" if sym=="BANKNIFTY" else "BANKNIFTY")
    daily = P.fetch_daily(sym)
    rows = [r for r in daily if r["date"] < day.isoformat()]
    prev, prev2 = rows[-1], rows[-2]
    last_v = P.VOLRIX_LAST_ENTRY[sym]
    dates = [r["date"] for r in daily]
    sa = None
    if last_v in dates:
        dates_before = [d for d in dates if d < day.isoformat()]
        if last_v in dates_before:
            sa = len(dates_before) - dates_before.index(last_v)
    week_used = False  # Nov 2-5 (same ISO week) had no V5 leg for either index per producer log / EOD notes; producer state v5_week is {} for 2026-11-06
    legs, notes = P.evaluate_legs(sym, own, conf, prev, prev2, week_used, sa, None)
    keys = P.merge_keys(legs)
    rec = {"bars": len(own), "first": own[0] if own else None, "last": own[-1] if own else None,
           "prev": prev, "prev2": prev2, "sessions_apart": sa,
           "legs": legs, "notes": notes,
           "keys": {d: {"sources": k["sources"], "entry_time": k["entry_time"], "representative": k["representative"], "first_signal": k["first_leg"]["signal_time"]} for d,k in keys.items()}}
    if sym=="BANKNIFTY":
        rec["b2"] = {d: (not P.b2_drop(k)) for d,k in keys.items()}
        leg, why = P.ns1_second_leg(own, prev)
        rec["ns1"] = {"leg": leg, "why": why}
    rec["spot_at"] = {}
    for b in own:
        rec["spot_at"][b["time"]]=b
    out[sym]=rec
print(json.dumps(out, indent=1, default=str))
