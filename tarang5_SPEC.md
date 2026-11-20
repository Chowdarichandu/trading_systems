# TARANG Round 5 — Frozen Spec (pre-registered): CORRECTED RE-MEASUREMENT

**Pre-registered:** 2026-11-17 18:50 IST, before any Round 5 scoring.
No Round 5 result exists at the time of writing; no parameter below has
been tuned against any Round 5 or corrected-machinery result for these
four books.

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per 100
shares, ₹40 per completed trade. Paper only, real money ₹0. No stock
options (closed surface). Nothing is armed; no paper run is started; no
live book is touched. Research only.

## 0. Why this round exists — the defect, and what is void

Round 4 (`tarang4_SPEC.md` Section 0, `tarang4_2026-11-17.md` Section 1)
established that the family's shared Rounds 1–3 machinery evaluated
**every exit on 2025-01-01's bars** (day-local bar positions passed into
`simulate_exit` together with full-length price arrays; 4,499 of 4,640
stored TARANG-A exits inconsistent with their own day). Every
exit-dependent number and verdict from Rounds 1–3 is therefore **void
as a measurement**. Entry-side facts survive (indicator computation,
signal generation, entry fills, caps — entries were indexed correctly).

Round 4 re-measured, on corrected machinery, the corrected TARANG-A
baseline and the two new candidates A4/A5. Those three corrected
measurements **stand** and are NOT rescored in this round.

Four books, however, were judged in Rounds 1–3 only through the
defective exit path and have never been measured on a valid ruler:

1. **TARANG R1** (Round 1) — "NO PASS, random beat it."
2. **TARANG-B** (Round 2) — "trend timing is dead."
3. **TARANG-A2** (Round 3) — "the validity-band dial moved backward."
4. **TARANG-A3** (Round 3) — "fixed 2025, missed 2026 by ₹3,341."

All four verdicts are void. This round re-measures those four books
**once**, with their original frozen rules unchanged, on the corrected
machinery. This is a re-measurement, not a tuning round.

## 1. Machinery (frozen — Round 4's corrected machinery, used as-is)

- Exit simulation evaluates each trade's exit path on **that trade's
  own day's bars** (the day's bar arrays sliced by that day's index
  map; local positions inside the slice) — `tarang4_score.py`'s
  `simulate_exit_A_local` (engine path) and `audit_exit_A_loop`
  (independent bar-loop audit path). All four books use the family's
  standard exits: target +0.8% / stop −0.5%, stop first on a both-hit
  bar, else the 15:15 square-off bar's close.
- Book assembly: Round 4's `collect_entries` + `allocate` (depth
  order), which reproduce the original fill rules and caps exactly:
  entry = next bar's open after the signal bar, same session, fill bar
  time in [09:45, 15:15]; one open position per name; max 2 entries
  per name per day; max 10 entries per day across the book; re-entry
  after an exit allowed subject to each book's own signal rule.
- Indicators: session VWAP (typical price × volume, cumulative from
  09:15), EMA-50 (SMA-seeded at bar 50, k = 2/51), RSI(7) Wilder (SMA
  seed) — the family's disclosed conventions in `tarang_score.py`,
  unchanged. All causal, computed on completed bars only.
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` (volume-bearing store,
  complete 2025-01-01 → 2026-11-13, OHLC verified identical to the
  frozen stores in earlier rounds).
- Universe: the frozen 25 names. A labelled TVSMOTOR-excluded
  sensitivity line is reported per book; TVSMOTOR is never silently
  dropped.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the November
  2026 slice reported separately, never pooled into one verdict.

## 2. The four books (original frozen rules, unchanged — no deltas)

1. **TARANG-R1** — `tarang_SPEC.md` Sections 4–8, exactly:
   trend∩pullback. Trend state per bar: UPTREND iff close > VWAP and
   close > EMA-50; DOWNTREND iff close < VWAP and close < EMA-50; else
   no state. LONG: in UPTREND, RSI(7) dips to ≤35 on a completed bar
   (arming), then a later completed bar's RSI(7) crosses back above 35
   while the state is still UPTREND → enter at the next bar's open.
   SHORT: mirror in DOWNTREND (rally ≥65, cross back below 65).
   Leaving the state disarms. A fresh dip/rally is required per entry.
   Depth = 35 − excursion minimum (LONG) / excursion maximum − 65
   (SHORT), for the same-bar tie-break. Engine generator:
   `tarang_score.gen_signals_primary`.
2. **TARANG-B** — `tarang2_SPEC.md` Section 3, exactly: trend-only, no
   RSI condition. A signal fires on the FIRST completed bar of a
   trend-state episode (first bar whose state is UPTREND after a bar
   whose state was not UPTREND → LONG; mirror → SHORT), per name-day,
   prior state "none" at session start. After an exit, re-entry in the
   same name requires the state to have left and re-established
   (transition-only signalling). Engine generator:
   `tarang2_score.gen_signals_trend_establish`.
3. **TARANG-A2** — `tarang3_SPEC.md` Section 2, exactly: TARANG-A's
   pure RSI(7) pullback trigger (no trend condition) plus the
   excursion validity band: a LONG excursion counts only if its
   minimum RSI(7) stays within [28, 35]; a SHORT excursion only if its
   maximum stays within [65, 72]. A voided excursion is consumed at
   its cross-back exactly like a fired one; a later fresh in-band
   excursion can still trigger. Engine generator:
   `tarang3_score.gen_signals_A2`.
4. **TARANG-A3** — `tarang3_SPEC.md` Section 3, exactly: TARANG-A's
   trigger plus volume confirmation: the entry fires only if the
   cross-back bar's volume exceeds the mean volume of the excursion's
   own bars. A failed test consumes the excursion — no later bar off
   the same excursion can fire. Engine generator:
   `tarang3_score.gen_signals_A3`.

## 3. Controls gate (identical, unmoved, per book — on corrected machinery)

Per `tarang_SPEC.md` Sections 9–10, `tarang4_SPEC.md` Section 4 and
`~/workspace/custom-skills/backtest_controls_gate/SKILL.md`, run in the
same run, before any verdict:

1. **Pre-scoring machinery checks (per book):** (a) the engine
   generator's full signal set is compared against an independently
   written validator (different code path: a separately written state
   machine for R1 and B; run-based excursion segmentation for A2 and
   A3) — sets and depths must match exactly; (b) the book's taken-trade
   ENTRY multiset (sym, date, side, entry time, entry price) is
   compared against the stored Rounds 1–3 trades CSV for that book —
   entries were correctly indexed in those rounds, so the multisets
   must match exactly. **If either check disagrees, STOP and report —
   do not score on a disputed ruler.**
2. **Timing/leak audit (per book):** independent recompute of the
   signal set (the Section 3.1 validators); every trade checked —
   entry after signal, entry exactly at the next bar, fill inside the
   entry window, exit re-simulated bar-by-bar **on the trade's own
   day's bars** by the independent bar-loop implementation and
   matched, net recomputed, caps (≤2/name/day, ≤10/day), no
   overlapping positions per name. Plus the square-off regression
   check: every square-off exit's price must equal its own day's
   square-off-bar close (the check that exposed the defect). Plus a
   truncation spot-check (indicators recomputed from bars cut at the
   signal bar must match the engine at that bar: state/VWAP/RSI for
   R1, state/VWAP for B, RSI for A2/A3). Violations must be 0.
3. **Random-entry placebo (per book, 200 seeded draws, seed base
   20261118 — the family base, kept so percentiles are read on the
   same ruler):** same names, same days, **same number of entries per
   day as that book took**, random eligible bars 09:45–14:45, random
   side, identical caps, the standard exits on corrected indexing. The
   book must beat the placebo 90th percentile in both years.
   Percentile = 100 × share of draws with net strictly below the
   book's net.
4. **Direction-flip placebo (information only):** the book's exact
   entries with the side flipped, standard exits, corrected indexing.
5. **Splits and stress:** first-half/second-half per year; full month
   table; ex-top-3 per year; max drawdown (cumulative net ordered by
   exit time, overall and per year); side splits (LONG vs SHORT nets
   per year); win rate; trade count; independent re-sum of headline
   nets from the written trades CSV.

## 4. Pass bar (pre-registered, frozen — identical for all four books)

A book PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in **both**
  years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is reported as
information.

## 5. Discipline

- **Re-measurement only:** no parameter changes, no new variants, no
  new dials. RSI length 7, thresholds 35/65, A2's band [28,35]/[65,72],
  A3's volume rule, exits +0.8%/−0.5%, caps, window — all exactly as
  frozen in the books' own specs.
- The corrected TARANG-A baseline and TARANG-A4/A5 from Round 4 stand
  as measured and are **not** rescored here.
- **No Round 6 is designed in this run.** If a book PASSES on corrected
  machinery, it is reported plainly as a forward-paper candidate for
  the owner's decision — nothing is started. If all four fail, the
  family summary states what is now honestly measured about every
  ingredient (trend timing, validity band, volume veto, the
  trend∩pullback combination) and that the TARANG family has no
  gate-passing book.
