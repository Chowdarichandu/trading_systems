#!/usr/bin/env python3
"""NOVEMBER REGIME FIX — final assembly arithmetic (stored legs only):
REGIME-REV merge vs stack, IOI-1 full-window increment, merged day
counts, November merged tables, independent re-sums."""
import csv, json
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
def rd(fn):
    with open(TR / fn) as f:
        return list(csv.DictReader(f))

# stack day nets Jan-Oct (205 programme days from the OI calendar)
cal = [r["date"] for r in rd("oi_history/banknifty_daily_oi.csv")
       if "2026-01-01" <= r["date"] <= "2026-10-31"]
stack_by_day = defaultdict(float)
for r in rd("solid60_programme_2026-11-13_bank_A_stack_features.csv"):
    stack_by_day[r["date"]] += float(r["x1_net"])
stack_days = set(stack_by_day)

def merged_counts(incr_by_day):
    g = r = nt = 0
    tot = 0.0
    for d in cal:
        net = stack_by_day.get(d, 0.0) + incr_by_day.get(d, 0.0)
        tot += net
        if d in stack_by_day or d in incr_by_day:
            if net > 0: g += 1
            elif net < 0: r += 1
            else: nt += 1
        else:
            nt += 1
    return dict(total=round(tot, 2), green=g, red=r, no_trade=nt)

out = {}
# ---- REGIME-REV Bank merge ----
fam = json.load(open(TR / "november_regime_family_results.json"))
rev_legs = fam["BANKNIFTY_janoct"]["real_legs"]
rev_incr = [l for l in rev_legs if l["date"] not in stack_days]
rev_incr_by_day = defaultdict(float)
for l in rev_incr:
    rev_incr_by_day[l["date"]] += float(l["net"])
out["regime_rev_merge"] = dict(
    increment_legs=len(rev_incr),
    increment_total=round(sum(float(l["net"]) for l in rev_incr), 2),
    merged=merged_counts(rev_incr_by_day))
out["regime_rev_h1_legs"] = sum(1 for l in rev_legs if l["date"][:7] <= "2026-05")
out["regime_rev_h2_legs"] = sum(1 for l in rev_legs if l["date"][:7] >= "2026-06")
# re-sum from the written trades CSV
rs = [r for r in rd("november_regime_family_trades.csv") if r["book"] == "BANK_real"]
out["regime_rev_resum"] = round(sum(float(r["net"]) for r in rs), 2)
assert out["regime_rev_resum"] == 15872.0, out["regime_rev_resum"]

# ---- IOI-1 full-window increment (supplementary arithmetic) ----
ioi = rd("round5_ioi_trades.csv")
ioi1 = [r for r in ioi if r["family"] == "IOI-1" and r["mode"] == "real"
        and r["window"] == "JANOCT"]
ioi1_incr = [r for r in ioi1 if r["date"] not in stack_days]
ibd = defaultdict(float)
for r in ioi1_incr:
    ibd[r["date"]] += float(r["net"])
out["ioi1_increment"] = dict(
    legs=len(ioi1_incr), total=round(sum(float(r["net"]) for r in ioi1_incr), 2),
    merged=merged_counts(ibd))
ioi1_by_day = defaultdict(float)
for r in ioi1:
    ioi1_by_day[r["date"]] += float(r["net"])
out["ioi1_day_counts"] = dict(
    green=sum(1 for v in ioi1_by_day.values() if v > 0),
    red=sum(1 for v in ioi1_by_day.values() if v < 0),
    trade_days=len(ioi1_by_day))
ioi2 = [r for r in ioi if r["family"] == "IOI-2" and r["mode"] == "real"
        and r["window"] == "JANOCT"]
ioi2_by_day = defaultdict(float)
for r in ioi2:
    ioi2_by_day[r["date"]] += float(r["net"])
out["ioi2_day_counts"] = dict(
    green=sum(1 for v in ioi2_by_day.values() if v > 0),
    red=sum(1 for v in ioi2_by_day.values() if v < 0),
    trade_days=len(ioi2_by_day))

# ---- November merged tables ----
NOVD = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
        "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
nov_stack = {"2026-11-04": 2480.0, "2026-11-09": -1720.0,
             "2026-11-12": -1720.0, "2026-11-13": -1720.0}
def nov_merged(incr_by_day):
    rows = {}
    for d in NOVD:
        rows[d] = round(nov_stack.get(d, 0.0) + incr_by_day.get(d, 0.0), 2)
    act = {d: v for d, v in rows.items() if d in nov_stack or d in incr_by_day}
    return dict(total=round(sum(rows.values()), 2),
                green=sum(1 for v in act.values() if v > 0),
                red=sum(1 for v in act.values() if v < 0),
                no_trade=9 - len(act), days=rows)
# IOI-1 November increment (idle days only)
ioi1_nov = [r for r in rd("november_regime_ioi_nov_legs.csv")
            if r["family"] == "IOI-1" and r["status"] == "leg"]
ibd_nov = {r["date"]: float(r["net"]) for r in ioi1_nov
           if r["date"] not in nov_stack}
out["nov_ioi1"] = dict(increment_total=round(sum(ibd_nov.values()), 2),
                       merged=nov_merged(ibd_nov))
# REGIME-REV November increment (all 4 legs are on stack-idle days)
rev_nov = fam["BANKNIFTY_november"]["real_legs"]
rbd_nov = {l["date"]: float(l["net"]) for l in rev_nov
           if l["date"] not in nov_stack}
out["nov_regime_rev"] = dict(
    increment_total=round(sum(rbd_nov.values()), 2),
    merged=nov_merged(rbd_nov),
    legs=[dict(date=l["date"], side=l["side"], strike=l["strike"],
               conf_time=l["conf_time"], entry=l["entry"], exit=l["exit"],
               exit_reason=l["exit_reason"], net=l["net"]) for l in rev_nov])
print(json.dumps(out, indent=1))
with open(TR / "november_regime_assembly.json", "w") as f:
    json.dump(out, f, indent=1)
print("ASSEMBLY DONE")
