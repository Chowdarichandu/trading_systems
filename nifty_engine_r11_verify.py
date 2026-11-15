#!/usr/bin/env python3
"""ROUND 11 Cycle 168 — DEC-S1 regeneration verification.
Rebuilds DEC-S1 from the frozen specification (nifty_engine_frozen.md
ROUND 11, S1-S5) using the certified builders, scores it under standing
geometry with the FULL controls gate in the same run, and compares every
field against the Round-9 Cycle-152 / Round-10 Cycle-167 record.
DEC-S1 is a labelled SHADOW: force-no-bank; the standing book and the
standing December candidate are never touched. Nifty only, premiums per
1 lot (65), cost 220, UNIQUE-ONCE. Paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
from nifty_engine_r2_harness import audit_exact
from nifty_engine_score import controls

TR = Path.home() / "workspace/trading"
GEOM = R7.STANDING_GEOM

EXPECTED = {
    "n": 97, "total": 91168.50, "ft_pct": 34.0, "per_week": 2.39,
    "halves": {"Jan-May": 45393.50, "Jun-Oct": 45775.00},
    "placebo": 52867.25, "ex_top3": 57703.50,
    "months": {"2026-01": 19211.25, "2026-02": 5038.75, "2026-03": -11846.50,
               "2026-04": 28416.00, "2026-05": 4574.00, "2026-06": -1331.00,
               "2026-07": 5839.00, "2026-08": 841.25, "2026-09": 20265.25,
               "2026-10": 20160.50},
    "audit_checked": 97, "audit_violations": 0, "nc": 0,
    "fade_standalone": 33624.75, "expiry_inpair_standalone": 3441.75,
    "standing_total": 54102.00,
}

def fetch_missing(legs, weekly=False):
    miss = R7.missing_candles(legs)
    if not miss:
        return
    print(f"  fetching {len(miss)} missing contracts (weekly={weekly}) ...")
    import nifty_engine_r7_fetch as F
    jobs = [(st, ty, d, exp, weekly) for (st, ty, d, exp) in miss]
    out = F.fetch_jobs(jobs)
    ok = sum(1 for _, r in out if isinstance(r, tuple)
             and r[0] not in ("NO_CONTRACTS_FILE",) and r[1])
    print(f"  fetch done: {ok}/{len(jobs)} returned candles")
    print(f"  still missing: {R7.missing_candles(legs)}")

def score(name, legs):
    res, nc, nc_legs = R6.score_r6(legs, geom=GEOM)
    pl, _, _ = R6.score_r6(legs, geom=GEOM, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    return c, res

def main():
    # ---- Component A: standing causal book (spec S2) ----
    A = R7.standing_legs()
    cA, _ = score("r11_c168_componentA", A)
    print(f"[A standing] n {cA['n']} total {cA['total']:+,.2f} "
          f"(expect +54,102.00) audit {cA['timing_audit']['checked']}/"
          f"{cA['timing_audit']['violations']} NC {cA['not_computed']} "
          f"resum {cA['resum_ok']}")

    # ---- Component B: fade-10:05 (spec S3) ----
    B, fex = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                 with_trend=False,
                                 exclude_keys=R7.keys_of(A))
    print(f"[B fade-10:05] legs {len(B)}, excluded {len(fex)}: {fex}")
    fetch_missing(B, weekly=False)
    totB, _ = R7.score_sleeve_alone("r11_c168 fade sleeve", B)
    print(f"[B fade-10:05] standalone {totB:+,.2f} (expect +33,624.75)")

    # ---- Component C: expiry sleeve (spec S4) ----
    C, eex = R8.expiry_sleeve_legs(R7.keys_of(A) | R7.keys_of(B))
    print(f"[C expiry] legs {len(C)}, excluded {len(eex)}: {eex}")
    fetch_missing(C, weekly=True)
    totC, _ = R7.score_sleeve_alone("r11_c168 expiry sleeve (in-pair)", C)
    print(f"[C expiry] in-pair standalone {totC:+,.2f} (expect +3,441.75)")

    # ---- DEC-S1 whole book (spec S1 assembly) ----
    pair = A + B + C
    c, res = score("r11_c168_decs1_regen_verify", pair)
    c["decision_support_force_no_bank"] = True
    c["shadow_label"] = "DEC-S1 (December shadow candidate — NOT adopted)"
    c["components"] = {"A_standing": len(A), "B_fade1005": len(B),
                       "C_expiry_inpair": len(C)}
    (TR / "nifty_engine_run3r11_r11_c168_decs1_regen_verify_summary.json"
     ).write_text(json.dumps(c, indent=1, default=str))
    legdump = [{"date": l["date"], "direction": l["direction"],
                "entry_time": l["entry_time"], "strike": l["strike"],
                "expiry": l["expiry"],
                "component": ("A" if l in A else "B" if l in B else "C")}
               for l in pair]
    (TR / "nifty_engine_r11_decs1_legs.json").write_text(
        json.dumps(legdump, indent=1))

    print(f"\n[DEC-S1] TOTAL {c['total']:+,.2f} | n {c['n']} | FT "
          f"{c['ft_pct']}% | {c['per_week']}/wk | halves "
          f"{c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | "
          f"placebo {c['placebo_shift30_total']:+,.2f} | exT3 "
          f"{c['ex_top3']:+,.2f} | audit {c['timing_audit']['checked']}/"
          f"{c['timing_audit']['violations']} | NC {c['not_computed']} | "
          f"resum {c['resum_ok']}")

    # ---- Field-by-field comparison vs the frozen S10 record ----
    checks = []
    def chk(label, got, want):
        ok = got == want
        checks.append(ok)
        print(f"  {'MATCH' if ok else 'MISMATCH'} {label}: got {got} "
              f"want {want}")
    chk("standing total", cA["total"], EXPECTED["standing_total"])
    chk("fade standalone", round(totB, 2), EXPECTED["fade_standalone"])
    chk("expiry in-pair standalone", round(totC, 2),
        EXPECTED["expiry_inpair_standalone"])
    chk("n legs", c["n"], EXPECTED["n"])
    chk("total", c["total"], EXPECTED["total"])
    chk("ft_pct", c["ft_pct"], EXPECTED["ft_pct"])
    chk("per_week", c["per_week"], EXPECTED["per_week"])
    chk("halves Jan-May", c["halves"]["Jan-May"], EXPECTED["halves"]["Jan-May"])
    chk("halves Jun-Oct", c["halves"]["Jun-Oct"], EXPECTED["halves"]["Jun-Oct"])
    chk("placebo", c["placebo_shift30_total"], EXPECTED["placebo"])
    chk("ex_top3", c["ex_top3"], EXPECTED["ex_top3"])
    for m, v in EXPECTED["months"].items():
        chk(f"month {m}", c["month_table"].get(m, [None])[0], v)
    chk("audit checked", c["timing_audit"]["checked"],
        EXPECTED["audit_checked"])
    chk("audit violations", c["timing_audit"]["violations"],
        EXPECTED["audit_violations"])
    chk("NC", c["not_computed"], EXPECTED["nc"])
    chk("resum exact", c["resum_ok"], True)
    chk("placebo beaten", c["total"] > c["placebo_shift30_total"], True)
    print("\nCYCLE 168 VERDICT:",
          "VERIFIED — DEC-S1 specification regenerates its Jan-Oct book "
          "leg-for-leg and to the paisa, full controls gate in the same run"
          if all(checks) else
          "MISMATCH — freeze void until reconciled in writing (see above)")
    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
