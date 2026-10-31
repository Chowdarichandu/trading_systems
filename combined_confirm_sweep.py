"""Combined-confirmation sweep (d)-(g), NIFTY Cluster 1 + 14 PE winners. Paper only.
Untried combinations ONLY -- do not re-run (a)-(c) alone or any earlier family alone.
Common replay (PE): entry=next bar open, stop=signal high, target=entry-2*risk,
stop before target per bar incl. entry bar, square-off 15:10, 100 shares, Rs40.
Green = net > 0. No-trade counted separately from green throughout.
Pass bar: 60% green (5/8) AND Cluster 1 total positive AND winners not collapsed.

(d) XC-RESCAN-ORL morning trade (first V4/Skill breakdown at/after BN break
    < BN OR low) PLUS RF-BAND-SCAN re-entry after its stop (re-entry risk in
    [10, rescan-trade risk], scanning to 11:30). Winners: same morning rule;
    re-entry applies generally if a rescan trade stops (prior XC-RESCAN winners
    had no stops, so this is expected to be inert there -- verified, not assumed).
(e) BN-confirmed RE-ENTRY: baseline morning trade; if it stops, re-entry =
    first bar after stop (scanning to 11:30) whose Nifty close < OR low AND
    Bank Nifty close on the SAME time label < BN OR low. Entry next open,
    stop that bar high, target 2x, Rs40 again. Day = morning + re-entry.
(f) Signal-low + risk band: baseline morning trade; if it stops, re-entry
    candidate must close < ORIGINAL signal bar low AND carry risk in
    [10, original risk]. F-DAY = first siglow candidate only (fails band ->
    no re-entry); F-SCAN = skip failing siglow candidates, continue to 11:30.
(g) Relative strength (scale-adjusted depth): depth_adj = (OR low - close) /
    scale, scale = prev close / 55000 for each index. BN depth must EXCEED
    Nifty depth in depth_adj, not merely close below BN OR low.
    G-FILTER: original trade kept only if, by Nifty signal time, some BN bar
    (>=09:30) closed < BN OR low with depth_adj > Nifty signal depth_adj;
    else no-trade (avoidance only, by construction).
    G-RESCAN: scan Nifty breakdown candidates in order; first candidate for
    which BN (bars <= candidate time) has a close < BN OR low with
    depth_adj > that candidate's depth_adj is the trade; else no-trade.
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import orig_trade, replay_pe
from reentry_filter_sweep import load_bn, day_data_bn, bn_break_time, reentry_filtered
from bounce_sizing_sweep import scan

QTY, COST = 100, 40.0

# ---------- (d) rescan trade, returning candles for re-entry ----------
def rescan_trade(dd, mode, day_bn):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    bt, bn_orl, bn_orh = bn_break_time(day_bn, day_bn[3], "orl")
    if bt is None:
        return None
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    sig = None
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > "11:30" or t < bt:
            continue
        cl = float(c["close"])
        if cl < orl and cl < pdl:
            if mode == "skill":
                sig = i; break
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                sig = i; break
    if sig is None or sig + 1 >= len(cand):
        return None
    s = cand.iloc[sig]
    entry = float(cand.iloc[sig + 1]["open"]); stop = float(s["high"]); risk = stop - entry
    target = entry - 2 * risk
    tr = replay_pe(cand, sig + 1, entry, stop, target)
    tr.update({"signal": s["time"], "bn_break": bt, "orl": orl})
    return {"candles": cand, "orl": orl, "orh": orh, "sig_idx": sig, "info": {"risk": risk, "signal": s["time"]}, "trade": tr}

def day_d(dd, mode, day_bn):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "bn_break": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None or tr.get("exit") != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"] if tr else None, "bn_break": tr.get("bn_break") if tr else None}
    re = reentry_filtered(r["candles"], r["orl"], tr["exit_idx"], {"risk": r["info"]["risk"]}, "RF-BAND-SCAN")
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "bn_break": tr.get("bn_break")}

# ---------- (e) BN-confirmed re-entry ----------
def bn_orl_and_map(day_bn):
    day_spot, pdh, pdc, pdl = day_bn
    or_c = day_spot[day_spot["time"] < "09:30"]
    orl = float(or_c["low"].min()); orh = float(or_c["high"].max())
    cmap = {row["time"]: float(row["close"]) for _, row in day_spot.iterrows()}
    return orl, orh, cmap

def day_e(dd, mode, day_bn):
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    if orig is None or orig["exit"] != "stop":
        return {"info": info, "orig": orig, "re": None, "day_net": orig["net"] if orig else None}
    bn_orl, _, cmap = bn_orl_and_map(day_bn)
    re = None
    for k in range(orig["exit_idx"] + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "11:30":
            break
        if float(c["close"]) < orl and cmap.get(t) is not None and cmap[t] < bn_orl:
            if k + 1 >= len(candles):
                break
            entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
            if risk <= 0:
                continue
            re = replay_pe(candles, k + 1, entry, stop, entry - 2 * risk)
            re.update({"re_signal": t, "bn_close": cmap[t], "bn_orl": bn_orl})
            break
    day_net = round(orig["net"] + re["net"], 2) if (re and re["net"] is not None) else orig["net"]
    return {"info": info, "orig": orig, "re": re, "day_net": day_net}

# ---------- (f) signal-low + risk band ----------
def day_f(dd, mode, scan_fwd):
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    if orig is None or orig["exit"] != "stop":
        return {"info": info, "orig": orig, "re": None, "day_net": orig["net"] if orig else None}
    sig_low = info["sig_low"]; orig_risk = info["risk"]
    re = None
    for k in range(orig["exit_idx"] + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "11:30":
            break
        if float(c["close"]) < sig_low:
            if k + 1 >= len(candles):
                break
            entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
            if risk <= 0:
                if scan_fwd:
                    continue
                break
            if 10 <= risk <= orig_risk:
                re = replay_pe(candles, k + 1, entry, stop, entry - 2 * risk)
                re.update({"re_signal": t, "sig_low": sig_low})
                break
            else:
                if scan_fwd:
                    continue
                break
    day_net = round(orig["net"] + re["net"], 2) if (re and re["net"] is not None) else orig["net"]
    return {"info": info, "orig": orig, "re": re, "day_net": day_net}

# ---------- (g) relative strength ----------
def bn_depth_adj_by_time(day_bn):
    """Returns (bn_orl, bn_scale, list of (time, close, depth_adj) for bars >=09:30 <=11:30)."""
    day_spot, pdh, pdc, pdl = day_bn
    or_c = day_spot[day_spot["time"] < "09:30"]
    orl = float(or_c["low"].min())
    scale = pdc / 55000.0 if pdc else 1.0
    rows = []
    for _, row in day_spot.iterrows():
        t = row["time"]
        if "09:30" <= t <= "11:30":
            cl = float(row["close"])
            rows.append((t, cl, (orl - cl) / scale if cl < orl else -1.0))
    return orl, scale, rows

def day_g_filter(dd, mode, day_bn):
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    bn_orl, bn_scale, bn_rows = bn_depth_adj_by_time(day_bn)
    n_scale = info["scale"]; d_n = (orl - info["sig_close"]) / n_scale
    max_bn = max([d for (t, cl, d) in bn_rows if t <= info["signal"] and d > 0], default=None)
    kept = max_bn is not None and max_bn > d_n
    return {"info": info, "orig": orig, "kept": kept, "d_n_adj": round(d_n, 2),
            "max_bn_adj": round(max_bn, 2) if max_bn is not None else None,
            "bn_orl": bn_orl, "net": orig["net"] if kept else None}

def day_g_rescan(dd, mode, day_bn):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    bn_orl, bn_scale, bn_rows = bn_depth_adj_by_time(day_bn)
    bn_by_time = {t: d for (t, cl, d) in bn_rows}
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > "11:30":
            break
        cl = float(c["close"])
        if not (cl < orl and cl < pdl):
            continue
        if mode != "skill":
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if not (or_width <= 360 * scale and room >= 200 * scale):
                continue
        d_n = (orl - cl) / scale
        max_bn = max([d for (tt, cl2, d) in bn_rows if tt <= t and d > 0], default=None)
        if max_bn is not None and max_bn > d_n:
            if i + 1 >= len(cand):
                return {"trade": None, "net": None, "signal": t, "d_n_adj": round(d_n, 2), "max_bn_adj": round(max_bn, 2)}
            s = cand.iloc[i]
            entry = float(cand.iloc[i + 1]["open"]); stop = float(s["high"]); risk = stop - entry
            tr = replay_pe(cand, i + 1, entry, stop, entry - 2 * risk)
            tr.update({"signal": t, "d_n_adj": round(d_n, 2), "max_bn_adj": round(max_bn, 2)})
            return {"trade": tr, "net": tr["net"], "signal": t, "d_n_adj": round(d_n, 2), "max_bn_adj": round(max_bn, 2)}
    return {"trade": None, "net": None, "signal": None, "d_n_adj": None, "max_bn_adj": None}

if __name__ == "__main__":
    spot, daily = load_nifty()
    bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02",
                "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    orig1 = {"2026-01-09": -3745, "2026-02-06": -2275, "2026-03-30": -2055, "2026-04-02": -2115,
             "2026-05-13": -5075, "2026-06-29": -4740, "2026-07-08": -1985, "2026-08-19": -2300}
    win_days = {"2026-01-21": 9280, "2026-02-24": 7350, "2026-03-16": 8940, "2026-03-13": 5400,
                "2026-03-23": 7260, "2026-04-24": 8820, "2026-05-05": 5040, "2026-07-22": 6320,
                "2026-08-12": 6250, "2026-08-27": 3000, "2026-09-29": 3790, "2026-09-07": 2990,
                "2026-10-08": 5440, "2026-10-23": 11390}
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    out = {}
    def summarise(rows, netkey):
        g = sum(1 for x in rows if x.get(netkey) is not None and x[netkey] > 0)
        nt = sum(1 for x in rows if x.get(netkey) is None)
        tot = sum(x[netkey] for x in rows if x.get(netkey) is not None)
        return g, nt, tot

    # baseline check
    print("=== BASELINE CHECK ===")
    for ds in cluster1:
        dd = day_data_nifty(spot, daily, ds)
        o = orig_trade(dd, modes1.get(ds, "v4")) if dd else None
        print(ds, "orig_reported", orig1[ds], "replayed", o[5]["net"] if o and o[5] else None, "signal", o[4]["signal"] if o else None)

    # (d)
    for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1), ("winners", list(win_days), win_days, modesw)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot, daily, ds)
            dbn = day_data_bn(bn_spot, bn_daily, ds)
            r = day_d(dd, modes.get(ds, "v4"), dbn) if dd and dbn else None
            rows.append({"date": ds, "orig_net": orig[ds], "result": r, "day_net": r["day_net"] if r else None})
        out.setdefault("d", {})[label] = rows
        g, nt, tot = summarise(rows, "day_net")
        print(f"\n=== (d) {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
        for x in rows:
            print(x["date"], "orig", x["orig_net"], "morning", x["result"]["morning"] if x["result"] else None, "re", x["result"]["re"] if x["result"] else None, "day", x["day_net"])

    # (e), (f) cluster1 only (winners never stop, so no re-entry; verify explicitly)
    for variant, fn in (("e", day_e),):
        rows = []
        for ds in cluster1:
            dd = day_data_nifty(spot, daily, ds)
            dbn = day_data_bn(bn_spot, bn_daily, ds)
            r = fn(dd, modes1.get(ds, "v4"), dbn) if dd and dbn else None
            rows.append({"date": ds, "orig_net": orig1[ds], "result": r, "day_net": r["day_net"] if r else None})
        out["e"] = rows
        g, nt, tot = summarise(rows, "day_net")
        print(f"\n=== (e) cluster1: day-green {g}/8 total {tot} ===")
        for x in rows:
            print(x["date"], "orig", x["orig_net"], "re", x["result"]["re"] if x["result"] else None, "day", x["day_net"])
        # winners check: do any winner days stop under baseline? (should be none)
        wstop = []
        for ds in win_days:
            dd = day_data_nifty(spot, daily, ds)
            o = orig_trade(dd, modesw.get(ds, "v4")) if dd else None
            if o and o[5] and o[5]["exit"] == "stop":
                wstop.append(ds)
        print("(e) winners that stop under baseline (hence could get a re-entry):", wstop)

    for scan_fwd, label in ((False, "f-day"), (True, "f-scan")):
        rows = []
        for ds in cluster1:
            dd = day_data_nifty(spot, daily, ds)
            r = day_f(dd, modes1.get(ds, "v4"), scan_fwd) if dd else None
            rows.append({"date": ds, "orig_net": orig1[ds], "result": r, "day_net": r["day_net"] if r else None})
        out[label] = rows
        g, nt, tot = summarise(rows, "day_net")
        print(f"\n=== (f) {label} cluster1: day-green {g}/8 total {tot} ===")
        for x in rows:
            print(x["date"], "orig", x["orig_net"], "re", x["result"]["re"] if x["result"] else None, "day", x["day_net"])

    # (g)
    for kind, fn in (("g-filter", day_g_filter), ("g-rescan", day_g_rescan)):
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1), ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds)
                dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = fn(dd, modes.get(ds, "v4"), dbn) if dd and dbn else None
                rows.append({"date": ds, "orig_net": orig[ds], "result": r, "net": r["net"] if r else None})
            out.setdefault(kind, {})[label] = rows
            g, nt, tot = summarise(rows, "net")
            print(f"\n=== (g) {kind} {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                print(x["date"], "orig", x["orig_net"], "->", x["result"])

    with open(os.path.expanduser("~/workspace/trading/combined_confirm_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
