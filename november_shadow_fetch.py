#!/usr/bin/env python3
"""November shadow premium-candle fetcher (2026-11-04).

Fetches 5-minute premium candles for November 2026 index-option contracts
and caches them in the aggressive_score cache format
({"data": {"candles": [[ts, o, h, l, c, v, ...], ...]}}) under
november_shadow_data/, which the shadow scorer prepends to
aggressive_score.DIRS in-process. Frozen files are never modified.

Routes (same as the November EOD logging):
- live contracts: instruments master (NSE.csv.gz) -> instrument_key ->
  v3 historical-candle day endpoint (completed days) or v3 intraday
  endpoint (today). Browser User-Agent on every call (2026-11-02 rule).
- expired weekly contracts (e.g. NIFTY weekly expiring on the trade
  date): fallback to the expired-instruments route
  (nifty_engine_r7_fetch.fetch_jobs), which caches into aggressive_data/.

Token: read inside live_signal_producer.load_token (never printed).
Paper only, no orders.
"""
import csv, gzip, io, json, sys, time
import urllib.request, urllib.parse
from datetime import date as ddate
from pathlib import Path

TR = Path.home() / "workspace/trading"
OUT = TR / "november_shadow_data"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(TR))
import live_signal_producer as P

UA = P.UA
INSTRUMENTS_URL = ("https://assets.upstox.com/market-quote/instruments/"
                   "exchange/NSE.csv.gz")
MASTER_CACHE = OUT / "instruments_NSE.csv"


def _get_json(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def master_rows(force=False):
    """Instruments master rows (dicts) for NSE, cached for the day."""
    today = ddate.today().isoformat()
    stamp = OUT / "instruments_stamp.txt"
    if force or not MASTER_CACHE.exists() or \
            (stamp.exists() and stamp.read_text().strip() != today):
        req = urllib.request.Request(INSTRUMENTS_URL, headers={
            "Accept": "application/gzip", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        MASTER_CACHE.write_bytes(gzip.decompress(raw))
        stamp.write_text(today)
    with open(MASTER_CACHE, newline="") as f:
        return list(csv.DictReader(f))


def option_key(rows, underlying, expiry, strike, typ):
    # Upstox NSE master: index options carry instrument_type OPTIDX;
    # CE/PE is the tradingsymbol suffix.
    for r in rows:
        if (r.get("name") == underlying and r.get("expiry") == expiry
                and r.get("instrument_type") == "OPTIDX"
                and (r.get("tradingsymbol") or "").endswith(typ)
                and float(r.get("strike") or 0) == float(strike)):
            return r["instrument_key"]
    return None


def expiries_for(rows, underlying):
    return sorted({r["expiry"] for r in rows
                   if r.get("name") == underlying and r.get("expiry")})


def cache_path(sym, strike, typ, day, exp):
    return OUT / f"candles_{sym}_{int(strike)}{typ}_{day}_{exp}.json"


SHARED_DIR = TR / "oi_buildup_data"


def shared_path(sym, strike, typ, day, exp):
    """The shared research-cache convention (oi_buildup_data/,
    expiry before day) — the filename read by
    oi_buildup_score.store_bars, the regime gate's prem_store
    folder fallback and the forward shadow scorers."""
    return SHARED_DIR / f"candles_{sym}_{int(strike)}{typ}_{exp}_{day}.json"


def mirror_shared(sym, strike, typ, day, exp, body):
    """PREMIUM PERSISTENCE FIX (scenario-proofing Item 2,
    2026-11-14): every premium series this fetcher holds is ALSO
    written under the shared cache convention, so the candles the
    November machinery fetches for scoring survive in the one
    store every other consumer reads. Until this fix the series
    lived only under this module's day-before-expiry filename in
    november_shadow_data/ — invisible to the shared convention,
    which is why later gates reported 'no premium store' for
    contracts the machinery had in fact fetched (verified
    2026-11-14: BANKNIFTY 60800PE 2026-11-13 was cached here yet
    store_bars returned None). Write-once: an existing shared
    file is never overwritten. Fetch layer only — no book logic,
    no ledger format, no job timing changes."""
    try:
        sp = shared_path(sym, strike, typ, day, exp)
        if sp.exists():
            return False
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if not cd:
            return False
        sp.write_text(json.dumps(body))
        return True
    except Exception:
        return False


def fetch_premium(sym, strike, typ, day, exp, token=None, rows=None):
    """Ensure candles for (sym, strike, typ, day, exp) are cached.
    Returns (status, n_bars): status in OK / OK_EXPIRED_ROUTE / NO_KEY /
    EMPTY / HTTP <code>. Never raises for a single contract."""
    p = cache_path(sym, strike, typ, day, exp)
    if p.exists():
        try:
            body0 = json.loads(p.read_text())
            data = body0.get("data", {}).get("candles", [])
            n = sum(1 for c in data if c[0][:10] == day)
            if n:
                mirror_shared(sym, strike, typ, day, exp, body0)
                return ("CACHED", n)
        except Exception:
            pass
    token = token or P.load_token()
    rows = rows if rows is not None else master_rows()
    key = option_key(rows, _underlying(sym), exp, strike, typ)
    if key:
        enc = urllib.parse.quote(key, safe="")
        today = ddate.today().isoformat()
        urls = []
        if day < today:
            urls.append(f"https://api.upstox.com/v3/historical-candle/"
                        f"{enc}/minutes/5/{day}/{day}")
        else:
            urls.append(f"https://api.upstox.com/v3/historical-candle/"
                        f"intraday/{enc}/minutes/5")
            urls.append(f"https://api.upstox.com/v3/historical-candle/"
                        f"{enc}/minutes/5/{day}/{day}")
        for url in urls:
            try:
                body = _get_json(url, token)
            except urllib.error.HTTPError as e:
                return (f"HTTP {e.code}", 0)
            except Exception as e:
                return (f"ERR {type(e).__name__}", 0)
            candles = (body.get("data") or {}).get("candles") or []
            rows_day = [c for c in candles if c[0][:10] == day]
            if rows_day:
                p.write_text(json.dumps(body))
                mirror_shared(sym, strike, typ, day, exp, body)
                return ("OK", len(rows_day))
        # fall through to expired route (contract may have just expired)
    # Expired-instruments route (NIFTY weekly sleeves; also any contract
    # the live master no longer lists).
    try:
        import nifty_engine_r7_fetch as F7
        weekly = (exp == day)
        res = F7.fetch_jobs([(int(strike), typ, day, exp, weekly)])
        (_job, (status, n)) = res[0]
        if status == "OK" and n:
            for cand in (p, TR / "aggressive_data" / p.name):
                if cand.exists():
                    try:
                        mirror_shared(sym, strike, typ, day, exp,
                                      json.loads(cand.read_text()))
                    except Exception:
                        pass
                    break
            return ("OK_EXPIRED_ROUTE", n)
        return (f"EXPIRED_ROUTE {status}", 0)
    except Exception as e:
        return (f"NO_KEY {type(e).__name__}", 0)


def _underlying(sym):
    return sym  # master "name" values are BANKNIFTY / NIFTY


def backfill_shared():
    """One-time mirror of every series already cached in
    november_shadow_data/ into the shared convention (Item 2 fix).
    Returns (mirrored, already_present, unparsed)."""
    import re
    pat = re.compile(r"^candles_([A-Z]+)_(\d+)(CE|PE)_"
                     r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json$")
    mirrored = present = unparsed = 0
    for fn in sorted(OUT.glob("candles_*.json")):
        m = pat.match(fn.name)
        if not m:
            unparsed += 1
            continue
        sym, strike, typ, day, exp = m.groups()
        if shared_path(sym, int(strike), typ, day, exp).exists():
            present += 1
            continue
        try:
            body = json.loads(fn.read_text())
        except Exception:
            unparsed += 1
            continue
        if mirror_shared(sym, int(strike), typ, day, exp, body):
            mirrored += 1
        else:
            unparsed += 1
    return mirrored, present, unparsed


if __name__ == "__main__":
    if sys.argv[1:2] == ["--backfill-shared"]:
        print("backfill:", backfill_shared())
    else:
        # manual probe: fetch_premium SYM STRIKE TYP DAY EXP
        sym, strike, typ, day, exp = sys.argv[1:6]
        print(fetch_premium(sym, int(strike), typ, day, exp))
