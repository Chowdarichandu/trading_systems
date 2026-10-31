"""Fetch 5-min candles WITH volume for the 25 stocks, Jan-Oct 2026, Upstox.
Read-only. Does NOT overwrite data/progressive (OHLC cache). Output:
data/progressive_vol/<SYM>/spot_5m_vol.csv (timestamp,open,high,low,close,volume).
One request per symbol-month, same endpoint as progressive_fetch.py."""
import json, os, sys, time, urllib.parse, calendar
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading/data/progressive_vol")
KEYS = json.load(open(os.path.expanduser("~/workspace/trading/data/progressive/keys.json")))
STOCKS = [k for k in KEYS if k not in ("NIFTY", "BANKNIFTY")]

def main():
    summary = {}
    for sym in STOCKS:
        key = KEYS[sym]
        enc = urllib.parse.quote(key, safe="")
        frames = []
        for month in range(1, 11):
            first = f"2026-{month:02d}-01"
            last = f"2026-{month:02d}-{calendar.monthrange(2026, month)[1]:02d}"
            try:
                p = call(f"/v3/historical-candle/{enc}/minutes/5/{last}/{first}")
                df = candles_df(p)
            except Exception as e:
                print(f"ERROR {sym} {month}: {e}", flush=True)
                df = pd.DataFrame()
            if not df.empty:
                frames.append(df[["timestamp", "open", "high", "low", "close", "volume"]])
            print(f"{sym} 2026-{month:02d}: {len(df)} bars", flush=True)
            time.sleep(0.3)
        full = pd.concat(frames).drop_duplicates("timestamp").sort_values("timestamp") if frames else pd.DataFrame()
        outdir = os.path.join(BASE, sym)
        os.makedirs(outdir, exist_ok=True)
        full.to_csv(os.path.join(outdir, "spot_5m_vol.csv"), index=False)
        summary[sym] = len(full)
        print(f"== {sym} TOTAL {len(full)}", flush=True)
    json.dump(summary, open(os.path.join(BASE, "fetch_counts.json"), "w"), indent=2)

if __name__ == "__main__":
    main()
