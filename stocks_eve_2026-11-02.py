#!/usr/bin/env python3
"""Stocks evening engine 2026-11-02: (A) MFE/MAE paths for today's trades from the
sarvaritu_fwd candles the loggers used; (B) historical failure-cause counts from stored
files; (C) full controls gate for two INV1 candidates on the stored standalone INV1
population (eq_round10_INV1_trades_T125.csv, Jan-Oct 2026). Paper only, Rs0.
Basis: equity cash, provisional per 100 shares, Rs40/trade."""
import csv, json, pathlib, collections
WS = pathlib.Path.home()/"workspace/trading"
FWD = WS/"data/sarvaritu_fwd"
def bars(sym):
    out=[]
    with open(FWD/sym/"spot_5m.csv") as f:
        for r in csv.reader(f):
            if r and r[0].startswith("2026-11-02"):
                out.append((r[0][11:16], float(r[1]), float(r[2]), float(r[3]), float(r[4])))
    return out
def path(sym, et, xt, dir_):
    bs=[b for b in bars(sym) if et <= b[0] <= xt]
    if not bs: return None
    if dir_=="LONG":
        mfe=max(b[2] for b in bs); mae=min(b[3] for b in bs)
    else:
        mfe=min(b[3] for b in bs); mae=max(b[2] for b in bs)
    return {"bars": len(bs), "mfe_price": mfe, "mae_price": mae}
today = [
 # label, sym, dir, entry_time, entry, exit_time, exit_price
 ("BOOK INV-LONG","HINDCOPPER","LONG","09:35",404.15,"10:40",409.20),
 ("BOOK N4-V3","NTPC","LONG","09:35",325.30,"11:50",322.70),
 ("SCORECARD N4-V3","NTPC","LONG","09:35",325.30,"10:05",323.67),
 ("BOOK F4","HINDCOPPER","LONG","10:05",404.55,"14:00",410.62),
 ("BOOK F4","HINDZINC","LONG","10:05",509.00,"13:35",516.63),
 ("SCORECARD P2F","GODREJCP","SHORT","09:15",813.00,"09:20",817.06),
 ("INV1","HINDCOPPER","LONG","09:35",404.15,"10:40",409.20),
 ("INV1","WIPRO","SHORT","09:35",195.84,"09:45",196.82),
 ("INV1","NATIONALUM","SHORT","09:40",322.00,"09:50",323.61),
 ("INV1","TVSMOTOR","SHORT","09:40",4180.80,"09:50",4201.70),
 ("INV1","UNITDSPR","LONG","09:40",1346.30,"10:00",1339.57),
 ("INV1","KALYANKJIL","LONG","09:45",503.70,"15:10",504.60),
 ("INV1","WIPRO","SHORT","09:55",196.02,"10:15",197.00),
 ("INV1","VEDL","LONG","10:15",242.54,"13:45",245.57),
]
paths={}
for lab,sym,d,et,ep,xt,xp in today:
    p=path(sym,et,xt,d)
    if p:
        sign=1 if d=="LONG" else -1
        p["mfe_rs"] = round(sign*(p["mfe_price"]-ep)*100,2)
        p["mae_rs"] = round(sign*(p["mae_price"]-ep)*100,2)
    paths[f"{lab} {sym} {et}"] = p
print("== PATHS =="); print(json.dumps(paths, indent=1))

# (B) history counts
def load(name):
    return list(csv.DictReader(open(WS/name)))
n4 = load("eq_n4deep_v3_trades_T125_janoct.csv")
from datetime import datetime
def mins(a,b): return (datetime.strptime(b,"%H:%M")-datetime.strptime(a,"%H:%M")).total_seconds()/60
n4_stops=[r for r in n4 if r['exit_reason']=='stop']
n4_qs=[r for r in n4_stops if mins(r['entry_time'],r['exit_time'])<=15]
print(f"N4-V3 scorecard history: n={len(n4)} stops={len(n4_stops)} stops<=15min={len(n4_qs)}")
inv1 = load("eq_round10_INV1_trades_T125.csv")
for r in inv1: r['net']=float(r['net_rs_provisional_per100'])
i_stops=[r for r in inv1 if r['exit_reason']=='stop']
i_qs=[r for r in i_stops if mins(r['entry_time'],r['exit_time'])<=15]
print(f"INV1 history: n={len(inv1)} net={sum(r['net'] for r in inv1):+.2f} stops={len(i_stops)} stops<=15min={len(i_qs)} targets={sum(1 for r in inv1 if r['exit_reason']=='target')}")

# (C) gate for INV1 candidates
def summ(rs): return {"n": len(rs), "net": round(sum(r['net'] for r in rs),2)}
def halves(rs):
    h1=[r for r in rs if r['date'][5:7] in ('01','02','03','04','05')]
    h2=[r for r in rs if r['date'][5:7] in ('06','07','08','09','10')]
    return {"H1": summ(h1), "H2": summ(h2)}
def months(rs):
    m=collections.defaultdict(float)
    for r in rs: m[r['date'][:7]]+=r['net']
    return {k: round(v,2) for k,v in sorted(m.items())}
def extop3(rs):
    s=sorted(rs, key=lambda r:-r['net']); return round(sum(r['net'] for r in s[3:]),2)
chron=sorted(inv1, key=lambda r:(r['date'], r['entry_time'], r['stock']))
base_net=round(sum(r['net'] for r in inv1),2)
print(f"INV1 baseline re-sum: n={len(inv1)} net={base_net:+.2f} halves={halves(inv1)} ex-top-3={extop3(inv1)}")
print("baseline months:", months(inv1))
cands = {
 "EVE-02 skip event_window": [r for r in inv1 if r['event_status']!='event_window'],
 "EVE-03 LONG-only (skip SHORT)": [r for r in inv1 if r['direction']=='LONG'],
}
for name, var in cands.items():
    dropped=len(inv1)-len(var)
    plac_chrono = chron[dropped:]  # skip same count chronologically
    print(f"\n{name}: variant={summ(var)} halves={halves(var)} ex-top-3={extop3(var)}")
    print("  variant months:", months(var))
    bm=months(inv1); vm=months(var)
    flips=[m for m in bm if bm[m]>0 and vm.get(m,0)<0]
    print("  green->red flips:", flips)
    print(f"  placebo chrono-skip-{dropped}: net={sum(r['net'] for r in plac_chrono):+.2f} (n={len(plac_chrono)})")
    if name.startswith("EVE-02"):
        mirror=[r for r in inv1 if r['event_status']=='event_window']
        print(f"  mirror (event_window only kept): net={sum(r['net'] for r in mirror):+.2f} (n={len(mirror)})")
    else:
        mirror=[r for r in inv1 if r['direction']=='SHORT']
        print(f"  mirror (SHORT only kept): net={sum(r['net'] for r in mirror):+.2f} (n={len(mirror)})")
