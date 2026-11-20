#!/usr/bin/env python3
"""SECTOR COVERAGE — Steps 1-3 data: for the frozen 25 and every
completion candidate, from the LOCAL daily dump only
(universe_daily/<SYM>.parquet):
  - median daily traded value (close x volume) over Oct 2026, Rs crore
  - latest close + date
  - 2026 YTD % (first 2026 close -> latest close)
Writes sector_liquidity.json. No external fetch."""
import json, os
import pandas as pd

WS = "/home/hatch/workspace/trading"
DUMP = f"{WS}/universe_daily"

FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]

# sector -> candidate symbols to evaluate
CANDIDATES = {
    "Cement": ["ULTRACEMCO", "AMBUJACEM"],
    "Capital Goods": ["LT"],
    "Insurance": ["SBILIFE", "HDFCLIFE", "ICICIPRULI"],
    "Hospitals": ["APOLLOHOSP", "MAXHEALTH"],
    "Banking": ["SBIN", "ICICIBANK"],
    "Energy (Oil & Gas)": ["RELIANCE", "ONGC"],
    "IT": ["INFY", "TCS"],
    "Auto": ["MARUTI", "M&M"],
    "Telecom": ["BHARTIARTL"],
    "Pharma": ["SUNPHARMA", "CIPLA"],
    "Retail / Consumer Durables": ["TRENT", "TITAN"],
}


def metrics(sym):
    path = f"{DUMP}/{sym}.parquet"
    if not os.path.exists(path):
        return {"sym": sym, "present": False}
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    oct26 = df[(df["date"] >= "2026-10-01") & (df["date"] <= "2026-10-31")]
    med_val_cr = float((oct26["close"] * oct26["volume"]).median()) / 1e7
    latest = df.iloc[-1]
    y26 = df[df["date"] >= "2026-01-01"]
    ytd = None
    if len(y26) > 1:
        ytd = round(100.0 * (float(y26.iloc[-1]["close"]) /
                             float(y26.iloc[0]["close"]) - 1.0), 1)
    return {"sym": sym, "present": True,
            "oct2026_median_traded_value_cr": round(med_val_cr, 2),
            "oct2026_sessions": int(len(oct26)),
            "latest_close": round(float(latest["close"]), 2),
            "latest_date": str(latest["date"].date()),
            "ytd2026_pct": ytd,
            "clears_1cr_floor_x": round(med_val_cr / 1.0, 1)}


def main():
    out = {"frozen25": {}, "candidates": {}}
    for s in FROZEN25:
        out["frozen25"][s] = metrics(s)
    for sector, syms in CANDIDATES.items():
        out["candidates"][sector] = [metrics(s) for s in syms]
    json.dump(out, open(f"{WS}/sector_liquidity.json", "w"), indent=1)
    for s, m in out["frozen25"].items():
        print(f"25  {s:12s} medVal ₹{m['oct2026_median_traded_value_cr']:>9} cr  "
              f"close {m['latest_close']:>9}  YTD26 {m['ytd2026_pct']}")
    for sector, rows in out["candidates"].items():
        for m in rows:
            if m["present"]:
                print(f"CAND {sector:28s} {m['sym']:12s} medVal "
                      f"₹{m['oct2026_median_traded_value_cr']:>9} cr  close "
                      f"{m['latest_close']:>9}  YTD26 {m['ytd2026_pct']}  "
                      f"floor x{m['clears_1cr_floor_x']}")
            else:
                print(f"CAND {sector:28s} {m['sym']:12s} MISSING FROM DUMP")


if __name__ == "__main__":
    main()
