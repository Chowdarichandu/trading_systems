#!/usr/bin/env python3
"""ROUND 6 WS3 (Cycles 142-143) + WS4 (Cycle 144).

WS3 — BANK GAP SLEEVE (new family, pre-registered here before scoring):
population = every trading day 2026-01-01..2026-10-28 whose overnight
gap |open / prior close - 1| >= 0.50% (open = the 09:15 bar's open print).
FOLLOW: gap up -> CE, gap down -> PE. FADE: the opposite direction.
Entry 09:35 (open of the 09:35 premium bar), strike = ATM at the 09:35
spot open (the book's own strike convention), expiry in force, exits =
book add-on exits (stream-state segment geometry; PLAIN on expiry day),
admission = the pipeline's sequential UNIQUE-ONCE + premium-band rules.
CAUSALITY CERTIFICATE: the gap is fully determined by the prior close
(known) and the 09:15 open print (printed at 09:15); the 09:35 entry is
strictly after both. No same-day information beyond 09:15 is used.

WS4 — BANK EXPIRY-DAY SLEEVE (new family, pre-registered before scoring):
population = B1 representatives (earliest component leg per (date,
direction), from the v20 component set incl. regenerated Volrix cd15)
on the 10 monthly expiry dates in EXPIRIES, entry in [09:15, 11:00].
CAUSALITY CERTIFICATE: a representative enters at its own system's
entry (signal+5, or 09:20 on a prior-day trigger) — knowable at that
bar; the sleeve applies NO end-of-day set-membership test (the V-SK
error is not repeated); admission against book keys is sequential.
If the representative population is < 8 legs: record and close."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r6_core as c
from bank_r6_core import judge6, v20_inputs, v20_ref, GDGU, GEO
from aggressive_score import EXPIRIES

ref = v20_ref()
pooled, ns1 = v20_inputs()
print(f"v20 ref: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")

# ---------- WS3 legs ----------
DAY_LIST, DAY_CLOSE, SPOT_OPEN = c5.DAY_LIST, c5.DAY_CLOSE, c5.SPOT_OPEN
def gap_legs(fade):
    legs = []
    for i in range(1, len(DAY_LIST)):
        date, prev = DAY_LIST[i], DAY_LIST[i - 1]
        if not ("2026-01-01" <= date <= "2026-10-28"): continue
        o = SPOT_OPEN.get((date, "09:15"))
        e = SPOT_OPEN.get((date, "09:35"))
        if o is None or e is None: continue
        gap = o / DAY_CLOSE[prev] - 1.0
        if abs(gap) < 0.005: continue
        d = "CE" if gap > 0 else "PE"
        if fade: d = "PE" if d == "CE" else "CE"
        legs.append(c5.mkleg(date, d, "09:35", c5.atm(e), c5.expiry_for(date),
                             "GAP_FADE" if fade else "GAP_FOLLOW",
                             family="GAP_FADE" if fade else "GAP_FOLLOW",
                             _gap=round(gap * 100, 3)))
    return legs

follow, fade = gap_legs(False), gap_legs(True)
print(f"WS3 population: {len(follow)} gap days >= 0.50%")
still = c5.fetch_missing(pooled + ns1 + follow + fade)
print("still missing:", still)
assert not still
r = judge6("C142 GAP FOLLOW", ref, pooled, ns1, ns3_causal_form=True,
           ns3_filter=GDGU, ns3_params=GEO,
           extra_families=[("GAPF", follow, None)])
print("   detail:", [d for d in r["detail"] if d["family"] == "GAPF"])
r = judge6("C143 GAP FADE", ref, pooled, ns1, ns3_causal_form=True,
           ns3_filter=GDGU, ns3_params=GEO,
           extra_families=[("GAPD", fade, None)])
print("   detail:", [d for d in r["detail"] if d["family"] == "GAPD"])

# ---------- WS4 legs ----------
comps = c5.component_legs(volrix=c5.volrix_gen_legs(-0.01, 15))
exp_days = [e for e in EXPIRIES if "2026-01-01" <= e <= "2026-10-28"]
by_key = {}
for l in comps:
    if l["date"] not in exp_days: continue
    if not ("09:15" <= l["entry_time"] <= "11:00"): continue
    k = (l["date"], l["direction"])
    if k not in by_key or l["entry_time"] < by_key[k]["entry_time"]:
        by_key[k] = l
exp_legs = []
for l in sorted(by_key.values(), key=lambda x: (x["date"], x["entry_time"])):
    l2 = dict(l); l2["family"] = "EXP_DAY"; l2["rep"] = "EXP_DAY"
    exp_legs.append(l2)
print(f"WS4 expiry dates: {exp_days}")
print(f"WS4 representative population: {len(exp_legs)} legs")
for l in exp_legs:
    print(f"   {l['date']} {l['direction']} {l['entry_time']} strike {l['strike']} (src {l['sources']})")
if len(exp_legs) < 8:
    print("C144 NOT RUN — population < 8, family recorded and closed.")
else:
    still = c5.fetch_missing(pooled + ns1 + exp_legs)
    print("still missing:", still)
    assert not still
    r = judge6("C144 EXPIRY-DAY sleeve", ref, pooled, ns1, ns3_causal_form=True,
               ns3_filter=GDGU, ns3_params=GEO,
               extra_families=[("EXP", exp_legs, None)])
    print("   detail:", [d for d in r["detail"] if d["family"] == "EXP"])
