#!/usr/bin/env python3
"""Fetch missing October NS option candles via the existing browser-fetch script-token
route (pattern from premium_fetch_oct.py). Paper only, no orders. Token is read from
the script token store by this script only and is never printed or logged.
Fetches ONLY the 18 missing contracts listed in index_options_newsetup_oct_contracts.csv."""
import sys, json, csv
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
IDX = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}
MISSING = [
    ("BANKNIFTY", "2026-10-27", 54200, "PE", "2026-10-27"),
    ("BANKNIFTY", "2026-10-27", 54400, "PE", "2026-10-05"),
    ("BANKNIFTY", "2026-10-27", 54600, "CE", "2026-10-27"),
    ("BANKNIFTY", "2026-10-27", 55000, "CE", "2026-10-01"),
    ("BANKNIFTY", "2026-10-27", 55100, "PE", "2026-10-21"),
    ("BANKNIFTY", "2026-10-27", 55300, "CE", "2026-10-07"),
    ("BANKNIFTY", "2026-10-27", 55500, "PE", "2026-10-21"),
    ("BANKNIFTY", "2026-10-27", 55600, "PE", "2026-10-16"),
    ("NIFTY", "2026-10-27", 22200, "PE", "2026-10-01"),
    ("NIFTY", "2026-10-27", 22400, "PE", "2026-10-01"),
    ("NIFTY", "2026-10-27", 22400, "PE", "2026-10-05"),
    ("NIFTY", "2026-10-27", 22500, "PE", "2026-10-05"),
    ("NIFTY", "2026-10-27", 22600, "PE", "2026-10-14"),
    ("NIFTY", "2026-10-27", 22700, "CE", "2026-10-06"),
    ("NIFTY", "2026-10-27", 22700, "CE", "2026-10-07"),
    ("NIFTY", "2026-10-27", 22700, "PE", "2026-10-23"),
    ("NIFTY", "2026-10-27", 22900, "PE", "2026-10-16"),
    ("NIFTY", "2026-11-03", 22700, "CE", "2026-10-28"),
]

def read_token():
    for line in (Path.home() / "workspace/trading/upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def main():
    token = read_token()
    contracts = {}
    for idx_key, exp in [(IDX["NIFTY"], "2026-10-27"), (IDX["BANKNIFTY"], "2026-10-27")]:
        p = OUT / f"contracts_{idx_key.split('|')[1].replace(' ', '_')}_{exp}.json"
        for c in json.loads(p.read_text()).get("data") or []:
            contracts[(idx_key, exp, float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
    nov3 = {}
    for row in json.loads((OUT / "chain_Nifty_50_2026-11-03.json").read_text()).get("data") or []:
        nov3[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
        nov3[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
    jobs = []
    for (sym, exp, strike, typ, day) in MISSING:
        tag = f"{sym}_{strike}{typ}_{day}_{exp}"
        if (OUT / f"candles_premium_{tag}.json").exists():
            print("cached", tag); continue
        if exp == "2026-11-03":
            key = nov3.get((float(strike), typ)); kind = "v3"
        else:
            key = contracts.get((IDX[sym], exp, float(strike), typ)); kind = "expired"
        if not key:
            print("NO_KEY", sym, exp, strike, typ); continue
        jobs.append((tag, key, kind, day))
    print(f"to fetch: {len(jobs)}")
    if not jobs:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = browser.new_context(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", **atr._local_proxy_kwargs())
        page = ctx.new_page()
        try:
            page.goto("https://api.upstox.com/", timeout=60000, wait_until="domcontentloaded")
        except Exception as e:
            print("origin:", str(e)[:200])
        def fetch(url):
            return page.evaluate("""async ([url, tok]) => {
                try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                    const t = await r.text(); return {status: r.status, body: t.slice(0,500000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])
        r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"])
        for tag, key, kind, day in jobs:
            if kind == "expired":
                url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
            else:
                url = f"https://api.upstox.com/v3/historical-candle/{quote(key, safe='')}/minutes/5/{day}/{day}"
            r = fetch(url)
            try:
                n = len(json.loads(r["body"]).get("data", {}).get("candles", []))
            except Exception:
                n = -1
            print(tag, r["status"], "candles", n)
            if r["status"] == 200:
                (OUT / f"candles_premium_{tag}.json").write_text(r["body"])
        browser.close()
    print("done")

if __name__ == "__main__":
    main()
