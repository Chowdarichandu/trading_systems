#!/usr/bin/env python3
"""WIDE-100 — STAGE 2 DATA BUILD. Fetches 5-minute bars (monthly
chunks, 2025-01-01 -> 2026-11-13) + daily bars (2024-10-01 ->
2026-11-13) for the 75 new WIDE-100 names into
data/wide100/<SYM>/{spot_5m.csv, spot_daily.csv} — the frozen
stores' exact layout. Route: the programme's established Upstox
connector route (surrogate auth, browser User-Agent), instrument
keys from universe_daily/universe.csv.

Checkpointing: wide100_fetch_manifest.json is rewritten after
every chunk; completed chunks are skipped on re-run (resumable).
HTTP 429 = HARD STOP for the attempt: the run stops at once with
the manifest marked RATE_LIMITED. No retries. Read-only API use.
No orders. No secrets stored (auth rides the surrogate exchange).
"""
import csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date

WS = "/home/hatch/workspace/trading"
ROOT = f"{WS}/data/wide100"
MANIFEST = f"{WS}/wide100_fetch_manifest.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response  # noqa: E402
import pandas as pd  # noqa: E402


class RateLimited(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(path):
    """One attempt, no retries. 429 -> RateLimited (hard stop)."""
    url = "https://api.upstox.com" + path
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": UA})
    add_surrogate_to_request(req, "custom.upstox",
                             allowed_hosts=["api.upstox.com"])
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=90) as resp:
            return read_json_response(resp)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"429 on {path}")
        raise


def candles(payload):
    rows = (payload.get("data") or {}).get("candles") or []
    out = []
    for r in rows:
        # "2025-01-01T09:15:00+05:30" -> "2025-01-01 09:15:00+05:30"
        ts = str(r[0]).replace("T", " ")[:19] + "+05:30"
        out.append([ts, r[1], r[2], r[3], r[4]])
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


def main():
    uni = {r["symbol"]: r["instrument_key"]
           for r in csv.DictReader(open(f"{WS}/universe_daily/universe.csv"))}
    stage1 = json.load(open(f"{WS}/wide100_universe_stage1.json"))
    syms = [r["sym"] for r in stage1["top75"]]
    man = load_manifest()
    man["status"] = "running"
    save_manifest(man)
    chunks = months()
    try:
        for sym in syms:
            key = uni[sym]
            enc = urllib.parse.quote(key, safe="")
            d = f"{ROOT}/{sym}"
            os.makedirs(d, exist_ok=True)
            rec = man["symbols"].setdefault(sym, {"chunks_done": []})
            # ---- daily (single range call), once
            if not rec.get("daily_done"):
                try:
                    payload = call(f"/v3/historical-candle/{enc}/days/1/2026-11-13/2024-10-01")
                    rows = candles(payload)
                except RateLimited:
                    raise
                except Exception:
                    payload = call(f"/v2/historical-candle/{enc}/day/2026-11-13/2024-10-01")
                    rows = candles(payload)
                daily = {}
                for ts, o, h, l, c in rows:
                    daily[ts[:10]] = [ts[:10], o, h, l, c]
                write_csv_atomic(f"{d}/spot_daily.csv",
                                 ["date", "open", "high", "low", "close"],
                                 [daily[k] for k in sorted(daily)])
                rec["daily"] = {"rows": len(daily),
                                "first": min(daily) if daily else None,
                                "last": max(daily) if daily else None}
                rec["daily_done"] = True
                save_manifest(man)
                print(f"{sym}: daily {len(daily)} rows "
                      f"{rec['daily']['first']}..{rec['daily']['last']}", flush=True)
                time.sleep(0.35)
            # ---- 5-minute, monthly chunks
            bars = {}
            spath = f"{d}/spot_5m.csv"
            if os.path.exists(spath):
                for r in csv.DictReader(open(spath)):
                    bars[r["timestamp"]] = [r["timestamp"], r["open"], r["high"],
                                            r["low"], r["close"]]
            for label, frm, to in chunks:
                if label in rec["chunks_done"]:
                    continue
                payload = call(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}")
                rows = candles(payload)
                for ts, o, h, l, c in rows:
                    bars[ts] = [ts, o, h, l, c]
                write_csv_atomic(spath, ["timestamp", "open", "high", "low", "close"],
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
    man["status"] = "complete"
    save_manifest(man)
    print("FETCH COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
