"""
Fetch Upstox data for the 3-Blue-Line Bank Nifty backtest engine.

Outputs (in --out-dir), matching backtest_3_blue_line.py:
  spot_5m.csv    timestamp, open, high, low, close
  spot_daily.csv date, open, high, low, close
  option_5m.csv  timestamp, strike, option_type, expiry, open, high, low, close

How it works, following Upstox's backtesting flow:
  1. Resolve the Bank Nifty index instrument key (search, or --index-key).
  2. Fetch spot 5-minute candles via Historical Candle Data V3.
  3. List expired option contracts for ONE expiry via Get Expired Option Contracts.
  4. For each trading day, fetch 5-minute candles only for CE/PE strikes
     near that day's spot range, so the run stays within rate limits.

Requirements and limits — read before running:
  * Expired Instruments APIs require the Upstox Plus plan. Instrument
    Search and Historical Candle V3 are available on all plans.
  * Upstox community support notes expired data before 15 June 2025 may be
    incomplete/inconsistent, and December 2024 expiries are not available.
    Start with an expiry from July 2025 onwards for a reliable test.
  * This script is READ-ONLY. It places no orders.
  * Never paste your token in chat or commit it. Pass it via environment:
        export UPSTOX_ACCESS_TOKEN='your_token_here'
    Tokens are short-lived (typically until the next trading day), so
    generate a fresh one for each fetch run.

Usage — first run, list index candidates:
  python3 fetch_upstox_banknifty.py --list-index

Usage — fetch one expiry month (example, replace key and expiry):
  python3 fetch_upstox_banknifty.py \
      --index-key 'NSE_INDEX|Nifty Bank' \
      --expiry 2025-07-29 \
      --from-date 2025-07-01 --to-date 2025-07-29 \
      --out-dir ./data/banknifty-2025-07

Then run the engine:
  python3 backtest_3_blue_line.py \
      --spot5m ./data/banknifty-2025-07/spot_5m.csv \
      --daily ./data/banknifty-2025-07/spot_daily.csv \
      --options ./data/banknifty-2025-07/option_5m.csv \
      --out ./data/banknifty-2025-07/trade_log.csv
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pandas as pd

BASE = "https://api.upstox.com"


def get(token, path, params=None):
    url = BASE + path
    if params:
        qs = "&".join(f"{k}={quote(str(v), safe='')}" for k, v in params.items())
        url += "?" + qs
    req = Request(url, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        # Upstox/Cloudflare blocks the default Python urllib user-agent.
        "User-Agent": "BankNiftyBacktestFetcher/1.0",
    })
    for attempt in range(4):
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode(errors="ignore")[:500]
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GET {url} -> HTTP {e.code}: {body}") from e


def candles_to_df(payload):
    rows = (payload.get("data") or {}).get("candles") or []
    df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-index", action="store_true")
    ap.add_argument("--index-key", default=None, help="e.g. NSE_INDEX|Nifty Bank (verify from --list-index output)")
    ap.add_argument("--expiry", default=None, help="YYYY-MM-DD, last Tuesday of the month for Bank Nifty")
    ap.add_argument("--from-date", default=None)
    ap.add_argument("--to-date", default=None)
    ap.add_argument("--out-dir", default="./data/banknifty")
    ap.add_argument("--sleep", type=float, default=0.35, help="Seconds between option-candle calls")
    args = ap.parse_args()

    token = os.environ.get("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("ERROR: set UPSTOX_ACCESS_TOKEN in your environment first. Do not paste it in chat.", file=sys.stderr)
        return 1

    if args.list_index:
        payload = get(token, "/v2/instruments/search",
                      {"query": "BANKNIFTY", "exchanges": "NSE", "segments": "INDEX"})
        print(json.dumps(payload, indent=2)[:4000])
        print("\nCopy the instrument_key for the Bank Nifty index and re-run with --index-key.")
        return 0

    if not all([args.index_key, args.expiry, args.from_date, args.to_date]):
        print("ERROR: --index-key, --expiry, --from-date and --to-date are required.", file=sys.stderr)
        return 2

    os.makedirs(args.out_dir, exist_ok=True)
    enc_key = quote(args.index_key, safe="")

    # 1. Spot 5-minute candles (V3).
    print(f"Fetching spot 5m candles {args.from_date} to {args.to_date} ...")
    spot_payload = get(token, f"/v3/historical-candle/{enc_key}/minutes/5/{args.to_date}/{args.from_date}")
    spot = candles_to_df(spot_payload)
    if spot.empty:
        print("ERROR: no spot candles returned. Check the index key and date range.", file=sys.stderr)
        return 3
    spot[["timestamp", "open", "high", "low", "close"]].to_csv(f"{args.out_dir}/spot_5m.csv", index=False)

    # 2. Daily spot, derived from the 5m data, for the engine's daily file.
    spot["date"] = spot["timestamp"].dt.normalize()
    daily = spot.groupby("date").agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")
    ).reset_index()
    daily.to_csv(f"{args.out_dir}/spot_daily.csv", index=False)
    print(f"Spot: {len(spot)} 5m candles, {len(daily)} days.")

    # 3. Expired option contracts for this expiry.
    print(f"Fetching expired option contracts for expiry {args.expiry} ...")
    contracts_payload = get(token, "/v2/expired-instruments/option/contract",
                            {"instrument_key": args.index_key, "expiry_date": args.expiry})
    contracts = (contracts_payload.get("data") or [])
    if isinstance(contracts, dict):
        contracts = contracts.get("contracts") or contracts.get("data") or []
    print(f"Contracts listed: {len(contracts)}")
    if not contracts:
        print("No contracts returned. Check Plus plan access, the expiry date, and the index key.", file=sys.stderr)
        return 4
    # Normalise contract fields defensively — field names vary by SDK version.
    norm = []
    for c in contracts:
        if not isinstance(c, dict):
            continue
        norm.append({
            "strike": c.get("strike_price") or c.get("strike") or c.get("strikePrice"),
            "type": (c.get("option_type") or c.get("optionType") or "").upper(),
            "key": c.get("expired_instrument_key") or c.get("instrument_key"),
            "symbol": c.get("trading_symbol") or c.get("symbol"),
        })
    norm = [c for c in norm if c["strike"] is not None and c["key"] and c["type"] in ("CE", "PE")]
    by_strike_type = {(float(c["strike"]), c["type"]): c["key"] for c in norm}
    print(f"Usable CE/PE contracts: {len(by_strike_type)}")

    # 4. Per day, fetch only strikes near that day's spot range.
    opt_rows = []
    for day, day_spot in spot.groupby("date"):
        day_str = day.strftime("%Y-%m-%d")
        lo = float(day_spot["low"].min()) - 300
        hi = float(day_spot["high"].max()) + 300
        strikes = [s for s in range(int(lo // 100 * 100), int(hi // 100 * 100) + 100, 100)]
        for strike in strikes:
            for opt_type in ("CE", "PE"):
                key = by_strike_type.get((float(strike), opt_type))
                if not key:
                    continue
                enc = quote(key, safe="")
                try:
                    payload = get(token, f"/v2/expired-instruments/historical-candle/{enc}/5minute/{day_str}/{day_str}")
                except RuntimeError as e:
                    print(f"  skip {strike} {opt_type} {day_str}: {e}")
                    continue
                df = candles_to_df(payload)
                for _, r in df.iterrows():
                    opt_rows.append({
                        "timestamp": r["timestamp"], "strike": strike,
                        "option_type": opt_type, "expiry": args.expiry,
                        "open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"],
                    })
                time.sleep(args.sleep)
        print(f"  {day_str}: collected {len(opt_rows)} option candles so far.")

    opts = pd.DataFrame(opt_rows)
    opts.to_csv(f"{args.out_dir}/option_5m.csv", index=False)
    print(f"Done. Files in {args.out_dir}: spot_5m.csv, spot_daily.csv, option_5m.csv ({len(opts)} option candles).")
    print("Next: run backtest_3_blue_line.py against these three files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
