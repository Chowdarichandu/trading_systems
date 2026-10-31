#!/usr/bin/env python3
"""Fetch Volrix-tuned October option 5-min candles via script-token browser route.
Paper only, no orders. Token read from script token store by this script only,
never printed/logged. Pattern from newsetup_premium_fetch.py."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
IDX = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}
# (sym, expiry, strike, type, day)
JOBS = [
    ("NIFTY", "2026-10-27", 22200, "CE", "2026-10-09"),
    ("NIFTY", "2026-10-27", 22200, "CE", "2026-10-15"),
    ("NIFTY", "2026-10-27", 22500, "CE", "2026-10-09"),
    ("NIFTY", "2026-10-27", 22500, "CE", "2026-10-15"),
    ("BANKNIFTY", "2026-10-27", 54300, "CE", "2026-10-26"),
    ("BANKNIFTY", "2026-10-27", 54300, "CE", "2026-10-27"),
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
    todo = []
    for (sym, exp, strike, typ, day) in JOBS:
        tag = f"{sym}_{strike}{typ}_{day}_{exp}"
        if (OUT / f"candles_premium_{tag}.json").exists():
            print("cached", tag); continue
        key = contracts.get((IDX[sym], exp, float(strike), typ))
        if not key:
            print("NO_KEY", sym, exp, strike, typ); continue
        todo.append((tag, key, day))
    print(f"to fetch: {len(todo)}")
    if not todo:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = browser.new_context(ignore_https_errors=True, **atr._local_proxy_kwargs())
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
        for tag, key, day in todo:
            url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
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
