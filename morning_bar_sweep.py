"""Morning-bar sweep + frozen gap-box forward validation. Paper only.
Reuses timing_sweep replay logic: entry=next bar open, stop=signal high (PE),
target=entry-2*risk, stop before target each bar incl entry bar, sq-off 15:10,
100 shares, 40/trade. No-trade counted separately from green."""
import pandas as pd, math, json, os
BASE=os.path.expanduser("~/workspace/trading/data/progressive/NIFTY")
QTY,COST=100,40.0
spot=pd.read_csv(os.path.join(BASE,"spot_5m.csv"), parse_dates=["timestamp"])
daily=pd.read_csv(os.path.join(BASE,"spot_daily.csv"), parse_dates=["date"])
spot["timestamp"]=pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
daily["date"]=pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
spot["date"]=spot["timestamp"].dt.normalize(); spot["time"]=spot["timestamp"].dt.strftime("%H:%M")
spot=spot.sort_values("timestamp"); daily=daily.sort_values("date")

def day_ctx(ds):
    d=pd.Timestamp(ds); day=spot[spot["date"]==d]; prev=daily[daily["date"]<d]
    if day.empty or prev.empty: return None
    y=prev.iloc[-1]; pdh,pdc,pdl=float(y["high"]),float(y["close"]),float(y["low"])
    # gap: day open (daily open) vs prev close
    today=daily[daily["date"]==d]
    gap=float(today.iloc[0]["open"])/pdc*100-100 if not today.empty else None
    scale=pdc/55000.0
    orc=day[day["time"]<"09:30"]; orh=float(orc["high"].max()); orl=float(orc["low"].min())
    cand=day[day["time"]>="09:30"].reset_index(drop=True)
    return dict(date=ds,day=day,orc=orc,orl=orl,orh=orh,cand=cand,pdh=pdh,pdc=pdc,pdl=pdl,scale=scale,gap=gap)

def bar_feat(c):
    o,h,l,cl=float(c["open"]),float(c["high"]),float(c["low"]),float(c["close"])
    rng=h-l; body=abs(cl-o); uw=h-max(o,cl); lw=min(o,cl)-l
    return dict(open=o,high=h,low=l,close=cl,range=rng,body=body,
        body_ratio=body/rng if rng else 0, uw=uw, uw_ratio=uw/rng if rng else 0, lw=lw, red=cl<o)

def find_signal(ctx, filt=None, mode="v4"):
    cand=ctx["cand"]; orl,orh,pdl,scale=ctx["orl"],ctx["orh"],ctx["pdl"],ctx["scale"]
    levels=sorted(set([ctx["pdh"],ctx["pdc"],ctx["pdl"]]))
    for i,(_,c) in enumerate(cand.iterrows()):
        t=c["time"]
        if t>"11:30": break
        close=float(c["close"])
        if close<orl and close<pdl:
            if mode=="v4":
                nxt=[l for l in levels if l<close]; room=(close-max(nxt)) if nxt else math.inf
                if not ((orh-orl)<=360*scale and room>=200*scale): continue
            if filt and not filt(bar_feat(c), ctx, i): continue
            return i
    return None

def replay(ctx, sig_idx, partial_survival=False, N=10):
    cand=ctx["cand"]; sig=cand.iloc[sig_idx]
    if sig_idx+1>=len(cand): return None
    entry=float(cand.iloc[sig_idx+1]["open"]); stop=float(sig["high"]); risk=stop-entry
    if risk<=0: return dict(signal=sig["time"],entry=entry,stop=stop,exit="invalid_risk",net=None)
    target=entry-2*risk; plevel=entry-0.9*risk
    gate_idx=sig_idx+1+N  # open of bar sig+1+N
    partial_reached=False; partialled=False; partial_profit=0.0
    bars_to_exit=None; mfe_low=entry
    for j in range(sig_idx+1, len(cand)):
        c=cand.iloc[j]; hi,lo,cl=float(c["high"]),float(c["low"]),float(c["close"]); tm=c["time"]
        # gate eligibility (interpretation B): at gate open, book already-earned partial
        if partial_survival and j==gate_idx and not partialled and partial_reached:
            partialled=True; partial_profit=50*0.9*risk; stop=entry
        cur_stop=stop
        if hi>=cur_stop:
            # stop before target/partial on this bar
            net=(partial_profit + (0 if partialled else 0) - COST) if partialled else -(cur_stop-entry)*QTY-COST
            # if partialled, remaining 50 at BE => 0; if not, full stop loss (PE: -(stop-entry)*100)
            if partialled: net=partial_profit-COST
            else: net=-(cur_stop-entry)*QTY-COST
            return dict(signal=sig["time"],entry=entry,stop=round(cur_stop,2),target=round(target,2),risk=round(risk,2),exit="stop",exit_time=tm,net=round(net,2),bars=j-(sig_idx+1),mfe_pts=round(entry-mfe_low,2))
        if lo<=plevel and not partial_reached: partial_reached=True
        if partial_survival and j>=gate_idx and not partialled and partial_reached:
            # armed from gate onward: partial triggers on this bar (adverse already checked)
            partialled=True; partial_profit=50*0.9*risk; stop=entry
            if lo<=target:
                net=partial_profit+50*2*risk-COST
                return dict(signal=sig["time"],entry=entry,stop=round(entry,2),target=round(target,2),risk=round(risk,2),exit="target_after_partial",exit_time=tm,net=round(net,2),bars=j-(sig_idx+1),mfe_pts=round(entry-mfe_low,2))
            # continue to next bars with BE stop (do not exit this bar on partial alone)
            mfe_low=min(mfe_low,lo); continue
        if lo<=target:
            if partialled:
                net=partial_profit+50*2*risk-COST
            else:
                net=2*risk*QTY-COST
            return dict(signal=sig["time"],entry=entry,stop=round(cur_stop,2),target=round(target,2),risk=round(risk,2),exit="target",exit_time=tm,net=round(net,2),bars=j-(sig_idx+1),mfe_pts=round(entry-mfe_low,2))
        if tm=="15:10":
            if partialled: net=partial_profit+50*(entry-cl)-COST
            else: net=(entry-cl)*QTY-COST
            return dict(signal=sig["time"],entry=entry,stop=round(cur_stop,2),target=round(target,2),risk=round(risk,2),exit="square_off",exit_time=tm,net=round(net,2),bars=j-(sig_idx+1),mfe_pts=round(entry-mfe_low,2))
        mfe_low=min(mfe_low,lo)
    c=cand.iloc[-1]
    return dict(signal=sig["time"],entry=entry,stop=stop,target=round(target,2),risk=round(risk,2),exit="square_off",exit_time=c["time"],net=round((entry-float(c["close"]))*QTY-COST,2),bars=len(cand)-(sig_idx+1),mfe_pts=round(entry-mfe_low,2))

def trade_for(ds, filt=None, mode="v4", partial_survival=False):
    ctx=day_ctx(ds)
    if not ctx: return None,None
    si=find_signal(ctx, filt=filt, mode=mode)
    if si is None: return ctx,None
    sig=ctx["cand"].iloc[si]
    return ctx, dict(ctx_sig=bar_feat(sig), signal_time=sig["time"],
        belowPDL=round(ctx["pdl"]-float(sig["close"]),2), gap=round(ctx["gap"],3) if ctx["gap"] is not None else None,
        **replay(ctx, si, partial_survival=partial_survival))

if __name__=="__main__":
    # verify survival B N=10 reproduction on Cluster3 + winners
    C3=["2026-02-13","2026-04-30","2026-05-18"]
    W=["2026-01-21","2026-02-24","2026-03-16","2026-03-13","2026-04-24","2026-05-05","2026-07-22","2026-08-12","2026-08-27","2026-09-29","2026-09-07","2026-10-08","2026-10-23"]
    # note 2026-03-23 skill winner missing from V4 scan; handle separately below
    for grp,dates in [("C3",C3),("W-v4",[d for d in W])]:
        tot=0
        for ds in dates:
            ctx,tr=trade_for(ds, partial_survival=True)
            print(grp,ds,tr)
            if tr and tr.get("net") is not None: tot+=tr["net"]
        print(grp,"TOTAL survivalB10",tot)
