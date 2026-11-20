#!/usr/bin/env python3
"""TARANG Round 5 — investigation of the entry-multiset stop.

Question: are the stored Rounds 1-3 taken-trade sets reproduced
EXACTLY by the original (defective-exit) machinery T.run_book? If
yes, the entry differences between the stored record and the Round 5
corrected books are fully explained by the defect itself: in
T.run_book, simulate_exit's (defective) exit index also set
busy_until, so the defect fed back into occupancy and changed which
later signals were taken. The stored taken sets are then artefacts
of the defective machinery, not of the books' frozen rules.
"""
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
    trades = T.run_book(data, gen_fn, NAMES)  # original defective path
    mine = Counter((t["sym"], t["date"], t["side"], t["entry_time"],
                    round(float(t["entry_price"]), 2),
                    t["exit_time"], round(float(t["exit_price"]), 2),
                    t["exit_reason"], round(float(t["net_inr"]), 2))
                   for t in trades)
    back = pd.read_csv(f"{T.WS}/{fname}")
    if cand is not None:
        back = back[back["candidate"] == cand]
    stored = Counter((r.sym, r.date, int(r.side), r.entry_time,
                      round(float(r.entry_price), 2),
                      r.exit_time, round(float(r.exit_price), 2),
                      r.exit_reason, round(float(r.net_inr), 2))
                     for r in back.itertuples())
    print(f"{label}: defective-machinery rows {sum(mine.values())} vs "
          f"stored {sum(stored.values())} | full-row multiset match: "
          f"{mine == stored} | only-repro "
          f"{int(sum((mine - stored).values()))} | only-stored "
          f"{int(sum((stored - mine).values()))}", flush=True)
print("REPRO CHECK DONE", flush=True)
