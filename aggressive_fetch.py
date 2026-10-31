#!/usr/bin/env python3
"""Aggressive tuning fetch: (a) ITM-strike October candles for base+addon legs,
(b) Jan-Sep premium candles for NS1 second / NS2 afternoon add-on legs.
Browser-fetch script-token route (same as historical_proof_fetch.py).
Token never printed/logged. Paper only."""
import sys, json, csv
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "aggressive_data"; OUT.mkdir(exist_ok=True)
HP = TR / "historical_proof_data"
OCTD = TR / "v4_options_oct_data"
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def contracts_map():
    m = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        for exp in EXPIRIES:
            for base in (HP, OCTD):
                name = f"contracts_{sym}_{exp}.json" if base == HP else \
                       f"contracts_{'Nifty_50' if sym=='NIFTY' else 'Nifty_Bank'}_{exp}.json"
                p = base / name
                if p.exists():
                    for c in json.loads(p.read_text()).get("data") or []:
                        if c.get("weekly") is False:
                            m[(sym, exp, float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
                    break
    # Nov-03 2026 weekly chain (Nifty only, from cached chain file)
    nov3 = {}
    p = OCTD / "chain_Nifty_50_2026-11-03.json"
    if p.exists():
        for row in json.loads(p.read_text()).get("data") or []:
            nov3[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
            nov3[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
    return m, nov3

def build_jobs():
    jobs = {}  # tag -> (key, kind, day)
    cmap, nov3 = contracts_map()
    def add(sym, strike, typ, day, exp):
        tag = f"{sym}_{int(strike)}{typ}_{day}_{exp}"
        if (OUT / f"candles_{tag}.json").exists(): return
        if exp == "2026-11-03":
            key = nov3.get((float(strike), typ)) if sym == "NIFTY" else None; kind = "v3"
        else:
            key = cmap.get((sym, exp, float(strike), typ)); kind = "expired"
        if not key:
            print("NO_KEY", tag); return
        jobs[tag] = (key, kind, day)
    # (a) ITM October legs: base B2/N1 Oct legs + NS addon Oct legs
    for f in ("historical_proof_bank_B2_trades.csv", "historical_proof_nifty_N1_trades.csv"):
        for r in csv.DictReader(open(TR / f)):
            if r["date"] < "2026-10-01": continue
            st = int(float(r["strike"])); itm = st - 100 if r["direction"] == "CE" else st + 100
            add(r["index"], itm, r["direction"], r["date"], r["expiry"])
    rows = list(csv.DictReader(open(TR / "index_options_newsetup_premium_october_trades.csv")))
    for r in rows:
        if (r["family"], r["leg"]) not in (("NS1", "second"), ("NS2", "afternoon_rescan")): continue
        st = int(float(r["strike"])); itm = st - 100 if r["direction"] == "CE" else st + 100
        add(r["index"], itm, r["direction"], r["date"], r["expiry"])
    # (b) NS Jan-Sep addon legs
    for f, legname in (("index_options_newsetup_ns1_trades_jan_oct_2026.csv", "second"),
                       ("index_options_newsetup_ns2_trades_jan_oct_2026.csv", "afternoon_rescan")):
        for r in csv.DictReader(open(TR / f)):
            if r["leg"] != legname or r["date"] >= "2026-10-01": continue
            strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
            exp = next(e for e in EXPIRIES if e >= r["date"])
            add(r["index"], strike, r["direction"], r["date"], exp)
    return jobs

def main():
    token = read_token()
    jobs = build_jobs()
    print(f"jobs: {len(jobs)}", flush=True)
    if not jobs: return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = browser.new_context(ignore_https_errors=True, **atr._local_proxy_kwargs())
        page = ctx.new_page()
        try: page.goto("https://api.upstox.com/", timeout=60000, wait_until="domcontentloaded")
        except Exception as e: print("origin:", str(e)[:150])
        def fetch(url):
            return page.evaluate("""async ([url, tok]) => {
                try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                    const t = await r.text(); return {status: r.status, body: t.slice(0,500000)}; }
                catch(e){ return {status:0, body:String(e).slice(0,500)}; }
            }""", [url, token])
        r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"], flush=True)
        ok = bad = 0
        for tag, (key, kind, day) in jobs.items():
            if kind == "expired":
                url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
            else:
                url = f"https://api.upstox.com/v3/historical-candle/{quote(key, safe='')}/minutes/5/{day}/{day}"
            r = fetch(url)
            try: n = len(json.loads(r["body"]).get("data", {}).get("candles", []))
            except Exception: n = -1
            if r["status"] == 200 and n > 0:
                (OUT / f"candles_{tag}.json").write_text(r["body"]); ok += 1
            else:
                bad += 1; print("FAIL", tag, r["status"], n, flush=True)
        print(f"done ok={ok} fail={bad}", flush=True)
        browser.close()

if __name__ == "__main__":
    main()
