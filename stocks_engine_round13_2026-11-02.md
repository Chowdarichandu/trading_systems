# Stocks (SarvaRitu) Engine — ROUND 13 · prior-day sweep + reclaim (new mechanism), REXP and NE-REV-NU geometry neighbours
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-12 ending book): 2025 Jan–Oct **+₹1,01,114.78** (₹10,111.48/mo; gap ₹48,885.22; red Jan–Oct months Jul −₹2,101.93 / Oct −₹3,751.28 — both decomposed in R12, neither carries a separator, **not re-tested here**) · 2026 Jan–Oct **+₹2,51,553.07** (₹25,155.31/mo; floor MET). To be re-verified by independent re-sum of `stocks_engine_r12_book{2025,2026}_trades.csv` in R13-01 before any Round-13 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): the 24 flagged entries through Round 12, incl. the max stack and its forms. Round 13 adopts nothing on Chandu's behalf; its bankable candidates are gated on the banked book. The single-leg flag re-test class is **exhausted** (R12-04) and is not re-screened.
- **Round 13's premise:** the re-test class is closed and both red months are information deserts; what remains untested is (1) one genuinely new mechanism — Chandu's own index method #4 (bear-trap / reclaim) transplanted to cash stocks, never gated on this book; and (2) the exit geometry of the two sleeves banked in Round 11, whose frozen cells were adopted at their birth geometries and never gridded on this book. Standing prior, recorded before scoring (Lesson 2): price-derived level events (PDH/PDL breaks, retest holds, rejections) have been information-free on his 25 in family after family — WS1 is gated in full knowledge of that prior; the gate, not the prior, decides.

---

## PRE-REGISTRATION (written before any Round-13 candidate is scored)

### R13-01 — Starting-book verification (audit)
The starting books are re-summed from `stocks_engine_r12_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹1,01,114.78 / full ₹1,01,111.57 / 1,105 rows; 2026 JO ₹2,51,553.07 / full ₹2,51,553.07 / 1,352 rows; Jul 2025 −₹2,101.93; Oct 2025 −₹3,751.28). No candidate is scored if the audit fails.

### WS1 — NEW MECHANISM: prior-day-low sweep + reclaim, LONG (R13-02 — bankable); prior-day-high sweep + rejection, SHORT (R13-03 — bankable, the pre-registered symmetric variant)
**Construction (frozen, both forms).** For each watchlist stock and each trading day with a prior session in the stored daily series (weekend days skipped, the engine convention):
- **Level:** the prior session's low (LONG form) / high (SHORT form), from the stored daily record — prior data, knowable before the day opens.
- **Morning window:** the 5-min bars timestamped 09:15 through 10:30 inclusive.
- **Sweep:** the first window bar whose low trades strictly below the prior low (LONG form) / whose high trades strictly above the prior high (SHORT form).
- **Reclaim / rejection:** the first bar at or after the sweep bar, still inside the window, whose close is strictly back above the prior low (LONG) / strictly back below the prior high (SHORT). The sweep bar itself may be its own reclaim bar (a pin-bar reclaim). If no such close occurs inside the window, no trade.
- **Entry:** the open of the bar immediately after the reclaim/rejection bar; the entry bar must exist and be timestamped ≤ 10:35. One trade per stock-day (the first sweep sequence only).
- **Exits:** T125/S050 via `replay_plain` (the book's family cell; stop checked before target inside a bar; square-off at the 15:10 close, the book convention).
- **Population:** all stock-days as above — no event, regime or name conditioning (the mechanism as tasked). Days lacking the needed bars are skipped and counted.
**Timing (asserted per trade):** the entry bar index is strictly greater than the reclaim bar index, which is ≥ the sweep bar index; the reclaim close is printed at the end of the reclaim bar, which is the entry bar's open instant; the level is prior-session data. Violations are counted and must be 0.
**Placebos (the engine convention):** the flipped book (opposite direction on identical entries) and the one-bar-late book (same direction, entry one bar later), each added to the starting book; the gate's leg (h) reads their combined totals.
**Comps:** `SWEEP-RECLAIM` (R13-02), `SWEEP-REJECT` (R13-03) — new components, added to the book.

### WS2 — REXP geometry neighbours (R13-04, R13-05 — bankable swaps)
The banked REXP-DOWN sleeve (comp `REXP`, SHORT, DOWN regime cells, entry 10:20) wears **T100/S065**. Each candidate replaces those rows, on the ending book, with the identical population re-scored at one adjacent cell: **R13-04: T125/S065** (target step only) · **R13-05: T100/S050** (stop step only). Builds via `rexp_geo` with the geometry parameterised; the frozen cell (T100/S065) must first reproduce the banked REXP rows exactly (multiset identity + Jan–Oct sums +₹10,243.45 / −₹5,899.72) as the swap anchor. Placebos: the same swap with the flipped / one-bar-late row sets at the candidate geometry.

### WS3 — NE-REV-NU geometry micro-grid (R13-06, R13-07 — bankable swaps)
The banked NE-REV-NU sleeve (comp `NE-REV-NU`, the NOTCH+UPGUARD-conditioned certified NE-REV population, signal 10:25 → entry 10:35) wears **T100/S065**, never gridded. At most two adjacent cells, pre-registered here: **R13-06: T125/S065** (target step only) · **R13-07: T100/S050** (stop step only). Each candidate replaces the banked NU rows with the identical population (the anchored `notchup` row set, 200 / 313 rows) re-scored from its own entry bars at the candidate geometry. The frozen cell re-scored at T100/S065 must reproduce the banked NU rows exactly (multiset identity + standalone sums +₹12,596.19 / +₹23,744.40) as the swap anchor. Placebos: the same swap with the flipped / late NU row sets re-scored at the candidate geometry.

### WS4 — Combinations + stack maintenance + December freeze addendum (R13-08)
Candidates are each gated against the **starting** book (the standing convention). Resolution (the R11/R12 WS5 rule verbatim): the WS1 additions and the WS2/WS3 swaps act on disjoint components and compose; if more than one banking passes, the union is re-gated whole-book against the starting book — if the union passes it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded. The four stack prices are restated on the ending book by the R12-09 generalised method (R2-26 and R5-03 swaps applied, banked NE-REV-family / REXP rows stripped by component, the stack's own slot rows applied — totals must reproduce the recorded prices exactly). **December freeze addendum:** the freeze document is extended to the new ending book, and the extension is **regeneration-verified** — the ending book rebuilt from the Round-12 CSVs plus the banked Round-13 constructions by fresh code must match the exported ending CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. Ending books exported to `stocks_engine_r13_book{2025,2026}_trades.csv` and independently re-summed. If nothing passes, WS4 closes by statement (stack prices and the freeze addendum are still restated/extended on the unchanged book). Rejected candidates failing at most two legs join the flagged list as owner decisions, with adoption values measured from the ending book (the candidate's construction applied to the ending book; disjoint components, so the arithmetic is exact).

### Verdict rule (frozen for all Round-13 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS4 resolution). A candidate failing any leg is recorded with its failing legs named; the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R13-01 — STARTING-BOOK VERIFICATION (audit, passed)
Books re-summed from the Round-12 CSVs: 2025 JO ₹1,01,114.78 / full ₹1,01,111.57 / 1,105 rows; 2026 JO ₹2,51,553.07 / full ₹2,51,553.07 / 1,352 rows — exact vs the Round-12 record; Jul 2025 −₹2,101.93 and Oct 2025 −₹3,751.28 asserted. No scoring preceded this audit.

## WS1 — THE SWEEP MECHANISM (R13-02, R13-03)

**R13-02 — SWEEP-RECLAIM LONG: REJECTED on nine of ten legs** (a, b, c, d, e, f, g, h, x — only the timing leg passes, violations 0). The mechanism fires constantly and loses constantly: 12,775 population stock-days → 4,176 sweep days → **2,885 signals** (1,291 sweeps never reclaimed inside the window; 0 signals lost to a missing entry bar). Standalone **2025 −₹1,62,923.55 on 1,585 trades · 2026 −₹1,06,668.60 on 1,300 trades** (combined expectancy ≈ −₹93/trade after costs). Added to the book: 2025 JO collapses to −₹46,030.81, 2026 JO falls to ₹1,44,884.47 (below the floor — leg (x) fails), combined ₹83,072.49. It also loses to **both** placebos (flipped book ₹3,20,661.65; late book ₹1,39,743.54): on identical entries the *opposite* direction is the less-bad side, and entering a bar later is better than entering on the reclaim — the reclaim close carries no information in the traded direction. Eight green months flip red across the two years.

**R13-03 — SWEEP-REJECT SHORT: REJECTED on seven legs** (a, b, c, d, e, f, h; halves and timing hold, leg (x) holds). 4,379 sweep days → **3,098 signals** (1,281 unrejected in-window). Standalone **2025 −₹11,893.51 on 1,794 trades · 2026 −₹370.85 on 1,304 trades** — expectancy ≈ −₹4/trade, i.e. gross zero before the ₹40 cost, the Lesson-2 signature exactly. Book combined falls to ₹3,40,400.28 and it loses to the late placebo (₹3,56,724.77). Four green months flip.

**WS1 verdict:** Chandu's index method #4 does not transplant to cash stocks in either direction. A single-name prior-day low is swept and reclaimed thousands of times a year on this universe and the event is information-free — the index version's content (if any) lives in index-level structure, not in single-name level geometry. The family is closed here; neither form is flagged (nine and seven failing legs are not near-misses).

## WS2 — REXP GEOMETRY NEIGHBOURS (R13-04, R13-05)
Anchor: `rexp_geo` at the frozen T100/S065 reproduces the banked REXP rows exactly (41/86 rows; JO +₹10,243.45 / −₹5,899.72).

**R13-04 — T125/S065: REJECTED on (a) + (c) + (e).** Sleeve JO +₹12,534.71 / −₹10,152.39: the wider target buys 2025 (+₹2,291.26; book JO → ₹1,03,406.04) and charges 2026 (−₹4,252.67; book JO → ₹2,47,300.40); combined falls to ₹3,50,703.23 and 2026's own ex-top-3 drops the (e) leg. Placebos beaten (₹3,39,926.06 / ₹3,48,821.03); no flips; timing 0. This is the sleeve's birth geometry trade-off (R7-03 at T125/S050) re-priced at S065 — the target axis on this sleeve trades years against each other. Three failing legs: under the frozen rule it is not flagged.

**R13-05 — T100/S050: BANKED — ALL TEN LEGS PASS.** Sleeve JO +₹12,486.11 / −₹4,384.34 — the tighter stop improves **both** years against the banked cell (+₹2,242.66 / +₹1,515.38): 2025 JO → **₹1,03,357.44**; 2026 JO → **₹2,53,068.45**; combined ₹3,52,664.64 → **₹3,56,422.68**. Placebos beaten (flipped ₹3,35,674.58; late ₹3,49,900.33); no flips; halves and cells hold; leg (x) holds. The banked sleeve's 0.65% stop was simply too wide for its population — REXP-DOWN's range-expansion entries that are going to work do so without being given the extra 0.15% of room.

## WS3 — NE-REV-NU GEOMETRY MICRO-GRID (R13-06, R13-07)
Anchor: `nu_geo` at the frozen T100/S065 reproduces the banked NU rows exactly (200/313 rows; standalone +₹12,596.19 / +₹23,744.40).

**R13-06 — T125/S065: REJECTED on (a) + (c) only.** Sleeve standalone +₹15,631.27 / +₹17,746.35: the wider target buys 2025 (book JO → ₹1,03,441.59, +₹2,326.81) and charges 2026 (book JO → ₹2,45,555.02, −₹5,998.05) — the same year-trade as R13-04, one sleeve over. Everything else passes: placebos beaten (₹2,78,439.03 / ₹3,25,212.08), no flips, cells and halves hold, leg (x) holds (2026 stays above the floor). **Flagged as an owner decision** (two failing legs): adoption from the Round-13 ending book → 2025 JO **₹1,05,684.25** / 2026 JO **₹2,47,070.40**.

**R13-07 — T100/S050: REJECTED on (a) + (b) + (c) + (f).** Sleeve standalone +₹9,924.27 / +₹23,004.18 — the tighter stop that paid REXP in the same round costs NU in **both** years (book JO → ₹98,085.98 / ₹2,50,812.85) and flips June 2025 red (+₹1,237.54 → −₹1,090.89). NU's dip-buying population needs its 0.65% of room; REXP's expansion population does not. NU's frozen cell is now bracketed on both axes: wider target fails (c), tighter stop fails (b) + (c) — T100/S065 stands as the measured cell, not an untested default.

## WS4 — COMBINATIONS + STACK PRICES + FREEZE ADDENDUM (R13-08)
The union of Round-13 bankings is R13-05 alone (R13-02/03/04/06/07 rejected), re-gated whole-book: **PASS**, identical to the R13-05 gate. Ending books exported to `stocks_engine_r13_book{2025,2026}_trades.csv` and independently re-summed to the paisa.

Stack prices restated on the ending book (generalised rebuild: swaps applied, banked NE-REV/REXP rows stripped by component, stack slot applied — totals reproduce the recorded prices **exactly**; adoption values now measured from the ending book):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹19,873.67 / **−₹5,521.20** | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹23,776.58 / **−₹8,607.22** | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹16,456.00 / **−₹5,889.66** | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹9,788.94 / **+₹4,735.43** | **passes all ten legs** |

**IDXCELL remains the only stack form that adds in both years** — and the ending book keeps absorbing the stacks' 2026 value (this round's REXP geometry gain accrues to the ending book, not to any stack form, since every stack re-prices REXP at its own frozen T125/S050).

**December freeze:** the R13-08 addendum to `stocks_engine_banked_book_FREEZE_dec2026.md` extends the freeze to the ending book (the R12-09 book with REXP-DOWN at T100/S050 — population, admission and entry unchanged; exit geometry carries no admission information), and **regeneration verification PASSED** — rebuilt from the Round-12 CSVs by fresh code (the REXP set rebuilt at T100/S050 by `rexp_geo`), the book matches the exported Round-13 CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. The December pass/kill lines apply to the ending book as a whole.

## ENDING PER-YEAR SCORECARD (banked book — after the R13-05 banking)

**2025:** JO **+₹1,03,357.44** on 1,058 Jan–Oct trades (full year +₹1,03,354.23, 1,105 rows) — **₹10,335.74/month vs the ₹15,000 floor; gap ₹46,642.56** (was ₹48,885.22). Months: Jan +4,047.65 · Feb +22,747.08 · Mar +7,027.83 · Apr +45,256.60 · May +5,831.22 · Jun +1,237.54 · Jul −2,000.01 · Aug +12,922.73 · Sep +10,038.08 · Oct −3,751.28. Ex-top-3 (full) +₹36,946.62. Red Jan–Oct months: Jul (improved +₹101.92 by the stop change), Oct (untouched to the paisa).

**2026:** JO **+₹2,53,068.45** on 1,352 trades — **₹25,306.85/month, floor MET**, every month green, ex-top-3 (full) +₹70,074.30.

## DECISION STATE after Round 13

- Banked book: **REXP-DOWN now wears T100/S050.** 2025 gap to floor: **₹46,642.56** (was ₹48,885.22).
- Round 13 banked: **1** (R13-05). Cycles: 8 (6 gated candidates, 2 audits incl. the WS4 finalise). Voided cells: **none**; timing violations 0 on every construction.
- Flagged list: 25 entries (R13-06 added: NU at T125/S065, fails (a) + (c), adoption +₹2,326.81 / −₹5,998.05 from the ending book). R13-04 fails three legs and is not flagged under the frozen rule.
- **WS1 closes a family:** the prior-day sweep + reclaim/rejection transplant loses in both directions at full gate — the last untested mechanism class named for this book is answered, and it was the Lesson-2 family the pre-registration flagged as the standing prior.
- Both Round-11 sleeves now have measured geometry: REXP's stop step paid in both years and is banked; its target step and both NU steps re-price the same 2025-for-2026 trade (NU's wider target is flagged at that price). The geometry axes on the banked pair are exhausted at the adjacent cells.
- The banked book (ending form) remains **frozen for December** with the pre-registered pass/kill lines (R11-07 freeze + R11-08, R12-09 and R13-08 addenda).
- Next-round leads: none inside the tested classes. The remaining honest routes to the 2025 floor are the ones already on record — December fresh data judged against the frozen book, a genuinely new data axis (bulk/block deals, delivery percentages — not in this workspace), or Chandu-level adoption decisions (the stacks, repriced above; R2-26; and now R13-06).

