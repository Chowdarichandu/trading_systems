#!/usr/bin/env python3
"""Browser-fetch option candles for premium completion, Oct 2026 (paper only).
Token from .env, never printed/logged. Reuses cached contracts/chain JSON where
present; fetches only missing candle files via Playwright + localhost forwarder
(same pattern as v4_options_browser_fetch.py). Muse connector NOT used (401)."""
import sys, json, csv, os
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

def read_token():
    for line in (Path.home() / "workspace/trading/upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
IDX = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}

def main():
    token = read_token()
    rows = list(csv.DictReader(open(Path.home() / "workspace/trading/index_options_premium_recon_oct.csv")))
    uniq = sorted({(r["index"], r["expiry"], int(r["strike"]), r["direction"], r["date"]) for r in rows})
    contracts = {}
    for idx_key, exp in [(IDX["NIFTY"], "2026-10-27"), (IDX["BANKNIFTY"], "2026-10-27")]:
        p = OUT / f"contracts_{idx_key.split('|')[1].replace(' ', '_')}_{exp}.json"
        data = json.loads(p.read_text()).get("data") or []
        for c in data:
            contracts[(idx_key, exp, float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
        print(f"contracts cached {idx_key} {exp}: {len(data)}")
    nov3 = {}
    chain = json.loads((OUT / "chain_Nifty_50_2026-11-03.json").read_text()).get("data") or []
    for row in chain:
        nov3[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
        nov3[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
    print(f"Nov03 chain cached: {len(chain)} strikes")
    # map each unique to key + outfile + url template
    jobs = []
    for (sym, exp, strike, typ, day) in uniq:
        idx_key = IDX[sym]
        tag = f"{sym}_{strike}{typ}_{day}_{exp}"
        # already-cached legacy filenames
        legacy = {"NIFTY_22500PE_2026-10-23_2026-10-27": "candles_Nifty_50_22500PE_2026-10-23.json",
                  "NIFTY_22600CE_2026-10-26_2026-10-27": "candles_Nifty_50_22600CE_2026-10-26.json",
                  "BANKNIFTY_54300PE_2026-10-26_2026-10-27": "candles_Nifty_Bank_54300PE_2026-10-26.json",
                  "BANKNIFTY_54400PE_2026-10-23_2026-10-27": "candles_Nifty_Bank_54400PE_2026-10-23.json",
                  "BANKNIFTY_55200PE_2026-10-21_2026-10-27": "candles_Nifty_Bank_55200PE_2026-10-21.json",
                  "NIFTY_22500PE_2026-10-28_2026-11-03": "candles_Nifty_50_22500PE_2026-10-28.json"}
        if tag in legacy and (OUT / legacy[tag]).exists():
            print("cached", tag); continue
        if exp == "2026-11-03":
            key = nov3.get((float(strike), typ)); kind = "v3"
        else:
            key = contracts.get((idx_key, exp, float(strike), typ)); kind = "expired"
        if not key:
            print("NO_KEY", sym, exp, strike, typ); continue
        jobs.append((tag, key, kind, day))
    print(f"to fetch: {len(jobs)}")
    if not jobs: return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
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
        r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"])
        for tag, key, kind, day in jobs:
            if kind == "expired":
                url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
            else:
                url = f"https://api.upstox.com/v3/historical-candle/{quote(key, safe='')}/minutes/5/{day}/{day}"
            r = fetch(url)
            try: n = len(json.loads(r["body"]).get("data", {}).get("candles", []))
            except Exception: n = -1
            print(tag, r["status"], "candles", n)
            if r["status"] == 200:
                (OUT / f"candles_premium_{tag}.json").write_text(r["body"])
        browser.close()
    print("done")

if __name__ == "__main__": main()
