# TARANG Design 9 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 9 scoring. No
Design 9 result exists at the time of writing; no parameter below
has been tuned against any Design 9 result.

**Programme note (owner's standing mandate):** the TARANG programme
CONTINUES — designs iterate from diagnosis until a gate pass or the
owner's stop. Design 9 is the direct continuation of Design 8,
seeded by Design 8's own diagnosis (`tarang8_2026-11-17.md`
Section 4):

> *Entry timing is exonerated as the binding constraint. Two
> different confirmations (Design 7's one-bar tick, Design 8's
> demonstrated re-cross) produce the same resolution mix (~62%
> stop-first) and the same broad losses. Every book-year is
> GROSS-positive per trade (+₹5.75 … +₹25.67) — the entry stream
> carries a small real edge that two untouched constants convert
> into net losses: (a) the frozen +0.8%/−0.5% exit geometry, whose
> payoff ratio (~1.44) needs a ~41% win rate no reversion stream
> delivers (37–40% across Designs 7–8), and (b) the ₹40/trade cost
> levied 4,640 times because the book saturates its 10/day cap.
> T8-Q (quiet-priority allocation) is a real second-order dial:
> +₹18,941/+₹41,639 vs T8 on the identical pool, 2026 placebo
> percentile 96.0, the family's first positive November slice.*

Design 9 therefore changes NOTHING on the entry side — entries are
frozen as T8-Q exactly — and attacks the two constants the
diagnosis names: the exit geometry (both books) and the cost term
via selectivity (T9-B only).

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per
100 shares, ₹40 per completed trade. Paper only, real money ₹0. No
stock options (closed surface). Nothing is armed; no paper run is
started; no live book is touched.

## 1. Universe and data (unchanged from Designs 6–8)

- Universe: the SAME 127 verified names of Round 6 — liquid +
  Nifty 100 / Nifty Midcap 150 member + F&O segment + ₹2,000 cap at
  selection, verification-passed (`tarang6_verify.json`: 127 names).
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` for the 21
  qualifying incumbents, `data/tarang_wide_vol/<SYM>/spot_5m_vol.csv`
  for the rest — the Round 6 verified volume-bearing stores,
  2025-01-01 → 2026-11-13. No new fetch, no new verification round.
- Indicators: Design 7's frames, imported unchanged
  (`tarang7_score.load_data7` / `add_bb_macd`) — Bollinger(20, 2)
  with POPULATION sd on the continuous 5-minute close series
  (mid = 20-bar SMA of close), MACD(12, 26, 9) with the family's
  SMA-seeded EMAs. Design 9 reads byte-identical indicator values
  to Designs 7–8.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the
  November 2026 slice reported separately, never pooled into one
  verdict.

## 2. Entries — FROZEN as T8-Q exactly

- Signal generation is Design 8's, imported unchanged
  (`tarang8_score.gen_signals_T8`): a beyond-band close arms a
  setup at its excursion's snap bar; a signal fires only on the
  band RE-CROSS — the first subsequent bar of the session closing
  back INSIDE the band, within 10 bars of the snap bar, with the
  MACD histogram still rising into the turn (LONG; mirrored
  SHORT). Allocation fields as Design 8: depth from the snap bar;
  vol_ratio = signal-bar volume ÷ mean volume of the 20 bars
  ending at the snap bar.
- Fill: the open of the next bar after the signal bar, same
  session, fill time in [09:45, 14:30] (Design 8's
  `collect_entries8`, imported unchanged).
- Allocation ranking: T8-Q's QUIET-priority — vol_ratio ASCENDING,
  then depth descending, then signal time, then symbol — for both
  Design 9 books. The books differ only in the day cap and the
  T9-B pre-selection (Section 4).

## 3. Exits — NEW geometry (the first exit change in the family)

Evaluated on the trade's OWN day's bars (the Round 4 corrected
indexing), scanning from the entry bar through the square-off bar
(the last bar at or before 15:15), first hit wins:

- **Target — the mid-band touch.** LONG: the first bar whose HIGH
  reaches that bar's own Bollinger mid-band value (bb_mid at that
  bar, the 20-period SMA of the continuous close series) exits at
  that mid-band price. SHORT mirrored: the first bar whose LOW
  reaches that bar's mid-band value exits at that mid-band price.
  Exit reason `target_mid`.
- **Disaster stop.** LONG: entry × 0.985 (−1.5%); SHORT: entry ×
  1.015 (+1.5%). A bar touching the stop exits at the stop price.
  Exit reason `stop`.
- **Both-hit bar:** if one bar touches BOTH the stop and the
  mid-band, the STOP fills first (stop-first convention).
- **Square-off:** if neither is touched through the square-off
  bar, exit at the square-off bar's close. Exit reason `squareoff`.
- A bar whose mid-band is undefined (series warm-up only; cannot
  occur after a valid signal, whose bands are defined) cannot
  register a target touch.
- Net = side × (exit − entry) × 100 − ₹40.

## 4. The two books

- **TARANG-T9-A** — T8-Q entries and quiet allocation exactly,
  day cap 10, with the Section 3 exits. The single new variable
  against T8-Q is the exit geometry.
- **TARANG-T9-B** — T9-A plus SELECTIVITY against the cost term:
  before allocation, each day's candidate entries are ranked by
  the quiet key (vol_ratio ascending — the family's signal-bar
  volume measure, as in T8-Q — ties by depth descending, then
  signal time, then symbol) and only the day's THREE strongest are
  eligible; allocation then proceeds chronologically over the
  eligible set with a day cap of 3. A pre-selected signal that
  cannot be taken (occupancy / per-name caps) is NOT replaced by
  the day's fourth signal — the three are the day's three.

Caps (both books, unchanged): one open position per name; max 2
entries per name per day; re-entry after an exit allowed.

## 5. Controls gate (identical, unmoved, per book)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6/7/8 audit
stack, and `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`,
run in the same run, before any verdict:

1. **Timing/leak audit (per book):** engine-vs-validator signal
   parity before scoring (Design 8's vectorised validator,
   imported unchanged — entries are frozen, so the parity result
   must reproduce Design 8's: 147,718 signals, 0 mismatches).
   Every trade checked — entry after signal, entry exactly at the
   next bar, fill inside [09:45, 14:30], exit re-simulated
   bar-by-bar on the trade's own day by an INDEPENDENT bar-loop
   implementation of the Section 3 exits (separately written from
   the engine's vectorised exit) and matched (bar, price, reason —
   including the mid-band price at the exit bar), square-off price
   equal to its own day's square-off-bar close (the regression
   check that exposed the Rounds 1–3 defect), net recomputed,
   caps (≤2/name/day, ≤ day cap/day), no overlapping positions per
   name, each trade's vol_ratio / depth / snap bar recomputed
   independently and matched, and the whole book rebuilt by an
   independently written allocator (validator signals + the book's
   ranking and pre-selection + bar-loop exits) and matched
   trade-for-trade. Plus a truncation spot-check: Bollinger bands
   (lo / mid / up) and MACD histogram recomputed from bars cut at
   the signal bar — and the bands from bars cut at the snap bar —
   must match the engine at those bars. Violations must be 0.
2. **Random-entry placebo (per book, 200 seeded draws, seed base
   20261118 — the family base):** same names, same days, same
   number of entries per day as that book took, random eligible
   bars 09:45–14:45 (the family's placebo window), random side,
   identical caps, and the Section 3 exits, all on corrected
   indexing. The book must beat the placebo 90th percentile in
   both years.
3. **Placebo percentile reporting:** per book and year, the book's
   percentile within its own 200-draw distribution.
4. **Direction-flip placebo (information only):** the book's exact
   entries with the side flipped, under the Section 3 exits.
5. **Splits and stress:** first-half/second-half per year; full
   month table; ex-top-3 per year; max drawdown (overall and per
   year); side splits (LONG vs SHORT nets per year); win rate;
   trade count; top-10 contributors per year; **the resolution
   mix — target-mid / disaster-stop / square-off counts, nets and
   shares per year**; **the cost anatomy — gross per trade, cost
   per trade, net per trade per book-year** (gross = net +
   ₹40 × trades); independent re-sum of headline nets from the
   written trades CSV.

## 6. Pass bar (pre-registered, frozen — per book)

A book PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in **both**
  years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is
reported as information.

## 7. Discipline

- No other parameter changes: the T8-Q signal set, ranking and
  fill rules, Bollinger (20, 2), MACD (12, 26, 9), the 10-bar
  re-cross window, the [09:45, 14:30] entry window, caps,
  universe, window — all frozen for this design. The only new
  variables are the Section 3 exits (both books) and the T9-B
  top-3 pre-selection.
- A PASS makes the book a forward-paper CANDIDATE for the owner's
  decision; nothing is armed or started by this run either way.
- Whatever the verdicts, the report closes with the diagnosis that
  seeds Design 10, in two lines: what specifically failed —
  evidenced from this run's splits, including whether the
  mid-band exit moved the resolution mix and whether the gross
  edge survives its cost at 3 entries/day.
