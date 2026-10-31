#!/usr/bin/env python3
"""LINE U1 — fetch 5-min bars for the Nifty 500 universe.
Checkpointed: symbols with a non-empty bar file are skipped.
One calendar month per API call (v3 rejects longer spans).
Status: data/u1/fetch_status.json, updated every symbol.
"""
import csv, json, os, sys, time, urllib.parse

sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df

BASE = "/home/hatch/workspace/trading"
OUT = f"{BASE}/data/u1/bars"
STATUS = f"{BASE}/data/u1/fetch_status.json"
CHUNKS = [("2026-08-01", "2026-08-31"),
          ("2026-09-01", "2026-09-30"),
          ("2026-10-01", "2026-10-30")]
SLEEP = 0.3


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(f"{BASE}/data/u1/nifty500list_raw.csv")))
    status = {}
    if os.path.exists(STATUS):
        status = json.load(open(STATUS))
    for i, r in enumerate(rows):
        sym = r["Symbol"]
        key = "NSE_EQ|" + r["ISIN Code"].strip()
        path = f"{OUT}/{sym}.csv"
        if os.path.exists(path) and os.path.getsize(path) > 0:
            if sym not in status:
                try:
                    with open(path) as f:
                        n = sum(1 for _ in f) - 1
                    status[sym] = {"rows": n, "err": None}
                except Exception as e:
                    status[sym] = {"rows": 0, "err": str(e)[:120]}
            continue
        enc = urllib.parse.quote(key, safe="")
        all_rows, err = [], None
        for frm, to in CHUNKS:
            try:
                df = candles_df(call(
                    f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}"))
                for _, x in df.iterrows():
                    all_rows.append((str(x["timestamp"])[:19], float(x["open"]),
                                     float(x["high"]), float(x["low"]),
                                     float(x["close"])))
            except Exception as e:
                err = str(e)[:160]
                break
            time.sleep(SLEEP)
        if err:
            status[sym] = {"rows": 0, "err": err}
            print(f"[{i+1}/{len(rows)}] {sym} FAIL {err}", flush=True)
            continue
        all_rows.sort()
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "open", "high", "low", "close"])
            w.writerows(all_rows)
        status[sym] = {"rows": len(all_rows), "err": None}
        if (i + 1) % 25 == 0 or i + 1 == len(rows):
            done = sum(1 for v in status.values() if v["err"] is None)
            print(f"[{i+1}/{len(rows)}] done-ok={done} last={sym} rows={len(all_rows)}",
                  flush=True)
        json.dump(status, open(STATUS, "w"), indent=1)
        time.sleep(SLEEP)
    json.dump(status, open(STATUS, "w"), indent=1)
    ok = sum(1 for v in status.values() if v["err"] is None)
    print(f"DONE fetch: ok={ok} failed={len(status) - ok} of {len(status)}",
          flush=True)


if __name__ == "__main__":
    main()
