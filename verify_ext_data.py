"""LINE 4 Step 1 — verification of the NEW universe data.
Per stock: 5m bar counts by month, trading days, bars/day anomalies,
zero-volume share, OHLC self-consistency (0 tolerance: daily row derived
from 5m bars must equal first/max/min/last of the day's bars exactly),
and a cross-check of the daily-ENDPOINT 2026 rows against the 5m-derived
daily rows (independent source — differences reported, not hidden).
Writes universe_ext_verification.json + prints a markdown table.
"""
import csv, json, os
from collections import defaultdict

TRADING = os.path.expanduser("~/workspace/trading")
EBASE = os.path.join(TRADING, "data/progressive_ext")
VBASE = os.path.join(TRADING, "data/progressive_vol_ext")
SYMS = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "LT",
        "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA",
        "TITAN", "M&M", "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC",
        "COALINDIA", "JSWSTEEL", "GRASIM", "CIPLA", "DRREDDY", "EICHERMOT"]

out = {}
for sym in SYMS:
    vp = os.path.join(VBASE, sym, "spot_5m_vol.csv")
    bars = defaultdict(list)
    zerovol = 0; tot = 0
    with open(vp) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            bars[d].append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                            float(r["low"]), float(r["close"]), float(r["volume"])))
            tot += 1
            if float(r["volume"]) == 0: zerovol += 1
    for d in bars: bars[d].sort()
    months = defaultdict(int)
    for d, bs in bars.items(): months[d[:7]] += len(bs)
    bad_days = {d: len(bs) for d, bs in bars.items() if len(bs) != 75}
    # self-consistency vs engine daily file (2026 rows)
    derived = {}
    with open(os.path.join(EBASE, sym, "spot_daily.csv")) as f:
        for r in csv.DictReader(f):
            derived[r["date"][:10]] = (float(r["open"]), float(r["high"]),
                                        float(r["low"]), float(r["close"]))
    self_bad = []
    for d, bs in bars.items():
        want = (bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4])
        got = derived.get(d)
        if got != want: self_bad.append(d)
    # cross-check vs daily endpoint (2026 rows only)
    api = {}
    with open(os.path.join(VBASE, sym, "daily_api.csv")) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            if d >= "2026-01-01":
                api[d] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    field_exact = [0, 0, 0, 0]; common = 0; maxdiff = [0.0] * 4; close_off = []
    for d, av in api.items():
        if d not in derived: continue
        common += 1
        dv = derived[d]
        for k in range(4):
            if av[k] == dv[k]: field_exact[k] += 1
            maxdiff[k] = max(maxdiff[k], abs(av[k] - dv[k]))
        if abs(av[3] - dv[3]) > 0.05: close_off.append((d, av[3], dv[3]))
    n2025 = sum(1 for d in derived if d < "2026-01-01")
    out[sym] = {"bars_total": tot, "trading_days": len(bars),
                "bars_by_month": dict(sorted(months.items())),
                "days_not_75_bars": bad_days,
                "zero_volume_bars": zerovol,
                "zero_volume_pct": round(100.0 * zerovol / tot, 3) if tot else None,
                "self_consistency_bad_days": self_bad,
                "daily_api_common_days": common,
                "daily_api_field_exact": {"open": field_exact[0], "high": field_exact[1],
                                          "low": field_exact[2], "close": field_exact[3]},
                "daily_api_max_abs_diff": {"open": maxdiff[0], "high": maxdiff[1],
                                           "low": maxdiff[2], "close": maxdiff[3]},
                "daily_close_diff_gt_0.05": close_off,
                "daily_rows_2025": n2025,
                "daily_first": min(derived) if derived else None,
                "daily_last": max(derived) if derived else None}
    print(f"{sym}: bars={tot} days={len(bars)} bad75={len(bad_days)} zerovol%={out[sym]['zero_volume_pct']} "
          f"selfbad={len(self_bad)} api_common={common} close_exact={field_exact[3]} "
          f"close_maxdiff={maxdiff[3]} rows2025={n2025}", flush=True)

json.dump(out, open(os.path.join(TRADING, "universe_ext_verification.json"), "w"), indent=1)
print("WROTE universe_ext_verification.json")
