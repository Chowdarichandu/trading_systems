#!/usr/bin/env python3
"""ROUND 5 — futures full-field refetch for FLOW-VOL (2026-11-14).
Round 4's stored FUT5 series kept OHLC only; this refetches every
in-force Bank Nifty near-month futures contract's 5-minute candles
with ALL 7 fields (volume + OI included), span [expiry-45d, expiry]
in <=14-day chunks, expired route (2026-11-23 via v3, as the frozen
scorers branch). Stores round5_history/FUT7_<exp>.json sorted rows
[date, time, o, h, l, c, vol, oi]; resume-safe .done markers.
On HTTP 429: hard stop, exit 2. Never prints the token.
"""
import json, sys, time
import urllib.request, urllib.error
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_history"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token

KEYS = json.loads((TR / "round2_history/futures_keys.json").read_text())
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
            "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
            "2026-09-29", "2026-10-27", "2026-11-23"]


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("RATE_LIMITED — HARD STOP", flush=True)
            sys.exit(2)
        return None


for exp in EXPIRIES:
    fn = OUT / f"FUT7_{exp}.json"
    if (OUT / f"FUT7_{exp}.done").exists():
        print(f"{exp}: cached", flush=True)
        continue
    key = KEYS[exp]["key"]
    enc = quote(key, safe="")
    end = date.fromisoformat(exp)
    start = end - timedelta(days=45)
    seen = {}
    d = start
    while d <= end:
        to = min(d + timedelta(days=13), end)
        if exp < "2026-11-13":
            url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
                   f"/5minute/{to.isoformat()}/{d.isoformat()}")
        else:
            url = (f"{API}/v3/historical-candle/{enc}"
                   f"/minutes/5/{to.isoformat()}/{d.isoformat()}")
        body = get(url)
        for c in ((body or {}).get("data") or {}).get("candles") or []:
            seen[(c[0][:10], c[0][11:16])] = (
                c[0][:10], c[0][11:16], float(c[1]), float(c[2]),
                float(c[3]), float(c[4]),
                float(c[5]) if len(c) > 5 else None,
                float(c[6]) if len(c) > 6 else None)
        time.sleep(0.3)
        d = to + timedelta(days=1)
    rows = sorted(seen.values())
    fn.write_text(json.dumps(rows))
    (OUT / f"FUT7_{exp}.done").write_text("ok")
    days = len({r[0] for r in rows})
    print(f"{exp}: {len(rows)} rows, {days} days", flush=True)
print("futures build complete", flush=True)
