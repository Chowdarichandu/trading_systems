# TARANG Design 7 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 7 scoring. No
Design 7 result exists at the time of writing; no parameter below has
been tuned against any Design 7 result.

**Programme note (owner's correction, 2026-11-17 20:41 IST):** the
TARANG programme CONTINUES. Designs 1–6 measured one entry geometry —
RSI(7) pullback — and it loses on every universe tested (frozen 25,
liquid-100, the owner's F&O 127, the 2025-screened 10; see
`tarang6_2026-11-17.md`). A failed geometry changes the DESIGN; it does
not end the programme. Design 7 changes ONLY the entry logic. The exit
geometry, the A4 volume-priority allocation, the caps, the universe and
the gate are carried over unchanged, so the entry logic is the single
new variable against Designs 1–6.

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per 100
shares, ₹40 per completed trade. Paper only, real money ₹0. No stock
options (closed surface). Nothing is armed; no paper run is started; no
live book is touched.

## 1. Universe and data (unchanged from Round 6)

- Universe: the SAME 127 verified names of Round 6 — liquid + Nifty
  100 / Nifty Midcap 150 member + F&O segment + ₹2,000 cap at
  selection, verification-passed (`tarang6_verify.json` /
  `tarang6_screen.json`: 127 names, identical sets).
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` for the 21 qualifying
  incumbents, `data/tarang_wide_vol/<SYM>/spot_5m_vol.csv` for the
  rest — the Round 6 verified volume-bearing stores, 2025-01-01 →
  2026-11-13. No new fetch, no new verification round; Round 6's
  verification stands.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the November
  2026 slice reported separately, never pooled into one verdict.

## 2. Indicators (new in Design 7; conventions frozen here)

Computed on the continuous 5-minute close series per name (the family's
treatment for EMA-50 / RSI(7): causal, seeded once at the head of the
series, never reset per session). All values use completed bars only.

- **Bollinger(20, 2):** mid = mean of the last 20 closes (bars
  k−19…k); sd = POPULATION standard deviation (ddof=0) of the same 20
  closes; upper = mid + 2·sd; lower = mid − 2·sd. Defined from bar 19.
- **MACD(12, 26, 9):** EMA-12 and EMA-26 of close, each SMA-seeded
  (EMA-12 seed = mean of first 12 closes at bar 11, k = 2/13; EMA-26
  seed = mean of first 26 closes at bar 25, k = 2/27) — the family's
  EMA-50 seeding convention. MACD line = EMA-12 − EMA-26, defined from
  bar 25. Signal line = EMA-9 of the MACD line, SMA-seeded (mean of
  the first 9 MACD values, bars 25…33, at bar 33, k = 2/10).
  Histogram = MACD line − signal line, defined from bar 33.
- RSI(7), VWAP and EMA-50 are NOT used by Design 7's entries (they
  remain in the loaded frame only because the shared loader computes
  them; no Design 7 rule reads them).

## 3. Entry logic — mean-reversion snap (the new variable)

Per name, per session, bars in order. Let bar `a` be a completed bar
and bar `k` the NEXT bar of the SAME session (`k = a + 1` within the
session; the first bar of a session has no predecessor and can never
be a signal bar).

- **LONG signal at bar `k`** iff BOTH hold:
  1. close[a] < Bollinger lower band at bar `a` (a close strictly
     below the lower band), and
  2. MACD histogram ticks UP at bar `k`: hist[k] > hist[a].
- **SHORT signal at bar `k`** iff BOTH hold:
  1. close[a] > Bollinger upper band at bar `a`, and
  2. MACD histogram ticks DOWN at bar `k`: hist[k] < hist[a].
- Each beyond-band close arms exactly ONE chance — the immediately
  following bar. There is no latching: if the histogram does not tick
  the right way at `k`, that arm is spent (a later signal needs a
  fresh beyond-band close at its own preceding bar — which a continued
  beyond-band close itself supplies, since the rule reads only the
  single preceding bar).
- Bars with undefined Bollinger or histogram values (warm-up) can
  neither arm nor signal.
- The signal bar is `k` (the confirmation bar). **Fill:** the open of
  the next bar (`k + 1`), same session — the family's fill convention.
  The fill bar's time must be ≥ 09:45 and ≤ **14:30** (Design 7's
  entry window; entries after 14:30 are not taken, so no position is
  opened inside the final 45 minutes).

Each signal carries two allocation fields, defined here (the Design 7
analogues of A4's volume ratio and depth):

- **vol_ratio** = volume at the signal bar `k` ÷ mean volume of the 20
  bars ending at the arming bar `a` (bars a−19…a). If that mean is 0,
  the ratio is 0.
- **depth** = the arming close's penetration beyond the band, in % of
  the arming close: LONG: (lower[a] − close[a]) / close[a] × 100;
  SHORT: (close[a] − upper[a]) / close[a] × 100. Strictly positive by
  construction.

## 4. Book assembly — A4 allocation, frozen exits (unchanged)

- **Allocation:** A4 volume-priority, exactly as `tarang4_SPEC.md`
  Section 2 with Design 7's fields: candidate entries are processed
  chronologically by fill bar; within the group filling at the same
  bar, order is vol_ratio descending, then depth descending, then
  signal time, then symbol. Every qualifying signal is eligible;
  nothing is vetoed in the base book.
- **Caps:** one open position per name; max 2 entries per name per
  day; max 10 entries per day across the book; re-entry after an exit
  allowed.
- **Exits (frozen, the family's standard geometry):** +0.8% target /
  −0.5% stop, stop first on a both-hit bar, else the 15:15 square-off
  bar's close — evaluated on the trade's OWN day's bars (the Round 4
  corrected indexing; `tarang4_score` exit paths). LONG stop =
  entry × 0.995, target = entry × 1.008; SHORT mirrored.
- Net = side × (exit − entry) × 100 − ₹40.

## 5. The one variant — TARANG-T7-V (volume veto)

Identical to the base book in every rule except entry eligibility:

- A signal is **vetoed** (never enters the candidate pool) iff the
  signal bar's volume is strictly below its 20-bar median volume,
  where the median is over the 20 bars immediately preceding the
  signal bar (bars k−20…k−1 of the name's continuous series; causal,
  excludes the signal bar itself).
- Disclosure: a volume veto was measured negatively inside the
  pullback family (TARANG-A3, corrected Round 5). It has never been
  measured on reversion entries. T7-V is a FRESH measurement on a new
  entry logic, not a retest of A3.

The two books — **TARANG-T7** (base) and **TARANG-T7-V** — are gated
separately.

## 6. Controls gate (identical, unmoved, per book)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6 audit stack, and
`~/workspace/custom-skills/backtest_controls_gate/SKILL.md`, run in the
same run, before any verdict:

1. **Timing/leak audit (per book):** independent recompute of the
   book's signal set by a separately written vectorised validator
   (different code path from the engine's per-day loop); every trade
   checked — entry after signal, entry exactly at the next bar, fill
   inside the entry window [09:45, 14:30], exit re-simulated
   bar-by-bar on the trade's own day's bars by the independent
   bar-loop exit and matched, square-off price equal to its own day's
   square-off-bar close (the regression check that exposed the Rounds
   1–3 defect), net recomputed, caps (≤2/name/day, ≤10/day), no
   overlapping positions per name, each trade's vol_ratio and depth
   recomputed independently and matched, and the whole book rebuilt by
   an independently written allocator (validator signals + Section 4
   ranking + bar-loop exits) and matched trade-for-trade. Plus a
   truncation spot-check: Bollinger and MACD histogram recomputed from
   bars cut at the signal bar must match the engine at that bar.
   Violations must be 0.
2. **Random-entry placebo (per book, 200 seeded draws, seed base
   20261118 — the family base):** same names, same days, same number
   of entries per day as that book took, random eligible bars
   09:45–14:45 (the family's placebo window, kept so percentiles read
   on the same ruler as Rounds 4–6), random side, identical caps, and
   the frozen exits of Section 4, all on corrected indexing. The book
   must beat the placebo 90th percentile in both years.
3. **Placebo percentile reporting:** per book and year, the book's
   percentile within its own 200-draw distribution.
4. **Direction-flip placebo (information only):** the book's exact
   entries with the side flipped, under the frozen exits.
5. **Splits and stress:** first-half/second-half per year; full month
   table; ex-top-3 per year; max drawdown (cumulative net ordered by
   exit time, overall and per year); side splits (LONG vs SHORT nets
   per year); win rate; trade count; top-10 contributors per year;
   independent re-sum of headline nets from the written trades CSV.

## 7. Pass bar (pre-registered, frozen — per book)

A book PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in **both**
  years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is reported
as information.

## 8. Discipline

- No other parameter changes: Bollinger (20, 2), MACD (12, 26, 9),
  the one-bar arm, the [09:45, 14:30] entry window, A4's ranking, the
  frozen exits, caps, universe, window — all frozen for this design.
- A PASS makes the book a forward-paper CANDIDATE for the owner's
  decision; nothing is armed or started by this run either way.
- Whatever the verdicts, the report closes with the diagnosis that
  seeds Design 8: what specifically failed — entry timing, exit
  geometry, or name mix — evidenced from this run's splits.
