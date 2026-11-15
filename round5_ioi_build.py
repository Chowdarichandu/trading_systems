#!/usr/bin/env python3
"""ROUND 5 — intraday-OI dataset build (2026-11-14).

Builds the Jan-Oct 2026 (+ Nov 2-13 counterfactual) Bank Nifty
intraday-OI dataset under the spec mapping frozen in
round5_ioi_gate_2026-11-14.md §1 BEFORE scoring:
per trading day, band = 11 strikes nearest the 10:55 spot close
(stored spot series); per band contract, baseline = first 5-min bar
(09:15), read = 10:55 bar; raw candles preserved with ALL SEVEN
fields (timestamp, OHLC, volume, OI) in round5_ioi_data/chunks/.
Resumable: a chunk file on disk is never refetched. On HTTP 429:
hard stop, progress saved, no retry (house rule).
"""
import csv, json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote
from datetime import date, timedelta

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_ioi_data"
CH = OUT / "chunks"
CH.mkdir(parents=True, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
IDXKEY = "NSE_INDEX|Nifty Bank"

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
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


# ---------------- spot (stored series, November machinery's own) ----
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
SPOT = {}
for d, bars in spot_raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
nov_bars = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
for d, bars in nov_bars.get("BANKNIFTY", {}).items():
    SPOT.setdefault(d, {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                                float(b[4])) for b in bars})
extra_fn = TR / "round4_history/spot_extra.json"
if extra_fn.exists():
    for d, bars in json.loads(extra_fn.read_text()).items():
        SPOT.setdefault(d, {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                                   float(b[4])) for b in bars})

# ---------------- day list ------------------------------------------
oi_rows = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        oi_rows[r["date"]] = r
DAYS = []  # (date, window, expiry)
for d in sorted(oi_rows):
    if "2026-01-01" <= d <= "2026-10-31":
        DAYS.append((d, "JANOCT", oi_rows[d]["expiry"]))
for d in ("2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
          "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
          "2026-11-13"):
    DAYS.append((d, "NOV", "2026-11-23"))

# ---------------- bands ----------------------------------------------
def band_of(day):
    bars = SPOT.get(day)
    if not bars or "10:55" not in bars:
        return None, None
    spot = bars["10:55"][3]
    atm = int(round(spot / 100.0)) * 100
    return spot, [atm + 100 * k for k in range(-5, 6)]

DAYINFO = {}
for d, w, exp in DAYS:
    spot, band = band_of(d)
    DAYINFO[d] = dict(window=w, expiry=exp, spot1055=spot, band=band)

# ---------------- contract keys --------------------------------------
_key_maps = {}
def key_map(exp):
    if exp in _key_maps:
        return _key_maps[exp]
    fn = OUT / f"keys_{exp}.json"
    if fn.exists():
        m = {tuple(k.split("|")): v
             for k, v in json.loads(fn.read_text()).items()}
        _key_maps[exp] = {(int(s), t): v for (s, t), v in m.items()}
        return _key_maps[exp]
    if exp < "2026-11-13":
        body = get(f"{API}/v2/expired-instruments/option/contract"
                   f"?instrument_key={quote(IDXKEY, safe='')}"
                   f"&expiry_date={exp}")
        m = {(int(float(c["strike_price"])), c["instrument_type"]):
             c["instrument_key"] for c in (body.get("data") or [])}
    else:
        rows = json.loads((TR / "daily2leg/instruments_cache.json")
                          .read_text())["rows"]
        m = {(int(float(r["strike"])), r["option_type"]): r["key"]
             for r in rows if r["name"] == "BANKNIFTY"
             and r["expiry"] == exp}
    fn.write_text(json.dumps({f"{s}|{t}": v for (s, t), v in m.items()}))
    _key_maps[exp] = m
    return m

# ---------------- fetch plan ------------------------------------------
# needed[(exp, strike, typ)] = sorted set of days
needed = {}
for d, info in DAYINFO.items():
    if info["band"] is None:
        continue
    for s in info["band"]:
        for t in ("CE", "PE"):
            needed.setdefault((info["expiry"], s, t), set()).add(d)

def chunks_for(exp, days):
    """Split a contract's needed days into <=30-day fetch windows."""
    days = sorted(days)
    out, start = [], days[0]
    prev = days[0]
    for d in days[1:]:
        if (date.fromisoformat(d) - date.fromisoformat(start)).days > 30:
            out.append((start, prev))
            start = d
        prev = d
    out.append((start, prev))
    return out

PLAN = []  # (chunk_id, exp, strike, typ, frm, to)
for (exp, s, t), days in sorted(needed.items()):
    if exp < "2026-11-13":
        for frm, to in chunks_for(exp, days):
            PLAN.append((f"{exp}_{s}{t}_{frm}_{to}", exp, s, t, frm, to))
    else:
        for d in sorted(days):
            PLAN.append((f"{exp}_{s}{t}_{d}_{d}", exp, s, t, d, d))
print(f"plan: {len(needed)} contracts, {len(PLAN)} chunks", flush=True)

progress_fn = OUT / "progress.json"
progress = {"chunks_total": len(PLAN), "chunks_done": 0,
            "failed_chunks": [], "rate_limited": False,
            "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
if progress_fn.exists():
    old = json.loads(progress_fn.read_text())
    progress["failed_chunks"] = old.get("failed_chunks", [])

def save_progress():
    progress_fn.write_text(json.dumps(progress, indent=1))

todo = []
for cid, exp, s, t, frm, to in PLAN:
    fn = CH / f"chunk_{cid}.json"
    if fn.exists():
        progress["chunks_done"] += 1
    else:
        todo.append((cid, exp, s, t, frm, to, fn))
print(f"already cached: {progress['chunks_done']}; to fetch: {len(todo)}",
      flush=True)
save_progress()

try:
    for i, (cid, exp, s, t, frm, to, fn) in enumerate(todo):
        key = key_map(exp).get((s, t))
        if not key:
            fn.write_text(json.dumps({"data": {"candles": []},
                                      "missing_key": True}))
            progress["failed_chunks"].append(cid + ":no_key")
            progress["chunks_done"] += 1
            continue
        if exp < "2026-11-13":
            url = (f"{API}/v2/expired-instruments/historical-candle/"
                   f"{quote(key, safe='')}/5minute/{to}/{frm}")
        else:
            url = (f"{API}/v3/historical-candle/{quote(key, safe='')}"
                   f"/minutes/5/{to}/{frm}")
        try:
            body = get(url)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimited()
            body = {"data": {"candles": []}, "http_error": e.code}
            progress["failed_chunks"].append(f"{cid}:http{e.code}")
        fn.write_text(json.dumps(body))
        progress["chunks_done"] += 1
        if i % 50 == 49:
            save_progress()
            print(f"fetched {progress['chunks_done']}/{len(PLAN)}",
                  flush=True)
        time.sleep(0.2)
except RateLimited:
    progress["rate_limited"] = True
    save_progress()
    print("RATE_LIMIT_STOP — build halted, progress saved", flush=True)
    sys.exit(3)
save_progress()
print("fetch complete", flush=True)

# ---------------- aggregate -------------------------------------------
_cache = {}
def contract_bars(exp, s, t):
    """{(date): {time: (o,h,l,c,vol,oi)}} from cached chunks."""
    ck = (exp, s, t)
    if ck in _cache:
        return _cache[ck]
    days = {}
    for fn in sorted(CH.glob(f"chunk_{exp}_{s}{t}_*.json")):
        body = json.loads(fn.read_text())
        for c in ((body.get("data") or {}).get("candles") or []):
            days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                float(c[5]), float(c[6]))
    _cache[ck] = days
    return days

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

rows = []
for d, info in DAYINFO.items():
    base = dict(date=d, window=info["window"], expiry=info["expiry"],
                spot1055=info["spot1055"],
                atm=(int(round(info["spot1055"] / 100.0)) * 100
                     if info["spot1055"] else ""))
    if info["band"] is None:
        rows.append({**base, "status": "NC_NO_SPOT", "nc_detail": "no 10:55 spot bar"})
        continue
    agg = {s: dict(doi=0.0, pb=0.0, pr=0.0) for s in ("CE", "PE")}
    missing = []
    for s in info["band"]:
        for t in ("CE", "PE"):
            bars = contract_bars(info["expiry"], s, t).get(d, {})
            b0, b1 = bars.get("09:15"), bars.get("10:55")
            if b0 is None or b1 is None:
                missing.append(f"{s}{t}:{'base' if b0 is None else ''}"
                               f"{'read' if b1 is None else ''}")
                continue
            agg[t]["doi"] += b1[5] - b0[5]
            agg[t]["pb"] += b0[3]
            agg[t]["pr"] += b1[3]
    if missing:
        rows.append({**base, "status": "NC_BAND",
                     "nc_detail": ";".join(missing[:6]),
                     "n_missing": len(missing)})
        continue
    ce, pe = agg["CE"], agg["PE"]
    rows.append({**base, "status": "complete",
                 "ce_doi": ce["doi"], "pe_doi": pe["doi"],
                 "ce_p_base": round(ce["pb"], 2),
                 "ce_p_read": round(ce["pr"], 2),
                 "ce_dp": round(ce["pr"] - ce["pb"], 2),
                 "pe_p_base": round(pe["pb"], 2),
                 "pe_p_read": round(pe["pr"], 2),
                 "pe_dp": round(pe["pr"] - pe["pb"], 2),
                 "ce_q": quadrant(ce["doi"], ce["pr"] - ce["pb"]),
                 "pe_q": quadrant(pe["doi"], pe["pr"] - pe["pb"]),
                 "nc_detail": ""})

fields = ["date", "window", "expiry", "spot1055", "atm", "status",
          "ce_doi", "pe_doi", "ce_p_base", "ce_p_read", "ce_dp",
          "pe_p_base", "pe_p_read", "pe_dp", "ce_q", "pe_q",
          "n_missing", "nc_detail"]
with open(TR / "round5_ioi_dataset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print("dataset:", Counter((r["window"], r["status"]) for r in rows),
      flush=True)
print("BUILD DONE", flush=True)
