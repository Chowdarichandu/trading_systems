#!/usr/bin/env python3
"""ROUND 11 — WS5 combinations + stack-price maintenance +
finalise (R11-08).

Bankings: R11-03 (cross-family pair NU + REXP-DOWN) BANKED.
R11-02 rejected on (e) only; R11-04 and R11-06 closed by
statement (no candidate). The WS5 union is therefore the
pair alone — re-gated whole-book here against the starting
book as the combination record. Ending book = starting book
+ NE-REV-NU rows + REXP-DOWN (T100/S065) rows.
Stack prices restated on the ending book by the generalised
method: apply the R2-26 and R5-03 swaps, strip every
NE-REV-family / REXP row the ending book now carries, then
apply the stack's own slot + REXP (T125/S050) rows — the
resulting stack books must equal the recorded Round-9/10
stack books exactly, and the adoption value is stated from
the ending book. Ending books exported and independently
re-summed; state updated.
"""
import sys, csv, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r11_lib as R11
import stocks_engine_r9_ingredients as ING
import stocks_engine_r8_builders as B8
import stocks_engine_floor_lib as FL

res = {r["cycle"]: r for r in json.load(open(f"{WS}/r11_results.json"))}
assert res["R11-03"]["banked"] is True
assert res["R11-02"]["banked"] is False
assert res["R11-02"]["legs"]["e_extop3"] is False

books = R11.load_books()
ing = ING.build_all()
cond = ING.build_cond()
nu = cond["notchup"]["real"]
rexp, rexp_f, rexp_l, viol_r = B8.rexp_geo(
    "SHORT", cells={"DOWN"}, tgt=1.00, stp=0.65)
assert viol_r == 0

def add2(bk, a, b):
    out = R11.add_comp(bk, a[2025][0]["comp"], a)
    return R11.add_comp(out, b[2025][0]["comp"], b)

ending = add2(books, nu, rexp)
pl = [R11.full_total(add2(books, cond["notchup"]["flip"], rexp_f)),
      R11.full_total(add2(books, cond["notchup"]["late"], rexp_l))]
out = R11.gate(books, ending, pl, timing_violations=viol_r)
assert out["verdict"], out["legs"]
R11.record_audit(
    "R11-08",
    "WS5 combinations + stack-price maintenance + finalise",
    f"Union of Round-11 bankings = the R11-03 pair alone "
    f"(R11-02 rejected; R11-04 / R11-06 produced no "
    f"candidate). Re-gated whole-book: verdict PASS (2025 "
    f"JO {out['var']['2025']['jan_oct']}; 2026 JO "
    f"{out['var']['2026']['jan_oct']}; combined "
    f"{out['sums']['variant_combined']}) — identical to the "
    f"R11-03 gate, as it must be. Ending book exported to "
    f"stocks_engine_r11_book{{2025,2026}}_trades.csv and "
    f"independently re-summed. Stack prices restated on the "
    f"ending book (see below).",
    extra={"union_verdict": True})

# ------------------------------------------- stack restate --
def strip_families(bk):
    return {yr: [t for t in bk[yr]
                 if not t["comp"].startswith("NE-REV")
                 and t["comp"] != "REXP"]
            for yr in (2025, 2026)}

base = strip_families(ING.apply_r503(
    ING.apply_r226(ending, ing), ing))

def stack_jo(slot_rows):
    out = R11.add_comp(base, slot_rows[2025][0]["comp"],
                       slot_rows)
    out = R11.add_comp(out, "REXP", ing["rexp"])
    return {yr: R11.jo(out, yr) for yr in (2025, 2026)}

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
end_jo = {yr: R11.jo(ending, yr) for yr in (2025, 2026)}
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
    path = f"{WS}/stocks_engine_r11_book{yr}_trades.csv"
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

# freeze addendum: the pair banked after the freeze was cut
with open(f"{WS}/stocks_engine_banked_book_FREEZE_dec2026.md",
          "a") as f:
    f.write(
        "\n## ADDENDUM (R11-08, same day) — the ending book\n"
        "After this freeze was cut, Round 11 banked the "
        "cross-family pair (R11-03): the book judged in "
        "December is the frozen book above PLUS two frozen "
        "constructions — NE-REV-NU (NOTCH+UPGUARD conditioned "
        "NE-REV LONG, signal 10:25 / entry 10:35, thr 2.0%, "
        "T100/S065, certified non-event population) and "
        "REXP-DOWN (range-expansion SHORT in DOWN regime "
        "cells, entry 10:20, T100/S065) — both reproduced "
        "from their Round-8/9 anchored builders at banking "
        "time with 0 timing violations. Ending book: 2025 "
        f"Jan-Oct {end_jo[2025]} on "
        f"{len(ending[2025])} rows; 2026 Jan-Oct "
        f"{end_jo[2026]} on {len(ending[2026])} rows. The "
        "December pass/kill lines above apply to the ending "
        "book as a whole.\n")

# ------------------------------------------------------ state ---
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round11_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 2,
    "decision_support": 1,
    "audits": 5,
    "banked": 1,
    "voided_rows": 0,
    "report": "stocks_engine_round11_2026-11-02.md",
    "evidence": "r11_results.json",
    "ending_book": "2025 JO 99,363.06; 2026 JO 2,47,540.89 "
                   "(R11-03 pair banked)",
    "workstreams": {
        "WS1_hard_dip": "R11-02 REJECTED on (e) only: "
            "removing INV-ABOVE hard-dip rows raises both "
            "years (2025 JO -> 80,171.76; 2026 JO -> "
            "2,33,708.39; combined +5,242.80, no flips, "
            "placebos beaten) but the removed losses sit in "
            "the book's carrier names, so ex-top-3 falls. "
            "Flagged as an owner decision.",
        "WS2_pair": "R11-03 BANKED: NE-REV-NU + REXP-DOWN "
            "(T100/S065) — the (e)-only failure and the "
            "(c)-only failure cure each other assembled. "
            "2025 JO -> 99,363.06 (+20,943.02); 2026 JO -> "
            "2,47,540.89 (+17,844.68); all ten legs pass. "
            "R11-04 substitution not triggered.",
        "WS3_anatomy": "R11-05: NU's (e) failure is a 2026 "
            "name-concentration fact — 2026 NU profit inside "
            "the top-3 +34,926.51 (TVSMOTOR 18,734.26 / "
            "OBEROIRLTY 11,376.19 / ASTRAL 4,816.06) while "
            "OUTSIDE the top-3 NU 2026 loses -11,182.11 "
            "(UNITDSPR -10,762.92 the largest). 2025 ex-top-3 "
            "rises +571.69. Separator test: 0 qualifying "
            "state slices — R11-06 closes by statement.",
        "WS4_freeze": "R11-07: banked book frozen in "
            "writing (stocks_engine_banked_book_FREEZE_"
            "dec2026.md) with per-feature timing "
            "certification; regeneration identity PASSED "
            "row-for-row and to the paisa; December pass/"
            "kill lines pre-registered. R11-08 addendum "
            "extends the freeze to the ending book.",
        "WS5": "R11-08: union = the pair alone, re-gated "
            "PASS. Stack totals reproduced exactly on the "
            "ending book; adoption values restated from the "
            "ending book (unconditioned +23,868.05 / +6.36; "
            "A +27,770.96 / -3,079.66; C +20,450.38 / "
            "-362.10; IDXCELL +13,783.32 / +10,262.99).",
    },
}
st["current_incumbent"] = {
    **st["current_incumbent"],
    "book_2025_csv": "stocks_engine_r11_book2025_trades.csv",
    "book_2026_csv": "stocks_engine_r11_book2026_trades.csv",
    "book_id": "R11-FINAL (R11-03 cross-family pair banked "
               "on the R10 book; exports verified by re-sum)",
    "floor_status": {
        "2025": "NOT MET - Rs99,363.06 (Rs9,936.31/mo), "
                "gap Rs50,636.94",
        "2026": "MET - Rs2,47,540.89 (Rs24,754.09/mo)",
    },
    "jan_oct_2025": 99363.06,
    "jan_oct_2026": 247540.89,
    "total_2025_full": 99880.95,
    "total_2026_full": 247540.89,
    "trades_2025": 1128,
    "trades_2026": 1368,
}
st["cycles_completed"] += [
    "R11-01 AUDIT (starting-book re-verification + INV-ABOVE "
    "state census: R10-05 bucket nets reproduced exactly; "
    "unknown 0)",
    "R11-02 REJECTED (INV-ABOVE hard-dip exclusion; fails e "
    "only — flagged)",
    "R11-03 BANKED (cross-family pair NE-REV-NU + REXP-DOWN "
    "T100/S065; all ten legs pass)",
    "R11-04 AUDIT (NOTCHCELL substitution closes by "
    "statement — trigger not met, pair banked)",
    "R11-05 AUDIT (leg-(e) anatomy of NU standalone: 2026 "
    "concentration fact; UNITDSPR -10,762.92 outside top-3)",
    "R11-06 AUDIT (conditioned NU variant closes by "
    "statement — 0 qualifying separators)",
    "R11-07 DECISION-SUPPORT (December freeze of the banked "
    "book; regeneration identity passed; pass/kill lines "
    "pre-registered)",
    "R11-08 AUDIT (WS5 combinations: union = the pair, "
    "re-gated PASS; stack prices restated on the ending "
    "book)",
]
st["flagged_awaiting_chandu"] += [
    {"id": "R11-02", "candidate": "INV-ABOVE hard-dip "
     "exclusion (remove INV-ABOVE rows on hard-dip "
     "index-state mornings)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; both years rise, no flips, "
             "placebos beaten. Adoption on the R11 starting "
             "book -> 2025 JO Rs80,171.76, 2026 JO "
             "Rs2,33,708.39 (combined +5,242.80). A removal — "
             "composes disjointly with the banked pair.",
     "delta_2025_jan_oct": 1751.72,
     "delta_2026_jan_oct": 4012.18},
]
st["consecutive_no_bank"] = 0
st["iteration"] = 48
st["updated"] = "2026-11-02"
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round11_summary, incumbent -> r11 CSVs, "
      "8 cycles, 1 new flagged entry (25 total)")

for yr in (2025, 2026):
    sc = FL.scorecard(ending[yr], yr)
    print(yr, "JO", sc["jan_oct_total"], "trades",
          sc["jan_oct_trades"], "ex_top3 full",
          sc["ex_top3_stocks"], "months", sc["months"])
print("finalise done.")
