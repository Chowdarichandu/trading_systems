#!/usr/bin/env python3
"""Results Intelligence Layer v1 — event study engine. Read-only, no orders.

Inputs:
  --dates CSV: stock,quarter,results_date,after_market,source,source_url,status
    results_date YYYY-MM-DD, after_market yes/no/unverified, status verified/unverified
  --data-dir DIR with daily OHLCV CSVs per symbol: <SYMBOL>.csv with
    date,open,high,low,close,volume  (from Upstox historical candles, daily)
    plus NIFTY50.csv for the benchmark (same columns).

Windows (fixed, documented in results_intelligence_v1.md):
  T = results announcement calendar date.
  pre_days  = last 5 trading days with date <= T (T itself if it is a trading day).
  reaction  = first trading day AFTER T if after_market in (yes, unverified-assumed-after),
              else T if T is a trading day, else first trading day after T.
  post_days = 5 trading days starting at reaction (i.e. trading T+1 .. T+5 when
              announcement was after market).
  lookback  = 20 trading days immediately before pre_days, for volume median / SMA.

Measures per event:
  pre_return, post_return, gap_pct (reaction open / last pre close - 1),
  pre_vol_ratio (mean pre volume / median lookback volume),
  post_vol_ratio, pre_range_pct, post_range_pct,
  excess vs Nifty (stock return - Nifty return, same windows),
  vwap_pos: last post close vs 20-day typical-price mean (APPROXIMATE, daily only),
  accumulation: pre_return > 0 AND pre_vol_ratio >= 1.2  (price up + volume up together;
    thresholds are provisional, labelled, NOT Chandu's rule).

Classification (per stock, rolling last 4 verified events only):
  3 of 4 agreeing on (accumulation, post direction) -> pattern, else NO_PATTERN.
  post direction: continuation if sign(post_return) == sign(pre_return) and |post|>1%,
                  reversal if sign differs and |post|>1%, else flat.
  Unverified dates are EXCLUDED from classification and flagged.

Outputs: per-event CSV and per-stock pattern CSV. No orders, no live trading.
"""
import argparse, csv, math, statistics
from datetime import date
from pathlib import Path


def parse_date(s):
    y, m, d = s.strip().split("-")
    return date(int(y), int(m), int(d))


def load_daily(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({
                    "date": parse_date(r["date"]),
                    "open": float(r["open"]), "high": float(r["high"]),
                    "low": float(r["low"]), "close": float(r["close"]),
                    "volume": float(r["volume"]) if r.get("volume") not in (None, "") else 0.0,
                })
            except Exception:
                continue
    rows.sort(key=lambda x: x["date"])
    return rows


def window_returns(rows, days):
    if len(days) < 2:
        return None
    first, last = days[0], days[-1]
    return last["close"] / first["close"] - 1 if first["close"] else None


def ret_from(rows, start_close, end_close):
    return end_close / start_close - 1 if start_close else None


def analyse_event(stock_rows, bench_rows, results_date, after_market):
    dates = [r["date"] for r in stock_rows]
    idx_by_date = {r["date"]: i for i, r in enumerate(stock_rows)}
    # pre: last 5 trading days <= T
    pre_idx = [i for i, d in enumerate(dates) if d <= results_date][-5:]
    if len(pre_idx) < 5:
        return None, "insufficient_pre_data"
    pre = [stock_rows[i] for i in pre_idx]
    look_idx = list(range(pre_idx[0] - 20, pre_idx[0]))
    if look_idx[0] < 0:
        return None, "insufficient_lookback"
    look = [stock_rows[i] for i in look_idx]
    # reaction day
    if after_market in ("yes", "unverified"):
        react_idx = next((i for i, d in enumerate(dates) if d > results_date), None)
    else:
        react_idx = idx_by_date.get(results_date)
        if react_idx is None:
            react_idx = next((i for i, d in enumerate(dates) if d > results_date), None)
    if react_idx is None or react_idx + 4 >= len(stock_rows):
        return None, "insufficient_post_data"
    post = stock_rows[react_idx:react_idx + 5]
    # returns: pre window return = close(last pre)/close(day before pre)-1
    pre_start_close = stock_rows[pre_idx[0] - 1]["close"]
    pre_ret = ret_from(stock_rows, pre_start_close, pre[-1]["close"])
    post_start_close = pre[-1]["close"]
    post_ret = ret_from(stock_rows, post_start_close, post[-1]["close"])
    gap = post[0]["open"] / pre[-1]["close"] - 1 if pre[-1]["close"] else None
    med_vol = statistics.median([r["volume"] for r in look]) if look else 0
    pre_vol_ratio = (statistics.mean([r["volume"] for r in pre]) / med_vol) if med_vol else None
    post_vol_ratio = (statistics.mean([r["volume"] for r in post]) / med_vol) if med_vol else None
    # benchmark excess, same trading-day indices (align by date)
    def bench_window(rows_b, target_dates):
        m = {r["date"]: r for r in rows_b}
        sel = [m[d] for d in target_dates if d in m]
        return sel
    bench_pre = bench_window(bench_rows, [r["date"] for r in pre])
    bench_post = bench_window(bench_rows, [r["date"] for r in post])
    def bench_ret(sel, start_date):
        m = {r["date"]: r for r in bench_rows}
        if len(sel) < 2 or start_date not in m:
            return None
        return sel[-1]["close"] / m[start_date]["close"] - 1
    bench_pre_ret = bench_ret(bench_pre, stock_rows[pre_idx[0] - 1]["date"]) if bench_rows else None
    bench_post_ret = bench_ret(bench_post, pre[-1]["date"]) if bench_rows else None
    excess_pre = (pre_ret - bench_pre_ret) if (pre_ret is not None and bench_pre_ret is not None) else None
    excess_post = (post_ret - bench_post_ret) if (post_ret is not None and bench_post_ret is not None) else None
    typ = statistics.mean([(r["high"] + r["low"] + r["close"]) / 3 for r in look]) if look else None
    vwap_pos = (post[-1]["close"] / typ - 1) if typ else None
    accumulation = bool(pre_ret is not None and pre_ret > 0 and pre_vol_ratio is not None and pre_vol_ratio >= 1.2)
    if post_ret is None:
        post_dir = "unknown"
    elif abs(post_ret) <= 0.01:
        post_dir = "flat"
    elif (post_ret > 0) == (pre_ret > 0):
        post_dir = "continuation"
    else:
        post_dir = "reversal"
    return {
        "reaction_date": post[0]["date"].isoformat(),
        "pre_start": pre[0]["date"].isoformat(), "pre_end": pre[-1]["date"].isoformat(),
        "post_start": post[0]["date"].isoformat(), "post_end": post[-1]["date"].isoformat(),
        "pre_return_pct": round(pre_ret * 100, 2), "post_return_pct": round(post_ret * 100, 2),
        "gap_pct": round(gap * 100, 2) if gap is not None else None,
        "pre_vol_ratio": round(pre_vol_ratio, 2) if pre_vol_ratio is not None else None,
        "post_vol_ratio": round(post_vol_ratio, 2) if post_vol_ratio is not None else None,
        "excess_pre_pct": round(excess_pre * 100, 2) if excess_pre is not None else None,
        "excess_post_pct": round(excess_post * 100, 2) if excess_post is not None else None,
        "vwap_pos_pct": round(vwap_pos * 100, 2) if vwap_pos is not None else None,
        "accumulation": accumulation, "post_direction": post_dir,
    }, None


def classify(events):
    """events: list of dicts with accumulation (bool) and post_direction. 3/4 rule."""
    if len(events) < 4:
        return "INSUFFICIENT_EVENTS", ""
    sigs = []
    for e in events:
        if e["accumulation"]:
            sigs.append("ACCUM+" + e["post_direction"])
        else:
            sigs.append("NOACCUM+" + e["post_direction"])
    from collections import Counter
    common, count = Counter(sigs).most_common(1)[0]
    if count >= 3:
        return "PATTERN", f"{common} in {count}/4"
    return "NO_PATTERN", f"most common {common} in {count}/4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-events", required=True)
    ap.add_argument("--out-patterns", required=True)
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    bench = load_daily(data_dir / "NIFTY50.csv") if (data_dir / "NIFTY50.csv").exists() else []
    events_by_stock = {}
    with open(args.dates, newline="") as f:
        date_rows = list(csv.DictReader(f))
    out_events = []
    for dr in date_rows:
        stock = dr["stock"].strip()
        fpath = data_dir / f"{stock}.csv"
        if not fpath.exists():
            out_events.append({**dr, "status_out": "missing_daily_data"})
            continue
        rows = load_daily(fpath)
        res, err = analyse_event(rows, bench, parse_date(dr["results_date"]), dr.get("after_market", "unverified").strip())
        if err:
            out_events.append({**dr, "status_out": err})
            continue
        rec = {**dr, **res, "status_out": "ok"}
        out_events.append(rec)
        if dr.get("status", "verified").strip() == "verified":
            events_by_stock.setdefault(stock, []).append(rec)
    with open(args.out_events, "w", newline="") as f:
        keys = []
        for e in out_events:
            for k in e.keys():
                if k not in keys:
                    keys.append(k)
        w = csv.DictWriter(f, fieldnames=keys if keys else ["stock"])
        w.writeheader(); w.writerows(out_events)
    patterns = []
    for stock, evs in sorted(events_by_stock.items()):
        # rolling last 4 by results_date
        evs_sorted = sorted(evs, key=lambda e: e["results_date"])[-4:]
        verdict, detail = classify(evs_sorted)
        patterns.append({"stock": stock, "n_verified_events_used": len(evs_sorted),
                         "verdict": verdict, "detail": detail,
                         "quarters": ";".join(e["quarter"] for e in evs_sorted)})
    with open(args.out_patterns, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["stock", "n_verified_events_used", "verdict", "detail", "quarters"])
        w.writeheader(); w.writerows(patterns)
    print(f"events: {len(out_events)}, ok: {sum(1 for e in out_events if e.get('status_out')=='ok')}, patterns: {len(patterns)}")
    for p in patterns:
        print(p)


if __name__ == "__main__":
    main()
