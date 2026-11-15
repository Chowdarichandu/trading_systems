#!/usr/bin/env python3
"""RUN 3 fetch #2 (2026-11-02): premium candles for the 21 BASE_S1 NIFTY legs
(outside the N1 premium pool) whose candles are absent locally.
Same expired-instruments route as nifty_engine_run3_fetch.py. Token never
printed. Paper only."""
import csv, json, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote
import sys
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
EXP = A.EXPIRIES

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token

def expf(d): return next(e for e in EXP if e >= d)

def contract_key(expiry, strike, typ):
    p = HP / f"contracts_NIFTY_{expiry}.json"
    if not p.exists(): return None
    data = json.loads(p.read_text()).get("data") or []
    hits = [c for c in data if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    monthly = [c for c in hits if c.get("weekly") is False]
    pick = monthly[0] if monthly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

n1keys = {(r["date"], r["direction"]) for r in csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv"))}
s1 = [r for r in csv.DictReader(open(TR / "index_options_newsetup_base_s1_trades_jan_oct_2026.csv"))
      if r["index"] == "NIFTY" and (r["date"], r["direction"]) not in n1keys]

report = []
for r in s1:
    day, typ = r["date"], r["direction"]
    strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
    exp = expf(day)
    if A.candles("NIFTY", strike, typ, day, exp):
        report.append(dict(date=day, dir=typ, strike=strike, expiry=exp, status="ALREADY_HAVE"))
        continue
    key = contract_key(exp, strike, typ)
    if not key:
        report.append(dict(date=day, dir=typ, strike=strike, expiry=exp, status="NO_KEY"))
        print("NO_KEY", day, typ, strike, exp, flush=True); continue
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        report.append(dict(date=day, dir=typ, strike=strike, expiry=exp, status=f"HTTP {e.code}"))
        print("HTTP", e.code, day, typ, strike, exp, flush=True); continue
    rows = [c for c in ((body.get("data") or {}).get("candles") or []) if c[0][:10] == day]
    if not rows:
        report.append(dict(date=day, dir=typ, strike=strike, expiry=exp, status="EMPTY"))
        print("EMPTY", day, typ, strike, exp, flush=True); continue
    (OUT / f"candles_NIFTY_{strike}{typ}_{day}_{exp}.json").write_text(json.dumps(body))
    A._cache.clear()
    cs = A.candles("NIFTY", strike, typ, day, exp)
    eb = bool(cs) and any(b[0] == r["entry_time"] for b in cs)
    report.append(dict(date=day, dir=typ, strike=strike, expiry=exp, status="OK",
                       rows=len(rows), entry_bar=eb))
    print("OK", day, typ, strike, exp, len(rows), "entry_bar:", eb, flush=True)
    time.sleep(0.4)

Path(TR / "nifty_engine_run3_fetch_s1_report.json").write_text(json.dumps(report, indent=1))
from collections import Counter
print(Counter(r["status"] for r in report))
