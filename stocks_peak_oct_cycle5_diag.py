#!/usr/bin/env python3
"""PEAK LAB CYCLE 5 - DIAGNOSIS at Cycle-3 banked basis (F4 @ T150/S125).
(i) MTM profile of F4 square-off trades at 13:00/14:00/14:30/15:00 closes vs 15:10.
(ii) F4 qualifier sub-band split [0.5,0.75) vs [0.75,1.0) (abs premove).
Anchors asserted. Paper, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1 = M2F.H1
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":9173.84,"2026-02":4939.87,"2026-03":21673.47,"2026-04":-632.4,
        "2026-05":26032.03,"2026-06":-817.99,"2026-07":1962.07,"2026-08":739.35,
        "2026-09":14970.43,"2026-10":53290.52}
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw, aud = build_f4(1.50, 1.25)
dump = rd("stocks_peak_oct_cycle3_f4s125_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S125 rebuild == cycle3 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")
inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
def filt(raw_):
    return [t for t in raw_ if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
f4 = filt(raw)
def mt(trades):
    m=defaultdict(float)
    for t in trades: m[t["date"][:7]]+=float(t["net"])
    return {k: round(v,2) for k,v in sorted(m.items())}
bt = mt(inv+n4+p2f+[{"date":t["date"],"net":float(t["net"])} for t in f4])
b_ok = bt == PEAK
print("ANCHOR B: union == cycle3 peak table:", b_ok, "| total", round(sum(float(t['net']) for t in inv+n4+p2f+f4),2) if False else bt)
assert a_ok and b_ok and aud["violations"]==0

ns = H1.M.get_ns(H1.WHICH)
TIMES = ["13:00","14:00","14:30","15:00"]
# (i) square-off MTM
sq_all = [t for t in f4 if t["exit_reason"]=="square_off"]
rows=[]
missing=[]
for t in sq_all:
    ctx = ns["DAYCTX"].get((t["symbol"], t["date"]))
    candles = ctx["candles"]
    cmap = {c["time"]: c for c in candles}
    sign = 1 if t["dir"]=="LONG" else -1
    entry = float(t["entry"])
    alt={}
    for tm in TIMES+["15:10"]:
        c = cmap.get(tm)
        if c is None: missing.append((t["date"],t["symbol"],tm)); alt[tm]=None
        else: alt[tm]=round(100.0*sign*(float(c["close"])-entry)-40.0,2)
    rows.append({"date":t["date"],"stock":t["symbol"],"dir":t["dir"],"setup":t["setup"],"round":int(t["round"]),
                 "entry_time":t["entry_time"],"entry":entry,"exit_time":t["exit_time"],"orig_net":float(t["net"]),
                 "premove_pct":float(t["premove_pct"]), **{f"net_{tm.replace(':','')}":alt[tm] for tm in TIMES+["15:10"]}})
print(f"\nSquare-off trades: full {len(rows)} | exit_times set: {set(r['exit_time'] for r in rows)} | missing bars: {len(missing)}")
# sanity: alt 15:10 should equal orig (close of 15:10 bar)
diffs=[abs(r["net_1510"]-r["orig_net"]) for r in rows if r["net_1510"] is not None]
print(f"max |alt1510 - orig| = {max(diffs) if diffs else None}")
def agg(rs, label):
    out={"label":label,"n":len(rs),"orig_net":round(sum(r["orig_net"] for r in rs),2),
         "orig_losers":sum(1 for r in rs if r["orig_net"]<0),"orig_loser_net":round(sum(r["orig_net"] for r in rs if r["orig_net"]<0),2)}
    for tm in TIMES:
        k=f"net_{tm.replace(':','')}"
        vals=[r[k] for r in rs if r[k] is not None]
        out[tm]={"n":len(vals),"net":round(sum(vals),2),"delta_vs_1510":round(sum(vals)-sum(r["orig_net"] for r in rs if r[k] is not None),2),
                 "losers":sum(1 for v in vals if v<0),"loser_net":round(sum(v for v in vals if v<0),2),
                 "winners":sum(1 for v in vals if v>=0)}
    print(f"\n{label}: n={out['n']} orig {out['orig_net']} losers {out['orig_losers']} ({out['orig_loser_net']})")
    for tm in TIMES: print(f"  {tm}: net {out[tm]['net']:>10.2f} delta {out[tm]['delta_vs_1510']:>+10.2f} losers {out[tm]['losers']} ({out[tm]['loser_net']})")
    return out
agg_oct = agg([r for r in rows if r["date"].startswith("2026-10")], "OCTOBER square-offs")
agg_full = agg(rows, "FULL square-offs")
# per-month delta for best times
print("\nPer-month square-off delta vs 15:10:")
for tm in TIMES:
    k=f"net_{tm.replace(':','')}"
    mm=defaultdict(float)
    for r in rows:
        if r[k] is not None: mm[r["date"][:7]]+= r[k]-r["orig_net"]
    print(f"  {tm}: " + " ".join(f"{m}:{round(v,2):+.2f}" for m,v in sorted(mm.items())))
# decay detail Oct losers
oct_rows=[r for r in rows if r["date"].startswith("2026-10")]
print("\nOctober square-off losers (orig) detail:")
for r in sorted(oct_rows, key=lambda x: x["orig_net"]):
    if r["orig_net"]<0:
        print(f"  {r['date']} {r['stock']:12} {r['dir']:5} r{r['round']} orig {r['orig_net']:>9.2f} | 1300 {r['net_1300']} 1400 {r['net_1400']} 1430 {r['net_1430']} 1500 {r['net_1500']}")

# (ii) sub-band split
print("\n=== F4 sub-band split (abs premove) ===")
def band(t): 
    a=abs(float(t["premove_pct"])); return "[0.5,0.75)" if a<0.75 else "[0.75,1.0)"
split={}
for b in ["[0.5,0.75)","[0.75,1.0)"]:
    allb=[t for t in f4 if band(t)==b]; octb=[t for t in allb if t["date"].startswith("2026-10")]
    split[b]={"full_n":len(allb),"full_net":round(sum(float(t['net']) for t in allb),2),
              "full_losers":sum(1 for t in allb if float(t['net'])<0),"full_loser_net":round(sum(float(t['net']) for t in allb if float(t['net'])<0),2),
              "oct_n":len(octb),"oct_net":round(sum(float(t['net']) for t in octb),2),
              "oct_losers":sum(1 for t in octb if float(t['net'])<0),"oct_loser_net":round(sum(float(t['net']) for t in octb if float(t['net'])<0),2),
              "oct_by_exit":{}}
    from collections import Counter
    split[b]["oct_by_exit"]=dict(Counter(t["exit_reason"] for t in octb))
    print(f"{b}: full {len(allb)} net {split[b]['full_net']} losers {split[b]['full_losers']} ({split[b]['full_loser_net']}) | Oct {len(octb)} net {split[b]['oct_net']} losers {split[b]['oct_losers']} ({split[b]['oct_loser_net']}) exits {split[b]['oct_by_exit']}")
    # months for band
    mm=defaultdict(float)
    for t in allb: mm[t["date"][:7]]+=float(t["net"])
    print(f"   months: " + " ".join(f"{m}:{round(v,2)}" for m,v in sorted(mm.items())))
json.dump({"anchorA":a_ok,"anchorB":b_ok,"audit":aud,"sq_oct":agg_oct,"sq_full":agg_full,"sq_rows":rows,"subband":split},
          open(f"{BASE}/stocks_peak_oct_cycle5_diag.json","w"), indent=1)
print("\nwrote stocks_peak_oct_cycle5_diag.json")
