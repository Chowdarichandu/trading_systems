#!/usr/bin/env python3
"""ROUND 15 — WS2 (R15-04): BUILD the daily-volume data axis.

Fetches daily candles (v3 days/1) for the 25 watchlist stocks
+ NIFTY via the registered connector path
(fetch_upstox_via_connector.call — browser User-Agent header,
credential only through the connector surrogate, never
printed or stored here). Stores a NEW dataset:
  stocks_daily_volume.csv          (stock, date, volume)
  stocks_daily_volume_coverage.json
No existing candle file is altered. Stored span 2024-11-15
-> 2026-10-31; the pre-2025 tail is lookback only, for the
trailing-20-day median in WS3's frozen definition. Coverage
is validated per stock-year for 2025 and 2026 against the
engine machinery's own daily series: every missing day is
named as a hole; zero-volume days are counted and named;
NO missing value is estimated.
"""
import csv, json, os, sys, time, urllib.parse
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
from fetch_upstox_via_connector import call, candles_df
import stocks_engine_r14_builders as B14

KEYS = json.load(open(f"{WS}/data/progressive/keys.json"))
SYMS = sorted(k for k in KEYS if k != "BANKNIFTY")
assert len(SYMS) == 26, SYMS  # 25 stocks + NIFTY
CHUNKS = [("2024-11-15", "2024-12-31"),
          ("2025-01-01", "2025-12-31"),
          ("2026-01-01", "2026-10-31")]

series = {}   # sym -> {date: volume}
errors = {}
for sym in SYMS:
    enc = urllib.parse.quote(KEYS[sym], safe="")
    got = {}
    for frm, to in CHUNKS:
        try:
            df = candles_df(call(
                f"/v3/historical-candle/{enc}/days/1/{to}/{frm}"))
        except Exception as e:
            errors.setdefault(sym, []).append(f"{frm}..{to}: "
                                              f"{str(e)[:120]}")
            continue
        for _, x in df.iterrows():
            d = str(x["timestamp"])[:10]
            got[d] = int(x["volume"])
        time.sleep(0.3)
    series[sym] = got
    print(f"{sym}: {len(got)} days "
          f"({min(got) if got else '-'} .. {max(got) if got else '-'})"
          f"{' ERRORS ' + str(errors[sym]) if sym in errors else ''}",
          flush=True)

# ------------------------------------------------------------ store --
out_path = f"{WS}/stocks_daily_volume.csv"
with open(out_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stock", "date", "volume"])
    for sym in SYMS:
        for d in sorted(series[sym]):
            w.writerow([sym, d, series[sym][d]])
print(f"stored {out_path}: "
      f"{sum(len(v) for v in series.values())} rows")

# --------------------------------------------------------- coverage --
g = B14.machinery()
STOCKS_E = g["STOCKS_E"]
expected = {}
for sym in SYMS:
    if sym == "NIFTY":
        continue
    daily = STOCKS_E[sym][1]
    expected[sym] = sorted({str(r["date"])[:10] for r in daily})
cal = sorted({d for sym in expected for d in expected[sym]})
expected["NIFTY"] = cal  # index validated against the union calendar

coverage = {"span_stored": ["2024-11-15", "2026-10-31"],
            "source": "Upstox v3 historical-candle days/1 via "
                      "registered connector (UA header; "
                      "surrogate credential)",
            "fetch_errors": errors,
            "per_stock_year": {}}
for sym in SYMS:
    for yr in (2025, 2026):
        exp = [d for d in expected[sym] if d[:4] == str(yr)]
        have = series[sym]
        holes = [d for d in exp if d not in have]
        zeros = [d for d in exp if d in have and have[d] == 0]
        extra = [d for d in have
                 if d[:4] == str(yr) and d not in set(exp)]
        coverage["per_stock_year"][f"{sym}|{yr}"] = {
            "expected_days": len(exp), "present": len(exp) - len(holes),
            "holes": holes, "zero_volume_days": zeros,
            "extra_days_not_in_machinery": extra}
        print(f"coverage {sym} {yr}: expected {len(exp)}, "
              f"holes {len(holes)}, zero-vol {len(zeros)}, "
              f"extra {len(extra)}")
json.dump(coverage, open(f"{WS}/stocks_daily_volume_coverage.json",
                         "w"), indent=1)
print("coverage written.")
