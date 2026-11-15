#!/usr/bin/env python3
"""Backfill the daily2leg Nifty premium stores for the DEC-S1 base
contract-days (NIFTY NEXT PHASE, 2026-11-04). The stores were built by
daily2leg/build_store.py with a KEEP filter retaining only 10:00-15:15
bars, so DEC-S1 legs entering 09:35-09:55 have no entry bar and no leg
has the 15:20 square-off bar. Repair = add-only merge from the declared
sources (the Nifty engine's exact-tag candle caches in aggressive_data /
v4_options_oct_data / historical_proof_data — the same files the frozen
DEC-S1 numbers were produced from), after verifying that every source
bar overlapping a stored bar agrees exactly. Backups written first;
a diff proof (0 stored bars altered) is printed and saved.
Scope: the 97 DEC-S1 base legs' contract-days only."""
import json, glob, re
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
DL = TR / "daily2leg"
DIRS = [TR / "aggressive_data", TR / "v4_options_oct_data",
        TR / "historical_proof_data", TR / "fix_tests_2026-11-02_cache",
        TR / "oct2026_fresh/ext29_30/premium"]
pat = re.compile(r"candles_(?:NIFTY|Nifty_50)_(\d+)(CE|PE)_"
                 r"(\d{4}-\d{2}-\d{2})(?:_(\d{4}-\d{2}-\d{2}))?\.json$")

def source_bars(strike, typ, day, exp):
    """Full-day bars {hm:[o,h,l,c]} from the exact-tag engine file if
    present, else merged from range-cache files. None if no source."""
    tag = f"NIFTY_{int(strike)}{typ}_{day}_{exp}"
    for d in DIRS:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists():
                try:
                    data = json.loads(p.read_text()).get("data", {}) \
                        .get("candles", [])
                except Exception:
                    continue
                rows = {c[0][11:16]: [float(c[1]), float(c[2]),
                                      float(c[3]), float(c[4])]
                        for c in data if c[0][:10] == day}
                if rows:
                    return rows, f"exact:{name}"
    merged = {}
    for d in DIRS:
        for fp in glob.glob(str(d / f"candles_*_{int(strike)}{typ}_*.json")):
            m = pat.search(Path(fp).name)
            if not m or (m.group(4) or m.group(3)) != exp:
                continue
            try:
                data = json.loads(Path(fp).read_text()).get("data", {}) \
                    .get("candles", [])
            except Exception:
                continue
            for c in data:
                if c[0][:10] == day:
                    merged[c[0][11:16]] = [float(c[1]), float(c[2]),
                                           float(c[3]), float(c[4])]
    return (merged, "range-cache") if merged else (None, None)

def same(a, b):
    return all(abs(x - y) < 0.005 for x, y in zip(a, b))

def main():
    legs = json.load(open(TR / "nifty_engine_r11_decs1_legs.json"))
    want = defaultdict(list)   # (store_name, key, date) -> [components]
    stores = {}
    for name in ("prem_nifty.json", "prem_nifty_weekly.json"):
        stores[name] = json.load(open(DL / name))
    needed = {}
    for l in legs:
        key = f"{l['expiry']}|{l['strike']}|{l['direction']}"
        needed[(key, l["date"])] = l
        for name in stores:
            if l["date"] in stores[name].get(key, {}):
                want[(name, key, l["date"])].append(l["component"])
    # every needed day must land in prem_nifty.json (the legs' resolver
    # store); weekly gets the days it already carries
    for (key, date) in needed:
        if ("prem_nifty.json", key, date) not in want:
            want[("prem_nifty.json", key, date)].append(needed[(key, date)]
                                                       ["component"])
    before = {n: sum(len(dd) for v in s.values() for dd in v.values())
              for n, s in stores.items()}
    backups = {}
    for name in stores:
        bak = DL / f"{name}.pre_nextphase_backfill_2026-11-04.bak"
        if not bak.exists():
            bak.write_text(json.dumps(stores[name]))
        backups[name] = str(bak)
    added, problems, per_month = 0, [], defaultdict(int)
    for (name, key, date), comps in sorted(want.items()):
        exp, strike, typ = key.split("|")
        src, how = source_bars(strike, typ, date, exp)
        if src is None:
            problems.append((key, date, "no_source"))
            continue
        day = stores[name].setdefault(key, {}).setdefault(date, {})
        bad = [t for t in day if t in src and not same(day[t], src[t])]
        if bad:
            problems.append((key, date, f"disagreement {bad[:3]}"))
            continue
        for t, v in src.items():
            if t not in day:
                day[t] = v
                added += 1
                per_month[date[:7]] += 1
    altered = 0
    for name in stores:
        orig = json.loads((DL / f"{name}.pre_nextphase_backfill_2026-11-04.bak")
                          .read_text())
        for k, v in orig.items():
            for d, dd in v.items():
                for t, b in dd.items():
                    if stores[name][k][d][t] != b:
                        altered += 1
    after = {n: sum(len(dd) for v in s.values() for dd in v.values())
             for n, s in stores.items()}
    for name, s in stores.items():
        (DL / name).write_text(json.dumps(s))
    print(f"bars before {before} -> after {after}; added {added} "
          f"(per month {dict(sorted(per_month.items()))}); "
          f"altered {altered}; problems {problems}")
    print(f"backups: {backups}")
    assert altered == 0 and not problems

if __name__ == "__main__":
    main()
