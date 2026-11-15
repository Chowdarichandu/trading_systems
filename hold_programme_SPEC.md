# HOLD PROGRAMME — SPEC (FROZEN 2026-11-15, before scoring)

Owner's order 2026-11-15: work on something like "buy today, sell three days
after, and something with weeks" — fixed-horizon swing holds. Research only;
arms nothing, touches no book/ledger/job.

## Basis
- Equity cash, LONG only, frozen 25-name Stock Book watchlist
  (`indicator_parameter_tuning_stocks_build.NAMES`), daily candles from
  `data/sarvaritu_fwd/<SYM>/spot_daily.csv` (2024-10-01 → 2026-11-13;
  Oct–Dec 2024 is indicator warm-up). All 25 series share one date set
  (526 bars, verified).
- **Per 100 shares PROVISIONAL** on every figure. ₹40 per completed position
  (entry + exit together). Paper only, real money ₹0.
- Net per trade = round((exit − entry) × 100 − 40, 2). Judged PER YEAR,
  never pooled into one verdict.

## Indicators (existing constructions, imported — not re-implemented)
- RSI(14): Wilder (`dial_stocks_build.rsi_wilder`, via the atlas build).
- Bollinger(20,2): window mean ± 2 × population SD on closes (atlas
  `bollinger_bands(c, 20)`); lower = mid − 2·SD. MA20 = the same mid.

## Entry triggers (signal at day t close → buy at day t+1 open; t+1 must exist)
- **E0 BASE** (no signal): buy at the OPEN of the stock's first bar of each
  ISO week (equivalently, a standing signal at the prior week's last close).
- **E1 DIP**: RSI[t−1] < 35 and RSI[t] ≥ 35, both defined.
- **E2 BAND**: close[t−1] < lower[t−1] and close[t] ≥ lower[t], lower defined
  at t (the EKAM-daily BB component's entry, verbatim).
- **E3 TREND**: close[t−1] ≤ MA20[t−1] and close[t] > MA20[t], both defined.

## Position rules
- One open position per stock at a time; signals while holding are ignored.
- Entry day = day 0. Exit at the CLOSE of day entry+H, H ∈ {3, 5, 10, 15, 20}.
- After an exit at the close of day x, scanning resumes at day x's close
  (a signal on day x itself counts; for E0 the next entry is the first
  week-bar strictly after day x).
- If entry+H is beyond the last bar: exit at the last close, kind = FORCED.
- Grid: 4 triggers × 5 holds = 20 cells, one state machine per cell over the
  full series.

## Year windows (scoring)
- A trade is scored in year Y if its ENTRY date ∈ [Y-01-01, Y-10-31],
  Y ∈ {2025, 2026}. Window end index w(Y) = last bar ≤ Y-10-31
  (2025-10-31; 2026-10-30).
- If the trade's exit index > w(Y): exit price is replaced by close[w(Y)],
  kind = WMARK, hold = w(Y) − entry index, net recomputed. The position
  still occupies the stock in the sim until its true exit.
- Trades entering Nov–Dec are not scored in either window.

## Stats per cell per year
Trades · net (₹) · WR (% of trades with net > 0) · average % move per trade
(gross, (exit/entry − 1) × 100, mean) · worst trade (₹) · max drawdown of the
cell's equity line (cumulative net over the year's trades ordered by exit
date, then entry date, then symbol; line starts at 0) · WMARK/FORCED counts.

## Placebo
For the best cell of each trigger (by two-year combined net): per stock, the
count is that cell's scored trade count for the stock across both windows;
each placebo trade draws an entry index uniformly from [0, n−1−H] (exit close
always exists in the full series), entry at that day's open, exit at the
close H days later, same net formula, overlaps ignored. 1,000 draws,
seed 20261115. Statistic = two-year combined net. Percentile = share of
draws ≤ the real combined net, × 100.

## Best overall cell + November note
Best overall = max two-year combined net over all 20 cells. Its full scored
trade list goes to a CSV. November note: its trades with entry date in
2026-11-02..2026-11-13 (true exits; FORCED at the 2026-11-13 close if the
hold runs past the data), listed with dates and nets.

## Reference (not rescored)
EKAM-daily 2c published lines: 2025 +₹42,954.60 · 2026 +₹1,41,328.40
(per 100 shares provisional), shown in the report's last table only.

## Timing
Signals use only closes up to day t; entries fill at t+1 open; exits are a
fixed day-count rule filled at that day's close. No future data enters any
decision.
