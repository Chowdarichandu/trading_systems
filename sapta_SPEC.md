# SAPTA — Frozen Spec (pre-registered BEFORE scoring)

**Frozen at:** 2026-11-17 ~17:30 IST, before any SAPTA number was computed.
**Status:** Research only. Nothing is armed, no paper run is started, no live book changes.
**Money basis (labelled everywhere):** equity cash, PROVISIONAL per 100 shares, ₹40 per completed trade. Paper only, real money ₹0. Equity cash ONLY — no stock options in any form.

## The concept (owner's words, 2026-11-17 17:25 IST)

"For Nifty index two top performing stocks and you need to build a strategy which works for them. Not AKM [EKAM], not TRIO. It should be like Sapta. Seven indexes, seven twos fourteen stocks. Seven three twenty one stocks."

SAPTA (Sanskrit: seven) = 7 sectoral indices × top performers per index. Two sizes are tested: **SAPTA-14** (top 2 per index) and **SAPTA-21** (top 3 per index). SAPTA is a separate new entity — not EKAM, not TRIO, not the Stock Book.

## Indices (7)

Primary: Nifty Bank, Nifty IT, Nifty Pharma, Nifty Auto, Nifty Metal, Nifty FMCG, Nifty Realty.
If an index cannot field the required names under the constraints below, substitute in this order: Nifty Energy, Nifty PSU Bank, Nifty Financial Services — and record the substitution and reason in the report.

## Constituents

Current published NSE constituent lists (niftyindices.com IndexConstituent CSVs, fetched 2026-11-17; any list that cannot be fetched is reconstructed from widely published lists and the source stated in the report).

**KNOWN LIMITATION (stated prominently in the report):** current (Nov 2026) constituent lists applied to a 2025–2026 backtest carry constituent look-ahead / survivorship bias — names that were removed from an index during 2025–26 (often for poor performance) are absent, and names added later are present for the whole window. The random-selection placebo (same current lists, same constraints) partially controls for this: it shares the same biased lists, so SAPTA must beat random picks *from the same lists*, not just make money.

## Selection (point-in-time, causal)

- Re-rank on the first trading day of each quarter (Jan / Apr / Jul / Oct). Ranking day R = first trading day of the quarter in the data (the union trading calendar from the universe dump).
- Ranking metric: trailing 126-trading-day return = close[R−1] / close[R−1−126] − 1, computed ONLY from closes strictly before R. Selections are effective for entry signals on days ≥ R.
- Constraints, all measured with data through R−1 only:
  - (a) **Owner rule:** price ≤ ₹2,000 (close at R−1).
  - (b) Liquidity: median daily traded value over the trailing 60 trading days (through R−1) ≥ ₹5 crore. Traded value = close × volume (the daily parquet dump carries no turnover field; close×volume is the standard approximation).
  - (c) History: the full 126-day trailing window exists (closes at R−127 … R−1 present).
- Take top 2 (SAPTA-14) / top 3 (SAPTA-21) per index by the ranking metric. Every quarterly selection list is recorded in the report. Names that would have been picked but are excluded by the ₹2,000 cap are listed as cap-excluded, with the next eligible name taking the slot.
- Eligibility for NEW entries requires the name to be in the current quarter's selection. A held name dropped at a re-rank exits at R's open (the decision uses only data through R−1, so it is known before R opens). A held name retained at a re-rank stays open under the normal exit rule.

## Strategy (momentum breakout — deliberately NOT EKAM's mean-reversion)

Daily bars, LONG only, per name:
- **Entry signal:** today's close > highest close of the prior 20 trading days (Donchian 20, closes) → buy at the NEXT trading day's open.
- **Exit signal:** today's close < lowest close of the prior 10 trading days (Donchian 10, closes) → sell at the NEXT trading day's open.
- One open position per name; no adding. No stop-loss beyond the 10-day-low exit rule — that rule IS the exit.
- **Max 10 concurrent positions** (both sizes). Order of operations at each open: exits fill first (re-rank drops + exit signals), then pending entries fill into free slots. If more entries are pending than slots, fill in trailing-return rank order — the ranking metric from the most recent quarterly ranking, descending; a skipped entry is dropped, not queued (the breakout must be re-signalled).
- Position size: 100 shares per position (the provisional basis).

## Window and accounting

- Entries from 2025-01-01 through 2026-11-13 (data end). Report 2025, 2026 (Jan 1 – Nov 13), and the November 2026 slice (trades entered 2026-11-01 – 2026-11-13, marked if still open) separately.
- Each position is charged ₹40 once, as a completed round trip. Positions still open at the 2026-11-13 close are marked at that close (with the ₹40 charged) and included in headline nets; closed-only nets are also reported for transparency.
- A trade's net is attributed to its exit month (open positions to Nov 2026) for the month table, and to its entry half (Jan–Jun / Jul–Dec of its entry year) for the halves split.
- Max drawdown: daily marked-to-market equity curve (cumulative closed net + open positions marked at each day's close, per-100-shares basis), peak-to-trough in ₹.
- Breadth: per-name net contribution is reported (how many traded names made money).

## Controls gate (same run, before any verdict)

1. **Timing/leak audit (programmatic, every trade):** entry fill date is the first trading day strictly after the signal close; ranking inputs use closes strictly before R; exit fills likewise; re-rank exits fill at R's open with inputs through R−1. Violation count must be 0.
2. **Placebos — 200 seeded draws each (seed base 20261117):**
   - (a) *Random entries:* same selections; each real trade's entry is shifted by a random offset of ±10…±120 trading days within the name's selected periods, exit rule re-applied from the shifted entry; one-position-per-name and the 10-cap enforced chronologically (conflicting shifted trades skipped, shortfall reported).
   - (b) *Random selection:* per quarter per index, randomly draw the same number of names from the same constraint-eligible constituent pool; identical strategy.
   SAPTA's net must beat the **90th percentile of BOTH placebos, in BOTH years** (placebo nets computed per entry-year).
3. **Halves split** per year; **full month table**; **ex-top-3 stress** (net after removing the 3 best trades, per size per year).
4. **Independent re-sum** of headline nets from the trades CSV by a separate pass; must match to the paisa.

## PASS BAR (pre-registered, per size — do not move after seeing results)

A size PASSES only if ALL hold:
- Net positive in BOTH 2025 and 2026.
- Beats both placebos' 90th percentile in both years.
- Ex-top-3 net positive in both years.
- No single month worse than −₹15,000.
- Timing audit clean (0 violations).

A failed size is never retested identically. Parameters (20/10 Donchian, 126-day ranking) are NOT tuned in this run — one frozen spec, one verdict per size.

## Comparison (labelled, never pooled)

Stock Book (frozen 25): 2025 +₹1,19,813 / 2026 +₹2,47,179. EKAM Daily: 2025 +₹42,955 / 2026 +₹1,41,328. SAPTA is judged on its own gate, not against these totals; overlap of SAPTA selections with the frozen 25 is reported as a count.
