"""Triple / untried-combination sweep (h)-(k), NIFTY Cluster 1 + 14 PE winners. Paper only.
Untried combinations ONLY -- do not re-run (a)-(g) or any earlier family alone.
Common replay (PE): entry=next bar open, stop=signal high, target=entry-2*risk
unless (i) says otherwise, stop before target per bar incl. entry bar,
square-off 15:10, 100 shares, Rs40/trade. Green = net > 0.
No-trade counted separately from green. Pass bar: 60% green (5/8) AND
Cluster 1 total positive AND winners not collapsed.
Morning trade in ALL variants = (d) BN-confirmed rescan morning
(XC-RESCAN-ORL): first V4/Skill breakdown at/after BN break time, <=11:30.
Re-entry scanning is SCAN-SKIP throughout: a candidate failing any
condition is skipped, scanning continues to the window end.
(h) TRIPLE: (d) morning + re-entry satisfying BOTH band [10, rescan risk]
    AND BN-confirmed (BN close on same time label < BN OR low), to 11:30.
    This is (d)+(e) together, tested only separately before.
(i) RECOVERY-TARGET: (d) morning + band-filtered re-entry (to 11:30),
    but re-entry target distance = (morning loss magnitude + Rs40)/100
    + 5 points margin. Morning loss magnitude = |morning net| (includes
    its Rs40 cost). So a target hit gives day net = +Rs500 exactly
    (re-entry net = mag+500, day = -mag + mag+500), before any
    stop/square-off outcome. Stop = re-entry bar high, unchanged.
    If recovery distance <= 0 it is not used; it is always >0 here
    because morning net is a stop loss.
(j) RS RE-ENTRY: (d) morning + band-filtered re-entry (to 11:30) whose
    bar ALSO satisfies BN depth_adj > Nifty re-entry depth_adj,
    depth_adj = (OR low - close)/scale, scale = prev close/55000
    per index. This moves the (g) magnitude condition to the 2nd trade.
(k) (d)-EXTENDED: (d) morning + band-filtered re-entry scanning to
    15:05 (not 11:30). Only as a combination with (d); RE-EXT alone
    is NOT re-run. A re-entry signal at 15:05 has no next bar, so it
    yields no trade (replay_pe returns None) -- recorded as no re-entry.
Winners: same morning + re-entry rules generally; a rescan winner
that stops would get a re-entry (verified, not assumed).
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import replay_pe
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade

QTY, COST = 100, 40.0

def bn_info(day_bn):
    day_spot, pdh, pdc, pdl = day_bn
    or_c = day_spot[day_spot["time"] < "09:30"]
    orl = float(or_c["low"].min()); orh = float(or_c["high"].max())
    cmap = {row["time"]: float(row["close"]) for _, row in day_spot.iterrows()}
    scale = pdc / 55000.0 if pdc else 1.0
    return orl, orh, cmap, scale, pdc

def replay_pe_actual(candles, start_idx, entry, stop, target):
    """Like replay_pe, but net is computed from the ACTUAL exit price,
    not from 2*risk. Required for (i), where target distance != 2*risk.
    For a target exit: net = (entry-target)*100-40. Stop/square-off
    nets coincide with replay_pe, but are recomputed here for safety."""
    risk = stop - entry
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk",
                "exit_time": None, "exit_idx": None, "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        if hi >= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if lo <= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": target,
                    "net": round((entry - target) * QTY - COST, 2), "risk": round(risk, 2)}
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2)}

def reentry_scan(candles, orl, stop_idx, rescan_risk, window, variant, bn=None, n_scale=None, morning_net=None):
    """Scan candidates after stop_idx. Returns re dict or None, plus skip detail."""
    skipped = []
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > window:
            break
        if float(c["close"]) >= orl:
            continue
        if k + 1 >= len(candles):
            skipped.append((t, "no_next_bar")); break
        entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
        if risk <= 0:
            skipped.append((t, "risk<=0")); continue
        if not (10 <= risk <= rescan_risk):
            skipped.append((t, f"band_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]")); continue
        if variant == "h":
            bn_orl, _, cmap, _, _ = bn
            bn_close = cmap.get(t)
            if bn_close is None or not (bn_close < bn_orl):
                skipped.append((t, f"bn_confirm_fail_bnclose={bn_close}_bn_orl={bn_orl}")); continue
            target = entry - 2 * risk
        elif variant == "j":
            bn_orl, _, cmap, bn_scale, _ = bn
            bn_close = cmap.get(t)
            d_n = (orl - float(c["close"])) / n_scale
            d_bn = (bn_orl - bn_close) / bn_scale if bn_close is not None else -1.0
            if not (d_bn > d_n):
                skipped.append((t, f"rs_fail_bn_adj={d_bn:.2f}_nifty_adj={d_n:.2f}")); continue
            target = entry - 2 * risk
        elif variant == "i":
            mag = abs(morning_net)
            dist = (mag + COST) / 100.0 + 5.0
            target = entry - dist
        elif variant == "k":
            target = entry - 2 * risk
        else:
            raise ValueError(variant)
        # (i) must use actual-distance net; replay_pe hardcodes 2*risk net,
        # which would overstate every recovery-target payoff.
        re = replay_pe_actual(candles, k + 1, entry, stop, target) if variant == "i" else replay_pe(candles, k + 1, entry, stop, target)
        re.update({"re_signal": t, "variant": variant, "target_dist": round(entry - target, 2)})
        return re, skipped
    return None, skipped

def day_variant(dd, mode, day_bn, variant, window):
    r = rescan_trade(dd, mode, day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None, "skipped": []}
    if tr.get("exit") != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    bn = bn_info(day_bn)
    n_scale = dd[5]
    re, skipped = reentry_scan(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"],
                               window, variant, bn=bn, n_scale=n_scale, morning_net=tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped,
            "bn_break": tr.get("bn_break")}

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
    variants = [("h", "11:30"), ("i", "11:30"), ("j", "11:30"), ("k", "15:05")]
    out = {}
    def summarise(rows):
        g = sum(1 for x in rows if x["day_net"] is not None and x["day_net"] > 0)
        nt = sum(1 for x in rows if x["day_net"] is None)
        tot = sum(x["day_net"] for x in rows if x["day_net"] is not None)
        return g, nt, tot
    # baseline check: (d) morning reproduction
    print("=== BASELINE CHECK: (d) mornings ===")
    for ds in cluster1:
        dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
        r = rescan_trade(dd, modes1.get(ds, "v4"), dbn) if dd and dbn else None
        print(ds, "rescan_morning", r["trade"] if r else None)
    for v, window in variants:
        for label, days, orig, modes in (("cluster1", cluster1, orig1, modes1),
                                         ("winners", list(win_days), win_days, modesw)):
            rows = []
            for ds in days:
                dd = day_data_nifty(spot, daily, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = day_variant(dd, modes.get(ds, "v4"), dbn, v, window) if dd and dbn else None
                rows.append({"date": ds, "orig_net": orig[ds], "result": r,
                             "day_net": r["day_net"] if r else None})
            out.setdefault(v, {})[label] = rows
            g, nt, tot = summarise(rows)
            print(f"\n=== ({v}) window {window} {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")
            for x in rows:
                res = x["result"]
                print(x["date"], "orig", x["orig_net"], "morning",
                      (res["morning"]["signal"], res["morning"]["net"], res["morning"]["exit"]) if res and res["morning"] else None,
                      "re", res["re"] if res else None, "day", x["day_net"],
                      "skipped", res["skipped"] if res else None)
    with open(os.path.expanduser("~/workspace/trading/triple_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
