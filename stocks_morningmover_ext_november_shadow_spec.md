# Stocks EQUITY — November 2026 SHADOW paper spec — Morning-Mover EXTENDED universe (MOVER-EXT-A / MOVER-EXT-B)

**FROZEN 2026-10-31, before November begins. SHADOW paper only,
no orders. Real money: ₹0. NO changes during November — any
change to the 1.0% pre-move threshold, the measurement times,
the discard-first construction, the exits, or the chain cap
voids the month as a hypothesis test for that variant.**

**EQUITY CASH intraday only. LONG/SHORT language only — no
options, no premiums. Every rupee figure: provisional per
100 shares, ₹40/trade flat cost.**

## Status — a SEPARATE additional SHADOW, on the NEW 25 only

This spec covers the **extended universe only**: the 25 new
large-cap stocks built in Tuning Loop Line 4
(`stocks_tuning_universe_report.md`). It is a **separate**
shadow from the Morning-Mover shadow on the original 25
watchlist (`stocks_morningmover_november_shadow_spec.md` /
`stocks_morningmover_november_shadow_log.csv`). **That spec
and log are not altered by this one in any way** — different
universe, different spec file, different log file, separate
judging.

The November primary for stocks remains N4-V3 (event-reaction),
in its own spec and log. The other shadows — P2-INV1, P2F, and
the home-universe Morning-Mover (MOVER-A / MOVER-B) — are
unaffected. This shadow exists for one reason: in Line 4, of
the three frozen candidates transferred verbatim to stocks
they were never tuned on, **only the Morning-Mover Second
Signal transferred** (DBL-LONG and P2F failed the transfer
gate and are not part of this shadow). Its two variants are
exactly the variants of the home shadow spec — **A (10:00
measurement, the frozen candidate)** and **B (10:15
measurement, observation OBS-2b-1)** — applied to the new 25,
sharing one log (this spec's log) and judged separately: one
dying does not kill the other. Log variant labels are
`MOVER-EXT-A` and `MOVER-EXT-B`, so no row of this log can
ever be confused with a home-universe row.

## The extended universe — exact (25 stocks)

RELIANCE, TCS, ICICIBANK, INFY, BHARTIARTL, SBIN, LT,
AXISBANK, KOTAKBANK, BAJFINANCE, HCLTECH, MARUTI, SUNPHARMA,
TITAN, M&M, ULTRACEMCO, NESTLEIND, POWERGRID, ONGC, COALINDIA,
JSWSTEEL, GRASIM, CIPLA, DRREDDY, EICHERMOT.

These are the most liquid Nifty-50 constituents NOT in the
original watchlist (Line 4, Step 1; TATAMOTORS excluded at
build time for its Oct-2025 demerger ambiguity). In-sample
data: 5-min candles with volume under
`data/progressive_vol_ext/`, engine-compat `spot_5m.csv` +
`spot_daily.csv` under `data/progressive_ext/` (15,375 bars
per stock, 205 trading days × 75, verified in
`universe_ext_verification.json`).

## Source results — Line 4 transfer test, in-sample Jan–Oct 2026 (evidence, NOT fresh data)

Scored on the Jan–Oct ext cache (October = 1–28 Oct only;
engines restrict scoring to ≤28 Oct via their frozen window
filters). Engines: `stocks_tuning_universe.py` — its
`build_chain` / `replay_plain` copied verbatim from
`stocks_tuning_vline.py` (mode `U5b`, cap 2) — over the
`stocks_equity_reentry_ext.py` signal-stream head. The Line 4
validation gate reproduced the rule's old-universe anchors to
the paisa with this same machinery before any transfer number
was trusted (424 chains, 698 trades, +₹84,671.74 on the
original 25 — see the Line 4 report).

### Variant A — MOVER-EXT-A (measurement before 10:00, frozen candidate, transferred verbatim)

| MOVER-EXT-A (in-sample, Line 4) | Chains | Trades | Net ₹ | Jan–May ₹ (chains) | Jun–Oct ₹ (chains) | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| **T125 (only exit)** | 199 | 300 | **+164,483.29** | +73,142.55 (126) | +91,340.74 (73) | +39,984.55 | 22/25 stocks net+ |

Chain win rate 59.8%, chain expectancy **+₹826.55/chain** —
higher than on the home universe (+₹199.71/chain, breadth
16/25). Leg split: chains with a second (re-entry) trade
+₹89,198.43 (101 chains); single-trade chains +₹75,284.86
(98) — on this universe both legs pay. Top-3 share 48.8%
(EICHERMOT +₹39,721.48 on 13 chains, LT +₹20,601.19, M&M
+₹19,988.47); only 2 stocks negative (JSWSTEEL −₹1,721.18,
KOTAKBANK −₹477.87) and 1 with no qualifying chains
(ICICIBANK). Source dump: `universe_ext_morningmover_trades.csv`.

> **What these numbers are:** the frozen rule was never tuned
> on these 25 stocks, so Line 4 is genuine *transfer*
> evidence — but it was scored on the same Jan–Oct 2026
> window, on a universe that was built and verified inside
> that window. **It is in-sample transfer evidence, NOT fresh
> data. November 2026 is this universe's first fresh window.**
> The +₹826.55/chain expectancy should be expected to shrink
> on fresh data, as every in-sample figure in this programme
> has.

### Variant B — MOVER-EXT-B (measurement before 10:15, OBS-2b-1 — OBSERVATION-GRADE, never scored on this universe)

Variant B has **never been scored on the extended universe**
— Line 4 transferred Variant A only. B's hypothesis source is
the home-universe robustness battery (OBS-2b-1, original 25,
in-sample: 589 chains, 941 trades, +₹169,328.31, halves
+₹92,266.39 / +₹77,061.92, October +₹36,815.02, breadth
24/25; source dump `vline2b_R4-W1015_trades.csv`). It is
included here exactly as in the home shadow spec — as a
*hypothesis*, not a favourite — and is judged in November
against exactly the same bar as A. Its first-ever ext-universe
numbers will be November's fresh ones.

## The rule — exact (as in the home shadow spec, universe swapped)

1. **Universe:** the 25 extended-universe stocks listed
   above. No other stock is ever logged under this spec.
2. **Signal stream:** the frozen V5 re-entry stream —
   `pool_pick` over `v4_head` / `skor_head` from the reentry
   engine (ext head: `stocks_equity_reentry_ext.py`), chained
   as in Round 8: entry = next bar's open after the signal;
   the next search starts at the previous exit bar (after a
   discarded signal, at the signal bar + 1). No direction
   filter is applied after the discard (the frozen definition
   is ANY-direction): the next signal is traded whatever
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

Engine authority note: the ext in-sample numbers above were
produced by `stocks_tuning_universe.py`'s `build_chain`
(copied verbatim from `stocks_tuning_vline.py`) over the ext
reentry head. That machinery and the home spec's battery
engine (`stocks_tuning_vline2b.py` `build_batt`) both
reproduced Variant A's published old-universe subset to the
paisa at the frozen parameters (424 chains, +₹84,671.74), and
the single-day generation validation for THIS spec is
recorded at the bottom. November generation follows the
frozen construction stated above — the same machine that
produced the in-sample numbers.

## November data source rules

- **Fresh Upstox fetches only.** November days are generated
  from 5-min candles fetched fresh from Upstox, through the
  same connector path used to build the ext universe
  (`fetch_vol_ext_janoct.py`'s path; instrument keys
  `NSE_EQ|<ISIN>` as established in Line 4, including the
  four split-adjusted ISINs for KOTAKBANK, BAJFINANCE,
  NESTLEIND, DRREDDY). The Jan–Oct caches end 28 Oct and are
  never used for November days.
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
  `stock` = the symbol, `variant` = `MOVER-EXT-A` /
  `MOVER-EXT-B`, direction and price fields blank, and
  `notes` = `DATA_MISSING`. Never silently skip a stock;
  never treat missing data as a non-qualifying day.
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

Log file: `stocks_morningmover_ext_november_shadow_log.csv`,
one row **per trade**, appended after the day's 15:10
square-off, both variants in the same file. Fields — the same
header as the home shadow log: `date, stock, variant,
pre_move_pct, pre_move_sign, direction, entry_time, entry,
exit_price, exit_time, exit_reason, chain_round,
net_rs_provisional_per100, notes`.

- `date` = the trading day; `stock` = the ext-universe symbol.
- `variant` = `MOVER-EXT-A` or `MOVER-EXT-B`.
- `pre_move_pct` = the **signed** pre-move in % at that
  variant's measurement time (e.g. `1.633` or `-2.041`);
  `pre_move_sign` = `UP` if positive, `DOWN` if negative
  (the ≥1% gate means it is never zero on a traded row).
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
N4-V3, INV1, P2F, or the home-universe Morning-Mover shadow.

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

- **This universe was built and scored in-sample, Jan–Oct
  2026.** The 25 stocks, their data verification, and the
  Line 4 transfer scoring all happened inside the Jan–Oct
  window. The rule itself was frozen on the ORIGINAL
  watchlist and transferred verbatim — it was never tuned on
  these stocks — but the quoted Line 4 figures
  (+₹164,483.29, halves +₹73,142.55 / +₹91,340.74, October
  +₹39,984.55) are **in-sample transfer evidence, NOT fresh
  data. November 2026 is the first fresh window for this
  universe**, and this shadow is that test.
- **Variant B has no ext-universe in-sample numbers at all.**
  It enters November on the strength of a home-universe
  diagnostic battery only (OBS-2b-1). Best-cell-of-a-battery
  numbers are the most likely of all to shrink out-of-sample;
  B's home-universe +₹169,328.31 should be expected to
  overstate whatever B really is, on any universe.
- **Qualifying days are rarer on large caps.** Variant A
  produced 199 chains over 203 in-sample trading days across
  25 stocks (~1 chain/day across the whole universe), because
  RELIANCE/TCS-class names pre-move ≥1% before 10:00 less
  often than the home watchlist. A November chain count under
  40 for a variant — and an inconclusive extension to
  December — is a realistic outcome, pre-registered above
  rather than improvised at month-end.
- **Concentration on this universe is moderate, not absent:**
  top-3 share 48.8% of Variant A's in-sample net, with
  EICHERMOT alone at +₹39,721.48 (≈24% of the net, 13
  chains). Breadth (22/25) is the counterweight; the November
  per-stock table should be compared against both.
- **The other two Line 4 candidates failed transfer and are
  excluded.** DBL-LONG failed both gate legs on this universe
  (Jun–Oct −₹3,339.63, breadth 5/25, MARUTI alone 185% of
  net); P2F failed the halves leg (Jan–May −₹196.26,
  expectancy collapsed +₹267 → +₹61/trade, top-3 share 438%).
  Nothing in this shadow rehabilitates them; they face their
  own already-frozen November terms on the home universe, or
  none.
- **This shadow changes nothing else.** The home-universe
  Morning-Mover spec and log, the INV1 and P2F shadows, and
  the N4-V3 primary proceed exactly as frozen. This file and
  its log are additive only.

## Validation of this freeze (2026-10-31)

The ext engine was re-run for one sample day and diffed
against the Line 4 trade dump (`universe_ext_morningmover_trades.csv`),
using the exact scored machinery: `stocks_tuning_universe.py`'s
`build_chain` (mode `U5b`, cap 2) over the
`stocks_equity_reentry_ext.py` head, all 25 ext stocks.

- **Required check — 2026-10-28, Variant A:** all 25
  stock-days were present in the engine's day contexts and
  genuinely evaluated; **0** stock-days met the ≥1% pre-move
  test that day, so the engine produced **0 trades** — and
  the Line 4 dump contains **0 rows** for 2026-10-28.
  Field-by-field match on all 15 dump columns (date, symbol,
  dir, setup, leg, round, entry_time, entry, exit_time,
  exit, exit_reason, gross, net, event, premoved) — over an
  empty set, stated plainly: 28 Oct was a no-qualification
  day on this universe, and both sides agree it was. **PASS.**
- **Supplementary check — 2026-10-26, Variant A** (run so the
  diff is also proven on a non-empty day): 5 pre-moved
  stock-days, engine produced **8 trades**, the dump holds
  the same **8 rows** for 2026-10-26, and every one of the 15
  fields matches on every row. **PASS.**

No discrepancy was found on either day. The November logging
instructions therefore describe the same machine that
produced the Line 4 ext-universe numbers for Variant A.
Nothing in this spec differs from what was scored.
