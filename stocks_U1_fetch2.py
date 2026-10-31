#!/usr/bin/env python3
"""LINE U1 - fetch 5-min bars for the Nifty 500 universe (threaded).
Checkpointed: symbols with a non-empty bar file are skipped.
One calendar month per API call (v3 rejects longer spans).
Status: data/u1/fetch_status.json, rewritten periodically.
"""
import csv, json, os, sys, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df

BASE = "/home/hatch/workspace/trading"
OUT = f"{BASE}/data/u1/bars"
STATUS = f"{BASE}/data/u1/fetch_status.json"
CHUNKS = [("2026-08-01", "2026-08-31"),
          ("2026-09-01", "2026-09-30"),
          ("2026-10-01", "2026-10-30")]
WORKERS = 5


def fetch_one(r):
    sym = r["Symbol"]
    key = "NSE_EQ|" + r["ISIN Code"].strip()
    path = f"{OUT}/{sym}.csv"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path) as f:
            return sym, {"rows": sum(1 for _ in f) - 1, "err": None}
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
        time.sleep(0.15)
    if err:
        return sym, {"rows": 0, "err": err}
    all_rows.sort()
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close"])
        w.writerows(all_rows)
    os.replace(tmp, path)
    return sym, {"rows": len(all_rows), "err": None}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(f"{BASE}/data/u1/nifty500list_raw.csv")))
    status = {}
    if os.path.exists(STATUS):
        status = json.load(open(STATUS))
    todo = [r for r in rows
            if not (os.path.exists(f"{OUT}/{r['Symbol']}.csv")
                    and os.path.getsize(f"{OUT}/{r['Symbol']}.csv") > 0)]
    print(f"total={len(rows)} todo={len(todo)}", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for sym, st in ex.map(fetch_one, rows):
            status[sym] = st
            done += 1
            if done % 50 == 0 or done == len(rows):
                ok = sum(1 for v in status.values() if v["err"] is None)
                print(f"[{done}/{len(rows)}] ok={ok}", flush=True)
                json.dump(status, open(STATUS, "w"), indent=1)
    json.dump(status, open(STATUS, "w"), indent=1)
    ok = sum(1 for v in status.values() if v["err"] is None)
    print(f"DONE fetch: ok={ok} failed={len(status) - ok} of {len(status)}",
          flush=True)


if __name__ == "__main__":
    main()
