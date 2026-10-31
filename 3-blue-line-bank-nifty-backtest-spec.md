# 3-Blue-Line Bank Nifty — Backtest Specification

**Version:** Draft v1.0 — 28 October 2026
**Status:** Testable spec, not a trading recommendation. Do not trade this live on the basis of this spec alone.
**System being tested:** Intraday Bank Nifty index options, previous-day high / close / low as "Blue Lines", 9:30 AM opening range, 5-minute closes, 200-point clear-room filter, 1 lot, -50 option points stop / +100 option points target, cost-trail, one trade per day.

> **Important distinction:** Anything marked **[ORIGINAL]** comes from the document you shared. Anything marked **[ASSUMPTION — confirm before running]** was missing or ambiguous in that document and has been given a precise, testable definition here so the backtest can actually be run. Changing an assumption after seeing results is not allowed in the primary test — that is what the sensitivity tests in Section 12 are for.

---

## 1. Objective and hypothesis

**Objective:** Measure, after all trading costs and slippage, whether this exact rule set would have made money, how much drawdown it would have caused, and in which market conditions it worked or failed.

**Hypothesis to test (not a claim):** Breakouts, breakdowns, and bounces at previous-day and multi-day levels, filtered for at least 200 points of clear room, produce a positive expectancy per trade with a 1:2 stop-to-target ratio.

**Primary result to report first:** Expectancy per trade after costs, in option points and in rupees for 1 lot. Everything else is supporting evidence.

---

## 2. Instrument and market regime

- **Underlying:** Bank Nifty index, NSE.
- **Instrument:** Bank Nifty index options, calls (CE) and puts (PE), bought only. No selling, no spreads, no futures in the primary test.
- **Expiry:** Monthly contracts only. Bank Nifty weekly options were discontinued in November 2024, and monthly contracts now expire on the last Tuesday of the month.
- **Contract selection [ASSUMPTION — confirm]:** The nearest monthly expiry contract. Do not switch contracts intraday.
- **Strike selection [ORIGINAL, with clarification]:** ATM at signal time, or the nearest slightly ITM strike if the ATM strike is illiquid. Strike interval for Bank Nifty is 100 points. Record the strike chosen on every trade.
- **Lot size:** 30 units per lot for January 2026 onwards. Older contracts used 35. Report P&L in both option points and rupees, so a lot-size change does not distort the comparison across periods.
- **Capital deployed per trade:** Entry premium × 30. This is not the same as risk. Risk is defined in Section 8.

---

## 3. Data required — this is the most important section

**Do not backtest this system on spot prices converted with a fixed 0.50 delta.** That is the single easiest way to get a misleading result. Option premiums move with delta, gamma, IV, and theta, not just spot.

Required data, all in IST:

| Data | Granularity | Purpose |
|---|---:|---|
| Bank Nifty spot OHLC | 15-minute and 5-minute | Blue Lines, opening range, room measurement, trail trigger |
| Bank Nifty option premiums for the traded strike (open, high, low, close) | 5-minute, ideally 1-minute for stop/target sequencing | Entry, stop, target, trail, square-off |
| Option bid/ask, if available | At signal time | Liquidity filter / slippage reality check |
| Expiry calendar and trading holidays | Daily | Days-to-expiry (DTE) bucketing, expiry-week analysis |
| Previous-day spot OHLC | Daily | PDH / PDC / PDL and closing strength |

**Data quality checks before any result is trusted:**
- No missing 5-minute candles between 9:15 and 15:30 on traded days.
- No use of a day's own high/low/close to set that same day's Blue Lines (look-ahead check).
- Timestamps converted to IST and aligned across spot and option series.
- Option series must be for the exact strike and expiry traded, not a continuous "ATM premium" series stitched from different strikes without documentation.

If genuine historical option premium data cannot be obtained, the honest output is "not backtestable with available data", not a spot-based proxy result presented as an option backtest.

---

## 4. Pre-market calculations (after 3:30 PM, for the next day)

### 4.1 The 3 Blue Lines [ORIGINAL]
- **Top Blue Line = Previous Day's High (PDH)**
- **Middle Blue Line = Previous Day's Close (PDC)**
- **Bottom Blue Line = Previous Day's Low (PDL)**

### 4.2 Multi-day pivots [ASSUMPTION — confirm]
The original doc refers to "major swing highs/lows" without a definition. For v1, use:
- **Prior 5-day high:** highest high of the 5 trading days before today, excluding yesterday if it is already PDH.
- **Prior 5-day low:** lowest low of the 5 trading days before today, excluding yesterday if it is already PDL.

Only un-breached levels count: a prior 5-day high that price has already closed above on a 5-minute candle before today is removed. These, plus PDH/PDC/PDL, form the full level set used for room measurement and targets.

### 4.3 Closing strength and bias [ORIGINAL formula, ASSUMPTION for the middle zone]

```
Closing Strength % = (Close - Low) / (High - Low) × 100
```

Using the previous day's spot OHLC.

| Closing strength | Bias for primary test [ASSUMPTION] |
|---:|---|
| < 35% | Bearish: only PE setups allowed |
| 35% to 80% | Neutral: both CE and PE setups allowed |
| > 80% | Bullish: only CE setups allowed |

The original doc gave no rule for 35–80%. The neutral treatment above is the assumption to test. A bias-on/bias-off sensitivity test is included in Section 12.

---

## 5. Session timeline

| Time (IST) | Rule |
|---|---|
| 9:15–9:30 | **No trades.** This 15-minute candle defines the opening range. |
| 9:30 | Opening Range High (ORH) = high of the 9:15–9:30 candle. Opening Range Low (ORL) = low of the same candle. |
| 9:30–14:30 | Entry window. No new entries after 14:30. |
| 15:15 | **Square-off [ASSUMPTION]:** Any open trade is closed at the option premium at 15:15, whatever its P&L. This closes the "what if neither stop nor target hits" gap in the original doc. |

---

## 6. Entry rules — formalised

**General rules for every entry:**
- Only the **first** valid signal after 9:30 counts. One trade per day, maximum. If the first signal is invalidated before execution, that day is a no-trade day — do not hunt for a second setup.
- A signal is only valid on a **completed 5-minute candle close**, never on a mid-candle wick.
- **Execution [ASSUMPTION]:** Enter at the option premium at the open of the next 5-minute candle after the signal candle closes. Entering at the signal candle's own close is a look-ahead shortcut and is only used as a sensitivity variant.
- If multiple setup types trigger on the same candle, priority is: Breakout/Breakdown > Retest > Bounce.

### 6.1 Breakout entry — CE [ORIGINAL]
All must be true:
1. A 5-minute candle closes above **both** ORH **and** the nearest Blue Line resistance above spot at that time.
2. Clear room (Section 7) is at least 200 index points to the next Blue Line above the entry spot.
3. Bias allows a CE trade (Section 4.3).

### 6.2 Breakdown entry — PE [ORIGINAL]
Mirror image:
1. A 5-minute candle closes below **both** ORL **and** the nearest Blue Line support below spot at that time.
2. Clear room is at least 200 index points to the next Blue Line below the entry spot.
3. Bias allows a PE trade.

### 6.3 Retest entry [ORIGINAL concept, ASSUMPTION for precision]
After a breakout/breakdown as in 6.1/6.2, price pulls back to within 25 index points of the broken level, then a 5-minute candle closes back in the breakout direction. Room is re-checked at the retest close. This counts as the day's one trade if no earlier trade was taken.

### 6.4 Bounce rejection entry [ORIGINAL concept, ASSUMPTION for precision]
**PE bounce at resistance:**
1. Price is in a bearish or neutral bias regime.
2. A 5-minute candle's high reaches or crosses a Blue Line resistance, but the candle closes back below that line.
3. The candle is bearish (close < open) and its upper wick is at least 1.5× its body. Body = |close − open|. Upper wick = high − max(open, close). If body is zero, the trade is invalid.
4. Clear room of at least 200 index points to the next Blue Line below.

**CE bounce at support:** Mirror image — low reaches or crosses a Blue Line support, candle closes back above it, bullish candle (close > open), lower wick at least 1.5× body, 200 points of room above.

---

## 7. The clear-room filter [ORIGINAL]

```
For CE: Room = (Next Blue Line above entry spot) − (Entry spot)
For PE: Room = (Entry spot) − (Next Blue Line below entry spot)
```

- **Rule:** Room must be ≥ 200 index points, measured from the signal candle's close spot price.
- The "next Blue Line" means the nearest level in the full set from Section 4 (PDH/PDC/PDL plus un-breached prior 5-day high/low).
- If there is no next Blue Line in that direction (for example, price is above all known resistance), the room is treated as unbounded and the filter passes — record this separately, because those trades are a different population.

The original 200-point derivation (100 option points ÷ 0.50 delta) is retained as the rationale, but the backtest must **not** assume delta stays at 0.50. Actual option premiums decide the outcome.

---

## 8. Exit and risk rules

| Rule | Value |
|---|---|
| Position size | Exactly 1 lot (30 units) |
| Hard stop-loss | Entry premium − 50 option points |
| Profit target | Entry premium + 100 option points |
| Cost-trail [ORIGINAL] | When spot moves 100 index points in your favour from entry spot, move the stop to entry premium (breakeven before costs). Checked at 5-minute closes. Trail applies once. |
| Square-off | 15:15 IST at prevailing option premium, if neither stop nor target has hit |
| One-and-done | Stop for the day once stop, target, trail-exit, or square-off occurs |

**Execution sequencing [ASSUMPTION]:** Within a single 5-minute option candle, if both stop and target levels are touched, assume the stop was hit first (conservative). If the trail level and the stop are both touched, assume the stop first.

**Risk per trade (before costs):**
- Losing trade: 50 points × 30 = ₹1,500
- Winning trade: 100 points × 30 = ₹3,000
- Breakeven / trailed trade: approximately ₹0 before costs, negative after costs

**Risk as a percentage [INPUT REQUIRED]:** ₹1,500 is not a risk percentage until trading capital is supplied. Formula: `Risk % = 1,500 / trading capital × 100`, before costs and slippage. Supply this number before interpreting drawdown.

---

## 9. The missing Filter 4 — proposed [ASSUMPTION — confirm]

The original doc promises 4 filters but lists 3. For the primary test, Filter 4 is a **liquidity + expiry gate**:

1. **Days-to-expiry:** Only trade when DTE is 4 or more trading days before expiry. The final 3 trading days before monthly expiry are excluded from the primary test and reported as a separate segment.
2. **Liquidity:** If bid/ask data is available, skip the trade if the bid-ask spread at signal time exceeds 10 option points. If bid/ask data is unavailable, this filter is marked "not testable" and slippage sensitivity (Section 10) becomes the control instead.

Rationale: monthly options far from expiry and very close to expiry behave differently, and wide spreads silently eat the 1:2 ratio.

---

## 10. Costs and slippage — must be included

Use the actual broker's charge structure for the period, not a guess. At minimum, include per round trip:

- Brokerage (flat per order, as charged by your broker)
- STT, exchange transaction charges, GST, SEBI charges, stamp duty — via the broker's charges calculator or contract notes
- **Slippage sensitivity:** Run the primary result at 0, 3, and 5 option points per leg. Report all three. A system that is only profitable at 0 slippage is not a tradable system.

Report results **gross, after brokerage/charges only, and after charges + slippage**. The after-charges-plus-slippage number is the headline.

---

## 11. Backtest design

- **Regime period:** Start no earlier than November 2024, when Bank Nifty moved to monthly-only expiries. Earlier weekly-expiry data is a different product and must not be mixed into the primary result.
- **Primary split [ASSUMPTION]:**
  - In-sample: December 2024 – June 2025 (rule definitions locked here, if any definitional fixes are needed)
  - Out-of-sample: July 2025 – present (no rule changes allowed)
- **No optimisation loop:** Parameters (200 room, −50/+100, 1.5× wick, 25-point retest band) are fixed before the run. Sensitivity tests in Section 12 are diagnostic only and must be labelled as such.
- **Minimum sample:** Do not draw a conclusion from fewer than 100 out-of-sample trades. Report the trade count prominently. With one trade per day maximum, this takes months of data.

---

## 12. Metrics and pre-registered pass criteria

### Metrics to compute (out-of-sample, after costs + slippage)
- Total trades, no-trade days, trades per month
- Win rate, average win, average loss, largest win, largest loss
- **Expectancy per trade** = (win rate × average win) − (loss rate × average loss)
- Profit factor = gross wins / gross losses
- Maximum drawdown in points, rupees, and % of trading capital
- Maximum consecutive losses, longest losing streak in days
- Monthly P&L table and equity curve
- Breakeven win rate for reference: 50 / (50 + 100) = 33.3% before costs; higher after costs

### Proposed pass criteria — confirm before running
A system is only worth forward-testing if **all** of these hold out-of-sample:
1. Expectancy per trade > 0 after costs + 3 points slippage per leg.
2. Profit factor > 1.1 after costs.
3. Maximum drawdown < 20% of stated trading capital.
4. At least 100 out-of-sample trades.
5. The result is not driven by a single month or a handful of trades (check monthly breakdown).

These thresholds are proposals, not guarantees. If they are changed, change them before the run and record why.

### Sensitivity tests (run after the primary result is locked)
- Room: 150 / 200 / 250 points
- Stop/target: −40/+80, −50/+100, −60/+120
- Entry at signal close vs next candle open
- Trail on vs trail off
- Bias filter on vs off
- Bounce trades included vs excluded
- Expiry-week (last 3 trading days) included vs excluded
- DTE buckets: 4–10 days, 11–20 days, 21+ days

### Segment breakdowns (always report)
- Breakout vs retest vs bounce
- CE vs PE
- Bias regime: bearish / neutral / bullish
- Gap days vs non-gap days (gap defined as open vs previous close beyond ±500 index points — sensitivity, not a primary filter)
- Expiry week vs non-expiry week

---

## 13. Trade log — required columns

For every trading day, one row, even on no-trade days:

```
date, bias, closing_strength_pct, PDH, PDC, PDL, prior_5d_high, prior_5d_low,
ORH, ORL, DTE, signal_time, setup_type, direction, strike, expiry,
entry_spot, entry_premium, entry_time, room_points,
stop_premium, target_premium, trail_triggered,
exit_time, exit_premium, exit_reason (target / stop / trail / squareoff / no_trade),
gross_points, gross_inr, costs_inr, slippage_points, net_inr,
cumulative_net_inr, drawdown_inr, notes
```

No trade log, no credible backtest. Summary statistics alone are not enough to audit.

---

## 14. Implementation checklist (for a data-engineering build)

1. Ingest and validate spot 15m/5m and option 5m data; log missing candles.
2. Compute prior-day Blue Lines and closing strength using only data available before the open (no look-ahead).
3. Compute opening range from the 9:15–9:30 candle only.
4. Generate signals candle by candle, in chronological order, stopping after the first valid signal per day.
5. Simulate exits candle by candle, applying the stop-before-target sequencing rule.
6. Apply costs and slippage at trade level, not as a portfolio-level haircut.
7. Split in-sample / out-of-sample before looking at out-of-sample results.
8. Produce the trade log, monthly table, equity curve, and segment breakdowns from the same run — no hand-edited results.
9. Re-run with sensitivity parameters only after the primary result is saved and timestamped.

---

## 15. Limitations — what this backtest cannot prove

- Past performance does not predict future results, especially across volatility regimes.
- Historical liquidity and spreads may differ from live conditions.
- One trade per day means statistical confidence builds slowly.
- The backtest assumes perfect discipline. Live one-and-done compliance, missed signals during work hours, and platform issues are not modelled.
- Taxes on net trading profit are separate from trading charges and are not included in expectancy.

---

## 16. Open decisions — confirm before running

- [ ] Trading capital (to convert ₹1,500 risk into a risk % and drawdown %)
- [ ] Broker and exact charge structure
- [ ] Historical option premium data source
- [ ] DTE gate: confirm excluding the last 3 trading days before expiry
- [ ] Square-off time: confirm 15:15 IST
- [ ] Bounce definition: confirm 1.5× wick rule and 25-point retest band
- [ ] Bias treatment for 35–80%: confirm neutral = both directions allowed
- [ ] Backtest period end date and in-sample / out-of-sample split
- [ ] Pass criteria in Section 12: confirm or amend before the run

---

*End of spec. Next step after confirmation: build the data pipeline and trade log from Section 13–14, then run the primary test exactly once before any sensitivity analysis.*
