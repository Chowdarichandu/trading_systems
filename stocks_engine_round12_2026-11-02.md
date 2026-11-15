# Stocks (SarvaRitu) Engine — ROUND 12 · hard-dip re-gate on the pair book, single-leg flag re-tests, October + July-residual wounds
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-11 ending book, the R11-03 cross-family pair banked): 2025 Jan–Oct **+₹99,363.06** (₹9,936.31/mo; gap ₹50,636.94; red Jan–Oct months Jul −₹2,101.93 / Oct −₹3,751.28) · 2026 Jan–Oct **+₹2,47,540.89** (₹24,754.09/mo; floor MET). To be re-verified by independent re-sum of `stocks_engine_r11_book{2025,2026}_trades.csv` in R12-01 before any Round-12 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round: a condition may reference state (index level/move, regime cell, price bands), never the calendar.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): all 25 flagged entries through Round 11, incl. the max stack, Variants A/C/IDXCELL, R2-26, and every standalone NE-REV form. Round 12 adopts nothing on Chandu's behalf; its bankable candidates are gated on the banked book.
- **Round 11's lesson (the round's premise):** the banked pair changed the book's breadth — combined ex-top-3 rose from ₹1,01,181.87 (pre-pair base) to ₹1,03,228.30 and the top-3 sets moved — so verdicts that turned on whole-book interaction legs may not survive contact with the new baseline, in either direction. Round 12 re-tests exactly that class, plus the two remaining red months.

---

## PRE-REGISTRATION (written before any Round-12 candidate is scored)

### R12-01 — Starting-book verification + INV-ABOVE state census (audit)
The starting books are re-summed from `stocks_engine_r11_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹99,363.06 / full ₹99,880.95 / 1,128 rows; 2026 JO ₹2,47,540.89 / full ₹2,47,540.89 / 1,368 rows; Jul 2025 −₹2,101.93; Oct 2025 −₹3,751.28). The audit also re-censuses every INV-ABOVE row by index-state bucket under the **frozen R10-05 state definition** — state = `nifty_move(date, entry_time − 5min)`, bucketed **hard-dip ≤ −0.30% · shallow-dip (−0.30%, 0) · up/flat ≥ 0** — and must reproduce R11-01's bucket nets exactly (the pair did not touch INV-ABOVE rows): 2025 hard 23 rows / −₹1,230.62 · shallow −₹620.96 · up +₹10,132.83; 2026 hard 16 rows / −₹4,012.18 · shallow +₹3,066.24 · up +₹4,295.15; unknown-state rows 0.

### WS1 — INV-ABOVE hard-dip exclusion, NEW BASELINE (R12-02 — bankable)
**Variant:** the Round-11 ending book minus every INV-ABOVE row whose state bucket (R12-01 definition) is **hard-dip**, in both years — the R11-02 construction verbatim, re-based. Unknown-state rows are never removed. R11-02 failed leg (e) **only, by ₹135.40 combined** (2025 ex-top-3 −₹1,269.78, 2026 +₹1,133.38), on a base whose combined ex-top-3 was ₹1,01,181.87; the pair book's is ₹1,03,228.30 with different carrier sets, and leg (e) is recomputed on the assembled book — the re-test is genuinely open.
**Placebos (frozen, the R10-06 removal convention):** **P1 chrono** — the same per-year count of INV-ABOVE rows removed, earliest first, any bucket; **P2 cross-bucket** — the same per-year count removed from the non-hard buckets (shallow + up), earliest first, shortfall from the hard bucket's earliest rows.
**Timing:** the bucketed bar completes exactly at each row's entry instant; asserted per removed row; violations counted and must be 0.

### WS2 — Single-leg flag re-tests (screening statement + R12-03 gate + R12-04 audit)
The flagged list's single-leg failures divide into two kinds. **Delta legs** — (b) 2025-no-fall and (c) 2026-no-fall compare the variant's year total against the base's; for a replacement or restriction, the sign of that difference is fixed by the ingredient's own rows versus the banked rows it displaces, on ANY baseline. No base change — the pair included — can cure a delta-leg failure. **Interaction legs** — (e) ex-top-3 and (f) month flips are recomputed on the assembled book (its top-3 sets, its month balances); these are the legs a new baseline can move. Screening the 25 flags against that distinction, in the pre-registration, before any scoring:
- **Every (c)-only flag is pre-refused, not scored:** R6-10 (REXP full population), R7-02 (REXP DOWN+FLAT), R7-03 / R8-07 (REXP-DOWN at T125/S050) each displace the banked REXP-DOWN T100/S065 leg (2026 −₹5,899.72) with a form whose 2026 net is more negative (−₹10,286.95 / −₹10,930.18 / −₹8,399.33); R8-06 (FADE-IDX) removes banked fade legs whose 2026 net is +₹2,477.24. Each variant's 2026 delta is negative by row identity — leg (c) fails arithmetically on the new baseline exactly as on the old. R12-04 prints this arithmetic per flag as the record.
- **Every NE-REV-slot alternative failing (e) only is pre-refused, not scored:** R6-02, R6-04, R9-07-IDXCELL, R10-04-NOTCHCELL are alternatives to the banked NE-REV-NU rows (same certified population lineage — never additive; adding any of them double-counts shared rows). As slot swaps against NU (standalone full-year +₹12,596.19 / +₹23,744.40), each one's 2025 standalone sits below NU's, so leg (b) fails arithmetically; the remaining slot form, NOTCH (R10-03, failing (e)+(f)), prices 2026 below NU (+₹21,026.84 < +₹23,744.40), so leg (c) fails arithmetically as a swap. R12-04 prints this arithmetic per form.
- **Exactly one flagged ingredient has an open re-test:** **R5-03-clean** — its only failing leg is (e), an interaction leg, and its construction is on a family the pair never touched.
**R12-03 variant (bankable):** the ending book with the **R5-03-clean swap applied verbatim** (`apply_r503`: GAP-FADE comp replaced by the ≥1.25% DOWN+FLAT fade-LONG sleeve, 09:20 entry, T125/S050 — sleeve anchored +₹32,064.93 / +₹4,270.42 — **and GAP-FADE-INC retired**). Birth record: gated at R5-03 on the Round-4 book, every leg true except (e); repriced as a stack slot in Rounds 6/8/9/11 decision support. The pair plausibly cures (e): the pair's profit lands outside the carrier names (R11-03's own (e) passed with combined ex-top-3 rising), and the swap's (e) arithmetic is read off the new book's top-3 sets, not the Round-4 book's.
**Placebos (the R5-03 birth convention):** the same swap applied with the **mirror** sleeve (follow-SHORT ≥1.25%, DOWN+FLAT) and with the **one-bar-late** sleeve (fade ≥1.25% at entry bar 2), GAP-FADE-INC retired in both; full combined totals of the two swapped books.
**Timing:** the gap signal completes at the bar-0 open print (the day's open vs prior close, both printed at 09:15); entries are at bar 1 (09:20) — violations 0 by construction (the R4-L2-compliant form; the 09:15-print entry form was voided at R4-07 and is not used).

### WS3 — October 2025 wound (R12-05 audit; R12-06 conditional gate)
**R12-05** decomposes every October-2025 row of the ending book by component × index-state bucket (the R10-05 method verbatim: state = `nifty_move(date, entry_time − 5min)`, buckets hard / shallow / up, unknown counted never guessed), asserted against the month net −₹3,751.28. The **offender** is the month's most negative component. **Separator test (frozen, R10-05's):** for each bucket of the offender — **(i)** the bucket's October net < 0 **and** |bucket October net| ≥ 50% of |offender October net|; **(ii)** the offender's full-year 2025 net in that bucket < 0; **(iii)** the offender's combined two-year full-year net in that bucket < 0. If **exactly one** bucket qualifies, R12-06 gates the removal variant (ending book minus the offender's rows in that bucket, both years) with the R10-06 chrono / cross-bucket placebos; otherwise WS3 closes by statement. No separator, no candidate. Timing for any removal: the bucketed bar completes exactly at the entry instant, asserted per removed row.

### WS4 — July 2025 residual (R12-07 audit; R12-08 conditional gate)
Identical method applied to July 2025's remaining −₹2,101.93 on the post-pair book (asserted in R12-07): decomposition, offender, the same frozen separator test, the same conditional removal gate (R12-08) with the same placebos — or closure by statement.

### WS5 — Combinations + stack maintenance + December freeze addendum (R12-09)
Candidates are each gated against the **starting** book (the standing convention). Resolution: the WS1/WS3/WS4 removals and the R5-03 swap act on disjoint components and compose; if more than one banking passes, the union is re-gated whole-book against the starting book — if the union passes it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded (the R11 WS5 rule verbatim). The four stack prices are restated on the ending book by the R11-08 generalised method (R2-26 and R5-03 swaps applied, banked NE-REV-family / REXP rows stripped by component, the stack's own slot rows applied — totals must reproduce the recorded prices exactly; if R5-03-clean itself banks in R12-03, the restatement's swap step is already satisfied in the ending book and the method reduces accordingly, with the identity still asserted). **December freeze addendum:** the freeze document is extended to the new ending book, and the extension is **regeneration-verified** — the ending book rebuilt from the Round-11 CSVs plus the banked Round-12 constructions by fresh code must match the exported ending CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. Ending books exported to `stocks_engine_r12_book{2025,2026}_trades.csv` and independently re-summed. If nothing passes, WS5 closes by statement (stack prices and the freeze addendum are still restated/extended on the unchanged book).

### Verdict rule (frozen for all Round-12 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS5 resolution). A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## WS1 — HARD-DIP EXCLUSION ON THE NEW BASELINE (R12-01, R12-02)

**R12-01 — AUDIT (passed, all assertions in code).** Starting books
re-summed independently from the Round-11 CSVs: 2025 1,128 rows, JO
₹99,363.06, full ₹99,880.95; 2026 1,368 rows, JO ₹2,47,540.89 — exact
vs the recorded totals; month nets asserted (Jul 2025 −₹2,101.93,
Oct 2025 −₹3,751.28). The INV-ABOVE census under the frozen R10-05
state definition reproduces R11-01's bucket nets to the paisa —
2025: hard 23 rows / −₹1,230.62 · shallow 33 / −₹620.96 · up 95 /
+₹10,132.83; 2026: hard 16 / −₹4,012.18 · shallow 10 / +₹3,066.24 ·
up 10 / +₹4,295.15 — with **zero unknown-state rows** in either
year. The pair left INV-ABOVE untouched, as constructed.

**R12-02 — INV-ABOVE hard-dip exclusion: BANKED — ALL TEN LEGS
PASS.** The identical construction that failed leg (e) by ₹135.40
on the pre-pair baseline passes on the pair book, without a single
row of the candidate changing. Removing the 23 / 16 hard-dip rows:
2025 JO ₹99,363.06 → **₹1,01,114.78** (+₹1,751.72); 2026 JO
₹2,47,540.89 → **₹2,51,553.07** (+₹4,012.18); combined ₹3,47,421.84
→ ₹3,52,664.64. The leg that refused it inverts: combined ex-top-3
₹1,03,228.30 → **₹1,04,182.04 (+₹953.74)** — on the old baseline the
same removal's ex-top-3 delta was **−₹135.40**. (2025's own
ex-top-3 still dips, −₹179.64; 2026's rises +₹1,133.38 on the moved
carrier sets; the leg reads the combined assembled book.) No month
flips, halves hold, cells hold, both removal placebos beaten
(chrono ₹3,48,898.96; cross-bucket ₹3,42,973.57), timing 0, leg
(x) holds. The R11-02 flag is retired — banked, not adopted.

## WS2 — SINGLE-LEG FLAG RE-TESTS (R12-03, R12-04)

**R12-03 — R5-03-clean re-gated on the pair book: REJECTED, on
legs (c) and (e).** The swap replaces the banked fade rows
(GAP-FADE + GAP-FADE-INC, netting ₹23,775.49 / ₹6,255.24) with the
≥1.25% sleeve (anchored ₹32,064.93 / ₹4,270.42 on 112/292 rows).
Raw deltas: 2025 **+₹8,289.44** (JO → ₹1,07,652.50), 2026
**−₹1,984.82** (JO → ₹2,45,556.07); combined rises to ₹3,53,726.46,
placebos beaten (mirror ₹2,83,779.80; late ₹3,07,751.29), no
flips, timing 0. But leg (c) fails — and leg (e) fails with it:
combined ex-top-3 falls to ₹97,652.34 (−₹5,575.96; 2026's own
ex-top-3 drops ₹8,580.46 — the swap's 2026 sleeve gains land in
carrier names on this book). The birth sheet (fails (e) only) is
superseded: the flag's recorded 2026 delta (+₹2,778.21) was
measured before GAP-FADE-INC existed — the "clean" swap must now
retire the banked R6-08 increment as well, and the increment's
2026 rows are worth more than the threshold widening gains there.
**The flag stays the owner's, repriced:** adoption from the
Round-12 ending book = 2025 JO **+₹6,537.72** / 2026 JO
**−₹5,997.00**, failing legs now (c) + (e).

**R12-04 — AUDIT (the screening record; no candidate scored).**
Every other single-leg flag is arithmetically pre-refused on the
new baseline, and the arithmetic is printed so the refusal is a
number, not an opinion:
- (c)-only REXP forms displace the banked REXP-DOWN T100/S065 leg
  (2026 −₹5,899.72): full population −₹10,286.95 (delta
  −₹4,387.23), DOWN+FLAT −₹10,930.18 (−₹5,030.46), T125/S050
  DOWN-only −₹8,399.33 (−₹2,499.61); R8-06 FADE-IDX removes banked
  fade legs netting +₹2,477.24 in 2026 (delta −₹2,477.24). Leg
  (c) is a delta comparison — its sign is fixed by the rows, on
  any baseline.
- NE-REV slot standalone sums (2025 / 2026, full-year): NU
  (banked) +₹12,596.19 / +₹23,744.40 · NOTCH +₹18,618.88 /
  +₹21,026.84 · NOTCHCELL +₹6,566.49 / +₹27,213.39 · IDXCELL
  +₹4,032.51 / +₹34,369.49 · thr-2.25 on the certified population
  (R6-02 rebuilt) +₹8,523.03 / +₹39,963.33. All are non-additive
  with NU (shared population); as slot swaps, IDXCELL /
  NOTCHCELL / thr-2.25 price 2025 below NU (leg (b) fails
  arithmetically) and NOTCH prices 2026 below NU (leg (c));
  R6-04's recorded 2025 delta (+₹544.11) is below NU's on its
  face. R5-03-clean was the only open re-test of the class — and
  it is now answered.

## WS3 — OCTOBER 2025 WOUND (R12-05, R12-06)

**R12-05 — AUDIT.** October 2025 = **−₹3,751.28 on 20 rows**
(asserted). By component: F4 **−₹3,021.83** · N4-V3 −₹793.80 ·
P2F −₹312.98 · P2F-R2 −₹288.00 · INV-ABOVE −₹207.92 ·
NE-REV-NU +₹193.25 · GAP-FADE-INC +₹680.00. The month is three
F4 trades, and all three sit in the **up** index-state bucket
(−₹3,021.83; hard 0, shallow 0). Separator test on the offender
(F4): the up bucket passes (i) (it is the whole wound) and (ii)
(F4's full-year 2025 up-bucket is −₹9,887.43) — and fails (iii)
decisively: F4's up-bucket nets **+₹30,693.95 combined** across
the two years (2026 alone +₹40,581.38). October's wound is the
weak-year face of the book's biggest 2026 state bucket.
**R12-06 — closes by statement:** 0 qualifying separators; no
candidate designed or scored. Full table in
`r12_oct_decomp.json`.

## WS4 — JULY 2025 RESIDUAL (R12-07, R12-08)

**R12-07 — AUDIT.** July 2025 = **−₹2,101.93 on 41 rows**
(asserted). The pair already repaired this month once (NU
+₹5,255.43, REXP −₹273.97 inside July). What remains: INV-ABOVE
**−₹2,473.45** (offender — 3 rows, all shallow-dip, the R10-05
cell verbatim) · N4-V3 −₹1,821.00 · GAP-FADE-INC −₹1,560.10 ·
F4 −₹1,025.28 (mixed states: hard +₹2,229.30, shallow −₹569.59,
up −₹2,684.99) · P2F −₹173.47 · P2F-R2 −₹170.85 · GAP-FADE
+₹140.76. Separator test on INV-ABOVE: the shallow bucket passes
(i) and (ii) and fails (iii) — its combined two-year net is
**+₹2,445.28**, exactly as in R10-05; the hard bucket passes (ii)
and (iii) but holds zero July rows, so (i) fails (and its
removal is in any case already banked book-wide at R12-02 — it
simply has no July rows to remove). **R12-08 — closes by
statement:** 0 qualifying separators; no candidate. Full table
in `r12_july_decomp.json`. July's residual is an information
desert (INV-ABOVE shallow-dip) plus diffuse small losses across
four components — no state slice owns it.

## WS5 — COMBINATIONS + STACK PRICES + FREEZE ADDENDUM (R12-09)

The union of Round-12 bankings is R12-02 alone (R12-03 rejected;
R12-06 / R12-08 produced no candidate), re-gated whole-book:
**PASS**, identical to the R12-02 gate. Ending books exported to
`stocks_engine_r12_book{2025,2026}_trades.csv` and independently
re-summed to the paisa.

Stack prices restated on the ending book (generalised rebuild:
swaps applied, banked NE-REV/REXP rows stripped by component,
stack slot applied — totals reproduce the recorded prices
**exactly**; adoption values now measured from the ending book):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹22,116.33 / **−₹4,005.82** | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹26,019.24 / **−₹7,091.84** | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹18,698.66 / **−₹4,374.28** | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹12,031.60 / **+₹6,250.81** | **passes all ten legs** |

Note for the owner: the ending book has absorbed value the
stacks used to supply (the pair, and now the hard-dip removal),
so the stack decision is worth less than it was — and its sign
has split: the unconditioned, A and C forms now **cost** 2026
against the ending book. Each stack form re-prices the whole
assembly (the R2-26 swap, the R5-03 swap — itself now a
2026-negative swap, per R12-03 — its NE-REV slot, and REXP at
T125/S050) against a book that banks NU + REXP-DOWN at
T100/S065 plus the hard-dip removal. **IDXCELL is now the only
stack form that adds in both years.**

**December freeze:** the R12-09 addendum to
`stocks_engine_banked_book_FREEZE_dec2026.md` extends the
freeze to the ending book (the R11-08 book plus the hard-dip
exclusion, specified in the addendum with its timing argument),
and **regeneration verification PASSED** — rebuilt from the
Round-11 CSVs by fresh code (the removal recomputed from the
state definition), the book matches the exported Round-12 CSVs
row-for-row (multiset identity on comp/date/stock/dir/
entry_time/net) and to the paisa in both years. The December
pass/kill lines apply to the ending book as a whole.

## ENDING PER-YEAR SCORECARD (banked book — after the R12-02 banking)

**2025:** JO **+₹1,01,114.78** on 1,058 Jan–Oct trades (full year
+₹1,01,111.57, 1,105 rows) — **₹10,111.48/month vs the ₹15,000
floor; gap ₹48,885.22** (was ₹50,636.94). Months: Jan +4,047.65 ·
Feb +22,684.31 · Mar +6,799.85 · Apr +44,851.99 · May +5,831.22 ·
Jun +1,237.54 · Jul −2,101.93 · Aug +11,477.35 · Sep +10,038.08 ·
Oct −3,751.28. Ex-top-3 (full) +₹35,085.01. Red Jan–Oct months:
Jul, Oct — both unchanged by this round's banking (the removal
holds no July rows, and its October rows net zero).

**2026:** JO **+₹2,51,553.07** on 1,352 trades — **₹25,155.31/
month, floor MET**, every month green, ex-top-3 (full)
+₹69,097.03.

## DECISION STATE after Round 12

- Banked book: **the hard-dip exclusion is in.** 2025 gap to
  floor: **₹48,885.22** (was ₹50,636.94).
- Round 12 banked: **1** (R12-02). Cycles: 9 (2 gated
  candidates, 7 audits incl. the WS5 finalise). Voided cells:
  **none**; timing violations 0 on every construction.
- Flagged list: 24 entries (R11-02 retired — banked at
  R12-02; R5-03 restated to its R12-03 sheet: fails (c) + (e),
  adoption +₹6,537.72 / −₹5,997.00 from the ending book).
- The re-test class Round 11's lesson opened is now
  **exhausted**: of the flagged single-leg failures, the two
  with interaction legs on disjoint families have been re-gated
  on the new baseline (one banked, one re-refused on a worse
  sheet); every other single-leg flag fails a delta leg, whose
  sign no baseline can change (R12-04 arithmetic on record).
- Both remaining red months have now been decomposed on the
  post-pair book and neither carries a separator: July is the
  shallow-dip desert cell (combined-positive, unremovable
  under the frozen test for the second time) plus diffuse
  losses; October is F4's up-state bucket, which is 2026's
  engine room (+₹40,581.38 there in 2026 alone).
- The banked book (ending form) remains **frozen for
  December** with the pre-registered pass/kill lines (R11-07
  freeze + R11-08 and R12-09 addenda).
- Next-round leads (untested, for pre-registration): none
  inside the re-test class. The remaining honest routes to
  the 2025 floor are the ones already on record — December
  fresh data judged against the frozen book, a genuinely new
  data axis (bulk/block deals, delivery percentages — not in
  this workspace), or Chandu-level adoption decisions (the
  stacks, now repriced above; R2-26, whose swap is inside
  every stack price).
