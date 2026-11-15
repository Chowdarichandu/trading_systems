#!/usr/bin/env python3
"""ROUND 7 — FINALISE (R7-07, R7-08): WS5 closes by statement (zero
Round-7 bankings — nothing exists to combine); R7-08 reprices the
R5-07 flag on the CERTIFIED population as decision support (the
R6-11 standard applied to the flag itself, force_no_bank); ending
books exported and independently re-summed; every flagged variant's
adoption value restated on the ending book (R6-L5); state updated.

The ending book is the Round-6 book UNCHANGED (Round 7 banked
nothing): exports are written to the r7 CSVs and verified identical
in total and count to the r6 books.
"""
import sys, json, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r7_lib as R7
import stocks_engine_r7_builders as B

books = R7.load_books()
JO = {yr: R7.jo(books, yr) for yr in (2025, 2026)}
assert JO == {2025: 78420.04, 2026: 229696.21}, JO

# ------------------------------------------------------------- R7-07 -
R7.record_audit(
    "R7-07",
    "WS5 combinations of Round-7 bankings — closes by statement",
    "Round 7 banked ZERO candidates (R7-02 and R7-03 rejected on "
    "leg (c) alone; R7-04 on seven legs; R7-05 on eight legs; "
    "R7-06 on legs (e) and (f)). With no bankings there is no "
    "combination to re-gate. Closes by statement, per the "
    "pre-registration.")

# ------------------------------------------------------------- R7-08 -
cert, r5set, added = B.certified_exclusions()
real, flipped, late, viol, stats = B.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.0, excl=cert)
assert viol == 0, viol
COMP = "NE-REV-CERT"
real_r = {yr: [dict(t, comp=COMP) for t in real[yr]] for yr in real}
flip_r = {yr: [dict(t, comp="NE-REV-CERT-S") for t in flipped[yr]]
          for yr in flipped}
late_r = {yr: [dict(t, comp=COMP) for t in late[yr]] for yr in late}
var = R7.add_comp(books, COMP, real_r)
pl = [R7.full_total(R7.add_comp(books, "NE-REV-CERT-S", flip_r)),
      R7.full_total(R7.add_comp(books, COMP, late_r))]
out = R7.gate(books, var, pl, timing_violations=viol)
cert_jo = {yr: R7.jo(var, yr) for yr in (2025, 2026)}
cert_delta = {yr: round(cert_jo[yr] - JO[yr], 2) for yr in (2025, 2026)}
cert_failed = [k for k, v in out["legs"].items()
               if isinstance(v, bool) and not v]
R7.record(
    "R7-08",
    "DECISION SUPPORT: R5-07 repriced on the CERTIFIED population "
    "(morning NE-REV, R6-11-strengthened non-event set) — NOT a "
    "banking", out,
    note=f"the R5-07 flag rebuilt on the certified population "
         f"(843 stock-days excluded vs the R5 set's 539; 30 of "
         f"R5-07's 691 population rows removed, and the certified "
         f"standalone is HIGHER in 2025: +14,105.64 vs +12,209.45 — "
         f"the removed rows were net losers in the weak year). "
         f"Adoption on the ending book -> 2025 JO {cert_jo[2025]}, "
         f"2026 JO {cert_jo[2026]} (JO deltas {cert_delta[2025]} / "
         f"{cert_delta[2026]}); failing legs: {cert_failed}. "
         f"Timing violations {viol}. Recorded with force_no_bank — "
         f"adoption is Chandu's, exactly as for the R5-population "
         f"flag.",
    extra={"jo_deltas": {str(k): v for k, v in cert_delta.items()},
           "adoption_jo": {str(k): v for k, v in cert_jo.items()},
           "failed_legs": cert_failed},
    force_no_bank=True)

# ------------------------------------------------------------- exports
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r7_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["comp", "date", "stock", "dir", "entry_time",
                    "net"])
        for t in sorted(books[yr],
                        key=lambda x: (x["date"], x["entry_time"],
                                       x["stock"], x["comp"])):
            w.writerow([t["comp"], t["date"], t["stock"], t["dir"],
                        t["entry_time"], f"{t['net']:.2f}"])
    chk = FL.load(f"stocks_engine_r7_book{yr}_trades.csv")
    cj = R7.jo({yr: chk}, yr)
    assert cj == JO[yr] and len(chk) == len(books[yr]), (yr, cj)
    print(f"export {yr}: {len(chk)} rows, JO re-summed {cj} OK "
          f"(identical to the Round-6 book)")

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

st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["cycles_completed"] = st.get("cycles_completed", []) + [
    "R7-01 AUDIT (REXP-SHORT 2026 damage decomposition: DOWN cell "
    "-8,399.33 is the damage; UP cell +643.23)",
    "R7-02 REJECTED (REXP-SHORT DOWN+FLAT; fails c only)",
    "R7-03 REJECTED (REXP-SHORT DOWN-only; fails c only)",
    "R7-04 REJECTED (NE-REV afternoon 13:25/13:35; fails a, b, d, "
    "e, f, g, h)",
    "R7-05 REJECTED (two-day dislocation reversal; fails a, b, c, "
    "d, e, f, g, h)",
    "R7-06 REJECTED (quiet-name NE-REV; fails e + f)",
    "R7-07 AUDIT (WS5 combinations: none — zero bankings)",
    "R7-08 DECISION-SUPPORT (R5-07 repriced on the certified "
    "population; fails e + f)"]
st["current_incumbent"] = {
    "book_2025_csv": "stocks_engine_r7_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r7_book2026_trades.csv",
    "book_id": "R7-FINAL = R6-FINAL unchanged (Round 7 banked "
               "nothing; exports verified identical to the r6 "
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

a = {}
a["R2-26"] = adopt(7534.00, 4122.33)
a["R5-03-clean"] = adopt(8289.44, -1984.82)
a["R5-07"] = adopt(12314.54, 24306.56)
a["R5-07-CERT"] = (cert_jo[2025], cert_jo[2026])
a["R6-02"] = adopt(6400.94, 40742.69)
a["R6-04"] = adopt(544.11, 32422.92)
a["R6-10"] = adopt(16015.00, -10286.95)
a["R7-02"] = adopt(12153.17, -10930.18)
a["R7-03"] = adopt(14870.39, -8399.33)
a["R7-06"] = adopt(4046.55, 12167.10)
triple = (106558.02, 256140.28)
maxstack = (round(triple[0] + 14870.39, 2),
            round(triple[1] - 8399.33, 2))

st["flagged_awaiting_chandu"] = [
    {"id": "R2-26", "candidate": "INV-ABOVE exits T150/S080 swap",
     "failed_legs": [],
     "note": f"clean sheet (R4-10); deltas unchanged by Rounds "
             f"6-7. Adoption on the R7 book -> 2025 JO "
             f"Rs{a['R2-26'][0]}, 2026 JO Rs{a['R2-26'][1]}",
     "delta_2025_jan_oct": 7534.00, "delta_2026_jan_oct": 4122.33},
    {"id": "R5-03", "candidate": "GAP-FADE thr 1.25% swap (DOWN+FLAT,"
                                " 09:20)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only. Clean adoption (retiring the banked "
             f"GAP-FADE-INC) on the R7 book -> 2025 JO "
             f"Rs{a['R5-03-clean'][0]}, 2026 JO "
             f"Rs{a['R5-03-clean'][1]}",
     "delta_2025_jan_oct": 10594.66, "delta_2026_jan_oct": 2778.21},
    {"id": "R5-07", "candidate": "NE-REV LONG (non-event reversal, "
                                "thr 2.0%, entry 10:35, T100/S065) "
                                "— R5 population form",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"as flagged at birth. Adoption on the R7 book -> "
             f"2025 JO Rs{a['R5-07'][0]}, 2026 JO "
             f"Rs{a['R5-07'][1]}. See R5-07-CERT for the same flag "
             f"repriced on the certified population",
     "delta_2025_jan_oct": 12314.54, "delta_2026_jan_oct": 24306.56},
    {"id": "R5-07-CERT", "candidate": "NE-REV LONG on the CERTIFIED "
                                     "population (R6-11 standard; "
                                     "R7-08 decision support)",
     "failed_legs": cert_failed,
     "note": f"the R5-07 flag rebuilt on the certified non-event "
             f"set (843 stock-days excluded; 30 R5-population rows "
             f"removed, weak-year standalone rises to +14,105.64). "
             f"Gated whole-book at R7-08 as decision support: fails "
             f"{cert_failed}. Adoption on the R7 book -> 2025 JO "
             f"Rs{cert_jo[2025]}, 2026 JO Rs{cert_jo[2026]}",
     "delta_2025_jan_oct": cert_delta[2025],
     "delta_2026_jan_oct": cert_delta[2026]},
    {"id": "R6-02", "candidate": "NE-REV LONG thr 2.25% (entry "
                                "10:35)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only; no month flips. Adoption on the R7 "
             f"book -> 2025 JO Rs{a['R6-02'][0]}, 2026 JO "
             f"Rs{a['R6-02'][1]}. NE-REV-family alternative — not "
             f"additive with R5-07 / R6-04 / R7-06",
     "delta_2025_jan_oct": 6400.94, "delta_2026_jan_oct": 40742.69},
    {"id": "R6-04", "candidate": "NE-REV LONG thr 2.0%, DOWN+FLAT "
                                "cells (entry 10:35)",
     "failed_legs": ["e_extop3"],
     "note": f"fails (e) only. Adoption on the R7 book -> 2025 JO "
             f"Rs{a['R6-04'][0]}, 2026 JO Rs{a['R6-04'][1]}. "
             f"NE-REV-family alternative — not additive with the "
             f"other NE-REV flags",
     "delta_2025_jan_oct": 544.11, "delta_2026_jan_oct": 32422.92},
    {"id": "R6-10", "candidate": "REXP SHORT (range-expansion "
                                "follow, entry 10:20, T125/S050) — "
                                "full population",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only. Adoption on the R7 book -> 2025 JO "
             f"Rs{a['R6-10'][0]}, 2026 JO Rs{a['R6-10'][1]} (2026 "
             f"stays above floor). R7-02 / R7-03 are its nested "
             f"cell-restricted subsets — alternatives to this flag, "
             f"never additive with it",
     "delta_2025_jan_oct": 16015.00, "delta_2026_jan_oct": -10286.95},
    {"id": "R7-02", "candidate": "REXP SHORT restricted to DOWN+FLAT"
                                " regime cells",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only (2026 JO delta -10,930.18 — the "
             f"restriction keeps the DOWN cell where the damage "
             f"lives and drops the UP cell's +643.23). Adoption on "
             f"the R7 book -> 2025 JO Rs{a['R7-02'][0]}, 2026 JO "
             f"Rs{a['R7-02'][1]}. Dominated by R7-03 on both years",
     "delta_2025_jan_oct": 12153.17,
     "delta_2026_jan_oct": -10930.18},
    {"id": "R7-03", "candidate": "REXP SHORT restricted to DOWN "
                                "regime cells only",
     "failed_legs": ["c_2026_no_fall"],
     "note": f"fails (c) only; the largest single-sleeve 2025 "
             f"delta on the flagged list (+14,870.39) at the "
             f"smallest 2026 cost of the REXP family (-8,399.33; "
             f"2026 stays above floor). Adoption on the R7 book -> "
             f"2025 JO Rs{a['R7-03'][0]}, 2026 JO Rs{a['R7-03'][1]}. "
             f"Dominates R7-02 and is a subset of R6-10",
     "delta_2025_jan_oct": 14870.39, "delta_2026_jan_oct": -8399.33},
    {"id": "R7-06", "candidate": "QUIET-NAME NE-REV (certified "
                                "population, trailing-range filter)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"fails (e) + (f) (Jan 2025 flips). Breadth by "
             f"construction did not cure (e): the sleeve's gains "
             f"land in the book's carrier names. Adoption on the "
             f"R7 book -> 2025 JO Rs{a['R7-06'][0]}, 2026 JO "
             f"Rs{a['R7-06'][1]}. Its rows are a subset of the "
             f"R5-07-CERT population — not additive with the "
             f"NE-REV family flags",
     "delta_2025_jan_oct": 4046.55, "delta_2026_jan_oct": 12167.10},
    {"id": "R6-01-TRIPLE", "candidate": "R2-26 + R5-03 + R5-07 "
                                       "combined (decision support)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": f"arithmetic restatement on the R7 book (unchanged "
             f"from R6): 2025 JO Rs{triple[0]} (Rs10,655.80/mo, gap "
             f"Rs43,441.98), 2026 JO Rs{triple[1]} — the R6-01 gate "
             f"sheet was run on the Round-5 book and is not re-run",
     "delta_2025_jan_oct": None, "delta_2026_jan_oct": None},
    {"id": "R7-MAXSTACK", "candidate": "Triple + R7-03 (REXP-SHORT "
                                      "DOWN-only) — arithmetic "
                                      "restatement",
     "failed_legs": ["c_2026_no_fall", "e_extop3",
                     "f_no_green_month_flips"],
     "note": f"the triple's restated totals plus R7-03's gated "
             f"delta (disjoint component, gated against this same "
             f"book at R7-03): 2025 JO Rs{maxstack[0]} "
             f"(Rs{round(maxstack[0]/10, 2)}/mo; gap "
             f"Rs{round(150000 - maxstack[0], 2)}), 2026 JO "
             f"Rs{maxstack[1]}. NOT a gated combination — the "
             f"components carry their own failing legs ((e)+(f) "
             f"from the triple's birth book, (c) from R7-03); "
             f"quoted so the owner's largest available stack is "
             f"priced, per R6-L5",
     "delta_2025_jan_oct": None, "delta_2026_jan_oct": None},
    {"id": "R3-10", "candidate": "GAP-FADE LONG-only sub-sleeve "
                                "(>=1.5%, all cells)",
     "failed_legs": ["c_2026_no_fall", "e_extop3",
                     "f_no_green_month_flips"],
     "note": "superseded in practice by the banked refinements "
             "R4-03 + R6-08; carried for the record",
     "delta_2025_jan_oct": 26979.39, "delta_2026_jan_oct": -4080.76}]
st["round7_summary"] = {
    "date": "2026-11-02", "gated_candidates": 5, "audits": 2,
    "decision_support": 1, "banked": 0, "voided_rows": 0,
    "report": "stocks_engine_round7_2026-11-02.md",
    "evidence": "r7_results.json",
    "ending_book": "2025 JO 78,420.04; 2026 JO 2,29,696.21 "
                   "(unchanged from Round 6 — zero bankings)",
    "workstreams": {
        "WS1_rexp_repair": "R7-01 decomposition: the 2026 damage "
                           "is DOWN-cell located (-8,399.33); UP "
                           "cell +643.23. R7-02 DOWN+FLAT and "
                           "R7-03 DOWN-only both fail leg (c) "
                           "alone — the restriction keeps the "
                           "damaged cell; both flagged, R7-03 "
                           "dominates",
        "WS2_nerev_afternoon": "R7-04 rejected on 7 legs "
                               "(2025 standalone -37,819.07): the "
                               "reversal is a morning phenomenon",
        "WS3_disloc_2d": "R7-05 rejected on 8 legs (standalone "
                         "-62,345.49 / -43,694.93): two-day falls "
                         "continue, they do not revert intraday",
        "WS4_quiet_nerev": "R7-06 rejected on (e) + (f): breadth "
                           "by construction does not cure leg (e)",
        "WS5_combinations": "none — zero bankings (R7-07)",
        "R7-08_decision_support": f"R5-07 repriced on the "
                                  f"certified population: adoption "
                                  f"-> 2025 JO {cert_jo[2025]} / "
                                  f"2026 JO {cert_jo[2026]}, fails "
                                  f"{cert_failed}"}}
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"), indent=1)
print("\nstate updated: round7_summary, current_incumbent, flagged "
      "list (13 entries), cycles_completed")
print("adoption map:", a)
print("triple:", triple, "| maxstack:", maxstack)
