#!/usr/bin/env python3
"""RUN 3 fetch #3 (2026-11-02): (Cycle 19) ITM +/-100 strike candles for the
59 incumbent legs (same monthly expiry); (Cycle 20) weekly-expiry-in-force
contracts + candles for the same 59 legs. Expired-instruments route.
Token never printed. Paper only."""
import csv, json, time
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

def fetch_candles(key, day):
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    body = get(url)
    rows = [c for c in ((body.get("data") or {}).get("candles") or []) if c[0][:10] == day]
    return body, rows

def monthly_key(expiry, strike, typ):
    p = HP / f"contracts_NIFTY_{expiry}.json"
    if not p.exists(): return None
    data = json.loads(p.read_text()).get("data") or []
    hits = [c for c in data if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    monthly = [c for c in hits if c.get("weekly") is False]
    pick = monthly[0] if monthly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]
assert len(EXP0) == 59

report = {"itm": [], "weekly": [], "weekly_map": {}}

# ---------- Cycle 19: ITM100 ----------
for l in EXP0:
    sh = l["strike"] - 100 if l["direction"] == "CE" else l["strike"] + 100
    day, typ, exp = l["date"], l["direction"], l["expiry"]
    if A.candles("NIFTY", sh, typ, day, exp):
        report["itm"].append(dict(date=day, dir=typ, strike=sh, status="ALREADY_HAVE")); continue
    key = monthly_key(exp, sh, typ)
    if not key:
        report["itm"].append(dict(date=day, dir=typ, strike=sh, status="NO_KEY"))
        print("ITM NO_KEY", day, typ, sh, exp, flush=True); continue
    try:
        body, rows = fetch_candles(key, day)
    except urllib.error.HTTPError as e:
        report["itm"].append(dict(date=day, dir=typ, strike=sh, status=f"HTTP {e.code}"))
        print("ITM HTTP", e.code, day, typ, sh, flush=True); continue
    if not rows:
        report["itm"].append(dict(date=day, dir=typ, strike=sh, status="EMPTY"))
        print("ITM EMPTY", day, typ, sh, flush=True); continue
    (OUT / f"candles_NIFTY_{sh}{typ}_{day}_{exp}.json").write_text(json.dumps(body))
    A._cache.clear()
    cs = A.candles("NIFTY", sh, typ, day, exp)
    eb = bool(cs) and any(b[0] == l["entry_time"] for b in cs)
    report["itm"].append(dict(date=day, dir=typ, strike=sh, status="OK", rows=len(rows), entry_bar=eb))
    print("ITM OK", day, typ, sh, exp, len(rows), "entry_bar:", eb, flush=True)
    time.sleep(0.35)

# ---------- Cycle 20: weekly expiry in force ----------
IDX = quote("NSE_INDEX|Nifty 50", safe='')
expiries = get(f"https://api.upstox.com/v2/expired-instruments/expiries?instrument_key={IDX}").get("data") or []
expiries = sorted(str(d) for d in expiries)
Path(TR / "nifty_engine_run3_expiries.json").write_text(json.dumps(expiries))

def weekly_in_force(day):
    after = [e for e in expiries if e > day]
    return after[0] if after else None

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
        contracts_cache[wexp] = data
        time.sleep(0.35)
    hits = [c for c in contracts_cache[wexp] if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    weekly = [c for c in hits if c.get("weekly") is True]
    pick = weekly[0] if weekly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

for l in EXP0:
    day, typ = l["date"], l["direction"]
    wexp = weekly_in_force(day)
    strike = l["strike"]
    report["weekly_map"][f"{day}|{typ}"] = wexp
    if wexp is None:
        report["weekly"].append(dict(date=day, dir=typ, status="NO_WEEKLY_EXPIRY")); continue
    if A.candles("NIFTY", strike, typ, day, wexp):
        report["weekly"].append(dict(date=day, dir=typ, strike=strike, wexp=wexp, status="ALREADY_HAVE")); continue
    key = weekly_key(wexp, strike, typ)
    if not key:
        report["weekly"].append(dict(date=day, dir=typ, strike=strike, wexp=wexp, status="NO_KEY"))
        print("WK NO_KEY", day, typ, strike, wexp, flush=True); continue
    try:
        body, rows = fetch_candles(key, day)
    except urllib.error.HTTPError as e:
        report["weekly"].append(dict(date=day, dir=typ, strike=strike, wexp=wexp, status=f"HTTP {e.code}"))
        print("WK HTTP", e.code, day, typ, strike, wexp, flush=True); continue
    if not rows:
        report["weekly"].append(dict(date=day, dir=typ, strike=strike, wexp=wexp, status="EMPTY"))
        print("WK EMPTY", day, typ, strike, wexp, flush=True); continue
    (OUT / f"candles_NIFTY_{strike}{typ}_{day}_{wexp}.json").write_text(json.dumps(body))
    A._cache.clear()
    cs = A.candles("NIFTY", strike, typ, day, wexp)
    eb = bool(cs) and any(b[0] == l["entry_time"] for b in cs)
    report["weekly"].append(dict(date=day, dir=typ, strike=strike, wexp=wexp, status="OK",
                                 rows=len(rows), entry_bar=eb))
    print("WK OK", day, typ, strike, wexp, len(rows), "entry_bar:", eb, flush=True)
    time.sleep(0.35)

Path(TR / "nifty_engine_run3_fetch_c19c20_report.json").write_text(json.dumps(report, indent=1))
from collections import Counter
print("ITM:", Counter(r["status"] for r in report["itm"]))
print("WEEKLY:", Counter(r["status"] for r in report["weekly"]))
