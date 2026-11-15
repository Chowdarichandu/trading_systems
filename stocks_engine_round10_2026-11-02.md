# Stocks (SarvaRitu) Engine — ROUND 10 · NE-REV conditioned forms standalone, July wound under the index-state lens, stack-price maintenance
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-6/7/8/9 ending book, causality-audited): 2025 Jan–Oct **+₹78,420.04** (₹7,842.00/mo; gap ₹71,579.96) · 2026 Jan–Oct **+₹2,29,696.21** (₹22,969.62/mo; floor MET). Re-verified by independent re-sum of the Round-9 exported CSVs in R10-01 before any Round-10 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round: a condition may reference state (index level/move, regime cell, price bands), never the calendar.**
- **Flagged, NOT adopted** (Chandu's calls; baselines stay on the book without them): all 21 Round-9 flagged entries, incl. the four stack forms (unconditioned R8-02; A R9-02; C R9-04 — passes all ten legs as decision support; IDXCELL R9-08 — passes all ten legs as decision support). Round 10 adopts nothing on Chandu's behalf; its bankable candidates are standalone ingredients gated on the banked book.

---

## PRE-REGISTRATION (written before any Round-10 candidate is scored; R10-01's audits are completed before the gates they inform)

### R10-01 — Starting-book verification + WS2 admission-rule algebra (audit)
The starting books are re-summed from `stocks_engine_r9_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹78,420.04 / 887 rows; 2026 JO ₹2,29,696.21 / 969 rows). The audit also verifies, in code, the row-set relations among the frozen NE-REV admission rules on the CERT population (291/370 rows):
- IDX admits rows with NIFTY 10:25 move ≤ −0.30% — every such row automatically satisfies NOTCH (move ∉ (−0.30%, 0)); hence IDXCELL ⊆ IDX ⊆ NOTCH-admissible.
- NU = NOTCH ∩ UPGUARD. Therefore the literal set-combinations of {IDXCELL, NOTCH} collapse: ∩ = IDXCELL (already gated standalone, R9-07) and ∪ = NOTCH (gated standalone in R10-03). Re-scoring either would re-run a Round-9 cell, which the round brief forbids.
- The one mechanically distinct composed form is frozen here for WS2: **NE-REV-NOTCHCELL** — CERT rows admitted iff NOTCH passes **and** the trade day's frozen regime cell ∈ {DOWN, FLAT} (IDXCELL's cell restriction composed with the notch on the CERT population, instead of on the IDX sub-population). It is distinct from IDXCELL (which additionally requires move ≤ −0.30%) and from NU (which keeps UP-cell rows whose move ≥ 0).

### WS1 — Conditioned NE-REV forms standalone (R10-02, R10-03 — bankable)
Round 9 gated these exact ingredient rows only as stack slots. Here they are gated as whole-book additions to the banked book, rows verbatim from the anchored Round-9 builds (`stocks_engine_r9_ingredients.build_cond`), placebos = the whole book plus the **flipped (SHORT)** rows / the **one-bar-late** rows under the identical conditions (the R9-07 convention), timing violations = the CERT build's counted violations (asserted 0; the conditions are date-level state from the 10:25 bar, which completes at 10:30 < every 10:35 entry):
- **R10-02 — NE-REV-NU standalone** (NOTCH+UPGUARD rows, comp `NE-REV-NU`; Round-9 standalone prices +₹12,596.19 / +₹23,744.40 on 200/313 rows).
- **R10-03 — NE-REV-NOTCH standalone** (NOTCH rows, comp `NE-REV-NOTCH`; Round-9 standalone prices +₹18,618.88 / +₹21,026.84 on 262/332 rows).

### WS2 — Composed form standalone (R10-04 — bankable)
**NE-REV-NOTCHCELL** as frozen in R10-01, built by filtering the anchored CERT / flipped / late rows on the composed date-level condition (state-unknown dates counted and never admitted). Placebos and timing as in WS1.

### WS3 — July wound under the index-state lens (R10-05 audit; R10-06 conditional gate)
- **State definition (frozen):** for a book row with entry time T on day D, the index state is `nifty_move(D, T−5min)` — the % move of the close of the last 5-min NIFTY bar completing at the entry instant vs D's prior close — bucketed as in R9-01: **hard-dip ≤ −0.30% · shallow-dip (−0.30%, 0) · up/flat ≥ 0**. A row whose state is unknown (no such bar, e.g. a 09:15 entry) is counted and attributed to no bucket — never guessed, and never removed by any variant.
- **R10-05** decomposes every July-2025 row of the banked book (month net asserted = −₹7,083.39) by component × state bucket.
- **Separator test (frozen, applied to the audit output before any variant is designed):** the offending component is the one carrying the largest July-2025 loss. A bucket is a separator for that component iff **(i)** its July net < 0 and |bucket net| ≥ 50% of |component July net|; **(ii)** the component's full-year 2025 net inside the bucket < 0; **(iii)** the component's combined (2025+2026) net inside the bucket < 0. If **exactly one** (component, bucket) qualifies, R10-06 gates ONE variant; otherwise WS3 closes with no candidate.
- **R10-06 (conditional) — removal variant:** the banked book minus the separator (component × bucket) rows in both years. Placebos (frozen): **P1 chrono** — the same per-year count of the same component's rows removed, earliest first, any bucket; **P2 cross-bucket** — the same per-year count of the same component's rows removed from the other two buckets, earliest first (shortfalls made up from the separator bucket's earliest rows). Timing violations 0: removal uses only the state knowable at each row's entry instant, asserted per removed row in code.

### WS4 — Stack-price maintenance (R10-08, decision support)
The four stack prices (unconditioned R8-02 · A R9-02 · C R9-04 · IDXCELL-slot R9-08) are restated on the ending book: each stack form is rebuilt on the ending book with its NE-REV slot's rows deduplicated against any banked NE-REV-family rows already present (row identity = date/stock/dir/entry_time/net), and the adoption value is stated as (stack-on-ending total − ending total) per year, method stated. Stack forms remain alternatives to each other and to the single flags — never additive.

### WS5 — Combinations (R10-07)
Standalone candidates are each gated against the **starting** book (the Round-9 convention). The NE-REV forms are nested/overlapping alternatives (NU ⊂ NOTCH; NOTCHCELL ⊂ NOTCH; NU ∪ NOTCHCELL ⊊ NOTCH), so bankings are resolved here: the union of all passing additions (deduplicated by row identity) is re-gated whole-book against the starting book; if the union passes, it banks; if the union fails while a single form passed, the single passing form with the highest combined total banks and the union's failure is recorded. A July removal banking (R10-06) composes with NE-REV additions disjointly (different rows) and is included in the same re-gate when both exist. If nothing passes, WS5 closes by statement.

### Verdict rule (frozen for all Round-10 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS5 resolution for overlapping NE-REV forms). A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## WS1 — CONDITIONED NE-REV FORMS STANDALONE (R10-01 … R10-03)

**R10-01 — AUDIT (passed, all assertions in code).** Starting books
re-summed independently from the Round-9 CSVs: 2025 887 rows, JO
₹78,420.04, full ₹77,041.31; 2026 969 rows, JO ₹2,29,696.21 — exact vs
the recorded totals. Admission-rule algebra on CERT (291/370 rows):
IDXCELL (139/233) ⊆ IDX (201/252) ⊆ CERT; every IDX row verified per-row
to carry NIFTY 10:25 move ≤ −0.30% (0 violations), hence IDX ⊆ NOTCH
(262/332); NU's row set == NOTCH ∩ UPGUARD exactly in both years. The
literal {IDXCELL, NOTCH} combinations collapse to already-gated forms —
the distinct composed form is NE-REV-NOTCHCELL (R10-04).

**R10-02 — NE-REV-NU standalone: REJECTED, on leg (e) ONLY.** Whole-book
2025 JO ₹78,420.04 → **₹89,119.61**; 2026 JO ₹2,29,696.21 →
**₹2,53,440.61**; combined ₹3,06,737.52 → ₹3,43,078.11. All other legs
pass: no flips, halves hold, cells hold, placebos beaten (flipped book
₹2,97,159.39; late book ₹2,91,396.83), timing 0, leg (x) holds. The
ex-top-3 total still falls (₹1,01,181.87 → ₹92,637.71) — the sleeve's
₹12,596.19 of 2025 money is concentrated in the same names the book
already leans on. **The Variant-C ingredient does NOT pass standalone;
inside the stack it passed because the stack supplies the breadth.**
Joins the flagged list as an owner decision at a different price
(standalone adoption → 2025 JO ₹89,119.61).

**R10-03 — NE-REV-NOTCH standalone: REJECTED on (e) + (f).** Whole-book
2025 JO → **₹96,440.19**; 2026 JO → **₹2,50,723.05**; combined →
₹3,46,383.24. December 2025 flips to −₹632.67 without the UP-guard —
the same wound the stack slot showed in R9-02, now confirmed as a
property of the population, not the context. Ex-top-3 falls to
₹82,713.68. Joins the flagged list (standalone adoption → 2025 JO
₹96,440.19, the largest 2025 standalone price of the family).

## WS2 — THE COMPOSED FORM (R10-04)

**R10-04 — NE-REV-NOTCHCELL standalone: REJECTED, on leg (e) ONLY.**
CERT rows in DOWN/FLAT cells with the shallow-dip notch: 2025 JO →
**₹84,986.53**; 2026 JO → **₹2,56,909.60** (the family's best 2026);
combined → ₹3,40,517.40. No flips; placebos beaten (flipped
₹2,98,772.13; late ₹2,91,032.09); timing 0. Distinctness verified in
code (IDXCELL a proper subset; row set ≠ NU's). Same single barrier:
ex-top-3 ₹88,800.38. Joins the flagged list.

> WS1+WS2 verdict in one line: every conditioned NE-REV form is now
> gated standalone; the family fails standalone on concentration
> alone (NOTCH additionally on December). No conditioned variant of
> this population remains ungated — the family's routes are the
> stack slot (gated, Round 9) or owner adoption (flagged, three
> standalone prices + four stack prices).

## WS3 — JULY WOUND UNDER THE INDEX-STATE LENS (R10-05, R10-06)

**R10-05 — AUDIT.** July 2025 = −₹7,083.39 on 33 rows (asserted). By
component: INV-ABOVE **−₹2,473.45** (the offender) · N4-V3 −₹1,821.00 ·
GAP-FADE-INC −₹1,560.10 · F4 −₹1,025.28 · P2F −₹173.47 · P2F-R2
−₹170.85 · GAP-FADE +₹140.76. The July wound is diffuse across six
components, not one sleeve's blow-up. INV-ABOVE's July loss is 3 rows,
**all in the shallow-dip state bucket** (−₹2,473.45 = 100% of its July
net). Separator test on (INV-ABOVE, shallow): (i) July concentration
passes; (ii) FY-2025 bucket net −₹620.96 < 0 passes; **(iii) combined
two-year bucket net = +₹2,445.28 — FAILS** (2026 shallow rows earn
+₹3,066.24). No bucket qualifies.

**R10-06 — closes by statement: NO CANDIDATE.** The July wound's only
index-state address is a state that pays for itself across the two
years; removing it would buy a July patch with 2026 money — exactly
what the frozen test exists to refuse.

*Observation for a future round's pre-registration (untested, not a
candidate):* INV-ABOVE's **hard-dip** rows lose in both years
(FY-2025 −₹1,230.62; FY-2026 −₹4,012.18) but have zero July rows, so
the July-frozen test correctly stayed silent. A hard-dip-state
removal belongs in Round 11's pre-registration if pursued — never in
a same-round improvised gate.

## WS5 — COMBINATIONS (R10-07)

Closes by statement: Round 10 banked zero candidates, so there is no
union to re-gate. The round's output is three gated standalone prices
and one closed wound, not a banking.

## WS4 — STACK-PRICE MAINTENANCE (R10-08, decision support)

Ending book = starting book (zero bankings), exported to
`stocks_engine_r10_book{2025,2026}_trades.csv` and independently
re-summed to the paisa. All four stack prices restated by full rebuild
on the ending book (NE-REV slot dedupe vacuous — the book carries no
NE-REV rows; asserted) and reproduced **exactly**:

| Stack form | 2025 JO | 2026 JO | Gate state |
|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | fails (f), Dec only |
| Variant C — NOTCH+UPGUARD slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | **passes all ten legs** |

Adoption values are unchanged from Round 9. The stack forms remain
alternatives — never additive.

## ENDING PER-YEAR SCORECARD (banked book — unchanged from Round 9)

**2025:** JO **+₹78,420.04** on 842 trades (full year +₹77,041.31,
887) — **₹7,842/month vs the ₹15,000 floor; gap ₹71,579.96.** Months:
Jan +2,200.31 · Feb +20,242.66 · Mar +8,953.57 · Apr +39,749.43 ·
May +2,498.99 · Jun −955.92 · Jul −7,083.39 · Aug +11,173.48 ·
Sep +5,585.44 · Oct −3,944.53. Ex-top-3 +₹23,708.10. Cells (full
year): DOWN +42,941.63 / FLAT +21,250.68 / UP +12,849.00.

**2026:** JO **+₹2,29,696.21** on 969 trades — **₹22,970/month, floor
MET**, every month green, ex-top-3 +₹77,473.77.

## DECISION STATE after Round 10

- Banked book: unchanged. 2025 gap to floor: **₹71,579.96**.
- Round 10 banked: **0**. Cycles: 8 (3 gated candidates, 4 audits,
  1 decision-support restatement). Voided cells: **none**.
- The conditioned NE-REV family is now **fully mapped**: gated
  standalone prices — NU ₹89,119.61 (fails (e)), NOTCH ₹96,440.19
  (fails (e)+(f)), NOTCHCELL ₹84,986.53 (fails (e)); gated stack-slot
  prices — C ₹1,19,813.44 and IDXCELL ₹1,13,146.38 (both pass all ten
  legs), A ₹1,27,134.02 (fails (f) Dec only), unconditioned
  ₹1,23,231.11 (fails (f)). All seven are the owner's adoption
  decision; the flagged list now carries 24 entries.
- July 2025 is closed under the index-state lens: no separator
  exists. Its loss is diffuse (six components) with one state address
  that is a cross-year asset.
- Next-round leads (for pre-registration, untested): the INV-ABOVE
  hard-dip two-year loser (−₹1,230.62 / −₹4,012.18) as a removal
  candidate under the standard removal gate; July's other components
  (N4-V3 −₹1,821.00, GAP-FADE-INC −₹1,560.10 in July) under the same
  lens if the engine continues past the NE-REV family.
