#!/usr/bin/env python3
"""ROUND 5 — signal census (DESCRIPTIVE ONLY, no legs, no P&L).
Computed after the Upstox HTTP 429 stopped the band build at
713/1,100 contracts. FLOW-VOL signals need only futures + spot
(both complete): full 205-day + November census. OPT-FLOW signals
need complete band mornings: census over the 104 complete Jan-Oct
days only, coverage-labelled. No API calls.
"""
import csv, json
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
R5H = TR / "round5_history"
ALL_EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
           "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
           "2026-09-29", "2026-10-27", "2026-11-23"]
MORN_TIMES = [f"{9 + (15 + 5 * i) // 60:02d}:{(15 + 5 * i) % 60:02d}"
              for i in range(21)]


def in_force(day):
    for e in ALL_EXP:
        if e >= day:
            return e
    return None


MF = {}
with open(R5H / "morning_flow.csv") as f:
    for r in csv.DictReader(f):
        MF[r["date"]] = r
JAN_OCT = sorted(d for d in MF if d <= "2026-10-31")
NOV = [d for d in ("2026-11-02", "2026-11-03", "2026-11-04",
                   "2026-11-05", "2026-11-06", "2026-11-09",
                   "2026-11-11", "2026-11-12", "2026-11-13") if d in MF]
ALL_DAYS = JAN_OCT + NOV
PRIOR = {d: (ALL_DAYS[i - 1] if i > 0 else "2025-12-31")
         for i, d in enumerate(ALL_DAYS)}

SPOT = {}
_raw = json.load(open(TR / "daily2leg/spot.json"))
for d, bars in _raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: float(b[4]) for b in bars}
for fn in (TR / "oi_history/spot_nov_bars.json",
           TR / "round4_history/spot_extra.json"):
    if fn.exists():
        data = json.loads(fn.read_text())
        if isinstance(data, dict) and "BANKNIFTY" in data:
            data = data["BANKNIFTY"]
        if isinstance(data, dict):
            for d, bars in data.items():
                if d not in SPOT and isinstance(bars, list) and bars:
                    SPOT[d] = {b[0]: float(b[4]) for b in bars}
_prog = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
if _prog.exists():
    with open(_prog) as f:
        for r in csv.DictReader(f):
            SPOT.setdefault(r["timestamp"][:10], {})[
                r["timestamp"][11:16]] = float(r["close"])

FUT = {}
for exp in ALL_EXP:
    fn = R5H / f"FUT7_{exp}.json"
    if fn.exists():
        byd = {}
        for r in json.loads(fn.read_text()):
            byd.setdefault(r[0], {})[r[1]] = r
        FUT[exp] = byd


def fut_morning(day):
    exp = in_force(day)
    bars = FUT.get(exp, {}).get(day, {})
    if any(t not in bars for t in MORN_TIMES):
        return None
    if any(bars[t][6] is None for t in MORN_TIMES):
        return None
    sday = SPOT.get(day, {})
    if "09:15" not in sday or "10:55" not in sday:
        return None
    v = sum(bars[t][6] for t in MORN_TIMES)
    return v, bars["09:15"][5] - sday["09:15"], \
        bars["10:55"][5] - sday["10:55"]


def flowvol(day):
    cur = fut_morning(day)
    if cur is None:
        return None
    pday = PRIOR[day]
    pbars = FUT.get(in_force(pday), {}).get(pday, {})
    if any(t not in pbars for t in MORN_TIMES) or \
            any(pbars[t][6] is None for t in MORN_TIMES):
        return None
    pv = sum(pbars[t][6] for t in MORN_TIMES)
    if pv <= 0:
        return None
    v, b0915, b1055 = cur
    ratio = v / pv
    db = b1055 - b0915
    sig = None
    if ratio >= 1.25 and db != 0:
        sig = "CE" if db > 0 else "PE"
    return {"ratio": round(ratio, 3), "dbasis": round(db, 2), "sig": sig}


out = {"flowvol_janoct": {}, "flowvol_nov": {}, "optflow_census": {}}
bym = defaultdict(lambda: {"days": 0, "thrust": 0, "CE": 0, "PE": 0})
fv_days = []
for d in JAN_OCT:
    r = flowvol(d)
    assert r is not None, d
    m = bym[d[:7]]
    m["days"] += 1
    if r["sig"]:
        m["thrust"] += 1
        m[r["sig"]] += 1
        fv_days.append({"date": d, **r})
out["flowvol_janoct"] = {"by_month": dict(bym), "signal_days": fv_days,
                         "n_signal_days": len(fv_days)}
for d in NOV:
    r = flowvol(d)
    out["flowvol_nov"][d] = r

comp = [d for d in JAN_OCT if MF[d]["complete"] == "True"]
of = {"complete_days": len(comp), "CE": 0, "PE": 0, "days": []}
for d in comp:
    row = MF[d]
    share = float(row["vol_share_CE"])
    sig = None
    if share >= 0.60 and float(row["dp_CE"]) > 0:
        sig = "CE"
    elif share <= 0.40 and float(row["dp_PE"]) > 0:
        sig = "PE"
    if sig:
        of[sig] += 1
        of["days"].append({"date": d, "side": sig,
                           "share_CE": share})
out["optflow_census"] = of

# stack overlap of FLOW-VOL signal days (descriptive)
stack_days = set()
for r in csv.DictReader(
        open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")):
    stack_days.add(r["date"])
out["flowvol_janoct"]["signal_days_on_stack_idle"] = sum(
    1 for x in fv_days if x["date"] not in stack_days)

(R5H / "round5_census.json").write_text(json.dumps(out, indent=1))
print(json.dumps({"flowvol_signals_janoct": len(fv_days),
                  "on_stack_idle": out["flowvol_janoct"]
                  ["signal_days_on_stack_idle"],
                  "optflow_complete_days": len(comp),
                  "optflow_signals": of["CE"] + of["PE"],
                  "flowvol_nov_signals": {d: (v or {}).get("sig")
                                          for d, v in
                                          out["flowvol_nov"].items()}},
                 indent=1))
