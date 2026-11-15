#!/usr/bin/env python3
"""ROUND 7 WS4 — STRIKE AXIS ON THE CAUSAL BOOK (Cycles 158-159).

Every v21 leg re-scored at 100 pts ITM relative to its traded strike:
CE strike -100, PE strike +100 (the root method's expiry-day strike
rule, tested as book geometry). Two cells:
  C158 (a) BLANKET — every leg shifted;
  C159 (b) EXPIRY-DAY-SCOPED — only legs whose trade date == expiry.
The shift applies to the whole construction: pooled members, NS1,
NS3 candidates and the S3 setups (their generators are patched for the
duration of the cell and restored after; the frozen leg objects are
copied, never mutated). Premium-band admission, UNIQUE-ONCE, segment
geometry and square-off then run on the ITM premium series exactly as
the frozen pipeline runs on ATM.
Real ITM premium candles come via the expired-instruments route
(bank_r3_fetch). Legs whose candles cannot be fetched are
NOT_COMPUTED, named in the output — and per the brief a cell with
NC > 0 is REPORTED, never banked, whatever the gate prints.
CAUSALITY CERTIFICATE: a strike choice is an order parameter fixed
before the entry bar; entries, admissions and exit bars are the frozen
causal ones — only the premium series changes.
Nifty's causal strike verdict (R5: closed) is NOT imported."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r6_core as c6
import bank_r7_core as c7
from bank_r7_core import judge7, v21_ref
from bank_r6_core import v20_inputs

ORIG_NS3 = c6.ns3_legs
ORIG_GEN = c6.gen_setups

def shifted(leg, expiry_only):
    l = dict(leg)
    if expiry_only and l["date"] != l["expiry"]:
        return l
    l["strike"] = int(l["strike"]) + (-100 if l["direction"] == "CE" else 100)
    return l

def apply_patch(expiry_only):
    c6.ns3_legs = lambda causal=False: [shifted(l, expiry_only)
                                        for l in ORIG_NS3(causal=causal)]
    c6.gen_setups = lambda: {k: [shifted(l, expiry_only) for l in v]
                             for k, v in ORIG_GEN().items()}

def restore():
    c6.ns3_legs = ORIG_NS3
    c6.gen_setups = ORIG_GEN

def run_cell(name, expiry_only, ref, pooled, ns1):
    sp = [shifted(l, expiry_only) for l in pooled]
    sn = [shifted(l, expiry_only) for l in ns1]
    apply_patch(expiry_only)
    try:
        ns3c = c6.ns3_legs(causal=True)
        gens = c6.gen_setups()
        targets = sp + sn + ns3c + [l for v in gens.values() for l in v]
        still = c5.fetch_missing(targets)
        changed = [t for t in targets]
        print(f"{name}: fetch still-missing: {still}")
        r = judge7(name, ref, sp, sn)
        nc_detail = sum(d["nc_legs"] for d in r["detail"])
        nc_pool = r.get("nc", 0)
        print(f"   NC accounting: pooled/ns1 nc={nc_pool} addon nc={nc_detail} "
              f"still-missing={len(still)}")
        if nc_pool or nc_detail or still:
            print("   VERDICT: NC > 0 — REPORTED, NOT BANKED (brief rule).")
        return r
    finally:
        restore()

ref = v21_ref()
pooled, ns1 = v20_inputs()
run_cell("C158 STRIKE ITM-100 BLANKET", False, ref, pooled, ns1)
run_cell("C159 STRIKE ITM-100 EXPIRY-DAY ONLY", True, ref, pooled, ns1)
chk = judge7("POST-RESTORE CHECK (must equal v21 exactly)", ref, pooled, ns1)
print(f"restore check: printed line above must read net=+83,650.50 n=99 "
      f"(judge return keys: {sorted(chk.keys())})")
