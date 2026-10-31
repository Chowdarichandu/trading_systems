"""LINE 7 STEP 1 — 1-minute feasibility probe for STOCKS via Upstox v3.
Samples: HDFCBANK, GLENMARK, OBEROIRLTY (home) + RELIANCE, TCS (ext).
Tests: (a) October 2026 full month in ONE request, (b) Feb 2026 week
2026-02-02..06 in ONE request. If a one-shot request errors or looks
truncated, falls back to weekly chunks to characterise the limit.
Read-only, paper only. Writes line7_feasibility_raw.json.
"""
import json, os, sys, time, urllib.parse
sys.path.insert(0, "/home/hatch/workspace/trading")
from fetch_upstox_via_connector import call, candles_df
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading")
KH = json.load(open(f"{BASE}/data/progressive/keys.json"))
KE = json.load(open(f"{BASE}/data/progressive_ext/keys_ext.json"))
SAMPLES = {"HDFCBANK": KH["HDFCBANK"], "GLENMARK": KH["GLENMARK"],
           "OBEROIRLTY": KH["OBEROIRLTY"], "RELIANCE": KE["RELIANCE"],
           "TCS": KE["TCS"]}
OCT_DAYS_CACHE = ['2026-10-01', '2026-10-05', '2026-10-06', '2026-10-07',
                  '2026-10-08', '2026-10-09', '2026-10-12', '2026-10-13',
                  '2026-10-14', '2026-10-15', '2026-10-16', '2026-10-19',
                  '2026-10-21', '2026-10-22', '2026-10-23', '2026-10-26',
                  '2026-10-27', '2026-10-28']
FEB_DAYS = ['2026-02-02', '2026-02-03', '2026-02-04', '2026-02-05', '2026-02-06']


def fetch(key, to_d, from_d):
    enc = urllib.parse.quote(key, safe="")
    p = call(f"/v3/historical-candle/{enc}/minutes/1/{to_d}/{from_d}")
    return candles_df(p)


def per_day(df):
    if df.empty:
        return {}
    d = df.copy()
    d["day"] = d["timestamp"].dt.strftime("%Y-%m-%d")
    return {k: int(v) for k, v in d.groupby("day").size().items()}


def probe(key, to_d, from_d, label):
    out = {"label": label, "to": to_d, "from": from_d}
    try:
        df = fetch(key, to_d, from_d)
        out["bars"] = int(len(df))
        out["per_day"] = per_day(df)
        out["error"] = None
    except Exception as e:
        out["bars"] = 0
        out["per_day"] = {}
        out["error"] = str(e)[:400]
    return out


def main():
    res = {}
    for sym, key in SAMPLES.items():
        print(f"=== {sym} ===", flush=True)
        r = {"oct_oneshot": probe(key, "2026-10-31", "2026-10-01", "oct_oneshot")}
        print(f"  Oct one-shot: bars={r['oct_oneshot']['bars']} err={r['oct_oneshot']['error']}", flush=True)
        time.sleep(0.4)
        r["feb_oneshot"] = probe(key, "2026-02-06", "2026-02-02", "feb_oneshot")
        print(f"  Feb one-shot: bars={r['feb_oneshot']['bars']} err={r['feb_oneshot']['error']}", flush=True)
        time.sleep(0.4)
        # If October one-shot failed/partial (< 18 days), characterise with weekly chunks
        got_days = set(r["oct_oneshot"]["per_day"].keys())
        if r["oct_oneshot"]["error"] or len(got_days) < len(OCT_DAYS_CACHE):
            r["oct_weekly"] = {}
            for wk, (a, b) in enumerate([("2026-10-01", "2026-10-07"), ("2026-10-08", "2026-10-14"),
                                          ("2026-10-15", "2026-10-21"), ("2026-10-22", "2026-10-28"),
                                          ("2026-10-29", "2026-10-31")]):
                pr = probe(key, b, a, f"oct_wk{wk}")
                r["oct_weekly"][f"{a}..{b}"] = pr
                print(f"  Oct wk {a}..{b}: bars={pr['bars']} err={pr['error']}", flush=True)
                time.sleep(0.4)
        res[sym] = r
    res["_expected"] = {"oct_cache_days": OCT_DAYS_CACHE, "feb_days": FEB_DAYS}
    json.dump(res, open(f"{BASE}/line7_feasibility_raw.json", "w"), indent=2)
    print("WROTE line7_feasibility_raw.json", flush=True)


if __name__ == "__main__":
    main()
