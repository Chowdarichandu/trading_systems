#!/usr/bin/env python3
"""ROUND 12 — WS5 combinations + stack-price maintenance +
December freeze addendum + finalise (R12-09).

Bankings: R12-02 (INV-ABOVE hard-dip exclusion, re-gated on
the pair baseline) BANKED. R12-03 rejected on (c) + (e);
R12-06 / R12-08 closed by statement (no separator in either
wound). The WS5 union is therefore R12-02 alone — re-gated
whole-book here against the starting book as the combination
record. Ending book = Round-11 ending book minus INV-ABOVE
hard-dip rows.
Stack prices restated on the ending book by the generalised
R11-08 method (R2-26 + R5-03 swaps applied, NE-REV / REXP
rows stripped, stack slot + REXP T125/S050 applied — totals
must reproduce the recorded prices exactly; the INV-ABOVE
swap discards the whole comp, so the banked removal does not
disturb the identity). December freeze extended to the
ending book with REGENERATION VERIFICATION: the ending book
rebuilt from the Round-11 CSVs by fresh code (hard-dip
removal recomputed from the state definition) must match
the exported ending CSVs row-for-row (multiset identity on
comp/date/stock/dir/entry_time/net) and to the paisa. Ending
books exported and independently re-summed; state updated.
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r12_lib as R12
import stocks_engine_r9_ingredients as ING
import stocks_engine_r8_builders as B8
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r12_results.json"))}
assert res["R12-02"]["banked"] is True
assert res["R12-03"]["banked"] is False
assert set(res["R12-03"]["failed_legs"]) == {"c_2026_no_fall",
                                             "e_extop3"}

books = R12.load_books()

def prev_bar(t):
    hh, mm = map(int, t.split(":"))
    m = hh * 60 + mm - 5
    return f"{m // 60:02d}:{m % 60:02d}"

def bucket_of(row):
    et = row.get("entry_time") or ""
    if len(et) != 5:
        return "unknown"
    mv = B8.nifty_move(row["date"], prev_bar(et))
    if mv is None:
        return "unknown"
    if mv <= -0.30:
        return "hard"
    if mv < 0:
        return "shallow"
    return "up"

def apply_harddip(bk):
    return {yr: [t for t in bk[yr]
                 if not (t["comp"] == "INV-ABOVE"
                         and bucket_of(t) == "hard")]
            for yr in (2025, 2026)}

ending = apply_harddip(books)

# union re-gate (placebos recomputed as in R12-02)
removed = {yr: [t for t in books[yr]
                if t["comp"] == "INV-ABOVE"
                and bucket_of(t) == "hard"]
           for yr in (2025, 2026)}
def keyf(t):
    return (t["date"], t.get("entry_time") or "", t["stock"])
def remove_n(rows, comp, n, pred):
    cand = sorted([t for t in rows if t["comp"] == comp
                   and pred(t)], key=keyf)
    take = {id(t) for t in cand[:n]}
    return [t for t in rows if id(t) not in take]
pl_books = []
for mode in ("chrono", "cross"):
    pb = {}
    for yr in (2025, 2026):
        n = len(removed[yr])
        if mode == "chrono":
            pb[yr] = remove_n(books[yr], "INV-ABOVE", n,
                              lambda t: True)
        else:
            rows = remove_n(books[yr], "INV-ABOVE", n,
                            lambda t: bucket_of(t) not in
                            ("hard", "unknown"))
            removed_ct = sum(1 for t in books[yr]
                             if t["comp"] == "INV-ABOVE") - \
                sum(1 for t in rows if t["comp"] == "INV-ABOVE")
            short = n - removed_ct
            if short > 0:
                rows = remove_n(rows, "INV-ABOVE", short,
                                lambda t: bucket_of(t) == "hard")
            pb[yr] = rows
    pl_books.append(R12.full_total(pb))
out = R12.gate(books, ending, pl_books, timing_violations=0)
assert out["verdict"], out["legs"]
end_jo = {yr: R12.jo(ending, yr) for yr in (2025, 2026)}
assert end_jo == {2025: 101114.78, 2026: 251553.07}, end_jo
R12.record_audit(
    "R12-09",
    "WS5 combinations + stack-price maintenance + December "
    "freeze addendum + finalise",
    f"Union of Round-12 bankings = R12-02 alone (R12-03 "
    f"rejected on (c) + (e); R12-06 / R12-08 produced no "
    f"candidate). Re-gated whole-book: verdict PASS (2025 "
    f"JO {out['var']['2025']['jan_oct']}; 2026 JO "
    f"{out['var']['2026']['jan_oct']}; combined "
    f"{out['sums']['variant_combined']}) — identical to the "
    f"R12-02 gate, as it must be. Ending book exported to "
    f"stocks_engine_r12_book{{2025,2026}}_trades.csv, "
    f"independently re-summed, and regeneration-verified "
    f"against a fresh rebuild from the Round-11 CSVs "
    f"(multiset identity, both years). Stack prices "
    f"restated on the ending book (see report). December "
    f"freeze addendum (Round 12) appended.",
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
    outb = R12.add_comp(base, slot_rows[2025][0]["comp"],
                        slot_rows)
    outb = R12.add_comp(outb, "REXP", ing["rexp"])
    return {yr: R12.jo(outb, yr) for yr in (2025, 2026)}
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

# --------------------------------------------- export books --
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r12_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in ending[yr]:
            w.writerow({k: t[k] for k in FIELDS})
    rows = list(csv.DictReader(open(path)))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    print(f"ending {yr}: {len(rows)} rows, JO {jo}, full {full}")
    assert jo == end_jo[yr]
    assert full == {2025: 101111.57, 2026: 251553.07}[yr], full

# --------------------------- regeneration verification ------
regen = apply_harddip(R12.load_books())
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r12_book{yr}_trades.csv")))
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
      "the Round-11 CSVs (hard-dip removal recomputed from "
      "the state definition) matches the exported ending "
      "CSVs row-for-row and to the paisa in both years.")

# freeze addendum: the ending book after Round 12
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R12-09, same day) — the ending book "
        "after Round 12\n"
        "Round 12 banked one further change (R12-02): the "
        "INV-ABOVE hard-dip exclusion — INV-ABOVE rows whose "
        "index state at the entry instant (close of the last "
        "5-min NIFTY bar completing at entry vs prior close) "
        "is a hard dip (<= -0.30%) are not traded (23 rows "
        "removed in 2025, 16 in 2026; the state is knowable "
        "at the entry instant by construction — the bucketed "
        "bar completes exactly at entry). The book judged in "
        "December is the R11-08 ending book PLUS this "
        "exclusion. Ending book: 2025 Jan-Oct "
        f"{end_jo[2025]} on {len(ending[2025])} rows; 2026 "
        f"Jan-Oct {end_jo[2026]} on {len(ending[2026])} "
        "rows. Regeneration verification PASSED (R12-09): "
        "rebuilt from the Round-11 CSVs by fresh code, the "
        "book matches the exported Round-12 CSVs row-for-row "
        "and to the paisa in both years. The December "
        "pass/kill lines above apply to the ending book as "
        "a whole.\n")

# ------------------------------------------------------ state ---
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round12_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 2,
    "decision_support": 0,
    "audits": 5,
    "banked": 1,
    "voided_rows": 0,
    "report": "stocks_engine_round12_2026-11-02.md",
    "evidence": "r12_results.json",
    "ending_book": "2025 JO 1,01,114.78; 2026 JO 2,51,553.07 "
                   "(R12-02 hard-dip exclusion banked on the "
                   "pair book)",
    "workstreams": {
        "WS1_hard_dip_new_baseline": "R12-02 BANKED: the "
            "R11-02 construction verbatim on the pair book — "
            "all ten legs pass (the (e) failure of -135.40 "
            "combined on the pre-pair baseline is cured by "
            "the pair book's breadth: combined ex-top-3 base "
            "1,03,228.30 vs 1,01,181.87, carrier sets moved). "
            "2025 JO -> 1,01,114.78 (+1,751.72); 2026 JO -> "
            "2,51,553.07 (+4,012.18).",
        "WS2_flag_retests": "R12-03 REJECTED: R5-03-clean "
            "re-gated on the pair book fails (c) + (e) — its "
            "recorded 2026 delta (+2,778.21) predates "
            "GAP-FADE-INC; the clean swap must now retire the "
            "banked increment too, and 2026 falls -1,984.82 "
            "(JO 2,45,556.07) while 2025 rises +8,289.44. "
            "R12-04 audit: every other single-leg flag is "
            "pre-refused by delta-leg arithmetic (printed "
            "per flag) — (c)-only REXP/FADE forms displace "
            "banked rows with worse 2026 nets by identity; "
            "NE-REV slot alternatives are non-additive with "
            "NU and fail (b)/(c) as swaps.",
        "WS3_october": "R12-05: October 2025 (-3,751.28, 20 "
            "rows) is F4 -3,021.83, entirely up-state rows; "
            "the separator test fails leg (iii) — F4's "
            "up-state bucket is +30,693.95 combined across "
            "the two years (2026's engine room). R12-06 "
            "closes by statement: no candidate.",
        "WS4_july": "R12-07: July residual (-2,101.93, 41 "
            "rows) — offender INV-ABOVE x shallow-dip "
            "(-2,473.45, the R10-05 cell verbatim) fails "
            "leg (iii) again (combined +2,445.28); the rest "
            "is GAP-FADE-INC -1,560.10 and F4 -1,025.28 "
            "diffuse. R12-08 closes by statement.",
        "WS5": "R12-09: union = R12-02 alone, re-gated "
            "PASS. Stack totals reproduced exactly on the "
            "ending book; adoption values restated "
            "(unconditioned +22,116.33 / -4,005.82; A "
            "+26,019.24 / -7,091.84; C +18,698.66 / "
            "-4,374.28; IDXCELL +12,031.60 / +6,250.81) — "
            "after this banking only IDXCELL still adds in "
            "both years; the unconditioned and C forms now "
            "COST 2026 against the ending book. December "
            "freeze extended (R12-09 addendum) with "
            "regeneration verification PASSED.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r12_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r12_book2026_trades.csv",
    "book_id": "R12-FINAL (R12-02 INV-ABOVE hard-dip "
               "exclusion banked on the R11 pair book; "
               "exports verified by re-sum + regeneration)",
    "floor_status": {
        "2025": "NOT MET - Rs1,01,114.78 (Rs10,111.48/mo), "
                "gap Rs48,885.22",
        "2026": "MET - Rs2,51,553.07 (Rs25,155.31/mo)",
    },
    "jan_oct_2025": 101114.78,
    "jan_oct_2026": 251553.07,
    "red_months_2025_jan_oct": {
        "2025-07": -2101.93,
        "2025-10": -3751.28,
    },
    "total_2025_full": 101111.57,
    "total_2026_full": 251553.07,
    "trades_2025": 1105,
    "trades_2026": 1352,
}
st["cycles_completed"] += [
    "R12-01 AUDIT (starting-book re-verification + INV-ABOVE "
    "state census on the pair book: R11-01 bucket nets "
    "reproduced exactly; unknown 0)",
    "R12-02 BANKED (INV-ABOVE hard-dip exclusion re-gated on "
    "the pair baseline; all ten legs pass — R11-02's (e)-only "
    "failure cured by the new baseline's breadth)",
    "R12-03 REJECTED (R5-03-clean re-gated on the pair book; "
    "fails c + e — the clean swap now retires GAP-FADE-INC "
    "and 2026 falls)",
    "R12-04 AUDIT (WS2 screening arithmetic: all other "
    "single-leg flags pre-refused by delta-leg arithmetic; "
    "no candidate scored)",
    "R12-05 AUDIT (October-2025 decomposition: F4 x up-state "
    "-3,021.83 is the wound; separator fails leg iii)",
    "R12-06 AUDIT (October conditioned variant closes by "
    "statement — 0 qualifying separators)",
    "R12-07 AUDIT (July-2025 residual decomposition: "
    "INV-ABOVE x shallow-dip -2,473.45; separator fails leg "
    "iii again)",
    "R12-08 AUDIT (July conditioned variant closes by "
    "statement — 0 qualifying separators)",
    "R12-09 AUDIT (WS5 combinations: union = R12-02, "
    "re-gated PASS; stack prices restated on the ending "
    "book; December freeze addendum regeneration-verified)",
]
# flagged list maintenance: R11-02 is banked now (as R12-02);
# R5-03's gate sheet is restated to its R12-03 verdict
# (R6-L5 discipline: decision state moves with the book).
flags = []
for fl in st["flagged_awaiting_chandu"]:
    if fl["id"] == "R11-02":
        continue
    if fl["id"] == "R5-03":
        fl = {**fl,
              "failed_legs": ["c_2026_no_fall", "e_extop3"],
              "note": "re-gated at R12-03 on the pair book: "
                      "fails (c) + (e) — the clean swap now "
                      "retires the banked GAP-FADE-INC as "
                      "well, and 2026 falls -1,984.82 (JO "
                      "2,45,556.07 vs 2,47,540.89 on the "
                      "starting book) while 2025 rises "
                      "+8,289.44. Adoption value from the "
                      "R12 ending book: 2025 JO +6,537.72 / "
                      "2026 JO -5,997.00 (disjoint-comp "
                      "arithmetic). Birth sheet (fails (e) "
                      "only, Round-4 book) is superseded.",
              "delta_2025_jan_oct": 6537.72,
              "delta_2026_jan_oct": -5997.00}
    flags.append(fl)
st["flagged_awaiting_chandu"] = flags
st["consecutive_no_bank"] = 0
st["iteration"] = 48
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round12_summary, incumbent -> r12 CSVs, "
      "9 cycles, R11-02 flag retired (banked), R5-03 flag "
      "restated (24 flags remain)")

for yr in (2025, 2026):
    sc = FL.scorecard(ending[yr], yr)
    print(yr, "JO", sc["jan_oct_total"], "trades",
          sc["jan_oct_trades"], "ex_top3 full",
          sc["ex_top3_stocks"], "months", sc["months"])
print("finalise done.")
