#!/usr/bin/env python3
"""STOCK ENGINE — LIVE SHADOW (VARIANT D DESIGN) — EOD SCORER.

Armed 2026-11-11 under the owner's delegation (2026-11-11 18:59-19:00
IST: design choices delegated; the v2 verdict in
sarvasetu_top3_v2_2026-11-11.md named variant D the winner; the owner
was told D goes live Thu 2026-11-12 unless the proof killed it — it
did not). Paper only, real Rs0, no orders. This scorer is the OFFICIAL
ledger path for Stock Engine from 2026-11-12. It supersedes the
unfiltered 4-intraday-component wide shadow design before that design
ever traded a live day (its producer survives, reworked, as the
intraday CANDIDATE layer — candidates are never counted picks).

THE DESIGN (LIVE SHADOW SPEC — Stock Engine, variant D, verbatim
from sarvasetu_top3_v2_2026-11-11.md):
  - Universe: the Stock Engine 1,081-name liquid NSE list
    (wide_nse_universe_2026-11-11.csv).
  - Candidate pool (daily, EOD-scored): every trade the November
    whole book would take that day across all seven components —
    F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND — via the
    book's own machinery (stocks_sarvaritu_logger.build_book family,
    v2/C24 law, C22-form INV-ABOVE, merged machinery event calendar),
    each trade carrying its native trigger magnitude. The machinery
    is imported from sarvasetu_top3_build.py (V1) — the identical
    code path that produced the anchored retrospective pools
    (25-restriction reproduces the frozen paper log trade-for-trade).
  - Ranking (the fixed rule): one representative per (stock,
    component) = that component's earliest trade on the stock that
    day. Each component's representative magnitudes are normalised
    to a within-day, within-component percentile (position
    percentile, best = 100). Confluence = distinct components
    flagging the stock-day (PRIMARY key); owner = the component with
    the highest normalised percentile (ties: earliest entry, then
    component name); score = confluence x 100 + owner percentile.
    Rank stock-days by score desc, then stock symbol.
  - Selection (variant D): from the ranked list take the first 6
    stock-days satisfying BOTH owner percentile >= 90 (conviction
    floor) AND owner-trade entry price <= Rs5,000 (price-risk cap).
    Fewer qualifying -> take what exists; NEVER pad. One trade per
    stock-day, under the owning component's own construction.
  - Scoring: each pick scored exactly as its component runs it
    (frozen geometries; square-off 15:10), Rs40/trade. TWO bases are
    logged for every pick: (primary) provisional per 100 shares;
    (secondary) fixed-capital lens at Rs25,000/trade notional —
    shares = floor(25,000/entry), min 1 (entry > Rs25,000 -> 1
    share, flagged in the retrospective; the Rs5,000 cap makes that
    case unreachable here). Judging is ex-top-3 first, on both bases.

DATA PATH (live): after the close, the day's completed 5-minute bars
for every universe name are fetched from the Upstox v3 intraday
endpoint — the identical source that supplied 2026-11-11's bars to
the retrospective bar store — with the mandatory browser User-Agent;
any HTTP 429 aborts the run BEFORE any write (hard stop, no retry
inside the run). Bars are appended to the rolling wide root
(data/wide1081_nov: spot_5m.csv + derived spot_daily.csv per symbol,
the exact format sarvasetu_top3_build.build_root created) and to the
bar-store JSON archive. NIFTY (regime input) is synced from the
frozen forward root data/sarvaritu_fwd (read-only source): its 5m
file is copied over, and a daily row for the target day is derived
from those bars if the forward daily file has not landed yet
(derivation verified byte-identical to the forward daily row on
2026-11-11). Event calendar: the machinery merged calendar UNION
the wide producer's accumulating calendar (curated seed + NSE
snapshots), deduped on (stock, event_date, event_type); producer
rows with no stored reaction date get the frozen convention —
first NIFTY trading day strictly after the event date — and rows
whose reaction date is after the target day are excluded (not due).

IDEMPOTENCY: a date already finalised in the state file (or present
in the ledger) is never re-scored or re-written; the run prints
status already_finalised. A day with no bars market-wide is recorded
as a holiday (no_trading_data) and never scored as zero. A day whose
data is incomplete (coverage < 95% of the universe with >= 50 bars,
or no regime label for the day) prints data_not_ready and writes NO
ledger rows — a later run the same evening retries.

Modes:
  (default)        score today (IST), fetching the day's bars first.
  --date YYYY-MM-DD  score that date instead.
  --offline        do not fetch; score from the root as it stands
                   (verification / catch-up path).
  --dry-run        dry outputs only (ledger/state .dryrun files).

Outputs:
  sarvasetu_top3_shadow_log.csv        OFFICIAL ledger (append-only)
  sarvasetu_top3_shadow_state.json     finalised dates + day summaries
  sarvasetu_top3_eod_scorer.log        run log
Stdout: STOCK_ENGINE_PICK lines (one per pick) + one
STOCK_ENGINE_EOD_SUMMARY JSON line.
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stocks_sarvaritu_logger as L
import stocks_wide_nse_shadow_producer as wide

IST = ZoneInfo("Asia/Kolkata")
ROOT = V1.ROOT
BARS = V1.BARS
MERGED_CAL = V1.MERGED_CAL
PROD_CAL = wide.RAW_CAL
RUNTIME_CAL = f"{WS}/screen_work/sarvasetu_live_calendar_runtime.csv"
FWD_NIFTY = f"{WS}/data/sarvaritu_fwd/NIFTY"
LEDGER = f"{WS}/sarvasetu_top3_shadow_log.csv"
LEDGER_DRY = f"{WS}/sarvasetu_top3_shadow_log.dryrun.csv"
STATE_F = f"{WS}/sarvasetu_top3_shadow_state.json"
STATE_DRY = f"{WS}/sarvasetu_top3_shadow_state.dryrun.json"
SLOG = f"{WS}/sarvasetu_top3_eod_scorer.log"
STORE_LO = "2026-09-30"
FLOOR_PCT = 90.0
PRICE_CAP = 5000.0
TOPN = 6
COV_MIN = 0.95
CAL_FIELDS = ["stock", "event_date", "event_type", "detail", "after_market",
              "source", "source_url", "reaction_date", "window_start",
              "window_end", "known_before_open", "coverage"]
LEDGER_FIELDS = ["date", "rank", "stock", "comp", "dir", "confluence",
                 "components", "native_magnitude", "mag_kind", "norm_pct",
                 "score", "entry_time", "entry", "exit_time", "exit",
                 "exit_reason", "net", "fc_shares", "fc_net", "regime",
                 "mode"]
MODE = "STOCK-ENGINE"
SYMS = V1.SYMS


def slog(msg):
    line = f"{datetime.now(IST).isoformat(timespec='seconds')} {msg}"
    with open(SLOG, "a") as f:
        f.write(line + "\n")


def summary(**kw):
    print(f"STOCK_ENGINE_EOD_SUMMARY {json.dumps(kw)}", flush=True)
    slog(f"summary {json.dumps(kw)[:600]}")


# ------------------------------------------------------------ calendar
def build_runtime_calendar(target):
    """Machinery merged calendar UNION the wide producer's
    accumulating calendar. Producer rows with a blank reaction date
    get the frozen convention (first NIFTY trading day strictly after
    the event date); rows not yet due (reaction > target) are
    excluded. Returns (rows_written, added_from_producer)."""
    rows, have = [], set()
    for r in csv.DictReader(open(MERGED_CAL)):
        row = {k: r.get(k, "") for k in CAL_FIELDS}
        rows.append(row)
        have.add((row["stock"], row["event_date"][:10], row["event_type"]))
    nifty_dates = set()
    p = f"{ROOT}/NIFTY/spot_daily.csv"
    if os.path.exists(p):
        nifty_dates = {r["date"][:10] for r in csv.DictReader(open(p))}
    nifty_dates.add(target)
    trading = sorted(nifty_dates)
    added = 0
    if os.path.exists(PROD_CAL):
        for r in csv.DictReader(open(PROD_CAL)):
            key = (r["stock"], (r["event_date"] or "")[:10], r["event_type"])
            if key in have or not key[1]:
                continue
            react = (r.get("reaction_date") or "")[:10]
            if not react:
                later = [d for d in trading if d > key[1]]
                if not later:
                    continue
                react = later[0]
            if react > target:
                continue
            row = {k: r.get(k, "") for k in CAL_FIELDS}
            row["reaction_date"] = react
            rows.append(row)
            have.add(key)
            added += 1
    with open(RUNTIME_CAL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAL_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows), added


# ------------------------------------------------------------ data root
def _daily_dates(sym):
    p = f"{ROOT}/{sym}/spot_daily.csv"
    if not os.path.exists(p):
        return set()
    return {r["date"][:10] for r in csv.DictReader(open(p))}


def append_day(sym, target, bars):
    """Append one day's bars to the bar-store JSON and the root CSVs
    (build_root's exact formats). Caller guarantees the symbol-day is
    absent from the root daily file. bars: [{timestamp 'YYYY-MM-DD
    HH:MM:SS', time, open, high, low, close}] sorted."""
    bars = sorted(bars, key=lambda b: b["timestamp"])
    jp = f"{BARS}/{sym}.json"
    if os.path.exists(jp):
        data = json.load(open(jp))
        if target not in data:
            data[target] = bars
            json.dump(data, open(jp, "w"))
    p5 = f"{ROOT}/{sym}/spot_5m.csv"
    have5 = False
    if os.path.exists(p5):
        with open(p5) as f:
            have5 = any(line.startswith(target) for line in f)
    if not have5:
        with open(p5, "a", newline="") as f:
            w = csv.writer(f)
            for b in bars:
                w.writerow([f"{b['timestamp']}+05:30", b["open"], b["high"],
                            b["low"], b["close"]])
    daily = {"date": target, "open": bars[0]["open"],
             "high": max(b["high"] for b in bars),
             "low": min(b["low"] for b in bars),
             "close": bars[-1]["close"]}
    pd_ = f"{ROOT}/{sym}/spot_daily.csv"
    if target not in _daily_dates(sym):
        with open(pd_, "a", newline="") as f:
            w = csv.writer(f)
            w.writerow([daily["date"], daily["open"], daily["high"],
                        daily["low"], daily["close"]])
    return daily


def sync_nifty(target):
    """Sync ROOT/NIFTY from the frozen forward root (read-only
    source): copy the 5m file; daily = forward daily rows plus a
    derived row for any 5m date not yet in the daily file
    (derivation verified identical to the forward daily row on
    2026-11-11). Returns NIFTY's last daily date in the root."""
    src5 = f"{FWD_NIFTY}/spot_5m.csv"
    dst5 = f"{ROOT}/NIFTY/spot_5m.csv"
    rows5 = list(csv.reader(open(src5)))
    with open(dst5, "w", newline="") as f:
        csv.writer(f).writerows(rows5)
    daily = {}
    for r in csv.DictReader(open(f"{FWD_NIFTY}/spot_daily.csv")):
        daily[r["date"][:10]] = [r["date"][:10], r["open"], r["high"],
                                 r["low"], r["close"]]
    by_day = defaultdict(list)
    for r in rows5[1:]:
        by_day[r[0][:10]].append(r)
    for d, rs in sorted(by_day.items()):
        if d in daily:
            continue
        rs.sort(key=lambda r: r[0])
        daily[d] = [d, rs[0][1], max(float(x[2]) for x in rs),
                    min(float(x[3]) for x in rs), rs[-1][4]]
    with open(f"{ROOT}/NIFTY/spot_daily.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close"])
        for d in sorted(daily):
            w.writerow(daily[d])
    return max(daily) if daily else None


def fetch_missing(target, missing):
    """Fetch today's bars for the missing symbols via the wide
    producer's guarded fetch (browser UA; 429 raises wide.RateLimited
    BEFORE anything is written). Returns {sym: bars-on-target}."""
    fetched = wide.fetch_many(missing)
    out = {}
    for sym, bars in fetched.items():
        tb = [b for b in (bars or []) if b["timestamp"][:10] == target]
        if tb:
            out[sym] = tb
    return out


# ------------------------------------------------------------ selection
def select_variant_d(pool, target):
    """Variant D selection — the ranking block of
    sarvasetu_top3_v2_build.py's main(), verbatim logic, restricted
    to one day's pool. Returns pick records in rank order."""
    reps = {}
    for t in pool:
        k = (t["date"], t["stock"], t["comp"])
        cur = reps.get(k)
        if cur is None or (t["entry_time"], t.get("round", 0)) < \
                (cur["entry_time"], cur.get("round", 0)):
            reps[k] = t
    by_dc = defaultdict(list)
    for (d, s, c) in reps:
        by_dc[(d, c)].append((d, s, c))
    norm_pct = {}
    for (d, c), keys in by_dc.items():
        keys.sort(key=lambda k: (-reps[k]["magnitude"],
                                 reps[k]["entry_time"], k[1]))
        n = len(keys)
        for i, k in enumerate(keys):
            norm_pct[k] = round(100.0 * (n - i) / n, 2)
    by_sd = defaultdict(set)
    for (d, s, c) in reps:
        by_sd[(d, s)].add(c)
    sd = {}
    for (d, s), comps in by_sd.items():
        comp_pct = {c: norm_pct[(d, s, c)] for c in comps}
        owner = sorted(comps, key=lambda c: (-comp_pct[c],
                                             reps[(d, s, c)]["entry_time"],
                                             c))[0]
        sd[(d, s)] = {"date": d, "stock": s, "confluence": len(comps),
                      "components": sorted(comps), "comp_pct": comp_pct,
                      "owner": owner, "owner_pct": comp_pct[owner],
                      "trade": reps[(d, s, owner)],
                      "score": len(comps) * 100 + comp_pct[owner]}
    recs = [r for (dd, _s), r in sd.items() if dd == target]
    recs.sort(key=lambda r: (-r["score"], r["stock"]))
    for i, r in enumerate(recs):
        r["rank"] = i + 1
    picks = []
    for r in recs:
        if r["owner_pct"] < FLOOR_PCT:
            continue
        e = r["trade"]["entry"]
        if (e if e is not None else float("inf")) > PRICE_CAP:
            continue
        picks.append(r)
        if len(picks) == TOPN:
            break
    return picks


def lens(trade):
    """Fixed-capital lens (Rs25,000/trade) — v2's formula verbatim."""
    e = trade["entry"]
    shares = 1 if (e is None or e > 25000) else max(1, math.floor(25000.0 / e))
    fc_net = round(((trade["net"] + 40.0) / 100.0) * shares - 40.0, 2)
    return shares, fc_net


# ------------------------------------------------------------ main flow
def load_state(path):
    if os.path.exists(path):
        try:
            return json.load(open(path))
        except Exception:
            pass
    return {"finalised": {}, "holidays": []}


def ledger_rows(path):
    if not os.path.exists(path):
        return []
    return list(csv.DictReader(open(path)))


def run(target, offline=False, dry=False):
    ledger_path = LEDGER_DRY if dry else LEDGER
    state_path = STATE_DRY if dry else STATE_F
    state = load_state(state_path)
    if datetime.fromisoformat(target).weekday() >= 5:
        summary(date=target, status="weekend", dry_run=dry)
        return 0
    if target in state.get("finalised", {}) or \
            any(r["date"] == target for r in ledger_rows(ledger_path)):
        summary(date=target, status="already_finalised", dry_run=dry)
        return 0
    if target in state.get("holidays", []):
        summary(date=target, status="no_trading_data", dry_run=dry)
        return 0

    # ---- data extension (live mode) ----
    fetched_n = 0
    if not offline:
        sync_nifty(target)
        missing = [s for s in SYMS if target not in _daily_dates(s)]
        if missing:
            try:
                got = fetch_missing(target, missing)
            except wide.RateLimited as e:
                summary(date=target, status="rate_limited_429",
                        dry_run=dry, detail=str(e)[:120])
                return 1
            for sym, bars in got.items():
                if len(bars) >= 50:
                    append_day(sym, target, bars)
                    fetched_n += 1
            slog(f"{target}: fetched+appended {fetched_n} symbols "
                 f"({len(missing)} were missing)")
    have = sum(1 for s in SYMS if target in _daily_dates(s))
    coverage = have / len(SYMS)
    if have == 0:
        state.setdefault("holidays", []).append(target)
        json.dump(state, open(state_path, "w"), indent=1)
        summary(date=target, status="no_trading_data", dry_run=dry,
                coverage=0.0)
        return 0
    if coverage < COV_MIN:
        summary(date=target, status="data_not_ready", dry_run=dry,
                coverage=round(coverage, 4), symbols_with_day=have)
        return 0

    # ---- machinery + pool for the target day ----
    n_cal, cal_added = build_runtime_calendar(target)
    g = V1.load_machinery(ROOT, target)
    if not any(dd == target for (_s, dd) in g["DAYCTX"]):
        summary(date=target, status="data_not_ready", dry_run=dry,
                coverage=round(coverage, 4), detail="target not in DAYCTX")
        return 0
    labels = L.regime_labels(g)
    if labels.get(target) in (None, "UNCLASSIFIED"):
        summary(date=target, status="data_not_ready", dry_run=dry,
                coverage=round(coverage, 4),
                detail="no regime label for target (NIFTY context stale)")
        return 0
    pct, _pool_sizes = V1.inv_pool_percentiles(g, [target])
    pool = V1.build_book_detailed(g, RUNTIME_CAL, STORE_LO, target,
                                  [target], pct)
    pool = [t for t in pool if t["date"] == target]

    # ---- selection + ledger write ----
    picks = select_variant_d(pool, target)
    rows = []
    for p in picks:
        t = p["trade"]
        shares, fc_net = lens(t)
        rows.append({"date": target, "rank": p["rank"], "stock": p["stock"],
                     "comp": p["owner"], "dir": t["dir"],
                     "confluence": p["confluence"],
                     "components": "+".join(p["components"]),
                     "native_magnitude": t["magnitude"],
                     "mag_kind": t["mag_kind"], "norm_pct": p["owner_pct"],
                     "score": round(p["score"], 2),
                     "entry_time": t["entry_time"], "entry": t["entry"],
                     "exit_time": t["exit_time"], "exit": t["exit"],
                     "exit_reason": t["exit_reason"], "net": t["net"],
                     "fc_shares": shares, "fc_net": fc_net,
                     "regime": t["regime"], "mode": MODE})
    exists = os.path.exists(ledger_path)
    with open(ledger_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    day_net = round(sum(r["net"] for r in rows), 2)
    day_fc = round(sum(r["fc_net"] for r in rows), 2)
    state.setdefault("finalised", {})[target] = {
        "picks": len(rows), "net": day_net, "fc_net": day_fc,
        "pool_trades": len(pool), "coverage": round(coverage, 4),
        "regime": labels.get(target), "calendar_rows": n_cal,
        "calendar_added_from_producer": cal_added,
        "fetched_symbols": fetched_n}
    json.dump(state, open(state_path, "w"), indent=1)

    allrows = ledger_rows(ledger_path)
    mtd_net = round(sum(float(r["net"]) for r in allrows), 2)
    mtd_fc = round(sum(float(r["fc_net"]) for r in allrows), 2)
    ex3, top3 = V1.extop3([{"stock": r["stock"], "net": float(r["net"])}
                           for r in allrows])
    for r in rows:
        print(f"STOCK_ENGINE_PICK {json.dumps(r)}", flush=True)
    summary(date=target, status="finalised", dry_run=dry,
            regime=labels.get(target), pool_trades=len(pool),
            picks=rows, day_net=day_net, day_fc_net=day_fc,
            mtd_trades=len(allrows), mtd_net=mtd_net, mtd_fc_net=mtd_fc,
            mtd_ex_top3=ex3, mtd_top3_stocks=top3,
            coverage=round(coverage, 4))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    target = args.date or datetime.now(IST).date().isoformat()
    return run(target, offline=args.offline, dry=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
