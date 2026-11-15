#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from datetime import date
from nifty_engine_r2_harness import pool, nsrc, run_cycle, pool_sets, validate_incumbent

INC_TOT, INC_FT = 98001.0, 39.0
INC_MONTHS = {"2026-01": 20646.50, "2026-02": 13592.00, "2026-03": 13630.00,
              "2026-04": 8436.50, "2026-05": -5793.00, "2026-06": 5400.00,
              "2026-07": 12239.00, "2026-08": -3671.00, "2026-09": 5371.00,
              "2026-10": 28150.00}
def d(s): y, m, dd = s.split("-"); return date(int(y), int(m), int(dd))
def verdict(c, ref_ft=INC_FT, ref_tot=INC_TOT, extra=""):
    g2r = [m for m, v in INC_MONTHS.items()
           if v > 0 and c["month_table"].get(m, [0, 0])[0] < 0]
    ok = (c["total"] > ref_tot and c["ft_pct"] >= ref_ft - 3.0
          and not g2r and c["halves"]["Jan-May"] >= 0 and c["halves"]["Jun-Oct"] >= 0
          and c["total"] > c["placebo_shift30_total"]
          and c["timing_audit"]["violations"] == 0 and c["not_computed"] == 0)
    print(f"  TOTAL {c['total']:+,.2f} | trades {c['n']} | FT {c['ft_pct']}% | "
          f"{c['per_week']}/wk | halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | "
          f"placebo {c['placebo_shift30_total']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
          f"g2r {g2r} | audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | "
          f"resum {c['resum_ok']} | NC {c['not_computed']} | {'BANK-CANDIDATE' if ok else 'NO-BANK'} {extra}")
    return ok

B, C3L, EXP0 = pool_sets()
print("incumbent validated: 59 trades +98,001.00")

# ---------- PHASE A ----------
print("\n== CYCLE 22 P1: pure 2-of-4 (no solo-(lA)) ==")
P1 = [l for l in EXP0 if nsrc(l) >= 2]
c, _ = run_cycle("run3r2_cycle22", P1); verdict(c)
print(f"  (dropped {len(EXP0)-len(P1)} solo-(lA) legs)")

print("\n== CYCLE 23 P2: (lA)-mandatory ==")
P2 = [l for l in EXP0 if "(lA) v2" in (l["sources"] or "")]
c, _ = run_cycle("run3r2_cycle23", P2); verdict(c)
print(f"  (legs {len(P2)} of 59)")

print("\n== CYCLE 24 P3: solo admission, entry >= 10:00 ==")
solos = [l for l in B if nsrc(l) == 1 and l["rep"] != "(lA) v2"
         and l["entry_time"] >= "10:00" and l["date"] != l["expiry"]]
keys = {(l["date"], l["direction"]) for l in EXP0}
P3 = EXP0 + [l for l in solos if (l["date"], l["direction"]) not in keys]
c, _ = run_cycle("run3r2_cycle24", P3)
verdict(c, extra=f"| NC legs: {c['nc_legs']}")

# ---------- PHASE B: G7 GRID ----------
print("\n== CYCLES 25-33: G7 GRID on EXP0 book ==")
cells = [(40,130),(40,150),(40,175),(50,130),(50,150),(50,175),(60,130),(60,150),(60,175)]
grid = {}
for i, (lk, t2) in enumerate(cells):
    cyc = 25 + i
    print(f"-- cycle {cyc}: lock{lk} tgt2-{t2}")
    c, _ = run_cycle(f"run3r2_cycle{cyc}", EXP0, lock=lk, tgt2=t2)
    verdict(c)
    grid[(lk, t2)] = c["total"]

# ---------- PHASE C ----------
print("\n== CYCLE 34 EXP1: skip DTE<=1 ==")
E1 = [l for l in EXP0 if (d(l["expiry"]) - d(l["date"])).days != 1]
c, _ = run_cycle("run3r2_cycle34", E1); verdict(c)
print(f"  (dropped {len(EXP0)-len(E1)} DTE-1 legs)")

print("\n== CYCLE 35 EW-G7: DTE 1-4 legs at lock50/tgt150 ==")
def ew_geom(l):
    dte = (d(l["expiry"]) - d(l["date"])).days
    return (50.0, 150.0) if 1 <= dte <= 4 else (75.0, 180.0)
c, _ = run_cycle("run3r2_cycle35", EXP0, geom_by_leg=ew_geom); verdict(c)

print("\nGRID TOTALS:", {f"{k[0]}/{k[1]}": round(v, 2) for k, v in grid.items()})
best = max(grid, key=grid.get)
print("best grid cell:", best, round(grid[best], 2))
