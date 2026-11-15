#!/usr/bin/env python3
"""ROUND 3 WS3 (2026-11-02): retry the expired-instruments route for the
one remaining NOT_COMPUTED leg — 2026-10-28, 22500 PE, weekly expiry
2026-11-03, entry 10:20, solo Skill V3 (Cycle 24's named leg).
Token never printed. Paper only."""
import json, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote
import sys
sys.path.insert(0, str(Path.home() / "workspace/trading"))

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
        "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

WEXP, DAY, STRIKE, TYP = "2026-11-03", "2026-10-28", 22500, "PE"
IDX = quote("NSE_INDEX|Nifty 50", safe='')
outp = OUT / f"candles_NIFTY_{STRIKE}{TYP}_{DAY}_{WEXP}.json"
if outp.exists():
    print("ALREADY_HAVE", outp.name); sys.exit(0)

body = None
for attempt in range(3):
    try:
        body = get(f"https://api.upstox.com/v2/expired-instruments/option/contract?instrument_key={IDX}&expiry_date={WEXP}")
    except urllib.error.HTTPError as e:
        print(f"attempt {attempt + 1}: HTTP {e.code}"); time.sleep(1.0); continue
    data = body.get("data") or []
    print(f"attempt {attempt + 1}: contracts returned = {len(data)}")
    if data: break
    time.sleep(1.0)

data = (body or {}).get("data") or []
if not data:
    print("REGISTRY_EMPTY: expiry 2026-11-03 contract list still empty after retries")
    sys.exit(0)
(TR / "historical_proof_data" / f"contracts_NIFTY_{WEXP}.json").write_text(json.dumps(body))
hits = [c for c in data if float(c["strike_price"]) == float(STRIKE) and c["instrument_type"] == TYP]
weekly = [c for c in hits if c.get("weekly") is True]
pick = weekly[0] if weekly else (hits[0] if hits else None)
print(f"strike/type hits: {len(hits)}, weekly-flagged: {len(weekly)}")
if not pick:
    print("NO_CONTRACT for 22500 PE in the 2026-11-03 list"); sys.exit(0)
key = pick["instrument_key"]
url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
       f"{quote(key, safe='')}/5minute/{DAY}/{DAY}")
try:
    cbody = get(url)
except urllib.error.HTTPError as e:
    print(f"candle fetch HTTP {e.code}"); sys.exit(0)
rows = [c for c in ((cbody.get("data") or {}).get("candles") or []) if c[0][:10] == DAY]
print(f"candle rows for {DAY}: {len(rows)}")
if not rows:
    print("EMPTY candles"); sys.exit(0)
outp.write_text(json.dumps(cbody))
has_entry = any(c[0][11:16] == "10:20" for c in rows)
print(f"saved {outp.name}; entry bar 10:20 present: {has_entry}")
