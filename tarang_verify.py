#!/usr/bin/env python3
"""TARANG data verification — per-name coverage of the new volume store
and OHLC agreement against the frozen sarvaritu_fwd stores on
overlapping bars. Read-only. Prints a JSON summary to stdout and
writes tarang_verify_results.json."""
import json
import numpy as np
import pandas as pd

WS = "/home/hatch/workspace/trading"
NAMES = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK", "HINDALCO",
         "HINDCOPPER", "HINDUNILVR", "HINDZINC", "INDUSTOWER", "IRCTC",
         "ITC", "KALYANKJIL", "NATIONALUM", "NHPC", "NTPC", "OBEROIRLTY",
         "OIL", "PFC", "RECLTD", "TATASTEEL", "TVSMOTOR", "UNITDSPR",
         "VEDL", "WIPRO"]

out = {}
for sym in NAMES:
    new = pd.read_csv(f"{WS}/data/tarang_vol/{sym}/spot_5m_vol.csv")
    old = pd.read_csv(f"{WS}/data/sarvaritu_fwd/{sym}/spot_5m.csv")
    new["ts"] = new["timestamp"].str.slice(0, 19)
    old["ts"] = old["timestamp"].str.slice(0, 19)
    days = sorted(set(t[:10] for t in new["ts"]))
    vol = new["volume"]
    rec = {
        "bars": int(len(new)),
        "days": len(days),
        "first": days[0] if days else None,
        "last": days[-1] if days else None,
        "vol_missing": int(vol.isna().sum()),
        "vol_zero_bars": int((vol == 0).sum()),
        "vol_zero_share_pct": round(100.0 * float((vol == 0).mean()), 3),
        "vol_min_positive": float(vol[vol > 0].min()) if (vol > 0).any() else None,
        "bars_per_day_min": int(new.groupby(new["ts"].str.slice(0, 10)).size().min()),
        "bars_per_day_max": int(new.groupby(new["ts"].str.slice(0, 10)).size().max()),
    }
    m = new.merge(old, on="ts", suffixes=("_new", "_old"), how="inner")
    rec["overlap_bars"] = int(len(m))
    agree = {}
    for f in ["open", "high", "low", "close"]:
        d = (m[f"{f}_new"] - m[f"{f}_old"]).abs()
        agree[f] = {
            "exact_match_pct": round(100.0 * float((d < 1e-9).mean()), 4),
            "max_abs_diff": float(d.max()),
            "n_diff": int((d >= 1e-9).sum()),
        }
    rec["ohlc_agreement"] = agree
    out[sym] = rec
    print(f"{sym}: bars={rec['bars']} days={rec['days']} {rec['first']}..{rec['last']} "
          f"vol0={rec['vol_zero_bars']} overlap={rec['overlap_bars']} "
          f"close_exact={agree['close']['exact_match_pct']}% maxdiff={agree['close']['max_abs_diff']}",
          flush=True)

json.dump(out, open(f"{WS}/tarang_verify_results.json", "w"), indent=1)
print("VERIFY DONE")
