#!/usr/bin/env python3
"""Cycles 118-121 — WS2: NS1 permutations on the audited-baseline pipeline.
One axis at a time vs REF_AUD: room {1.4, 1.6} at window 14:30; window
{14:00, 15:00} at room 1.5. Sanity first: gen at (1.5, 14:30) pooled against
the causal B2 must reproduce the audited baseline's NS1 set exactly."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from aggressive_score import unique_once
from bank_r3_setups import generate as gen_setups

pooled, ns1_base = c.aud_inputs()
ref = c.aud_ref()
print(f"REF_AUD: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']} "
      f"freq={ref['per_week']}/wk placebo={ref['placebo']['net']:+,.2f}")

cells = [(118, 1.4, "14:30"), (119, 1.6, "14:30"),
         (120, 1.5, "14:00"), (121, 1.5, "15:00")]
gen_sets = {}
for cyc, room, win in cells:
    gen_sets[cyc] = c.ns1_gen_legs(room, win)[0]
gen_base = c.ns1_gen_legs(1.5, "14:30")[0]

# sanity: the assembled baseline book's NS1 rows == the audited baseline
# trades CSV (Cycle 115) — validates the WS2 input path end to end
import csv
_ = c.aud_ref()
surv = {(r["date"], r["direction"], r["entry_time"], r["net"])
        for r in c._AUD["rows"] if r["family"].startswith("NS1")}
want = {(r["date"], r["direction"], r["entry_time"], float(r["net_inr"]))
        for r in csv.DictReader(open("bank_engine_r5_causal_trades.csv"))
        if r["family"].startswith("NS1")}
print(f"sanity NS1 assembled {len(surv)} vs audited book {len(want)}; diff {sorted(surv ^ want)[:6]}")
assert surv == want, "WS2 sanity failed — stop"

gen = gen_setups()
all_legs = pooled + ns1_base + c.ns3_legs(causal=True) + gen["S3A"] + gen["S3E"] + gen["S3D"]
for s in gen_sets.values(): all_legs += s
still = c.fetch_missing(all_legs)
print("still missing:", still)
assert not still, "unfetchable legs — would be NOT_COMPUTED"

for cyc, room, win in cells:
    res = c.judge(f"C{cyc} NS1 room={room} window={win}", ref, pooled, gen_sets[cyc],
                  ns3_causal_form=True, ns3_filter=c.GDGU, ns3_params=c.GEO)
    print("   detail:", res["detail"])
