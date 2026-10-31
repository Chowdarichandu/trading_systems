"""Family (o): (lA) + partial/trail exit on the MORNING trade only. NIFTY, paper only.
Base (lA) = (k) BN-confirmed rescan morning + band re-entry, afternoon
stop-on-first-fail, to 15:05 (extended_window_sweep.scan_reentry, variant lA).
(o) replaces ONLY the morning replay with a partial replay; the re-entry
itself is plain (full 2x target, original stop), NOT partialled -- distinct
from (m), which partialled the re-entry only.

Variants, one at a time:
  o1 partial50_trailBE: trigger entry-1.0*risk, book 50, remaining stop -> BE.
  o2 partial50_noTrail: trigger entry-1.0*risk, book 50, remaining keeps orig stop.
  o3 partial25_trailBE: trigger entry-0.5*risk, book 50, remaining stop -> BE.
Accounting/order, as in partial_trail_sweep / extended_window_sweep:
100 shares split 50/50, Rs40 cost once, adverse (stop/trailed stop) checked
BEFORE favourable (partial/target) on each bar, partial+target same bar =
partial profit + remaining target profit (150*risk-40 for o1/o2, 125*risk-40 for o3).
Green = net > 0. No-trade counted separately from green throughout.

Re-entry rule, stated before results (this is the one judgement in (o)):
re-entry scan (lA) runs ONLY if the morning trade's final exit is a stop:
plain stop (no partial booked) or stop_after_partial under o2 (remaining
hits the original stop, morning net = -Rs40 scratch). If the morning exits
at target, at breakeven after a partial (o1/o3, morning net positive), or
at square-off, the day is closed -- no re-entry. Morning net and re-entry
net are reported separately per day, so the decomposition is auditable
and the no-re-entry-after-scratch alternative can be read off (day net
would then be the morning net alone on any such day).

Pass bar, same as (l)-(n): 60% green (5/8) AND Cluster 1 total positive
AND winners not collapsed (winners = 14 V5 Nifty PE target days, rescan
mornings under (lA): 12/14 green, 2 no-trade, +Rs83,380).
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import replay_pe
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import scan_reentry
QTY, COST = 100, 40.0


def replay_morning_partial(candles, start_idx, entry, stop, target, trigger_frac, trail_be):
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk",
                "exit_time": None, "exit_idx": None, "net": None, "risk": round(risk, 2)}
    plevel = entry - trigger_frac * risk
    partial_booked = False; partial_net = 0.0; partial_time = None
    cur_stop = stop; trailed = False
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if hi >= cur_stop:
            if partial_booked:
                rem = -(cur_stop - entry) * 50
                kind = "breakeven_stop_after_partial" if trailed else "stop_after_partial"
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": kind,
                        "exit_time": t, "exit_idx": j, "exit_price": cur_stop,
                        "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time, "partial_level": round(plevel, 2),
                        "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": t, "exit_idx": j, "exit_price": cur_stop,
                    "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2),
                    "partial_booked": False, "partial_time": None, "partial_level": round(plevel, 2),
                    "trailed": False}
        if not partial_booked and lo <= plevel:
            partial_booked = True; partial_time = t; partial_net = (entry - plevel) * 50
            if trail_be:
                cur_stop = entry; trailed = True
            if lo <= target:
                rem = (entry - target) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_same_bar_as_partial",
                        "exit_time": t, "exit_idx": j, "exit_price": target,
                        "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time, "partial_level": round(plevel, 2),
                        "trailed": trailed}
        if lo <= target:
            if partial_booked:
                rem = (entry - target) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_after_partial",
                        "exit_time": t, "exit_idx": j, "exit_price": target,
                        "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time, "partial_level": round(plevel, 2),
                        "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": t, "exit_idx": j, "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2),
                    "partial_booked": False, "partial_time": None, "partial_level": round(plevel, 2),
                    "trailed": False}
        if t == "15:10":
            if partial_booked:
                rem = (entry - cl) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial",
                        "exit_time": t, "exit_idx": j, "exit_price": cl,
                        "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time, "partial_level": round(plevel, 2),
                        "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": t, "exit_idx": j, "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2),
                    "partial_booked": False, "partial_time": None, "partial_level": round(plevel, 2),
                    "trailed": False}
    c = candles.iloc[-1]
    if partial_booked:
        rem = (entry - float(c["close"])) * 50
        return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial",
                "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
                "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                "partial_booked": True, "partial_time": partial_time, "partial_level": round(plevel, 2),
                "trailed": trailed}
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2),
            "partial_booked": False, "partial_time": None, "partial_level": round(plevel, 2),
            "trailed": False}


def day_o(dd, mode, day_bn, trigger_frac, trail_be):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": [], "bn_break": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None, "skipped": [], "bn_break": tr0.get("bn_break") if tr0 else None}
    cand = r["candles"]; sig_idx = r["sig_idx"]
    entry = float(cand.iloc[sig_idx + 1]["open"]); stop = float(cand.iloc[sig_idx]["high"]); risk = stop - entry
    target = entry - 2 * risk
    m = replay_morning_partial(cand, sig_idx + 1, entry, stop, target, trigger_frac, trail_be)
    m.update({"signal": cand.iloc[sig_idx]["time"], "bn_break": tr0.get("bn_break"), "orl": r["orl"],
              "plain_morning_net": tr0["net"], "plain_morning_exit": tr0["exit"]})
    if m["exit"] in ("stop", "stop_after_partial"):
        re, skipped = scan_reentry(cand, r["orl"], m["exit_idx"], risk, "lA", m["net"])
        day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
        return {"morning": m, "re": re, "day_net": day_net, "skipped": skipped, "bn_break": tr0.get("bn_break")}
    return {"morning": m, "re": None, "day_net": m["net"], "skipped": [], "bn_break": tr0.get("bn_break")}


if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02", "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    la1 = {"2026-01-09": 2295, "2026-02-06": 1120, "2026-03-30": -2055, "2026-04-02": -3730,
           "2026-05-13": -5075, "2026-06-29": 2100, "2026-07-08": 955, "2026-08-19": 1670}
    win_days = {"2026-01-21": 9280, "2026-02-24": 7350, "2026-03-16": 8940, "2026-03-13": 5400,
                "2026-03-23": 7260, "2026-04-24": 8820, "2026-05-05": 5040, "2026-07-22": 6320,
                "2026-08-12": 6250, "2026-08-27": 3000, "2026-09-29": 3790, "2026-09-07": 2990,
                "2026-10-08": 5440, "2026-10-23": 11390}
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    variants = [("o1", 1.0, True), ("o2", 1.0, False), ("o3", 0.5, True)]
    out = {}

    def summarise(rows):
        g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
        nt = sum(1 for x in rows if x["day_net"] is None)
        tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
        return g, nt, tot

    for name, frac, trail in variants:
        for label, days, modes in (("cluster1", cluster1, modes1), ("winners", list(win_days), modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                res = day_o(dd, modes.get(ds, "v4"), dbn, frac, trail) if dd and dbn else None
                rows.append({"date": ds, "la_day_net": la1.get(ds), "result": res, "day_net": res["day_net"] if res else None})
            out.setdefault(name, {})[label] = rows
            g, nt, tot = summarise(rows)
            print(f"\n=== ({name}) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                res = x["result"]
                if res is None:
                    print(x["date"], "NO DATA"); continue
                m = res["morning"]
                print(x["date"], "morning sig", m["signal"] if m else None, "entry", m["entry"] if m else None,
                      "risk", m["risk"] if m else None, "partial_level", m.get("partial_level") if m else None,
                      "partial", m.get("partial_time") if m else None, "exit", m["exit"] if m else None,
                      "exit_time", m["exit_time"] if m else None, "morning_net", m["net"] if m else None,
                      "| re", res["re"], "| day", x["day_net"], "| skipped", res["skipped"])
    with open(os.path.expanduser("~/workspace/trading/morning_partial_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
