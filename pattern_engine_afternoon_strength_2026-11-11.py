#!/usr/bin/env python3
"""
ENGINE 1 — AFTERNOON STRENGTH -> NEXT-DAY pattern study (2026-11-11).
Owner's observation: market rises from the afternoon onwards and closes strong
-> next session gaps up / continues. Fresh instances: Fri 2026-11-06 (both
indices closed AT highs) -> Mon 11-09 gap up; Mon 11-09 Bank ran into the close
-> Wed 11-11 gap up (Tue 11-10 holiday).

RESEARCH ONLY. Nothing armed, no trading rules change, no cron touched.

STEP 0 verifies the instances against Upstox daily candles (+ 5-min for the
afternoon measures on Nov 6 / Nov 9). On HTTP 429: hard-stop ALL fetching and
report; the stored-data study still runs.

STUDY DATA: daily2leg/spot.json — 5-min spot bars [time,O,H,L,C], both indices.
Windows (signal days): Jan-Oct 2026 (primary) and Jan-Oct 2025 (out-of-sample
check). Next-day outcomes use the next trading day in the store.

PRE-REGISTERED BUCKETS (fixed here, before any outcome is computed):
  B_CS80   : closing strength CS% = (C-L)/(H-L)*100 >= 80
  B_AFT30  : afternoon run (close - 13:00 level) >= +0.30% of the 13:00 level
  B_TOPQ   : afternoon run as % of day range in the window's top quartile
             (threshold is in-sample by construction — flagged wherever used)
  B_COMBO  : B_CS80 AND B_AFT30
  M_CS20   : CS <= 20                      (mirror / weakness)
  M_AFT30  : afternoon run <= -0.30%       (mirror / weakness)
Measures knowable at the close: afternoon run (pts, % of 13:00 level, % of day
range), post-13:00 up-bar share, CS%, distance of close from day high.
Outcomes (next trading day): gap pts/%, open->close %, full-day change %,
next-day higher high (Y/N).
Controls: mirror buckets, Jan-May vs Jun-Oct halves (2026), 2025 window.
"""

import json, math, os, sys, urllib.parse, urllib.request, urllib.error
from statistics import mean, median

WS = os.path.expanduser("~/workspace/trading")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"

# ---------------- STEP 0: Upstox verification ----------------

class HardStop(Exception):
    pass

def load_token():
    env = {}
    with open(os.path.join(WS, "upstox_refresh/.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env["UPSTOX_ACCESS_TOKEN"]

def api_get(token, path):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": UA,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise HardStop("HTTP 429 from Upstox — fetch hard-stopped per rule")
        raise

def fetch_daily(token, key, to_d, from_d):
    enc = urllib.parse.quote(key, safe="")
    p = api_get(token, f"/v3/historical-candle/{enc}/days/1/{to_d}/{from_d}")
    out = {}
    for c in p["data"]["candles"]:
        out[c[0][:10]] = {"open": c[1], "high": c[2], "low": c[3], "close": c[4]}
    return out

def fetch_5min(token, key, to_d, from_d):
    enc = urllib.parse.quote(key, safe="")
    p = api_get(token, f"/v3/historical-candle/{enc}/minutes/5/{to_d}/{from_d}")
    days = {}
    for c in p["data"]["candles"]:
        d, t = c[0][:10], c[0][11:16]
        days.setdefault(d, []).append([t, c[1], c[2], c[3], c[4]])
    for d in days:
        days[d].sort(key=lambda b: b[0])
    return days

# ---------------- study machinery ----------------

def day_measures(bars):
    """bars: [[time,O,H,L,C],...] sorted. Returns dict or None if unusable."""
    if len(bars) < 70:
        return None
    O = bars[0][1]; C = bars[-1][4]
    H = max(b[2] for b in bars); L = min(b[3] for b in bars)
    rng = H - L
    if rng <= 0:
        return None
    by_time = {b[0]: b for b in bars}
    if "12:55" in by_time:
        lvl1300 = by_time["12:55"][4]
    elif "13:00" in by_time:
        lvl1300 = by_time["13:00"][1]
    else:
        return None
    aft = [b for b in bars if b[0] >= "13:00"]
    if len(aft) < 25:
        return None
    up_share = sum(1 for b in aft if b[4] > b[1]) / len(aft)
    aft_run = C - lvl1300
    return {
        "open": O, "high": H, "low": L, "close": C, "range": rng,
        "lvl1300": lvl1300, "aft_run": aft_run,
        "aft_run_pct": aft_run / lvl1300 * 100.0,
        "aft_run_range_pct": aft_run / rng * 100.0,
        "aft_up_share": up_share,
        "cs": (C - L) / rng * 100.0,
        "dist_high_range_pct": (H - C) / rng * 100.0,
        "close_at_high": (H - C) <= 0.05,
    }

def build_rows(store, index, win_start, win_end):
    days = sorted(store[index].keys())
    rows, excluded = [], 0
    for i, d in enumerate(days):
        if not (win_start <= d <= win_end):
            continue
        m = day_measures(store[index][d])
        if m is None:
            excluded += 1
            continue
        row = {"index": index, "date": d, **m}
        if i + 1 < len(days):
            nd = days[i + 1]
            nm = day_measures(store[index][nd])
            if nm is not None:
                row["next_date"] = nd
                row["gap"] = nm["open"] - m["close"]
                row["gap_pct"] = (nm["open"] - m["close"]) / m["close"] * 100.0
                row["next_oc_pct"] = (nm["close"] - nm["open"]) / nm["open"] * 100.0
                row["next_full_pct"] = (nm["close"] - m["close"]) / m["close"] * 100.0
                row["next_higher_high"] = 1 if nm["high"] > m["high"] else 0
        rows.append(row)
    return rows, excluded

def stats(rows):
    if not rows:
        return {"n": 0}
    g = [r["gap_pct"] for r in rows]
    return {
        "n": len(rows),
        "mean_gap_pts": round(mean(r["gap"] for r in rows), 2),
        "median_gap_pts": round(median(r["gap"] for r in rows), 2),
        "mean_gap_pct": round(mean(g), 3),
        "median_gap_pct": round(median(g), 3),
        "se_gap_pct": round(( (sum((x-mean(g))**2 for x in g)/ (len(g)-1) )**0.5 / math.sqrt(len(g)) ), 3) if len(g) > 1 else None,
        "pct_gap_up": round(100.0 * sum(1 for r in rows if r["gap"] > 0) / len(rows), 1),
        "pct_next_close_up": round(100.0 * sum(1 for r in rows if r["next_full_pct"] > 0) / len(rows), 1),
        "mean_next_full_pct": round(mean(r["next_full_pct"] for r in rows), 3),
        "mean_next_oc_pct": round(mean(r["next_oc_pct"] for r in rows), 3),
        "pct_next_higher_high": round(100.0 * sum(r["next_higher_high"] for r in rows) / len(rows), 1),
    }

def bucket_rows(rows, name, topq_threshold=None):
    if name == "B_CS80":
        return [r for r in rows if r["cs"] >= 80]
    if name == "B_AFT30":
        return [r for r in rows if r["aft_run_pct"] >= 0.30]
    if name == "B_TOPQ":
        return [r for r in rows if r["aft_run_range_pct"] >= topq_threshold]
    if name == "B_COMBO":
        return [r for r in rows if r["cs"] >= 80 and r["aft_run_pct"] >= 0.30]
    if name == "M_CS20":
        return [r for r in rows if r["cs"] <= 20]
    if name == "M_AFT30":
        return [r for r in rows if r["aft_run_pct"] <= -0.30]
    raise ValueError(name)

def pctile(vals, q):
    s = sorted(vals)
    k = (len(s) - 1) * q
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)

BUCKETS = ["B_CS80", "B_AFT30", "B_TOPQ", "B_COMBO", "M_CS20", "M_AFT30"]

def analyse(rows):
    scored = [r for r in rows if "gap_pct" in r]
    topq = pctile([r["aft_run_range_pct"] for r in rows], 0.75)
    out = {"n_signal_days": len(rows), "n_scored": len(scored),
           "topq_threshold_aft_run_range_pct": round(topq, 2),
           "base": stats(scored), "buckets": {}}
    for b in BUCKETS:
        out["buckets"][b] = stats(bucket_rows(scored, b, topq))
    # halves within the window's own year (Jan-May vs Jun-Oct)
    yr = rows[0]["date"][:4] if rows else "2026"
    h1 = [r for r in scored if r["date"] <= f"{yr}-05-31"]
    h2 = [r for r in scored if r["date"] >= f"{yr}-06-01"]
    out["halves"] = {}
    for b in BUCKETS:
        out["halves"][b] = {
            "H1_JanMay": stats(bucket_rows(h1, b, topq)),
            "H2_JunOct": stats(bucket_rows(h2, b, topq)),
        }
    out["halves"]["base"] = {"H1_JanMay": stats(h1), "H2_JunOct": stats(h2)}
    return out

def main():
    result = {"step0": {}, "study": {}, "nov_instances": {}}
    store = json.load(open(os.path.join(WS, "daily2leg/spot.json")))

    # ---- STEP 0 ----
    try:
        token = load_token()
        keys = {"BANKNIFTY": "NSE_INDEX|Nifty Bank", "NIFTY": "NSE_INDEX|Nifty 50"}
        daily, five = {}, {}
        for idx, key in keys.items():
            daily[idx] = fetch_daily(token, key, "2026-11-11", "2026-11-05")
            five[idx] = fetch_5min(token, key, "2026-11-11", "2026-11-06")
        result["step0"]["daily_candles"] = daily
        for idx in keys:
            d06, d09, d11 = daily[idx].get("2026-11-06"), daily[idx].get("2026-11-09"), daily[idx].get("2026-11-11")
            inst = {}
            if d06 and d09:
                inst["fri06_close"] = d06["close"]
                inst["mon09_open"] = d09["open"]
                inst["gap_fri_to_mon_pts"] = round(d09["open"] - d06["close"], 2)
                inst["gap_fri_to_mon_pct"] = round((d09["open"] - d06["close"]) / d06["close"] * 100, 3)
                inst["fri06_close_at_high"] = abs(d06["close"] - d06["high"]) <= 0.05
            if d09 and d11:
                inst["mon09_close"] = d09["close"]
                inst["wed11_open"] = d11["open"]
                inst["gap_mon_to_wed_pts"] = round(d11["open"] - d09["close"], 2)
                inst["gap_mon_to_wed_pct"] = round((d11["open"] - d09["close"]) / d09["close"] * 100, 3)
            # afternoon measures for Nov 6 and Nov 9 from 5-min bars
            for dt, tag in (("2026-11-06", "nov06"), ("2026-11-09", "nov09")):
                bars = five[idx].get(dt)
                if bars:
                    m = day_measures(bars)
                    if m:
                        inst[tag] = {k: (round(v, 2) if isinstance(v, float) else v)
                                     for k, v in m.items()}
            result["nov_instances"][idx] = inst
        result["step0"]["status"] = "OK"
    except HardStop as e:
        result["step0"]["status"] = f"HARD STOP — {e}"
    except Exception as e:
        result["step0"]["status"] = f"FAILED — {type(e).__name__}: {e}"

    # ---- STUDY ----
    windows = {"2026": ("2026-01-01", "2026-10-31"), "2025": ("2025-01-01", "2025-10-31")}
    all_rows = []
    for idx in ("BANKNIFTY", "NIFTY"):
        result["study"][idx] = {}
        for wname, (ws, we) in windows.items():
            rows, excl = build_rows(store, idx, ws, we)
            a = analyse(rows)
            a["n_excluded_unusable"] = excl
            result["study"][idx][wname] = a
            for r in rows:
                r2 = dict(r); r2["window"] = wname
                all_rows.append(r2)
        # Bank/Nifty Sep-Oct 2026 CS>=80 sub-check (reconciliation vs 24-day study)
        rows26, _ = build_rows(store, idx, "2026-01-01", "2026-10-31")
        sub = [r for r in rows26 if "2026-09-30" <= r["date"] <= "2026-10-29" and "gap_pct" in r]
        result["study"][idx]["sep_oct_2026_cs80_subcheck"] = {
            "all_days": stats(sub),
            "cs80": stats([r for r in sub if r["cs"] >= 80]),
            "strict_bullish_days": [r["date"] for r in sub if r["cs"] >= 80],
        }
        result["study"][idx]["store_days_total"] = len(store[idx])

    # ---- write outputs ----
    with open(os.path.join(WS, "pattern_engine_afternoon_strength_2026-11-11_results.json"), "w") as f:
        json.dump(result, f, indent=1)
    import csv
    cols = ["window", "index", "date", "open", "high", "low", "close", "lvl1300",
            "aft_run", "aft_run_pct", "aft_run_range_pct", "aft_up_share", "cs",
            "dist_high_range_pct", "close_at_high", "next_date", "gap", "gap_pct",
            "next_oc_pct", "next_full_pct", "next_higher_high"]
    with open(os.path.join(WS, "pattern_engine_afternoon_strength_2026-11-11_days.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in all_rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print(json.dumps({"step0_status": result["step0"]["status"],
                      "nov": result["nov_instances"]}, indent=1))
    for idx in ("BANKNIFTY", "NIFTY"):
        for wname in ("2026", "2025"):
            a = result["study"][idx][wname]
            print(idx, wname, "n_scored:", a["n_scored"], "base:", a["base"])
            for b in BUCKETS:
                print("   ", b, a["buckets"][b])

if __name__ == "__main__":
    main()
