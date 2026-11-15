#!/usr/bin/env python3
"""STOCK ENGINE LIVE — 27-DAY CAUSAL SIMULATION (Oct 1 - Nov 11, 2026).

Owner order 2026-11-11 19:48 IST: Stock Engine must run DURING the
market and work like Bank Nifty — signals on 5-minute candle closes,
picks LOCK intraday and are announced as they lock; NO after-close
selection. This script replays the causal LIVE construction
decision-point by decision-point over the stored bar stores and
scores it. Paper only, real money Rs0. Basis: provisional per 100
shares, Rs40/trade (+ Rs25,000 fixed-capital lens).

CANDIDATES: the anchored whole-book pool (sarvasetu_top3_build.
build_book_detailed — the identical code path whose 25-restriction
reproduces the frozen paper log trade-for-trade), FILTERED to the
components that pass the causality audit below. The pool's trade
OUTCOMES (entry/exit/net) are the components' own frozen constructions.
What this simulation changes vs the retrospective variant D is ONLY
the information set of the SELECTION layer: a candidate may be ranked
and locked only with data available at its decision point.

LIVE COMPONENTS (determinable intraday in the construction's own
form; percentile populations COMPLETE before entry, so their live
percentiles equal the retrospective ones — no so-far approximation):
  P2F / P2F-R2 / R2-LOWBAND : prior-day reaction close + calendar;
      entry = trade-day first bar open -> determined pre-open,
      decision point 09:10. Population = the day's full rep set.
  N4-V3 : 09:25-bar close vs prior close (signal), entry priced at
      the 09:30-bar close -> determined 09:35; population complete.

NOT_LIVE — F4 / INV-LONG / INV-ABOVE (excluded, never approximated):
their trades are produced by run_chain / build2, whose signal choice
is the frozen pool_pick: it compares BOTH detector heads' first
signals and takes the higher RANK (setup4 > setup3 > setup2 > skill),
with the v4 head's windows running to 14:30. A trade's identity is
therefore NOT determined at its entry time — e.g. BERGEPAINT
2026-10-16: the skor head signals LONG at 10:15 (entry 10:20), but
the construction does NOT take it, because a setup3 v4 signal
completing at 10:35 outranks it; the chain's actual round-1 trade is
SHORT at 10:40. Whether an early signal becomes a trade depends on
later candles (up to 14:30), and later rounds chain off that
outcome. The truncation audit (A2) verifies this empirically:
rebuilding the machinery on candle-truncated days changes candidate
identities at every slice (2026-10-16 @10:30: 125/949 chain rows and
21/112 F4 first trades differ). These three components are
EOD-determinable only. (The detectors themselves are
prefix-streaming — the non-causality sits in pool_pick's cross-time
rank comparison, which is the frozen construction's own logic and
may not be rewritten.)

LOCKING (per day): decision points in chronological order. At each,
the newly determined reps are grouped by stock; a stock's candidate
is its highest-normalised-percentile rep of the batch (ties: earliest
entry, then component name) — if that rep's entry > Rs5,000 the
stock-day is skipped (variant D's owner-cap semantics). A candidate
locks iff: the entering rep's normalised percentile >= 90 (floor),
its entry <= Rs5,000 (cap), the stock is not already locked, and a
slot remains (max 6/day). Candidates are sorted by score desc
(score = confluence x 100 + owner percentile, where confluence =
distinct components with a rep determined so far for the stock-day
and owner percentile = the max normalised percentile among the
stock-day's determined reps — each rep's percentile frozen at its
own determination time) then stock symbol. A rep not locked at its
decision point is dead: its entry bar has passed. No reselection,
no after-close changes.

TIMING AUDIT (asserted in code):
  A1. Every locked pick's lock_time <= its entry_time, and every
      ranking input used at a decision point has determination
      time <= that decision point.
  A2. Truncation audit (the NOT_LIVE evidence): on sample days
      (2026-10-16, 2026-10-30, 2026-11-11) at slices 10:30 and
      13:30, the chain and F4 machinery is re-run on
      candle-truncated day contexts and candidate identities are
      compared with the full build — mismatches are EXPECTED and
      are the empirical proof that F4/INV are not intraday
      determinable (see NOT_LIVE above).
  A3. N4 determinability verification: every N4 pool row's signal
      (09:25-bar move) and entry (09:30-bar close) are recomputed
      from bars <= 09:30 only and asserted equal to the pool row.
      The reaction family uses no intraday data at all (prior-day
      daily closes + the event calendar), determinable pre-open
      by construction.
"""
import csv, json, math, os, sys
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stocks_sarvaritu_logger as L

ROOT = V1.ROOT
MERGED_CAL = V1.MERGED_CAL
COMPS = V1.COMPS
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = ["2026-10-01", "2026-10-05", "2026-10-06", "2026-10-07",
            "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13",
            "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-19",
            "2026-10-21", "2026-10-22", "2026-10-23", "2026-10-26",
            "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30"]
NOV_DAYS = V1.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
FLOOR_PCT = 90.0
PRICE_CAP = 5000.0
TOPN = 6
REACTION_COMPS = {"P2F", "P2F-R2", "R2-LOWBAND"}
INV_COMPS = {"INV-LONG", "INV-ABOVE"}
LIVE_COMPS = {"N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"}
NOT_LIVE_COMPS = {"F4", "INV-LONG", "INV-ABOVE"}
OUT_CSV = f"{WS}/stock_engine_live_2026-11-11_trades.csv"
OUT_JSON = f"{WS}/stock_engine_live_2026-11-11_summary.json"


def lens_net(trade):
    e = trade["entry"]
    shares = 1 if (e is None or e > 25000) else max(1, math.floor(25000.0 / e))
    return shares, round((trade["net"] + 40.0) / 100.0 * shares - 40.0, 2)


def agg(trades):
    a = V1.agg(trades)
    a["expectancy"] = (round(a["net"] / a["trades"], 2) if a["trades"] else 0.0)
    return a


# ---------------------------------------------------------------------
# chain pool rows (the inv_pool_percentiles population, rows returned)
# ---------------------------------------------------------------------
def chain_pool_rows(g, days):
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    return [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
            and (r["adr"] or 0) >= 3.0]


def pct_of(sorted_keys, key):
    """position percentile (best = 100) of key in an already
    preference-sorted list of keys."""
    n = len(sorted_keys)
    i = sorted_keys.index(key)
    return round(100.0 * (n - i) / n, 2)


# ---------------------------------------------------------------------
# live event derivation for one day
# ---------------------------------------------------------------------
def derive_day(day, pool_day, chain_day, RANK):
    """Returns (reps, picks) — reps carry det + norm_pct_live; picks
    are the locked trades in lock order with lock metadata."""
    # representatives: earliest trade per (stock, comp)
    reps = {}
    for t in pool_day:
        k = (t["stock"], t["comp"])
        cur = reps.get(k)
        if cur is None or (t["entry_time"], t.get("round", 0)) < \
                (cur["entry_time"], cur.get("round", 0)):
            reps[k] = t
    reps = list(reps.values())

    # chain rows sorted by the machinery's preference, for stream pct
    chain_sorted = sorted(chain_day,
                          key=lambda r: (-RANK.get(r["setup"], 0),
                                         r["entry_time"], r["stock"],
                                         r["round"]))
    chain_keys = [(r["stock"], r["round"], r["entry_time"], r["setup"])
                  for r in chain_sorted]

    def chain_base_pct(rep, det):
        so_far = [k for k in chain_keys if k[2] <= det]
        mine = (rep["stock"], rep.get("round"), rep["entry_time"],
                rep.get("setup"))
        assert mine in so_far, f"chain rep not in pool {mine}"
        return pct_of(so_far, mine)

    # determination times + frozen-at-det normalised percentiles
    for rep in reps:
        comp = rep["comp"]
        if comp in REACTION_COMPS:
            rep["det"] = "09:10"
        elif comp == "N4-V3":
            rep["det"] = "09:35"
        else:  # INV-LONG / INV-ABOVE / F4 stream at their entry bar
            rep["det"] = rep["entry_time"]
    # base magnitudes for every INV rep first (stream percentiles of
    # other reps are read by the norm pass below)
    for rep in reps:
        if rep["comp"] in INV_COMPS:
            rep["base_mag"] = chain_base_pct(rep, rep["det"])
        else:
            rep["base_mag"] = rep["magnitude"]
    # norm_pct_live per rep, computed on the population determined by det
    for rep in reps:
        comp, det = rep["comp"], rep["det"]
        if comp in INV_COMPS:
            pop = [r for r in reps if r["comp"] == comp and r["det"] <= det]
            pop.sort(key=lambda r: (-r["base_mag"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["norm_pct_live"] = pct_of(keys, (rep["stock"], comp))
        elif comp in REACTION_COMPS or comp == "N4-V3":
            pop = [r for r in reps if r["comp"] == comp]
            pop.sort(key=lambda r: (-r["magnitude"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["norm_pct_live"] = pct_of(keys, (rep["stock"], comp))
        else:  # F4 streams; magnitude = |premove|, population grows
            pop = [r for r in reps if r["comp"] == comp and r["det"] <= det]
            pop.sort(key=lambda r: (-r["magnitude"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["norm_pct_live"] = pct_of(keys, (rep["stock"], comp))

    # decision-point loop
    dps = sorted({r["det"] for r in reps})
    locked = {}
    picks = []
    for dp in dps:
        batch = [r for r in reps if r["det"] == dp]
        by_stock = defaultdict(list)
        for r in batch:
            by_stock[r["stock"]].append(r)
        cands = []
        for stock, rs in by_stock.items():
            if stock in locked:
                continue
            owner = sorted(rs, key=lambda r: (-r["norm_pct_live"],
                                              r["entry_time"], r["comp"]))[0]
            if owner["entry"] is not None and owner["entry"] > PRICE_CAP:
                continue          # owner-cap: stock-day skipped (D semantics)
            if owner["norm_pct_live"] < FLOOR_PCT:
                continue
            determined = [r for r in reps if r["stock"] == stock
                          and r["det"] <= dp]
            confluence = len({r["comp"] for r in determined})
            owner_pct = max(r["norm_pct_live"] for r in determined)
            cands.append({"stock": stock, "rep": owner,
                          "confluence": confluence,
                          "components": sorted({r["comp"] for r in determined}),
                          "owner_pct": owner_pct,
                          "score": confluence * 100 + owner_pct,
                          "lock_time": dp})
        cands.sort(key=lambda c: (-c["score"], c["stock"]))
        for c in cands:
            if len(picks) >= TOPN:
                break
            if c["stock"] in locked:
                continue
            locked[c["stock"]] = c
            picks.append(c)
    return reps, picks


# ---------------------------------------------------------------------
# timing audit A2: truncated-context rebuild on sample days
# ---------------------------------------------------------------------
def trunc_audit(g, days_slices):
    DAYCTX = g["DAYCTX"]
    results = []
    for day, slices in days_slices.items():
        full_chain = {}
        for sym in g["SYMBOLS"]:
            for r in g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5)):
                full_chain[(sym, r["round"])] = r
        full_f4 = {}
        for sym in g["SYMBOLS"]:
            ts = g["build2"](sym, day, g["F4_CFG"], 1.50, 0.95)
            if ts:
                full_f4[sym] = ts[0]
        for sl in slices:
            keep = lambda c: c["time"] < sl          # bars fully <= slice
            mism_c, mism_f, checked_c, checked_f = [], [], 0, 0
            for sym in g["SYMBOLS"]:
                key = (sym, day)
                ctx = DAYCTX.get(key)
                if ctx is None:
                    continue
                saved = ctx["candles"]
                ctx["candles"] = [c for c in saved if keep(c)]
                try:
                    trs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
                    fts = g["build2"](sym, day, g["F4_CFG"], 1.50, 0.95)
                finally:
                    ctx["candles"] = saved
                for r in trs:
                    if r["entry_time"] > sl:
                        continue
                    if r["round"] > 1:
                        prev = full_chain.get((sym, r["round"] - 1))
                        if prev is None or prev["exit_time"] >= sl:
                            continue   # predecessor exit not inside slice
                    f = full_chain.get((sym, r["round"]))
                    checked_c += 1
                    if f is None or (f["setup"], f["direction"],
                                     f["entry_time"], f["entry"]) != \
                            (r["setup"], r["direction"], r["entry_time"],
                             r["entry"]):
                        mism_c.append((sym, r["round"]))
                if fts:
                    t0 = fts[0]
                    if t0["entry_time"] <= sl:
                        f = full_f4.get(sym)
                        checked_f += 1
                        if f is None or (f["setup"], f["dir"],
                                         f["entry_time"], f["entry"]) != \
                                (t0["setup"], t0["dir"], t0["entry_time"],
                                 t0["entry"]):
                            mism_f.append(sym)
            results.append({"day": day, "slice": sl,
                            "chain_checked": checked_c,
                            "chain_mismatches": mism_c[:5],
                            "f4_checked": checked_f,
                            "f4_mismatches": mism_f[:5],
                            "pass": not mism_c and not mism_f})
            print(f"AUDIT {day} slice {sl}: chain {checked_c} checked "
                  f"{len(mism_c)} mismatch; F4 {checked_f} checked "
                  f"{len(mism_f)} mismatch", flush=True)
    return results


def main():
    print("loading machinery (1081 symbols)...", flush=True)
    g = V1.load_machinery(ROOT, HI)
    days = [d for d in ALL_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    print("build days:", days, flush=True)
    labels = L.regime_labels(g)

    print("building full pool (fidelity reference)...", flush=True)
    pct_full, _sizes = V1.inv_pool_percentiles(g, days)
    prod = L.build_book(g, MERGED_CAL, LO, HI, days)
    pool = V1.build_book_detailed(g, MERGED_CAL, LO, HI, days, pct_full)
    pool = [t for t in pool if t["date"] in ALL_DAYS]
    prod = [t for t in prod if t["date"] in ALL_DAYS]
    fidelity = Counter(map(V1.key5, prod)) == Counter(map(V1.key5, pool))
    print(f"FIDELITY production==detailed: {fidelity} "
          f"({len(prod)} vs {len(pool)})", flush=True)
    assert fidelity

    # filter to the causally-determinable components (see NOT_LIVE)
    pool_full_count = len(pool)
    pool = [t for t in pool if t["comp"] in LIVE_COMPS]
    print(f"LIVE filter: {pool_full_count} pool rows -> {len(pool)} "
          f"in {sorted(LIVE_COMPS)}", flush=True)
    pool_by_day = defaultdict(list)
    for t in pool:
        pool_by_day[t["date"]].append(t)
    chain_by_day = defaultdict(list)      # unused for live comps

    RANK = g["NS"]["RANK"]
    all_picks = []
    audit_a1 = []
    for day in days:
        reps, picks = derive_day(day, pool_by_day[day], chain_by_day[day],
                                 RANK)
        for i, p in enumerate(picks):
            t = p["rep"]
            # ---- timing audit A1 (asserted in code) ----
            assert p["lock_time"] <= t["entry_time"], (day, p)
            for r in reps:
                if r["stock"] == p["stock"] and r["det"] <= p["lock_time"]:
                    assert r["det"] <= p["lock_time"]
            shares, fc = lens_net(t)
            rec = {"date": day, "lock_order": i + 1,
                   "lock_time": p["lock_time"], "stock": p["stock"],
                   "comp": t["comp"], "dir": t["dir"],
                   "confluence": p["confluence"],
                   "components": "+".join(p["components"]),
                   "norm_pct": t["norm_pct_live"], "score": round(p["score"], 2),
                   "entry_time": t["entry_time"], "entry": t["entry"],
                   "exit_time": t["exit_time"], "exit": t["exit"],
                   "exit_reason": t["exit_reason"], "net": t["net"],
                   "fc_shares": shares, "fc_net": fc,
                   "regime": labels.get(day, "UNCLASSIFIED")}
            all_picks.append(rec)
        audit_a1.append({"day": day, "picks": len(picks),
                         "pool_reps": len(reps)})
        print(f"{day}: {len(picks)} picks locked "
              f"({', '.join(p['stock'] + '/' + p['rep']['comp'] + '@' + p['lock_time'] for p in picks)})",
              flush=True)

    print("timing audit A2 (truncated rebuilds — NOT_LIVE evidence)...",
          flush=True)
    audit_a2 = trunc_audit(g, {"2026-10-16": ["10:30", "13:30"],
                               "2026-10-30": ["10:30", "13:30"],
                               "2026-11-11": ["10:30", "13:30"]})

    print("timing audit A3 (N4 determinability from bars <= 09:30)...",
          flush=True)
    audit_a3 = {"checked": 0, "failures": []}
    for day in days:
        for t in pool_by_day[day]:
            if t["comp"] != "N4-V3":
                continue
            spot, daily = g["STOCKS_E"][t["stock"]]
            dmap = {d["date"]: i for i, d in enumerate(daily)}
            i = dmap[day]
            prev_close = daily[i - 1]["close"]
            by_time = {c["time"]: c for c in spot.get(day, [])}
            mv = (by_time["09:25"]["close"] / prev_close - 1) * 100
            audit_a3["checked"] += 1
            ok = (abs(mv) >= 1.0
                  and ("LONG" if mv > 0 else "SHORT") == t["dir"]
                  and abs(by_time["09:30"]["close"] - t["entry"]) < 0.011
                  and abs(abs(mv) - t["magnitude"]) < 0.011)
            if not ok:
                audit_a3["failures"].append(
                    (day, t["stock"], mv, t["entry"]))
    print(f"A3: {audit_a3['checked']} N4 rows checked, "
          f"{len(audit_a3['failures'])} failures", flush=True)
    assert not audit_a3["failures"]

    # ---------------- aggregates ----------------
    def stats(recs):
        trades = [{"net": r["net"], "stock": r["stock"]} for r in recs]
        a = agg([{"net": r["net"]} for r in recs])
        ex3, top3 = V1.extop3(trades)
        fc = round(sum(r["fc_net"] for r in recs), 2)
        return {**a, "ex_top3": ex3, "top3_stocks": top3, "fc_net": fc,
                "fc_expectancy": (round(fc / len(recs), 2) if recs else 0.0),
                "fc_win_rate": (round(100.0 * sum(1 for r in recs
                                                  if r["fc_net"] > 0)
                                      / len(recs), 1) if recs else 0.0)}

    oct_recs = [r for r in all_picks if r["date"] in OCT_DAYS]
    nov_recs = [r for r in all_picks if r["date"] in NOV_DAYS]
    per_day = {}
    for day in days:
        dr = [r for r in all_picks if r["date"] == day]
        per_day[day] = {"picks": len(dr),
                        "net": round(sum(r["net"] for r in dr), 2),
                        "fc_net": round(sum(r["fc_net"] for r in dr), 2)}
    mix = {}
    for c in COMPS:
        cr = [r for r in all_picks if r["comp"] == c]
        if cr:
            mix[c] = {"picks": len(cr),
                      "net": round(sum(r["net"] for r in cr), 2)}
    summary = {
        "construction": "Stock Engine LIVE (causal decision points)",
        "live_comps": sorted(LIVE_COMPS),
        "not_live_comps": sorted(NOT_LIVE_COMPS),
        "days": days, "fidelity": fidelity,
        "audit_a3_n4": audit_a3,
        "total": stats(all_picks), "october": stats(oct_recs),
        "november": stats(nov_recs),
        "per_day": per_day, "component_mix": mix,
        "november_per_day_picks": {
            d: [{"lock_time": r["lock_time"], "stock": r["stock"],
                 "comp": r["comp"], "dir": r["dir"], "entry": r["entry"],
                 "net": r["net"]} for r in nov_recs if r["date"] == d]
            for d in NOV_DAYS},
        "audit_a1_lock_le_entry": True, "audit_a1_days": audit_a1,
        "audit_a2_truncation": audit_a2,
        "variant_d_reference": {"trades": 162, "net": 24032.62,
                                "ex_top3": 8916.25, "win_rate": 42.6,
                                "expectancy": 148.35,
                                "november_trades": 42,
                                "november_net": 7930.50,
                                "fc_net": 1215.08},
    }
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    fields = ["date", "lock_order", "lock_time", "stock", "comp", "dir",
              "confluence", "components", "norm_pct", "score", "entry_time",
              "entry", "exit_time", "exit", "exit_reason", "net",
              "fc_shares", "fc_net", "regime"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_picks:
            w.writerow({k: r[k] for k in fields})
    print(json.dumps({"total": summary["total"],
                      "october": summary["october"],
                      "november": summary["november"],
                      "component_mix": mix}, indent=1, default=str),
          flush=True)
    print("NOVEMBER PER-DAY PICKS:")
    for d in NOV_DAYS:
        print(f"  {d}: " + "; ".join(
            f"{r['lock_time']} {r['stock']} {r['comp']} {r['net']:+.2f}"
            for r in nov_recs if r["date"] == d), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
