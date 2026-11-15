#!/usr/bin/env python3
"""EOD frozen construction for 2026-11-13 November paper (primary+control).
Uses live_signal_producer functions with API bars. Paper only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from datetime import date
import live_signal_producer as P

day = date(2026,11,13)
out = {}
# V5 week: same ISO week as 2026-11-09. NIFTY had a V5 leg on 2026-11-09 -> week_used True for NIFTY.
# BANKNIFTY had no V5 leg Nov 9-12 -> week_used False for BANK.
week_used_map = {"BANKNIFTY": False, "NIFTY": True}
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
    week_used = week_used_map[sym]
    legs, notes = P.evaluate_legs(sym, own, conf, prev, prev2, week_used, sa, None)
    keys = P.merge_keys(legs)
    rec = {"bars": len(own), "first": own[0] if own else None, "last": own[-1] if own else None,
           "prev": prev, "prev2": prev2, "sessions_apart": sa, "week_used": week_used,
           "legs": legs, "notes": notes,
           "keys": {d: {"sources": k["sources"], "entry_time": k["entry_time"], "representative": k["representative"], "first_signal": k["first_leg"]["signal_time"]} for d,k in keys.items()}}
    if sym=="BANKNIFTY":
        rec["b2"] = {d: (not P.b2_drop(k)) for d,k in keys.items()}
        leg, why = P.ns1_second_leg(own, prev)
        rec["ns1"] = {"leg": leg, "why": why}
    out[sym]=rec
print(json.dumps(out, indent=1, default=str))
