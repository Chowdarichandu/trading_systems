#!/usr/bin/env python3
"""Spot-store integrity audit for the invention round (Bank)."""
import glob
import pandas as pd

monthly_files = [f for f in sorted(glob.glob("data/banknifty-2026-*/spot_5m.csv"))
                 if "jul-oct" not in f and "2026-11" not in f]
frames = [pd.read_csv(f) for f in monthly_files]
spot_m = pd.concat(frames)
print("monthly-dirs rows:", len(spot_m), "dup ts:", int(spot_m.duplicated(subset=["timestamp"]).sum()))
spot_m = spot_m.drop_duplicates(subset=["timestamp"], keep="first")
print("distinct days Jan-Oct (monthly dirs):", spot_m["timestamp"].str[:10].nunique())

jo = pd.read_csv("data/banknifty-2026-jul-oct/spot_5m.csv")
m = spot_m.set_index("timestamp")
both = 0
diff = 0
for _, r in jo.iterrows():
    ts = r["timestamp"]
    if ts in m.index:
        both += 1
        o = m.loc[ts]
        if not (float(o["open"]) == float(r["open"]) and float(o["high"]) == float(r["high"])
                and float(o["low"]) == float(r["low"]) and float(o["close"]) == float(r["close"])):
            diff += 1
print(f"jul-oct rows overlapping monthly dirs: {both}, value-different: {diff}")
print("jul-oct days not in monthly dirs:",
      sorted(set(jo["timestamp"].str[:10]) - set(spot_m["timestamp"].str[:10])))

# full trading calendar from Nifty daily (same exchange calendar)
nd = pd.read_csv("data/full_hist/NIFTY/spot_daily.csv")
cal = sorted(d for d in nd["date"] if "2026-01-01" <= d <= "2026-10-31")
bank_days = set(spot_m["timestamp"].str[:10])
print("NSE calendar days Jan-Oct (per Nifty daily):", len(cal))
print("Bank store missing calendar days:", [d for d in cal if d not in bank_days])
print("Bank store days not in calendar:", sorted(bank_days - set(cal)))
