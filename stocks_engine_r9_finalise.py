#!/usr/bin/env python3
"""ROUND 9 — FINALISE (R9-09): WS4 combinations close by
statement (zero Round-9 bankings — R9-05 rejected on eight legs,
R9-07 on (e) alone; R9-02/03/04 and R9-08 are decision support
by construction); ending books exported and independently
re-summed; flagged list and stack prices restated on the ending
book; state updated.

HEADLINE OF THE ROUND: two stack forms PASS ALL TEN LEGS —
R9-04 (NE-REV-NOTCH+UPGUARD slot): 2025 JO Rs1,19,813.44;
R9-08 (NE-REV-IDXCELL slot): 2025 JO Rs1,13,146.38. Both are
recorded as decision support (force_no_bank): adopting a stack
remains Chandu's act, now at a fully-gated price.
"""
import sys, json, csv
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r9_lib as R9

books = R9.load_books()
JO = {yr: R9.jo(books, yr) for yr in (2025, 2026)}
assert JO == {2025: 78420.04, 2026: 229696.21}, JO

# ------------------------------------------- export + re-sum ---
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_r9_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in books[yr]:
            w.writerow({**{k: t[k] for k in FIELDS[:-1]},
                        "net": f"{t['net']:.2f}"})
    chk = FL.load(f"stocks_engine_r9_book{yr}_trades.csv")
    jo = round(sum(t["net"] for t in chk
                   if t["date"] <= f"{yr}-10-31"), 2)
    assert jo == JO[yr] and len(chk) == len(books[yr]), (yr, jo)
    print(f"r9 book {yr}: exported {len(chk)} rows, re-sum JO "
          f"{jo} — verified identical to the starting book")

R9.record_audit(
    "R9-09",
    "WS4 combinations of Round-9 bankings — closes by "
    "statement; finalise",
    "Round 9 banked ZERO candidates (R9-05 ATH rejected on "
    "eight legs; R9-07 IDXCELL rejected on (e) alone; R9-02 / "
    "R9-03 / R9-04 / R9-08 are decision support by "
    "construction). With no bankings there is no combination "
    "to re-gate. Ending books exported to the r9 CSVs and "
    "independently re-summed to the paisa (2025 JO 78,420.04 / "
    "887 rows; 2026 JO 2,29,696.21 / 969 rows — the starting "
    "book unchanged). Flagged list and stack prices restated "
    "on the ending book in the state file and the Round-9 "
    "report.",
    extra={"banked_round9": 0})

# ------------------------------------------------ state update -
st = json.load(open(f"{WS}/stocks_engine_state.json"))
st["round9_summary"] = {
    "date": "2026-11-02",
    "gated_candidates": 2,
    "decision_support": 4,
    "audits": 3,
    "banked": 0,
    "voided_rows": 0,
    "report": "stocks_engine_round9_2026-11-02.md",
    "evidence": "r9_results.json",
    "ending_book": "2025 JO 78,420.04; 2026 JO 2,29,696.21 "
                   "(unchanged from Round 8 — zero bankings)",
    "workstreams": {
        "WS0_flip_decomposition":
            "R9-01 audit: BOTH max-stack flips belong to "
            "NE-REV-CERT alone — Jan 2025 delta -2,950.92 (66 "
            "rows, all DOWN-cell; the wound's address is "
            "DOWN x NIFTY-shallow-dip (-0.30%,0): -5,192.36 of "
            "it) and Dec 2025 delta -1,840.62 (6 rows, all "
            "UP-cell). R2-26 / R5-03-clean / R7-03 contribute "
            "+64.16 / -29.01 / 0.00 to Jan and +532.91 / 0 / 0 "
            "to Dec",
        "WS1_stack_minus_flaw":
            "R9-02 Variant A (NOTCH slot): 2025 JO 1,27,134.02 "
            "/ 2026 JO 2,44,461.23 — fails (f) Dec only, and is "
            "worth MORE than the unconditioned stack. R9-03 "
            "Variant B (UPGUARD slot): 1,15,155.58 / "
            "2,50,060.98 — fails (e)+(f). R9-04 Variant C "
            "(NOTCH+UPGUARD slot): 1,19,813.44 / 2,47,178.79 "
            "— PASSES ALL TEN LEGS (decision support; the "
            "clean-adoption price: Rs11,981.34/mo, gap "
            "Rs30,186.56)",
        "WS2_ath":
            "R9-05 ATH-PROXIMITY rejected on eight legs "
            "(standalone -21,322.97 / -27,329.31; 342 trades): "
            "buying 52-week-high proximity loses in both years "
            "on the home 25 — the follow family stays closed",
        "WS3_idx_repair":
            "R9-06 audit: IDX December = 3 UP-cell rows "
            "(-2,046.64). R9-07 NE-REV-IDXCELL standalone "
            "rejected on (e) ONLY (no flips; 2025 JO "
            "82,452.55, 2026 JO 2,64,065.70) — flagged. R9-08 "
            "stack with IDXCELL slot: 1,13,146.38 / "
            "2,57,803.88 — PASSES ALL TEN LEGS (decision "
            "support; second clean stack price)",
        "WS4_combinations":
            "none — zero bankings (R9-09 closes by statement)",
    },
}
new_flags = [
    {"id": "R9-04-STACK-NU",
     "candidate": "MAX STACK with NE-REV-NOTCH+UPGUARD in the "
                  "NE-REV slot (R2-26 + R5-03-clean + "
                  "NE-REV-NU + R7-03), gated whole at R9-04",
     "failed_legs": [],
     "note": "DECISION SUPPORT — PASSES ALL TEN LEGS. The "
             "clean-adoption price of the stack: adoption on "
             "the R9 book -> 2025 JO Rs1,19,813.44 "
             "(Rs11,981.34/mo; gap Rs30,186.56), 2026 JO "
             "Rs2,47,178.79. NOTCH cures the Jan flip (stack "
             "Jan +4,476.90), UPGUARD cures the Dec flip "
             "(stack Dec +1,946.88). Supersedes "
             "R8-MAXSTACK-GATED as the headline stack decision; "
             "not additive with any single flag (it contains "
             "one NE-REV form)",
     "delta_2025_jan_oct": 41393.40,
     "delta_2026_jan_oct": 17482.58},
    {"id": "R9-02-STACK-NOTCH",
     "candidate": "MAX STACK with NE-REV-NOTCH in the NE-REV "
                  "slot, gated whole at R9-02",
     "failed_legs": ["f_no_green_month_flips"],
     "note": "DECISION SUPPORT — fails (f) on the Dec flip "
             "only (Jan cured). Adoption -> 2025 JO "
             "Rs1,27,134.02 (the highest 2025 stack price), "
             "2026 JO Rs2,44,461.23. Worth more than the "
             "unconditioned R8-MAXSTACK on 2025 and combined. "
             "Alternative stack form — never additive with "
             "R9-04 / R9-08 / R8-MAXSTACK-GATED",
     "delta_2025_jan_oct": 48713.98,
     "delta_2026_jan_oct": 14765.02},
    {"id": "R9-08-STACK-IDXCELL",
     "candidate": "MAX STACK with NE-REV-IDXCELL in the "
                  "NE-REV slot, gated whole at R9-08",
     "failed_legs": [],
     "note": "DECISION SUPPORT — PASSES ALL TEN LEGS (stack "
             "Jan +1,807.31, Dec +1,740.86). Adoption -> 2025 "
             "JO Rs1,13,146.38 (Rs11,314.64/mo; gap "
             "Rs36,853.62), 2026 JO Rs2,57,803.88 (the "
             "highest 2026 stack price). Alternative stack "
             "form — never additive with R9-04 / R9-02",
     "delta_2025_jan_oct": 34726.34,
     "delta_2026_jan_oct": 28107.67},
    {"id": "R9-03-STACK-UPGUARD",
     "candidate": "MAX STACK with NE-REV-UPGUARD in the "
                  "NE-REV slot, gated whole at R9-03",
     "failed_legs": ["e_extop3", "f_no_green_month_flips"],
     "note": "DECISION SUPPORT — Dec cured, Jan flip remains "
             "and (e) fails in the stack. Adoption -> 2025 JO "
             "Rs1,15,155.58, 2026 JO Rs2,50,060.98. Dominated "
             "by R9-04 as a stack form; recorded for "
             "completeness",
     "delta_2025_jan_oct": 36735.54,
     "delta_2026_jan_oct": 20364.77},
    {"id": "R9-07-IDXCELL",
     "candidate": "NE-REV-IDXCELL (R8-05 IDX rows restricted "
                  "to DOWN+FLAT regime cells)",
     "failed_legs": ["e_extop3"],
     "note": "fails (e) only; NO month flips (the December "
             "repair holds by construction — the form carries "
             "no Dec-2025 rows). Adoption on the R9 book -> "
             "2025 JO Rs82,452.55, 2026 JO Rs2,64,065.70. "
             "NE-REV-family alternative — not additive with "
             "R5-07 / R5-07-CERT / R8-05 / R6-02 / R6-04 / "
             "R7-06",
     "delta_2025_jan_oct": 4032.51,
     "delta_2026_jan_oct": 34369.49},
]
ids = {e["id"] for e in st["flagged_awaiting_chandu"]}
st["flagged_awaiting_chandu"] += [e for e in new_flags
                                  if e["id"] not in ids]
for e in st["flagged_awaiting_chandu"]:
    if e["id"] == "R8-MAXSTACK-GATED":
        e["note"] += (" Round-9 restatement: still fails (f) "
                      "only at 2025 JO Rs1,23,231.11; the "
                      "all-legs-pass forms are R9-04-STACK-NU "
                      "(Rs1,19,813.44) and R9-08-STACK-IDXCELL "
                      "(Rs1,13,146.38) — the (f) failure now "
                      "has two fully-gated cures priced.")
st["current_incumbent"]["book_2025_csv"] = \
    "stocks_engine_r9_book2025_trades.csv"
st["current_incumbent"]["book_2026_csv"] = \
    "stocks_engine_r9_book2026_trades.csv"
st["current_incumbent"]["book_id"] = (
    "R9-FINAL = R8-FINAL unchanged (Round 9 banked nothing; "
    "exports verified identical to the starting book by re-sum)")
st["updated"] = ("2026-11-02 (Round 9 complete: 2 gated "
                 "candidates + 4 decision-support gates + 3 "
                 "audits, 0 banked, book unchanged; two stack "
                 "forms pass all ten legs as decision support)")
json.dump(st, open(f"{WS}/stocks_engine_state.json", "w"),
          indent=1)
print("state updated: round9_summary + 5 flagged entries "
      "(21 total)")
print("WS4/finalise done.")
