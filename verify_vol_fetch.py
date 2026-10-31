"""Verify data/progressive_vol vs the Part 1 OHLC cache: coverage per
stock/month, zero-volume share, OHLC mismatch on all overlapping bars."""
import csv, json, os
from collections import defaultdict

VOL = "/home/hatch/workspace/trading/data/progressive_vol"
OHLC = "/home/hatch/workspace/trading/data/progressive"
SYMS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
        "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
        "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
        "ASTRAL","BDL","OIL","HINDUNILVR"]
LO, HI = "2026-01-01", "2026-10-28"

out = {}
for sym in SYMS:
    cache = {}
    with open(f"{OHLC}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            if LO <= r["timestamp"][:10] <= HI:
                cache[r["timestamp"][:16]] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    vol = {}
    with open(f"{VOL}/{sym}/spot_5m_vol.csv") as f:
        for r in csv.DictReader(f):
            if LO <= r["timestamp"][:10] <= HI:
                vol[r["timestamp"][:16]] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["volume"]))
    months = defaultdict(lambda: [0, 0])
    mism = 0; checked = 0; zero = 0
    for ts, v in vol.items():
        months[ts[5:7]][0] += 1
        if v[4] == 0: zero += 1; months[ts[5:7]][1] += 1
        c = cache.get(ts)
        if c is not None:
            checked += 1
            if any(abs(c[k] - v[k]) > 0.011 for k in range(4)): mism += 1
    missing_in_vol = sum(1 for ts in cache if ts not in vol)
    out[sym] = {"vol_bars": len(vol), "cache_bars": len(cache), "ohlc_checked": checked,
                "ohlc_mismatch_bars": mism, "cache_bars_missing_in_vol": missing_in_vol,
                "zero_vol_bars": zero, "zero_vol_pct": round(100 * zero / max(1, len(vol)), 2),
                "months": {m: {"bars": v[0], "zero": v[1]} for m, v in sorted(months.items())}}
    print(sym, json.dumps({k: out[sym][k] for k in list(out[sym])[:6]}), flush=True)
json.dump(out, open(f"{VOL}/verification.json", "w"), indent=1)
tot_mism = sum(v["ohlc_mismatch_bars"] for v in out.values())
tot_vol = sum(v["vol_bars"] for v in out.values())
tot_zero = sum(v["zero_vol_bars"] for v in out.values())
print("TOTAL vol bars", tot_vol, "mismatch", tot_mism, "zero-vol pct", round(100 * tot_zero / tot_vol, 2))
