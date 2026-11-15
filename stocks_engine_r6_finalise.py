#!/usr/bin/env python3
"""ROUND 6 — FINALISE: record the causality audit (R6-11), apply its
void to the incumbent, export the ending books, re-sum independently,
and update stocks_engine_state.json.

THE VOID (R6-11, admission causality, Nifty-R5-WS0 standard):
4 N4-V3 rows whose event-day tag was not knowable at their 09:35
entry — one proven (BDL 2025-01-16: the calendar's own detail records
the exchange filing at 13:49 on the reaction day), three
uncertifiable (same-day results rows the calendar affirmatively marks
as declared during market hours, am="no", with no pre-09:35 evidence:
HINDZINC 2026-07-24, HINDUNILVR 2026-10-28, VEDL 2026-10-28).
Voided nets: +1,691.75 / -460.80 / -1,482.24 / +303.20 = +51.91
combined — the book was not carried by them. All other components
certified clean (see the audit section of the Round-6 report;
r6_causality_audit.json + this script's printed checks).
Every Round-6 candidate delta is on components disjoint from N4-V3,
so all R6 verdicts stand unchanged against the re-baselined book;
only the baseline moves (2025 -1,691.75; 2026 +1,639.84).
"""
import sys, json, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r6_lib as R6

books = R6.load_books()

VOID = [("2025-01-16", "BDL", "LONG", "09:35", 1691.75),
        ("2026-07-24", "HINDZINC", None, "09:35", -460.80),
        ("2026-10-28", "HINDUNILVR", "SHORT", "09:35", -1482.24),
        ("2026-10-28", "VEDL", "LONG", "09:35", 303.20)]

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

pre = {yr: jo(books, yr) for yr in (2025, 2026)}
removed = []
for yr in (2025, 2026):
    keep = []
    for t in books[yr]:
        hit = None
        for (d, s, dr, et, net) in VOID:
            if (t["comp"] == "N4-V3" and t["date"] == d
                    and t["stock"] == s and t["entry_time"] == et
                    and t["net"] == net
                    and (dr is None or t["dir"] == dr)):
                hit = (d, s)
                break
        if hit:
            removed.append(t)
        else:
            keep.append(t)
    books[yr] = keep
assert len(removed) == 4, removed
assert round(sum(t["net"] for t in removed), 2) == 51.91
post = {yr: jo(books, yr) for yr in (2025, 2026)}
print("void applied: 4 N4-V3 rows removed (combined net +51.91)")
print(f"  2025 JO {pre[2025]} -> {post[2025]} (expect 78420.04)")
print(f"  2026 JO {pre[2026]} -> {post[2026]} (expect 229696.21)")
assert post == {2025: 78420.04, 2026: 229696.21}, post
R6.save_books(books)

R6.record_audit(
    "R6-11",
    "ADMISSION-CAUSALITY AUDIT of the incumbent (Nifty-R5-WS0 model) "
    "— 4 N4-V3 rows VOIDED, book re-baselined; all other components "
    "certified clean",
    "1,860 rows checked mechanically (inputs recomputed from stored "
    "data) + code-level certification of the chain machinery. CLEAN: "
    "regime gates (below50/cond_inv1/g1 and FL.LABELS use prior "
    "closes only — every F4/INV row's date gate recomputed); F4 "
    "premove (bars < 10:00, band + direction recomputed for all 601 "
    "rows incl. Oct 29/30 from the fwd root; all entries >= 10:05); "
    "INV cutoffs (LONG <= 11:00, ABOVE <= 10:30); ADR prior-10-day "
    "only (code); chain heads build state in bar order, entries at "
    "idx+1, and pool_pick's price tie-break is unreachable across "
    "heads (RANK: v4 setups 1..3, skor 0); N4 move/cap/reaction-day "
    "checks (73 rows); P2F/P2F-R2/R2-LOWBAND (entry R+1/R+2 at the "
    "open, reaction return complete at R's close; bands + directions "
    "recomputed, 105 rows); GAP-FADE/GAP-FADE-INC (gap + prior-day "
    "label recomputed for all 404 rows; entries strictly after the "
    "signal print). VIOLATION — N4-V3's event-day tag on same-day "
    "intraday announcements (the morning move itself is causal; the "
    "day's membership in the reaction set was not knowable at 09:35): "
    "PROVEN 1 row — BDL 2025-01-16 (+1,691.75), the calendar's own "
    "detail records the exchange filing at 13:49 that day. "
    "UNCERTIFIABLE 3 rows — same-day results the calendar marks "
    "declared during market hours (am='no'), no pre-09:35 evidence: "
    "HINDZINC 2026-07-24 (-460.80), HINDUNILVR 2026-10-28 "
    "(-1,482.24), VEDL 2026-10-28 (+303.20). All 4 VOIDED and the "
    "book re-baselined the same run: 2025 JO 80,111.79 -> 78,420.04; "
    "2026 JO 2,28,056.37 -> 2,29,696.21; voided combined net "
    "+51.91. DISCLOSED, NOT VOIDED: BDL 2025-03-26 (-1,100.68) — "
    "same-day large_order with no timestamp and no intraday mark in "
    "the record (its 01-16 sibling was 13:49; inference is not "
    "evidence). 64 of 73 N4 rows have R > event_date (clean); the "
    "other same-day rows carry pre-open-public evidence on their "
    "records (prior-day-announced block deal, ex-date, opening block "
    "window, overnight USFDA approval). All Round-6 deltas are on "
    "components disjoint from N4-V3, so every R6 verdict stands; "
    "only the baseline moved. Detail: r6_causality_audit.json.",
    extra={"voided_rows": [{"date": t["date"], "stock": t["stock"],
                            "dir": t["dir"], "net": t["net"]}
                           for t in removed],
           "voided_combined_net": 51.91,
           "rows_checked": 1860,
           "baseline_after": {"2025_JO": post[2025],
                              "2026_JO": post[2026]}})

# ------------------------------------------------------------- exports
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r6_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["comp", "date", "stock", "dir", "entry_time", "net"])
        for t in sorted(books[yr],
                        key=lambda x: (x["date"], x["entry_time"],
                                       x["stock"], x["comp"])):
            w.writerow([t["comp"], t["date"], t["stock"], t["dir"],
                        t["entry_time"], f"{t['net']:.2f}"])
    chk = FL.load(f"stocks_engine_r6_book{yr}_trades.csv")
    cj = round(sum(t["net"] for t in chk
                   if t["date"] <= f"{yr}-10-31"), 2)
    assert cj == post[yr] and len(chk) == len(books[yr]), (yr, cj)
    print(f"export {yr}: {len(chk)} rows, JO re-summed {cj} OK")

# --------------------------------------------------------- scorecards
for yr in (2025, 2026):
    sc = FL.scorecard(books[yr], yr)
    cells, missing = FL.cells(books[yr])
    print(f"\n{yr}: full {sc['total']} | JO {sc['jan_oct_total']} "
          f"({round(sc['jan_oct_total']/10, 2)}/mo) | trades "
          f"{sc['trades']} | ex-top3 {sc['ex_top3_stocks']} | top3 "
          f"{sc['top3_stocks']}")
    print(f"  months {sc['months']}")
    print(f"  H1 {sc['jan_oct_H1_jan_may']} H2 "
          f"{sc['jan_oct_H2_jun_oct']} | cells {cells} missing "
          f"{len(missing)}")
    print(f"  comps {sc['by_comp']}")

# -------------------------------------------------------------- state
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["cycles_completed"] = st.get("cycles_completed", []) + [
    "R6-01 DECISION-SUPPORT (triple R2-26+R5-03+R5-07: exactly "
    "additive, fails e + f only; priced on the Round-5 book)",
    "R6-02 REJECTED (NE-REV thr 2.25; fails e only)",
    "R6-03 REJECTED (NE-REV thr 2.50; fails b, e, f)",
    "R6-04 REJECTED (NE-REV DOWN+FLAT; fails e only)",
    "R6-05 REJECTED (NE-REV entry 11:05; fails a, b, e, f)",
    "R6-06 AUDIT (NE-REV carrier exclusion skipped — no causal "
    "prior-year book ranking for 2025)",
    "R6-07 REJECTED (fade increment DOWN-only; fails e only)",
    "R6-08 BANKED (fade increment DOWN+FLAT at 09:40)",
    "R6-09 REJECTED (REXP LONG; fails a, b, c, d, e, f, h)",
    "R6-10 REJECTED (REXP SHORT; fails c only)",
    "R6-11 AUDIT (admission causality: 4 N4-V3 rows VOIDED, book "
    "re-baselined; all other components certified clean)"]
st["current_incumbent"] = {
    "book_2025_csv": "stocks_engine_r6_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r6_book2026_trades.csv",
    "book_id": "R6-FINAL = R5-FINAL + R6-08 GAP-FADE-INC (increment "
               "[1.25%,1.5%), DOWN+FLAT, entry 09:40, T125/S050) "
               "- R6-11 audit void (4 N4-V3 rows, combined +51.91)",
    "floor_status": {
        "2025": "NOT MET - Rs78,420.04 (Rs7,842.00/mo), gap "
                "Rs71,579.96",
        "2026": "MET - Rs2,29,696.21 (Rs22,969.62/mo)"},
    "jan_oct_2025": post[2025], "jan_oct_2026": post[2026],
    "red_months_2025_jan_oct": {"2025-06": -955.92,
                                "2025-07": -5523.29,
                                "2025-10": -4624.53},
    "total_2025_full": round(sum(t["net"] for t in books[2025]), 2),
    "total_2026_full": round(sum(t["net"] for t in books[2026]), 2),
    "trades_2025": len(books[2025]), "trades_2026": len(books[2026])}
st["flagged_awaiting_chandu"] = [
    {"id": "R2-26", "candidate": "INV-ABOVE exits T150/S080 swap",
     "failed_legs": [],
     "note": "clean sheet (R4-10); deltas unchanged by R6 (+7,534.00 "
             "/ +4,122.33). Adoption on the R6 book -> 2025 JO "
             "Rs85,954.04, 2026 JO Rs2,33,818.54",
     "delta_2025_jan_oct": 7534.00, "delta_2026_jan_oct": 4122.33},
    {"id": "R5-03", "candidate": "GAP-FADE thr 1.25% swap (DOWN+FLAT, "
                                "09:20)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only. Its [1.25,1.5) increment is now "
             "partially banked in the 09:40 form (R6-08); a clean "
             "adoption (swap, retiring GAP-FADE-INC) nets +8,289.44 "
             "in 2025 and -1,984.82 in 2026 over the R6 book -> 2025 "
             "JO Rs86,709.48, 2026 JO Rs2,27,711.39",
     "delta_2025_jan_oct": 10594.66, "delta_2026_jan_oct": 2778.21},
    {"id": "R5-07", "candidate": "NE-REV LONG (non-event reversal, "
                                "thr 2.0%, entry 10:35, T100/S065)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": "deltas unchanged by R6. Adoption on the R6 book -> "
             "2025 JO Rs90,734.58, 2026 JO Rs2,54,002.77",
     "delta_2025_jan_oct": 12314.54, "delta_2026_jan_oct": 24306.56},
    {"id": "R6-01-TRIPLE", "candidate": "R2-26 + R5-03 + R5-07 "
                                       "combined (decision support)",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": "priced on the Round-5 book (exactly additive): 2025 JO "
             "Rs1,08,249.77 / 2026 JO Rs2,54,500.44, failing (e) and "
             "(f). Restated on the R6 ending book (void applied, "
             "R5-03 at its clean-adoption net over the banked "
             "GAP-FADE-INC): 2025 JO Rs1,06,558.02 (Rs10,655.80/mo, "
             "gap Rs43,441.98), 2026 JO Rs2,56,140.28 — totals "
             "restated arithmetically; the R6-01 gate sheet itself "
             "was run on the Round-5 book and is not re-run",
     "delta_2025_jan_oct": None, "delta_2026_jan_oct": None},
    {"id": "R6-02", "candidate": "NE-REV LONG thr 2.25% (entry 10:35)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; no month flips. Adoption on the R6 "
             "book -> 2025 JO Rs84,820.98, 2026 JO Rs2,70,438.90",
     "delta_2025_jan_oct": 6400.94, "delta_2026_jan_oct": 40742.69},
    {"id": "R6-04", "candidate": "NE-REV LONG thr 2.0%, DOWN+FLAT "
                                "cells (entry 10:35)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; the DOWN+FLAT restriction repairs "
             "R5-07's Dec-2025 flip. Adoption on the R6 book -> 2025 "
             "JO Rs78,964.15, 2026 JO Rs2,62,119.13",
     "delta_2025_jan_oct": 544.11, "delta_2026_jan_oct": 32422.92},
    {"id": "R6-10", "candidate": "REXP SHORT (range-expansion follow, "
                                "entry 10:20, T125/S050)",
     "failed_legs": ["c_2026_no_fall"],
     "note": "fails (c) only: +16,015.00 to 2025, -10,286.95 to 2026 "
             "(2026 stays above floor). Adoption on the R6 book -> "
             "2025 JO Rs94,435.04, 2026 JO Rs2,19,409.26",
     "delta_2025_jan_oct": 16015.00, "delta_2026_jan_oct": -10286.95},
    {"id": "R3-10", "candidate": "GAP-FADE LONG-only sub-sleeve "
                                "(>=1.5%, all cells)",
     "failed_legs": ["c_2026_no_fall", "e_extop3",
                     "f_no_green_month_flips"],
     "note": "superseded in practice by the banked refinements "
             "R4-03 + R6-08; carried for the record",
     "delta_2025_jan_oct": 26979.39, "delta_2026_jan_oct": -4080.76}]
st["round6_summary"] = {
    "date": "2026-11-02", "gated_candidates": 9, "audits": 2,
    "decision_support": 1, "banked": 1, "voided_rows": 4,
    "report": "stocks_engine_round6_2026-11-02.md",
    "evidence": "r6_results.json",
    "ending_book": "2025 JO 78,420.04; 2026 JO 2,29,696.21 (after "
                   "the R6-08 banking and the R6-11 audit void)",
    "workstreams": {
        "WS0_triple": "R6-01: exactly additive on the Round-5 book "
                      "(2025 JO 1,08,249.77; 2026 JO 2,54,500.44); "
                      "fails (e) and (f) only; NOT banked",
        "WS1_nerev_repairs": "R6-02 thr 2.25 fails (e) only; R6-03 "
                             "thr 2.50 fails b/e/f; R6-04 DOWN+FLAT "
                             "fails (e) only; R6-05 entry 11:05 fails "
                             "a/b/e/f; R6-06 carrier exclusion "
                             "skipped (no causal 2024 book)",
        "WS2_increment": "R6-07 DOWN-only fails (e) only; R6-08 "
                         "09:40 entry BANKED (+2,305.22 / +4,763.03, "
                         "all legs)",
        "WS3_range_expansion": "R6-09 LONG fails 7 legs; R6-10 "
                               "SHORT fails (c) only (+16,015.00 / "
                               "-10,286.95)",
        "WS0B_causality_audit": "R6-11: 4 N4-V3 rows voided "
                                "(combined +51.91), book "
                                "re-baselined; all other components "
                                "certified clean"}}
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"), indent=1)
print("\nstate updated: round6_summary, current_incumbent, flagged "
      "list (8 entries), cycles_completed")
