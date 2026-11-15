#!/usr/bin/env python3
"""PHASE-3 BUILDUP NIFTY - LOCAL INVENTORY (no network)."""
import csv, json, re
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"

legs = list(csv.DictReader(open(TR / "november_books_fix_repair_nifty_legs.csv")))
leg_days = sorted(set(r["date"] for r in legs))
print(f"legs {len(legs)}  leg-days {len(leg_days)}")

# ---- spot coverage (progressive store) ----
spot_days = set()
sp = open(TR / "data/progressive/NIFTY/spot_5m.csv").read().splitlines()
hdr = sp[0]
for line in sp[1:]:
    if line.strip():
        spot_days.add(line.split(",")[0][:10])
miss_spot = [d for d in leg_days if d not in spot_days]
print(f"spot: {len(spot_days)} days in store; leg-days missing spot: {miss_spot}")
print("spot has 2026-11-03:", "2026-11-03" in spot_days,
      "| spot range:", min(spot_days), max(spot_days))

# ---- FUT5 price-only coverage ----
import glob
fut_days = set()
for fn in glob.glob(str(TR / "round4_history/FUT5_NIFTY_*.json")):
    for row in json.load(open(fn)):
        fut_days.add(row[0])
miss_fut = [d for d in leg_days if d not in fut_days]
print(f"FUT5 price days: {len(fut_days)}; leg-days missing FUT5 price: {miss_fut}")

# ---- fetched option cache inventory ----
pat = re.compile(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json")
cache = defaultdict(set)   # day -> set of (strike, typ, exp)
for fn in (TR / "oi_buildup_data").glob("candles_NIFTY_*.json"):
    m = pat.match(fn.name)
    if m:
        cache[m.group(4)].add((int(m.group(1)), m.group(2), m.group(3)))
print(f"fetched-cache days: {len(cache)}")
cov = {d: len(cache.get(d, ())) for d in leg_days}
full = [d for d in leg_days if cov[d] >= 22]
part = [d for d in leg_days if 0 < cov[d] < 22]
none = [d for d in leg_days if cov[d] == 0]
print(f"leg-days with >=22 cached contracts: {len(full)}; partial: {len(part)}; none: {len(none)}")
print("partial days detail:", {d: cov[d] for d in part})
print("none days:", none)
print("Nov 3 cached contracts:", len(cache.get("2026-11-03", ())),
      sorted(cache.get("2026-11-03", ()))[:30])
