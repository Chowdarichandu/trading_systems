#!/usr/bin/env python3
"""WIDE-100 Stage-2 coverage audit (run with wide100_venv python —
needs pyarrow for the universe_daily parquets).

For each new name: fetched 5-min session dates (data/wide100) vs
the name's own trading dates in the local daily dump
(universe_daily) inside 2025-01-01 -> 2026-11-13. Writes the
coverage block into wide100_fetch_manifest.json and prints a
summary. Read-only on the stores; the manifest is the only write.
"""
import csv, json, os
import pandas as pd

WS = "/home/hatch/workspace/trading"
LO, HI = "2025-01-01", "2026-11-13"


def main():
    man = json.load(open(f"{WS}/wide100_fetch_manifest.json"))
    stage1 = json.load(open(f"{WS}/wide100_universe_stage1.json"))
    cov = {}
    for r in stage1["top75"]:
        sym = r["sym"]
        p5 = f"{WS}/data/wide100/{sym}/spot_5m.csv"
        got = set()
        if os.path.exists(p5):
            with open(p5) as f:
                for row in csv.reader(f):
                    if row and row[0] != "timestamp":
                        got.add(row[0][:10])
        dump = pd.read_parquet(f"{WS}/universe_daily/{sym}.parquet")
        dcol = "date" if "date" in dump.columns else dump.columns[0]
        dates = pd.to_datetime(dump[dcol]).dt.strftime("%Y-%m-%d")
        exp = {d for d in dates if LO <= d <= HI}
        got_w = {d for d in got if LO <= d <= HI}
        miss = sorted(exp - got_w)
        cov[sym] = dict(expected_sessions=len(exp),
                        fetched_sessions=len(got_w),
                        coverage_pct=round(100.0 * len(got_w) / len(exp), 2)
                        if exp else None,
                        missing_sessions=miss)
    man["coverage"] = cov
    full = sum(1 for v in cov.values() if v["coverage_pct"] == 100.0)
    worst = sorted(cov.items(), key=lambda kv: kv[1]["coverage_pct"])[:8]
    print(f"coverage: {full}/75 names at 100%")
    for s, v in worst:
        print(f"  {s}: {v['coverage_pct']}% ({v['fetched_sessions']}/"
              f"{v['expected_sessions']}) missing {v['missing_sessions'][:5]}")
    json.dump(man, open(f"{WS}/wide100_fetch_manifest.json", "w"), indent=1)
    print("manifest updated with coverage block")


if __name__ == "__main__":
    main()
