"""Merged backtest extension: Day Trader Skill + (lA), NIFTY + BANKNIFTY, Jan-Oct 2026.
Paper only, no orders. EXACT frozen merged definition from merged_skill_la_october.py /
merged_skill_la_index_october_2026.md — NO re-tuning of ranking, cap, filter, Bank mirror,
or (lA) encoding. Only change vs October script: the month loop (Jan-Oct 2026, Oct = 1-28
only, as in cache) and cap applied WITHIN each calendar month, exactly as the capped-v2
Jan-Oct precedent (run_v2_month per month) and as the October merge did within October.
That per-month cap is what makes the October slice of this run identical to the standalone
October merge (a pooled Jan-Oct cap would let Sep 28-30, ISO W40, displace Oct 1 trades).
No bug fix was needed; October must reproduce exactly (checked in output).
Month JSONs use the same schema as merged_skill_la_summary_2026-10.json.
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
        ndays_v2, _v4, _raw, skill_filt = v2_candidates(2026, month)
        skill_idx = [t for t in skill_filt if t["symbol"] in INDEX]
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
        pool = {}
        for t in skill_idx:
            pool[(t["symbol"], t["date"])] = t
        for t in la:
            pool[(t["symbol"], t["date"])] = t
        merged_cap, merged_ranked = cap_select(list(pool.values()))
        out = {"year": 2026, "month": month, "days": len(month_days),
               "skill_index_candidates": skill_idx, "la_candidates": la, "la_diag": la_diag,
               "skill_capped": metrics(skill_cap), "skill_capped_trades": skill_cap,
               "skill_nifty": leg(skill_cap, "NIFTY"), "skill_banknifty": leg(skill_cap, "BANKNIFTY"),
               "la_capped": metrics(la_cap), "la_capped_trades": la_cap,
               "la_nifty": leg(la_cap, "NIFTY"), "la_banknifty": leg(la_cap, "BANKNIFTY"),
               "merged_capped": metrics(merged_cap), "merged_capped_trades": merged_cap,
               "merged_nifty": leg(merged_cap, "NIFTY"), "merged_banknifty": leg(merged_cap, "BANKNIFTY"),
               "merged_ranked_pool": merged_ranked}
        month_outs[month] = out
        all_skill += skill_cap; all_la += la_cap
        # merged capped trades accumulated separately below (per-month capped sets)
        with open(f"{OUT}/merged_skill_la_summary_2026-{month:02d}.json", "w") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"MONTH {month:02d} days={len(month_days)} skill_cand={len(skill_idx)} la_cand={len(la)} "
              f"skill_cap={out['skill_capped']} la_cap={out['la_capped']} merged={out['merged_capped']}", flush=True)
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
    agg = {"year": 2026, "months": "2026-01 to 2026-10 (Oct 1-28 only)", "days": 203,
           "skill_capped": metrics(skill_all), "skill_capped_trades": skill_all,
           "skill_nifty": leg(skill_all, "NIFTY"), "skill_banknifty": leg(skill_all, "BANKNIFTY"),
           "la_capped": metrics(la_all), "la_capped_trades": la_all,
           "la_nifty": leg(la_all, "NIFTY"), "la_banknifty": leg(la_all, "BANKNIFTY"),
           "merged_capped": metrics(merged_all), "merged_capped_trades": merged_all,
           "merged_nifty": leg(merged_all, "NIFTY"), "merged_banknifty": leg(merged_all, "BANKNIFTY"),
           "by_month": {f"2026-{m:02d}": {"skill": month_outs[m]["skill_capped"],
                                          "la": month_outs[m]["la_capped"],
                                          "merged": month_outs[m]["merged_capped"],
                                          "skill_nifty": month_outs[m]["skill_nifty"],
                                          "skill_banknifty": month_outs[m]["skill_banknifty"],
                                          "la_nifty": month_outs[m]["la_nifty"],
                                          "la_banknifty": month_outs[m]["la_banknifty"],
                                          "merged_nifty": month_outs[m]["merged_nifty"],
                                          "merged_banknifty": month_outs[m]["merged_banknifty"]}
                         for m in range(1, 11)}}
    with open(f"{OUT}/merged_skill_la_summary_2026-jan-oct.json", "w") as f:
        json.dump(agg, f, indent=2, default=str)
    print("=== JAN-OCT SKILL ===", agg["skill_capped"], agg["skill_nifty"], agg["skill_banknifty"])
    print("=== JAN-OCT (lA) ===", agg["la_capped"], agg["la_nifty"], agg["la_banknifty"])
    print("=== JAN-OCT MERGED ===", agg["merged_capped"], agg["merged_nifty"], agg["merged_banknifty"])
    # October reproduction check against the frozen October reference
    oct_m = month_outs[10]["merged_capped_trades"]
    print("OCT merged trades:", sorted([(t['date'], t['symbol'], t['method'], t['net_rs']) for t in oct_m]))
    print("OCT merged metrics:", month_outs[10]["merged_capped"], "expected 6 trades 4 green +46975")
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
