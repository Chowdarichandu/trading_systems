"""Retest-breakdown + Cluster3 partial + stall sweeps, NIFTY only, paper only.
Reuses timing_sweep load/day_data. Exit order: stop before target on each
bar, including entry bar, square-off 15:10. 100 shares, Rs40/trade.
Retest definition (distinct from second-close and from re-entry):
 - First qualifying breakdown (V4 setup2 PE, or Skill OR for 2026-04-02 /
   2026-03-23) is SKIPPED entirely, no loss booked.
 - Bounce = first later bar whose CLOSE >= OR low (back into/above OR).
 - Second breakdown = first later bar whose close < OR low and < PDL
   (same V4/Skill conditions as first, incl. room/width for V4).
 - Entry = next bar open after second signal, stop = second signal high,
   target = entry - 2*risk. R1: second signal must be <=11:30.
   R2: second signal any time (up to last bar that still allows an entry
   bar before 15:10); reported separately so R1 is not cherry-picked.
Cluster3 partial: original entry/stop/target; partial_level = entry -
 frac*2*risk where frac = 0.50/0.45/0.40 of target distance; 50 shares
 booked there, remaining stop moved to breakeven (entry). Adverse
 (current stop) checked before favourable (partial/target) each bar.
Stall: original entry/stop/target; track best favourable low (PE) /
 high (CE) from entry bar onward. A bar that does not make a new
 favourable extreme increments the stall counter; a new extreme resets
 it to 0. When counter reaches N (10 or 20), exit at that bar's close
 (stop/target checked first on that bar). Stall counting starts on the
 bar AFTER the entry bar.
"""
import pandas as pd, math, os, json, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
BASE = os.path.expanduser("~/workspace/trading")
QTY, COST = 100, 40.0
spot, daily = load()

def candles_for(ds):
    dd = day_data(spot, daily, ds)
    if not dd: return None
    day_spot, pdh, pdc, pdl, bias, scale = dd
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    return day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles

def qualifies(c, orl, pdl, orh, scale, mode):
    close = float(c["close"])
    if not (close < orl and close < pdl): return False
    if mode == "skill": return True
    # room as in original scan: levels pdh/pdc/pdl below close
    return True  # room/width checked by caller with levels

def find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, tmax="11:30"):
    levels = sorted(set([pdh, pdc, pdl]))
    for i in range(len(candles)):
        c = candles.iloc[i]
        if c["time"] > tmax: break
        close = float(c["close"])
        if close < orl and close < pdl:
            if mode == "skill": return i
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if (orh - orl) <= 360*scale and room >= 200*scale: return i
    return None

def replay_from_signal(candles, sig_idx, direction="PE"):
    """direction PE: entry next open, stop=sig high, target=entry-2*risk.
    CE mirrored: stop=sig low, target=entry+2*risk. Returns dict or None."""
    if sig_idx is None or sig_idx+1 >= len(candles): return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx+1]["open"])
    if direction == "PE":
        stop = float(sig["high"]); risk = stop - entry; target = entry - 2*risk
        if risk <= 0: return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
        for j in range(sig_idx+1, len(candles)):
            c = candles.iloc[j]
            if float(c["high"]) >= stop:
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop", "exit_time": c["time"], "exit_price": stop, "net": round(-(stop-entry)*QTY-COST,2)}
            if float(c["low"]) <= target:
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": c["time"], "exit_price": target, "net": round((entry-target)*QTY-COST,2)}
            if c["time"] == "15:10":
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry-float(c["close"]))*QTY-COST,2)}
    else:
        stop = float(sig["low"]); risk = entry - stop; target = entry + 2*risk
        if risk <= 0: return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
        for j in range(sig_idx+1, len(candles)):
            c = candles.iloc[j]
            if float(c["low"]) <= stop:
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop", "exit_time": c["time"], "exit_price": stop, "net": round(-(entry-stop)*QTY-COST,2)}
            if float(c["high"]) >= target:
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": c["time"], "exit_price": target, "net": round((target-entry)*QTY-COST,2)}
            if c["time"] == "15:10":
                return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((float(c["close"])-entry)*QTY-COST,2)}
    c = candles.iloc[-1]
    if direction == "PE":
        return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry-float(c["close"]))*QTY-COST,2)}
    return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((float(c["close"])-entry)*QTY-COST,2)}

def retest(ds, mode="v4", strict=True):
    ctx = candles_for(ds)
    if not ctx: return None
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx
    first = find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, "11:30")
    if first is None: return {"first": None, "bounce": None, "second": None, "trade": None}
    bounce = None
    for j in range(first+1, len(candles)):
        if float(candles.iloc[j]["close"]) >= orl: bounce = j; break
    if bounce is None: return {"first": candles.iloc[first]["time"], "bounce": None, "second": None, "trade": None}
    # second: first qualifying breakdown after bounce
    second = None
    # reuse find logic but starting at bounce+1, with its own tmax
    levels = sorted(set([pdh, pdc, pdl]))
    tmax = "11:30" if strict else "15:05"
    for j in range(bounce+1, len(candles)):
        c = candles.iloc[j]
        if c["time"] > tmax: break
        close = float(c["close"])
        if close < orl and close < pdl:
            if mode == "skill": second = j; break
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if (orh - orl) <= 360*scale and room >= 200*scale: second = j; break
    trade = replay_from_signal(candles, second, "PE") if second is not None else None
    return {"first": candles.iloc[first]["time"], "bounce": candles.iloc[bounce]["time"], "second": candles.iloc[second]["time"] if second is not None else None, "trade": trade, "orl": orl, "orh": orh}

def baseline_pe(ds, mode="v4"):
    ctx = candles_for(ds)
    if not ctx: return None
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx
    sig = find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, "11:30")
    return replay_from_signal(candles, sig, "PE") if sig is not None else None

def partial_trail(ds, mode, frac, direction="PE", orig_sig_time=None):
    """frac = fraction of target distance (0.50/0.45/0.40). Original signal
    (first qualifying breakdown) for PE; for CE Cluster2 use given orig
    signal time from failing-cases report (reclaim, not OR scan)."""
    ctx = candles_for(ds)
    if not ctx: return None
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx
    if direction == "PE":
        sig = find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, "11:30")
    else:
        sig = None
        for i in range(len(candles)):
            if candles.iloc[i]["time"] == orig_sig_time: sig = i; break
    if sig is None or sig+1 >= len(candles): return None
    s = candles.iloc[sig]; entry = float(candles.iloc[sig+1]["open"])
    if direction == "PE":
        stop = float(s["high"]); risk = stop-entry; target = entry-2*risk; plevel = entry - frac*2*risk
    else:
        stop = float(s["low"]); risk = entry-stop; target = entry+2*risk; plevel = entry + frac*2*risk
    if risk <= 0: return {"signal": s["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None}
    booked=False; pnet=0.0; ptime=None; cur_stop=stop; trailed=False
    for j in range(sig+1, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        # adverse first
        if direction=="PE" and hi >= cur_stop:
            if booked:
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop_after_partial", "exit_time": t, "exit_price": cur_stop, "net": round(pnet - (cur_stop-entry)*50 - COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop", "exit_time": t, "exit_price": cur_stop, "net": round(-(cur_stop-entry)*QTY-COST,2)}
        if direction=="CE" and lo <= cur_stop:
            if booked:
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop_after_partial", "exit_time": t, "exit_price": cur_stop, "net": round(pnet + (cur_stop-entry)*50 - COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop", "exit_time": t, "exit_price": cur_stop, "net": round(-(entry-cur_stop)*QTY-COST,2)}
        # partial
        if not booked and ((direction=="PE" and lo <= plevel) or (direction=="CE" and hi >= plevel)):
            booked=True; ptime=t
            pnet = (entry-plevel)*50 if direction=="PE" else (plevel-entry)*50
            cur_stop=entry; trailed=True
        # target
        if (direction=="PE" and lo <= target) or (direction=="CE" and hi >= target):
            if booked:
                rem = (entry-target)*50 if direction=="PE" else (target-entry)*50
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target_after_partial", "exit_time": t, "exit_price": target, "net": round(pnet+rem-COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": t, "exit_price": target, "net": round((entry-target)*QTY-COST,2) if direction=="PE" else round((target-entry)*QTY-COST,2)}
        if t=="15:10":
            if booked:
                rem = (entry-cl)*50 if direction=="PE" else (cl-entry)*50
                return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off_after_partial", "exit_time": t, "exit_price": cl, "net": round(pnet+rem-COST,2), "partial_time": ptime}
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": t, "exit_price": cl, "net": round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)}
    c=candles.iloc[-1]
    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry-float(c["close"]))*QTY-COST,2)}

def stall(ds, mode, N, direction="PE", orig_sig_time=None):
    ctx = candles_for(ds)
    if not ctx: return None
    day_spot, pdh, pdc, pdl, bias, scale, orl, orh, candles = ctx
    if direction=="PE":
        sig = find_first(candles, pdh, pdc, pdl, orl, orh, scale, mode, "11:30")
    else:
        sig=None
        for i in range(len(candles)):
            if candles.iloc[i]["time"]==orig_sig_time: sig=i; break
    if sig is None or sig+1>=len(candles): return None
    s=candles.iloc[sig]; entry=float(candles.iloc[sig+1]["open"])
    if direction=="PE":
        stop=float(s["high"]); risk=stop-entry; target=entry-2*risk
    else:
        stop=float(s["low"]); risk=entry-stop; target=entry+2*risk
    if risk<=0: return {"signal": s["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None}
    # best favourable from entry bar
    first_bar=candles.iloc[sig+1]
    best = float(first_bar["low"]) if direction=="PE" else float(first_bar["high"])
    counter=0
    # check entry bar stop/target first (same order as baseline)
    def check_bar(c):
        nonlocal best, counter
        hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if direction=="PE":
            if hi>=stop: return ("stop", stop, t, round(-(stop-entry)*QTY-COST,2))
            if lo<=target: return ("target", target, t, round((entry-target)*QTY-COST,2))
        else:
            if lo<=stop: return ("stop", stop, t, round(-(entry-stop)*QTY-COST,2))
            if hi>=target: return ("target", target, t, round((target-entry)*QTY-COST,2))
        return None
    r=check_bar(first_bar)
    if r: return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": r[0], "exit_time": r[2], "exit_price": r[1], "net": r[3]}
    if first_bar["time"]=="15:10":
        return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": "15:10", "exit_price": float(first_bar["close"]), "net": round((entry-float(first_bar["close"]))*QTY-COST,2)}
    for j in range(sig+2, len(candles)):
        c=candles.iloc[j]
        r=check_bar(c)
        if r: return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": r[0], "exit_time": r[2], "exit_price": r[1], "net": r[3]}
        # stall update
        if direction=="PE":
            if float(c["low"]) < best: best=float(c["low"]); counter=0
            else: counter+=1
        else:
            if float(c["high"]) > best: best=float(c["high"]); counter=0
            else: counter+=1
        if counter>=N:
            cl=float(c["close"])
            net = round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": f"stall{N}", "exit_time": c["time"], "exit_price": cl, "net": net, "best": round(best,2), "stall_bars": N}
        if c["time"]=="15:10":
            cl=float(c["close"])
            net = round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)
            return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": cl, "net": net}
    c=candles.iloc[-1]; cl=float(c["close"])
    net = round((entry-cl)*QTY-COST,2) if direction=="PE" else round((cl-entry)*QTY-COST,2)
    return {"signal": s["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": cl, "net": net}

def summ(rows):
    traded=[r for r in rows if r.get("trade") is not None and r["trade"].get("net") is not None]
    green=sum(1 for r in traded if r["trade"]["net"]>0)
    nt=sum(1 for r in rows if r.get("trade") is None or r["trade"].get("net") is None)
    loss=sum(1 for r in traded if r["trade"]["net"]<=0)
    total=round(sum(r["trade"]["net"] for r in traded),2)
    return {"green": green, "no_trade": nt, "still_loss_or_scratch": loss, "traded_total": total, "n_traded": len(traded)}

if __name__=="__main__":
    cluster1=["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    orig1={"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,"2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
    modes={"2026-04-02":"skill"}
    win_days={"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,"2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,"2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,"2026-10-08":5440,"2026-10-23":11390}
    win_modes={"2026-03-23":"skill"}
    cluster3=["2026-02-13","2026-04-30","2026-05-18"]
    orig3={"2026-02-13":-3750,"2026-04-30":-3165,"2026-05-18":-3670}
    cluster2=[("2026-01-14","11:15",-2785),("2026-10-26","09:55",-8635)]
    out={}
    for strict in (True, False):
        name=f"retest_strict{strict}"
        rows=[]
        for ds in cluster1:
            r=retest(ds, modes.get(ds,"v4"), strict)
            rows.append({"date": ds, "orig_net": orig1[ds], **r})
        out[name]={"cluster1": rows, "summary": summ([{"trade": r["trade"]} for r in rows])}
        print(f"\n=== RETEST strict={strict} Cluster1 {out[name]['summary']} ===")
        for r in rows: print(r["date"], r["orig_net"], "first", r["first"], "bounce", r["bounce"], "second", r["second"], "->", r["trade"])
        wrows=[]
        for ds, onet in win_days.items():
            r=retest(ds, win_modes.get(ds,"v4"), strict)
            wrows.append({"date": ds, "orig_net": onet, **r})
        out[name]["winning_pe"]=[{"date": r["date"], "orig_net": r["orig_net"], "first": r["first"], "bounce": r["bounce"], "second": r["second"], "trade": r["trade"]} for r in wrows]
        out[name]["winning_summary"]=summ([{"trade": r["trade"]} for r in wrows])
        print(f"--- RETEST strict={strict} Winning PE {out[name]['winning_summary']} ---")
        for r in wrows: print(r["date"], r["orig_net"], "first", r["first"], "bounce", r["bounce"], "second", r["second"], "->", r["trade"])
        # Cluster3 extension check (PE, same retest)
        c3rows=[]
        for ds in cluster3:
            r=retest(ds, "v4", strict)
            c3rows.append({"date": ds, "orig_net": orig3[ds], **r})
        out[name]["cluster3_retest"]=c3rows
        out[name]["cluster3_retest_summary"]=summ([{"trade": r["trade"]} for r in c3rows])
        print(f"--- RETEST strict={strict} Cluster3 (extension check) {out[name]['cluster3_retest_summary']} ---")
        for r in c3rows: print(r["date"], r["orig_net"], "first", r["first"], "bounce", r["bounce"], "second", r["second"], "->", r["trade"])
    for frac in (0.50, 0.45, 0.40):
        rows=[]
        for ds in cluster3:
            t=partial_trail(ds, "v4", frac, "PE")
            rows.append({"date": ds, "orig_net": orig3[ds], "trade": t})
        out[f"cluster3_partial{int(frac*100)}"]={"cluster3": rows, "summary": summ(rows)}
        print(f"\n=== CLUSTER3 partial {int(frac*100)}% of target + trail BE {out[f'cluster3_partial{int(frac*100)}']['summary']} ===")
        for r in rows: print(r["date"], r["orig_net"], "->", r["trade"])
        # same partial on Cluster1 for context (is it still tiny?)
        c1rows=[]
        for ds in cluster1:
            t=partial_trail(ds, modes.get(ds,"v4"), frac, "PE")
            c1rows.append({"date": ds, "orig_net": orig1[ds], "trade": t})
        out[f"cluster3_partial{int(frac*100)}"]["cluster1_context"]=c1rows
        out[f"cluster3_partial{int(frac*100)}"]["cluster1_context_summary"]=summ(c1rows)
        print(f"--- same partial on Cluster1 (context) {out[f'cluster3_partial{int(frac*100)}']['cluster1_context_summary']} ---")
        for r in c1rows: print(r["date"], r["orig_net"], "->", r["trade"])
    for N in (10, 20):
        for label, days, origs, mode_map, direction, sig_map in [
            ("cluster3", cluster3, orig3, {}, "PE", {}),
            ("cluster1", cluster1, orig1, modes, "PE", {}),
            ("cluster2", [d for d,_,_ in cluster2], {d:o for d,_,o in cluster2}, {}, "CE", {d:s for d,s,_ in cluster2}),
        ]:
            rows=[]
            for ds in days:
                t=stall(ds, mode_map.get(ds,"v4"), N, direction, sig_map.get(ds))
                rows.append({"date": ds, "orig_net": origs[ds], "trade": t})
            out[f"stall{N}_{label}"]={"rows": rows, "summary": summ(rows)}
            print(f"\n=== STALL N={N} {label} {out[f'stall{N}_{label}']['summary']} ===")
            for r in rows: print(r["date"], r["orig_net"], "->", r["trade"])
        # winners stall PE
        wrows=[]
        for ds, onet in win_days.items():
            t=stall(ds, win_modes.get(ds,"v4"), N, "PE")
            wrows.append({"date": ds, "orig_net": onet, "trade": t})
        out[f"stall{N}_winning"]={"rows": wrows, "summary": summ(wrows)}
        print(f"--- STALL N={N} Winning PE {out[f'stall{N}_winning']['summary']} ---")
        for r in wrows: print(r["date"], r["orig_net"], "->", r["trade"])
    with open(os.path.join(BASE, "retest_stall_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
