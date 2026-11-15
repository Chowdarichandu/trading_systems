#!/usr/bin/env python3
"""ROUND 5 fetch: contracts absent from the local store, needed by the
WS0 causal re-timing (4) — same expired-instruments route as Rounds 3–4
(browser UA, token from upstox_refresh/.env, never printed). Saves into
aggressive_data/ in the exact-tag format candles_exact reads. Jobs are
appended by later workstreams as needed. Paper only."""
import json, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token, "no token"

def contract_key(expiry, strike, typ, weekly=False):
    p = HP / f"contracts_NIFTY_{expiry}.json"
    if not p.exists(): return None
    data = json.loads(p.read_text()).get("data") or []
    hits = [c for c in data if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    sel = [c for c in hits if c.get("weekly") is weekly]
    pick = sel[0] if sel else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

def fetch_one(strike, typ, day, exp, weekly=False):
    key = contract_key(exp, strike, typ, weekly=weekly)
    if not key: return ("NO_KEY", None)
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}", None)
    candles = (body.get("data") or {}).get("candles") or []
    rows = [c for c in candles if c[0][:10] == day]
    if not rows: return ("EMPTY", 0)
    tag = f"NIFTY_{int(strike)}{typ}_{day}_{exp}"
    (OUT / f"candles_{tag}.json").write_text(json.dumps(body))
    return ("OK", len(rows))

if __name__ == "__main__":
    JOBS = [  # WS0 causal re-timed legs: (strike, type, day, monthly expiry)
        (24900, "CE", "2026-02-02", "2026-02-24"),
        (25000, "CE", "2026-03-02", "2026-03-30"),
        (24100, "CE", "2026-04-27", "2026-04-28"),
        (24100, "CE", "2026-07-09", "2026-07-28"),
    ]
    for j in JOBS:
        print(j, fetch_one(*j))
