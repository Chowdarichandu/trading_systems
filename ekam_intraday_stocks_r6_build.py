#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 6: the 2025 Jul-Oct cell.
Spec: ekam_intraday_stocks_r6_SPEC.md (frozen 2026-11-14, before scoring).
Reuses R1 (data/votes/candidates/audit), R2 (CAND exit stack, year_rows,
placebo) and R5 (candidate collection, contexts, S2 selection, bar check).
Research only. Writes ekam_intraday_stocks_r6_results.json.
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
JO25 = ("2025-07-01", "2025-10-31")
JO26 = ("2026-07-01", "2026-10-31")

def split_block(ctxs, nets, idx):
    return r2.block([nets[i] for i in idx])

def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_r5_results.json")) as f:
        r5res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    daymap, pre_cap = r5.collect_day_candidates(stocks)

    # ---- CONTROL: S2 EARLIEST-3 must reproduce R5 exactly
    ctx_s2 = r5.contexts_from(daymap, by_sym, r5.sel_s2)
    nets_s2 = [r2.net_of(t, **CAND) for t in ctx_s2]
    yr_s2 = r2.year_rows(ctx_s2, nets_s2)
    pub = r5res["rows"]["S2"]
    ok = True
    for y in (2025, 2026):
        py = pub["years"][str(y)]
        for w in ("jan_jun", "jul_oct", "jan_oct"):
            got = {k: yr_s2[y][w][k] for k in ("trades", "total", "wr", "expectancy")}
            if got != {k: py[w][k] for k in ("trades", "total", "wr", "expectancy")}: ok = False
        if yr_s2[y]["ex_top3"] != py["ex_top3"]: ok = False
    got_nov = {k: yr_s2["november_cf"][k] for k in ("trades", "total", "wr")}
    if got_nov != {k: pub["november_cf"][k] for k in ("trades", "total", "wr")}: ok = False
    if not ok:
        print("CONTROL MISMATCH — S2 not reproduced; run stopped.")
        print(json.dumps(yr_s2, indent=1, default=str)); return
    print("CONTROL OK — S2 EARLIEST-3 reproduced exactly "
          f"(2025 {yr_s2[2025]['jan_oct']['total']:+.2f} · 2026 {yr_s2[2026]['jan_oct']['total']:+.2f} · "
          f"Nov {yr_s2['november_cf']['total']:+.2f}).")

    # ---- timing audit (R5 design: every 37th pre-cap T=5 candidate)
    flat = sorted(pre_cap, key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — truncated recompute {checked} checked, {mism} mismatches.")

    # ---- STEP 1: anatomy of S2's 2025 Jul-Oct trades (+ 2026 Jul-Oct by side)
    idx25 = [i for i, t in enumerate(ctx_s2) if JO25[0] <= t["date"] <= JO25[1]]
    idx26 = [i for i, t in enumerate(ctx_s2) if JO26[0] <= t["date"] <= JO26[1]]
    assert len(idx25) == 252, len(idx25)
    def by_month(idx):
        return {m: split_block(ctx_s2, nets_s2,
                               [i for i in idx if ctx_s2[i]["date"][5:7] == m])
                for m in ("07", "08", "09", "10")}
    def by_side(idx):
        return {("LONG" if sd == 1 else "SHORT"):
                split_block(ctx_s2, nets_s2, [i for i in idx if ctx_s2[i]["side"] == sd])
                for sd in (1, -1)}
    def by_votes(idx):
        return {str(v): split_block(ctx_s2, nets_s2,
                                    [i for i in idx if ctx_s2[i]["votes"] == v])
                for v in (5, 6)}
    def by_stock(idx):
        agg = {}
        for i in idx:
            a = agg.setdefault(ctx_s2[i]["sym"], [])
            a.append(nets_s2[i])
        rows = [dict(sym=s, **r2.block(v)) for s, v in agg.items()]
        rows.sort(key=lambda x: x["total"])
        return rows
    anatomy = dict(window=split_block(ctx_s2, nets_s2, idx25),
                   by_month=by_month(idx25),
                   by_side=by_side(idx25),
                   by_side_2026_jul_oct=by_side(idx26),
                   by_votes=by_votes(idx25),
                   worst_stocks=by_stock(idx25)[:5],
                   all_stocks=by_stock(idx25))
    print("ANATOMY 2025 Jul-Oct:", json.dumps(anatomy["window"]))
    print(" by month:", json.dumps(anatomy["by_month"]))
    print(" by side :", json.dumps(anatomy["by_side"]),
          "| 2026 Jul-Oct by side:", json.dumps(anatomy["by_side_2026_jul_oct"]))
    print(" by votes:", json.dumps(anatomy["by_votes"]))
    print(" worst stocks:", json.dumps(anatomy["worst_stocks"]))

    # ---- STEP 2: the dial, by the frozen mapping (checked in spec order)
    s25 = {sd: anatomy["by_side"][("LONG" if sd == 1 else "SHORT")]["total"] for sd in (1, -1)}
    s26 = {sd: anatomy["by_side_2026_jul_oct"][("LONG" if sd == 1 else "SHORT")]["total"]
           for sd in (1, -1)}
    qualifying = [sd for sd in (1, -1)
                  if s25[sd] < 0 and (s26[sd] < 0 or s26[sd] <= s26[-sd])]
    dial, dial_detail = None, {}
    if qualifying:
        drop = min(qualifying, key=lambda sd: s25[sd])  # the wound carrier if both qualify
        dial = "SIDE_DROP"
        dial_detail = dict(dropped_side=("LONG" if drop == 1 else "SHORT"),
                           dropped_side_value=drop, qualifying_sides=qualifying,
                           side_net_2025_jul_oct={("LONG" if k == 1 else "SHORT"): v
                                                  for k, v in s25.items()},
                           side_net_2026_jul_oct={("LONG" if k == 1 else "SHORT"): v
                                                  for k, v in s26.items()})
        keep = -drop
        filt = {d: [c for c in cs if c["side"] == keep] for d, cs in daymap.items()}
    else:
        worst_month = min(anatomy["by_month"].items(), key=lambda kv: kv[1]["total"])
        if worst_month[1]["total"] <= anatomy["window"]["total"]:
            dial = "NONE_MONTH_CONCENTRATION"
            dial_detail = dict(worst_month=worst_month[0],
                               worst_month_net=worst_month[1]["total"],
                               window_net=anatomy["window"]["total"])
        else:
            dial = "BREADTH_GATE"
            # breadth at (date, stamp): share of names with a bar at that stamp
            # whose close is above their own session VWAP-proxy at that bar
            above, total = {}, {}
            for S in stocks:
                for date, D in S["days"].items():
                    for li, stamp in enumerate(D["st"]):
                        key = (date, stamp)
                        total[key] = total.get(key, 0) + 1
                        if D["c"][li] > D["vwap"][li]:
                            above[key] = above.get(key, 0) + 1
            def gated(cs):
                out = []
                for c in cs:
                    b = above.get((c["date"], c["signal_stamp"]), 0) / \
                        total[(c["date"], c["signal_stamp"])]
                    if c["side"] == 1 and b < 0.40: continue
                    if c["side"] == -1 and b > 0.60: continue
                    out.append(c)
                return out
            filt = {d: gated(cs) for d, cs in daymap.items()}
            dial_detail = dict(rule="skip LONG if breadth<40%, SHORT if breadth>60% "
                                    "at the signal bar")
    print("DIAL:", dial, json.dumps(dial_detail, default=str))

    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r6_SPEC.md (frozen 2026-11-14)",
               "control": dict(reproduced=True,
                               full={y: yr_s2[y]["jan_oct"] for y in (2025, 2026)},
                               jul_oct={y: yr_s2[y]["jul_oct"] for y in (2025, 2026)},
                               november_cf=yr_s2["november_cf"]),
               "timing_audit": dict(entry_after_signal_asserted_on_all_trades=True,
                                    truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "anatomy_2025_jul_oct": anatomy,
               "dial": dial, "dial_detail": dial_detail,
               "dialed_row": None, "desired_bar": None}

    # ---- STEP 3: re-score only if a real dial was chosen
    if dial in ("SIDE_DROP", "BREADTH_GATE"):
        ctx_d = r5.contexts_from(filt, by_sym, r5.sel_s2)
        nets_d = [r2.net_of(t, **CAND) for t in ctx_d]
        yr_d = r2.year_rows(ctx_d, nets_d)
        entry = dict(years={}, november_cf=yr_d["november_cf"])
        per_year = {}
        for y in (2025, 2026):
            real = yr_d[y]["jan_oct"]["total"]; cnt = yr_d[y]["jan_oct"]["trades"]
            draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            yr_d[y]["placebo_pct"] = pct
            yr_d[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                             median=round(sorted(draws)[100], 2),
                                             max=round(max(draws), 2)) if draws else None)
            entry["years"][y] = yr_d[y]
            per_year[y] = r5.bar_check(yr_d[y], pct)
        entry["desired_bar"] = dict(per_year=per_year,
                                    reached=bool(per_year[2025]["all"] and per_year[2026]["all"]))
        results["dialed_row"] = entry
        results["desired_bar"] = entry["desired_bar"]
        print(f"DIALED: 2025 {yr_d[2025]['jan_oct']} placebo {yr_d[2025]['placebo_pct']} | "
              f"2026 {yr_d[2026]['jan_oct']} placebo {yr_d[2026]['placebo_pct']} | "
              f"NOV {yr_d['november_cf']} | BAR {entry['desired_bar']['reached']}")
    else:
        print("NO DIAL SCORED — month concentration (spec Step 2.2).")

    with open(os.path.join(WS, "ekam_intraday_stocks_r6_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r6_results.json")

if __name__ == "__main__":
    main()
