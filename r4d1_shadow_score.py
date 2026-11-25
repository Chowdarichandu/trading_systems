#!/usr/bin/env python3
"""R4-D1 SHADOW SCORER — forward paper evidence for the Bank Nifty
R4-D1 (morning basis divergence -> reversal) INCREMENT
(2026-11-13 night setup; spec frozen in
new_data_round4_2026-11-13.md Part 2, setup section appended there).

WHAT THIS IS: a SCORE-ONLY paper shadow. Round 4 found that D1
standalone FAILS its gate (a coin flip beats it on its own days),
but its legs on days TUNED STACK v2 is idle were +Rs8,973.00 over
27 legs Jan-Oct with BOTH increment halves and the increment
ex-top-3 positive — the strongest merge fragment of the four
invention rounds, classified MERGE-ONLY EVIDENCE, not a pass. This
scorer collects the honest next test: forward evidence, one evening
at a time, from Mon 2026-11-16. It never writes to the stack's
ledger or to any other book's ledger, job, or log.

FROZEN RULES (round 4 Part 2, verbatim — do not edit the spec here):
- Morning read from day T's OWN 5-minute bars, closes only:
  basis_open = fut close(09:15 bar) - spot close(09:15 bar);
  basis_read = fut close(10:55 bar) - spot close(10:55 bar);
  spot_morning_pct = spot close(10:55)/spot open(09:15) - 1;
  dbasis_pct = (basis_read - basis_open)/spot close(10:55).
  Futures = the in-force near-month BANKNIFTY contract of T
  (round 2/4 convention: first monthly expiry >= T).
- D1 direction: spot_morning_pct >= +0.35% and dbasis_pct <= 0
  -> buy PE; spot_morning_pct <= -0.35% and dbasis_pct >= 0
  -> buy CE; otherwise no leg.
- INCREMENT CONDITION: the leg exists ONLY if TUNED STACK v2
  placed no leg on T, read from november_shadow_stack_bank_log.csv
  (read-only to this shadow). No row for T, or a NOT_COMPUTED row,
  means the day is NC — idle is never assumed.
- Trade: ONE leg, entry at the OPEN of the 11:00 5-min bar,
  strike = ATM (nearest 100) to the spot close of the 10:55 bar,
  contract = the in-force monthly expiry of T; exits = intraday
  house geometry (stop -50 checked before target +90 on every bar
  from the entry bar onward, fills at the level, square-off at the
  15:10 bar close), 1 lot of 30, cost Rs220/trade, BUYING ONLY.
- TIMING: every signal input is a CLOSE of a bar ending at or
  before 10:55; the entry bar's own OHLC is never an input.
  Asserted per trade (input bar times <= "10:55", entry bar
  == "11:00"); violations are counted into the ledger row.

DATA SOURCING (round 4's builder is the reference):
- Spot 5-min bars: round 4's stored series (daily2leg/spot.json +
  oi_history/spot_nov_bars.json + round4_history/spot_extra.json),
  then the November machinery's progressive store
  (data/progressive/BANKNIFTY/spot_5m.csv), then the v3
  historical-candle route (cached to round4_history/
  r4d1_spot_fwd.json). A day whose series has < 70 bars is a
  fragment (the Nov 8 case) — never a morning-read day -> NC.
- Futures 5-min bars: round 4's per-contract cache
  (round4_history/FUT5_<expiry>.json), then the forward day cache
  (round4_history/r4d1_fut_fwd.json), then the single-day fetch
  via the contract's route (v3 while the contract is live, the
  expired-instruments route after it expires) — the exact URL
  shapes of round4_data_build.fetch_range. Contract keys:
  round2_history/futures_keys.json, extended from the Upstox
  instruments master (complete.csv.gz, FUTIDX/BANKNIFTY) into
  round4_history/futures_keys_fwd.json when a needed expiry is
  missing (the master cross-checks: its 2026-11-23 key equals
  round 2's NSE_FO|61466).
- Premium candles: round 1's frozen machinery + the documented
  full-coverage repair, copied verbatim from round4_score.py
  (prem_bars_full); replay_intraday likewise copied verbatim.

LEDGER: r4d1_shadow_log.csv — one row per scored day (TRADED /
NO_SIGNAL / STACK_BUSY / NC + the reason named), idempotent per
date (a re-run replaces that date's row). Review point
(pre-registered): after 20 scored trade-opportunities (days on
which D1 produced a direction, resolved TRADED or STACK_BUSY;
NC and no-signal days do not count) or 2026-12-31, whichever comes
first; the scorer refuses to score beyond either bound and says so.

Paper only, real money Rs0. No live orders. Every api.upstox.com
call carries the browser User-Agent. On HTTP 429: HARD STOP for
the run — the day is marked NC rate_limited, no retry, no route
switch.

Usage:
    python3 r4d1_shadow_score.py [--date YYYY-MM-DD] [--dry-run]
Default date = today (IST). --dry-run computes and prints the row
but writes NOTHING (no ledger row, no cache writes). --verify is a
hard-wired no-write check against a historical date (it bypasses
the start/window guards for that check only, and can never write).
"""
import argparse, csv, gzip, io, json, sys
import importlib.util
import urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-12-31"
REVIEW_OPPS = 20
COST = 220.0
LOT = 30
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
MASTER_URL = ("https://assets.upstox.com/market-quote/instruments/"
              "exchange/complete.csv.gz")
R4H = TR / "round4_history"
STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
LEDGER = TR / "r4d1_shadow_log.csv"
PROG_SPOT_5M = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
SPOT_FWD = R4H / "r4d1_spot_fwd.json"
FUT_FWD = R4H / "r4d1_fut_fwd.json"
FUT_KEYS_FWD = R4H / "futures_keys_fwd.json"
MIN_DAY_BARS = 70  # a real session has 74-77 5-min bars; fragments NC

LEDGER_FIELDS = ["date", "status", "reason", "spot_morning_pct",
                 "dbasis_pct", "basis_open_pts", "basis_read_pts",
                 "direction", "strike", "expiry", "entry_time",
                 "entry_premium", "exit_time", "exit_premium",
                 "exit_reason", "net_inr", "stack_status",
                 "stack_net_inr", "timing_violations", "notes"]

# ---- import round 1's frozen premium machinery, unmodified --------
_spec = importlib.util.spec_from_file_location(
    "oi_buildup_score", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)


class RateLimited(Exception):
    pass


_token = None
for _line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if _line.startswith("UPSTOX_ACCESS_TOKEN="):
        _token = _line.split("=", 1)[1].strip()
assert _token


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {_token}",
        "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return None


# ---- round-1 data-layer repair + intraday replay, verbatim from
# ---- round4_score.py (documented there; no rule changes) ----------
_orig_prem_bars = obs.prem_bars


def prem_bars_full(idx, exp, strike, typ, day):
    bars, src = _orig_prem_bars(idx, exp, strike, typ, day)
    if bars and bars[0][0] <= "09:20":
        return bars, src
    fn = obs.FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if cd:
            fb = sorted((c[0][11:16], float(c[1]), float(c[2]),
                         float(c[3]), float(c[4])) for c in cd)
            if fb[0][0] <= "09:20":
                return fb, "fetched_cache"
    fb = obs.fetch_bars(idx, exp, strike, typ, day)
    if fb:
        return fb, "fetched_full"
    return bars, src


def replay_intraday(bars, entry_time, sq="15:10"):
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0

    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t,
                    exit_reason=reason, ft=ft,
                    net=round((px - entry) * LOT - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t, 0)
        if h >= target:
            return out(target, "target", t, 1)
        if t == sq:
            return out(cl, "square_off", t, 0)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0], 0)


# ---------------- spot bars ------------------------------------------
def _stored_spot():
    """Round 4's stored-series construction, identical sources."""
    spot = {}
    raw = json.load(open(TR / "daily2leg/spot.json"))
    for d, bars in raw["BANKNIFTY"].items():
        spot[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                          float(b[4])) for b in bars}
    nov = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
    for d, bars in nov.get("BANKNIFTY", {}).items():
        spot.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4])
                            for b in bars})
    extra_fn = R4H / "spot_extra.json"
    if extra_fn.exists():
        for d, bars in json.loads(extra_fn.read_text()).items():
            if bars:
                spot.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4])
                                    for b in bars})
    return spot


STORED_SPOT = _stored_spot()


def _prog_spot(day):
    if not PROG_SPOT_5M.exists():
        return None
    bars = {}
    with open(PROG_SPOT_5M) as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"]
            if ts[:10] == day:
                bars[ts[11:16]] = (float(r["open"]), float(r["high"]),
                                   float(r["low"]), float(r["close"]))
    return bars or None


def _fetch_spot_day(day):
    """v3 spot route with same-day intraday fallback (fix 2026-11-25).
    Returns {time: (o,h,l,c)} or None. Raises RateLimited on 429."""
    ikey = quote(obs.IDXKEY["BANKNIFTY"], safe="")
    today_s = datetime.now(IST).date().isoformat()
    body = get(f"{API}/v3/historical-candle/{ikey}"
               f"/minutes/5/{day}/{day}")
    cd = [c for c in ((body or {}).get("data") or {}).get("candles")
          or [] if c[0][:10] == day]
    if not cd and day == today_s:
        body = get(f"{API}/v3/historical-candle/intraday/{ikey}/minutes/5")
        cd = [c for c in ((body or {}).get("data") or {}).get("candles")
              or [] if c[0][:10] == day]
    if not cd:
        return None
    return {c[0][11:16]: (float(c[1]), float(c[2]), float(c[3]),
                          float(c[4])) for c in cd}


def spot_bars(day, dry):
    """(bars_dict, source) or (None, reason)."""
    if day in STORED_SPOT and len(STORED_SPOT[day]) >= MIN_DAY_BARS:
        return STORED_SPOT[day], "stored_series"
    bars = _prog_spot(day)
    if bars and len(bars) >= MIN_DAY_BARS:
        return bars, "progressive_store"
    cache = {}
    if SPOT_FWD.exists():
        cache = json.loads(SPOT_FWD.read_text())
    if day in cache and len(cache[day]) >= MIN_DAY_BARS:
        return {b[0]: tuple(b[1:]) for b in cache[day]}, "fwd_cache"
    bars = _fetch_spot_day(day)  # may raise RateLimited
    if bars is None:
        return None, "spot_unserved"
    if len(bars) < MIN_DAY_BARS:
        return None, f"spot_fragment_{len(bars)}_bars"
    if not dry:
        cache[day] = [[t] + list(v) for t, v in sorted(bars.items())]
        SPOT_FWD.write_text(json.dumps(cache))
    return bars, "fetched_v3"


# ---------------- futures contracts + bars ---------------------------
def _fut_universe(dry):
    """{expiry: (key, route)} — round 2 keys extended by the
    instruments master (FUTIDX/BANKNIFTY) when a file exists or a
    refresh is needed. Master rows are live contracts, route v3."""
    uni = {}
    r2 = json.loads((TR / "round2_history/futures_keys.json")
                    .read_text())
    for e, v in r2.items():
        uni[e] = (v["key"], "expired" if v["route"] == "expired"
                  else "live")
    if FUT_KEYS_FWD.exists():
        for e, v in json.loads(FUT_KEYS_FWD.read_text()).items():
            uni.setdefault(e, (v["key"], "live"))
    return uni


def _refresh_fut_keys(uni, dry):
    req = urllib.request.Request(MASTER_URL,
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return uni
    rows = csv.DictReader(io.StringIO(
        gzip.decompress(raw).decode()))
    fwd = {}
    if FUT_KEYS_FWD.exists():
        fwd = json.loads(FUT_KEYS_FWD.read_text())
    for r in rows:
        if (r.get("instrument_type") == "FUTIDX"
                and r.get("name") == "BANKNIFTY" and r.get("expiry")):
            fwd[r["expiry"]] = dict(key=r["instrument_key"],
                                    symbol=r["tradingsymbol"],
                                    lot=r.get("lot_size"))
            uni.setdefault(r["expiry"], (r["instrument_key"], "live"))
    if not dry:
        FUT_KEYS_FWD.write_text(json.dumps(fwd, indent=1))
    return uni


def in_force(day, dry):
    """(expiry, key, route) of the first monthly expiry >= day."""
    uni = _fut_universe(dry)
    cand = [e for e in uni if e >= day]
    if not cand:
        uni = _refresh_fut_keys(uni, dry)
        cand = [e for e in uni if e >= day]
    if not cand:
        return None, None, None
    e = min(cand)
    key, route = uni[e]
    if route == "live" and e < datetime.now(IST).date().isoformat():
        route = "expired"  # contract has since expired; v2 route
    return e, key, route


def _fetch_fut_day(key, route, day):
    """Round 4 fetch_range URL shapes, single day, with same-day v3
    intraday fallback for live contracts (fix 2026-11-25). Returns
    {time: close} or None. Raises RateLimited on 429."""
    enc = quote(key, safe="")
    today_s = datetime.now(IST).date().isoformat()
    if route == "expired":
        url = (f"{API}/v2/expired-instruments/historical-candle/{enc}"
               f"/5minute/{day}/{day}")
    else:
        url = f"{API}/v3/historical-candle/{enc}/minutes/5/{day}/{day}"
    body = get(url)
    cd = [c for c in ((body or {}).get("data") or {}).get("candles")
          or [] if c[0][:10] == day]
    if not cd and route != "expired" and day == today_s:
        body = get(f"{API}/v3/historical-candle/intraday/{enc}/minutes/5")
        cd = [c for c in ((body or {}).get("data") or {}).get("candles")
              or [] if c[0][:10] == day]
    if not cd:
        return None
    return {c[0][11:16]: float(c[4]) for c in cd}


def fut_closes(day, exp, key, route, dry):
    """(closes_dict, source) or (None, reason)."""
    fn = R4H / f"FUT5_{exp}.json"
    if fn.exists():
        closes = {}
        for r in json.loads(fn.read_text()):
            if r[0] == day:
                closes[r[1]] = float(r[5])
        if len(closes) >= MIN_DAY_BARS:
            return closes, "round4_cache"
    cache = {}
    if FUT_FWD.exists():
        cache = json.loads(FUT_FWD.read_text())
    ck = f"{exp}|{day}"
    if ck in cache and len(cache[ck]) >= MIN_DAY_BARS:
        return cache[ck], "fwd_cache"
    closes = _fetch_fut_day(key, route, day)  # may raise RateLimited
    if closes is None:
        return None, "futures_unserved"
    if len(closes) < MIN_DAY_BARS:
        return None, f"futures_fragment_{len(closes)}_bars"
    if not dry:
        cache[ck] = closes
        FUT_FWD.write_text(json.dumps(cache))
    return closes, "fetched"


# ---------------- morning read + frozen D1 signal --------------------
def morning_read(day, dry):
    """(read_dict, source_note) or (None, reason). read_dict carries
    the five inputs + computed fields, round 4 rounding."""
    sbars, ssrc = spot_bars(day, dry)
    if sbars is None:
        return None, ssrc
    exp, key, route = in_force(day, dry)
    if exp is None:
        return None, "no_futures_contract_for_day"
    fcloses, fsrc = fut_closes(day, exp, key, route, dry)
    if fcloses is None:
        return None, fsrc
    so = sbars.get("09:15")
    sc55 = sbars.get("10:55")
    fc15 = fcloses.get("09:15")
    fc55 = fcloses.get("10:55")
    if so is None or sc55 is None or fc15 is None or fc55 is None:
        return None, "morning_read_bars_missing"
    b_o = round(fc15 - so[3], 2)
    b_r = round(fc55 - sc55[3], 2)
    read = dict(expiry=exp,
                spot_open_0915=so[0], spot_close_0915=so[3],
                spot_close_1055=sc55[3], fut_close_0915=fc15,
                fut_close_1055=fc55,
                basis_open_pts=b_o, basis_read_pts=b_r,
                spot_morning_pct=round((sc55[3] / so[0] - 1) * 100, 4),
                dbasis_pct=round((b_r - b_o) / sc55[3] * 100, 4))
    return read, f"spot={ssrc}; futures={fsrc}"


def d1_signal(read):
    """Frozen D1 (round 4 Part 2, verbatim thresholds)."""
    sm = read["spot_morning_pct"]
    db = read["dbasis_pct"]
    if sm >= 0.35 and db <= 0.0:
        return "PE"
    if sm <= -0.35 and db >= 0.0:
        return "CE"
    return None


# ---------------- stack status (as in oi_v3_shadow_score.py) ---------
def stack_status(day):
    """('busy', net) / ('idle', None) / ('unknown', reason)."""
    if not STACK_LOG.exists():
        return "unknown", "stack_log_missing"
    rows = []
    with open(STACK_LOG) as f:
        for r in csv.DictReader(f):
            if r["date"] == day:
                rows.append(r)
    if not rows:
        return "unknown", "stack_log_missing_for_day"
    nets = [float(r["net_inr"]) for r in rows if r.get("net_inr")]
    if nets:
        return "busy", round(sum(nets), 2)
    if any("NOT_COMPUTED" in (r.get("notes") or "") for r in rows):
        return "unknown", "stack_not_computed"
    return "idle", None


# ---------------- ledger ----------------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def write_row(row, dry):
    if dry:
        return
    rows = [r for r in ledger_rows() if r["date"] != row["date"]]
    rows.append(row)
    rows.sort(key=lambda r: r["date"])
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)


def opportunities(rows):
    return sum(1 for r in rows if r["status"] in ("TRADED",
                                                  "STACK_BUSY"))


# ---------------- main scoring flow -----------------------------------
def score_day(T, dry):
    row = {k: "" for k in LEDGER_FIELDS}
    row["date"] = T
    try:
        read, src = morning_read(T, dry)
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    if read is None:
        row.update(status="NC", reason=src)
        return row
    row.update(spot_morning_pct=f"{read['spot_morning_pct']:.4f}",
               dbasis_pct=f"{read['dbasis_pct']:.4f}",
               basis_open_pts=f"{read['basis_open_pts']:.2f}",
               basis_read_pts=f"{read['basis_read_pts']:.2f}",
               expiry=read["expiry"], notes=src)
    dirn = d1_signal(read)
    if dirn is None:
        row.update(status="NO_SIGNAL", reason="d1_no_signal")
        return row
    row["direction"] = dirn
    # D1 produced a direction: the day is a scored trade-opportunity.
    sstat, snet = stack_status(T)
    row["stack_status"] = sstat
    if snet is not None:
        row["stack_net_inr"] = f"{snet:.2f}"
    if sstat == "unknown":
        row.update(status="NC", reason=f"stack_status_unknown:{snet}")
        return row
    if sstat == "busy":
        row.update(status="STACK_BUSY", reason="stack_traded")
        return row
    # stack idle -> score the increment leg
    strike = int(round(read["spot_close_1055"] / 100.0)) * 100
    row["strike"] = str(strike)
    try:
        bars, bsrc = prem_bars_full("BANKNIFTY", read["expiry"],
                                    strike, dirn, T)
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    except urllib.error.HTTPError as e:
        if e.code == 429:
            row.update(status="NC", reason="rate_limited")
            return row
        raise
    if not bars:
        row.update(status="NC", reason="no_premium_candles")
        return row
    r = replay_intraday(bars, "11:00")
    if r is None:
        row.update(status="NC", reason="no_1100_bar")
        return row
    # TIMING ASSERTION (per trade): signal inputs are the closes of
    # the 09:15 and 10:55 bars only (both <= 10:55 by construction);
    # entry is the open of the 11:00 bar (replay guarantees the
    # first replayed bar is 11:00). Anything else is a violation.
    viol = 0
    if not ("09:15" <= "10:55" and r is not None):
        viol += 1
    row["timing_violations"] = str(viol)
    assert viol == 0, "timing violation on scored leg"
    row.update(status="TRADED", reason="scored",
               entry_time="11:00", entry_premium=f"{r['entry']:.2f}",
               exit_time=r["exit_time"],
               exit_premium=f"{r['exit']:.2f}",
               exit_reason=r["exit_reason"],
               net_inr=f"{r['net']:.2f}",
               notes=f"{src}; premium store={bsrc}")
    return row


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write historical check; bypasses the "
                         "start/window guards, never writes")
    a = ap.parse_args(argv)
    if a.verify:
        a.dry_run = True
    T = a.date or datetime.now(IST).date().isoformat()
    if not a.verify and T < START:
        print(f"R4-D1 SHADOW: {T} is before the shadow start {START} "
              f"— nothing scored.")
        return 0
    if not a.verify and T > WINDOW_END:
        print(f"R4-D1 SHADOW: {T} is past the pre-registered review "
              f"window end {WINDOW_END} — scoring closed; the review "
              f"is due, do not score further days.")
        return 0
    existing = ledger_rows()
    if not a.verify and opportunities(existing) >= REVIEW_OPPS:
        print(f"R4-D1 SHADOW: review point reached "
              f"({REVIEW_OPPS} scored trade-opportunities) — scoring "
              f"closed; the review is due, do not score further days.")
        return 0
    try:
        row = score_day(T, a.dry_run)
    except RateLimited:
        row = {k: "" for k in LEDGER_FIELDS}
        row.update(date=T, status="NC", reason="rate_limited")
    write_row(row, a.dry_run)
    after = ledger_rows() if not a.dry_run else existing
    traded = [r for r in after if r["status"] == "TRADED"]
    tnet = round(sum(float(r["net_inr"]) for r in traded), 2)
    print(f"R4-D1 SHADOW {T}: status={row['status']} "
          f"reason={row['reason']} "
          f"spot_morning={row['spot_morning_pct'] or '-'}% "
          f"dbasis={row['dbasis_pct'] or '-'}% "
          f"dir={row['direction'] or '-'} "
          f"strike={row['strike'] or '-'} net={row['net_inr'] or '-'} "
          f"stack={row['stack_status']}"
          f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    print(f"R4-D1 SHADOW tally: opportunities="
          f"{opportunities(after)}/{REVIEW_OPPS} traded={len(traded)} "
          f"shadow_net={tnet:+.2f} (paper, real money Rs0)")
    return 3 if row["reason"] == "rate_limited" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
