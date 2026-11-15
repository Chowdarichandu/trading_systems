#!/usr/bin/env python3
"""ROUND 14 — R14-08: combinations + stack-price maintenance +
December freeze addendum + finalise.

Bankings: R14-04 (INV-ABOVE geometry swap to T150/S050) and
R14-05 (GAP-FADE family geometry swap to T125/S065) — each
passed all ten legs against the starting book. They act on
disjoint components, so the union is re-gated whole-book here
against the starting book; per the standing resolution rule
the union, if it passes, is the ending book. R14-02 and
R14-03 each fail exactly two legs ((a) + (c)) and join the
flagged list with adoption values measured from the ending
book; R14-06 (four legs) and R14-07 (three legs) do not.
Stack prices restated on the ending book by the generalised
R12-09 method — totals must reproduce the recorded prices
exactly. December freeze extended to the ending book with
REGENERATION VERIFICATION: the ending book rebuilt from the
Round-13 CSVs by fresh code (both banked constructions
rebuilt) must match the exported ending CSVs row-for-row
(multiset identity) and to the paisa in both years.
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r14_lib as R14
import stocks_engine_r14_builders as B14
import stocks_engine_r9_ingredients as ING
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r14_results.json"))}
assert res["R14-04"]["banked"] is True
assert res["R14-05"]["banked"] is True
for cyc in ("R14-02", "R14-03", "R14-06", "R14-07"):
    assert res[cyc]["banked"] is False, cyc
assert res["R14-02"]["failed_legs"] == ["a_combined_rises",
                                        "c_2026_no_fall"]
assert res["R14-03"]["failed_legs"] == ["a_combined_rises",
                                        "c_2026_no_fall"]
assert res["R14-06"]["failed_legs"] == ["a_combined_rises",
                                        "b_2025_no_fall",
                                        "c_2026_no_fall",
                                        "e_extop3"]
assert res["R14-07"]["failed_legs"] == ["a_combined_rises",
                                        "b_2025_no_fall",
                                        "e_extop3"]

books = R14.load_books()

# --------------------------------------------- ending book --
inv_real, inv_side, inv_dropped = B14.inv_above_geo(1.50, 0.50)
fg = B14.fade_geo(1.25, 0.65)

def apply_swaps(bk, inv_rows, fade_sets, fade_kind="real"):
    out = R14.swap(bk, "INV-ABOVE", inv_rows)
    out = R14.swap(out, "GAP-FADE", fade_sets["GAP-FADE"][fade_kind])
    out = R14.swap(out, "GAP-FADE-INC",
                   fade_sets["GAP-FADE-INC"][fade_kind])
    return out

ending = apply_swaps(books, inv_real, fg, "real")
pl = [R14.full_total(apply_swaps(books, inv_side, fg, "flip")),
      R14.full_total(apply_swaps(books, inv_side, fg, "late"))]
out = R14.gate(books, ending, pl, timing_violations=0)
assert out["verdict"], out["legs"]
end_jo = {yr: R14.jo(ending, yr) for yr in (2025, 2026)}
print(f"union re-gate PASS: ending JO {end_jo}; placebos {pl}")
R14.record_audit(
    "R14-08",
    "WS5 combinations + stack-price maintenance + December "
    "freeze addendum + finalise",
    f"Union of Round-14 bankings = R14-04 (INV-ABOVE "
    f"T150/S050) + R14-05 (GAP-FADE family T125/S065), "
    f"re-gated whole-book against the starting book: "
    f"verdict PASS (2025 JO {out['var']['2025']['jan_oct']}; "
    f"2026 JO {out['var']['2026']['jan_oct']}; combined "
    f"{out['sums']['variant_combined']}; placebos: fade-flip "
    f"+ INV-side book {pl[0]}, fade-late + INV-side book "
    f"{pl[1]}). R14-02 rejected on (a)+(c); R14-03 on "
    f"(a)+(c); R14-06 on (a)+(b)+(c)+(e); R14-07 on "
    f"(a)+(b)+(e). Ending book exported to "
    f"stocks_engine_r14_book{{2025,2026}}_trades.csv, "
    f"independently re-summed, and regeneration-verified "
    f"against a fresh rebuild from the Round-13 CSVs "
    f"(multiset identity, both years). Stack prices "
    f"restated on the ending book (see report). December "
    f"freeze addendum (Round 14) appended.",
    extra={"union_verdict": True,
           "ending_jo": {str(k): v for k, v in end_jo.items()}})

# ------------------------------------------- stack restate --
ing = ING.build_all()
def strip_families(bk):
    return {yr: [t for t in bk[yr]
                 if not t["comp"].startswith("NE-REV")
                 and t["comp"] != "REXP"]
            for yr in (2025, 2026)}
base = strip_families(ING.apply_r503(
    ING.apply_r226(ending, ing), ing))
def stack_jo(slot_rows):
    outb = R14.add_comp(base, slot_rows[2025][0]["comp"],
                        slot_rows)
    outb = R14.add_comp(outb, "REXP", ing["rexp"])
    return {yr: R14.jo(outb, yr) for yr in (2025, 2026)}
cond = ING.build_cond()
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
restated, adopt_val = {}, {}
for name, (got, want) in prices.items():
    assert got == want, (name, got, want)
    restated[name] = {str(yr): got[yr] for yr in (2025, 2026)}
    adopt_val[name] = {str(yr): round(got[yr] - end_jo[yr], 2)
                       for yr in (2025, 2026)}
    print(f"stack {name}: totals {got} == recorded {want}; "
          f"adoption value from ending book {adopt_val[name]}")

# -------------------------------------- flag pricing (R14-02/03)
f4_real, _ff, _fl, miss = B14.f4_geo(ending, 1.75, 0.95,
                                     "plain")
assert miss == 0, miss
f4_book = R14.swap(ending, "F4", f4_real)
f4_delta = {yr: round(R14.jo(f4_book, yr) - end_jo[yr], 2)
            for yr in (2025, 2026)}
assert f4_delta == {2025: 6280.30, 2026: -10767.28}, f4_delta
print(f"R14-02 flag: adoption from ending book -> deltas "
      f"{f4_delta}")

il_real, _is = B14.inv_long_geo(1.50, 0.50)
il_book = R14.swap(ending, "INV-LONG", il_real)
il_delta = {yr: round(R14.jo(il_book, yr) - end_jo[yr], 2)
            for yr in (2025, 2026)}
assert il_delta == {2025: 4275.39, 2026: -10547.95}, il_delta
print(f"R14-03 flag: adoption from ending book -> deltas "
      f"{il_delta}")

# --------------------------------------------- export books --
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
end_full = {}
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r14_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in ending[yr]:
            w.writerow({k: t[k] for k in FIELDS})
    rows = list(csv.DictReader(open(path)))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    end_full[yr] = full
    print(f"ending {yr}: {len(rows)} rows, JO {jo}, full {full}")
    assert jo == end_jo[yr]

# --------------------------- regeneration verification ------
inv2, _s2, _d2 = B14.inv_above_geo(1.50, 0.50)
fg2 = B14.fade_geo(1.25, 0.65)
regen = apply_swaps(R14.load_books(), inv2, fg2, "real")
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r14_book{yr}_trades.csv")))
    got = Counter((r["comp"], r["date"], r["stock"], r["dir"],
                   r["entry_time"], round(float(r["net"]), 2))
                  for r in rows)
    want = Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2))
                   for t in regen[yr])
    assert got == want, (yr, "multiset mismatch")
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    assert jo == end_jo[yr]
print("regeneration verification PASSED: fresh rebuild from "
      "the Round-13 CSVs (INV-ABOVE rebuilt at T150/S050 by "
      "run_chain + law + hard-dip exclusion; GAP-FADE family "
      "rebuilt at T125/S065 by gap_rows) matches the exported "
      "ending CSVs row-for-row and to the paisa in both years.")

# freeze addendum: the ending book after Round 14
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R14-08, same day) — the ending book "
        "after Round 14\n"
        "Round 14 banked two further exit-geometry changes, "
        "both whole-sleeve swaps gated on the Round-13 ending "
        "book: (1) R14-04 — the INV-ABOVE sleeve's exit "
        "geometry moves from T125/S050 to **T150/S050** "
        "(target step only; population re-formed by the "
        "chain at the new geometry under the incumbent law "
        "— ADR >= 3.0, rounds <= 2, entry < 10:30 — with "
        "the R12-02 hard-dip exclusion re-applied to the "
        f"new rows, dropping {inv_dropped[2025]} / "
        f"{inv_dropped[2026]} rows; sleeve Jan-Oct "
        "+10,463.16 / +7,361.39 at the old cell -> "
        "+12,513.28 / +10,114.82 at T150/S050). (2) R14-05 "
        "— the GAP-FADE family's exit geometry moves from "
        "T125/S050 to **T125/S065** (stop step only, both "
        "GAP-FADE and GAP-FADE-INC; populations, bands, "
        "cells and entries unchanged; family Jan-Oct "
        "+23,775.49 / +6,255.24 at the old cell -> "
        "+24,355.17 / +7,733.66 at T125/S065). Exit "
        "geometry carries no admission information, so the "
        "freeze's timing argument is unaffected. The book "
        "judged in December is the R13-08 ending book PLUS "
        "these two geometry changes. Ending book: 2025 "
        f"Jan-Oct {end_jo[2025]} on {len(ending[2025])} "
        f"rows; 2026 Jan-Oct {end_jo[2026]} on "
        f"{len(ending[2026])} rows. Regeneration "
        "verification PASSED (R14-08): rebuilt from the "
        "Round-13 CSVs by fresh code, the book matches the "
        "exported Round-14 CSVs row-for-row and to the "
        "paisa in both years. The December pass/kill lines "
        "above apply to the ending book as a whole.\n")

# ------------------------------------------------------ state ---
sc = {yr: FL.scorecard(ending[yr], yr) for yr in (2025, 2026)}
red_months = {m: v for m, v in sc[2025]["months"].items()
              if m <= "2025-10" and v < 0}
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round14_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 6,
    "decision_support": 0,
    "audits": 2,
    "banked": 2,
    "voided_rows": 0,
    "report": "stocks_engine_round14_2026-11-02.md",
    "evidence": "r14_results.json",
    "ending_book": "2025 JO 1,05,987.24; 2026 JO 2,57,300.30 "
                   "(R14-04 INV-ABOVE geometry swap to "
                   "T150/S050 + R14-05 GAP-FADE family geometry "
                   "swap to T125/S065 banked)",
    "workstreams": {
        "WS1_f4": "R14-02 F4 T175/S095 REJECTED on (a) + (c): "
            "sleeve JO 2025 +6,280.30 / 2026 -10,767.28 vs the "
            "banked cell — the target step is a year-trade on "
            "F4 too, now on an exact cross-year score (SAT-12 "
            "closed the family on an estimate; Lesson 31's "
            "re-test confirms the closure in substance). "
            "Flagged as an owner decision (two legs).",
        "WS2_inv": "R14-03 INV-LONG T150/S050 REJECTED on "
            "(a) + (c) (+4,275.39 / -10,547.95) — flagged. "
            "R14-04 INV-ABOVE T150/S050 BANKED, all ten legs: "
            "2025 JO +2,050.12, 2026 JO +2,753.43. The cell "
            "decomposes flagged R2-26 (T150/S080): at the "
            "incumbent stop the wider target does NOT flip "
            "March — R2-26's flip was its stop widening, not "
            "its target.",
        "WS3_fade_n4": "R14-05 GAP-FADE family T125/S065 "
            "BANKED, all ten legs (2025 JO +579.68, 2026 JO "
            "+1,478.42; the diagnostic's stop-axis pick, exact "
            "gain well under the +12,157.87 rough estimate — "
            "Lesson 31's magnitude warning, direction right). "
            "R14-06 N4-V3 T125/S050 (scorecard cell) REJECTED "
            "on (a) + (b) + (c) + (e): the SAT-15 rebuild is "
            "worth more on the current population than at "
            "birth (2025 JO -8,137.41 / 2026 JO -18,013.98 "
            "for reverting); the book cell and the scorecard "
            "cell are different systems on this population.",
        "WS4_p2f": "R14-07 P2F family T150/S050 REJECTED on "
            "(a) + (b) + (e): JO rises in both years (+627.22 "
            "/ +111.87) but full-year 2025 falls and ex-top-3 "
            "falls — the attribution the cell was bought for: "
            "Lesson 33's two-axis 2025 bleed was the STOP "
            "widening, not the target (at the incumbent stop "
            "the wider target is mildly JO-positive).",
        "WS5": "R14-08: union of the two bankings re-gated "
            "PASS. Stack totals reproduced exactly on the "
            "ending book; adoption values restated "
            "(unconditioned +17,243.87 / -9,753.05; A "
            "+21,146.78 / -12,839.07; C +13,826.20 / "
            "-10,121.51; IDXCELL +7,159.14 / +503.58) — "
            "IDXCELL remains the only stack form adding in "
            "both years, now marginally in 2026. December "
            "freeze extended (R14-08 addendum) with "
            "regeneration verification PASSED.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r14_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r14_book2026_trades.csv",
    "book_id": "R14-FINAL (R14-04 INV-ABOVE T150/S050 + "
               "R14-05 GAP-FADE family T125/S065 banked on "
               "the R13 book; exports verified by re-sum + "
               "regeneration)",
    "floor_status": {
        "2025": "NOT MET - Rs1,05,987.24 (Rs10,598.72/mo), "
                "gap Rs44,012.76",
        "2026": "MET - Rs2,57,300.30 (Rs25,730.03/mo)",
    },
    "jan_oct_2025": end_jo[2025],
    "jan_oct_2026": end_jo[2026],
    "red_months_2025_jan_oct": {k: round(v, 2)
                                for k, v in red_months.items()},
    "total_2025_full": end_full[2025],
    "total_2026_full": end_full[2026],
    "trades_2025": len(ending[2025]),
    "trades_2026": len(ending[2026]),
}
st["cycles_completed"] += [
    "R14-01 AUDIT (starting-book re-verification from the "
    "R13 CSVs: totals/rows exact; Jul -2,000.01 / Oct "
    "-3,751.28 asserted)",
    "R14-02 REJECTED (F4 geometry swap T175/S095; fails "
    "a + c — flagged as an owner decision)",
    "R14-03 REJECTED (INV-LONG geometry swap T150/S050; "
    "fails a + c — flagged as an owner decision)",
    "R14-04 BANKED (INV-ABOVE geometry swap T150/S050; all "
    "ten legs pass — 2025 JO +2,050.12, 2026 JO +2,753.43)",
    "R14-05 BANKED (GAP-FADE family geometry swap "
    "T125/S065; all ten legs pass — 2025 JO +579.68, 2026 "
    "JO +1,478.42)",
    "R14-06 REJECTED (N4-V3 geometry swap to the scorecard "
    "cell T125/S050; fails a + b + c + e)",
    "R14-07 REJECTED (P2F family geometry swap T150/S050; "
    "fails a + b + e)",
    "R14-08 AUDIT (WS5 combinations: union of R14-04 + "
    "R14-05 re-gated PASS; stack prices restated on the "
    "ending book; December freeze addendum "
    "regeneration-verified)",
]
st["flagged_awaiting_chandu"] = st["flagged_awaiting_chandu"] + [
    {
        "id": "R14-02",
        "candidate": "F4 geometry swap to T175/S095 (banked "
                     "F4 sleeve at the wider target)",
        "failed_legs": ["a_combined_rises", "c_2026_no_fall"],
        "note": "fails (a) + (c) only; no flips, placebos "
                "beaten. Adoption on the R14 ending book -> "
                "2025 JO +6,280.30, 2026 JO -10,767.28 (2026 "
                "stays above floor). The F4 target step at "
                "one price: it buys the weak year with the "
                "strong year's money — the same year-trade "
                "the REXP/NU target steps priced in Round 13. "
                "Alternative form of the banked F4 sleeve — "
                "never additive with it.",
        "delta_2025_jan_oct": 6280.30,
        "delta_2026_jan_oct": -10767.28,
    },
    {
        "id": "R14-03",
        "candidate": "INV-LONG geometry swap to T150/S050 "
                     "(banked INV-LONG sleeve at the wider "
                     "target)",
        "failed_legs": ["a_combined_rises", "c_2026_no_fall"],
        "note": "fails (a) + (c) only; no flips, side "
                "placebo beaten. Adoption on the R14 ending "
                "book -> 2025 JO +4,275.39, 2026 JO "
                "-10,547.95 (2026 stays above floor). The "
                "INV-LONG target step at one price, the same "
                "year-trade as R14-02. Alternative form of "
                "the banked INV-LONG sleeve — never additive "
                "with it.",
        "delta_2025_jan_oct": 4275.39,
        "delta_2026_jan_oct": -10547.95,
    },
]
st["consecutive_no_bank"] = 0
st["iteration"] = 49
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round14_summary, incumbent -> r14 CSVs, "
      "8 cycles, R14-02 + R14-03 flags added (27 flags)")

for yr in (2025, 2026):
    print(yr, "JO", sc[yr]["jan_oct_total"], "trades",
          sc[yr]["jan_oct_trades"], "ex_top3 full",
          sc[yr]["ex_top3_stocks"], "months", sc[yr]["months"])
print("finalise done.")
