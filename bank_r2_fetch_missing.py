#!/usr/bin/env python3
"""ROUND 2 data completion: fetch the 15 expired BANKNIFTY contracts whose
5-min premium candles are missing from the caches (1 room-1.3/1.4 NS1 second
leg, 1 window-15:00 NS1 second leg, 13 distinct ITM-strike NS1 second legs
[14 legs, one contract shared]). Route: Upstox expired-instruments API,
direct request with the browser User-Agent (the 2026-11-02 fix). Token read
from upstox_refresh/.env, never printed. A 429 is a hard stop (no retry).
Files saved in the caches' raw payload format under historical_proof_data/."""
import json, sys, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

TR = Path.home() / "workspace/trading"
OUT = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
TARGETS = [  # (date, direction, strike, expiry)
    ("2026-01-07", "PE", 59900, "2026-01-27"),
    ("2026-09-03", "PE", 57500, "2026-09-29"),
    ("2026-01-20", "PE", 59900, "2026-01-27"),
    ("2026-01-22", "PE", 59200, "2026-01-27"),
    ("2026-01-23", "PE", 59200, "2026-01-27"),
    ("2026-02-03", "PE", 60100, "2026-02-24"),
    ("2026-02-05", "PE", 60200, "2026-02-24"),
    ("2026-03-05", "PE", 58900, "2026-03-30"),
    ("2026-03-24", "PE", 52200, "2026-03-30"),
    ("2026-04-09", "PE", 55300, "2026-04-28"),
    ("2026-04-15", "PE", 56400, "2026-04-28"),
    ("2026-06-01", "PE", 54200, "2026-06-30"),
    ("2026-07-02", "PE", 58200, "2026-07-28"),
    ("2026-07-22", "PE", 57400, "2026-07-28"),
    ("2026-07-28", "PE", 57000, "2026-07-28"),
    ("2026-09-01", "PE", 57400, "2026-09-29"),
]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token in .env")

def get(token, path):
    req = Request("https://api.upstox.com" + path, headers={
        "Accept": "application/json", "Authorization": f"Bearer {token}",
        "User-Agent": UA})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode(errors="ignore")[:300]
        raise SystemExit(f"HTTP {e.code} on {path.split('/')[2]}: {body}")

def main():
    token = read_token()
    contracts = {}
    done, failed = [], []
    seen = set()
    for date, typ, strike, expiry in TARGETS:
        tag = f"BANKNIFTY_{strike}{typ}_{date}_{expiry}"
        if tag in seen: continue
        seen.add(tag)
        out = OUT / f"candles_{tag}.json"
        if out.exists():
            done.append((tag, "already cached")); continue
        if expiry not in contracts:
            contracts[expiry] = json.loads((OUT / f"contracts_BANKNIFTY_{expiry}.json").read_text())
        rows = contracts[expiry]
        if isinstance(rows, dict): rows = rows.get("data") or []
        match = [c for c in rows if c.get("instrument_type") == typ
                 and f" {strike} {typ} " in (c.get("trading_symbol") or "")]
        if len(match) != 1:
            failed.append((tag, f"contract match count {len(match)}")); continue
        key = quote(match[0]["instrument_key"], safe="")
        payload = get(token, f"/v2/expired-instruments/historical-candle/{key}/5minute/{date}/{date}")
        n = len((payload.get("data") or {}).get("candles") or [])
        if n == 0:
            failed.append((tag, "empty candle payload")); continue
        out.write_text(json.dumps(payload))
        done.append((tag, f"{n} candles"))
        time.sleep(0.4)
    for t, s in done: print("OK  ", t, s)
    for t, s in failed: print("FAIL", t, s)
    print(f"fetched/cached {len(done)} | failed {len(failed)}")

if __name__ == "__main__":
    main()
