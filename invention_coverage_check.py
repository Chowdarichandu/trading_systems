#!/usr/bin/env python3
"""Coverage pre-check for the invention round: Bank option_5m.csv store."""
import glob
import pandas as pd

EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28", "2026-05-26",
       "2026-06-30", "2026-07-28", "2026-08-25", "2026-09-29", "2026-10-27",
       "2026-11-23"]

frames = []
for f in sorted(glob.glob("data/banknifty-2026-*/option_5m.csv")):
    frames.append(pd.read_csv(f, usecols=["timestamp", "strike", "option_type", "expiry"]))
opt = pd.concat(frames)
opt["date"] = opt["timestamp"].str[:10]
opt["time"] = opt["timestamp"].str[11:16]

spot_frames = []
for f in sorted(glob.glob("data/banknifty-2026-*/spot_5m.csv")):
    spot_frames.append(pd.read_csv(f, usecols=["timestamp", "open", "high", "low", "close"]))
spot = pd.concat(spot_frames).sort_values("timestamp")
print("spot rows:", len(spot), "dup timestamps:", int(spot.duplicated(subset=["timestamp"]).sum()))
spot = spot.drop_duplicates(subset=["timestamp"], keep="first")
spot["date"] = spot["timestamp"].str[:10]
spot["time"] = spot["timestamp"].str[11:16]
spot = spot[spot["date"] <= "2026-10-31"]

contracts = {}
for (d, e), g in opt.groupby(["date", "expiry"]):
    contracts[(d, e)] = set(zip(g["strike"], g["option_type"]))

s1300 = spot[spot["time"] == "13:00"].set_index("date")["close"]
days = sorted(s1300.index)
ok, bad = 0, []
for d in days:
    exp = next(e for e in EXP if e >= d)
    atm = int(round(float(s1300[d]) / 100.0) * 100)
    tset = contracts.get((d, exp), set())
    if (atm, "CE") in tset and (atm, "PE") in tset:
        ok += 1
    else:
        bad.append((d, atm, (atm, "CE") in tset, (atm, "PE") in tset))
print("days with 13:00 spot bar:", len(days))
print("ATM strike present both types (13:00):", ok, " missing:", len(bad))
for b in bad[:15]:
    print("  missing:", b)

# afternoon bar completeness for ATM contracts: bars from 12:00 to 15:10
sub = opt[(opt["date"] == "2026-06-15") & (opt["time"] >= "12:00")]
print("2026-06-15 afternoon bars per contract: min",
      sub.groupby(["strike", "option_type"]).size().min(),
      "max", sub.groupby(["strike", "option_type"]).size().max())

# overall: how many bars does a typical contract-day have (full day)?
full = opt.groupby(["date", "strike", "option_type", "expiry"]).size()
print("contract-day bar counts: min", full.min(), "p5", full.quantile(0.05),
      "median", full.median(), "max", full.max())
print("contract-days with <70 bars:", int((full < 70).sum()), "of", len(full))
