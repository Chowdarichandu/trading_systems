#!/usr/bin/env python3
"""STOCK OPTIONS — FETCH (SPEC stock_options_SPEC.md s.3-s.5).
Stage 1: expiry discovery + expired-contract lists per stock-month.
Stage 2: premium candles for every selected contract (daily ranges for
sources (a)/(b); 5-minute day files for CAP exits and source (c)).
All responses cached under stock_options_data/; resumable — cached items
are never re-fetched. Browser User-Agent on every call. Token from
upstox_refresh/.env, never printed. Pacing >= 0.4s. On HTTP 429:
hard-stop the attempt (exit 3). Token check failure: exit 2 before any
data call. Research only; places no orders."""
import csv, json, os, sys, time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

WS = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(WS))
import stock_options_common as C

DATA = C.DATA
DATA.mkdir(exist_ok=True)
BASE = "https://api.upstox.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
PACE = 0.45
_last = [0.0]

def _token():
    for line in (WS / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no UPSTOX_ACCESS_TOKEN in .env")

TOK = _token()
EQ = C.eq_keys()

class RateLimited(Exception):
    pass

def get(path):
    wait = PACE - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = Request(BASE + path, headers={"Accept": "application/json",
                  "Authorization": f"Bearer {TOK}", "User-Agent": UA})
    try:
        with urlopen(req, timeout=30) as r:
            _last[0] = time.time()
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        _last[0] = time.time()
        if e.code == 429:
            raise RateLimited(path)
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}

# ---------------- stage 1: discovery ----------------
_exp_fn = DATA / "expiries.json"
EXPIRIES = json.loads(_exp_fn.read_text()) if _exp_fn.exists() else {}
_endpoint_dead = [False]

def _save_exp():
    _exp_fn.write_text(json.dumps(EXPIRIES, indent=1))

def _last_weekday(year, month, weekday):
    d = (date(year, 12, 31) if month == 12
         else date(year, month + 1, 1) - timedelta(days=1))
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d

def probe_contracts(sym, expiry):
    fn = DATA / f"contracts_{sym}_{expiry}.json"
    if fn.exists():
        return True
    s, body = get("/v2/expired-instruments/option/contract?"
                  f"instrument_key={quote(EQ[sym], safe='')}"
                  f"&expiry_date={expiry}")
    data = body.get("data") if isinstance(body, dict) else None
    if isinstance(data, dict):
        data = data.get("contracts") or data.get("data") or []
    if s == 200 and data:
        fn.write_text(json.dumps(data))
        return True
    return False

# Live (not-yet-expired) contracts: the index premium builds used the v3
# route for the then-current expiry (premium_fetch_oct.py kind="v3"); the
# same fallback applies here for the 2026-11 expiry, still live today.
LIVE_KEYS = set()
LIVE_ROWS = []
with open(WS / "november_shadow_data/instruments_NSE.csv") as _f:
    for _r in csv.DictReader(_f):
        if _r["exchange"] == "NSE_FO":
            LIVE_KEYS.add(_r["instrument_key"])
            LIVE_ROWS.append(_r)

def live_contracts_for(sym, expiry):
    import re
    out = []
    for r in LIVE_ROWS:
        if r["expiry"] != expiry or r["instrument_type"] != "OPTSTK":
            continue
        m = re.match(r"^([A-Z&]+)\d{2}[A-Z]{3}[\d.]+(CE|PE)$",
                     r["tradingsymbol"])
        if m and m.group(1) == sym:
            out.append(dict(name=sym, segment="NSE_FO", exchange="NSE",
                            expiry=expiry, instrument_key=r["instrument_key"],
                            trading_symbol=r["tradingsymbol"],
                            lot_size=float(r["lot_size"]),
                            instrument_type=r["option_type"],
                            strike_price=float(r["strike"])))
    return out

def discover_expiry(sym, year, month):
    key = f"{sym}|{year}-{month:02d}"
    if key in EXPIRIES:
        return EXPIRIES[key]
    found = None
    if not _endpoint_dead[0]:
        s, body = get("/v2/expired-instruments/option/expiries?"
                      f"instrument_key={quote(EQ[sym], safe='')}")
        data = body.get("data") if isinstance(body, dict) else None
        if s == 200 and isinstance(data, list) and data:
            for e in data:
                if isinstance(e, str) and len(e) == 10:
                    EXPIRIES[f"{sym}|{e[:7]}"] = e
            _save_exp()
            return EXPIRIES.get(key)
        _endpoint_dead[0] = True
    cands = []
    # exchange-wide calendar: if any stock already found this month's
    # expiry, probe that exact date first (monthly expiry is one date
    # for all stocks).
    cal = [v for k2, v in EXPIRIES.items()
           if v and k2.split("|")[1] == f"{year}-{month:02d}"]
    if cal:
        cands.append(date.fromisoformat(sorted(cal)[0]))
    cands += [_last_weekday(year, month, 1), _last_weekday(year, month, 3)]
    base = _last_weekday(year, month, 1)
    cands += [base + timedelta(days=sh) for sh in (-1, -2, -3, 1, -4, 2)]
    seen = set()
    for d in cands:
        if d in seen or d.month != month:
            continue
        seen.add(d)
        if probe_contracts(sym, d.isoformat()):
            found = d.isoformat()
            break
    if found is None:
        # not-yet-expired month (e.g. 2026-11): take the expiry the live
        # instrument master itself lists for this symbol-month (the last
        # Tuesday can shift for holidays — 2026-11 lists 2026-11-23);
        # v3 route serves its candles (house method).
        import re as _re
        live_exps = sorted({
            r["expiry"] for r in LIVE_ROWS
            if r["instrument_type"] == "OPTSTK"
            and r["expiry"][:7] == f"{year}-{month:02d}"
            and _re.match(r"^([A-Z&]+)\d{2}[A-Z]{3}[\d.]+(CE|PE)$",
                          r["tradingsymbol"])
            and _re.match(r"^([A-Z&]+)\d{2}[A-Z]{3}[\d.]+(CE|PE)$",
                          r["tradingsymbol"]).group(1) == sym})
        for le in live_exps:
            if le < date.today().isoformat():
                continue
            live = live_contracts_for(sym, le)
            if live:
                fn = DATA / f"contracts_{sym}_{le}.json"
                fn.write_text(json.dumps(live))
                found = le
                print(f"  live expiry used for {sym} {year}-{month:02d}: "
                      f"{found} ({len(live)} contracts)")
                break
    EXPIRIES[key] = found
    _save_exp()
    return found

# ---------------- stage 2: candles ----------------
def fetch_daily(exp_key, frm, to):
    fn = DATA / f"daily_{exp_key.replace('|', '_')}.json"
    if fn.exists():
        store = json.loads(fn.read_text())
        if store.get("_range") == [frm, to]:
            return
    if exp_key in LIVE_KEYS:
        s, body = get(f"/v3/historical-candle/{quote(exp_key, safe='')}"
                      f"/days/1/{to}/{frm}")
    else:
        s, body = get(f"/v2/expired-instruments/historical-candle/"
                      f"{quote(exp_key, safe='')}/day/{to}/{frm}")
    rows = (body.get("data") or {}).get("candles") if isinstance(body, dict) else None
    if s != 200:
        print(f"  daily FAILED (HTTP {s}), not cached: {exp_key} {frm}..{to}")
        return
    candles = {}
    for c in rows or []:
        candles[c[0][:10]] = [float(c[1]), float(c[2]), float(c[3]),
                              float(c[4])]
    fn.write_text(json.dumps({"_range": [frm, to], "candles": candles}))
    if not candles:
        print(f"  daily empty: {exp_key} {frm}..{to} (HTTP {s})")

def fetch_m5(exp_key, day):
    fn = DATA / f"m5_{exp_key.replace('|', '_')}_{day}.json"
    if fn.exists():
        return
    if exp_key in LIVE_KEYS:
        s, body = get(f"/v3/historical-candle/{quote(exp_key, safe='')}"
                      f"/minutes/5/{day}/{day}")
    else:
        s, body = get(f"/v2/expired-instruments/historical-candle/"
                      f"{quote(exp_key, safe='')}/5minute/{day}/{day}")
    rows = (body.get("data") or {}).get("candles") if isinstance(body, dict) else None
    if s != 200:
        print(f"  m5 FAILED (HTTP {s}), not cached: {exp_key} {day}")
        return
    out = [[c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
            float(c[4])] for c in rows or []]
    fn.write_text(json.dumps(out))

def main():
    s, _ = get("/v2/user/profile")
    if s != 200:
        print(f"BLOCKED_TOKEN: profile check HTTP {s}; no data calls made.")
        return 2
    print("token OK")
    # purge pre-live-path None discoveries for not-yet-expired months
    stale = [k for k, v in EXPIRIES.items()
             if v is None and k.split("|")[1] >= "2026-11"]
    for k in stale:
        del EXPIRIES[k]
    if stale:
        _save_exp()
        print(f"purged {len(stale)} stale future-month None expiries")
    rows = list(csv.DictReader(open(WS / "stock_options_trades.csv")))
    pend = [r for r in rows if r["status"] == "PENDING_FETCH"]
    print(f"trades pending fetch: {len(pend)}")
    try:
        months = {}
        for r in pend:
            ed = date.fromisoformat(r["entry_date"])
            ms = {(ed.year, ed.month)}
            nm = ed.replace(day=1) + timedelta(days=32)
            ms.add((nm.year, nm.month))
            months.setdefault(r["sym"], set()).update(ms)
        for sym in sorted(months):
            for (y, m) in sorted(months[sym]):
                e = discover_expiry(sym, y, m)
                print(f"expiry {sym} {y}-{m:02d}: {e}")
        # selection -> candle plan
        plan_daily, plan_m5 = {}, set()
        nosel = 0
        for r in pend:
            sel, reason = C.choose_contract(r, EXPIRIES)
            if sel is None:
                nosel += 1
                continue
            if r["source"] in ("EKAM2C", "HOLD"):
                frm = r["entry_date"]
                to = max(r["exit_date"], sel["expiry"])
                plan_daily[sel["key"]] = (
                    min(plan_daily.get(sel["key"], (frm, to))[0], frm),
                    max(plan_daily.get(sel["key"], (frm, to))[1], to))
                if r["cash_exit_kind"] == "CAP":
                    plan_m5.add((sel["key"], r["exit_date"]))
            else:  # source (c): intraday — 5-min for the trade day
                plan_m5.add((sel["key"], r["entry_date"]))
        print(f"selection: {len(pend) - nosel} ok, {nosel} no-contract; "
              f"daily pulls {len(plan_daily)}, 5-min pulls {len(plan_m5)}")
        for key, (frm, to) in sorted(plan_daily.items()):
            fetch_daily(key, frm, to)
        for key, day in sorted(plan_m5):
            fetch_m5(key, day)
    except RateLimited:
        print("RATE_LIMITED: attempt hard-stopped; cache kept. "
              "Unfetched trades score as NC RATE_LIMITED for this attempt.")
        return 3
    print("fetch complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
