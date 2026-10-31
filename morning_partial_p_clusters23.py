"""Family (p) passing variants applied to Clusters 2/3 original trades.
Same TRADES and bar order as morning_partial_clusters23.py, adapted:
PE: adverse high>=stop, favourable low<=partial/target.
CE: adverse low<=stop, favourable high>=partial/target.
Trail: BE=entry, Mid=entry +/-0.5*risk (PE minus, CE plus).
High-touch trails start NEXT bar after partial (as in fixed (p) sweep);
close trails may use partial bar's close. Original stop always intra-bar.
Time cutoff: partial booked only if trigger bar time < cutoff, else plain.
"""
import pandas as pd, json, os
BASE = os.path.expanduser("~/workspace/trading/data/progressive/NIFTY")
spot = pd.read_csv(os.path.join(BASE, "spot_5m.csv"), parse_dates=["timestamp"])
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot["date"] = spot["timestamp"].dt.normalize()
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
TRADES = [
    ("2", "2026-01-14", "CE", "11:15", 25747.75, 25720.30, 25802.65, -2785),
    ("2", "2026-10-26", "CE", "09:55", 22635.70, 22549.75, 22807.60, -8635),
    ("3", "2026-02-13", "PE", "09:30", 25549.00, 25586.10, 25474.80, -3750),
    ("3", "2026-04-30", "PE", "10:00", 23848.75, 23880.00, 23786.25, -3165),
    ("3", "2026-05-18", "PE", "09:35", 23358.50, 23394.80, 23285.90, -3670),
]

def plain(cand, sig_idx, direction, entry, stop, target, risk):
    for j in range(sig_idx+1, len(cand)):
        c=cand.iloc[j]; hi,lo,cl,t=float(c["high"]),float(c["low"]),float(c["close"]),c["time"]
        adv=(hi>=stop) if direction=="PE" else (lo<=stop)
        if adv: return {"exit":"stop","exit_time":t,"net":round(-risk*100-40,2),"partial_time":None}
        fav=(lo<=target) if direction=="PE" else (hi>=target)
        if fav: return {"exit":"target","exit_time":t,"net":round(2*risk*100-40,2),"partial_time":None}
        if t=="15:10":
            net=(entry-cl)*100-40 if direction=="PE" else (cl-entry)*100-40
            return {"exit":"square_off","exit_time":t,"net":round(net,2),"partial_time":None}
    return {"exit":"end_of_data","exit_time":cand.iloc[-1]["time"],"net":None,"partial_time":None}

def replay(date, direction, signal, entry, stop, target, trail_mode, cutoff):
    d=pd.Timestamp(date); day=spot[spot["date"]==d].sort_values("timestamp").reset_index(drop=True)
    cand=day[day["time"]>="09:30"].reset_index(drop=True)
    sig_idx=cand.index[cand["time"]==signal].tolist()[0]
    assert abs(float(cand.iloc[sig_idx+1]["open"])-entry)<0.01
    risk=abs(stop-entry)
    plevel=entry-risk if direction=="PE" else entry+risk
    mid=entry-0.5*risk if direction=="PE" else entry+0.5*risk
    trail_level=entry if "BE" in trail_mode else mid
    close_only=trail_mode.startswith("close")
    pb=False; pnet=0.0; ptime=None; pidx=None
    for j in range(sig_idx+1, len(cand)):
        c=cand.iloc[j]; hi,lo,cl,t=float(c["high"]),float(c["low"]),float(c["close"]),c["time"]
        adv=(hi>=stop) if direction=="PE" else (lo<=stop)
        if adv:
            if pb:
                rem=-(stop-entry)*50 if direction=="PE" else (stop-entry)*50
                return {"exit":"stop_after_partial","exit_time":t,"net":round(pnet+rem-40,2),"partial_time":ptime,"partial_level":round(plevel,2)}
            return {"exit":"stop","exit_time":t,"net":round(-risk*100-40,2),"partial_time":None,"partial_level":round(plevel,2)}
        fav_p=(lo<=plevel) if direction=="PE" else (hi>=plevel)
        if not pb and fav_p:
            if cutoff is not None and t>=cutoff:
                return {**plain(cand, sig_idx, direction, entry, stop, target, risk), "partial_level":round(plevel,2), "partial_gated_out":True}
            pb=True; ptime=t; pidx=j; pnet=(entry-plevel)*50 if direction=="PE" else (plevel-entry)*50
            fav_t=(lo<=target) if direction=="PE" else (hi>=target)
            if fav_t:
                rem=(entry-target)*50 if direction=="PE" else (target-entry)*50
                return {"exit":"target_same_bar_as_partial","exit_time":t,"net":round(pnet+rem-40,2),"partial_time":ptime,"partial_level":round(plevel,2)}
        if pb and (close_only or j>pidx):
            if close_only:
                hit=(cl>=trail_level) if direction=="PE" else (cl<=trail_level)
            else:
                hit=(hi>=trail_level) if direction=="PE" else (lo<=trail_level)
            if hit:
                rem=(entry-trail_level)*50 if direction=="PE" else (trail_level-entry)*50
                kind=("breakeven_close_after_partial" if close_only and trail_level==entry else
                      "mid_close_after_partial" if close_only else
                      "breakeven_stop_after_partial" if trail_level==entry else "mid_stop_after_partial")
                return {"exit":kind,"exit_time":t,"net":round(pnet+rem-40,2),"partial_time":ptime,"partial_level":round(plevel,2)}
        fav_t=(lo<=target) if direction=="PE" else (hi>=target)
        if fav_t:
            if pb:
                rem=(entry-target)*50 if direction=="PE" else (target-entry)*50
                return {"exit":"target_after_partial","exit_time":t,"net":round(pnet+rem-40,2),"partial_time":ptime,"partial_level":round(plevel,2)}
            return {"exit":"target","exit_time":t,"net":round(2*risk*100-40,2),"partial_time":None,"partial_level":round(plevel,2)}
        if t=="15:10":
            if pb:
                rem=(entry-cl)*50 if direction=="PE" else (cl-entry)*50
                return {"exit":"square_off_after_partial","exit_time":t,"net":round(pnet+rem-40,2),"partial_time":ptime,"partial_level":round(plevel,2)}
            net=(entry-cl)*100-40 if direction=="PE" else (cl-entry)*100-40
            return {"exit":"square_off","exit_time":t,"net":round(net,2),"partial_time":None,"partial_level":round(plevel,2)}
    return {"exit":"end_of_data","exit_time":cand.iloc[-1]["time"],"net":None,"partial_time":ptime,"partial_level":round(plevel,2)}

if __name__=="__main__":
    variants=[("p4","highBE","10:00"),("p5","highBE","09:45"),("p8","closeMid","10:00"),("p1","closeBE",None),("p2","closeMid",None)]
    out={}
    for name,mode,cut in variants:
        print(f"\n=== ({name} {mode} cutoff={cut}) Clusters 2+3 ==="); rows=[]
        for cl,ds,dirc,sig,entry,stop,target,orig in TRADES:
            r=replay(ds,dirc,sig,entry,stop,target,mode,cut); rows.append({"cluster":cl,"date":ds,"dir":dirc,"orig_net":orig,**r}); print(ds,f"C{cl} {dirc} orig {orig} ->",r)
        for cl in ("2","3"):
            sub=[x for x in rows if x["cluster"]==cl]; g=sum(1 for x in sub if x["net"] is not None and x["net"]>0); tot=sum(x["net"] for x in sub if x["net"] is not None); print(f"Cluster {cl}: green {g}/{len(sub)} total {tot}")
        g=sum(1 for x in rows if x["net"] is not None and x["net"]>0); tot=sum(x["net"] for x in rows if x["net"] is not None); print(f"Combined 2+3: green {g}/5 total {tot} (orig -22005)"); out[name]=rows
    json.dump(out, open(os.path.expanduser("~/workspace/trading/morning_partial_p_clusters23_raw.json"),"w"), indent=2, default=str)
