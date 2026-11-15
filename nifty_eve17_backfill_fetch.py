#!/usr/bin/env python3
"""Fetch the 3 premium candle files missing for NIFTY-EVE-17 scoring
(2026-11-09 Nifty evening engine): the DEC-S1 Component-A legs
  2026-01-23 25100 PE (expiry 2026-01-27)
  2026-10-09 22400 CE (expiry 2026-10-27)
  2026-10-21 22800 PE (expiry 2026-10-27)
into the engine's store ~/workspace/trading/aggressive_data/ as
candles_NIFTY_{strike}{typ}_{day}_{expiry}.json (raw Upstox response body,
the exact format aggressive_fetch.py wrote).

Machinery: aggressive_fetch.py's own route — Playwright browser fetch with
the browser User-Agent, script token from upstox_refresh/.env (never
printed), instrument keys from historical_proof_data/contracts_NIFTY_{exp}
.json (monthly, weekly is False), expired-instruments v2 endpoint.
Add-only: creates NEW files only; refuses to overwrite an existing file.
HTTP 429 = hard stop: abort immediately, no retry, no route switch.
Fetch only — EVE-17 is scored by the evening engine, not here."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

TARGETS = [  # (strike, typ, day, expiry)
    (25100, "PE", "2026-01-23", "2026-01-27"),
    (22400, "CE", "2026-10-09", "2026-10-27"),
    (22800, "PE", "2026-10-21", "2026-10-27"),
]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def key_for(strike, typ, exp):
    data = json.loads((HP / f"contracts_NIFTY_{exp}.json").read_text()).get("data") or []
    hits = [c["instrument_key"] for c in data
            if c.get("weekly") is False
            and float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    assert len(hits) == 1, (strike, typ, exp, hits)
    return hits[0]

def main():
    token = read_token()
    jobs = []
    for strike, typ, day, exp in TARGETS:
        tag = f"NIFTY_{strike}{typ}_{day}_{exp}"
        dest = OUT / f"candles_{tag}.json"
        if dest.exists():
            print("SKIP_EXISTS", tag, flush=True)
            continue
        jobs.append((tag, key_for(strike, typ, exp), day, dest))
    print(f"jobs: {len(jobs)}", flush=True)
    if not jobs:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox",
            "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = browser.new_context(ignore_https_errors=True, user_agent=UA,
                                  **atr._local_proxy_kwargs())
        page = ctx.new_page()
        try:
            page.goto("https://api.upstox.com/", timeout=60000,
                      wait_until="domcontentloaded")
        except Exception as e:
            print("origin:", str(e)[:150], flush=True)

        def fetch(url):
            return page.evaluate("""async ([url, tok]) => {
                try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                    const t = await r.text(); return {status: r.status, body: t.slice(0,500000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])

        r = fetch("https://api.upstox.com/v2/user/profile")
        print("profile", r["status"], flush=True)
        if r["status"] == 429:
            print("HARD_STOP_429 at profile check — nothing fetched", flush=True)
            browser.close()
            return
        for tag, key, day, dest in jobs:
            url = (f"https://api.upstox.com/v2/expired-instruments/"
                   f"historical-candle/{quote(key, safe='')}/5minute/{day}/{day}")
            r = fetch(url)
            if r["status"] == 429:
                print("HARD_STOP_429", tag, "— aborting, no retry", flush=True)
                break
            try:
                candles = json.loads(r["body"]).get("data", {}).get("candles", [])
            except Exception:
                candles = []
            if r["status"] == 200 and candles:
                dest.write_text(r["body"])
                print(f"WROTE {tag} bars={len(candles)} "
                      f"first={candles[0][0]} last={candles[-1][0]}", flush=True)
            else:
                print(f"FAIL {tag} status={r['status']} bars={len(candles)} "
                      f"body_head={r['body'][:200]!r}", flush=True)
        browser.close()

if __name__ == "__main__":
    main()
