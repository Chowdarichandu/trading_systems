# BTST-2 — SPEC (FROZEN 2026-11-15, before scoring)

Owner's order 2026-11-15: work on BTST-style holds. Research only; arms
nothing, touches no book/ledger/job.

## Honesty frame (read first — this is NOT the old BTST)

The original BTST programme (2026-11-13) FAILED both arms and is CLOSED:
Bank options −₹6,436 / 190 trades; stocks −₹289,328 / 613 trades with
10/10 months red. Its stocks arm bought STRENGTH into the close (signal at
day close: day gain ≥ +1.00% AND close-strength (C−L)/(H−L) ≥ 75, top 5/day,
filled at the close). BTST-2 is a DIFFERENT test, not a retest of that
programme: it takes the HOLD programme's entries — a no-signal weekly base
and three dip/base triggers — and scores the two shortest holds the HOLD
grid never ran, H1 (sell tomorrow) and H2 (sell the day after). Different
entries, different fill (next open, not the close), different question.

## Basis — identical to the HOLD programme, machinery imported, not rebuilt

- Build: `hold_programme_build.py` imported verbatim (`prep`, `sim`,
  `score_year`, `stats`, `placebo`, `NAMES`, `YEARS`). No indicator,
  signal, or state machine is re-implemented.
- Equity cash, LONG only, frozen 25-name Stock Book watchlist, daily
  candles from `data/sarvaritu_fwd/<SYM>/spot_daily.csv`
  (2024-10-01 → 2026-11-13; Oct–Dec 2024 is indicator warm-up).
- **Per 100 shares PROVISIONAL** on every figure. ₹40 per completed
  position (entry + exit together). Paper only, real money ₹0.
- Net per trade = round((exit − entry) × 100 − 40, 2). Judged PER YEAR,
  never pooled into one verdict.

## Entry triggers (verbatim from HOLD; signal at day t close → buy t+1 open)

- **E0 BASE** (no signal): buy at the OPEN of the stock's first bar of
  each ISO week.
- **E1 DIP**: RSI(14)[t−1] < 35 and RSI(14)[t] ≥ 35 (Wilder).
- **E2 BAND**: close[t−1] < lower Bollinger(20,2)[t−1] and
  close[t] ≥ lower[t] (EKAM-daily's BB entry).
- **E3 TREND**: close[t−1] ≤ MA20[t−1] and close[t] > MA20[t].

## Cells and position rules

- Grid: 4 triggers × 2 holds = 8 cells, H ∈ {1, 2}. Entry day = day 0;
  exit at the CLOSE of day entry+H. If entry+H is beyond the last bar:
  exit at the last close, kind = FORCED.
- One open position per stock at a time; signals while holding are
  ignored. After an exit at the close of day x, scanning resumes at day
  x's close (for E0, the next entry is the first week-bar strictly after
  day x). Exactly the HOLD state machine (`sim`), only H changes.

## Year windows (scoring) — identical to HOLD

- A trade is scored in year Y if its ENTRY date ∈ [Y-01-01, Y-10-31],
  Y ∈ {2025, 2026}. If the trade's exit index > window-end index w(Y)
  (last bar ≤ Y-10-31: 2025-10-31 / 2026-10-30), the exit is re-marked at
  close[w(Y)], kind = WMARK, net recomputed. Trades entering Nov–Dec are
  not scored in either window.

## Stats per cell per year

Trades · net (₹) · WR (% of trades with net > 0) · average % move per
trade (gross, (exit/entry − 1) × 100, mean) · worst trade (₹) · max
drawdown of the cell's equity line (as in HOLD) · WMARK/FORCED counts.

## Placebo

For the best cell of each trigger (by two-year combined net): per stock,
the count is that cell's scored trade count for the stock across both
windows; each placebo trade draws an entry index uniformly from
[0, n−1−H] (exit close always exists in the full series), entry at that
day's open, exit at the close H days later, same net formula, overlaps
ignored. 1,000 draws, seed 20261115 (the HOLD seed/protocol, via the
imported `placebo`). Statistic = two-year combined net. Percentile =
share of draws ≤ the real combined net, × 100.

## Verification before scoring (abort if it fails)

The build first re-runs one published HOLD R1 cell (E0-H3) through the
imported machinery and checks the stats reproduce the HOLD report exactly
(2025: 1,050 trades · +₹79,560 · WR 50.5 · avg +0.31 · worst −₹18,860;
2026: 1,050 trades · −₹154,371 · WR 45.1 · avg −0.17 · worst −₹45,165).
H1/H2 are scored only if the check passes.

## Reference rows (quoted in the report's final table, NOT rescored)

- The same four triggers at H3 from the HOLD R1 build
  (`hold_programme_2026-11-15.md`), so H1 / H2 / H3 sit side by side.
- The closed BTST programme's stocks arm: −₹289,328 / 613 trades
  (strength entries at the close), for one comparison line on how
  BTST-2's best cell differs and why the entries differ.

## Timing

Signals use only closes up to day t; entries fill at t+1 open; exits are
a fixed day-count rule filled at that day's close. No future data enters
any decision.
