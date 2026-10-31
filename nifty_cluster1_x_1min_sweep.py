"""Family (x) -- 1-MIN REPLAY of (lA). Nifty only, paper only, no orders.

(lA) = BN-confirmed rescan morning + band-filtered re-entry, afternoon
stop-on-first-fail to 15:05. This script replays the SAME logic on 1-min
bars and compares day-by-day to the reproduced 5-min (lA) nets.

1-min adaptations (stated explicitly, as required):
- Bars are labelled by start minute. A 1-min bar labelled HH:MM covers
  HH:MM-HH:MM+1. The 5-min bar labelled HH:MM covered HH:MM-HH:MM+5.
- Opening range (OR) = 1-min bars with label < 09:30 (09:15-09:29, 15 bars).
  OR low = min 1-min low, OR high = max 1-min high. This can differ
  slightly from the 5-min OR (3 bars) on the same day; both are reported.
- BN break time = first 1-min BN bar with label >= 09:30 and <= 11:30
  whose close < BN 1-min OR low. (5-min: first 5-min bar, label <= 11:30,
  close < BN 5-min OR low.) The 1-min break can therefore fall inside
  the 5-min bar that the 5-min engine labelled as the break.
- Nifty rescan = first 1-min Nifty bar with label >= BN break label and
  <= 11:30 whose close < Nifty 1-min OR low AND < PDL. V4 mode
  additionally requires OR width <= 360*scale and room >= 200*scale
  (room = close minus highest PD level below close, or infinity if none).
  Skill mode skips the room/width filter. (Same conditions as 5-min
  rescan_trade, only the bar grid changes.)
- Entry = next 1-min bar open, stop = signal-bar (1-min) high,
  target = entry - 2*risk, square-off at the 15:10 1-min bar close,
  100 shares, Rs40/trade. Stop checked before target on every bar
  including the entry bar (same within-bar convention as 5-min; within
  a single 1-min bar, ordering is still unobserved).
- Re-entry (only after a morning stop): scan 1-min bars after the stop
  bar; candidate = close < Nifty 1-min OR low; window labels <= 15:05.
  Morning phase (label <= 11:30): skip band-failing candidates.
  Afternoon phase (label > 11:30): FIRST band-failing candidate ENDS
  the scan (lA stop-on-first-fail). Band = risk in [10, rescan risk].
  Entry next 1-min open, stop candidate-bar high, target 2*risk, Rs40.
- PD levels (PDH/PDC/PDL) and scale come from the existing 5-min daily
  cache, exactly as the 5-min engine uses them, so only the bar grid
  changes, not the levels.
- Green = day net > 0. No-trade counted separately from green.
  Risks under ~5 points are flagged as knife-edge artefacts.
"""
import os, sys, json, math
import pandas as pd
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_5m, day_data as day_data_5m
from extended_window_sweep import day_variant as day_5m_lA
from reentry_filter_sweep import load_bn as load_5m_bn, day_data_bn as day_data_5m_bn

QTY, COST = 100, 40.0
BASE1 = os.path.expanduser("~/workspace/trading/data/1min")

def load_1m(idx, day):
    df = pd.read_csv(os.path.join(BASE1, idx, f"spot_1m_{day}.csv"))
    df["time"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M")
    return df.sort_values("time").reset_index(drop=True)

def replay_pe_1m(candles, start_idx, entry, stop, target):
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
                    "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": cl,
                    "net": round((entry - cl) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
            "net": round((entry - float(c["close"])) * QTY - COST, 2), "risk": round(risk, 2)}

def or_levels(df):
    or_c = df[df["time"] < "09:30"]
    return float(or_c["high"].max()), float(or_c["low"].min())

def bn_break_1m(bn_df):
    orh, orl = or_levels(bn_df)
    for _, c in bn_df.iterrows():
        t = c["time"]
        if "09:30" <= t <= "11:30" and float(c["close"]) < orl:
            return t, orl, orh
    return None, orl, orh

def rescan_trade_1m(n_df, pdh, pdc, pdl, scale, mode, bn_df):
    bt, bn_orl, bn_orh = bn_break_1m(bn_df)
    if bt is None:
        return None
    orh, orl = or_levels(n_df)
    or_width = orh - orl
    cand = n_df[n_df["time"] >= "09:30"].reset_index(drop=True)
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
    tr = replay_pe_1m(cand, sig + 1, entry, stop, target)
    tr.update({"signal": s["time"], "bn_break": bt, "orl": orl})
    return {"candles": cand, "orl": orl, "orh": orh, "sig_idx": sig,
            "info": {"risk": risk, "signal": s["time"]}, "trade": tr,
            "bn_break": bt, "bn_orl": bn_orl}

def scan_reentry_1m(candles, orl, stop_idx, rescan_risk):
    skipped = []
    for k in range(stop_idx + 1, len(candles)):
        c = candles.iloc[k]; t = c["time"]
        if t > "15:05":
            break
        if float(c["close"]) >= orl:
            continue
        if k + 1 >= len(candles):
            skipped.append((t, "no_next_bar")); break
        entry = float(candles.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
        afternoon = t > "11:30"
        band_ok = risk > 0 and 10 <= risk <= rescan_risk
        if afternoon and not band_ok:
            skipped.append((t, f"afternoon_first_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]_scan_ends"))
            break
        if not band_ok:
            skipped.append((t, f"band_fail_risk={risk:.2f}_band=[10,{rescan_risk:.2f}]")); continue
        re = replay_pe_1m(candles, k + 1, entry, stop, entry - 2 * risk)
        re.update({"re_signal": t, "variant": "lA-1min"})
        return re, skipped
    return None, skipped

def day_1m(n_df, bn_df, pdh, pdc, pdl, scale, mode):
    r = rescan_trade_1m(n_df, pdh, pdc, pdl, scale, mode, bn_df)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": [], "bn_break": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None, "skipped": [], "bn_break": r["bn_break"]}
    if tr.get("exit") != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": [], "bn_break": r["bn_break"]}
    re, skipped = scan_reentry_1m(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped, "bn_break": r["bn_break"]}

def diagnostic_entry_bar(day, bar_label, entry, stop):
    """Minute-by-minute path inside one 5-min entry bar (5 consecutive 1-min bars)."""
    import datetime
    df = load_1m("NIFTY", day)
    b = datetime.datetime.strptime(bar_label, "%H:%M")
    want = [(b + datetime.timedelta(minutes=k)).strftime("%H:%M") for k in range(5)]
    mins = df[df["time"].isin(want)]
    rows = [{"time": r["time"], "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"])} for _, r in mins.iterrows()]
    stop_min = None; mfe_before = 0.0
    for r in rows:
        if r["high"] >= stop:
            stop_min = r["time"]; break
        mfe_before = max(mfe_before, entry - r["low"])
    mfe_bar = round(entry - min(r["low"] for r in rows), 2)
    return {"day": day, "entry_bar": bar_label, "entry": entry, "stop": stop,
            "risk": round(stop - entry, 2), "minutes": rows,
            "first_stop_touch_minute": stop_min,
            "mfe_before_stop_minute": round(mfe_before, 2),
            "mfe_within_entry_bar": mfe_bar,
            "moved_favourably_first": mfe_before > 0,
            "stop_touched_in_entry_bar": stop_min is not None}

if __name__ == "__main__":
    spot5, daily5 = load_5m(); bn5, bnd5 = load_5m_bn()
    cluster1 = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02",
                "2026-05-13", "2026-06-29", "2026-07-08", "2026-08-19"]
    win_days = ["2026-01-21", "2026-02-24", "2026-03-16", "2026-03-13", "2026-03-23",
                "2026-04-24", "2026-05-05", "2026-07-22", "2026-08-12", "2026-08-27",
                "2026-09-29", "2026-09-07", "2026-10-08", "2026-10-23"]
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    out = {"diagnostic": [], "cluster1": [], "winners": []}

    # ---- Diagnostic: 5-min (lA) entry-bar stops + winner contrast ----
    # (entry bar / entry / stop taken from the reproduced 5-min (lA) trades)
    diag_cases = [
        ("2026-03-30", "11:30", 22468.10, 22488.25, "morning"),
        ("2026-04-02", "10:50", 22204.85, 22225.10, "morning"),
        ("2026-04-02", "11:30", 22206.50, 22222.75, "re-entry"),
        ("2026-03-23", "09:55", 22628.55, 22665.05, "winner-morning"),
    ]
    for day, bar, entry, stop, kind in diag_cases:
        d = diagnostic_entry_bar(day, bar, entry, stop)
        d["trade"] = kind
        out["diagnostic"].append(d)
        print(f"DIAG {day} {kind} entry-bar {bar} entry {entry} stop {stop} "
              f"first-stop-minute {d['first_stop_touch_minute']} "
              f"MFE-before-stop {d['mfe_before_stop_minute']} "
              f"favourable-first {d['moved_favourably_first']} "
              f"MFE-in-bar {d['mfe_within_entry_bar']}")
        for r in d["minutes"]:
            print("   ", r)

    # 2 Apr afternoon reversal note (diagnostic only, not a candidate)
    df2 = load_1m("NIFTY", "2026-04-02")
    sub = df2[df2["time"] > "11:33"]
    imax = sub["close"].idxmax()
    out["diag_2apr_afternoon"] = {
        "reentry_stop_minute": "11:33", "close_at_1133": float(df2[df2['time'] == '11:33']['close'].iloc[0]),
        "max_close_after": float(sub.loc[imax, "close"]), "max_close_time": str(sub.loc[imax, "time"]),
        "close_1510": float(df2[df2['time'] == '15:10']['close'].iloc[0])}
    print("DIAG 2Apr afternoon:", out["diag_2apr_afternoon"])

    def summarise(rows):
        g = sum(1 for x in rows if x["day_net_1m"] is not None and x["day_net_1m"] > 0)
        nt = sum(1 for x in rows if x["day_net_1m"] is None)
        tot = sum(x["day_net_1m"] for x in rows if x["day_net_1m"] is not None)
        return g, nt, tot

    for label, days, modes in (("cluster1", cluster1, modes1), ("winners", win_days, modesw)):
        for ds in days:
            dd5 = day_data_5m(spot5, daily5, ds)
            dbn5 = day_data_5m_bn(bn5, bnd5, ds)
            r5 = day_5m_lA(dd5, modes.get(ds, "v4"), dbn5, "lA") if dd5 and dbn5 else None
            net5 = r5["day_net"] if r5 else None
            _, pdh, pdc, pdl, bias, scale = dd5
            n1 = load_1m("NIFTY", ds); b1 = load_1m("BANKNIFTY", ds)
            orh1, orl1 = or_levels(n1); borh1, borl1 = or_levels(b1)
            r1 = day_1m(n1, b1, pdh, pdc, pdl, scale, modes.get(ds, "v4"))
            knife = []
            for tr in (r1["morning"], r1["re"]):
                if tr and tr.get("risk") is not None and tr["risk"] < 5:
                    knife.append(tr)
            row = {"date": ds, "mode": modes.get(ds, "v4"),
                   "day_net_5m_lA": net5,
                   "morning_5m": r5["morning"] if r5 else None,
                   "re_5m": r5["re"] if r5 else None,
                   "orl_1m": orl1, "orh_1m": orh1, "bn_orl_1m": borl1,
                   "bn_break_1m": r1["bn_break"],
                   "morning_1m": r1["morning"], "re_1m": r1["re"],
                   "day_net_1m": r1["day_net"], "skipped_1m": r1["skipped"],
                   "knife_edge_trades": knife}
            out[label].append(row)
            print(f"{label} {ds} 5m(lA) {net5} -> 1m {r1['day_net']} "
                  f"morning1m {r1['morning']} re1m {r1['re']} skipped {r1['skipped']}")
        rows = out[label]
        g, nt, tot = summarise(rows)
        print(f"=== 1m {label}: green {g}/{len(rows)} no-trade {nt} total {tot} ===")

    g1, nt1, tot1 = summarise(out["cluster1"])
    g2, nt2, tot2 = summarise(out["winners"])
    out["summary_1m"] = {"cluster1": {"green": g1, "no_trade": nt1, "total": tot1},
                         "winners": {"green": g2, "no_trade": nt2, "total": tot2},
                         "combined": tot1 + tot2}
    out["summary_5m_lA_reproduced"] = {
        "cluster1_total": sum(x["day_net_5m_lA"] for x in out["cluster1"] if x["day_net_5m_lA"] is not None),
        "winners_total": sum(x["day_net_5m_lA"] for x in out["winners"] if x["day_net_5m_lA"] is not None)}
    print("SUMMARY 1m:", out["summary_1m"])
    print("SUMMARY 5m reproduced:", out["summary_5m_lA_reproduced"])
    with open(os.path.expanduser("~/workspace/trading/nifty_cluster1_x_1min_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
