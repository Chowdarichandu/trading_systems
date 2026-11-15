#!/usr/bin/env python3
"""Fetch missing October premium contract-days via Upstox API through the
localhost CONNECT forwarder (same route prior premium work used inside the
browser; here a plain API GET, no browser navigation). Token read from the
script's own .env store, never printed. Paper only, no orders."""
import sys, json, csv
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path.home() / "workspace/trading/upstox_refresh"))
import auto_token_refresh as atr
import requests

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
IDX = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}

def read_token():
    for line in (Path.home() / "workspace/trading/upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

def main():
    atr._local_proxy_kwargs()
    tok = read_token()
    proxies = {"http": "http://127.0.0.1:8899", "https": "http://127.0.0.1:8899"}
    H = {"Authorization": "Bearer " + tok, "Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
    rows = list(csv.DictReader(open(Path.home() / "workspace/trading/index_options_skill_tuned_oct30_trades.csv")))
    need = sorted({(r["index"], r["date"], int(r["strike"]), r["direction"], r["expiry"])
                   for r in rows if r["premium_status"] == "NOT_COMPUTED"})
    print("need", len(need))
    # contract keys for 27 Oct
    contracts = {}
    for idx_key, exp, tag in [(IDX["NIFTY"], "2026-10-27", "Nifty_50"),
                              (IDX["BANKNIFTY"], "2026-10-27", "Nifty_Bank")]:
        p = OUT / f"contracts_{tag}_{exp}.json"
        data = json.loads(p.read_text()).get("data") or []
        for c in data:
            contracts[(idx_key, exp, float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
        print("contracts cached", idx_key, exp, len(data))
    nov3 = {}
    chain = json.loads((OUT / "chain_Nifty_50_2026-11-03.json").read_text()).get("data") or []
    for row in chain:
        nov3[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
        nov3[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
    print("Nov03 Nifty chain cached", len(chain))
    # Bank Nov03 chain via API (prior log: Bank post-Oct chain gap)
    bank_nov3 = {}
    try:
        r = requests.get("https://api.upstox.com/v2/option/chain",
                         params={"instrument_key": IDX["BANKNIFTY"], "expiry_date": "2026-11-03"},
                         headers=H, proxies=proxies, timeout=30)
        print("Bank Nov03 chain status", r.status_code)
        if r.status_code == 200:
            for row in r.json().get("data") or []:
                bank_nov3[(float(row["strike_price"]), "CE")] = row["call_options"]["instrument_key"]
                bank_nov3[(float(row["strike_price"]), "PE")] = row["put_options"]["instrument_key"]
            print("Bank Nov03 chain strikes", len(bank_nov3) // 2)
    except Exception as e:
        print("Bank Nov03 chain error", type(e).__name__, str(e)[:200])
    for (sym, day, strike, typ, exp) in need:
        tag = f"{sym}_{strike}{typ}_{day}_{exp}"
        outp = OUT / f"candles_premium_{tag}.json"
        if outp.exists():
            print("already", tag); continue
        if exp == "2026-11-03":
            key = nov3.get((float(strike), typ)) if sym == "NIFTY" else bank_nov3.get((float(strike), typ))
            url = f"https://api.upstox.com/v3/historical-candle/{quote(key, safe='')}/minutes/5/{day}/{day}" if key else None
        else:
            key = contracts.get((IDX[sym], exp, float(strike), typ))
            url = f"https://api.upstox.com/v2/expired-instruments/historical-candle/{quote(key, safe='')}/5minute/{day}/{day}" if key else None
        if not url:
            print("NO_KEY", tag); continue
        try:
            r = requests.get(url, headers=H, proxies=proxies, timeout=60)
            n = -1
            try:
                n = len(r.json().get("data", {}).get("candles", []))
            except Exception:
                pass
            print(tag, r.status_code, "candles", n)
            if r.status_code == 200 and n > 0:
                outp.write_text(r.text)
        except Exception as e:
            print(tag, "error", type(e).__name__, str(e)[:200])

if __name__ == "__main__":
    main()
