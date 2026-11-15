#!/usr/bin/env python3
"""Diagnostics for nifty_next_phase_score.py (decision support only —
nothing here is a candidate): (1) correct entry-bar presence check for
the 97 base legs; (2) ALL re-entry triggers with the day-cap NOT applied
(real and +60-min placebo), their nets/halves/ex-top-3/whipsaws;
(3) the cap variant excluding the anchor leg itself; (4) base exit
anatomy; (5) brute-force trigger cross-check on sample stop days."""
import json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nps", Path.home() / "workspace/trading/nifty_next_phase_score.py")
# import as a module would re-run everything; instead re-implement the
# small pieces by exec'ing only the definitions up to STEP 0 marker.
src = (Path.home() / "workspace/trading/nifty_next_phase_score.py") \
    .read_text().split("# ---------------- STEP 0")[0]
g = {}
exec(src, g)
prem_day, replay, merged_day = g["prem_day"], g["replay"], g["merged_day"]
SPOT, STIMES, BASE_LEGS = g["SPOT"], g["STIMES"], g["BASE_LEGS"]

# (1) entry-bar presence, correct check
bad = []
for l in BASE_LEGS:
    bars, _ = prem_day(l["expiry"], l["strike"], l["direction"],
                       l["date"], l["component"])
    times = {b[0] for b in bars} if bars else set()
    if l["entry_time"] not in times or "15:20" not in times:
        bad.append((l["date"], l["component"], l["entry_time"],
                    l["entry_time"] in times, "15:20" in times))
print(f"(1) base legs missing entry or 15:20 bar: {len(bad)} {bad}")

# base results from the scorer's own output file (single source of truth)
res = json.loads((Path.home() / "workspace/trading"
                  / "nifty_next_phase_results.json").read_text())
trades = {}
import csv
for row in csv.DictReader(open(Path.home() / "workspace/trading"
                               / "nifty_next_phase_trades.csv")):
    if row["set"] == "BASE":
        trades.setdefault(row["date"], []).append(row)

# (4) exit anatomy
anat = defaultdict(lambda: [0, 0.0])
for rows in trades.values():
    for r in rows:
        anat[r["exit_reason"]][0] += 1
        anat[r["exit_reason"]][1] += float(r["net_inr"])
print("(4) base exit anatomy:", {k: (v[0], round(v[1], 2))
                                 for k, v in sorted(anat.items())})

# (2)/(3) triggers without cap + cap-excluding-anchor
def realised(d, trig, exclude=None):
    return round(sum(float(r["net_inr"]) for r in trades.get(d, [])
                     if r["exit_time"] <= trig and r is not exclude), 2)

def anchor_of(d):
    stops = [r for r in trades.get(d, []) if r["exit_reason"] == "stop"]
    if not stops:
        return None
    return sorted(stops, key=lambda r: (r["exit_time"], r["entry_time"]))[0]

def find(d, shift=0):
    a = anchor_of(d)
    if not a:
        return None
    side = a["direction"]
    b, ts = SPOT[d], STIMES[d]
    mh = max(b[t][1] for t in ts if t <= "11:55")
    ml = min(b[t][2] for t in ts if t <= "11:55")
    start = g["add_min"](max("12:00", a["exit_time"]), shift)
    for t in ts:
        if t < start:
            continue
        c = b[t][3]
        if (side == "CE" and c > mh) or (side == "PE" and c < ml):
            return dict(side=side, trig=t, anchor=a)
    return None

def build(d, f):
    ts = STIMES[d]
    i = ts.index(f["trig"])
    et = ts[i + 1] if i + 1 < len(ts) else None
    if et is None or et > "15:20":
        return None, "no_time"
    a = f["anchor"]
    strike = g["atm100"](SPOT[d][et][0])
    bars, tag = merged_day(a["expiry"], strike, f["side"], d, a["component"])
    if bars is None:
        return None, tag
    times = {b[0] for b in bars}
    if et not in times or "15:20" not in times:
        return None, "incomplete_day"
    r = replay(bars, et)
    if r is None:
        return None, "replay_none"
    return dict(date=d, trig=f["trig"], entry_time=et, net=r["net"],
                exit_reason=r["exit_reason"]), "ok"

stop_days = sorted(trades_d for trades_d in trades
                   if any(r["exit_reason"] == "stop"
                          for r in trades[trades_d]))
for label, shift, capmode in (("NO-CAP", 0, "none"),
                              ("PLACEBO+60 NO-CAP", 60, "none"),
                              ("CAP-EXCL-ANCHOR", 0, "excl")):
    legs, nc, blocked = [], [], 0
    for d in stop_days:
        f = find(d, shift)
        if not f:
            continue
        if capmode == "excl":
            a = f["anchor"]
            others = round(sum(float(r["net_inr"])
                                 for r in trades.get(d, [])
                                 if r["exit_time"] <= f["trig"]
                                 and r is not a), 2)
            if others <= -3000.0:
                blocked += 1
                continue
        leg, st = build(d, f)
        if leg:
            legs.append(leg)
        else:
            nc.append((d, st))
    tot = round(sum(x["net"] for x in legs), 2)
    h1 = round(sum(x["net"] for x in legs if x["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(x["net"] for x in legs if x["date"][:7] >= "2026-06"), 2)
    t3 = sorted((x["net"] for x in legs), reverse=True)[:3]
    wh = sum(1 for x in legs if x["exit_reason"] == "stop")
    print(f"({label}) triggers->legs {len(legs)} total {tot:+,.2f} "
          f"halves {h1:+,.2f}/{h2:+,.2f} ex-top3 "
          f"{round(tot - sum(t3), 2):+,.2f} double-stops {wh} "
          f"blocked {blocked} NC {nc}")
    for x in legs:
        print(f"    {x['date']} trig {x['trig']} entry {x['entry_time']} "
              f"{x['exit_reason']} {x['net']:+,.2f}")

# (5) brute-force cross-check on the 3 stop days with the largest |day net|
big = sorted(stop_days,
             key=lambda d: -abs(sum(float(r["net_inr"])
                                    for r in trades[d])))[:3]
for d in big:
    a = anchor_of(d)
    b, ts = SPOT[d], STIMES[d]
    mh = max(b[t][1] for t in ts if t <= "11:55")
    ml = min(b[t][2] for t in ts if t <= "11:55")
    side = a["direction"]
    hits = [t for t in ts if t >= max("12:00", a["exit_time"])
            and ((side == "CE" and b[t][3] > mh)
                 or (side == "PE" and b[t][3] < ml))]
    print(f"(5) {d} anchor {side} stop-exit {a['exit_time']} "
          f"morning range [{ml}, {mh}] reclaim bars: {hits[:3]}")
