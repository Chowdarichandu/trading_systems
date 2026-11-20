#!/usr/bin/env python3
"""Stocks evening engine 2026-11-19 — SCORE-ONLY per owner settlement 2026-11-13.
Part A only: candle-verified detail for today's Stock Book + N4 scorecard trades.
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade.
"""
import csv, json, pathlib
WS = pathlib.Path.home() / "workspace/trading"
FWD = WS / "data/sarvaritu_fwd"
COST = 40.0
def bars(root, sym, day):
    out=[]
    p=root/sym/"spot_5m.csv"
    if not p.exists(): return out
    for r in csv.DictReader(open(p)):
        if r["timestamp"][:10]==day:
            out.append((r["timestamp"][11:16], float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return sorted(out)
def daily_closes(root, sym):
    p=root/sym/"spot_5m.csv"
    days={}
    for r in csv.DictReader(open(p)):
        days[r["timestamp"][:10]]=float(r["close"])  # last bar close approx; use daily file if exists
    return days
def scan(bars_, entry_time, entry, stop, target, direction, include_entry_bar=False):
    started=False; mfe=mae=None; mfe_t=mae_t=None
    for t,o,h,l,c in bars_:
        if t==entry_time:
            started=True
            if not include_entry_bar: continue
        if t<entry_time or not started or t>"15:10": continue
        if direction=="LONG":
            fav=(h-entry)*100; adv=(l-entry)*100
        else:
            fav=(entry-l)*100; adv=(entry-h)*100
        if mfe is None or fav>mfe: mfe, mfe_t = fav, t
        if mae is None or adv<mae: mae, mae_t = adv, t
        if direction=="LONG":
            if l<=stop: return t,stop,"stop",mfe,mae,mfe_t,mae_t
            if h>=target: return t,target,"target",mfe,mae,mfe_t,mae_t
        else:
            if h>=stop: return t,stop,"stop",mfe,mae,mfe_t,mae_t
            if l<=target: return t,target,"target",mfe,mae,mfe_t,mae_t
        if t=="15:10": return t,c,"square_off",mfe,mae,mfe_t,mae_t
    return None,None,"no_exit",mfe,mae,mfe_t,mae_t
def net_of(entry, xp, d):
    return round(((xp-entry) if d=="LONG" else (entry-xp))*100-COST,2)
def levels(entry,d,sp,tp):
    if d=="LONG": return round(entry*(1-sp),2), round(entry*(1+tp),2)
    return round(entry*(1+sp),2), round(entry*(1-tp),2)

# ASTRAL book INV-ABOVE T125/S050: entry inferred 1238.70 (09:35 open), logged exit 1251.0 net +1190.00
for label,sym,d,et,entry,sp,tp,logged in [
    ("INV-ABOVE/book T125S050","ASTRAL","LONG","09:35",1238.70,0.0050,0.0125,1190.00),
]:
    b=bars(FWD,sym,"2026-11-19")
    stop,tgt=levels(entry,d,sp,tp)
    xt,xp,xr,mfe,mae,mfet,maet=scan(b,et,entry,stop,tgt,d)
    print(json.dumps({"label":label,"stock":sym,"dir":d,"entry_time":et,"entry":entry,"stop":stop,"target":tgt,"exit_time":xt,"exit_price":xp,"exit_reason":xr,"net_recomputed":net_of(entry,xp,d) if xp else None,"net_logged":logged,"mfe_rs":round(mfe,2) if mfe is not None else None,"mfe_time":mfet,"mae_rs":round(mae,2) if mae is not None else None,"mae_time":maet,"nbars":len(b)}))
    print(json.dumps({sym+"_day":{"open":b[0][1],"high":max(x[2] for x in b),"high_bar":[x[0] for x in b if x[2]==max(y[2] for y in b)],"low":min(x[3] for x in b),"close_1510":[x[4] for x in b if x[0]=="15:10"][0],"nbars":len(b)}}))
    # bars near target
    for t,o,h,l,c in b:
        if h>=tgt-1: print(" near-target bar",t,o,h,l,c)
# UNITDSPR N4 scorecard: entry 1399.40 stop 1406.40 target 1381.91 logged -739.70, exit 09:35 stop
b=bars(FWD,"UNITDSPR","2026-11-19")
print(json.dumps({"UNITDSPR_bars_0930_0950":b[4:8]}))
# scan including entry bar (N4 convention per its log notes: 09:35 bar itself stopped)
xt,xp,xr,mfe,mae,_,_=scan(b,"09:35",1399.40,1406.40,1381.91,"SHORT",include_entry_bar=True)
print(json.dumps({"N4_UNITDSPR_incl_entrybar":{"exit_time":xt,"exit_price":xp,"exit_reason":xr,"net":net_of(1399.40,xp,"SHORT") if xp else None,"mfe":round(mfe,2) if mfe else None,"mae":round(mae,2) if mae else None}}))
xt2,xp2,xr2,mfe2,mae2,_,_=scan(b,"09:35",1399.40,1406.40,1381.91,"SHORT",include_entry_bar=False)
print(json.dumps({"N4_UNITDSPR_excl_entrybar":{"exit_time":xt2,"exit_price":xp2,"exit_reason":xr2,"net":net_of(1399.40,xp2,"SHORT") if xp2 else None,"mfe":round(mfe2,2) if mfe2 else None,"mae":round(mae2,2) if mae2 else None}}))
print(json.dumps({"UNITDSPR_day":{"open":b[0][1],"high":max(x[2] for x in b),"low":min(x[3] for x in b),"close_1510":[x[4] for x in b if x[0]=="15:10"][0]}}))
# ASTRAL prior-day closes for v2 (use fwd daily closes file if present)
import glob
for cand in [FWD/"ASTRAL"/"daily.csv", WS/"data/sarvaritu_fwd/ASTRAL/daily.csv"]:
    print("daily cand", cand, cand.exists())
print("ASTRAL fwd dir:", sorted([str(p) for p in (FWD/"ASTRAL").iterdir()]))
