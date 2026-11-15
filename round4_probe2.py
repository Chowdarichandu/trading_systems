#!/usr/bin/env python3
"""ROUND 4 PROBE 2 — November coverage routes (live futures + index spot)."""
import json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()

def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read()), 200
    except urllib.error.HTTPError as e:
        return None, e.code

KEYS = json.loads((TR / "round2_history/futures_keys.json").read_text())
fkey = quote(KEYS["2026-11-23"]["key"], safe="")
for day in ("2026-11-02", "2026-11-11", "2026-11-12", "2026-11-13"):
    body, code = get(f"{API}/v3/historical-candle/{fkey}/minutes/5/{day}/{day}")
    if code == 429:
        print("RATE_LIMIT_STOP"); sys.exit(2)
    cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []
          if c[0][:10] == day]
    print(f"FUT live Nov23 {day}: HTTP {code} candles={len(cd)}"
          + (f" first={cd[-1][0]} last={cd[0][0]}" if cd else ""))
    time.sleep(0.4)

ikey = quote("NSE_INDEX|Nifty Bank", safe="")
for day in ("2026-11-12", "2026-11-13"):
    body, code = get(f"{API}/v3/historical-candle/{ikey}/minutes/5/{day}/{day}")
    if code == 429:
        print("RATE_LIMIT_STOP"); sys.exit(2)
    cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []
          if c[0][:10] == day]
    print(f"SPOT index {day}: HTTP {code} candles={len(cd)}"
          + (f" first={cd[-1][0]} last={cd[0][0]}" if cd else ""))
    time.sleep(0.4)
print("PROBE2 DONE")
