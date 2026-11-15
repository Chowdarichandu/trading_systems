#!/usr/bin/env python3
"""ROUND 3 data completion: fetch the expired BANKNIFTY contracts whose
5-min premium candles are missing for the NS3/NS5a/NS5b NOT_COMPUTED legs
(targets from bank_r3_census.json). Route: Upstox expired-instruments API,
browser User-Agent (the 2026-11-02 fix). Token from upstox_refresh/.env,
never printed. A 429 is a hard stop. Saves the caches' raw payload format
under historical_proof_data/."""
import json, sys, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

TR = Path.home() / "workspace/trading"
OUT = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

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
        if e.code == 429:
            raise SystemExit(f"HTTP 429 HARD STOP on {path}")
        raise SystemExit(f"HTTP {e.code} on {path}: {body}")

def main():
    if len(sys.argv) > 1:
        targets = [tuple(t) for t in json.loads(Path(sys.argv[1]).read_text())]
    else:
        census = json.loads((TR / "bank_r3_census.json").read_text())
        targets = [tuple(t) for t in census["fetch_targets"]]
    token = read_token()
    contracts = {}
    done, failed = [], []
    for date, typ, strike, expiry in targets:
        tag = f"BANKNIFTY_{strike}{typ}_{date}_{expiry}"
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
