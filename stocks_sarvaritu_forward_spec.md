# SARVARITU — FORWARD PAPER TEST SPEC (FROZEN 2026-10-31)

**User order (2026-10-31 20:36 IST):** test the stocks strategy live, on the
underlying stocks themselves. "SarvaRitu" = the final v2 engine book
(post-Cycle-24 state) — the cross-year-validated, regime-complete book.
This spec freezes the test BEFORE the first live day. Nothing in it may be
changed during Nov–Dec 2026; any change is a new version, tested from
January 2027.

## The book — VERBATIM (post-C24)

Equity cash intraday, LONG/SHORT, on the underlying 25 watchlist stocks
(GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC,
INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM,
VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL,
HINDUNILVR). Per 100 shares (provisional), ₹40/trade, square-off 15:10,
paper only, real ₹0, no orders. RF-1 book-wide: no trades on
weekend/special sessions.

Components (definitions frozen in `stocks_engine_frozen.md`,
`stocks_engine_candidate_spec.md`, `stocks_engine_v2_build.py`,
`stocks_engine_2025_validation.py` §§2–8 — the logger runs that audited
machinery, it does not re-implement it):

1. **F4** — state-gated follow: NIFTY prior close ≤ 50DMA AND the stock's
   move by 10:00 in [0.5%, 1.0%); follow the move; first qualifying signal
   per stock-day only; exits T150/S095; v1 direction exclusions
   (EXCL_DIR, 12 pairs).
2. **INV-LONG** — INV chain pool (PLAIN chains, round ≤ 2, entry < 10:30,
   ADR ≥ 3.0) on below-trend days (prior close ≤ 50DMA), LONG only,
   T125/S050; base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER,
   KALYANKJIL}.
3. **INV-ABOVE** (v2 Cycle 22) — the identical INV pool on above-trend
   days (prior close > 50DMA), LONG only, T125/S050, same base exclusions.
4. **N4-V3** — event reaction day (results + SINGLE_NEWS classes):
   |move by 09:30| ≥ 1.0% vs prior close → follow, entry 09:35 close,
   exits T150/S080; excludes ASTRAL, TVSMOTOR LONG, OIL LONG.
5. **P2F** — results reactions |reaction-day return| ≥ 2.5% → follow at
   R+1 09:15 open, T125/S050; excludes ASTRAL, HINDUNILVR, HINDALCO LONG.
6. **P2F-R2** — same at R+2 (≥ 2.5% band), T125/S050; frozen exclusions
   (ASTRAL, HINDUNILVR ungated set per SAT-13), no TVSMOTOR LONG.
7. **R2-LOWBAND** — results reactions in [2.0%, 2.5%) at R+2, T125/S050;
   excludes ASTRAL, HINDUNILVR, HINDALCO LONG.

**v2 law (banked C1–C24, applied as mechanism-scoped filters):**
- (comp × stock × direction) deletions: F4×GLENMARK×SHORT,
  N4-V3×GLENMARK×SHORT, N4-V3×BDL×SHORT, F4×HDFCBANK×SHORT,
  F4×KALYANKJIL×LONG, N4-V3×HINDALCO×SHORT, N4-V3×HINDZINC×LONG,
  N4-V3×UNITDSPR×LONG, N4-V3×RECLTD×LONG, N4-V3×WIPRO×SHORT,
  P2F-R2×KALYANKJIL×LONG.
- INV-LONG takes no HINDALCO, UNITDSPR or TATASTEEL signals (the same law
  binds INV-ABOVE).
- **C23:** R2-LOWBAND stands aside on UP days. **C24:** INV-LONG stands
  aside on FLAT days. (Labels: REGIME-CLASSIFIER-1, frozen — NIFTY prior
  close vs the 50DMA of closes strictly before the day, plus the line's
  5-day slope: UP = above a non-falling line; DOWN = at/below a
  non-rising line; FLAT = disagreement. Prior-close information only.)

## Test protocol

- **Logger:** `stocks_sarvaritu_logger.py` (modes `--setup-fwd`,
  `--control`, `--run`). Data root `data/sarvaritu_fwd/` (seeded from the
  frozen `data/full_hist`, then append-only Upstox fills — existing dates
  are never overwritten; the frozen history cannot drift).
- **Daily run (Mon–Fri ~16:35 IST, from Mon 2026-11-02):** fetch-merge
  the last ~16 calendar days (5m + daily, all 25 + NIFTY) → rebuild the
  whole epoch book (epoch 2026-10-26) from causal data only → append
  every unlogged row dated ≥ 2026-11-02 to
  `stocks_sarvaritu_paper_log.csv` (columns: date, comp, stock, dir,
  entry_time, exit, net, regime) → append the one-line day summary to
  `stocks_sarvaritu_daily_summary.md`. The rebuild-and-diff design makes
  runs idempotent: a missed day is caught up exactly by the next run.
- **Events** come from `stocks_sarvaritu_calendar_live.csv` (same schema
  as the frozen calendars), seeded from the verified November watchlist.
  The daily run's filings check maintains it: only an actual results
  announcement or a SINGLE_NEWS-class item (management_change,
  large_order, fda_approval, block_deal, sector_policy, pricing,
  corporate_action) is an event — administrative filings (earnings-call
  intimations, investor meets) are NOT. Reaction date rule: after-market
  announcement → next trading day; pre-open → same day; intraday → next
  trading day.
- **Guards:** if NIFTY or ≥ 20 symbols lack the day's bars after fetch,
  the day is treated as no-market-data (holiday/outage): nothing is
  logged and the summary says so. Individual missing symbols are named
  as DATA_MISSING in the day line — never silently skipped, never scored
  as no-signal.
- **TODO (dated): refresh the December watchlist and seed December
  events into the live calendar in the last week of November
  (by Fri 2026-11-27)** — file `stock_event_watchlist_dec2026.md`,
  same verification standard as the November refresh.

## Control evidence (run 2026-10-31, BEFORE any live logging)

`python3 stocks_sarvaritu_logger.py --control` — **PASS on every leg:**
- 2025 full book rebuilt from machinery + v2 law == post-C24 dump
  **per-trade** (745 tr / +₹27,479.24).
- 2026 full book == post-C24 dump **per-trade** (626 tr / +₹211,588.10).
- **October 2026 subset: 91 trades / +₹52,696.68 — exact.**
- Windowed October rebuild (October days only, calendar sourced from
  late September — the live-mode shape) == full-build October, per-trade.
- Known bounded divergence, disclosed: on 2026-10-29/30 only, the
  forward root's native Upstox 5m bars produce two extra INV-LONG chain
  trades (+₹175.00, +₹202.39) that the frozen book lacks, because the
  frozen book's context for those two days was built from a 1-minute
  cache aggregation (the progressive cache ended 2026-10-28). Both dates
  precede the test window and can never be logged; every test day uses
  native 5m bars end-to-end, exactly as in the control's Jan–Oct 28
  reproduction. The frozen dumps are NOT altered to match.

## Judging — PRE-REGISTERED (no changes during the window)

- November 2026 and December 2026 are scored **separately**.
- A month is a **PASS** iff (i) its total is positive AND (ii) no regime
  cell (REGIME-CLASSIFIER-1) is worse than **−₹5,000** in that month.
- **Book verdict after December:** both months PASS (positive) →
  **SarvaRitu is confirmed as forward-validated**. Either month negative
  → the verdict is stated plainly (the book failed forward validation),
  with the month and cell evidence. A month that passes on total but
  breaches a cell floor is reported as a qualified pass, not hidden.
- **No re-tuning during the test window.** No parameter, exclusion,
  calendar-rule or classifier changes. Any change = a new version,
  frozen and tested from January 2027.
- This whole-book log runs ALONGSIDE the existing November component
  loggers (N4-V3 primary; INV1 and P2F shadows), which are unchanged and
  judged by their own specs. Overlap between logs is expected (the same
  underlying signals) and is not double-counted anywhere: each log is
  judged on its own.

## Files

- Spec: `stocks_sarvaritu_forward_spec.md` (this file)
- Logger: `stocks_sarvaritu_logger.py`
- Live calendar: `stocks_sarvaritu_calendar_live.csv`
- Paper log: `stocks_sarvaritu_paper_log.csv`
- Daily summary: `stocks_sarvaritu_daily_summary.md`
- Data: `data/sarvaritu_fwd/` (frozen seed: `data/full_hist/`)
- Frozen book dumps: `stocks_engine_v2_c24_book2025_trades.csv`,
  `stocks_engine_v2_c24_book2026_trades.csv`
- Cron: `stocks-sarvaritu-paper-logging` (goal: stocks-intraday-systems)
