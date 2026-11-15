#!/usr/bin/env python3
"""NIFTY-EVE-12 population fetch (2026-11-10): the 20 (contract, day) premium
cells the DEC-S1 construction store (daily2leg/prem_nifty.json) is missing for
the Jan-Oct 2026 afternoon window (ATM band around the 12:25 spot close +
every strike spot touches 12:30-15:10, monthly expiry in force).

Route = the house route (nifty_eve17_backfill_fetch.py / aggressive_fetch.py):
Playwright browser fetch, browser User-Agent, script token from
upstox_refresh/.env (never printed).
  - Expired expiries (<= 2026-10-27): instrument key from
    historical_proof_data/contracts_NIFTY_{exp}.json (weekly is False),
    /v2/expired-instruments/historical-candle/{key}/5minute/{day}/{day}
  - Live expiry 2026-11-23: keys from a live /v2/option/chain call for
    NSE_INDEX|Nifty 50 (raw chain cached add-only at
    v4_options_oct_data/chain_Nifty_50_2026-11-23.json, the Nov-03 weekly
    precedent), /v3/historical-candle/{key}/minutes/5/{day}/{day}
Add-only: raw bodies written to aggressive_data/ only if the file does not
exist; fetched candles go to a sidecar (/tmp/eve12_fetched.json) for the
separate merge step. HTTP 429 = HARD STOP, no retry, no route switch;
progress is preserved in the sidecar."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"
HP = TR / "historical_proof_data"
OCTD = TR / "v4_options_oct_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
SIDECAR = Path("/tmp/eve12_fetched.json")

def read_token():
    prefix = "UPSTOX_ACCESS_" + "TOKEN" + "="
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def key_expired(strike, typ, exp):
    data = json.loads((HP / f"contracts_NIFTY_{exp}.json").read_text()).get("data") or []
    hits = [c["instrument_key"] for c in data
            if c.get("weekly") is False
            and float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    assert len(hits) == 1, (strike, typ, exp, hits)
    return hits[0]

def main():
    token = read_token()
    jobs = [tuple(j) for j in json.load(open("/tmp/eve12_jobs.json"))]
    print(f"jobs: {len(jobs)}", flush=True)
    sidecar = json.loads(SIDECAR.read_text()) if SIDECAR.exists() else {}
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
                    const t = await r.text(); return {status: r.status, body: t.slice(0,900000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])

        r = fetch("https://api.upstox.com/v2/user/profile")
        print("profile", r["status"], flush=True)
        if r["status"] == 429:
            print("HARD_STOP_429 at profile check - nothing fetched", flush=True)
            browser.close(); return
        if r["status"] != 200:
            print("PROFILE_NOT_200 - aborting", r["status"], flush=True)
            browser.close(); return

        # live chain for the 2026-11-23 monthly (only if v3 jobs exist)
        chain_keys = {}
        if any(j[0] == "2026-11-23" for j in jobs):
            dest = OCTD / "chain_Nifty_50_2026-11-23.json"
            if dest.exists():
                body = dest.read_text()
                print("chain: cached file exists, using it", flush=True)
            else:
                url = ("https://api.upstox.com/v2/option/chain?instrument_key=" +
                       quote("NSE_INDEX|Nifty 50", safe="") + "&expiry_date=2026-11-23")
                r = fetch(url)
                if r["status"] == 429:
                    print("HARD_STOP_429 at chain fetch - nothing fetched", flush=True)
                    browser.close(); return
                if r["status"] != 200:
                    print("CHAIN_FAIL", r["status"], r["body"][:200], flush=True)
                    browser.close(); return
                body = r["body"]
                dest.write_text(body)
                print("chain: fetched + cached add-only", flush=True)
            for row in json.loads(body).get("data") or []:
                chain_keys[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
                chain_keys[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
            print(f"chain keys: {len(chain_keys)}", flush=True)

        done = 0
        for exp, strike, typ, day in jobs:
            tag = f"NIFTY_{strike}{typ}_{day}_{exp}"
            skey = f"{exp}|{strike}|{typ}|{day}"
            if skey in sidecar:
                print("SKIP_SIDECAR", tag, flush=True); continue
            if exp == "2026-11-23":
                key = chain_keys.get((float(strike), typ))
                url = (f"https://api.upstox.com/v3/historical-candle/"
                       f"{quote(key, safe='')}/minutes/5/{day}/{day}") if key else None
            else:
                key = key_expired(strike, typ, exp)
                url = (f"https://api.upstox.com/v2/expired-instruments/"
                       f"historical-candle/{quote(key, safe='')}/5minute/{day}/{day}")
            if not url:
                print("NO_KEY", tag, flush=True); continue
            r = fetch(url)
            if r["status"] == 429:
                print("HARD_STOP_429", tag, f"- aborting after {done} fetched, no retry", flush=True)
                break
            try:
                candles = json.loads(r["body"]).get("data", {}).get("candles", [])
            except Exception:
                candles = []
            if r["status"] == 200 and candles:
                dest = OUT / f"candles_{tag}.json"
                if dest.exists():
                    print(f"RAW_EXISTS {tag} (kept existing file; fresh body used for merge)", flush=True)
                else:
                    dest.write_text(r["body"])
                sidecar[skey] = candles
                SIDECAR.write_text(json.dumps(sidecar))
                done += 1
                print(f"WROTE {tag} bars={len(candles)} first={candles[0][0]} last={candles[-1][0]}", flush=True)
            else:
                print(f"FAIL {tag} status={r['status']} bars={len(candles)} body_head={r['body'][:200]!r}", flush=True)
            page.wait_for_timeout(150)
        print(f"session done: fetched_this_run={done} sidecar_total={len(sidecar)}", flush=True)
        browser.close()

if __name__ == "__main__":
    main()
