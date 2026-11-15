#!/usr/bin/env python3
"""NIFTY WEEKLY-EXPIRY CHAIN BACKFILL (2026-11-12) — Family B data build.

Spec: invention_round_2026-11-12.md §3. For each of the 33 Nifty weekly
expiry days Jan-Oct 2026 (nifty_engine_run3_expiries.json minus the 10
monthly expiries = last expiry of each month), fetch historical 5-min
candles for the expiring weekly contract at every 50-pt strike in the
band [floor((spot_low-100)/50)*50, ceil((spot_high+100)/50)*50] (spot
high/low from data/full_hist/NIFTY/spot_daily.csv, verified against the
5m spot store), both CE and PE. 760 contract-day files total.

Route: identical to nifty_engine_run3_fetch_weekly.py (expired-instruments
option/contract + historical-candle, browser User-Agent per standing fix).
Token read from upstox_refresh/.env, never printed.

Output: nifty_weekly_expiry_chain/candles_NIFTY_<strike><CE|PE>_<day>_<day>.json
(raw API body, the standard store format) + manifest.csv (all 760 planned
rows, status updated incrementally) + BUILD_REPORT.md.

On HTTP 429: HARD STOP the whole build, manifest + partial report are
written, exit code 2. No retries, no route switch. Re-running resumes
from the manifest (OK rows skipped, everything else re-attempted).
"""
import csv, json, math, sys, time
import urllib.request, urllib.error
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "nifty_weekly_expiry_chain"
HP = TR / "historical_proof_data"
MANIFEST = OUT / "manifest.csv"
REPORT = OUT / "BUILD_REPORT.md"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
IDX = quote("NSE_INDEX|Nifty 50", safe='')

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token

STOP = {"hit": False, "where": None}

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
        "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

# ---------- plan ----------
exps = [d for d in json.loads((TR / "nifty_engine_run3_expiries.json").read_text())
        if "2026-01-01" <= d <= "2026-10-31"]
bymonth = defaultdict(list)
for d in exps:
    bymonth[d[:7]].append(d)
monthly = sorted(v[-1] for v in bymonth.values())
WEEKLY = sorted(d for d in exps if d not in monthly)
assert len(WEEKLY) == 33, len(WEEKLY)

import pandas as pd
sd = pd.read_csv(TR / "data/full_hist/NIFTY/spot_daily.csv").set_index("date")

PLAN = []  # (date, strike, type, spot_low, spot_high)
for day in WEEKLY:
    lo, hi = float(sd.loc[day, "low"]), float(sd.loc[day, "high"])
    k0 = math.floor((lo - 100) / 50) * 50
    k1 = math.ceil((hi + 100) / 50) * 50
    for strike in range(k0, k1 + 1, 50):
        for typ in ("CE", "PE"):
            PLAN.append((day, strike, typ, lo, hi))
assert len(PLAN) == 760, len(PLAN)
print(f"plan: {len(WEEKLY)} weekly days, {len(PLAN)} contract-days", flush=True)

# ---------- manifest ----------
FIELDS = ["date", "strike", "type", "status", "reason", "bars", "file"]
OUT.mkdir(exist_ok=True)
state = {}
if MANIFEST.exists():
    for row in csv.DictReader(MANIFEST.open()):
        state[(row["date"], int(row["strike"]), row["type"])] = row
for (day, strike, typ, lo, hi) in PLAN:
    state.setdefault((day, strike, typ),
                     dict(date=day, strike=strike, type=typ, status="PENDING",
                          reason="", bars="", file=""))

def save_manifest():
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for (day, strike, typ, lo, hi) in PLAN:
            w.writerow(state[(day, strike, typ)])

def fname(day, strike, typ):
    return f"candles_NIFTY_{strike}{typ}_{day}_{day}.json"

# ---------- contracts (proven route, cached like the original) ----------
contracts_cache = {}
def weekly_key(wexp, strike, typ):
    if wexp not in contracts_cache:
        p = HP / f"contracts_NIFTY_{wexp}.json"
        if p.exists():
            data = json.loads(p.read_text()).get("data") or []
        else:
            body = get(f"https://api.upstox.com/v2/expired-instruments/option/contract"
                       f"?instrument_key={IDX}&expiry_date={wexp}")
            data = body.get("data") or []
            p.write_text(json.dumps(body))
            time.sleep(0.35)
        contracts_cache[wexp] = data
    hits = [c for c in contracts_cache[wexp] if float(c["strike_price"]) == float(strike)
            and c["instrument_type"] == typ]
    weekly = [c for c in hits if c.get("weekly") is True]
    pick = weekly[0] if weekly else (hits[0] if hits else None)
    return pick["instrument_key"] if pick else None

# ---------- build ----------
done = skipped = 0
for (day, strike, typ, lo, hi) in PLAN:
    row = state[(day, strike, typ)]
    if row["status"] == "OK" and (OUT / fname(day, strike, typ)).exists():
        skipped += 1
        continue
    if STOP["hit"]:
        break
    try:
        key = weekly_key(day, strike, typ)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            STOP.update(hit=True, where=f"contract list {day}")
            break
        row.update(status="MISSING", reason=f"contract list HTTP {e.code}", bars="")
        save_manifest(); continue
    if not key:
        row.update(status="MISSING", reason="NO_KEY (no expired weekly contract for strike/type)", bars="")
        save_manifest(); continue
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{quote(key, safe='')}/5minute/{day}/{day}")
    try:
        body = get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            STOP.update(hit=True, where=f"candle {day} {strike}{typ}")
            break
        row.update(status="MISSING", reason=f"HTTP {e.code}", bars="")
        save_manifest()
        print("HTTP", e.code, day, strike, typ, flush=True); continue
    rows = [c for c in ((body.get("data") or {}).get("candles") or []) if c[0][:10] == day]
    if not rows:
        row.update(status="MISSING", reason="EMPTY (API returned no candles for this contract-day)", bars=0)
        save_manifest()
        print("EMPTY", day, strike, typ, flush=True); continue
    (OUT / fname(day, strike, typ)).write_text(json.dumps(body))
    row.update(status="OK", reason="", bars=len(rows), file=fname(day, strike, typ))
    done += 1
    save_manifest()
    if done % 50 == 0:
        print(f"progress: {done} fetched this run, {skipped} resumed OK", flush=True)
    time.sleep(0.35)
save_manifest()

# ---------- cross-validation vs the 15 pre-existing files ----------
import glob, re
val = []
for f in glob.glob(str(TR / "aggressive_data/candles_NIFTY_*.json")):
    m = re.match(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json",
                 Path(f).name)
    if m and m.group(3) == m.group(4) and m.group(3) in WEEKLY:
        day, strike, typ = m.group(3), int(m.group(1)), m.group(2)
        newp = OUT / fname(day, strike, typ)
        if not newp.exists():
            val.append((day, strike, typ, "NOT_FETCHED", ""))
            continue
        old = (json.loads(Path(f).read_text()).get("data") or {}).get("candles") or []
        new = (json.loads(newp.read_text()).get("data") or {}).get("candles") or []
        oldm = {c[0]: c[1:] for c in old}
        newm = {c[0]: c[1:] for c in new}
        common = set(oldm) & set(newm)
        diffs = [ts for ts in common if oldm[ts] != newm[ts]]
        status = "IDENTICAL" if (len(old) == len(new) and not diffs and set(oldm) == set(newm)) else "MISMATCH"
        val.append((day, strike, typ, status,
                    f"old {len(old)} bars, new {len(new)} bars, common {len(common)}, differing {len(diffs)}"
                    + (f", first diff {diffs[0]}: old {oldm[diffs[0]]} vs new {newm[diffs[0]]}" if diffs else "")))

# ---------- report ----------
ok = [r for r in state.values() if r["status"] == "OK"]
miss = [r for r in state.values() if r["status"] == "MISSING"]
pend = [r for r in state.values() if r["status"] == "PENDING"]
lines = ["# Nifty Weekly-Expiry Chain — Build Report", ""]
if STOP["hit"]:
    lines += [f"**STOPPED BY UPSTOX HTTP 429** at: {STOP['where']}. "
              f"Coverage so far: {len(ok)}/760. Resume by re-running the build script; "
              f"the manifest holds the exact resume point ({len(pend)} rows still PENDING).", ""]
lines += [f"- Weekly expiry days: 33 (Jan–Oct 2026; monthly expiries excluded: {', '.join(monthly)})",
          f"- Planned contract-days: 760",
          f"- Fetched OK: **{len(ok)}** (this run {done}, resumed from prior manifest {skipped})",
          f"- MISSING: {len(miss)}",
          f"- PENDING (not yet attempted): {len(pend)}",
          f"- Band rule: strikes = 50-pt grid from floor((spot low − 100)/50)·50 to "
          f"ceil((spot high + 100)/50)·50, spot from data/full_hist/NIFTY/spot_daily.csv "
          f"(verified identical to the 5m spot store on sampled days).", ""]
if miss:
    lines += ["## MISSING contract-days", ""]
    for r in sorted(miss, key=lambda r: (r["date"], int(r["strike"]), r["type"])):
        lines.append(f"- {r['date']} {r['strike']}{r['type']} — {r['reason']}")
    lines.append("")
lines += ["## Cross-validation vs pre-existing store (the 15 already-covered contract-days)", ""]
for (day, strike, typ, status, detail) in sorted(val):
    lines.append(f"- {day} {strike}{typ}: **{status}** — {detail}")
vm = [v for v in val if v[3] == "MISMATCH"]
lines += ["", f"Validation summary: {sum(1 for v in val if v[3]=='IDENTICAL')}/{len(val)} identical, "
          f"{len(vm)} mismatched."]
REPORT.write_text("\n".join(lines) + "\n")
print(f"DONE ok={len(ok)}/760 missing={len(miss)} pending={len(pend)} "
      f"validation: {sum(1 for v in val if v[3]=='IDENTICAL')}/{len(val)} identical", flush=True)
if STOP["hit"]:
    print(f"429 STOP at {STOP['where']}", flush=True)
    sys.exit(2)
