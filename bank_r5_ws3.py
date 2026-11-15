#!/usr/bin/env python3
"""Cycles 122-124 — WS3: Skill-solo early-leg re-admission on the audited
pipeline. Population (frozen): B1 keys whose source systems are exactly
{Skill V3}, entry <= 09:55, absent from B2 — 72 legs (51 CE, 21 PE).
Cells: (a) PE only, (b) CE only, (c) room_ratio >= 1.5 at the leg's own
signal bar (levels = prior-day PDH/PDC/PDL; risk = |entry_spot - stop_spot|
from the Skill source record; October legs: signal-bar extreme)."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
import newsetups_score as ns
from bank_r3_setups import generate as gen_setups

ref = c.aud_ref()
print(f"REF_AUD: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")

comps0 = c.component_legs()
groups = defaultdict(list)
for l in comps0: groups[(l["date"], l["direction"])].append(l)
b2keys = {(l["date"], l["direction"]) for l in c.pool_b2(comps0, solo_rule="eod")}
pop = []
for k, ls in groups.items():
    if {x["rep"] for x in ls} == {"Skill V3"}:
        l = ls[0]
        if l["entry_time"] <= "09:55" and k not in b2keys:
            pop.append((l["date"], l["direction"], l["entry_time"]))
popset = set(pop)
print(f"population {len(pop)} legs")

# room ratios for cell (c)
jansep = {(r["date"], r["direction"]): r for r in c.load_csv("index_options_U1_skillV3_jansep_spot.csv")
          if r["index"] == "BANKNIFTY"}
tuned = {(r["date"], r["direction"]): r for r in c.load_csv("index_options_skill_tuned_oct30_trades.csv")
         if r["index"] == "BANKNIFTY" and r["variant"] == "V3"}
_daily = ns.DATA["BANKNIFTY"][1]
RAW_DATE = {str(d)[:10]: d for d in _daily["date"]}
def room_ok(leg):
    info = ns.day_info("BANKNIFTY", RAW_DATE[leg["date"]])
    if info is None: return False
    sig = leg.get("_signal") or ""
    bar = next((b for b in info["bars"] if b["time"] == sig), None)
    if bar is None: return False
    key = (leg["date"], leg["direction"])
    if key in jansep:
        r = jansep[key]
        risk = abs(float(r["entry_spot"]) - float(r["stop_spot"]))
    else:
        r = tuned.get(key)
        espot = float(r["entry_spot"]) if r else c.SPOT_OPEN.get((leg["date"], leg["entry_time"]))
        if espot is None: return False
        stop = bar["low"] if leg["direction"] == "CE" else bar["high"]
        risk = abs(espot - stop)
    if not risk: return False
    rr, _room = ns.room_ratio(bar["close"], leg["direction"], info, risk)
    return rr >= 1.5

def variant_pooled(selector):
    comps = c.component_legs()
    n_flag = 0
    for l in comps:
        if (l["date"], l["direction"], l["entry_time"]) in popset and selector(l):
            l["_readmit"] = True; n_flag += 1
    return c.pool_b2(comps, solo_rule="causal"), n_flag

cells = [
    (122, "PE only", lambda l: l["direction"] == "PE"),
    (123, "CE only", lambda l: l["direction"] == "CE"),
    (124, "room>=1.5 at signal bar", room_ok),
]
_ns1 = c.aud_inputs()[1]
gen = gen_setups()
variants = {}
for cyc, name, sel in cells:
    pooled_v, n_flag = variant_pooled(sel)
    variants[cyc] = pooled_v
    print(f"C{cyc} {name}: flagged {n_flag} population legs; pooled {len(pooled_v)}")
all_legs = _ns1 + c.ns3_legs(causal=True) + gen["S3A"] + gen["S3E"] + gen["S3D"]
for v in variants.values(): all_legs += v
still = c.fetch_missing(all_legs)
print("still missing:", still)
assert not still
for cyc, name, sel in cells:
    res = c.judge(f"C{cyc} readmit {name}", ref, variants[cyc], _ns1,
                  ns3_causal_form=True, ns3_filter=c.GDGU, ns3_params=c.GEO)
    print("   detail:", res["detail"])
