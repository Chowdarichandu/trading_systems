"""Family (u): 23Mar-vs-untouched pair comparison + bounce-persistence
re-entry guards + 13May give-back variants validated OOS + Cluster 2 new axes.
NIFTY only, paper only, no orders. Pass bar: 60% green ON THE FAILING SET
AND total positive AND combined NOT below (lA) on same window, winners not
collapsed. No-trade separate from green throughout; a filter/guard can only
avoid, never convert. 100 shares, Rs40/trade, square-off 15:10, stop before
target per bar except where a variant states otherwise.

Part 1: (lA) rescan mornings for Cluster 1 (8) + PE winners (14), with
post-entry path axes (bounce depth/duration, first close >= entry /
>= signal high / >= OR low, BN path after signal, prev-close position).
Then two NEW re-entry guards, defined before results:
  U1: skip a re-entry candidate if ANY of the 3 bars before it closed
      >= OR low (bounce still present in last 3 bars); scan continues.
  U2: skip a re-entry candidate unless the bar immediately before it
      also closed < OR low (two consecutive closes below OR low ending
      at the candidate); scan continues.
Both keep the (lA) band [10, rescan risk] and the afternoon first-fail
rule (a candidate that PASSES the guard but fails the band in the
afternoon ends the scan, as in (lA)); a guard-skip never ends the scan.
If the morning does not stop, the day closes (no re-entry), as in (lA).

Part 2: 13May on its own terms. Generic morning partial replay:
partial at k x risk (level entry-k*risk, 50 shares booked = 50*k*risk),
remaining 50 trailed to BE (entry) or MID (entry-0.5*risk), high-touch
trails start NEXT bar after partial bar, close trails may use partial
bar close, original stop intra-bar first, target beats trail-close on
same bar, square-off 15:10. Re-entry (lA scan) only if morning final
exit is a stop (plain or stop_after_partial). Variants, defined before
results: G1 k=1.0 BE high, no cutoff (ungated o1 shape); G2 k=0.9 BE
high, no cutoff; G3 k=0.5 BE high, no cutoff; G4 k=1.0 BE high,
cutoff <10:00 (= p4, REFERENCE only, already OOS-failed in (q));
G5 k=1.0 MID close, no cutoff. Each variant is run on 13May, on
Cluster 1 + winners, AND on the 92-day OOS PE window (morning_bar_
universe.json, in_sample==False) with (lA) baseline on same window.
A 13May variant passes only if it passes on OOS too (green >=60% of
traded OOS days AND total positive AND total NOT below (lA) OOS).

Part 3: Cluster 2 new axes, both years together (2026 fitted 3 + 2025
held-out 3, same reclaim scan as (t)): post-signal path (first close
below L, first low below L, MFE before exit), BN day trend (BN close
vs open), BN first close above BN OR high after the signal. No rule
is fitted from these axes unless it separates all 6 trades; if none
does, Cluster 2 is recorded as unfixable on the available sample.
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import day_variant as day_lA
from close_reentry_sweep import replay_pe
from progressive_engine import load as load_prog
from daytrader_cash_backtest import find_signal, run_day, bias_of

QTY, COST = 100, 40.0
CLUSTER1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
WINNERS = ["2026-01-21","2026-02-24","2026-03-16","2026-03-13","2026-03-23","2026-04-24","2026-05-05","2026-07-22","2026-08-12","2026-08-27","2026-09-29","2026-09-07","2026-10-08","2026-10-23"]
MODES1 = {"2026-04-02": "skill"}; MODESW = {"2026-03-23": "skill"}

# ---------- Part 1: path axes ----------
def path_axes(ds, mode, spot, daily, bn_spot, bn_daily):
    dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
    if not dd or not dbn: return {"date": ds, "rescan": None}
    r = rescan_trade(dd, mode, dbn)
    if r is None: return {"date": ds, "rescan": None}
    day_spot, pdh, pdc, pdl, bias, scale = dd
    cand = r["candles"]; si = r["sig_idx"]; sig = cand.iloc[si]
    entry = float(cand.iloc[si + 1]["open"]); stop = float(sig["high"]); risk = stop - entry; orl = r["orl"]
    def first_close(cond):
        for k in range(si + 1, len(cand)):
            if cond(float(cand.iloc[k]["close"])): return cand.iloc[k]["time"]
        return None
    bars = []
    for k in range(si + 1, min(si + 6, len(cand))):
        c = cand.iloc[k]
        bars.append({"t": c["time"], "h-entry": round(float(c["high"]) - entry, 2), "cl-entry": round(float(c["close"]) - entry, 2),
                     "cl>=sighi": bool(float(c["close"]) >= stop), "cl>=orl": bool(float(c["close"]) >= orl)})
    bspot, bpdh, bpdc, bpdl = dbn
    bor = bspot[bspot["time"] < "09:30"]; borh = float(bor["high"].max()); borl = float(bor["low"].min())
    brow = bspot[bspot["time"] == sig["time"]]
    bcl = float(brow.iloc[0]["close"]) if not brow.empty else None
    bopen = float(bspot.iloc[0]["open"])
    brow15 = bspot[bspot["time"] == "15:10"]
    bclose = float(brow15.iloc[0]["close"]) if not brow15.empty else float(bspot.iloc[-1]["close"])
    bafter = bspot[bspot["time"] > sig["time"]].head(3)
    return {"date": ds, "signal": sig["time"], "sig_close": float(sig["close"]), "orl": orl, "entry": entry, "stop": stop,
            "risk": round(risk, 2), "morning_exit": r["trade"]["exit"], "morning_net": r["trade"]["net"],
            "prev_close_pos": round((pdc - pdl) / (pdh - pdl), 3) if pdh > pdl else None,
            "sig_vs_prevclose": round(pdc - float(sig["close"]), 2),
            "bars_after_entry": bars,
            "max_high_3": round(max(float(cand.iloc[k]["high"]) for k in range(si + 1, min(si + 4, len(cand)))) - entry, 2),
            "first_close_ge_entry": first_close(lambda cl: cl >= entry),
            "first_close_ge_sighi": first_close(lambda cl: cl >= stop),
            "first_close_ge_orl": first_close(lambda cl: cl >= orl),
            "bn_gap_pct": round((bopen - bpdc) / bpdc * 100, 3), "bn_day_ret_pct": round((bclose - bopen) / bopen * 100, 3),
            "bn_sig_vs_borl": round(bcl - borl, 2) if bcl is not None else None,
            "bn_sig_vs_borh": round(bcl - borh, 2) if bcl is not None else None,
            "bn_path_after": [{"t": row["time"], "cl-borl": round(float(row["close"]) - borl, 2)} for _, row in bafter.iterrows()]}

# ---------- Part 1: bounce-persistence re-entry guards ----------
def scan_reentry_guard(candles, orl, stop_idx, rescan_risk, guard, morning_net):
    skipped = []
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "15:05": break
        if float(c["close"]) >= orl: continue
        # guard, evaluated before band
        if guard == "U1":
            prev = [float(candles.iloc[j]["close"]) for j in range(max(stop_idx + 1, k - 3), k)]
            if any(cl >= orl for cl in prev):
                skipped.append((t, "U1_bounce_in_last3")); continue
        elif guard == "U2":
            if k - 1 <= stop_idx or float(candles.iloc[k - 1]["close"]) >= orl:
                skipped.append((t, "U2_prev_not_below_orl")); continue
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
        re.update({"re_signal": t, "guard": guard})
        return re, skipped
    return None, skipped

def day_guard(dd, mode, day_bn, guard):
    r = rescan_trade(dd, mode, day_bn)
    if r is None: return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None: return {"morning": tr, "re": None, "day_net": None, "skipped": []}
    if tr.get("exit") != "stop": return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    re, skipped = scan_reentry_guard(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], guard, tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}

# ---------- Part 2: generic morning partial ----------
def replay_partial_gen(candles, start_idx, entry, stop, target, k_frac, trail_kind, cutoff):
    risk = stop - entry
    if risk <= 0: return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    plevel = entry - k_frac * risk
    trail_level = entry if trail_kind == "BE" else entry - 0.5 * risk
    close_only = trail_kind == "MID"
    partial_booked = False; partial_net = 0.0; partial_time = None; partial_idx = None
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if hi >= stop:
            if partial_booked:
                return {"exit": "stop_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net - (stop - entry) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time}
            return {"exit": "stop", "exit_time": t, "exit_idx": j, "net": round(-risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None}
        if not partial_booked and lo <= plevel:
            if cutoff is not None and t >= cutoff:
                return replay_pe(candles, j, entry, stop, target) | {"partial_gated_out": True, "partial_time": None}
            partial_booked = True; partial_time = t; partial_net = k_frac * risk * 50; partial_idx = j
            if lo <= target:
                return {"exit": "target_same_bar_as_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - target) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time}
        if partial_booked and (close_only or j > partial_idx):
            if close_only:
                if cl >= trail_level:
                    rem = (entry - trail_level) * 50
                    return {"exit": "mid_close_after_partial", "exit_time": t, "exit_idx": j,
                            "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                            "partial_booked": True, "partial_time": partial_time}
            else:
                if hi >= trail_level:
                    rem = (entry - trail_level) * 50
                    return {"exit": "breakeven_after_partial", "exit_time": t, "exit_idx": j,
                            "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2),
                            "partial_booked": True, "partial_time": partial_time}
        if lo <= target:
            if partial_booked:
                return {"exit": "target_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - target) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time}
            return {"exit": "target", "exit_time": t, "exit_idx": j, "net": round(2 * risk * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None}
        if t == "15:10":
            if partial_booked:
                return {"exit": "square_off_after_partial", "exit_time": t, "exit_idx": j,
                        "net": round(partial_net + (entry - cl) * 50 - COST, 2), "risk": round(risk, 2),
                        "partial_booked": True, "partial_time": partial_time}
            return {"exit": "square_off", "exit_time": t, "exit_idx": j, "net": round((entry - cl) * QTY - COST, 2),
                    "risk": round(risk, 2), "partial_booked": False, "partial_time": None}
    c = candles.iloc[-1]
    if partial_booked:
        return {"exit": "square_off_after_partial", "exit_time": c["time"], "exit_idx": len(candles) - 1,
                "net": round(partial_net + (entry - float(c["close"])) * 50 - COST, 2), "risk": round(risk, 2),
                "partial_booked": True, "partial_time": partial_time}
    return {"exit": "square_off", "exit_time": c["time"], "exit_idx": len(candles) - 1,
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2),
            "partial_booked": False, "partial_time": None}

def day_partial(dd, mode, day_bn, k_frac, trail_kind, cutoff):
    from extended_window_sweep import scan_reentry
    r = rescan_trade(dd, mode, day_bn)
    if r is None: return {"morning": None, "re": None, "day_net": None}
    tr0 = r["trade"]
    if tr0 is None or tr0.get("net") is None: return {"morning": tr0, "re": None, "day_net": None}
    cand = r["candles"]; si = r["sig_idx"]
    entry = float(cand.iloc[si + 1]["open"]); stop = float(cand.iloc[si]["high"]); risk = stop - entry; target = entry - 2 * risk
    m = replay_partial_gen(cand, si + 1, entry, stop, target, k_frac, trail_kind, cutoff)
    m.update({"signal": cand.iloc[si]["time"], "entry": entry, "plain_morning_net": tr0["net"]})
    if m["exit"] in ("stop", "stop_after_partial") and m.get("exit_idx") is not None:
        re, skipped = scan_reentry(cand, r["orl"], m["exit_idx"], risk, "lA", m["net"])
        day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
        return {"morning": m, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": m, "re": None, "day_net": m["net"], "skipped": []}

def day_lA_plain(dd, mode, day_bn):
    from extended_window_sweep import scan_reentry
    r = rescan_trade(dd, mode, day_bn)
    if r is None: return {"morning": None, "re": None, "day_net": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None: return {"morning": tr, "re": None, "day_net": None}
    if tr["exit"] == "stop" and tr.get("exit_idx") is not None:
        re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], "lA", tr["net"])
        day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
        return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}
    return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}

# ---------- Part 3: reclaim new axes ----------
def reclaim_axes(ds, spot, daily, bn_spot, bn_daily):
    dl = daily.to_dict("records")
    for i, y in enumerate(dl):
        if str(y["date"])[:10] != ds: continue
        prev = dl[i - 1]; day_spot = spot[spot["date"] == y["date"]]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, _ = bias_of(prev); scale = pdc / 55000.0
        setup, dirn, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
        if setup != "setup4_reclaim": return None
        orig = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40)
        orh = float(day_spot[day_spot["time"] < "09:30"]["high"].max()); L = max(orh, pdc)
        cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        si = int(cand[cand["time"] == sig["time"]].index[0])
        entry = orig["entry_price"]
        post = []
        for k in range(si + 1, min(si + 4, len(cand))):
            c = cand.iloc[k]
            post.append({"t": c["time"], "cl-L": round(float(c["close"]) - L, 2), "lo-L": round(float(c["low"]) - L, 2)})
        first_cl = first_lo = None; mfe = 0.0
        for k in range(si + 1, len(cand)):
            c = cand.iloc[k]
            if first_cl is None and float(c["close"]) < L: first_cl = c["time"]
            if first_lo is None and float(c["low"]) < L: first_lo = c["time"]
            mfe = max(mfe, float(c["high"]) - entry)
            if c["time"] == orig.get("exit_time"): break
        dbn = day_data_bn(bn_spot, bn_daily, ds); bspot, bpdh, bpdc, bpdl = dbn
        bopen = float(bspot.iloc[0]["open"])
        brow15 = bspot[bspot["time"] == "15:10"]
        bclose = float(brow15.iloc[0]["close"]) if not brow15.empty else float(bspot.iloc[-1]["close"])
        bor = bspot[bspot["time"] < "09:30"]; borh = float(bor["high"].max())
        b_at = bspot[bspot["time"] == sig["time"]]
        bcl = float(b_at.iloc[0]["close"]) if not b_at.empty else None
        bn_first_orh = None
        for _, row in bspot[bspot["time"] > sig["time"]].iterrows():
            if float(row["close"]) > borh: bn_first_orh = row["time"]; break
        return {"date": ds, "signal": sig["time"], "L": round(L, 2), "above_L": round(float(sig["close"]) - L, 2),
                "orig_entry": entry, "orig_risk": round(entry - orig["stop_price"], 2), "orig_net": orig["net_rs"],
                "orig_exit": orig["exit_reason"], "post_signal": post, "first_close_below_L": first_cl,
                "first_low_below_L": first_lo, "MFE_pts": round(mfe, 2),
                "BN_gap_pct": round((bopen - bpdc) / bpdc * 100, 3),
                "BN_day_ret_pct": round((bclose - bopen) / bopen * 100, 3),
                "BN_sig_vs_borh": round(bcl - borh, 2) if bcl is not None else None,
                "BN_first_close_above_ORH_after_sig": bn_first_orh}
    return None

if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    out = {}
    # Part 1 axes
    print("##### PART 1 axes #####")
    axes = {}
    for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
        rows = []
        for ds in days:
            a = path_axes(ds, modes.get(ds, "v4"), spot, daily, bn_spot, bn_daily); rows.append(a)
            print(ds, json.dumps(a, default=str))
        axes[label] = rows
    out["part1_axes"] = axes
    # Part 1 guards
    print("\n##### PART 1 guards #####")
    for guard in ("U1", "U2"):
        for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_guard(dd, modes.get(ds, "v4"), dbn, guard) if dd and dbn else None
                rows.append({"date": ds, "day_net": r["day_net"] if r else None, "morning": r["morning"] if r else None,
                             "re": r["re"] if r else None, "skipped": r["skipped"] if r else None})
            out.setdefault(guard, {})[label] = rows
            g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
            tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
            print(f"({guard}) {label}: green {g}/{len(rows)} total {tot}")
            for x in rows:
                print("   ", x["date"], "morning", (x["morning"] or {}).get("net"), "re", (x["re"] or {}).get("net") if x.get("re") else None,
                      "day", x["day_net"], "skipped", x["skipped"])
    # (lA) baseline reproduction
    print("\n##### (lA) baseline #####")
    for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            r = day_lA(dd, modes.get(ds, "v4"), dbn, "lA") if dd and dbn else None
            rows.append({"date": ds, "day_net": r["day_net"] if r else None})
        out["lA_" + label] = rows
        print(f"(lA) {label}: green {sum(1 for x in rows if x['day_net'] is not None and x['day_net']>0)} total {sum(x['day_net'] for x in rows if x['day_net'] is not None)}")
    # Part 2
    print("\n##### PART 2: 13May + C1/winners #####")
    variants = [("G1", 1.0, "BE", None), ("G2", 0.9, "BE", None), ("G3", 0.5, "BE", None),
                ("G4_p4ref", 1.0, "BE", "10:00"), ("G5", 1.0, "MID", None)]
    for name, k_frac, trail, cutoff in variants:
        for label, days, modes in (("cluster1", CLUSTER1, MODES1), ("winners", WINNERS, MODESW)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_partial(dd, modes.get(ds, "v4"), dbn, k_frac, trail, cutoff) if dd and dbn else None
                rows.append({"date": ds, "day_net": r["day_net"] if r else None, "morning": r["morning"] if r else None, "re": r["re"] if r else None})
            out.setdefault(name, {})[label] = rows
            g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
            tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
            print(f"({name} k={k_frac} trail={trail} cutoff={cutoff}) {label}: green {g}/{len(rows)} total {tot}")
            for x in rows: print("   ", x["date"], "morning", (x["morning"] or {}).get("exit"), (x["morning"] or {}).get("net"),
                                 "partial", (x["morning"] or {}).get("partial_time"), "re", (x["re"] or {}).get("net") if x.get("re") else None, "day", x["day_net"])
    # Part 2 OOS
    print("\n##### PART 2: OOS window #####")
    univ = json.load(open(os.path.expanduser("~/workspace/trading/morning_bar_universe.json")))
    oos = [u for u in univ if not u.get("in_sample")]
    print(f"OOS days: {len(oos)}")
    for name, k_frac, trail, cutoff in [("lA", None, None, None)] + variants:
        rows = []
        for u in oos:
            ds = u["date"]; mode = u["mode"]
            dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            if not dd or not dbn:
                rows.append({"date": ds, "mode": mode, "day_net": None, "note": "no_cache"}); continue
            res = day_lA_plain(dd, mode, dbn) if name == "lA" else day_partial(dd, mode, dbn, k_frac, trail, cutoff)
            rows.append({"date": ds, "mode": mode, "day_net": res["day_net"] if res else None,
                         "morning_exit": (res["morning"] or {}).get("exit") if res and res.get("morning") else None,
                         "morning_net": (res["morning"] or {}).get("net") if res and res.get("morning") else None,
                         "partial_time": (res["morning"] or {}).get("partial_time") if res and res.get("morning") else None,
                         "re_net": (res["re"]["net"] if res and res.get("re") else None)})
        out.setdefault(name, {})["oos"] = rows
        traded = [x for x in rows if x["day_net"] is not None]
        g = sum(1 for x in traded if x["day_net"] > 0)
        tot = sum(x["day_net"] for x in traded)
        print(f"({name}) OOS: traded {len(traded)}/{len(rows)} green {g} rate {round(100*g/len(traded),1) if traded else None}% total {tot}")
    la_oos = {x["date"]: x["day_net"] for x in out["lA"]["oos"]}
    for name, _, _, _ in variants:
        for grp, cond in (("lA-winners", lambda d: la_oos[d] is not None and la_oos[d] > 0),
                          ("lA-losers", lambda d: la_oos[d] is not None and la_oos[d] <= 0)):
            sub_la = [x for x in out["lA"]["oos"] if cond(x["date"])]
            sub_v = [x for x in out[name]["oos"] if cond(x["date"])]
            tot_la = sum(x["day_net"] for x in sub_la if x["day_net"] is not None)
            tot_v = sum(x["day_net"] for x in sub_v if x["day_net"] is not None)
            g_v = sum(1 for x in sub_v if x["day_net"] is not None and x["day_net"] > 0)
            tr_v = sum(1 for x in sub_v if x["day_net"] is not None)
            print(f"({name}) {grp}: n={len(sub_la)} lA_total={tot_la} variant_total={tot_v} variant_green={g_v}/{tr_v}")
    # Part 3
    print("\n##### PART 3: reclaim new axes #####")
    spotp, dailyp = load_prog("NIFTY")
    rec = {}
    for yr, dates in (("2026", ["2026-01-14","2026-07-01","2026-10-26"]), ("2025", ["2025-02-20","2025-06-06","2025-08-01"])):
        rows = []
        for ds in dates:
            r = reclaim_axes(ds, spotp, dailyp, bn_spot, bn_daily); rows.append(r); print(ds, json.dumps(r, default=str))
        rec[yr] = rows
    out["part3_reclaim"] = rec
    with open(os.path.expanduser("~/workspace/trading/u_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/u_sweep_raw.json")
