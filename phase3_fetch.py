#!/usr/bin/env python3
"""PHASE-3 BUILDUP NIFTY - DATA COMPLETION FETCH (2026-11-14).

Fetches, via the expired-instruments route (browser UA, 0.3s pacing):
  (1) NIFTY monthly FUTURES 7-field 5-min candles for all 11 in-force
      expiries, full traded life in <=30-day chunks ->
      phase3_buildup_data/futures/FUT7_NIFTY_<exp>_<from>_<to>.json
  (2) the near-band OPTION contract-days (11 strikes x CE/PE, band
      anchored at the 09:55 and 10:55 spot closes) for the 66 TUNED v1
      leg-days + 2026-11-03, in-force monthly expiry ->
      oi_buildup_data/candles_NIFTY_<strike><TYP>_<exp>_<day>.json
      (the shared cache convention, raw response body, exactly as
      oi_buildup_score.fetch_bars writes it).
Resumable: anything already on disk is skipped. On HTTP 429: HARD
STOP - progress written, exit 3, no retry, no route switch.
Never prints the token. Research only: no book/ledger/job touched.
"""
import csv, json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "phase3_buildup_data"
FUTDIR = OUT / "futures"
FUTDIR.mkdir(parents=True, exist_ok=True)
FETCH_DIR = TR / "oi_buildup_data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
IDXKEY = "NSE_INDEX|Nifty 50"
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
            "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
            "2026-09-29", "2026-10-27", "2026-11-23"]
PROG = OUT / "fetch_progress.json"

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


def save_prog(d):
    PROG.write_text(json.dumps(d, indent=1))


# ---------------- spot ----------------
SPOT = {}
import pandas as pd
s = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv")
s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
s["date"] = s["timestamp"].dt.strftime("%Y-%m-%d")
s["time"] = s["timestamp"].dt.strftime("%H:%M")
for d, g in s.groupby("date"):
    if len(g) >= 70:
        SPOT[d] = {r.time: float(r.close) for r in g.itertuples()}


def in_force(day):
    for e in EXPIRIES:
        if e >= day:
            return e
    return None


# ---------------- (1) futures ----------------
def fetch_futures(prog):
    # URL convention copied from round4_data_build_nifty.py (proven):
    # the range endpoints take the dates REVERSED - /5minute/{to}/{frm}.
    # Nov 2026 monthly is still live: key NSE_FO|61471 via the v3 route
    # (round4's resolution), same reversed-date shape.
    keys = json.load(open(TR / "round4_history/futures_keys_nifty.json"))
    from datetime import date, timedelta
    def pd_(x):
        y, m, dd = map(int, x.split("-"))
        return date(y, m, dd)
    todo, done = [], 0
    for exp in EXPIRIES:
        if exp == "2026-11-23":
            key, route = "NSE_FO|61471", "live"
            start, last = date(2026, 9, 25), date(2026, 11, 13)
        else:
            key, route = keys[exp]["key"], "expired"
            start, last = pd_(exp) - timedelta(days=75), pd_(exp)
        cur = start
        while cur <= last:
            end = min(cur + timedelta(days=14), last)
            fn = FUTDIR / f"FUT7_NIFTY_{exp}_{cur}_{end}.json"
            if fn.exists():
                done += 1
            else:
                todo.append((exp, key, route, str(cur), str(end), fn))
            cur = end + timedelta(days=1)
    print(f"futures chunks: {done} cached, {len(todo)} to fetch")
    for i, (exp, key, route, frm, to, fn) in enumerate(todo):
        enc = quote(key, safe="")
        if route == "expired":
            url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
                   f"/5minute/{to}/{frm}")
        else:
            url = f"{API}/v3/historical-candle/{enc}/minutes/5/{to}/{frm}"
        try:
            body = get(url)
        except RateLimited:
            prog.update(stage="futures", rate_limited=True,
                        fut_done=done + i, fut_total=done + len(todo))
            save_prog(prog)
            print("429 HARD STOP during futures fetch")
            sys.exit(3)
        fn.write_text(json.dumps(body))
        time.sleep(0.3)
        if (i + 1) % 20 == 0:
            print(f"futures {i + 1}/{len(todo)}")
    print("futures fetch complete")


# ---------------- (2) band options ----------------
def needed_option_days():
    legs = list(csv.DictReader(open(TR / "november_books_fix_repair_nifty_legs.csv")))
    days = sorted(set(r["date"] for r in legs)) + ["2026-11-03"]
    need = {}   # (exp, strike, typ, day) -> True
    for d in days:
        bars = SPOT.get(d)
        if not bars or "09:55" not in bars or "10:55" not in bars:
            print(f"WARN no spot anchors for {d}")
            continue
        exp = in_force(d)
        strikes = set()
        for anchor in (bars["09:55"], bars["10:55"]):
            atm = round(anchor / 50.0) * 50
            for k in range(-5, 6):
                strikes.add(atm + 50 * k)
        for st in strikes:
            for typ in ("CE", "PE"):
                need[(exp, st, typ, d)] = True
    return need


def cache_ok(exp, strike, typ, day):
    fn = FETCH_DIR / f"candles_NIFTY_{strike}{typ}_{exp}_{day}.json"
    if not fn.exists():
        return False
    try:
        body = json.loads(fn.read_text())
    except Exception:
        return False
    cd = [c for c in ((body.get("data") or {}).get("candles") or [])
          if c[0][:10] == day]
    times = {c[0][11:16] for c in cd}
    return "09:15" in times and "09:55" in times and "10:55" in times


def fetch_options(prog):
    need = needed_option_days()
    print(f"option contract-days needed: {len(need)}")
    keymaps = {}
    todo = []
    have = 0
    for (exp, strike, typ, day) in sorted(need, key=lambda x: (x[3], x[0], x[1], x[2])):
        if cache_ok(exp, strike, typ, day):
            have += 1
        else:
            todo.append((exp, strike, typ, day))
    print(f"already complete in cache: {have}; to fetch: {len(todo)}")
    prog.update(opt_needed=len(need), opt_have=have, opt_todo=len(todo))
    save_prog(prog)
    fetched = failed = 0
    for i, (exp, strike, typ, day) in enumerate(todo):
        if exp not in keymaps:
            kfn = OUT / f"keys_NIFTY_{exp}.json"
            if kfn.exists():
                keymaps[exp] = json.loads(kfn.read_text())
            else:
                body = get(f"{API}/v2/expired-instruments/option/contract"
                           f"?instrument_key={quote(IDXKEY, safe='')}"
                           f"&expiry_date={exp}")
                km = {}
                for c in (body.get("data") or []):
                    km[f"{int(float(c['strike_price']))}|{c['instrument_type']}"] = \
                        c["instrument_key"]
                kfn.write_text(json.dumps(km))
                keymaps[exp] = km
                time.sleep(0.3)
        key = keymaps[exp].get(f"{strike}|{typ}")
        if not key:
            failed += 1
            continue
        url = (f"{API}/v2/expired-instruments/historical-candle/"
               f"{quote(key, safe='')}/5minute/{day}/{day}")
        try:
            body = get(url)
        except RateLimited:
            prog.update(stage="options", rate_limited=True,
                        opt_fetched=fetched, opt_failed=failed,
                        opt_index=i)
            save_prog(prog)
            print(f"429 HARD STOP during options fetch at {i}/{len(todo)}")
            sys.exit(3)
        if body is None:
            failed += 1
            continue
        fn = FETCH_DIR / f"candles_NIFTY_{strike}{typ}_{exp}_{day}.json"
        fn.write_text(json.dumps(body))
        fetched += 1
        time.sleep(0.3)
        if (i + 1) % 100 == 0:
            print(f"options {i + 1}/{len(todo)} fetched={fetched} failed={failed}")
            prog.update(opt_fetched=fetched, opt_failed=failed, opt_index=i + 1)
            save_prog(prog)
    print(f"options fetch complete: fetched={fetched} failed={failed}")
    prog.update(opt_fetched=fetched, opt_failed=failed, done=True)
    save_prog(prog)


if __name__ == "__main__":
    prog = {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    save_prog(prog)
    fetch_futures(prog)
    fetch_options(prog)
    print("ALL DONE")
