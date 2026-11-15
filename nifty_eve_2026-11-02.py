#!/usr/bin/env python3
"""NIFTY EVENING ENGINE 2026-11-02 — candidates from today's blocked signal.
Today (2026-11-02) NF-PAPER-C3G7 blocked a solo Skill V3 CE key
(signal 09:35, entry 09:40) because C3 requires >=2 source systems.
Question: does adding solo Skill V3 legs (in mechanically distinct
slices) to the standing causal book (+54,102.00, 35 legs, lock60/
TGT2-175, sq 15:20) pass the full controls gate in the same run?
Candidates (one family, three distinct slices, never retested identically):
 EVE-01: standing + solo Skill CE, entry > 09:55
 EVE-02: standing + solo Skill CE, entry <= 09:55  (today's exact class)
 EVE-03: standing + solo Skill PE, entry <= 09:55
Basis: Nifty options premiums, 1 lot 65, cost 220/trade, UNIQUE-ONCE
(date+direction collisions with standing dropped and counted).
Full gate per backtest_controls_gate: timing/leak audit, placebo
(shift+30min via delay_bars=6 in harness controls), halves, full month
table, ex-top-3, independent re-sum — all inside run_r6/controls.
Paper only, real money Rs0. November primary untouched (read-only).
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r6_harness as R6
import nifty_engine_r7_harness as R7
from nifty_engine_score import pool

TR = Path.home() / "workspace/trading"
GEOM = R7.STANDING_GEOM

def main():
    standing = R7.standing_legs()
    c0, _ = R6.run_r6("nov_eve_validate_standing", standing, geom=GEOM, save=False, gate=False)
    assert c0["total"] == 54102.00 and c0["n"] == 35, (c0["total"], c0["n"])
    print(f"VALIDATION standing causal book: {c0['total']:+,.2f} n={c0['n']} FT {c0['ft_pct']}% audit {c0['timing_audit']}")
    R6.set_current(c0, "Standing causal book +54,102.00 (35 legs, lock60/TGT2-175 sq15:20)")
    skeys = {(l["date"], l["direction"]) for l in standing}

    # solo Skill V3 population from the U1 pool, EXP0-style (not expiry day)
    solo_skill = []
    for l in pool():
        srcs = R6.sources_of(l)
        if len(srcs) == 1 and srcs[0] == "Skill V3" and l["date"] != l["expiry"]:
            solo_skill.append(dict(l))
    print(f"solo Skill V3 population (EXP0-filtered): {len(solo_skill)} legs")

    def slice_legs(direction, early):
        out, coll = [], 0
        for l in solo_skill:
            if l["direction"] != direction: continue
            if early and not (l["entry_time"] <= "09:55"): continue
            if not early and not (l["entry_time"] > "09:55"): continue
            if (l["date"], l["direction"]) in skeys: coll += 1; continue
            out.append(l)
        return out, coll

    results = {}
    for name, direction, early, label in [
        ("nov_eve01_skill_ce_late", "CE", False, "EVE-01 standing + solo Skill CE entry>09:55"),
        ("nov_eve02_skill_ce_early", "CE", True, "EVE-02 standing + solo Skill CE entry<=09:55 (today's class)"),
        ("nov_eve03_skill_pe_early", "PE", True, "EVE-03 standing + solo Skill PE entry<=09:55"),
    ]:
        adds, coll = slice_legs(direction, early)
        print(f"\n[{label}] additions {len(adds)}, UNIQUE-ONCE collisions dropped {coll}")
        for a in adds: print(f"   add {a['date']} {a['direction']} entry {a['entry_time']} strike {a['strike']} exp {a['expiry']}")
        combined = standing + adds
        c, res = R6.run_r6(name, combined, geom=GEOM)
        # sleeve standalone for context
        cs, _ = R6.run_r6(name + "_sleeve", adds, geom=GEOM, save=False, gate=False)
        print(f"   sleeve standalone: {cs['total']:+,.2f} n={cs['n']} NC={cs['not_computed']} legs={cs['nc_legs']}")
        c["eve_label"] = label; c["eve_additions"] = len(adds); c["eve_collisions"] = coll
        c["eve_sleeve_total"] = cs["total"]; c["eve_sleeve_n"] = cs["n"]; c["eve_sleeve_nc"] = cs["not_computed"]
        Path(TR / f"nifty_engine_run3r6_{name}_summary.json").write_text(json.dumps(c, indent=1, default=str))
        results[name] = c
    out = {k: {"total": v["total"], "n": v["n"], "ft_pct": v["ft_pct"], "per_week": v["per_week"],
               "halves": v["halves"], "ex_top3": v["ex_top3"], "placebo": v["placebo_shift30_total"],
               "banked": v.get("gate_relative", {}).get("banked"),
               "failed": [kk for kk, vv in v.get("gate_relative", {}).get("checks", {}).items() if not vv],
               "additions": v["eve_additions"], "sleeve_total": v["eve_sleeve_total"], "nc": v["not_computed"]}
           for k, v in results.items()}
    Path(TR / "nifty_eve_2026-11-02_summary.json").write_text(json.dumps(out, indent=1))
    print("\nSUMMARY", json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
