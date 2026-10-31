"""TRIPLE backtest: V4 + Day Trader Skill + (lA), NIFTY + BANKNIFTY, Jan-Oct 2026.
Paper only, no orders. NOT adopted on this run alone. Frozen definitions from
merged_skill_la_october.py / merged_skill_la_index_october_2026.md (Skill + (lA))
plus V4 index candidates from progressive_capped_v2.candidates_for_month.
NO re-tuning of ranking, cap, filter, Bank mirror, or (lA) encoding.
Dedup same symbol+date priority: (lA) first, then V4, then Skill (priority decides
only which source survives a same-day overlap; ranking for cap is still
setup_rank -> bias_strong -> room_ratio -> prospective target, so (lA) rank 1
ties with V4 setup2 rank 1 and sits below V4 setup3/4).
Cap applied WITHIN each calendar month, as in the capped-v2 Jan-Oct precedent
and the dual Jan-Oct run, so the October slice is comparable to the dual
October merge plus V4. Month JSONs are triple_* only — this script never
writes merged_skill_la_summary_* files (the dual run owns those).
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped_v2 import candidates_for_month as v2_candidates
from progressive_capped import room_ratio
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from merged_skill_la_october import (cap_select, metrics, load_bank, day_data_bank,
                                     day_la_nifty, day_la_bank, INDEX)

QTY, COST = 100, 40.0
OUT = os.path.expanduser("~/workspace/trading/data/progressive")

def leg(trades, sym):
    return metrics([t for t in trades if t["symbol"] == sym])

def main():
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    all_skill, all_la, all_la_diag = [], [], []
    month_outs = {}
    for month in range(1, 11):
        ndays_v2, v4_all, _raw, skill_filt = v2_candidates(2026, month)
        skill_idx = [t for t in skill_filt if t["symbol"] in INDEX]
        v4_idx = [t for t in v4_all if t["symbol"] in INDEX]
        month_days = [d.date().isoformat() for d in daily_n["date"]
                      if d.year == 2026 and d.month == month]
        # Oct in cache is already 1-28 only; assert it, do not add 29 Oct.
        if month == 10:
            assert month_days[-1] == "2026-10-28" and len(month_days) == 18, month_days
        la, la_diag = [], []
        for ds in month_days:
            dd_n = day_data_nifty(spot_n, daily_n, ds)
            dbn = day_data_bn(bn_spot, bn_daily, ds)
            dd_b = day_data_bank(bank_spot, bank_daily, ds)
            rn = day_la_nifty(dd_n, dbn) if (dd_n and dbn) else {"morning": None, "re": None, "day_net": None}
            day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3]) if dd_n else None
            rb = day_la_bank(dd_b, day_nifty_tuple) if (dd_b and day_nifty_tuple) else {"morning": None, "re": None, "day_net": None}
            for sym, res, dd in (("NIFTY", rn, dd_n), ("BANKNIFTY", rb, dd_b)):
                m = res["morning"]
                la_diag.append({"date": ds, "symbol": sym, "morning": m, "re": res["re"], "day_net": res["day_net"]})
                if m is None or res["day_net"] is None:
                    continue
                bias, scale = dd[4], dd[5]
                pdh, pdc, pdl = dd[1], dd[2], dd[3]
                day_spot = dd[0]
                cand = day_spot[day_spot["time"] >= "09:30"]
                sig_row = cand[cand["time"] == m["signal"]]
                sig_close = float(sig_row.iloc[0]["close"]) if len(sig_row) else float(m["entry"])
                rr, room = room_ratio(sig_close, "PE", pdh, pdc, pdl, scale)
                morning_target_net = round(2 * float(m["risk"]) * QTY - COST, 2) if m.get("risk") else 0.0
                wk = pd.Timestamp(ds).isocalendar()
                la.append({"method": "(lA)", "symbol": sym, "date": ds, "week": f"{wk[0]}-W{wk[1]:02d}",
                           "setup": "la_pe_rescan_reentry", "direction": "PE",
                           "exit_reason": ("target" if res["day_net"] > 0 and res["re"] is None and m["exit"] == "target"
                                           else "day_green" if res["day_net"] > 0 else "day_loss"),
                           "net_rs": round(float(res["day_net"]), 2), "target_net_rs": morning_target_net,
                           "setup_rank": 1, "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                           "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                           "morning_signal": m["signal"], "morning_exit": m["exit"],
                           "morning_net": m["net"],
                           "re_signal": res["re"]["re_signal"] if res["re"] else None,
                           "re_exit": res["re"]["exit"] if res["re"] else None,
                           "re_net": res["re"]["net"] if res["re"] else None})
        skill_cap, _ = cap_select(skill_idx)
        la_cap, _ = cap_select(la)
        v4_cap, _ = cap_select(v4_idx)
        # Dual pool (for comparison, same as dual run): (lA) overwrites Skill
        dual_pool = {}
        for t in skill_idx:
            dual_pool[(t["symbol"], t["date"])] = t
        for t in la:
            dual_pool[(t["symbol"], t["date"])] = t
        dual_cap, _ = cap_select(list(dual_pool.values()))
        # Triple pool: priority (lA) > V4 > Skill on same symbol+date
        pool = {}
        for t in skill_idx:
            pool[(t["symbol"], t["date"])] = t
        for t in v4_idx:
            pool[(t["symbol"], t["date"])] = t
        for t in la:
            pool[(t["symbol"], t["date"])] = t
        # Overlap accounting (before cap, on the pooled candidate sets)
        overlaps = []
        all_keys = set()
        for src, cands in (("Skill", skill_idx), ("V4", v4_idx), ("(lA)", la)):
            for t in cands:
                all_keys.add((t["symbol"], t["date"]))
        for (sym, ds) in sorted(all_keys):
            present = {}
            for src, cands in (("Skill", skill_idx), ("V4", v4_idx), ("(lA)", la)):
                hit = [t for t in cands if t["symbol"] == sym and t["date"] == ds]
                if hit:
                    present[src] = hit[0]
            if len(present) > 1:
                winner = "(lA)" if "(lA)" in present else "V4" if "V4" in present else "Skill"
                overlaps.append({"symbol": sym, "date": ds, "sources": sorted(present),
                                 "winner": winner,
                                 "nets": {k: v["net_rs"] for k, v in present.items()},
                                 "setups": {k: v.get("setup") for k, v in present.items()}})
        merged_cap, merged_ranked = cap_select(list(pool.values()))
        out = {"year": 2026, "month": month, "days": len(month_days),
               "skill_index_candidates": skill_idx, "v4_index_candidates": v4_idx,
               "la_candidates": la, "la_diag": la_diag, "overlaps": overlaps,
               "skill_capped": metrics(skill_cap), "skill_capped_trades": skill_cap,
               "skill_nifty": leg(skill_cap, "NIFTY"), "skill_banknifty": leg(skill_cap, "BANKNIFTY"),
               "la_capped": metrics(la_cap), "la_capped_trades": la_cap,
               "la_nifty": leg(la_cap, "NIFTY"), "la_banknifty": leg(la_cap, "BANKNIFTY"),
               "v4_capped": metrics(v4_cap), "v4_capped_trades": v4_cap,
               "v4_nifty": leg(v4_cap, "NIFTY"), "v4_banknifty": leg(v4_cap, "BANKNIFTY"),
               "dual_capped": metrics(dual_cap), "dual_capped_trades": dual_cap,
               "dual_nifty": leg(dual_cap, "NIFTY"), "dual_banknifty": leg(dual_cap, "BANKNIFTY"),
               "merged_capped": metrics(merged_cap), "merged_capped_trades": merged_cap,
               "merged_nifty": leg(merged_cap, "NIFTY"), "merged_banknifty": leg(merged_cap, "BANKNIFTY"),
               "merged_ranked_pool": merged_ranked}
        month_outs[month] = out
        all_skill += skill_cap; all_la += la_cap
        with open(f"{OUT}/triple_v4_skill_la_summary_2026-{month:02d}.json", "w") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"MONTH {month:02d} days={len(month_days)} v4_cand={len(v4_idx)} skill_cand={len(skill_idx)} la_cand={len(la)} "
              f"v4_cap={out['v4_capped']} skill_cap={out['skill_capped']} la_cap={out['la_capped']} "
              f"dual={out['dual_capped']} triple={out['merged_capped']} overlaps={len(overlaps)}", flush=True)
    # Jan-Oct totals = sum of per-month capped sets (same convention as capped-v2 Jan-Oct).
    merged_all = []
    for m in range(1, 11):
        merged_all += month_outs[m]["merged_capped_trades"]
    skill_all = []
    for m in range(1, 11):
        skill_all += month_outs[m]["skill_capped_trades"]
    la_all = []
    for m in range(1, 11):
        la_all += month_outs[m]["la_capped_trades"]
    v4_all = []
    for m in range(1, 11):
        v4_all += month_outs[m]["v4_capped_trades"]
    dual_all = []
    for m in range(1, 11):
        dual_all += month_outs[m]["dual_capped_trades"]
    all_overlaps = []
    for m in range(1, 11):
        all_overlaps += month_outs[m]["overlaps"]
    agg = {"year": 2026, "months": "2026-01 to 2026-10 (Oct 1-28 only)", "days": 203,
           "skill_capped": metrics(skill_all), "skill_capped_trades": skill_all,
           "skill_nifty": leg(skill_all, "NIFTY"), "skill_banknifty": leg(skill_all, "BANKNIFTY"),
           "la_capped": metrics(la_all), "la_capped_trades": la_all,
           "la_nifty": leg(la_all, "NIFTY"), "la_banknifty": leg(la_all, "BANKNIFTY"),
           "v4_capped": metrics(v4_all), "v4_capped_trades": v4_all,
           "v4_nifty": leg(v4_all, "NIFTY"), "v4_banknifty": leg(v4_all, "BANKNIFTY"),
           "dual_capped": metrics(dual_all), "dual_capped_trades": dual_all,
           "dual_nifty": leg(dual_all, "NIFTY"), "dual_banknifty": leg(dual_all, "BANKNIFTY"),
           "merged_capped": metrics(merged_all), "merged_capped_trades": merged_all,
           "merged_nifty": leg(merged_all, "NIFTY"), "merged_banknifty": leg(merged_all, "BANKNIFTY"),
           "overlaps": all_overlaps,
           "by_month": {f"2026-{m:02d}": {"skill": month_outs[m]["skill_capped"],
                                          "la": month_outs[m]["la_capped"],
                                          "v4": month_outs[m]["v4_capped"],
                                          "dual": month_outs[m]["dual_capped"],
                                          "merged": month_outs[m]["merged_capped"],
                                          "skill_nifty": month_outs[m]["skill_nifty"],
                                          "skill_banknifty": month_outs[m]["skill_banknifty"],
                                          "la_nifty": month_outs[m]["la_nifty"],
                                          "la_banknifty": month_outs[m]["la_banknifty"],
                                          "v4_nifty": month_outs[m]["v4_nifty"],
                                          "v4_banknifty": month_outs[m]["v4_banknifty"],
                                          "dual_nifty": month_outs[m]["dual_nifty"],
                                          "dual_banknifty": month_outs[m]["dual_banknifty"],
                                          "merged_nifty": month_outs[m]["merged_nifty"],
                                          "merged_banknifty": month_outs[m]["merged_banknifty"]}
                         for m in range(1, 11)}}
    with open(f"{OUT}/triple_v4_skill_la_summary_2026-jan-oct.json", "w") as f:
        json.dump(agg, f, indent=2, default=str)
    print("=== JAN-OCT V4 ===", agg["v4_capped"], agg["v4_nifty"], agg["v4_banknifty"])
    print("=== JAN-OCT SKILL ===", agg["skill_capped"], agg["skill_nifty"], agg["skill_banknifty"])
    print("=== JAN-OCT (lA) ===", agg["la_capped"], agg["la_nifty"], agg["la_banknifty"])
    print("=== JAN-OCT DUAL ===", agg["dual_capped"], agg["dual_nifty"], agg["dual_banknifty"])
    print("=== JAN-OCT TRIPLE ===", agg["merged_capped"], agg["merged_nifty"], agg["merged_banknifty"])
    print(f"=== OVERLAPS total {len(all_overlaps)} ===")
    for o in all_overlaps:
        print("OV", o["date"], o["symbol"], o["sources"], "winner", o["winner"], o["nets"], o["setups"])
    # October checks: dual slice must match dual October merge; triple October is new
    oct_m = month_outs[10]["merged_capped_trades"]
    print("OCT triple trades:", sorted([(t['date'], t['symbol'], t['method'], t['net_rs']) for t in oct_m]))
    print("OCT triple metrics:", month_outs[10]["merged_capped"])
    print("OCT dual metrics:", month_outs[10]["dual_capped"], "expected 6 trades 4 green +46975")
    print("OCT v4 metrics:", month_outs[10]["v4_capped"], "expected 7 trades +51825")
    print("OCT overlaps:", month_outs[10]["overlaps"])
    # Re-entry legs Jan-Oct
    re_fired = []
    for m in range(1, 11):
        for t in month_outs[m]["la_candidates"]:
            if t["re_signal"] is not None:
                re_fired.append(t)
    print(f"RE-ENTRY legs fired (all (lA) candidates, before cap): {len(re_fired)}")
    for t in re_fired:
        print("RE", t["date"], t["symbol"], t["morning_exit"], t["morning_net"], "re", t["re_signal"], t["re_exit"], t["re_net"], "day", t["net_rs"])

if __name__ == "__main__":
    main()
