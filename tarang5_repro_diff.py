#!/usr/bin/env python3
"""Inspect the residual rows: defective-machinery reproduction vs the
stored Rounds 1-3 record — which fields differ, entries or exits?"""
import pandas as pd
from collections import Counter

import tarang_score as T
import tarang2_score as T2
import tarang3_score as T3

NAMES = T.NAMES
data = {}
T.day_maps_cache = {}
for sym in NAMES:
    df = T.add_indicators(T.load_name(sym))
    data[sym] = df
    for date, val in T.day_maps(df).items():
        T.day_maps_cache[(sym, date)] = val
print("data loaded", flush=True)

BOOKS = [
    ("TARANG-R1", T.gen_signals_primary, "tarang_trades.csv", None),
    ("TARANG-B", T2.gen_signals_trend_establish, "tarang2_trades.csv",
     "TARANG-B"),
    ("TARANG-A2", T3.gen_signals_A2, "tarang3_trades.csv", "TARANG-A2"),
    ("TARANG-A3", T3.gen_signals_A3, "tarang3_trades.csv", "TARANG-A3"),
]

for label, gen_fn, fname, cand in BOOKS:
    trades = T.run_book(data, gen_fn, NAMES)
    ekey = lambda t: (t["sym"], t["date"], t["side"], t["entry_time"],
                      round(float(t["entry_price"]), 2))
    xkey = lambda t: (t["exit_time"], round(float(t["exit_price"]), 2),
                      t["exit_reason"], round(float(t["net_inr"]), 2))
    mine_e = Counter(ekey(t) for t in trades)
    mine_full = {(ekey(t)): xkey(t) for t in trades}
    back = pd.read_csv(f"{T.WS}/{fname}")
    if cand is not None:
        back = back[back["candidate"] == cand]
    stored_e = Counter()
    stored_full = {}
    for r in back.itertuples():
        k = (r.sym, r.date, int(r.side), r.entry_time,
             round(float(r.entry_price), 2))
        stored_e[k] += 1
        stored_full[k] = (r.exit_time, round(float(r.exit_price), 2),
                          r.exit_reason, round(float(r.net_inr), 2))
    print(f"\n{label}: entry multiset match (defective machinery): "
          f"{mine_e == stored_e} | only-repro "
          f"{int(sum((mine_e - stored_e).values()))} | only-stored "
          f"{int(sum((stored_e - mine_e).values()))}")
    # for shared entries, compare exits
    diffs = [(k, mine_full[k], stored_full[k]) for k in mine_full
             if k in stored_full and mine_full[k] != stored_full[k]]
    print(f"{label}: shared entries with differing exit fields: "
          f"{len(diffs)}")
    for k, a, b in diffs[:6]:
        print(f"   {k}\n     repro : {a}\n     stored: {b}")
    only_r = list((mine_e - stored_e).elements())[:4]
    only_s = list((stored_e - mine_e).elements())[:4]
    for k in only_r:
        print(f"   only-repro entry: {k}")
    for k in only_s:
        print(f"   only-stored entry: {k}")
print("\nDIFF INSPECTION DONE", flush=True)
