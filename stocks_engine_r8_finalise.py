#!/usr/bin/env python3
"""ROUND 8 — FINALISE (R8-08): WS4 combinations close by statement
(zero Round-8 bankings — nothing exists to combine); ending books
exported and independently re-summed; every flagged variant's
adoption value restated on the ending book (R6-L5); state updated.

The ending book is the Round-7 book UNCHANGED (Round 8 banked
nothing): exports are written to the r8 CSVs and verified identical
in total and count to the r7 books.
"""
import sys, json, csv, re
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r8_lib as R8

books = R8.load_books()
JO = {yr: R8.jo(books, yr) for yr in (2025, 2026)}
assert JO == {2025: 78420.04, 2026: 229696.21}, JO

res = json.load(open(f"{WS}/r8_results.json"))
def rec(cycle):
    return [r for r in res if r["cycle"] == cycle][0]
r802 = rec("R8-02")
m = re.search(r"Placebos: P1 all-placebo ([\d]+\.\d{2}); P2 swaps "
              r"\+ sleeves late ([\d]+\.\d{2}); P3 R2-26 \+ sleeve "
              r"late \+ real sleeves ([\d]+\.\d{2})", r802["note"])
pl802 = [float(m.group(i)) for i in (1, 2, 3)] if m else None
print("R8-02 placebos:", pl802)

# ------------------------------------------------------------- R8-08 -
R8.record_audit(
    "R8-08",
    "WS4 combinations of Round-8 bankings — closes by statement; "
    "finalise",
    "Round 8 banked ZERO candidates (R8-03 rejected on seven "
    "legs; R8-04 twin not triggered under its frozen rule; R8-05 "
    "on (e)+(f); R8-06 and R8-07 on (c) alone; R8-02 is decision "
    "support by construction). With no bankings there is no "
    "combination to re-gate. Closes by statement, per the "
    "pre-registration. Ending books exported to the r8 CSVs and "
    "independently re-summed; flagged list restated on the "
    "unchanged book.")

# ------------------------------------------------------------- exports
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r8_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["comp", "date", "stock", "dir", "entry_time",
                    "net"])
        for t in sorted(books[yr],
                        key=lambda x: (x["date"], x["entry_time"],
                                       x["stock"], x["comp"])):
            w.writerow([t["comp"], t["date"], t["stock"], t["dir"],
                        t["entry_time"], f"{t['net']:.2f}"])
    chk = FL.load(f"stocks_engine_r8_book{yr}_trades.csv")
    cj = R8.jo({yr: chk}, yr)
    assert cj == JO[yr] and len(chk) == len(books[yr]), (yr, cj)
    print(f"export {yr}: {len(chk)} rows, JO re-summed {cj} OK "
          f"(identical to the Round-7 book)")

# ---------------------------------------------------------- scorecards
scs = {}
for yr in (2025, 2026):
    sc = FL.scorecard(books[yr], yr)
    cells, missing = FL.cells(books[yr])
    scs[yr] = (sc, cells)
    print(f"\n{yr}: full {sc['total']} | JO {sc['jan_oct_total']} "
          f"({round(sc['jan_oct_total']/10, 2)}/mo) | trades "
          f"{sc['trades']} | ex-top3 {sc['ex_top3_stocks']} | top3 "
          f"{sc['top3_stocks']}")
    print(f"  months {sc['months']}")
    print(f"  H1 {sc['jan_oct_H1_jan_may']} H2 "
          f"{sc['jan_oct_H2_jun_oct']} | cells {cells}")
    print(f"  comps {sc['by_comp']}")

# --------------------------------------------------------------- state
def adopt(d25, d26):
    return (round(JO[2025] + d25, 2), round(JO[2026] + d26, 2))

a = {}
a["R2-26"] = adopt(7534.00, 4122.33)
a["R5-03-clean"] = adopt(8289.44, -1984.82)
a["R5-03-asgated"] = adopt(10594.66, 2778.21)
a["R5-07"] = adopt(12314.54, 24306.56)
a["R5-07-CERT"] = adopt(14117.24, 24112.86)
a["R8-05"] = adopt(11353.09, 31651.93)
a["R6-02"] = adopt(6400.94, 40742.69)
a["R6-04"] = adopt(544.11, 32422.92)
a["R6-10"] = adopt(16015.00, -10286.95)
a["R7-02"] = adopt(12153.17, -10930.18)
a["R8-07"] = adopt(10243.45, -5899.72)
a["R7-03"] = adopt(14870.39, -8399.33)
a["R7-06"] = adopt(4046.55, 12167.10)
a["R8-06"] = adopt(3598.21, -2477.24)
maxstack = (r802["var"]["2025"]["jan_oct"],
            r802["var"]["2026"]["jan_oct"])
triple_birth = (106558.02, 256140.28)
triple_cert = (round(a["R5-07-CERT"][0] + 7534.00 + 8289.44
                     - JO[2025], 2) if False else
               round(JO[2025] + 7534.00 + 8289.44 + 14117.24, 2),
               round(JO[2026] + 4122.33 - 1984.82 + 24112.86, 2))

st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["cycles_completed"] = st.get("cycles_completed", []) + [
    "R8-01 AUDIT (WS0 ingredient anchors: all four reproduce their "
    "flagged prices on the R7 book exactly)",
    "R8-02 DECISION-SUPPORT (MAX STACK gated whole: 2025 JO "
    "1,23,231.11 / 2026 JO 2,47,547.25; fails leg (f) ONLY — Jan "
    "and Dec 2025 flips; force_no_bank)",
    "R8-03 REJECTED (DRIVE-CONTINUATION LONG; fails a, b, c, d, e, "
    "f, h — standalone -1,710.67 / -28,882.57)",
    "R8-04 AUDIT (DRIVE SHORT twin not scored — frozen rule not "
    "triggered)",
    "R8-05 REJECTED (NE-REV-IDX, NIFTY-down conditioning; fails "
    "e + f, Dec flip only)",
    "R8-06 REJECTED (banked fade x NIFTY-down restriction; fails "
    "c only)",
    "R8-07 REJECTED (REXP-SHORT DOWN-only T100/S065; fails c "
    "only — flagged as the preferred REXP-DOWN form)",
    "R8-08 AUDIT (WS4 combinations: none — zero bankings; "
    "finalise)"]
st["current_incumbent"] = {
    "book_2025_csv": "stocks_engine_r8_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r8_book2026_trades.csv",
    "book_id": "R8-FINAL = R7-FINAL unchanged (Round 8 banked "
               "nothing; exports verified identical to the r7 "
               "books by re-sum)",
    "floor_status": {
        "2025": "NOT MET - Rs78,420.04 (Rs7,842.00/mo), gap "
                "Rs71,579.96",
        "2026": "MET - Rs2,29,696.21 (Rs22,969.62/mo)"},
    "jan_oct_2025": JO[2025], "jan_oct_2026": JO[2026],
    "red_months_2025_jan_oct": {
        m: scs[2025][0]["months"][m]
        for m in ("2025-06", "2025-07", "2025-10")},
    "total_2025_full": scs[2025][0]["total"],
    "total_2026_full": scs[2026][0]["total"],
    "trades_2025": len(books[2025]), "trades_2026": len(books[2026])}

st["flagged_awaiting_chandu"] = [
    {"id": "R2-26", "candidate": "INV-ABOVE exits T150/S080 swap",
     "failed_legs": [],
     "note": f"clean sheet (R4-10); deltas unchanged by Rounds "
             f"6-8. Adoption on the R8 book -> 2025 JO "
             f"Rs{a['R2-26'][0]}, 2026 JO Rs{a['R2-26'][1]}",
     "delta_2025_jan_oct": 7534.00, "delta_2026_jan_oct": 4122.33},
    {"id": "R5-03", "candidate": "GAP-FADE thr 1.25% swap (DOWN+FLAT,"
                                " 09:20)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only. Clean adoption (retiring the banked "
             f"GAP-FADE-INC) on the R8 book -> 2025 JO "
             f"Rs{a['R5-03-clean'][0]}, 2026 JO "
             f"Rs{a['R5-03-clean'][1]}",
     "delta_2025_jan_oct": 10594.66, "delta_2026_jan_oct": 2778.21},
    {"id": "R5-07", "candidate": "NE-REV LONG (non-event reversal, "
                                "thr 2.0%, entry 10:35, T100/S065) "
                                "— R5 population form",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"as flagged at birth. Adoption on the R8 book -> "
             f"2025 JO Rs{a['R5-07'][0]}, 2026 JO "
             f"Rs{a['R5-07'][1]}. See R5-07-CERT for the same flag "
             f"repriced on the certified population",
     "delta_2025_jan_oct": 12314.54, "delta_2026_jan_oct": 24306.56},
    {"id": "R5-07-CERT", "candidate": "NE-REV LONG on the CERTIFIED "
                                     "population (R6-11 standard; "
                                     "R7-08 decision support)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"the R5-07 flag rebuilt on the certified non-event "
             f"set (843 stock-days excluded; 30 R5-population rows "
             f"removed, weak-year standalone +14,105.64). Adoption "
             f"on the R8 book -> 2025 JO Rs{a['R5-07-CERT'][0]}, "
             f"2026 JO Rs{a['R5-07-CERT'][1]}",
     "delta_2025_jan_oct": 14117.24,
     "delta_2026_jan_oct": 24112.86},
    {"id": "R8-05", "candidate": "NE-REV-IDX (certified NE-REV "
                                "admitted only when NIFTY 10:25-bar "
                                "close <= -0.30% vs prior close)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"NEW Round-8 flag. Index conditioning kept 453 of "
             f"661 certified rows and cured the Jan-2025 flip; "
             f"still fails (e) and the Dec-2025 flip alone. "
             f"Adoption on the R8 book -> 2025 JO Rs{a['R8-05'][0]}, "
             f"2026 JO Rs{a['R8-05'][1]}. NE-REV-family alternative "
             f"— not additive with R5-07 / R5-07-CERT / R6-02 / "
             f"R6-04 / R7-06",
     "delta_2025_jan_oct": 11353.09,
     "delta_2026_jan_oct": 31651.93},
    {"id": "R6-02", "candidate": "NE-REV LONG thr 2.25% (entry "
                                "10:35)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only; no month flips. Adoption on the R8 "
             f"book -> 2025 JO Rs{a['R6-02'][0]}, 2026 JO "
             f"Rs{a['R6-02'][1]}. NE-REV-family alternative — not "
             f"additive with the other NE-REV flags",
     "delta_2025_jan_oct": 6400.94, "delta_2026_jan_oct": 40742.69},
    {"id": "R6-04", "candidate": "NE-REV LONG thr 2.0%, DOWN+FLAT "
                                "cells (entry 10:35)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only. Adoption on the R8 book -> 2025 JO "
             f"Rs{a['R6-04'][0]}, 2026 JO Rs{a['R6-04'][1]}. "
             f"NE-REV-family alternative — not additive with the "
             f"other NE-REV flags",
     "delta_2025_jan_oct": 544.11, "delta_2026_jan_oct": 32422.92},
    {"id": "R6-10", "candidate": "REXP SHORT (range-expansion "
                                "follow, entry 10:20, T125/S050) — "
                                "full population",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only. Adoption on the R8 book -> 2025 JO "
             f"Rs{a['R6-10'][0]}, 2026 JO Rs{a['R6-10'][1]} (2026 "
             f"stays above floor). R7-02 / R7-03 / R8-07 are its "
             f"nested restricted/geometry forms — alternatives to "
             f"this flag, never additive with it",
     "delta_2025_jan_oct": 16015.00, "delta_2026_jan_oct": -10286.95},
    {"id": "R7-02", "candidate": "REXP SHORT restricted to DOWN+FLAT"
                                " regime cells",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only. Adoption on the R8 book -> 2025 JO "
             f"Rs{a['R7-02'][0]}, 2026 JO Rs{a['R7-02'][1]}. "
             f"Dominated by R7-03 / R8-07 on both years",
     "delta_2025_jan_oct": 12153.17,
     "delta_2026_jan_oct": -10930.18},
    {"id": "R8-07", "candidate": "REXP-SHORT DOWN-only at T100/S065 "
                                "(geometry neighbour of R7-03)",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"NEW Round-8 flag — the PREFERRED REXP-DOWN form "
             f"per the Round-8 tasking (both prices stated): at "
             f"T100/S065 adoption on the R8 book -> 2025 JO "
             f"Rs{a['R8-07'][0]}, 2026 JO Rs{a['R8-07'][1]} (2026 "
             f"cost -5,899.72, the family's smallest); at the "
             f"frozen T125/S050 (R7-03) -> 2025 JO "
             f"Rs{a['R7-03'][0]}, 2026 JO Rs{a['R7-03'][1]} (2026 "
             f"cost -8,399.33, the family's largest 2025 gain). "
             f"The tighter target cuts the 2026 bleed by 2,499.61 "
             f"and the 2025 gain by 4,626.94 — the (c) question at "
             f"two prices. Fails (c) only; every other leg passes",
     "delta_2025_jan_oct": 10243.45, "delta_2026_jan_oct": -5899.72},
    {"id": "R7-03", "candidate": "REXP SHORT restricted to DOWN "
                                "regime cells only (T125/S050)",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only; the largest single-sleeve 2025 "
             f"delta on the flagged list (+14,870.39). Adoption on "
             f"the R8 book -> 2025 JO Rs{a['R7-03'][0]}, 2026 JO "
             f"Rs{a['R7-03'][1]}. Alternate geometry form of the "
             f"REXP-DOWN flag — see R8-07 (preferred form, "
             f"T100/S065). Subset of R6-10",
     "delta_2025_jan_oct": 14870.39, "delta_2026_jan_oct": -8399.33},
    {"id": "R7-06", "candidate": "QUIET-NAME NE-REV (certified "
                                "population, trailing-range filter)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"fails (e) + (f) (Jan 2025 flips). Adoption on the "
             f"R8 book -> 2025 JO Rs{a['R7-06'][0]}, 2026 JO "
             f"Rs{a['R7-06'][1]}. Subset of the R5-07-CERT "
             f"population — not additive with the NE-REV family",
     "delta_2025_jan_oct": 4046.55, "delta_2026_jan_oct": 12167.10},
    {"id": "R8-06", "candidate": "FADE-IDX restriction (banked "
                                "GAP-FADE + GAP-FADE-INC legs kept "
                                "only on NIFTY-down mornings)",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"NEW Round-8 flag — a RESTRICTION of banked legs, "
             f"not an addition: 350 of 404 fade legs sit on "
             f"NIFTY-down mornings (the banked sleeve was already "
             f"implicitly index-conditioned); applying the "
             f"restriction removes 54 legs (2025 +3,598.21 — the "
             f"removed legs were net losers there; 2026 -2,477.24 "
             f"— net winners there) and fails (c) only. Adoption "
             f"on the R8 book -> 2025 JO Rs{a['R8-06'][0]}, 2026 "
             f"JO Rs{a['R8-06'][1]}",
     "delta_2025_jan_oct": 3598.21, "delta_2026_jan_oct": -2477.24},
    {"id": "R6-01-TRIPLE", "candidate": "R2-26 + R5-03 + R5-07 "
                                       "combined (decision support)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"arithmetic restatement: with R5-07 in its birth "
             f"form -> 2025 JO Rs{triple_birth[0]}, 2026 JO "
             f"Rs{triple_birth[1]}; with R5-07-CERT and R5-03-clean "
             f"-> 2025 JO Rs{triple_cert[0]}, 2026 JO "
             f"Rs{triple_cert[1]}. Superseded as the priced stack "
             f"by R8-MAXSTACK-GATED (gated whole at R8-02)",
     "delta_2025_jan_oct": None, "delta_2026_jan_oct": None},
    {"id": "R8-MAXSTACK-GATED", "candidate": "MAX STACK — R2-26 + "
                                             "R5-03 (clean) + "
                                             "R5-07-CERT + R7-03, "
                                             "GATED whole (R8-02)",
     "failed_legs": ["f_no_green_month_flips"],
     "note": f"the owner's largest decision, now with a real gate "
             f"sheet (R8-02, force_no_bank): adoption -> 2025 JO "
             f"Rs{maxstack[0]} (Rs{round(maxstack[0]/10, 2)}/mo; "
             f"gap Rs{round(150000 - maxstack[0], 2)}), 2026 JO "
             f"Rs{maxstack[1]}. Exactly additive at row level; "
             f"fails leg (f) ONLY — Jan 2025 +2,200.31 -> -715.46 "
             f"and Dec 2025 +1,207.95 -> -99.76 flip green-to-red; "
             f"every other leg passes, incl. (e) (2025 ex-top-3 "
             f"rises to +44,205.13) and (x). Placebos beaten: P1 "
             f"{pl802[0]}, P2 {pl802[1]}, P3 {pl802[2]} vs variant "
             f"combined 3,70,821.53. Supersedes the R7 arithmetic "
             f"restatement (Rs1,21,428.41), which understated the "
             f"stack by using R5-07's birth form and R5-03's "
             f"as-gated delta",
     "delta_2025_jan_oct": round(maxstack[0] - JO[2025], 2),
     "delta_2026_jan_oct": round(maxstack[1] - JO[2026], 2)},
    {"id": "R3-10", "candidate": "GAP-FADE LONG-only sub-sleeve "
                                "(>=1.5%, all cells)",
     "failed_legs": ["c_2026_no_fall", "e_extop3",
                     "f_no_green_month_flips"],
     "note": "superseded in practice by the banked refinements "
             "R4-03 + R6-08; carried for the record",
     "delta_2025_jan_oct": 26979.39, "delta_2026_jan_oct": -4080.76}]
st["round8_summary"] = {
    "date": "2026-11-02", "gated_candidates": 4, "audits": 3,
    "decision_support": 1, "banked": 0, "voided_rows": 0,
    "report": "stocks_engine_round8_2026-11-02.md",
    "evidence": "r8_results.json",
    "ending_book": "2025 JO 78,420.04; 2026 JO 2,29,696.21 "
                   "(unchanged from Round 7 — zero bankings)",
    "workstreams": {
        "WS0_max_stack": f"R8-01 anchors exact. R8-02 gated "
                         f"whole (force_no_bank): 2025 JO "
                         f"Rs{maxstack[0]} (Rs"
                         f"{round(maxstack[0]/10, 2)}/mo; gap Rs"
                         f"{round(150000 - maxstack[0], 2)}), 2026 "
                         f"JO Rs{maxstack[1]}; exactly additive; "
                         f"fails leg (f) ONLY (Jan + Dec 2025 "
                         f"flips); (e) and (x) pass; placebos "
                         f"beaten",
        "WS1_drive": "R8-03 DRIVE-CONTINUATION LONG rejected on "
                     "seven legs (standalone -1,710.67 / "
                     "-28,882.57; 800 trades): morning up-drives "
                     "do not continue on the home 25. R8-04 SHORT "
                     "twin not scored — frozen rule not triggered",
        "WS2_index_state": "R8-05 NE-REV-IDX rejected on (e)+(f) "
                           "(Dec flip only — conditioning cured "
                           "the Jan flip; 453/661 rows kept; JO "
                           "deltas +11,353.09 / +31,651.93) — "
                           "flagged. R8-06 fade x NIFTY-down "
                           "restriction rejected on (c) only "
                           "(350/404 legs already down-state) — "
                           "flagged",
        "WS3_rexp_geometry": "R8-07 REXP-DOWN T100/S065 rejected "
                             "on (c) only: 2025 +10,243.45, 2026 "
                             "-5,899.72 (vs T125/S050 +14,870.39 / "
                             "-8,399.33) — flagged as the preferred "
                             "REXP-DOWN form with both prices",
        "WS4_combinations": "none — zero bankings (R8-08)"}}
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"), indent=1)
print("\nstate updated: round8_summary, current_incumbent, flagged "
      "list (16 entries), cycles_completed")
print("adoption map:", a)
print("max stack (gated):", maxstack, "| triple CERT arithmetic:",
      triple_cert)
