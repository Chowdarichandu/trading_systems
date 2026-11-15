#!/usr/bin/env python3
"""ROUND 4 PROBE (2026-11-13 night) — data feasibility only, no scoring.
1) Bank Nifty near-month FUTURES 5-minute candles via the expired-
   instruments route: single-day and multi-day range requests.
2) Stored spot coverage: bar counts/times for gate days + November.
Never prints the token. On HTTP 429: hard stop, reported.
"""
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
assert token

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
print("futures keys available:", {k: v["route"] for k, v in KEYS.items()})

# --- probe 1: single day, expired contract 2026-10-27, day 2026-10-01
key = KEYS["2026-10-27"]["key"]
enc = quote(key, safe="")
url = f"{API}/v2/expired-instruments/historical-candle/{enc}/5minute/2026-10-01/2026-10-01"
body, code = get(url)
if code == 429:
    print("RATE_LIMIT_STOP on probe 1"); sys.exit(2)
cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []]
print(f"probe1 single-day 2026-10-01: HTTP {code}, candles={len(cd)}")
if cd:
    print("  first:", cd[0][0], cd[0][1:5], " last:", cd[-1][0], cd[-1][1:5])
time.sleep(0.4)

# --- probe 2: multi-day range (one week) same contract
url = f"{API}/v2/expired-instruments/historical-candle/{enc}/5minute/2026-10-05/2026-10-01"
body, code = get(url)
if code == 429:
    print("RATE_LIMIT_STOP on probe 2"); sys.exit(2)
cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []]
days = sorted({c[0][:10] for c in cd})
print(f"probe2 range 2026-10-01..05: HTTP {code}, candles={len(cd)}, days={days}")
time.sleep(0.4)

# --- probe 3: one-month range
url = f"{API}/v2/expired-instruments/historical-candle/{enc}/5minute/2026-10-27/2026-10-01"
body, code = get(url)
if code == 429:
    print("RATE_LIMIT_STOP on probe 3"); sys.exit(2)
cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []]
days = sorted({c[0][:10] for c in cd})
print(f"probe3 range Oct 2026: HTTP {code}, candles={len(cd)}, n_days={len(days)}")
if days:
    print("  first day:", days[0], " last day:", days[-1])
time.sleep(0.4)

# --- probe 4: live contract (2026-11-23) via v3 minutes route, Nov 13
key = KEYS["2026-11-23"]["key"]
enc = quote(key, safe="")
url = f"{API}/v3/historical-candle/{enc}/minutes/5/2026-11-13/2026-11-13"
body, code = get(url)
if code == 429:
    print("RATE_LIMIT_STOP on probe 4"); sys.exit(2)
cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []]
print(f"probe4 live-contract Nov 13: HTTP {code}, candles={len(cd)}")
if cd:
    print("  first:", cd[0][0], " last:", cd[-1][0])

# --- spot coverage
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
nov = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
bk = spot_raw["BANKNIFTY"]
gate = [d for d in sorted(bk) if "2026-01-01" <= d <= "2026-10-31"]
print(f"\nspot BANKNIFTY gate days: {len(gate)}")
bad = []
for d in gate:
    bars = bk[d]
    times = [b[0] for b in bars]
    if len(bars) < 70 or times[0] != "09:15" or "10:55" not in times or "11:00" not in times:
        bad.append((d, len(bars), times[0] if times else None, times[-1] if times else None))
print(f"spot days lacking full morning window: {len(bad)} {bad[:8]}")
print("nov spot days:", sorted(nov.get("BANKNIFTY", {}).keys()))
for d in sorted(nov.get("BANKNIFTY", {})):
    bars = nov["BANKNIFTY"][d]
    print(f"  {d}: {len(bars)} bars, {bars[0][0]}..{bars[-1][0]}")
print("PROBE DONE")
