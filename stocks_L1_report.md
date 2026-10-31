# LINE L1 — LEVEL-NATIVE ENTRIES on Chandu's own 25 stocks — COMPLETE

**Verdict: NO CANDIDATE. The level family, traded exactly in Chandu's own
philosophy, has no honest edge on his 25 stocks at any tested exit — every one
of the 18 cells loses money in total, and every cell loses to its own
lag-placebo.** Controls ran in the same run (mandatory protocol): timing audit
**68,865 trades, 0 violations**; Oct 29–30 aggregation validated (1,875 bars
re-checked vs the cached Oct 28 bars, 0 mismatches; all 25 symbols added for
both days). The numbers below are therefore the honest ones, not machinery
artefacts.

Basis: equity cash, LONG/SHORT, paper only, real ₹0, provisional per
100 shares, net = gross − ₹40/trade, HOME 25 only, Jan–Oct 2026. Spec frozen
in [stocks_L1_frozen.md](sandbox://workspace/trading/stocks_L1_frozen.md)
before scoring. Engine: `stocks_L1.py`; full results:
[stocks_L1_results.json](sandbox://workspace/trading/stocks_L1_results.json);
best-cell trade dump:
[stocks_L1_best_trades.csv](sandbox://workspace/trading/stocks_L1_best_trades.csv).

## What was tested
- **L1-A Breakout-Retest** — close breaks PDH/PDL, a later 5-min retest holds
  the level (his Filter-4 shape), enter next bar in the break direction.
- **L1-B Level Rejection** — bar touches PDH/PDL within 0.1% and closes back
  inside; enter against the touch at the next bar's open.
- **L1-C Multi-Day Break** — first intraday break of the prior-20-day
  high/low; enter next bar, no retest wait.
Each × exits {T05/S050, T10/S050, T125/S065} × contexts {all, Nifty below50}.
Re-entry allowed (his rule), cap 4 entries/stock/day. Placebo = identical
cells on levels shifted +1 day (yesterday's levels used today).

## Results — all 18 cells (Jan–Oct 2026)
| Cell | Trades | Net ₹ | Jan–May | Jun–Oct | Oct | Breadth | Exp/trade | Months green | Placebo net ₹ |
|---|---|---|---|---|---|---|---|---|---|
| L1-A · T05/S050 · all | 5,546 | −277,904.65 | −158,072.70 | −119,831.95 | −2,100.64 | 2/25 | −50.11 | 0/10 | −183,466.16 |
| L1-A · T05/S050 · below50 | 3,802 | −190,335.05 | −133,849.14 | −56,485.91 | −2,100.64 | 1/25 | −50.06 | 0/10 | −123,919.91 |
| L1-A · T10/S050 · all | 4,759 | −245,232.39 | −124,874.75 | −120,357.64 | +12,567.47 | 3/25 | −51.53 | 2/10 | −178,863.83 |
| L1-A · T10/S050 · below50 | 3,252 | −179,303.01 | −126,296.45 | −53,006.56 | +12,567.47 | 2/25 | −55.14 | 2/10 | −125,241.21 |
| L1-A · T125/S065 · all | 4,175 | −210,271.54 | −67,761.76 | −142,509.78 | +15,626.92 | 2/25 | −50.36 | 2/10 | −170,551.95 |
| L1-A · T125/S065 · below50 | 2,847 | −153,845.61 | −80,195.91 | −73,649.70 | +15,626.92 | 4/25 | −54.04 | 2/10 | −117,611.51 |
| L1-B · T05/S050 · all | 7,535 | −348,224.11 | −173,242.73 | −174,981.38 | −62,341.28 | 3/25 | −46.21 | 0/10 | −210,876.09 |
| L1-B · T05/S050 · below50 | 5,091 | −277,168.16 | −144,226.31 | −132,941.85 | −62,341.28 | 2/25 | −54.44 | 1/10 | −176,772.45 |
| L1-B · T10/S050 · all | 6,487 | −316,499.89 | −158,738.33 | −157,761.56 | −36,078.32 | 2/25 | −48.79 | 1/10 | −144,657.13 |
| L1-B · T10/S050 · below50 | 4,376 | −211,060.89 | −121,209.33 | −89,851.56 | −36,078.32 | 3/25 | −48.23 | 1/10 | −124,526.82 |
| L1-B · T125/S065 · all | 5,635 | −253,184.52 | −123,962.62 | −129,221.90 | −32,064.80 | 3/25 | −44.93 | 1/10 | −110,942.36 |
| L1-B · T125/S065 · below50 | 3,801 | −155,524.26 | −80,638.80 | −74,885.46 | −32,064.80 | 5/25 | −40.92 | 2/10 | −103,806.72 |
| L1-C · T05/S050 · all | 1,223 | −53,919.97 | −42,680.46 | −11,239.51 | −1,541.03 | 3/25 | −44.09 | 2/10 | −44,451.20 |
| L1-C · T05/S050 · below50 | 818 | −32,236.60 | −32,301.97 | +65.37 | −1,541.03 | 5/25 | −39.41 | 1/10 | −24,691.86 |
| L1-C · T10/S050 · all | 1,223 | −40,545.35 | −51,814.90 | +11,269.55 | −3,481.45 | 8/25 | −33.15 | 3/10 | −38,469.95 |
| L1-C · T10/S050 · below50 | 818 | −48,090.73 | −50,472.13 | +2,381.40 | −3,481.45 | 6/25 | −58.79 | 2/10 | −32,927.67 |
| L1-C · T125/S065 · all | 1,223 | −53,011.21 | −43,332.21 | −9,679.00 | −6,133.16 | 7/25 | −43.35 | 3/10 | −36,341.01 |
| L1-C · T125/S065 · below50 | 818 | −47,164.16 | −40,882.37 | −6,281.79 | −6,133.16 | 7/25 | −57.66 | 2/10 | −27,811.54 |

**Gate outcome: 0 of 18 cells pass a single money leg.** No cell is positive
in total, in Jan–May, or (except the two L1-C T10/T05 Jun–Oct slices, against
deeply negative Jan–May) in a half. No cell reaches breadth 15/25 (best 8/25),
expectancy +₹100 (best −₹33.15), or 9/10 green months (best 3/10) — so there
is **no month-repair flag either**.

## The placebo result is the sharpest finding
In **all 18 cells the placebo beats the real cell**: trading at *yesterday's
stale* PDH/PDL/20-day levels loses less than trading at the true levels.
Entering at the actual prior-day levels on these 25 stocks is therefore not
merely edgeless — it is systematically worse than entering at arbitrary stale
levels. Net expectancy is −₹33 to −₹59 per trade against a ₹40 cost, i.e.
gross expectancy is ≈ ₹0 to −₹19/trade: at 5-minute resolution with
next-bar-open fills, the level itself carries no exploitable information on
this universe in either direction (breakout-retest, rejection, and 20-day
break all fail), and what little gross movement exists is on the wrong side.

Two honest nuances, neither of which changes the verdict:
- **L1-A's October is positive at the wider exits** (+₹12,567.47 at T10,
  +₹15,626.92 at T125/S065 — October 2026 was 100% below-50DMA days, so both
  contexts coincide there). But the same cells lose −₹125k/−₹68k in Jan–May;
  this is the known October-only pattern, not a system.
- **L1-C (20-day break) is the least-bad mechanism** — fewest trades (1,223),
  best expectancy (−₹33.15 at T10/S050·all), best breadth (8/25), and a
  positive Jun–Oct (+₹11,269.55) — but Jan–May is −₹51,814.90 and it still
  loses to its placebo. If the level family is ever revisited, it is here,
  and only with a mechanism change, not an exit tweak.

## Month tables (net ₹ per month, Jan→Oct)
- **L1-A · T05/S050 · all:** −26,181 · −66,171 · −4,901 · −32,357 · −28,462 · −38,382 · −25,221 · −36,162 · −17,966 · −2,101
- **L1-A · T05/S050 · below50:** −22,343 · −48,119 · −4,901 · −37,349 · −21,137 · −28,605 · −908 · −6,907 · −17,966 · −2,101
- **L1-A · T10/S050 · all:** −29,699 · −61,240 · +17,583 · −40,661 · −10,858 · −51,414 · −17,302 · −41,830 · −22,378 · +12,567
- **L1-A · T10/S050 · below50:** −33,540 · −49,931 · +17,583 · −47,100 · −13,309 · −35,988 · −118 · −7,090 · −22,378 · +12,567
- **L1-A · T125/S065 · all:** −18,590 · −47,411 · +42,279 · −29,015 · −15,025 · −61,894 · −24,520 · −39,502 · −32,222 · +15,627
- **L1-A · T125/S065 · below50:** −26,776 · −37,596 · +42,279 · −39,838 · −18,265 · −44,586 · −2,532 · −9,937 · −32,222 · +15,627
- **L1-B · T05/S050 · all:** −12,220 · −56,839 · −48,069 · −33,666 · −22,449 · −22,648 · −627 · −31,587 · −57,778 · −62,341
- **L1-B · T05/S050 · below50:** −8,090 · −48,546 · −48,069 · −24,483 · −15,039 · −12,640 · −305 · +123 · −57,778 · −62,341
- **L1-B · T10/S050 · all:** +2,839 · −63,734 · −52,841 · −25,732 · −19,270 · −19,111 · −15,014 · −47,324 · −40,234 · −36,078
- **L1-B · T10/S050 · below50:** +10,875 · −55,859 · −52,841 · −14,629 · −8,756 · −10,962 · −2,523 · −54 · −40,234 · −36,078
- **L1-B · T125/S065 · all:** +6,749 · −41,715 · −50,720 · −12,916 · −25,361 · −2,565 · −21,616 · −39,131 · −33,846 · −32,065
- **L1-B · T125/S065 · below50:** +13,967 · −31,320 · −50,720 · −3,139 · −9,427 · +2,213 · −4,187 · −7,001 · −33,846 · −32,065
- **L1-C · T05/S050 · all:** −9,296 · −8,789 · −2,255 · −14,875 · −7,466 · −2,427 · +8,659 · −25,926 · +9,995 · −1,541
- **L1-C · T05/S050 · below50:** −2,303 · −7,544 · −2,255 · −13,853 · −6,347 · −4,105 · −78 · −4,206 · +9,995 · −1,541
- **L1-C · T10/S050 · all:** −5,993 · −8,832 · −11,207 · −19,344 · −6,439 · +855 · +26,672 · −23,276 · +10,500 · −3,481
- **L1-C · T10/S050 · below50:** −4,432 · −9,513 · −11,207 · −20,357 · −4,965 · −2,915 · +662 · −2,384 · +10,500 · −3,481
- **L1-C · T125/S065 · all:** −10,290 · −4,571 · −10,303 · −17,955 · −213 · +2,454 · +17,788 · −26,528 · +2,741 · −6,133
- **L1-C · T125/S065 · below50:** −7,612 · −3,483 · −10,303 · −18,886 · −598 · −1,268 · +811 · −2,432 · +2,741 · −6,133

## Controls (same run, as mandated)
- **Timing audit:** 68,865 trades (real + placebo, all cells) independently
  re-verified against levels re-derived from `spot_daily.csv` — trigger
  conditions, break/retest structure for L1-A, first-break property for L1-C,
  entry = open of the bar after the trigger bar, no overlapping trades,
  ≤ 4 entries/stock/day: **0 violations**.
- **Aggregation check:** Oct 29–30 built from the 1-min cache; 1,875 bars
  re-validated against cached Oct 28 bars, **0 mismatches**.
- **Placebo:** all 18 real cells score BELOW their lag-placebos (table above).

## Honest ceiling of the level family (on his 25)
The best cell by net is **L1-C · T05/S050 · below50 at −₹32,236.60** — the
family's ceiling is negative under every frozen configuration. No candidate
spec is frozen and no December judging is scheduled for L1. The conclusion is
narrow and mechanical, not a judgement on level trading in general: on these
25 stocks, at 5-minute bars, entering on the next bar's open after a PDH/PDL
or 20-day level event, with 0.5–1.25% targets, the level event itself holds
no edge after a ₹40 cost — consistent with the programme's standing diagnosis
that pure price-structure entries on this universe have ≈ ₹0 gross expectancy,
and with the index experience that his level setups work there because of
what the premium/strike structure adds, which equity cash does not have.
