#!/usr/bin/env python3
"""ROUND 9 — WS1: STACK-MINUS-FLAW VARIANTS (R9-02/03/04).

The R8-02 max stack with the NE-REV slot conditioned by the
frozen state rules of the Round-9 pre-registration:
  R9-02 Variant A: NE-REV-NOTCH   (drop NIFTY 10:25 move in
                                  (-0.30%, 0))
  R9-03 Variant B: NE-REV-UPGUARD (UP-regime days need NIFTY
                                  10:25 move >= 0)
  R9-04 Variant C: both conditions.
All three are DECISION SUPPORT (force_no_bank) — adoption of any
stack form is Chandu's. Placebos per the freeze: P1 all-placebo
stack, P2 conditioned NE-REV one bar late, P3 gap sleeve one bar
late. Timing violations = the ingredients' own counted
violations (NE-REV 0 + REXP 0, asserted at build); the state
conditions read the 10:25 NIFTY bar (completes 10:30), strictly
before every 10:35 entry, and add none.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
cond = ING.build_cond()
books = ing["books"]
viol = ing["viol_c"] + ing["viol_r"]
assert viol == 0, viol

def stack_with(rows_by_comp):
    out = ING.apply_r503(ING.apply_r226(books, ing), ing)
    for comp, rows in rows_by_comp:
        out = R9.add_comp(out, comp, rows)
    return out

VARIANTS = [
    ("R9-02", "notch", "NE-REV-NOTCH",
     "Variant A — stack with NE-REV-NOTCH (CERT rows admitted "
     "only when NIFTY's 10:25-bar move vs prior close is NOT in "
     "(-0.30%, 0))"),
    ("R9-03", "upguard", "NE-REV-UPGUARD",
     "Variant B — stack with NE-REV-UPGUARD (CERT rows on "
     "UP-regime days admitted only when NIFTY's 10:25-bar move "
     ">= 0)"),
    ("R9-04", "notchup", "NE-REV-NU",
     "Variant C — stack with NE-REV-NOTCH+UPGUARD (both frozen "
     "conditions)"),
]

for cyc, form, comp, label in VARIANTS:
    f = cond[form]
    real, flip, late = f["real"], f["flip"], f["late"]
    var = stack_with([(comp, real), ("REXP", ing["rexp"])])

    p1 = ING.without(books, "GAP-FADE-INC")
    p1 = R9.swap(p1, "INV-ABOVE", ing["above150_short"])
    p1 = R9.swap(p1, "GAP-FADE", ing["sleeve125_mirror"])
    p1 = R9.add_comp(p1, comp, flip)
    p1 = R9.add_comp(p1, "REXP", ing["rexp_flip"])

    p2 = stack_with([(comp, late), ("REXP", ing["rexp"])])
    base503 = ING.without(
        R9.swap(ING.apply_r226(books, ing), "GAP-FADE",
                ing["sleeve125_late"]), "GAP-FADE-INC")
    p3 = R9.add_comp(base503, comp, real)
    p3 = R9.add_comp(p3, "REXP", ing["rexp"])

    pl = [R9.full_total(p1), R9.full_total(p2), R9.full_total(p3)]
    out = R9.gate(books, var, pl, timing_violations=viol)
    jan = R9.month_net(var[2025], "2025-01")
    dec = R9.month_net(var[2025], "2025-12")
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    R9.record(
        cyc, f"DECISION SUPPORT: MAX STACK with {comp} — NOT a "
             f"banking", out,
        note=f"{label}. Conditioned sleeve standalone: {sa[2025]} "
             f"(2025) / {sa[2026]} (2026) on "
             f"{len(real[2025])}/{len(real[2026])} rows (CERT "
             f"population 291/370; state-unknown rows dropped "
             f"{f['real_unknown']}, counted, never guessed). "
             f"Stack months: Jan 2025 -> {jan} (base +2,200.31; "
             f"unconditioned stack -715.46); Dec 2025 -> {dec} "
             f"(base +1,207.95; unconditioned stack -99.76). "
             f"Failing legs: {failed}; flips: "
             f"{out['legs']['flip_detail']}. Placebos: P1 "
             f"all-placebo {pl[0]}; P2 conditioned NE-REV late "
             f"{pl[1]}; P3 gap sleeve late {pl[2]}. Timing "
             f"violations {viol}. Adoption is Chandu's; nothing "
             f"banked here regardless of verdict.",
        extra={"sleeve_standalone": {str(k): v for k, v in
                                     sa.items()},
               "stack_jan_2025": jan, "stack_dec_2025": dec,
               "failed_legs": failed},
        force_no_bank=True)
print("WS1 done.")
