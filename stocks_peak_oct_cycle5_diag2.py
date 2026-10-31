import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
BASE="/home/hatch/workspace/trading"
def load_mod(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
_argv=sys.argv; sys.argv=["M2F"]
M2F=load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv=_argv
H1=M2F.H1
H1.ensure_prep()
ns=H1.M.get_ns(H1.WHICH)
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
raw=rd("stocks_peak_oct_cycle3_f4s125_trades.csv")
def wk(d): return datetime.date.fromisoformat(d).weekday()>=5
f4=[t for t in raw if not wk(t["date"]) and t["setup"]!="setup3_bounce_rejection"]
TIMES=["13:00","14:00","14:30","15:00"]
for tm in TIMES:
    for scope, rows in [("OCT",[t for t in f4 if t["date"].startswith("2026-10")]),("FULL",f4)]:
        delta=0.0; changed=0; orig_changed=0.0
        for t in rows:
            if t["exit_time"]<=tm: continue
            # trade was open after tm bar? need: did it hit target/stop in bars <= tm? Since original exit > tm and replay checks every bar from entry, if it had hit <=tm its exit would be <=tm. So no.
            ctx=ns["DAYCTX"].get((t["symbol"],t["date"])); cmap={c["time"]:c for c in ctx["candles"]}
            c=cmap.get(tm)
            if c is None: continue
            sign=1 if t["dir"]=="LONG" else -1
            alt=round(100.0*sign*(float(c["close"])-float(t["entry"]))-40.0,2)
            delta+=alt-float(t["net"]); changed+=1; orig_changed+=float(t["net"])
        print(tm, scope, f"changed={changed} orig_net_changed={round(orig_changed,2)} same-entry delta={round(delta,2)}")
    # per month for 15:00 etc printed above aggregated; also month split
    mm=defaultdict(float)
    for t in f4:
        if t["exit_time"]<=tm: continue
        ctx=ns["DAYCTX"].get((t["symbol"],t["date"])); cmap={c["time"]:c for c in ctx["candles"]}
        c=cmap.get(tm)
        if c is None: continue
        sign=1 if t["dir"]=="LONG" else -1
        alt=round(100.0*sign*(float(c["close"])-float(t["entry"]))-40.0,2)
        mm[t["date"][:7]]+=alt-float(t["net"])
    print("   months:", {k:round(v,2) for k,v in sorted(mm.items())})
# breakdown: original exit reasons for trades with exit_time > 15:00
from collections import Counter
late=[t for t in f4 if t["exit_time"]>"15:00"]
print("trades exit_time>15:00:", len(late), Counter(t["exit_reason"] for t in late), Counter(t["exit_time"] for t in late))
lo=[t for t in late if t["date"].startswith("2026-10")]
print("Oct late:", len(lo), Counter(t["exit_reason"] for t in lo))
