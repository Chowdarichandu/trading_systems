#!/usr/bin/env python3
"""ROUND 2 sanity: the generalised core must reproduce book v14 (+104,567.00,
82 legs, FT 53.7, placebo 10,830.70, ex-top3 75,527.00, halves 84,980/19,587)
and book v8 (+77,196.50) through the new code paths before any grid cell is read."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import build_fixed, controls, V14, V8

for name, params, expect in (("v14", V14, dict(net=104567.00, n=82, placebo=10830.70,
                                              ex_top3=75527.00, jm=84980.0, jo=19587.0)),
                             ("v8", V8, dict(net=77196.50, n=82, placebo=None,
                                             ex_top3=None, jm=None, jo=None))):
    rows, nc, lbk = build_fixed(params, delay=0)
    prows, pnc, _ = build_fixed(params, delay=6)
    c = controls(rows, nc, lbk, prows, pnc)
    print(f"== {name}: n={c['n']} net={c['net']} ft={c['ft_pct']} ft90={c['ft90_pct']} "
          f"pw={c['per_week_raw']} nc={c['not_computed']} reds={c['red_month_ends']}")
    print(f"   placebo net={c['placebo']['net']} nc={c['placebo']['not_computed']} | "
          f"ex_top3={c['ex_top3_total']} | halves={c['halves']} | viol={len(c['timing_violations'])}")
    print(f"   months={c['months']}")
    ok = (c["net"] == expect["net"] and c["n"] == expect["n"] and c["not_computed"] == 0
          and c["timing_violations"] == [] and c["red_month_ends"] == [])
    if expect["placebo"] is not None:
        ok = ok and c["placebo"]["net"] == expect["placebo"] and c["ex_top3_total"] == expect["ex_top3"] \
            and c["halves"]["jan_may"] == expect["jm"] and c["halves"]["jun_oct"] == expect["jo"]
    print(f"   SANITY {'PASS' if ok else '*** FAIL ***'}")
