"""LINE 4 Step 1 — fetch the NEW 25-stock universe (Nifty 50 names NOT in the
original watchlist). Same verified Upstox connector path as
fetch_vol_janoct.py (call/candles_df from fetch_upstox_via_connector).
Read-only, no orders. Instrument-search endpoint returns 401 today, so keys
are NSE_EQ|<ISIN> with ISINs taken from the NSE Indices NIFTY-50 constituent
list (cross-checked: the 7 ISINs that overlap the original keys.json match
exactly); TITAN/ULTRACEMCO ISINs confirmed against NSE circular / Moneycontrol.

Outputs:
  data/progressive_vol_ext/<SYM>/spot_5m_vol.csv   (Jan-Oct 2026, with volume)
  data/progressive_vol_ext/<SYM>/daily_api.csv     (daily endpoint, 2025-01-01..2026-10-28)
  data/progressive_ext/<SYM>/spot_5m.csv           (OHLC view of the same 5m bars)
  data/progressive_ext/<SYM>/spot_daily.csv        (2026 daily derived from 5m bars,
      exactly as progressive_fetch.py built the original cache; 2025 rows from the
      daily endpoint for MA/ADR lookback parity with the original universe)
  data/progressive_ext/keys_ext.json
"""
import calendar, json, os, sys, time, urllib.parse
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df
import pandas as pd

TRADING = os.path.expanduser("~/workspace/trading")
VBASE = os.path.join(TRADING, "data/progressive_vol_ext")
EBASE = os.path.join(TRADING, "data/progressive_ext")

ISIN = {
    "RELIANCE": "INE002A01018", "TCS": "INE467B01029", "ICICIBANK": "INE090A01021",
    "INFY": "INE009A01021", "BHARTIARTL": "INE397D01024", "SBIN": "INE062A01020",
    "LT": "INE018A01030", "AXISBANK": "INE238A01034", "KOTAKBANK": "INE237A01028",
    "BAJFINANCE": "INE296A01024", "HCLTECH": "INE860A01027", "MARUTI": "INE585B01010",
    "SUNPHARMA": "INE044A01036", "TITAN": "INE280A01028", "M&M": "INE101A01026",
    "ULTRACEMCO": "INE481G01011", "NESTLEIND": "INE239A01016", "POWERGRID": "INE752E01010",
    "ONGC": "INE213A01029", "COALINDIA": "INE522F01014", "JSWSTEEL": "INE019A01038",
    "GRASIM": "INE047A01021", "CIPLA": "INE059A01026", "DRREDDY": "INE089A01023",
    "EICHERMOT": "INE066A01021",
}
KEYS = {s: f"NSE_EQ|{v}" for s, v in ISIN.items()}

def fetch_5m(key):
    enc = urllib.parse.quote(key, safe="")
    frames = []
    for month in range(1, 11):
        first = f"2026-{month:02d}-01"
        last = f"2026-{month:02d}-{calendar.monthrange(2026, month)[1]:02d}"
        try:
            p = call(f"/v3/historical-candle/{enc}/minutes/5/{last}/{first}")
            df = candles_df(p)
        except Exception as e:
            print(f"  ERROR 5m {month}: {e}", flush=True)
            df = pd.DataFrame()
        if not df.empty:
            frames.append(df[["timestamp", "open", "high", "low", "close", "volume"]])
        print(f"  2026-{month:02d}: {len(df)} bars", flush=True)
        time.sleep(0.3)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames).drop_duplicates("timestamp").sort_values("timestamp")

def fetch_daily(key):
    enc = urllib.parse.quote(key, safe="")
    frames = []
    # quarterly chunks 2025-01-01 .. 2026-10-28
    chunks = [("2025-03-31", "2025-01-01"), ("2025-06-30", "2025-04-01"),
              ("2025-09-30", "2025-07-01"), ("2025-12-31", "2025-10-01"),
              ("2026-03-31", "2026-01-01"), ("2026-06-30", "2026-04-01"),
              ("2026-09-30", "2026-07-01"), ("2026-10-28", "2026-10-01")]
    for last, first in chunks:
        try:
            p = call(f"/v3/historical-candle/{enc}/days/1/{last}/{first}")
            df = candles_df(p)
        except Exception as e:
            print(f"  ERROR daily {first}..{last}: {e}", flush=True)
            df = pd.DataFrame()
        if not df.empty:
            frames.append(df[["timestamp", "open", "high", "low", "close", "volume"]])
        time.sleep(0.3)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames).drop_duplicates("timestamp").sort_values("timestamp")
    return out

def main():
    os.makedirs(VBASE, exist_ok=True); os.makedirs(EBASE, exist_ok=True)
    json.dump(KEYS, open(os.path.join(EBASE, "keys_ext.json"), "w"), indent=2)
    summary = {}
    for sym, key in KEYS.items():
        print(f"== {sym} {key}", flush=True)
        vdir = os.path.join(VBASE, sym); edir = os.path.join(EBASE, sym)
        os.makedirs(vdir, exist_ok=True); os.makedirs(edir, exist_ok=True)
        f5 = fetch_5m(key)
        f5.to_csv(os.path.join(vdir, "spot_5m_vol.csv"), index=False)
        fd = fetch_daily(key)
        fd.to_csv(os.path.join(vdir, "daily_api.csv"), index=False)
        # engine-compat OHLC 5m (timestamps naive, as the original cache)
        e5 = f5.copy()
        if not e5.empty:
            e5["timestamp"] = pd.to_datetime(e5["timestamp"]).dt.tz_localize(None)
            e5[["timestamp", "open", "high", "low", "close"]].to_csv(
                os.path.join(edir, "spot_5m.csv"), index=False)
            d = e5.copy(); d["date"] = d["timestamp"].dt.normalize()
            daily26 = d.groupby("date").agg(open=("open", "first"), high=("high", "max"),
                                            low=("low", "min"), close=("close", "last")).reset_index()
        else:
            daily26 = pd.DataFrame(columns=["date", "open", "high", "low", "close"])
        # 2025 daily rows from the daily endpoint (dates not in the 5m-derived set)
        rows = []
        have = set(pd.to_datetime(daily26["date"]).dt.strftime("%Y-%m-%d")) if not daily26.empty else set()
        for _, r in fd.iterrows():
            ds = pd.to_datetime(r["timestamp"]).strftime("%Y-%m-%d")
            if ds < "2026-01-01" and ds not in have:
                rows.append({"date": pd.Timestamp(ds), "open": r["open"], "high": r["high"],
                             "low": r["low"], "close": r["close"]})
        daily_all = pd.concat([pd.DataFrame(rows), daily26]).sort_values("date") if rows or not daily26.empty else daily26
        daily_all.to_csv(os.path.join(edir, "spot_daily.csv"), index=False)
        summary[sym] = {"bars_5m": int(len(f5)), "daily_api_rows": int(len(fd)),
                        "daily_rows_total": int(len(daily_all))}
        print(f"== {sym} DONE 5m={len(f5)} daily_api={len(fd)} daily_total={len(daily_all)}", flush=True)
    json.dump(summary, open(os.path.join(VBASE, "fetch_counts.json"), "w"), indent=2)
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    main()
