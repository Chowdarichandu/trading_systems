"""Family (p): morning partial whose trail is NOT breakeven-on-high, and/or
partial NOT applied blindly to every morning. NIFTY, paper only.
Base (lA): (k) BN-confirmed rescan morning + band re-entry, afternoon
stop-on-first-fail to 15:05. (p) replaces ONLY the morning replay;
re-entry, if any, is plain full trade, as in (o).

Variants, defined BEFORE results (no hindsight, no outcome-based choice):
  p1 closeBE:    partial50 at 1.0x risk; remaining trail = entry, but exit
                 ONLY on a 5-min CLOSE >= entry (PE; wick high touch alone
                 does not exit). Original stop still exits intra-bar.
  p2 closeMid:   partial50 at 1.0x; remaining trail = entry-0.5x risk,
                 exit ONLY on close >= that mid level. Locks 75x risk-40
                 on a trail exit instead of 50x risk-40.
  p3 highMid:    partial50 at 1.0x; remaining trail = entry-0.5x risk,
                 exit on intra-bar HIGH >= mid level.
  p4 time1000:   (o1) highBE, but partial booked ONLY if the partial
                 trigger bar time < 10:00; later partials are plain trades.
  p5 time0945:   as p4, cutoff < 09:45.
  p6 time1030:   as p4, cutoff < 10:30.
  p7 time1000_closeBE: p4 + p1 combined (partial <10:00, trail BE on close).
  p8 time1000_closeMid: p4 + p2 combined.
Accounting: 100 shares 50/50, Rs40 once, adverse (original stop) BEFORE
favourable (partial/target) per bar; target on a bar beats a trail-close
on the same bar (low <= target). Trail exit net: BE = 50x risk-40;
mid = 75x risk-40. Green = net > 0, no-trade separate.
Re-entry rule as in (o): re-entry scan (lA) runs ONLY if morning final
exit is a stop (plain stop, or stop_after_partial at original stop).
If morning exits at target, trail exit, or square-off, day closed.
Pass bar: Cluster 1 green >=5/8 AND Cluster 1 total positive AND
combined PE total NOT below (lA) +Rs80,660 (Cluster 1 -2720 + winners
83380). Winners = 14 V5 Nifty PE days, (lA) rescan mornings.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import replay_pe
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import scan_reentry
QTY, COST = 100, 40.0


def replay_p(candles, start_idx, entry, stop, target, trail_mode, time_cutoff):
    risk = stop - entry
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    plevel = entry - risk
    mid = entry - 0.5 * risk
    trail_level = entry if "BE" in trail_mode else mid
    close_only = trail_mode.startswith("close")
    partial_booked = False; partial_net = 0.0; partial_time = None
    partial_idx = None
    trailed = False
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        # 1. original hard stop (intra-bar high) -- before anything else
        if hi >= stop:
            if partial_booked:
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop_after_partial",
                        "exit_time": t, "exit_idx": j, "net": round(partial_net - (stop - entry) * 50 - COST, 2),
                        "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                        "partial_level": round(plevel, 2), "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "partial_level": round(plevel, 2), "trailed": False}
        # 2. partial booking (intra-bar low), unless time-gated out
        if not partial_booked and lo <= plevel:
            if time_cutoff is not None and t >= time_cutoff:
                # partial never booked on this or any later bar: plain trade
                # mark by setting a flag via partial_time sentinel: use trailed=False and
                # skip booking forever by breaking to plain replay below
                return replay_pe(candles, j, entry, stop, target) | {"partial_gated_out": True, "partial_time": None}
            partial_booked = True; partial_time = t; partial_net = (entry - plevel) * 50
            partial_idx = j
            trailed = True
            if lo <= target:
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_same_bar_as_partial",
                        "exit_time": t, "exit_idx": j, "net": round(partial_net + (entry - target) * 50 - COST, 2),
                        "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                        "partial_level": round(plevel, 2), "trailed": trailed}
        # 3. trail exit: high-touch, or close-only. High-touch trails start
        # on the NEXT bar (as in (o)): the partial bar's high may pre-date
        # the low touch within the bar. Close trails may use the partial
        # bar's own close, which is after the touch.
        if partial_booked and trailed and (close_only or j > partial_idx):
            if close_only:
                if cl >= trail_level:
                    rem = (entry - trail_level) * 50
                    kind = "breakeven_close_after_partial" if trail_level == entry else "mid_close_after_partial"
                    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": kind,
                            "exit_time": t, "exit_idx": j, "net": round(partial_net + rem - COST, 2),
                            "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                            "partial_level": round(plevel, 2), "trailed": True}
            else:
                if hi >= trail_level:
                    rem = (entry - trail_level) * 50
                    kind = "breakeven_stop_after_partial" if trail_level == entry else "mid_stop_after_partial"
                    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": kind,
                            "exit_time": t, "exit_idx": j, "net": round(partial_net + rem - COST, 2),
                            "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                            "partial_level": round(plevel, 2), "trailed": True}
        # 4. target (intra-bar low), after partial / trail checks above
        if lo <= target:
            if partial_booked:
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_after_partial",
                        "exit_time": t, "exit_idx": j, "net": round(partial_net + (entry - target) * 50 - COST, 2),
                        "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                        "partial_level": round(plevel, 2), "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "partial_level": round(plevel, 2), "trailed": False}
        if t == "15:10":
            if partial_booked:
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial",
                        "exit_time": t, "exit_idx": j, "net": round(partial_net + (entry - cl) * 50 - COST, 2),
                        "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                        "partial_level": round(plevel, 2), "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "partial_level": round(plevel, 2), "trailed": False}
    c = candles.iloc[-1]
    if partial_booked:
        return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial",
                "exit_time": c["time"], "exit_idx": len(candles) - 1,
                "net": round(partial_net + (entry - float(c["close"])) * 50 - COST, 2),
                "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time,
                "partial_level": round(plevel, 2), "trailed": trailed}
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1,
            "net": round((entry - float(c["close"])) * QTY - COST, 2),
            "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
            "partial_level": round(plevel, 2), "trailed": False}


def day_p(dd, mode, day_bn, trail_mode, time_cutoff):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None}
    cand = r["candles"]; sig_idx = r["sig_idx"]
    entry = float(cand.iloc[sig_idx + 1]["open"]); stop = float(cand.iloc[sig_idx]["high"]); risk = stop - entry
    target = entry - 2 * risk
    m = replay_p(cand, sig_idx + 1, entry, stop, target, trail_mode, time_cutoff)
    m.update({"signal": cand.iloc[sig_idx]["time"], "bn_break": tr0.get("bn_break"), "orl": r["orl"],
              "plain_morning_net": tr0["net"], "plain_morning_exit": tr0["exit"]})
    # replay_pe fallback (time-gated plain) returns a different shape; normalise
    if "exit_idx" not in m and m.get("exit_time") is not None:
        pass
    exit_idx = m.get("exit_idx")
    if m["exit"] in ("stop", "stop_after_partial") and exit_idx is not None:
        re, skipped = scan_reentry(cand, r["orl"], exit_idx, risk, "lA", m["net"])
        day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
        return {"morning": m, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": m, "re": None, "day_net": m["net"], "skipped": []}


if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02", "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    win_days = ["2026-01-21", "2026-02-24", "2026-03-16", "2026-03-13", "2026-03-23", "2026-04-24", "2026-05-05", "2026-07-22",
                "2026-08-12", "2026-08-27", "2026-09-29", "2026-09-07", "2026-10-08", "2026-10-23"]
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    variants = [("p1", "closeBE", None), ("p2", "closeMid", None), ("p3", "highMid", None),
                ("p4", "highBE", "10:00"), ("p5", "highBE", "09:45"), ("p6", "highBE", "10:30"),
                ("p7", "closeBE", "10:00"), ("p8", "closeMid", "10:00")]
    out = {}

    def summarise(rows):
        g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
        nt = sum(1 for x in rows if x["day_net"] is None)
        tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
        return g, nt, tot

    for name, trail_mode, cutoff in variants:
        for label, days, modes in (("cluster1", cluster1, modes1), ("winners", win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                res = day_p(dd, modes.get(ds, "v4"), dbn, trail_mode, cutoff) if dd and dbn else None
                rows.append({"date": ds, "result": res, "day_net": res["day_net"] if res else None})
            out.setdefault(name, {})[label] = rows
            g, nt, tot = summarise(rows)
            print(f"\n=== ({name} trail={trail_mode} cutoff={cutoff}) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                res = x["result"]
                if res is None or res["morning"] is None:
                    print(x["date"], "NOTRADE"); continue
                m = res["morning"]
                print(x["date"], "sig", m.get("signal"), "entry", m.get("entry"), "risk", m.get("risk"),
                      "partial", m.get("partial_time"), "exit", m.get("exit"), "@", m.get("exit_time"),
                      "morning_net", m.get("net"), "| re", (res["re"] or {}).get("net") if res.get("re") else None,
                      "| day", x["day_net"])
    with open(os.path.expanduser("~/workspace/trading/morning_partial_p_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
