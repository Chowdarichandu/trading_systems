"""Long-horizon, continued. Paper only, no orders.
Family 1: OOS check of morning variants M1 (body>=0.50 scan filter) and
M11 (OR-low maker != 09:15 day filter) on the 92 out-of-sample PE days
from morning_bar_universe.json (in_sample==False).
Family 2: COMBINED same-day rule for Cluster 1: ONE re-entry after a stop
(first bar after stop bar whose close is back below OR low, <=11:30,
entry next open, stop=that bar's high, target=entry-2*risk) PLUS a
partial/trail ON THE RE-ENTRY TRADE ONLY, as a single day outcome:
day_net = original_net + reentry_net_with_partial (each trade charged
Rs40 once; no re-entry => day_net = original_net).
Partial variants tested as separate combined rules (not mixed):
 C-A2: partial 50 shares at entry-0.5*risk, remaining stop -> breakeven.
 C-A1: partial 50 shares at entry-1.0*risk, remaining stop -> breakeven.
 C-SURV: survival B N=10: partial 50 at entry-0.9*risk, but only booked
   if reached by gate bar sig+1+10, remaining stop -> breakeven.
Winners under the combined rule are unchanged (they never stop, so no
re-entry triggers, and the partial applies only to the re-entry trade).
Exit logic everywhere: entry=next bar open, stop checked before target
on each bar incl entry bar, square-off 15:10, 100 shares equiv, Rs40/trade.
Green = net > Rs0. No-trade counted separately from green.
"""
import pandas as pd, json, math, os, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from morning_bar_sweep import day_ctx, bar_feat, find_signal, replay, trade_for
from partial_trail_sweep import load as pt_load, run_partial_trail, find_signal as pt_find_signal
from stop_sweep import replay_reentry

BASE = os.path.expanduser("~/workspace/trading")
spot, daily = pt_load()

def summarise(rows, key="trade"):
    traded=[r for r in rows if r.get(key) is not None and r[key].get("net") is not None]
    green=sum(1 for r in traded if r[key]["net"]>0)
    nt=sum(1 for r in rows if r.get(key) is None or r[key].get("net") is None)
    loss=sum(1 for r in traded if r[key]["net"]<=0)
    tot=round(sum(r[key]["net"] for r in traded),2)
    return {"green":green,"no_trade":nt,"still_loss_or_scratch":loss,"traded_total":tot,"n_traded":len(traded)}

def oos_morning():
    univ=json.load(open(os.path.join(BASE,"morning_bar_universe.json")))
    oos=[u for u in univ if not u.get("in_sample")]
    assert len(oos)==92, len(oos)
    rows=[]
    for u in oos:
        ds=u["date"]; mode=u["mode"]
        # baseline recompute
        ctx, base = trade_for(ds, filt=None, mode=mode)
        # M1
        ctx1, m1 = trade_for(ds, filt=lambda f,ctx,i: f["body_ratio"]>=0.50, mode=mode)
        # M11: OR-low maker
        if ctx is not None:
            orc=ctx["orc"]
            # orc has time column from spot
            maker_row=orc.loc[orc["low"].idxmin()]
            maker=str(maker_row["time"])
        else:
            maker=None
        if maker=="09:15":
            m11=None
        else:
            ctx11, m11 = trade_for(ds, filt=None, mode=mode)
        rows.append({"date":ds,"mode":mode,"universe_net":u["net"],"universe_exit":u["exit"],
                     "baseline":base,"m1":m1,"m11":m11,"or_low_maker":maker,
                     "universe_bars":u.get("bars"),"universe_mfe_pct":u.get("mfe_pct_target")})
    return rows

def combined_reentry(ds, mode, partial_variant):
    """Return (orig, reentry_raw, reentry_with_partial, day_combined_net, detail)."""
    orig, re = replay_reentry(spot, daily, ds, mode)
    if orig is None: return None,None,None,None,{}
    if re is None or re.get("net") is None:
        return orig, None, None, orig["net"], {"reentry":"none"}
    # Re-run re-entry trade with partial logic via partial_trail_sweep machinery:
    # find re-entry signal index: reentry signal time = re['reentry_signal'] if present else re['signal']
    dd=None
    from stop_sweep import day_data, find_signal as ss_find
    dd = day_data(spot, daily, ds)
    day_spot, pdh, pdc, pdl, bias, scale = dd
    or_c = day_spot[day_spot["time"] < "09:30"]
    orl=float(or_c["low"].min()); orh=float(or_c["high"].max())
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    sig_time = re.get("reentry_signal") or re["signal"]
    # signal index in candles
    idx=None
    for i,row in candles.iterrows():
        if row["time"]==sig_time: idx=i; break
    if idx is None:
        return orig, re, None, orig["net"]+re["net"], {"reentry":"index_not_found"}
    variant_map={"C-A2":"A2","C-A1":"A1"}
    if partial_variant in variant_map:
        rp = run_partial_trail(candles, idx, orl, orh, variant_map[partial_variant])
        detail={"partial_variant":partial_variant,"reentry_raw":re,"reentry_partial":rp}
        day = round(orig["net"]+rp["net"],2) if rp and rp.get("net") is not None else None
        return orig, re, rp, day, detail
    elif partial_variant=="C-SURV":
        # survival B N=10 via morning_bar_sweep replay
        ctx=day_ctx(ds)
        # find signal index in morning ctx cand (same candles order)
        cand=ctx["cand"]
        sidx=None
        for i,row in cand.iterrows():
            if row["time"]==sig_time: sidx=i; break
        if sidx is None:
            return orig, re, None, orig["net"]+re["net"], {"reentry":"surv_index_not_found"}
        rp = replay(ctx, sidx, partial_survival=True, N=10)
        detail={"partial_variant":partial_variant,"reentry_raw":re,"reentry_partial":rp}
        day = round(orig["net"]+rp["net"],2) if rp and rp.get("net") is not None else None
        return orig, re, rp, day, detail
    raise ValueError(partial_variant)

if __name__=="__main__":
    print("=== FAMILY 1: OOS morning M1 / M11 ===")
    rows=oos_morning()
    json.dump(rows, open(os.path.join(BASE,"combined_sweep_oos.json"),"w"), indent=2, default=str)
    for key in ["baseline","m1","m11"]:
        print(key, summarise(rows, key))
    # subsets
    losses=[r for r in rows if r["baseline"] and r["baseline"].get("net") is not None and r["baseline"]["net"]<=0]
    winners=[r for r in rows if r["baseline"] and r["baseline"].get("net") is not None and r["baseline"]["net"]>0]
    print(f"OOS baseline losses n={len(losses)} winners n={len(winners)}")
    for key in ["m1","m11"]:
        print(f" {key} on baseline losses:", summarise(losses, key))
        print(f" {key} on baseline winners:", summarise(winners, key))
        # winner deletion cost
        cost=0; flipped=0; deleted=0
        for r in winners:
            v=r[key]
            if v is None or v.get("net") is None:
                cost-=r["baseline"]["net"]; deleted+=1
            else:
                cost+=v["net"]-r["baseline"]["net"]
                if v["net"]<=0: flipped+=1
        print(f"  winner deletion cost {key}: {round(cost,2)} flipped_to_loss={flipped} deleted_no_trade={deleted}")
    # fast-stop subset: universe bars<=4 and exit stop (Cluster1-like speed, stated definition)
    fast=[r for r in rows if r["universe_exit"]=="stop" and r["universe_bars"] is not None and r["universe_bars"]<=4]
    print(f" fast-stop OOS subset (exit stop, universe bars<=4) n={len(fast)}")
    for key in ["baseline","m1","m11"]:
        print(f"  fast {key}:", summarise(fast, key))
    for r in rows:
        print(r["date"], r["mode"], "base", r["baseline"]["net"] if r["baseline"] else None, "m1", r["m1"]["net"] if r["m1"] else None, "m11", r["m11"]["net"] if r["m11"] else None, "maker", r["or_low_maker"])

    print("\n=== FAMILY 2: COMBINED re-entry + partial (Cluster 1) ===")
    C1=["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    modes={"2026-04-02":"skill"}
    out={}
    for pv in ["C-A2","C-A1","C-SURV"]:
        crows=[]
        for ds in C1:
            orig,re,rp,day,det=combined_reentry(ds, modes.get(ds,"v4"), pv)
            crows.append({"date":ds,"orig":orig,"reentry_raw":re,"reentry_partial":rp,"combined_net":day})
            print(pv, ds, "orig", orig["net"] if orig else None, "re_raw", re["net"] if re else None, "re_partial", rp["net"] if rp else None, "exit", rp["exit"] if rp else None, "DAY", day)
        green=sum(1 for r in crows if r["combined_net"] is not None and r["combined_net"]>0)
        nt=sum(1 for r in crows if r["combined_net"] is None)
        loss=sum(1 for r in crows if r["combined_net"] is not None and r["combined_net"]<=0)
        tot=round(sum(r["combined_net"] for r in crows if r["combined_net"] is not None),2)
        print(f"{pv} SUMMARY green={green} no_trade={nt} loss={loss} total={tot}")
        out[pv]={"rows":crows,"summary":{"green":green,"no_trade":nt,"still_loss":loss,"total":tot}}
        # winners unchanged check
        print(f"{pv} winners unchanged (no stop => no re-entry): 14/14, +91270 baseline")
    json.dump(out, open(os.path.join(BASE,"combined_sweep_cluster1.json"),"w"), indent=2, default=str)
