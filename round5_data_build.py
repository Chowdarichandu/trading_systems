#!/usr/bin/env python3
"""ROUND 5 DATA BUILD (2026-11-14) — morning flow dataset, Bank Nifty.

For every trading day Jan-Oct 2026 + November (Nov 2,3,4,5,6,9,11,12,
13): the 11-strike near-ATM band (nearest the spot close of the 10:55
bar, in-force monthly expiry), every band contract's FULL 5-minute
candles WITH volume and OI (fields 5/6 the earlier rounds dropped),
fetched via the expired-instruments route (live 2026-11-23 expiry via
v3, exactly as the frozen scorers branch). Per-contract caches in
round5_history/C5_<exp>_<strike><typ>.json (+ .done markers) make the
build resume-safe. Assembles round5_history/morning_flow.csv: per day
and side -- OI at 09:15 / 10:55 bars, dOI, premium index at both bars,
dP, morning traded volume (bars 09:15..10:55), Part 7 quadrant.
Also fetches the November futures contract's full-field 5-min series
(forensic map only) -> round5_history/FUT5N_NOV.json.

On HTTP 429: HARD STOP, manifest written, exit 2. Never prints token.
"""
import csv, json, sys, time
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
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]

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
SPOT = {}
raw = json.load(open(TR / "daily2leg/spot.json"))
for d, bars in raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
for fn in (TR / "oi_history/spot_nov_bars.json",
           TR / "round4_history/spot_extra.json",
           TR / "round4_history/r4d1_spot_fwd.json"):
    if not fn.exists():
        continue
    data = json.loads(fn.read_text())
    if isinstance(data, dict) and "BANKNIFTY" in data:
        data = data["BANKNIFTY"]
    if isinstance(data, dict):
        for d, bars in data.items():
            if d not in SPOT and isinstance(bars, list) and bars:
                SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                                  float(b[4])) for b in bars}

# progressive store (carries Nov 13 spot, landed after round 4)
_prog = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
if _prog.exists():
    import csv as _csv
    with open(_prog) as f:
        for r in _csv.DictReader(f):
            d, t = r["timestamp"][:10], r["timestamp"][11:16]
            SPOT.setdefault(d, {})[t] = (float(r["open"]), float(r["high"]),
                                         float(r["low"]), float(r["close"]))

DAYS = sorted(d for d in SPOT
              if "2026-01-01" <= d <= "2026-10-31") + \
       [d for d in NOV_DAYS if d in SPOT]
print(f"days: {len(DAYS)} (Jan-Oct "
      f"{sum(1 for d in DAYS if d <= '2026-10-31')}, Nov "
      f"{sum(1 for d in DAYS if d > '2026-10-31')})", flush=True)

# ---------------- bands ----------------
BAND = {}   # day -> (expiry, atm, [strikes])
for d in DAYS:
    s = SPOT[d].get("10:55")
    if s is None:
        continue
    atm = int(round(s[3] / 100.0)) * 100
    BAND[d] = (in_force(d), atm, [atm + 100 * k for k in range(-5, 6)])
print(f"band days: {len(BAND)}", flush=True)

# ---------------- contract keys ----------------
_keycache = {}


def contract_key(exp, strike, typ):
    ck = (exp, strike, typ)
    if ck in _keycache:
        return _keycache[ck]
    if exp not in _keycache.setdefault("__maps__", {}):
        pass
    maps = _keycache.setdefault("__maps__", {})
    if exp not in maps:
        if exp < "2026-11-13":
            body = get(f"{API}/v2/expired-instruments/option/contract"
                       f"?instrument_key={quote(IDXKEY, safe='')}"
                       f"&expiry_date={exp}")
            maps[exp] = {(int(float(c["strike_price"])),
                          c["instrument_type"]): c["instrument_key"]
                         for c in ((body or {}).get("data") or [])}
        else:
            rows = json.loads((TR / "daily2leg/instruments_cache.json")
                              .read_text())["rows"]
            maps[exp] = {(int(float(r["strike"])), r["option_type"]):
                         r["key"] for r in rows
                         if r["name"] == "BANKNIFTY" and r["expiry"] == exp}
        time.sleep(0.2)
    _keycache[ck] = maps[exp].get((strike, typ))
    return _keycache[ck]


def fetch_range(key, exp, frm, to):
    enc = quote(key, safe="")
    if exp < "2026-11-13":
        url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
               f"/5minute/{to}/{frm}")
    else:
        url = f"{API}/v3/historical-candle/{enc}/minutes/5/{to}/{frm}"
    body = get(url)
    if body is None:
        return []
    return [c for c in ((body.get("data") or {}).get("candles") or [])
            if frm <= c[0][:10] <= to]


# needed days per contract
NEED = {}
for d, (exp, atm, strikes) in BAND.items():
    for s in strikes:
        for typ in ("CE", "PE"):
            NEED.setdefault((exp, s, typ), set()).add(d)

manifest = {"contracts_total": len(NEED), "contracts_done": 0,
            "stopped_on_429": False, "calls": 0}
print(f"contracts to fetch: {len(NEED)}", flush=True)

from datetime import date, timedelta


def fetch_contract(exp, strike, typ, days):
    fn = OUT / f"C5_{exp}_{strike}{typ}.json"
    if (OUT / f"C5_{exp}_{strike}{typ}.done").exists():
        return json.loads(fn.read_text())
    key = contract_key(exp, strike, typ)
    if not key:
        fn.write_text("[]")
        (OUT / f"C5_{exp}_{strike}{typ}.done").write_text("nokey")
        return []
    days = sorted(days)
    seen = {}
    # chunk needed days into <=14-calendar-day windows
    chunks = []
    start = prev = days[0]
    for d in days[1:]:
        if (date.fromisoformat(d) - date.fromisoformat(prev)).days > 3 or \
           (date.fromisoformat(d) - date.fromisoformat(start)).days > 13:
            chunks.append((start, prev))
            start = d
        prev = d
    chunks.append((start, prev))
    for frm, to in chunks:
        for c in fetch_range(key, exp, frm, to):
            seen[(c[0][:10], c[0][11:16])] = (
                c[0][:10], c[0][11:16], float(c[1]), float(c[2]),
                float(c[3]), float(c[4]),
                float(c[5]) if len(c) > 5 else None,
                float(c[6]) if len(c) > 6 else None)
        manifest["calls"] += 1
        time.sleep(0.3)
    rows = sorted(seen.values())
    fn.write_text(json.dumps(rows))
    (OUT / f"C5_{exp}_{strike}{typ}.done").write_text("ok")
    return rows


CONTRACTS = {}
try:
    items = sorted(NEED.items())
    for i, ((exp, s, typ), days) in enumerate(items):
        CONTRACTS[(exp, s, typ)] = fetch_contract(exp, s, typ, days)
        manifest["contracts_done"] = i + 1
        if (i + 1) % 100 == 0:
            print(f"  contracts {i + 1}/{len(items)} "
                  f"calls={manifest['calls']}", flush=True)
            (OUT / "build_manifest.json").write_text(
                json.dumps(manifest, indent=1))
except RateLimited:
    manifest["stopped_on_429"] = True
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))
    print("RATE_LIMITED — HARD STOP", flush=True)
    sys.exit(2)
(OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1))

# ---------------- November futures (forensic only) ----------------
fut_fn = OUT / "FUT5N_NOV.json"
if not fut_fn.exists():
    fkeys = json.loads((TR / "round2_history/futures_keys.json")
                       .read_text())
    key = fkeys["2026-11-23"]["key"]
    rows = {}
    for c in fetch_range(key, "2026-11-23", "2026-11-02", "2026-11-13"):
        rows[(c[0][:10], c[0][11:16])] = (
            c[0][:10], c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
            float(c[4]), float(c[5]) if len(c) > 5 else None,
            float(c[6]) if len(c) > 6 else None)
    fut_fn.write_text(json.dumps(sorted(rows.values())))
    print(f"nov futures rows: {len(rows)}", flush=True)

# ---------------- assemble morning_flow.csv ----------------
CIDX = {}
for (exp, s, typ), rows in CONTRACTS.items():
    byd = {}
    for r in rows:
        byd.setdefault(r[0], {})[r[1]] = r
    CIDX[(exp, s, typ)] = byd


def contract_day(exp, s, typ, day):
    return CIDX.get((exp, s, typ), {}).get(day, {})


def quadrant(doi, dp):
    if doi == 0 or dp == 0:
        return "FLAT"
    if doi > 0 and dp > 0:
        return "LONG_BUILDUP"
    if doi > 0 and dp < 0:
        return "SHORT_BUILDUP"
    if doi < 0 and dp > 0:
        return "SHORT_COVERING"
    return "LONG_UNWINDING"


out_rows = []
for d in DAYS:
    if d not in BAND:
        continue
    exp, atm, strikes = BAND[d]
    row = {"date": d, "expiry": exp, "atm": atm,
           "spot_close_1055": SPOT[d]["10:55"][3]}
    complete = True
    for typ in ("CE", "PE"):
        oi15 = oi55 = p15 = p55 = vol = 0.0
        ok = True
        for s in strikes:
            bars = contract_day(exp, s, typ, d)
            b15, b55 = bars.get("09:15"), bars.get("10:55")
            if b15 is None or b55 is None or b15[7] is None \
                    or b55[7] is None:
                ok = False
                break
            oi15 += b15[7]
            oi55 += b55[7]
            p15 += b15[5]
            p55 += b55[5]
            vol += sum(r[6] for r in bars.values()
                       if "09:15" <= r[1] <= "10:55"
                       and r[6] is not None)
        if not ok:
            complete = False
            break
        row[f"oi0915_{typ}"] = oi15
        row[f"oi1055_{typ}"] = oi55
        row[f"doi_{typ}"] = oi55 - oi15
        row[f"p0915_{typ}"] = round(p15, 2)
        row[f"p1055_{typ}"] = round(p55, 2)
        row[f"dp_{typ}"] = round(p55 - p15, 2)
        row[f"vol_{typ}"] = vol
        row[f"quad_{typ}"] = quadrant(oi55 - oi15, p55 - p15)
    row["complete"] = complete
    if complete:
        tv = row["vol_CE"] + row["vol_PE"]
        row["vol_share_CE"] = round(row["vol_CE"] / tv, 4) if tv else None
    out_rows.append(row)

with open(OUT / "morning_flow.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)
ncomp = sum(1 for r in out_rows if r["complete"])
print(f"morning_flow rows: {len(out_rows)}, complete: {ncomp}", flush=True)
print("build complete", flush=True)
