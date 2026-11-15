#!/usr/bin/env python3
"""LADDER-BANK store repair (2026-11-03): backfill pre-10:00 5-min premium
bars into daily2leg/prem_bank.json for the 31 failed v21 contract-days and
their flipped-direction counterparts (gate placebo), from the sources
daily2leg/build_store.py already declares, in its merge order:
  1) data/banknifty-2026-MM/option_5m.csv   (first)
  2) candles_*.json caches                  (later wins, as in build_store)
ADD-ONLY: a bar already in the store is never altered. The store is backed
up before writing. Every addition and every CSV/cache disagreement on a
new bar is logged.
"""
import csv, json, re, glob, shutil
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
STORE = TR / "daily2leg/prem_bank.json"
BACKUP = TR / "daily2leg/prem_bank.json.pre_ladder_backfill_2026-11-03.bak"

audit = list(csv.DictReader(open(TR / "ladder_bank_reconstruction_audit.csv")))
failed = [a for a in audit if a["status"] != "RECONSTRUCTED_EXACT"]
assert len(failed) == 31
FLIP = {"CE": "PE", "PE": "CE"}
need = {}
for a in failed:
    k = (a["expiry"], int(a["strike"]), a["direction"], a["date"])
    need[k] = "leg"
    need.setdefault((a["expiry"], int(a["strike"]), FLIP[a["direction"]],
                     a["date"]), "flip")
PRE = [f"09:{m:02d}" for m in range(15, 60, 5)]

cand = defaultdict(dict)          # key -> {hm: [o,h,l,c]}
src = defaultdict(dict)           # key -> {hm: "csv"/"cache"}
conflicts = []
def offer(k, hm, bar, s):
    if hm in cand[k] and cand[k][hm] != bar:
        conflicts.append((k, hm, src[k][hm], cand[k][hm], s, bar))
    cand[k][hm] = bar
    src[k][hm] = s

for m in range(1, 11):
    p = TR / f"data/banknifty-2026-{m:02d}/option_5m.csv"
    with open(p) as f:
        for r in csv.DictReader(f):
            k = (r["expiry"], int(r["strike"]), r["option_type"], r["timestamp"][:10])
            hm = r["timestamp"][11:16]
            if k in need and hm < "10:00":
                offer(k, hm, [float(r["open"]), float(r["high"]),
                              float(r["low"]), float(r["close"])], "csv")

pat = re.compile(r"candles_(BANKNIFTY|NIFTY|Nifty_50|Nifty_Bank)_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})(?:_(\d{4}-\d{2}-\d{2}))?\.json$")
for d in ("aggressive_data", "historical_proof_data", "v4_options_oct_data",
          "fix_tests_2026-11-02_cache", "oct2026_fresh/ext29_30/premium"):
    for fp in glob.glob(str(TR / d / "candles_*.json")):
        mm = pat.search(Path(fp).name)
        if not mm or mm.group(1) not in ("BANKNIFTY", "Nifty_Bank"):
            continue
        k0 = (mm.group(5) or mm.group(4), int(mm.group(2)), mm.group(3))
        try:
            data = json.loads(Path(fp).read_text())
        except Exception:
            continue
        for c in data.get("data", {}).get("candles", []):
            k = k0 + (c[0][:10],)
            hm = c[0][11:16]
            if k in need and hm < "10:00":
                offer(k, hm, [float(c[1]), float(c[2]), float(c[3]),
                              float(c[4])], "cache")

# entry-bar verification from candidates for all 31 legs BEFORE merging
print("--- candidate entry-bar check (31 legs) ---")
for a in failed:
    k = (a["expiry"], int(a["strike"]), a["direction"], a["date"])
    bar = cand.get(k, {}).get(a["entry_time"])
    ep = float(a["entry_premium"])
    assert bar is not None, ("no candidate entry bar", k, a["entry_time"])
    d = round(bar[0] - ep, 4)
    print(a["date"], a["direction"], a["entry_time"], "cand_open", bar[0],
          "recorded", ep, "diff", d, "src", src[k][a["entry_time"]])
    assert abs(d) <= 0.005, ("entry mismatch", k, d)
print("all 31 entry bars EXACT from declared sources")

print(f"\nCSV/cache disagreements on new bars: {len(conflicts)}")
for c in conflicts:
    print("  CONFLICT", c)

# ---- merge (add-only) -------------------------------------------------------
shutil.copy2(STORE, BACKUP)
print("backup written:", BACKUP.name)
prem = json.load(open(STORE))
added_by_month = defaultdict(int)
added_by_src = defaultdict(int)
days_completed = []
still_missing = []
for k in sorted(need):
    expiry, strike, typ, date = k
    ck = f"{expiry}|{strike}|{typ}"
    day = prem.setdefault(ck, {}).setdefault(date, {})
    added = 0
    for hm in PRE:
        if hm in cand.get(k, {}) and hm not in day:
            day[hm] = cand[k][hm]
            added += 1
            added_by_month[date[:7]] += 1
            added_by_src[src[k][hm]] += 1
        elif hm not in cand.get(k, {}) and hm not in day:
            still_missing.append((k, hm))
    if added:
        prem[ck][date] = dict(sorted(day.items()))
        days_completed.append((k, need[k], added))
with open(STORE, "w") as f:
    json.dump(prem, f)

print(f"\ncontract-days touched: {len(days_completed)}")
for k, role, n in days_completed:
    print("  ", k, role, f"+{n} bars")
print("bars added by month:", dict(sorted(added_by_month.items())))
print("bars added by source:", dict(added_by_src))
print("total bars added:", sum(added_by_month.values()))
print("still missing (no declared source):", still_missing)

# post-merge verification: 31 legs exact in the STORE
prem = json.load(open(STORE))
for a in failed:
    ck = f"{a['expiry']}|{int(a['strike'])}|{a['direction']}"
    bar = prem[ck][a["date"]][a["entry_time"]]
    assert abs(bar[0] - float(a["entry_premium"])) <= 0.005
print("post-merge store check: all 31 entry bars EXACT")
