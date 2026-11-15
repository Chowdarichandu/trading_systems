#!/usr/bin/env python3
"""Phase-0 BULK fetch: genuine 1-min Bank Nifty spot (v3) + option premiums
(v2 expired-instruments), Jan-Oct 2026. Range calls per contract over its
expiry window; per-day top-ups for any needed day the range call missed.
NOTHING is resampled or fabricated: every candle comes from the API.
Token never printed. Output: ~/workspace/trading/scalp_1min_data/"""
import sys, json, csv, glob, math
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr

TR = Path.home() / "workspace/trading"
OUT = TR / "scalp_1min_data"; (OUT / "options").mkdir(parents=True, exist_ok=True)
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")
token = read_token()

# ---- trading days, day OHLC from the 5-min spot union (day set + strike bands only)
dayohlc = {}
for f in glob.glob(str(TR / "data/banknifty-2026-*/spot_5m.csv")):
    for r in csv.DictReader(open(f)):
        d = r["timestamp"][:10]
        o,h,l = float(r["open"]), float(r["high"]), float(r["low"])
        if d in dayohlc:
            dayohlc[d][1] = max(dayohlc[d][1], h); dayohlc[d][2] = min(dayohlc[d][2], l)
        else: dayohlc[d] = [o, h, l]
days = sorted(dayohlc)
print(f"trading days: {len(days)} {days[0]}..{days[-1]}", flush=True)

def exp_for(day): return next(e for e in EXPIRIES if e >= day)

# needed strikes per (expiry, strike, type): days whose [low,high] band (+-100) covers the strike
needed = {}   # (exp, strike, typ) -> set(days)
for d in days:
    o,h,l = dayohlc[d]; exp = exp_for(d)
    lo = math.floor((l-100)/100)*100; hi = math.ceil((h+100)/100)*100
    s = lo
    while s <= hi:
        for typ in ("CE","PE"): needed.setdefault((exp, s, typ), set()).add(d)
        s += 100
print(f"contracts needed: {len(needed)}", flush=True)

# instrument keys
keymap = {}
for exp in EXPIRIES:
    p = TR / f"historical_proof_data/contracts_BANKNIFTY_{exp}.json"
    for c in json.loads(p.read_text())["data"]:
        if c.get("weekly") is False:
            keymap[(exp, int(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]

from playwright.sync_api import sync_playwright
manifest = {"spot_days_ok": [], "spot_days_fail": [], "contracts": {}, "missing": []}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
    ctx = browser.new_context(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", **atr._local_proxy_kwargs())
    page = ctx.new_page()
    try: page.goto("https://api.upstox.com/", timeout=60000, wait_until="domcontentloaded")
    except Exception as e: print("origin:", str(e)[:120], flush=True)
    def fetch(url):
        return page.evaluate("""async ([url, tok]) => {
            try { const r = await fetch(url, {headers: {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}});
                const t = await r.text(); return {status: r.status, body: t}; }
            catch(e){ return {status:0, body:String(e).slice(0,500)}; }
        }""", [url, token])
    r = fetch("https://api.upstox.com/v2/user/profile"); print("profile", r["status"], flush=True)
    IDX = quote('NSE_INDEX|Nifty Bank', safe='')

    # ---- spot: one range call per month
    for m in range(1, 11):
        md = [d for d in days if d[5:7] == f"{m:02d}"]
        if not md: continue
        url = f"https://api.upstox.com/v3/historical-candle/{IDX}/minutes/1/{md[-1]}/{md[0]}"
        r = fetch(url)
        try: candles = json.loads(r["body"]).get("data", {}).get("candles", [])
        except Exception: candles = []
        got = {}
        for c in candles: got.setdefault(c[0][:10], []).append(c)
        rows = []
        for d in md:
            if d in got and len(got[d]) >= 300:
                manifest["spot_days_ok"].append(d)
                rows += sorted(got[d])
            else:
                manifest["spot_days_fail"].append(d); print("SPOT MISS", d, len(got.get(d, [])), flush=True)
        with open(OUT / f"spot_1m_2026-{m:02d}.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["timestamp","open","high","low","close"])
            for c in rows: w.writerow([c[0], c[1], c[2], c[3], c[4]])
        print(f"spot month {m:02d}: days ok {sum(1 for d in md if d in manifest['spot_days_ok'])}/{len(md)}", flush=True)

    # ---- options: one range call per contract over the days it is needed
    items = sorted(needed.items())
    for i, ((exp, strike, typ), ndays) in enumerate(items):
        key = keymap.get((exp, strike, typ))
        tag = f"{exp}_{strike}{typ}"
        if not key:
            manifest["contracts"][tag] = "NO_KEY"; manifest["missing"] += [[d, strike, typ] for d in sorted(ndays)]
            continue
        nd = sorted(ndays)
        url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/1minute/{nd[-1]}/{nd[0]}"
        r = fetch(url)
        try: candles = json.loads(r["body"]).get("data", {}).get("candles", [])
        except Exception: candles = []
        got = {}
        for c in candles: got.setdefault(c[0][:10], []).append(c)
        miss = [d for d in nd if len(got.get(d, [])) < 300]
        # per-day top-ups for missed needed days
        for d in miss:
            url1 = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/1minute/{d}/{d}"
            r1 = fetch(url1)
            try: c1 = json.loads(r1["body"]).get("data", {}).get("candles", [])
            except Exception: c1 = []
            if len(c1) >= 300: got[d] = c1
        still = [d for d in nd if len(got.get(d, [])) < 300]
        rows = []
        for d in nd:
            if d in got: rows += sorted(got[d])
        edir = OUT / "options" / exp; edir.mkdir(exist_ok=True)
        with open(edir / f"opt_{strike}{typ}.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["timestamp","open","high","low","close","volume","oi"])
            for c in rows: w.writerow([c[0], c[1], c[2], c[3], c[4], c[5], c[6]])
        manifest["contracts"][tag] = {"days_needed": len(nd), "days_got": len(nd) - len(still), "missing_days": still}
        for d in still: manifest["missing"].append([d, strike, typ])
        if (i+1) % 50 == 0: print(f"options {i+1}/{len(items)}", flush=True)
    browser.close()

(OUT / "fetch_manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"DONE spot_ok={len(manifest['spot_days_ok'])}/{len(days)} contracts={len(manifest['contracts'])} missing_cells={len(manifest['missing'])}", flush=True)
