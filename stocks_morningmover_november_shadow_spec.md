# Stocks EQUITY — November 2026 SHADOW paper spec — Morning-Mover (MOVER-A / MOVER-B)

**FROZEN 2026-10-31, before November begins. SHADOW paper only,
no orders. Real money: ₹0. NO changes during November — any
change to the 1.0% pre-move threshold, the measurement times,
the discard-first construction, the exits, or the chain cap
voids the month as a hypothesis test for that variant.**

**EQUITY CASH intraday only. LONG/SHORT language only — no
options, no premiums. Every rupee figure: provisional per
100 shares, ₹40/trade flat cost.**

## Status — SHADOW, and why this exists

This is a **shadow** log. The November primary for stocks is
N4-V3 (event-reaction), in its own spec and log
(`stocks_n4_november_paper_spec.md` /
`stocks_n4_november_paper_log.csv`). Two shadows already run
alongside it, each in its own spec and log: P2-INV1
(`stocks_p2inv_november_shadow_spec.md`) and P2F
(`stocks_p2f_november_shadow_spec.md`). The Morning-Mover
shadow runs alongside all three and changes nothing about any
of them.

It carries the v2 candidate frozen in
`stocks_vline_v2_candidate_spec.md` (the "Morning-Mover Second
Signal": on stock-days where the stock has already moved
≥1% before 10:00, discard the day's first V5-stream signal and
trade the next one) into a fresh-window test, together with a
second, independently-judged variant built on observation
OBS-2b-1 from the Line 2b robustness battery
(`stocks_tuning_vline_report.md`). The candidate spec
envisaged December 2026 as this rule's first possible window;
the parent thread has advanced it to November as an additional
shadow. **The rules are exactly as frozen — only the window
moved.** The two variants share one log and are judged
separately: one dying does not kill the other.

> **Hypothesis A (frozen candidate, Jan–Oct-generated):** a
> stock that has already moved ≥1% by 10:00 is in a
> committed intraday regime; its first V5 signal of the day
> is the probe, and the *next* signal — traded at T125 with
> one re-entry allowed — is net-positive after costs.
>
> **Hypothesis B (observation OBS-2b-1, battery-generated):**
> the same construction measured at 10:15 instead of 10:00
> is at least as good — in-sample it was the strongest single
> variation in the battery. Observation-grade only: it was
> read off a diagnostic battery after the fact, which is
> exactly the kind of number that shrinks on fresh data.

## Source results — in-sample, Jan–Oct 2026 (discovery, not proof)

Scored on the Jan–Oct cache (October = 1–28 Oct only; 29 Oct
is absent from the cache and was never counted). Engines:
`stocks_tuning_vline.py` (frozen V5 re-entry stream + exit
replay) and `stocks_tuning_vline2b.py` (`build_batt` chain
construction). The battery's validation gate reproduced
Variant A's published subset to the paisa before any cell was
scored (see the validation section below).

### Variant A — MOVER-A (measurement before 10:00, frozen candidate)

| MOVER-A (in-sample) | Chains | Trades | Net ₹ | Jan–May ₹ (chains) | Jun–Oct ₹ (chains) | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| **T125 (only exit)** | 424 | 698 | **+84,671.74** | +52,884.19 (272) | +31,787.55 (152) | +16,825.42 | 16/25 stocks net+ |

Chain win rate 55.0%, chain expectancy +₹199.70. Leg split:
direct leg (first traded signal) 424 trades **+₹93,575.31**;
re-entry leg 274 trades **−₹8,903.57**. Breakeven flat cost
**₹161.31/trade** (Jan–May ₹155.22 / Jun–Oct ₹173.00) — the
in-sample result does not hinge on the frozen ₹40 assumption
or on the user's still-unknown real broker charges. Source
dump: `vline2b_FROZEN_trades.csv`.

### Variant B — MOVER-B (measurement before 10:15, OBS-2b-1 — OBSERVATION-GRADE)

| MOVER-B (in-sample) | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| **T125 (only exit)** | 589 | 941 | **+169,328.31** | +92,266.39 | +77,061.92 | +36,815.02 | 24/25 stocks net+ |

Uniquely among the battery's variants, B's re-entry leg is
positive in-sample (+₹10,642.17 on 352 trades). These are the
hypothesis-source numbers for B, labelled **in-sample,
observation-grade**: B was never a frozen family; it is the
best-looking cell of a robustness battery, selected after
scoring. It earns a fresh-window test as a *hypothesis*, not
as a favourite, and it is judged in November against exactly
the same bar as A. Source dump: `vline2b_R4-W1015_trades.csv`.

## The rule — exact (engine-faithful)

Definitions below are the scored definitions of
`stocks_tuning_vline2b.py`'s `build_batt` at the frozen
parameters (the engine is the authority), restating the
candidate spec's rule verbatim where they coincide.

1. **Universe:** the 25 watchlist stocks.
2. **Signal stream:** the frozen V5 re-entry stream —
   `pool_pick` over `v4_head` / `skor_head` from
   `stocks_equity_reentry.py`, chained as in Round 8: entry =
   next bar's open after the signal; the next search starts
   at the previous exit bar (after a discarded signal, at the
   signal bar + 1). No direction filter is applied after the
   discard (battery R5 confirmed the frozen definition is
   ANY-direction): the next signal is traded whatever
   direction the stream returns. Both LONG and SHORT trade.
3. **Pre-move test (ex-ante, known at the measurement time):**
   let day open = the open of the first 5-min bar of the day,
   and pre-close = the close of the last bar with time
   **< 10:00 (Variant A)** or **< 10:15 (Variant B)**. Signed
   pre-move = pre-close / day open − 1. The stock-day
   **qualifies for that variant** iff |pre-move| ≥ 1.0%.
   The two variants are computed independently: a stock-day
   may qualify under A, under B, under both, or under
   neither, and is logged under each variant it qualifies
   for.
4. **Non-qualifying days: NO TRADES AT ALL under that
   variant.** The variant simply does nothing that stock-day.
5. **Qualifying days:** discard the first V5-stream signal
   of the day entirely (no trade, no cost). Trade the next
   signal at **T125 (target +1.25% / stop −0.5%)**: entry at
   the next bar's open; exit replay per the frozen convention
   (scan from the entry bar; **stop checked before target**
   within a bar; otherwise **15:10 square-off** at that bar's
   close). After that trade exits, **ONE further re-entry**
   is allowed if another signal occurs (also T125, same
   construction). **Chain cap = 2 trades per stock-day per
   variant.**
6. If a qualifying day has a first signal but no second
   signal, **no trade is taken** that day under that variant.
7. **No ADR filter, no morning-entry cutoff, no event
   filter, no per-stock exclusions.** Signals after the
   measurement time are traded whenever they occur in the
   stream, up to the chain cap.
8. **Chain** = the set of trades (1 or 2) taken on one
   qualifying stock-day under one variant. `chain_round` 1 =
   the direct leg (the first traded signal, after the
   discard); `chain_round` 2 = the re-entry leg.
9. **Net per trade** = sign × (exit price − entry) × 100
   shares − **₹40** flat cost. Chain net = the sum of its
   trades' nets. All November judging is on **chain-total
   net at T125** — T125 is the only exit; there is no shadow
   exit column for this system.

## November data source rules

- **Fresh Upstox fetches only.** November days are generated
  from 5-min candles fetched fresh from Upstox (the same
  connector path as the October cache builds and the volume
  fetch). The Jan–Oct caches end 28 Oct and are never used
  for November days.
- **Fetch windows span at least the last 5 trading days —
  never a single-day range.** Short-range Upstox responses
  intermittently omit the newest day entirely (found in the
  2026-10-30 dry run: a single-day fetch silently returned
  zero bars for the day); a single-day fetch is therefore
  prohibited. The wide window also supplies the prior-day
  context the signal stream's heads are built on. After
  fetching, verify the day's bars are actually present in
  the returned window before generating that stock-day.
- **DATA_MISSING rule:** if a stock's bars for the day still
  cannot be obtained after one retry with a 10-trading-day
  window, log one row per variant for that stock with
  `stock` = the symbol, `variant` = MOVER-A / MOVER-B,
  direction and price fields blank, and `notes` =
  `DATA_MISSING`. Never silently skip a stock; never treat
  missing data as a non-qualifying day.
- **Holiday / outage guard:** if the day is not a trading
  day, no rows are written and nothing is reported beyond
  one line. If it is a trading day but market-wide data is
  absent, every stock is handled under the DATA_MISSING
  rule above.
- **Unclassifiable rows:** if a stock-day's generation cannot
  be completed for any other reason (e.g. a malformed series
  that prevents the pre-move test), log one row per variant
  with the reason in `notes` (`unclassifiable: <reason>`).
  Never guess a qualification into existence; never silently
  skip one either.

## Logging

Log file: `stocks_morningmover_november_shadow_log.csv`, one
row **per trade**, appended after the day's 15:10 square-off,
both variants in the same file. Fields: `date, stock,
variant, pre_move_pct, pre_move_sign, direction, entry_time,
entry, exit_price, exit_time, exit_reason, chain_round,
net_rs_provisional_per100, notes`.

- `date` = the trading day; `stock` = the watchlist symbol.
- `variant` = `MOVER-A` or `MOVER-B`.
- `pre_move_pct` = the **signed** pre-move in % at that
  variant's measurement time (the engine's `premove_pct`,
  e.g. `1.633` or `-2.041`); `pre_move_sign` = `UP` if
  positive, `DOWN` if negative (the ≥1% gate means it is
  never zero on a traded row).
- `direction` = the traded signal's direction, `LONG` or
  `SHORT` — independent of the pre-move sign (ANY-direction
  rule).
- `chain_round` = 1 (direct) or 2 (re-entry).
- `net_rs_provisional_per100` = that trade's net at T125,
  ₹40 already deducted.
- `notes` carries DATA_MISSING / unclassifiable markers and
  any observation; observations change nothing until the
  month-end judgement.

## Judging rules — pre-registered, per variant, judged once at month-end

Judged once, after the last November trading day, **per
variant separately**, on that variant's chain-total net at
T125 (provisional per 100 shares, ₹40/trade), with win % and
chain/trade counts reported alongside. One variant's verdict
never affects the other's, and neither verdict modifies
N4-V3, INV1 or P2F.

- **≥ 40 chains and November net positive:** the variant is
  **upgraded to candidate** — it earns a further frozen
  decision (e.g. a second fresh window or a primary slot
  contest). It is NOT adopted on one month.
- **≥ 40 chains and November net negative:** the variant is
  **killed** — recorded as a Jan–Oct in-sample artefact, no
  re-tuning, no threshold change, no measurement-time change,
  no direction split after the fact.
- **Fewer than 40 chains in November:** the test is
  **inconclusive** for that variant — neither passed nor
  failed — and that variant **extends to December** under
  these same frozen rules, judged at December month-end on
  the combined Nov+Dec sample against the same ≥40-chain /
  positive-net bar.
- **November net exactly ₹0 with ≥ 40 chains:** not positive,
  so no upgrade; not negative, so no kill — treated as
  inconclusive and extended to December as above.

**No parameter changes during November:** no change to the
1.0% threshold, the 10:00 / 10:15 measurement times, the
discard-first construction, the chain cap of 2, the T125
exits, the cost, or these judging rules — for either variant.

## Mandatory disclosures (part of the frozen record)

- **Everything above is in-sample.** Jan–Oct 2026 was used
  to discover Variant A's subset and to observe Variant B.
  Their in-sample figures are evidence for testing them, not
  evidence they work. Neither variant has any fresh-data
  result yet.
- **Variant A was elevated after reading scored output.**
  The subset definition itself was frozen ex-ante inside
  Line 2's U5 family and was pre-declared as a diagnostic
  subset — but the decision to elevate it to a candidate
  came from its scored result. Under this project's
  discipline that earns a fresh-window test only, which is
  what this shadow is.
- **Variant B is observation-grade.** OBS-2b-1 was the
  strongest cell of a diagnostic robustness battery, named
  after scoring. Best-cell-of-a-battery numbers are the most
  likely of all to shrink out-of-sample; B's in-sample
  +₹169,328.31 should be expected to overstate whatever B
  really is.
- **A's re-entry leg is negative in-sample** (−₹8,903.57 on
  274 trades) while its direct leg carries the result
  (+₹93,575.31). The frozen rule — and both variants here —
  include the second leg exactly as observed. A direct-only
  variant would be a new hypothesis requiring its own frozen
  spec, not an edit to this one.
- **A's mover-up flank is thin in the second half.**
  Partitioning A's frozen chains by the sign of the pre-move:
  mover-DOWN chains are the strong flank (221 chains,
  +₹58,812.88, balanced halves, breadth 19/25); mover-UP
  chains earn only +₹3,174.31 across Jun–Oct (87 chains,
  ≈ +₹36/chain), and the rule's entire negative re-entry leg
  lives in mover-up chains (−₹9,249.00). If A weakens on
  fresh data, this is the flank to inspect first. Nothing is
  filtered on it in November — both move signs trade.
- **September was A's worst month in-sample:** −₹2,272.08
  on 17 chains (also the thinnest month). Only two of ten
  months were negative, both small; the largest month, April
  (+₹25,718.06 ≈ 30% of the net), does not carry the result
  (removing it leaves +₹58,953.68, both halves positive) —
  recorded so a soft November month is read in context, not
  as a surprise.
- **Concentration in A is moderate, not absent:** top-3
  stocks (GLENMARK, BDL, TVSMOTOR) = 60.7% of the net. The
  candidate survived its in-sample stress (excluding the
  top-3 entirely: +₹33,312.91, both halves positive;
  winsorised at +₹2,000/stock: +₹15,622.16) — disclosed here
  so the November per-stock table is compared against it.
- **The threshold is a plateau, the measurement time is
  not.** In-sample, thresholds 0.75% / 1.25% / 1.5% are all
  both-halves positive (battery R1) — 1.0% is an interior
  point of a working region. Measurement time is one-sided
  sensitive: 09:45 breaks the rule in-sample (Jun–Oct
  −₹1,536.44, breadth 9/25). The load-bearing choices are
  therefore the full morning window and the ≥1% size, and
  both are frozen exactly as stated.
- **Most days, a variant does nothing.** A qualified on 424
  of 4,111 signal stock-days in-sample (~10%). A thin
  November chain count — and an inconclusive extension to
  December — is a realistic outcome, pre-registered above
  rather than improvised at month-end.

## Validation of this freeze (2026-10-31)

Two levels of validation anchor this spec to the machinery
that produced the in-sample numbers:

1. **Full-window gate (battery, already on record):**
   `stocks_tuning_vline2b.py` at the frozen parameters
   (threshold 1.0%, window < 10:00, ANY direction, cap 2)
   reproduced Variant A's published subset **to the paisa**:
   424 chains, 698 trades, net +₹84,671.74, Jan–May
   +₹52,884.19 (272 chains), Jun–Oct +₹31,787.55 (152
   chains), October +₹16,825.42, chain win 55.0%, breadth
   16/25, direct leg +₹93,575.31, re-entry leg −₹8,903.57.
2. **Single-day generation checks (run for this spec,
   2026-10-31):** the battery engine's `build_batt` was
   re-run for one sample day — **2026-10-28** — one variant
   at a time, all 25 stocks, and the produced trades were
   diffed field-by-field against the battery's own trade
   dumps for that date:
   - **Variant A** (frozen defaults) produced exactly **1
     trade**: BDL, LONG, setup `skill_or_breakout`, direct
     (chain_round 1), entry 09:50 @ 1009.50, exit 10:15 @
     1004.45 (stop), gross −₹504.75, net −₹544.75, pre-move
     +1.633% — **identical on every field** to the
     2026-10-28 row of `vline2b_FROZEN_trades.csv`. No other
     stock produced a trade that day under A. **PASS.**
   - **Variant B** (`window_end = 10:15`, everything else
     identical) produced exactly **2 trades** — the same BDL
     trade (pre-move +1.572% at the 10:15 measurement) plus
     GLENMARK, LONG, `skill_or_breakout`, direct, entry 10:00
     @ 2296.60, exit 15:10 @ 2285.12 (stop), net −₹1,188.30,
     pre-move +1.140% — **identical on every field** to the
     2026-10-28 rows of `vline2b_R4-W1015_trades.csv`.
     **PASS.**

The November logging instructions therefore describe the
same machine that produced the in-sample numbers for both
variants. No discrepancy was found. Nothing in this spec
differs from what was scored.
