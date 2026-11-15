#!/usr/bin/env python3
"""OI HISTORY — November spot patch (2026-11-13).
The v3 range fetch for November spot returned the Diwali Muhurat
session (Sun 2026-11-08, 14 bars) and dropped 2026-11-12 entirely.
Fix spot_nov_bars.json: drop Nov 8 (non-full day; the workspace day
convention is >=74 bars) and fetch Nov 12 per index via the
completed-day single-day v3 route (the live producer's fetch_day_bars
route). Then the OI build can be re-run on cached contracts."""
import json, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OI = TR / "oi_history"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
IDXKEY = {"BANKNIFTY": "NSE_INDEX|Nifty Bank", "NIFTY": "NSE_INDEX|Nifty 50"}
token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()

def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

nov = json.loads((OI / "spot_nov_bars.json").read_text())
for idx in nov:
    dropped = nov[idx].pop("2026-11-08", None)
    print(f"{idx}: dropped 2026-11-08 ({len(dropped) if dropped else 0} bars)")
    if "2026-11-12" not in nov[idx]:
        key = quote(IDXKEY[idx], safe='')
        body = get(f"https://api.upstox.com/v3/historical-candle/{key}"
                   f"/minutes/5/2026-11-12/2026-11-12")
        bars = [[c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
                 float(c[4])] for c in
                ((body.get("data") or {}).get("candles") or [])
                if c[0][:10] == "2026-11-12"]
        bars.sort()
        nov[idx]["2026-11-12"] = bars
        print(f"{idx}: fetched 2026-11-12 -> {len(bars)} bars, "
              f"close {bars[-1][4] if bars else None}")
(OI / "spot_nov_bars.json").write_text(json.dumps(nov))
print("spot_nov_bars.json patched:",
      {i: sorted(v) for i, v in nov.items()})
