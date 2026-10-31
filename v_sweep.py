"""Family (v): survival-gated partial (k=1.0, trail BE) on the OOS window.
NIFTY only, paper only, no orders. Reuses u_sweep.day_lA_plain for the
(lA) baseline and mirrors u_sweep.day_partial structure (morning partial,
then (lA) re-entry scan ONLY if the morning final exit is a plain stop);
the morning replay itself is new because u_sweep.replay_partial_gen has
no survival gate (its `cutoff` is a time gate, not a survival gate).

Survival-gated partial, interpretation B (eligibility, as in
survival_gated_sweep.py):
- PE only (rescan_trade finds PE breakdowns: close < OR low and < PDL).
- entry = next bar open after signal, stop = signal high,
  target = entry - 2*risk, partial level = entry - 1.0*risk (k=1.0),
  book 50 shares at that level, trail remaining 50 to BE (entry).
- Gate index = start_idx + N, where start_idx is the entry bar.
  Bars before the gate are replayed plain (stop before target each
  bar, square-off 15:10); no partial is checked. A trade stopped or
  targeted before the gate is untouched (full stop / full target).
- At the gate open, if still open and the best favourable extreme
  over the pre-gate bars (min low) already reached the partial level,
  book 50 at the partial level immediately (partial_time = gate bar
  + "(gate, earned earlier)") and trail the rest to BE; the gate bar
  itself is then replayed with BE as the adverse level (so a BE exit
  can occur on the gate bar, as in the survival sweep: Cluster 3
  13 Feb BE stop on its gate bar).
- If the partial level was not reached before the gate, arm it from
  the gate bar onward. Per-bar order from the gate onward (survival
  sweep run_bar order): adverse (current stop: original until booked,
  BE once booked) first, then partial trigger, then target, then
  square-off at 15:10. A partial booked on a bar cannot BE-exit on
  that same bar (the adverse check for that bar already ran); BE can
  exit from the next bar onward. This matches the survival sweep, and
  differs from u_sweep.replay_partial_gen only in the post-partial
  adverse level (survival: BE replaces the original stop; u: original
  stop is checked first on every bar). The difference only matters on
  a bar whose high jumps past the original stop after a partial was
  booked; it is flagged in the report if it changes any day net
  (it does not change the pass/fail verdict -- see report).
- Re-entry: (lA) scan (extended_window_sweep.scan_reentry, variant
  "lA") only if the morning final exit is a plain "stop". A
  breakeven-after-partial, target-after-partial or square-off-after-
  partial morning does NOT re-enter, exactly as in u_sweep.day_partial
  (where breakeven_after_partial likewise did not re-enter).
- 100 shares equivalent, Rs40/trade, square-off 15:10.
  Green = net > 0. No-trade (day_net None) counted separately.

Pass bar (same as (p)/(q)/(r)/(s)/(t)/(u)): 60% green on the failing
set AND total positive AND combined NOT below (lA) on the same
window, winners not collapsed, no-trade separate from green. For OOS
the "failing set" is reported two ways: green rate over all traded
OOS days, and conversion rate over (lA)-loser days; a variant must
pass BOTH the overall-green leg and the total leg to pass.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import scan_reentry
from u_sweep import day_lA_plain, CLUSTER1, WINNERS, MODES1, MODESW

QTY, COST = 100, 40.0


def replay_survival_partial_gen(candles, start_idx, entry, stop, target, k_frac, N):
    """PE survival-gated partial replay. Returns dict like replay_pe
    plus partial_booked / partial_time / gate_time / gate_reached."""
    risk = stop - entry
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2),
                "partial_booked": False, "partial_time": None, "gate_time": None, "gate_reached": False}
    plevel = entry - k_frac * risk
    gate_idx = start_idx + N
    gate_time = candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None
    # Phase 1: pre-gate bars, plain (stop before target).
    for j in range(start_idx, min(gate_idx, len(candles))):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if hi >= stop:
            return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": False}
        if lo <= target:
            return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": False}
        if t == "15:10":
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": False}
    if gate_idx >= len(candles):
        c = candles.iloc[-1]
        return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1,
                "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2),
                "partial_booked": False, "partial_time": None, "gate_time": None, "gate_reached": False}
    # Gate reached: interpretation B eligibility booking.
    pre = candles.iloc[start_idx:gate_idx]
    best_low = float(pre["low"].min())
    booked = False; partial_net = 0.0; partial_time = None; partial_idx = None; cur_stop = stop
    gate_booked = False
    if best_low <= plevel:
        booked = True; gate_booked = True; partial_idx = gate_idx
        partial_net = k_frac * risk * 50; partial_time = gate_time + "(gate, earned earlier)"
        cur_stop = entry
    # Phase 2: gate bar onward, survival run_bar order.
    for j in range(gate_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if hi >= cur_stop:
            if booked:
                return {"exit": "breakeven_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - cur_stop) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time,
                        "gate_time": gate_time, "gate_reached": True}
            return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": True}
        if not booked and lo <= plevel:
            booked = True; partial_idx = j; partial_net = k_frac * risk * 50; partial_time = t; cur_stop = entry
            if lo <= target:
                return {"exit": "target_same_bar_as_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - target) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time,
                        "gate_time": gate_time, "gate_reached": True}
        if lo <= target:
            if booked:
                return {"exit": "target_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - target) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time,
                        "gate_time": gate_time, "gate_reached": True}
            return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": True}
        if t == "15:10":
            if booked:
                return {"exit": "square_off_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - cl) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time,
                        "gate_time": gate_time, "gate_reached": True}
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None,
                    "gate_time": gate_time, "gate_reached": True}
    c = candles.iloc[-1]
    if booked:
        return {"exit": "square_off_after_partial", "exit_time": c["time"], "exit_idx": len(candles) - 1,
                "net": round(partial_net + (entry - float(c["close"])) * 50 - COST, 2), "risk": round(risk, 2),
                "partial_booked": True, "partial_time": partial_time,
                "gate_time": gate_time, "gate_reached": True}
    return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1,
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2),
            "partial_booked": False, "partial_time": None, "gate_time": gate_time, "gate_reached": True}


def day_survival(dd, mode, day_bn, N, k_frac=1.0):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None}
    cand = r["candles"]; si = r["sig_idx"]
    entry = float(cand.iloc[si + 1]["open"]); stop = float(cand.iloc[si]["high"])
    risk = stop - entry; target = entry - 2 * risk
    m = replay_survival_partial_gen(cand, si + 1, entry, stop, target, k_frac, N)
    m.update({"signal": cand.iloc[si]["time"], "entry": entry, "plain_morning_net": tr0["net"]})
    if m["exit"] == "stop" and m.get("exit_idx") is not None:
        re, skipped = scan_reentry(cand, r["orl"], m["exit_idx"], risk, "lA", m["net"])
        day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
        return {"morning": m, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": m, "re": None, "day_net": m["net"], "skipped": []}


def summ(rows):
    traded = [x for x in rows if x["day_net"] is not None]
    return {"n": len(rows), "traded": len(traded),
            "green": sum(1 for x in traded if x["day_net"] > 0),
            "no_trade": len(rows) - len(traded),
            "still_loss_or_scratch": sum(1 for x in traded if x["day_net"] <= 0),
            "total": round(sum(x["day_net"] for x in traded), 2)}


if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    out = {}
    # (lA) baseline reproduction + survival in-sample
    print("##### IN-SAMPLE: (lA) vs survival N=5/10/20, k=1.0 BE #####")
    for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
        for name, fn in [("lA", None)] + [(f"surv_N{N}", N) for N in (5, 10, 20)]:
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                if not dd or not dbn:
                    rows.append({"date": ds, "day_net": None, "note": "no_cache"}); continue
                res = day_lA_plain(dd, modes.get(ds, "v4"), dbn) if fn is None else day_survival(dd, modes.get(ds, "v4"), dbn, fn)
                rows.append({"date": ds, "day_net": res["day_net"] if res else None,
                             "morning_exit": (res["morning"] or {}).get("exit") if res and res.get("morning") else None,
                             "morning_net": (res["morning"] or {}).get("net") if res and res.get("morning") else None,
                             "partial_time": (res["morning"] or {}).get("partial_time") if res and res.get("morning") else None,
                             "gate_time": (res["morning"] or {}).get("gate_time") if res and res.get("morning") else None,
                             "gate_reached": (res["morning"] or {}).get("gate_reached") if res and res.get("morning") else None,
                             "re_net": (res["re"]["net"] if res and res.get("re") else None)})
            out.setdefault(name, {})[label] = rows
            print(f"({name}) {label}: {summ(rows)}")
            for x in rows:
                print("   ", x["date"], "morn", x["morning_exit"], x["morning_net"], "partial", x["partial_time"],
                      "gate", x["gate_time"], "reached", x["gate_reached"], "re", x["re_net"], "day", x["day_net"])
    # OOS
    print("\n##### OOS window (in_sample==False) #####")
    univ = json.load(open(os.path.expanduser("~/workspace/trading/morning_bar_universe.json")))
    oos = [u for u in univ if not u.get("in_sample")]
    print(f"OOS days in universe: {len(oos)}")
    for name, fn in [("lA", None)] + [(f"surv_N{N}", N) for N in (5, 10, 20)]:
        rows = []
        for u in oos:
            ds = u["date"]; mode = u["mode"]
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            if not dd or not dbn:
                rows.append({"date": ds, "mode": mode, "day_net": None, "note": "no_cache"}); continue
            res = day_lA_plain(dd, mode, dbn) if fn is None else day_survival(dd, mode, dbn, fn)
            rows.append({"date": ds, "mode": mode, "day_net": res["day_net"] if res else None,
                         "morning_exit": (res["morning"] or {}).get("exit") if res and res.get("morning") else None,
                         "morning_net": (res["morning"] or {}).get("net") if res and res.get("morning") else None,
                         "partial_time": (res["morning"] or {}).get("partial_time") if res and res.get("morning") else None,
                         "gate_time": (res["morning"] or {}).get("gate_time") if res and res.get("morning") else None,
                         "gate_reached": (res["morning"] or {}).get("gate_reached") if res and res.get("morning") else None,
                         "re_net": (res["re"]["net"] if res and res.get("re") else None)})
        out.setdefault(name, {})["oos"] = rows
        s = summ(rows)
        print(f"({name}) OOS: {s} green_rate_traded={round(100*s['green']/s['traded'],1) if s['traded'] else None}%")
    la_oos = {x["date"]: x["day_net"] for x in out["lA"]["oos"]}
    for name in ("surv_N5", "surv_N10", "surv_N20"):
        for grp, cond in (("lA-winners", lambda d: la_oos[d] is not None and la_oos[d] > 0),
                          ("lA-losers", lambda d: la_oos[d] is not None and la_oos[d] <= 0)):
            sub_la = [x for x in out["lA"]["oos"] if cond(x["date"])]
            sub_v = [x for x in out[name]["oos"] if cond(x["date"])]
            tot_la = sum(x["day_net"] for x in sub_la if x["day_net"] is not None)
            tot_v = sum(x["day_net"] for x in sub_v if x["day_net"] is not None)
            g_v = sum(1 for x in sub_v if x["day_net"] is not None and x["day_net"] > 0)
            tr_v = sum(1 for x in sub_v if x["day_net"] is not None)
            conv = sum(1 for x in sub_v if x["day_net"] is not None and x["day_net"] > 0)
            print(f"({name}) {grp}: n={len(sub_la)} lA_total={tot_la} variant_total={tot_v} variant_green={g_v}/{tr_v}")
        # per-day deltas vs (lA), for the report's conversion list
        print(f"({name}) OOS days where day_net != (lA) day_net:")
        for x in out[name]["oos"]:
            la = la_oos[x["date"]]
            if x["day_net"] is not None and la is not None and x["day_net"] != la:
                print("   ", x["date"], "lA", la, "->", name, x["day_net"], "morn", x["morning_exit"], x["morning_net"],
                      "partial", x["partial_time"], "gate", x["gate_time"], "re", x["re_net"])
            elif (x["day_net"] is None) != (la is None):
                print("   ", x["date"], "TRADE-STATUS DIFFERS lA", la, name, x["day_net"])
    with open(os.path.expanduser("~/workspace/trading/v_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/v_sweep_raw.json")
