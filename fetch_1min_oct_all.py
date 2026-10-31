"""LINE 7 STEP 2a — fetch 1-min candles, October 2026, all 50 stocks.
One request per stock (feasibility showed a one-month 1-min request
returns complete data). Saves data/1min_stocks_oct2026/<old|ext>/<SYM>.csv
(timestamp,open,high,low,close,volume) and a verification JSON:
bars per stock, days, per-day counts, non-375 days.
Read-only, paper only.
"""
import json, os, sys, time, urllib.parse
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df

BASE = os.path.expanduser("~/workspace/trading")
OUT = f"{BASE}/data/1min_stocks_oct2026"
KH = json.load(open(f"{BASE}/data/progressive/keys.json"))
KE = json.load(open(f"{BASE}/data/progressive_ext/keys_ext.json"))
UNIV = {"old": {k: v for k, v in KH.items() if k not in ("NIFTY", "BANKNIFTY")},
        "ext": {k: v for k, v in KE.items() if k not in ("NIFTY", "BANKNIFTY")}}


def main():
    verify = {}
    for which, keys in UNIV.items():
        os.makedirs(f"{OUT}/{which}", exist_ok=True)
        for sym, key in keys.items():
            path = f"{OUT}/{which}/{sym}.csv"
            if os.path.exists(path):
                print(f"cached {which}/{sym}", flush=True)
                continue
            enc = urllib.parse.quote(key, safe="")
            try:
                df = candles_df(call(f"/v3/historical-candle/{enc}/minutes/1/2026-10-31/2026-10-01"))
            except Exception as e:
                verify[f"{which}/{sym}"] = {"error": str(e)[:300]}
                print(f"ERROR {which}/{sym}: {e}", flush=True)
                continue
            df[["timestamp", "open", "high", "low", "close", "volume"]].to_csv(path, index=False)
            d = df.copy()
            d["day"] = d["timestamp"].dt.strftime("%Y-%m-%d")
            per_day = {k: int(v) for k, v in d.groupby("day").size().items()}
            verify[f"{which}/{sym}"] = {
                "bars": int(len(df)), "days": len(per_day),
                "non375": {k: v for k, v in per_day.items() if v != 375},
                "day_list": sorted(per_day.keys())}
            print(f"ok {which}/{sym}: {len(df)} bars, {len(per_day)} days, "
                  f"non375={verify[f'{which}/{sym}']['non375']}", flush=True)
            time.sleep(0.3)
    json.dump(verify, open(f"{OUT}/verification.json", "w"), indent=2)
    print("WROTE verification.json", flush=True)


if __name__ == "__main__":
    main()
