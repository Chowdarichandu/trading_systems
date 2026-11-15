#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 3: fix the Jul-Oct wound.
Spec: ekam_intraday_stocks_r3_SPEC.md (frozen 2026-11-14, before scoring).
Reuses ekam_intraday_stocks_r2_build.py (R2), which reuses R1, for data, votes,
contexts, the parameterised X2 exit, summaries and the placebo. Research only.
Writes ekam_intraday_stocks_r3_results.json. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2

WS = r1.WS
CAND = dict(D=3, S=0.0100, C=None)   # CAND-T5 exit params (R2, frozen)

# ---------------------------------------------------------------- helpers
def blk(nets):
    return r2.block(nets)

def cell_stats(recs, year):
    idx = [x for x in recs if x["date"][:4] == str(year)]
    def sel(lo, hi):
        return blk([x["net"] for x in idx if lo <= x["date"] <= hi])
    return dict(jan_jun=sel(f"{year}-01-01", f"{year}-06-30"),
                jul_oct=sel(f"{year}-07-01", f"{year}-10-31"),
                jan_oct=sel(f"{year}-01-01", f"{year}-10-31"))

def hour_bucket(stamp):
    if stamp < "11:00": return "09-11"
    if stamp < "13:00": return "11-13"
    return "13-15"

# ---------------------------------------------------------------- main
def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_r2_results.json")) as f:
        r2res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}

    ctxs, pre = {}, {}
    for T in (4, 5):
        ctxs[T], pre[T] = r2.build_contexts(stocks, by_sym, T)

    # ---- CONTROL: CAND-T5 reproduced exactly (windows, months, ex-top3, November)
    base_ctxs = ctxs[5]
    base_nets = [r2.net_of(t, **CAND) for t in base_ctxs]
    yr = r2.year_rows(base_ctxs, base_nets)
    pub = r2res["candidates"]["CAND-T5"]
    ok = True
    for y in (2025, 2026):
        py = pub["years"][str(y)]
        for w in ("jan_jun", "jul_oct", "jan_oct"):
            got = {k: yr[y][w][k] for k in ("trades", "total", "wr")}
            if got != {k: py[w][k] for k in ("trades", "total", "wr")}: ok = False
        if yr[y]["months"] != py["months"]: ok = False
        if yr[y]["ex_top3"] != py["ex_top3"]: ok = False
    got_nov = {k: yr["november_cf"][k] for k in ("trades", "total", "wr")}
    if got_nov != {k: pub["november_cf"][k] for k in ("trades", "total", "wr")}: ok = False
    if not ok:
        print("CONTROL MISMATCH — CAND-T5 not reproduced; run stopped.")
        print(json.dumps(yr, indent=1)); return
    print("CONTROL OK — CAND-T5 reproduced exactly (all windows, months, ex-top-3, November).")

    # ---- timing audit sample (R2 design, pre-cap candidates T4+T5)
    flat = sorted(pre[4] + pre[5], key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — truncated recompute {checked} checked, {mism} mismatches.")

    # ---- STEP 1: ANATOMY of CAND-T5
    recs = []
    for t, n in zip(base_ctxs, base_nets):
        if t["votes"] not in (5, 6):
            print("DATA ERROR — T5 trade with votes =", t["votes"]); return
        recs.append(dict(sym=t["sym"], date=t["date"], side=t["side"], votes=t["votes"],
                         entry_stamp=t["entry_stamp"], net=n, ctx=t))
    splits = {
        "side":  [("LONG", lambda x: x["side"] == 1), ("SHORT", lambda x: x["side"] == -1)],
        "hour":  [("09-11", lambda x: hour_bucket(x["entry_stamp"]) == "09-11"),
                  ("11-13", lambda x: hour_bucket(x["entry_stamp"]) == "11-13"),
                  ("13-15", lambda x: hour_bucket(x["entry_stamp"]) == "13-15")],
        "votes": [("5", lambda x: x["votes"] == 5), ("6", lambda x: x["votes"] == 6)],
    }
    anatomy, wounds = {}, []
    for sname, cells in splits.items():
        anatomy[sname] = {}
        for cname, fn in cells:
            sub = [x for x in recs if fn(x)]
            per = {y: cell_stats(sub, y) for y in (2025, 2026)}
            anatomy[sname][cname] = per
            # wound test: (i) Jul-Oct net < 0 both years; (ii) full net negative OR
            # lowest among this split's cells, in both years.
            cond = []
            for y in (2025, 2026):
                fulls = {cn: cell_stats([x for x in recs if f2(x)], y)["jan_oct"]["total"]
                         for cn, f2 in cells}
                lowest = min(fulls.values())
                cfull = per[y]["jan_oct"]["total"]
                cond.append(per[y]["jul_oct"]["total"] < 0 and (cfull < 0 or cfull == lowest))
            if all(cond):
                comb_jo = per[2025]["jul_oct"]["total"] + per[2026]["jul_oct"]["total"]
                wounds.append(dict(split=sname, cell=cname, combined_jul_oct=round(comb_jo, 2)))
    print("ANATOMY wounds:", json.dumps(wounds))

    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r3_SPEC.md (frozen 2026-11-14)",
               "control": dict(reproduced=True,
                               full={y: yr[y]["jan_oct"] for y in (2025, 2026)},
                               november_cf=yr["november_cf"]),
               "timing_audit": dict(truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "anatomy": anatomy, "wounds": wounds}

    # ---- STEP 2: choose the ONE dial by the frozen mapping
    dial = None
    if wounds:
        splits_hit = {w["split"] for w in wounds}
        if len(splits_hit) == 1:
            chosen = min((w for w in wounds if w["split"] in splits_hit),
                         key=lambda w: w["combined_jul_oct"])
        else:
            order = {"side": 0, "votes": 1, "hour": 2}
            chosen = min(wounds, key=lambda w: (w["combined_jul_oct"], order[w["split"]]))
        results["wound_chosen"] = chosen
        s, c = chosen["split"], chosen["cell"]
        if s == "side":
            dial = dict(kind="drop_side", drop=("LONG" if c == "LONG" else "SHORT"))
        elif s == "votes" and c == "5":
            dial = dict(kind="confirmation_bar")
        elif s == "hour" and c == "13-15":
            dial = dict(kind="cutoff_1300")
        else:
            results["dial"] = None
            results["no_dial_reason"] = f"wound cell {s}/{c} has no mapping in the frozen spec"
    else:
        results["wound_chosen"] = None
        results["dial"] = None
        results["no_dial_reason"] = "no cell meets the wound rule"
    print("DIAL:", json.dumps(dial))

    # ---- STEP 3: score the dialed candidate
    if dial is not None:
        cand_recs, detail = [], {}
        if dial["kind"] == "drop_side":
            drop_side = 1 if dial["drop"] == "LONG" else -1
            cand_recs = [x for x in recs if x["side"] != drop_side]
            detail = dict(dropped_trades=len(recs) - len(cand_recs))
        elif dial["kind"] == "cutoff_1300":
            cand_recs = [x for x in recs if x["entry_stamp"] < "13:00"]
            detail = dict(dropped_trades=len(recs) - len(cand_recs))
        elif dial["kind"] == "confirmation_bar":
            kept5 = conf = dropped = 0
            for x in recs:
                if x["votes"] == 6:
                    cand_recs.append(x); continue
                t = x["ctx"]; eli = t["entry_li"]
                v = t["own"][eli] if eli < len(t["own"]) else None
                okv = v is not None and not (isinstance(v, float) and math.isnan(v)) and v >= 5
                if not okv or eli + 1 > t["sq_li"]:
                    dropped += 1; continue
                Dd = by_sym[t["sym"]]["days"][t["date"]]
                nt = dict(t); nt["entry_li"] = eli + 1
                nt["entry_stamp"] = Dd["st"][eli + 1]
                nt["E"] = float(Dd["o"][eli + 1])
                nnet = r2.net_of(nt, **CAND)
                cand_recs.append(dict(x, entry_stamp=nt["entry_stamp"], net=nnet, ctx=nt))
                conf += 1; kept5 += 1
            detail = dict(votes5_trades=sum(1 for x in recs if x["votes"] == 5),
                          confirmed_and_shifted=conf, dropped_unconfirmed=dropped)
        # timing assert on candidate entries
        for x in cand_recs:
            assert x["entry_stamp"] > x["ctx"]["signal_stamp"]
        cctx = [x["ctx"] for x in cand_recs]
        cnets = [x["net"] for x in cand_recs]
        # year_rows uses ctx dates only; build shadow ctx list with candidate dates
        shadow = [dict(date=x["date"]) for x in cand_recs]
        cyr = r2.year_rows(shadow, cnets)
        entry = dict(dial=dial, detail=detail, years={}, november_cf=cyr["november_cf"])
        per_year_pass = {}
        for y in (2025, 2026):
            real = cyr[y]["jan_oct"]["total"]; cnt = cyr[y]["jan_oct"]["trades"]
            draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            cyr[y]["placebo_pct"] = pct
            cyr[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                            median=round(sorted(draws)[100], 2),
                                            max=round(max(draws), 2)) if draws else None)
            entry["years"][y] = cyr[y]
            per_year_pass[y] = dict(
                year_positive=cyr[y]["jan_oct"]["total"] > 0,
                jan_jun_positive=cyr[y]["jan_jun"]["total"] > 0,
                jul_oct_positive=cyr[y]["jul_oct"]["total"] > 0,
                expectancy_ge_80=(cyr[y]["jan_oct"]["expectancy"] is not None
                                  and cyr[y]["jan_oct"]["expectancy"] >= 80.0),
                placebo_ge_95=(pct is not None and pct >= 95.0))
            per_year_pass[y]["all"] = all(per_year_pass[y].values())
        entry["desired_bar"] = dict(per_year=per_year_pass,
                                    reached=bool(per_year_pass[2025]["all"] and per_year_pass[2026]["all"]))
        results["candidate"] = entry
        results["desired_bar_reached"] = entry["desired_bar"]["reached"]
        print("CANDIDATE:", json.dumps({y: entry["years"][y]["jan_oct"] for y in (2025, 2026)}),
              "NOV", entry["november_cf"], "BAR", entry["desired_bar"])

    with open(os.path.join(WS, "ekam_intraday_stocks_r3_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r3_results.json")

if __name__ == "__main__":
    main()
