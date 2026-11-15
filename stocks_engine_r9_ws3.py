#!/usr/bin/env python3
"""ROUND 9 — WS3: NE-REV-IDX DECEMBER REPAIR.

R9-06 (audit): decomposition of the R8-05 IDX form's
December-2025 rows — 3 rows, all UP-regime cell (BDL 2025-12-08
-991.79, HINDCOPPER 2025-12-16 -125.00, BDL 2025-12-16
-929.85; sum -2,046.64 = the form's whole December delta).
R9-07: the frozen repair — NE-REV-IDXCELL (IDX rows restricted
to DOWN+FLAT regime cells) — gated standalone as a whole-book
addition (bankable ingredient). R9-08: the max stack priced
with the NE-REV slot = NE-REV-IDXCELL (decision support,
force_no_bank; placebos shaped as in WS1).
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
cond = ING.build_cond()
books = ing["books"]
viol = ing["viol_c"]
assert viol == 0, viol

# ------------------------------------------------------------- R9-06 -
idx = ing["idx_r"]
dec = {}
for yr in (2025, 2026):
    rows = [t for t in idx[yr] if t["date"][:7] == f"{yr}-12"]
    dec[yr] = (len(rows), round(sum(t["net"] for t in rows), 2))
up = {}
for yr in (2025, 2026):
    rows = [t for t in idx[yr] if R9.LABELS.get(t["date"]) == "UP"]
    up[yr] = (len(rows), round(sum(t["net"] for t in rows), 2))
R9.record_audit(
    "R9-06",
    "WS3 decomposition of NE-REV-IDX December rows (audit — no "
    "candidate scored)",
    f"IDX December rows: 2025: {dec[2025][0]} rows net "
    f"{dec[2025][1]} (2025-12-08 BDL -991.79; 2025-12-16 "
    f"HINDCOPPER -125.00; 2025-12-16 BDL -929.85 — every one on "
    f"an UP-regime day, every one with NIFTY <= -0.30% by the "
    f"form's own admission rule); 2026: {dec[2026][0]} rows. "
    f"The IDX UP-cell bucket overall: 2025 {up[2025][0]} rows "
    f"net {up[2025][1]}; 2026 {up[2026][0]} rows net "
    f"{up[2026][1]} — the December wound is 3 rows inside a "
    f"bucket that is the form's best 2025 cell and its only "
    f"negative 2026 cell. The frozen separator (Round-9 "
    f"pre-registration) is the regime cell itself: IDXCELL "
    f"drops UP-cell rows. Stated cost before scoring: the "
    f"repair removes +6,022.69 of 2025 standalone to remove "
    f"-2,046.64 of December rows.",
    extra={"idx_dec_rows": {str(k): v for k, v in dec.items()},
           "idx_up_bucket": {str(k): v for k, v in up.items()}})

# ------------------------------------------------------------- R9-07 -
f = cond["idxcell"]
real, flip, late = f["real"], f["flip"], f["late"]
COMP = "NE-REV-IDX"
var = R9.add_comp(books, COMP, real)
pl = [R9.full_total(R9.add_comp(books, COMP, flip)),
      R9.full_total(R9.add_comp(books, COMP, late))]
out = R9.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
R9.record(
    "R9-07",
    "NE-REV-IDXCELL (R8-05 IDX rows restricted to DOWN+FLAT "
    "regime cells)", out,
    note=f"repaired ingredient standalone: {sa[2025]} (2025) / "
         f"{sa[2026]} (2026) on {len(real[2025])}/"
         f"{len(real[2026])} rows (IDX population 201/252; the "
         f"UP-cell restriction removes {201 - len(real[2025])}/"
         f"{252 - len(real[2026])} rows). December-2025 delta "
         f"of the repaired form: "
         f"{R9.month_net(real[2025], '2025-12')} (the unrepaired "
         f"IDX form: -2,046.64) — no December rows remain, so "
         f"the (f) exposure is removed by construction. "
         f"Placebos (same cell restriction): flipped book "
         f"{pl[0]}; one-bar-late book {pl[1]}. Timing "
         f"violations {viol}. Failed legs: {failed}.",
    extra={"standalone": {str(k): v for k, v in sa.items()},
           "population_trades": {"2025": len(real[2025]),
                                 "2026": len(real[2026])}})

# ------------------------------------------------------------- R9-08 -
out8 = ING.apply_r503(ING.apply_r226(books, ing), ing)
var8 = R9.add_comp(out8, COMP, real)
var8 = R9.add_comp(var8, "REXP", ing["rexp"])

p1 = ING.without(books, "GAP-FADE-INC")
p1 = R9.swap(p1, "INV-ABOVE", ing["above150_short"])
p1 = R9.swap(p1, "GAP-FADE", ing["sleeve125_mirror"])
p1 = R9.add_comp(p1, COMP, flip)
p1 = R9.add_comp(p1, "REXP", ing["rexp_flip"])

p2base = ING.apply_r503(ING.apply_r226(books, ing), ing)
p2 = R9.add_comp(p2base, COMP, late)
p2 = R9.add_comp(p2, "REXP", ing["rexp"])

p3base = ING.without(
    R9.swap(ING.apply_r226(books, ing), "GAP-FADE",
            ing["sleeve125_late"]), "GAP-FADE-INC")
p3 = R9.add_comp(p3base, COMP, real)
p3 = R9.add_comp(p3, "REXP", ing["rexp"])

pl8 = [R9.full_total(p1), R9.full_total(p2), R9.full_total(p3)]
viol8 = ing["viol_c"] + ing["viol_r"]
outg = R9.gate(books, var8, pl8, timing_violations=viol8)
jan = R9.month_net(var8[2025], "2025-01")
dec8 = R9.month_net(var8[2025], "2025-12")
failed8 = [k for k, v in outg["legs"].items()
           if isinstance(v, bool) and not v]
R9.record(
    "R9-08",
    "DECISION SUPPORT: MAX STACK with NE-REV-IDXCELL in the "
    "NE-REV slot — NOT a banking", outg,
    note=f"stack months: Jan 2025 -> {jan} (base +2,200.31; "
         f"unconditioned stack -715.46; IDX-slot stack cured "
         f"Jan at R8-05's sleeve level); Dec 2025 -> {dec8} "
         f"(base +1,207.95; unconditioned stack -99.76; the "
         f"repaired slot carries no December rows). Failing "
         f"legs: {failed8}; flips: {outg['legs']['flip_detail']}. "
         f"Placebos: P1 all-placebo {pl8[0]}; P2 IDXCELL late "
         f"{pl8[1]}; P3 gap sleeve late {pl8[2]}. Timing "
         f"violations {viol8}. Adoption is Chandu's; nothing "
         f"banked here regardless of verdict.",
    extra={"stack_jan_2025": jan, "stack_dec_2025": dec8,
           "failed_legs": failed8},
    force_no_bank=True)
print("WS3 done.")
