#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 7: six votes under the cap-3 selection.
Spec: ekam_intraday_stocks_r7_SPEC.md (frozen 2026-11-14, before scoring).
Reuses R1 (data, votes, candidates, audit), R2 (CAND exit stack, summaries,
placebo) and R5 (day-candidate collection, contexts, EARLIEST-3 selection).
Only the entry threshold changes: T=6 candidates under S2's EARLIEST-3 cap.
Research only. Writes ekam_intraday_stocks_r7_results.json.
Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

WS = r1.WS
CAND = dict(D=3, S=0.0100, C=None)   # CAND-T5 exit params (R2, frozen)


def collect_day_candidates_T(stocks, T):
    """R5 collect_day_candidates verbatim, with the threshold parameterised."""
    all_dates = sorted({d for S in stocks for d in S["days"]})
    daymap, pre_cap = {}, []
    for date in all_dates:
        cands = []
        for S in stocks:
            cd = r1.day_candidates(S, date, T)
            if cd: cands.append(cd)
        cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))
        daymap[date] = cands
        pre_cap.extend(cands)
    return daymap, pre_cap


def score_row(ctxs):
    nets = [r2.net_of(t, **CAND) for t in ctxs]
    return nets, r2.year_rows(ctxs, nets)


def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_r5_results.json")) as f:
        r5res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}

    # ---- CONTROL: S2 EARLIEST-3 (T=5) reproduced exactly
    daymap5, pre5 = r5.collect_day_candidates(stocks)
    ctx_s2 = r5.contexts_from(daymap5, by_sym, r5.sel_s2)
    _, yr_s2 = score_row(ctx_s2)
    pub = r5res["rows"]["S2"]
    ok = True
    for y in (2025, 2026):
        py = pub["years"][str(y)]
        for w in ("jan_jun", "jul_oct", "jan_oct"):
            got = {k: yr_s2[y][w][k] for k in ("trades", "total", "wr")}
            if got != {k: py[w][k] for k in ("trades", "total", "wr")}: ok = False
        if yr_s2[y]["months"] != py["months"]: ok = False
        if yr_s2[y]["ex_top3"] != py["ex_top3"]: ok = False
    got_nov = {k: yr_s2["november_cf"][k] for k in ("trades", "total", "wr")}
    if got_nov != {k: pub["november_cf"][k] for k in ("trades", "total", "wr")}: ok = False
    if not ok:
        print("CONTROL MISMATCH — S2 EARLIEST-3 not reproduced; run stopped.")
        print(json.dumps(yr_s2, indent=1)); return
    print("CONTROL OK — S2 EARLIEST-3 reproduced exactly (all windows, months, ex-top-3, November).")

    # ---- THE ROW: S2-T6 (T=6 candidates, EARLIEST-3 selection, CAND exits)
    daymap6, pre6 = collect_day_candidates_T(stocks, 6)
    ctx_t6 = r5.contexts_from(daymap6, by_sym, r5.sel_s2)
    for t in ctx_t6:
        if t["votes"] != 6:
            print("DATA ERROR — S2-T6 trade with votes =", t["votes"]); return
        assert t["entry_stamp"] > t["signal_stamp"]  # timing audit
    _, yr_t6 = score_row(ctx_t6)

    # ---- timing audit (R2/R4 design: every 37th of combined pre-cap T5+T6)
    flat = sorted(pre5 + pre6, key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — truncated recompute {checked} checked, {mism} mismatches.")

    # ---- placebo + bar check for S2-T6
    entry = dict(label="S2-T6 (6-of-6 votes, EARLIEST-3, CAND-T5 exits)", years={},
                 november_cf=yr_t6["november_cf"])
    per_year = {}
    for y in (2025, 2026):
        real = yr_t6[y]["jan_oct"]["total"]; cnt = yr_t6[y]["jan_oct"]["trades"]
        draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
        pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
        yr_t6[y]["placebo_pct"] = pct
        yr_t6[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                          median=round(sorted(draws)[100], 2),
                                          max=round(max(draws), 2)) if draws else None)
        entry["years"][y] = yr_t6[y]
        per_year[y] = r5.bar_check(yr_t6[y], pct)
    entry["desired_bar"] = dict(per_year=per_year,
                                reached=bool(per_year[2025]["all"] and per_year[2026]["all"]))

    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r7_SPEC.md (frozen 2026-11-14)",
               "control": dict(row="S2 EARLIEST-3", reproduced=True,
                               full={y: yr_s2[y]["jan_oct"] for y in (2025, 2026)},
                               november_cf=yr_s2["november_cf"]),
               "timing_audit": dict(truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "row": entry}
    print(f"S2-T6: 2025 {yr_t6[2025]['jan_oct']} | 2026 {yr_t6[2026]['jan_oct']} | "
          f"NOV {yr_t6['november_cf']} | BAR {entry['desired_bar']['reached']}")

    with open(os.path.join(WS, "ekam_intraday_stocks_r7_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r7_results.json")


if __name__ == "__main__":
    main()
