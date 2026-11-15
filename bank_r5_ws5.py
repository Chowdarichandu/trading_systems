#!/usr/bin/env python3
"""Cycles 133-134 — WS5: bias-conditioned exit split on the audited baseline.
Bias = prior trading day's closing strength cs = (close-low)/(high-low)*100
(causal). Cell A (133): bearish-day (cs<35) legs with a runner lock get
lock:=+40. Cell B (134): bullish-day (cs>=80) legs with a second target get
tgt2:=+130. Two cells, frozen in the Round-5 appendix before scoring."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
import newsetups_score as ns
from bank_r3_setups import generate as gen_setups

ref = c.aud_ref()
pooled, ns1 = c.aud_inputs()
print(f"REF_AUD: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")

daily = ns.DATA["BANKNIFTY"][1]
D = {str(d)[:10]: (float(h), float(l), float(cl))
     for d, h, l, cl in zip(daily["date"], daily["high"], daily["low"], daily["close"])}
DL = sorted(D)
CS = {}
for i in range(1, len(DL)):
    h, l, cl = D[DL[i - 1]]
    CS[DL[i]] = (cl - l) / (h - l) * 100.0 if h > l else 50.0

def cellA(row, leg):
    if CS.get(row["date"], 50.0) < 35.0 and row["_params"].get("lock") is not None:
        p = dict(row["_params"]); p["lock"] = 40.0; return p
    return None

def cellB(row, leg):
    if CS.get(row["date"], 50.0) >= 80.0 and row["_params"].get("tgt2") is not None:
        p = dict(row["_params"]); p["tgt2"] = 130.0; return p
    return None

gen = gen_setups()
still = c.fetch_missing(pooled + ns1 + c.ns3_legs(causal=True) +
                        gen["S3A"] + gen["S3E"] + gen["S3D"])
assert not still
for cyc, name, fn in ((133, "bearish-day lock:=40", cellA),
                      (134, "bullish-day tgt2:=130", cellB)):
    res = c.judge(f"C{cyc} {name}", ref, pooled, ns1, ns3_causal_form=True,
                  ns3_filter=c.GDGU, ns3_params=c.GEO, geometry_override=fn)
    print("   detail:", res["detail"])
