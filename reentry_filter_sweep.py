"""Re-entry-filter sweep, NIFTY Cluster 1 + 14 PE winners. Paper only.
Families (untried only):
 (a) Re-entry filtered by its OWN risk.
 (b) Re-entry requiring close below the ORIGINAL SIGNAL BAR'S LOW.
 (c) Cross-instrument (Bank Nifty) confirmation for the morning trade.
Common replay (PE): entry=next bar open, stop=signal high, target=entry-2*risk,
stop before target per bar incl. entry bar, square-off 15:10, 100 shares, Rs40.
Green = net > 0. No-trade counted separately from green throughout.
Winners under (a)/(b) are unchanged (a winner never stops, so no re-entry
triggers) -- stated, not hidden; they are still replayed under (c).
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from close_reentry_sweep import orig_trade, replay_pe
from bounce_sizing_sweep import scan

QTY, COST = 100, 40.0
BASE_BN = os.path.expanduser("~/workspace/trading/data/progressive/BANKNIFTY")

def load_bn():
    spot = pd.read_csv(os.path.join(BASE_BN, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE_BN, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def day_data_bn(spot, daily, datestr):
    d = pd.Timestamp(datestr)
    day_spot = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day_spot.empty or prev.empty:
        return None
    y = prev.iloc[-1]
    return day_spot, float(y["high"]), float(y["close"]), float(y["low"])

def bn_break_time(day_bn, pdl, mode):
    """First BN bar >=09:30, <=11:30, close < BN OR low (and < PDL if mode=pdl).
    Returns (time, orl, orh) or (None, orl, orh)."""
    day_spot, pdh, pdc, pdlv = day_bn
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    cand = day_spot[(day_spot["time"] >= "09:30") & (day_spot["time"] <= "11:30")]
    for _, c in cand.iterrows():
        cl = float(c["close"])
        if cl < orl and (mode == "orl" or cl < pdlv):
            return c["time"], orl, orh
    return None, orl, orh

def reentry_candidate(candles, k):
    entry = float(candles.iloc[k+1]["open"]); stop = float(candles.iloc[k]["high"])
    return entry, stop, stop - entry

def reentry_filtered(candles, orl, stop_idx, info, variant):
    """(a) variants. Returns dict like reentry_full: re or None, day_net logic
    handled by caller. scan=True means skip a failing candidate and keep
    scanning; day=True means first candidate only, else no re-entry."""
    scan_fwd = variant.endswith("-SCAN")
    base = variant.replace("-SCAN", "").replace("-DAY", "")
    # base: RF-MIN10, RF-BAND, RF-MAXORIG
    for k in range(stop_idx+1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "11:30":
            break
        if float(c["close"]) >= orl:
            continue
        if k+1 >= len(candles):
            break
        entry, stop, risk = reentry_candidate(candles, k)
        if risk <= 0:
            continue
        ok = False
        if base == "RF-MIN10":
            ok = risk >= 10
        elif base == "RF-BAND":
            ok = 10 <= risk <= info["risk"]
        elif base == "RF-MAXORIG":
            ok = risk <= info["risk"]
        else:
            raise ValueError(base)
        if not ok:
            if scan_fwd:
                continue
            return None
        target = entry - 2*risk
        re = replay_pe(candles, k+1, entry, stop, target)
        re.update({"re_signal": t})
        return re
    return None

def reentry_siglow(candles, orl, stop_idx, info):
    """(b) First bar after stop whose close < original signal bar's low."""
    sig_low = info["sig_low"]
    for k in range(stop_idx+1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "11:30":
            break
        if float(c["close"]) < sig_low:
            if k+1 >= len(candles):
                return None
            entry, stop, risk = reentry_candidate(candles, k)
            if risk <= 0:
                return None
            target = entry - 2*risk
            re = replay_pe(candles, k+1, entry, stop, target)
            re.update({"re_signal": t, "sig_low": sig_low})
            return re
    return None

def day_reentry(dd, mode, fn):
    o = orig_trade(dd, mode)
    if o is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    if orig is None or orig["exit"] != "stop":
        return {"info": info, "orig": orig, "re": None, "day_net": orig["net"] if orig else None}
    re = fn(candles, orl, orig["exit_idx"], info)
    day_net = round(orig["net"] + re["net"], 2) if (orig["net"] is not None and re and re["net"] is not None) else orig["net"]
    return {"info": info, "orig": orig, "re": re, "day_net": day_net}

def xc_filter_day(dd, mode, day_bn, bn_mode):
    """(c) FILTER: original trade only if BN broke by Nifty signal time."""
    o = orig_trade(dd, mode)
    if o is None or day_bn is None:
        return None
    candles, orh, orl, sig_idx, info, orig = o
    bt, bn_orl, bn_orh = bn_break_time(day_bn, day_bn[3], bn_mode)
    kept = bt is not None and bt <= info["signal"]
    return {"info": info, "orig": orig, "bn_break": bt, "bn_orl": bn_orl,
            "kept": kept, "net": orig["net"] if kept else None}

def xc_rescan_day(dd, mode, day_bn, bn_mode):
    """(c) RESCAN: first Nifty V4/Skill breakdown bar at/after BN break time."""
    day_spot, pdh, pdc, pdl, bias, scale = dd
    if day_bn is None:
        return None
    bt, bn_orl, bn_orh = bn_break_time(day_bn, day_bn[3], bn_mode)
    if bt is None:
        return {"bn_break": None, "trade": None, "net": None}
    candles, orh, orl, sig_idx_all = scan(day_spot, pdh, pdc, pdl, scale, mode)
    # scan() returns FIRST breakdown bar; need first breakdown bar >= bt.
    # Re-implement scan loop with time constraint.
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh2 = float(or_c["high"].max()); orl2 = float(or_c["low"].min())
    or_width = orh2 - orl2
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    sig = None
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > "11:30" or t < bt:
            continue
        cl = float(c["close"])
        if cl < orl2 and cl < pdl:
            if mode == "skill":
                sig = i; break
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360*scale and room >= 200*scale:
                sig = i; break
    if sig is None or sig+1 >= len(cand):
        return {"bn_break": bt, "trade": None, "net": None}
    s = cand.iloc[sig]
    entry = float(cand.iloc[sig+1]["open"]); stop = float(s["high"]); risk = stop-entry
    target = entry - 2*risk
    tr = replay_pe(cand, sig+1, entry, stop, target)
    tr.update({"signal": s["time"], "bn_break": bt})
    return {"bn_break": bt, "trade": tr, "net": tr["net"]}

if __name__ == "__main__":
    spot, daily = load_nifty()
    bn_spot, bn_daily = load_bn()
    cluster1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02",
                "2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    orig1 = {"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,
             "2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
    win_days = {"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,
                "2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,
                "2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,
                "2026-10-08":5440,"2026-10-23":11390}
    modes1 = {"2026-04-02":"skill"}; modesw = {"2026-03-23":"skill"}
    out = {}
    # --- (a) + (b) Cluster 1 ---
    variants_a = ["RF-MIN10-SCAN","RF-MIN10-DAY","RF-BAND-SCAN","RF-BAND-DAY","RF-MAXORIG-SCAN","RF-MAXORIG-DAY"]
    for v in variants_a:
        rows = []
        for ds in cluster1:
            dd = day_data_nifty(spot, daily, ds)
            r = day_reentry(dd, modes1.get(ds,"v4"), lambda c,o,s,i, v=v: reentry_filtered(c,o,s,i,v)) if dd else None
            rows.append({"date": ds, "orig_net": orig1[ds], "result": r})
        out.setdefault("reentry_risk", {})[v] = rows
        dg = sum(1 for x in rows if x["result"] and x["result"]["day_net"] is not None and x["result"]["day_net"]>0)
        tot = sum(x["result"]["day_net"] for x in rows if x["result"] and x["result"]["day_net"] is not None)
        print(f"\n=== (a) {v}: day-green {dg}/8 total {tot} ===")
        for x in rows:
            r=x["result"]; print(x["date"], "orig", x["orig_net"], "re", r["re"] if r else None, "day", r["day_net"] if r else None)
    rows=[]
    for ds in cluster1:
        dd = day_data_nifty(spot, daily, ds)
        r = day_reentry(dd, modes1.get(ds,"v4"), lambda c,o,s,i: reentry_siglow(c,o,s,i)) if dd else None
        rows.append({"date": ds, "orig_net": orig1[ds], "result": r})
    out["reentry_siglow"] = rows
    dg = sum(1 for x in rows if x["result"] and x["result"]["day_net"] is not None and x["result"]["day_net"]>0)
    tot = sum(x["result"]["day_net"] for x in rows if x["result"] and x["result"]["day_net"] is not None)
    print(f"\n=== (b) RB-SIGLOW: day-green {dg}/8 total {tot} ===")
    for x in rows:
        r=x["result"]; print(x["date"], "orig", x["orig_net"], "sig_low", r["info"]["sig_low"] if r else None, "re", r["re"] if r else None, "day", r["day_net"] if r else None)
    # --- (c) Cluster 1 + winners, filter and rescan ---
    for bn_mode in ["orl","pdl"]:
        for kind in ["FILTER","RESCAN"]:
            rows=[]
            for ds in cluster1:
                dd = day_data_nifty(spot, daily, ds)
                dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = xc_filter_day(dd, modes1.get(ds,"v4"), dbn, bn_mode) if kind=="FILTER" else xc_rescan_day(dd, modes1.get(ds,"v4"), dbn, bn_mode)
                rows.append({"date": ds, "orig_net": orig1[ds], "result": r})
            out.setdefault("xc_cluster1", {})[f"{kind}-{bn_mode.upper()}"] = rows
            if kind=="FILTER":
                g=sum(1 for x in rows if x["result"] and x["result"]["net"] is not None and x["result"]["net"]>0)
                nt=sum(1 for x in rows if x["result"] and not x["result"]["kept"])
                tot=sum(x["result"]["net"] for x in rows if x["result"] and x["result"]["net"] is not None)
            else:
                g=sum(1 for x in rows if x["result"] and x["result"]["net"] is not None and x["result"]["net"]>0)
                nt=sum(1 for x in rows if x["result"] and x["result"]["trade"] is None)
                tot=sum(x["result"]["net"] for x in rows if x["result"] and x["result"]["net"] is not None)
            print(f"\n=== (c) {kind}-{bn_mode.upper()} Cluster1: green {g}/8 no-trade {nt} total {tot} ===")
            for x in rows:
                print(x["date"], "orig", x["orig_net"], "->", x["result"])
            # winners
            wrows=[]
            for ds, onet in win_days.items():
                dd = day_data_nifty(spot, daily, ds)
                dbn = day_data_bn(bn_spot, bn_daily, ds)
                r = xc_filter_day(dd, modesw.get(ds,"v4"), dbn, bn_mode) if kind=="FILTER" else xc_rescan_day(dd, modesw.get(ds,"v4"), dbn, bn_mode)
                wrows.append({"date": ds, "orig_net": onet, "result": r})
            out.setdefault("xc_winners", {})[f"{kind}-{bn_mode.upper()}"] = wrows
            if kind=="FILTER":
                wg=sum(1 for x in wrows if x["result"] and x["result"]["net"] is not None and x["result"]["net"]>0)
                wnt=sum(1 for x in wrows if x["result"] and not x["result"]["kept"])
                wtot=sum(x["result"]["net"] for x in wrows if x["result"] and x["result"]["net"] is not None)
            else:
                wg=sum(1 for x in wrows if x["result"] and x["result"]["net"] is not None and x["result"]["net"]>0)
                wnt=sum(1 for x in wrows if x["result"] and x["result"]["trade"] is None)
                wtot=sum(x["result"]["net"] for x in wrows if x["result"] and x["result"]["net"] is not None)
            print(f"--- (c) {kind}-{bn_mode.upper()} Winners: green {wg}/14 no-trade {wnt} total {wtot} ---")
            for x in wrows:
                print(x["date"], "orig", x["orig_net"], "->", x["result"])
    with open(os.path.expanduser("~/workspace/trading/reentry_filter_sweep_raw.json"),"w") as f:
        json.dump(out, f, indent=2, default=str)
