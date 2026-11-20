# TARANG Round 3 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 18:26 IST, before any Round 3 scoring. No
Round 3 result exists at the time of writing; no parameter below has been
tuned against any Round 3 result.

**Class:** the EKAM-style tuning family for TARANG, Round 3. Rounds 1+2
measured: the trend∩pullback intersection destroys value (R1 NO PASS);
VWAP/EMA trend timing has **no** entry edge on this universe — measured
three times including direction flips (R1 combination, R2 TARANG-B) — and
**no trend-timing variant is built in this round or implied by it**. The
one live ingredient is TARANG-A (pure RSI(7) pullback, no trend
condition): net positive both years, beats its random-entry placebo
median both years and the p90 in 2026, ex-top-3 / month / November /
audit legs all pass — NO PASS by exactly one leg, the **2025
random-entry placebo p90** (A ₹239,391.25 vs p90 ₹260,464.32). Round 1's
diagnosis also measured that the deepest-pullback tercile is the worst
(≈+₹10/trade vs +₹68 shallow): waterfall dips and runaway rallies are
the bad entries. Round 3 tests exactly two diagnosis-driven dials on A —
a validity band on the excursion, and volume confirmation on the
cross-back — each as its own candidate under the full, unmoved gate.

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per 100
shares, ₹40 per completed trade. Paper only, real money ₹0. No stock
options (closed surface). Nothing is armed; no paper run is started; no
live book is touched.

## 1. What is unchanged from TARANG-A (exact)

Everything in `tarang2_SPEC.md` Section 2 (candidate TARANG-A) and the
shared machinery of its Section 1, except the two candidate deltas in
Sections 2–3 below:

- Universe: the frozen 25 names. A labelled TVSMOTOR-excluded
  sensitivity line is reported per candidate; TVSMOTOR is never
  silently dropped.
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` (volume-bearing store,
  complete 2025-01-01 → 2026-11-13, OHLC verified identical to the
  frozen stores).
- Indicators: session VWAP, EMA-50, RSI(7) Wilder — the Round 1
  scorer's disclosed conventions, unchanged. All causal, computed on
  completed bars only. (VWAP/EMA are carried by the machinery; neither
  candidate uses the trend state in any way.)
- Base trigger (TARANG-A): entries from 09:45. LONG: RSI(7) dips to ≤35
  on a completed bar (arming an excursion), then a later completed bar's
  RSI(7) crosses back above 35 → enter LONG at the next bar's open.
  SHORT: mirror at ≥65 / cross back below 65. A fresh excursion is
  required for each entry. An **excursion** is the maximal run of
  completed bars with RSI(7) ≤35 (LONG) / ≥65 (SHORT) within one
  name-day; its **extreme** is the minimum (LONG) / maximum (SHORT)
  RSI(7) over the run; the **cross-back bar** is the first completed bar
  after the run (RSI back above 35 / below 65); the signal fires on the
  cross-back bar and fills at the next bar's open.
- Exits (first hit wins): target +0.8% / stop −0.5% from entry,
  evaluated on completed bars, **stop first** on a bar whose range spans
  both; square-off at the 15:15 bar close if neither is hit.
  Net = side × (exit − entry) × 100 − ₹40.
- Entry fill: next bar's open after the signal bar, same session, fill
  bar time ≥ 09:45 and ≤ 15:15.
- Caps: one open position per name; max 2 entries per name per day; max
  10 entries per day across the book; same-bar contention ordered
  deepest RSI excursion first (depth = 35 − excursion minimum for
  longs, excursion maximum − 65 for shorts, as in A); re-entry after an
  exit allowed subject to the candidate's own signal rule.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the November
  2026 slice reported separately, never pooled into one verdict.

## 2. Candidate TARANG-A2 — validity band on the excursion

- An excursion **counts** only if its extreme stays inside the band:
  - LONG: the dip's minimum RSI(7) must be within **[28, 35]**. If
    RSI(7) falls below 28 at any bar before the cross-back, the
    excursion is **void** — the cross-back produces no entry.
  - SHORT: the rally's maximum RSI(7) must be within **[65, 72]**. If
    RSI(7) rises above 72 before the cross-back, the excursion is void.
- A voided excursion is consumed exactly as a fired one is (the state
  machine resets at its cross-back); a later **fresh** excursion that
  stays in-band can still trigger. Nothing else changes: the base
  trigger thresholds (35/65), the cross-back rule, depth (for the
  tie-break, computed on surviving signals as in A), caps, exits.
- Rationale (pre-registered): skip waterfall dips and runaway rallies —
  the deepest-pullback tercile measured worst in R1 — and keep healthy
  pullbacks.

## 3. Candidate TARANG-A3 — volume confirmation on the cross-back

- A's entry fires only if the **cross-back bar's volume exceeds the
  average volume of the bars that formed the excursion** (the dip bars
  for LONG, the rally bars for SHORT — i.e. the bars of the excursion
  run itself; the cross-back bar is not part of the average).
- If the cross-back bar fails the volume test, that excursion produces
  **no entry** — the state machine resets at that cross-back exactly as
  for a fired signal; there is no waiting for a later bar off the same
  excursion. Nothing else changes.
- Rationale (pre-registered): buyers/sellers returning on the turn —
  the cross-back should arrive on participation, not on drift.

## 4. Controls gate (identical, unmoved, per candidate)

Per `tarang_SPEC.md` Sections 9–10 and
`~/workspace/custom-skills/backtest_controls_gate/SKILL.md`, run in the
same run, before any verdict:

1. **Timing/leak audit (per candidate):** independent recompute of the
   candidate's signal set (separately written state machine — run-based
   segmentation, a different code path from the engine's incremental
   machine); every trade checked — entry after signal, entry exactly at
   the next bar, fill inside the entry window, exit re-simulated
   bar-by-bar and matched, net recomputed, caps (≤2/name/day, ≤10/day),
   no overlapping positions per name. Plus a truncation spot-check
   (RSI(7) recomputed from bars cut at the signal bar must match the
   engine at that bar). Violations must be 0.
2. **Random-entry placebo (per candidate, 200 seeded draws, seed base
   20261118 — the TARANG family's Round 2 base, kept so percentiles are
   read on the same ruler):** same names, same days, **same number of
   entries per day as that candidate took**, random eligible bars
   09:45–14:45, random side, identical exit geometry and caps. The
   candidate must beat the placebo 90th percentile in both years.
3. **Placebo percentile reporting:** for each candidate and year, the
   candidate's percentile within its own 200-draw distribution
   (100 × share of draws with net strictly below the candidate's net),
   reported beside TARANG-A's own percentile within A's Round 2
   distribution (regenerated with the identical machinery and seed
   base, and verified against the stored Round 2 p90/median) — the
   specific question: **did the dial move the 2025 placebo leg that
   failed?**
4. **Direction-flip placebo (information only):** the candidate's exact
   entries with the side flipped.
5. **Splits and stress:** first-half/second-half per year; full month
   table; ex-top-3 per year; max drawdown (cumulative net ordered by
   exit time, overall and per year); side splits (LONG vs SHORT nets
   per year); win rate; trade count; independent re-sum of headline
   nets from the written trades CSV.

## 5. Pass bar (pre-registered, frozen — identical for both candidates)

A candidate PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is reported as
information.

## 6. Discipline

- No other parameter changes: RSI length 7, base trigger thresholds
  35/65, the A2 band edges (28/72) and the A3 volume rule as written
  above, exits +0.8%/−0.5%, and all caps stay frozen for this round.
- **No Round 4 is designed in this run.** If both candidates fail, the
  report states the family position plainly — what three rounds have
  measured about RSI-pullback timing on this universe — and lists the
  remaining untested mechanical ingredients (list only, no builds).
