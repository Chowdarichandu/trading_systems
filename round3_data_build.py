#!/usr/bin/env python3
"""ROUND 3 DATA BUILD (2026-11-13 night) — NSE F&O participant-wise OI.

Source: NSE's own archive files (no mirror):
  https://archives.nseindia.com/content/nsccl/fao_participant_oi_DDMMYYYY.csv
Each file is one session's participant-wise open interest (contracts),
published on that session's EVENING (timing audit in the report).
Downloads every calendar date 2025-09-01 .. 2026-11-13, keeps the ones
that parse as valid participant files (real sessions), validates the
TOTAL row against the participant sum, and assembles
round3_history/participant_daily.csv.

FII/DII CASH flows: NSE's api/fiidiiTradeReact returns only the latest
session (probed 2026-11-13: single day 13-Nov-2026) — no Jan-Oct daily
history is obtainable from NSE; cash is dropped from this round and the
surface is the F&O participant OI file (documented in the report).

Paper only, real money Rs0. No running book touched.
"""
import csv, io, json, time
import urllib.request, urllib.error
from datetime import date, timedelta
from pathlib import Path

TR = Path.home() / "workspace/trading"
OUT = TR / "round3_history"
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
URL = ("https://archives.nseindia.com/content/nsccl/"
       "fao_participant_oi_{}.csv")

COLS = ["future_index_long", "future_index_short", "future_stock_long",
        "future_stock_short", "option_index_call_long",
        "option_index_put_long", "option_index_call_short",
        "option_index_put_short", "option_stock_call_long",
        "option_stock_put_long", "option_stock_call_short",
        "option_stock_put_short", "total_long", "total_short"]
PARTS = ["Client", "DII", "FII", "Pro"]


def fetch(dstr):
    fn = RAW / f"fao_participant_oi_{dstr}.csv"
    if fn.exists() and fn.stat().st_size > 200:
        return fn.read_text()
    req = urllib.request.Request(URL.format(dstr),
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else (_ for _ in ()).throw(e)
    except Exception:
        return None
    if "Participant wise Open Interest" not in body:
        return None
    fn.write_text(body)
    return body


def parse(body):
    rows = {}
    rd = csv.reader(io.StringIO(body))
    lines = [r for r in rd if r and r[0].strip()]
    hdr_date = lines[0][0] if lines else ""
    for r in lines[2:]:
        name = r[0].strip()
        if name in PARTS + ["TOTAL"]:
            vals = [int(float(x.replace(",", "").strip() or 0))
                    for x in r[1:15]]
            rows[name] = dict(zip(COLS, vals))
    return hdr_date, rows


def main():
    d = date(2025, 9, 1)
    end = date(2026, 11, 13)
    manifest, series = [], []
    while d <= end:
        dstr = d.strftime("%d%m%Y")
        iso = d.isoformat()
        body = fetch(dstr)
        if body is None:
            manifest.append(dict(date=iso, status="no_file"))
            d += timedelta(days=1)
            continue
        hdr, rows = parse(body)
        ok = all(p in rows for p in PARTS) and "TOTAL" in rows
        valid = False
        if ok:
            s = sum(rows[p]["future_index_long"] for p in PARTS)
            valid = (s == rows["TOTAL"]["future_index_long"])
        manifest.append(dict(date=iso, status="ok" if valid else "invalid",
                             header=hdr))
        if valid:
            fii = rows["FII"]
            fil, fis = fii["future_index_long"], fii["future_index_short"]
            cl, cs = (fii["option_index_call_long"],
                      fii["option_index_call_short"])
            pl, ps = (fii["option_index_put_long"],
                      fii["option_index_put_short"])
            series.append(dict(
                date=iso,
                fii_fut_long=fil, fii_fut_short=fis,
                fii_fut_net=fil - fis,
                fii_lr=round(fil / (fil + fis), 6) if fil + fis else None,
                fii_call_long=cl, fii_call_short=cs,
                fii_put_long=pl, fii_put_short=ps,
                fii_opt_net=(cl - cs) - (pl - ps),
                fii_opt_total=cl + cs + pl + ps,
                dii_fut_net=(rows["DII"]["future_index_long"]
                             - rows["DII"]["future_index_short"]),
                pro_fut_net=(rows["Pro"]["future_index_long"]
                             - rows["Pro"]["future_index_short"]),
                client_fut_net=(rows["Client"]["future_index_long"]
                                - rows["Client"]["future_index_short"]),
                total_fut_idx_oi=rows["TOTAL"]["future_index_long"]
                + rows["TOTAL"]["future_index_short"]))
        d += timedelta(days=1)
        time.sleep(0.05)

    with open(OUT / "participant_daily.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(series[0].keys()))
        w.writeheader()
        w.writerows(series)
    with open(OUT / "fetch_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "status", "header"])
        w.writeheader()
        w.writerows(manifest)
    gate = [r for r in series if "2026-01-01" <= r["date"] <= "2026-10-31"]
    nov = [r for r in series if r["date"] >= "2026-11-01"]
    summary = dict(rows=len(series), first=series[0]["date"],
                   last=series[-1]["date"], gate_window_rows=len(gate),
                   november_rows=[r["date"] for r in nov],
                   invalid=[m["date"] for m in manifest
                            if m["status"] == "invalid"])
    (OUT / "build_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
