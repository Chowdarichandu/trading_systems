#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 5: the selection turn.
Spec: ekam_intraday_stocks_r5_SPEC.md (frozen 2026-11-14, before scoring).
Reuses ekam_intraday_stocks_build.py (R1) and ekam_intraday_stocks_r2_build.py
(R2) for data, votes, candidates, the CAND exit stack, summaries and the placebo.
Only the day-cap SELECTION differs per row. Research only.
Writes ekam_intraday_stocks_r5_results.json. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2

WS = r1.WS
CAND = dict(D=3, S=0.0100, C=None)   # CAND-T5 exit params (R2, frozen)

# ---------------------------------------------------------------- selection rules
def sel_s0(cands):   # EARLIEST-5 (control, R2 verbatim)
    return cands[:r1.DAY_CAP]

def sel_s1(cands):   # PRIORITY-5: <=3 from signals stamped < 11:00, <=2 from >= 11:00
    a = [c for c in cands if c["signal_stamp"] < "11:00"][:3]
    b = [c for c in cands if c["signal_stamp"] >= "11:00"][:2]
    return a + b

def sel_s2(cands):   # EARLIEST-3
    return cands[:3]

def sel_s3(cands):   # FIRST-HOUR-ONLY: signals stamped <= 10:30, earliest 5
    return [c for c in cands if c["signal_stamp"] <= "10:30"][:r1.DAY_CAP]

ROWS = [("S0", "EARLIEST-5 (control = CAND-T5)", sel_s0),
        ("S1", "PRIORITY-5 (<=3 before 11:00, <=2 from 11:00)", sel_s1),
        ("S2", "EARLIEST-3", sel_s2),
        ("S3", "FIRST-HOUR-ONLY (signals <= 10:30, cap 5)", sel_s3)]

# ---------------------------------------------------------------- contexts
def collect_day_candidates(stocks):
    """Per-date sorted T=5 candidate lists + the flat pre-cap list (once)."""
    all_dates = sorted({d for S in stocks for d in S["days"]})
    daymap, pre_cap = {}, []
    for date in all_dates:
        cands = []
        for S in stocks:
            cd = r1.day_candidates(S, date, 5)
            if cd: cands.append(cd)
        cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))
        daymap[date] = cands
        pre_cap.extend(cands)
    return daymap, pre_cap

def contexts_from(daymap, by_sym, selector):
    """R2 build_contexts verbatim, with the day cap replaced by `selector`."""
    ctxs = []
    for date in sorted(daymap):
        for cd in selector(daymap[date]):
            S = by_sym[cd["sym"]]; Dd = S["days"][cd["date"]]
            eli = cd["entry_li"]; E = float(Dd["o"][eli])
            assert cd["entry_stamp"] > cd["signal_stamp"]  # timing audit
            ctxs.append(dict(sym=cd["sym"], date=cd["date"], side=cd["side"],
                             votes=cd["votes"], signal_stamp=cd["signal_stamp"],
                             entry_stamp=cd["entry_stamp"], E=E, entry_li=eli,
                             sq_li=Dd["sq_li"], o=Dd["o"], h=Dd["h"], l=Dd["l"], c=Dd["c"],
                             own=(Dd["LV"] if cd["side"] == 1 else Dd["SV"])))
    return ctxs

def bar_check(yr_row, pct):
    chk = dict(year_positive=bool(yr_row["jan_oct"]["total"] > 0),
               jan_jun_positive=bool(yr_row["jan_jun"]["total"] > 0),
               jul_oct_positive=bool(yr_row["jul_oct"]["total"] > 0),
               expectancy_ge_80=bool(yr_row["jan_oct"]["expectancy"] is not None
                                     and yr_row["jan_oct"]["expectancy"] >= 80.0),
               placebo_ge_95=bool(pct is not None and pct >= 95.0))
    chk["all"] = bool(all(chk.values()))
    return chk

def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_r2_results.json")) as f:
        r2res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    daymap, pre_cap = collect_day_candidates(stocks)

    rows_ctx = {name: contexts_from(daymap, by_sym, sel) for name, _, sel in ROWS}

    # ---- CONTROL: S0 must reproduce CAND-T5 exactly (windows, months, ex-top3, Nov)
    nets0 = [r2.net_of(t, **CAND) for t in rows_ctx["S0"]]
    yr0 = r2.year_rows(rows_ctx["S0"], nets0)
    pub = r2res["candidates"]["CAND-T5"]
    ok = True
    for y in (2025, 2026):
        py = pub["years"][str(y)]
        for w in ("jan_jun", "jul_oct", "jan_oct"):
            got = {k: yr0[y][w][k] for k in ("trades", "total", "wr")}
            if got != {k: py[w][k] for k in ("trades", "total", "wr")}: ok = False
        if yr0[y]["months"] != py["months"]: ok = False
        if yr0[y]["ex_top3"] != py["ex_top3"]: ok = False
    got_nov = {k: yr0["november_cf"][k] for k in ("trades", "total", "wr")}
    if got_nov != {k: pub["november_cf"][k] for k in ("trades", "total", "wr")}: ok = False
    if not ok:
        print("CONTROL MISMATCH — S0/CAND-T5 not reproduced; run stopped.")
        print(json.dumps(yr0, indent=1)); return
    print("CONTROL OK — S0 = CAND-T5 reproduced exactly (all windows, months, ex-top-3, November).")

    # ---- timing audit (R2 design: every 37th pre-cap T=5 candidate)
    flat = sorted(pre_cap, key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — truncated recompute {checked} checked, {mism} mismatches.")

    # ---- score every row
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r5_SPEC.md (frozen 2026-11-14)",
               "control": dict(reproduced=True,
                               full={y: yr0[y]["jan_oct"] for y in (2025, 2026)},
                               november_cf=yr0["november_cf"]),
               "timing_audit": dict(truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "rows": {}}
    totals = {}
    for name, label, _ in ROWS:
        nets = nets0 if name == "S0" else [r2.net_of(t, **CAND) for t in rows_ctx[name]]
        yr = yr0 if name == "S0" else r2.year_rows(rows_ctx[name], nets)
        entry = dict(label=label, years={}, november_cf=yr["november_cf"])
        per_year = {}
        for y in (2025, 2026):
            real = yr[y]["jan_oct"]["total"]; cnt = yr[y]["jan_oct"]["trades"]
            draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            yr[y]["placebo_pct"] = pct
            yr[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                           median=round(sorted(draws)[100], 2),
                                           max=round(max(draws), 2)) if draws else None)
            entry["years"][y] = yr[y]
            per_year[y] = bar_check(yr[y], pct)
        entry["desired_bar"] = dict(per_year=per_year,
                                    reached=bool(per_year[2025]["all"] and per_year[2026]["all"]))
        results["rows"][name] = entry
        totals[name] = (yr[2025]["jan_oct"]["total"] + yr[2026]["jan_oct"]["total"],
                        min(yr[2025]["jan_oct"]["total"], yr[2026]["jan_oct"]["total"]))
        print(f"{name} {label}: 2025 {yr[2025]['jan_oct']} | 2026 {yr[2026]['jan_oct']} | "
              f"NOV {yr['november_cf']} | BAR {entry['desired_bar']['reached']}")

    # ---- best non-control row (frozen rule) for the month table
    best = max(("S1", "S2", "S3"), key=lambda n: (totals[n][0], totals[n][1],
                                                  -("S1", "S2", "S3").index(n)))
    results["best_row"] = best
    results["desired_bar_any_reached"] = any(results["rows"][n]["desired_bar"]["reached"]
                                             for n, _, _ in ROWS)
    print("BEST ROW (non-control, by combined two-year total):", best)
    print("BAR REACHED BY ANY ROW:", results["desired_bar_any_reached"])

    with open(os.path.join(WS, "ekam_intraday_stocks_r5_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r5_results.json")

if __name__ == "__main__":
    main()
