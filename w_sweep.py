"""Family (w): NIFTY only, paper only, no orders.
Pass bar: 60% green on the failing set AND total positive AND combined
NOT below (lA) on same window, winners not collapsed, no-trade separate.
Failing set under (lA) = Cluster 1 days with day_net <= 0: 30 Mar, 2 Apr,
13 May (3 days). Green = net > 0. 100 shares, Rs40/trade, square-off 15:10.

Variants, defined before results (not re-runs of the (w) forbidden list):
W-Tm: morning target multiple ONLY. Entry = next bar open after signal,
  stop = signal high (unchanged), target = entry - m*risk, m in
  {0.5, 1.0, 1.5}, full 100 shares (NOT a partial: the whole position
  exits at the m-level). Stop checked before target per bar (as in
  every prior sweep). If the morning stops, (lA) re-entry scan runs
  unchanged (band cap = original rescan risk). If the morning targets
  or square-offs, no re-entry. This is NOT a partial (no 50-share
  booking, no BE/MID trail), NOT a stop buffer, NOT a retest, NOT a
  timing gate (signal, entry bar and stop are all unchanged).
W-RK: re-entry cooling delay ONLY. Morning = (lA) exactly. After a
  morning stop, re-entry candidates whose signal-bar index <=
  stop_idx + K are skipped, K in {2, 7}; thereafter the (lA) scan
  runs unchanged (morning phase scan-skip, afternoon first band-fail
  ends the scan, band [10, rescan risk], window to 15:05). A delayed
  scan can still trade a later candidate (it is not a no-trade rule).
  The three working (lA) re-entries (29 Jun, 8 Jul, 19 Aug) are
  tabulated for every K before any claim about 30 Mar / 2 Apr.
W-ORD (DIAGNOSTIC ONLY, not a candidate): target-before-stop intra-bar
  ordering on both morning and re-entry, original 2x target. A bar
  whose low reaches target AND whose high reaches stop exits at
  target. This cannot be adopted on 5-min data (intra-bar order is
  unobserved); it bounds how much of the failure is an ordering
  assumption vs the price path. If it is inert, ordering is not
  the issue.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from close_reentry_sweep import replay_pe
from extended_window_sweep import scan_reentry
from u_sweep import day_lA_plain, CLUSTER1, WINNERS, MODES1, MODESW

QTY, COST = 100, 40.0


def replay_target_first(candles, start_idx, entry, stop, target):
    """Same as replay_pe except target beats stop on a bar hitting both."""
    risk = stop - entry
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if lo <= target:
            return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if hi >= stop:
            return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if t == "15:10":
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1,
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2)}


def day_target_mult(dd, mode, day_bn, m):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None}
    cand = r["candles"]; si = r["sig_idx"]
    entry = float(cand.iloc[si + 1]["open"]); stop = float(cand.iloc[si]["high"])
    risk = stop - entry; target = entry - m * risk
    morn = replay_pe(cand, si + 1, entry, stop, target)
    # replay_pe computes target net as 2*risk*QTY-COST; correct it for m != 2.
    if morn["exit"] == "target":
        morn = dict(morn); morn["net"] = round(m * risk * QTY - COST, 2); morn["target_dist"] = round(m * risk, 2)
    morn.update({"signal": cand.iloc[si]["time"], "entry": entry, "plain_morning_net": tr0["net"], "m": m})
    if morn["exit"] == "stop" and morn.get("exit_idx") is not None:
        re, skipped = scan_reentry(cand, r["orl"], morn["exit_idx"], r["info"]["risk"], "lA", morn["net"])
        day_net = round(morn["net"] + re["net"], 2) if (re and re["net"] is not None) else morn["net"]
        return {"morning": morn, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": morn, "re": None, "day_net": morn["net"], "skipped": []}


def scan_reentry_cool(candles, orl, stop_idx, rescan_risk, K, morning_net):
    """(lA) scan_reentry with candidates at index <= stop_idx+K skipped."""
    skipped = []
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "15:05":
            break
        if float(c["close"]) >= orl:
            continue
        if k <= stop_idx + K:
            skipped.append((t, f"cool_skip_K={K}_idx={k}_stop_idx={stop_idx}")); continue
        if k + 1 >= len(candles):
            skipped.append((t, "no_next_bar")); break
        entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
        afternoon = t > "11:30"
        band_ok = risk > 0 and 10 <= risk <= rescan_risk
        if afternoon and not band_ok:
            skipped.append((t, f"afternoon_first_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]_scan_ends")); break
        if not band_ok:
            skipped.append((t, f"band_fail_risk={risk:.2f}")); continue
        target = entry - 2 * risk
        re = replay_pe(candles, k + 1, entry, stop, target)
        re.update({"re_signal": t, "variant": f"cool_K{K}"})
        return re, skipped
    return None, skipped


def day_cool(dd, mode, day_bn, K):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None}
    if tr["exit"] != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    re, skipped = scan_reentry_cool(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], K, tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}


def day_target_first(dd, mode, day_bn):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None:
        return {"morning": tr0, "re": None, "day_net": None}
    cand = r["candles"]; si = r["sig_idx"]
    entry = float(cand.iloc[si + 1]["open"]); stop = float(cand.iloc[si]["high"])
    risk = stop - entry; target = entry - 2 * risk
    morn = replay_target_first(cand, si + 1, entry, stop, target)
    morn.update({"signal": cand.iloc[si]["time"], "entry": entry, "plain_morning_net": tr0["net"]})
    if morn["exit"] == "stop" and morn.get("exit_idx") is not None:
        # re-entry with target-first replay, (lA) scan logic (candidate choice unchanged)
        re, skipped = scan_reentry(cand, r["orl"], morn["exit_idx"], r["info"]["risk"], "lA", morn["net"])
        if re is not None:
            # replay the chosen re-entry trade target-first
            rsig_idx = None
            for k in range(morn["exit_idx"] + 1, len(cand)):
                if cand.iloc[k]["time"] == re["re_signal"]:
                    rsig_idx = k; break
            if rsig_idx is not None:
                re2 = replay_target_first(cand, rsig_idx + 1, re["entry"], re["stop"], re["target"])
                re2.update({"re_signal": re["re_signal"], "variant": "target_first"})
                re = re2
        day_net = round(morn["net"] + re["net"], 2) if (re and re["net"] is not None) else morn["net"]
        return {"morning": morn, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": morn, "re": None, "day_net": morn["net"], "skipped": []}


def summ(rows):
    traded = [x for x in rows if x["day_net"] is not None]
    return {"n": len(rows), "traded": len(traded),
            "green": sum(1 for x in traded if x["day_net"] > 0),
            "no_trade": len(rows) - len(traded),
            "still_loss": sum(1 for x in traded if x["day_net"] <= 0),
            "total": round(sum(x["day_net"] for x in traded), 2)}


def run_days(fn, days, modes):
    rows = []
    for ds in days:
        dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
        if not dd or not dbn:
            rows.append({"date": ds, "day_net": None, "note": "no_cache"}); continue
        res = fn(dd, modes.get(ds, "v4"), dbn)
        rows.append({"date": ds, "day_net": res["day_net"] if res else None,
                     "morning_exit": (res["morning"] or {}).get("exit") if res and res.get("morning") else None,
                     "morning_net": (res["morning"] or {}).get("net") if res and res.get("morning") else None,
                     "morning_time": (res["morning"] or {}).get("exit_time") if res and res.get("morning") else None,
                     "re_signal": (res["re"] or {}).get("re_signal") if res and res.get("re") else None,
                     "re_exit": (res["re"] or {}).get("exit") if res and res.get("re") else None,
                     "re_net": (res["re"] or {}).get("net") if res and res.get("re") else None,
                     "skipped": res.get("skipped") if res else None})
    return rows


if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    out = {}
    variants = [("lA", lambda dd, mo, db: day_lA_plain(dd, mo, db))]
    for m in (0.5, 1.0, 1.5):
        variants.append((f"W-T{m}", (lambda mm: lambda dd, mo, db: day_target_mult(dd, mo, db, mm))(m)))
    for K in (2, 7):
        variants.append((f"W-RK{K}", (lambda KK: lambda dd, mo, db: day_cool(dd, mo, db, KK))(K)))
    variants.append(("W-ORD_diag", lambda dd, mo, db: day_target_first(dd, mo, db)))
    for name, fn in variants:
        for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
            rows = run_days(fn, days, modes)
            out.setdefault(name, {})[label] = rows
            print(f"({name}) {label}: {summ(rows)}")
            for x in rows:
                print("   ", x["date"], "morn", x["morning_exit"], x["morning_net"], x["morning_time"],
                      "re", x["re_signal"], x["re_exit"], x["re_net"], "day", x["day_net"])
        c1 = out[name]["cluster1"]; wn = out[name]["winners"]
        print(f"({name}) COMBINED: {summ(c1)['total'] + summ(wn)['total']} (C1 {summ(c1)['total']} + W {summ(wn)['total']})")
    # OOS for best target variant only (W-T0.5), as a secondary check, not a pass claim
    univ = json.load(open(os.path.expanduser("~/workspace/trading/morning_bar_universe.json")))
    oos = [u for u in univ if not u.get("in_sample")]
    print(f"\nOOS days: {len(oos)}")
    for name, fn in [("lA", lambda dd, mo, db: day_lA_plain(dd, mo, db)),
                     ("W-T0.5", lambda dd, mo, db: day_target_mult(dd, mo, db, 0.5))]:
        rows = []
        for u in oos:
            ds = u["date"]; mode = u["mode"]
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            if not dd or not dbn:
                rows.append({"date": ds, "mode": mode, "day_net": None, "note": "no_cache"}); continue
            res = fn(dd, mode, dbn)
            rows.append({"date": ds, "mode": mode, "day_net": res["day_net"] if res else None,
                         "morning_exit": (res["morning"] or {}).get("exit") if res and res.get("morning") else None,
                         "morning_net": (res["morning"] or {}).get("net") if res and res.get("morning") else None,
                         "re_net": (res["re"]["net"] if res and res.get("re") else None)})
        out.setdefault(name, {})["oos"] = rows
        print(f"({name}) OOS: {summ(rows)}")
    la_oos = {x["date"]: x["day_net"] for x in out["lA"]["oos"]}
    for grp, cond in (("lA-winners", lambda d: la_oos[d] is not None and la_oos[d] > 0),
                      ("lA-losers", lambda d: la_oos[d] is not None and la_oos[d] <= 0)):
        sub_la = [x for x in out["lA"]["oos"] if cond(x["date"])]
        sub_v = [x for x in out["W-T0.5"]["oos"] if cond(x["date"])]
        print(f"(W-T0.5) {grp}: n={len(sub_la)} lA_total={sum(x['day_net'] for x in sub_la if x['day_net'] is not None)} "
              f"variant_total={sum(x['day_net'] for x in sub_v if x['day_net'] is not None)} "
              f"variant_green={sum(1 for x in sub_v if x['day_net'] is not None and x['day_net']>0)}/{sum(1 for x in sub_v if x['day_net'] is not None)}")
    with open(os.path.expanduser("~/workspace/trading/w_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/w_sweep_raw.json")
