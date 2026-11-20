# TARANG Design 14 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 14
scoring. No Design 14 result exists at the time of writing; no
parameter below has been tuned against any Design 14 result.

**Programme note (owner's standing mandate):** the TARANG
programme CONTINUES — designs iterate from diagnosis until a
gate pass or the owner's stop. Design 14 is the direct
continuation of Design 13, seeded by Design 13's own diagnosis
(`tarang13_2026-11-17.md` Sections 2 and 5):

> *The snap-reversion arithmetic is closed at every count.
> Thirteen designs varied entries, exits, side, selectivity,
> allocation and count, and the family's gross ceiling stands
> at +₹26.90 per trade against a ₹40 levy no configuration
> escapes in both years. What thirteen designs of reversion
> books kept leaving behind as a profitable residue is the
> trades that never reverted: the drift to the close. T13's
> square-offs — positions that hit neither target nor stop
> and simply rode to 15:15 — are net positive after the full
> levy in both years (91 trades +₹8,172.00 in 2025; 45 trades
> +₹3,758.00 in 2026; +₹87–90 per trade), and Design 12's
> delay measurement said the same thing from the other side:
> after the re-cross, the aftermath runs WITH the excursion,
> not against it.*

Design 14 therefore **leaves the snap-reversion stream
itself** and trades the stream the evidence points to:
**continuation**. The same Bollinger excursions, read as
information about direction rather than exhaustion — traded
in the excursion's OWN direction and held toward the close,
the geometry the profitable square-off residue of thirteen
designs has been tracing all along. The pre-registered,
decisive question of this design: **does the continuation
stream's gross per trade clear the ₹40 levy in both years** —
the line every reversion configuration failed?

**Basis (labelled everywhere):** equity cash only,
PROVISIONAL per 100 shares, ₹40 per completed trade. Paper
only, real money ₹0. No stock options (closed surface).
Nothing is armed; no paper run is started; no live book is
touched.

## 1. Universe and data (unchanged from Designs 6–13)

- Universe: the SAME 127 verified names of Round 6 — liquid +
  Nifty 100 / Nifty Midcap 150 member + F&O segment + ₹2,000
  cap at selection, verification-passed (`tarang6_verify.json`).
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` for the 21
  qualifying incumbents, `data/tarang_wide_vol/<SYM>/spot_5m_vol.csv`
  for the rest — the Round 6 verified volume-bearing stores,
  2025-01-01 → 2026-11-13. No new fetch.
- Indicators: Design 7's frames, imported unchanged
  (`tarang7_score.load_data7` / `add_bb_macd`) — Bollinger
  (20, 2) with POPULATION sd on the continuous 5-minute close
  series, MACD (12, 26, 9) with the family's SMA-seeded EMAs.
  Design 14 reads the bands only; the MACD frame is carried
  for the shared data path and the truncation spot-check.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the
  November 2026 slice reported separately, never pooled into
  one verdict.

## 2. The signal — the excursion itself, traded WITH it

- A bar is **beyond-high** if close > upper band, **beyond-low**
  if close < lower band, **inside** if lower ≤ close ≤ upper;
  a bar with undefined bands is inert (and breaks a run, as in
  the reversion family's state machine). An **excursion** is a
  maximal run of consecutive same-side beyond closes within a
  session; its first bar is the **excursion bar** `a` — the
  reversion family's snap bar, identically defined.
- **The signal fires AT the excursion bar `a`.** There is no
  confirmation bar, no re-cross, and the MACD histogram is NOT
  read. Direction is WITH the excursion: beyond-high → **LONG**
  (+1); beyond-low → **SHORT** (−1). (This is the exact
  opposite side from the reversion family's trade on the same
  bar — Designs 7–13 faded this bar; Design 14 follows it.)
  Later bars of the same excursion run do not re-fire; a new
  excursion (after an inside close, or an opposite beyond
  close) fires a new signal.
- **Freshness (T12-B's lesson, binding):** the fill is the
  open of bar `a+1` — one bar after the excursion close,
  inside the 5-bar freshness bound this programme measured in
  Design 12 (delay destroys this family's gross; T12's two-bar
  confirmation and the freshness window both pointed the same
  way). The fill is NEVER deferred: a candidate whose `a+1`
  fill falls in another session or outside the fill window is
  dropped, not postponed to a later bar. The audit counts the
  entry lag of every trade (must be exactly 1, hence ≤ 5).
- **Fill window:** [09:45, 14:30], same session as the signal.
- **Allocation fields:** **depth** = the excursion close's
  penetration beyond the band in % of the excursion close
  (LONG: (close − upper) / close × 100; SHORT: (lower −
  close) / close × 100); **vol_ratio** = volume at the
  excursion bar ÷ mean volume of the 20 bars ending at the
  excursion bar (0 if that mean is 0) — A4's field
  construction with the signal bar equal to the excursion bar.

## 3. Allocation — A4 volume-priority (the family's original dial)

Candidate entries are processed in (date, entry_time,
vol_ratio DESCENDING, depth descending, signal_time, symbol)
order — A4's ranking, exactly as in Designs 4–8 (the
vol-ratio-descending path of the shared allocator). Caps:
one open position per name (occupancy to the exit bar);
max 2 entries per name per day; max 10 entries per book per
day; re-entry after an exit allowed.

## 4. Exits — held toward the close

Evaluated on the trade's OWN day's bars (the Round 4
corrected indexing), scanning from the entry bar to the
square-off bar inclusive; a stop (and target) fills AT its
level price on the first bar whose range touches it.

- **TARANG-T14-A (the residue geometry):** a −1.0% disaster
  stop only (LONG: entry × 0.99; SHORT: entry × 1.01);
  otherwise the position rides to the **15:15 square-off
  bar's close**. No target.
- **TARANG-T14-B:** T14-A plus a **+1.25% runner target**
  (LONG: entry × 1.0125; SHORT: entry × 0.9875). First hit
  wins; on a bar touching both stop and target, the **stop
  fills first** (the family's stop-first convention).
- Net = side × (exit − entry) × 100 − ₹40. Exit reasons:
  `stop`, `target` (T14-B only), `squareoff`.

## 5. Controls gate (identical stack, unmoved)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6/7/8 audit
stack, and `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`,
run in the same run, before any verdict:

1. **Pre-scoring controls:** (a) machinery integrity —
   Design 12's generator and validator at the base
   configuration (W = 10, no second bar), imported unchanged,
   must reproduce Design 8's engine AND validator signal sets
   EXACTLY on all 127 names (147,718 signals), as in Designs
   12–13; (b) **Design 14 parity** — the Design 14 engine
   generator and the independently written vectorised
   validator must agree EXACTLY on every name (signal set,
   snap index, depth, vol_ratio). Any failure aborts the run.
2. **Timing/leak audit (per book):** every trade checked —
   entry after signal; entry exactly at signal + 1 bar; entry
   lag ≤ 5 (the freshness counter); fill inside [09:45,
   14:30]; exit re-simulated bar-by-bar on the trade's own
   day by the independent bar-loop exit of Section 4 and
   matched (bar, price, reason); square-off price equal to
   its own day's square-off-bar close (the regression check
   that exposed the Rounds 1–3 defect); net recomputed; caps
   (≤2/name/day, ≤10/day); no overlapping positions per name;
   each trade's vol_ratio / depth / excursion bar recomputed
   independently (from the validator) and matched; and the
   whole book rebuilt by an independently written allocator
   (validator signals + A4 ranking + bar-loop exits) and
   matched trade-for-trade. Plus a truncation spot-check:
   Bollinger bands and MACD histogram recomputed from bars
   cut at the signal bar must match the engine at that bar.
   Violations must be 0.
3. **Random-entry placebo (200 seeded draws, seed base
   20261118 — the family base):** same names, same days, same
   number of entries per day as the book took, random eligible
   bars 09:45–14:45 (the family's placebo window), random
   side, identical caps — and **the book's OWN exit geometry**
   (Section 4), per the family's placebo principle
   (`tarang4_score.placebo_r4`: the placebo runs "with the
   candidate's own exit rule"). The family's `placebo_r6`
   hardcodes the retired +0.8%/−0.5% exits and therefore does
   NOT apply to Design 14; Design 14's placebo is
   `placebo_r6`'s body with the exit simulator replaced by
   Section 4's, stated openly here. The book must beat the
   placebo 90th percentile in both years.
4. **Placebo percentile reporting:** the book's percentile
   within its own 200-draw distribution, per year.
5. **Direction-flip placebo (information only):** the book's
   exact entries with the side flipped, under the book's own
   exits.
6. **Splits and stress:** as listed in Section 6;
   independent re-sum of headline nets from the written
   trades CSV.

## 6. Reporting (binding)

Per book (TARANG-T14-A, TARANG-T14-B): the full gate table
(Section 7); placebo percentiles; side splits (LONG vs SHORT
nets per year); win rate; trade count; halves; full month
table; ex-top-3 per year; max drawdown (overall and per
year); top-10 contributors per year; the **resolution mix**
— stop / target / square-off counts, nets and shares of all
trades, per year (the residue hypothesis predicts square-off
dominance; T14-A's target count is structurally zero); the
November 2026 slice with its trade count; monthly pace vs
the ₹15,000/month stocks floor (information); and the **cost
anatomy** — trades, gross, levy, gross per trade, net per
trade, per year — with **the decisive line stated plainly:
the continuation stream's gross per trade against the ₹40
levy, in each year**.

## 7. Pass bar (pre-registered, frozen)

A Design 14 book PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in
  **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

## 8. Discipline

- The ONLY new variables are the stream (continuation, on
  the excursion bar, no confirmation), the exit geometry
  (Section 4) and the allocation dial's return to A4
  volume-priority — each named in Design 13's seed or in
  this spec's seed quote. Bollinger (20, 2), the excursion
  definition, the [09:45, 14:30] entry window, the name and
  day caps, universe and window are frozen. Nothing is
  scanned.
- A PASS makes the book a forward-paper CANDIDATE for the
  owner's decision; nothing is armed or started by this run
  either way.
- Whatever the verdict, the report closes with the diagnosis
  that seeds Design 15, in two lines.
