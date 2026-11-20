# TARANG Design 8 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 8 scoring. No
Design 8 result exists at the time of writing; no parameter below has
been tuned against any Design 8 result.

**Programme note (owner's standing mandate):** the TARANG programme
CONTINUES — designs iterate from diagnosis until a gate pass or the
owner's stop. Design 8 is the direct continuation of Design 7, seeded
by Design 7's own diagnosis (`tarang7_2026-11-17.md` Section 4):

> *What failed in Design 7 is ENTRY TIMING. The one-bar histogram
> tick confirms nothing: after a beyond-band close, price continues
> in the same direction more often than it snaps — 63% of resolved
> trades stopped (−0.5%) before targeting, while the trades that
> merely drifted (square-offs) were net positive both years. The
> entries fire mid-move, one bar after the extreme, before any
> actual turn exists. And on reversion entries the volume dial runs
> backwards: quiet snaps revert, violent ones continue (T7-V's veto
> inverted by year).*

Design 8 changes ONLY the entry confirmation and adds ONE
allocation-side book carrying the inverted volume dial. The exit
geometry, caps, universe, data and gate are carried over from
Design 7 unchanged, so the entry confirmation is the single new
variable against Design 7, and the allocation direction is the
single difference between the two Design 8 books.

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per
100 shares, ₹40 per completed trade. Paper only, real money ₹0. No
stock options (closed surface). Nothing is armed; no paper run is
started; no live book is touched.

## 1. Universe and data (unchanged from Designs 6–7)

- Universe: the SAME 127 verified names of Round 6 — liquid + Nifty
  100 / Nifty Midcap 150 member + F&O segment + ₹2,000 cap at
  selection, verification-passed (`tarang6_verify.json`: 127 names).
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` for the 21
  qualifying incumbents, `data/tarang_wide_vol/<SYM>/spot_5m_vol.csv`
  for the rest — the Round 6 verified volume-bearing stores,
  2025-01-01 → 2026-11-13. No new fetch, no new verification round.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the
  November 2026 slice reported separately, never pooled into one
  verdict.

## 2. Indicators (unchanged from Design 7, Section 2)

Computed on the continuous 5-minute close series per name (causal,
seeded once at the head of the series, never reset per session). All
values use completed bars only.

- **Bollinger(20, 2):** mid = mean of the last 20 closes; sd =
  POPULATION standard deviation (ddof=0) of the same 20 closes;
  upper = mid + 2·sd; lower = mid − 2·sd. Defined from bar 19.
- **MACD(12, 26, 9):** EMA-12 / EMA-26 of close, each SMA-seeded
  (the family's convention); MACD line = EMA-12 − EMA-26 (from bar
  25); signal line = EMA-9 of the MACD line, SMA-seeded (from bar
  33); histogram = MACD line − signal line (from bar 33).
- The indicator frames are produced by Design 7's own loader
  (`tarang7_score.load_data7` / `add_bb_macd`), imported unchanged,
  so Design 8 reads byte-identical indicator values to Design 7.

## 3. Entry logic — band re-cross confirmation (the fix)

Per name, per session, bars in order. All band tests read a bar's
own close against its own bands:

- A bar is **beyond-low** if close < lower band, **beyond-high** if
  close > upper band, **inside** if lower ≤ close ≤ upper. A bar
  whose bands are undefined (series warm-up only) is **inert**: it
  arms nothing, confirms nothing, and leaves any active setup's
  state unchanged.
- An **excursion** is a maximal run of consecutive same-side
  beyond closes within a session. Its first bar is the **snap
  bar** `a`: a beyond bar whose previous bar of the same session
  was NOT beyond on the same side (the first bar of a session, if
  beyond, is a snap bar). The snap bar **arms a setup** of its side.
  The histogram is NOT read at the snap bar.
- The setup stays active while the excursion continues. It ends at
  the first bar after `a` that is not beyond on the setup's side:
  - **Re-cross bar `r`** — that bar closes **inside** the band. A
    **signal** fires at `r` iff BOTH hold:
    1. `r − a ≤ 10` (bar distance within the session), and
    2. the MACD histogram is still rising into the turn — LONG:
       hist[r] > hist[r−1]; SHORT: hist[r] < hist[r−1] — where
       r−1 is the previous bar of the same session and both
       histogram values are defined.
    Whether or not the signal fires, the re-cross spends the
    setup: an inside close without the histogram condition (or
    beyond the 10-bar window) arms nothing further.
  - **Opposite beyond close** — that bar closes beyond the
    OPPOSITE band before any inside close: the setup ends unfilled
    and that bar is itself the snap bar of an opposite-side setup.
  - **Expiry** — if the excursion is still beyond on the setup's
    side at bar distance `r − a > 10`, the setup expires unfilled;
    the continuing excursion arms nothing further (a later signal
    needs a fresh excursion after an inside close).

Each signal carries two allocation fields, defined exactly as in
Design 7 with `a` = the snap bar and `r` = the signal (re-cross)
bar:

- **vol_ratio** = volume at the signal bar `r` ÷ mean volume of the
  20 bars ending at the snap bar `a` (bars a−19…a of the continuous
  series; the snap bar's bands are defined, so a ≥ 19 and the full
  20 bars exist). If that mean is 0, the ratio is 0.
- **depth** = the snap close's penetration beyond the band, in % of
  the snap close: LONG: (lower[a] − close[a]) / close[a] × 100;
  SHORT: (close[a] − upper[a]) / close[a] × 100. Strictly positive
  by construction.

**Fill:** the open of the next bar (`r + 1`), same session — the
family's fill convention. The fill bar's time must be ≥ 09:45 and
≤ **14:30** (the frozen entry window; no position is opened inside
the final 45 minutes). A setup whose re-cross would fill after
14:30 is simply not taken; the 14:30 bound is the fill bound, as in
Design 7.

## 4. The two books — allocation is the only difference

Book assembly is chronological by fill bar, with the family's caps
and occupancy (Section 5). Within the group of candidate entries
filling at the same bar, the ranking is:

- **TARANG-T8** — A4 volume-priority, exactly as Designs 4–7:
  vol_ratio **descending**, then depth descending, then signal
  time, then symbol.
- **TARANG-T8-Q** — QUIET-priority, the reversed dial Design 7's
  diagnosis points to: vol_ratio **ascending** (the identical
  field T8 ranks descending — the signal bar's volume relative to
  the 20-bar mean ending at the snap bar), then depth descending,
  then signal time, then symbol.

T8-Q differs from T8 ONLY in the direction of the vol_ratio ranking
key. Signal sets, fills, caps and exits are identical; the two books
will generally take different trades only where the 10/day cap
binds and the ranking decides which competing signals get slots.

## 5. Caps and exits (frozen, unchanged from Design 7)

- **Caps:** one open position per name; max 2 entries per name per
  day; max 10 entries per day across the book; re-entry after an
  exit allowed.
- **Exits (the family's standard geometry):** +0.8% target / −0.5%
  stop, stop first on a both-hit bar, else the 15:15 square-off
  bar's close — evaluated on the trade's OWN day's bars (the Round 4
  corrected indexing). LONG stop = entry × 0.995, target = entry ×
  1.008; SHORT mirrored.
- Net = side × (exit − entry) × 100 − ₹40.

## 6. Controls gate (identical, unmoved, per book)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6/7 audit stack,
and `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`,
run in the same run, before any verdict:

1. **Timing/leak audit (per book):** independent recompute of the
   book's signal set by a separately written VECTORISED validator
   (excursions segmented by run-start markers and forward-filled
   snap indices — a different code path from the engine's per-day
   state machine); before scoring, the engine and validator signal
   sets must agree exactly on every name (counts, sides, depths,
   vol_ratios). Every trade checked — entry after signal, entry
   exactly at the next bar, fill inside the entry window
   [09:45, 14:30], exit re-simulated bar-by-bar on the trade's own
   day's bars by the independent bar-loop exit and matched,
   square-off price equal to its own day's square-off-bar close
   (the regression check that exposed the Rounds 1–3 defect), net
   recomputed, caps (≤2/name/day, ≤10/day), no overlapping
   positions per name, each trade's vol_ratio and depth recomputed
   independently (from the validator's own snap bar) and matched,
   and the whole book rebuilt by an independently written allocator
   (validator signals + that book's Section 4 ranking + bar-loop
   exits) and matched trade-for-trade. Plus a truncation
   spot-check: Bollinger bands and MACD histogram recomputed from
   bars cut at the signal bar — and the bands from bars cut at the
   snap bar — must match the engine at those bars. Violations must
   be 0.
2. **Random-entry placebo (per book, 200 seeded draws, seed base
   20261118 — the family base):** same names, same days, same
   number of entries per day as that book took, random eligible
   bars 09:45–14:45 (the family's placebo window), random side,
   identical caps, and the frozen exits of Section 5, all on
   corrected indexing. The book must beat the placebo 90th
   percentile in both years.
3. **Placebo percentile reporting:** per book and year, the book's
   percentile within its own 200-draw distribution.
4. **Direction-flip placebo (information only):** the book's exact
   entries with the side flipped, under the frozen exits.
5. **Splits and stress:** first-half/second-half per year; full
   month table; ex-top-3 per year; max drawdown (overall and per
   year); side splits (LONG vs SHORT nets per year); win rate;
   trade count; top-10 contributors per year; **the resolution
   mix — stop / target / square-off counts and nets per year, and
   the stop share of resolved (stop+target) trades, the Design 7
   diagnosis metric**; independent re-sum of headline nets from
   the written trades CSV.

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
  the 10-bar re-cross window, the [09:45, 14:30] entry window, the
  two rankings of Section 4, the frozen exits, caps, universe,
  window — all frozen for this design.
- A PASS makes the book a forward-paper CANDIDATE for the owner's
  decision; nothing is armed or started by this run either way.
- Whatever the verdicts, the report closes with the diagnosis that
  seeds Design 9, in two lines: what specifically failed — entry
  timing, exit geometry, or name mix — evidenced from this run's
  splits, including whether the re-cross confirmation moved the
  63% stop-first rate.
