#!/usr/bin/env python3
"""ROUND 2 DATA BUILD (2026-11-13 night) — two NEW day-level surfaces for
Bank Nifty that no candle book has ever read:

  SURFACE A — near-month BANKNIFTY FUTURES BASIS (futures close minus
  spot close, day D). Futures daily candles via the Upstox expired-
  instruments route (v2 future/contract + historical-candle/day);
  the live 2026-11-23 contract via the public NSE instruments dump +
  v3 days route. Spot closes from the same stored 5-min series the OI
  programme used (daily2leg/spot.json + oi_history/spot_nov_bars.json).
  SURFACE B — INDIA VIX daily close (public historical series: NSE
  /api/historical/vix primary, Yahoo ^INDIAVIX cross-check/fallback).

Window: trading days 2025-12-22 -> 2026-11-12 (lookback for the first
January signals' day-over-day changes; gate window Jan-Oct 2026;
November lens signal days through Nov 12).

TIMING: every field of row D is a day-D CLOSE (futures daily candle,
spot last bar, published VIX close). A signal read from row D is
knowable only after D's close and is traded on D+1. The scorer asserts
signal_date < trade_date on every trade.

Resume-safe: per-contract series cached under round2_history/; cached
files are skipped. On HTTP 429 (Upstox scope): HARD STOP, partial
state recorded in the manifest, exit 2. Never prints the token.
"""
import csv, gzip, io, json, sys, time
import urllib.request, urllib.error
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "round2_history"
OUT.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
IDXKEY = "NSE_INDEX|Nifty Bank"
FIRST, LAST = "2025-12-22", "2026-11-12"

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token, "no token"


class RateLimited(Exception):
    pass


def get(url, auth=True, raw=False):
    h = {"Accept": "application/json", "User-Agent": UA}
    if auth:
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        raise
    return body if raw else json.loads(body)


# ---------------- calendar + spot closes ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
nov_bars = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
SPOT_CLOSE, SPOT_DAYS = {}, {}
for d, bars in spot_raw["BANKNIFTY"].items():
    if bars:
        SPOT_CLOSE[d] = float(bars[-1][4])
        SPOT_DAYS[d] = {b[0] for b in bars}
for d, bars in nov_bars.get("BANKNIFTY", {}).items():
    if bars and d not in SPOT_CLOSE:
        SPOT_CLOSE[d] = float(bars[-1][4])
DAYS = sorted(d for d in SPOT_CLOSE if FIRST <= d <= LAST)
print(f"trading days {DAYS[0]} -> {DAYS[-1]}: {len(DAYS)}", flush=True)

# in-force monthly expiry per day: the OI dataset's own convention
# (first monthly expiry >= day), verified against its expiry column.
sys.path.insert(0, str(TR))
from btst_common import MONTHLY_EXPIRIES as BANK_MONTHLY  # noqa: E402
ALL_EXP = ["2025-12-30"] + list(BANK_MONTHLY)  # Dec-2025 monthly expiry


def in_force(day):
    for e in ALL_EXP:
        if e >= day:
            return e
    return None


oi_rows = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        oi_rows[r["date"]] = r
mismatch = [d for d in DAYS if d in oi_rows
            and oi_rows[d]["expiry"] != in_force(d)]
print(f"in-force convention vs OI dataset expiry column: "
      f"{len(mismatch)} mismatches {mismatch[:5]}", flush=True)
oi_spot_diff = [d for d in DAYS if d in oi_rows
                and abs(float(oi_rows[d]["spot_close"]) - SPOT_CLOSE[d])
                > 0.011]
print(f"spot close vs OI dataset spot_close: {len(oi_spot_diff)} days "
      f"differ by >0.01 {oi_spot_diff[:5]}", flush=True)

# ---------------- futures contract keys ----------------
manifest = {"built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "contracts": {}, "stopped_on_429": False}
keys_file = OUT / "futures_keys.json"
KEYS = json.loads(keys_file.read_text()) if keys_file.exists() else {}
expiries_needed = sorted({in_force(d) for d in DAYS})
print(f"futures expiries needed: {expiries_needed}", flush=True)

try:
    for exp in expiries_needed:
        if exp in KEYS:
            continue
        if exp < "2026-11-13":  # expired route
            url = (f"{API}/v2/expired-instruments/future/contract"
                   f"?instrument_key={quote(IDXKEY, safe='')}"
                   f"&expiry_date={exp}")
            body = get(url)
            data = body.get("data") or []
            assert len(data) == 1, f"{exp}: {len(data)} futures contracts"
            KEYS[exp] = dict(key=data[0]["instrument_key"],
                             route="expired", symbol=data[0]["trading_symbol"])
        else:  # live contract: public NSE instruments dump (expiry = epoch ms)
            raw = get("https://assets.upstox.com/market-quote/instruments/"
                      "exchange/NSE.json.gz", auth=False, raw=True)
            rows = json.loads(gzip.decompress(raw))
            from datetime import datetime, timezone
            ist = timezone(timedelta(hours=5, minutes=30))

            def exp_str(r):
                e = r.get("expiry")
                if isinstance(e, (int, float)):
                    return datetime.fromtimestamp(e / 1000, ist) \
                        .date().isoformat()
                return str(e)[:10]
            hit = [r for r in rows
                   if r.get("underlying_symbol") == "BANKNIFTY"
                   and r.get("instrument_type") == "FUT"
                   and exp_str(r) == exp]
            assert len(hit) == 1, f"{exp}: {len(hit)} live futures"
            KEYS[exp] = dict(key=hit[0]["instrument_key"], route="live",
                             symbol=hit[0]["trading_symbol"])
        keys_file.write_text(json.dumps(KEYS, indent=1))
        print(f"key {exp}: {KEYS[exp]['symbol']} ({KEYS[exp]['route']})",
              flush=True)
        time.sleep(0.3)
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
    print("RATE_LIMIT_STOP during contract-key fetch", flush=True)
    sys.exit(2)

# ---------------- futures daily series ----------------
def fetch_fut_series(exp):
    fn = OUT / f"FUT_{exp}.json"
    if fn.exists():
        return json.loads(fn.read_text()), "cached"
    e = date.fromisoformat(exp)
    f = max(date(2025, 11, 15), e - timedelta(days=60)).isoformat()
    key = KEYS[exp]["key"]
    enc = quote(key, safe="")
    if KEYS[exp]["route"] == "expired":
        url = f"{API}/v2/expired-instruments/historical-candle/{enc}/day/{exp}/{f}"
    else:
        url = f"{API}/v3/historical-candle/{enc}/days/1/{exp}/{f}"
    body = get(url)
    rows = []
    for c in ((body.get("data") or {}).get("candles") or []):
        rows.append([c[0][:10], float(c[1]), float(c[2]), float(c[3]),
                     float(c[4]), float(c[5])])
    rows.sort()
    fn.write_text(json.dumps(rows))
    time.sleep(0.3)
    return rows, "fetched"


FUT = {}  # (expiry, date) -> close
try:
    for exp in expiries_needed:
        rows, src = fetch_fut_series(exp)
        for r in rows:
            FUT[(exp, r[0])] = r[4]
        manifest["contracts"][exp] = dict(
            source=src, n_rows=len(rows),
            first=rows[0][0] if rows else None,
            last=rows[-1][0] if rows else None)
        print(f"series {exp}: {len(rows)} rows ({src})", flush=True)
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
    print("RATE_LIMIT_STOP during futures series fetch", flush=True)
    sys.exit(2)

# ---------------- basis dataset ----------------
out_rows, missing = [], []
prev_close = None
for d in DAYS:
    exp = in_force(d)
    fc = FUT.get((exp, d))
    sc = SPOT_CLOSE[d]
    chg = None if prev_close is None else round(sc - prev_close, 2)
    if fc is None:
        missing.append(d)
    out_rows.append(dict(
        date=d, expiry=exp, spot_close=sc, spot_chg_pts=chg,
        fut_close=fc,
        basis_pts=None if fc is None else round(fc - sc, 2),
        basis_pct=None if fc is None else round((fc - sc) / sc * 100, 4)))
    prev_close = sc
with open(OUT / "banknifty_basis_daily.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)
gate_days = [r for r in out_rows if "2026-01-01" <= r["date"] <= "2026-10-31"]
print(f"basis rows: {len(out_rows)}; gate-window days: {len(gate_days)}; "
      f"missing futures close on: {missing}", flush=True)
manifest["basis"] = dict(rows=len(out_rows), missing_fut_close=missing)

# ---------------- INDIA VIX ----------------
vix = {}   # date -> close (NSE primary)
nse_note = None
try:
    s = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    s.open(urllib.request.Request("https://www.nseindia.com",
                                  headers={"User-Agent": UA}), timeout=30)
    url = ("https://www.nseindia.com/api/historical/vix"
           "?from=22-12-2025&to=12-11-2026")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json",
        "Referer": "https://www.nseindia.com/products-services/"
                   "indices-india-vix-historical-data"})
    with s.open(req, timeout=60) as r:
        body = json.loads(r.read())
    from datetime import datetime
    for row in (body.get("data") or []):
        d = row.get("EOD_TIMESTAMP") or row.get("timestamp") or ""
        dd = datetime.strptime(d, "%d-%b-%Y").date().isoformat()
        vix[dd] = float(row.get("EOD_CLOSE_INDEX_VAL") or row["close"])
    nse_note = f"NSE rows: {len(vix)}"
except Exception as ex:
    nse_note = f"NSE failed: {type(ex).__name__}: {ex}"
print(nse_note, flush=True)

# Yahoo cross-check / fallback
yh = {}
try:
    p1 = int(time.mktime(time.strptime("2025-12-20", "%Y-%m-%d")))
    p2 = int(time.mktime(time.strptime("2026-11-14", "%Y-%m-%d")))
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/%5EINDIAVIX"
           f"?period1={p1}&period2={p2}&interval=1d")
    body = get(url, auth=False)
    res = (body.get("chart") or {}).get("result") or []
    if res:
        ts = res[0].get("timestamp") or []
        cl = (res[0].get("indicators", {}).get("quote") or [{}])[0] \
            .get("close") or []
        for t, c in zip(ts, cl):
            if c is not None:
                yh[time.strftime("%Y-%m-%d", time.gmtime(t))] = round(c, 2)
    print(f"Yahoo rows: {len(yh)}", flush=True)
except Exception as ex:
    print(f"Yahoo failed: {type(ex).__name__}: {ex}", flush=True)

source = "NSE" if len(vix) >= 200 else ("Yahoo" if yh else None)
if source == "Yahoo":
    vix = yh
both = sorted(set(vix) & set(yh))
diffs = [(d, vix[d], yh[d]) for d in both if abs(vix[d] - yh[d]) > 0.05]
vix_rows = []
for d in DAYS:
    vix_rows.append(dict(date=d, vix_close=vix.get(d)))
with open(OUT / "india_vix_daily.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "vix_close"])
    w.writeheader()
    w.writerows(vix_rows)
miss_vix = [r["date"] for r in vix_rows if r["vix_close"] is None]
gate_vix = [r for r in vix_rows if "2026-01-01" <= r["date"] <= "2026-10-31"]
print(f"VIX source: {source}; rows on trading calendar: "
      f"{len(vix_rows) - len(miss_vix)}/{len(vix_rows)}; missing: "
      f"{miss_vix}; NSE-vs-Yahoo disagreements >0.05: {len(diffs)} "
      f"{diffs[:5]}", flush=True)
manifest["vix"] = dict(source=source, nse_note=nse_note,
                       yahoo_rows=len(yh), missing_on_calendar=miss_vix,
                       xcheck_disagreements=diffs[:20])
# ---------------- Nov 12 supplementary (signal day for Nov 13) -------
# The stored 5-min spot calendar ends Nov 11; Nov 12's spot close comes
# from the official index daily candle (v3 days route). Used ONLY by
# the labelled supplementary Nov-13 check, exactly as round 1 used the
# archived chain for its Nov-12 signal read.
try:
    url = (f"{API}/v3/historical-candle/{quote(IDXKEY, safe='')}"
           f"/days/1/2026-11-12/2026-11-12")
    body = get(url)
    cd = [c for c in ((body.get("data") or {}).get("candles") or [])
          if c[0][:10] == "2026-11-12"]
    fut12 = FUT.get(("2026-11-23", "2026-11-12"))
    supp = dict(date="2026-11-12", expiry="2026-11-23",
                spot_close=float(cd[0][4]) if cd else None,
                fut_close=fut12,
                vix_close=vix.get("2026-11-12"))
    if supp["spot_close"] and fut12:
        supp["basis_pts"] = round(fut12 - supp["spot_close"], 2)
        supp["basis_pct"] = round(supp["basis_pts"] / supp["spot_close"]
                                  * 100, 4)
    (OUT / "nov12_supplementary.json").write_text(json.dumps(supp, indent=1))
    print(f"Nov 12 supplementary: {supp}", flush=True)
    manifest["nov12_supplementary"] = supp
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
    print("RATE_LIMIT_STOP during supplementary fetch", flush=True)
    sys.exit(2)

(OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
print("BUILD DONE", flush=True)
