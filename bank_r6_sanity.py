#!/usr/bin/env python3
"""ROUND 6 sanity + Cycle 136 (WS1 decomposition) + WS2 decomposition data.
Reproduce REF_AUD and v20 exactly through the Round-5 machinery, then
decompose v20 by family / rep / NS3 subleg at causal times.
Certification: every number below is produced by bank_r5_core's causal
pipeline (causal-solo B2 pool, NS1 regenerated at causal entries,
NS3 at signal+5); no Round 1-4 magnitude is cited as evidence."""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r2_core import controls, gate

# --- REF_AUD reproduction ---
ref = c.aud_ref()
print(f"REF_AUD reproduced: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']} "
      f"placebo={ref['placebo']['net']:+,.2f} nc={ref['not_computed']}")
assert abs(ref["net"] - 69940.50) < 0.005 and ref["n"] == 102, "REF_AUD mismatch"

# --- v20 reproduction (Round-5 WS6 build path) ---
_ns1 = c.aud_inputs()[1]
comps = c.component_legs(volrix=c.volrix_gen_legs(-0.01, 15))
pooled20 = c.pool_b2(comps, solo_rule="causal")
rows, nc, lbk, detail, plan = c._assemble(pooled20, _ns1, delay=0,
                                          ns3_causal_form=True,
                                          ns3_filter=c.GDGU, ns3_params=c.GEO)
prows, pnc, _pl, _pd, _p2 = c._assemble(pooled20, _ns1, delay=6,
                                        ns3_causal_form=True,
                                        ns3_filter=c.GDGU, ns3_params=c.GEO,
                                        plan=plan)
v20 = controls(rows, nc, lbk, prows, pnc)
print(f"v20 reproduced: net={v20['net']:+,.2f} n={v20['n']} FT90={v20['ft90_pct']} "
      f"per_week={v20['per_week_raw']} placebo={v20['placebo']['net']:+,.2f} "
      f"ex_top3={v20['ex_top3_total']:+,.2f} nc={v20['not_computed']} "
      f"viol={len(v20['timing_violations'])}")
assert abs(v20["net"] - 78250.50) < 0.005 and v20["n"] == 99, "v20 mismatch"
ok, why = gate(v20, ref)
print(f"v20 gate vs REF_AUD: {ok} {why}")
print("assemble detail:", detail)

# --- Cycle 136: family decomposition of v20 (causal times) ---
def decomp(rows, keyfn, label):
    agg = defaultdict(lambda: [0, 0.0, 0])
    for r in rows:
        k = keyfn(r)
        agg[k][0] += 1
        agg[k][1] += r["net"]
        agg[k][2] += r.get("ft90", 0)
    print(f"--- {label} ---")
    for k in sorted(agg):
        n, net, ft = agg[k]
        print(f"  {k}: {n} legs, net {net:+,.2f}, FT90 legs {ft}")
    return {k: (v[0], round(v[1], 2)) for k, v in agg.items()}

fam = decomp(rows, lambda r: r["family"], "v20 by family")
rep = decomp(rows, lambda r: r["rep"], "v20 by rep")

# NS3 subleg split needs the leg objects: rebuild lbk lookup per row
ns3_rows = [r for r in rows if r["family"].startswith("NS3")]
print(f"NS3 rows in v20: {len(ns3_rows)}")
sub = defaultdict(lambda: [0, 0.0])
for r in ns3_rows:
    leg = lbk.get(r["leg_key"])
    s = leg.get("_subleg") if leg else None
    if s is None and leg is not None:
        s = c.enrich(leg)["_subleg"]
    sub[s][0] += 1
    sub[s][1] += r["net"]
for k in sorted(sub, key=lambda x: str(x)):
    print(f"  NS3 subleg {k}: {sub[k][0]} legs, net {sub[k][1]:+,.2f}")

s3 = {k: v for k, v in fam.items() if k.startswith("S3")}
print("WS2 decomposition (S3 families in v20):", s3)
json.dump({"ref": {"net": ref["net"], "n": ref["n"]},
           "v20": {"net": v20["net"], "n": v20["n"], "ft90": v20["ft90_pct"]},
           "family": fam, "rep": rep,
           "ns3_subleg": {str(k): v for k, v in sub.items()}},
          open("bank_r6_decomp.json", "w"), indent=1, default=str)
print("saved bank_r6_decomp.json")
