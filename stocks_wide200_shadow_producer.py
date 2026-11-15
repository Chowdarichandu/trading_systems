#!/usr/bin/env python3
"""WIDE-200 SHADOW PRODUCER — SarvaRitu intraday-causal components over
the NIFTY 200 universe, run as a labelled paper SHADOW beside (never
inside) the frozen 25-stock SarvaRitu book. Owner approval 2026-11-11
17:02 IST (Bank+Nifty chat). First official live day: Thu 2026-11-12.
Paper only, real Rs0, no orders. Provisional per 100 shares, Rs40/trade
— identical money basis to the frozen book.

SIGNAL CONSTRUCTION: this file does NOT re-implement any signal logic.
It imports stocks_live_shadow_producer.py and reuses its frozen
Evaluator / due_candidates / calendar_events / comp_allowed /
scan_exit / net_of VERBATIM (the module's SYMBOLS, KEYS and load_daily
globals are rebound to the wide data layer before the Evaluator is
constructed). Only the BOOK layer is evaluated (Evaluator.step) —
components N4-V3 (T150/S080), P2F, P2F-R2, R2-LOWBAND (T125/S050).
The scorecard layer (N4-PRIMARY / P2F-SHADOW) is the 25-book's own and
is NOT run here. F4 / INV-LONG / INV-ABOVE are EOD-only sleeves in the
frozen construction and are OUT OF THIS SHADOW'S SCOPE.

ADAPTATIONS vs the 25-stock live producer (data layer only — every
signal rule, threshold, geometry and exclusion is the frozen code's):
  A1. Universe: NIFTY 200 constituents (wide200_universe_2026-11-11.csv,
      official niftyindices.com list fetched 2026-11-11) instead of the
      frozen 25. The 25 watchlist names are all inside the 200 and are
      NOT deduplicated — this shadow is its own book.
  A2. Instrument keys: constructed as NSE_EQ|<ISIN> from the official
      constituents CSV (data/wide200_keys.json). Verified at build
      time: the construction reproduces all 25 equity keys in
      data/progressive/keys.json exactly (25/25).
  A3. Daily bars: the frozen book reads the EOD logger's forward root
      (data/sarvaritu_fwd/, 25 names only). The wide producer keeps its
      own store (data/wide200_fwd/<SYM>/spot_daily.csv, same schema),
      refreshed once per day from the Upstox v2 historical daily
      endpoint (the v3 day endpoint rejects the call; v2 output was
      verified byte-identical to the forward root on TATASTEEL,
      including the 2026-11-08 session). NIFTY daily (regime input)
      is still read from the forward root, read-only, exactly as the
      frozen producer reads it.
  A4. Event calendar: the frozen book uses a hand-curated 25-name
      calendar (stocks_sarvaritu_calendar_live.csv). No systematic
      exchange-wide equivalent exists tonight: the NSE event calendar
      is forward-only, and the BSE API / Moneycontrol are blocked from
      this network. The wide calendar (stocks_wide200_calendar.csv)
      therefore ACCUMULATES: seeded with (a) the curated calendar's
      rows verbatim (full fidelity for watchlist names, incl. its one
      management_change row) and (b) the NSE event-calendar snapshot
      of 2026-11-11 (Financial Results purposes, NIFTY 200 symbols),
      and merged with a fresh NSE snapshot on the first cycle of every
      day. Reaction dates mirror the curated calendar's uniform
      convention — first trading day strictly after the event date —
      computed at runtime from the NIFTY trading calendar; curated
      rows keep their stored reaction dates. CONSEQUENCES, on record:
      (i) wide N4 reaction days arise from RESULTS events only (the
      curated calendar's SINGLE_NEWS classes are not systematically
      available for 200 names); (ii) BOOTSTRAP GAP — board dates on or
      before 2026-11-11 for non-watchlist names are not retrievable,
      so P2F-family entries in the first live days can miss events
      whose board dates fell 2026-11-09..11 outside the curated 25.
  A5. Fetch scope: the frozen producer fetches all 25 symbols every
      cycle. In the frozen step() a symbol with no due candidate, no
      N4 reaction day today and no open position is a strict no-op, so
      each wide cycle fetches intraday bars ONLY for that active set
      (mathematically identical outputs, ~8x less API load). Daily
      context for all 200 is refreshed once per day (A3). Guard
      change that follows: no_market_data is declared when every
      ACTIVE fetch is empty (the frozen book's >=20-of-25 rule does
      not scale).
  A6. Fetches run on an 8-thread pool (the frozen producer is
      sequential over 25). Any HTTP 429 from Upstox aborts the run
      immediately (hard stop) with no state/log writes.
  A7. Threshold note (NOT an adaptation — the frozen code is used as
      is): the producer's N4 trigger is a >= 1.0% 09:25-bar move; the
      adopted SarvaRitu book spec elsewhere records 0.8%. The standing
      discrepancy is noted here unresolved, exactly as instructed;
      this shadow mirrors the PRODUCER (1.0%), like the live layer
      of the frozen book does.

Outputs (all wide-labelled, never the book's files):
  stocks_wide200_shadow_state.json        open positions / entered set
  stocks_wide200_shadow_log.csv           closed trades (mode WIDE200-SHADOW)
  stocks_wide200_shadow_producer.log      every evaluation
  data/wide200_fwd/                       daily store + refresh marker
Dry-run mode (--dry-run) writes ONLY the .dryrun-suffixed state/log
and never the live record.

Modes:
  (default)        one live evaluation pass for today (IST).
  --dry-run        full pass for today against completed data, dry
                   outputs only, plus a full-universe fetch timing probe.
"""
import argparse, csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_live_shadow_producer as base

IST = ZoneInfo("Asia/Kolkata")
UA = base.UA
UNIVERSE_CSV = f"{WS}/wide200_universe_2026-11-11.csv"
KEYS_JSON = f"{WS}/data/wide200_keys.json"
FWD_WIDE = f"{WS}/data/wide200_fwd"
RAW_CAL = f"{WS}/stocks_wide200_calendar.csv"
RUNTIME_CAL = f"{WS}/stocks_wide200_calendar_runtime.csv"
CURATED_CAL = base.LIVE_CAL
STATE = f"{WS}/stocks_wide200_shadow_state.json"
STATE_DRY = f"{WS}/stocks_wide200_shadow_state.dryrun.json"
LOG = f"{WS}/stocks_wide200_shadow_log.csv"
LOG_DRY = f"{WS}/stocks_wide200_shadow_log.dryrun.csv"
PLOG = f"{WS}/stocks_wide200_shadow_producer.log"
MARKER = f"{FWD_WIDE}/_refresh.json"
DAILY_FROM = "2026-09-01"
NSE_HOME = "https://www.nseindia.com"
NSE_EVENTS = "https://www.nseindia.com/api/event-calendar?index=equities"
CAL_FIELDS = ["stock", "event_date", "event_type", "detail", "after_market",
              "source", "source_url", "reaction_date", "window_start",
              "window_end", "known_before_open", "coverage"]


class RateLimited(Exception):
    pass


def plog(msg):
    line = f"{datetime.now(IST).isoformat(timespec='seconds')} {msg}"
    with open(PLOG, "a") as f:
        f.write(line + "\n")


# ------------------------------------------------------------ universe
def load_universe():
    rdr = csv.DictReader([l for l in open(UNIVERSE_CSV) if not l.startswith("#")])
    return [r["Symbol"] for r in rdr]


WIDE = load_universe()
KEYS = json.load(open(KEYS_JSON))

# Rebind the frozen producer's data layer to the wide universe. All
# signal code (Evaluator, calendar_events, due_candidates, comp_allowed,
# scan_exit, net_of) is the frozen module's own, resolved against these
# globals at call time.
base.SYMBOLS = WIDE
base.KEYS = KEYS_JSON


def wide_load_daily(sym, upto=None):
    """Same parse/semantics as base.load_daily, over the wide store.
    NIFTY (the regime input) delegates to the frozen forward root."""
    if sym == "NIFTY":
        return base_load_daily_fwd(sym, upto=upto)
    rows = []
    p = f"{FWD_WIDE}/{sym}/spot_daily.csv"
    if not os.path.exists(p):
        return rows
    for r in csv.DictReader(open(p)):
        d = r["date"][:10]
        if upto and d > upto:
            continue
        rows.append({"date": d, "open": float(r["open"]), "high": float(r["high"]),
                     "low": float(r["low"]), "close": float(r["close"])})
    rows.sort(key=lambda x: x["date"])
    return rows


base_load_daily_fwd = base.load_daily
base.load_daily = wide_load_daily

# ------------------------------------------------------------ api help
def api_get_v2(path):
    req = urllib.request.Request(base.API + path, headers={
        "Authorization": f"Bearer {base.load_token()}",
        "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"429 on {path}")
        raise


def fetch_daily_v2(sym, to_d, from_d):
    enc = urllib.parse.quote(KEYS[sym], safe="")
    payload = api_get_v2(f"/v2/historical-candle/{enc}/day/{to_d}/{from_d}")
    rows = (payload.get("data") or {}).get("candles") or []
    out = []
    for c in rows:
        out.append({"date": str(c[0])[:10], "open": float(c[1]),
                    "high": float(c[2]), "low": float(c[3]), "close": float(c[4])})
    out.sort(key=lambda x: x["date"])
    return out


def fetch_intraday_guarded(sym):
    try:
        return base.fetch_intraday_5m(sym)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"429 intraday {sym}")
        raise


# ------------------------------------------------------------ daily store
def refresh_daily(target):
    """Once-per-day refresh of all 200 daily series. Returns
    (symbols_with_rows, seconds). Raises RateLimited on any 429."""
    marker = {}
    if os.path.exists(MARKER):
        try:
            marker = json.load(open(MARKER))
        except Exception:
            marker = {}
    if marker.get("date") == target:
        return marker.get("ok", 0), 0.0
    t0 = time.time()

    def one(sym):
        rows = fetch_daily_v2(sym, target, DAILY_FROM)
        d = f"{FWD_WIDE}/{sym}"
        os.makedirs(d, exist_ok=True)
        with open(f"{d}/spot_daily.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close"])
            for r in rows:
                w.writerow([r["date"], r["open"], r["high"], r["low"], r["close"]])
        return sym, len(rows)

    ok = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for sym, n in ex.map(one, WIDE):
            if n > 0:
                ok += 1
    secs = round(time.time() - t0, 1)
    json.dump({"date": target, "ok": ok, "seconds": secs}, open(MARKER, "w"))
    plog(f"daily refresh {target}: {ok}/{len(WIDE)} symbols with rows in {secs}s")
    return ok, secs


# ------------------------------------------------------------ calendar
def fetch_nse_events():
    import http.cookiejar
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(urllib.request.Request(NSE_HOME, headers={"User-Agent": UA}),
                timeout=30).read()
    req = urllib.request.Request(NSE_EVENTS, headers={
        "User-Agent": UA, "Accept": "application/json"})
    with opener.open(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _read_raw_calendar():
    if not os.path.exists(RAW_CAL):
        return []
    return list(csv.DictReader(open(RAW_CAL)))


def _write_raw_calendar(rows):
    with open(RAW_CAL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAL_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CAL_FIELDS})


def seed_and_merge_calendar(today_iso):
    """Seed the raw store from the curated calendar on first use, then
    merge a fresh NSE event-calendar snapshot (best effort — a failed
    fetch leaves the stored calendar in force and is logged)."""
    rows = _read_raw_calendar()
    have = {(r["stock"], r["event_date"][:10], r["event_type"]) for r in rows}
    if not rows:
        for r in csv.DictReader(open(CURATED_CAL)):
            rows.append({k: r.get(k, "") for k in CAL_FIELDS})
            have.add((r["stock"], r["event_date"][:10], r["event_type"]))
        _write_raw_calendar(rows)
        plog(f"calendar seeded from curated live calendar: {len(rows)} rows")
    marker = {}
    if os.path.exists(MARKER):
        try:
            marker = json.load(open(MARKER))
        except Exception:
            marker = {}
    if marker.get("nse_snapshot_date") == today_iso:
        return len(rows)
    try:
        events = fetch_nse_events()
    except Exception as e:
        plog(f"NSE snapshot fetch failed ({str(e)[:120]}); stored calendar in force")
        return len(rows)
    added = 0
    for e in events:
        sym = e.get("symbol", "")
        if sym not in KEYS or "Financial Results" not in (e.get("purpose") or ""):
            continue
        try:
            ev_date = datetime.strptime(e["date"], "%d-%b-%Y").date().isoformat()
        except Exception:
            continue
        key = (sym, ev_date, "results")
        if key in have:
            continue
        have.add(key)
        rows.append({"stock": sym, "event_date": ev_date, "event_type": "results",
                     "detail": (e.get("bm_desc") or "")[:120],
                     "after_market": "unverified",
                     "source": f"NSE event calendar snapshot {today_iso}",
                     "source_url": "", "reaction_date": "", "window_start": "",
                     "window_end": "", "known_before_open": "reaction_day_onwards",
                     "coverage": "nse_snapshot"})
        added += 1
    _write_raw_calendar(rows)
    marker["nse_snapshot_date"] = today_iso
    json.dump(marker, open(MARKER, "w"))
    plog(f"NSE snapshot merged {today_iso}: +{added} rows (total {len(rows)})")
    return len(rows)


def build_runtime_calendar(target):
    """Runtime calendar for `target`: raw rows whose reaction date is
    knowable and <= target. Reaction = first NIFTY trading day strictly
    after the event date (the curated calendar's uniform convention);
    curated rows keep their stored reaction date. Rows dated on/after
    target are excluded — under the frozen convention they react next
    session and cannot be due yet (this also stops eff_reaction's
    event-date fallback from creating phantom same-day candidates)."""
    trading = sorted({d["date"] for d in wide_load_daily("NIFTY", upto=target)}
                     | {target})
    out = []
    for r in _read_raw_calendar():
        sym, ev_date = r["stock"], (r["event_date"] or "")[:10]
        if sym not in KEYS or not ev_date or ev_date >= target:
            continue
        react = (r.get("reaction_date") or "")[:10]
        if not react:
            later = [d for d in trading if d > ev_date]
            if not later:
                continue
            react = later[0]
        if react > target:
            continue
        row = {k: r.get(k, "") for k in CAL_FIELDS}
        row["reaction_date"] = react
        out.append(row)
    with open(RUNTIME_CAL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAL_FIELDS)
        w.writeheader()
        for r in out:
            w.writerow(r)
    return len(out)


# ------------------------------------------------------------ evaluate
def run_pass(dry=False):
    now = datetime.now(IST)
    target = now.date().isoformat()
    state_path = STATE_DRY if dry else STATE
    log_path = LOG_DRY if dry else LOG
    tag = "DRY-RUN " if dry else ""
    t_start = time.time()
    try:
        daily_ok, daily_secs = refresh_daily(target)
        seed_and_merge_calendar(target)
        n_runtime = build_runtime_calendar(target)
        ev = base.Evaluator(target, RUNTIME_CAL)
    except RateLimited as e:
        plog(f"{tag}run {target} ABORTED rate-limited: {e}")
        print(f"RUN_SUMMARY {json.dumps({'date': target, 'status': 'rate_limited_429', 'dry_run': dry})}")
        return 1

    state = {"date": target, "positions": {}, "entered": []}
    if os.path.exists(state_path):
        try:
            state = json.load(open(state_path))
        except Exception:
            pass
    if state.get("date") != target:
        state = {"date": target, "positions": {}, "entered": []}
    ev.entered = {tuple(x) for x in state.get("entered", [])}
    for k, v in state.get("positions", {}).items():
        comp, stock = k.split("|")
        ev.positions[(comp, stock)] = v

    active = sorted({c["stock"] for c in ev.cands}
                    | {s for (s, d) in ev.n4_days if d == target}
                    | {k[1] for k in ev.positions})
    fetched, missing = {}, []
    try:
        if active:
            with ThreadPoolExecutor(max_workers=8) as ex:
                results = dict(zip(active, ex.map(fetch_intraday_guarded, active)))
            for s in active:
                bars = results.get(s) or []
                if dry:
                    done = bars
                else:
                    done = [b for b in bars
                            if datetime.fromisoformat(b["timestamp"]).replace(tzinfo=IST)
                            + timedelta(minutes=5) <= now]
                if done:
                    fetched[s] = done
                else:
                    missing.append(s)
    except RateLimited as e:
        plog(f"{tag}run {target} ABORTED rate-limited during intraday fetch: {e}")
        print(f"RUN_SUMMARY {json.dumps({'date': target, 'status': 'rate_limited_429', 'dry_run': dry})}")
        return 1

    actions = []
    if base.wk(target):
        summary = {"date": target, "status": "weekend_rf1", "dry_run": dry, "actions": []}
    elif active and not fetched:
        summary = {"date": target, "status": "no_market_data", "dry_run": dry,
                   "active_symbols": active, "actions": []}
        plog(f"{tag}run {target} no_market_data (active={len(active)}, all fetches empty)")
    else:
        for s in active:
            if s in fetched:
                actions.extend(ev.step(s, fetched[s]))
        state = {"date": target,
                 "positions": {f"{k[0]}|{k[1]}": v for k, v in ev.positions.items()},
                 "entered": sorted(list(x) for x in ev.entered)}
        with open(state_path, "w") as f:
            json.dump(state, f, indent=1)
        exits = [dict(a, mode="WIDE200-SHADOW") for a in actions
                 if a["action"] == "EXIT" and a.get("layer") == "book"]
        if exits:
            exists = os.path.exists(log_path)
            with open(log_path, "a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=base.LOG_FIELDS)
                if not exists:
                    w.writeheader()
                for r in exits:
                    w.writerow({k: r.get(k) for k in base.LOG_FIELDS})
        summary = {"date": target, "status": "ok", "dry_run": dry,
                   "regime": ev.regime,
                   "candidates": ev.cands,
                   "n4_today": sorted(s for (s, d) in ev.n4_days if d == target),
                   "active_symbols": active,
                   "intraday_missing": missing,
                   "daily_coverage": f"{daily_ok}/{len(WIDE)}",
                   "daily_fetch_seconds": daily_secs,
                   "runtime_calendar_rows": n_runtime,
                   "open_positions": [f"{k[0]}:{k[1]}" for k in ev.positions],
                   "cycle_seconds": round(time.time() - t_start, 1),
                   "actions": actions}
    for a in actions:
        print(f"WIDE200_SHADOW_{a['action']} {json.dumps(a)}")
    print(f"RUN_SUMMARY {json.dumps(summary)}")
    plog(f"{tag}run {target} summary {json.dumps(summary)[:900]}")
    return 0


def probe_full_fetch():
    """Timing probe: fetch today's intraday bars for ALL 200 symbols
    (fetch-only, no evaluation) to size the worst-case cycle."""
    t0 = time.time()
    try:
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(fetch_intraday_guarded, WIDE))
    except RateLimited as e:
        print(f"PROBE_ABORTED rate-limited: {e}")
        return
    with_data = sum(1 for r in results if r)
    secs = round(time.time() - t0, 1)
    print(f"PROBE_FULL_FETCH symbols_with_data={with_data}/{len(WIDE)} seconds={secs}")
    plog(f"probe full fetch: {with_data}/{len(WIDE)} symbols with data in {secs}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="evaluate today against completed data; dry outputs only")
    ap.add_argument("--probe", action="store_true",
                    help="with --dry-run: also time a full 200-symbol intraday fetch")
    args = ap.parse_args()
    if args.dry_run:
        rc = run_pass(dry=True)
        if args.probe:
            probe_full_fetch()
        return rc
    return run_pass(dry=False)


if __name__ == "__main__":
    raise SystemExit(main())
