"""Survival-gated exit + Cluster3 discriminator + Cluster2 stall+partial.
NIFTY only, paper only. Reuses timing_sweep.load/day_data and
retest_stall_sweep.candles_for / find_first / replay helpers where
possible, but implements survival-gated partial explicitly.

Definitions (reproducible, no look-ahead beyond the bar being replayed):
- Baseline: entry = next bar open after signal, stop = signal high (PE)
  / low (CE), target = entry -/+ 2*risk, stop before target each bar,
  square-off 15:10, 100 shares, Rs40/trade.
- Partial 45%: level = entry -/+ 0.9*risk (45% of 2*risk target distance).
  Book 50 shares there, trail remaining 50 to breakeven (entry).
- SURVIVAL GATE, interpretation B (primary, 'eligibility'):
  The partial is eligible ONLY if the trade is still open at the open
  of bar sig+1+N (i.e. it survived N full bars after the entry bar).
  At that gate open, if the best favourable extreme so far already
  reached the partial level, book 50 at the partial level immediately
  and trail the rest to breakeven, then replay gate bar onward with
  BE stop. If not yet reached, arm the partial from the gate bar onward
  (adverse first, then partial, then target each bar).
  Trades stopped before the gate, and trades reaching target before
  the gate, are untouched (full stop / full target).
- SURVIVAL GATE, interpretation A (strict-arm, reported for honesty):
  Partial trigger is simply not checked until the gate bar; a partial
  level passed before the gate does NOT book retroactively. Only bars
  from the gate onward can trigger it. This is stricter and, as the
  results show, kills early partials that Cluster 3 earned before N.
- Stall: as in retest_stall_sweep.stall — a bar that does not make a
  new favourable extreme increments counter, new extreme resets to 0,
  exit at that bar's close when counter reaches N, stop/target first.
- Cluster2 combined (stall10 + partial45): both rules live. Partial
  (un-gated, as in prior sweep) books 50 and trails rest to BE;
  stall counter keeps running on favourable extremes; on a bar,
  order is: adverse (current stop, original or BE) first, then partial,
  then target, then stall exit at close for the still-open quantity
  (100 if unbooked, 50 if booked). Square-off 15:10 same.
"""
import pandas as pd, math, os, json, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
from retest_stall_sweep import candles_for, find_first, stall as stall_fn, partial_trail as partial_fn
BASE = os.path.expanduser("~/workspace/trading")
QTY, COST = 100, 40.0
spot, daily = load()

CL1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
ORIG1 = {"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,"2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
MODE1 = {"2026-04-02":"skill"}
CL3 = ["2026-02-13","2026-04-30","2026-05-18"]
ORIG3 = {"2026-02-13":-3750,"2026-04-30":-3165,"2026-05-18":-3670}
CL2 = [("2026-01-14","11:15",-2785),("2026-10-26","09:55",-8635)]
WIN = {"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,"2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,"2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,"2026-10-08":5440,"2026-10-23":11390}
WINMODE = {"2026-03-23":"skill"}

def ctx(ds):
    return candles_for(ds)

def base_signal(ds, mode, direction="PE", sig_time=None):
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx(ds)
    if direction == "PE":
        sig = find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, "11:30")
    else:
        sig = next((i for i in range(len(candles)) if candles.iloc[i]["time"] == sig_time), None)
    return day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles, sig

def survival(ds, mode, N, interp="B", direction="PE", sig_time=None):
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles, sig = base_signal(ds, mode, direction, sig_time)
    if sig is None or sig+1 >= len(candles):
        return None
    s = candles.iloc[sig]; entry = float(candles.iloc[sig+1]["open"])
    if direction == "PE":
        stop = float(s["high"]); risk = stop-entry; target = entry-2*risk; plevel = entry-0.9*risk
    else:
        stop = float(s["low"]); risk = entry-stop; target = entry+2*risk; plevel = entry+0.9*risk
    if risk <= 0:
        return {"signal": s["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
    gate_idx = sig+1+N  # first bar whose open is after N full bars past entry bar
    booked = False; pnet = 0.0; ptime = None; cur_stop = stop
    # helper for a bar with current rules
    def run_bar(j, allow_partial):
        nonlocal booked, pnet, ptime, cur_stop
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if direction == "PE":
            if hi >= cur_stop:
                net = round(pnet - (cur_stop-entry)*50 - COST, 2) if booked else round(-(cur_stop-entry)*QTY-COST, 2)
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop_after_partial" if booked else "stop", "exit_time": t, "exit_price": cur_stop, "net": net, "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
            if allow_partial and not booked and lo <= plevel:
                booked = True; ptime = t; pnet = (entry-plevel)*50; cur_stop = entry
            if lo <= target:
                if booked:
                    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target_after_partial", "exit_time": t, "exit_price": target, "net": round(pnet+(entry-target)*50-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": t, "exit_price": target, "net": round((entry-target)*QTY-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
            if t == "15:10":
                if booked:
                    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off_after_partial", "exit_time": t, "exit_price": cl, "net": round(pnet+(entry-cl)*50-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": t, "exit_price": cl, "net": round((entry-cl)*QTY-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
        else:
            if lo <= cur_stop:
                net = round(pnet + (cur_stop-entry)*50 - COST, 2) if booked else round(-(entry-cur_stop)*QTY-COST, 2)
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop_after_partial" if booked else "stop", "exit_time": t, "exit_price": cur_stop, "net": net, "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
            if allow_partial and not booked and hi >= plevel:
                booked = True; ptime = t; pnet = (plevel-entry)*50; cur_stop = entry
            if hi >= target:
                if booked:
                    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target_after_partial", "exit_time": t, "exit_price": target, "net": round(pnet+(target-entry)*50-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": t, "exit_price": target, "net": round((target-entry)*QTY-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
            if t == "15:10":
                if booked:
                    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off_after_partial", "exit_time": t, "exit_price": cl, "net": round(pnet+(cl-entry)*50-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": t, "exit_price": cl, "net": round((cl-entry)*QTY-COST,2), "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"] if gate_idx < len(candles) else None}
        return None
    # bars before gate: no partial
    for j in range(sig+1, min(gate_idx, len(candles))):
        r = run_bar(j, allow_partial=False)
        if r: return r
    if gate_idx >= len(candles):
        c = candles.iloc[-1]; cl = float(c["close"])
        net = round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)
        return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": cl, "net": net, "partial_time": None, "gate_bar": None}
    # gate reached: interpretation B books retroactively if MFE already >= partial
    if interp == "B":
        pre = candles.iloc[sig+1:gate_idx]
        best = float(pre["low"].min()) if direction=="PE" else float(pre["high"].max())
        if (direction=="PE" and best <= plevel) or (direction=="CE" and best >= plevel):
            booked = True; ptime = candles.iloc[gate_idx]["time"]+"(gate, earned earlier)"; pnet = (entry-plevel)*50 if direction=="PE" else (plevel-entry)*50; cur_stop = entry
    for j in range(gate_idx, len(candles)):
        r = run_bar(j, allow_partial=True)
        if r: return r
    c = candles.iloc[-1]; cl = float(c["close"])
    if booked:
        net = round(pnet + ((entry-cl)*50 if direction=="PE" else (cl-entry)*50) - COST, 2)
        ex = "square_off_after_partial"
    else:
        net = round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)
        ex = "square_off"
    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": ex, "exit_time": c["time"], "exit_price": cl, "net": net, "partial_time": ptime, "gate_bar": candles.iloc[gate_idx]["time"]}

def stall_partial_ce(ds, sig_time, N=10, frac=0.45):
    """Cluster 2 combined: stall N + partial frac, CE. Order per bar:
    adverse (current stop) -> partial -> target -> stall exit at close."""
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx(ds)
    sig = next((i for i in range(len(candles)) if candles.iloc[i]["time"] == sig_time), None)
    if sig is None or sig+1 >= len(candles): return None
    s = candles.iloc[sig]; entry = float(candles.iloc[sig+1]["open"])
    stop = float(s["low"]); risk = entry-stop; target = entry+2*risk; plevel = entry+frac*2*risk
    if risk <= 0: return {"signal": s["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None}
    booked=False; pnet=0.0; ptime=None; cur_stop=stop
    best=float(candles.iloc[sig+1]["high"]); counter=0
    def bar_result(j, is_entry_bar):
        nonlocal booked, pnet, ptime, cur_stop, best, counter
        c=candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if lo <= cur_stop:
            net = round(pnet+(cur_stop-entry)*50-COST,2) if booked else round(-(entry-cur_stop)*QTY-COST,2)
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop_after_partial" if booked else "stop", "exit_time": t, "exit_price": cur_stop, "net": net, "partial_time": ptime}
        if not booked and hi >= plevel:
            booked=True; ptime=t; pnet=(plevel-entry)*50; cur_stop=entry
        if hi >= target:
            if booked:
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target_after_partial", "exit_time": t, "exit_price": target, "net": round(pnet+(target-entry)*50-COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": t, "exit_price": target, "net": round((target-entry)*QTY-COST,2), "partial_time": ptime}
        if t=="15:10":
            if booked:
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off_after_partial", "exit_time": t, "exit_price": cl, "net": round(pnet+(cl-entry)*50-COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": t, "exit_price": cl, "net": round((cl-entry)*QTY-COST,2), "partial_time": ptime}
        if not is_entry_bar:
            if hi > best: best=hi; counter=0
            else: counter+=1
            if counter>=N:
                qty=50 if booked else 100
                rem=(cl-entry)*qty
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": f"stall{N}"+("_after_partial" if booked else ""), "exit_time": t, "exit_price": cl, "net": round(pnet+rem-COST,2), "partial_time": ptime}
        return None
    r=bar_result(sig+1, True)
    if r: return r
    for j in range(sig+2, len(candles)):
        r=bar_result(j, False)
        if r: return r
    c=candles.iloc[-1]; cl=float(c["close"])
    net = round(pnet+(cl-entry)*50-COST,2) if booked else round((cl-entry)*QTY-COST,2)
    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off"+("_after_partial" if booked else ""), "exit_time": c["time"], "exit_price": cl, "net": net, "partial_time": ptime}

def features(ds, mode, direction="PE", sig_time=None):
    """Signal-time features only (no look-ahead). Returns dict."""
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles, sig = base_signal(ds, mode, direction, sig_time)
    if sig is None: return {"date": ds, "signal": None}
    s = candles.iloc[sig]
    # day open / first bar 09:15
    pre = day_spot[day_spot["time"] < "09:30"]
    first = pre.iloc[0] if len(pre) else None
    day_open = float(first["open"]) if first is not None else None
    first_range = float(first["high"]-first["low"]) if first is not None else None
    gap = (day_open-pdc)/pdc*100 if day_open else None
    rng_prev = pdh-pdl
    cs = (pdc-pdl)/rng_prev*100 if rng_prev else 50.0
    sig_idx_in_day = sig  # candles start 09:30, so index 0 = 09:30 bar
    close = float(s["close"])
    levels_below = sorted([l for l in set([pdh,pdc,pdl]) if l < close])
    room = close-max(levels_below) if levels_below else float("inf")
    entry = float(candles.iloc[sig+1]["open"]) if sig+1 < len(candles) else None
    if direction=="PE":
        risk = float(s["high"])-entry if entry else None
    else:
        risk = entry-float(s["low"]) if entry else None
    return {"date": ds, "signal": s["time"], "bars_since_0930": int(sig_idx_in_day),
            "gap_pct": round(gap,3) if gap is not None else None,
            "bias_score": round(cs,1), "bias": bias,
            "or_low": orl, "or_high": orh, "or_width": round(orh-orl,2),
            "pdh": pdh, "pdc": pdc, "pdl": pdl, "prev_range": round(rng_prev,2),
            "first_bar_range": round(first_range,2) if first_range else None,
            "sig_candle_range": round(float(s["high"])-float(s["low"]),2),
            "sig_close_below_orl": round(orl-close,2),
            "sig_close_below_pdl": round(pdl-close,2),
            "room_below": round(room,2) if room!=float("inf") else None,
            "entry": entry, "risk": round(risk,2) if risk else None}

def summ(rows):
    traded=[r for r in rows if r and r.get("net") is not None]
    green=sum(1 for r in traded if r["net"]>0)
    nt=sum(1 for r in rows if r is None or r.get("net") is None)
    loss=sum(1 for r in traded if r["net"]<=0)
    return {"green": green, "no_trade": nt, "still_loss_or_scratch": loss, "traded_total": round(sum(r["net"] for r in traded),2), "n_traded": len(traded)}

if __name__ == "__main__":
    out={}
    for interp in ("B","A"):
        for N in (10,20):
            for label, days, origs, modes, direction, sigmap in [
                ("cluster3", CL3, ORIG3, {}, "PE", {}),
                ("cluster1", CL1, ORIG1, MODE1, "PE", {}),
                ("cluster2", [d for d,_,_ in CL2], {d:o for d,_,o in CL2}, {}, "CE", {d:s for d,s,_ in CL2}),
                ("winning_pe", list(WIN.keys()), WIN, WINMODE, "PE", {}),
            ]:
                rows=[]
                for ds in days:
                    t=survival(ds, modes.get(ds,"v4"), N, interp, direction, sigmap.get(ds))
                    rows.append({"date": ds, "orig_net": origs[ds], "trade": t})
                key=f"survival_{interp}_N{N}_{label}"
                out[key]={"rows": rows, "summary": summ([r["trade"] for r in rows])}
                print(f"\n=== SURVIVAL {interp} N={N} {label} {out[key]['summary']} ===")
                for r in rows: print(r["date"], r["orig_net"], "->", r["trade"])
    # discriminator features
    feats=[]
    for ds in CL1:
        f=features(ds, MODE1.get(ds,"v4"), "PE"); f["group"]="Cluster1"; feats.append(f)
    for ds in CL3:
        f=features(ds, "v4", "PE"); f["group"]="Cluster3"; feats.append(f)
    for ds in WIN:
        f=features(ds, WINMODE.get(ds,"v4"), "PE"); f["group"]="WinnerPE"; feats.append(f)
    out["discriminator_features"]=feats
    print("\n=== DISCRIMINATOR FEATURES ===")
    for f in feats: print(f)
    # Cluster2 combined
    c2rows=[]
    for ds, st, onet in CL2:
        t=stall_partial_ce(ds, st, 10, 0.45)
        c2rows.append({"date": ds, "orig_net": onet, "signal": st, "trade": t})
    out["cluster2_stall10_partial45"]={"rows": c2rows, "summary": summ([r["trade"] for r in c2rows])}
    print(f"\n=== CLUSTER2 stall10+partial45 {out['cluster2_stall10_partial45']['summary']} ===")
    for r in c2rows: print(r["date"], r["orig_net"], "->", r["trade"])
    with open(os.path.join(BASE, "survival_gated_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
