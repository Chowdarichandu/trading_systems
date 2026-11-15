#!/usr/bin/env python3
"""ROUND 5 — PHASE 0 DATA AUDIT PROBE (2026-11-14).

Audits what the Upstox historical/intraday candle routes ACTUALLY
return for Jan-Oct 2026, on sample days across the window:
 (a) near-month BANKNIFTY FUTURES 5-min candles (expired route)
 (b) expired near-ATM BANKNIFTY OPTION 5-min candles (CE and PE)
Fields audited: candle width, volume (idx 5), oi (idx 6) -- present?
nonzero? does OI VARY intraday? last-bar OI vs the known daily OI.
Round 4's stored FUT5 series holds OHLC only (6 fields) -- checked
in the report; this probe reads the RAW API response.

On HTTP 429: HARD STOP, report and exit 2. Never prints the token.
"""
import json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_history"
OUT.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
IDXKEY = "NSE_INDEX|Nifty Bank"
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


# ---------------- calendars / reference data ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
SPOTDAYS = sorted(d for d in spot_raw["BANKNIFTY"]
                  if "2026-01-01" <= d <= "2026-10-31")
SPOT = {}
for d, bars in spot_raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
FUTKEYS = json.loads((TR / "round2_history/futures_keys.json").read_text())

# sample days: first + middle trading day of each month, Jan..Oct
samples = []
bymonth = {}
for d in SPOTDAYS:
    bymonth.setdefault(d[:7], []).append(d)
for m in sorted(bymonth):
    ds = bymonth[m]
    samples.append(ds[0])
    samples.append(ds[len(ds) // 2])
samples = sorted(set(samples))

# round-2 daily futures series (for daily-OI cross-check)
FUTDAILY = {}
for exp in ALL_EXP:
    fn = TR / "round2_history" / f"FUT_{exp}.json"
    if fn.exists():
        for row in json.loads(fn.read_text()):
            FUTDAILY[(exp, row[0])] = row


def field_audit(candles):
    """candles: raw API rows [ts,o,h,l,c,vol,oi?]."""
    a = {"n": len(candles)}
    if not candles:
        return a
    a["widths"] = sorted({len(c) for c in candles})
    vols = [c[5] for c in candles if len(c) > 5]
    a["vol_present"] = len(vols) == len(candles)
    a["vol_nonzero_bars"] = sum(1 for v in vols if v and v > 0)
    a["vol_sum"] = sum(v for v in vols if v)
    ois = [c[6] for c in candles if len(c) > 6]
    a["oi_present"] = len(ois) == len(candles) and len(ois) > 0
    if ois:
        a["oi_nonzero_bars"] = sum(1 for v in ois if v and v > 0)
        a["oi_distinct"] = len(set(ois))
        a["oi_first"] = ois[0]
        a["oi_last"] = ois[-1]
        morn = [c[6] for c in candles
                if len(c) > 6 and c[0][11:16] <= "10:55"]
        a["oi_morning_distinct"] = len(set(morn))
        a["oi_0915"] = next((c[6] for c in candles
                             if len(c) > 6 and c[0][11:16] == "09:15"),
                            None)
        a["oi_1055"] = next((c[6] for c in candles
                             if len(c) > 6 and c[0][11:16] == "10:55"),
                            None)
    return a


def fetch_5min_expired(key, day):
    url = (f"{API}/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    body = get(url)
    if body is None:
        return []
    return [c for c in ((body.get("data") or {}).get("candles") or [])
            if c[0][:10] == day]


result = {"samples": samples, "futures": [], "options": []}
try:
    # ---------- (a) FUTURES ----------
    for day in samples:
        exp = in_force(day)
        key = FUTKEYS[exp]["key"]
        cd = fetch_5min_expired(key, day)
        a = field_audit(cd)
        a["date"] = day
        a["expiry"] = exp
        drow = FUTDAILY.get((exp, day))
        a["daily_oi_ref"] = (drow[6] if drow and len(drow) > 6 else None)
        a["lastbar_oi_eq_daily"] = (
            a.get("oi_last") == a["daily_oi_ref"]
            if a.get("oi_last") is not None and a["daily_oi_ref"]
            is not None else None)
        result["futures"].append(a)
        print(f"FUT {day} exp={exp} n={a['n']} widths={a.get('widths')} "
              f"vol_nz={a.get('vol_nonzero_bars')} oi_pres={a.get('oi_present')} "
              f"oi_distinct={a.get('oi_distinct')} oi_morn_distinct="
              f"{a.get('oi_morning_distinct')} lastEqDaily="
              f"{a['lastbar_oi_eq_daily']}", flush=True)
        time.sleep(0.25)

    # ---------- (b) OPTIONS (first sample day of each month) ----------
    opt_samples = samples[::2]
    keycache = {}
    for day in opt_samples:
        exp = in_force(day)
        if exp not in keycache:
            body = get(f"{API}/v2/expired-instruments/option/contract"
                       f"?instrument_key={quote(IDXKEY, safe='')}"
                       f"&expiry_date={exp}")
            keycache[exp] = {
                (int(float(c["strike_price"])), c["instrument_type"]):
                c["instrument_key"] for c in (body.get("data") or [])}
            time.sleep(0.25)
        s1055 = SPOT[day].get("10:55")
        if s1055 is None:
            continue
        atm = int(round(s1055[3] / 100.0)) * 100
        for typ in ("CE", "PE"):
            key = keycache[exp].get((atm, typ))
            if not key:
                result["options"].append({"date": day, "type": typ,
                                          "error": "no_key"})
                continue
            cd = fetch_5min_expired(key, day)
            a = field_audit(cd)
            a["date"] = day
            a["expiry"] = exp
            a["strike"] = atm
            a["type"] = typ
            # daily OI cross-check from round-1 contract cache
            cfn = (TR / "oi_history/contracts" /
                   f"BANKNIFTY_{exp}_{atm}{typ}.json")
            ref = None
            if cfn.exists():
                for row in json.loads(cfn.read_text()):
                    if row[0] == day and len(row) > 6:
                        ref = row[6]
            a["daily_oi_ref"] = ref
            a["lastbar_oi_eq_daily"] = (
                a.get("oi_last") == ref
                if a.get("oi_last") is not None and ref is not None
                else None)
            result["options"].append(a)
            print(f"OPT {day} {atm}{typ} exp={exp} n={a['n']} "
                  f"widths={a.get('widths')} vol_nz="
                  f"{a.get('vol_nonzero_bars')} oi_pres={a.get('oi_present')} "
                  f"oi_distinct={a.get('oi_distinct')} oi_morn_distinct="
                  f"{a.get('oi_morning_distinct')} lastEqDaily="
                  f"{a['lastbar_oi_eq_daily']}", flush=True)
            time.sleep(0.25)
except RateLimited:
    print("RATE_LIMITED — HARD STOP", flush=True)
    result["rate_limited"] = True
    (OUT / "probe_audit.json").write_text(json.dumps(result, indent=1))
    sys.exit(2)

(OUT / "probe_audit.json").write_text(json.dumps(result, indent=1))
print("probe complete ->", OUT / "probe_audit.json")
