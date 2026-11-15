#!/usr/bin/env python3
"""ROUND 10 — WS1: conditioned NE-REV forms STANDALONE.

R10-01 (audit): starting-book verification (independent CSV
re-sum vs the recorded totals) + the WS2 admission-rule algebra
on the CERT population, verified in code.
R10-02: NE-REV-NU (NOTCH+UPGUARD) gated as a whole-book addition
to the banked book — the exact rows Round 9 gated only as a
stack slot (R9-04). R10-03: NE-REV-NOTCH standalone, likewise
(R9-02's ingredient). Placebos: flipped / one-bar-late rows
under the identical conditions (R9-07 convention). Timing
violations: the CERT build's counted violations (asserted 0).
"""
import sys, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r10_lib as R10
import stocks_engine_r9_ingredients as ING
import stocks_engine_r8_builders as B8

# ------------------------------------------------------- R10-01 -
raw = {}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r9_book{yr}_trades.csv")))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    raw[yr] = (len(rows), jo, full)
    assert jo == R10.JO_BASE[yr] and full == R10.FULL_BASE[yr], \
        (yr, jo, full)
    assert len(rows) == R10.ROWS_BASE[yr], (yr, len(rows))

books = R10.load_books()
ing = ING.build_all()
cond = ING.build_cond()
viol = ing["viol_c"]
assert viol == 0, viol

cert_ids = {yr: {R10.row_id(t) for t in ing["cert"][yr]}
            for yr in (2025, 2026)}
idx_ids = {yr: {R10.row_id(t) for t in ing["idx_r"][yr]}
           for yr in (2025, 2026)}
notch_ids = {yr: {R10.row_id(t) for t in cond["notch"]["real"][yr]}
             for yr in (2025, 2026)}
upg_ids = {yr: {R10.row_id(t) for t in cond["upguard"]["real"][yr]}
           for yr in (2025, 2026)}
nu_ids = {yr: {R10.row_id(t) for t in cond["notchup"]["real"][yr]}
          for yr in (2025, 2026)}
idxcell_ids = {yr: {R10.row_id(t)
                    for t in cond["idxcell"]["real"][yr]}
               for yr in (2025, 2026)}
checks = {}
for yr in (2025, 2026):
    # every IDX row carries move <= -0.30 (its own admission rule),
    # hence satisfies NOTCH — verified per row, not assumed
    mv_bad = 0
    for t in ing["idx_r"][yr]:
        mv = B8.nifty_move(t["date"], "10:25")
        if mv is None or mv > -0.30:
            mv_bad += 1
    checks[yr] = {
        "cert": len(cert_ids[yr]), "idx": len(idx_ids[yr]),
        "idxcell": len(idxcell_ids[yr]), "notch": len(notch_ids[yr]),
        "upguard": len(upg_ids[yr]), "nu": len(nu_ids[yr]),
        "idx_mv_violations": mv_bad,
        "idx_subset_cert": idx_ids[yr] <= cert_ids[yr],
        "idxcell_subset_idx": idxcell_ids[yr] <= idx_ids[yr],
        "idx_subset_notch": idx_ids[yr] <= notch_ids[yr],
        "nu_eq_notch_cap_upguard":
            nu_ids[yr] == (notch_ids[yr] & upg_ids[yr]),
    }
    c = checks[yr]
    assert c["idx_mv_violations"] == 0, (yr, c)
    assert c["idx_subset_cert"] and c["idxcell_subset_idx"], (yr, c)
    assert c["idx_subset_notch"], (yr, c)
    assert c["nu_eq_notch_cap_upguard"], (yr, c)
R10.record_audit(
    "R10-01",
    "Starting-book verification + WS2 admission-rule algebra "
    "(audit — no candidate scored)",
    f"Starting books re-summed independently from the Round-9 "
    f"CSVs: 2025 {raw[2025][0]} rows, JO {raw[2025][1]}, full "
    f"{raw[2025][2]}; 2026 {raw[2026][0]} rows, JO "
    f"{raw[2026][1]}, full {raw[2026][2]} — exact vs the "
    f"recorded totals. Algebra on CERT (291/370): IDXCELL "
    f"({checks[2025]['idxcell']}/{checks[2026]['idxcell']}) "
    f"subset IDX ({checks[2025]['idx']}/{checks[2026]['idx']}) "
    f"subset CERT, and every IDX row verified per-row to carry "
    f"NIFTY 10:25 move <= -0.30 (0 violations), hence to "
    f"satisfy NOTCH (IDX subset of NOTCH's "
    f"{checks[2025]['notch']}/{checks[2026]['notch']} rows); "
    f"NU row set == NOTCH cap UPGUARD exactly in both years. "
    f"The literal set-combinations of {{IDXCELL, NOTCH}} "
    f"therefore collapse to already-gated forms (cap = "
    f"IDXCELL, R9-07; cup = NOTCH, R10-03) — the distinct "
    f"composed form is NE-REV-NOTCHCELL as frozen in the "
    f"Round-10 pre-registration, gated in R10-04.",
    extra={"book_check": {str(k): v for k, v in raw.items()},
           "algebra": {str(k): v for k, v in checks.items()}})

# ------------------------------------------------- gate helper --
def gate_form(cycle, form_key, comp, label):
    f = cond[form_key]
    real, flip, late = f["real"], f["flip"], f["late"]
    var = R10.add_comp(books, comp, real)
    pl = [R10.full_total(R10.add_comp(books, comp, flip)),
          R10.full_total(R10.add_comp(books, comp, late))]
    out = R10.gate(books, var, pl, timing_violations=viol)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    R10.record(
        cycle, label, out,
        note=f"standalone addition of the exact Round-9 "
             f"ingredient rows: standalone {sa[2025]} (2025) / "
             f"{sa[2026]} (2026) on {len(real[2025])}/"
             f"{len(real[2026])} rows; state-unknown rows "
             f"dropped {f['real_unknown']} (counted, never "
             f"guessed). Placebos (identical conditions): "
             f"flipped book {pl[0]}; one-bar-late book {pl[1]}. "
             f"Timing violations {viol}. Failed legs: {failed}.",
        extra={"standalone": {str(k): v for k, v in sa.items()},
               "population_trades": {"2025": len(real[2025]),
                                     "2026": len(real[2026])},
               "failed_legs": failed})
    return out

# ------------------------------------------------------- R10-02 -
gate_form("R10-02", "notchup", "NE-REV-NU",
          "NE-REV-NU standalone (NOTCH+UPGUARD conditioned "
          "NE-REV; the R9-04 stack-slot ingredient gated on "
          "the banked book)")

# ------------------------------------------------------- R10-03 -
gate_form("R10-03", "notch", "NE-REV-NOTCH",
          "NE-REV-NOTCH standalone (NOTCH conditioned NE-REV; "
          "the R9-02 stack-slot ingredient gated on the banked "
          "book)")
print("WS1 done.")
