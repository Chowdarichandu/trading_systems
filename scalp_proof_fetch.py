#!/usr/bin/env python3
"""Phase-0 proof fetch: genuine 1-min candles via browser script-token route.
Tests: (a) BANKNIFTY index 1-min via v3, (b) expired ATM option 1-min via v2
expired-instruments, (c) same option via v3. Token never printed."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "scalp_1min_data/proof"; OUT.mkdir(parents=True, exist_ok=True)
DAY = "2026-10-27"

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

token = read_token()
contracts = json.loads((TR / "historical_proof_data/contracts_BANKNIFTY_2026-10-27.json").read_text())["data"]
keys = {}
for c in contracts:
    if c.get("weekly") is False and float(c["strike_price"]) in (54400.0, 54500.0):
        keys[(int(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
print("keys found:", sorted(keys), flush=True)

jobs = {
    "index_v3": f"https://api.upstox.com/v3/historical-candle/{quote('NSE_INDEX|Nifty Bank', safe='')}/minutes/1/{DAY}/{DAY}",
}
for (st, typ), k in keys.items():
    jobs[f"opt{st}{typ}_v2exp_1minute"] = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(k, safe='')}/1minute/{DAY}/{DAY}"
    jobs[f"opt{st}{typ}_v3"] = f"https://api.upstox.com/v3/historical-candle/{quote(k, safe='')}/minutes/1/{DAY}/{DAY}"

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
                const t = await r.text(); return {status: r.status, body: t.slice(0,2000000)}; }
            catch(e){ return {status:0, body:String(e).slice(0,500)}; }
        }""", [url, token])
    r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"], flush=True)
    for tag, url in jobs.items():
        r = fetch(url)
        try:
            candles = json.loads(r["body"]).get("data", {}).get("candles", [])
            n = len(candles)
            first = candles[-1][0] if n else None; last = candles[0][0] if n else None
        except Exception:
            n, first, last = -1, None, None
        print(f"{tag}: status={r['status']} candles={n} first={first} last={last}", flush=True)
        if r["status"] == 200 and n > 0:
            (OUT / f"{tag}_{DAY}.json").write_text(r["body"])
    browser.close()
print("PROOF DONE", flush=True)
