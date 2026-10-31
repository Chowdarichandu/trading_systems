# Stocks EQUITY — Line O2 report: the 11:00 fade as a frozen EXT-ONLY system

Equity cash intraday only, LONG/SHORT. **Paper only — real money
₹0, no orders.** Every figure: **provisional per 100 shares,
₹40/trade** cost deducted. All cells were frozen in
`stocks_O2_frozen.md` BEFORE scoring. Universe: the 25 large caps
(`data/progressive_ext/`); the home 25 appears once as a control
read and is not part of the system.

## SELECTION DISCLOSURE

**This system was selected from a 1,344-cell October-first scan
(Line O1) — it is that scan's single best ext-universe cell.
Every in-sample number below is an UPPER BOUND, not an
expectation. December fresh data is the real judge; the gate
below is a necessary screen, not proof.**

The system: measure each stock's morning move at 11:00 (close of
the last bar before 11:00 vs the 09:30 bar's open). If |move| ≥
1%, enter at the 11:00 bar's open AGAINST the move (fade — up
movers are shorted, down movers are bought), one trade per
stock-day, exits target +1.25% / stop −0.65%, 15:10 square-off.

One bookkeeping note: the commissioning brief said "6 cells +
base" but enumerated 7 neighbourhood variations (2 threshold +
2 measurement + 2 exits + 1 context). All 7 enumerated variations
were frozen and run; the enumerated list governed.

## Anchor validation — REPRODUCED TO THE PAISA

| Slice (base cell) | O2 result | O1 published | |
|---|---|---|---|
| Ext October | **+₹98,153.17** (104 trades) | +₹98,153.17 | ✓ exact |
| Ext Jan–Sep | **+₹206,273.84** (596 trades) | +₹206,273.84 | ✓ exact |
| Home Jan–Sep (control) | **+₹3,901.89** | +₹3,901.89 | ✓ exact |
| Home October (control) | **+₹341.29** | +₹341.29 | ✓ exact |

The Nifty regime map extended cleanly to Oct 30 (Oct 28–30 all
below-50DMA days, as in O1).

## Timing audit — CLEAN, 0 violations everywhere

Two independent checks, asserted in the same run as scoring:
(1) O1's built-in audit counters — 0 violations across all cells
and placebos; (2) an independent re-derivation from the dumped
trades — for every trade, the qualifier pre-move was recomputed
from bars strictly before the measurement time, and the
threshold, the fade direction, and the exact entry bar (first bar
≥ measurement time) were verified: base 700/700 clean, placebo
700/700 clean, every neighbourhood cell and its placebo clean.
The rule is real-time executable exactly as scored: the 11:00
measurement is complete at 11:00 and the entry is the 11:00 bar's
open.

## Base cell — O2-BASE (ext 25, Jan–Oct 2026)

**700 trades, net +₹304,427.01, expectancy +₹434.90/trade.**
Halves: Jan–May **+₹170,988.68** / Jun–Oct **+₹133,438.33** —
both positive. October **+₹98,153.17**. Breadth **17/25**.
Frequency: **70 trades/month** (~3.3 per trading day).

| Month | Trades | Net ₹ |
|---|---|---|
| Jan | 61 | +57,081.02 |
| Feb | 57 | +8,218.74 |
| Mar | 107 | +16,783.02 |
| Apr | 98 | +33,824.88 |
| May | 77 | +55,081.02 |
| Jun | 64 | +35,388.50 |
| Jul | 68 | **−22,467.91** |
| Aug | 32 | +24,514.73 |
| Sep | 32 | −2,150.16 |
| Oct | 104 | +98,153.17 |

8 of 10 months positive. Worst month **July −₹22,467.91**.
**Max drawdown −₹72,977.52** (daily-aggregated) — about 24% of
the total net; this book's path is not smooth.

## Home-25 control read (base cell)

Jan–Oct net **+₹4,243.18**, breadth 8/25 — flat, as O1 found
(Jan–Sep +₹3,901.89, October +₹341.29; losing months Feb, Apr,
Jun, Jul, Aug). The effect does not exist on the home watchlist.
This remains an ext-universe phenomenon, exactly as disclosed.

## Neighbourhood cells (ext 25, Jan–Oct; one change from base each)

| Cell | Change | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Ex-top-3 ₹ | Gate |
|---|---|---|---|---|---|---|---|---|---|
| **BASE** | — | 700 | **+304,427.01** | +170,988.68 | +133,438.33 | +98,153.17 | 17/25 | +95,157.68 | **PASS** |
| N1 | thr 1.25% | 392 | +173,419.13 | +105,593.00 | +67,826.13 | +61,791.38 | 15/25 | +37,947.70 | **PASS** |
| N2 | thr 1.5% | 220 | +128,501.20 | +124,840.62 | +3,660.58 | +17,791.63 | 14/25 | +7,504.50 | FAIL — breadth |
| N3 | measure 10:45 | 580 | +216,920.49 | +142,921.55 | +73,998.94 | +59,770.75 | 14/25 | +5,463.10 | FAIL — breadth |
| N4 | measure 11:15 | 755 | +136,939.07 | +55,121.04 | +81,818.03 | +59,811.39 | 11/25 | −1,721.39 | FAIL — breadth + ex-top-3 |
| N5 | exits T125/S050 | 700 | +238,164.92 | +168,912.90 | +69,252.02 | +96,448.93 | 19/25 | +84,359.94 | **PASS** |
| N6 | exits T10/S065 | 700 | +249,705.23 | +118,650.83 | +131,054.40 | +78,307.84 | 14/25 | +76,755.28 | FAIL — breadth (by one stock) |
| N7 | below-50DMA days only | 524 | +285,290.48 | +149,196.12 | +136,094.36 | +98,153.17 | 17/25 | +83,799.71 | **PASS** |

Reads, stated plainly:
- **11:00 is a genuine local peak**: 10:45 keeps the money but
  loses breadth (14/25, top-3 share 97.5%); 11:15 collapses
  (breadth 11/25, ex-top-3 negative, max DD −₹112,962.05).
- **The wider stop matters**: S065 (base) beats S050 (N5) by
  ~₹66k on identical entries, though N5 has the best breadth
  (19/25) and also passes the full gate.
- **The regime filter (N7) is protective in-sample**: dropping
  above-50DMA days removes most of the July hole (July +₹670.00
  vs base −₹22,467.91) and cuts max DD to −₹57,994.02, for a
  ~₹19k total give-back on 176 fewer trades. Recorded as an
  observation — the candidate below is the base cell, not N7;
  swapping to N7 now because it looks smoother would be another
  layer of selection on the same data.
- Higher thresholds (N1/N2) shrink the book fast; N1 still
  passes, N2's Jun–Oct nearly vanishes (+₹3,660.58).

## Placebo (lagged qualifier, base cell)

Yesterday's 11:00 move, faded today at 11:05-equivalent entry,
same exits, ext Jan–Oct: 700 trades, **+₹38,437.66** — positive
(a one-day-old morning move still carries some fade value on
these names) but the base cell beats it **~7.9×** (+₹304,427.01).
The same-day timing is the effect; the placebo leg is beaten
clearly. (Placebos for the gate-passing neighbourhood cells:
N1 +₹41,699.34 vs its +₹173,419.13; N5 +₹32,573.82 vs
+₹238,164.92; N7 +₹23,599.39 vs +₹285,290.48 — all beaten.)

## Stress battery (base cell)

- **Ex-top-3:** remove MARUTI (+₹91,453.90), EICHERMOT
  (+₹77,319.78), ULTRACEMCO (+₹40,495.65) → net **+₹95,157.68**,
  halves +₹75,169.74 / +₹19,987.94 — still positive in both
  halves. The book survives losing its three best stocks.
- **Winsorised at +₹2,000/stock:** net **+₹11,638.40** —
  positive but thin. Capping every stock's contribution at
  ₹2,000 leaves only ~4% of the headline net: this book's profit
  is carried by a handful of large payers, and the winsorised
  figure is the honest measure of how much.
- **Concentration:** top-3 share **68.7%** of net; top-5
  (MARUTI, EICHERMOT, ULTRACEMCO, M&M +₹25,179.23, GRASIM
  +₹26,047.57) ≈ 85%. It is an auto/cement-heavy large-cap
  phenomenon. 8 of 25 stocks are net-negative, led by AXISBANK
  −₹7,185.50 and DRREDDY −₹4,879.60.
- **Worst month:** July −₹22,467.91. **Max DD −₹72,977.52.**

## Gate verdict — O2-BASE PASSES ALL SIX PRE-DECLARED LEGS

1. Net > 0: **+₹304,427.01** ✓
2. Both halves > 0: +₹170,988.68 / +₹133,438.33 ✓
3. Ext breadth ≥ 15/25: **17/25** ✓
4. October > 0: +₹98,153.17 ✓
5. Placebo beaten: +₹304,427.01 vs +₹38,437.66 ✓
6. Ex-top-3 > 0: +₹95,157.68 ✓

**O2-BASE is frozen as the O2 CANDIDATE**
(`stocks_O2_candidate_spec.md`) for a December 2026 fresh-window
test — the first honest test this effect has faced on data it
was not selected from. In-sample run-rate: **+₹30,443/month**
(70 trades/month) — an upper bound by construction (see the
selection disclosure), against the user's ₹50,000/month bar:
even taken at face value it does not reach the bar; it is the
closest honestly-screened book the hunt has produced, carried
into December at its true size, not dressed up.

Files: `stocks_O2_frozen.md` (frozen plan) · `stocks_O2.py`
(engine) · `stocks_O2_results.json` (full results) ·
`stocks_O2_BASE_trades.csv`, `stocks_O2_BASE_PLACEBO_trades.csv`,
`stocks_O2_N1..N7_trades.csv` (+ placebos for N1/N5/N7) ·
`stocks_O2_candidate_spec.md`.
