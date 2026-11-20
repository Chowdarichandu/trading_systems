#!/usr/bin/env python3
"""TARANG-T25-C forward-paper scorer (PREPARATION ONLY —
see tarang25c_forward_pack.md). Prepared under Design 26
WS1 (tarang26_SPEC.md S.2). NOT scheduled, NOT a live
book, no cron: it runs only when invoked by hand.

Given a date, it computes that day's T25-C signals from
the stored bars and scores them with the frozen Design
25 exits, using the same family machinery as the
backtest (tarang23 prep/day_ctx, tarang24 sig_gapw2,
tarang23 take_trade, tarang25 allocate25/vol_ratio_at),
so a forward day is scored by the identical definitions
that passed the gate.

Frozen rules (tarang25_SPEC.md S.2-S.4, book
TARANG-T25-C): gap% = first-bar open / previous store
day's last close - 1; gap% >= +0.015 -> SHORT at the
first-bar open; exit = -1.0% disaster stop stop-first
(entry x 1.01 for SHORT) else close of the last bar
<= 15:15; caps 10/day, 1/name-day; allocation |gap%|
DESC, vol_ratio DESC, universe order ASC.

Basis: equity cash, PROVISIONAL per 100 shares,
Rs 40/trade, paper only, real money Rs 0.

Usage:
  python3 tarang25c_scorer.py --date 2025-08-18
  python3 tarang25c_scorer.py --date 2025-08-18 --json out.json
  python3 tarang25c_scorer.py --selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

import tarang_score as T
import tarang23_score as T23
import tarang24_score as T24
import tarang25_score as T25

WS = T.WS
STREAM = "GAP-FADE-UP-15"
BOOK = "TARANG-T25-C"
NAMES = list(T23.NAMES23)            # 127 names, verified order
SELFTEST_DAYS = ["2025-08-18", "2026-03-24"]
PUBLISHED = f"{WS}/tarang25_trades_TARANG-T25-C.csv"


def day_candidates(data, date):
    """T25-C candidates for one date, built exactly as
    tarang25_score.gen_candidates builds them (same ctx,
    same signal fn, same standalone trade, same keys)."""
    cands = []
    for sym in NAMES:
        D = data[sym]
        for di, day in enumerate(D["days"]):
            if day["date"] != date:
                continue
            if di == 0:
                break           # first store day: no candidate
            pii = D["days"][di - 1]["ii"]
            prev = dict(pdh=float(D["h"][pii].max()),
                        pdl=float(D["l"][pii].min()),
                        last_close=float(D["c"][pii[-1]]))
            ctx = T23.day_ctx(D, day, prev)
            sigs, _sk = T24.sig_gapw2(ctx)
            for (stream, sl, side, el) in sigs:
                if stream != STREAM:
                    continue
                tr = T23.take_trade(D, day, ctx, stream, sl,
                                    side, el)
                if tr is None:
                    continue
                tr = dict(tr)
                gap = float(ctx["o"][0] / prev["last_close"] - 1.0)
                tr["gap_pct"] = round(gap, 6)
                tr["vol_ratio"] = round(
                    T25.vol_ratio_at(D, int(day["ii"][0])), 6)
                tr["univ"] = T25.UNIV_ORDER[sym]
                cands.append(tr)
            break
    return cands


def score_day(data, date):
    """Returns (candidates, taken trade rows in the
    Design 25 tarang25_trades_<BOOK>.csv format)."""
    cands = day_candidates(data, date)
    taken, _cap_days, _dec = T25.allocate25(cands)
    rows = []
    for tr in taken:
        row = {k: tr[k] for k in T25.TRADE_COLS[2:]}
        row["book"] = BOOK
        row["stream"] = STREAM
        rows.append({k: row[k] for k in T25.TRADE_COLS})
    return cands, rows


def print_day(date, cands, rows):
    print(f"TARANG-T25-C — {date}: {len(cands)} candidates, "
          f"{len(rows)} taken (cap 10/day)")
    for r in rows:
        print(f"  {r['sym']:<12} SHORT gap {r['gap_pct']:+.4f} "
              f"entry {r['entry_price']:.2f} @ {r['entry_time']} -> "
              f"exit {r['exit_price']:.2f} @ {r['exit_time']} "
              f"({r['exit_reason']})  net {r['net_inr']:+.2f}")
    if rows:
        print(f"  day net: {sum(r['net_inr'] for r in rows):+.2f}")


def selftest(data):
    pub = pd.read_csv(PUBLISHED)
    ok_all = True
    for date in SELFTEST_DAYS:
        _cands, rows = score_day(data, date)
        ref = pub[pub["date"] == date].to_dict("records")
        key = lambda r: r["sym"]
        mine = {key(r): r for r in rows}
        theirs = {key(r): r for r in ref}
        ok = set(mine) == set(theirs)
        detail = ""
        if ok:
            for sym, r in mine.items():
                p = theirs[sym]
                for f in ("side", "entry_time", "exit_time",
                          "exit_reason", "sig_local",
                          "entry_local", "exit_local"):
                    if r[f] != p[f]:
                        ok = False
                        detail = f"{sym} field {f}: {r[f]} != {p[f]}"
                        break
                for f in ("gap_pct", "vol_ratio", "entry_price",
                          "exit_price", "gross_inr", "net_inr"):
                    if abs(float(r[f]) - float(p[f])) > 1e-9:
                        ok = False
                        detail = f"{sym} field {f}: {r[f]} != {p[f]}"
                        break
                if not ok:
                    break
        else:
            detail = (f"taken sets differ: scorer "
                      f"{sorted(mine)} vs published "
                      f"{sorted(theirs)}")
        print(f"SELFTEST {date}: {len(rows)} scorer trades vs "
              f"{len(ref)} published — "
              f"{'EXACT MATCH' if ok else 'MISMATCH: ' + detail}")
        ok_all &= ok
    print(f"SELFTEST RESULT: {'PASS' if ok_all else 'FAIL'}")
    return ok_all


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="trading day YYYY-MM-DD")
    ap.add_argument("--json", help="write taken rows to this path")
    ap.add_argument("--selftest", action="store_true",
                    help="verify against the published Design 25 "
                         "trades for the two pre-registered days")
    args = ap.parse_args()
    if not args.selftest and not args.date:
        ap.error("give --date or --selftest")
    print(f"loading stored bars ({len(NAMES)} names) ...",
          flush=True)
    data = T23.prep(NAMES)
    if args.selftest:
        sys.exit(0 if selftest(data) else 1)
    cands, rows = score_day(data, args.date)
    print_day(args.date, cands, rows)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(rows, f, indent=1)
        print(f"wrote {len(rows)} rows to {args.json}")


if __name__ == "__main__":
    main()
