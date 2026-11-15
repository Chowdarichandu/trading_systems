#!/usr/bin/env python3
"""STOCK ENGINE — PRODUCER (CANDIDATE LAYER, VARIANT D DESIGN).
Reworked 2026-11-11 evening: this producer is now ONLY the intraday
CANDIDATE layer of the Stock Engine live shadow (variant D design, spec in
sarvasetu_top3_v2_2026-11-11.md). It detects intraday candidates over
the wide liquid-NSE universe; a candidate is NOT a counted pick. The
OFFICIAL Stock Engine ledger is finalised after the close by
sarvasetu_top3_eod_scorer.py, which applies variant D's ranking /
conviction floor / price cap over the full day's whole-book pool
(all seven components) and writes the day's <= 6 picks to
sarvasetu_top3_shadow_log.csv. This producer's own exits file is a
candidates log (mode STOCK-ENGINE-CANDIDATE), never the ledger.
Owner approval 2026-11-11 17:02 IST, universe widened to all liquid
NSE stocks at 17:08 IST, variant D delegated 18:59-19:00 IST
(Bank+Nifty chat). First official live day: Thu 2026-11-12.
NAMING: the one user-visible name is Stock Engine (owner order
2026-11-11 19:40 IST). Build-day history: this layer was briefly
labelled WIDE-NSE SHADOW, then Sarvasetu, on 2026-11-11 — both
retired the same day; files and identifiers not renamed.
Paper only, real Rs0, no orders. Provisional per 100 shares,
Rs40/trade — identical money basis to the frozen book.

SIGNAL CONSTRUCTION: this file does NOT re-implement any signal logic.
It imports stocks_live_shadow_producer.py and reuses its frozen
Evaluator / due_candidates / calendar_events / comp_allowed /
scan_exit / net_of VERBATIM (the module's SYMBOLS, KEYS and load_daily
globals are rebound to the wide data layer before the Evaluator is
constructed). Only the BOOK layer is evaluated (Evaluator.step) —
components N4-V3 (T150/S080), P2F, P2F-R2, R2-LOWBAND (T125/S050).
The scorecard layer (N4-PRIMARY / P2F-SHADOW) is the 25-book's own and
is NOT run here. F4 / INV-LONG / INV-ABOVE are EOD-only sleeves in the
frozen construction: they have NO intraday candidate path here (a
NOT_LIVE gap for intraday announcements only) and enter Stock Engine
solely through the EOD scorer's whole-book pool, where all seven
components are computed. The intraday candidates this producer emits
(N4-V3, P2F, P2F-R2, R2-LOWBAND) are the same four components the
EOD pool also contains; the EOD selection — not this layer —
decides what counts.

UNIVERSE (wide_nse_universe_2026-11-11.csv, fetched/built 2026-11-11):
FINAL COUNT 1,081 names. NIFTY 500 tier (500 names): official
niftyindices.com constituents passing a liquidity screen on
2026-11-11 itself (>= 50 completed 5-min bars; index membership
certifies liquidity, so no value floor — the DUMMYHEG placeholder row
is excluded as not a traded company). EXTENSION tier (581 names):
every other main-board NSE equity from the Upstox NSE instrument
master passing the same bars test AND traded value >= Rs6 crore on
2026-11-11. Master pre-filters: exchange NSE_EQ, instrument EQUITY,
lot_size 1 (main-board rolling settlement; NSE SME Emerge names trade
in fixed lots > 1 and fall out here), ISIN under INE, no ETFs by
name, and any name with no usable intraday candles is excluded. All
4,303 pool names were screened (zero HTTP 429). The rule and counts
are also in the universe file's header and the registry entry.

CADENCE DESIGN (the ~1,000-name honesty section — a full-universe
fetch every 5 minutes is NOT run; measured full-scan cost is in the
producer log / dry-run report):
  - Before the open each day: daily context for all names refreshed
    once (v2 daily candles, ~1-2 min), NSE event-calendar snapshot
    merged, and the day's candidate set precomputed by the frozen
    construction: P2F-family entries due today (they key off PRIOR
    days' reactions and enter at the 09:15 open) + today's N4
    reaction-day names + open positions = the MORNING ACTIVE SET
    (typically a few dozen names).
  - 09:15-09:32 cycles fetch ONLY the morning active set (+ open
    positions). P2F-family entries are therefore announced promptly:
    worst case ~09:26 (first cycle after the 09:15 bar completes at
    09:20, plus < 1 min fetch/eval on the small set).
  - ONE FULL SCAN at the first cycle at/after 09:32: every universe
    name's completed opening bars are fetched once and fed to the
    evaluator (coverage verification + the N4 decision point). From
    the scan, the QUALIFIER set is computed — reaction-day names whose
    |09:25-bar move| >= 1.0% (the measurable half of the frozen N4
    trigger; the entry itself still resolves inside the frozen step()
    once the 09:30 bar completes) — and persisted in state.
  - After the scan, cycles fetch ONLY actives + qualifiers + open
    positions. N4 entries announce by ~09:42 worst case (09:30 bar
    completes 09:35; one 5-min cycle + small-set fetch), typically
    ~09:37. Exits announce within ~7 min of the exit bar completing.
  - A symbol outside these sets is a strict no-op in the frozen
    step() (no due candidate, no reaction day, no open position), so
    the cadence changes fetch load only, never outputs.
  - HTTP 429 from Upstox aborts the run immediately (hard stop): no
    state/log writes, status reported; never a retry loop.

ADAPTATIONS vs the 25-stock live producer (data layer only — every
signal rule, threshold, geometry and exclusion is the frozen code's):
  A1. Universe: the wide liquid-NSE set above instead of the frozen
      25 (which are all inside it; no deduplication — own book).
  A2. Instrument keys: the Upstox master file's own keys, verified to
      equal NSE_EQ|<ISIN> for every index constituent checked
      (500/500 NIFTY 500 names matched their official ISINs).
  A3. Daily bars: own store (data/wide_nse_fwd/<SYM>/spot_daily.csv,
      same schema as the frozen forward root), refreshed once daily
      from the Upstox v2 historical daily endpoint (v2 output verified
      byte-identical to the forward root on TATASTEEL at build time,
      including the 2026-11-08 session). NIFTY daily (regime input)
      is still read from the forward root, read-only, exactly as the
      frozen producer reads it.
  A4. Event calendar: accumulating wide calendar
      (stocks_wide_nse_calendar.csv) — seeded with the curated
      25-name live calendar verbatim + the NSE event-calendar
      snapshot of 2026-11-11 (Financial Results purposes, universe
      symbols), merged with a fresh snapshot on the first cycle of
      every day. Reaction dates mirror the curated calendar's uniform
      convention (first trading day strictly after the event date).
      CONSEQUENCES, on record: (i) wide N4 reaction days arise from
      RESULTS events only (curated SINGLE_NEWS classes are not
      systematically available market-wide); (ii) BOOTSTRAP GAP —
      board dates on or before 2026-11-11 for non-watchlist names
      are not retrievable (NSE calendar is forward-only; BSE API and
      Moneycontrol are blocked from this network), so P2F-family
      entries in the first live days can miss events whose board
      dates fell 2026-11-09..11 outside the curated 25.
  A5. Fetch cadence: the targeted-scan design above (frozen producer
      fetches all 25 every cycle). no_market_data is declared when
      every ACTIVE fetch of a cycle is empty.
  A6. Fetches run on an 8-thread pool (frozen producer is sequential
      over 25).
  A7. Threshold note (NOT an adaptation — frozen code as is): the
      producer's N4 trigger is a >= 1.0% 09:25-bar move; the adopted
      SarvaRitu book spec elsewhere records 0.8%. Noted unresolved,
      as instructed; this shadow mirrors the PRODUCER (1.0%).

Outputs (all Stock Engine-labelled, never the book's files):
  stocks_wide_nse_shadow_state.json       positions / entered / scan state
  stocks_wide_nse_shadow_candidates_log.csv  closed CANDIDATE trades
                                             (mode STOCK-ENGINE-CANDIDATE;
                                             never the official ledger)
  stocks_wide_nse_shadow_producer.log     every evaluation
  data/wide_nse_fwd/                      daily store + refresh marker
Dry-run mode (--dry-run) writes ONLY the .dryrun-suffixed state/log.

Modes:
  (default)        one live evaluation pass for today (IST).
  --dry-run        full pass for today against completed data (daily
                   refresh + precompute + full scan + evaluation),
                   dry outputs only, with coverage and timing stats.
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
UNIVERSE_CSV = f"{WS}/wide_nse_universe_2026-11-11.csv"
KEYS_JSON = f"{WS}/data/wide_nse_keys.json"
FWD_WIDE = f"{WS}/data/wide_nse_fwd"
RAW_CAL = f"{WS}/stocks_wide_nse_calendar.csv"
RUNTIME_CAL = f"{WS}/stocks_wide_nse_calendar_runtime.csv"
CURATED_CAL = base.LIVE_CAL
STATE = f"{WS}/stocks_wide_nse_shadow_state.json"
STATE_DRY = f"{WS}/stocks_wide_nse_shadow_state.dryrun.json"
LOG = f"{WS}/stocks_wide_nse_shadow_candidates_log.csv"
LOG_DRY = f"{WS}/stocks_wide_nse_shadow_candidates_log.dryrun.csv"
PLOG = f"{WS}/stocks_wide_nse_shadow_producer.log"
MARKER = f"{FWD_WIDE}/_refresh.json"
DAILY_FROM = "2026-09-01"
FULL_SCAN_AFTER = "09:32"
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
# signal code is the frozen module's own, resolved against these
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


def fetch_many(symbols):
    """Threaded intraday fetch; returns {sym: bars}. Raises RateLimited."""
    if not symbols:
        return {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(fetch_intraday_guarded, symbols))
    return dict(zip(symbols, results))


def completed(bars, now, dry):
    if dry:
        return bars
    return [b for b in bars
            if datetime.fromisoformat(b["timestamp"]).replace(tzinfo=IST)
            + timedelta(minutes=5) <= now]


# ------------------------------------------------------------ daily store
def refresh_daily(target):
    """Once-per-day refresh of all universe daily series. Returns
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
    # NSE's bot wall 403s the urllib route intermittently (seen
    # 2026-11-11 17:26 IST while the identical curl flow succeeded) —
    # use curl with a cookie jar, the route verified at build time.
    import subprocess, tempfile
    jar = tempfile.mktemp(suffix=".cookies")
    hdr = ["-A", UA]
    subprocess.run(["curl", "-s", *hdr, "-c", jar, NSE_HOME, "-o", "/dev/null",
                    "--max-time", "30"], check=True)
    out = subprocess.run(
        ["curl", "-s", *hdr, "-b", jar, "-H", "Accept: application/json",
         "-H", f"Referer: {NSE_HOME}/companies-listing/corporate-filings-event-calendar",
         NSE_EVENTS, "--max-time", "60"],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


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
def _fresh_state(target):
    return {"date": target, "positions": {}, "entered": [],
            "full_scan_date": None, "qualifiers": []}


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

    state = _fresh_state(target)
    if os.path.exists(state_path):
        try:
            state = json.load(open(state_path))
        except Exception:
            pass
    if state.get("date") != target:
        state = _fresh_state(target)
    ev.entered = {tuple(x) for x in state.get("entered", [])}
    for k, v in state.get("positions", {}).items():
        comp, stock = k.split("|")
        ev.positions[(comp, stock)] = v

    morning_actives = sorted({c["stock"] for c in ev.cands}
                             | {s for (s, d) in ev.n4_days if d == target})
    open_stocks = sorted({k[1] for k in ev.positions})
    qualifiers = sorted(set(state.get("qualifiers", [])))
    do_full_scan = dry or (now.strftime("%H:%M") >= FULL_SCAN_AFTER
                           and state.get("full_scan_date") != target)

    actions = []
    coverage = {}
    scan_secs = 0.0
    try:
        if base.wk(target):
            summary = {"date": target, "status": "weekend_rf1", "dry_run": dry,
                       "actions": []}
            print(f"RUN_SUMMARY {json.dumps(summary)}")
            plog(f"{tag}run {target} weekend — no evaluation")
            return 0
        if do_full_scan:
            t_scan = time.time()
            all_bars = fetch_many(WIDE)
            scan_secs = round(time.time() - t_scan, 1)
            usable50 = 0
            for s in WIDE:
                bars = completed(all_bars.get(s) or [], now, dry)
                if len(bars) >= 50:
                    usable50 += 1
                if bars:
                    coverage[s] = len(bars)
                    actions.extend(ev.step(s, bars))
            # qualifier set from the scan: reaction-day names whose
            # |09:25-bar move| >= 1.0% (measurable half of the frozen
            # N4 trigger), plus anything already entered/positioned.
            quals = set()
            for s in {x for (x, d) in ev.n4_days if d == target}:
                bars = completed(all_bars.get(s) or [], now, dry)
                by_time = {b["time"]: b for b in bars}
                pc = ev.prev_close(s)
                if "09:25" in by_time and pc:
                    move = (by_time["09:25"]["close"] / pc - 1) * 100
                    if abs(move) >= 1.0:
                        quals.add(s)
            qualifiers = sorted(quals | {k[1] for k in ev.positions}
                                | {x[1] for x in ev.entered})
            state["full_scan_date"] = target
            state["qualifiers"] = qualifiers
            fetch_set = sorted(set(morning_actives) | set(qualifiers) | set(open_stocks))
            summary_extra = {"full_scan": True, "full_scan_seconds": scan_secs,
                             "symbols_with_bars": len(coverage),
                             "symbols_usable_50bars": usable50,
                             "universe": len(WIDE)}
        else:
            fetch_set = sorted(set(morning_actives) | set(qualifiers) | set(open_stocks))
            fetched = fetch_many(fetch_set)
            got = 0
            for s in fetch_set:
                bars = completed(fetched.get(s) or [], now, dry)
                if bars:
                    got += 1
                    actions.extend(ev.step(s, bars))
            if fetch_set and got == 0:
                summary = {"date": target, "status": "no_market_data", "dry_run": dry,
                           "fetch_set": fetch_set, "actions": []}
                print(f"RUN_SUMMARY {json.dumps(summary)}")
                plog(f"{tag}run {target} no_market_data (fetch_set={len(fetch_set)})")
                return 0
            summary_extra = {"full_scan": False}
    except RateLimited as e:
        plog(f"{tag}run {target} ABORTED rate-limited during intraday fetch: {e}")
        print(f"RUN_SUMMARY {json.dumps({'date': target, 'status': 'rate_limited_429', 'dry_run': dry})}")
        return 1

    state["date"] = target
    state["positions"] = {f"{k[0]}|{k[1]}": v for k, v in ev.positions.items()}
    state["entered"] = sorted(list(x) for x in ev.entered)
    state["qualifiers"] = qualifiers
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)
    exits = [dict(a, mode="STOCK-ENGINE-CANDIDATE") for a in actions
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
               "morning_actives": morning_actives,
               "qualifiers": qualifiers,
               "daily_coverage": f"{daily_ok}/{len(WIDE)}",
               "daily_fetch_seconds": daily_secs,
               "runtime_calendar_rows": n_runtime,
               "open_positions": [f"{k[0]}:{k[1]}" for k in ev.positions],
               "cycle_seconds": round(time.time() - t_start, 1),
               "actions": actions}
    summary.update(summary_extra)
    for a in actions:
        print(f"STOCK_ENGINE_CANDIDATE_{a['action']} {json.dumps(a)}")
    print(f"RUN_SUMMARY {json.dumps(summary)}")
    plog(f"{tag}run {target} summary {json.dumps(summary)[:900]}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="evaluate today against completed data; dry outputs only")
    args = ap.parse_args()
    return run_pass(dry=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
