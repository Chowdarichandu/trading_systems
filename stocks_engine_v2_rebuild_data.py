#!/usr/bin/env python3
"""v2 data rebuild: recreate the 2025-validation shadow dataset PERSISTENTLY.

The validation's shadow dataset (/tmp/val2025/data) was lost with /tmp.
This rebuilds the identical construction under ~/workspace/trading/data/full_hist/:
  = copy of data/progressive for the 25 stocks + NIFTY
  + Sep-2025 5m+daily fills for ASTRAL, BDL, HINDUNILVR, OIL (fetched fresh, Upstox)
  + Q4-2024 daily lookback rows prepended to every symbol's spot_daily.csv
    (daily bars only; 5m untouched for 2024, exactly as the validation did)
The main cache data/progressive is NEVER written.
Equivalence is proven downstream by the anchors in stocks_engine_v2_build.py
(F4/INV 2025 must reproduce 506 trades / +Rs2,548.77 exactly).
Read-only API use. No orders. No secrets stored.
"""
import json, os, shutil, sys, time, urllib.parse
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df
import pandas as pd

SRC = "/home/hatch/workspace/trading/data/progressive"
DST = "/home/hatch/workspace/trading/data/full_hist"
SYMS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
        "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
        "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
        "ASTRAL","BDL","OIL","HINDUNILVR","NIFTY"]
FILL_SYMS = ["ASTRAL","BDL","HINDUNILVR","OIL"]
KEYS = json.load(open(f"{SRC}/keys.json"))

def daterange_daily(key, frm, to):
    """Daily bars via v3 days/1, fallback v2 day. Returns DataFrame[date,open,high,low,close]."""
    enc = urllib.parse.quote(key, safe="")
    try:
        payload = call(f"/v3/historical-candle/{enc}/days/1/{to}/{frm}")
        df = candles_df(payload)
    except Exception as e:
        print(f"    v3 days failed ({e}); trying v2 day", flush=True)
        df = pd.DataFrame()
    if df.empty:
        payload = call(f"/v2/historical-candle/{enc}/day/{to}/{frm}")
        df = candles_df(payload)
    if df.empty:
        return df
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    return df[["date","open","high","low","close"]].drop_duplicates("date").sort_values("date")

def main():
    os.makedirs(DST, exist_ok=True)
    # 1) copy main cache
    for s in SYMS:
        d = os.path.join(DST, s)
        os.makedirs(d, exist_ok=True)
        for fn in ("spot_5m.csv","spot_daily.csv"):
            src_f, dst_f = os.path.join(SRC, s, fn), os.path.join(d, fn)
            if not os.path.exists(dst_f):
                shutil.copyfile(src_f, dst_f)
    print("copied main cache -> full_hist", flush=True)
    # 2) Sep-2025 fills (5m merge + daily rebuild) for the 4 hole symbols
    for s in FILL_SYMS:
        key = KEYS[s]; enc = urllib.parse.quote(key, safe="")
        payload = call(f"/v3/historical-candle/{enc}/minutes/5/2025-09-30/2025-09-01")
        df = candles_df(payload)
        if df.empty:
            print(f"FILL {s}: EMPTY - PROBLEM", flush=True); continue
        df = df[["timestamp","open","high","low","close"]].copy()
        df["timestamp"] = (pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
                           .dt.strftime("%Y-%m-%d %H:%M:%S") + "+05:30")
        spot_path = os.path.join(DST, s, "spot_5m.csv")
        old = pd.read_csv(spot_path, dtype={"timestamp": str})
        merged = pd.concat([old, df]).drop_duplicates("timestamp").sort_values("timestamp")
        merged.to_csv(spot_path, index=False)
        d = merged.copy()
        d["date"] = pd.to_datetime(d["timestamp"]).dt.strftime("%Y-%m-%d")
        daily = d.groupby("date").agg(open=("open","first"), high=("high","max"),
                                      low=("low","min"), close=("close","last")).reset_index()
        daily["date"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m-%d")
        daily.to_csv(os.path.join(DST, s, "spot_daily.csv"), index=False)
        sep_days = daily[(daily["date"] >= "2025-09-01") & (daily["date"] <= "2025-09-30")]
        print(f"FILL {s}: sep-2025 days now {len(sep_days)} (expect 22), total daily {len(daily)}", flush=True)
        time.sleep(0.3)
    # 3) Q4-2024 daily lookback for every symbol (skip if already present)
    for s in SYMS:
        dp = os.path.join(DST, s, "spot_daily.csv")
        daily = pd.read_csv(dp)
        if str(daily["date"].min()) <= "2024-12-31":
            print(f"LOOKBACK {s}: already starts {daily['date'].min()}, skip", flush=True)
            continue
        lb = daterange_daily(KEYS[s], "2024-10-01", "2024-12-31")
        if lb.empty:
            print(f"LOOKBACK {s}: EMPTY - PROBLEM", flush=True); continue
        out = pd.concat([lb, daily]).drop_duplicates("date").sort_values("date")
        out.to_csv(dp, index=False)
        print(f"LOOKBACK {s}: +{len(lb)} rows, daily now {out['date'].min()}..{out['date'].max()} ({len(out)})", flush=True)
        time.sleep(0.3)
    print("REBUILD DONE", flush=True)

if __name__ == "__main__":
    raise SystemExit(main())
