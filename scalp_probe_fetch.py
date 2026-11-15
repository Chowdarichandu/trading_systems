#!/usr/bin/env python3
"""Phase-0 backward probe: does genuine 1-min data exist for earlier months?
One mid-month day per month Jan-Sep 2026: index v3 1-min + ATM CE v2-expired
1minute. Plus a RANGE test (Oct 54400CE, 2026-10-19..27). Token never printed."""
import sys, json, csv, glob
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")
token = read_token()

# trading days + opens from 5-min spot union
spot = {}
for f in glob.glob(str(TR / "data/banknifty-2026-*/spot_5m.csv")):
    for r in csv.DictReader(open(f)):
        d = r["timestamp"][:10]
        if d not in spot: spot[d] = float(r["open"])
days = sorted(spot)
probes = []
for m in range(1, 10):
    md = [d for d in days if d[5:7] == f"{m:02d}"]
    if md: probes.append(md[len(md)//2])

def exp_for(day): return next(e for e in EXPIRIES if e >= day)

def atm_key(day, typ):
    exp = exp_for(day)
    p = TR / f"historical_proof_data/contracts_BANKNIFTY_{exp}.json"
    if not p.exists():
        # some expiries have near-date contract files; fall back to any file whose expiry == exp in name variants
        return None, exp, None
    atm = round(spot[day]/100)*100
    for c in json.loads(p.read_text())["data"]:
        if c.get("weekly") is False and float(c["strike_price"]) == atm and c["instrument_type"] == typ:
            return c["instrument_key"], exp, atm
    return None, exp, atm

jobs = {}  # tag -> url
for d in probes:
    jobs[f"IDX_{d}"] = f"https://api.upstox.com/v3/historical-candle/{quote('NSE_INDEX|Nifty Bank', safe='')}/minutes/1/{d}/{d}"
    k, exp, atm = atm_key(d, "CE")
    if k: jobs[f"CE_{d}_exp{exp}_atm{atm}"] = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(k, safe='')}/1minute/{d}/{d}"
    else: print("NO_KEY", d, exp, atm, flush=True)
# range test on Oct 54400CE
k, _, _ = atm_key("2026-10-27", "CE")
contracts = json.loads((TR / "historical_proof_data/contracts_BANKNIFTY_2026-10-27.json").read_text())["data"]
k544 = next(c["instrument_key"] for c in contracts if c.get("weekly") is False and float(c["strike_price"]) == 54400.0 and c["instrument_type"] == "CE")
jobs["RANGE_54400CE_to1027_from1019"] = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(k544, safe='')}/1minute/2026-10-27/2026-10-19"

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
    ctx = browser.new_context(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", **atr._local_proxy_kwargs())
    page = ctx.new_page()
    try: page.goto("https://api.upstox.com/", timeout=60000, wait_until="domcontentloaded")
    except Exception as e: print("origin:", str(e)[:120], flush=True)
    def fetch(url):
        return page.evaluate("""async ([url, tok]) => {
            try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                const t = await r.text(); return {status: r.status, body: t.slice(0,4000000)}; }
            catch(e){ return {status:0, body:String(e).slice(0,500)}; }
        }""", [url, token])
    r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"], flush=True)
    for tag, url in jobs.items():
        r = fetch(url)
        try:
            candles = json.loads(r["body"]).get("data", {}).get("candles", [])
            dates = sorted({c[0][:10] for c in candles})
            print(f"{tag}: status={r['status']} candles={len(candles)} days={dates[:3]}{'...' if len(dates)>3 else ''} n_days={len(dates)}", flush=True)
        except Exception as e:
            print(f"{tag}: status={r['status']} PARSE_ERR {str(e)[:80]} body[:120]={r['body'][:120]}", flush=True)
    browser.close()
print("PROBE DONE", flush=True)
