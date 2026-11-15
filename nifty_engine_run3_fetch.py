#!/usr/bin/env python3
"""RUN 3 fetch (2026-11-02): premium candles for the legs previous sessions
could not score — (a) the 5 dropped solo non-Skill U1 legs, (b) BASE_S1
NIFTY legs whose (date,direction) key is not in the U1 pool and whose
candles are absent locally. Route: expired-instruments historical-candle
(the route the NSE index work uses successfully). Token read from the
script .env, never printed. Saves into aggressive_data/ in the cache
format aggressive_score.candles() reads. Paper only."""
import csv, json, time
import urllib.request
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28", "2026-05-26",
            "2026-06-30", "2026-07-28", "2026-08-25", "2026-09-29", "2026-10-27"]

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token, "no token"

def exp_in_force(day):
    return next(e for e in EXPIRIES if e >= day)

def contract_key(expiry, strike, typ):
    p = HP / f"contracts_NIFTY_{expiry}.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text()).get("data") or []
    hits = [c for c in data if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    monthly = [c for c in hits if c.get("weekly") is False]
    pick = monthly[0] if monthly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

def have_candles(strike, typ, day, exp):
    import aggressive_score as A
    return A.candles("NIFTY", strike, typ, day, exp) is not None

def fetch_one(strike, typ, day, exp):
    key = contract_key(exp, strike, typ)
    if not key:
        return ("NO_KEY", None)
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
    if not rows:
        return ("EMPTY", 0)
    tag = f"NIFTY_{int(strike)}{typ}_{day}_{exp}"
    (OUT / f"candles_{tag}.json").write_text(json.dumps(body))
    return ("OK", len(rows))

jobs = []  # (label, date, direction, strike, expiry, entry_time)

# (a) the 5 dropped solo non-Skill U1 legs (verified against the U1 file)
EV5 = [("EV5", "2026-01-09", "CE", 25900, "2026-01-27", "09:20"),
       ("EV5", "2026-05-12", "CE", 23700, "2026-05-26", "09:20"),
       ("EV5", "2026-06-01", "CE", 23600, "2026-06-30", "09:20"),
       ("EV5", "2026-09-16", "CE", 23200, "2026-09-29", "09:20"),
       ("EV5", "2026-08-10", "PE", 24500, "2026-08-25", "09:45")]
jobs += EV5

# (b) BASE_S1 NIFTY legs not in the U1 pool
u1 = [r for r in csv.DictReader(open(TR / "index_options_U1_janoct_trades.csv"))
      if r["index"] == "NIFTY"]
u1keys = {(r["date"], r["direction"]) for r in u1}
s1 = [r for r in csv.DictReader(open(TR / "index_options_newsetup_base_s1_trades_jan_oct_2026.csv"))
      if r["index"] == "NIFTY" and (r["date"], r["direction"]) not in u1keys]
print("S1 non-U1 NIFTY legs:", len(s1))
for r in s1:
    strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
    jobs.append(("S1", r["date"], r["direction"], strike,
                 exp_in_force(r["date"]), r["entry_time"]))

report = []
for label, day, typ, strike, exp, et in jobs:
    if have_candles(strike, typ, day, exp):
        report.append(dict(label=label, date=day, dir=typ, strike=strike,
                           expiry=exp, status="ALREADY_HAVE"))
        continue
    status, n = fetch_one(strike, typ, day, exp)
    ok_bars = None
    if status == "OK":
        import aggressive_score as A
        A._cache.clear()
        cs = A.candles("NIFTY", strike, typ, day, exp)
        ok_bars = bool(cs) and any(b[0] == et for b in cs)
    report.append(dict(label=label, date=day, dir=typ, strike=strike,
                       expiry=exp, status=status, rows=n, entry_bar=ok_bars))
    print(label, day, typ, strike, exp, status, n, "entry_bar:", ok_bars, flush=True)
    time.sleep(0.4)

Path(TR / "nifty_engine_run3_fetch_report.json").write_text(json.dumps(report, indent=1))
from collections import Counter
print(Counter((r["label"], r["status"]) for r in report))
