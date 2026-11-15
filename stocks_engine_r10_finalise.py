#!/usr/bin/env python3
"""ROUND 10 — WS5 combinations (R10-07) + WS4 stack-price
maintenance and finalise (R10-08).

R10-07: Round 10 banked ZERO candidates (R10-02 fails (e);
R10-03 fails (e)+(f); R10-04 fails (e); R10-06 produced no
candidate) — the WS5 union rule has nothing to resolve and
closes by statement.
R10-08: ending books (= starting books) exported to the r10
CSVs and independently re-summed; the four stack prices
restated on the ending book by rebuilding each stack form
with its NE-REV slot (the ending book carries no NE-REV-family
rows, so the frozen dedupe is vacuous — asserted in code) and
checked to the paisa against the recorded Round-8/9 prices.
State updated: round10_summary, incumbent, cycles, flags.
"""
import sys, csv, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r10_lib as R10
import stocks_engine_r9_ingredients as ING
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r10_results.json"))}
assert not any(res[c].get("banked") for c in
               ("R10-02", "R10-03", "R10-04")), "unexpected banking"
assert res["R10-02"]["legs"]["e_extop3"] is False
assert res["R10-04"]["legs"]["e_extop3"] is False

R10.record_audit(
    "R10-07",
    "WS5 combinations of Round-10 bankings — closes by "
    "statement",
    "Round 10 banked ZERO candidates: R10-02 NE-REV-NU "
    "standalone fails leg (e) only (2025 JO -> 89,119.61; no "
    "flips); R10-03 NE-REV-NOTCH standalone fails (e)+(f) "
    "(2025 JO -> 96,440.19; Dec 2025 flips to -632.67); "
    "R10-04 NE-REV-NOTCHCELL standalone fails leg (e) only "
    "(2025 JO -> 84,986.53; 2026 JO -> 2,56,909.60; no "
    "flips); R10-06 produced no candidate (no separator). "
    "With no bankings there is no union to re-gate. The three "
    "conditioned NE-REV forms join the flagged list as "
    "standalone owner decisions; their stack-slot prices "
    "stand as restated in R10-08.")

books = R10.load_books()
ing = ING.build_all()
cond = ING.build_cond()

# ending books export + independent re-sum
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r10_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in books[yr]:
            w.writerow({k: t[k] for k in FIELDS})
    rows = list(csv.DictReader(open(path)))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    assert (len(rows), jo, full) == (R10.ROWS_BASE[yr],
                                     R10.JO_BASE[yr],
                                     R10.FULL_BASE[yr]), (yr, jo)

# stack restatement (decision support): slot rows deduplicated
# against banked NE-REV-family rows in the ending book — there
# are none (asserted), so each price must reproduce exactly.
assert not any(t["comp"].startswith("NE-REV")
               for yr in (2025, 2026) for t in books[yr])
base = ING.apply_r503(ING.apply_r226(books, ing), ing)

def stack_jo(slot_rows):
    out = R10.add_comp(base, slot_rows[2025][0]["comp"], slot_rows)
    out = R10.add_comp(out, "REXP", ing["rexp"])
    return {yr: R10.jo(out, yr) for yr in (2025, 2026)}

prices = {
    "unconditioned_R8-02": (stack_jo(ing["cert_r"]),
                            {2025: 123231.11, 2026: 247547.25}),
    "A_NOTCH_R9-02": (stack_jo(cond["notch"]["real"]),
                      {2025: 127134.02, 2026: 244461.23}),
    "C_NOTCHUPGUARD_R9-04": (stack_jo(cond["notchup"]["real"]),
                             {2025: 119813.44, 2026: 247178.79}),
    "IDXCELL_R9-08": (stack_jo(cond["idxcell"]["real"]),
                      {2025: 113146.38, 2026: 257803.88}),
}
restated = {}
for name, (got, want) in prices.items():
    assert got == want, (name, got, want)
    restated[name] = {str(yr): got[yr] for yr in (2025, 2026)}
    print(f"stack {name}: restated {got} == recorded {want}")

R10.record_audit(
    "R10-08",
    "WS4 stack-price maintenance + finalise (decision "
    "support)",
    "Ending book is the starting book (zero bankings); "
    "exported to stocks_engine_r10_book{2025,2026}_trades.csv "
    "and independently re-summed to the paisa (2025 JO "
    "78,420.04 / 887 rows; 2026 JO 2,29,696.21 / 969 rows). "
    "Stack prices restated on the ending book by full "
    "rebuild (NE-REV slot dedupe vacuous — the book carries "
    "no NE-REV rows; asserted) and reproduced EXACTLY: "
    "unconditioned (R8-02) 2025 JO 1,23,231.11 / 2026 JO "
    "2,47,547.25 (fails (f)); Variant A NOTCH (R9-02) "
    "1,27,134.02 / 2,44,461.23 (fails (f) Dec only); Variant "
    "C NOTCH+UPGUARD (R9-04) 1,19,813.44 / 2,47,178.79 "
    "(passes all ten legs); IDXCELL slot (R9-08) 1,13,146.38 "
    "/ 2,57,803.88 (passes all ten legs). Adoption values on "
    "the ending book are unchanged from Round 9. Stack forms "
    "remain alternatives — never additive.",
    extra={"stack_prices_restated": restated})

# ------------------------------------------------------ state ---
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round10_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 3,
    "decision_support": 1,
    "audits": 4,
    "banked": 0,
    "voided_rows": 0,
    "report": "stocks_engine_round10_2026-11-02.md",
    "evidence": "r10_results.json",
    "ending_book": "2025 JO 78,420.04; 2026 JO 2,29,696.21 "
                   "(unchanged from Round 9 — zero bankings)",
    "workstreams": {
        "WS1_NU_standalone": "R10-02 REJECTED on (e) only: "
            "2025 JO -> 89,119.61, 2026 JO -> 2,53,440.61, no "
            "flips, placebos beaten. The R9-04 stack-slot form "
            "does NOT pass standalone — leg (e) is supplied "
            "by the stack, not the sleeve.",
        "WS1_NOTCH_standalone": "R10-03 REJECTED on (e)+(f): "
            "2025 JO -> 96,440.19, Dec 2025 flips to -632.67 "
            "(UPGUARD is the December cure in every context).",
        "WS2_NOTCHCELL": "R10-01 algebra audit: literal "
            "IDXCELL x NOTCH combinations collapse (cap = "
            "IDXCELL, cup = NOTCH). R10-04 composed form "
            "NE-REV-NOTCHCELL REJECTED on (e) only: 2025 JO "
            "-> 84,986.53, 2026 JO -> 2,56,909.60, no flips.",
        "WS3_July": "R10-05 audit: July wound's offender is "
            "INV-ABOVE (-2,473.45, entirely shallow-dip-state "
            "rows). Separator test FAILS at leg (iii): the "
            "shallow bucket is a combined two-year earner "
            "for the component (+2,445.28; 2026 +3,066.24). "
            "R10-06 closes by statement — no candidate.",
        "WS4_stack_prices": "All four stack prices restated "
            "on the ending book and reproduced to the paisa "
            "(R10-08). C and IDXCELL forms still pass all "
            "ten legs as decision support.",
        "WS5_combinations": "R10-07 closes by statement — "
            "zero bankings.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r10_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r10_book2026_trades.csv",
    "book_id": "R10-FINAL = R9-FINAL unchanged (Round 10 "
               "banked nothing; exports verified identical "
               "to the starting book by re-sum)",
}
st["cycles_completed"] += [
    "R10-01 AUDIT (starting-book re-verification + NE-REV "
    "admission-rule algebra: IDXCELL subset IDX subset NOTCH; "
    "NU = NOTCH cap UPGUARD)",
    "R10-02 REJECTED (NE-REV-NU standalone; fails e only)",
    "R10-03 REJECTED (NE-REV-NOTCH standalone; fails e + f)",
    "R10-04 REJECTED (NE-REV-NOTCHCELL standalone; fails e "
    "only)",
    "R10-05 AUDIT (July-2025 decomposition x index-state: "
    "offender INV-ABOVE x shallow-dip; separator fails leg "
    "iii)",
    "R10-06 AUDIT (July variant closes by statement — no "
    "separator)",
    "R10-07 AUDIT (WS5 combinations: none — zero bankings)",
    "R10-08 DECISION-SUPPORT (stack prices restated on the "
    "ending book; reproduced exactly)",
]
st["flagged_awaiting_chandu"] += [
    {"id": "R10-02", "candidate": "NE-REV-NU standalone "
     "(NOTCH+UPGUARD conditioned NE-REV, the R9-04 stack-slot "
     "ingredient on the banked book)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; no flips. Adoption on the R10 "
             "book -> 2025 JO Rs89,119.61, 2026 JO "
             "Rs2,53,440.61. NE-REV-family alternative.",
     "delta_2025_jan_oct": 10699.57,
     "delta_2026_jan_oct": 23744.4},
    {"id": "R10-03", "candidate": "NE-REV-NOTCH standalone "
     "(NOTCH conditioned NE-REV, the R9-02 stack-slot "
     "ingredient on the banked book)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": "fails (e)+(f); Dec 2025 flips to -632.67. "
             "Adoption on the R10 book -> 2025 JO "
             "Rs96,440.19, 2026 JO Rs2,50,723.05. NE-REV-"
             "family alternative.",
     "delta_2025_jan_oct": 18020.15,
     "delta_2026_jan_oct": 21026.84},
    {"id": "R10-04", "candidate": "NE-REV-NOTCHCELL standalone "
     "(NOTCH x DOWN+FLAT-cell restriction on CERT)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; no flips; highest 2026 of the "
             "conditioned forms. Adoption on the R10 book -> "
             "2025 JO Rs84,986.53, 2026 JO Rs2,56,909.60. "
             "NE-REV-family alternative.",
     "delta_2025_jan_oct": 6566.49,
     "delta_2026_jan_oct": 27213.39},
]
st["consecutive_no_bank"] = 4
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"), indent=1)
print("state updated: round10_summary, incumbent -> r10 CSVs, "
      "8 cycles, 3 new flagged entries (24 total)")

for yr in (2025, 2026):
    sc = FL.scorecard(books[yr], yr)
    print(yr, "JO", sc["jan_oct_total"], "trades",
          sc["jan_oct_trades"], "ex_top3_JO-basis full",
          sc["ex_top3_stocks"], "months", sc["months"])
print("finalise done.")
