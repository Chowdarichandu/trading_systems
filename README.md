# Chandu Trading Systems — Private Research Repository

Private research repo. **Paper trading only — real money ₹0, no live orders.**
Everything here is backtest / paper-test research on Indian markets (NSE),
built and run with Muse. Not investment advice; not shared with anyone.

## The two systems

### SarvaRitu — stocks (equity cash intraday, Chandu's 25-stock watchlist)
"All seasons": a multi-component intraday equity book designed to have an
earner in every market regime (UP / DOWN / FLAT), validated cross-year
(2025 out-of-sample + 2026) under a recursive self-improvement engine.
Components: F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND (+ RF-1
book-wide law). A frozen forward paper test runs Nov–Dec 2026.

### CRACK / ACRACK — index options (Nifty + Bank Nifty)
Level-based, small-profit, one-and-done index-options system. Bank Nifty and
Nifty are always reported **per index, separately** — never pooled.
November 2026 paper primaries: BNF-PAPER-V1 (Bank Nifty), NF-PAPER-C3G7
(Nifty). ACRACK is the v3 successor in development.

## Basis conventions (read before quoting any number)

- **Stocks:** provisional per **100 shares**, **₹40/trade** cost deducted,
  equity cash LONG/SHORT only, square-off 15:10, paper only.
- **Index:** premium rupees per **1 options lot**, UNIQUE-ONCE counting,
  paper only.
- A number is only quotable after its controls + timing/leak audit pass in
  the same run (standing rule — see the backtest controls gate).

## Where the live documents are

| Document | What it is |
|---|---|
| `stocks_sarvaritu_forward_spec.md` | Frozen SarvaRitu forward-test spec (the live Nov–Dec 2026 test) |
| `stocks_sarvaritu_roof.md` | The one-roof registry: every stocks strategy, its status |
| `stocks_engine_lessons.md` | The engine's lessons registry (read before any new cycle) |
| `stocks_RECURSIVE_ENGINE.md` | Recursive self-improvement engine protocol (v1/v2/v3 charters) |
| `stocks_engine_candidate_spec.md` | Frozen engine candidate spec + December judging rules |
| `stocks_engine_log.md` | Full engine journal |
| `stocks_sarvaritu_paper_log.csv` | SarvaRitu forward paper log (from 2026-11-02) |
| `stocks_n4_november_paper_log.csv` | N4-V3 November primary paper log |
| `november_paper_MAP.md` | November 2026 paper-test board (all channels) |

## Directory map

- `*.py` (repo root) — engines, backtests, loggers, fetchers, diagnostics
  for both systems (file prefixes: `stocks_*` = SarvaRitu, `vline_/u1_*` =
  index lines, `tuning_*` = index tuning sweeps)
- `*.md` — specs, frozen definitions, lessons, logs, candidate registries
- `*.csv` — result books, paper logs, event calendars, scorecards
  (modest-size results only — see exclusions below)
- `*.json` — engine state files and run outputs
- `v2_out/`, `v3_out/` — per-cycle evidence from engine v2 / v3

## What is deliberately NOT in this repo

- Market-data caches (the local `data/**` and `*_cache*/` trees, ~700 MB) —
  regenerable from the data pipeline; kept local only.
- Broker/API token tooling and any credential-like file — the local
  `upstox_refresh/` directory (contains a real `.env`) is excluded in full.
- Virtual environments, `__pycache__`, chart PNGs, and per-trade dumps
  larger than 50 KB from closed experiments (kept locally).
- Sync metadata (`*.muse-github-snapshot-sync.json`) — lives outside the
  repo next to the local staging copy.

See `.gitignore` for the full exclusion list.
