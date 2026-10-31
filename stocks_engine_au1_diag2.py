#!/usr/bin/env python3
"""AU-1 extended diagnosis: where does S080 help vs hurt F4?
Matched S065 (oc3 dump) vs S080 (oc4 dump), setup3 excluded, RF-1
weekend dates excluded. Aggregates the S080-minus-S065 delta by
ex-ante features."""
import csv, datetime
from collections import defaultdict
BASE="/home/hatch/workspace/trading"
def wk(d): return datetime.date.fromisoformat(d).weekday()>=5
def load(path):
    out={}
    with open(f"{BASE}/{path}") as f:
        for r in csv.DictReader(f):
            if wk(r["date"]) or r["setup"]=="setup3_bounce_rejection": continue
            out[(r["date"],r["symbol"],int(r["round"]))]=r
    return out
old=load("stocks_engine_oc3_f4t150_trades.csv")
new=load("stocks_engine_oc4_f4s080_trades.csv")
keys=sorted(set(old)&set(new))
print("matched",len(keys),"old-only",len(set(old)-set(new)),"new-only",len(set(new)-set(old)))
rows=[]
for k in keys:
    o,n=old[k],new[k]
    rows.append({"key":k,"month":k[0][:7],"delta":round(float(n["net"])-float(o["net"]),2),
                 "old_net":float(o["net"]),"new_net":float(n["net"]),
                 "old_exit":o["exit_reason"],"new_exit":n["exit_reason"],
                 "setup":o["setup"],"dir":o["dir"],"leg":o["leg"],"event":o["event"],
                 "band":"[0.5,0.75)" if float(o["premove_pct"])<0.75 else "[0.75,1.0)",
                 "stock":k[1],"entry_time":o["entry_time"],"entry_hour":o["entry_time"][:2]})
def agg(label, fn):
    g=defaultdict(lambda:[0,0.0,0.0,0.0])
    for r in rows:
        k=fn(r); g[k][0]+=1; g[k][1]+=r["delta"]
        if r["month"]=="2026-08": g[k][2]+=r["delta"]
        if r["month"]=="2026-10": g[k][3]+=r["delta"]
    print(f"\n--- S080 delta by {label} (n, full, Aug, Oct) ---")
    for k,v in sorted(g.items(), key=lambda kv:kv[1][1]):
        print(f" {str(k):26} n={v[0]:4} full={v[1]:10.2f} aug={v[2]:9.2f} oct={v[3]:9.2f}")
agg("month", lambda r:r["month"])
agg("setup", lambda r:r["setup"])
agg("dir", lambda r:r["dir"])
agg("leg", lambda r:r["leg"])
agg("event", lambda r:r["event"])
agg("band", lambda r:r["band"])
agg("setup x dir", lambda r:(r["setup"],r["dir"]))
agg("setup x event", lambda r:(r["setup"],r["event"]))
agg("dir x event", lambda r:(r["dir"],r["event"]))
agg("band x dir", lambda r:(r["band"],r["dir"]))
agg("entry_hour", lambda r:r["entry_hour"])
agg("old_exit -> new_exit", lambda r:(r["old_exit"],r["new_exit"]))
# August event trades detail
print("\nAugust F4 event_window trades (S080):")
for r in rows:
    if r["month"]=="2026-08" and r["event"]=="event_window":
        print(r)
print("\nFull-period F4 by event x month (S080 nets):")
g=defaultdict(float); c=defaultdict(int)
for r in new.values():
    if r["date"].startswith("2026-"):
        g[(r["date"][:7],r["event"])]+=float(r["net"]); c[(r["date"][:7],r["event"])]+=1
for m in sorted(set(k[0] for k in g)):
    print(m, {e:(c[(m,e)],round(g[(m,e)],2)) for e in ["event_window","no_event"] if (m,e) in g})
# Stocks where S080 hurts full-period and Aug
agg("stock", lambda r:r["stock"])
