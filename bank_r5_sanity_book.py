#!/usr/bin/env python3
"""Stage-2 sanity: build_book on frozen inputs must reproduce v19 per-leg."""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r3_setups import generate as gen_setups

TR = Path.home() / "workspace/trading"
comps = c.component_legs()
pooled = c.pool_b2(comps, solo_rule="eod")
ns1 = c.ns1_recorded_legs()
gen = gen_setups()
all_legs = pooled + ns1 + c.ns3_legs(causal=False) + gen["S3A"] + gen["S3E"] + gen["S3D"]
still = c.fetch_missing(all_legs)
print("still missing:", still)

rows, nc, lbk, detail, plan = c._assemble(pooled, ns1, delay=0, ns3_causal_form=False,
                                          ns3_filter=c.GDGU, ns3_params=c.GEO)
print("detail:", detail, "nc:", nc)
want = {}
for r in csv.DictReader(open(TR / "bank_engine_r4_v19_trades.csv")):
    want[(r["date"], r["direction"], r["entry_time"])] = float(r["net_inr"])
got = {(r["date"], r["direction"], r["entry_time"]): r["net"] for r in rows}
print(f"rows {len(rows)} net {sum(r['net'] for r in rows):+,.2f} vs v19 {len(want)} {sum(want.values()):+,.2f}")
mism = [(k, got.get(k), want.get(k)) for k in set(got) | set(want)
        if got.get(k) is None or want.get(k) is None or abs(got[k] - want[k]) > 0.005]
print("per-leg mismatches:", len(mism), mism[:8])

prows, pnc, _pl, _pd, _p2 = c._assemble(pooled, ns1, delay=6, ns3_causal_form=False,
                                        ns3_filter=c.GDGU, ns3_params=c.GEO, plan=plan)
from bank_engine_run2_cycle14 import stream_keys
base6 = {r["leg_key"] for r in prows if r["family"] in ("BASE",) or r["family"].startswith("NS1")}
print("placebo rows", len(prows), "net", round(sum(r['net'] for r in prows), 2),
      "pool keys == stream_keys(6):", base6 == set(stream_keys(6)))
