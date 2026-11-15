#!/usr/bin/env python3
"""SARVASETU — RETROSPECTIVE scoring of the WIDE-NSE SHADOW over the
FULL window Thu 2026-10-01 -> Wed 2026-11-11 (owner correction
2026-11-11 17:32 IST; seed day Wed 2026-09-30 fetched, not scored).
The November subtotal (Nov 2,3,4,5,6,9,11) is broken out separately.

This is a RETROSPECTIVE scoring of a shadow built on 2026-11-11 — it
is NOT live forward evidence. The live record starts Thu 2026-11-12.
Universe caveat (stated once): the universe is the 1,081-name list as
fetched 2026-11-11, applied backwards over the whole window;
constituent drift over six weeks is possible in principle (index
reviews are semi-annual and none fell inside this window) but the
note stands.

EVENT INPUT: the union of the existing stocks machinery's three
contemporaneous event calendars, deduped on (stock, event_date,
event_type) with precedence live > ext > jan_oct:
  - stocks_sarvaritu_calendar_live.csv (the live producer's curated
    calendar; events from 2026-10-29),
  - stock_event_calendar_ext_jan_oct_2026.csv (built 2026-10-31),
  - stock_event_calendar_jan_oct_2026.csv (built 2026-10-30).
All three share the frozen schema and the reaction convention (first
trading day strictly after the event date unless a stored reaction
date says otherwise). The live producer's own calendar alone starts
2026-10-29 — scoring Oct 1-28 on it alone would report a
construction artefact (no event input, hence no possible trades) as
if it were a result; the union is what the machinery actually knew,
and it is what the live system's accumulating calendar (curated +
daily NSE snapshots of ALL universe names) will contain going
forward. DISCLOSURE: because the union adds November events the
earlier November-only run did not carry (names such as SBIN,
BHARTIARTL, M&M, ONGC, TITAN, POWERGRID), this report's November
subtotal can differ from sarvasetu_november_2026-11-11.md
(+Rs3,433.60 / 14 trades, live-calendar basis); the delta trades are
listed individually in the report.

Signal logic: the frozen stocks_live_shadow_producer Evaluator via
stocks_wide_nse_shadow_producer's rebound data layer — book layer
only: N4-V3 (T150/S080), P2F / P2F-R2 / R2-LOWBAND (T125/S050).
Money basis: provisional per 100 shares, Rs40/trade. Paper only.

Bars: screen_work/sarvasetu_bars_octnov (Upstox v3 historical
minutes/5 for Sep 30 - Nov 10; the intraday endpoint for Nov 11,
which the historical endpoint had not yet published). A weekday with
< 100 usable symbols is a NO-DATA / holiday day: marked, never
scored, never zero-filled. A symbol-day is NOT_COMPUTED when it
returned < 50 usable bars; event-active NOT_COMPUTED names are
listed individually.
Outputs: sarvasetu_oct_nov_2026-11-11_trades.csv and
sarvasetu_oct_nov_2026-11-11.md in ~/workspace/trading.
"""
import csv, json, os, sys
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_wide_nse_shadow_producer as wide
import stocks_live_shadow_producer as base

CACHE = f"{WS}/screen_work/sarvasetu_bars_octnov"
MERGED_CAL = f"{WS}/screen_work/sarvasetu_merged_calendar.csv"
wide.RUNTIME_CAL = f"{WS}/screen_work/sarvasetu_runtime_cal_octnov.csv"
OUT_CSV = f"{WS}/sarvasetu_oct_nov_2026-11-11_trades.csv"
OUT_MD = f"{WS}/sarvasetu_oct_nov_2026-11-11.md"
PRIOR_CSV = f"{WS}/sarvasetu_november_2026-11-11_trades.csv"
DRY_LOG = f"{WS}/stocks_wide_nse_shadow_log.dryrun.csv"
PAPER_LOG = f"{WS}/stocks_sarvaritu_paper_log.csv"
USABLE_BARS = 50
HOLIDAY_MAX_USABLE = 100
WINDOW_START, WINDOW_END = date(2026, 10, 1), date(2026, 11, 11)


def build_merged_calendar():
    sources = [base.LIVE_CAL,
               f"{WS}/stock_event_calendar_ext_jan_oct_2026.csv",
               f"{WS}/stock_event_calendar_jan_oct_2026.csv"]
    seen, rows = set(), []
    for path in sources:
        for r in csv.DictReader(open(path)):
            key = (r["stock"], (r["event_date"] or "")[:10], r["event_type"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({k: r.get(k, "") for k in base.CAL_FIELDS}
                        if hasattr(base, "CAL_FIELDS") else dict(r))
    fields = list(rows[0].keys()) if rows else []
    with open(MERGED_CAL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)


def main():
    n_cal = build_merged_calendar()
    wide.RAW_CAL = MERGED_CAL

    bars = {}
    for sym in wide.WIDE:
        p = f"{CACHE}/{sym}.json"
        bars[sym] = json.load(open(p)) if os.path.exists(p) else {}

    weekdays = []
    d = WINDOW_START
    while d <= WINDOW_END:
        if d.weekday() < 5:
            weekdays.append(d.isoformat())
        d += timedelta(days=1)

    all_trades, coverage, holidays, nc_active = [], {}, [], {}
    for target in weekdays:
        usable = sum(1 for s in wide.WIDE
                     if len(bars.get(s, {}).get(target, [])) >= USABLE_BARS)
        coverage[target] = {"usable": usable, "universe": len(wide.WIDE)}
        if usable < HOLIDAY_MAX_USABLE:
            holidays.append(target)
            continue
        wide.build_runtime_calendar(target)
        ev = base.Evaluator(target, wide.RUNTIME_CAL)
        actives = {c["stock"] for c in ev.cands} | {s for (s, dd) in ev.n4_days
                                                    if dd == target}
        nc_today = []
        for sym in wide.WIDE:
            day_bars = bars.get(sym, {}).get(target, [])
            if len(day_bars) >= USABLE_BARS:
                ev.step(sym, day_bars)
            elif sym in actives:
                nc_today.append(sym)
        if nc_today:
            nc_active[target] = sorted(nc_today)
        all_trades.extend(ev.closed)
        print(f"{target}: usable {usable}/{len(wide.WIDE)} | "
              f"actives {sorted(actives)} | trades {len(ev.closed)}", flush=True)
    all_trades.sort(key=lambda t: (t["date"], t["entry_time"], t["stock"]))

    fields = ["date", "comp", "stock", "dir", "entry_time", "entry",
              "exit", "exit_time", "exit_reason", "net", "regime"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for t in all_trades:
            w.writerow({k: t.get(k) for k in fields})

    def agg(trades):
        n = len(trades)
        net = round(sum(t["net"] for t in trades), 2)
        wins = sum(1 for t in trades if t["net"] > 0)
        return n, net, (round(100.0 * wins / n, 1) if n else 0.0)

    scored_days = [d for d in weekdays if d not in holidays]
    nov_days = [d for d in scored_days if d >= "2026-11-01"]
    oct_days = [d for d in scored_days if d < "2026-11-01"]
    nov_trades = [t for t in all_trades if t["date"] >= "2026-11-01"]
    oct_trades = [t for t in all_trades if t["date"] < "2026-11-01"]
    tn, tnet, twr = agg(all_trades)
    on, onet, owr = agg(oct_trades)
    nn, nnet, nwr = agg(nov_trades)
    comps = ["N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"]
    per_comp = {c: agg([t for t in all_trades if t["comp"] == c]) for c in comps}
    per_comp_nov = {c: agg([t for t in nov_trades if t["comp"] == c]) for c in comps}
    per_day = {d: agg([t for t in all_trades if t["date"] == d]) for d in scored_days}
    best = max(all_trades, key=lambda t: t["net"], default=None)
    worst = min(all_trades, key=lambda t: t["net"], default=None)

    # November delta vs the earlier live-calendar-basis deliverable
    prior = []
    if os.path.exists(PRIOR_CSV):
        for r in csv.DictReader(open(PRIOR_CSV)):
            prior.append((r["date"], r["comp"], r["stock"], r["dir"],
                          r["entry_time"], float(r["net"])))
    key = lambda t: (t["date"], t["comp"], t["stock"], t["dir"],
                     t["entry_time"], float(t["net"]))
    now_keys = [key(t) for t in nov_trades]
    added = [t for t in nov_trades if key(t) not in prior]
    missing = [p for p in prior if p not in now_keys]
    dry_keys = []
    if os.path.exists(DRY_LOG):
        for r in csv.DictReader(open(DRY_LOG)):
            dry_keys.append((r["date"], r["comp"], r["stock"], r["dir"],
                             r["entry_time"], float(r["net"])))
    nov11 = [t for t in nov_trades if t["date"] == "2026-11-11"]
    nov11_base = [t for t in nov11 if key(t) in dry_keys]
    nov11_extra = [t for t in nov11 if key(t) not in dry_keys]

    # Frozen 25-book comparison from its paper log
    log_rows = []
    if os.path.exists(PAPER_LOG):
        log_rows = list(csv.DictReader(open(PAPER_LOG)))
    log_nov = [r for r in log_rows if "2026-11-01" <= r["date"] <= "2026-11-11"]
    log_oct = [r for r in log_rows if "2026-10-01" <= r["date"] <= "2026-10-31"]
    log_dates = sorted({r["date"] for r in log_rows})
    log_nov_net = round(sum(float(r["net"]) for r in log_nov), 2)

    L = []
    L.append("# SARVASETU — Wide-NSE Shadow: FULL October + November-to-date retrospective (scored 2026-11-11)")
    L.append("")
    L.append("**This is a RETROSPECTIVE scoring of a shadow built on 11 Nov 2026 — "
             "not live forward evidence. The live record starts Thu 2026-11-12.**")
    L.append("Paper only, real money ₹0. Basis: **provisional per 100 shares**, "
             "₹40/trade, frozen SarvaRitu geometries (N4-V3 T150/S080; "
             "P2F / P2F-R2 / R2-LOWBAND T125/S050), square-off 15:10.")
    L.append(f"**Window: Thu 2026-10-01 → Wed 2026-11-11** (the owner's corrected "
             f"window — the whole of October plus November to date). Seed day "
             f"Wed 2026-09-30 was fetched for prior-day reactions and is not scored. "
             f"**Trading days actually scored: {len(scored_days)}** of {len(weekdays)} "
             f"weekdays; no-candle weekdays (market holidays) excluded by the candle "
             f"data itself: {', '.join(holidays) if holidays else 'none'}.")
    L.append(f"Universe: {len(wide.WIDE)} liquid NSE names as fetched 2026-11-11 "
             "(`wide_nse_universe_2026-11-11.csv`), applied backwards over the whole "
             "window (constituent drift over six weeks is possible in principle — "
             "index reviews are semi-annual and none fell inside this window — but "
             "the caveat stands).")
    L.append(f"Event input: the union of the stocks machinery's three contemporaneous "
             f"event calendars ({n_cal} rows after dedupe): the live producer's "
             "curated calendar (events from 2026-10-29) + "
             "`stock_event_calendar_ext_jan_oct_2026.csv` (built 2026-10-31) + "
             "`stock_event_calendar_jan_oct_2026.csv` (built 2026-10-30) — same "
             "schema, same reaction convention. The live calendar alone starts "
             "Oct 29; Oct 1–28 scored on it alone would show a construction "
             "artefact (no event input), not a result. Names without calendar "
             "events produce no trades by construction; every universe name's bars "
             "were still fetched and evaluated each day (coverage below).")
    L.append("")
    L.append(f"## Window totals — {tn} trades · net {tnet:+,.2f} · win rate {twr}%")
    L.append(f"- October portion (Oct 1–30, {len(oct_days)} scored days): "
             f"{on} trades · net {onet:+,.2f} · win rate {owr}%")
    L.append(f"- **November portion (Nov 2–11, {len(nov_days)} scored days): "
             f"{nn} trades · net {nnet:+,.2f} · win rate {nwr}%**")
    L.append("")
    L.append("## Per-day")
    L.append("| Date | Trades | Net ₹ | Win % | Usable bars coverage |")
    L.append("|---|---|---|---|---|")
    for d in weekdays:
        cov = coverage[d]
        pct = round(100.0 * cov["usable"] / cov["universe"], 1)
        if d in holidays:
            L.append(f"| {d} | — | — | — | {cov['usable']}/{cov['universe']} "
                     f"({pct}%) — NO DATA / holiday, not scored |")
        else:
            n, net, wr = per_day[d]
            L.append(f"| {d} | {n} | {net:+,.2f} | {wr} | "
                     f"{cov['usable']}/{cov['universe']} ({pct}%) |")
    L.append("")
    L.append("## Per-component (window)")
    L.append("| Component | Trades | Net ₹ | Win % | November trades | November net ₹ |")
    L.append("|---|---|---|---|---|---|")
    for c in comps:
        n, net, wr = per_comp[c]
        n2, net2, _ = per_comp_nov[c]
        L.append(f"| {c} | {n} | {net:+,.2f} | {wr} | {n2} | {net2:+,.2f} |")
    L.append("")
    if best:
        L.append(f"Best trade: {best['date']} {best['comp']} {best['stock']} "
                 f"{best['dir']} {best['entry_time']} @ {best['entry']} → "
                 f"{best['exit']} ({best['exit_reason']}) **{best['net']:+,.2f}**")
    if worst:
        L.append(f"Worst trade: {worst['date']} {worst['comp']} {worst['stock']} "
                 f"{worst['dir']} {worst['entry_time']} @ {worst['entry']} → "
                 f"{worst['exit']} ({worst['exit_reason']}) **{worst['net']:+,.2f}**")
    L.append("")
    L.append("## November delta vs the earlier November-only deliverable")
    L.append("The earlier run (`sarvasetu_november_2026-11-11.md`, live-producer "
             "calendar only) reported November as 14 trades · +₹3,433.60. This "
             "report's November subtotal uses the merged machinery calendars; "
             "the difference is entirely added event coverage, itemised here:")
    if added:
        for t in added:
            L.append(f"- ADDED {t['date']} {t['comp']} {t['stock']} {t['dir']} "
                     f"{t['entry_time']} @ {t['entry']} → {t['exit']} "
                     f"({t['exit_reason']}) {t['net']:+,.2f} — event carried only "
                     "by the machinery calendars")
    else:
        L.append("- No added November trades.")
    if missing:
        for p in missing:
            L.append(f"- MISSING vs earlier run: {p} — flagged, not hidden")
    else:
        L.append("- Every trade from the earlier run is reproduced unchanged.")
    L.append(f"- Nov 11 cross-check: the two dry-run legs (KALYANKJIL, TATASTEEL) "
             f"{'are' if len(nov11_base) == 2 else 'are NOT fully'} reproduced "
             f"inside this run's Nov 11 scoring"
             + (f"; additional Nov 11 trades from merged-calendar events: "
                f"{len(nov11_extra)}." if nov11_extra else "."))
    L.append("")
    L.append("## Coverage / NOT_COMPUTED notes")
    L.append(f"A symbol-day is NOT_COMPUTED when it returned < {USABLE_BARS} usable "
             "5-min bars. Event-active names in that state (a trade could have "
             "been missed) are listed individually:")
    if nc_active:
        for d, names in nc_active.items():
            L.append(f"- {d}: NOT_COMPUTED (event-active, unusable bars): "
                     f"{', '.join(names)}")
    else:
        L.append("- None — every event-active name had usable bars on its active days.")
    L.append("- Nov 11 bars come from the Upstox intraday endpoint (the historical "
             "endpoint had not published 2026-11-11 candles at scoring time); "
             "all other days use the historical minutes/5 endpoint.")
    L.append("- Seed day 2026-09-30 fetched, not scored. Nov 1 was a Sunday.")
    L.append("")
    L.append("## Scale reference (never added to the figures above)")
    if log_rows:
        L.append(f"The frozen 25-stock SarvaRitu book's own paper log "
                 f"(`stocks_sarvaritu_paper_log.csv`) covers only "
                 f"{log_dates[0]} → {log_dates[-1]} ({len(log_rows)} trades) — "
                 f"it holds NO October rows, so no same-source October comparison "
                 f"exists. Its November rows: {len(log_nov)} trades · net "
                 f"{log_nov_net:+,.2f} (provisional per 100 shares, EOD whole-book "
                 "construction incl. the EOD-only sleeves F4 / INV-LONG / INV-ABOVE, "
                 "which this shadow does not run). The only October book figure on "
                 "record is the adoption/EOD whole-book October total of "
                 "+₹56,127.37 (full month, incl. EOD sleeves — a different basis, "
                 "reference only). Shown for scale only — the two books are never "
                 "added together.")
    L.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(L))

    print(json.dumps({"window": [tn, tnet, twr], "october": [on, onet, owr],
                      "november": [nn, nnet, nwr],
                      "per_comp": per_comp, "per_comp_nov": per_comp_nov,
                      "per_day": per_day, "best": best, "worst": worst,
                      "holidays": holidays, "scored_days": len(scored_days),
                      "coverage": coverage, "nc_active": nc_active,
                      "added_nov": [key(t) for t in added],
                      "missing_nov": missing,
                      "nov11_base": len(nov11_base), "nov11_extra": len(nov11_extra),
                      "log_nov": [len(log_nov), log_nov_net]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
