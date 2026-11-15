#!/usr/bin/env python3
"""ROUND 16 — R16-05 combinations + stack maintenance, and
R16-06 December freeze addendum + finalise.

Round 16 banked NOTHING: R16-02 (F4 volume mirror) was
rejected on five legs and R16-03 (N4-V3 volume mirror) on
four — neither joins the flagged list (the standing rule
flags rejections failing at most two legs). R16-04 (P2F
mirror) was not run: the condition frozen in the
pre-registration (WS1 or WS2 banks or fails on exactly one
leg) was not met. The ending book therefore EQUALS the
starting (Round-15) book. Stack prices are restated on the
ending book by the generalised R12-09 method — totals must
reproduce the recorded prices exactly. December freeze
addendum records the no-change round; regeneration
verification: the ending book rebuilt from the Round-15
CSVs by fresh code (no Round-16 construction is banked, so
the rebuild is the audited starting book itself) must match
the exported Round-16 CSVs row-for-row and to the paisa.
Cross-round identity asserted: each mirror's kept /
dropped-high counts equal Round 15's diagnostic dropped-low
/ kept counts exactly (the two forms partition the
classifiable rows).
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r16_lib as R16
import stocks_engine_r9_ingredients as ING
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r16_results.json"))}
assert res["R16-02"]["banked"] is False
assert res["R16-02"]["failed_legs"] == ["a_combined_rises",
                                        "b_2025_no_fall",
                                        "c_2026_no_fall",
                                        "e_extop3",
                                        "f_no_green_month_flips"]
assert res["R16-03"]["banked"] is False
assert res["R16-03"]["failed_legs"] == ["a_combined_rises",
                                        "b_2025_no_fall",
                                        "c_2026_no_fall",
                                        "e_extop3"]
assert res["R16-04"]["type"] == "audit"

# cross-round partition identity vs the R15 diagnostic
r15 = {r["cycle"]: r for r in json.load(open(f"{WS}/r15_results.json"))}
diag = r15["R15-05"]["diagnostic"]
for cyc, sleeve in (("R16-02", "F4"), ("R16-03", "N4-V3")):
    st = res[cyc]["conditioned_stats"]
    for yr in ("2025", "2026"):
        assert st["kept"][yr] == diag[sleeve]["low"][yr], (cyc, yr)
        assert st["high"][yr] == diag[sleeve]["kept"][yr], (cyc, yr)
        assert st["unclass"][yr] == diag[sleeve]["unclass"][yr]
print("partition identity OK: mirror kept/dropped counts == "
      "R15 diagnostic low/kept counts for F4 and N4-V3")

books = R16.load_books()
ending = books  # no bankings: ending book == starting book
end_jo = {yr: R16.jo(ending, yr) for yr in (2025, 2026)}
assert end_jo == {2025: 105987.24, 2026: 257300.30}, end_jo

R16.record_audit(
    "R16-05",
    "WS4 combinations + stack-price maintenance",
    "Combinations: NOTHING banked in Round 16, so there is "
    "no union to re-gate — the ending book is the starting "
    "(Round-15) book unchanged (2025 JO 105987.24; 2026 JO "
    "257300.30). R16-02 (F4 mirror) rejected on (a) + (b) + "
    "(c) + (e) + (f); R16-03 (N4-V3 mirror) rejected on (a) "
    "+ (b) + (c) + (e); R16-04 (P2F mirror) not run under "
    "the frozen WS3 condition. Neither rejection is flagged "
    "(both fail more than two legs; the standing rule flags "
    "at most two). Stack prices restated on the ending book "
    "(see report) — totals reproduce the recorded prices "
    "exactly, adoption values unchanged from Round 15.",
    extra={"ending_jo": {str(k): v for k, v in end_jo.items()},
           "banked_round16": 0})

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
    outb = R16.add_comp(base, slot_rows[2025][0]["comp"],
                        slot_rows)
    outb = R16.add_comp(outb, "REXP", ing["rexp"])
    return {yr: R16.jo(outb, yr) for yr in (2025, 2026)}
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
end_full = {}
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r16_book{yr}_trades.csv"
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
fresh = {yr: FL.load(f"stocks_engine_r15_book{yr}_trades.csv")
         for yr in (2025, 2026)}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r16_book{yr}_trades.csv")))
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
      "Round-15 CSVs (no Round-16 construction is banked) "
      "matches the exported Round-16 CSVs row-for-row and to "
      "the paisa in both years.")

# freeze addendum: no change to the frozen book in Round 16
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R16-06, same day) — Round 16: the "
        "frozen book is UNCHANGED\n"
        "Round 16 banked nothing, so the book judged in "
        "December is exactly the Round-15 ending book (the "
        "Round-14 book: INV-ABOVE at T150/S050, the GAP-FADE "
        "family at T125/S065), at 2025 Jan-Oct "
        f"{end_jo[2025]} on {len(ending[2025])} rows and "
        f"2026 Jan-Oct {end_jo[2026]} on "
        f"{len(ending[2026])} rows. Round 16's tested cells "
        "are NOT in the frozen book: the volume MIRROR forms "
        "(keep prior-day relative volume < 1.0 vs the "
        "trailing-20-day median, the exact complement of "
        "Round 15's frozen feature, under the same causality "
        "law — a day's volume conditions only later days' "
        "decisions) were gated whole-book and refused: F4 "
        "mirror rejected on legs (a) + (b) + (c) + (e) + (f) "
        "(2025 JO -2,064.08 / 2026 JO -53,727.42; March 2026 "
        "flips), N4-V3 mirror rejected on (a) + (b) + (c) + "
        "(e) (2025 JO -3,937.27 / 2026 JO -24,363.08); the "
        "P2F-family mirror was not run (the pre-registered "
        "condition — a banking or a single-leg near-miss in "
        "WS1/WS2 — was not met). The frozen band's volume "
        "axis is now measured in BOTH directions on the two "
        "largest sleeves and separates nothing: no volume "
        "rule is frozen. Regeneration verification PASSED "
        "(R16-06): the exported Round-16 CSVs match a fresh "
        "load of the Round-15 CSVs row-for-row and to the "
        "paisa in both years. The December pass/kill lines "
        "above apply to the book as a whole, unchanged.\n")

R16.record_audit(
    "R16-06",
    "December freeze addendum + finalise",
    "December freeze addendum (Round 16) appended: the "
    "frozen book is UNCHANGED by Round 16 — neither mirror "
    "form enters it. Ending book exported to stocks_engine"
    "_r16_book{2025,2026}_trades.csv, independently "
    "re-summed, and regeneration-verified against a fresh "
    "load of the Round-15 CSVs (multiset identity, both "
    "years). The volume axis at the frozen band is closed "
    "in both directions (see report).",
    extra={"ending_jo": {str(k): v for k, v in end_jo.items()},
           "banked_round16": 0})

# ------------------------------------------------------ state ---
sc = {yr: FL.scorecard(ending[yr], yr) for yr in (2025, 2026)}
red_months = {m: v for m, v in sc[2025]["months"].items()
              if m <= "2025-10" and v < 0}
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round16_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 2,
    "decision_support": 0,
    "audits": 4,
    "banked": 0,
    "voided_rows": 0,
    "report": "stocks_engine_round16_2026-11-02.md",
    "evidence": "r16_results.json",
    "ending_book": "UNCHANGED from Round 15 — 2025 JO "
                   "1,05,987.24; 2026 JO 2,57,300.30 (no "
                   "Round-16 banking)",
    "workstreams": {
        "WS1_F4_mirror": "R16-02 REJECTED on (a) + (b) + "
            "(c) + (e) + (f): keep prior-day rvol < 1.0 "
            "(134 / 165 rows kept of 246 / 355) — 2025 JO "
            "-2,064.08, 2026 JO -53,727.42, combined "
            "3,64,889.48 -> 3,09,097.98; March 2026 flips "
            "(+11,344.23 -> -673.18); placebos beaten; "
            "timing 0. Deleting F4's high-volume half cost "
            "2026 -49,328.51 at diagnostic (R15); deleting "
            "its quiet half costs -53,727.42 exact: the "
            "sleeve's 2026 value lives in BOTH halves.",
        "WS2_N4_mirror": "R16-03 REJECTED on (a) + (b) + "
            "(c) + (e): keep prior-day rvol < 1.0 (17 / 13 "
            "rows kept of 35 / 34) — 2025 JO -3,937.27, "
            "2026 JO -24,363.08, combined -> 3,38,225.04; "
            "no flips; placebos beaten; timing 0.",
        "WS3_P2F_mirror": "R16-04 NOT RUN — the frozen "
            "condition (WS1 or WS2 banks, or fails on "
            "exactly one leg) was not met (five and four "
            "failed legs). No P2F mirror number computed.",
        "WS4": "R16-05 / R16-06: no bankings, no union to "
            "re-gate; ending book == starting book. "
            "Neither rejection flagged (both fail more "
            "than two legs); flagged list stays at 28. "
            "Stack totals reproduced exactly; adoption "
            "values unchanged from Round 15 "
            "(unconditioned +17,243.87 / -9,753.05; A "
            "+21,146.78 / -12,839.07; C +13,826.20 / "
            "-10,121.51; IDXCELL +7,159.14 / +503.58). "
            "December freeze addendum (Round 16) appended: "
            "frozen book unchanged; regeneration "
            "verification PASSED. Frontier finding recorded "
            "in the report: the in-sample programme stands "
            "where the other segments stand — December "
            "fresh data, November forward evidence, owner "
            "decisions.",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r16_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r16_book2026_trades.csv",
    "book_id": "R16-FINAL == R15-FINAL == R14-FINAL (Round 16 "
               "banked nothing; exports verified by re-sum + "
               "regeneration against the Round-15 CSVs)",
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
    "R16-01 AUDIT (starting-book re-verification from the "
    "R15 CSVs: totals/rows exact; Jul -2,733.21 / Oct "
    "-4,152.19 asserted)",
    "R16-02 REJECTED (F4 volume MIRROR keep prior-day rvol "
    "< 1.0; fails a + b + c + e + f — March 2026 flips)",
    "R16-03 REJECTED (N4-V3 volume MIRROR keep prior-day "
    "rvol < 1.0; fails a + b + c + e)",
    "R16-04 AUDIT (P2F volume MIRROR NOT RUN — frozen WS3 "
    "condition unmet: no banking, no single-leg near-miss)",
    "R16-05 AUDIT (WS4: no bankings; stack prices restated "
    "exactly on the unchanged ending book; neither "
    "rejection flagged — more than two failed legs)",
    "R16-06 AUDIT (December freeze addendum — book "
    "unchanged — regeneration-verified; finalise)",
]
st["consecutive_no_bank"] = 2
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round16_summary, incumbent -> r16 CSVs, "
      "6 cycles, flags unchanged (28), "
      f"cycles_completed total {len(st['cycles_completed'])}")

for yr in (2025, 2026):
    print(yr, "JO", sc[yr]["jan_oct_total"], "trades",
          sc[yr]["jan_oct_trades"], "ex_top3 full",
          sc[yr]["ex_top3_stocks"], "months", sc[yr]["months"])
print("finalise done.")
