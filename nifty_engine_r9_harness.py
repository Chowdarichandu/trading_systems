#!/usr/bin/env python3
"""RUN 3 ROUND 9 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Baseline: the Round-6/7/8 standing book
(+54,102.00, causal 35 legs, lock60/TGT2-175, sq 15:20). Freeze:
nifty_engine_frozen.md ROUND 9 section (written before any Round-9
candidate scoring).

Workstreams: WS1 fade's last cell (with-trend x entry 10:05), WS2
flagged-pair gate (DECISION SUPPORT, force-no-bank), WS3 causal-May
diagnosis + conditional candidate (Bank WS1 separator standard), WS4
causal union (solo-(lA) legs the confirmation window missed, at (lA)'s
own bar), WS5 combinations/closure.

Gate: RELATIVE gate is the banking test (net up, FT and frequency not
degraded vs the standing baseline, no baseline-green month flips red, no
red month-ends, halves >= 0, placebo beaten, ex-top-3 >= 0, audit clean,
NC = 0, re-sum exact). OLD ABSOLUTE lines (FT >= 42.0%, frequency
>= 1.00/wk) printed as STATUS ONLY for every verdict.

Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0.
November primary untouched (read-only at most)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
from nifty_engine_r2_harness import candles_exact, audit_exact, pool_sets
from nifty_engine_score import controls

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
STANDING_GEOM = R7.STANDING_GEOM

def run_r9(name, legs, save=True, gate=True, force_no_bank=False):
    """Round-7 run form, Round-9 summary prefix. force_no_bank: the gate
    is computed and printed in full but the cycle is DECISION SUPPORT —
    callers must never treat it as a banking or update the standing book."""
    res, nc, nc_legs = R6.score_r6(legs, geom=STANDING_GEOM)
    pl, _, _ = R6.score_r6(legs, geom=STANDING_GEOM, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["june"] = c["month_table"].get("2026-06", [0, 0])[0]
    c["march"] = c["month_table"].get("2026-03", [0, 0])[0]
    c["nc_named_not_computed"] = ("2026-10-28 22500 PE weekly expiry 2026-11-03 — NOT_COMPUTED "
                                  "(registry 0 contracts, Rounds 3-6); not in any Round-9 population")
    if force_no_bank:
        c["decision_support_force_no_bank"] = True
    if gate and R6.CURRENT["total"] is not None:
        banked, rel, abs_lines, g2r = R6.gate_r6(c)
        c["gate_relative"] = {"banked": banked, "checks": rel, "green_to_red": g2r,
                              "vs_label": R6.CURRENT["label"], "vs_total": R6.CURRENT["total"],
                              "vs_ft_pct": R6.CURRENT["ft_pct"], "vs_per_week": R6.CURRENT["per_week"]}
        c["old_absolute_lines_status"] = abs_lines
    if save:
        Path(TR / f"nifty_engine_run3r9_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    g = c.get("gate_relative", {})
    a = c.get("old_absolute_lines_status", {})
    tag = " [DECISION SUPPORT — FORCE NO BANK]" if force_no_bank else ""
    print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
          f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
          f"exT3 {c['ex_top3']:+,.2f} | Mar {c['march']:+,.2f} | May {c['may']:+,.2f} | Jun {c['june']:+,.2f} | Aug {c['august']:+,.2f} | "
          f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
          f"REL-GATE {'BANKED' if g.get('banked') else 'FAIL ' + str([k for k, v in g.get('checks', {}).items() if not v])} | "
          f"ABS-LINES FT42 {'PASS' if a.get('FT>=42.0') else 'FAIL'} / FREQ1.00 {'PASS' if a.get('freq>=1.00/wk') else 'FAIL'} (status only){tag}")
    return c, res

def score_sleeve_alone(name, legs):
    return R7.score_sleeve_alone(name, legs)

# ---------------- WS4: causal union population ----------------
def union_legs(exclude_keys):
    """EXP0 pool keys with (lA) v2 among sources AND >= 2 sources AND key
    not in the standing book; entry at (lA)'s OWN sysmap time, strike
    re-struck ATM100 at that bar. Returns (legs, excluded_named)."""
    S = R6.sysmap()
    _, _, EXP0 = pool_sets()
    legs, excluded = [], []
    for l in EXP0:
        srcs = R6.sources_of(l)
        if "(lA) v2" not in srcs or len(srcs) < 2: continue
        if (l["date"], l["direction"]) in exclude_keys:
            excluded.append((l["date"], l["direction"], "key-in-standing-book")); continue
        t = S.get((l["date"], l["direction"]), {}).get("(lA) v2")
        if t is None:
            excluded.append((l["date"], l["direction"], "lA-time-missing")); continue
        nl = dict(l); nl["entry_time"] = t
        if t != l["entry_time"]:
            so = R6.spot_open(l["date"], t)
            if so is None:
                excluded.append((l["date"], l["direction"], "no-spot-bar")); continue
            nl["strike"] = R6.atm100(so)
        nl["rep"] = "R9-UNION-lA"
        nl["family"] = "R9WS4"
        legs.append(nl)
    return legs, excluded

def missing_candles(legs):
    return R7.missing_candles(legs)
