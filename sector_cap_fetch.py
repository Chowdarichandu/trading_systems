#!/usr/bin/env python3
"""SECTOR-CAP RETEST — data build for the two capped-set names missing
from data/wide100 (AMBUJACEM, ASIANPAINT). Same route, layout and
checkpoint discipline as wide100_fetch.py: Upstox historical candles
via the programme's surrogate route (browser User-Agent), 5-minute
bars in monthly chunks 2025-01-01 -> 2026-11-13 + daily bars
2024-10-01 -> 2026-11-13, written to data/wide100/<SYM>/ in the
frozen layout. Own manifest: sector_cap_fetch_manifest.json,
rewritten after every chunk (resumable). HTTP 429 = HARD STOP for
the attempt. Read-only API use. No orders. No secrets stored."""
import csv, json, os, sys, time
sys.path.insert(0, "/home/hatch/workspace/trading")
import wide100_fetch as F

WS = F.WS
ROOT = F.ROOT
MANIFEST = f"{WS}/sector_cap_fetch_manifest.json"
SYMS = ["AMBUJACEM", "ASIANPAINT"]


def load_manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST))
    return {"symbols": {}, "status": "running"}


def save_manifest(man):
    tmp = MANIFEST + ".tmp"
    json.dump(man, open(tmp, "w"), indent=1)
    os.replace(tmp, MANIFEST)


def main():
    uni = {r["symbol"]: r["instrument_key"]
           for r in csv.DictReader(open(f"{WS}/universe_daily/universe.csv"))}
    man = load_manifest()
    man["status"] = "running"
    save_manifest(man)
    chunks = F.months()
    try:
        for sym in SYMS:
            key = uni[sym]
            enc = F.urllib.parse.quote(key, safe="")
            d = f"{ROOT}/{sym}"
            os.makedirs(d, exist_ok=True)
            rec = man["symbols"].setdefault(sym, {"chunks_done": []})
            if not rec.get("daily_done"):
                try:
                    payload = F.call(f"/v3/historical-candle/{enc}/days/1/2026-11-13/2024-10-01")
                    rows = F.candles(payload)
                except F.RateLimited:
                    raise
                except Exception:
                    payload = F.call(f"/v2/historical-candle/{enc}/day/2026-11-13/2024-10-01")
                    rows = F.candles(payload)
                daily = {}
                for ts, o, h, l, c in rows:
                    daily[ts[:10]] = [ts[:10], o, h, l, c]
                F.write_csv_atomic(f"{d}/spot_daily.csv",
                                   ["date", "open", "high", "low", "close"],
                                   [daily[k] for k in sorted(daily)])
                rec["daily"] = {"rows": len(daily),
                                "first": min(daily) if daily else None,
                                "last": max(daily) if daily else None}
                rec["daily_done"] = True
                save_manifest(man)
                print(f"{sym}: daily {len(daily)} rows "
                      f"{rec['daily']['first']}..{rec['daily']['last']}",
                      flush=True)
                time.sleep(0.35)
            bars = {}
            spath = f"{d}/spot_5m.csv"
            if os.path.exists(spath):
                for r in csv.DictReader(open(spath)):
                    bars[r["timestamp"]] = [r["timestamp"], r["open"],
                                            r["high"], r["low"], r["close"]]
            for label, frm, to in chunks:
                if label in rec["chunks_done"]:
                    continue
                payload = F.call(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}")
                rows = F.candles(payload)
                for ts, o, h, l, c in rows:
                    bars[ts] = [ts, o, h, l, c]
                F.write_csv_atomic(spath,
                                   ["timestamp", "open", "high", "low", "close"],
                                   [bars[k] for k in sorted(bars)])
                rec["chunks_done"].append(label)
                rec["bars_5m"] = len(bars)
                if bars:
                    rec["first_5m"] = min(bars)[:10]
                    rec["last_5m"] = max(bars)[:10]
                save_manifest(man)
                print(f"{sym}: chunk {label} +{len(rows)} bars "
                      f"(total {len(bars)})", flush=True)
                time.sleep(0.35)
            rec["status"] = "done"
            save_manifest(man)
    except F.RateLimited as e:
        man["status"] = "RATE_LIMITED"
        man["rate_limited_on"] = str(e)
        save_manifest(man)
        print(f"HARD STOP — {e}; manifest checkpointed.", flush=True)
        return 3
    man["status"] = "complete"
    save_manifest(man)
    print("FETCH COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
