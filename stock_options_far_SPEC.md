# STOCK OPTIONS — FAR-EXPIRY TEST — SPEC (FROZEN 2026-11-15, before any far-expiry fetch or scoring)

Owner approved 2026-11-15 11:38. This extends the completed stock-options
programme (`stock_options_SPEC.md`, results `stock_options_2026-11-15.md`).
It reuses that programme's entry lists, premium-fetch machinery, cache
(`stock_options_data/`) and NC conventions. The near-expiry variant is NOT
re-run.

Question: the near-expiry run died mostly because the contract expired
before EKAM's hold ended (EKAM-only: 35 of 66 scored in 2025 and 56 of 95
in 2026 hit expiry first). Does choosing a FAR expiry — one that can
survive the hold — change the verdict vs cash?

Research only. Arms nothing. OPTION BUYING ONLY — no selling, ever.
Paper only, real money Rs0. Judged per year, never pooled.

## 1. Entries (one source only)

EKAM-DAILY 2c — the exact cash positions of the first run, from
`ekam2c_trades.csv` (book = EKAM2c), entries dated 1 Jan – 31 Oct:
2025 = 74 positions, cash +Rs42,954.60 per 100 shares;
2026 = 102 positions, cash +Rs1,41,328.40 per 100 shares.
All entries LONG -> bought CE. Same signal days; option entry at the
premium OPEN on the cash entry_date — identical timing to the cash and
near-expiry runs.

## 2. Contract selection — THE ONLY CHANGE vs the first run

Expiry: among the stock's listed monthly expiries (Upstox
expired-instruments listing / live master for not-yet-expired months,
discovered for the entry month and the three following months), choose
the FIRST expiry with expiry_date − entry_date >= 45 calendar days.
If no listed expiry reaches 45 days, take the FARTHEST available expiry
and record its days-to-expiry on the trade row. If the name has no
option expiries listed at all in that span -> NC NO_OPTIONS. If expiries
exist but no contract satisfies the strike/type/lot rules -> NC
NO_CONTRACT (incl. NO_LOTSIZE / NO_SPOT_REF as in the first run).

Strike: the listed CE strike nearest the entry-day CLOSE of the
underlying (local daily store `data/sarvaritu_fwd/{sym}/spot_daily.csv`).
Tie -> lower strike. Lot size from the expired-contract record, stated
per trade.

## 3. Entry / exit premium (identical to the first run, SPEC s.3)

Premium data: Upstox expired-instruments route only, browser User-Agent
header on every call, token read from `upstox_refresh/.env` and never
printed/logged. Disk cache under `stock_options_data/`; cached responses
are reused, never re-fetched except where a wider date range is needed.

- Entry: premium OPEN on the cash entry_date.
- Exit, by the cash trade's own exit kind, on the cash exit_date:
  - SIGNAL-BB / SIGNAL-RSI / TIME (cash exits at the open) -> premium OPEN.
  - FORCED (cash marks at the close) -> premium CLOSE.
  - CAP (cash exits intraday at underlying entry x 1.10) -> first
    5-minute bar on exit_date whose spot high reaches the level; exit =
    that bar's premium CLOSE from 5-minute premium candles; if 5-minute
    premium candles are unavailable, premium daily CLOSE, labelled
    CAP_CLOSE.
- Expiry truncation: if the chosen contract STILL expires before the
  cash exit date, exit at the premium CLOSE on the expiry date,
  exit_kind = EXPIRY. These positions are counted and reported per year
  (the "still died at expiry" count).
- EXIT_STALE (scored, labelled — not NC): exit candle missing on the
  exact exit date; last available candle on/before that date (and
  on/after entry) is used, its actual date recorded.

## 4. NC rules (counted and listed, never substituted, never estimated)

Same codes as the first run: NO_OPTIONS, NO_CONTRACT, NO_ENTRY_CANDLE,
NO_EXIT_CANDLE, NO_LOTSIZE, NO_SPOT_REF, RATE_LIMITED (HTTP 429 stops
the fetch attempt immediately; unfetched trades are NC RATE_LIMITED for
that attempt — no retry, no route switch inside the attempt; a later
gentle run is a new attempt and may fill cache misses only).

## 5. Money

Cost Rs220 per completed option position. Per-trade option net
(per 1 lot) = (exit_premium − entry_premium) x lot_size − 220.
Per-100-shares equivalent = net_per_lot / lot_size x 100.
WR = share of scored trades with net > 0. Halves: Jan–Jun / Jul–Oct by
entry date, nets of scored trades, per year. Best/worst trade per year.

## 6. Control (verified before scoring, 2026-11-15)

From the first run's STORED trades (`stock_options_trades.csv`,
EKAM2C rows) — reproduced exactly:
- 2025: 66 scored, net per lot −Rs212,268.75, NC 8, expiry-truncated 35.
- 2026: 95 scored, net per lot −Rs396,390.75, NC 7, expiry-truncated 56.
And from `ekam2c_trades.csv` (prep asserts): cash 2025 = 74 trades,
+Rs42,954.60; cash 2026 = 102 trades, +Rs1,41,328.40.

## 7. Reporting (deliverables)

`stock_options_far_2026-11-15.md` + `stock_options_far_results.json` +
`stock_options_far_trades.csv` (one row per position, incl. chosen
expiry, days_to_expiry, strike, lot size, premiums, exit kind, nets,
status/NC reason). Per year: option trades scored, NC count by reason,
net per lot, per-100 equivalent, WR, best/worst, halves, still-died-at-
expiry count; beside it the near-expiry line and the cash line. One
closing line: far-expiry vs near-expiry vs cash — which made more
(on the per-100 equivalent).

## 8. Data-status note at freeze time

The first run's fetch completed today (~11:00 IST) on the current
stored token with no 429. The far fetch reuses the same token mechanism
and cache; far contracts are mostly NOT yet cached, so a real fetch is
expected. If the token check fails, the fetch exits before any data
call and unfetched trades score NC BLOCKED_TOKEN — nothing estimated.
