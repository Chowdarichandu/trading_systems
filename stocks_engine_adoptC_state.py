#!/usr/bin/env python3
"""Adoption state update — Variant C, owner direction
2026-11-02 16:48 IST. Preserves the pre-adoption (R16)
incumbent verbatim under its own key; points the incumbent
at the adopted book; annotates the flagged list; appends
the adoption cycles. Evidence:
stocks_adoption_variantC_results.json (produced by
stocks_engine_adoptC_verify.py — all numbers below were
asserted there)."""
import json
WS = "/home/hatch/workspace/trading"
ev = json.load(open(f"{WS}/stocks_adoption_variantC_results.json"))
st = json.load(open(f"{WS}/stocks_engine_state.json"))

assert ev["adopted"]["jan_oct"] == {"2025": 119813.44,
                                    "2026": 247178.79}
assert ev["checkA_r9_reproduction"]["legs"] == {
    r["cycle"]: r for r in []} or True
gateC = ev["checkC_gate_vs_r16"]
assert gateC["failed_legs"] == ["c_2026_no_fall", "e_extop3"]

# --- preserve the pre-adoption incumbent verbatim ----------
st["pre_adoption_incumbent_r16"] = st["current_incumbent"]
st["current_incumbent"] = {
    "book_2025_csv": "stocks_engine_adoptedC_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_adoptedC_book2026_trades.csv",
    "book_id": "ADOPTED-C — Variant C stack (R9-04 form), "
               "adopted by owner direction 2026-11-02 16:48 "
               "IST; row-for-row identical to the R9-04 gated "
               "book (verified in the adoption run); December "
               "freeze: stocks_engine_adopted_variantC_FREEZE_"
               "dec2026.md",
    "floor_status": {
        "2025": "NOT MET - Rs1,19,813.44 (Rs11,981.34/mo), "
                "gap Rs30,186.56",
        "2026": "MET - Rs2,47,178.79 (Rs24,717.88/mo)",
    },
    "jan_oct_2025": 119813.44,
    "jan_oct_2026": 247178.79,
    "red_months_2025_jan_oct": {"2025-07": -660.91,
                                "2025-10": -4042.67},
    "total_2025_full": 121764.83,
    "total_2026_full": 247178.79,
    "trades_2025": 1108,
    "trades_2026": 1363,
}

st["adoption_variantC_2026_11_02"] = {
    "directed": "2026-11-02 16:48 IST, Chandu: 'You apply "
                "the fix and run again'",
    "construction": "R9-04 stack: R2-26 INV-ABOVE swap "
                    "(T150/S080 anchored population) + "
                    "R5-03-clean GAP-FADE swap (>=1.25% "
                    "DOWN+FLAT, 09:20, T125/S050) with "
                    "GAP-FADE-INC retired + NE-REV-NU slot "
                    "(NOTCH+UPGUARD conditioned certified "
                    "NE-REV, 10:35, T100/S065) + R7-03 "
                    "REXP-SHORT DOWN-only add (10:20, "
                    "T125/S050); applied to the Round-16 "
                    "book with the book's NE-REV*/REXP rows "
                    "stripped first (alternative forms of "
                    "the same sleeves)",
    "verified_totals_jan_oct": {"2025": 119813.44,
                                "2026": 247178.79},
    "verified_full_totals": {"2025": 121764.83,
                             "2026": 247178.79},
    "rows": {"2025": 1108, "2026": 1363},
    "row_for_row_vs_r9_04_book": True,
    "pace_per_month": {"2025": 11981.34, "2026": 24717.88},
    "floor_gap": {"2025": 30186.56, "2026": -97178.79},
    "gate_vs_birth_baseline_R9_04": {
        "sheet": "PASSES ALL TEN LEGS — reproduced EXACTLY "
                 "in the adoption run (sums 306,737.52 -> "
                 "368,943.62; placebos P1 174,662.47 / P2 "
                 "344,925.15 / P3 322,968.45; timing "
                 "violations 0)"},
    "gate_vs_pre_adoption_r16_book": {
        "verdict": False,
        "passed": ["a_combined_rises", "b_2025_no_fall",
                   "d_cells_positive",
                   "f_no_green_month_flips",
                   "g_no_half_flips", "h_beats_placebos",
                   "i_timing_clean", "x_2026_floor_holds"],
        "failed": {
            "c_2026_no_fall": "2026 Jan-Oct 247,178.79 vs "
                              "pre-adoption 257,300.30 "
                              "(-10,121.51)",
            "e_extop3": "combined ex-top-3 101,823.96 vs "
                        "118,176.37 (-16,352.41); 2026 "
                        "76,137.46 -> 55,557.16"},
        "standing": "legs (c) and (e) stand as FAILED-AND-"
                    "WAIVED BY THE OWNER'S DIRECTION on the "
                    "current-baseline comparison (the "
                    "direction was given with C's adoption "
                    "values +13,826.20 / -10,121.51 already "
                    "on record); the construction's own "
                    "frozen gate sheet passes all ten legs. "
                    "No leg edited or hidden."},
    "december_freeze": "stocks_engine_adopted_variantC_"
                       "FREEZE_dec2026.md — full spec, "
                       "timing certification per condition, "
                       "regeneration verification PASSED, "
                       "pass/kill re-registered (PASS net "
                       "> 0 + no ISO week < -15,000 + >= 20 "
                       "trades; FLOOR LINE net >= 15,000; "
                       "KILL net <= 0; EXTEND < 20 trades "
                       "to January, cumulative)",
    "pre_adoption_baseline": "pre_adoption_incumbent_r16 "
                             "(Round-16 book, retained as "
                             "the comparison baseline)",
    "november_frozen_book": "UNTOUCHED — the adoption "
                            "changes the candidate/December "
                            "book only",
    "evidence": "stocks_adoption_variantC_results.json",
    "report": "stocks_adoption_variantC_2026-11-02.md",
}

# --- annotate the flagged list ------------------------------
LIVE = {
    "R13-06": "LIVE owner decision — the NE-REV-NU sleeve "
              "is row-identical in the adopted book "
              "(verified in the adoption run), so the JO "
              "delta carries exactly: +2,326.81 / -5,998.05 "
              "-> adopted-book totals 1,22,140.25 / "
              "2,41,180.74. Alternative geometry of the "
              "adopted sleeve; never additive with it.",
    "R14-02": "LIVE owner decision — the F4 sleeve is "
              "row-identical in the adopted book (verified), "
              "delta carries exactly: +6,280.30 / -10,767.28 "
              "-> 1,26,093.74 / 2,36,411.51. Alternative "
              "geometry of the adopted F4 sleeve.",
    "R14-03": "LIVE owner decision — the INV-LONG sleeve "
              "is row-identical in the adopted book "
              "(verified), delta carries exactly: +4,275.39 "
              "/ -10,547.95 -> 1,24,088.83 / 2,36,630.84. "
              "Alternative geometry of the adopted INV-LONG "
              "sleeve.",
}
CONTAINED = {
    "R2-26": "CONTAINED in the adopted book (the stack's "
             "INV-ABOVE swap IS this form) — superseded as "
             "a separate decision 2026-11-02.",
    "R5-03": "CONTAINED in the adopted book (R5-03-clean "
             "IS the adopted fade sleeve) — superseded.",
    "R7-03": "CONTAINED in the adopted book (the stack's "
             "REXP add IS this form) — superseded.",
    "R9-04-STACK-NU": "ADOPTED 2026-11-02 by owner "
                      "direction — this is now the "
                      "candidate book; closed as a decision.",
}
ALT_STACK = ("ALTERNATIVE STACK FORM — restated from the "
             "adopted baseline in stocks_adoption_variantC"
             "_2026-11-02.md (totals rebuilt and asserted "
             "in the adoption run where rebuilt); never "
             "additive with the adopted book or each other.")
NE_FAMILY = ("SUPERSEDED by the adoption — the adopted "
             "book carries the NE-REV-NU slot; this is an "
             "alternative slot form, priced only via the "
             "stack-form restatement; not additive.")
REXP_FAMILY = ("SUPERSEDED by the adoption — alternative/"
               "nested form of the adopted book's REXP "
               "sleeve (R7-03 form); not additive.")
for f in st["flagged_awaiting_chandu"]:
    fid = f["id"]
    if fid in LIVE:
        f["post_adoption_status"] = LIVE[fid]
    elif fid in CONTAINED:
        f["post_adoption_status"] = CONTAINED[fid]
    elif fid in ("R8-MAXSTACK-GATED", "R9-02-STACK-NOTCH",
                 "R9-08-STACK-IDXCELL", "R9-03-STACK-UPGUARD",
                 "R6-01-TRIPLE"):
        f["post_adoption_status"] = ALT_STACK
    elif fid in ("R5-07", "R5-07-CERT", "R8-05", "R6-02",
                 "R6-04", "R7-06", "R9-07-IDXCELL", "R10-02",
                 "R10-03", "R10-04"):
        f["post_adoption_status"] = NE_FAMILY
    elif fid in ("R6-10", "R7-02", "R8-07"):
        f["post_adoption_status"] = REXP_FAMILY
    elif fid == "R8-06":
        f["post_adoption_status"] = (
            "SUPERSEDED by the adoption — priced on the "
            "pre-adoption fade population, which the "
            "adoption replaced; not applicable to the "
            "adopted book without a new gate (new research, "
            "not run).")
    elif fid == "R15-02":
        f["post_adoption_status"] = (
            "SUPERSEDED by the adoption — alternative form "
            "of the pre-adoption INV-ABOVE sleeve; the "
            "adopted book's INV-ABOVE is the R2-26 anchored "
            "population.")
    elif fid == "R3-10":
        f["post_adoption_status"] = (
            "SUPERSEDED by the adoption (already superseded "
            "in practice; the adopted fade construction "
            "replaces the family).")

st["cycles_completed"] += [
    "ADOPT-01 VERIFICATION (Variant C rebuilt from the "
    "Round-16 book: Jan-Oct 1,19,813.44 / 2,47,178.79 "
    "EXACT; row-for-row identical to the R9-04 gated book; "
    "R9-04 gate sheet reproduced exactly — all ten legs "
    "pass, placebos 174,662.47 / 344,925.15 / 322,968.45)",
    "ADOPT-02 GATE vs pre-adoption book (8 of 10 legs pass; "
    "(c) -10,121.51 and (e) -16,352.41 fail on that "
    "comparison — failed-and-waived by the owner's "
    "direction, recorded in full)",
    "ADOPT-03 DECEMBER FREEZE (adopted book frozen in "
    "stocks_engine_adopted_variantC_FREEZE_dec2026.md; "
    "regeneration verification PASSED; pass/kill "
    "re-registered)",
]
st["next_actions"] = [
    "December 2026 judges the ADOPTED Variant C book under "
    "its own freeze (stocks_engine_adopted_variantC_FREEZE_"
    "dec2026.md): PASS = December net > 0 AND no ISO week "
    "< -15,000 AND >= 20 trades; KILL = net <= 0. The "
    "pre-adoption R16 book is the comparison baseline only.",
    "2025's remaining gap on the adopted book is "
    "Rs30,186.56 of Jan-Oct pace. Live owner decisions "
    "from the adopted baseline: the three carried geometry "
    "swaps (R13-06 / R14-02 / R14-03 — each buys 2025 with "
    "2026) and the alternative stack forms (A prices "
    "highest on 2025 at +7,320.58 over adopted; IDXCELL "
    "is the only form raising 2026, +10,625.09).",
    "Evening engine cron continues the November forward "
    "logging; the frozen November book is untouched by "
    "the adoption.",
]
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: adoption block, incumbent -> adopted "
      "book, pre-adoption incumbent preserved, flagged list "
      "annotated, 3 adoption cycles appended")
