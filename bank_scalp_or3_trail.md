# Bank Nifty Scalping — OR3-TRAIL: trailing stop on 3-minute opening-range bursts

Bank Nifty only. Paper only, real money ₹0. Premiums per 1 lot (30), cost ₹220/trade.
Window: **2026-01-01 – 2026-10-27, 192 trading days**, genuine 1-min candles
(`scalp_1min_data/`). This scores the one untested cell of the frozen Charter v2 —
trailing stops on the 3-min OR-burst signal. A measurement only: the scalp engine's
TERMINATED SATURATED verdict is unchanged, nothing is banked, nothing re-tuned.

**One precision on "untested":** the trail-distance ridge (7/4/3) previously ran only
on 1-min OR bursts (Cycles 9–11). The trail-5 point on 3-min *was* scored in Cycle 7–8
as "OR3-TRAIL" — it is re-run here in the same script for a uniform table and
**reproduces Cycle 7–8 row-for-row exactly (605/605 trades)**, which also validates
the machinery. Trail 7, 4 and 3 on 3-min are the genuinely new cells.

## Frozen definition (Charter v2 verbatim, decision bars 3-min)

- **3-min bars** = OHLC aggregation of three consecutive genuine 1-min bars of the
  same day, aligned 09:15, 09:18, … (aggregation up from genuine finer data —
  legitimate; no bar is ever split down).
- **Opening range** = spot high/low over 09:15–09:30, i.e. the first five 3-min bars
  (starting 09:15, 09:18, 09:21, 09:24, 09:27).
- **Signal** = first 3-min bar (bars starting 09:30 through 13:30) whose close crosses
  beyond the OR high (→ CE) or OR low (→ PE) relative to the previous 3-min bar's
  close; fresh crosses thereafter re-trigger (re-entry by design).
- **Entry** = open of the next 1-min option candle after the signal 3-min bar closes;
  ATM nearest 100 at the last close before entry; expiry in force for the date.
- **Exit (trailing):** initial stop −9; when a 1-min bar's high first reaches ≥ entry
  +8 the trailing stop activates at running peak high − trail distance, updated after
  each bar's checks (no intra-bar lookahead); stop tested before any target logic
  within a bar; **hard max hold 5 minutes** (entry bar + 4, residual exit at the open
  of entry bar +5).
- **Re-entry/cap:** flat-only (next entry strictly after the previous exit bar),
  cap 8 entries/day. UNIQUE-ONCE per (variant, date, direction, trigger bar).
- Variants: trail distance **7 / 5 / 4 / 3** — spec ("T", act +8, trail, stop −9).

## Results — full window (Jan 1 – Oct 27 2026)

All four variants take the same 605 signals (only exits differ). NOT_COMPUTED = 0,
busy-skips = 0, timing audit = **0 violations** on all four, independent re-sum from
the written CSV matched to the paisa on all four. Halves = trading-day split,
H1 = Jan 1 – Jun 9 (96 days), H2 = Jun 10 – Oct 27 (96 days).

| Variant | Trades | Gross ₹ | Gross pts/tr | Net ₹ | Win % | Days green % | Median day ₹ | Worst day ₹ | Best day ₹ | H1 ₹ | H2 ₹ | Ex-top-3 ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OR3-TRAILT7 | 605 | +27,319.50 | 1.51 | **−105,780.50** | 27.4 | 25.0 | −496.50 | −3,543.50 | +1,887.50 | −58,907.50 | −46,873.00 | −111,395.00 |
| OR3-TRAIL (5) | 605 | +33,948.00 | 1.87 | **−99,152.00** | 30.7 | 29.4 | −490.00 | −3,483.50 | +1,539.50 | −51,290.50 | −47,861.50 | −103,520.00 |
| OR3-TRAILT4 | 605 | +37,381.50 | 2.06 | **−95,718.50** | 31.9 | 29.4 | −490.00 | −3,453.50 | +1,629.50 | −48,656.50 | −47,062.00 | −100,103.00 |
| OR3-TRAILT3 | 605 | +43,066.50 | 2.37 | **−90,033.50** | 36.0 | 30.0 | −490.00 | −3,423.50 | +1,719.50 | −46,322.50 | −43,711.00 | −94,508.00 |

Gross pts/trade vs the **7.33-pt cost breakeven**: 1.51 / 1.87 / 2.06 / 2.37 — the best
cell (trail 3) captures **32%** of breakeven. Cost load at 605 trades = ₹133,100 per
variant against gross of ₹27–43k. Days traded: 180 of 192 for every variant.
**Every month is negative for every variant (40 of 40 variant-months red)** — full
month table in `bank_scalp_or3_trail_summary.json`.

### Placebos (same run)

| Variant | Lag +1 decision bar (+3 min) ₹ | Lag +1 min (engine convention) ₹ | Random mean ₹ | Random range ₹ |
|---|---|---|---|---|
| OR3-TRAILT7 | −129,027.50 | −116,517.50 | −121,811.53 | −141,670.70 … −103,230.20 |
| OR3-TRAIL (5) | −120,614.00 | −113,820.50 | −116,365.27 | −138,147.20 … −95,671.70 |
| OR3-TRAILT4 | −116,802.50 | −111,981.50 | −113,415.42 | −133,447.70 … −94,703.00 |
| OR3-TRAILT3 | −111,888.50 | −112,280.00 | −109,956.80 | −135,012.20 … −88,740.20 |

All four variants beat both lag placebos and the random-placebo **mean** — the signal
is not worthless. Stated exactly: the single best of the 20 random draws marginally
exceeds each variant's net (by ₹1.0–3.5k), i.e. in net terms the family sits inside
the top of the random range even while beating its centre — gross dominance at
~⅓ of breakeven does not survive contact with ₹220/trade.

### October slice (labelled slice, Oct 1–27, 17 trading days; 16 had OR3 trades)

| Variant | Trades | Net ₹ | Gross pts/tr | Days green % |
|---|---|---|---|---|
| OR3-TRAILT7 | 44 | −6,761.00 | 2.21 | 31.3 |
| OR3-TRAIL (5) | 44 | −7,800.50 | 1.42 | 37.5 |
| OR3-TRAILT4 | 44 | −7,560.50 | 1.61 | 37.5 |
| OR3-TRAILT3 | 44 | −6,990.50 | 2.04 | 37.5 |

No variant is net-positive in October either; the slice ordering (trail 7 least-bad
on net) reverses the full-window ridge ordering — slice noise, as expected at n=44.

## Head-to-head vs OR1-TRAILT3 (the terminated engine's best variant)

| | OR3-TRAILT3 | OR1-TRAILT3 |
|---|---|---|
| Trades | 605 | 859 |
| Gross ₹ | +43,066.50 | +84,184.80 |
| Gross pts/trade | **2.37** | **3.27** |
| Net ₹ | −90,033.50 | −104,795.20 |
| Win % | 36.0 | 37.4 |
| Days green % | 30.0 | 25.4 |
| Median / worst / best day ₹ | −490 / −3,423.50 / +1,719.50 | −490 / −3,920 / +3,369.50 |
| H1 / H2 ₹ | −46,322.50 / −43,711.00 | −49,309.00 / −55,486.20 |
| Lag (+1 min) / random mean ₹ | −112,280.00 / −109,956.80 | −138,460.00 / −153,365.32 |
| October net (gross pts/tr, days green) | −6,990.50 (2.04, 37.5%) | −9,339.50 (3.13, 29.4%) |

The trail ridge has the same shape on both timeframes — gross rises monotonically as
the trail tightens (3-min: 1.51 → 1.87 → 2.06 → 2.37; 1-min: 2.53 → 2.91 → 3.14 →
3.27) — but the 3-min ridge sits **~0.9–1.0 pts/trade below** the 1-min ridge at every
rung. OR3-TRAILT3's smaller net loss vs OR1-TRAILT3 (−₹90,033.50 vs −₹104,795.20) is
purely a frequency effect: 254 fewer trades = ₹55,880 less cost paid against ₹41,118
less gross captured. Per trade, 3-min is strictly worse; per rupee of edge, nothing
improves. Days-green is the one metric that ticks up (30.0% vs 25.4%) — still ~7 days
in 10 ending red, against the charter's end-the-day-in-profit objective.

## Honest read

**It is the same wall.** Moving the trailing design to 3-minute decision bars changes
the trade count, not the arithmetic: the later, coarser signal enters after more of
the micro-move has already happened, so each trade captures *less* gross (2.37 vs
3.27 pts/trade at the best rung, 32% vs 45% of the 7.33-pt breakeven), and the ridge
was already decelerating on 1-min — on 3-min it starts lower and flattens against a
lower ceiling (~2.4 pts and rising slowly). No variant passes any leg of the banking
gate that matters: both halves deeply negative, pace ≈ −₹9,000/month for the best
cell, every month red. The terminated engine's conclusion stands with the last cell
filled in: at ₹220/trade on 1 lot, sub-5-minute Bank Nifty premium scalping tops out
at roughly a third to a half of its cost breakeven on every timeframe and exit
geometry tested — revival still needs a structurally different cost basis or a
mechanism with more than double the best gross measured, not a timeframe change.

Files: trades `bank_scalp_or3_trail_trades.csv` (2,420 rows, all four variants),
summary `bank_scalp_or3_trail_summary.json`, scorer `bank_scalp_or3_trail_run.py`.
