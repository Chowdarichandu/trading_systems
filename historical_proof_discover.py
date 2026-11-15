#!/usr/bin/env python3
"""Historical proof stage 1: discover monthly expiries Jan-Oct 2026 per index.
Monthly = contracts with weekly==False. Candidates: Tue/Wed/Thu of the last
week of each month and the day before each (holiday shift). Token from .env,
never printed. Browser-fetch route only (connector not used)."""
import sys, json
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

def read_token():
    for line in (Path.home() / "workspace/trading/upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

OUT = Path.home() / "workspace/trading/historical_proof_data"
OUT.mkdir(exist_ok=True)
IDX = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}

import datetime as dt
def candidates(y, m):
    # last day of month
    if m == 12: last = dt.date(y, 12, 31)
    else: last = dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    days = set()
    d = last
    while (last - d).days < 7:
        if d.weekday() in (1, 2, 3):  # Tue Wed Thu
            days.add(d); days.add(d - dt.timedelta(days=1))
        d -= dt.timedelta(days=1)
    return sorted(days)

def main():
    token = read_token()
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
                    const t = await r.text(); return {status: r.status, body: t.slice(0,3000000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])
        r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"])
        if r["status"] != 200:
            print("TOKEN NOT VALID, abort"); return
        result = {}
        for sym, idx in IDX.items():
            result[sym] = {}
            for m in range(1, 11):
                found = None
                for d in candidates(2026, m):
                    ds = d.isoformat()
                    if (OUT / f"contracts_{sym}_{ds}.json").exists():
                        data = json.loads((OUT / f"contracts_{sym}_{ds}.json").read_text()).get("data") or []
                    else:
                        url = f"https://api.upstox.com/v2/expired-instruments/option/contract?instrument_key={quote(idx, safe='')}&expiry_date={ds}"
                        r = fetch(url)
                        if r["status"] != 200:
                            print(sym, ds, "status", r["status"]); continue
                        (OUT / f"contracts_{sym}_{ds}.json").write_text(r["body"])
                        data = json.loads(r["body"]).get("data") or []
                    monthly = [c for c in data if c.get("weekly") is False]
                    if monthly:
                        lots = sorted({c["lot_size"] for c in monthly})
                        found = (ds, len(monthly), lots)
                        print(sym, "month", m, "MONTHLY expiry", ds, "contracts", len(monthly), "lots", lots)
                        break
                    else:
                        print(sym, ds, "no monthly contracts (rows", len(data), ")")
                result[sym][str(m)] = found
        (OUT / "monthly_expiries.json").write_text(json.dumps(result, indent=1))
        browser.close()
    print("done")

if __name__ == "__main__":
    main()
