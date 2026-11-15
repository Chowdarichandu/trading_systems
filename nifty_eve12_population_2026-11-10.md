# NIFTY-EVE-12 Population Build — Coverage Report (2026-11-10)

**Purpose.** NIFTY-EVE-12 (registered 2026-11-05, `november_rsi_candidates.md`) — *while the book is flat, the first fresh day-range break after 12:30 is taken ATM100 on the break side with DEC-S1 geometry, max 1/day* — could not be scored because its Jan–Oct population was not built (“no stored Jan–Oct 5-minute Nifty spot population”, status note 2026-11-06). This build creates that population. **Data only — no candidate was scored, no number is quoted for EVE-12.** Paper/research data only, real money ₹0.

## What the population is

- **Spot:** NIFTY 5-minute candles, Jan–Oct 2026, full session 09:15–15:30 (75 bars/day, 09:15–15:25), every trading day — the trigger side (morning range + afternoon break detection).
- **Premium:** the matching ATM option 5-min series in the **DEC-S1 construction store** — `daily2leg/prem_nifty.json`, format `{"EXPIRY|STRIKE|TYPE": {"YYYY-MM-DD": {"HH:MM": [o,h,l,c]}}}`, monthly expiry family (expiry in force = nearest monthly ≥ date, the A/B-leg convention in `nifty_engine_r11_decs1_legs.json`), bars kept in the store's own window **10:00–15:15** (the `build_store.py` convention; EVE-12 entries ≥12:30 and DEC-S1 exits incl. 15:10 square-off sit inside it). Read via the standing `prem_day` convention, exactly as DEC-S1 scoring reads it.

## Spot — already present, verified complete (no fetch needed)

`daily2leg/spot.json` → `NIFTY` already holds **all 205 trading days Jan–Oct 2026, each with the full 75 bars 09:15–15:25** (this is the same store the 2026-11-08 break→trend study ran on: 205 days/index). Afternoon coverage verified explicitly per month below (every day's bars run to 15:25). The 2026-11-06 registry note is superseded on this point: the file existed in the daily2leg store; the Nifty engine's own directories had no copy. 2026-01-26 (Republic Day) is correctly absent; 2026-02-01 (Budget Sunday special session) is correctly present.

## Premium — audit first, then a surgical fill

Sufficiency was audited under three nested tests, per (expiry-in-force, strike, CE/PE, day) cell, “complete” = ≥33 of the 34 afternoon bars 12:30–15:15 present in the store:

- **(A) Core pair:** the day's ATM100 pair, ATM from the 12:25 spot close (last bar before the window).
- **(B) Band:** ATM±100, both types (6 cells/day).
- **(C) Touched set (strictest):** every strike that spot's afternoon closes **or bar highs/lows** touch between 12:30 and 15:10 — covers a scorer re-picking ATM100 at any afternoon bar, by close or by extreme.

**Before the fill:** core pair complete on 202/205 days; 15 band cells missing (Feb 1; Oct 28–30 under the 2026-11-23 monthly); 12 touched-close cells missing; 2 further touched-extreme cells missing (2026-02-01, 24600 CE/PE). **Total: 22 (contract, day) cells missing, 0 partial.** Everything else — 1,215 band cells and ~1,000 touched cells — was already in the construction store from the earlier proof/aggressive/next-phase builds.

**The fill (house route only, add-only):** script `nifty_eve12_population_fetch.py` — Playwright browser fetch with the browser User-Agent, token from `upstox_refresh/.env` (never printed), profile check 200, **no HTTP 429 encountered**.

- Expired expiries (2026-02-24, 2026-04-28): instrument keys from `historical_proof_data/contracts_NIFTY_{exp}.json` (monthly, `weekly is False`), `/v2/expired-instruments/historical-candle/{key}/5minute/{day}/{day}` — 2 cells.
- Live expiry 2026-11-23 (for Oct 28–30): keys from a live `/v2/option/chain` call for `NSE_INDEX|Nifty 50` (raw chain cached add-only at `v4_options_oct_data/chain_Nifty_50_2026-11-23.json`, the Nov-03 weekly precedent), `/v3/historical-candle/{key}/minutes/5/{day}/{day}` — 20 cells.
- Raw response bodies saved add-only to `aggressive_data/candles_NIFTY_{strike}{typ}_{day}_{expiry}.json` (22 new files; no existing file overwritten).
- Merge into `daily2leg/prem_nifty.json` at bar level, add-only, trimmed to the store window 10:00–15:15: **1,408 bars added (22 cells × 64), 0 conflicts, contracts 964 → 976, contract-days 8,771 → 8,793.** Pre-build backup: `daily2leg/prem_nifty.json.pre_eve12_backfill_2026-11-10.bak`.
- **Add-only proof:** canonical SHA-256 over all 561,674 pre-existing bars is identical before and after (`e287df30c0ab2e96001d3ccb4c00386cce9c6628dfad5feabb68ddd9811e3dec`); every pre-existing bar re-verified present and unchanged after both merges.
- **NOT_AVAILABLE: none.** Every missing series was obtainable from Upstox; nothing was fabricated or interpolated.

## Final coverage (after the fill)

| Month | Trading days | Spot full-session | Core ATM pair days | Band cells (ATM±100 × CE/PE) | Touched cells (closes+extremes) |
|---|---|---|---|---|---|
| 2026-01 | 20 | 20/20 | 20/20 | 120/120 | 92/92 |
| 2026-02 | 21 | 21/21 | 21/21 | 126/126 | 106/106 |
| 2026-03 | 19 | 19/19 | 19/19 | 114/114 | 132/132 |
| 2026-04 | 20 | 20/20 | 20/20 | 120/120 | 102/102 |
| 2026-05 | 19 | 19/19 | 19/19 | 114/114 | 102/102 |
| 2026-06 | 21 | 21/21 | 21/21 | 126/126 | 108/108 |
| 2026-07 | 23 | 23/23 | 23/23 | 138/138 | 96/96 |
| 2026-08 | 21 | 21/21 | 21/21 | 126/126 | 80/80 |
| 2026-09 | 21 | 21/21 | 21/21 | 126/126 | 90/90 |
| 2026-10 | 20 | 20/20 | 20/20 | 120/120 | 102/102 |
| **Total** | **205** | **205/205** | **205/205** | **1,230/1,230** | **1,010/1,010** |

## Sufficiency verdict

**YES — the population is now sufficient to score NIFTY-EVE-12 under the full gate.** Every trading day Jan–Oct 2026 has full-session spot (morning range + afternoon path) and, in the frozen DEC-S1 construction store itself, the complete afternoon premium series for the ATM100 strike however it is picked at the break bar (12:25-anchored band, any afternoon close, or any afternoon extreme). The gate's remaining legs (timing audit, placebos, halves, month table, ex-top-3, re-sum) are computations over this population and need no further data. Bounds, stated once: the premium store's window is 10:00–15:15 by its own standing design — EVE-12 as registered (entries after 12:30, DEC-S1 geometry, 15:10 square-off) needs nothing outside it; a future variant wanting pre-10:00 or post-15:15 premium bars would need a new build, and the spot side already covers the full session.

*Files: `daily2leg/spot.json` (verified, untouched) · `daily2leg/prem_nifty.json` (22 cells added, add-only) · backup `daily2leg/prem_nifty.json.pre_eve12_backfill_2026-11-10.bak` · raw bodies `aggressive_data/candles_NIFTY_*.json` (22 new) · `v4_options_oct_data/chain_Nifty_50_2026-11-23.json` (new) · fetch script `nifty_eve12_population_fetch.py`.*
