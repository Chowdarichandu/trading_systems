#!/usr/bin/env python3
"""TARANG Round 6 — dump-side stats for the 73 extra F&O/index names
(SPEC S.8 verification leg): for each name, its universe_daily
sessions inside 2025-01-01..2026-11-13 and the official close per
date. Written to tarang6_dumpstats.json for tarang6_score.py (which
runs on the system python without a parquet engine). Run with the
parquet-capable venv python. Data QA only; no strategy scoring."""
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
uni = json.load(open(os.path.join(ROOT, "tarang6_universe.json")))
extra = sorted(r["symbol"] for r in uni["qualifying"]
               if r["data_status"] == "needs_fetch")
out = {}
for sym in extra:
    df = pd.read_parquet(os.path.join(ROOT, "universe_daily",
                                      f"{sym}.parquet"),
                         columns=["date", "close"])
    df["date"] = pd.to_datetime(df["date"])
    w = df[(df["date"] >= "2025-01-01") & (df["date"] <= "2026-11-13")]
    out[sym] = {"sessions": int(len(w)),
                "closes": {str(d.date()): float(c)
                           for d, c in zip(w["date"], w["close"])}}
    print(sym, "sessions", len(w), flush=True)
json.dump(out, open(os.path.join(ROOT, "tarang6_dumpstats.json"), "w"))
print("WROTE tarang6_dumpstats.json for", len(out), "names")
