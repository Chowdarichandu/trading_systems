#!/usr/bin/env python3
"""ROUND 15 — R15-08: combinations + stack-price maintenance
+ December freeze addendum + finalise.

Round 15 banked NOTHING: R15-02 (INV-ABOVE T175/S050) was
rejected on leg (c) only and joins the flagged list with its
adoption value measured from the ending book; R15-03
(GAP-FADE family T125/S080) failed four legs and is not
flagged; the volume axis (WS2/WS3) produced no gated cell —
the frozen diagnostic was negative on all three sleeves, so
no volume gate ran. The ending book therefore EQUALS the
starting (Round-14) book. Stack prices are restated on the
ending book by the generalised R12-09 method — totals must
reproduce the recorded prices exactly. December freeze
addendum records the no-change round; regeneration
verification: the ending book rebuilt from the Round-14
CSVs by fresh code (no Round-15 construction is banked, so
the rebuild is the audited starting book itself) must match
the exported Round-15 CSVs row-for-row and to the paisa.
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r15_lib as R15
import stocks_engine_r14_builders as B14
import stocks_engine_r9_ingredients as ING
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r15_results.json"))}
assert res["R15-02"]["banked"] is False
assert res["R15-02"]["failed_legs"] == ["c_2026_no_fall"]
assert res["R15-03"]["banked"] is False
assert res["R15-03"]["failed_legs"] == ["a_combined_rises",
                                        "b_2025_no_fall",
                                        "c_2026_no_fall",
                                        "e_extop3"]
assert res["R15-06"]["type"] == "audit"
assert res["R15-07"]["type"] == "audit"

books = R15.load_books()
ending = books  # no bankings: ending book == starting book
end_jo = {yr: R15.jo(ending, yr) for yr in (2025, 2026)}
assert end_jo == {2025: 105987.24, 2026: 257300.30}, end_jo

R15.record_audit(
    "R15-08",
    "WS4 combinations + stack-price maintenance + December "
    "freeze addendum + finalise",
    "Combinations: NOTHING banked in Round 15, so there is "
    "no union to re-gate — the ending book is the starting "
    "(Round-14) book unchanged (2025 JO 105987.24; 2026 JO "
    "257300.30). R15-02 rejected on (c) only — FLAGGED as "
    "an owner decision; R15-03 rejected on (a) + (b) + (c) "
    "+ (e) — not flagged. Volume: coverage complete for "
    "every gated population (0 unclassifiable rows), the "
    "frozen diagnostic negative on all three sleeves, no "
    "volume gate ran and nothing volume-based is in the "
    "book. Ending book exported to stocks_engine_r15_book"
    "{2025,2026}_trades.csv, independently re-summed, and "
    "regeneration-verified against a fresh load of the "
    "Round-14 CSVs (multiset identity, both years). Stack "
    "prices restated on the ending book (see report). "
    "December freeze addendum (Round 15) appended: the "
    "frozen book is unchanged.",
    extra={"ending_jo": {str(k): v for k, v in end_jo.items()},
           "banked_round15": 0})

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
    outb = R15.add_comp(base, slot_rows[2025][0]["comp"],
                        slot_rows)
    outb = R15.add_comp(outb, "REXP", ing["rexp"])
    return {yr: R15.jo(outb, yr) for yr in (2025, 2026)}
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

# -------------------------------------- flag pricing (R15-02)
real_a, _side, _dr = B14.inv_above_geo(1.75, 0.50)
a_book = R15.swap(ending, "INV-ABOVE", real_a)
a_delta = {yr: round(R15.jo(a_book, yr) - end_jo[yr], 2)
           for yr in (2025, 2026)}
assert a_delta == {2025: 92.57, 2026: -1198.29}, a_delta
print(f"R15-02 flag: adoption from ending book -> deltas "
      f"{a_delta}")

# --------------------------------------------- export books --
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
end_full = {}
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r15_book{yr}_trades.csv"
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
fresh = {yr: FL.load(f"stocks_engine_r14_book{yr}_trades.csv")
         for yr in (2025, 2026)}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r15_book{yr}_trades.csv")))
    got = Counter((r["comp"], r["date"], r["stock"], r["dir"],
                   r["entry_time"], round(float(r["net"]), 2))
                  for r in rows)
    want = Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2))
                   for t in fresh[yr])
    assert got == want, (yr, "multiset mismatch")
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    assert jo == end_jo[yr]
print("regeneration verification PASSED: fresh load of the "
      "Round-14 CSVs (no Round-15 construction is banked) "
      "matches the exported Round-15 CSVs row-for-row and to "
      "the paisa in both years.")

# freeze addendum: no change to the frozen book in Round 15
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R15-08, same day) — Round 15: the "
        "frozen book is UNCHANGED\n"
        "Round 15 banked nothing, so the book judged in "
        "December is exactly the Round-14 ending book (the "
        "R13-08 book with INV-ABOVE at T150/S050 and the "
        "GAP-FADE family at T125/S065), at 2025 Jan-Oct "
        f"{end_jo[2025]} on {len(ending[2025])} rows and "
        f"2026 Jan-Oct {end_jo[2026]} on "
        f"{len(ending[2026])} rows. Round 15's tested cells "
        "are NOT in the frozen book: INV-ABOVE T175/S050 "
        "(rejected on leg (c) only; flagged for the owner — "
        "adoption from the ending book: 2025 JO +92.57 / "
        "2026 JO -1,198.29), the GAP-FADE family at "
        "T125/S080 (rejected on four legs; the family's stop "
        "axis is closed at S065), and NO volume-conditioned "
        "form (the volume data axis was built this round — "
        "stocks_daily_volume.csv — under the causality law "
        "that a day's volume may condition only later days' "
        "decisions; the frozen rvol >= 1.0 diagnostic was "
        "negative on F4, N4-V3 and the P2F family, so no "
        "volume gate ran and no volume rule is frozen). "
        "Regeneration verification PASSED (R15-08): the "
        "exported Round-15 CSVs match a fresh load of the "
        "Round-14 CSVs row-for-row and to the paisa in both "
        "years. The December pass/kill lines above apply to "
        "the book as a whole, unchanged.\n")

# ------------------------------------------------------ state ---
sc = {yr: FL.scorecard(ending[yr], yr) for yr in (2025, 2026)}
red_months = {m: v for m, v in sc[2025]["months"].items()
              if m <= "2025-10" and v < 0}
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round15_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 2,
    "decision_support": 0,
    "audits": 5,
    "banked": 0,
    "voided_rows": 0,
    "report": "stocks_engine_round15_2026-11-02.md",
    "evidence": "r15_results.json",
    "ending_book": "UNCHANGED from Round 14 — 2025 JO "
                   "1,05,987.24; 2026 JO 2,57,300.30 (no "
                   "Round-15 banking)",
    "workstreams": {
        "WS1_two_step_geometry": "R15-02 INV-ABOVE "
            "T175/S050 REJECTED on (c) only: 2025 JO "
            "+92.57, 2026 JO -1,198.29 — the second target "
            "step is the year-trade again at a much smaller "
            "price; FLAGGED (one leg). R15-03 GAP-FADE "
            "family T125/S080 REJECTED on (a) + (b) + (c) "
            "+ (e): 2025 JO -2,548.14, 2026 JO -4,790.90 — "
            "the stop axis that paid at S065 reverses at "
            "S080; not flagged (four legs). Both banked "
            "directions are now measured at their second "
            "rung: geometry is closed at two steps as it "
            "was at one.",
        "WS2_volume_build": "Daily volume fetched for the "
            "25 stocks + NIFTY (v3 days/1 via the connector "
            "path) into the NEW dataset "
            "stocks_daily_volume.csv (12,584 rows, "
            "2024-11-15..2026-10-31; pre-2025 tail is "
            "lookback only). Coverage per stock-year "
            "COMPLETE for all 25 stocks in both years "
            "(249/249 in 2025, 203/203 in 2026; zero holes, "
            "zero zero-volume days; the series also covers "
            "2026-10-29/30 beyond the machinery's stored "
            "daily span). NIFTY volume is 0 on every day as "
            "returned (an index has no traded volume) — "
            "stored as returned, used by no gate. No "
            "existing candle file altered.",
        "WS3_volume_gates": "Frozen diagnostic (keep "
            "prior-day rvol >= 1.0 vs trailing-20-day "
            "median; causality asserted row by row; 0 "
            "unclassifiable rows in any sleeve): F4 "
            "combined -47,355.57 (+1,972.94 / -49,328.51), "
            "N4-V3 -9,385.58, P2F family -3,003.70 — NO "
            "sleeve positive, so per the frozen rule NO "
            "volume gate ran (R15-06 / R15-07 close as "
            "audits). High prior-day volume is where these "
            "sleeves' losers concentrate in 2026, above all "
            "F4's.",
        "WS4": "R15-08: no bankings, no union to re-gate; "
            "ending book == starting book. Stack totals "
            "reproduced exactly; adoption values unchanged "
            "from Round 14 (unconditioned +17,243.87 / "
            "-9,753.05; A +21,146.78 / -12,839.07; C "
            "+13,826.20 / -10,121.51; IDXCELL +7,159.14 / "
            "+503.58). December freeze addendum (Round 15) "
            "appended: frozen book unchanged; regeneration "
            "verification PASSED.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r15_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r15_book2026_trades.csv",
    "book_id": "R15-FINAL == R14-FINAL (Round 15 banked "
               "nothing; exports verified by re-sum + "
               "regeneration against the Round-14 CSVs)",
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
    "R15-01 AUDIT (starting-book re-verification from the "
    "R14 CSVs: totals/rows exact; Jul -2,733.21 / Oct "
    "-4,152.19 asserted)",
    "R15-02 REJECTED (INV-ABOVE geometry swap T175/S050, "
    "second target step; fails c only — flagged as an "
    "owner decision)",
    "R15-03 REJECTED (GAP-FADE family geometry swap "
    "T125/S080, second stop step; fails a + b + c + e)",
    "R15-04 AUDIT (volume axis build: daily volume for 25 "
    "stocks + NIFTY stored as stocks_daily_volume.csv; "
    "coverage complete both years, zero holes)",
    "R15-05 AUDIT (volume diagnostic: rvol >= 1.0 combined "
    "deltas F4 -47,355.57 / N4-V3 -9,385.58 / P2F family "
    "-3,003.70 — no sleeve positive)",
    "R15-06 AUDIT (volume gate 1 NOT RUN — frozen rule: no "
    "positive diagnostic sleeve)",
    "R15-07 AUDIT (volume gate 2 NOT RUN — frozen rule)",
    "R15-08 AUDIT (WS4: no bankings; stack prices restated "
    "exactly on the unchanged ending book; December "
    "freeze addendum — book unchanged — "
    "regeneration-verified)",
]
st["flagged_awaiting_chandu"] = st["flagged_awaiting_chandu"] + [
    {
        "id": "R15-02",
        "candidate": "INV-ABOVE geometry swap to T175/S050 "
                     "(banked INV-ABOVE sleeve at the "
                     "second-step wider target)",
        "failed_legs": ["c_2026_no_fall"],
        "note": "fails (c) only; no flips, placebos beaten, "
                "combined full-year total RISES (+1,001.66) "
                "on Nov/Dec-2025 strength. Adoption on the "
                "R15 ending book -> 2025 JO +92.57, 2026 JO "
                "-1,198.29 (2026 stays far above floor). "
                "Alternative form of the banked INV-ABOVE "
                "sleeve — never additive with it or with "
                "R2-26 (same sleeve).",
        "delta_2025_jan_oct": 92.57,
        "delta_2026_jan_oct": -1198.29,
    },
]
st["consecutive_no_bank"] = 1
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round15_summary, incumbent -> r15 CSVs, "
      "8 cycles, R15-02 flag added (28 flags)")

for yr in (2025, 2026):
    print(yr, "JO", sc[yr]["jan_oct_total"], "trades",
          sc[yr]["jan_oct_trades"], "ex_top3 full",
          sc[yr]["ex_top3_stocks"], "months", sc[yr]["months"])
print("finalise done.")
