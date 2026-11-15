#!/usr/bin/env python3
"""LADDER-BANK backfill CHECK (no writes): do the declared store sources
hold pre-10:00 5-min premium bars for the 31 failed contract-days (and
their flipped-direction counterparts, needed by the gate placebo)?

Sources checked in build_store.py order:
  1) data/banknifty-2026-MM/option_5m.csv
  2) candles_*.json caches: aggressive_data, historical_proof_data,
     v4_options_oct_data, fix_tests_2026-11-02_cache,
     oct2026_fresh/ext29_30/premium
"""
import csv, json, re, glob
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
audit = list(csv.DictReader(open(TR / "ladder_bank_reconstruction_audit.csv")))
failed = [a for a in audit if a["status"] != "RECONSTRUCTED_EXACT"]
print(f"failed legs: {len(failed)}")

FLIP = {"CE": "PE", "PE": "CE"}
need = {}   # (expiry, strike, typ, date) -> role
for a in failed:
    k = (a["expiry"], int(a["strike"]), a["direction"], a["date"])
    need[k] = "leg"
    kf = (a["expiry"], int(a["strike"]), FLIP[a["direction"]], a["date"])
    need.setdefault(kf, "flip")
print(f"contract-days needed (legs + flips): {len(need)}")

PRE = [f"{h:02d}:{m:02d}" for h in (9,) for m in range(15, 60, 5)]  # 09:15..09:55
print("pre-10:00 grid:", PRE)

# ---- source 1: monthly CSVs -------------------------------------------------
csvbars = defaultdict(dict)   # key -> {hm: [o,h,l,c]}
for m in range(1, 11):
    p = TR / f"data/banknifty-2026-{m:02d}/option_5m.csv"
    with open(p) as f:
        for r in csv.DictReader(f):
            k = (r["expiry"], int(r["strike"]), r["option_type"], r["timestamp"][:10])
            if k in need:
                hm = r["timestamp"][11:16]
                if hm < "10:00":
                    csvbars[k][hm] = [float(r["open"]), float(r["high"]),
                                      float(r["low"]), float(r["close"])]
print("\n--- CSV coverage of needed contract-days (pre-10:00) ---")
miss_csv = []
for k in sorted(need):
    got = sorted(csvbars.get(k, {}))
    flag = "FULL" if got == PRE else ("none" if not got else "partial")
    if flag != "FULL":
        miss_csv.append(k)
    print(k, need[k], flag, got if flag != "FULL" else "")

# entry-bar open check from CSV for the 31 legs
print("\n--- CSV entry-bar open vs recorded entry premium ---")
bad_ep = []
for a in failed:
    k = (a["expiry"], int(a["strike"]), a["direction"], a["date"])
    bar = csvbars.get(k, {}).get(a["entry_time"])
    ep = float(a["entry_premium"])
    if bar is None:
        print(a["date"], a["direction"], a["entry_time"], "NO CSV BAR")
        bad_ep.append(a)
    else:
        d = round(bar[0] - ep, 4)
        print(a["date"], a["direction"], a["entry_time"], "csv_open", bar[0],
              "recorded", ep, "diff", d, "EXACT" if abs(d) <= 0.005 else "MISMATCH")
        if abs(d) > 0.005:
            bad_ep.append(a)
print("legs without exact CSV entry bar:", len(bad_ep))

# ---- source 2: JSON caches ---------------------------------------------------
pat = re.compile(r"candles_(BANKNIFTY|NIFTY|Nifty_50|Nifty_Bank)_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})(?:_(\d{4}-\d{2}-\d{2}))?\.json$")
IDX = {"BANKNIFTY": "BANKNIFTY", "Nifty_Bank": "BANKNIFTY"}
cachebars = defaultdict(dict)
for d in ("aggressive_data", "historical_proof_data", "v4_options_oct_data",
          "fix_tests_2026-11-02_cache", "oct2026_fresh/ext29_30/premium"):
    for fp in glob.glob(str(TR / d / "candles_*.json")):
        mm = pat.search(Path(fp).name)
        if not mm or IDX.get(mm.group(1)) != "BANKNIFTY":
            continue
        strike, typ = int(mm.group(2)), mm.group(3)
        expiry = mm.group(5) or mm.group(4)
        try:
            data = json.loads(Path(fp).read_text())
        except Exception:
            continue
        for c in data.get("data", {}).get("candles", []):
            k = (expiry, strike, typ, c[0][:10])
            if k in need and c[0][11:16] < "10:00":
                cachebars[k][c[0][11:16]] = [float(c[1]), float(c[2]),
                                             float(c[3]), float(c[4])]
print("\n--- cache coverage for contract-days not FULL in CSV ---")
for k in miss_csv:
    got = sorted(cachebars.get(k, {}))
    print(k, need[k], "cache bars:", got)
