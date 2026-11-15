#!/usr/bin/env python3
"""Stocks evening engine 2026-11-03: STOCKS-EVE-04 gate.
Candidate: P2F family cooldown - skip a P2F-family entry if the same stock's most
recent prior P2F-family trade (any cell: P2F / P2F-R2 / R2-LOWBAND) was a loser
(net<0) within the previous 10 calendar days. Diagnosed from 2026-11-03: the book's
R2-LOWBAND GODREJCP SHORT stopped one bar after entry, one day after the same name's
P2F scorecard SHORT stopped the same way (2026-11-02, -446.50).
Universe A (primary gate): stored family files, 87 trades Jan-Oct 2026 (same universe
as STOCKS-FIX-01; baseline must re-sum to +27,293.58).
Universe B (cross-year check): frozen c24 book dumps' P2F-family rows, 2025 + 2026.
Paper only, Rs0. Basis: equity cash, provisional per 100 shares, Rs40/trade (in nets).
"""
import csv, json, pathlib, collections
from datetime import date
WS = pathlib.Path.home()/"workspace/trading"
def d(s): 
    y,m,dd = s.split("-"); return date(int(y),int(m),int(dd))
def load_family():
    out=[]
    for f,col in [("stocks_engine_ch1_p2fprofile_trades.csv","net"),
                  ("stocks_engine_sat13_p2fr2_trades.csv","net_rs"),
                  ("stocks_engine_sat33_r2lowband_trades.csv","net_rs")]:
        for r in csv.DictReader(open(WS/f)):
            out.append({"date":r["date"],"stock":r["symbol"],"dir":r["direction"],
                        "net":float(r[col]),"exit_reason":r["exit_reason"],
                        "entry_time":r["entry_time"],"exit_time":r["exit_time"]})
    out.sort(key=lambda r:(r["date"],r["entry_time"],r["stock"]))
    return out
def apply_cooldown(rows, days=10):
    kept, dropped, last = [], [], {}
    for r in rows:
        prev = last.get(r["stock"])
        if prev and prev["net"] < 0 and 0 <= (d(r["date"])-d(prev["date"])).days <= days:
            dropped.append(r)
        else:
            kept.append(r)
        last[r["stock"]] = r
    return kept, dropped
def summ(rs): return {"n": len(rs), "net": round(sum(r["net"] for r in rs),2)}
def halves(rs):
    h1=[r for r in rs if r["date"][5:7] in ("01","02","03","04","05")]
    h2=[r for r in rs if r["date"][5:7] in ("06","07","08","09","10")]
    return {"H1": summ(h1), "H2": summ(h2)}
def months(rs):
    m=collections.defaultdict(float)
    for r in rs: m[r["date"][:7]]+=r["net"]
    return {k: round(v,2) for k,v in sorted(m.items())}
def extop3(rs):
    s=sorted(rs, key=lambda r:-r["net"]); return round(sum(r["net"] for r in s[3:]),2)

fam = load_family()
base = summ(fam)
print("FAMILY baseline:", base, "assert +27293.58:", abs(base["net"]-27293.58)<0.01)
kept, dropped = apply_cooldown(fam)
print("EVE-04 variant:", summ(kept), "dropped:", [(r["date"],r["stock"],r["net"]) for r in dropped])
print("variant halves:", halves(kept), "| baseline halves:", halves(fam))
print("variant ex-top-3:", extop3(kept), "| baseline ex-top-3:", extop3(fam))
bm, vm = months(fam), months(kept)
print("baseline months:", bm); print("variant months:", vm)
print("green->red flips:", [m for m in bm if bm[m]>0 and vm.get(m,0)<0])
plac = fam[len(dropped):]
print(f"placebo chrono-skip-{len(dropped)}: net={sum(r['net'] for r in plac):+.2f} (n={len(plac)})")
# quick-stop count change
from datetime import datetime
def mins(a,b): return (datetime.strptime(b,"%H:%M")-datetime.strptime(a,"%H:%M")).total_seconds()/60
qs_b = sum(1 for r in fam if r["exit_reason"]=="stop" and mins(r["entry_time"],r["exit_time"])<=15)
qs_v = sum(1 for r in kept if r["exit_reason"]=="stop" and mins(r["entry_time"],r["exit_time"])<=15)
print(f"quick stops <=15min: baseline {qs_b} -> variant {qs_v}")
# Cross-year on c24 book dumps (family rows only)
for yr in ("2025","2026"):
    rows=[{"date":r["date"],"stock":r["stock"],"net":float(r["net"])}
          for r in csv.DictReader(open(WS/f"stocks_engine_v2_c24_book{yr}_trades.csv"))
          if r["comp"] in ("P2F","P2F-R2","R2-LOWBAND")]
    rows.sort(key=lambda r:(r["date"],r["stock"]))
    k,dr = apply_cooldown(rows)
    print(f"CROSS-YEAR {yr}: family rows baseline {summ(rows)} -> variant {summ(k)} (dropped {len(dr)}: {[(r['date'],r['stock'],r['net']) for r in dr]})")
# Today counterfactual
print("TODAY: GODREJCP R2-LOWBAND 2026-11-03 prior family trade = GODREJCP P2F 2026-11-02 net -446.50 (1 day, loser) -> EVE-04 would SKIP today's book trade (-451.85 avoided, counterfactual only). NTPC P2F 2026-11-03: no prior P2F-family NTPC trade (its Nov 2 trade was N4-V3) -> kept, -201.50 stands.")
