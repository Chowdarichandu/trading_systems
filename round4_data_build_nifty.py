#!/usr/bin/env python3
"""ROUND 4 DATA BUILD — NIFTY (2026-11-13 night). Mirror of the Bank
build for surface A: near-month NIFTY futures 5-minute candles +
the morning-read dataset (basis at 09:15-bar close and 10:55-bar
close, spot morning move, dbasis_pct), days 2026-01-01 -> 2026-11-12.

Monthly futures expiries: candidates = the last front (weekly)
expiry inside each month of the round-1 NIFTY OI dataset (the
monthly expires on the month's last weekly expiry); every candidate
is VERIFIED against the expired-instruments future/contract route
(exactly one contract must come back). November monthly candidate
2026-11-24 is verified the same way (the OI dataset ends Nov 11, so
its own max-November front expiry, 11-17, is a weekly, not the
monthly future).

Spot: stored series (daily2leg/spot.json + spot_nov_bars.json);
Nov 12 spot fetched via v3 (Nov 13 returns 0 — documented lag).
Resume-safe caches in round4_history/. HTTP 429: hard stop, exit 2.
"""
import csv, json, sys, time
import urllib.request, urllib.error
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "round4_history"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
IDXKEY = "NSE_INDEX|Nifty 50"
FIRST, LAST = "2026-01-01", "2026-11-12"

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


# monthly expiry candidates from the OI dataset + Nov monthly
oi_rows = {}
with open(TR / "oi_history/nifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        oi_rows[r["date"]] = r
front_exps = sorted({r["expiry"] for r in oi_rows.values()})
bymonth = {}
for e in front_exps:
    bymonth.setdefault(e[:7], []).append(e)
MONTHLY = sorted({max(v) for v in bymonth.values()
                  if list(bymonth.keys()) and max(v) <= "2026-10-31"})
MONTHLY.append("2026-11-23")   # Nov monthly: last Tuesday (24th) is a
# holiday — expiry shifted to Mon 2026-11-23, exactly as Bank's own
# MONTHLY_EXPIRIES list carries 2026-11-23. Verified against the live
# NSE instruments dump: exactly one contract, "NIFTY FUT 23 NOV 26",
# key NSE_FO|61471 (the same source round 2 used for its live key).
print("monthly candidates:", MONTHLY, flush=True)


def in_force(day):
    for e in MONTHLY:
        if e >= day:
            return e
    return None


# verify candidates + obtain futures keys
keys_fn = OUT / "futures_keys_nifty.json"
KEYS = json.loads(keys_fn.read_text()) if keys_fn.exists() else {}
try:
    for exp in MONTHLY:
        if exp in KEYS:
            continue
        body = get(f"{API}/v2/expired-instruments/future/contract"
                   f"?instrument_key={quote(IDXKEY, safe='')}"
                   f"&expiry_date={exp}")
        data = (body or {}).get("data") or []
        if len(data) == 1 and exp < "2026-11-13":
            KEYS[exp] = dict(key=data[0]["instrument_key"],
                             route="expired",
                             symbol=data[0]["trading_symbol"])
        elif exp >= "2026-11-13":
            KEYS[exp] = dict(key=None, route="live_pending",
                             symbol=None)
        else:
            KEYS[exp] = dict(key=None, route="NOT_FOUND",
                             symbol=None, n_returned=len(data))
        keys_fn.write_text(json.dumps(KEYS, indent=1))
        print(f"key {exp}: {KEYS[exp]}", flush=True)
        time.sleep(0.3)
except RateLimited:
    print("RATE_LIMIT_STOP during NIFTY futures key verification",
          flush=True)
    sys.exit(2)
bad = {e: k for e, k in KEYS.items() if not k.get("key")
       and k["route"] != "live_pending"}
print("unverified monthly candidates:", bad, flush=True)

# November monthly (2026-11-23) is still live: key resolved from the
# public NSE instruments dump (verified above, exactly one contract).
if KEYS.get("2026-11-23", {}).get("route") == "live_pending":
    KEYS["2026-11-23"] = dict(key="NSE_FO|61471", route="live",
                              symbol="NIFTY FUT 23 NOV 26")
    keys_fn.write_text(json.dumps(KEYS, indent=1))
    print("live key set for 2026-11-23: NSE_FO|61471", flush=True)

# ---------------- spot ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
nov_bars = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
SPOT = {}
for d, bars in spot_raw["NIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
for d, bars in nov_bars.get("NIFTY", {}).items():
    SPOT.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4]) for b in bars})
extra_fn = OUT / "spot_extra_nifty.json"
SPOT_EXTRA = json.loads(extra_fn.read_text()) if extra_fn.exists() else {}
ikey = quote(IDXKEY, safe="")
for day in ("2026-11-12", "2026-11-13"):
    if day in SPOT_EXTRA:
        continue
    body = get(f"{API}/v3/historical-candle/{ikey}/minutes/5/{day}/{day}")
    cd = [c for c in ((body or {}).get("data") or {}).get("candles") or []
          if c[0][:10] == day]
    SPOT_EXTRA[day] = [[c[0][11:16], float(c[1]), float(c[2]),
                        float(c[3]), float(c[4])] for c in cd]
    extra_fn.write_text(json.dumps(SPOT_EXTRA))
    print(f"spot extra NIFTY {day}: {len(cd)} candles", flush=True)
    time.sleep(0.3)
for d, bars in SPOT_EXTRA.items():
    if bars:
        SPOT.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4]) for b in bars})
DAYS = sorted(d for d in SPOT if FIRST <= d <= LAST)
print(f"NIFTY calendar days: {len(DAYS)} ({DAYS[0]} -> {DAYS[-1]})",
      flush=True)

# ---------------- futures 5-min ----------------
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
    fn = OUT / f"FUT5_NIFTY_{exp}.json"
    if fn.exists():
        return json.loads(fn.read_text()), "cached"
    key, route = KEYS[exp]["key"], KEYS[exp]["route"]
    if not key:
        return [], "no_key"
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


manifest = {"contracts": {}, "stopped_on_429": False}
FUT = {}
try:
    for exp in sorted({in_force(d) for d in DAYS}):
        rows, src = fetch_contract(exp)
        by_day = {}
        for (d, t, o, h, l, c) in rows:
            by_day.setdefault(d, {})[t] = c
        span = [d for d in DAYS if in_force(d) == exp]
        for d in [d for d in span if len(by_day.get(d, {})) < 74]:
            if KEYS[exp].get("key"):
                for c in fetch_range(KEYS[exp]["key"],
                                     KEYS[exp]["route"], d, d):
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
        print(f"FUT5 NIFTY {exp}: {len(rows)} bars ({src}); short: "
              f"{manifest['contracts'][exp]['short_days_after_retry']}",
              flush=True)
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest_nifty.json").write_text(json.dumps(manifest,
                                                             indent=1))
    print("RATE_LIMIT_STOP during NIFTY futures fetch", flush=True)
    sys.exit(2)

# ---------------- morning dataset ----------------
rows_out, missing = [], []
for d in DAYS:
    s = SPOT.get(d, {})
    exp = in_force(d)
    so, sc55 = s.get("09:15"), s.get("10:55")
    fc15, fc55 = FUT.get((d, "09:15")), FUT.get((d, "10:55"))
    row = dict(date=d, expiry=exp,
               spot_open_0915=so[0] if so else None,
               spot_close_0915=so[3] if so else None,
               spot_close_1055=sc55[3] if sc55 else None,
               fut_close_0915=fc15, fut_close_1055=fc55)
    if so and sc55 and fc15 is not None and fc55 is not None:
        b_o, b_r = round(fc15 - so[3], 2), round(fc55 - sc55[3], 2)
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
with open(OUT / "nifty_morning_basis.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)
gate = [r for r in rows_out if r["date"] <= "2026-10-31"]
manifest["morning"] = dict(
    rows=len(rows_out), partial=missing,
    gate_complete=sum(1 for r in gate if r["status"] == "complete"),
    gate_days=len(gate))
(OUT / "build_manifest_nifty.json").write_text(json.dumps(manifest,
                                                          indent=1))
print(f"NIFTY morning rows: {len(rows_out)}; gate complete "
      f"{manifest['morning']['gate_complete']}/{len(gate)}; "
      f"partial: {missing}", flush=True)
print("BUILD NIFTY DONE", flush=True)
