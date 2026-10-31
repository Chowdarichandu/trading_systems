"""Extended-window sweep (l)-(n) on (k), NIFTY Cluster 1 + 14 PE winners. Paper only.
Base (k) = (d) BN-confirmed rescan morning + band-filtered re-entry
(risk in [10, rescan_risk]), scan-skip, to 15:05, target 2x risk.
Morning = rescan_trade from combined_confirm_sweep. Re-entry scan below
is implemented per variant; (h)-(k) and earlier families are NOT re-run alone.

(l) (k) + rule avoiding the 30 Mar afternoon stop without losing 8 Jul afternoon green:
  lA afternoon STOP-ON-FIRST-FAIL: morning phase (<=11:30) scan-skip as in (k);
     afternoon phase (>11:30): first candidate (close<ORL) failing the band
     ENDS afternoon scanning (no re-entry). First afternoon candidate passing
     the band is traded. 30 Mar: 11:45 fails band -> end, no 13:55 stop.
     8 Jul: 12:05 passes -> green preserved. This is NOT whole-scan stop-on-first-fail
     (that would kill 8 Jul at its 10:20 morning-phase band fail).
  lB afternoon risk-ratio: morning scan-skip to 11:30; afternoon scan-skip to 15:05
     with extra condition risk >= 0.70*rescan_risk (in addition to band).
     Scan-skip continues past failing afternoon candidates (prior-sweep convention).
  lC afternoon window to 12:30 only: morning scan-skip to 11:30; afternoon scan-skip
     to 12:30. 30 Mar: no passing afternoon candidate by 12:30 -> no re-entry.
     8 Jul: 12:05 passes -> green preserved.
(m) (k) + partial/trail ON THE RE-ENTRY ONLY (morning unchanged):
  m1 partial50_trailBE: trigger entry-1.0*risk, book 50, remaining stop -> breakeven.
  m2 partial50_noTrail: trigger entry-1.0*risk, book 50, remaining keeps original stop.
  m3 partial25_trailBE: trigger entry-0.5*risk, book 50, remaining stop -> breakeven.
  Accounting/order as in partial_trail_sweep: cost Rs40 total, adverse (stop) checked
  before favourable (partial/target) per bar; partial+target same bar handled.
(n) Morning-loss cap on (k):
  n1 skip ANY re-entry if |morning net| > 4000.
  n2 skip ANY re-entry if |morning net| > 3000.
  n3 skip AFTERNOON re-entry only if |morning net| > 2000 (morning-phase re-entries
     unaffected). 30 Mar morning 2055 vs 8 Jul morning 1985: threshold 2000 separates
     them by Rs70 -- flagged as knife-edge/fitted, not robust, wherever it appears.
Pass bar: 60% green (5/8) AND Cluster 1 total positive AND winners not collapsed.
Green = net > 0. No-trade counted separately from green throughout.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import replay_pe
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
QTY, COST = 100, 40.0

def replay_partial(candles, start_idx, entry, stop, target, trigger_frac, trail_be):
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk", "exit_time": None, "net": None, "risk": round(risk, 2)}
    plevel = entry - trigger_frac * risk
    partial_booked = False; partial_net = 0.0; partial_time = None; cur_stop = stop; trailed = False
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if hi >= cur_stop:
            if partial_booked:
                rem = -(cur_stop - entry) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop_after_partial", "exit_time": t, "exit_price": cur_stop, "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time, "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop", "exit_time": t, "exit_price": cur_stop, "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2), "partial_booked": False, "partial_time": None, "trailed": False}
        if not partial_booked and lo <= plevel:
            partial_booked = True; partial_time = t; partial_net = (entry - plevel) * 50
            if trail_be: cur_stop = entry; trailed = True
            if lo <= target:
                rem = (entry - target) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_same_bar_as_partial", "exit_time": t, "exit_price": target, "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time, "trailed": trailed}
        if lo <= target:
            if partial_booked:
                rem = (entry - target) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target_after_partial", "exit_time": t, "exit_price": target, "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time, "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target", "exit_time": t, "exit_price": target, "net": round((entry - target) * QTY - COST, 2), "risk": round(risk, 2), "partial_booked": False, "partial_time": None, "trailed": trailed}
        if t == "15:10":
            if partial_booked:
                rem = (entry - cl) * 50
                return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial", "exit_time": t, "exit_price": cl, "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time, "trailed": trailed}
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off", "exit_time": t, "exit_price": cl, "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2), "partial_booked": False, "partial_time": None, "trailed": trailed}
    c = candles.iloc[-1]
    if partial_booked:
        rem = (entry - float(c["close"])) * 50
        return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off_after_partial", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round(partial_net + rem - COST, 2), "risk": round(risk, 2), "partial_booked": True, "partial_time": partial_time, "trailed": trailed}
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2), "partial_booked": False, "partial_time": None, "trailed": trailed}

def scan_reentry(candles, orl, stop_idx, rescan_risk, variant, morning_net):
    """Returns (re_dict_or_None, skipped_list). Candidate = close < orl, entry next open."""
    skipped = []
    def candidate(k):
        c = candles.iloc[k]; t = c["time"]
        if k + 1 >= len(candles): return None, (t, "no_next_bar")
        entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
        return (t, entry, stop, risk), None
    if variant in ("n1", "n2"):
        cap = 4000 if variant == "n1" else 3000
        if abs(morning_net) > cap: return None, [("cap", f"|morning|={abs(morning_net)}>{cap}_reentry_skipped")]
    # phases: morning <=11:30, afternoon >11:30
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "15:05": break
        if float(c["close"]) >= orl: continue
        cand, err = candidate(k)
        if err: skipped.append(err); break
        t, entry, stop, risk = cand
        afternoon = t > "11:30"
        # (n3): afternoon cap only
        if variant == "n3" and afternoon and abs(morning_net) > 2000:
            return None, [("cap_afternoon", f"|morning|={abs(morning_net)}>2000_afternoon_reentry_skipped")]
        # (lC): afternoon window ends 12:30
        if variant == "lC" and afternoon and t > "12:30": break
        band_ok = risk > 0 and 10 <= risk <= rescan_risk
        if variant == "lA" and afternoon and not band_ok:
            skipped.append((t, f"afternoon_first_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]_scan_ends")); break
        if not band_ok:
            skipped.append((t, f"band_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]")); continue
        if variant == "lB" and afternoon and risk < 0.70 * rescan_risk:
            skipped.append((t, f"ratio_fail_risk={risk:.2f}_ratio={risk/rescan_risk:.3f}<0.70")); continue
        target = entry - 2 * risk
        if variant == "m1": re = replay_partial(candles, k + 1, entry, stop, target, 1.0, True)
        elif variant == "m2": re = replay_partial(candles, k + 1, entry, stop, target, 1.0, False)
        elif variant == "m3": re = replay_partial(candles, k + 1, entry, stop, target, 0.5, True)
        else: re = replay_pe(candles, k + 1, entry, stop, target)
        re.update({"re_signal": t, "variant": variant, "target_dist": round(entry - target, 2)})
        return re, skipped
    return None, skipped

def day_variant(dd, mode, day_bn, variant):
    r = rescan_trade(dd, mode, day_bn)
    if r is None: return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None: return {"morning": tr, "re": None, "day_net": None, "skipped": []}
    if tr.get("exit") != "stop": return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], variant, tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}

if __name__ == "__main__":
    spot, daily = load_nifty(); bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02", "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    orig1 = {"2026-01-09": -3745, "2026-02-06": -2275, "2026-03-30": -2055, "2026-04-02": -2115, "2026-05-13": -5075, "2026-06-29": -4740, "2026-07-08": -1985, "2026-08-19": -2300}
    win_days = {"2026-01-21": 9280, "2026-02-24": 7350, "2026-03-16": 8940, "2026-03-13": 5400, "2026-03-23": 7260, "2026-04-24": 8820, "2026-05-05": 5040, "2026-07-22": 6320, "2026-08-12": 6250, "2026-08-27": 3000, "2026-09-29": 3790, "2026-09-07": 2990, "2026-10-08": 5440, "2026-10-23": 11390}
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    variants = ["lA", "lB", "lC", "m1", "m2", "m3", "n1", "n2", "n3"]
    out = {}
    def summarise(rows):
        g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
        nt = sum(1 for x in rows if x["day_net"] is None)
        tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
        return g, nt, tot
    # k baseline reproduction check
    print("=== (k) reproduction check ===")
    for ds in cluster1:
        dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
        r = day_variant(dd, modes1.get(ds, "v4"), dbn, "k") if dd and dbn else None
        print(ds, "k_day", r["day_net"] if r else None, "morning", r["morning"]["net"] if r and r["morning"] else None, "re", r["re"] if r else None)
    for v in variants:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1), ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_variant(dd, modes.get(ds, "v4"), dbn, v) if dd and dbn else None
                rows.append({"date": ds, "orig_net": orig[ds], "result": r, "day_net": r["day_net"] if r else None})
            out.setdefault(v, {})[label] = rows
            g, nt, tot = summarise(rows)
            print(f"\n=== ({v}) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                res = x["result"]
                print(x["date"], "morning", (res["morning"]["signal"], res["morning"]["net"]) if res and res["morning"] else None, "re", res["re"] if res else None, "day", x["day_net"], "skipped", res["skipped"] if res else None)
    with open(os.path.expanduser("~/workspace/trading/extended_window_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
