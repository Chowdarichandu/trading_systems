#!/usr/bin/env python3
"""SARVASETU — RETROSPECTIVE scoring of the WIDE-NSE SHADOW over
November 2026 month-to-date (owner request 2026-11-11 17:11 IST).
Scores the four frozen intraday-causal components (N4-V3, P2F,
P2F-R2, R2-LOWBAND) across the full wide universe for every November
trading day: 2026-11-02, 03, 04, 05, 06, 09, 11 (2026-11-10 was the
Diwali-Balipratipada holiday; 2026-11-01 was a Sunday).

This is a RETROSPECTIVE scoring of a shadow built on 2026-11-11 — it
is NOT live forward evidence. The live record starts Thu 2026-11-12.
Universe caveat: the universe is the list as fetched 2026-11-11,
applied backwards over Nov 2-11 (constituent drift over 7 trading
days is negligible, but the note stands). Event-calendar coverage for
Nov 2-11 is the curated 25-name SarvaRitu calendar (the only event
source retrievable for those dates — see the producer's adaptation
A4); names without calendar events produce no trades BY CONSTRUCTION
(not NOT_COMPUTED). A symbol-day is NOT_COMPUTED only when its 5-min
bars are unusable (< 50 bars), so a trade could have been missed;
event-active NOT_COMPUTED names are listed individually.

Signal logic: the frozen stocks_live_shadow_producer Evaluator, via
stocks_wide_nse_shadow_producer's rebound data layer. The Nov 11 leg
is taken from the dry-run log (stocks_wide_nse_shadow_log.dryrun.csv)
and cross-checked against a retrospective re-score of the same day.
Money basis: provisional per 100 shares, Rs40/trade. Paper only.

Bars: Upstox v3 historical 5-min candles for 2026-11-02..2026-11-11,
fetched once per symbol into /tmp/sarvasetu_bars/ (resumable). Any
HTTP 429 aborts the fetch phase (hard stop).
Outputs: sarvasetu_november_2026-11-11_trades.csv and
sarvasetu_november_2026-11-11.md in ~/workspace/trading.
"""
import csv, json, os, sys, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_wide_nse_shadow_producer as wide
import stocks_live_shadow_producer as base

IST = ZoneInfo("Asia/Kolkata")
BARS_DIR = "/home/hatch/workspace/trading/screen_work/sarvasetu_bars"
DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
        "2026-11-06", "2026-11-09", "2026-11-11"]
OUT_CSV = f"{WS}/sarvasetu_november_2026-11-11_trades.csv"
OUT_MD = f"{WS}/sarvasetu_november_2026-11-11.md"
DRY_LOG = f"{WS}/stocks_wide_nse_shadow_log.dryrun.csv"
FROM_D, TO_D = "2026-11-02", "2026-11-11"
USABLE_BARS = 50

# keep the producer's own runtime-calendar file untouched
wide.RUNTIME_CAL = "/home/hatch/workspace/trading/screen_work/sarvasetu_runtime_cal.csv"


class RateLimited(Exception):
    pass


def fetch_range_bars(sym):
    path = f"{BARS_DIR}/{sym}.json"
    if os.path.exists(path):
        return sym, json.load(open(path))
    enc = urllib.parse.quote(wide.KEYS[sym], safe="")
    req = urllib.request.Request(
        base.API + f"/v3/historical-candle/{enc}/minutes/5/{TO_D}/{FROM_D}",
        headers={"Authorization": f"Bearer {base.load_token()}",
                 "Accept": "application/json", "User-Agent": base.UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"429 on {sym}")
        payload = {}
    rows = (payload.get("data") or {}).get("candles") or []
    by_day = {}
    for c in rows:
        ts = str(c[0])[:19].replace("T", " ")
        bar = {"timestamp": ts, "time": ts[11:16], "open": float(c[1]),
               "high": float(c[2]), "low": float(c[3]), "close": float(c[4])}
        by_day.setdefault(ts[:10], []).append(bar)
    for d in by_day:
        by_day[d].sort(key=lambda x: x["timestamp"])
    json.dump(by_day, open(path, "w"))
    return sym, by_day


def main():
    os.makedirs(BARS_DIR, exist_ok=True)
    print(f"fetching range bars for {len(wide.WIDE)} symbols...", flush=True)
    bars = {}
    try:
        with ThreadPoolExecutor(max_workers=8) as ex:
            for sym, by_day in ex.map(fetch_range_bars, wide.WIDE):
                bars[sym] = by_day
    except RateLimited as e:
        print(f"ABORTED rate-limited during bar fetch: {e}")
        return 1
    print("bars fetched for all symbols", flush=True)

    all_trades = []
    coverage = {}
    nc_active = {}
    for target in DAYS:
        wide.build_runtime_calendar(target)
        ev = base.Evaluator(target, wide.RUNTIME_CAL)
        actives = {c["stock"] for c in ev.cands} | {s for (s, d) in ev.n4_days
                                                    if d == target}
        usable = 0
        nc_today = []
        for sym in wide.WIDE:
            day_bars = bars.get(sym, {}).get(target, [])
            if len(day_bars) >= USABLE_BARS:
                usable += 1
                ev.step(sym, day_bars)
            elif sym in actives:
                nc_today.append(sym)
        coverage[target] = {"usable": usable, "universe": len(wide.WIDE)}
        if nc_today:
            nc_active[target] = sorted(nc_today)
        all_trades.extend(ev.closed)
        print(f"{target}: usable {usable}/{len(wide.WIDE)} | "
              f"actives {sorted(actives)} | trades {len(ev.closed)}", flush=True)

    # Nov 11 leg: official = dry-run log; cross-check vs re-score
    dry_trades = []
    if os.path.exists(DRY_LOG):
        for r in csv.DictReader(open(DRY_LOG)):
            dry_trades.append({"date": r["date"], "comp": r["comp"],
                               "stock": r["stock"], "dir": r["dir"],
                               "entry_time": r["entry_time"],
                               "entry": float(r["entry"]), "exit": float(r["exit"]),
                               "exit_time": r["exit_time"],
                               "exit_reason": r["exit_reason"],
                               "net": float(r["net"]), "regime": r["regime"]})
    retro_11 = [t for t in all_trades if t["date"] == "2026-11-11"]
    key = lambda t: (t["comp"], t["stock"], t["dir"], t["entry_time"],
                     float(t["entry"]), float(t["exit"]), t["exit_reason"],
                     float(t["net"]))
    crosscheck_ok = sorted(map(key, dry_trades)) == sorted(map(key, retro_11))
    final_trades = [t for t in all_trades if t["date"] != "2026-11-11"] + dry_trades
    final_trades.sort(key=lambda t: (t["date"], t["entry_time"], t["stock"]))

    fields = ["date", "comp", "stock", "dir", "entry_time", "entry",
              "exit", "exit_time", "exit_reason", "net", "regime"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for t in final_trades:
            w.writerow({k: t.get(k) for k in fields})

    # ---- aggregates
    def agg(trades):
        n = len(trades)
        net = round(sum(t["net"] for t in trades), 2)
        wins = sum(1 for t in trades if t["net"] > 0)
        return n, net, (round(100.0 * wins / n, 1) if n else 0.0)

    tn, tnet, twr = agg(final_trades)
    per_day = {d: agg([t for t in final_trades if t["date"] == d]) for d in DAYS}
    comps = ["N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"]
    per_comp = {c: agg([t for t in final_trades if t["comp"] == c]) for c in comps}
    best = max(final_trades, key=lambda t: t["net"], default=None)
    worst = min(final_trades, key=lambda t: t["net"], default=None)

    lines = []
    lines.append("# SARVASETU — Wide-NSE Shadow: November 2026 retrospective (scored 2026-11-11)")
    lines.append("")
    lines.append("**This is a RETROSPECTIVE scoring of a shadow built on 11 Nov 2026 — "
                 "not live forward evidence. The live record starts Thu 2026-11-12.**")
    lines.append("Paper only, real money ₹0. Basis: **provisional per 100 shares**, "
                 "₹40/trade, frozen SarvaRitu geometries (N4-V3 T150/S080; "
                 "P2F / P2F-R2 / R2-LOWBAND T125/S050), square-off 15:10.")
    lines.append(f"Universe: {len(wide.WIDE)} liquid NSE names as fetched 2026-11-11 "
                 "(`wide_nse_universe_2026-11-11.csv`), applied backwards over "
                 "Nov 2–11 (constituent drift over 7 trading days is negligible; "
                 "the caveat stands).")
    lines.append("Event-calendar coverage for Nov 2–11 is the curated 25-name SarvaRitu "
                 "calendar — the only event source retrievable for those dates "
                 "(NSE event calendar is forward-only; BSE API / Moneycontrol blocked "
                 "from this network). Names without calendar events produce no trades "
                 "by construction; every universe name's bars were still fetched and "
                 "evaluated each day (coverage below).")
    lines.append("")
    lines.append(f"## Totals — {tn} trades · net {tnet:+,.2f} · win rate {twr}%")
    lines.append("")
    lines.append("## Per-day")
    lines.append("| Date | Trades | Net ₹ | Win % | Usable bars coverage |")
    lines.append("|---|---|---|---|---|")
    for d in DAYS:
        n, net, wr = per_day[d]
        cov = coverage[d]
        lines.append(f"| {d} | {n} | {net:+,.2f} | {wr} | "
                     f"{cov['usable']}/{cov['universe']} "
                     f"({round(100.0 * cov['usable'] / cov['universe'], 1)}%) |")
    lines.append("")
    lines.append("## Per-component")
    lines.append("| Component | Trades | Net ₹ | Win % |")
    lines.append("|---|---|---|---|")
    for c in comps:
        n, net, wr = per_comp[c]
        lines.append(f"| {c} | {n} | {net:+,.2f} | {wr} |")
    lines.append("")
    if best:
        lines.append(f"Best trade: {best['date']} {best['comp']} {best['stock']} "
                     f"{best['dir']} {best['entry_time']} @ {best['entry']} → "
                     f"{best['exit']} ({best['exit_reason']}) **{best['net']:+,.2f}**")
    if worst:
        lines.append(f"Worst trade: {worst['date']} {worst['comp']} {worst['stock']} "
                     f"{worst['dir']} {worst['entry_time']} @ {worst['entry']} → "
                     f"{worst['exit']} ({worst['exit_reason']}) **{worst['net']:+,.2f}**")
    lines.append("")
    lines.append("## Coverage / NOT_COMPUTED notes")
    lines.append(f"A symbol-day is NOT_COMPUTED when it returned < {USABLE_BARS} usable "
                 "5-min bars (no trade can be scored for it that day). Non-event names "
                 "in that state miss nothing by construction; event-active names in "
                 "that state are listed here individually:")
    if nc_active:
        for d, names in nc_active.items():
            lines.append(f"- {d}: NOT_COMPUTED (event-active, unusable bars): "
                         f"{', '.join(names)}")
    else:
        lines.append("- None — every event-active name had usable bars on its active days.")
    if coverage["2026-11-11"]["usable"] == 0:
        lines.append("- Nov 11 leg taken from the dry-run log (evaluated on the "
                     "intraday endpoint's completed bars). A retrospective re-score "
                     "of Nov 11 was NOT POSSIBLE at scoring time: the v3 historical "
                     "endpoint had not yet published 2026-11-11 candles (the same "
                     "publication lag that blocked the index shadow scorer today), "
                     "so Nov 11 coverage above reads 0 by that route — the dry-run "
                     "leg stands as the day's record.")
    else:
        lines.append(f"- Nov 11 leg taken from the dry-run log; retrospective re-score "
                     f"cross-check: {'MATCH' if crosscheck_ok else 'MISMATCH - see trades CSV (dry-run leg retained)'}.")
    lines.append("- Nov 10: market holiday (Diwali-Balipratipada) — no run. "
                 "Nov 1: Sunday — no run.")
    lines.append("")
    lines.append("## Scale reference (never added to the figures above)")
    lines.append("The frozen 25-stock SarvaRitu book's own November book net over the "
                 "same days (Nov 2–11) is **+₹8,391.28** over its trades (provisional "
                 "per 100 shares, EOD construction incl. the EOD-only sleeves F4 / "
                 "INV-LONG / INV-ABOVE, which this shadow does not run). Shown for "
                 "scale only — the two books are never added together.")
    lines.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines))

    print(json.dumps({"trades": tn, "net": tnet, "win_rate": twr,
                      "per_day": {d: per_day[d] for d in DAYS},
                      "per_comp": {c: per_comp[c] for c in comps},
                      "best": best, "worst": worst,
                      "coverage": coverage, "nc_active": nc_active,
                      "crosscheck_ok": crosscheck_ok}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
