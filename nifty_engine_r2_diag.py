#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from datetime import date
from nifty_engine_r2_harness import pool, nsrc, score_g, pool_sets
from collections import defaultdict

B, C3L, EXP0 = pool_sets()
EXP0set = {(l["date"], l["direction"]) for l in EXP0}
def d(s): y, m, dd = s.split("-"); return date(int(y), int(m), int(dd))
res, nc, _ = score_g(EXP0); assert nc == 0
netmap = {(r["date"], r["direction"]): r["net"] for r in res}
legmap = {(l["date"], l["direction"]): l for l in B}

print("=== POOL COMPOSITION (108 N1 pool legs) ===")
comp = defaultdict(int)
for l in B: comp[(nsrc(l), l["rep"])] += 1
for k in sorted(comp): print("  nsrc", k[0], "| rep", k[1], "| legs", comp[k])

print("\n=== EXP0 BOOK COMPOSITION (59) ===")
cc = defaultdict(lambda: [0, 0.0])
for l in EXP0:
    cls = "confirmed" if nsrc(l) >= 2 else "solo-(lA)"
    cc[cls][0] += 1; cc[cls][1] += netmap[(l["date"], l["direction"])]
for k, (n, s) in cc.items(): print(f"  {k}: {n} legs, net {round(s,2):+,.2f}")

print("\n=== SOLO LEGS IN POOL NOT IN C3L (candidates for gated admission) ===")
solos = [l for l in B if nsrc(l) == 1 and l["rep"] != "(lA) v2"]
byrep = defaultdict(list)
for l in solos: byrep[l["rep"]].append(l)
for rep, ls in byrep.items():
    early = [l for l in ls if l["entry_time"] < "10:00"]
    late = [l for l in ls if l["entry_time"] >= "10:00"]
    print(f"  {rep}: total {len(ls)}, <10:00 {len(early)}, >=10:00 {len(late)}")
late_all = [l for l in solos if l["entry_time"] >= "10:00"]
late_exp0 = [l for l in late_all if l["date"] != l["expiry"]]
print("  late solos total:", len(late_all), "| after EXP0:", len(late_exp0))
r2, nc2, _ = score_g(late_exp0)
print("  late solos scored under book geometry:", len(r2), "nc", nc2,
      "sum net", round(sum(x['net'] for x in r2), 2))
for x in sorted(r2, key=lambda x: x["date"]):
    print(f"    {x['date']} {x['direction']} {x['rep']} @{x['entry_time']} net {x['net']:+,.2f} {x['exit_reason']}")

print("\n=== (lA)-ANCHORED SET: legs with (lA) in sources, EXP0 ===")
la = [l for l in B if "(lA) v2" in (l["sources"] or "")]
la_exp0 = [l for l in la if l["date"] != l["expiry"]]
print("  legs:", len(la), "| after EXP0:", len(la_exp0))
inpool = [l for l in la_exp0 if (l["date"], l["direction"]) in EXP0set]
print("  of those, already in EXP0 book:", len(inpool),
      "| extra (solo?? none expected):", len(la_exp0) - len(inpool))

print("\n=== DTE BUCKETS ON EXP0 BOOK (by incumbent net) ===")
buck = defaultdict(lambda: [0, 0.0])
for l in EXP0:
    dte = (d(l["expiry"]) - d(l["date"])).days
    b = "0" if dte == 0 else "1" if dte == 1 else "2-4" if dte <= 4 else "5+"
    buck[b][0] += 1; buck[b][1] += netmap[(l["date"], l["direction"])]
for b in ("1", "2-4", "5+"):
    print(f"  DTE {b}: {buck[b][0]} legs, net {round(buck[b][1],2):+,.2f}")
print("  (DTE 0 legs were removed by EXP0; count in C3L:", 
      sum(1 for l in C3L if l["date"] == l["expiry"]), ")")

print("\n=== EXPIRY-WEEK LEGS (DTE 1-4) in EXP0 book ===")
ew = [l for l in EXP0 if 1 <= (d(l["expiry"]) - d(l["date"])).days <= 4]
print("  legs:", len(ew), "net:", round(sum(netmap[(l['date'], l['direction'])] for l in ew), 2))
