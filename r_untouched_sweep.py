"""Family (r): untouched Cluster 1 days (30 Mar, 2 Apr) + Clusters 2/3 on their
own terms. NIFTY only, paper only, no orders, nothing fabricated.
Base (lA) = BN-confirmed rescan morning + afternoon stop-on-first-fail
re-entry scan, exactly as in extended_window_sweep (variant lA).
Variants below replace ONLY the re-entry scan (part A) or ONLY the
Cluster 2 entry confirmation (part B) or ONLY the Cluster 3 exit (part C),
one at a time. No (p) cutoff is re-run. No-trade is counted separately
from green throughout. Green = net > 0. 100 shares, Rs40/trade,
square-off 15:10, stop checked before target on each bar (PE: high>=stop
first; CE: low<=stop first).
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from close_reentry_sweep import replay_pe
from extended_window_sweep import day_variant as day_lA
from progressive_engine import load as load_prog
from daytrader_cash_backtest import find_signal, run_day, bias_of

QTY, COST = 100, 40.0

# ---------- generic plain replay (PE and CE) ----------
def replay(candles, start_idx, entry, stop, target, direction):
    risk = abs(stop - entry)
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if direction == "PE":
            if hi >= stop:
                return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
            if lo <= target:
                return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        else:
            if lo <= stop:
                return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
            if hi >= target:
                return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if t == "15:10":
            net = round((entry - cl) * QTY - COST, 2) if direction == "PE" else round((cl - entry) * QTY - COST, 2)
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": net, "risk": round(risk, 2)}
    c = candles.iloc[-1]
    net = round((entry - float(c["close"])) * QTY - COST, 2) if direction == "PE" else round((float(c["close"]) - entry) * QTY - COST, 2)
    return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1, "net": net, "risk": round(risk, 2)}

# ---------- part A: re-entry scan variants on (lA) mornings ----------
def scan_reentry_variant(candles, orl, stop_idx, rescan_risk, sig_low, morning_entry, variant, max_reentries=1):
    """candles: rescan candles (time>=09:30, reset index). Returns (list_of_re_trades, skipped).
    Trigger definitions (all PE, close-based, to 15:05, one re-entry unless max_reentries=2):
      rB band150: close<orl, band [10, 1.5*rescan_risk], scan-skip band fails
      rC siglow:  close<sig_low, band [10, rescan_risk], scan-skip
      rD entry:   close<morning_entry, band [10, rescan_risk], scan-skip
      rE runlow:  close<running intraday low (min low of bars before candidate), band [10, rescan_risk], scan-skip
      rF two:     close<orl, band [10, rescan_risk], scan-skip, up to 2 re-entries
      rH after13: close<orl, band [10, rescan_risk], scan-skip, only candidates >=13:00
      rI pair:    two consecutive closes<orl; entry after 2nd, stop=2nd bar high;
                  banded version scan-skips band fails, unbanded trades first pair
    """
    res, skipped = [], []
    start = stop_idx + 1
    running_low = None
    k = start
    # running low over bars before candidate: min low of bars from start of day to k-1
    all_lows = [float(candles.iloc[i]["low"]) for i in range(len(candles))]
    while k < len(candles):
        c = candles.iloc[k]; t = c["time"]
        if t > "15:05" or len(res) >= max_reentries:
            break
        cl, hi = float(c["close"]), float(c["high"])
        trigger = False; trig_name = ""
        if variant == "rB":
            trigger = cl < orl
        elif variant == "rC":
            trigger = cl < sig_low
        elif variant == "rD":
            trigger = cl < morning_entry
        elif variant == "rE":
            running_low = min(all_lows[:k]) if k > 0 else None
            trigger = running_low is not None and cl < running_low
        elif variant in ("rF",):
            trigger = cl < orl
        elif variant == "rH":
            trigger = t >= "13:00" and cl < orl
        elif variant in ("rI_banded", "rI_unbanded"):
            # need two consecutive closes < orl ending at k
            if k >= 1 and cl < orl and float(candles.iloc[k - 1]["close"]) < orl:
                trigger = True
            else:
                k += 1; continue
        else:
            raise ValueError(variant)
        if not trigger:
            k += 1; continue
        if k + 1 >= len(candles):
            skipped.append((t, "no_next_bar")); break
        entry = float(candles.iloc[k + 1]["open"]); stop = hi; risk = stop - entry
        band_hi = 1.5 * rescan_risk if variant == "rB" else rescan_risk
        if variant == "rI_unbanded":
            pass  # trade regardless of band (risk>0 still required)
        elif not (10 <= risk <= band_hi):
            skipped.append((t, f"band_fail_risk={risk:.2f}_band=[10,{band_hi:.2f}]"))
            k += 1; continue
        if risk <= 0:
            skipped.append((t, "invalid_risk")); k += 1; continue
        tr = replay(candles, k + 1, entry, stop, entry - 2 * risk, "PE")
        tr.update({"re_signal": t, "entry": entry, "stop": stop, "target": round(entry - 2 * risk, 2)})
        res.append(tr)
        if tr.get("exit_idx") is not None:
            k = tr["exit_idx"] + 1
        else:
            break
    return res, skipped

def day_A(dd, mode, day_bn, variant):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": [], "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": [], "day_net": None, "skipped": []}
    if tr.get("exit") != "stop":
        return {"morning": tr, "re": [], "day_net": tr["net"], "skipped": []}
    sig_low = float(r["candles"].iloc[r["sig_idx"]]["low"])
    max_re = 2 if variant == "rF" else 1
    res, skipped = scan_reentry_variant(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"],
                                        sig_low, tr["entry"], variant, max_reentries=max_re)
    if not res:
        return {"morning": tr, "re": [], "day_net": tr["net"], "skipped": skipped,
                "orl": r["orl"], "sig_low": sig_low, "sig_time": r["info"]["signal"]}
    day_net = round(tr["net"] + sum(x["net"] for x in res if x["net"] is not None), 2)
    return {"morning": tr, "re": res, "day_net": day_net, "skipped": skipped,
            "orl": r["orl"], "sig_low": sig_low, "sig_time": r["info"]["signal"]}

# ---------- part B: Cluster 2 confirmation ----------
def day_B(ds):
    spot, daily = load_prog("NIFTY")
    dl = daily.to_dict("records")
    for i, y in enumerate(dl):
        if str(y["date"])[:10] != ds:
            continue
        prev = dl[i - 1]; day_spot = spot[spot["date"] == y["date"]]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev); scale = pdc / 55000.0
        setup, dirn, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
        if setup != "setup4_reclaim":
            return {"date": ds, "note": f"not setup4_reclaim: {setup}"}
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        sig_idx = int(candles[candles["time"] == sig["time"]].index[0])
        orh = float(day_spot[day_spot["time"] < "09:30"]["high"].max())
        L = max(orh, pdc)
        orig = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40)
        out = {"date": ds, "signal": sig["time"], "sig_close": float(sig["close"]), "L": L,
               "above_L": round(float(sig["close"]) - L, 2), "orig_entry": orig["entry_price"],
               "orig_stop": orig["stop_price"], "orig_target": orig["target_price"], "orig_net": orig["net_rs"]}
        # c2-A second-close hold
        if sig_idx + 2 < len(candles):
            second = candles.iloc[sig_idx + 1]
            if float(second["close"]) > L:
                entry = float(candles.iloc[sig_idx + 2]["open"]); stop = float(second["low"]); risk = entry - stop
                tr = replay(candles, sig_idx + 2, entry, stop, entry + 2 * risk, "CE") if risk > 0 else {"exit": "invalid_risk", "net": None}
                out["c2A"] = {"second_close": float(second["close"]), "entry": entry, "stop": stop, "risk": round(risk, 2), **tr}
            else:
                out["c2A"] = {"second_close": float(second["close"]), "result": "no_trade_hold_fails"}
            # c2-E stronger hold: second close > L AND > signal close
            if float(second["close"]) > L and float(second["close"]) > float(sig["close"]):
                entry = float(candles.iloc[sig_idx + 2]["open"]); stop = float(second["low"]); risk = entry - stop
                tr = replay(candles, sig_idx + 2, entry, stop, entry + 2 * risk, "CE") if risk > 0 else {"exit": "invalid_risk", "net": None}
                out["c2E"] = {"second_close": float(second["close"]), "entry": entry, "stop": stop, "risk": round(risk, 2), **tr}
            else:
                out["c2E"] = {"second_close": float(second["close"]), "result": "no_trade_strong_hold_fails"}
        # c2-B distance filter (no-trade if signal close < L+10 / L+20; else original trade)
        for th in (10, 20):
            out[f"c2B{th}"] = "original_trade" if float(sig["close"]) >= L + th else "no_trade_distance_fails"
        return out
    return {"date": ds, "note": "not_found"}

# ---------- part C: Cluster 3 survival, reimplemented + validated vs known ----------
def replay_survival(candles, start_idx, entry, stop, target, partial_frac, gate_n, interp="B"):
    """Partial level = entry - partial_frac*risk (PE). Interpretation B (eligibility):
    if still open at gate open (bar start_idx+gate_n), and partial level already
    reached by then, book 50 at partial level immediately and trail rest to BE.
    If not yet reached, arm from gate bar onward. Original stop before partial
    on each bar; target beats trail-close (no close trails here, BE on high touch
    from next bar after partial bar, as in (o)/(p) highBE)."""
    risk = stop - entry
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None}
    plevel = entry - partial_frac * risk
    gate_idx = start_idx + gate_n
    partial_booked = False; partial_net = 0.0; partial_time = None; partial_idx = None
    # pre-gate: plain replay until gate_idx, tracking whether partial level reached
    reached_before_gate = False
    j = start_idx
    while j < min(gate_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, t = float(c["high"]), float(c["low"]), c["time"]
        if hi >= stop:
            return {"exit": "stop", "exit_time": t, "net": round(-risk * QTY - COST, 2), "partial": False}
        if lo <= target:
            return {"exit": "target", "exit_time": t, "net": round(2 * risk * QTY - COST, 2), "partial": False}
        if lo <= plevel:
            reached_before_gate = True
        if t == "15:10":
            cl = float(c["close"])
            return {"exit": "square_off", "exit_time": t, "net": round((entry - cl) * QTY - COST, 2), "partial": False}
        j += 1
    if interp == "B" and reached_before_gate:
        partial_booked = True; partial_net = partial_frac * risk * 50; partial_time = candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None
        partial_idx = gate_idx - 1  # trail starts on gate bar (next bar after the bar that reached it, conservatively)
    # from gate onward. Once partialled, the remaining 50 shares' stop IS
    # breakeven (entry) — a high >= entry exits them at 0, and a high >=
    # original stop on the same bar cannot be a larger loss than that,
    # because entry is crossed first. (Prior sweeps check cur_stop=entry.)
    for j in range(gate_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if partial_booked and hi >= entry:
            return {"exit": "breakeven_after_partial", "exit_time": t, "net": round(partial_net - COST, 2), "partial": True, "partial_time": partial_time}
        if hi >= stop:
            return {"exit": "stop", "exit_time": t, "net": round(-risk * QTY - COST, 2), "partial": partial_booked}
        if not partial_booked and lo <= plevel:
            partial_booked = True; partial_net = partial_frac * risk * 50; partial_time = t; partial_idx = j
            if lo <= target:
                return {"exit": "target_same_bar_as_partial", "exit_time": t, "net": round(partial_net + (entry - target) * 50 - COST, 2), "partial": True, "partial_time": partial_time}
        if lo <= target:
            if partial_booked:
                return {"exit": "target_after_partial", "exit_time": t, "net": round(partial_net + (entry - target) * 50 - COST, 2), "partial": True, "partial_time": partial_time}
            return {"exit": "target", "exit_time": t, "net": round(2 * risk * QTY - COST, 2), "partial": False}
        if t == "15:10":
            if partial_booked:
                return {"exit": "square_off_after_partial", "exit_time": t, "net": round(partial_net + (entry - cl) * 50 - COST, 2), "partial": True, "partial_time": partial_time}
            return {"exit": "square_off", "exit_time": t, "net": round((entry - cl) * QTY - COST, 2), "partial": False}
    c = candles.iloc[-1]; cl = float(c["close"])
    if partial_booked:
        return {"exit": "square_off_after_partial", "exit_time": c["time"], "net": round(partial_net + (entry - cl) * 50 - COST, 2), "partial": True, "partial_time": partial_time}
    return {"exit": "square_off", "exit_time": c["time"], "net": round((entry - cl) * QTY - COST, 2), "partial": False}

def day_C(ds, partial_frac, gate_n):
    spot, daily = load_prog("NIFTY")
    dl = daily.to_dict("records")
    for i, y in enumerate(dl):
        if str(y["date"])[:10] != ds:
            continue
        prev = dl[i - 1]; day_spot = spot[spot["date"] == y["date"]]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev); scale = pdc / 55000.0
        setup, dirn, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
        if dirn != "PE":
            # Skill-mode fallback (universe mode skill, e.g. 2026-03-23):
            # first close below OR low up to 11:30, same plain exit as V4.
            orl_ = float(day_spot[day_spot["time"] < "09:30"]["low"].min())
            cand = day_spot[day_spot["time"] >= "09:30"]
            sig = None
            for _, c in cand.iterrows():
                if c["time"] > "11:30":
                    break
                if float(c["close"]) < orl_:
                    sig = c; break
            if sig is None:
                return {"date": ds, "note": f"not PE: {setup} {dirn}, no skill OR breakdown"}
            setup, dirn = "skill_or_breakdown", "PE"
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        sig_idx = int(candles[candles["time"] == sig["time"]].index[0])
        entry = float(candles.iloc[sig_idx + 1]["open"]); stop = float(sig["high"]); risk = stop - entry
        if setup == "skill_or_breakdown":
            orig_net = replay(candles, sig_idx + 1, entry, stop, entry - 2 * risk, "PE")["net"]
        else:
            orig_net = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40)["net_rs"]
        tr = replay_survival(candles, sig_idx + 1, entry, stop, entry - 2 * risk, partial_frac, gate_n)
        return {"date": ds, "setup": setup, "signal": sig["time"], "entry": entry, "stop": stop,
                "risk": round(risk, 2), "orig_net": orig_net, **tr}
    return {"date": ds, "note": "not_found"}

if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02", "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    winners = ["2026-01-21", "2026-02-24", "2026-03-16", "2026-03-13", "2026-03-23", "2026-04-24", "2026-05-05", "2026-07-22", "2026-08-12", "2026-08-27", "2026-09-29", "2026-09-07", "2026-10-08", "2026-10-23"]
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    out = {}
    # (lA) baseline
    for label, days, modes in (("cluster1", cluster1, modes1), ("winners", winners, modesw)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            r = day_lA(dd, modes.get(ds, "v4"), dbn, "lA") if dd and dbn else None
            rows.append({"date": ds, "day_net": r["day_net"] if r else None,
                         "morning": (r["morning"]["signal"], r["morning"]["net"]) if r and r["morning"] else None,
                         "re": r["re"] if r else None, "skipped": r["skipped"] if r else None})
        out["lA_" + label] = rows
        g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
        nt = sum(1 for x in rows if x["day_net"] is None)
        print(f"(lA) {label}: green {g}/{len(rows)} no-trade {nt} total {sum(x['day_net'] for x in rows if x['day_net'] is not None)}")
        for x in rows: print("   ", x)
    # part A variants
    for v in ["rB", "rC", "rD", "rE", "rF", "rH", "rI_banded", "rI_unbanded"]:
        for label, days, modes in (("cluster1", cluster1, modes1), ("winners", winners, modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_A(dd, modes.get(ds, "v4"), dbn, v) if dd and dbn else None
                rows.append({"date": ds, "day_net": r["day_net"] if r else None,
                             "morning_net": r["morning"]["net"] if r and r["morning"] else None,
                             "re": r["re"] if r else None, "skipped": r["skipped"] if r else None})
            out.setdefault(v, {})[label] = rows
            g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
            nt = sum(1 for x in rows if x["day_net"] is None)
            tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
            print(f"\n=== ({v}) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows: print("   ", x)
    # part B
    out["cluster2"] = []
    for ds in ["2026-01-14", "2026-10-26", "2026-07-01"]:
        r = day_B(ds); out["cluster2"].append(r); print("\nCluster2:", r)
    # part C: validate N=10/20 against known, then N=5,15,25,30 and partial50 N=10
    c3 = ["2026-02-13", "2026-04-30", "2026-05-18"]
    for pf, gn, tag in [(0.9, 10, "surv45_N10"), (0.9, 20, "surv45_N20"), (0.9, 5, "surv45_N5"),
                        (0.9, 15, "surv45_N15"), (0.9, 25, "surv45_N25"), (0.9, 30, "surv45_N30"),
                        (1.0, 10, "surv50_N10")]:
        for label, days in (("cluster3", c3), ("winners", winners)):
            rows = []
            for ds in days:
                r = day_C(ds, pf, gn); rows.append(r)
            out.setdefault(tag, {})[label] = rows
            g = sum(1 for x in rows if x.get("net") is not None and x["net"] > 0)
            tot = sum(x["net"] for x in rows if x.get("net") is not None)
            print(f"\n=== ({tag}) {label}: green {g}/{len(rows)} total {tot} ===")
            for x in rows: print("   ", x)
    with open(os.path.expanduser("~/workspace/trading/r_untouched_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
