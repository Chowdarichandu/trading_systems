#!/usr/bin/env python3
"""SARVASETU TOP-3 v2 — FIXED RANKING + WIDER PROOF WINDOW (Oct 1 -
Nov 11, 27 trading days) + pick-count variants A-F. Owner delegation
2026-11-11 18:59 IST ("make it more profitable, it's up to you") +
addendum 19:00 IST (variants D/E/F). RETROSPECTIVE paper scoring —
NOT live evidence. Paper only, real money Rs0. Basis: provisional per
100 shares, Rs40/trade.

WHAT CHANGED vs v1 (sarvasetu_top3_build.py, same machinery reused by
import): v1's ranking mixed scales — INV magnitudes were pool
percentiles (0-100) while other components carried genuine % moves
(0.5-10), so INV owned all 21 picks. THE FIX (Step 2): every
component's trigger magnitude is normalised to a WITHIN-DAY,
WITHIN-COMPONENT percentile (0-100) across that day's stock-day
representatives of that component (position percentile, best = 100 —
the same convention v1's INV pool percentile used). Conviction =
confluence (distinct components flagging the stock-day) PRIMARY,
owning component's normalised magnitude SECONDARY. A stock-day is
owned by its highest-normalised-magnitude component; the trade scored
is that component's earliest trade on the stock that day.

VARIANTS (same pools, same ranking, Oct 1 - Nov 11, 27 days):
  A  top 3/day, no floor
  B  top 3/day + conviction floor (owner normalised pct >= 90)
  C  B + price-risk cap (pick entry price <= Rs5,000)
  D  top 6/day, floor + cap
  E  SPLIT BASKET: morning basket (N4-V3, P2F, P2F-R2, R2-LOWBAND, F4)
     top 3 + pool basket (INV-LONG, INV-ABOVE) top 3, each basket
     ranked/floored/capped independently (confluence counted WITHIN
     the basket's component set); a stock in both baskets counts once
     (morning owns it; pool basket walks to its next-ranked name);
     up to 6 trades/day
  F  top 9/day, floor + cap

Judging order (pre-registered): ex-top-3 net FIRST, then per-trade
expectancy, then win rate. Winner gets the fixed-capital lens
(Rs25,000/trade notional) and the LIVE SHADOW SPEC.

Outputs: sarvasetu_top3_v2_2026-11-11_summary.json,
sarvasetu_top3_v2_2026-11-11_trades.csv (winner's picks),
sarvasetu_top3_october_2026-11-11_pool.csv (October pool),
sarvasetu_top3_v2_2026-11-11_pool.csv (combined 27-day pool).
No frozen book, log, producer, or index file is touched.
"""
import csv, json, math, os, sys
from collections import Counter, defaultdict
from datetime import date as _date, timedelta as _td

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stocks_sarvaritu_logger as L

ROOT = V1.ROOT
BARS = V1.BARS
MERGED_CAL = V1.MERGED_CAL
SYMS = V1.SYMS
COMPS = V1.COMPS
WATCH25 = V1.WATCH25
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = ["2026-10-01", "2026-10-05", "2026-10-06", "2026-10-07",
            "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13",
            "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-19",
            "2026-10-21", "2026-10-22", "2026-10-23", "2026-10-26",
            "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30"]
NOV_DAYS = V1.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
V1_POOL_CSV = f"{WS}/sarvasetu_top3_november_2026-11-11_pool.csv"
OUT_POOL_OCT = f"{WS}/sarvasetu_top3_october_2026-11-11_pool.csv"
OUT_POOL_ALL = f"{WS}/sarvasetu_top3_v2_2026-11-11_pool.csv"
OUT_CSV = f"{WS}/sarvasetu_top3_v2_2026-11-11_trades.csv"
OUT_JSON = f"{WS}/sarvasetu_top3_v2_2026-11-11_summary.json"
FLOOR_PCT = 90.0
PRICE_CAP = 5000.0
MORNING_COMPS = {"N4-V3", "P2F", "P2F-R2", "R2-LOWBAND", "F4"}
POOL_COMPS = {"INV-LONG", "INV-ABOVE"}


def agg(trades):
    a = V1.agg(trades)
    a["expectancy"] = (round(a["net"] / a["trades"], 2) if a["trades"] else 0.0)
    return a


def variant_stats(picks):
    """picks: list of pick dicts with .trade, .date, .stock, .owner."""
    trades = [p["trade"] for p in picks]
    a = agg(trades)
    ex3, top3 = V1.extop3(trades)
    by_day = defaultdict(float)
    cnt_day = defaultdict(int)
    for p in picks:
        by_day[p["date"]] += p["trade"]["net"]
        cnt_day[p["date"]] += 1
    day_nets = {d: round(v, 2) for d, v in sorted(by_day.items())}
    best_day = max(day_nets.items(), key=lambda kv: kv[1]) if day_nets else None
    worst_day = min(day_nets.items(), key=lambda kv: kv[1]) if day_nets else None
    nov = [p for p in picks if p["date"] in NOV_DAYS]
    mix = {}
    for c in COMPS:
        cp = [p for p in picks if p["owner"] == c]
        if cp:
            mix[c] = {"picks": len(cp),
                      "net": round(sum(p["trade"]["net"] for p in cp), 2)}
    return {"trades": a["trades"], "net": a["net"], "win_rate": a["win_rate"],
            "expectancy": a["expectancy"], "ex_top3": ex3,
            "top3_stocks": top3, "day_nets": day_nets,
            "best_day": best_day, "worst_day": worst_day,
            "days_with_picks": len(day_nets),
            "zero_pick_days": [d for d in ALL_DAYS if d not in day_nets],
            "november": agg([p["trade"] for p in nov]),
            "november_picks": len(nov),
            "component_mix": mix}


def main():
    V1.build_root()
    print("loading machinery (1081 symbols)...", flush=True)
    g = V1.load_machinery(ROOT, HI)
    days = [d for d in ALL_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    missing_days = [d for d in ALL_DAYS if d not in days]
    print("build days (in DAYCTX):", days, flush=True)
    print("days NOT in DAYCTX:", missing_days, flush=True)
    labels = L.regime_labels(g)
    print("regime labels:", {d: labels.get(d) for d in ALL_DAYS}, flush=True)

    print("building INV pool percentiles (27 days)...", flush=True)
    pct, pool_sizes = V1.inv_pool_percentiles(g, days)
    print("INV chain pool sizes per day:", pool_sizes, flush=True)

    print("production build (fidelity reference)...", flush=True)
    prod = L.build_book(g, MERGED_CAL, LO, HI, days)
    print("detailed build...", flush=True)
    mine = V1.build_book_detailed(g, MERGED_CAL, LO, HI, days, pct)
    pool = [t for t in mine if t["date"] in ALL_DAYS]
    prod27 = [t for t in prod if t["date"] in ALL_DAYS]
    fidelity = Counter(map(V1.key5, prod27)) == Counter(map(V1.key5, pool))
    print(f"FIDELITY production==detailed on 27 days: {fidelity} "
          f"({len(prod27)} vs {len(pool)} rows)", flush=True)
    out_rows = [t for t in mine if t["date"] not in ALL_DAYS]
    print("detailed rows outside the 27 days:",
          [(t["date"], t["comp"], t["stock"], t["net"]) for t in out_rows],
          flush=True)

    # ---- ANCHOR: November subset == today's v1 pool CSV, exactly ----
    v1rows = list(csv.DictReader(open(V1_POOL_CSV)))
    v1key = Counter((r["comp"], r["date"], r["stock"], r["dir"],
                     r["entry_time"], round(float(r["net"]), 2),
                     round(float(r["magnitude"]), 2)) for r in v1rows)
    nov_pool = [t for t in pool if t["date"] in NOV_DAYS]
    mykey = Counter((t["comp"], t["date"], t["stock"], t["dir"],
                     t["entry_time"], round(float(t["net"]), 2),
                     round(float(t["magnitude"]), 2)) for t in nov_pool)
    anchor_pool = (v1key == mykey)
    print(f"ANCHOR November pool == v1 pool CSV: {anchor_pool} "
          f"({sum(v1key.values())} vs {sum(mykey.values())} rows)", flush=True)
    if not anchor_pool:
        print("  v1-only sample:", list((v1key - mykey).elements())[:5],
              flush=True)
        print("  v2-only sample:", list((mykey - v1key).elements())[:5],
              flush=True)
    # 25-restriction anchor vs the frozen paper log (November)
    log_rows = list(csv.DictReader(open(L.LOGCSV)))
    log_nov = [r for r in log_rows if r["date"] in NOV_DAYS]
    mine25 = [t for t in nov_pool if t["stock"] in WATCH25]
    lk = Counter((r["comp"], r["date"], r["stock"], r["dir"], r["entry_time"],
                  round(float(r["net"]), 2)) for r in log_nov)
    mk = Counter(map(V1.key5, mine25))
    anchor25 = (lk == mk)
    print(f"ANCHOR 25-restriction vs paper log: {anchor25} "
          f"({len(log_nov)} vs {len(mine25)})", flush=True)

    # ---- pool outputs ----
    pfields = ["date", "comp", "stock", "dir", "entry_time", "entry",
               "exit", "exit_time", "exit_reason", "net", "regime",
               "magnitude", "mag_kind"]
    oct_pool = [t for t in pool if t["date"] in OCT_DAYS]
    for path, rows_ in ((OUT_POOL_OCT, oct_pool), (OUT_POOL_ALL, pool)):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=pfields)
            w.writeheader()
            for t in rows_:
                w.writerow({k: t.get(k) for k in pfields})
    print(f"pools written: October {len(oct_pool)} rows, combined "
          f"{len(pool)} rows", flush=True)

    # ================= STEP 2: FIXED RANKING =================
    # stock-day representatives: earliest trade per (date, stock, comp)
    reps = {}      # (date, stock, comp) -> trade
    for t in pool:
        k = (t["date"], t["stock"], t["comp"])
        cur = reps.get(k)
        if cur is None or (t["entry_time"], t.get("round", 0)) < \
                (cur["entry_time"], cur.get("round", 0)):
            reps[k] = t
    # within-day, within-component percentile of the rep magnitudes
    by_dc = defaultdict(list)          # (date, comp) -> [(date, stock, comp)]
    for (d, s, c) in reps:
        by_dc[(d, c)].append((d, s, c))
    norm_pct = {}                      # (date, stock, comp) -> percentile
    for (d, c), keys in by_dc.items():
        keys.sort(key=lambda k: (-reps[k]["magnitude"],
                                 reps[k]["entry_time"], k[1]))
        n = len(keys)
        for i, k in enumerate(keys):
            norm_pct[k] = round(100.0 * (n - i) / n, 2)
    # stock-day records
    by_sd = defaultdict(set)           # (date, stock) -> comps flagging
    for (d, s, c) in reps:
        by_sd[(d, s)].add(c)
    sd = {}                            # (date, stock) -> record
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
    ranked = {}                        # day -> [records] in rank order
    for d in days:
        recs = [r for (dd, _s), r in sd.items() if dd == d]
        recs.sort(key=lambda r: (-r["score"], r["stock"]))
        for i, r in enumerate(recs):
            r["rank"] = i + 1
        ranked[d] = recs

    def entry_of(r):
        e = r["trade"]["entry"]
        return e if e is not None else float("inf")

    def take(recs, n, floor=False, cap=False, skip_stocks=frozenset()):
        out = []
        for r in recs:
            if r["stock"] in skip_stocks:
                continue
            if floor and r["owner_pct"] < FLOOR_PCT:
                continue
            if cap and entry_of(r) > PRICE_CAP:
                continue
            out.append(r)
            if len(out) == n:
                break
        return out

    picks = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
    for d in days:
        recs = ranked[d]
        picks["A"].extend(take(recs, 3))
        picks["B"].extend(take(recs, 3, floor=True))
        picks["C"].extend(take(recs, 3, floor=True, cap=True))
        picks["D"].extend(take(recs, 6, floor=True, cap=True))
        picks["F"].extend(take(recs, 9, floor=True, cap=True))
        # ---- E: split basket ----
        def basket(recs_all, comp_set):
            brecs = []
            for (dd, s), r in sd.items():
                if dd != d:
                    continue
                bc = [c for c in r["components"] if c in comp_set]
                if not bc:
                    continue
                bowner = sorted(bc, key=lambda c: (-r["comp_pct"][c],
                                                   reps[(d, s, c)]["entry_time"],
                                                   c))[0]
                brecs.append({"date": d, "stock": s,
                              "confluence": len(bc), "components": bc,
                              "comp_pct": r["comp_pct"], "owner": bowner,
                              "owner_pct": r["comp_pct"][bowner],
                              "trade": reps[(d, s, bowner)],
                              "score": len(bc) * 100 + r["comp_pct"][bowner],
                              "full": r})
            brecs.sort(key=lambda r: (-r["score"], r["stock"]))
            for i, r in enumerate(brecs):
                r["rank"] = i + 1
            return brecs
        morn = basket(recs, MORNING_COMPS)
        poolb = basket(recs, POOL_COMPS)
        mpicks = take(morn, 3, floor=True, cap=True)
        for r in mpicks:
            r["basket"] = "MORNING"
        ppicks = take(poolb, 3, floor=True, cap=True,
                      skip_stocks={r["stock"] for r in mpicks})
        for r in ppicks:
            r["basket"] = "POOL"
        picks["E"].extend(mpicks + ppicks)

    stats = {v: variant_stats(picks[v]) for v in "ABCDEF"}
    for v in "ABCDEF":
        s = stats[v]
        print(f"VARIANT {v}: trades={s['trades']} net={s['net']} "
              f"WR={s['win_rate']} exp={s['expectancy']} "
              f"exT3={s['ex_top3']} Nov={s['november']} mix={s['component_mix']}",
              flush=True)

    # ---- winner by the pre-registered judging order ----
    order = sorted("ABCDEF", key=lambda v: (-stats[v]["ex_top3"],
                                            -stats[v]["expectancy"],
                                            -stats[v]["win_rate"]))
    winner = order[0]
    not_proven = all(stats[v]["ex_top3"] <= 0 for v in "ABCDEF")
    print(f"JUDGING ORDER: {order} -> WINNER {winner}; "
          f"all-ex-top3<=0 (not proven): {not_proven}", flush=True)

    # ---- STEP 4: fixed-capital lens on the winner ----
    fc_rows = []
    for p in picks[winner]:
        t = p["trade"]
        e = t["entry"]
        shares = 1 if (e is None or e > 25000) else \
            max(1, math.floor(25000.0 / e))
        gain_per_share = (t["net"] + 40.0) / 100.0   # exact: net is built
        # at unrounded exit levels; (net+40)/100 is the signed per-share
        # gain in the trade's favour on the per-100-shares basis.
        fc_net = round(gain_per_share * shares - 40.0, 2)
        fc_rows.append({**p, "fc_shares": shares, "fc_net": fc_net,
                        "fc_one_share": bool(e is not None and e > 25000)})
    fc = {"trades": len(fc_rows),
          "net": round(sum(r["fc_net"] for r in fc_rows), 2),
          "win_rate": (round(100.0 * sum(1 for r in fc_rows
                                         if r["fc_net"] > 0) / len(fc_rows), 1)
                       if fc_rows else 0.0),
          "expectancy": (round(sum(r["fc_net"] for r in fc_rows) /
                               len(fc_rows), 2) if fc_rows else 0.0),
          "one_share_trades": sum(1 for r in fc_rows if r["fc_one_share"]),
          "november_net": round(sum(r["fc_net"] for r in fc_rows
                                    if r["date"] in NOV_DAYS), 2),
          "total_shares": sum(r["fc_shares"] for r in fc_rows)}
    fc_by_key = {(r["date"], r["stock"], r["owner"]): r for r in fc_rows}
    print("FIXED-CAPITAL LENS (winner):", json.dumps(fc), flush=True)

    # ---- coverage / NOT_COMPUTED (27 days) ----
    store = {}
    coverage = {}
    for sym in SYMS:
        store[sym] = json.load(open(f"{BARS}/{sym}.json"))
    for d in ALL_DAYS:
        coverage[d] = {"usable": sum(1 for sym in SYMS
                                     if len(store[sym].get(d, [])) >= 50),
                       "universe": len(SYMS)}
    SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
                   "block_deal", "sector_policy", "pricing",
                   "corporate_action"}
    active = set()
    for c in g["reaction_candidates"](MERGED_CAL, LO, HI):
        _spot, daily = g["STOCKS_E"][c["symbol"]]
        for lag in (1, 2):
            if c["ri"] + lag < len(daily):
                dd = daily[c["ri"] + lag]["date"]
                if dd in ALL_DAYS:
                    active.add((c["symbol"], dd))
    for r in csv.DictReader(open(MERGED_CAL)):
        sym = r["stock"]
        if sym not in SYMS:
            continue
        et = r["event_type"]
        if et != "results" and et not in SINGLE_NEWS:
            continue
        if not r["event_date"]:
            continue
        ev = _date.fromisoformat(r["event_date"][:10])
        react = _date.fromisoformat(r["reaction_date"][:10]) \
            if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + _td(days=7)) else ev
        ds = eff.isoformat()
        if ds in ALL_DAYS:
            active.add((sym, ds))
    nc_active = [{"symbol": s, "date": d, "bars": len(store[s].get(d, []))}
                 for s, d in sorted(active) if len(store[s].get(d, [])) < 50]
    print("coverage:", json.dumps(coverage), flush=True)
    print("event-active pairs:", len(active), "NOT_COMPUTED:", nc_active,
          flush=True)

    # ---- winner trades CSV ----
    wfields = ["date", "rank", "basket", "stock", "comp", "dir",
               "confluence", "components", "native_magnitude", "mag_kind",
               "norm_pct", "score", "entry_time", "entry", "exit_time",
               "exit", "exit_reason", "net", "regime", "fc_shares",
               "fc_net"]
    win_picks = sorted(picks[winner], key=lambda p: (p["date"],
                                                     p.get("rank", 0),
                                                     p["stock"]))
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=wfields)
        w.writeheader()
        for p in win_picks:
            t = p["trade"]
            fr = fc_by_key.get((p["date"], p["stock"], p["owner"]), {})
            w.writerow({"date": p["date"], "rank": p.get("rank"),
                        "basket": p.get("basket", ""),
                        "stock": p["stock"], "comp": p["owner"],
                        "dir": t["dir"], "confluence": p["confluence"],
                        "components": "+".join(p["components"]),
                        "native_magnitude": t["magnitude"],
                        "mag_kind": t["mag_kind"],
                        "norm_pct": p["owner_pct"],
                        "score": round(p["score"], 2),
                        "entry_time": t["entry_time"], "entry": t["entry"],
                        "exit_time": t["exit_time"], "exit": t["exit"],
                        "exit_reason": t["exit_reason"], "net": t["net"],
                        "regime": t["regime"],
                        "fc_shares": fr.get("fc_shares"),
                        "fc_net": fr.get("fc_net")})

    summary = {
        "universe": len(SYMS), "days": days, "missing_days": missing_days,
        "labels": {d: labels.get(d) for d in ALL_DAYS},
        "fidelity": fidelity, "anchor_november_pool_eq_v1": anchor_pool,
        "anchor_25_log": anchor25,
        "out_of_window_rows": [{k: t[k] for k in ("date", "comp", "stock",
                                                  "dir", "net")}
                               for t in out_rows],
        "pool_total": agg(pool), "pool_october": agg(oct_pool),
        "pool_november": agg(nov_pool),
        "pool_ex_top3": V1.extop3(pool)[0],
        "pool_per_comp": {c: agg([t for t in pool if t["comp"] == c])
                          for c in COMPS},
        "pool_per_comp_october": {c: agg([t for t in oct_pool
                                          if t["comp"] == c]) for c in COMPS},
        "pool_per_day": {d: agg([t for t in pool if t["date"] == d])
                         for d in ALL_DAYS},
        "inv_pool_sizes": pool_sizes,
        "variants": stats, "judging_order": order, "winner": winner,
        "not_proven": not_proven, "fixed_capital_lens": fc,
        "winner_picks": [
            {"date": p["date"], "rank": p.get("rank"),
             "basket": p.get("basket", ""), "stock": p["stock"],
             "owner": p["owner"], "confluence": p["confluence"],
             "components": p["components"], "comp_pct": p["comp_pct"],
             "owner_pct": p["owner_pct"], "score": round(p["score"], 2),
             "dir": p["trade"]["dir"], "entry_time": p["trade"]["entry_time"],
             "entry": p["trade"]["entry"], "exit": p["trade"]["exit"],
             "exit_time": p["trade"]["exit_time"],
             "exit_reason": p["trade"]["exit_reason"],
             "net": p["trade"]["net"], "mag_kind": p["trade"]["mag_kind"],
             "native_magnitude": p["trade"]["magnitude"],
             "regime": p["trade"]["regime"],
             "fc_shares": fc_by_key.get((p["date"], p["stock"],
                                         p["owner"]), {}).get("fc_shares"),
             "fc_net": fc_by_key.get((p["date"], p["stock"],
                                      p["owner"]), {}).get("fc_net")}
            for p in win_picks],
        "all_variant_picks": {
            v: [{"date": p["date"], "rank": p.get("rank"),
                 "basket": p.get("basket", ""), "stock": p["stock"],
                 "owner": p["owner"], "confluence": p["confluence"],
                 "components": p["components"],
                 "owner_pct": p["owner_pct"], "entry": p["trade"]["entry"],
                 "net": p["trade"]["net"]} for p in
                sorted(picks[v], key=lambda p: (p["date"],
                                                p.get("rank", 0),
                                                p["stock"]))]
            for v in "ABCDEF"},
        "ranked_top10": {d: [{"rank": r["rank"], "stock": r["stock"],
                              "owner": r["owner"],
                              "confluence": r["confluence"],
                              "components": r["components"],
                              "owner_pct": r["owner_pct"],
                              "entry": r["trade"]["entry"],
                              "net": r["trade"]["net"]}
                             for r in ranked[d][:10]] for d in days},
        "coverage": coverage, "nc_active": nc_active,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print("WINNER PICKS:")
    for p in win_picks:
        print(f"  {p['date']} {p.get('basket','')} #{p.get('rank')} "
              f"{p['stock']} {p['owner']} conf={p['confluence']} "
              f"pct={p['owner_pct']} entry={p['trade']['entry']} "
              f"net={p['trade']['net']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
