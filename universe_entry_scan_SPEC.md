# Universe Entry Scan — SPEC (FROZEN 2026-11-16, before any scan run)

Owner's order 2026-11-16 07:11: the EKAM-daily entry-pattern checker runs on ALL
NSE-listed stocks, and the output must be FORWARD-looking — stocks whose entry is
NEAR (setting up), not patterns that fired weeks ago. This spec is frozen before
the scan runs; the NEAR rule below is NOT tuned after seeing results.

## Data
- Universe: NSE official EQUITY_L.csv (2026-11-16) — 2,646 listed equities,
  100% cross-validated against the fresh Upstox NSE_EQ instrument master
  (symbol + ISIN → instrument_key). File: `universe_daily/universe.csv`.
- Bars: daily OHLCV per symbol from Upstox `/v3/historical-candle`, 2019-01-01
  (or earliest available) through Fri 2026-11-13, stored as Parquet in
  `universe_daily/`. Scan runs ONLY on symbols whose dump completed.
- As-of date for classification: the symbol's own latest close (2026-11-13 for
  actively traded names; older for suspended/thin names — recorded per row).

## Frozen signal definitions (verbatim from ekam_SPEC.md, EKAM-daily = EKAM-2c)
- Bollinger(20,2): window mean ± 2 · population-SD on closes.
  lower[t], mid[t] computed on the 20 closes ending at t.
- RSI(14): Wilder.
- **BB-REV signal at day t:** close[t−1] < lower[t−1] AND close[t] ≥ lower[t].
- **RSI-REV signal at day t:** RSI[t−1] ≤ 30 < RSI[t].
- (EKAM fill convention — signal at t close → entry t+1 open — is context only;
  this scan classifies signal STATE, it does not simulate trades.)

## Classification (per symbol, at its latest close = day T)
- **FIRED** — a BB-REV or RSI-REV signal fired on any of the last 5 trading days
  (T−4 … T). Record which pattern(s) and the most recent firing date.
- **NEAR** — no FIRED signal, AND at least one of these three frozen setup rules
  holds at day T ("falling" = value at T strictly less than value at T−1):
  - **N1 (RSI approaching):** 30 < RSI[T] ≤ 40 AND RSI falling.
  - **N2 (band approach):** close[T] above lower[T], distance-to-lower-band
    (close/lower − 1) ≤ 3%, AND close falling (close[T] < close[T−1]).
  - **N3 (weak-below-middle):** close[T] < mid[T] AND RSI[T] < 45 AND RSI falling.
  Record which rule(s) matched.
- **ABSENT** — everything else (count only). Symbols with < 60 daily bars are
  INSUFFICIENT-DATA (listed separately, not counted as ABSENT).

## Per-stock recorded values
latest close, last date, RSI(14), %B = (close − lower)/(upper − lower),
distance-to-lower-band %, close vs 50-DMA (above/below), close vs 200-DMA
(above/below), class, pattern/rule detail.

## Quality overlay (Stage 4)
- PROVEN tags from our own records only: v2 screener PASS
  (`value_screener_v2_2026-11-11.csv`), the ₹30–200 proof packs
  (`investing_longterm_30_200_2026-11-15.csv` — SOLID / WATCH verdicts),
  frozen-25 Stock Book membership.
- Everything else: UNPROVEN (chart setup only — never presented as
  fundamentally good).

## Deliverables
`universe_entry_scan_2026-11-16.csv` (all scanned rows) + `.md` report:
NEAR list PROVEN-first, then FIRED-PROVEN, counts, honest gaps.
