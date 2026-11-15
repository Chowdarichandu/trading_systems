#!/usr/bin/env python3
"""ROUND 13 — WS4 combinations + stack-price maintenance +
December freeze addendum + finalise (R13-08).

Bankings: R13-05 (REXP-DOWN geometry swap to T100/S050)
BANKED. R13-02 rejected on nine legs, R13-03 on seven,
R13-04 on (a) + (c) + (e), R13-06 on (a) + (c), R13-07 on
(a) + (b) + (c) + (f). The WS4 union is therefore R13-05
alone — re-gated whole-book here against the starting book
as the combination record. Ending book = Round-12 ending
book with the REXP rows replaced by the T100/S050 set.
Stack prices restated on the ending book by the generalised
R12-09 method (the REXP / NE-REV strips are by component,
so the banked geometry change does not disturb the identity
— totals must reproduce the recorded prices exactly).
December freeze extended to the ending book with
REGENERATION VERIFICATION: the ending book rebuilt from the
Round-12 CSVs by fresh code (the T100/S050 REXP set rebuilt
by rexp_geo) must match the exported ending CSVs row-for-row
(multiset identity on comp/date/stock/dir/entry_time/net)
and to the paisa. Ending books exported and independently
re-summed; state updated. Near-miss flags: R13-06 fails
exactly two legs and joins the flagged list with its
adoption value measured from the ending book; R13-04 fails
three legs and, under the frozen Round-13 rule (at most two),
does not.
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r13_lib as R13
import stocks_engine_r8_builders as B8
import stocks_engine_r9_ingredients as ING
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r13_results.json"))}
assert res["R13-05"]["banked"] is True
for cyc in ("R13-02", "R13-03", "R13-04", "R13-06", "R13-07"):
    assert res[cyc]["banked"] is False, cyc
assert res["R13-04"]["failed_legs"] == ["a_combined_rises",
                                        "c_2026_no_fall",
                                        "e_extop3"]
assert res["R13-06"]["failed_legs"] == ["a_combined_rises",
                                        "c_2026_no_fall"]

books = R13.load_books()

# --------------------------------------------- ending book --
rexp_new, rexp_f, rexp_l, viol = B8.rexp_geo(
    "SHORT", cells={"DOWN"}, tgt=1.00, stp=0.50)
assert viol == 0, viol
ending = R13.swap(books, "REXP", rexp_new)
pl = [R13.full_total(R13.swap(books, "REXP", rexp_f)),
      R13.full_total(R13.swap(books, "REXP", rexp_l))]
out = R13.gate(books, ending, pl, timing_violations=viol)
assert out["verdict"], out["legs"]
end_jo = {yr: R13.jo(ending, yr) for yr in (2025, 2026)}
assert end_jo == {2025: 103357.44, 2026: 253068.45}, end_jo
R13.record_audit(
    "R13-08",
    "WS4 combinations + stack-price maintenance + December "
    "freeze addendum + finalise",
    f"Union of Round-13 bankings = R13-05 alone (R13-02 "
    f"rejected on nine legs; R13-03 on seven; R13-04 on "
    f"(a)+(c)+(e); R13-06 on (a)+(c); R13-07 on (a)+(b)+"
    f"(c)+(f)). Re-gated whole-book: verdict PASS (2025 JO "
    f"{out['var']['2025']['jan_oct']}; 2026 JO "
    f"{out['var']['2026']['jan_oct']}; combined "
    f"{out['sums']['variant_combined']}) — identical to the "
    f"R13-05 gate, as it must be. Ending book exported to "
    f"stocks_engine_r13_book{{2025,2026}}_trades.csv, "
    f"independently re-summed, and regeneration-verified "
    f"against a fresh rebuild from the Round-12 CSVs "
    f"(multiset identity, both years). Stack prices "
    f"restated on the ending book (see report). December "
    f"freeze addendum (Round 13) appended.",
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
    outb = R13.add_comp(base, slot_rows[2025][0]["comp"],
                        slot_rows)
    outb = R13.add_comp(outb, "REXP", ing["rexp"])
    return {yr: R13.jo(outb, yr) for yr in (2025, 2026)}
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

# ------------------------------------ R13-06 flag pricing ---
import stocks_engine_r13_builders as B13
nu125, nu125_f, nu125_l = B13.nu_geo(1.25, 0.65)
flag_book = R13.swap(ending, "NE-REV-NU", nu125)
flag_jo = {yr: R13.jo(flag_book, yr) for yr in (2025, 2026)}
flag_delta = {yr: round(flag_jo[yr] - end_jo[yr], 2)
              for yr in (2025, 2026)}
assert flag_delta == {2025: 2326.81, 2026: -5998.05}, flag_delta
print(f"R13-06 flag: adoption from ending book -> 2025 JO "
      f"{flag_jo[2025]} / 2026 JO {flag_jo[2026]} (deltas "
      f"{flag_delta})")

# --------------------------------------------- export books --
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
end_full = {}
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r13_book{yr}_trades.csv"
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
rx2, _f2, _l2, v2 = B8.rexp_geo("SHORT", cells={"DOWN"},
                                tgt=1.00, stp=0.50)
assert v2 == 0
regen = R13.swap(R13.load_books(), "REXP", rx2)
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r13_book{yr}_trades.csv")))
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
      "the Round-12 CSVs (REXP-DOWN rebuilt at T100/S050 by "
      "rexp_geo) matches the exported ending CSVs row-for-row "
      "and to the paisa in both years.")

# freeze addendum: the ending book after Round 13
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R13-08, same day) — the ending book "
        "after Round 13\n"
        "Round 13 banked one further change (R13-05): the "
        "REXP-DOWN sleeve's exit geometry moves from "
        "T100/S065 to **T100/S050** — the sleeve's population, "
        "admission and entry (SHORT, DOWN regime cells, 10:20 "
        "entry) are unchanged; only the stop tightens from "
        "0.65% to 0.50% (41 rows in 2025, 86 in 2026; sleeve "
        "Jan-Oct +10,243.45 / -5,899.72 at T100/S065 -> "
        "+12,486.11 / -4,384.34 at T100/S050). Exit geometry "
        "carries no admission "
        "information, so the freeze's timing argument is "
        "unaffected. The book judged in December is the "
        "R12-09 ending book PLUS this geometry change. "
        "Ending book: 2025 Jan-Oct "
        f"{end_jo[2025]} on {len(ending[2025])} rows; 2026 "
        f"Jan-Oct {end_jo[2026]} on {len(ending[2026])} "
        "rows. Regeneration verification PASSED (R13-08): "
        "rebuilt from the Round-12 CSVs by fresh code, the "
        "book matches the exported Round-13 CSVs row-for-row "
        "and to the paisa in both years. The December "
        "pass/kill lines above apply to the ending book as "
        "a whole.\n")

# ------------------------------------------------------ state ---
sc = {yr: FL.scorecard(ending[yr], yr) for yr in (2025, 2026)}
red_months = {m: v for m, v in sc[2025]["months"].items()
              if m <= "2025-10" and v < 0}
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round13_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 6,
    "decision_support": 0,
    "audits": 2,
    "banked": 1,
    "voided_rows": 0,
    "report": "stocks_engine_round13_2026-11-02.md",
    "evidence": "r13_results.json",
    "ending_book": "2025 JO 1,03,357.44; 2026 JO 2,53,068.45 "
                   "(R13-05 REXP-DOWN geometry swap to "
                   "T100/S050 banked)",
    "workstreams": {
        "WS1_sweep": "R13-02 SWEEP-RECLAIM REJECTED on nine "
            "of ten legs — standalone deeply negative in both "
            "years (book combined 3,52,664.64 -> 83,072.49 "
            "with it added); R13-03 SWEEP-REJECT REJECTED on "
            "seven legs (combined -> 3,40,400.28). Chandu's "
            "index method #4 transplanted to cash stocks is "
            "closed: the prior-day level event carries no "
            "information on his 25 (Lesson 2's family, "
            "confirming instance).",
        "WS2_rexp_geo": "R13-04 T125/S065 REJECTED on (a) + "
            "(c) + (e): 2025 +2,291.26, 2026 -4,252.67 — the "
            "wider target re-prices the birth trade-off. "
            "R13-05 T100/S050 BANKED, all ten legs: 2025 JO "
            "-> 1,03,357.44 (+2,242.66), 2026 JO -> "
            "2,53,068.45 (+1,515.38); the banked sleeve's "
            "0.65% stop was too wide for its population.",
        "WS3_nu_geo": "R13-06 T125/S065 REJECTED on (a) + "
            "(c) only (2025 +2,326.81 / 2026 -5,998.05) — "
            "flagged as an owner decision. R13-07 T100/S050 "
            "REJECTED on (a) + (b) + (c) + (f): the tighter "
            "stop that paid REXP hurts NU in both years — "
            "exit medicine is population-specific (Lesson 4), "
            "again. NU's frozen cell is bracketed: wider "
            "target fails (c), tighter stop fails (b)+(c).",
        "WS4": "R13-08: union = R13-05 alone, re-gated PASS. "
            "Stack totals reproduced exactly on the ending "
            "book; adoption values restated (unconditioned "
            "+19,873.67 / -5,521.20; A +23,776.58 / "
            "-8,607.22; C +16,456.00 / -5,889.66; IDXCELL "
            "+9,789.94 / +4,735.43) — IDXCELL remains the "
            "only stack form adding in both years. December "
            "freeze extended (R13-08 addendum) with "
            "regeneration verification PASSED.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r13_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r13_book2026_trades.csv",
    "book_id": "R13-FINAL (R13-05 REXP-DOWN geometry swap to "
               "T100/S050 banked on the R12 book; exports "
               "verified by re-sum + regeneration)",
    "floor_status": {
        "2025": "NOT MET - Rs1,03,357.44 (Rs10,335.74/mo), "
                "gap Rs46,642.56",
        "2026": "MET - Rs2,53,068.45 (Rs25,306.85/mo)",
    },
    "jan_oct_2025": 103357.44,
    "jan_oct_2026": 253068.45,
    "red_months_2025_jan_oct": {k: round(v, 2)
                                for k, v in red_months.items()},
    "total_2025_full": end_full[2025],
    "total_2026_full": end_full[2026],
    "trades_2025": len(ending[2025]),
    "trades_2026": len(ending[2026]),
}
st["cycles_completed"] += [
    "R13-01 AUDIT (starting-book re-verification from the "
    "R12 CSVs: totals/rows exact; Jul -2,101.93 / Oct "
    "-3,751.28 asserted)",
    "R13-02 REJECTED (SWEEP-RECLAIM LONG, prior-day-low "
    "sweep + reclaim, T125/S050; fails nine of ten legs — "
    "standalone deeply negative both years)",
    "R13-03 REJECTED (SWEEP-REJECT SHORT, prior-day-high "
    "sweep + rejection; fails a, b, c, d, e, f, h)",
    "R13-04 REJECTED (REXP-DOWN geometry swap T125/S065; "
    "fails a + c + e)",
    "R13-05 BANKED (REXP-DOWN geometry swap T100/S050; all "
    "ten legs pass — 2025 JO +2,242.66, 2026 JO +1,515.38)",
    "R13-06 REJECTED (NE-REV-NU geometry swap T125/S065; "
    "fails a + c only — flagged as an owner decision)",
    "R13-07 REJECTED (NE-REV-NU geometry swap T100/S050; "
    "fails a + b + c + f — Jun 2025 flips)",
    "R13-08 AUDIT (WS4 combinations: union = R13-05, "
    "re-gated PASS; stack prices restated on the ending "
    "book; December freeze addendum regeneration-verified)",
]
st["flagged_awaiting_chandu"] = st["flagged_awaiting_chandu"] + [{
    "id": "R13-06",
    "candidate": "NE-REV-NU geometry swap to T125/S065 "
                 "(banked NU sleeve at the wider target)",
    "failed_legs": ["a_combined_rises", "c_2026_no_fall"],
    "note": "fails (a) + (c) only; no flips, placebos beaten. "
            "Adoption on the R13 ending book -> 2025 JO "
            "Rs1,05,684.25 (+2,326.81), 2026 JO Rs2,47,070.40 "
            "(-5,998.05; 2026 stays above floor). The NU "
            "sleeve's 2025/2026 geometry trade-off at one "
            "price: the wider target buys the weak year with "
            "the strong year's money. Alternative form of the "
            "banked NU sleeve — never additive with it.",
    "delta_2025_jan_oct": 2326.81,
    "delta_2026_jan_oct": -5998.05,
}]
st["consecutive_no_bank"] = 0
st["iteration"] = 48
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round13_summary, incumbent -> r13 CSVs, "
      "8 cycles, R13-06 flag added (25 flags)")

for yr in (2025, 2026):
    print(yr, "JO", sc[yr]["jan_oct_total"], "trades",
          sc[yr]["jan_oct_trades"], "ex_top3 full",
          sc[yr]["ex_top3_stocks"], "months", sc[yr]["months"])
print("finalise done.")
