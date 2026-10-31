"""Progressive fetcher Jan 2025-Oct 2026, Nifty/BankNifty/stocks, Upstox only.
Read-only, no orders. Cache in ~/workspace/trading/data/progressive/<SYMBOL>/spot_5m.csv
and spot_daily.csv. One request per instrument-month (5-min candles).
Instrument keys resolved via Upstox instrument search, exact trading_symbol
match preferred; otherwise first NSE_EQ result is recorded in keys.json and
must be checked before use.
"""
import argparse, json, os, sys, time, urllib.parse
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
SYMBOLS = {
 "NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank",
 "GODREJCP": None, "GLENMARK": None, "ITC": None, "RECLTD": None, "TVSMOTOR": None,
 "UNITDSPR": None, "OBEROIRLTY": None, "NTPC": None, "INDUSTOWER": None,
 "KALYANKJIL": None, "HDFCBANK": None, "NHPC": None, "PFC": None, "IRCTC": None,
 "WIPRO": None, "NATIONALUM": None, "VEDL": None, "HINDCOPPER": None,
 "HINDZINC": None, "HINDALCO": None, "TATASTEEL": None, "ASTRAL": None,
 "BDL": None, "OIL": None, "HINDUNILVR": None,
}
# Known Upstox trading_symbol aliases for TradingView tickers
ALIASES = {"RECLTD": "REC", "KALYANKJIL": "KALYANKJIL", "NATIONALUM": "NATIONALUM",
           "HINDCOPPER": "HINDCOPPER", "HINDUNILVR": "HINDUNILVR"}

def resolve(symbol):
    if SYMBOLS[symbol]:
        return SYMBOLS[symbol]
    q = ALIASES.get(symbol, symbol)
    p = call("/v2/instruments/search", {"query": q, "exchanges": "NSE", "segments": "EQ"})
    data = p.get("data") or []
    for d in data:
        if d.get("trading_symbol") == q:
            return d["instrument_key"]
    for d in data:
        if d.get("trading_symbol") == symbol:
            return d["instrument_key"]
    if data:
        return data[0]["instrument_key"]
    raise RuntimeError(f"No instrument found for {symbol} (query {q})")

def month_range(year, month):
    import calendar
    first = f"{year}-{month:02d}-01"
    last = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
    return first, last

def fetch_month(symbol, key, year, month):
    outdir = os.path.join(BASE, symbol)
    os.makedirs(outdir, exist_ok=True)
    first, last = month_range(year, month)
    enc = urllib.parse.quote(key, safe="")
    # Upstox v3: /minutes/5/{to}/{from}
    payload = call(f"/v3/historical-candle/{enc}/minutes/5/{last}/{first}")
    df = candles_df(payload)
    if df.empty:
        print(f"{symbol} {year}-{month:02d}: EMPTY", flush=True)
        return 0
    df = df[["timestamp","open","high","low","close"]]
    spot_path = os.path.join(outdir, "spot_5m.csv")
    if os.path.exists(spot_path):
        old = pd.read_csv(spot_path, parse_dates=["timestamp"])
        df = pd.concat([old, df]).drop_duplicates("timestamp").sort_values("timestamp")
    df.to_csv(spot_path, index=False)
    d = df.copy()
    d["timestamp"] = pd.to_datetime(d["timestamp"]).dt.tz_localize(None)
    d["date"] = d["timestamp"].dt.normalize()
    daily = d.groupby("date").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).reset_index()
    daily.to_csv(os.path.join(outdir, "spot_daily.csv"), index=False)
    print(f"{symbol} {year}-{month:02d}: {len(df)} cumulative bars, {len(daily)} days", flush=True)
    return len(df)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--month", type=int, required=True)
    ap.add_argument("--symbols", nargs="*", default=None)
    ap.add_argument("--sleep", type=float, default=0.3)
    a = ap.parse_args()
    syms = a.symbols or list(SYMBOLS.keys())
    keys_path = os.path.join(BASE, "keys.json")
    keys = json.load(open(keys_path)) if os.path.exists(keys_path) else {}
    for s in syms:
        try:
            if s not in keys:
                keys[s] = resolve(s)
                os.makedirs(BASE, exist_ok=True)
                json.dump(keys, open(keys_path,"w"), indent=2)
                print(f"KEY {s} -> {keys[s]}", flush=True)
            fetch_month(s, keys[s], a.year, a.month)
        except Exception as e:
            print(f"ERROR {s}: {e}", flush=True)
        time.sleep(a.sleep)

if __name__ == "__main__":
    main()
