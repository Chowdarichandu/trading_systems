#!/usr/bin/env python3
"""CAUSAL VARIANTS GATE — F4-C / INV-LONG-C / INV-ABOVE-C for Stock
Engine (owner order 2026-11-12 06:16 IST: convert the three EOD-only
sleeves so they fall under the same live causality discipline as the
four live components; Stock Engine to run 7 live strategies).

THE CONVERSION (mechanical, minimal): identical detectors, signals,
regime gates, chain rounds, entry/exit geometry as the frozen
constructions. The ONLY change is round selection: where the frozen
pool_pick compares both detector heads' first signals by RANK across
the whole day (a later higher-rank signal displaces an earlier one),
pool_pick_causal LOCKS the round at the moment the first signal for
that round completes; the construction's own priority key applies
only among signals completed by that moment (same-candle ties);
once locked, no later signal can displace it. Entry per the frozen
convention (next candle open); rounds chain from the exit exactly
as frozen.

GATE (this script = legs 1+2; leg 3 in stock_engine_causal3_hist.py):
  LEG 1 — CAUSALITY PROOF: truncation test on 11 sample days
  (incl. 2026-10-16, 2026-11-11), slices 10:30/12:00/13:30/15:00.
  Causal chain + causal F4 trades up to each cut must be IDENTICAL
  at every cut. Any mismatch = FAIL.
  LEG 2 — WIDE-WIDTH SCORING: 1,081 names, Oct 1 - Nov 11 2026
  (27 trading days). Per-variant books + the combined 7-live Stock
  Engine (stock_engine_live_sim.derive_day selection, unchanged)
  vs the 4-live baseline (39 tr / +Rs8,724.39 / ex-top-3
  -Rs3,256.65). PASS requires combined ex-top-3 to IMPROVE on
  -Rs3,256.65. Baseline reproduction is asserted first.

Paper only, real money Rs0. Basis: provisional per 100 shares,
Rs40/trade; Rs25,000 lens on the combined engine.
Outputs: stock_engine_causal3_gate_summary.json,
stock_engine_causal3_2026-11-12_trades.csv (combined picks),
stock_engine_causal3_variant_rows.csv (causal variant book rows).
"""
import csv, json, sys, time
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stock_engine_live_sim as SIM
import stocks_sarvaritu_logger as L

ROOT = V1.ROOT
MERGED_CAL = V1.MERGED_CAL
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = SIM.OCT_DAYS
NOV_DAYS = SIM.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
CELL = ("PLAIN", 1.25, 0.5)
BASELINE = {"trades": 39, "net": 8724.39, "ex_top3": -3256.65}
AUDIT_DAYS = ["2026-10-01", "2026-10-06", "2026-10-09", "2026-10-13",
              "2026-10-16", "2026-10-19", "2026-10-22", "2026-10-27",
              "2026-10-30", "2026-11-06", "2026-11-11"]
SLICES = ["10:30", "12:00", "13:30", "15:00"]


# =====================================================================
# THE CAUSAL CONVERSION
# =====================================================================
def pool_pick_causal(NS, ctx, v4, skor):
    """Frozen pool_pick's inputs, causal selection: lock at the
    earliest-completing signal; frozen priority key among signals
    completed by that moment (same candle index)."""
    candles = ctx["candles"]
    RANK = NS["RANK"]
    pool = [st for st in (v4, skor)
            if st[0] is not None and st[3] + 1 < len(candles)]
    if not pool:
        return None
    first_idx = min(st[3] for st in pool)
    completed = [st for st in pool if st[3] == first_idx]

    def key(p):
        setup, dirc, sig, idx = p
        entry_px = candles[idx + 1]["open"]
        return (-RANK.get(setup, 0), -(0.01 * entry_px * 100 - 40.0),
                sig["time"])
    return sorted(completed, key=key)[0]


def run_chain_causal(g, sym, day, cell=CELL):
    """stocks_engine_2025_validation.run_chain verbatim except the
    pick: pool_pick_causal instead of NS['pool_pick']."""
    NS = g["NS"]
    ctx = g["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    trades, start = [], 0
    while True:
        chosen = pool_pick_causal(NS, ctx, NS["v4_head"](ctx, start),
                                  NS["skor_head"](ctx, start))
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        _, tp, sp = cell
        er, ep, et, exit_idx, gross = g["replay_plain"](
            candles, entry_idx, sign, entry, tp, sp)
        trades.append({"date": day, "stock": sym, "direction": direction,
                       "setup": setup, "round": len(trades) + 1,
                       "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit_price": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - 40.0, 2),
                       "event_status": ctx["event_status"]})
        start = exit_idx
    return trades


def build2_causal(g, sym, day, cfg, TP, SP, pm_override=None):
    """validation build2 verbatim except the pick is causal."""
    NS = g["NS"]
    ctx = g["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    if cfg.get("regime") == "below50" and not g["below50"](day):
        return []
    candles = ctx["candles"]
    T_MEAS = g["T_MEAS"]
    pm = pm_override if pm_override is not None else g["premove"](candles, T_MEAS)
    if pm is None or abs(pm) < 0.005:
        return []
    hi = cfg.get("band_hi")
    if hi is not None and abs(pm) >= hi / 100.0:
        return []
    move_dir = 1 if pm > 0 else -1
    want = move_dir
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= T_MEAS),
                 None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = pool_pick_causal(NS, ctx, NS["v4_head"](ctx, start),
                                  NS["skor_head"](ctx, start))
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = g["replay_plain"](candles, ei, sign, entry,
                                                  TP, SP)
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - 40.0, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3),
                       "meas_time": T_MEAS})
        start = xi
    return trades


def collect2_causal(g, days, cfg, TP, SP):
    out = []
    for sym in g["SYMBOLS"]:
        for day in days:
            out.extend(build2_causal(g, sym, day, cfg, TP, SP))
    return out


# =====================================================================
# LEG 1 — truncation audit on the CAUSAL machinery
# =====================================================================
def leg1_truncation(g):
    results = []
    total_mism = 0
    for day in AUDIT_DAYS:
        full_chain = {}
        for sym in g["SYMBOLS"]:
            for r in run_chain_causal(g, sym, day):
                full_chain[(sym, r["round"])] = r
        full_f4 = {}
        for sym in g["SYMBOLS"]:
            ts = build2_causal(g, sym, day, g["F4_CFG"], 1.50, 0.95)
            if ts:
                full_f4[sym] = ts[0]
        for sl in SLICES:
            mism_c, mism_f, checked_c, checked_f = [], [], 0, 0
            for sym in g["SYMBOLS"]:
                ctx = g["DAYCTX"].get((sym, day))
                if ctx is None:
                    continue
                saved = ctx["candles"]
                ctx["candles"] = [c for c in saved if c["time"] < sl]
                try:
                    trs = run_chain_causal(g, sym, day)
                    fts = build2_causal(g, sym, day, g["F4_CFG"], 1.50, 0.95)
                finally:
                    ctx["candles"] = saved
                for r in trs:
                    if r["entry_time"] > sl:
                        continue
                    if r["round"] > 1:
                        prev = full_chain.get((sym, r["round"] - 1))
                        if prev is None or prev["exit_time"] >= sl:
                            continue
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
            total_mism += len(mism_c) + len(mism_f)
            results.append({"day": day, "slice": sl,
                            "chain_checked": checked_c,
                            "chain_mismatches": mism_c[:5],
                            "f4_checked": checked_f,
                            "f4_mismatches": mism_f[:5],
                            "pass": not mism_c and not mism_f})
            print(f"LEG1 {day} slice {sl}: chain {checked_c} checked "
                  f"{len(mism_c)} mismatch; F4 {checked_f} checked "
                  f"{len(mism_f)} mismatch", flush=True)
    return results, total_mism == 0


# =====================================================================
# LEG 2 — builders
# =====================================================================
def build_live4_detailed(g, cal_path, lo, hi, days):
    """V1.build_base_detailed restricted to the four live comps
    (reaction + N4 blocks verbatim; no chain machinery involved)."""
    out = []

    def norm(comp, t, stock, dir_, entry, exit_price, exit_reason,
             exit_time, magnitude, mag_kind):
        return {"comp": comp, "date": t["date"], "stock": stock,
                "dir": dir_, "entry_time": t["entry_time"],
                "entry": (round(float(entry), 2) if entry is not None else None),
                "exit": (round(float(exit_price), 2)
                         if exit_price is not None else None),
                "exit_reason": exit_reason, "exit_time": exit_time,
                "net": round(float(t["net"]), 2),
                "magnitude": magnitude, "mag_kind": mag_kind}

    cands = g["reaction_candidates"](cal_path, lo, hi)
    p2f_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 1) for c in cands
                         if abs(c["reaction_ret_pct"]) >= 2.5) if t}
    for t in g["p2f_book"](cands):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        r = p2f_raw[k]
        out.append(norm("P2F", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    _ge, frozen_r2, book_r2 = g["p2fr2_sets"](cands)
    fr2 = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
           for t in frozen_r2}
    for t in book_r2:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        r = fr2[k]
        out.append(norm("P2F-R2", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    low_c, book_low = g["r2lowband_book"](cands)
    low_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 2) for c in low_c) if t}
    for t in book_low:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        r = low_raw[k]
        out.append(norm("R2-LOWBAND", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    n4r = g["n4_raw"](cal_path, lo, hi)
    n4x = {(t["date"], t["symbol"], t["direction"], t["net"]): t
           for t in n4r}
    for t in g["n4_book"](n4r):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        r = n4x[k]
        mv = V1.n4_move_pct(g, t["stock"], t["date"])
        out.append(norm("N4-V3", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(mv), "move_0930_pct"))
    return out


def causal_variant_rows(g, days, chains_c):
    """F4-C / INV-LONG-C / INV-ABOVE-C book rows (pre-law), built from
    ONE causal chain pass + causal F4 collect. Mirrors
    V1.build_base_detailed / build_inv_above_detailed exactly, with
    run_chain_causal and causal pool percentiles."""
    RANK = g["NS"]["RANK"]
    # causal chain pool population + percentiles (V1.inv_pool_percentiles
    # convention, causal chains)
    pop = []
    for sym in g["SYMBOLS"]:
        for day in days:
            for r in chains_c[(sym, day)]:
                if r["round"] <= 2 and r["entry_time"] < "10:30" \
                        and (g["ADR"].get((sym, day)) or 0) >= 3.0:
                    pop.append(r)
    by_day = defaultdict(list)
    for r in pop:
        by_day[r["date"]].append(r)
    pct = {}
    for day, rs in by_day.items():
        rs.sort(key=lambda r: (-RANK.get(r["setup"], 0), r["entry_time"],
                               r["stock"], r["round"]))
        n = len(rs)
        for i, r in enumerate(rs):
            pct[(r["date"], r["stock"], r["round"], r["entry_time"])] = \
                round(100.0 * (n - i) / n, 2)

    def norm(comp, t, stock, dir_, entry, exit_price, exit_reason,
             exit_time, magnitude, mag_kind, extra=None):
        d = {"comp": comp, "date": t["date"], "stock": stock, "dir": dir_,
             "entry_time": t["entry_time"],
             "entry": (round(float(entry), 2) if entry is not None else None),
             "exit": (round(float(exit_price), 2)
                      if exit_price is not None else None),
             "exit_reason": exit_reason, "exit_time": exit_time,
             "net": round(float(t["net"]), 2),
             "magnitude": magnitude, "mag_kind": mag_kind}
        if extra:
            d.update(extra)
        return d

    out = []
    # F4-C
    raw095 = collect2_causal(g, days, g["F4_CFG"], 1.50, 0.95)
    for t in raw095:
        if g["f4_keep"](t):
            out.append(norm("F4-C", t, t["symbol"], t["dir"], t["entry"],
                            t["exit"], t["exit_reason"], t["exit_time"],
                            abs(t["premove_pct"]), "first_move_pct"))
    # INV-LONG-C: build_inv's filters over causal chains
    lng = [r for r in pop if g["cond_inv1"](r["date"])
           and r["direction"] == "LONG"]
    for r in lng:
        if not g["wk"](r["date"]) and r["stock"] not in \
                {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}:
            p = pct[(r["date"], r["stock"], r["round"], r["entry_time"])]
            out.append(norm("INV-LONG-C", r, r["stock"], "LONG", r["entry"],
                            r["exit_price"], r["exit_reason"], r["exit_time"],
                            p, "pool_percentile",
                            {"round": r["round"], "setup": r["setup"]}))
    # INV-ABOVE-C: build_inv_above_detailed's filter over causal chains
    for r in pop:
        if g["g1"](r["date"]) and r["direction"] == "LONG" \
                and not g["wk"](r["date"]) and r["stock"] not in L.BASE_EXCL \
                and r["stock"] not in L.V2_INV_LAW:
            p = pct[(r["date"], r["stock"], r["round"], r["entry_time"])]
            out.append(norm("INV-ABOVE-C", r, r["stock"], r["direction"],
                            r["entry"], r["exit_price"], r["exit_reason"],
                            r["exit_time"], p, "pool_percentile",
                            {"round": r["round"], "setup": r["setup"]}))
    return out, pop


def apply_law_mapped(rows, labels):
    """L.apply_law keys on base comp names; map -C names to base,
    apply, restore."""
    tmp = []
    for t in rows:
        t2 = dict(t)
        t2["comp"] = t["comp"].replace("-C", "") \
            if t["comp"] in ("F4-C", "INV-LONG-C", "INV-ABOVE-C") \
            else t["comp"]
        tmp.append(t2)
    kept = L.apply_law(tmp, labels)
    keys = {(t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"],
             round(float(t["net"]), 2)) for t in kept}
    return [t for t in rows
            if ((t["comp"].replace("-C", "")
                 if t["comp"].endswith("-C") else t["comp"]),
                t["date"], t["stock"], t["dir"], t["entry_time"],
                round(float(t["net"]), 2)) in keys]


def book_stats(rows):
    a = V1.agg(rows)
    ex3, top3 = V1.extop3(rows)
    wins = sum(1 for t in rows if t["net"] > 0)
    return {**a, "ex_top3": ex3, "top3_stocks": top3}


def main():
    t0 = time.time()
    out = {"started": time.strftime("%Y-%m-%d %H:%M UTC")}
    print("loading wide machinery...", flush=True)
    g = V1.load_machinery(ROOT, HI)
    days = [d for d in ALL_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    print("build days:", days, flush=True)
    assert days == ALL_DAYS, days
    labels = L.regime_labels(g)

    # ---------------- LEG 1 ----------------
    print("LEG 1 — causal truncation audit...", flush=True)
    leg1, leg1_pass = leg1_truncation(g)
    out["leg1"] = {"days": AUDIT_DAYS, "slices": SLICES,
                   "results": leg1, "pass": leg1_pass}
    print(f"LEG 1 PASS: {leg1_pass} ({time.time()-t0:.0f}s)", flush=True)

    # ---------------- LEG 2 ----------------
    print("building causal chains (27d x 1081)...", flush=True)
    chains_c = {}
    for sym in g["SYMBOLS"]:
        for day in days:
            chains_c[(sym, day)] = run_chain_causal(g, sym, day)
    n_chain_rows = sum(len(v) for v in chains_c.values())
    print(f"causal chain rows: {n_chain_rows} ({time.time()-t0:.0f}s)",
          flush=True)

    print("building causal variant rows + live-4 rows...", flush=True)
    var_rows, causal_pop = causal_variant_rows(g, days, chains_c)
    live4 = build_live4_detailed(g, MERGED_CAL, LO, HI, days)
    live4 = L.apply_law(live4, labels)
    for t in live4:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    var_rows = apply_law_mapped(var_rows, labels)
    for t in var_rows:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    print(f"live4 rows: {len(live4)}; causal variant rows: "
          f"{len(var_rows)} ({time.time()-t0:.0f}s)", flush=True)

    # per-variant standalone stats (post-law), frozen twins from the
    # v2 pool CSV (same machinery, post-law, same window)
    frozen_pool = list(csv.DictReader(
        open(f"{WS}/sarvasetu_top3_v2_2026-11-11_pool.csv")))
    variants = {}
    for vc, fc in (("F4-C", "F4"), ("INV-LONG-C", "INV-LONG"),
                   ("INV-ABOVE-C", "INV-ABOVE")):
        vr = [t for t in var_rows if t["comp"] == vc]
        fr = [{"net": float(t["net"]), "stock": t["stock"]}
              for t in frozen_pool if t["comp"] == fc]
        variants[vc] = {"causal": book_stats(vr),
                        "frozen_twin_wide": book_stats(fr)}
        print(f"{vc}: causal {variants[vc]['causal']} | frozen "
              f"{variants[vc]['frozen_twin_wide']}", flush=True)
    out["leg2_variants"] = variants

    # chain pool per day (causal) for derive_day stream percentiles
    chain_by_day = defaultdict(list)
    for r in causal_pop:
        chain_by_day[r["date"]].append(r)
    pool_by_day4 = defaultdict(list)
    for t in live4:
        pool_by_day4[t["date"]].append(t)
    pool_by_day7 = defaultdict(list)
    for t in live4 + var_rows:
        pool_by_day7[t["date"]].append(t)

    RANK = g["NS"]["RANK"]

    def run_selection(pool_by_day, chain_by_day_):
        picks_all = []
        for day in days:
            _reps, picks = SIM.derive_day(day, pool_by_day[day],
                                          chain_by_day_[day], RANK)
            for i, p in enumerate(picks):
                t = p["rep"]
                shares, fc = SIM.lens_net(t)
                picks_all.append(
                    {"date": day, "lock_order": i + 1,
                     "lock_time": p["lock_time"], "stock": p["stock"],
                     "comp": t["comp"], "dir": t["dir"],
                     "confluence": p["confluence"],
                     "components": "+".join(p["components"]),
                     "norm_pct": t["norm_pct_live"],
                     "score": round(p["score"], 2),
                     "entry_time": t["entry_time"], "entry": t["entry"],
                     "exit_time": t["exit_time"], "exit": t["exit"],
                     "exit_reason": t["exit_reason"], "net": t["net"],
                     "fc_shares": shares, "fc_net": fc,
                     "regime": labels.get(day, "UNCLASSIFIED")})
        return picks_all

    def pick_stats(recs):
        a = V1.agg(recs)
        ex3, top3 = V1.extop3(recs)
        fc = round(sum(r["fc_net"] for r in recs), 2)
        return {**a, "expectancy": (round(a["net"] / a["trades"], 2)
                                    if a["trades"] else 0.0),
                "ex_top3": ex3, "top3_stocks": top3, "fc_net": fc}

    print("baseline reproduction (4 live comps)...", flush=True)
    base_picks = run_selection(pool_by_day4, defaultdict(list))
    base_stats = pick_stats(base_picks)
    saved = list(csv.DictReader(
        open(f"{WS}/stock_engine_live_2026-11-11_trades.csv")))
    saved_keys = Counter((r["date"], r["stock"], r["comp"],
                          round(float(r["net"]), 2)) for r in saved)
    base_keys = Counter((r["date"], r["stock"], r["comp"],
                         round(float(r["net"]), 2)) for r in base_picks)
    repro = (saved_keys == base_keys
             and base_stats["trades"] == BASELINE["trades"]
             and base_stats["net"] == BASELINE["net"]
             and base_stats["ex_top3"] == BASELINE["ex_top3"])
    print(f"baseline repro: {repro} — mine {base_stats['trades']} tr "
          f"{base_stats['net']:+.2f} ex3 {base_stats['ex_top3']:+.2f} "
          f"vs saved {len(saved)} tr", flush=True)
    out["baseline_repro"] = {"pass": repro, "stats": base_stats}
    assert repro, "baseline reproduction FAILED — do not trust combined"

    print("combined 7-live selection...", flush=True)
    SIM.INV_COMPS = {"INV-LONG-C", "INV-ABOVE-C"}
    comb_picks = run_selection(pool_by_day7, chain_by_day)
    comb_stats = pick_stats(comb_picks)
    oct_p = [r for r in comb_picks if r["date"] in OCT_DAYS]
    nov_p = [r for r in comb_picks if r["date"] in NOV_DAYS]
    mix = {}
    for c in ("N4-V3", "P2F", "P2F-R2", "R2-LOWBAND", "F4-C",
              "INV-LONG-C", "INV-ABOVE-C"):
        cr = [r for r in comb_picks if r["comp"] == c]
        if cr:
            mix[c] = {"picks": len(cr),
                      "net": round(sum(r["net"] for r in cr), 2)}
    leg2_pass = comb_stats["ex_top3"] > BASELINE["ex_top3"]
    print(f"COMBINED: {comb_stats} | Oct {pick_stats(oct_p)} | "
          f"Nov {pick_stats(nov_p)}", flush=True)
    print(f"LEG 2 PASS (ex-top-3 {comb_stats['ex_top3']:+.2f} > "
          f"{BASELINE['ex_top3']:+.2f}): {leg2_pass}", flush=True)
    out["leg2_combined"] = {"stats": comb_stats,
                            "october": pick_stats(oct_p),
                            "november": pick_stats(nov_p),
                            "component_mix": mix, "pass": leg2_pass,
                            "baseline": BASELINE}

    fields = ["date", "lock_order", "lock_time", "stock", "comp", "dir",
              "confluence", "components", "norm_pct", "score",
              "entry_time", "entry", "exit_time", "exit", "exit_reason",
              "net", "fc_shares", "fc_net", "regime"]
    with open(f"{WS}/stock_engine_causal3_2026-11-12_trades.csv", "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in comb_picks:
            w.writerow({k: r[k] for k in fields})
    vfields = ["date", "comp", "stock", "dir", "entry_time", "entry",
               "exit", "exit_time", "exit_reason", "net", "regime",
               "magnitude", "mag_kind"]
    with open(f"{WS}/stock_engine_causal3_variant_rows.csv", "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=vfields)
        w.writeheader()
        for t in sorted(var_rows, key=lambda t: (t["date"], t["comp"],
                                                 t["stock"])):
            w.writerow({k: t.get(k) for k in vfields})
    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/stock_engine_causal3_gate_summary.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"DONE legs 1+2 in {out['elapsed_secs']}s — leg1 "
          f"{leg1_pass}, leg2 {leg2_pass}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
