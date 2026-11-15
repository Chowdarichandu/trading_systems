#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 4: the 6-vote turn.
Spec: ekam_intraday_stocks_r4_SPEC.md (frozen 2026-11-14, before scoring).
Reuses ekam_intraday_stocks_r2_build.py (R2), which reuses R1, for data, votes,
contexts, the parameterised X2 exit, summaries and the placebo. Research only.
Writes ekam_intraday_stocks_r4_results.json. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2

WS = r1.WS
CAND = dict(D=3, S=0.0100, C=None)   # CAND exit params (R2, frozen)

def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_r2_results.json")) as f:
        r2res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}

    ctxs, pre = {}, {}
    for T in (5, 6):
        ctxs[T], pre[T] = r2.build_contexts(stocks, by_sym, T)

    # ---- CONTROL: CAND-T5 reproduced exactly (windows, months, ex-top3, November)
    base_nets = [r2.net_of(t, **CAND) for t in ctxs[5]]
    yr5 = r2.year_rows(ctxs[5], base_nets)
    pub = r2res["candidates"]["CAND-T5"]
    ok = True
    for y in (2025, 2026):
        py = pub["years"][str(y)]
        for w in ("jan_jun", "jul_oct", "jan_oct"):
            got = {k: yr5[y][w][k] for k in ("trades", "total", "wr")}
            if got != {k: py[w][k] for k in ("trades", "total", "wr")}: ok = False
        if yr5[y]["months"] != py["months"]: ok = False
        if yr5[y]["ex_top3"] != py["ex_top3"]: ok = False
    got_nov = {k: yr5["november_cf"][k] for k in ("trades", "total", "wr")}
    if got_nov != {k: pub["november_cf"][k] for k in ("trades", "total", "wr")}: ok = False
    if not ok:
        print("CONTROL MISMATCH — CAND-T5 not reproduced; run stopped.")
        print(json.dumps(yr5, indent=1)); return
    print("CONTROL OK — CAND-T5 reproduced exactly (all windows, months, ex-top-3, November).")

    # ---- timing audit sample (R2 design, pre-cap candidates T5+T6)
    flat = sorted(pre[5] + pre[6], key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — truncated recompute {checked} checked, {mism} mismatches.")

    # ---- THE TURN: CAND-T6 = T6 contexts, CAND exit stack unchanged
    t6 = ctxs[6]
    for t in t6:
        if t["votes"] != 6:
            print("DATA ERROR — T6 trade with votes =", t["votes"]); return
        assert t["entry_stamp"] > t["signal_stamp"]
    nets6 = [r2.net_of(t, **CAND) for t in t6]
    yr6 = r2.year_rows(t6, nets6)

    entry = dict(params=dict(T=6, **CAND), years={}, november_cf=yr6["november_cf"])
    per_year_pass = {}
    for y in (2025, 2026):
        real = yr6[y]["jan_oct"]["total"]; cnt = yr6[y]["jan_oct"]["trades"]
        draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
        pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
        yr6[y]["placebo_pct"] = pct
        yr6[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                        median=round(sorted(draws)[100], 2),
                                        max=round(max(draws), 2)) if draws else None)
        entry["years"][y] = yr6[y]
        per_year_pass[y] = dict(
            year_positive=bool(yr6[y]["jan_oct"]["total"] > 0),
            jan_jun_positive=bool(yr6[y]["jan_jun"]["total"] > 0),
            jul_oct_positive=bool(yr6[y]["jul_oct"]["total"] > 0),
            expectancy_ge_80=bool(yr6[y]["jan_oct"]["expectancy"] is not None
                                  and yr6[y]["jan_oct"]["expectancy"] >= 80.0),
            placebo_ge_95=bool(pct is not None and pct >= 95.0))
        per_year_pass[y]["all"] = bool(all(per_year_pass[y].values()))
    entry["desired_bar"] = dict(per_year=per_year_pass,
                                reached=bool(per_year_pass[2025]["all"] and per_year_pass[2026]["all"]))

    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r4_SPEC.md (frozen 2026-11-14)",
               "control": dict(reproduced=True,
                               full={y: yr5[y]["jan_oct"] for y in (2025, 2026)},
                               november_cf=yr5["november_cf"]),
               "timing_audit": dict(truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "candidate": entry,
               "desired_bar_reached": entry["desired_bar"]["reached"]}
    print("CAND-T6:", json.dumps({y: entry["years"][y]["jan_oct"] for y in (2025, 2026)}),
          "NOV", entry["november_cf"], "BAR", entry["desired_bar"])

    with open(os.path.join(WS, "ekam_intraday_stocks_r4_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r4_results.json")

if __name__ == "__main__":
    main()
