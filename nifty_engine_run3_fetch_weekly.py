#!/usr/bin/env python3
"""RUN 3 fetch #4 (2026-11-02): the 44 weekly-expiry candle files that
fetch #3 missed (its have-check was fooled by aggressive_score's glob
fallback returning the MONTHLY file). This script checks EXACT cache-file
existence, fetches via the expired option/contract + historical-candle
routes, and sanity-checks that each saved weekly file's content differs
from the same leg's monthly file. Token never printed. Paper only."""
import json, time, hashlib
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote
import sys
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
DIRS = [TR / "aggressive_data", TR / "v4_options_oct_data", TR / "historical_proof_data"]
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

def exact_file(strike, typ, day, exp):
    tag = f"NIFTY_{int(strike)}{typ}_{day}_{exp}"
    for d in DIRS:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists(): return p
    return None

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]
wmap = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]
IDX = quote("NSE_INDEX|Nifty 50", safe='')

contracts_cache = {}
def weekly_key(wexp, strike, typ):
    if wexp not in contracts_cache:
        p = HP / f"contracts_NIFTY_{wexp}.json"
        if p.exists():
            data = json.loads(p.read_text()).get("data") or []
        else:
            body = get(f"https://api.upstox.com/v2/expired-instruments/option/contract?instrument_key={IDX}&expiry_date={wexp}")
            data = body.get("data") or []
            p.write_text(json.dumps(body))
            time.sleep(0.35)
        contracts_cache[wexp] = data
    hits = [c for c in contracts_cache[wexp] if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    weekly = [c for c in hits if c.get("weekly") is True]
    pick = weekly[0] if weekly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

report = []
for l in EXP0:
    day, typ, strike = l["date"], l["direction"], l["strike"]
    wexp = wmap[f"{day}|{typ}"]
    if exact_file(strike, typ, day, wexp):
        report.append(dict(date=day, dir=typ, wexp=wexp, status="ALREADY_HAVE")); continue
    key = weekly_key(wexp, strike, typ)
    if not key:
        report.append(dict(date=day, dir=typ, wexp=wexp, status="NO_KEY"))
        print("NO_KEY", day, typ, strike, wexp, flush=True); continue
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    try:
        body = get(url)
    except urllib.error.HTTPError as e:
        report.append(dict(date=day, dir=typ, wexp=wexp, status=f"HTTP {e.code}"))
        print("HTTP", e.code, day, typ, strike, wexp, flush=True); continue
    rows = [c for c in ((body.get("data") or {}).get("candles") or []) if c[0][:10] == day]
    if not rows:
        report.append(dict(date=day, dir=typ, wexp=wexp, status="EMPTY"))
        print("EMPTY", day, typ, strike, wexp, flush=True); continue
    outp = OUT / f"candles_NIFTY_{strike}{typ}_{day}_{wexp}.json"
    outp.write_text(json.dumps(body))
    mp = exact_file(strike, typ, day, l["expiry"])
    same = None
    if mp:
        same = hashlib.md5(mp.read_bytes()).hexdigest() == hashlib.md5(outp.read_bytes()).hexdigest()
    cs = A.candles("NIFTY", strike, typ, day, wexp)
    eb = bool(cs) and any(b[0] == l["entry_time"] for b in cs)
    report.append(dict(date=day, dir=typ, wexp=wexp, status="OK", rows=len(rows),
                       entry_bar=eb, identical_to_monthly=same))
    print("OK", day, typ, strike, wexp, len(rows), "entry_bar:", eb, "identical_to_monthly:", same, flush=True)
    time.sleep(0.35)

Path(TR / "nifty_engine_run3_fetch_weekly_report.json").write_text(json.dumps(report, indent=1))
from collections import Counter
print(Counter(r["status"] for r in report))
print("identical_to_monthly True count:", sum(1 for r in report if r.get("identical_to_monthly")))
