#!/usr/bin/env python3
"""Cycle 115 (completion): the WS0 causal rebuild = REF_AUD.
Causal solo rule on the pool, causal (signal+5) NS1 and NS3 entries,
everything else frozen-identical to v19. Full controls in the same run."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r2_core import controls, write_trades
from bank_r3_setups import generate as gen_setups

TR = Path.home() / "workspace/trading"
pooled, ns1 = c.aud_inputs()
gen = gen_setups()
still = c.fetch_missing(pooled + ns1 + c.ns3_legs(causal=True) +
                        gen["S3A"] + gen["S3E"] + gen["S3D"])
print("still missing after fetch:", still)

rows, nc, lbk, detail, plan = c._assemble(pooled, ns1, delay=0, ns3_causal_form=True,
                                          ns3_filter=c.GDGU, ns3_params=c.GEO)
prows, pnc, _pl, _pd, _p2 = c._assemble(pooled, ns1, delay=6, ns3_causal_form=True,
                                        ns3_filter=c.GDGU, ns3_params=c.GEO, plan=plan)
ctrl = controls(rows, nc, lbk, prows, pnc)
resum = write_trades(rows, "bank_engine_r5_causal_trades.csv")
ctrl["independent_resum"] = resum
ctrl["resum_matches"] = (resum["n"] == ctrl["n"] and abs(resum["net"] - ctrl["net"]) < 0.005)
print("detail:", detail)
print(json.dumps(ctrl, indent=1, default=str))

v19 = {}
for r in csv.DictReader(open(TR / "bank_engine_r4_v19_trades.csv")):
    v19[(r["date"], r["direction"], r["entry_time"])] = (r["family"], float(r["net_inr"]))
aud = {(r["date"], r["direction"], r["entry_time"]): (r["family"], r["net"]) for r in rows}
print("\n--- leg diff vs v19 ---")
for k in sorted(set(v19) | set(aud)):
    a, b = v19.get(k), aud.get(k)
    if a != b:
        print(k, "v19:", a, "-> audited:", b)
print("v19 net", round(sum(v for _, v in v19.values()), 2),
      "-> audited net", round(sum(v for _, v in aud.values()), 2))
