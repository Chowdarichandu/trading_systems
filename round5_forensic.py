#!/usr/bin/env python3
"""ROUND 5 PHASE 1 — November forensic map for the NEW series only
(descriptive; derives no rule). Reads morning_flow.csv (Nov rows) and
FUT5N_NOV.json (November futures full-field 5-min). Prints the table
for new_data_round5_2026-11-14.md.
"""
import csv, json
from pathlib import Path

TR = Path.home() / "workspace/trading"
R5H = TR / "round5_history"
NOV = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
       "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
       "2026-11-13"]

MF = {}
with open(R5H / "morning_flow.csv") as f:
    for r in csv.DictReader(f):
        MF[r["date"]] = r

fut = {}
for r in json.loads((R5H / "FUT7_2026-11-23.json").read_text()):
    fut.setdefault(r[0], {})[r[1]] = r  # [date,time,o,h,l,c,vol,oi]

stack = {}
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r["net_inr"]:
            stack[r["date"]] = (r["direction"], float(r["net_inr"]))


def quadrant(doi, dp):
    if doi == 0 or dp == 0:
        return "FLAT"
    if doi > 0 and dp > 0:
        return "LB"
    if doi > 0 and dp < 0:
        return "SB"
    if doi < 0 and dp > 0:
        return "SC"
    return "LU"


for d in NOV:
    row = MF.get(d)
    fb = fut.get(d, {})
    fvol = sum(r[6] for t, r in fb.items()
               if "09:15" <= t <= "10:55" and r[6] is not None)
    foi = None
    if "09:15" in fb and "10:55" in fb:
        foi = fb["10:55"][7] - fb["09:15"][7]
    st = stack.get(d)
    print(f"== {d}  stack: "
          f"{(st[0] + ' ' + format(st[1], '+.0f')) if st else 'no-trade'}")
    print(f"   FUT morning vol={fvol:,.0f}  fut dOI(09:15->10:55)="
          f"{foi if foi is None else format(foi, '+,.0f')}")
    if row is None or row["complete"] != "True":
        print("   options band: INCOMPLETE (NC)")
        continue
    qc = quadrant(float(row["doi_CE"]), float(row["dp_CE"]))
    qp = quadrant(float(row["doi_PE"]), float(row["dp_PE"]))
    share = float(row["vol_share_CE"])
    print(f"   CE dOI={float(row['doi_CE']):+,.0f} dP={float(row['dp_CE']):+.2f} [{qc}]"
          f" | PE dOI={float(row['doi_PE']):+,.0f} dP={float(row['dp_PE']):+.2f} [{qp}]")
    print(f"   vol CE={float(row['vol_CE']):,.0f} PE={float(row['vol_PE']):,.0f}"
          f" share_CE={share:.2f}")
    io1 = ("CE" if qc == "LB" and qp != "LB" else
           "PE" if qp == "LB" and qc != "LB" else "-")
    io2 = ("CE" if qc == "SC" and qp != "LB" else
           "PE" if qp == "SC" and qc != "LB" else "-")
    flow = ("CE" if share >= 0.60 and float(row["dp_CE"]) > 0 else
            "PE" if share <= 0.40 and float(row["dp_PE"]) > 0 else "-")
    print(f"   would-be signals (descriptive only): IOI-1={io1} "
          f"IOI-2={io2} OPT-FLOW={flow}")
