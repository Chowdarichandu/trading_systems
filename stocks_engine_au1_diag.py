#!/usr/bin/env python3
"""ENGINE AU-1 diagnosis: August on the banked book.
Anchor must reproduce state exactly. Compares F4 August at T150/S065
(OC-3 dump) vs T150/S080 (OC-4 dump), matched by date+symbol+round,
to identify exactly what OC-4's wider stop changed. Paper only."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 12433.74, "2026-02": 4173.49, "2026-03": 20322.06,
         "2026-04": 50.73, "2026-05": 27844.38, "2026-06": -1233.49,
         "2026-07": 2096.63, "2026-08": -1484.26, "2026-09": 17413.79,
         "2026-10": 50029.72}

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "round": int(r["round"]), "net": float(r["net"]),
        "entry_time": r["entry_time"], "exit_reason": r["exit_reason"],
        "event_status": r["event"], "premove_pct": float(r["premove_pct"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
for t in inv + n4 + p2f:
    t.setdefault("setup", None); t.setdefault("leg", None)
    t.setdefault("premove_pct", None)
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

bt, bc = mt(book)
tot = round(sum(t["net"] for t in book), 2)
anchor_ok = bt == STATE and tot == 131646.79 and len(book) == 934
print("ANCHOR:", anchor_ok, f"| trades {len(book)} total {tot}")
assert anchor_ok

aug = [t for t in book if t["date"].startswith("2026-08")]
print(f"AUGUST: {len(aug)} trades net {round(sum(t['net'] for t in aug),2)}")

def split(trades, keyfn, label, min_n=1):
    g = defaultdict(lambda: [0, 0.0])
    for t in trades:
        k = keyfn(t)
        if k is None: continue
        g[k][0] += 1; g[k][1] += t["net"]
    print(f"\n--- August by {label} ---")
    for k, v in sorted(g.items(), key=lambda kv: kv[1][1]):
        if v[0] >= min_n:
            print(f" {str(k):28} n={v[0]:3} net={v[1]:10.2f}")
    return g

split(aug, lambda t: t["comp"], "component")
split(aug, lambda t: t["stock"], "stock")
split(aug, lambda t: t["dir"], "direction")
split(aug, lambda t: t["exit_reason"], "exit")
split([t for t in aug if t["comp"]=="F4"], lambda t: t["setup"], "F4 setup")
split([t for t in aug if t["comp"]=="F4"], lambda t: t["leg"], "F4 leg")
split([t for t in aug if t["comp"]=="F4"], lambda t: "[0.5,0.75)" if t["premove_pct"]<0.75 else "[0.75,1.0)", "F4 band")
split([t for t in aug if t.get("event_status")], lambda t: t["event_status"], "event")
byday = split(aug, lambda t: t["date"], "day")

# Drag: negative Aug and full-period
def drag(keyfn, trades_all, trades_aug, label, min_n=2):
    full = defaultdict(lambda:[0,0.0]); a = defaultdict(lambda:[0,0.0])
    for t in trades_all:
        k=keyfn(t)
        if k is not None: full[k][0]+=1; full[k][1]+=t["net"]
    for t in trades_aug:
        k=keyfn(t)
        if k is not None: a[k][0]+=1; a[k][1]+=t["net"]
    hits=[]
    for k,v in a.items():
        if v[1]<0 and v[0]>=min_n and full[k][1]<0:
            hits.append((k,v,full[k]))
    print(f"DRAG[{label}]: " + ("; ".join(f"{k}: Aug n={v[0]} {v[1]:.2f} | full n={f[0]} {f[1]:.2f}" for k,v,f in hits) if hits else "none"))
    return hits

drags=[]
drags += drag(lambda t:t["comp"], book, aug, "component", 1)
drags += drag(lambda t:t["stock"], book, aug, "stock", 2)
drags += drag(lambda t:t["dir"], book, aug, "dir", 1)
drags += drag(lambda t:t["setup"], [t for t in book if t["comp"]=="F4"], [t for t in aug if t["comp"]=="F4"], "F4 setup", 1)
drags += drag(lambda t:t["leg"], [t for t in book if t["comp"]=="F4"], [t for t in aug if t["comp"]=="F4"], "F4 leg", 1)
drags += drag(lambda t:"[0.5,0.75)" if t["premove_pct"]<0.75 else "[0.75,1.0)", [t for t in book if t["comp"]=="F4"], [t for t in aug if t["comp"]=="F4"], "F4 band", 1)
drags += drag(lambda t:t.get("event_status"), [t for t in book if t.get("event_status")], [t for t in aug if t.get("event_status")], "event", 1)

# Exact OC-4 comparison for F4 August: S065 (oc3 dump) vs S080 (oc4 dump)
def f4aug(path):
    out={}
    for r in rd(path):
        if r["date"].startswith("2026-08") and not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection":
            out[(r["date"], r["symbol"], int(r["round"]))] = r
    return out
old=f4aug("stocks_engine_oc3_f4t150_trades.csv")
new=f4aug("stocks_engine_oc4_f4s080_trades.csv")
print(f"\nF4 AUGUST S065: {len(old)} tr net {round(sum(float(r['net']) for r in old.values()),2)}")
print(f"F4 AUGUST S080: {len(new)} tr net {round(sum(float(r['net']) for r in new.values()),2)}")
print("Matched deltas worst first:")
rows=[]
for k in sorted(set(old)|set(new)):
    o=float(old[k]["net"]) if k in old else 0.0
    n=float(new[k]["net"]) if k in new else 0.0
    rows.append((round(n-o,2), k, o, n, old.get(k,{}).get("exit_reason"), new.get(k,{}).get("exit_reason"), old.get(k,{}).get("setup") or new.get(k,{}).get("setup"), old.get(k,{}).get("dir") or new.get(k,{}).get("dir"), old.get(k,{}).get("leg") or new.get(k,{}).get("leg")))
for d,k,o,n,oe,ne,su,di,le in sorted(rows)[:25]:
    print(f" {k} {di} {su} {le}: S065 {o:.2f} ({oe}) -> S080 {n:.2f} ({ne}) delta {d:.2f}")
changed=[r for r in rows if abs(r[0])>0.01]
print(f"changed matched trades: {len(changed)}, total delta {round(sum(r[0] for r in changed),2)}")

# S080 exit progress in August: stop exits severity etc.
f4aug080=[t for t in aug if t["comp"]=="F4"]
for er in sorted(set(t["exit_reason"] for t in f4aug080)):
    sel=[t for t in f4aug080 if t["exit_reason"]==er]
    print(f"F4 Aug exit {er}: n={len(sel)} net={round(sum(t['net'] for t in sel),2)}")

print("\nAugust biggest losers:")
for t in sorted(aug, key=lambda x:x["net"])[:15]:
    print(f" {t['date']} {t['stock']:12} {t['comp']:8} {t['dir']:5} setup={t.get('setup')} leg={t.get('leg')} entry={t['entry_time']} exit={t['exit_reason']} net={t['net']:.2f}")

out={"anchor_ok":anchor_ok,"aug_trades":len(aug),"aug_net":round(sum(t['net'] for t in aug),2),
"f4_aug_s065_net":round(sum(float(r['net']) for r in old.values()),2),"f4_aug_s080_net":round(sum(float(r['net']) for r in new.values()),2),
"changed_trades":[{"key":str(k),"delta":d,"old":o,"new":n,"old_exit":oe,"new_exit":ne,"setup":su,"dir":di,"leg":le} for d,k,o,n,oe,ne,su,di,le in sorted(rows) if abs(d)>0.01]}
json.dump(out, open(f"{BASE}/stocks_engine_au1_diag.json","w"), indent=1)
print("wrote stocks_engine_au1_diag.json")
