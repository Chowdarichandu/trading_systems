# TARANG Design 13 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 13
scoring. No Design 13 result exists at the time of writing; no
parameter below has been tuned against any Design 13 result.

**Programme note (owner's standing mandate):** the TARANG
programme CONTINUES — designs iterate from diagnosis until a
gate pass or the owner's stop. Design 13 is the direct
continuation of Design 12, seeded by Design 12's own diagnosis
(`tarang12_2026-11-17.md` Sections 3 and 6):

> *The binding term that remains is the count itself. T12-B
> posts the family's best gross in both years (+₹15.94 /
> +₹26.90 per trade), passes both placebo legs, keeps November
> positive — and still loses both years, because 4,640 trades
> × ₹40 = ₹1,85,600 of levy stands against a gross of
> ₹97,525.84, and the net is the difference, to the rupee. The
> count did not fall under any confirmation change: ~195–200
> candidate entries a day saturate the 10/day cap in every
> variant. Every term of the trade has now been varied —
> entries (Designs 7, 8, 12), exits (Designs 9, 10, 11), side
> (Design 11), selectivity by two quality keys (Designs 9,
> 10), allocation (Design 8) — except the number of trades
> itself. Whether the day's EARLIEST signals carry a gross per
> trade the later ones dilute is the one decomposition never
> taken, and a hard cap is the only dial that moves the levy.*

Design 13 therefore freezes **T12-B WHOLE** — freshness-5
re-cross entries, QUIET-priority allocation among competing
signals, frozen +0.8% / −0.5% exits — and changes ONLY the day
cap: **10 → 3, BY TIME**. The decisive, pre-registered
diagnostic of this design: **the first-3 stream's gross per
trade, by year, against T12-B's full-stream gross per trade
(+₹15.94 / +₹26.90) and against the ₹40 levy** — does the
early stream clear the levy per trade, or does the arithmetic
close (a ~₹27 gross ceiling against a ₹40 levy at ANY count)?

**Basis (labelled everywhere):** equity cash only,
PROVISIONAL per 100 shares, ₹40 per completed trade. Paper
only, real money ₹0. No stock options (closed surface).
Nothing is armed; no paper run is started; no live book is
touched.

## 1. Universe and data (unchanged from Designs 6–12)

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
  Design 13 reads byte-identical indicator values to Designs
  7–12 (the signal machinery is Design 12's, imported, not
  re-written).
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the
  November 2026 slice reported separately, never pooled into
  one verdict.

## 2. The frozen base — T12-B (Design 12, Section 3)

- A bar is **beyond-low** if close < lower band, **beyond-high**
  if close > upper band, **inside** if lower ≤ close ≤ upper; a
  bar with undefined bands is inert. An **excursion** is a
  maximal run of consecutive same-side beyond closes within a
  session; its first bar is the **snap bar** `a` and arms a
  setup of its side. The histogram is NOT read at the snap bar.
- The setup ends at the first bar after `a` that is not beyond
  on the setup's side. That bar, if it closes **inside**, is
  the **re-cross bar** `r`. An opposite beyond close ends the
  setup unfilled and itself arms an opposite setup. A
  still-beyond bar at distance > 5 (the freshness window)
  expires the setup mid-excursion.
- A signal fires at `r` iff `r − a ≤ 5` and the MACD histogram
  is still rising into the turn — LONG: hist[r] > hist[r−1];
  SHORT: hist[r] < hist[r−1] — with r−1 the previous bar of the
  same session and both values defined. The re-cross spends
  the setup whether or not the signal fires.
- **Fill: the open of bar `r+1`**, same session, fill time in
  [09:45, 14:30].
- Allocation fields (frozen): **vol_ratio** = volume at the
  signal bar `r` ÷ mean volume of the 20 bars ending at the
  snap bar `a` (0 if that mean is 0); **depth** = the snap
  close's penetration beyond the band in % of the snap close.
- Allocation order (frozen): candidate entries are processed
  in (date, entry_time, vol_ratio ASCENDING, depth descending,
  signal_time, symbol) order — chronological by fill time,
  the QUIET ranking acting only among entries sharing a fill
  time. Caps: one open position per name; max 2 entries per
  name per day; **the day cap of Section 3**; re-entry after
  an exit allowed.
- Exits (frozen family geometry): +0.8% target / −0.5% stop,
  stop first on a both-hit bar, else the 15:15 square-off
  bar's close — evaluated on the trade's OWN day's bars (the
  Round 4 corrected indexing). Net = side × (exit − entry) ×
  100 − ₹40.

## 3. The one change — day cap 10 → 3 BY TIME

**TARANG-T13** is T12-B with the book-level day cap cut from
10 to **3**, applied in the allocator's own processing order
(Section 2): the day's **first 3 entries in fill order** are
taken; every later candidate that day is skipped. No quality
key, no ranking change, no other change of any kind — entries,
allocation order, name caps, occupancy, exits, universe and
window are T12-B's, frozen.

Two consequences are pre-registered as checks, not assumed:

- **Subset identity.** Because allocation is sequential in
  fill order and every other constraint is unchanged, the
  T13 book must be EXACTLY the first-3-per-day subset (in fill
  order) of the T12-B book produced by the same run's cap-10
  allocation. This identity is verified trade-for-trade as a
  binding audit counter (Section 5); any mismatch aborts the
  verdict — it would mean the cap change leaked into another
  term.
- **Levy identity.** Net = gross − ₹40 × trades, exactly. The
  report states gross, levy and net per year for T13 beside
  T12-B's, so the count term is isolated arithmetically: the
  cap cut removes ~70% of the levy; whether it removes the
  loss depends only on the first-3 stream's gross per trade.

## 4. Reporting (binding)

For TARANG-T13: the full gate table (Section 6); placebo
percentiles; side splits (LONG vs SHORT nets per year); win
rate; trade count; halves; full month table; ex-top-3 per
year; max drawdown (overall and per year); top-10
contributors per year; the resolution mix (stop / target /
square-off counts, nets, stop share of resolved, per year);
the November 2026 slice with its trade count; monthly pace
vs the ₹15,000/month stocks floor (information); **the cost
anatomy with T12-B re-stated beside it** — trades, gross,
levy, gross per trade, net per trade, per year — and **the
decisive diagnostic**: the first-3 stream's gross per trade
by year (T13's own gross per trade) against T12-B's
full-stream gross per trade (+₹15.94 / +₹26.90) and the ₹40
levy, with the levy-vs-gross identity verified to the rupee.

## 5. Controls gate (identical, unmoved)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6/7/8 audit
stack, and `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`,
run in the same run, before any verdict:

1. **Pre-scoring controls:** (a) Design 12's generator and
   validator at the base configuration (W = 10, no second
   bar), imported unchanged, must reproduce Design 8's engine
   AND validator signal sets EXACTLY on all 127 names
   (147,718 signals); (b) engine-vs-validator parity for the
   W = 5 configuration and the subset property against Design
   8's validator set (identical snap/depth/vol_ratio), as in
   Design 12; (c) **T12-B reproduction:** the cap-10 QUIET
   allocation on the W = 5 candidate stream, run inside this
   script, must reproduce Design 12's T12-B exactly — nets
   −₹59,900.69 (2025) / −₹28,173.47 (2026), 4,640 trades, and
   the `tarang12_trades.csv` T12-B rows trade-for-trade.
   Any failure aborts the run.
2. **Subset identity (Design 13's own control):** the T13
   trades must equal, trade-for-trade and in order, the
   first-3-per-day (fill order) subset of the reproduced
   T12-B book. Mismatches must be 0.
3. **Timing/leak audit:** every T13 trade checked — entry
   after signal, entry exactly at signal + 1 bar, fill inside
   [09:45, 14:30], exit re-simulated bar-by-bar on the
   trade's own day by the independent bar-loop exit and
   matched (bar, price, reason), square-off price equal to
   its own day's square-off-bar close (the regression check
   that exposed the Rounds 1–3 defect), net recomputed, caps
   (≤2/name/day, **≤3/day**), no overlapping positions per
   name, each trade's vol_ratio / depth / snap bar recomputed
   independently (from the validator) and matched, and the
   whole book rebuilt by an independently written allocator
   (validator signals + QUIET ranking + **day cap 3** +
   bar-loop exits) and matched trade-for-trade. Plus a
   truncation spot-check: Bollinger bands and MACD histogram
   recomputed from bars cut at the signal bar — and the
   bands from bars cut at the snap bar — must match the
   engine at those bars. Violations must be 0.
4. **Random-entry placebo (200 seeded draws, seed base
   20261118 — the family base):** same names, same days,
   same number of entries per day as T13 took, random
   eligible bars 09:45–14:45 (the family's placebo window),
   random side, identical caps, and the frozen exits of
   Section 2, all on corrected indexing (the family's
   `placebo_r6`, unchanged). The book must beat the placebo
   90th percentile in both years.
5. **Placebo percentile reporting:** the book's percentile
   within its own 200-draw distribution, per year.
6. **Direction-flip placebo (information only):** the book's
   exact entries with the side flipped, under the frozen
   exits.
7. **Splits and stress:** as listed in Section 4;
   independent re-sum of headline nets from the written
   trades CSV.

## 6. Pass bar (pre-registered, frozen)

TARANG-T13 PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in
  **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check and subset
  identity included);
- November 2026 slice not worse than −₹3,000.

## 7. Discipline

- No other parameter changes: Bollinger (20, 2), MACD
  (12, 26, 9), the snap/re-cross state machine, the freshness
  window (5), the QUIET allocation order, the [09:45, 14:30]
  entry window, the frozen exits, the name caps, universe,
  window — all frozen as T12-B. The day cap (10 → 3) is the
  single new variable, and it is not scanned.
- A PASS makes the book a forward-paper CANDIDATE for the
  owner's decision; nothing is armed or started by this run
  either way.
- Whatever the verdict, the report closes with the diagnosis
  that seeds Design 14, in two lines — per Design 12's seed:
  if the first-3 stream cannot clear the levy, the arithmetic
  is closed (a ~₹27 gross ceiling against a ₹40 levy at ANY
  count) and Design 14 leaves the snap-reversion stream
  itself; the report names the candidate stream the evidence
  points to.
