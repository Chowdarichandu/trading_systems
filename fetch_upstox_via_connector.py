"""Fetch Upstox Bank Nifty data via the registered custom.upstox connector.

Read-only. No orders. No secret is stored here; the credential reaches the
request only through the dynamic-credentials surrogate exchange.

Modes:
  --step spot       spot 5m + daily only
  --step contracts  expired option contracts for --expiry only
  --step options    option 5m candles, using cached spot + contracts
  --step all        all of the above, in order

Example (October 2026 pilot):
  python3 fetch_upstox_via_connector.py --step all \
      --index-key 'NSE_INDEX|Nifty Bank' --expiry 2026-10-27 \
      --from-date 2026-09-29 --to-date 2026-10-27 \
      --out-dir ~/workspace/trading/data/banknifty-2026-10
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(path, params=None):
    url = "https://api.upstox.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "BankNiftyBacktestFetcher/1.0",
    })
    add_surrogate_to_request(req, "custom.upstox", allowed_hosts=["api.upstox.com"])
    for attempt in range(4):
        try:
            with urllib.request.build_opener(NoRedirect()).open(req, timeout=60) as resp:
                return read_json_response(resp)
        except Exception as e:
            msg = str(e)
            if "429" in msg and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise


def candles_df(payload):
    rows = (payload.get("data") or {}).get("candles") or []
    df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=["spot", "contracts", "options", "all"], default="all")
    ap.add_argument("--index-key", default="NSE_INDEX|Nifty Bank")
    ap.add_argument("--expiry", required=True)
    ap.add_argument("--from-date", required=True)
    ap.add_argument("--to-date", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--sleep", type=float, default=0.25)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    enc_key = urllib.parse.quote(args.index_key, safe="")

    spot_path = f"{args.out_dir}/spot_5m.csv"
    daily_path = f"{args.out_dir}/spot_daily.csv"
    contracts_path = f"{args.out_dir}/contracts.json"
    opts_path = f"{args.out_dir}/option_5m.csv"

    if args.step in ("spot", "all"):
        print(f"Fetching spot 5m {args.from_date} to {args.to_date} ...", flush=True)
        payload = call(f"/v3/historical-candle/{enc_key}/minutes/5/{args.to_date}/{args.from_date}")
        spot = candles_df(payload)
        print(f"Spot candles: {len(spot)}", flush=True)
        if spot.empty:
            print("ERROR: no spot candles returned.", file=sys.stderr)
            return 3
        spot[["timestamp", "open", "high", "low", "close"]].to_csv(spot_path, index=False)
        spot["date"] = spot["timestamp"].dt.normalize()
        daily = spot.groupby("date").agg(
            open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")
        ).reset_index()
        daily.to_csv(daily_path, index=False)
        print(f"Spot days: {len(daily)}", flush=True)

    if args.step in ("contracts", "all"):
        print(f"Fetching expired option contracts for {args.expiry} ...", flush=True)
        payload = call("/v2/expired-instruments/option/contract",
                       {"instrument_key": args.index_key, "expiry_date": args.expiry})
        with open(contracts_path, "w") as f:
            json.dump(payload, f, indent=2)
        data = payload.get("data") or []
        print(f"Contracts returned: {len(data)}", flush=True)
        if data:
            print("Sample contract keys:", list(data[0].keys()), flush=True)
            print(json.dumps(data[0], indent=2)[:1000], flush=True)

    if args.step in ("options", "all"):
        spot = pd.read_csv(spot_path, parse_dates=["timestamp"])
        with open(contracts_path) as f:
            payload = json.load(f)
        contracts = payload.get("data") or []
        by_key = {}
        for c in contracts:
            if not isinstance(c, dict):
                continue
            strike = c.get("strike_price") or c.get("strike")
            otype = (c.get("option_type") or c.get("optionType") or c.get("instrument_type") or "").upper()
            key = c.get("expired_instrument_key") or c.get("instrument_key")
            if strike is not None and key and otype in ("CE", "PE"):
                by_key[(float(strike), otype)] = key
        print(f"Usable contracts: {len(by_key)}", flush=True)
        if not by_key:
            print("ERROR: no usable contracts. Inspect contracts.json field names.", file=sys.stderr)
            return 4
        # Resume: skip strike/day pairs already in the output file.
        done = set()
        if os.path.exists(opts_path):
            try:
                old = pd.read_csv(opts_path, parse_dates=["timestamp"])
                if not old.empty:
                    old["date"] = old["timestamp"].dt.strftime("%Y-%m-%d")
                    done = set(zip(old["date"], old["strike"].astype(float), old["option_type"]))
                    print(f"Resuming, already fetched pairs: {len(done)}", flush=True)
            except Exception:
                pass
        spot["date"] = spot["timestamp"].dt.normalize()
        rows = []
        for day, day_spot in spot.groupby("date"):
            day_str = day.strftime("%Y-%m-%d")
            lo = float(day_spot["low"].min()) - 300
            hi = float(day_spot["high"].max()) + 300
            strikes = list(range(int(lo // 100 * 100), int(hi // 100 * 100) + 100, 100))
            for strike in strikes:
                for otype in ("CE", "PE"):
                    if (day_str, float(strike), otype) in done:
                        continue
                    key = by_key.get((float(strike), otype))
                    if not key:
                        continue
                    enc = urllib.parse.quote(key, safe="")
                    try:
                        payload = call(f"/v2/expired-instruments/historical-candle/{enc}/5minute/{day_str}/{day_str}")
                    except Exception as e:
                        print(f"  skip {strike} {otype} {day_str}: {e}", flush=True)
                        continue
                    df = candles_df(payload)
                    for _, r in df.iterrows():
                        rows.append({"timestamp": r["timestamp"], "strike": strike,
                                     "option_type": otype, "expiry": args.expiry,
                                     "open": r["open"], "high": r["high"], "low": r["low"], "close": r["close"]})
                    time.sleep(args.sleep)
            print(f"  {day_str}: cumulative option rows {len(rows)}", flush=True)
            if rows:
                pd.DataFrame(rows).to_csv(opts_path, index=False)
        if rows:
            pd.DataFrame(rows).to_csv(opts_path, index=False)
        print(f"Done. Option rows this run: {len(rows)} -> {opts_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
