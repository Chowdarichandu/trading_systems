#!/usr/bin/env python3
"""STOCKS TUNING PROGRAMME T-S2 (owner order 2026-11-12 16:23 IST) —
N4 THRESHOLD RECONCILIATION.

The discrepancy (open since 2026-11-03): the frozen November book's
N4-V3, its frozen spec (stocks_sarvaritu_forward_spec.md §4) and the
live producer ALL trigger on |move by 09:30| >= 1.0% (09:25-bar close
vs prior close), while the adopted Variant C December axis uses
0.8% (recorded in november_rsi_stocks_log.md, 2026-11-03 entries:
NATIONALUM -0.869% "crosses the 0.8% threshold used elsewhere
(adopted Variant C axis), but frozen November N4-V3 law is 1.0%").

This script scores the Stock Book's N4-V3 component under BOTH
thresholds, from the book's own machinery (stocks_sarvaritu_logger
.load_machinery -> the v2_build n4_raw construction, copied verbatim
with the threshold as a parameter; n4_book filters + the v2 law's
EXCL_V2 N4 deletions applied exactly as build_book does), on:
  - Jan-Oct 2026 (data/full_hist, stock_event_calendar_jan_oct_2026)
  - Jan-Oct 2025 guard year (same machinery/calendar family)
  - Nov 2-11 2026 forward (data/sarvaritu_fwd, live calendar, epoch
    2026-10-26; the fwd root's candles end 2026-11-11 — Nov 12 is
    scored by tonight's logger run; Nov 12's only N4 signal,
    HINDCOPPER LONG at +3.88% by 09:30, qualifies under BOTH
    thresholds identically, so it cannot change the comparison).

VALIDATION ANCHORS (abort if any fails): at thr=1.0 the runs must
reproduce, trade-for-trade on (date, stock, dir, entry_time, net):
  - the post-C24 frozen book dumps' N4-V3 rows (2026: 35 rows;
    2025 Jan-Oct subset of the 2025 dump);
  - the November paper log's N4-V3 rows (5 rows, Nov 2-11).
Superset property asserted: every thr=1.0 trade appears in the
thr=0.8 set with an identical net (lowering the threshold only ADDS
the [0.8%, 1.0%) band; it cannot alter an existing trade — entries
and exits are per-trade).

Basis: per 100 shares, Rs40/trade (inside the machinery's nets).
Paper only, real money Rs0.
Outputs: tuning_stocks_2026-11-12_ts2_summary.json,
tuning_stocks_2026-11-12_ts2_trades_<window>_<thr>.csv.
"""
import csv, json, sys, time
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L

CAL26 = f"{WS}/stock_event_calendar_jan_oct_2026.csv"
CAL25 = f"{WS}/stock_event_calendar_2025.csv"
SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
               "block_deal", "sector_policy", "pricing",
               "corporate_action"}


def n4_raw_thr(g, cal_path, lo, hi, thr):
    """stocks_engine_v2_build.n4_raw verbatim, threshold parameterised."""
    from datetime import date, timedelta
    SYMBOLS = g["SYMBOLS"]
    STOCKS_E = g["STOCKS_E"]
    NIFTY_DAILY_E = g["NIFTY_DAILY_E"]
    replay = g["replay"]
    COST = g["COST"]
    combined = {s: set() for s in SYMBOLS}
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in combined:
                continue
            et = r["event_type"]
            if et != "results" and et not in SINGLE_NEWS:
                continue
            if not r["event_date"]:
                continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) \
                if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) \
                else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                combined[sym].add(ds)
    all_days = sorted(d["date"] for d in NIFTY_DAILY_E
                      if lo <= d["date"] <= hi)
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        dmap = {d["date"]: i for i, d in enumerate(daily)}
        for day in all_days:
            if day not in combined[sym]:
                continue
            if day not in dmap or dmap[day] == 0:
                continue
            raw = spot.get(day, [])
            if not raw:
                continue
            prev_close = daily[dmap[day] - 1]["close"]
            if not prev_close:
                continue
            by_time = {c["time"]: c for c in raw}
            idx_of = {c["timestamp"]: i for i, c in enumerate(raw)}
            b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
            if b0925 is None or b0930 is None:
                continue
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= thr:
                direction = "LONG" if move_pct > 0 else "SHORT"
                ei = idx_of[b0930["timestamp"]]
                entry = b0930["close"]
                r = replay(raw, ei, entry, direction, 1.50, 0.80)
                if r is None:
                    continue
                er, ep, et = r
                sign = 1 if direction == "LONG" else -1
                out.append({"symbol": sym, "date": day,
                            "direction": direction,
                            "entry_time": "09:35",
                            "entry": round(entry, 2),
                            "exit_reason": er,
                            "exit_price": round(ep, 2),
                            "exit_time": et,
                            "move_pct": round(move_pct, 3),
                            "net": round(sign * (ep - entry) * 100
                                         - COST, 2)})
    return out


def book_slice(g, raw):
    """n4_book + the v2 law's EXCL_V2 deletions (build_book's N4 path);
    raw fields (entry/exit/move) joined back on the logger's own key."""
    rawmap = {(t["date"], t["symbol"], t["direction"], t["net"]): t
              for t in raw}
    rows = []
    for t in g["n4_book"](raw):
        if ("N4-V3", t["stock"], t["dir"]) in L.EXCL_V2:
            continue
        r = rawmap[(t["date"], t["stock"], t["dir"], t["net"])]
        rows.append({"date": t["date"], "stock": t["stock"],
                     "dir": t["dir"], "entry_time": t["entry_time"],
                     "entry": r["entry"], "exit_time": r["exit_time"],
                     "exit_price": r["exit_price"],
                     "exit_reason": r["exit_reason"],
                     "move_pct": r["move_pct"], "net": t["net"]})
    return rows


def stats(rows):
    if not rows:
        return {"trades": 0, "net": 0.0, "wins": 0, "win_rate": 0.0,
                "expectancy": 0.0, "ex_top3": 0.0, "top3_stocks": [],
                "long": {"trades": 0, "net": 0.0},
                "short": {"trades": 0, "net": 0.0}, "months": {}}
    net = round(sum(t["net"] for t in rows), 2)
    wins = sum(1 for t in rows if t["net"] > 0)
    by_stock = defaultdict(float)
    for t in rows:
        by_stock[t["stock"]] += t["net"]
    top3 = sorted(by_stock.items(), key=lambda kv: -kv[1])[:3]
    months = defaultdict(float)
    for t in rows:
        months[t["date"][:7]] += t["net"]
    lg = [t for t in rows if t["dir"] == "LONG"]
    sh = [t for t in rows if t["dir"] == "SHORT"]
    return {"trades": len(rows), "net": net, "wins": wins,
            "win_rate": round(100.0 * wins / len(rows), 1),
            "expectancy": round(net / len(rows), 2),
            "ex_top3": round(net - sum(v for _k, v in top3), 2),
            "top3_stocks": [(k, round(v, 2)) for k, v in top3],
            "long": {"trades": len(lg),
                     "net": round(sum(t["net"] for t in lg), 2)},
            "short": {"trades": len(sh),
                      "net": round(sum(t["net"] for t in sh), 2)},
            "months": {k: round(v, 2) for k, v in sorted(months.items())}}


def keyset(rows):
    return sorted((t["date"], t["stock"], t["dir"], t["entry_time"],
                   round(float(t["net"]), 2)) for t in rows)


def write_trades(name, rows):
    fields = ["date", "stock", "dir", "entry_time", "entry",
              "exit_time", "exit", "exit_reason", "move_pct", "net"]
    with open(f"{WS}/tuning_stocks_2026-11-12_ts2_trades_{name}.csv",
              "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for t in sorted(rows, key=lambda x: (x["date"], x["stock"])):
            w.writerow({"date": t["date"], "stock": t["stock"],
                        "dir": t["dir"], "entry_time": t["entry_time"],
                        "entry": t["entry"], "exit_time": t["exit_time"],
                        "exit": t["exit_price"],
                        "exit_reason": t["exit_reason"],
                        "move_pct": t["move_pct"], "net": t["net"]})


def main():
    t0 = time.time()
    out = {"started": time.strftime("%Y-%m-%d %H:%M UTC")}
    print("loading book machinery (full_hist)...", flush=True)
    g_full = L.load_machinery(L.FULLHIST, "2026-10-28")
    print("loading book machinery (fwd)...", flush=True)
    g_fwd = L.load_machinery(L.FWD, "2026-12-31")

    runs = {}
    # ---- Jan-Oct 2026, both thresholds
    for thr, tag in ((1.0, "thr100"), (0.8, "thr080")):
        raw = n4_raw_thr(g_full, CAL26, "2026-01-01", "2026-10-28", thr)
        runs[f"2026_{tag}"] = book_slice(g_full, raw)
    # ---- Jan-Oct 2025 guard, both thresholds
    for thr, tag in ((1.0, "thr100"), (0.8, "thr080")):
        raw = n4_raw_thr(g_full, CAL25, "2025-01-01", "2025-10-31", thr)
        runs[f"2025_{tag}"] = book_slice(g_full, raw)
    # ---- November forward (Nov 2-11 scored from fwd root)
    for thr, tag in ((1.0, "thr100"), (0.8, "thr080")):
        raw = n4_raw_thr(g_fwd, L.LIVE_CAL, "2026-10-26", "2026-11-11",
                         thr)
        runs[f"nov_{tag}"] = [t for t in book_slice(g_fwd, raw)
                              if t["date"] >= "2026-11-02"]

    # ---- validation anchors at thr=1.0
    dump26 = [r for r in csv.DictReader(
        open(f"{WS}/stocks_engine_v2_c24_book2026_trades.csv"))
        if r["comp"] == "N4-V3"]
    want26 = sorted((r["date"], r["stock"], r["dir"], r["entry_time"],
                     round(float(r["net"]), 2)) for r in dump26)
    got26 = keyset(runs["2026_thr100"])
    ok26 = got26 == want26
    print(f"anchor 2026 thr1.0 vs C24 dump: {ok26} "
          f"({len(got26)} vs {len(want26)} rows)", flush=True)
    assert ok26, "2026 anchor FAILED — abort"

    dump25 = [r for r in csv.DictReader(
        open(f"{WS}/stocks_engine_v2_c24_book2025_trades.csv"))
        if r["comp"] == "N4-V3" and r["date"] <= "2025-10-31"]
    want25 = sorted((r["date"], r["stock"], r["dir"], r["entry_time"],
                     round(float(r["net"]), 2)) for r in dump25)
    got25 = keyset(runs["2025_thr100"])
    ok25 = got25 == want25
    print(f"anchor 2025 thr1.0 vs C24 dump (Jan-Oct): {ok25} "
          f"({len(got25)} vs {len(want25)} rows)", flush=True)
    assert ok25, "2025 anchor FAILED — abort"

    plog = [r for r in csv.DictReader(open(L.LOGCSV))
            if r["comp"] == "N4-V3" and "2026-11-02" <= r["date"]
            <= "2026-11-11"]
    wantn = sorted((r["date"], r["stock"], r["dir"], r["entry_time"],
                    round(float(r["net"]), 2)) for r in plog)
    gotn = keyset(runs["nov_thr100"])
    okn = gotn == wantn
    print(f"anchor Nov thr1.0 vs paper log: {okn} "
          f"({len(gotn)} vs {len(wantn)} rows)", flush=True)
    assert okn, "November anchor FAILED — abort"
    out["anchors"] = {"2026_thr100_vs_c24_dump": ok26,
                      "2025_thr100_vs_c24_dump_janoct": ok25,
                      "nov_thr100_vs_paper_log": okn}

    # ---- superset property + the marginal [0.8, 1.0) band
    band_report = {}
    for wname in ("2026", "2025", "nov"):
        hi_rows = {(t["date"], t["stock"], t["dir"]): t
                   for t in runs[f"{wname}_thr100"]}
        lo_rows = {(t["date"], t["stock"], t["dir"]): t
                   for t in runs[f"{wname}_thr080"]}
        assert set(hi_rows) <= set(lo_rows), f"superset violated {wname}"
        for k in hi_rows:
            assert hi_rows[k]["net"] == lo_rows[k]["net"], \
                f"shared trade net changed {wname} {k}"
        band = [lo_rows[k] for k in sorted(set(lo_rows) - set(hi_rows))]
        band_report[wname] = {"band_trades": stats(band),
                              "band_rows": [
                                  {"date": t["date"], "stock": t["stock"],
                                   "dir": t["dir"],
                                   "move_pct": t["move_pct"],
                                   "net": t["net"]} for t in band]}
        print(f"{wname}: thr1.0 {len(hi_rows)} tr; thr0.8 "
              f"{len(lo_rows)} tr; band {len(band)} tr net "
              f"{stats(band)['net']:+.2f}", flush=True)
    out["marginal_band"] = band_report

    for wname in ("2026", "2025", "nov"):
        for tag in ("thr100", "thr080"):
            out[f"{wname}_{tag}"] = stats(runs[f"{wname}_{tag}"])
            write_trades(f"{wname}_{tag}", runs[f"{wname}_{tag}"])
    for wname in ("2026", "2025", "nov"):
        a, b = out[f"{wname}_thr100"], out[f"{wname}_thr080"]
        print(f"{wname}: 1.0% -> {a['trades']} tr {a['net']:+.2f} "
              f"(WR {a['win_rate']}, ex3 {a['ex_top3']:+.2f}) | "
              f"0.8% -> {b['trades']} tr {b['net']:+.2f} "
              f"(WR {b['win_rate']}, ex3 {b['ex_top3']:+.2f})",
              flush=True)

    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/tuning_stocks_2026-11-12_ts2_summary.json",
              "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"T-S2 DONE in {out['elapsed_secs']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
