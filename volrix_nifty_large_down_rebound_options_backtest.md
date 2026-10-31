# Volrix NiftyLargeDownRebound — OPTIONS translation (separate system, paper only, no orders)

**Status: separate translation only. NOT mixed into v4 / (lA) totals, NOT mixed into the
futures/spot rebound backtest totals, NOT adopted.**
This is a NEW translation of the Volrix code into long ATM monthly Nifty calls. Every
options-specific choice below is PROVISIONAL and is labelled as such. It is not the pasted
Volrix code (which trades futures), and it is not Chandu's rule.

## 0. Verdict first

**INCONCLUSIVE overall, HURTS on the only window with data.**

- Only **5 of the 30** futures-backtest entries could be tested with actual traded option
  premiums. The other 25 drop out because Upstox's expired-instruments route returns no
  monthly option contracts before October 2024 (see Section 2). Five trades cannot settle
  a system, and the missing 25 include the COVID-crash period that dominates the futures
  result — so no general claim about options-vs-futures is made here.
- On the 5 testable trades, options **underperform futures on the same entries**:
  options net **+₹76,917.61** vs futures/spot-proxy net **+₹1,28,814.82** on those same 5
  entries, a shortfall of **₹51,897.21**. Win rate 2/5 (options) vs 3/5 (futures).
  The mechanism is visible trade by trade (Section 4): the call captures only ~65–68% of
  a large spot rebound, loses *more* premium points than the spot move on down/flat holds,
  and loses outright on 2026-07-09 even though spot rose +109.15 points over the hold.
  That pattern is consistent with buying peak post-crash implied volatility plus 4 days of
  time decay — but IV itself was not measured here (no IV series was fetched), so "IV crush
  + theta" is the consistent mechanism, not a measured decomposition.
- The options total is still positive only because two very large rebounds (April 2025,
  April 2026) carried three losses. That is the same concentration risk as the futures
  version, on a far smaller sample.

## 1. Primary translation — frozen before results

Fixed before any premium outcome was observed (the one pre-run probe only established
that the expired-instruments candle endpoint works; it did not influence any rule):

- **Trigger / cooldown / skip:** identical to the futures code, by reusing its 30 entry
  dates verbatim from `~/workspace/trading/volrix/positions_daily.json` (verified: the 30
  dates match the futures report's list, including 2019-07-09, 2019-09-04, 2020-02-03,
  2020-02-25, 2020-03-11, 2020-03-31, 2020-04-22, 2020-05-15, 2020-06-12, 2020-09-01,
  2020-09-22, 2020-10-16, 2020-12-22, 2021-02-23, 2021-04-13, 2021-12-21, 2022-01-25,
  2022-02-15, 2022-03-08, 2022-05-05, 2022-05-20, 2022-06-14, 2024-01-18, 2024-06-05,
  2024-08-06, 2024-10-04, 2025-04-08, 2026-03-16, 2026-04-01, 2026-07-09).
  The 10-session cooldown and the skip-after-monthly-expiry-change quirk are therefore
  already embodied in that list and were not re-simulated.
- **Instrument (PROVISIONAL):** LONG ATM Nifty CALL, monthly expiry 0, 1 lot.
  No stop loss, no target — to match the code.
- **Strike basis (PROVISIONAL, ONE basis used throughout):** nearest 50-point strike to
  the PREVIOUS TRADING DAY's Nifty spot close (the trigger-day close, known before the
  open). Not 09:16 spot. This keeps strike selection uniform across all years and free
  of intraday dependence.
- **Monthly expiry 0 (PROVISIONAL):** the first expiry date within 40 days after the entry
  date, from Upstox's expired-instruments expiries list, whose contracts are flagged
  `weekly=false`. See Section 2 for the calendar correction this produced for 2026.
- **Entry premium (PROVISIONAL):** close of the 1-minute bar starting 09:16 on the entry
  day, from Upstox `/v2/expired-instruments/historical-candle/<key>/1minute/<day>/<day>`.
  All 5 traded entries used an exact 09:16 bar; no fallback was needed.
- **Exit premium (PROVISIONAL):** close of the 1-minute bar starting 15:15 on the 5th
  session (entry day = session 1, same exit dates as the futures backtest).
  All 5 traded exits used an exact 15:15 bar; no fallback was needed.
- **Expiry inside hold (PROVISIONAL, honest default):** exit at 15:15 on the expiry day
  and the trade ends there; NO roll into a new call, and roll cost/decay is therefore
  never hidden. **No testable trade hits this case** — every traded monthly expiry falls
  after its 5th-session exit — so the rule is stated but unexercised.
- **Lot schedule (CORRECTED from the task's suggestion, per contract):** the task
  suggested 75 before Jan 2026 and 65 after. Upstox's own contract records say otherwise
  for the one 2024 trade: **25 for the 2024-10-31 monthly chain (all 230 contracts),
  75 for 2025-04-24 (all 232), 65 for all three 2026 chains (316 / 306 / 210 contracts).**
  This report uses each contract's own `lot_size` field. If NSE's circular history says
  something different for October 2024, that is a discrepancy to verify against NSE, not
  something adjusted here — but note the sensitivity: at lot 75 the 2024-10-04 trade would
  have lost ₹16,777.50 gross (₹16,856.76 net) instead of ₹5,592.50, and the options total would fall to
  about ₹65,711 net. The lot-25 figure is what Upstox returns and is used throughout.
- **Costs (PROVISIONAL approximation, on PREMIUM turnover only — premium x lot, not
  notional):** brokerage ₹20/order = ₹40 round trip; STT 0.0625% of sell premium value;
  exchange transaction 0.03503% of (buy + sell) premium value; SEBI ₹10 per crore of
  (buy + sell) premium value; stamp duty 0.003% of buy premium value; GST 18% on
  (brokerage + exchange + SEBI). Gross premium P&L is always shown alongside net.
  Total charges on 5 trades: only ₹584.14, because option premiums are small vs futures
  notional — costs are NOT what hurts this translation.
- **No Black-Scholes backfill.** No premium was estimated from spot or volatility for any
  missing trade. Missing trades are dropouts, listed in Section 3.

## 2. Data actually available — and what was NOT available

- **Upstox expired-instruments expiries list runs from 2024-10-03 to 2026-10-27 only.**
  The contracts endpoint returns empty for every earlier monthly expiry tested
  (2020-02-27, 2022-01-27, 2024-01-25 directly probed; all other pre-Oct-2024 entries
  fail the bounded monthly-expiry search in Section 1). The futures backtest had the same
  class of problem for futures history; here it bites harder because an option contract
  must exist for the exact strike and expiry.
- **Actual testable window: 2024-10-04 to 2026-07-15 (5 trades).** Not 2019–2026.
  The 25 dropouts are: all 16 entries from 2019–2021, all 6 from 2022, and 2024-01-18,
  2024-06-05, 2024-08-06 (no monthly expiry retrievable within 40 days after entry).
  A first-pass script bug that matched pre-2024 entries to the October 2024 chain was
  caught and fixed by bounding the monthly search to 40 days; the dropout list above is
  from the corrected run.
- **Expired option candles:** the v3 historical endpoint returns HTTP 400 for expired
  option keys. The working route is the v2 expired-instruments candle endpoint
  (`/v2/expired-instruments/historical-candle/<key>/1minute/<day>/<day>`), which returns
  full 375-bar days for all 5 traded contracts. An earlier 0-bar result for a wrongly
  matched August 2024 contract disappeared once the monthly-expiry bound was fixed; it
  is not evidence about August 2024 data.
- **Monthly-expiry calendar correction for 2026:** the futures backtest used a
  last-Thursday calendar (2026-03-26, 2026-04-30, 2026-07-30, stated there as unverified).
  Upstox's actual monthly contracts expire on the last Tuesday: **2026-03-30, 2026-04-28,
  2026-07-28**. All three 2026 options exits (03-20, 04-08, 07-15) fall before those
  expiries, so this changes contract identity only, not any P&L here — but it means the
  futures backtest's 2026 skip/roll dates deserve re-checking against the Tuesday calendar
  if that report is ever revised. It does not change its published numbers in this report.
- **Spot comparison prices** are the futures report's 09:16 / 15:15 1-minute spot closes
  for the same dates (Section 4 of that report). All 5 testable trades are on that basis.

## 3. Headline results (primary: monthly ATM call, previous-close strike, 1 lot)

| Metric | Value |
|---|---|
| Period actually tested | 2024-10-04 entry to 2026-07-15 exit (5 trades; 25 of 30 entries dropped out, Section 2) |
| Trades (1 lot each) | 5 |
| Wins / losses (net > 0) | 2 / 3 |
| Win rate | 40.0% |
| Gross premium P&L | +₹77,501.75 |
| Charges (formula in Section 1) | −₹584.14 |
| Net P&L (1 lot throughout) | +₹76,917.61 |
| Profit factor, gross | 5.60 (gross wins ₹94,336.00 / gross losses ₹16,834.25) |
| Profit factor, net | 5.51 (net wins ₹93,973.76 / net losses ₹17,056.15) |
| Expectancy, net | +₹15,383.52 per trade |
| Average net win / average net loss | +₹46,986.88 / −₹5,685.38 |
| Largest win / largest loss (net) | +₹50,839.48 (2026-04-01) / −₹9,548.99 (2026-03-16) |
| Max drawdown, net ₹ (peak-to-trough on cumulative net) | ₹9,548.99 — peak after 2025-04-08 (+₹37,483.89), trough after 2026-03-16 (+₹27,934.90) |
| Expiry-inside-hold cases | 0 (no roll, no expiry exit in the testable set) |

### By year (options net, 1 lot)

| Year | Trades | Wins | Net ₹ |
|---|---|---|---|
| 2024 | 1 | 0 | −5,650.39 |
| 2025 | 1 | 1 | +43,134.28 |
| 2026 (to 15 Jul) | 3 | 1 | +39,433.72 |
| **Total** | **5** | **2** | **+76,917.61** |

## 4. Full trade list (actual traded premiums; spot move over the same hold for comparison)

Entry premium = 09:16 1-min bar close on entry day; exit premium = 15:15 1-min bar close
on the 5th session. All bars exact (no fallback used). "Spot move" is the futures report's
spot entry→exit move over the same dates. **Flagged rows are where spot rose but the call
still lost, or the premium loss exceeded the spot move — decay/IV effect, not hidden.**

| # | Entry | Trigger % | Strike / monthly expiry | Entry prem. | Exit date / reason | Exit prem. | Prem. change | Spot move | Net ₹ / lot | Flag |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2024-10-04 | −2.12% | 25250 CE / 2024-10-31, lot 25 | 444.70 | 2024-10-10 / 5th_session_close | 221.00 | −223.70 | −209.60 | −5,650.39 | Premium lost slightly MORE than spot fell |
| 2 | 2025-04-08 | −3.24% | 22150 CE / 2025-04-24, lot 75 | 671.65 | 2025-04-16 / 5th_session_close | 1,249.00 | +577.35 | +891.75 | +43,134.28 | Call captured 65% of the spot rebound |
| 3 | 2026-03-16 | −2.06% | 23150 CE / 2026-03-30, lot 65 | 493.75 | 2026-03-20 / 5th_session_close | 348.15 | −145.60 | −39.80 | −9,548.99 | Premium loss 3.7x the spot fall — post-crash IV/theta bleed on a near-flat hold |
| 4 | 2026-04-01 | −2.14% | 22350 CE / 2026-04-28, lot 65 | 985.00 | 2026-04-08 / 5th_session_close | 1,770.15 | +785.15 | +1,162.80 | +50,839.48 | Call captured 68% of the spot rebound |
| 5 | 2026-07-09 | −2.12% | 23900 CE / 2026-07-28, lot 65 | 349.05 | 2026-07-15 / 5th_session_close | 321.70 | −27.35 | **+109.15** | −1,856.77 | **SPOT ROSE BUT THE CALL LOST — decay beat a +109-point rebound** |

Detail per trade (gross = premium change x lot; charges per Section 1):

| Entry | Contract | Entry bar | Exit bar | Gross ₹ | Charges ₹ | Net ₹ |
|---|---|---|---|---|---|---|
| 2024-10-04 | NIFTY 25250 CE 31 OCT 24 (`NSE_FO\|54784\|31-10-2024`) | 2024-10-04T09:16 | 2024-10-10T15:15 | −5,592.50 | 57.89 | −5,650.39 |
| 2025-04-08 | NIFTY 22150 CE 24 APR 25 (`NSE_FO\|79295\|24-04-2025`) | 2025-04-08T09:16 | 2025-04-16T15:15 | +43,301.25 | 166.97 | +43,134.28 |
| 2026-03-16 | NIFTY 23150 CE 30 MAR 26 (`NSE_FO\|54502\|30-03-2026`) | 2026-03-16T09:16 | 2026-03-20T15:15 | −9,464.00 | 84.99 | −9,548.99 |
| 2026-04-01 | NIFTY 22350 CE 28 APR 26 (`NSE_FO\|71963\|28-04-2026`) | 2026-04-01T09:16 | 2026-04-08T15:15 | +51,034.75 | 195.27 | +50,839.48 |
| 2026-07-09 | NIFTY 23900 CE 28 JUL 26 (`NSE_FO\|63935\|28-07-2026`) | 2026-07-09T09:16 | 2026-07-15T15:15 | −1,777.75 | 79.02 | −1,856.77 |

Cumulative net in trade order: −₹5,650.39 → +₹37,483.89 → +₹27,934.90 → +₹78,774.38 →
+₹76,917.61.

### Dropouts (25 entries, no premium fabricated for any of them)

All entries 2019-07-09 through 2022-06-14 (22 entries), plus 2024-01-18, 2024-06-05 and
2024-08-06: no expired monthly option contracts retrievable via Upstox within 40 days
after entry (expired-instruments expiries list starts 2024-10-03). Full per-entry dropout
records are in `options_trades.json` (status field).

## 5. Honest comparison

### (a) vs the futures/spot rebound backtest (same system, futures code)

| Figure | Futures/spot backtest, full (30 trades, spot proxy) | Futures/spot, same 5 entries | Options translation, same 5 entries |
|---|---|---|---|
| Net ₹ (1 lot) | +3,37,730.11 | +1,28,814.82 | +76,917.61 |
| Wins | 20/30 (66.7%) | 3/5 (60.0%) | 2/5 (40.0%) |
| Profit factor, net | 2.24 | 7.67 | 5.51 |
| Max drawdown | ₹1,40,336.12 | — (subset, not computed) | ₹9,548.99 (subset only; not comparable to a 30-trade drawdown) |

On the same 5 entries, options keep 60% of the futures net and lose one trade futures
wins (2026-07-09: futures +₹6,629.74 on a +109.15 spot move; options −₹1,856.77).
The two big rebound trades still win in both versions, but the call gives back roughly
a third of the spot move (65–68% capture) and bleeds on flat/down holds. Charges do not
explain the gap (₹584 options vs several thousand on the futures subset's notional-based
charges). **On testable evidence, the options translation HURTS vs futures.**

### (b) vs the Volrix card (PF 2.00, win 60.6%)

The options result (PF 5.51 net, win 40.0%) matches neither card figure — but on n=5
that comparison is meaningless either way: the card's trade count, capital base and
definitions are undisclosed (see Section 5 of the futures report), and this sample
contains none of the card's 2019–2023 history. No agreement or disagreement with the
card is claimed from 5 trades. The futures report's own comparison (PF 2.24, win 66.7%
on 30 spot-proxy trades) remains the closer, but still proxy-based, reference.

### Why the translation hurts on this window (mechanism, not proof)

1. **You buy the fear.** Entry is the morning after a ≥2% down day, when option
   premiums are elevated. The 2026-03-16 trade is the cleanest exhibit: spot ended the
   hold only −39.80 points lower, yet the ATM call lost −145.60 premium points.
   Something other than delta — collapsing IV and/or theta over 4 sessions — took
   roughly 100 extra points. IV was not separately measured, so this is inference from
   the premium-vs-spot gap, labelled as such.
2. **You keep only two-thirds of the rebound.** On both big wins the call captured
   65% (2025-04-08) and 68% (2026-04-01) of the spot move. An ATM call's delta is below
   1 and theta/IV work against it throughout the hold; futures/spot capture the full move.
3. **Small rebounds do not pay for the decay.** 2026-07-09 (+109.15 spot) still lost
   money in the call. The futures version's edge includes small positive holds; the
   options version needs a large rebound just to break even on premium.
4. **Data gaps dominate the verdict.** The 25 untestable trades include every 2019–2022
   entry and the March 2020 crash continuation (−₹1,02,775 futures loss on 2020-03-11).
   Whether options would have softened that crash loss (limited premium at risk, but a
   near-total premium wipeout was possible) or amplified it cannot be answered from
   Upstox's expired-instruments route. That is why the overall verdict stays
   INCONCLUSIVE despite the negative testable subset.

## 6. What this does and does not prove

- It proves, on actual traded premiums for 5 entries, that a monthly ATM call held
  5 sessions after a ≥2% Nifty down day is **positive in total (+₹76,918) but weaker
  than the same entries in futures/spot (+₹1,28,815)**, with a decay-driven loss on a
  rising hold.
- It does **not** prove the options translation is good or bad in general: n=5, no
  2019–2024 coverage, no crash-period observation.
- It does **not** use any estimated, Black-Scholes or spot-derived premium anywhere in
  the primary result. A Black-Scholes sensitivity was not run (it would answer a
  different question and could not be labelled as traded prices).
- A weekly-ATM-call sensitivity was **not** run. It is permitted as a labelled
  sensitivity only, and weekly calls decay faster than monthly ones over a 5-session
  hold, so it is unlikely to reverse the direction found here — but that is a hypothesis,
  not a result, and it is not reported as one.
- It does **not** change the futures/spot backtest, the v4 / (lA) verdicts, or any
  adoption decision. Separate system, paper only, no orders, no live trading.

## 7. Files

- This report: `volrix_nifty_large_down_rebound_options_backtest.md`
- Engine + fetch (read-only, no orders): `volrix_options/fetch_and_compute.py`
- Per-entry results incl. dropouts: `volrix_options/options_trades.json`
- Upstox expiries list used: `volrix_options/expiries.json`
- Raw 1-min option candles per traded contract: `volrix_options/candles_<entry>_<strike>CE_<expiry>.json`
- Source entry universe: `volrix/positions_daily.json` (futures backtest)
