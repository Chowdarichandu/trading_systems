# DIAL — NIFTY · standalone indicator system · gate run 2026-11-14

Spec: `dial_nifty_SPEC.md` (core frozen verbatim before scoring; one data-fill
correction inside, disclosed below). Numbers: `dial_nifty_results.json` ·
trades: `dial_nifty_trades.csv` · build: `dial_nifty_build.py`.
Standalone — signals from spot candles only; not a filter on any book.
Buying only, 1 lot (65), paper only, real money ₹0. Nifty segment only.

## Coverage
- Window Jan–Oct 2026: **203 trading days** in the spot store.
- Signals generated: **334** (T 176 implied by scored+NC split below; R the rest) —
  scored **205**, NC **129**, every NC = `nc_no_file` (the exact nearest-strike weekly
  contract-day was never stored; no substitution, per spec). Scored split: T 112, R 93.
  The premium store was built for other books' leg days and band fetches, so this NC
  share is a property of the store, not of the system; the gate judges the scored book
  and the NC count stands next to every total.

## Fill correction (disclosed, core untouched)
The first fill compared the SPOT close with the FUTURES-price session VWAP. Futures
carry a basis over spot, so the test was not like-for-like (measured: spot close above
futures VWAP on only 22.5% of bars vs 49.0% for a futures close) and mechanically
starved DIAL-T of CE signals (scored 79 PE vs 17 CE). The fill was corrected to the
basis-consistent comparison (futures close vs futures VWAP ≡ spot vs basis-adjusted
VWAP; the Supertrend flip itself remains on spot) and the gate re-run in full.
First-fill headline, for the record (`dial_nifty_results_fill1_disclosed.json`):
combined 189 trades, −₹89,913.35, WR 34.4%, placebo 7.2nd pct — it failed every leg
too. The correction changed T's composition (now 60 CE / 52 PE), not the verdict.

## Results (corrected fill, final)

| Line | Trades | Total | WR | ₹/trade-day | Pace/mo | Red months |
|---|---|---|---|---|---|---|
| DIAL-T (Supertrend flip + VWAP side) | 112 | **−₹51,821.70** | 36.6% | −462.69 | −5,182 | 7 |
| DIAL-R (RSI/%B extreme reversion) | 93 | **−₹37,665.50** | 36.6% | −405.01 | −3,767 | 7 |
| **Combined DIAL-Nifty** | **205** | **−₹89,487.20** | **36.6%** | **−604.64** | **−8,949** | **8** |

Combined month table (₹): Jan +13,445.40 · Feb −1,094.50 · Mar −15,650.00 ·
Apr +1,338.25 · May −4,265.75 · Jun −24,822.00 · Jul −25,688.50 · Aug −9,236.60 ·
Sep −20,356.75 · Oct −3,156.75. Only Jan and Apr positive.
Halves: H1 (Jan–May) −₹6,226.60 · H2 (Jun–Oct) −₹83,260.60 — both negative.
Ex-top-3: −₹106,377.20. Exit mix: 101 square-offs at 15:20, 68 stops, 36 targets —
the +90 target was reached on only 17.6% of trades, against a −50 stop; with ₹220
cost, that geometry needs roughly double the observed target rate to break even.
Direction texture (descriptive): T loses on both sides (CE −₹28,272.85, PE
−₹23,548.85). Inside R, the LONG side (buy CE at RSI ≤ 30) is −₹70,179.00 while the
SHORT side (buy PE at RSI ≥ 70) is +₹32,513.50 — noted as an observation only;
carving it out post-hoc would be a new hypothesis needing its own frozen run.

## Gate (combined book, frozen bar) — FAIL on all eight legs
1. Random-entry placebo ≥ 95th pct → **11th pct** (1,000 iterations; placebo mean
   −₹36,040.34, p95 +₹37,207.45). The real book is worse than ~89% of random books —
   and worse than the random mean itself.
2. Beat +30-min shift placebo → **NO**: shifted entries total −₹29,402.85 (204
   trades, 1 dropped) vs the real −₹89,487.20. Entering 30 minutes later in the same
   contracts loses far less — the indicator moments are actively harmful, not neutral.
3. Halves positive → **NO** (both negative).
4. Ex-top-3 positive → **NO** (−₹106,377.20).
5. ₹/trade-day ≥ 900 → **NO** (−604.64).
6. WR ≥ 60% → **NO** (36.6%).
7. Monthly pace ≥ ₹7,500 → **NO** (−8,949).
8. Red months ≤ 2 → **NO** (8).
Timing audit: PASSED — every scored trade's entry bar is exactly signal bar + 5 min
with entry premium equal to the stored bar open; an independent code path reproduced
RSI(14) and EMA50 at both components' first signal bars to the printed digit.
DIAL-T and DIAL-R each also fail the bar's ₹/trade-day, WR, pace and red-month legs
on their own lines (descriptive; the placebo legs are combined-book tests).

## November counterfactual (Nov 2–13, descriptive)
14 signals, 12 NC (no stored contract), 2 scored trades, both losses:
T — Nov 2, PE 23250 (exp 11-03), in 12:55 @84.35, square-off 49.90 → −₹2,459.25.
R — Nov 4, PE 23850 (exp 11-09), in 09:20 @193.05, stop 143.05 → −₹3,470.00.
November net: **−₹5,929.25**, WR 0%.

## Verdict
**FAIL — decisively, on every leg of the frozen bar.** There is no standalone
indicator channel in Nifty on this core: the Supertrend-flip-with-VWAP trend leg and
the RSI/Bollinger reversion leg both bleed through the −50/+90 geometry, in both
directions, in both halves of the year, and the entries are worse than entering the
same contracts 30 minutes later or at random. DIAL-Nifty is not adopted, not armed,
and nothing that runs was changed. The one positive quadrant (R's put-buying side at
overbought extremes, +₹32,513.50) is recorded above as a hypothesis seed for a future
frozen run, not as a finding.
