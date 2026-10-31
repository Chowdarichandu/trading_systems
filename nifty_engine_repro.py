#!/usr/bin/env python3
"""Nifty recursive engine — incumbent reproduction.
Rebuilds C3+G7 from the frozen pool using the aggressive run's own scorer
(aggressive_score.py). C3 = legs whose source_systems count >= 2.
G7 = mode runner_lock50, stop 50, target 90.
Compares against references in aggressive_oct_nifty.md to the paisa.
Nifty ONLY. Paper, real money Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import base_legs, score_legs, agg, month_end_reds

REF_MONTHS = {
    "2026-01": 16643.75, "2026-02": 11264.00, "2026-03": 8210.00, "2026-04": 4240.75,
    "2026-05": -5793.00, "2026-06": 9131.00, "2026-07": 10809.00, "2026-08": -4129.25,
    "2026-09": -2562.25, "2026-10": 18805.25,
}
REF_TOTAL, REF_N, REF_FT_PCT = 66619.25, 56, 37.5

def confirmed(legs):
    return [l for l in legs if len([s for s in l["sources"].split(";") if s.strip()]) >= 2]

def main():
    B = base_legs("NIFTY")
    C3 = confirmed(B)
    print(f"pool legs: {len(B)}  confirmed (C3): {len(C3)}")
    res, nc = score_legs(C3, stop=50, target=90, mode="runner_lock50")
    a = agg(res, 40.6)
    reds, total, table = month_end_reds(res)
    print("scored:", a, "NOT_COMPUTED:", nc, "red_month_ends:", reds)
    ok = True
    def chk(label, got, want):
        nonlocal ok
        good = abs(got - want) < 0.005
        ok = ok and good
        print(f"  {'OK ' if good else 'FAIL'} {label}: got {got} want {want}")
    chk("total", total, REF_TOTAL)
    chk("agg total", a["net"], REF_TOTAL)
    chk("n", a["n"], REF_N)
    chk("ft_pct", a["ft_pct"], REF_FT_PCT)
    for m, want in REF_MONTHS.items():
        chk(f"month {m}", table.get(m, (None,))[0] if m in table else None or 0, want)
    print("RECONCILED" if ok and nc == 0 else "MISMATCH")
    out = {"agg": a, "not_computed": nc, "red_month_ends": reds,
           "month_table": {m: v for m, v in table.items()}, "reconciled": bool(ok and nc == 0)}
    Path("nifty_engine_repro.json").write_text(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
