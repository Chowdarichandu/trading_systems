#!/usr/bin/env python3
"""ROUND 4 WS4 (Cycle 97): the ONE candidate the frozen near-miss audit
permits. In the flagged stack, legs with DTE >= 14 keep their own exit
assembly with the stop widened -50 -> -65 (trig/lock/tgt2/square-off
unchanged). Exactness pre-check: re-scoring every matched leg at its own
assembly (stop unchanged) must reproduce its stored row exactly."""
import datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r2_core import controls, gate
from bank_r2_expiry import LBK
from bank_r2_ns1 import V15
from bank_r4_core import build_stack, score_leg, stack_ref, REF17

TR = Path.home() / "workspace/trading"

def own_params(row, leg):
    if leg["date"] == leg["expiry"]:
        return dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
    return dict(V15[row["segment"]])

def transform(delay):
    rows, nc, lbk, detail = build_stack(delay=delay)
    matched, mism = [], 0
    for i, r in enumerate(rows):
        leg = lbk[r["leg_key"]]
        dte = (dt.date.fromisoformat(leg["expiry"]) - dt.date.fromisoformat(leg["date"])).days
        if dte < 14:
            continue
        matched.append(r["leg_key"])
        p0 = own_params(r, leg)
        chk = score_leg(leg, p0, delay=delay)
        assert chk is not None
        if abs(chk["net"] - r["net"]) > 0.005 or chk.get("ft90", 0) != r.get("ft90", 0):
            mism += 1
            print(f"  MISMATCH delay={delay} {r['leg_key']}: stored {r['net']}/{r.get('ft90')} vs re-scored {chk['net']}/{chk.get('ft90')}")
            continue
        p65 = dict(p0, stop=65.0)
        nr = score_leg(leg, p65, delay=delay)
        assert nr is not None
        rows[i] = {**r, **nr}
    return rows, nc, lbk, matched, mism

def main():
    rows, nc, lbk, matched, mism = transform(0)
    prows, pnc, _pl, pmatched, pmism = transform(6)
    print(f"matched DTE>=14 legs: main {len(matched)}, placebo {len(pmatched)}; exactness mismatches: main {mism}, placebo {pmism}")
    assert mism == 0 and pmism == 0, "own-assembly reconstruction is not exact — candidate not scored"
    c = controls(rows, nc, lbk, prows, pnc)
    ok, why = gate(c, REF17)
    sref = stack_ref()
    ok_s, why_s = gate(c, sref)
    print(f"Cycle 97 WS4 flagged stack, DTE>=14 legs stop -65: net={c['net']:+,.2f} n={c['n']} "
          f"FT90={c['ft90_pct']} placebo={c['placebo']['net']:+,.2f} NC={c['not_computed']}")
    print(f"gate vs v17: pass={ok} why={why}")
    print(f"gate vs flagged stack: pass={ok_s} why={why_s}")
    json.dump(dict(controls=c, gate_v17=dict(passed=ok, failed=why),
                   gate_stack=dict(passed=ok_s, failed=why_s),
                   matched_main=len(matched), matched_placebo=len(pmatched)),
              open(TR / "bank_r4_ws4_results.json", "w"), indent=1, default=str)
    print("results -> bank_r4_ws4_results.json")

if __name__ == "__main__":
    main()
