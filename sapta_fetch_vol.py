#!/usr/bin/env python3
"""TARANG Round 6 data pull — volume-bearing 5-minute bars for the 75
wide-100 names (the frozen 25 already sit in data/tarang_vol/), covering
2025-01-01 -> 2026-11-13, into data/sapta_vol/<SYM>/spot_5m_vol.csv
(columns: timestamp,open,high,low,close,volume).

Machinery: identical to tarang_fetch_vol.py (the tarang_vol pull) —
Upstox v3 historical-candle API, script-token route
(UPSTOX_ACCESS_TOKEN read at runtime from upstox_refresh/.env, never
printed or written anywhere), browser User-Agent on every call.

Checkpointing: sapta_fetch_manifest.json rewritten after every chunk;
completed chunks are skipped on re-run (resumable).
HTTP 429 = HARD STOP for the whole pull: no retries, manifest marked
RATE_LIMITED, exit code 3. Any other HTTP error stops the run with the
error recorded (exit code 4). Read-only API use. No orders.
"""
import csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date

WS = "/home/hatch/workspace/trading"
ROOT = f"{WS}/data/sapta_vol"
MANIFEST = f"{WS}/sapta_fetch_manifest.json"
ENV_PATH = f"{WS}/upstox_refresh/.env"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
NAMES = ['APLAPOLLO', 'ASHOKLEY', 'AUBANK', 'AUROPHARMA', 'BANKINDIA', 'BHARATFORG', 'BIOCON', 'BPCL', 'CGPOWER', 'DLF', 'FORTIS', 'GAIL', 'GODFRYPHLP', 'HAVELLS', 'INDIANB', 'IOC', 'JINDALSTEL', 'LODHA', 'MARICO', 'MFSL', 'MOTHERSON', 'ONGC', 'PATANJALI', 'PETRONET', 'PHOENIXLTD', 'SBICARD', 'TATACONSUM', 'UNOMINDA', 'VBL', 'VOLTAS', 'YESBANK', 'ZYDUSLIFE']


class RateLimited(Exception):
    pass


def load_token():
    for line in open(ENV_PATH):
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("UPSTOX_ACCESS_TOKEN not found in .env")


TOKEN = load_token()


def call(path):
    """One attempt, no retries. 429 -> RateLimited (hard stop)."""
    url = "https://api.upstox.com" + path
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": UA,
        "Authorization": f"Bearer {TOKEN}",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"429 on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def candles(payload):
    rows = (payload.get("data") or {}).get("candles") or []
    out = []
    for r in rows:
        ts = str(r[0]).replace("T", " ")[:19] + "+05:30"
        out.append([ts, r[1], r[2], r[3], r[4], r[5]])
    return out


def months():
    out, y, m = [], 2025, 1
    while (y, m) <= (2026, 11):
        frm = date(y, m, 1)
        nxt = date(y + (m == 12), (m % 12) + 1, 1)
        to = min(nxt.fromordinal(nxt.toordinal() - 1), date(2026, 11, 13))
        out.append((f"{y}-{m:02d}", frm.isoformat(), to.isoformat()))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def load_manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST))
    return {"symbols": {}, "status": "running"}


def save_manifest(man):
    tmp = MANIFEST + ".tmp"
    json.dump(man, open(tmp, "w"), indent=1)
    os.replace(tmp, MANIFEST)


def write_csv_atomic(path, header, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def probe():
    uni = {r["symbol"]: r["instrument_key"]
           for r in csv.DictReader(open(f"{WS}/universe_daily/universe.csv"))}
    enc = urllib.parse.quote(uni["RELIANCE"], safe="")
    payload = call(f"/v3/historical-candle/{enc}/minutes/5/2025-01-31/2025-01-01")
    rows = candles(payload)
    vols = [r[5] for r in rows]
    print(f"PROBE RELIANCE 2025-01: {len(rows)} bars")
    if rows:
        print("first:", rows[-1])   # API returns newest first
        print("last:", rows[0])
        print(f"volume: min={min(vols)} max={max(vols)} "
              f"zero_bars={sum(1 for v in vols if not v)} "
              f"none_bars={sum(1 for v in vols if v is None)}")
    return 0


def main():
    if "--probe" in sys.argv:
        return probe()
    uni = {r["symbol"]: r["instrument_key"]
           for r in csv.DictReader(open(f"{WS}/universe_daily/universe.csv"))}
    man = load_manifest()
    man["status"] = "running"
    save_manifest(man)
    chunks = months()
    try:
        for sym in NAMES:
            key = uni[sym]
            enc = urllib.parse.quote(key, safe="")
            d = f"{ROOT}/{sym}"
            os.makedirs(d, exist_ok=True)
            rec = man["symbols"].setdefault(sym, {"chunks_done": []})
            bars = {}
            spath = f"{d}/spot_5m_vol.csv"
            if os.path.exists(spath):
                for r in csv.DictReader(open(spath)):
                    bars[r["timestamp"]] = [r["timestamp"], r["open"], r["high"],
                                            r["low"], r["close"], r["volume"]]
            for label, frm, to in chunks:
                if label in rec["chunks_done"]:
                    continue
                payload = call(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}")
                rows = candles(payload)
                for ts, o, h, l, c, v in rows:
                    bars[ts] = [ts, o, h, l, c, v]
                write_csv_atomic(spath,
                                 ["timestamp", "open", "high", "low", "close", "volume"],
                                 [bars[k] for k in sorted(bars)])
                rec["chunks_done"].append(label)
                rec["bars_5m"] = len(bars)
                if bars:
                    rec["first_5m"] = min(bars)[:10]
                    rec["last_5m"] = max(bars)[:10]
                save_manifest(man)
                print(f"{sym}: chunk {label} +{len(rows)} bars (total {len(bars)})",
                      flush=True)
                time.sleep(0.35)
            rec["status"] = "done"
            save_manifest(man)
    except RateLimited as e:
        man["status"] = "RATE_LIMITED"
        man["rate_limited_on"] = str(e)
        save_manifest(man)
        print(f"HARD STOP — {e}; manifest checkpointed.", flush=True)
        return 3
    except Exception as e:
        man["status"] = "ERROR"
        man["error"] = str(e)
        save_manifest(man)
        print(f"STOP — {e}; manifest checkpointed.", flush=True)
        return 4
    man["status"] = "complete"
    save_manifest(man)
    print("FETCH COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
