#!/usr/bin/env python3
"""OI HISTORY BUILD (2026-11-13) — Part 1 of the option-chain build-up
programme. Reconstructs daily open-interest history for BANKNIFTY and
NIFTY, 2026-01-01 -> 2026-11-12, from per-contract daily candles
(7th candle field = OI).

Per trading day per index, for the in-force expiry (Bank: monthly;
Nifty: front/weekly), over the ATM band (the 11 strikes nearest that
day's spot close): aggregate CE OI, PE OI, day-over-day changes
(same-contract), PCR(OI), spot close and day change.

Routes: expired expiries -> v2 expired-instruments (contract list +
historical-candle/day range); live expiries (2026-11-17 NIFTY,
2026-11-23 BANKNIFTY) -> instruments_cache key + v3 historical-candle.
Browser User-Agent on every call. Token from upstox_refresh/.env, never
printed. On HTTP 429: HARD STOP (exit 2), manifest records partial state.
Resume-safe: cached contract series are skipped.
"""
import csv, json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "oi_history"
CDIR = OUT / "contracts"
OUT.mkdir(exist_ok=True)
CDIR.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
TODAY = "2026-11-13"
FIRST_DAY, LAST_DAY = "2026-01-01", "2026-11-12"

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token, "no token"

def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

class RateLimited(Exception):
    pass

def get_safe(url):
    try:
        return get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        raise

# ---------------- calendar + spot ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
STEP = {"BANKNIFTY": 100, "NIFTY": 50}
IDXKEY = {"BANKNIFTY": "NSE_INDEX|Nifty Bank", "NIFTY": "NSE_INDEX|Nifty 50"}

def spot_closes(idx):
    out = {}
    for d, bars in spot_raw[idx].items():
        if bars:
            out[d] = float(bars[-1][4])
    return out

CLOSES = {i: spot_closes(i) for i in STEP}

# November spot (Nov 1-12) is not in spot.json: fetch 5-min index bars once.
nov_cache = OUT / "spot_nov_bars.json"
if nov_cache.exists():
    nov = json.loads(nov_cache.read_text())
else:
    nov = {}
    for idx, key in IDXKEY.items():
        days = {}
        for to_d, from_d in (("2026-11-05", "2026-11-01"),
                             ("2026-11-12", "2026-11-06")):
            url = (f"{API}/v3/historical-candle/{quote(key, safe='')}"
                   f"/minutes/5/{to_d}/{from_d}")
            body = get_safe(url)
            for c in ((body.get("data") or {}).get("candles") or []):
                d, t = c[0][:10], c[0][11:16]
                days.setdefault(d, []).append(
                    [t, float(c[1]), float(c[2]), float(c[3]), float(c[4])])
        nov[idx] = {d: sorted(b) for d, b in days.items()}
        print(f"nov spot {idx}: {sorted(days)}", flush=True)
    nov_cache.write_text(json.dumps(nov))
for idx in STEP:
    for d, bars in nov.get(idx, {}).items():
        if bars and d not in CLOSES[idx]:
            CLOSES[idx][d] = float(bars[-1][4])

ALL_DAYS = sorted(d for d in CLOSES["NIFTY"]
                  if "2025-12-22" <= d <= LAST_DAY
                  and d in CLOSES["BANKNIFTY"])
print(f"trading days in span: {len(ALL_DAYS)} "
      f"({ALL_DAYS[0]} -> {ALL_DAYS[-1]})", flush=True)

# ---------------- expiry calendars (exchange-derived) ----------------
# Store-key calendars proved polluted (bogus BANKNIFTY 2026-10-21/23/26 keys;
# NIFTY weeks missing: Jun 16, Aug 11, Sep 15, Oct 6). Ground truth used
# instead: Bank monthly list frozen in btst_common.py (MONTHLY_EXPIRIES)
# and the engine's exchange-derived Nifty expiry list
# (nifty_engine_run3_expiries.json), extended with the November expiries
# (Nov 3 stored; Nov 9 = Diwali-shifted weekly, 294 contracts on the
# expired endpoint; Nov 17 = live front weekly).
def exps_from(*files):
    s = set()
    for f in files:
        d = json.load(open(TR / "daily2leg" / f))
        s |= {k.split("|")[0] for k in d}
    return sorted(e for e in s if "2025-12-01" <= e <= "2026-12-31")

_btst = json.loads("[]")
sys.path.insert(0, str(TR))
from btst_common import MONTHLY_EXPIRIES as BANK_MONTHLY
_run3 = json.load(open(TR / "nifty_engine_run3_expiries.json"))
EXPS = {
    "BANKNIFTY": sorted(e for e in BANK_MONTHLY
                        if "2026-01-01" <= e <= "2026-11-30"),
    "NIFTY": sorted({e for e in _run3 if "2025-12-01" <= e <= "2026-10-31"}
                    | {"2026-11-03", "2026-11-09", "2026-11-17"}),
}
for i, es in EXPS.items():
    gaps = [(es[k + 1], es[k]) for k in range(len(es) - 1)]
    print(f"{i} expiries ({len(es)}): {es[0]} -> {es[-1]}", flush=True)

def in_force(idx, day):
    for e in EXPS[idx]:
        if e >= day:
            return e
    return None

def atm(idx, close):
    st = STEP[idx]
    return int(round(close / st)) * st

# ---------------- contract key maps ----------------
live_rows = None
def contract_map(idx, exp):
    """(strike, type) -> instrument_key for one expiry."""
    if exp < TODAY:  # expired route
        url = (f"{API}/v2/expired-instruments/option/contract"
               f"?instrument_key={quote(IDXKEY[idx], safe='')}"
               f"&expiry_date={exp}")
        body = get_safe(url)
        m = {}
        for c in (body.get("data") or []):
            m[(int(float(c["strike_price"])), c["instrument_type"])] = \
                c["instrument_key"]
        return m, "expired"
    global live_rows
    if live_rows is None:
        live_rows = json.loads(
            (TR / "daily2leg/instruments_cache.json").read_text())["rows"]
    m = {}
    for r in live_rows:
        if r["name"] == idx and r["expiry"] == exp:
            m[(int(float(r["strike"])), r["option_type"])] = r["key"]
    return m, "live"

# ---------------- daily series fetch ----------------
def fetch_series(idx, exp, strike, typ, key, route):
    """Daily candles [date,o,h,l,c,vol,oi] ascending, cached on disk."""
    fn = CDIR / f"{idx}_{exp}_{strike}{typ}.json"
    if fn.exists():
        return json.loads(fn.read_text()), "cached"
    frm = (json.loads('"%s"' % exp))  # expiry string
    from datetime import date, timedelta
    e = date.fromisoformat(exp)
    f = max(date(2025, 11, 15), e - timedelta(days=55)).isoformat()
    enc = quote(key, safe='')
    if route == "expired":
        url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
               f"/day/{exp}/{f}")
    else:
        url = f"{API}/v3/historical-candle/{enc}/days/1/{exp}/{f}"
    body = get_safe(url)
    rows = []
    for c in ((body.get("data") or {}).get("candles") or []):
        rows.append([c[0][:10], float(c[1]), float(c[2]), float(c[3]),
                     float(c[4]), float(c[5]),
                     float(c[6]) if len(c) > 6 else None])
    rows.sort()
    fn.write_text(json.dumps(rows))
    return rows, "fetched"

# ---------------- build ----------------
manifest = []
datasets = {}
coverage = {}
stopped = False
for idx in STEP:
    rows_out = []
    oi_by_contract = {}  # (exp, strike, typ) -> {date: oi}
    exps_needed = sorted({in_force(idx, d) for d in ALL_DAYS
                          if in_force(idx, d)})
    for exp in exps_needed:
        if stopped:
            break
        window = [d for d in ALL_DAYS if in_force(idx, d) == exp]
        if not window:
            continue
        strikes = set()
        for d in window:
            a = atm(idx, CLOSES[idx][d])
            for k in range(-5, 6):
                strikes.add(a + k * STEP[idx])
        try:
            cmap, route = contract_map(idx, exp)
        except RateLimited:
            print(f"HTTP 429 resolving contracts {idx} {exp} — HARD STOP",
                  flush=True)
            stopped = True
            break
        got, miss = 0, 0
        for strike in sorted(strikes):
            for typ in ("CE", "PE"):
                key = cmap.get((strike, typ))
                if not key:
                    miss += 1
                    manifest.append([idx, exp, strike, typ, "NO_KEY"])
                    continue
                try:
                    series, how = fetch_series(idx, exp, strike, typ,
                                               key, route)
                except RateLimited:
                    print(f"HTTP 429 at {idx} {exp} {strike}{typ} — "
                          f"HARD STOP", flush=True)
                    stopped = True
                    break
                except Exception as ex:
                    miss += 1
                    manifest.append([idx, exp, strike, typ,
                                     f"ERR {type(ex).__name__}"])
                    continue
                oi_by_contract[(exp, strike, typ)] = \
                    {r[0]: r[6] for r in series if r[6] is not None}
                got += 1
                manifest.append([idx, exp, strike, typ,
                                 f"OK_{how} {len(series)}d"])
                if how == "fetched":
                    time.sleep(0.3)
            if stopped:
                break
        print(f"{idx} {exp}: window {window[0]}->{window[-1]} "
              f"({len(window)}d), band-union {len(strikes)} strikes, "
              f"contracts ok {got}, missing {miss}", flush=True)
    if stopped:
        break
    # assemble per-day rows
    prev_day = {}
    for i, d in enumerate(ALL_DAYS):
        prev_day[d] = ALL_DAYS[i - 1] if i > 0 else None
    complete = partial = nodata = 0
    for d in [x for x in ALL_DAYS if FIRST_DAY <= x <= LAST_DAY]:
        exp = in_force(idx, d)
        a = atm(idx, CLOSES[idx][d])
        band = [a + k * STEP[idx] for k in range(-5, 6)]
        pd = prev_day[d]
        ce = pe = dce = dpe = 0.0
        have = pairs = 0
        for strike in band:
            for typ, side in (("CE", "ce"), ("PE", "pe")):
                s = oi_by_contract.get((exp, strike, typ), {})
                oi = s.get(d)
                if oi is None:
                    continue
                have += 1
                if side == "ce":
                    ce += oi
                else:
                    pe += oi
                oi_prev = s.get(pd) if pd else None
                if oi_prev is not None:
                    pairs += 1
                    if side == "ce":
                        dce += oi - oi_prev
                    else:
                        dpe += oi - oi_prev
        chg = CLOSES[idx][d] - CLOSES[idx][pd] if pd else None
        status = ("complete" if have == 22 and pairs == 22 else
                  "partial" if have > 0 else "nodata")
        if status == "complete":
            complete += 1
        elif status == "partial":
            partial += 1
        else:
            nodata += 1
        rows_out.append({
            "date": d, "expiry": exp, "spot_close": CLOSES[idx][d],
            "spot_chg_pts": (round(chg, 2) if chg is not None else None),
            "spot_chg_pct": (round(100 * chg / CLOSES[idx][pd], 3)
                             if chg is not None else None),
            "atm": a, "ce_oi": ce if have else None,
            "pe_oi": pe if have else None,
            "d_ce_oi": (round(dce, 1) if pairs else None),
            "d_pe_oi": (round(dpe, 1) if pairs else None),
            "pcr_oi": (round(pe / ce, 4) if ce else None),
            "band_contracts": have, "delta_pairs": pairs,
            "status": status})
    datasets[idx] = rows_out
    coverage[idx] = {"days": len(rows_out), "complete": complete,
                     "partial": partial, "nodata": nodata}
    with open(OUT / f"{idx.lower()}_daily_oi.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"{idx}: dataset {len(rows_out)} days — complete {complete}, "
          f"partial {partial}, nodata {nodata}", flush=True)

with open(OUT / "fetch_manifest.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["index", "expiry", "strike", "type", "status"])
    w.writerows(manifest)
(OUT / "coverage.json").write_text(json.dumps(
    {"coverage": coverage, "stopped_on_429": stopped,
     "span": [FIRST_DAY, LAST_DAY]}, indent=1))
print(f"manifest rows {len(manifest)}; stopped_on_429={stopped}")
sys.exit(2 if stopped else 0)
