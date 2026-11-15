#!/usr/bin/env python3
"""STOCKS-EVE-05: narrower cooldown - skip a P2F-family entry only if the same stock's
most recent prior family trade was a QUICK STOP (exit_reason stop, exit-entry <=15 min)
within the previous 10 calendar days. Mechanically distinct from EVE-04 (any loser)."""
import csv, pathlib, collections
from datetime import date, datetime
WS = pathlib.Path.home()/"workspace/trading"
def d(s):
    y,m,dd=s.split("-"); return date(int(y),int(m),int(dd))
def mins(a,b): return (datetime.strptime(b,"%H:%M")-datetime.strptime(a,"%H:%M")).total_seconds()/60
def load_family():
    out=[]
    for f,col in [("stocks_engine_ch1_p2fprofile_trades.csv","net"),("stocks_engine_sat13_p2fr2_trades.csv","net_rs"),("stocks_engine_sat33_r2lowband_trades.csv","net_rs")]:
        for r in csv.DictReader(open(WS/f)):
            out.append({"date":r["date"],"stock":r["symbol"],"net":float(r[col]),"exit_reason":r["exit_reason"],"entry_time":r["entry_time"],"exit_time":r["exit_time"]})
    out.sort(key=lambda r:(r["date"],r["entry_time"],r["stock"])); return out
def summ(rs): return {"n":len(rs),"net":round(sum(r["net"] for r in rs),2)}
def halves(rs):
    h1=[r for r in rs if r["date"][5:7] in ("01","02","03","04","05")]; h2=[r for r in rs if r["date"][5:7] in ("06","07","08","09","10")]
    return {"H1":summ(h1),"H2":summ(h2)}
def months(rs):
    m=collections.defaultdict(float)
    for r in rs: m[r["date"][:7]]+=r["net"]
    return {k:round(v,2) for k,v in sorted(m.items())}
def extop3(rs):
    s=sorted(rs,key=lambda r:-r["net"]); return round(sum(r["net"] for r in s[3:]),2)
def quickstop(r): return r["exit_reason"]=="stop" and mins(r["entry_time"],r["exit_time"])<=15
def apply(rows):
    kept,dropped,last=[],[],{}
    for r in rows:
        prev=last.get(r["stock"])
        if prev and quickstop(prev) and 0<=(d(r["date"])-d(prev["date"])).days<=10: dropped.append(r)
        else: kept.append(r)
        last[r["stock"]]=r
    return kept,dropped
fam=load_family(); print("baseline:",summ(fam))
kept,dropped=apply(fam)
print("EVE-05 variant:",summ(kept),"dropped:",[(r["date"],r["stock"],r["net"]) for r in dropped])
print("halves base/var:",halves(fam),halves(kept))
print("ex-top3 base/var:",extop3(fam),extop3(kept))
bm,vm=months(fam),months(kept); print("flips:",[m for m in bm if bm[m]>0 and vm.get(m,0)<0])
plac=fam[len(dropped):]; print(f"placebo chrono-skip-{len(dropped)}: {sum(r['net'] for r in plac):+.2f}")
print("quick stops:",sum(1 for r in fam if quickstop(r)),"->",sum(1 for r in kept if quickstop(r)))
for yr in ("2025","2026"):
    rows=[{"date":r["date"],"stock":r["stock"],"net":float(r["net"]),"exit_reason":"","entry_time":r["entry_time"],"exit_time":""}
          for r in csv.DictReader(open(WS/f"stocks_engine_v2_c24_book{yr}_trades.csv")) if r["comp"] in ("P2F","P2F-R2","R2-LOWBAND")]
    print(f"CROSS-YEAR {yr}: NOT COMPUTABLE - c24 book dumps carry no exit_reason/exit_time, so the quick-stop trigger cannot be identified in 2025/2026 book rows.")
print("TODAY: GODREJCP Nov 2 P2F stop at 09:20 (5 min, quick stop) -> EVE-05 would also SKIP today's book trade (counterfactual only).")
