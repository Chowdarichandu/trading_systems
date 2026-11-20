#!/usr/bin/env python3
"""TARANG-T26-C-TRAIL forward-paper scorer (PREPARATION
ONLY — see tarang25c_trail_forward_pack.md). Prepared
under Design 27 WS1 (tarang27_SPEC.md S.2). NOT
scheduled, NOT a live book, no cron: it runs only when
invoked by hand.

Given a date, it computes that day's T25-C entries from
the stored bars through the same family machinery as
the frozen pack (tarang23 prep/day_ctx, tarang24
sig_gapw2, tarang25 allocate25/vol_ratio_at) and scores
them with the TRAIL exit (tarang26 exit26_trail_engine)
— the identical definitions that passed the Design 26
full gate as line TARANG-T26-C-TRAIL.

Frozen rules (tarang26_SPEC.md S.4): entries are
T25-C's — gap% = first-bar open / previous store day's
last close - 1; gap% >= +0.015 -> SHORT at the first-bar
open; caps 10/day, 1/name-day; allocation |gap%| DESC,
vol_ratio DESC, universe order ASC. Exit: -1.0% disaster
stop stop-first (entry x 1.01 for SHORT) until a bar's
low reaches H = (entry + prev_close) / 2; from the NEXT
bar the stop is breakeven (entry), same fill rules;
else close of the last bar <= 15:15. Reasons: stop /
trailstop / squareoff.

Basis: equity cash, PROVISIONAL per 100 shares,
Rs 40/trade, paper only, real money Rs 0.

Usage:
  python3 tarang25c_trail_scorer.py --date 2025-08-18
  python3 tarang25c_trail_scorer.py --date 2025-08-18 --json out.json
  python3 tarang25c_trail_scorer.py --selftest
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
import tarang26_score as T26

WS = T.WS
COST = 40.0
QTY = 100
STREAM = "GAP-FADE-UP-15"
BOOK = "TARANG-T25-C"
LINE = "TARANG-T26-C-TRAIL"
NAMES = list(T23.NAMES23)            # 127 names, verified order
SELFTEST_DAYS = ["2025-08-18", "2026-03-24"]
PUBLISHED = f"{WS}/tarang26_trades.csv"
ROW_COLS = ["line", "book", "stream", "sym", "date", "year",
            "side", "gap_pct", "vol_ratio", "signal_time",
            "entry_time", "entry_price", "exit_time",
            "exit_price", "exit_reason", "gross_inr",
            "net_inr", "sig_local", "entry_local", "exit_local"]


def day_candidates(data, date):
    """T25-C candidates for one date, built exactly as
    tarang25c_scorer builds them (same ctx, same signal
    fn, same standalone trade, same keys), plus the
    prev_close the TRAIL exit needs. Returns (cands,
    daymap) where daymap[(sym, date)] = (D, day)."""
    cands = []
    daymap = {}
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
                tr["prev_close"] = prev["last_close"]
                cands.append(tr)
                daymap[(sym, date)] = (D, day)
            break
    return cands, daymap


def trail_exit(data, daymap, tr):
    """Re-exit one taken candidate under the TRAIL exit
    (tarang26 exit26_trail_engine), exactly as Design 26
    WS3 built its trades."""
    D, day = daymap[(tr["sym"], tr["date"])]
    ii = day["ii"]
    o, h, l, c = D["o"][ii], D["h"][ii], D["l"][ii], D["c"][ii]
    px = float(tr["entry_price"])
    tgt = (px + float(tr["prev_close"])) / 2.0
    xj, xpx, reason = T26.exit26_trail_engine(
        o, h, l, c, int(tr["entry_local"]), day["sq"],
        int(tr["side"]), px, tgt)
    nt = dict(tr)
    nt["exit_time"] = str(day["times"][xj])
    nt["exit_price"] = float(xpx)
    nt["exit_reason"] = reason
    nt["exit_local"] = int(xj)
    gross = (float(xpx) - px) * int(tr["side"]) * QTY
    nt["gross_inr"] = round(gross, 2)
    nt["net_inr"] = round(gross - COST, 2)
    return nt


def score_day(data, date):
    """Returns (candidates, taken rows in the Design 26
    tarang26_trades.csv format for line
    TARANG-T26-C-TRAIL)."""
    cands, daymap = day_candidates(data, date)
    taken, _cap_days, _dec = T25.allocate25(cands)
    rows = []
    for tr in taken:
        nt = trail_exit(data, daymap, tr)
        row = {k: nt[k] for k in ROW_COLS[3:]}
        row["line"] = LINE
        row["book"] = BOOK
        row["stream"] = STREAM
        rows.append({k: row[k] for k in ROW_COLS})
    return cands, rows


def print_day(date, cands, rows):
    print(f"{LINE} — {date}: {len(cands)} candidates, "
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
    pub = pub[pub["line"] == LINE]
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
                    help="verify against the published Design 26 "
                         "TRAIL trades for the two pre-registered days")
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
