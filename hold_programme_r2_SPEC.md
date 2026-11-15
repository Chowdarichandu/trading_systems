# HOLD PROGRAMME — ROUND 2 SPEC (FROZEN 2026-11-15, before scoring)

Diagnosis from Round 1 (`hold_programme_2026-11-15.md`): of the 20 cells,
only ONE trigger/hold pairing is positive in BOTH years at the same setting —
E1 (RSI(14) cross up through 35) at H15: 2025 +₹42,163 (83t, WR 63.9%) /
2026 +₹83,963 (103t, WR 41.7%). The combined-best cell E0-H5 hides a losing
2026 and is NOT a candidate. Round 2 tunes the E1 neighbourhood in small
steps. Research only; arms nothing, touches no book/ledger/job.

## Basis (unchanged from Round 1)
- Equity cash, LONG only, frozen 25-name Stock Book watchlist
  (`indicator_parameter_tuning_stocks_build.NAMES`), daily candles from
  `data/sarvaritu_fwd/<SYM>/spot_daily.csv` (to 2026-11-13).
- **Per 100 shares PROVISIONAL** on every figure. ₹40 per completed position.
  Paper only, real money ₹0. Judged PER YEAR, never pooled.
- Engine, position rules, year windows, WMARK marking, and stats are Round
  1's verbatim (`hold_programme_build.py`): signal at day t close → buy at
  day t+1 open → sell at the close of day entry+H; one position per stock;
  trades scored in year Y by entry date in [Y-01-01, Y-10-31], exits past
  the window end marked at the window-end close.

## The grid (9 cells)
- Trigger E1-L: RSI(14) (Wilder, Round 1 construction) crosses up through
  level L: RSI[t−1] < L and RSI[t] ≥ L, both defined.
  L ∈ {30, 35, 40}. L = 35 is Round 1's E1 exactly.
- Hold H ∈ {10, 15, 20}. H15 is Round 1's hold.
- CONTROL = L35-H15. It must reproduce Round 1's E1-H15 exactly
  (2025: 83 trades, +₹42,163 · 2026: 103 trades, +₹83,963) before any other
  cell is read.

## Reporting
- Per cell per year: trades · net (₹) · WR % · average % move per trade
  (gross) · worst trade (₹) · max drawdown (₹) — Round 1 definitions.
- Best cell by the frozen rule: among cells positive in BOTH years, the
  highest two-year combined net. (If no cell is positive in both years,
  there is no best cell and the extra reporting is done on the control.)
- For the best cell: random-entry placebo (Round 1 construction: per-stock
  scored counts across both windows, random entry days, same hold, 1,000
  draws, seed 20261115, statistic = two-year combined net, percentile =
  share of draws ≤ real) · ex-top-3 net per year (year net minus its three
  largest trade nets) · month table (per year, by entry month: trades and
  net) · its November trades (entries 2026-11-02..2026-11-13 at true exits;
  positions whose hold runs past the data are FORCED at the 2026-11-13
  close and labelled OPEN/MARKED).
- State plainly whether any cell beats the control in BOTH years.

## Timing
Signals use only closes up to day t; entries fill at t+1 open; exits are a
fixed day-count rule filled at that day's close. No future data.
