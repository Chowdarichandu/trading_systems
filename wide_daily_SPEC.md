# WIDE-DAILY — SPEC (FROZEN 2026-11-17, before any scoring)

Programme: EKAM-DAILY (EKAM-2c) on the full-NSE universe, owner's order
2026-11-17 06:14 IST ("run EKAM and TRIO stocks related with large amount of
universe" — this arm is the EKAM-DAILY part). Research only — no book,
ledger or job is touched. Basis: equity cash · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0. Judged PER YEAR (2025, 2026), never
pooled.

## 0. Machinery — verbatim, only the data source changes

The engine is the frozen EKAM-2c machinery, imported / copied, never
re-implemented:

- Signal construction: `ekam_build.prep` exactly (Bollinger(20,2) population
  bands on closes via `indicator_parameter_tuning_stocks_build.bollinger_bands`;
  RSI(14) Wilder via `dial_stocks_build.rsi_wilder`; BB entry = close back
  inside the lower band after a close below it; RSI entry = RSI cross up
  through 30; BB exit signal = close ≥ middle band; RSI exit signal =
  RSI ≥ 70).
- Simulation: `ekam2c_build.sim2c` imported and called as-is (BB-REV-D +
  RSI-REV(TIME60) merged, one open position per name, entry at next session's
  open after the signal close, RSI-upgrade exit conversion of pure-BB
  positions, NO stop).
- Year attribution and stats: `ekam_build.stats` (entry date in
  Jan 1 – Oct 31 of the year), extended only where §3 asks for fields it
  does not carry (ex-top-10, name shares) using its own definitions.

DATA SOURCE (the one change): `~/workspace/trading/universe_daily/<SYM>.parquet`
(daily OHLCV, 2019 → 2026-11-13) instead of the frozen
`data/sarvaritu_fwd/<SYM>/spot_daily.csv` stores. Full parquet history is
used for indicator warm-up, exactly as the published run used its full store
history. Dates are the parquet `date` values formatted YYYY-MM-DD, ascending.

KNOWN DATA FACT (recorded before scoring, from inspection): the frozen
stores' daily close is the close of the last 5-minute bar (15:25) of the
intraday store, while the parquet close is the exchange daily close; the two
differ on ~73% of days for the frozen 25 (open/high/low agree almost
everywhere). This is precisely what the §1 control exists to judge.

## 1. CONTROL (mandatory, before any wide scoring)

Run the §0 machinery on the frozen 25 names (`ATLAS.NAMES`) fed from the
parquet files. PASS = `ekam_build.stats` full stats-dict equality with
`ekam2c_results.json` (`EKAM2c`) for BOTH years. Headline anchors:
2025 — 74 trades · +₹42,954.60 · 2026 — 102 trades · +₹1,41,328.40.
**Any mismatch = STOP: no wide scoring is produced; the report carries the
miss, its size, and the diagnosis.**

## 2. WIDE RUN (only if the control passes)

Universe: every symbol with a parquet file in `universe_daily/`
(2,646 listed in `universe.csv`; the file count on disk governs). A symbol
whose parquet lacks usable OHLC rows is excluded and counted, named in the
results JSON — never estimated.

### 2a. Raw run
`sim2c` on every usable symbol, all history. Per year (Jan–Oct entry
window): trades · net · WR · ex-top-3 · ex-top-10 · best/worst entry month ·
max drawdown (EKAM.stats ordering) · distinct names traded · top-5 names'
share of the year's net.

### 2b. Liquidity-screened run
Identical simulation, with ONE entry gate (exits, upgrades and position
management are untouched):

> A signal on day t may open a position only if the name is LIQUID at t:
> the median of daily traded value (close × volume) over the 60 sessions
> ending at t (t inclusive) is ≥ ₹1,00,00,000 (₹1 crore), computed on the
> parquet series. Fewer than 60 sessions of history ending at t, or any
> null volume inside the window, ⇒ not liquid at t.

Rationale (frozen): ₹1 crore median daily value is a conservative
tradability floor — below it, a name's daily bars are dominated by
micro-cap noise and a real 100-share order book is questionable; the screen
keeps the wide result from being carried by names nobody could trade. A
symbol whose parquet has NO volume column / all-null volume can never be
liquid: it stays in the raw run, is excluded from the screened run, and is
counted and named. A held position is never force-closed by the screen.

Per year, same fields as §2a, PLUS the placebo (§2c).

### 2c. Placebo (screened run only)
The EKAM random-entry design (`ekam_build.placebo`, seed 20261114, 200
draws), adapted only in its sampling pool: per year, N = the screened run's
trade count that year; each draw sums N random entries, each drawn as —
symbol uniform over names having ≥1 liquid day in the year's Jan–Oct
window with a next session available; day uniform over that name's such
liquid days; entry at the next session's open; exit by
`ekam_build.placebo_exit_net` verbatim (TIME60 → middle-band stack, no
stop). Report percentile of the real total among the draw totals, draw mean
and median. "Placebo beaten" = percentile ≥ 95.0.

## 3. November slice (descriptive, both runs)

Entries with entry date 2026-11-02 – 2026-11-13: count, closed net, and
positions still open at the 2026-11-13 close (sim2c forced-at-end trades)
with their marked net shown separately. November is never inside the year
totals and never selects anything.

## 4. VERDICT (frozen)

The wide run is a **SUCCESS** only if the SCREENED run is positive in BOTH
years AND the placebo is beaten (§2c) in BOTH years. Concentration is a
headline fact, not a footnote: if the year's top-3 trades or top-5 names
carry the year's net (ex-top-3 ≤ 0 or top-5 share ≥ 100%), the headline
says so in words. Any other outcome is reported as measured — positive,
negative, or concentrated — without relabelling.

## 5. Standing

WIDE-DAILY arms nothing and replaces nothing. EKAM-2c on the frozen 25 and
its live forward paper are untouched whatever this run finds.
