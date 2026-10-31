"""Family (q): out-of-sample validation of (p) passing variants, FROZEN.
NIFTY only, paper only. Cutoffs frozen: p5 <09:45 highBE, p4 <10:00 highBE,
p8 <10:00 closeMid. NO re-tuning on the OOS window.
OOS window: morning_bar_universe.json in_sample==False, 92 PE days
(65 in 2025, 27 in 2026, none in Cluster 1 / winners in-sample set).
(lA) baseline on same window = (k) BN-confirmed rescan morning (plain)
+ (lA) re-entry scan after a morning stop, exactly as day_p's re-entry
logic but with the plain morning. (p) variants use day_p() unchanged.
Pass bar translated to a unified OOS window (no Cluster1/winner split
exists here): green rate >=60% of TRADED days AND total positive AND
total NOT below (lA) total on same window AND (lA)-winner total not
collapsed (winner = day green under (lA); loser = day <=0 under (lA),
traded days only). No-trade counted separately from green throughout.
November 2026 paper spec is prepared separately, NOT run here:
November has not happened, no November results are claimed.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import scan_reentry
from morning_partial_p_sweep import day_p

def day_lA(dd, mode, day_bn):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None}
    if tr["exit"] == "stop" and tr.get("exit_idx") is not None:
        re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], "lA", tr["net"])
        day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
        return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}

def summarise(rows):
    traded = [x for x in rows if x["day_net"] is not None]
    g = sum(1 for x in traded if x["day_net"] > 0)
    nt = len(rows) - len(traded)
    tot = sum(x["day_net"] for x in traded)
    return {"n": len(rows), "traded": len(traded), "green": g,
            "green_rate_traded": round(100*g/len(traded), 1) if traded else None,
            "no_trade": nt, "total": round(tot, 2)}

if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    univ = json.load(open(os.path.expanduser("~/workspace/trading/morning_bar_universe.json")))
    oos = [u for u in univ if not u.get("in_sample")]
    print(f"OOS days: {len(oos)}")
    variants = [("lA", None, None), ("p5", "highBE", "09:45"), ("p4", "highBE", "10:00"), ("p8", "closeMid", "10:00")]
    out = {}
    for name, trail_mode, cutoff in variants:
        rows = []
        for u in oos:
            ds = u["date"]; mode = u["mode"]
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            if not dd or not dbn:
                rows.append({"date": ds, "mode": mode, "universe_net": u["net"], "result": None, "day_net": None, "note": "no_cache"})
                continue
            res = day_lA(dd, mode, dbn) if name == "lA" else day_p(dd, mode, dbn, trail_mode, cutoff)
            m = res.get("morning") if res else None
            rows.append({"date": ds, "mode": mode, "universe_net": u["net"],
                         "signal": m.get("signal") if m else None,
                         "morning_exit": m.get("exit") if m else None,
                         "morning_net": m.get("net") if m else None,
                         "partial_time": m.get("partial_time") if m else None,
                         "re_net": (res["re"]["net"] if res.get("re") else None),
                         "day_net": res["day_net"] if res else None})
        out[name] = rows
        s = summarise(rows)
        print(f"\n=== ({name} trail={trail_mode} cutoff={cutoff}) {s} ===")
        for x in rows:
            print(x["date"], x["mode"], "sig", x["signal"], "morning", x["morning_exit"], x["morning_net"],
                  "partial", x["partial_time"], "re", x["re_net"], "day", x["day_net"])
    # winner/loser split under (lA), applied to (p) variants
    la = {x["date"]: x["day_net"] for x in out["lA"]}
    for name in ("p5", "p4", "p8"):
        for grp, cond in (("lA-winners", lambda d: la[d] is not None and la[d] > 0),
                          ("lA-losers", lambda d: la[d] is not None and la[d] <= 0)):
            sub_la = [x for x in out["lA"] if cond(x["date"])]
            sub_p = [x for x in out[name] if cond(x["date"])]
            tot_la = sum(x["day_net"] for x in sub_la if x["day_net"] is not None)
            tot_p = sum(x["day_net"] for x in sub_p if x["day_net"] is not None)
            g_p = sum(1 for x in sub_p if x["day_net"] is not None and x["day_net"] > 0)
            tr_p = sum(1 for x in sub_p if x["day_net"] is not None)
            print(f"({name}) {grp}: n={len(sub_la)} lA_total={tot_la} p_total={tot_p} p_green={g_p}/{tr_p}")
    with open(os.path.expanduser("~/workspace/trading/q_outofsample_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
