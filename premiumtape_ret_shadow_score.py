#!/usr/bin/env python3
"""PREMIUM-TAPE P-RET (STEP A) SHADOW SCORER — forward paper
evidence for the Bank Nifty PREMIUM-TAPE premium-retest family,
Step A configuration (set up 2026-11-14 under the owner's radio
rule: once a configuration is tuned and clears its bar, it moves
to the listening stage — forward paper — before any adoption).

WHAT THIS IS: a SCORE-ONLY paper shadow. PREMIUM-TAPE signals off
the option premium's OWN chart (not spot indicators): a contract's
premium breaks its own opening-range high, pulls back to its own
premium VWAP, and the retest hold is the entry. Round 3 Step A —
the 120-minute retest watch — CLEARED its pre-registered
desired-result bar on Jan-Oct 2026: 58 trades, +Rs16,692.50,
WR 48.3%, BOTH windows positive (Jan-Jun +Rs11,244.50 /
Jul-Oct +Rs5,448.00), random-entry placebo 99.4th percentile,
above the Round-2 control's +Rs12,132.50 (46 trades, 60-min
watch). It is armed nowhere and changes no running book; this
scorer only collects forward evidence, one evening at a time,
from Mon 2026-11-16 to the Nov 30 verdicts (the review bound).

FROZEN RULES (premium_tape_bank_SPEC.md +
premium_tape_bank_r2_SPEC.md + premium_tape_bank_r3_SPEC.md
Step A, verbatim):
- Each day: the CE and PE of the strike nearest spot at 09:15
  (100-step, exact half rounds up) of the in-force expiry (the
  OI-map expiry; November 2026-11-23 override). Spot is used ONLY
  for this 09:15 selection.
- Per contract-day, premium VWAP = cumulative volume-weighted
  typical price of that contract's own 5-min premium candles (the
  equal-weighted typical-price proxy only on a no-volume source);
  premium opening-range high = high of the bars labelled
  09:15..09:45 (7 bars).
- BREAK EVENT: the first bar i labelled in 09:50..14:20 whose
  premium close > premium opening-range high AND close > premium
  VWAP at bar i. Only the first event per contract-day is tracked.
- WATCH (Step A): bars j = i+1 .. min(i+24, the 14:25 bar) — 24
  watch bars = 120 minutes; no retest may complete after 14:25
  (entry by 14:30). RETEST HOLD at the first j with low[j] <=
  VWAP[j] AND close[j] > VWAP[j]; FAIL at the first j with
  close[j] <= VWAP[j] and no hold (event expires,
  close_below_vwap); if the watch ends with no hold, the event
  expires (window_end).
- DAY TRADE: the earliest completed retest across the two
  contracts. Same-bar tie: larger touch depth (VWAP[j] - low[j])
  first, then CE before PE. ONE trade per day. Entry = open of
  bar j+1.
- EXITS (X1 only): walk from the entry bar through the 15:20 bar;
  stop -50 checked before target +90 on each bar, fills AT the
  level; the entry bar itself can trigger; if neither is hit
  through the 15:20 bar, exit at the 15:20 close (the 15:20 bar
  is itself checked for level fills first).
- Net = (exit - entry) x 30 - Rs220. 1 lot (30). BUYING ONLY.
- A side is scoreable only if its premium series carries every
  bar labelled 09:15..15:20; a missing side is NC for the day —
  counted, never substituted, never estimated. Any missing
  contract/day data = UNSCORED with the reason named.

DATA SOURCING: EXACTLY the premium-tape builds' machinery — the
Round-1 definitions (premium_tape_bank_build.py, loaded the same
way premium_tape_bank_r3_build.py loads them): the progressive
spot store (09:15 selection), the in-force expiry map, and the
premium stores in frozen priority (round5 C5 store, then the
per-day candle folders btst_data / november_shadow_data /
nifty_weekly_expiry_chain / oi_buildup_data, then
daily2leg/prem_bank.json). For a FORWARD day (2026-11-16 on) not
yet in those stores, the scorer may fetch the day's spot bars via
the v3 route (cached to premiumtape_ret_spot_fwd.json) and the
day's contract candles via round 1's fetch machinery
(oi_buildup_score.fetch_bars, which caches into oi_buildup_data
in the shared convention); a day that still cannot be sourced is
UNSCORED with the reason — never estimated.

LEDGER: november_shadow_premiumtape_bank_log.csv — one row per
scored day (TRADED / NO_TRADE / NC + the reason named),
idempotent per date. The Nov 2-13 rows are seeded
BACKFILL_COUNTERFACTUAL (pre-shadow history, never live
evidence). Review bound: the scorer refuses to score days after
2026-11-30 (the Nov 30 verdicts decide the family's future; the
scorer says so).

DRY-RUN VERIFICATION (2026-11-14, --verify against November):
reproduces the Round-3 build's Step A November CF exactly —
3 trades, -Rs960.00 total, 1 win (Nov counts: 9 break events,
3 completed retests). --seed-backfill writes those rows only
after the same reproduction passes.

Paper only, real money Rs0. No live orders. Every
api.upstox.com call carries the browser User-Agent. On HTTP 429:
HARD STOP for the run — the day is marked NC rate_limited, no
retry, no route switch.

Usage:
    python3 premiumtape_ret_shadow_score.py [--date YYYY-MM-DD]
                        [--dry-run] [--verify] [--seed-backfill]
Default date = today (IST). --dry-run computes and prints the
row but writes NOTHING. --verify is a hard-wired no-write check
over Nov 2-13 (bypasses the start/window guards, never writes).
--seed-backfill writes ONLY the Nov 2-13 BACKFILL_COUNTERFACTUAL
rows, and only if the reproduction passes.
"""
import argparse, csv, json, sys
import importlib.util
import urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
COST = 220.0
LOT = 30
WATCH_BARS = 24             # Step A: 120-minute retest watch
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
LEDGER = TR / "november_shadow_premiumtape_bank_log.csv"
SPOT_FWD = TR / "premiumtape_ret_spot_fwd.json"
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
EXPECT_NOV_TRADES = 3
EXPECT_NOV_TOTAL = -960.00
EXPECT_NOV_WINS = 1

LEDGER_FIELDS = ["date", "row_type", "status", "reason", "side",
                 "strike", "expiry", "event_time", "retest_time",
                 "entry_time", "entry_premium", "exit_time",
                 "exit_premium", "exit_reason", "net_inr",
                 "timing_violations", "notes"]

# ---- the premium-tape builds' machinery, loaded EXACTLY as the
# ---- Round-3 build loads it (definitions only, no scoring runs)
_src = (TR / "premium_tape_bank_build.py").read_text()
_defs = _src.split("# ---------------- run a window ----------------")[0]
_ns = {"__name__": "premium_tape_bank_r1_defs",
       "__file__": str(TR / "premium_tape_bank_build.py")}
exec(compile(_defs, "premium_tape_bank_build.py(defs)", "exec"), _ns)

TIMES = _ns["TIMES"]; TIDX = _ns["TIDX"]
SPOT915 = _ns["SPOT915"]; EXP = _ns["EXP"]
get_day = _ns["get_day"]; load_side = _ns["load_side"]
score_exit = _ns["score_exit"]
_day_cache = _ns["_day"]

EVENT_LO = TIDX["09:50"]; EVENT_HI = TIDX["14:20"]
WATCH_HI = TIDX["14:25"]

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


# ---------------- forward-day spot (09:15 selection only) --------
def _csv_spot_915(fn):
    out = {}
    if not fn.exists():
        return out
    with open(fn) as f:
        for r in csv.DictReader(f):
            if r["timestamp"][11:16] == "09:15":
                out[r["timestamp"][:10]] = float(r["close"])
    return out


def _fetch_spot_915(day):
    """Fetch 09:15 Bank Nifty spot close with same-day v3 intraday fallback
    (fix 2026-11-25)."""
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
    bars = {c[0][11:16]: float(c[4]) for c in cd}
    if "09:15" not in bars:
        return None
    return bars["09:15"]


def _expiry_for(day):
    if day in EXP:
        return EXP[day]
    cand = sorted(set(EXP.values()) | {"2026-11-23", "2026-12-29"})
    fut = [e for e in cand if e >= day]
    return fut[0] if fut else None


def ensure_day(day, dry):
    """Make `day` loadable by the builds' machinery. Returns
    (ok, spot_source). Days already in the frozen stores need
    nothing; a forward day gets its 09:15 spot close from the
    November overlay store, this scorer's forward cache, or the
    v3 route (cached), plus its in-force expiry."""
    if day in SPOT915:
        return True, "stored"
    ov = _csv_spot_915(TR / "data/banknifty-2026-11/spot_5m.csv")
    close915 = ov.get(day)
    src = "overlay_2026_11"
    if close915 is None and SPOT_FWD.exists():
        cache = json.loads(SPOT_FWD.read_text())
        if day in cache:
            close915, src = cache[day], "fwd_cache"
    if close915 is None:
        close915 = _fetch_spot_915(day)  # may raise RateLimited
        src = "fetched_v3"
        if close915 is not None and not dry:
            cache = {}
            if SPOT_FWD.exists():
                cache = json.loads(SPOT_FWD.read_text())
            cache[day] = close915
            SPOT_FWD.write_text(json.dumps(cache))
    if close915 is None:
        return False, "spot_unavailable"
    exp = _expiry_for(day)
    if exp is None:
        return False, "no_expiry"
    SPOT915[day] = close915
    EXP[day] = exp
    _day_cache.pop(day, None)
    return True, src


def load_side_fwd(day, typ):
    """The builds' load_side, plus — for a day the stores miss —
    round 1's fetch machinery (caches into oi_buildup_data), then
    one reload. Returns the series dict or None (NC)."""
    s = load_side(day, typ)
    if s is not None:
        return s
    import math
    strike = int(math.floor(SPOT915[day] / 100 + 0.5)) * 100
    try:
        bars = obs.fetch_bars("BANKNIFTY", EXP[day], strike, typ, day)
    except Exception as e:
        if type(e).__name__ == "RateLimited" or \
                getattr(obs, "RateLimited", None) is type(e):
            raise RateLimited()
        bars = None
    if not bars:
        return None
    _day_cache.pop(day, None)
    return load_side(day, typ)


# ---------------- frozen Step A logic (Round-3 verbatim) ---------
def find_retest(s, start_i, watch_bars):
    """First break event at/after start_i (and >= EVENT_LO, <=
    EVENT_HI) and its watch outcome — premium_tape_bank_r3_build
    verbatim."""
    C, L, VW = s["C"], s["L"], s["VWAP"]
    lo = max(start_i, EVENT_LO)
    event_i = None
    for i in range(lo, EVENT_HI + 1):
        if C[i] > s["or_high"] and C[i] > VW[i]:
            event_i = i
            break
    if event_i is None:
        return dict(status="no_event", event_i=None, retest_i=None,
                    expiry_reason=None)
    end = min(event_i + watch_bars, WATCH_HI)
    for j in range(event_i + 1, end + 1):
        if L[j] <= VW[j] and C[j] > VW[j]:
            return dict(status="retest", event_i=event_i,
                        retest_i=j, expiry_reason=None)
        if C[j] <= VW[j]:
            return dict(status="expired", event_i=event_i,
                        retest_i=None, expiry_reason="close_below_vwap")
    return dict(status="expired", event_i=event_i, retest_i=None,
                expiry_reason="window_end")


# ---------------- ledger -----------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def write_rows(new_rows, replace_dates=True):
    rows = ledger_rows()
    if replace_dates:
        dates = {r["date"] for r in new_rows}
        rows = [r for r in rows if r["date"] not in dates]
    rows.extend(new_rows)
    rows.sort(key=lambda r: (r["date"], r["row_type"]))
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)


# ---------------- scoring flow -----------------------------------
def score_day(T, dry, row_type="SCORED"):
    row = {k: "" for k in LEDGER_FIELDS}
    row["date"] = T
    row["row_type"] = row_type
    try:
        ok, ssrc = ensure_day(T, dry)
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    if not ok:
        row.update(status="NC", reason=ssrc)
        return row
    sides, side_src = {}, {}
    try:
        for typ in ("CE", "PE"):
            sides[typ] = load_side_fwd(T, typ)
            if sides[typ] is not None:
                side_src[typ] = sides[typ]["src"]
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    nc_sides = [t for t in ("CE", "PE") if sides[t] is None]
    if len(nc_sides) == 2:
        row.update(status="NC", reason="both_sides_no_data",
                   notes=f"spot={ssrc}")
        return row
    cands, outcomes = [], []
    for typ in ("CE", "PE"):
        s = sides[typ]
        if s is None:
            outcomes.append(f"{typ}:nc")
            continue
        r = find_retest(s, EVENT_LO, WATCH_BARS)
        if r["status"] == "no_event":
            outcomes.append(f"{typ}:no_event")
            continue
        if r["status"] == "expired":
            outcomes.append(f"{typ}:expired_{r['expiry_reason']}")
            continue
        outcomes.append(f"{typ}:retest")
        cands.append(dict(
            side=typ, event_i=r["event_i"], retest_i=r["retest_i"],
            touch_depth=round(s["VWAP"][r["retest_i"]] -
                              s["L"][r["retest_i"]], 4)))
    note = f"spot={ssrc}; " + "; ".join(outcomes)
    if nc_sides:
        note += f"; side_nc={','.join(nc_sides)}"
    if not cands:
        has_event = any("expired" in o for o in outcomes)
        row.update(status="NO_TRADE",
                   reason=("retest_expired" if has_event
                           else "no_break_event"),
                   notes=note)
        return row
    cand = sorted(cands, key=lambda c: (c["retest_i"],
                                        -c["touch_depth"],
                                        0 if c["side"] == "CE"
                                        else 1))[0]
    s = sides[cand["side"]]
    r = score_exit(s, cand["retest_i"], "X1")
    if r is None:
        row.update(status="NC", reason="exit_unscoreable",
                   notes=note)
        return row
    entry_px, exit_px, xt, xreason = r
    net = round((exit_px - entry_px) * LOT - COST, 2)
    # TIMING ASSERTION: entry is exactly the bar after the retest
    # bar, at that bar's stored open (the frozen convention).
    viol = 0
    entry_time = TIMES[cand["retest_i"] + 1]
    if abs(entry_px - s["O"][cand["retest_i"] + 1]) > 1e-9:
        viol += 1
    row["timing_violations"] = str(viol)
    assert viol == 0, "timing violation on scored leg"
    note += (f"; premium={s['src']}; vwap={s['vwap_mode']}")
    row.update(status="TRADED", reason="scored", side=cand["side"],
               strike=str(s["strike"]), expiry=s["expiry"],
               event_time=TIMES[cand["event_i"]],
               retest_time=TIMES[cand["retest_i"]],
               entry_time=entry_time,
               entry_premium=f"{entry_px:.2f}", exit_time=xt,
               exit_premium=f"{exit_px:.2f}", exit_reason=xreason,
               net_inr=f"{net:.2f}", notes=note)
    return row


def _nov_check(rows):
    traded = [r for r in rows if r["status"] == "TRADED"]
    total = round(sum(float(r["net_inr"]) for r in traded), 2)
    wins = sum(1 for r in traded if float(r["net_inr"]) > 0)
    return traded, total, wins


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check over "
                         "Nov 2-13; bypasses the start/window "
                         "guards, never writes")
    ap.add_argument("--seed-backfill", action="store_true",
                    help="write ONLY the Nov 2-13 "
                         "BACKFILL_COUNTERFACTUAL rows, and only "
                         "if the reproduction passes")
    a = ap.parse_args(argv)

    if a.verify or a.seed_backfill:
        rows = []
        try:
            for d in NOV_DAYS:
                rows.append(score_day(d, True,
                                      row_type="BACKFILL_COUNTERFACTUAL"))
        except RateLimited:
            print("PREMIUM-TAPE P-RET SHADOW VERIFY: rate limited "
                  "during the November check — nothing written.")
            return 3
        traded, total, wins = _nov_check(rows)
        ok = (len(traded) == EXPECT_NOV_TRADES and
              total == EXPECT_NOV_TOTAL and wins == EXPECT_NOV_WINS)
        for r in rows:
            print(f"  {r['date']}: {r['status']} {r['reason']} "
                  f"{r['side'] or ''} {r['strike'] or ''} "
                  f"net={r['net_inr'] or '-'}")
        print(f"PREMIUM-TAPE P-RET SHADOW VERIFY (Nov 2-13, Step A): "
              f"trades={len(traded)} total={total:+.2f} wins={wins} "
              f"vs R3 build {EXPECT_NOV_TRADES} trades / "
              f"{EXPECT_NOV_TOTAL:+.2f} / {EXPECT_NOV_WINS} win — "
              f"{'PASS — exact reproduction' if ok else 'FAIL'}")
        if not ok:
            print("Nothing written.")
            return 1
        if a.seed_backfill:
            write_rows(rows)
            print(f"Seeded {len(rows)} BACKFILL_COUNTERFACTUAL rows "
                  f"into {LEDGER.name} (3 trades, {total:+.2f}).")
        else:
            print("(--verify: nothing written.)")
        return 0

    if a.dry_run:
        pass
    T = a.date or datetime.now(IST).date().isoformat()
    if T < START:
        print(f"PREMIUM-TAPE P-RET SHADOW: {T} is before the "
              f"shadow start {START} — nothing scored.")
        return 0
    if T > WINDOW_END:
        print(f"PREMIUM-TAPE P-RET SHADOW: {T} is past the review "
              f"bound {WINDOW_END} (the Nov 30 verdicts) — scoring "
              f"closed; the review is due, do not score further "
              f"days.")
        return 0
    try:
        row = score_day(T, a.dry_run)
    except RateLimited:
        row = {k: "" for k in LEDGER_FIELDS}
        row.update(date=T, row_type="SCORED", status="NC",
                   reason="rate_limited")
    if not a.dry_run:
        write_rows([row])
    after = ledger_rows() if not a.dry_run else []
    fwd = [r for r in after
           if r["row_type"] == "SCORED" and r["status"] == "TRADED"]
    fnet = round(sum(float(r["net_inr"]) for r in fwd), 2)
    bf = [r for r in after
          if r["row_type"] == "BACKFILL_COUNTERFACTUAL"
          and r["status"] == "TRADED"]
    print(f"PREMIUM-TAPE P-RET SHADOW {T}: status={row['status']} "
          f"reason={row['reason']} side={row['side'] or '-'} "
          f"strike={row['strike'] or '-'} "
          f"event={row['event_time'] or '-'} "
          f"retest={row['retest_time'] or '-'} "
          f"entry={row['entry_time'] or '-'}@"
          f"{row['entry_premium'] or '-'} "
          f"net={row['net_inr'] or '-'}"
          f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    if not a.dry_run:
        print(f"PREMIUM-TAPE P-RET SHADOW tally: forward "
              f"traded={len(fwd)} shadow_net={fnet:+.2f} "
              f"(backfill {len(bf)} trades, pre-shadow history, "
              f"excluded) (paper, real money Rs0)")
    return 3 if row["reason"] == "rate_limited" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
