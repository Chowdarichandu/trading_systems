#!/usr/bin/env python3
"""OI-V3 SHADOW SCORER — forward paper evidence for the Bank Nifty
OI-V3 "short-covering squeeze" INCREMENT (2026-11-13 night setup).

WHAT THIS IS: a SCORE-ONLY paper shadow. The gated OI programme
(oi_buildup_programme_2026-11-13.md, Part 2B + merge section) found
that V3 standalone FAILS its gate, but its legs on days TUNED STACK v2
is idle were +Rs3,360.00 over 42 legs Jan-Oct (merged book
Rs130,711.50, zero red months) with flipped halves — MERGE-ONLY
EVIDENCE, not a pass. This scorer collects the honest next test:
forward evidence, one evening at a time, from Mon 2026-11-16.

FROZEN RULES (Part 2B spec, verbatim — do not edit the spec here):
- Signal from day S's CLOSE data only (day-level OI dataset row S),
  traded on the next trading day T = S+1 session. No look-ahead: the
  scorer asserts signal_date < trade_date on every scored leg.
- V3 direction: CE iff CE quadrant = SHORT_COVERING and PE quadrant
  != LONG_BUILDUP; PE iff PE quadrant = SHORT_COVERING and CE
  quadrant != LONG_BUILDUP; else no signal. (Quadrants and the V3
  direction come from the programme's own code — oi_buildup_score.py
  imported unmodified, plus the direction3 extension exactly as in
  oi_buildup_run_bank.py.)
- INCREMENT CONDITION: the leg exists ONLY if TUNED STACK v2 placed
  no leg on T (read from november_shadow_stack_bank_log.csv — this
  scorer NEVER writes to that log or to any other book's ledger).
- Trade: ONE leg, entry at the OPEN of the 09:20 5-min bar, strike =
  ATM nearest 100 to that bar's spot open, contract = in-force
  monthly expiry of T, Bank G0 exits (stop -50 checked before target
  +90 on every bar incl. the entry bar, fills at the level, square-off
  at the 15:10 bar close), 1 lot of 30, cost Rs220/trade, BUYING ONLY.
- Premium candles: the programme's own route with its data-layer
  repair (prem_bars_full from oi_buildup_run_bank.py): the same
  stores the November shadow scoring uses; a stored series whose
  first bar is later than 09:20 counts as missing and the frozen
  fetch route supplies full-day candles.

FORWARD OI FEED: the historical dataset (oi_history/
banknifty_daily_oi.csv, frozen) ends 2026-11-11. Each later day D's
row is built from the option-chain archive: the earliest pre-open
bucket (< 09:15 IST) of the first archive file dated after D carries,
per strike, oi = D's close OI and prev_oi = D-1's close OI (this is
the exact construction the programme cross-validated to the contract
against the Nov 11 dataset row, and the one its Nov-12 supplementary
signal was read from). Band = the 11 strikes nearest D's spot close
(the bucket's spot = D's close); deltas are same-contract sums over
that band; status complete iff all 22 band contracts carry oi AND
prev_oi, else partial (partial days emit no signal, per the frozen
rule). Forward rows are appended to a SEPARATE file,
oi_history/banknifty_daily_oi_fwd.csv — the frozen historical
dataset is never modified. A day whose row cannot be built is NC
with the reason — never estimated, never skipped silently.

LEDGER: oi_v3_shadow_log.csv — one row per scored day (TRADE /
NO_SIGNAL / STACK_BUSY / NC + reason), idempotent per date (a re-run
replaces that date's row). Review point (pre-registered): after 20
scored trade-opportunities (days on which V3 produced a direction,
resolved TRADED or STACK_BUSY) or 2026-12-31, whichever comes first;
the scorer refuses to score beyond either bound and says so.

Paper only, real money Rs0. No live orders. Upstox calls use the
browser User-Agent (via the frozen scorer's get()); HTTP 429 is a
hard stop for the run — the day is marked NC rate_limited, no retry.

Usage:
    python3 oi_v3_shadow_score.py [--date YYYY-MM-DD] [--dry-run]
Default date = today (IST). --dry-run computes and prints the row
but writes NOTHING (no ledger row, no forward OI append). --verify
is a hard-wired no-write check against a historical date (it bypasses
the start/window guards for that check only, and can never write).
"""
import argparse, csv, json, sys
import importlib.util
import urllib.error
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-12-31"
REVIEW_OPPS = 20
HIST_OI = TR / "oi_history/banknifty_daily_oi.csv"
FWD_OI = TR / "oi_history/banknifty_daily_oi_fwd.csv"
ARCH = TR / "option_chain_archive"
STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
LEDGER = TR / "oi_v3_shadow_log.csv"
PROG_SPOT_5M = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
PROG_SPOT_DAILY = TR / "data/progressive/BANKNIFTY/spot_daily.csv"
SPOT_CACHE = TR / "oi_buildup_data"

OI_FIELDS = ["date", "expiry", "spot_close", "spot_chg_pts",
             "spot_chg_pct", "atm", "ce_oi", "pe_oi", "d_ce_oi",
             "d_pe_oi", "pcr_oi", "band_contracts", "delta_pairs",
             "status"]
LEDGER_FIELDS = ["date", "signal_date", "status", "reason",
                 "ce_quadrant", "pe_quadrant", "direction", "strike",
                 "expiry", "entry_time", "entry_premium", "exit_time",
                 "exit_premium", "exit_reason", "net_inr",
                 "stack_status", "stack_net_inr", "oi_row_source",
                 "notes"]

# ---- import the programme's frozen scorer, unmodified --------------
_spec = importlib.util.spec_from_file_location(
    "oi_buildup_score", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)

_orig_direction = obs.direction


def direction3(variant, q):
    """Copied verbatim from oi_buildup_run_bank.py (the frozen V3
    extension registered in Part 2B before any scoring)."""
    if variant == "V3":
        if q is None:
            return None
        ce, pe = q
        if ce == "SHORT_COVERING" and pe != "LONG_BUILDUP":
            return "CE"
        if pe == "SHORT_COVERING" and ce != "LONG_BUILDUP":
            return "PE"
        return None
    return _orig_direction(variant, q)


# ---- the run driver's data-layer repair, copied verbatim ------------
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


# ---------------- OI rows: historical + forward ----------------------
def _read_oi_file(path):
    rows = {}
    if path.exists():
        with open(path) as f:
            for r in csv.DictReader(f):
                rows[r["date"]] = r
    return rows


def merged_oi():
    rows = _read_oi_file(HIST_OI)
    rows.update(_read_oi_file(FWD_OI))
    return rows


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _archive_files_after(day):
    out = []
    for fn in sorted(ARCH.glob("banknifty_*.csv")):
        d = fn.stem.split("_", 1)[1]
        if d > day:
            out.append((d, fn))
    return out


def build_fwd_row(day, rows):
    """Build day `day`'s OI row from the earliest pre-open bucket of
    the first archive file dated after `day`. Returns (row, source)
    or (None, reason). `rows` = merged OI view (for the previous
    trading day's spot close)."""
    prev_dates = [d for d in rows if d < day]
    if not prev_dates:
        return None, "no_prior_oi_row_for_spot_chg"
    prev_close = _num(rows[max(prev_dates)]["spot_close"])
    if prev_close is None:
        return None, "prior_spot_close_unreadable"
    files = _archive_files_after(day)
    if not files:
        return None, "no_archive_file_after_day"
    fdate, fn = files[0]
    with open(fn) as f:
        arows = [r for r in csv.DictReader(f)
                 if r["index"] == "BANKNIFTY"]
    if not arows:
        return None, f"archive_file_empty:{fn.name}"
    buckets = sorted({r["bucket_ist"] for r in arows})
    first = buckets[0]
    if first[11:16] >= "09:15":
        return None, f"first_bucket_not_preopen:{first}"
    snap = [r for r in arows if r["bucket_ist"] == first]
    spots = {_num(r["spot"]) for r in snap} - {None}
    if len(spots) != 1:
        return None, "bucket_spot_ambiguous"
    spot_close = spots.pop()
    expiries = {r["expiry"] for r in snap if r["expiry"]}
    if len(expiries) != 1:
        return None, "bucket_expiry_ambiguous"
    expiry = expiries.pop()
    atm = int(round(spot_close / 100.0)) * 100
    band = [atm + 100 * k for k in range(-5, 6)]
    by_strike = {int(float(r["strike"])): r for r in snap}
    ce_oi = pe_oi = d_ce = d_pe = 0.0
    contracts = pairs = 0
    for st in band:
        r = by_strike.get(st)
        if r is None:
            continue
        for side in ("ce", "pe"):
            oi = _num(r[f"{side}_oi"])
            poi = _num(r[f"{side}_prev_oi"])
            if oi is not None:
                contracts += 1
                if side == "ce":
                    ce_oi += oi
                else:
                    pe_oi += oi
            if oi is not None and poi is not None:
                pairs += 1
                if side == "ce":
                    d_ce += oi - poi
                else:
                    d_pe += oi - poi
    chg = round(spot_close - prev_close, 2)
    row = {"date": day, "expiry": expiry,
           "spot_close": f"{spot_close:.2f}",
           "spot_chg_pts": f"{chg:.2f}",
           "spot_chg_pct": f"{round(100.0 * chg / prev_close, 3):.3f}",
           "atm": str(atm),
           "ce_oi": f"{ce_oi:.1f}", "pe_oi": f"{pe_oi:.1f}",
           "d_ce_oi": f"{d_ce:.1f}", "d_pe_oi": f"{d_pe:.1f}",
           "pcr_oi": f"{round(pe_oi / ce_oi, 4):.4f}" if ce_oi else "",
           "band_contracts": str(contracts),
           "delta_pairs": str(pairs),
           "status": "complete" if contracts == 22 and pairs == 22
                     else "partial"}
    return row, f"archive:{fn.name}@{first}"


def ensure_fwd_rows(signal_day, rows, dry):
    """Build any missing forward rows from 2026-11-12 up to
    signal_day (in date order — each row's spot change chains off the
    previous row). Returns (ok, reason). Appends new rows to the fwd
    file unless dry."""
    built = []
    d = datetime(2026, 11, 12).date()
    end = datetime.strptime(signal_day, "%Y-%m-%d").date()
    while d <= end:
        ds = d.isoformat()
        if ds not in rows:
            row, src = build_fwd_row(ds, rows)
            if row is None:
                return False, f"oi_row_unbuildable:{ds}:{src}"
            row["_source"] = src
            rows[ds] = row
            built.append(row)
        d += timedelta(days=1)
    if built and not dry:
        newfile = not FWD_OI.exists()
        with open(FWD_OI, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=OI_FIELDS)
            if newfile:
                w.writeheader()
            for row in built:
                w.writerow({k: row[k] for k in OI_FIELDS})
    return True, "ok"


# ---------------- stack status ---------------------------------------
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


# ---------------- spot 09:20 open ------------------------------------
def spot_0920_open(day):
    """Open of the day's 09:20 5-min spot bar. Store first (the
    progressive spot store the November machinery persists nightly),
    then the frozen scorer's own v3 intraday route; cached. Raises
    obs.RateLimited on HTTP 429 (hard stop)."""
    if PROG_SPOT_5M.exists():
        with open(PROG_SPOT_5M) as f:
            for r in csv.DictReader(f):
                ts = r["timestamp"]
                if ts[:10] == day and ts[11:16] == "09:20":
                    return float(r["open"]), "progressive_store"
    fn = SPOT_CACHE / f"spot_BANKNIFTY_{day}.json"
    if fn.exists():
        cd = [c for c in ((json.loads(fn.read_text()).get("data") or {})
                          .get("candles") or []) if c[0][:10] == day]
        for c in cd:
            if c[0][11:16] == "09:20":
                return float(c[1]), "fetched_cache"
    url = (f"{obs.API}/v3/historical-candle/"
           f"{quote(obs.IDXKEY['BANKNIFTY'], safe='')}"
           f"/minutes/5/{day}/{day}")
    today_s = datetime.now(IST).date().isoformat()
    try:
        body = obs.get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise obs.RateLimited()
        body = None
    cd = [c for c in (((body or {}).get("data") or {}).get("candles") or [])
          if c[0][:10] == day]
    if not cd and day == today_s:
        intraday_url = (f"{obs.API}/v3/historical-candle/intraday/"
                        f"{quote(obs.IDXKEY['BANKNIFTY'], safe='')}/minutes/5")
        try:
            body = obs.get(intraday_url)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise obs.RateLimited()
            return None, None
        cd = [c for c in (((body or {}).get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
    if not cd:
        return None, None
    fn.write_text(json.dumps(body))
    for c in cd:
        if c[0][11:16] == "09:20":
            return float(c[1]), "fetched"
    return None, None


def trade_day_expiry(day):
    fn = ARCH / f"banknifty_{day}.csv"
    if not fn.exists():
        return None
    exps = {}
    with open(fn) as f:
        for r in csv.DictReader(f):
            if r["index"] == "BANKNIFTY" and r["expiry"]:
                exps[r["expiry"]] = exps.get(r["expiry"], 0) + 1
    return max(exps, key=exps.get) if exps else None


def _prog_spot_close(day):
    if PROG_SPOT_DAILY.exists():
        with open(PROG_SPOT_DAILY) as f:
            for r in csv.DictReader(f):
                if r["date"] == day:
                    return float(r["close"])
    return None


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
    rows = merged_oi()
    # signal day = latest weekday before T whose row exists or builds
    S = None
    d = datetime.strptime(T, "%Y-%m-%d").date() - timedelta(days=1)
    for _ in range(5):
        if d.weekday() < 5:  # Mon-Fri
            S = d.isoformat()
            break
        d -= timedelta(days=1)
    if S is None:
        row.update(status="NC", reason="no_signal_day_found")
        return row
    row["signal_date"] = S
    ok, why = ensure_fwd_rows(S, rows, dry)
    if not ok:
        row.update(status="NC", reason=why)
        return row
    srow = rows[S]
    row["oi_row_source"] = srow.get("_source", "dataset")
    # spot-close cross-check vs the November machinery's daily store
    # Fix (2026-11-25): progressive spot_daily.csv stores the 15:25 5-min bar
    # close, whereas the pre-open option-chain archive carries the exchange
    # official weighted close. On Bank Nifty those legitimately differ by
    # ~40-250 pts (0.07%-0.40%), so a 0.05-rupee tolerance falsely NC'd 100%
    # of live days. Keep a 1.5% corruption/wrong-date guard and record the
    # exact official-vs-15:25 difference in `notes`.
    pclose = _prog_spot_close(S)
    spot_diff_note = ""
    if pclose is not None and pclose > 0:
        sclose = float(srow["spot_close"])
        rel_diff = abs(pclose - sclose) / pclose
        if rel_diff > 0.015:
            row.update(status="NC",
                       reason=f"oi_row_spot_mismatch:{srow['spot_close']}"
                              f"_vs_progressive_{pclose}")
            return row
        if abs(pclose - sclose) > 0.05:
            spot_diff_note = (f"official_vs_1525_diff="
                              f"{sclose - pclose:+.2f}pts")
    sstat, snet = stack_status(T)
    row["stack_status"] = sstat
    if snet is not None:
        row["stack_net_inr"] = f"{snet:.2f}"
    if srow["status"] != "complete":
        row.update(status="NO_SIGNAL", reason="signal_day_partial")
        return row
    q = obs.quadrants(srow)
    if q is None:
        row.update(status="NO_SIGNAL", reason="signal_quadrants_none")
        return row
    row["ce_quadrant"], row["pe_quadrant"] = q
    dirn = direction3("V3", q)
    if dirn is None:
        row.update(status="NO_SIGNAL", reason="v3_no_signal")
        return row
    row["direction"] = dirn
    # V3 produced a direction: the day is a scored trade-opportunity.
    if sstat == "unknown":
        row.update(status="NC", reason=f"stack_status_unknown:{snet}")
        return row
    if sstat == "busy":
        row.update(status="STACK_BUSY", reason="stack_traded")
        return row
    # stack idle -> score the increment leg
    exp = trade_day_expiry(T)
    if exp is None:
        row.update(status="NC", reason="trade_day_expiry_unknown")
        return row
    row["expiry"] = exp
    try:
        sopen, ssrc = spot_0920_open(T)
        if sopen is None:
            row.update(status="NC", reason="spot_0920_unavailable")
            return row
        strike = int(round(sopen / 100.0)) * 100
        row["strike"] = str(strike)
        bars, bsrc = prem_bars_full("BANKNIFTY", exp, strike, dirn, T)
        if not bars:
            row.update(status="NC", reason="no_premium_candles")
            return row
        r = obs.replay_g0(bars, 30)
        if r is None:
            row.update(status="NC", reason="replay_none")
            return row
    except obs.RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    assert S < T, "timing violation: signal day not before trade day"
    note_parts = [f"premium store={bsrc}", f"spot src={ssrc}"]
    if spot_diff_note:
        note_parts.append(spot_diff_note)
    row.update(status="TRADED", reason="scored",
               entry_time="09:20", entry_premium=f"{r['entry']:.2f}",
               exit_time=r["exit_time"],
               exit_premium=f"{r['exit']:.2f}",
               exit_reason=r["exit_reason"],
               net_inr=f"{r['net']:.2f}",
               notes="; ".join(note_parts))
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
        print(f"OI-V3 SHADOW: {T} is before the shadow start {START} "
              f"— nothing scored.")
        return 0
    if not a.verify and T > WINDOW_END:
        print(f"OI-V3 SHADOW: {T} is past the pre-registered review "
              f"window end {WINDOW_END} — scoring closed; the review "
              f"is due, do not score further days.")
        return 0
    existing = ledger_rows()
    if not a.verify and opportunities(existing) >= REVIEW_OPPS:
        print(f"OI-V3 SHADOW: review point reached "
              f"({REVIEW_OPPS} scored trade-opportunities) — scoring "
              f"closed; the review is due, do not score further days.")
        return 0
    try:
        row = score_day(T, a.dry_run)
    except obs.RateLimited:
        row = {k: "" for k in LEDGER_FIELDS}
        row.update(date=T, status="NC", reason="rate_limited")
    write_row(row, a.dry_run)
    after = ledger_rows() if not a.dry_run else existing
    traded = [r for r in after if r["status"] == "TRADED"]
    tnet = round(sum(float(r["net_inr"]) for r in traded), 2)
    print(f"OI-V3 SHADOW {T}: status={row['status']} "
          f"reason={row['reason']} signal_day={row['signal_date']} "
          f"quadrants=({row['ce_quadrant']},{row['pe_quadrant']}) "
          f"dir={row['direction'] or '-'} "
          f"strike={row['strike'] or '-'} net={row['net_inr'] or '-'} "
          f"stack={row['stack_status']}"
          f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    print(f"OI-V3 SHADOW tally: opportunities="
          f"{opportunities(after)}/{REVIEW_OPPS} traded={len(traded)} "
          f"shadow_net={tnet:+.2f} (paper, real money Rs0)")
    return 3 if row["reason"] == "rate_limited" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
