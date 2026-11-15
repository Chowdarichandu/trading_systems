# STOCKS REPAIR — SPEC (FROZEN AFTER ANATOMY, BEFORE ANY GATE SCORING)

Frozen: 2026-11-14 (IST), after Step-1 anatomy (`stocks_repair_anatomy.py`
/ `stocks_repair_anatomy.json`), before any repair gate is scored.
Owner's order: 2026-11-14 12:08 IST — stocks to get the same three-lines
treatment as Bank/Nifty (RAW · +REPAIR · +CONFIDENCE). The Stock Book has
never had a repair; this run builds it by the books-fix method.
Research only — no book, ledger, or job is changed.

**BASIS (labelled on every figure): equity cash intraday, per 100 shares
PROVISIONAL, ₹40/trade, paper only, real ₹0. Years judged SEPARATELY —
stocks are never pooled for a verdict (pooled figures are anatomy
description only).**

## Book and CONTROL (reproduced exactly in anatomy; run stops on any miss)
Gated store: `stocks_engine_adoptedC_book{2025,2026}_trades.csv`, Jan–Oct
only (2025 file's Nov–Dec rows excluded — outside the adopted window).
Fields per leg: comp, date, stock, dir, entry_time, net.
- 2025: **1,064 legs · +₹119,813.44 · WR 45.39% · red months Jul, Oct**
- 2026: **1,363 legs · +₹247,178.79 · WR 44.75% · zero red months**
- November actual (paper log, Nov 2–13): **+₹7,517.94 · 32 trades**

## Anatomy audit — dimensions
Carried by the gated store and knowable at entry: **component × side ×
entry-time bucket**. Buckets (frozen): **B1 ≤09:35** (open wave) ·
**B2 09:40–10:25** · **B3 ≥10:30** (second wave; this book enters almost
entirely before 11:00, so the index books' pre-11:00 buckets do not apply).
NOT carried → dropped, stated: **prior-day-move band** (not in the store;
per-stock daily bars cannot uniformly reconstruct it across both years —
the same ruling as the confidence run) and **price band** (entry price is
not in the gated store; the partial store that carries it joins only 39%
of legs). Exit class is not entry-knowable — never a slice for a rule.

## The candidates (at most two — frozen here; no third will be tried)
Anatomy screen: cells net-negative in a year, ≥15 legs in a year (or ≥25
pooled), ex-top-3 also negative (negativity is broad, not one trade).
Only TWO cells in the whole cross are pooled-negative, and both are the
INV components' open wave:
- **S-FIX-1 — skip INV-ABOVE legs with entry_time ≤ 09:35 (B1).**
  2025: 30 legs, −₹4,100.03, WR 33.33%, ex-top-3 −₹10,764.68 ·
  2026: 4 legs, +₹2,572.66, WR 75.00% · pooled 34 legs −₹1,527.37.
  (All INV-ABOVE B1 legs are LONG; the rule is stated on comp × bucket,
  side is not a condition.)
- **S-FIX-2 — skip INV-LONG legs with entry_time ≤ 09:35 (B1).**
  2025: 55 legs, −₹2,635.88, WR 38.18%, ex-top-3 −₹8,296.70 ·
  2026: 30 legs, +₹1,289.99, WR 30.00% (ex-top-3 −₹7,477.50 — its 2026
  profit is ≤3 trades deep) · pooled 85 legs −₹1,345.89.
Knowable at entry: component and entry time are the leg's own signal
fields, fixed at the entry moment. No post-entry information.

Named and NOT chosen (anatomy rejects them before the gate): **REXP**
(2026 −₹8,399.33/86 legs but 2025 +₹14,870.39 — a year-flip, skipping it
would degrade 2025 by 12.4%) and **F4 × SHORT** (2025 −₹5,090.70/110 legs
but 2026 +₹55,706.05 — the book's 2026 engine; skipping it would degrade
2026 by 22.5%). Both fail gate leg (a) by inspection; freezing them as
candidates would waste the two slots. Recorded here so the choice is
auditable.

## GATE (per candidate, per year — all legs frozen, before scoring)
(a) **Cross-year:** repaired total IMPROVES on raw in at least one year,
    and the other year's total does not degrade by more than 2% of that
    year's raw total (2025 tolerance ₹2,396.27; 2026 tolerance ₹4,943.58).
(b) **Red months:** no NEW red month in either year (a month raw ≥ 0
    turning < 0 after repair). Raw red set: 2025 {Jul, Oct}; 2026 {}.
(c) **Placebo (each improved year):** 200 random skip-sets of the same
    leg count k as the rule skips in that year (seeds 2000–2199, uniform
    without replacement). The repaired year's total must exceed ≥ 95% of
    the 200 placebo totals.
(d) **Halves (stated plainly, with this frozen tolerance):** halves are
    Jan–May / Jun–Oct. A candidate fails (d) if any half in any year
    drops below its raw half by more than 2% of that year's raw total.
(e) **November (descriptive, NOT pass/fail):** the rule applied to the
    32 November paper-log trades (comp and entry_time are carried in
    `stocks_sarvaritu_paper_log.csv`; no volume factor is used, so no
    UNSCORED trades arise). Report skipped legs and the repaired
    November total against actual +₹7,517.94.
A candidate failing ANY of (a)–(d) = FAIL, reported with its anatomy.
No iteration to further candidates in this run.

## Table selection rule (frozen)
For the three-lines month table's "+ REPAIR" column: if exactly one
candidate passes, it is the column. If both pass, the column is the one
with the larger pooled Jan–Oct improvement (the other is reported as
also-passed). If none passes, the column is the candidate with the
larger pooled Jan–Oct improvement, labelled FAILED in the table and
report.
