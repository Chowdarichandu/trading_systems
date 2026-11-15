#!/usr/bin/env python3
"""BTST PROGRAMME — gap fetch (2026-11-13).
Computes every Bank Nifty contract-day the BTST scorer needs (Arm 1, both
sides, Jan-Oct 2026 gate window + November counterfactual), diffs against
the local stores (option_5m chain store + prem_bank.json), and fetches only
the missing contract-days into btst_data/ (raw API bodies, chain-build
format) with manifest.csv. Resume-safe: existing files are skipped.
Routes: expired monthly expiries -> v2 expired-instruments (contract +
historical-candle); the live 2026-11-23 expiry -> instruments_cache key +
v3 historical-candle. Browser User-Agent on every call (standing fix).
On HTTP 429: HARD STOP (exit 2), no retry, no route switch."""
import csv, json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path.home() / "workspace/trading"))
from btst_common import (TR, PremStore, load_bank_spot, spot_bar, btst_expiry,
                         atm_strike, EXIT_BARS, trading_days)

OUT = TR / "btst_data"
OUT.mkdir(exist_ok=True)
MANIFEST = OUT / "manifest.csv"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
IDX = quote("NSE_INDEX|Nifty Bank", safe='')

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token, "no token"

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
        "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

# ---------------- needs ----------------
spot = load_bank_spot()
cal = [d for d in trading_days(spot) if "2026-01-01" <= d <= "2026-11-12"]
next_day = {cal[i]: cal[i + 1] for i in range(len(cal) - 1)}

entry_days = [d for d in cal if d <= "2026-10-29"] + \
             [d for d in cal if "2026-11-02" <= d <= "2026-11-12"]
needs = set()  # (exp, strike, side, day, kind) kind in {entry, exit}
for D in entry_days:
    b = spot_bar(spot, D, "15:10")
    if b is None:
        continue
    exp, strike = btst_expiry(D), atm_strike(b[4])
    for side in ("CE", "PE"):
        needs.add((exp, strike, side, D, "entry"))
        D1 = next_day.get(D)
        if D1 and D1 <= "2026-11-12":
            needs.add((exp, strike, side, D1, "exit"))

store = PremStore()
missing = {}  # (exp, strike, side, day) -> kinds
for exp, strike, side, day, kind in sorted(needs):
    bars = store.bars(exp, strike, side, day)
    if kind == "entry" and "15:15" not in bars:
        missing.setdefault((exp, strike, side, day), set()).add(kind)
    if kind == "exit" and any(hm not in bars for hm in EXIT_BARS):
        missing.setdefault((exp, strike, side, day), set()).add(kind)
print(f"needs: {len(needs)} contract-day-uses; missing contract-days: {len(missing)}", flush=True)

# ---------------- fetch ----------------
key_cache = {}
def expired_key(exp, strike, side):
    ck = ("EXP", exp)
    if ck not in key_cache:
        body = get(f"https://api.upstox.com/v2/expired-instruments/option/contract"
                   f"?instrument_key={IDX}&expiry_date={exp}")
        m = {}
        for c in (body.get("data") or []):
            m[(int(float(c["strike_price"])), c["instrument_type"])] = c["instrument_key"]
        key_cache[ck] = m
    return key_cache[ck].get((strike, side))

live_rows = None
def live_key(exp, strike, side):
    global live_rows
    if live_rows is None:
        live_rows = json.loads((TR / "daily2leg/instruments_cache.json").read_text())["rows"]
    for r in live_rows:
        if r["name"] == "BANKNIFTY" and r["expiry"] == exp and int(float(r["strike"])) == strike \
                and r["option_type"] == side:
            return r["key"]
    return None

rows_out = []
stop = False
for (exp, strike, side, day), kinds in sorted(missing.items()):
    fn = OUT / f"candles_BANKNIFTY_{strike}{side}_{exp}_{day}.json"
    if fn.exists():
        rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "OK_CACHED", ""])
        continue
    try:
        if exp <= "2026-10-27":
            key = expired_key(exp, strike, side)
            if not key:
                rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "MISSING", "NO_KEY"])
                continue
            url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
                   f"{quote(key, safe='')}/5minute/{day}/{day}")
        else:
            key = live_key(exp, strike, side)
            if not key:
                rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "MISSING", "NO_LIVE_KEY"])
                continue
            url = (f"https://api.upstox.com/v3/historical-candle/"
                   f"{quote(key, safe='')}/minutes/5/{day}/{day}")
        body = get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"HTTP 429 at {exp} {strike}{side} {day} — HARD STOP", flush=True)
            stop = True
            break
        rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "MISSING", f"HTTP {e.code}"])
        continue
    candles = [c for c in ((body.get("data") or {}).get("candles") or []) if c[0][:10] == day]
    if not candles:
        rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "MISSING", "NO_CANDLES"])
        continue
    fn.write_text(json.dumps(body))
    rows_out.append([exp, strike, side, day, "+".join(sorted(kinds)), "OK", len(candles)])
    print(f"fetched {exp} {strike}{side} {day} ({len(candles)} bars)", flush=True)
    time.sleep(0.35)

with open(MANIFEST, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["expiry", "strike", "side", "day", "kinds", "status", "detail"])
    w.writerows(rows_out)
ok = sum(1 for r in rows_out if r[5].startswith("OK"))
print(f"done: {ok}/{len(missing)} fetched-or-cached; manifest -> {MANIFEST}")
sys.exit(2 if stop else 0)
