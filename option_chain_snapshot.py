#!/usr/bin/env python3
"""Option-chain snapshot archiver + build-up classifier (started 2026-11-13).

Pulls the full front-expiry Bank Nifty + Nifty option chains from the Upstox
API and appends one row per strike to dated CSVs under
~/workspace/trading/option_chain_archive/.

Usage:
    python3 option_chain_snapshot.py            # snapshot + archive + classify vs prev close
    python3 option_chain_snapshot.py --classify # re-classify latest archived snapshot of today

Design rules:
- Token read from ~/workspace/trading/upstox_refresh/.env, never printed.
- Browser User-Agent on every api.upstox.com call (a 403 without it is a
  Cloudflare header problem, not a token failure).
- HTTP 429 = hard stop: nothing is written, exit code 3, message printed.
- Idempotent per 5-minute bucket (IST): re-invoking inside a bucket that is
  already archived for an index writes nothing for that index.
- Tolerant of missing strikes/sides: absent market data becomes empty cells.
Paper/research only. No orders are placed by this script.
"""
import csv, gzip, io, json, sys
import urllib.request, urllib.error, urllib.parse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
API = "https://api.upstox.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
ROOT = Path.home() / "workspace/trading"
ENV_FILE = ROOT / "upstox_refresh/.env"
ARCHIVE = ROOT / "option_chain_archive"
MASTER_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
INDEXES = {  # label -> (instrument master name, index instrument key, file tag)
    "BANKNIFTY": ("BANKNIFTY", "NSE_INDEX|Nifty Bank", "banknifty"),
    "NIFTY": ("NIFTY", "NSE_INDEX|Nifty 50", "nifty"),
}
COLS = ["timestamp_ist", "bucket_ist", "index", "expiry", "strike", "spot",
        "ce_oi", "ce_prev_oi", "ce_ltp", "ce_close", "ce_volume",
        "pe_oi", "pe_prev_oi", "pe_ltp", "pe_close", "pe_volume", "row_pcr"]


class RateLimited(Exception):
    pass


def load_token():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("UPSTOX_ACCESS_TOKEN not found in .env")


def get_json(url, token, accept="application/json"):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        raise RuntimeError(f"HTTP {e.code} for {url.split('?')[0]}: "
                           f"{e.read()[:200]!r}")


def get_raw(url, accept):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        raise RuntimeError(f"HTTP {e.code} for master download")


def front_expiries(token, today):
    """Front (nearest live) expiry per index, from the instrument master,
    cached per calendar day inside the archive dir."""
    cache = ARCHIVE / "_front_expiry_cache.json"
    if cache.exists():
        try:
            c = json.loads(cache.read_text())
            if c.get("date") == today:
                return c["front"]
        except Exception:
            pass
    raw = get_raw(MASTER_URL, "application/gzip")
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(raw).decode())))
    front = {}
    for label, (name, _key, _tag) in INDEXES.items():
        exps = sorted({r["expiry"] for r in rows
                       if r.get("instrument_type") == "OPTIDX"
                       and r.get("name") == name and r.get("expiry")
                       and r["expiry"] >= today})
        if exps:
            front[label] = exps[0]
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"date": today, "front": front}))
    return front


def fetch_chain(token, index_key, expiry):
    url = (f"{API}/v2/option/chain?instrument_key="
           f"{urllib.parse.quote(index_key, safe='')}&expiry_date={expiry}")
    data = get_json(url, token)
    return data.get("data") or []


def bucket_of(dt):
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)


def side_md(row, side):
    leg = row.get(side) or {}
    return leg.get("market_data") or {}


def chain_to_rows(label, expiry, chain, ts, bucket):
    out = []
    for row in sorted(chain, key=lambda r: float(r.get("strike_price") or 0)):
        ce, pe = side_md(row, "call_options"), side_md(row, "put_options")
        out.append({
            "timestamp_ist": ts.isoformat(),
            "bucket_ist": bucket.isoformat(),
            "index": label, "expiry": expiry,
            "strike": row.get("strike_price"),
            "spot": row.get("underlying_spot_price"),
            "ce_oi": ce.get("oi"), "ce_prev_oi": ce.get("prev_oi"),
            "ce_ltp": ce.get("ltp"), "ce_close": ce.get("close_price"),
            "ce_volume": ce.get("volume"),
            "pe_oi": pe.get("oi"), "pe_prev_oi": pe.get("prev_oi"),
            "pe_ltp": pe.get("ltp"), "pe_close": pe.get("close_price"),
            "pe_volume": pe.get("volume"),
            "row_pcr": row.get("pcr"),
        })
    return out


def already_archived(path, bucket_iso, label):
    if not path.exists():
        return False
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r.get("bucket_ist") == bucket_iso and r.get("index") == label:
                return True
    return False


def append_rows(path, rows):
    new_file = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})


# ---------------------------------------------------------------- classifier
def classify_buildup(price_change, oi_change):
    """The four build-up quadrants from price change + OI change.
    price up + OI up      -> LONG_BUILDUP
    price down + OI up    -> SHORT_BUILDUP
    price down + OI down  -> LONG_UNWINDING
    price up + OI down    -> SHORT_COVERING
    either change zero/missing -> FLAT_OR_UNKNOWN"""
    if price_change is None or oi_change is None:
        return "FLAT_OR_UNKNOWN"
    if price_change == 0 or oi_change == 0:
        return "FLAT_OR_UNKNOWN"
    if price_change > 0:
        return "LONG_BUILDUP" if oi_change > 0 else "SHORT_COVERING"
    return "SHORT_BUILDUP" if oi_change > 0 else "LONG_UNWINDING"


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def classify_vs_prev_close(rows):
    """Per-strike + index-aggregate build-up using the baseline embedded in
    the chain itself: oi vs prev_oi and ltp vs close_price (i.e. the last
    completed session's change vs the session before it)."""
    per_strike, counts = [], {}
    agg = {"ce_doi": 0.0, "pe_doi": 0.0, "ce_oi": 0.0, "pe_oi": 0.0}
    for r in rows:
        ce_p = _f(r["ce_ltp"]) - _f(r["ce_close"]) if _f(r["ce_ltp"]) is not None and _f(r["ce_close"]) is not None else None
        ce_o = _f(r["ce_oi"]) - _f(r["ce_prev_oi"]) if _f(r["ce_oi"]) is not None and _f(r["ce_prev_oi"]) is not None else None
        pe_p = _f(r["pe_ltp"]) - _f(r["pe_close"]) if _f(r["pe_ltp"]) is not None and _f(r["pe_close"]) is not None else None
        pe_o = _f(r["pe_oi"]) - _f(r["pe_prev_oi"]) if _f(r["pe_oi"]) is not None and _f(r["pe_prev_oi"]) is not None else None
        ce_q, pe_q = classify_buildup(ce_p, ce_o), classify_buildup(pe_p, pe_o)
        for q in (ce_q, pe_q):
            counts[q] = counts.get(q, 0) + 1
        if ce_o is not None:
            agg["ce_doi"] += ce_o
        if pe_o is not None:
            agg["pe_doi"] += pe_o
        if _f(r["ce_oi"]) is not None:
            agg["ce_oi"] += _f(r["ce_oi"])
        if _f(r["pe_oi"]) is not None:
            agg["pe_oi"] += _f(r["pe_oi"])
        per_strike.append({"strike": r["strike"], "ce": ce_q, "pe": pe_q,
                           "ce_doi": ce_o, "pe_doi": pe_o})
    agg["pcr_oi"] = (agg["pe_oi"] / agg["ce_oi"]) if agg["ce_oi"] else None
    return per_strike, counts, agg


def print_classification(label, rows):
    per_strike, counts, agg = classify_vs_prev_close(rows)
    spot = rows[0]["spot"] if rows else None
    print(f"[{label}] spot {spot} | aggregate OI change vs prev close: "
          f"CE {agg['ce_doi']:+,.0f} | PE {agg['pe_doi']:+,.0f} | "
          f"total OI CE {agg['ce_oi']:,.0f} PE {agg['pe_oi']:,.0f} | "
          f"PCR(OI) {agg['pcr_oi']:.3f}" if agg["pcr_oi"] else
          f"[{label}] aggregate unavailable")
    print(f"[{label}] per-strike quadrant counts (CE+PE legs): "
          + " | ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    near = sorted(per_strike, key=lambda x: abs(float(x["strike"]) - float(spot or 0)))[:5]
    for r in sorted(near, key=lambda x: float(x["strike"])):
        print(f"[{label}]   strike {r['strike']}: CE {r['ce']} "
              f"(dOI {r['ce_doi']:+,.0f}) | PE {r['pe']} (dOI {r['pe_doi']:+,.0f})"
              if r["ce_doi"] is not None and r["pe_doi"] is not None else
              f"[{label}]   strike {r['strike']}: CE {r['ce']} | PE {r['pe']}")
    return counts, agg


# ---------------------------------------------------------------- main
def snapshot():
    now = datetime.now(IST)
    today = now.date().isoformat()
    bucket = bucket_of(now)
    token = load_token()
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    front = front_expiries(token, today)
    fetched = {}
    try:
        for label, (_name, key, _tag) in INDEXES.items():
            exp = front.get(label)
            if not exp:
                print(f"[{label}] no front expiry found — skipped")
                continue
            fetched[label] = (exp, fetch_chain(token, key, exp))
    except RateLimited:
        print("RATE_LIMIT_STOP: HTTP 429 from Upstox — nothing written.")
        return 3
    for label, (exp, chain) in fetched.items():
        tag = INDEXES[label][2]
        path = ARCHIVE / f"{tag}_{today}.csv"
        if already_archived(path, bucket.isoformat(), label):
            print(f"[{label}] bucket {bucket.strftime('%H:%M')} already archived — skipped")
            continue
        rows = chain_to_rows(label, exp, chain, now, bucket)
        append_rows(path, rows)
        print(f"[{label}] wrote {len(rows)} strike rows (expiry {exp}) -> {path.name} "
              f"bucket {bucket.strftime('%H:%M')}")
        print_classification(label, rows)
    return 0


def classify_latest():
    today = datetime.now(IST).date().isoformat()
    for label, (_n, _k, tag) in INDEXES.items():
        path = ARCHIVE / f"{tag}_{today}.csv"
        if not path.exists():
            print(f"[{label}] no archive for {today} yet")
            continue
        rows = list(csv.DictReader(open(path, newline="")))
        latest = max(r["bucket_ist"] for r in rows)
        snap = [r for r in rows if r["bucket_ist"] == latest]
        print(f"[{label}] latest bucket {latest}: {len(snap)} strikes")
        print_classification(label, snap)
    return 0


if __name__ == "__main__":
    if "--classify" in sys.argv:
        sys.exit(classify_latest())
    sys.exit(snapshot())
