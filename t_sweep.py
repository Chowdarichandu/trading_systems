"""Family (t): bounce-bar-aware stops + morning-bar structure beyond thinness
+ NEW Cluster 2 ideas (not a stronger hold). NIFTY only, paper only, no orders.
Pass bar: 60% green ON THE FAILING SET and total positive and combined NOT
below (lA) on the same window, winners not collapsed. No-trade separate from
green throughout; a filter can only avoid, never convert. 100 shares, Rs40,
square-off 15:10, stop before target per bar except where a variant states
otherwise (t5 close-stop, t1/t3/t4 armed bars).

Part 1 base: (lA) BN-confirmed rescan morning (combined_confirm_sweep).
Morning entry = open of bar after signal, stop = signal high (PE),
target = entry - 2*risk. Bounce bar = entry bar (bar after signal).
If a variant morning stops, (lA) re-entry scan runs (extended_window_sweep
scan_reentry, variant lA, band cap = VARIANT risk, stated up front).
If variant morning does not stop, day closes (no re-entry), as in (lA).
Variants, defined before results:
  t1 arm1: stop ignored on entry bar only; same stop/target after.
  t2 bounce-high: stop = entry-bar high, target recomputed entry-2*new_risk,
       stop arms from bar AFTER entry bar (else it would stop on entry bar
       itself by construction). New risk stated per day.
  t3 arm2: stop ignored on entry bar AND next bar; same stop/target after.
  t4 arm2-bounce-high: stop = entry-bar high, target recomputed, stop arms
       from 2 bars after entry bar.
  t5 close-stop: stop checked ONLY on 5-min CLOSE >= stop (exit at close,
       so loss can exceed original risk); target checked intra-bar first
       on each bar (as in close-trail families), square-off 15:10.
  t6 bounce-high-target-kept: stop = entry-bar high, target KEPT at original
       target (diagnostic: isolates widening from farther target).
t2/t4/t6 are NOT +10/+20 buffers and NOT OR-high stop: the new stop is
exactly the bounce (entry) bar's high, a bar-specific extreme.
Part 2: morning-bar features for (lA) Cluster 1 + winners, and pure
no-trade filters from them (gap, below-PDL, OR width/scale, combinations).
Part 3: Cluster 2 reclaim, 2026 fitted + 2025 held-out (same set that
discarded c2-A). New ideas only: BN cross-confirmation, time box,
risk cap (no-trade), risk-size scaling, stop = reclaimed level L,
retest-of-L entry. No second-close hold variant is re-run.
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import day_variant as day_lA, scan_reentry
from progressive_engine import load as load_prog
from daytrader_cash_backtest import find_signal, run_day, bias_of

QTY, COST = 100, 40.0
CLUSTER1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
WINNERS = ["2026-01-21","2026-02-24","2026-03-16","2026-03-13","2026-03-23","2026-04-24","2026-05-05","2026-07-22","2026-08-12","2026-08-27","2026-09-29","2026-09-07","2026-10-08","2026-10-23"]
MODES1 = {"2026-04-02": "skill"}; MODESW = {"2026-03-23": "skill"}

def replay_variant(candles, start_idx, entry, stop, target, variant):
    """PE replay. start_idx = entry-bar index. Returns trade dict with exit_idx."""
    risk = stop - entry
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None}
    entrybar_high = float(candles.iloc[start_idx]["high"])
    if variant in ("t2", "t4", "t6"):
        stop2 = entrybar_high; risk2 = stop2 - entry
        target2 = entry - 2 * risk2 if variant in ("t2", "t4") else target
        if risk2 <= 0:
            return {"exit": "invalid_risk", "net": None}
    else:
        stop2, risk2, target2 = stop, risk, target
    arm_until = start_idx if variant in ("t1", "t2") else (start_idx + 1 if variant in ("t3", "t4") else -1)
    # t6 arms entry bar like t2 (stop = its high); t1/t2 arm entry bar only.
    if variant == "t6":
        arm_until = start_idx
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        armed = j > arm_until
        if variant == "t5":
            if lo <= target2:
                return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk2 * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}
            if cl >= stop2:
                return {"exit": "stop_on_close", "exit_time": t, "exit_idx": j, "exit_price": cl, "net": round(-(cl - entry) * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}
        else:
            if armed and hi >= stop2:
                return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk2 * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}
            if lo <= target2:
                return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk2 * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}
        if t == "15:10":
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}
    c = candles.iloc[-1]
    return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1, "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk2, 2), "stop": round(stop2, 2), "target": round(target2, 2)}

def day_t(dd, mode, day_bn, variant):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None, "skipped": []}
    cand = r["candles"]; sig_idx = r["sig_idx"]
    entry = float(cand.iloc[sig_idx + 1]["open"]); stop = float(cand.iloc[sig_idx]["high"]); risk = stop - entry; target = entry - 2 * risk
    entrybar = cand.iloc[sig_idx + 1]
    m = replay_variant(cand, sig_idx + 1, entry, stop, target, variant)
    m.update({"signal": cand.iloc[sig_idx]["time"], "entry": entry, "orig_stop": stop, "orig_target": round(target, 2),
              "entrybar_high": float(entrybar["high"]), "entrybar_low": float(entrybar["low"]), "entrybar_close": float(entrybar["close"]),
              "orl": r["orl"], "plain_morning_net": tr0["net"], "plain_morning_exit": tr0["exit"]})
    if m["exit"] in ("stop", "stop_on_close") and m.get("exit_idx") is not None:
        re, skipped = scan_reentry(cand, r["orl"], m["exit_idx"], m["risk"], "lA", m["net"])
        day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
        return {"morning": m, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": m, "re": None, "day_net": m["net"], "skipped": []}

def features(dd, mode, day_bn):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return None
    cand = r["candles"]; sig = cand.iloc[r["sig_idx"]]
    or_c = day_spot[day_spot["time"] < "09:30"]; orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    dayopen = float(day_spot.iloc[0]["open"])
    return {"signal": sig["time"], "sig_close": float(sig["close"]), "dist_orl": round(orl - float(sig["close"]), 2),
            "below_pdl": round(pdl - float(sig["close"]), 2), "sig_range": round(float(sig["high"]) - float(sig["low"]), 2),
            "or_width": round(orh - orl, 2), "or_width_scale": round((orh - orl) / scale, 1),
            "gap_pct": round((dayopen - pdc) / pdc * 100, 3), "prev_range": round(pdh - pdl, 2), "bias": bias}

# ---------- Part 3: reclaim ----------
def replay_ce(candles, start_idx, entry, stop, target):
    risk = entry - stop
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if lo <= stop:
            return {"exit": "stop", "exit_time": t, "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if hi >= target:
            return {"exit": "target", "exit_time": t, "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if t == "15:10":
            return {"exit": "square_off", "exit_time": t, "net": round((cl - entry) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"exit": "square_off", "exit_time": c["time"], "net": round((float(c["close"]) - entry) * QTY - COST, 2), "risk": round(risk, 2)}

def reclaim_day(ds, spot, daily, bn_spot, bn_daily):
    dl = daily.to_dict("records")
    for i, y in enumerate(dl):
        if str(y["date"])[:10] != ds:
            continue
        prev = dl[i - 1]; day_spot = spot[spot["date"] == y["date"]]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev); scale = pdc / 55000.0
        setup, dirn, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
        if setup != "setup4_reclaim":
            return None
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        sig_idx = int(candles[candles["time"] == sig["time"]].index[0])
        orh = float(day_spot[day_spot["time"] < "09:30"]["high"].max()); L = max(orh, pdc)
        orig = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40)
        entry = orig["entry_price"]; stop = orig["stop_price"]; risk = entry - stop
        out = {"date": ds, "signal": sig["time"], "sig_close": float(sig["close"]), "L": round(L, 2),
               "above_L": round(float(sig["close"]) - L, 2), "orig_entry": entry, "orig_stop": stop,
               "orig_risk": round(risk, 2), "orig_net": orig["net_rs"], "orig_exit": orig["exit_reason"]}
        # BN at signal bar
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        if dbn:
            bspot, bpdh, bpdc, bpdl = dbn; bor = bspot[bspot["time"] < "09:30"]
            borh = float(bor["high"].max()); brow = bspot[bspot["time"] == sig["time"]]
            if not brow.empty:
                bcl = float(brow.iloc[0]["close"])
                out["bn_close"] = bcl; out["bn_orh"] = round(borh, 2); out["bn_above_orh"] = round(bcl - borh, 2)
                out["bn_above_prev"] = round(bcl - bpdc, 2)
        # BN-ORH / BN-prev filters: original trade if pass else no-trade
        out["bn_orh"] = "original_trade" if out.get("bn_above_orh", -1e9) > 0 else "no_trade"
        out["bn_prev"] = "original_trade" if out.get("bn_above_prev", -1e9) > 0 else "no_trade"
        out["time1030"] = "original_trade" if sig["time"] <= "10:30" else "no_trade"
        for cap in (30, 50):
            out[f"riskcap{cap}"] = "original_trade" if risk <= cap else "no_trade"
        # risk-size scaling to 30-pt cap, integer shares, cost Rs40 flat
        shares = 100 if risk <= 30 else max(1, int(100 * 30 / risk))
        tr = replay_ce(candles, sig_idx + 1, entry, stop, entry + 2 * risk)
        if tr["exit"] == "target":
            snet = round(2 * risk * shares - COST, 2)
        elif tr["exit"] == "stop":
            snet = round(-risk * shares - COST, 2)
        else:
            # square-off: use last close at exit time
            row = candles[candles["time"] == tr["exit_time"]]
            cl = float(row.iloc[0]["close"]) if not row.empty else float(candles.iloc[-1]["close"])
            snet = round((cl - entry) * shares - COST, 2)
        out["risksize30"] = {"shares": shares, "exit": tr["exit"], "net": snet}
        # stop = L
        trL = replay_ce(candles, sig_idx + 1, entry, L, entry + 2 * (entry - L)) if entry - L > 0 else {"exit": "invalid_risk", "net": None}
        out["stopL"] = {"stop": round(L, 2), "risk": round(entry - L, 2), "knife_lt10": (entry - L) < 10, **trL}
        # retest of L: first bar after signal whose low <= L, entry next open, stop = touch-bar low
        retest = None
        for k in range(sig_idx + 1, len(candles)):
            if float(candles.iloc[k]["low"]) <= L:
                if k + 1 < len(candles):
                    e2 = float(candles.iloc[k + 1]["open"]); s2 = float(candles.iloc[k]["low"]); r2 = e2 - s2
                    tr2 = replay_ce(candles, k + 1, e2, s2, e2 + 2 * r2) if r2 > 0 else {"exit": "invalid_risk", "net": None}
                    retest = {"touch_time": candles.iloc[k]["time"], "entry": e2, "stop": s2, "risk": round(r2, 2), **tr2}
                break
        out["retestL"] = retest if retest else {"result": "no_trade_no_touch"}
        return out
    return None

if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    out = {}
    # (lA) baseline
    for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            r = day_lA(dd, modes.get(ds, "v4"), dbn, "lA") if dd and dbn else None
            rows.append({"date": ds, "day_net": r["day_net"] if r else None})
        out["lA_" + label] = rows
        print(f"(lA) {label}: green {sum(1 for x in rows if x['day_net'] is not None and x['day_net']>0)}/{len(rows)} no-trade {sum(1 for x in rows if x['day_net'] is None)} total {sum(x['day_net'] for x in rows if x['day_net'] is not None)}")
        for x in rows: print("   ", x)
    # Part 1 variants
    for v in ["t1", "t2", "t3", "t4", "t5", "t6"]:
        for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_t(dd, modes.get(ds, "v4"), dbn, v) if dd and dbn else None
                rows.append({"date": ds, "day_net": r["day_net"] if r else None, "morning": r["morning"] if r else None, "re": r["re"] if r else None, "skipped": r["skipped"] if r else None})
            out.setdefault(v, {})[label] = rows
            g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0); nt = sum(1 for x in rows if x["day_net"] is None)
            tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
            print(f"\n=== ({v}) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                m = x["morning"]
                print("   ", x["date"], "morning", (m.get("signal"), m.get("entry"), "stop", m.get("stop"), "risk", m.get("risk"), "exit", m.get("exit"), m.get("exit_time"), "net", m.get("net")) if m else None, "| re", (x["re"] or {}).get("net") if x.get("re") else None, "| day", x["day_net"])
    # Part 2 features + filters
    feat = {}
    for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            f = features(dd, modes.get(ds, "v4"), dbn) if dd and dbn else None
            d = day_lA(dd, modes.get(ds, "v4"), dbn, "lA") if dd and dbn else None
            rows.append({"date": ds, "features": f, "lA_day_net": d["day_net"] if d else None})
        feat[label] = rows
        print(f"\n=== features {label} ===")
        for x in rows: print("   ", x)
    out["features"] = feat
    filters = {"gap_lt_-1.25": lambda f: f["gap_pct"] < -1.25,
               "belowPDL_gt_300": lambda f: f["below_pdl"] > 300,
               "gap_and_below": lambda f: f["gap_pct"] < -1.25 and f["below_pdl"] > 300,
               "orw_scale_gt_350": lambda f: f["or_width_scale"] > 350,
               "gap_and_orw": lambda f: f["gap_pct"] < -1.25 and f["or_width_scale"] > 350}
    for fname, fn in filters.items():
        print(f"\n=== filter {fname} as pure (lA) no-trade ===")
        for label in ("cluster1", "winners"):
            rows = feat[label]; kept = [x for x in rows if x["features"] and not fn(x["features"]) and x["lA_day_net"] is not None]
            removed = [x["date"] for x in rows if x["features"] and fn(x["features"])]
            g = sum(1 for x in kept if x["lA_day_net"] > 0); tot = sum(x["lA_day_net"] for x in kept)
            print(f"  {label}: kept green {g} total {tot} removed {removed}")
    # Part 3 reclaim
    spotp, dailyp = load_prog("NIFTY")
    for yr, dates in (("2026", ["2026-01-14","2026-10-26","2026-07-01"]), ("2025", ["2025-02-20","2025-06-06","2025-08-01"])):
        rows = []
        for ds in dates:
            r = reclaim_day(ds, spotp, dailyp, bn_spot, bn_daily); rows.append(r); print(f"\nreclaim {ds}: {r}")
        out[f"reclaim_{yr}"] = rows
    with open(os.path.expanduser("~/workspace/trading/t_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/t_sweep_raw.json")
