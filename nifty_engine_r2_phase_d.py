#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from datetime import date
from nifty_engine_r2_harness import pool, nsrc, run_cycle, pool_sets, validate_incumbent

INC_MONTHS = {"2026-01": 20646.50, "2026-02": 13592.00, "2026-03": 13630.00,
              "2026-04": 8436.50, "2026-05": -5793.00, "2026-06": 5400.00,
              "2026-07": 12239.00, "2026-08": -3671.00, "2026-09": 5371.00,
              "2026-10": 28150.00}
def d(s): y, m, dd = s.split("-"); return date(int(y), int(m), int(dd))
def verdict_ch3(c):
    g2r = [m for m, v in INC_MONTHS.items() if v > 0 and c["month_table"].get(m, [0, 0])[0] < 0]
    std = (c["total"] > 98001.0 and c["ft_pct"] >= 36.0 and not g2r
           and c["halves"]["Jan-May"] >= 0 and c["halves"]["Jun-Oct"] >= 0
           and c["total"] > c["placebo_shift30_total"]
           and c["timing_audit"]["violations"] == 0 and c["not_computed"] == 0)
    fam = (c["august"] >= -3671.0) and (c["per_week"] >= 1.30)
    print(f"  TOTAL {c['total']:+,.2f} | trades {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
          f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
          f"May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | g2r {g2r} | audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | "
          f"resum {c['resum_ok']} | NC {c['not_computed']}")
    print(f"  standard gate: {'PASS' if std else 'FAIL'} | CH3 family clauses (Aug >= -3,671; freq >= 1.30/wk): {'PASS' if fam else 'FAIL'} "
          f"-> {'BANKED' if (std and fam) else 'NOT BANKED'}")

validate_incumbent()
B, C3L, EXP0 = pool_sets()
CH3R = [l for l in EXP0 if not (nsrc(l) >= 2 and l["entry_time"] > "09:55")]
print(f"CH3-R leg set: {len(CH3R)} legs")

print("\n== CYCLE 36: CH3-R x grid-best (lock50/TGT2-175) ==")
c, _ = run_cycle("run3r2_cycle36", CH3R, lock=50.0, tgt2=175.0); verdict_ch3(c)

print("\n== CYCLE 37: CH3-R x EW-G7 ==")
def ew(l):
    dte = (d(l["expiry"]) - d(l["date"])).days
    return (50.0, 150.0) if 1 <= dte <= 4 else (75.0, 180.0)
c, _ = run_cycle("run3r2_cycle37", CH3R, geom_by_leg=ew); verdict_ch3(c)

print("\n== CYCLE 38: CH3S (confirmed-only, entry <= 09:55) ==")
CH3S = [l for l in EXP0 if nsrc(l) >= 2 and l["entry_time"] <= "09:55"]
print(f"CH3S leg set: {len(CH3S)} legs")
c, _ = run_cycle("run3r2_cycle38", CH3S); verdict_ch3(c)
