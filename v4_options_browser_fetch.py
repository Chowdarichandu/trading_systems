#!/usr/bin/env python3
"""V4 options browser-fetch (2026-10-30 task). Token from .env, never printed.
Uses Playwright + localhost CONNECT forwarder from auto_token_refresh.py.
Writes raw JSON under ~/workspace/trading/v4_options_oct_data/ (persistent)."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

def read_token():
    for line in (Path.home() / "workspace/trading/upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=",1)[1].strip()
    raise SystemExit("no token")

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
OUT.mkdir(exist_ok=True)

def main():
    token = read_token()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        ctx = browser.new_context(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", **atr._local_proxy_kwargs())
        page = ctx.new_page()
        try: page.goto("https://api.upstox.com/", timeout=60000, wait_until="domcontentloaded")
        except Exception as e: print("origin:", str(e)[:200])
        def fetch(url):
            return page.evaluate("""async ([url, tok]) => {
                try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                    const t = await r.text(); return {status: r.status, body: t.slice(0,500000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])
        r = fetch("https://api.upstox.com/v2/user/profile")
        print("profile", r["status"])
        contracts = {}
        for idx, exp in [("NSE_INDEX|Nifty Bank","2026-10-27"), ("NSE_INDEX|Nifty 50","2026-10-27")]:
            url = f"https://api.upstox.com/v2/expired-instruments/option/contract?instrument_key={quote(idx, safe='')}&expiry_date={exp}"
            r = fetch(url)
            print(f"contracts {idx} {exp}", r["status"])
            (OUT / f"contracts_{idx.split('|')[1].replace(' ','_')}_{exp}.json").write_text(r["body"])
            for c in json.loads(r["body"]).get("data") or []:
                contracts[(idx, exp, float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
        targets = [
            ("NSE_INDEX|Nifty Bank","2026-10-27",55200,"PE","2026-10-21"),
            ("NSE_INDEX|Nifty Bank","2026-10-27",54400,"PE","2026-10-23"),
            ("NSE_INDEX|Nifty 50","2026-10-27",22500,"PE","2026-10-23"),
            ("NSE_INDEX|Nifty 50","2026-10-27",22600,"CE","2026-10-26"),
            ("NSE_INDEX|Nifty Bank","2026-10-27",54300,"PE","2026-10-26"),
        ]
        for idx, exp, strike, typ, day in targets:
            key = contracts.get((idx, exp, float(strike), typ))
            print("target", idx, strike, typ, day, key)
            url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
            r = fetch(url)
            print("  candles", r["status"])
            (OUT / f"candles_{idx.split('|')[1].replace(' ','_')}_{strike}{typ}_{day}.json").write_text(r["body"])
        # Nifty Nov-03 chain + v3 candles for Oct-28 22500PE
        url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote('NSE_INDEX|Nifty 50', safe='')}&expiry_date=2026-11-03"
        r = fetch(url); print("Nifty chain 2026-11-03", r["status"])
        (OUT / "chain_Nifty_50_2026-11-03.json").write_text(r["body"])
        key = None
        for row in json.loads(r["body"]).get("data") or []:
            if row["strike_price"] == 22500: key = row["put_options"]["instrument_key"]
        print("Nifty 22500PE Nov03 key", key)
        if key:
            url = f"https://api.upstox.com/v3/historical-candle/{quote(key, safe='')}/minutes/5/2026-10-28/2026-10-28"
            r = fetch(url); print("v3 candles Oct28", r["status"])
            (OUT / "candles_Nifty_50_22500PE_2026-10-28.json").write_text(r["body"])
        # Bank chain scan for post-Oct27 expiries
        for exp in ("2026-11-02","2026-11-06","2026-11-12","2026-11-13","2026-11-19","2026-11-20","2026-11-24","2026-11-26","2026-11-27","2026-11-30"):
            url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote('NSE_INDEX|Nifty Bank', safe='')}&expiry_date={exp}"
            r = fetch(url)
            try: n = len(json.loads(r["body"]).get("data") or [])
            except Exception: n = -1
            print(f"Bank chain {exp}", r["status"], "rows", n)
            if n > 0:
                (OUT / f"chain_Nifty_Bank_{exp}.json").write_text(r["body"])
        browser.close()
    print("done")

if __name__ == "__main__":
    main()
