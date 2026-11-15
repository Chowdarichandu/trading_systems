#!/usr/bin/env python3
"""Historical proof stage 2: prepare Jan-Sep legs (spot entry from cached
progressive spot_5m where the U1 file has none; strike = ATM nearest 100;
expiry = first monthly expiry >= trade date) and fetch 5-min premium candles
via browser-fetch script-token route. Token never printed."""
import sys, json, csv
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "historical_proof_data"
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def load_spot(sym):
    d = {}
    with open(TR / f"data/progressive/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d[(r["timestamp"][:10], r["timestamp"][11:16])] = float(r["open"])
    return d

def prep():
    legs = []
    for fname, sysname in [("index_options_U1_B2_bank_trades.csv", "B2"),
                           ("index_options_U1_N1_nifty_trades.csv", "N1")]:
        rows = list(csv.DictReader(open(TR / fname)))
        spot = None
        for r in rows:
            if r["net_unit"] != "spot_provisional":
                continue
            sym = r["index"]
            if spot is None or spot[0] != sym:
                spot = (sym, load_spot(sym))
            ev = r["entry_value"]
            if ev:
                entry_spot = float(ev); src = "u1_file"
            else:
                entry_spot = spot[1].get((r["date"], r["entry_time"]))
                src = "spot_5m_open_at_entry_bar"
                if entry_spot is None:
                    legs.append({**r, "system": sysname, "prep_status": "NO_SPOT_BAR"})
                    continue
            strike = int(round(entry_spot / 100.0) * 100)
            expiry = next(e for e in EXPIRIES if e >= r["date"])
            legs.append({"system": sysname, "index": sym, "date": r["date"],
                         "direction": r["direction"], "representative_system": r["representative_system"],
                         "source_systems": r["source_systems"], "entry_time": r["entry_time"],
                         "entry_spot": entry_spot, "entry_spot_source": src,
                         "strike": strike, "expiry": expiry,
                         "old_spot_net": float(r["net_rs"]), "old_exit_reason": r["exit_reason"],
                         "prep_status": "OK"})
    return legs

def main():
    legs = prep()
    ok = [l for l in legs if l["prep_status"] == "OK"]
    bad = [l for l in legs if l["prep_status"] != "OK"]
    print(f"legs total {len(legs)} ok {len(ok)} no_spot {len(bad)}")
    for b in bad: print("NO_SPOT", b["system"], b["date"], b["entry_time"])
    with open(OUT / "legs_jansep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(legs[0].keys())); w.writeheader(); w.writerows(legs)
    # contracts for chosen expiries (monthly files already saved by discovery)
    contracts = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        for exp in EXPIRIES:
            p = OUT / f"contracts_{sym}_{exp}.json"
            if not p.exists():
                p2 = TR / f"v4_options_oct_data/contracts_{'Nifty_50' if sym=='NIFTY' else 'Nifty_Bank'}_{exp}.json"
                data = json.loads(p2.read_text()).get("data") or [] if p2.exists() else []
            else:
                data = json.loads(p.read_text()).get("data") or []
            for c in data:
                if c.get("weekly") is False:
                    contracts[(sym, exp, float(c["strike_price"]), c["instrument_type"])] = (c["instrument_key"], c["lot_size"])
    print("monthly contracts mapped", len(contracts))
    jobs = []
    for l in ok:
        key = contracts.get((l["index"], l["expiry"], float(l["strike"]), l["direction"]))
        tag = f"{l['index']}_{l['strike']}{l['direction']}_{l['date']}_{l['expiry']}"
        l["lot"] = key[1] if key else ""
        l["tag"] = tag
        if not key:
            l["fetch_status"] = "NO_CONTRACT"; print("NO_CONTRACT", tag); continue
        if (OUT / f"candles_{tag}.json").exists():
            l["fetch_status"] = "CACHED"; continue
        jobs.append((tag, key[0], l["date"]))
    print("to fetch", len(jobs))
    if jobs:
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
                        const t = await r.text(); return {status: r.status, body: t.slice(0,1000000)}; }
                    catch(e){ return {status:0, body:String(e).slice(0,500)}; }
                }""", [url, token])
            r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"])
            bytag = {l["tag"]: l for l in ok}
            for tag, key, day in jobs:
                url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}"
                r = fetch(url)
                try: n = len(json.loads(r["body"]).get("data", {}).get("candles", []))
                except Exception: n = -1
                print(tag, r["status"], "candles", n)
                if r["status"] == 200 and n > 0:
                    (OUT / f"candles_{tag}.json").write_text(r["body"])
                    bytag[tag]["fetch_status"] = f"FETCHED_{n}"
                else:
                    bytag[tag]["fetch_status"] = f"FAILED_status{r['status']}_candles{n}"
            browser.close()
    with open(OUT / "legs_jansep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(legs[0].keys())); w.writeheader(); w.writerows(legs)
    print("done")

if __name__ == "__main__":
    main()
