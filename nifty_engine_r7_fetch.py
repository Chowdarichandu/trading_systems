#!/usr/bin/env python3
"""ROUND 7 fetch: contracts absent from the local store, needed by the new
signal families — same expired-instruments route as Rounds 3–6 (browser
UA, token read inside nifty_engine_r5_fetch, never printed). If a
contracts file for an expiry is absent, it is first built via the
option/contract discovery endpoint (the run3_fetch_weekly pattern), then
the candle fetch proceeds. Paper only."""
import sys, json, time
import urllib.request
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r5_fetch as F5

TR = Path.home() / "workspace/trading"
HP = TR / "historical_proof_data"
IDX = quote("NSE_INDEX|Nifty 50", safe='')

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {F5.token}",
        "Accept": "application/json", "User-Agent": F5.UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def ensure_contracts(expiry):
    p = HP / f"contracts_NIFTY_{expiry}.json"
    if p.exists(): return True
    try:
        body = get(f"https://api.upstox.com/v2/expired-instruments/option/contract"
                   f"?instrument_key={IDX}&expiry_date={expiry}")
    except Exception as e:
        print(f"discovery {expiry}: FAILED {type(e).__name__}")
        return False
    data = body.get("data") or []
    if not data:
        print(f"discovery {expiry}: EMPTY")
        return False
    p.write_text(json.dumps(body))
    print(f"discovery {expiry}: built contracts file ({len(data)} contracts)")
    time.sleep(0.35)
    return True

def expiries_list():
    body = get(f"https://api.upstox.com/v2/expired-instruments/expiries?instrument_key={IDX}")
    return body.get("data") or []

def fetch_jobs(jobs):
    """jobs: list of (strike, typ, day, expiry, weekly). Returns results."""
    out = []
    for strike, typ, day, exp, wk in jobs:
        if not ensure_contracts(exp):
            out.append(((strike, typ, day, exp, wk), ("NO_CONTRACTS_FILE", None))); continue
        out.append(((strike, typ, day, exp, wk), F5.fetch_one(strike, typ, day, exp, weekly=wk)))
        time.sleep(0.2)
    return out

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "expiries":
        exps = expiries_list()
        print(len(exps), "expiries")
        print(json.dumps(exps))
