#!/usr/bin/env python3
"""ROUND 4 DATA BUILD (2026-11-13 night) — SURFACE A: INTRADAY futures
basis, Bank Nifty. Fetches near-month BANKNIFTY futures 5-minute
candles (Upstox expired-instruments route; the live 2026-11-23
contract via v3) for every trading day 2026-01-01 -> 2026-11-12 and
builds the MORNING-READ dataset:

  basis_open = fut_close(09:15 bar) - spot_close(09:15 bar)  [known 09:20]
  basis_read = fut_close(10:55 bar) - spot_close(10:55 bar)  [known 11:00]
  spot_morning_pct = spot_close(10:55)/spot_open(09:15) - 1
  dbasis_pct      = (basis_read - basis_open)/spot_close(10:55)

Spot: stored series (daily2leg/spot.json + oi_history/spot_nov_bars.json);
Nov 12 spot fetched via v3 (stored series ends Nov 11); Nov 13 was
probed and returns 0 candles tonight (documented data lag) -> the
November lens ends Nov 12, Nov 13 is NC, never estimated.

Resume-safe per-contract caches in round4_history/. On HTTP 429:
HARD STOP, partial state in the manifest, exit 2. Never prints token.
"""
import json, sys, time
import urllib.request, urllib.error
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "round4_history"
OUT.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
FIRST, LAST = "2026-01-01", "2026-11-12"
ALL_EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
           "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
           "2026-09-29", "2026-10-27", "2026-11-23"]

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token


class RateLimited(Exception):
    pass


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return None


def in_force(day):
    for e in ALL_EXP:
        if e >= day:
            return e
    return None


# ---------------- spot ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
nov_bars = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
SPOT = {}
for d, bars in spot_raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
for d, bars in nov_bars.get("BANKNIFTY", {}).items():
    SPOT.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4]) for b in bars})

# November tail: fetch spot 5-min for Nov 12 (+ probe Nov 13) via v3
extra_fn = OUT / "spot_extra.json"
SPOT_EXTRA = json.loads(extra_fn.read_text()) if extra_fn.exists() else {}
ikey = quote("NSE_INDEX|Nifty Bank", safe="")
for day in ("2026-11-12", "2026-11-13"):
    if day in SPOT_EXTRA:
        continue
    body = get(f"{API}/v3/historical-candle/{ikey}/minutes/5/{day}/{day}")
    cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []
          if c[0][:10] == day]
    SPOT_EXTRA[day] = [[c[0][11:16], float(c[1]), float(c[2]),
                        float(c[3]), float(c[4])] for c in cd]
    extra_fn.write_text(json.dumps(SPOT_EXTRA))
    print(f"spot extra {day}: {len(cd)} candles", flush=True)
    time.sleep(0.3)
for d, bars in SPOT_EXTRA.items():
    if bars:
        SPOT.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4]) for b in bars})

DAYS = sorted(d for d in SPOT if FIRST <= d <= LAST)
print(f"calendar days {DAYS[0]} -> {DAYS[-1]}: {len(DAYS)}", flush=True)

# ---------------- futures 5-min series ----------------
KEYS = json.loads((TR / "round2_history/futures_keys.json").read_text())
manifest = {"built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "contracts": {}, "stopped_on_429": False}


def fetch_range(key, route, frm, to):
    enc = quote(key, safe="")
    if route == "expired":
        url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
               f"/5minute/{to}/{frm}")
    else:
        url = f"{API}/v3/historical-candle/{enc}/minutes/5/{to}/{frm}"
    body = get(url)
    if body is None:
        return []
    return [c for c in ((body.get("data") or {}).get("candles") or [])
            if frm <= c[0][:10] <= to]


def fetch_contract(exp):
    fn = OUT / f"FUT5_{exp}.json"
    if fn.exists():
        return json.loads(fn.read_text()), "cached"
    key, route = KEYS[exp]["key"], KEYS[exp]["route"]
    e = date.fromisoformat(exp)
    start = e - timedelta(days=58)
    seen = {}
    cur = start
    while cur <= e:
        nxt = min(cur + timedelta(days=14), e)
        for c in fetch_range(key, route, cur.isoformat(), nxt.isoformat()):
            seen[(c[0][:10], c[0][11:16])] = (
                c[0][:10], c[0][11:16], float(c[1]), float(c[2]),
                float(c[3]), float(c[4]))
        time.sleep(0.3)
        cur = nxt + timedelta(days=1)
    rows = sorted(seen.values())
    fn.write_text(json.dumps(rows))
    return rows, "fetched"


FUT = {}   # (date, time) -> close, for the in-force contract of that date
try:
    for exp in sorted({in_force(d) for d in DAYS}):
        rows, src = fetch_contract(exp)
        by_day = {}
        for (d, t, o, h, l, c) in rows:
            by_day.setdefault(d, {})[t] = c
        span = [d for d in DAYS if in_force(d) == exp]
        short = [d for d in span
                 if len(by_day.get(d, {})) < 74]
        # per-day retry for any short in-force day
        for d in short:
            got = fetch_range(KEYS[exp]["key"], KEYS[exp]["route"], d, d)
            for c in got:
                by_day.setdefault(d, {})[c[0][11:16]] = float(c[4])
            time.sleep(0.3)
        for d, bars in by_day.items():
            if in_force(d) == exp:
                for t, c in bars.items():
                    FUT[(d, t)] = c
        manifest["contracts"][exp] = dict(
            source=src, rows=len(rows), in_force_days=len(span),
            short_days_after_retry=[d for d in span
                                    if len(by_day.get(d, {})) < 74])
        print(f"FUT5 {exp}: {len(rows)} bars ({src}); in-force days "
              f"{len(span)}; short after retry: "
              f"{manifest['contracts'][exp]['short_days_after_retry']}",
              flush=True)
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
    print("RATE_LIMIT_STOP during futures fetch", flush=True)
    sys.exit(2)

# ---------------- morning-read dataset ----------------
import csv
rows_out, missing = [], []
for d in DAYS:
    s = SPOT.get(d, {})
    exp = in_force(d)
    so = s.get("09:15")
    fc15 = FUT.get((d, "09:15"))
    sc55 = s.get("10:55")
    fc55 = FUT.get((d, "10:55"))
    row = dict(date=d, expiry=exp,
               spot_open_0915=so[0] if so else None,
               spot_close_0915=so[3] if so else None,
               spot_close_1055=sc55[3] if sc55 else None,
               fut_close_0915=fc15, fut_close_1055=fc55)
    if so and sc55 and fc15 is not None and fc55 is not None:
        b_o = round(fc15 - so[3], 2)
        b_r = round(fc55 - sc55[3], 2)
        row.update(basis_open_pts=b_o, basis_read_pts=b_r,
                   basis_open_pct=round(b_o / so[3] * 100, 4),
                   basis_read_pct=round(b_r / sc55[3] * 100, 4),
                   dbasis_pct=round((b_r - b_o) / sc55[3] * 100, 4),
                   spot_morning_pct=round((sc55[3] / so[0] - 1) * 100, 4),
                   status="complete")
    else:
        row.update(basis_open_pts=None, basis_read_pts=None,
                   basis_open_pct=None, basis_read_pct=None,
                   dbasis_pct=None, spot_morning_pct=None,
                   status="partial")
        missing.append(d)
    rows_out.append(row)
with open(OUT / "banknifty_morning_basis.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)
gate = [r for r in rows_out if r["date"] <= "2026-10-31"]
nov = [r for r in rows_out if r["date"] >= "2026-11-01"]
print(f"morning rows: {len(rows_out)} (gate {len(gate)}, Nov {len(nov)}); "
      f"partial/missing: {missing}", flush=True)

def quartiles(vals):
    v = sorted(vals)
    n = len(v)
    return dict(n=n, min=v[0], p25=v[n // 4], median=v[n // 2],
                p75=v[3 * n // 4], max=v[-1])
manifest["morning"] = dict(
    rows=len(rows_out), partial=missing,
    gate_complete=sum(1 for r in gate if r["status"] == "complete"),
    gate_days=len(gate),
    spot_morning_pct_dist=quartiles(
        [r["spot_morning_pct"] for r in gate if r["status"] == "complete"]),
    dbasis_pct_dist=quartiles(
        [r["dbasis_pct"] for r in gate if r["status"] == "complete"]),
    basis_open_pct_dist=quartiles(
        [r["basis_open_pct"] for r in gate if r["status"] == "complete"]))
(OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
print(json.dumps(manifest["morning"], indent=1), flush=True)
print("BUILD DONE", flush=True)
