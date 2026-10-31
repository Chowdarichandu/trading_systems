#!/usr/bin/env python3
"""ENGINE OC-2 STEP 1: October diagnosis of the banked union book +
DBL-LONG anchor verification. Read-only. Paper, real Rs0, per 100 sh."""
import csv, sys
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("M1", "/home/hatch/workspace/trading/stocks_M1.py")
M1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M1)
BASE = "/home/hatch/workspace/trading"

def is_weekend(d):
    import datetime
    return datetime.date.fromisoformat(d).weekday() >= 5

def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

# --- components with RF-1 applied (drop weekend-session trades) ---
inv = [t for t in M1.load_inv_long() if not is_weekend(t["date"])]
n4  = [t for t in M1.load_n4() if not is_weekend(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not is_weekend(t["date"])]
f4 = []
for r in rd("stocks_M2_F4_trades.csv"):
    if is_weekend(r["date"]): continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"]), "entry_time": r["entry_time"],
               "exit_reason": r["exit_reason"], "setup": r["setup"],
               "premove_pct": float(r["premove_pct"])})
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(lambda: [0, 0.0])
    for t in trades:
        k = t["date"][:7]; m[k][0] += 1; m[k][1] += t["net"]
    return {k: (v[0], round(v[1], 2)) for k, v in sorted(m.items())}

print("=== UNION ANCHOR CHECK vs state (expect total 97574.23, 1043 trades, Oct 43011.62) ===")
t = mt(book)
print("trades:", len(book), "total:", round(sum(x['net'] for x in book), 2))
for k, v in t.items(): print(" ", k, v)

oct_trades = [x for x in book if x["date"].startswith("2026-10")]
print("\n=== OCTOBER BY COMPONENT ===")
for comp in ["INV-LONG", "N4-V3", "P2F", "F4"]:
    sel = [x for x in oct_trades if x["comp"] == comp]
    print(f"  {comp}: {len(sel)} trades net={round(sum(x['net'] for x in sel),2)}")
print("\n=== OCTOBER BY STOCK (worst 12 / best 6) ===")
bs = defaultdict(float); cnt = defaultdict(int)
for x in oct_trades: bs[x["stock"]] += x["net"]; cnt[x["stock"]] += 1
for s, v in sorted(bs.items(), key=lambda kv: kv[1])[:12]: print(f"  {s}: {cnt[s]} tr net={round(v,2)}")
print("  ...")
for s, v in sorted(bs.items(), key=lambda kv: -kv[1])[:6]: print(f"  {s}: {cnt[s]} tr net={round(v,2)}")
print("\n=== OCTOBER BY DAY (negative days) ===")
bd = defaultdict(float); cd = defaultdict(int)
for x in oct_trades: bd[x["date"]] += x["net"]; cd[x["date"]] += 1
neg = {d: v for d, v in bd.items() if v < 0}
print(f"  {len(neg)} negative days of {len(bd)} traded days; sum neg days = {round(sum(neg.values()),2)}")
for d, v in sorted(neg.items(), key=lambda kv: kv[1]): print(f"  {d}: {cd[d]} tr net={round(v,2)}")
print("\n=== F4 OCTOBER LOSERS (detail) ===")
f4o = [x for x in oct_trades if x["comp"] == "F4"]
los = [x for x in f4o if x["net"] < 0]; win = [x for x in f4o if x["net"] >= 0]
print(f"  F4 Oct: {len(f4o)} trades, {len(win)} win +{round(sum(x['net'] for x in win),2)}, {len(los)} lose {round(sum(x['net'] for x in los),2)}")
for x in sorted(los, key=lambda z: z["net"]):
    print(f"  {x['date']} {x['stock']} {x['dir']} setup={x['setup']} premove={x['premove_pct']}% entry@{x['entry_time']} exit={x['exit_reason']} net={x['net']}")
print("\n=== F4 OCTOBER LOSERS BY QUALIFIER BAND / DIR / SETUP ===")
def band(p): return "[0.5,0.75)" if abs(p) < 0.75 else "[0.75,1.0)"
for key, fn in [("band", lambda x: band(x["premove_pct"])), ("dir", lambda x: x["dir"]), ("setup", lambda x: x["setup"])]:
    agg = defaultdict(lambda: [0, 0.0])
    for x in f4o: agg[fn(x)][0] += 1; agg[fn(x)][1] += x["net"]
    print(f"  by {key}: " + "; ".join(f"{k}: {v[0]} tr {round(v[1],2)}" for k, v in sorted(agg.items())))

print("\n=== DBL-LONG ANCHOR CHECK (expect 133 trades, +24327.37, Oct +7957.95, halves +15426.61/+8900.76) ===")
dbl = []
for r in rd("tuning_inv_L1b_S2_DBL_LONG_T125_S050_trades.csv"):
    dbl.append({"date": r["date"], "stock": r["stock"], "comp": "DBL-LONG", "dir": r["direction"],
                "net": float(r["net_rs_provisional_per100"]), "entry_time": r["entry_time"],
                "exit_reason": r["exit_reason"], "setup": r["setup"]})
print("trades:", len(dbl), "total:", round(sum(x['net'] for x in dbl), 2))
dm = mt(dbl)
for k, v in dm.items(): print(" ", k, v)
jm = round(sum(v[1] for k, v in dm.items() if k <= "2026-05"), 2)
jn = round(sum(v[1] for k, v in dm.items() if k >= "2026-06"), 2)
print("halves Jan-May / Jun-Oct:", jm, "/", jn)
dbl_we = [x for x in dbl if is_weekend(x["date"])]
print("DBL weekend-session (RF-1) trades:", len(dbl_we), "net:", round(sum(x['net'] for x in dbl_we), 2),
      [(x['date'], x['stock'], x['net']) for x in dbl_we])
print("DBL October trades:", dm.get("2026-10"))
# overlap with INV-LONG (same date+stock+entry_time)
invkeys = {(x["date"], x["stock"], x["entry_time"]) for x in inv}
ov = [x for x in dbl if (x["date"], x["stock"], x["entry_time"]) in invkeys]
print("DBL trades identical to an INV-LONG trade (date+stock+entry_time):", len(ov),
      "net:", round(sum(x['net'] for x in ov), 2))
