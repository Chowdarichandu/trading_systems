# Stocks (SarvaRitu) Engine — ROUND 11 · INV-ABOVE hard-dip exclusion, cross-family pair (NE-REV-NU + REXP-DOWN), leg-(e) anatomy, December freeze of the banked book
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-10 ending book, causality-audited): 2025 Jan–Oct **+₹78,420.04** (₹7,842.00/mo; gap ₹71,579.96) · 2026 Jan–Oct **+₹2,29,696.21** (₹22,969.62/mo; floor MET). Re-verified by independent re-sum of the Round-10 exported CSVs in R11-01 before any Round-11 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round: a condition may reference state (index level/move, regime cell, price bands), never the calendar.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): all 24 flagged entries through Round 10, incl. the max stack, Variant C, and every standalone NE-REV form. Round 11 adopts nothing on Chandu's behalf; its bankable candidates are gated on the banked book.

---

## PRE-REGISTRATION (written before any Round-11 candidate is scored)

### R11-01 — Starting-book verification + INV-ABOVE state census (audit)
The starting books are re-summed from `stocks_engine_r10_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹78,420.04 / full ₹77,041.31 / 887 rows; 2026 JO ₹2,29,696.21 / 969 rows). The audit also censuses every INV-ABOVE row of the banked book by index-state bucket under the **frozen R10-05 state definition** — state = `nifty_move(date, entry_time − 5min)`, the % move of the close of the last 5-min NIFTY bar completing at the entry instant vs the prior close, bucketed **hard-dip ≤ −0.30% · shallow-dip (−0.30%, 0) · up/flat ≥ 0**; unknown states counted, never guessed — and must reproduce R10-05's full-year INV-ABOVE bucket nets exactly (2025: hard −₹1,230.62 · shallow −₹620.96 · up +₹10,132.83; 2026: hard −₹4,012.18 · shallow +₹3,066.24 · up +₹4,295.15).

### WS1 — INV-ABOVE hard-dip exclusion (R11-02 — bankable)
**Variant:** the banked book minus every INV-ABOVE row whose state bucket (R11-01 definition) is **hard-dip**, in both years. Unknown-state rows are never removed. This is the loss-removal candidate R10-L4 named: the hard-dip rows lose in both years (−₹1,230.62 / −₹4,012.18) and are disjoint from the July wound (zero July rows).
**Placebos (frozen, the R10-06 removal convention):** **P1 chrono** — the same per-year count of INV-ABOVE rows removed, earliest first, any bucket; **P2 cross-bucket** — the same per-year count of INV-ABOVE rows removed from the non-hard buckets (shallow + up), earliest first, any shortfall made up from the hard bucket's earliest rows.
**Timing:** the bucketed bar completes exactly at each row's entry instant, so the state is knowable strictly before the entry fill; asserted per removed row in code; violations counted and must be 0.

### WS2 — Cross-family pair (R11-03 — bankable; R11-04 — one conditional substitution)
**R11-03 variant:** the banked book **+ NE-REV-NU rows** (the exact `build_cond()["notchup"]` rows, comp NE-REV-NU; anchor: standalone +₹12,596.19 / +₹23,744.40 on 200/313 rows, asserted at build) **+ REXP-DOWN rows at the preferred geometry T100/S065** (`rexp_geo("SHORT", cells={"DOWN"}, tgt=1.00, stp=0.65)`; anchor: Jan–Oct deltas +₹10,243.45 / −₹5,899.72 per the R8-07 record, asserted at build). The two ingredients come from different families and fail different single legs standalone — NU fails (e) only, REXP-DOWN fails (c) only; the pair tests whether the failures cure each other assembled.
**Placebos:** the book plus both ingredients' **flipped** rows; the book plus both ingredients' **one-bar-late** rows (identical conditions throughout).
**Timing:** CERT build violations + REXP build violations, both counted at build and asserted 0.
**R11-04 (conditional, exactly one substitution, pre-registered trigger):** runs **iff** R11-03 fails **and** its failed-leg set intersects {c_2026_no_fall, e_extop3} — i.e. the (e)/(c) legs are trading places assembled. The substitution replaces NU with **NE-REV-NOTCHCELL** rows (the exact R10-04 rows) alongside the same REXP-DOWN rows, with the same composed placebos. If the trigger does not fire, R11-04 closes by statement. No second substitution exists.

### WS3 — Leg-(e) anatomy of NE-REV-NU standalone + one conditional variant (R11-05 audit; R11-06 conditional gate)
**R11-05** recomputes the R10-02 construction (banked book + NU rows) and decomposes its leg-(e) failure exactly, per year, under the gate's own definition (full-year totals; each book judged against its OWN top-3 stock set): Δex-top-3 = (NU profit in names outside the variant's top-3) + (base profit in names leaving the top-3) − (base profit in names entering the top-3), with the variant/base top-3 sets, the per-stock NU profit table, and the largest NU trades sitting inside the variant's top-3 names all printed to `r11_nu_anatomy.json`.
**Separator test (frozen, applied to the anatomy before any variant is designed):** the only slices searched are **state slices** of the NU population — (a) the trade day's frozen regime cell (DOWN / FLAT / UP, REGIME-CLASSIFIER-1 labels) and (b) the 10:25 index-state bucket (hard-dip / up — the shallow bucket is inadmissible under NOTCH by construction and is verified so, not searched). Name-based slices are diagnosis only, never separators. A slice qualifies iff **(i)** its combined two-year NU net < 0; **(ii)** its NU net < 0 in **each** year separately; **(iii)** |combined net| ≥ 50% of the combined leg-(e) shortfall measured in R11-05. If **exactly one** slice qualifies, R11-06 gates **NU-minus-that-slice** standalone (placebos: the flipped / late NU rows minus the same slice — the slice is date-level state, so all three row sets filter identically). Otherwise WS3 closes by statement: no candidate.

### WS4 — December freeze of the BANKED book (R11-07 — decision support)
The banked book's full tradeable specification is frozen in writing to `stocks_engine_banked_book_FREEZE_dec2026.md`: basis, universe, regime law, and for every component its admission conditions, decision bar, entry, exits and banked exclusions — with **every admission condition and every feature certified knowable at its decision bar** in a timing-certification table. **Regeneration verification:** the book is rebuilt through its documented construction chain (Round-8 ending CSVs → the Round-9 load chain → the Round-10 export) by fresh code and must match the Round-10 book CSVs **row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years**, behind the frozen book's own controls (month table, halves, regime cells, ex-top-3 printed). **December pass/kill lines are pre-registered in the freeze document.** Flagged forms are NOT frozen here — an adopted stack would get its own freeze.

### WS5 — Combinations + stack-price maintenance (R11-08)
Standalone candidates are each gated against the **starting** book (the standing convention). Bankings resolve here: the removal (R11-02) composes disjointly with any addition; the NU-family bankings (R11-03 pair / R11-04 substitution / R11-06 conditioned NU) are **alternatives, never additive** — if more than one passes, the one with the highest combined total enters the union. The union is re-gated whole-book against the starting book; if the union passes, it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded. The four stack prices are restated on the ending book by the R10-08 rebuild method, generalised: any NE-REV-family or REXP rows already banked in the ending book are first removed by component, then the stack's own slot rows are applied (row-identity dedupe), so each price is the adoption value **from the ending book**. If nothing passes, WS5 closes by statement.

### Verdict rule (frozen for all Round-11 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS5 resolution for alternative NU-family forms). A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## WS1 — INV-ABOVE HARD-DIP EXCLUSION (R11-01, R11-02)

**R11-01 — AUDIT (passed, all assertions in code).** Starting books
re-summed independently from the Round-10 CSVs: 2025 887 rows, JO
₹78,420.04, full ₹77,041.31; 2026 969 rows, JO ₹2,29,696.21 — exact
vs the recorded totals. The INV-ABOVE census under the frozen
R10-05 state definition reproduces R10-05's full-year bucket nets
to the paisa — 2025: hard 23 rows / −₹1,230.62 · shallow −₹620.96 ·
up +₹10,132.83; 2026: hard 16 rows / −₹4,012.18 · shallow
+₹3,066.24 · up +₹4,295.15 — with **zero unknown-state rows** in
either year.

**R11-02 — INV-ABOVE hard-dip exclusion: REJECTED, on leg (e)
ONLY — by ₹135.40.** Removing the 23 / 16 hard-dip rows raises
both years: 2025 JO ₹78,420.04 → **₹80,171.76** (+₹1,751.72);
2026 JO ₹2,29,696.21 → **₹2,33,708.39** (+₹4,012.18); combined
₹3,06,737.52 → ₹3,11,980.32. No month flips, halves hold, cells
hold, both removal placebos beaten, timing 0, leg (x) holds. The
single failing leg is concentration: combined ex-top-3
₹1,01,181.87 → ₹1,01,046.47 (−₹135.40; 2025 ex-top-3 −₹1,269.78,
2026 +₹1,133.38). The removed losses sit partly inside the book's
carrier names — deleting a loss from a top-3 name raises the
top-3 sum and lowers ex-top-3 by the same amount. **Joins the
flagged list** as an owner decision (a removal; composes
disjointly with the banked pair).

## WS2 — CROSS-FAMILY PAIR (R11-03, R11-04)

**R11-03 — NE-REV-NU + REXP-DOWN (T100/S065): BANKED — ALL TEN
LEGS PASS.** The two ingredients fail different single legs
standalone (NU: (e) only, R10-02; REXP-DOWN: (c) only, R8-07) and
cure each other assembled: NU's 2026 volume (+₹23,744.40)
absorbs REXP's 2026 cost (−₹5,899.72), curing (c); REXP's profit
lands outside NU's carrier names, curing (e) — combined ex-top-3
rises to ₹1,03,228.30 (2025 ₹35,264.65 / 2026 ₹67,963.65).
Whole-book: 2025 JO → **₹99,363.06** (+₹20,943.02); 2026 JO →
**₹2,47,540.89** (+₹17,844.68); combined ₹3,06,737.52 →
**₹3,47,421.84**. No flips (June 2025 in fact greens:
−₹955.92 → +₹1,343.41; July 2025 −₹7,083.39 → −₹2,101.93);
placebos beaten (flipped pair book and late pair book both
below the variant); timing violations 0 (CERT 0 + REXP 0,
asserted at build; anchors reproduced exactly — NU +₹12,596.19 /
+₹23,744.40 on 200/313 rows, REXP-DOWN Jan–Oct +₹10,243.45 /
−₹5,899.72 on 41/86 rows).

**R11-04 — closes by statement:** the pre-registered trigger
(pair fails with (c) or (e) among the failed legs) did not fire —
the pair banked. No substitution was designed or scored.

## WS3 — LEG-(e) ANATOMY OF NE-REV-NU (R11-05, R11-06)

**R11-05 — AUDIT.** Combined ex-top-3 ₹1,01,181.87 → ₹90,571.45;
shortfall **₹10,610.42**, decomposed exactly (asserted in code)
and it is **entirely a 2026 phenomenon**:
- **2025: ex-top-3 RISES +₹571.69.** NU profit outside the
  variant top-3 is only +₹553.09 of its +₹12,596.19 — ₹12,043.10
  lands inside the top-3 (ASTRAL / GODREJCP / OBEROIRLTY) — but
  the top-3 set churns (GLENMARK leaves, +₹8,324.51 of base
  profit becomes visible; GODREJCP enters, −₹8,305.91), netting
  positive.
- **2026: ex-top-3 FALLS −₹11,182.11 with the top-3 set
  unchanged** — and the decomposition is one term: NU's 2026
  profit **outside** the top-3 names is **−₹11,182.11**. NU's
  2026 standalone +₹23,744.40 = **+₹34,926.51 inside the top-3**
  (TVSMOTOR +₹18,734.26 · OBEROIRLTY +₹11,376.19 · ASTRAL
  +₹4,816.06) **minus ₹11,182.11 outside it** (UNITDSPR
  −₹10,762.92 the largest single drag; HINDCOPPER −₹3,149.00).
  The sleeve's 2026 breadth is not merely thin — it is negative;
  its entire profit is three carrier names.

**Separator test: 0 qualifying slices.** No regime-cell slice and
no 10:25-bucket slice is negative in both years (the worst state
slice, 10:25-bucket UP — 2025 +₹8,563.68 / 2026 −₹10,625.09 —
flips sign across years and fails (ii) and (iii); the shallow
bucket is verified empty in NU, as NOTCH requires). The (e)
failure is a **name** fact, not a state fact — and names are
diagnosis only under the frozen rules.

**R11-06 — closes by statement:** no separator, no candidate.
NU's standalone routes remain what they were: assembly (banked
as the pair, R11-03) or owner adoption (flagged, R10-02).

## WS4 — DECEMBER FREEZE (R11-07, decision support)

**The banked book is frozen in writing:**
`stocks_engine_banked_book_FREEZE_dec2026.md` — basis, universe,
regime law, every component's admission / decision bar / entry /
exits / banked exclusions, and a **per-feature timing
certification table** (prior-close features knowable pre-open;
reaction-day status only from the R6-11 certified set — a
same-day intraday announcement never qualifies its own day;
09:30 move from the 09:25 bar close, entry 09:35; gap from the
open print, entries 09:20/09:40; F4 move through the 10:00 bar,
entries strictly after).
**Regeneration verification PASSED:** rebuilt through the
documented chain (Round-8 ending CSVs → the Round-9/10 identity
chain) by fresh code, the book matches the Round-10 CSVs
**row-for-row** (multiset identity on
comp/date/stock/dir/entry_time/net) **and to the paisa** in both
years. Structural audit clean on all 1,856 rows (universe,
entry times, date years). Frozen-book controls: halves positive
in both years, all regime cells positive, ex-top-3 +₹23,708.10 /
+₹77,473.77.
**December lines pre-registered in the freeze doc:** PASS =
December net > ₹0 AND no ISO week worse than −₹15,000 AND ≥ 20
trades · FLOOR LINE = December net ≥ ₹15,000 · KILL = December
net ≤ ₹0 · < 20 trades extends judging to January. No parameter
changes in December. Flagged forms are not frozen; the R11-08
addendum to the freeze doc extends it to the ending book (the
banked pair rides the same lines).

## WS5 — COMBINATIONS + STACK PRICES (R11-08)

The union of Round-11 bankings is the R11-03 pair alone
(R11-02 rejected; R11-04 / R11-06 produced no candidate),
re-gated whole-book: **PASS**, identical to the R11-03 gate.
Ending books exported to `stocks_engine_r11_book{2025,2026}_
trades.csv` and independently re-summed to the paisa.

Stack prices restated on the ending book (generalised rebuild:
swaps applied, banked NE-REV/REXP rows stripped by component,
stack slot applied — totals reproduce the recorded prices
**exactly**, adoption values now measured from the ending book):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹23,868.05 / +₹6.36 | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹27,770.96 / −₹3,079.66 | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹20,450.38 / −₹362.10 | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹13,783.32 / +₹10,262.99 | **passes all ten legs** |

Note for the owner: the ending book already contains Variant
C's NE-REV slot ingredient (NU) plus REXP at the tighter
T100/S065 geometry — the stack decision is now worth less than
it was (its remaining content is the R2-26 exit swap, the
R5-03 fade swap, and REXP at T125/S050 in place of T100/S065).

## ENDING PER-YEAR SCORECARD (banked book — after the R11-03 banking)

**2025:** JO **+₹99,363.06** on 1,078 trades (full year
+₹99,880.95, 1,128) — **₹9,936.31/month vs the ₹15,000 floor;
gap ₹50,636.94.** Months: Jan +4,441.75 · Feb +22,684.31 ·
Mar +6,799.85 · Apr +44,851.99 · May +3,774.99 · Jun +1,343.41 ·
Jul −2,101.93 · Aug +11,477.35 · Sep +9,842.62 · Oct −3,751.28.
Ex-top-3 (full) +₹35,264.65. Red Jan–Oct months: Jul, Oct.

**2026:** JO **+₹2,47,540.89** on 1,368 trades — **₹24,754.09/
month, floor MET**, every month green, ex-top-3 (full)
+₹67,963.65.

## DECISION STATE after Round 11

- Banked book: **the pair is in.** 2025 gap to floor:
  **₹50,636.94** (was ₹71,579.96).
- Round 11 banked: **1** (R11-03). Cycles: 8 (2 gated
  candidates, 5 audits, 1 decision-support freeze). Voided
  cells: **none**; timing violations 0 on every construction.
- New flag: **R11-02** (INV-ABOVE hard-dip exclusion — fails
  (e) by ₹135.40 combined; adoption → 2025 JO ₹80,171.76 /
  2026 JO ₹2,33,708.39 on the starting book; a removal, so it
  composes disjointly with the banked pair). Flagged list now
  carries 25 entries.
- The conditioned-NE-REV standalone question is **closed**:
  the anatomy (R11-05) shows the (e) failure is a 2026
  name-concentration fact with no state separator; the pair
  banking is the assembled cure the anatomy points to.
- The banked book (ending form) is **frozen for December**
  with pre-registered pass/kill lines (R11-07 + R11-08
  addendum).
- Next-round leads (for pre-registration, untested): 2025's
  remaining red months are July (−₹2,101.93) and October
  (−₹3,751.28) on the new book; the flagged R11-02 removal
  remains an owner decision, not an engine banking.
