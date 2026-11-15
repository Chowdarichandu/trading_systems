# STOCK OPTIONS — FAR-EXPIRY TEST on EKAM-daily entries (2026-11-15)

Research only; option BUYING only; paper, real money Rs0. Cost Rs220 per completed option position. Per-100-shares equivalent = net per lot / lot size x 100.

Same EKAM-daily 2c entries, entry timing and exits as the near-expiry run — the ONLY change: the bought ATM call's expiry is the first listed expiry >= 45 days after entry (farthest available if none reaches 45 days, days-to-expiry recorded per trade).

## EKAM-daily 2c, FAR expiry — 2025

- Option trades scored: 13 · NC: 61 {'NO_OPTIONS': 2, 'NO_ENTRY_CANDLE': 59}
- Net per 1 lot: 3988.75 · per-100 equivalent: 7048.41 · WR: 53.8
- Best/worst trade (per lot): 24102.5 / -42070.0 · halves per lot (Jan-Jun / Jul-Oct): [-21138.75, 25127.5]
- Still died at expiry (contract expired before the cash exit): 2 of 13 scored (near-expiry run: 35 of 66)
- Farthest-fallback trades (no >= 45-day expiry listed): 1 ['HINDCOPPER entry 2025-07-30 expiry 2025-07-31 dte 1']
- NO_ENTRY_CANDLE anatomy: {'candles_start_after_entry': 50, 'file_empty_all_range': 9} (candles_start_after_entry = the far contract had not traded yet at entry)
- Near-expiry line: 66 scored, net per lot -212268.75, per-100 -53945.74, WR 37.9, NC 8
- Cash line (published, per 100 shares): +Rs42954.6
- Verdict: CASH made more (far per-100 7048.41 vs near per-100 -53945.74 vs cash +Rs42954.6).

## EKAM-daily 2c, FAR expiry — 2026

- Option trades scored: 25 · NC: 77 {'NO_ENTRY_CANDLE': 71, 'NO_OPTIONS': 6}
- Net per 1 lot: -175865.0 · per-100 equivalent: -18399.47 · WR: 28.0
- Best/worst trade (per lot): 17145.0 / -35188.75 · halves per lot (Jan-Jun / Jul-Oct): [-136782.5, -39082.5]
- Still died at expiry (contract expired before the cash exit): 6 of 25 scored (near-expiry run: 56 of 95)
- Farthest-fallback trades (no >= 45-day expiry listed): 0 
- NO_ENTRY_CANDLE anatomy: {'candles_start_after_entry': 66, 'file_empty_all_range': 5} (candles_start_after_entry = the far contract had not traded yet at entry)
- Near-expiry line: 95 scored, net per lot -396390.75, per-100 -50482.24, WR 30.5, NC 7
- Cash line (published, per 100 shares): +Rs141328.4
- Verdict: CASH made more (far per-100 -18399.47 vs near per-100 -50482.24 vs cash +Rs141328.4).

## Closing line

- 2025: FAR 7048.41 vs NEAR -53945.74 vs CASH +42954.6 per 100 -> CASH made more
- 2026: FAR -18399.47 vs NEAR -50482.24 vs CASH +141328.4 per 100 -> CASH made more

## Notes

- Control (SPEC s.6): the near-expiry EKAM rows were reproduced from the first run's stored trades before scoring — 2025: 66 scored / -Rs212,268.75 per lot / NC 8 / 35 expiry-truncated; 2026: 95 scored / -Rs396,390.75 per lot / NC 7 / 56 expiry-truncated. Cash totals re-asserted in prep: 74 / +Rs42,954.60 (2025), 102 / +Rs1,41,328.40 (2026).
- Entry premium = contract open on the cash entry date; exits mirror the cash exit kind exactly (SIGNAL/TIME at the open, FORCED at the close, CAP at the 5-minute trigger bar), with expiry truncation at the expiry-day close when the contract still dies first.
- NC ANATOMY (the dominant finding): of the 138 NC positions, 130 are NO_ENTRY_CANDLE — and 116 of those 130 are cases where the chosen far contract's FIRST candle in the entire fetched range falls AFTER the entry date (the other 14 files are empty across the range, incl. the patchy Mar-2025 expiry set already known from the first run). Upstox returns a candle only for days the contract traded: the far-month contract was listed but had no trades yet when EKAM signalled. This is a liquidity wall, not a fetch failure — in live trading the same wall appears as no quote to buy.
- SCORED-SUBSET CAVEAT: the 38 scored trades are self-selected for exactly the names/dates where a far contract was already trading at entry, so the scored far-expiry lines OVERSTATE what the rule could have done across all 176 signals. The year verdicts are therefore read as: far expiry beats near expiry where it can be traded at all, and still loses to cash in both years.
- FALLBACK DETAIL: the single farthest-fallback trade is HINDCOPPER entered 2025-07-30 — discovery holds no listed expiry for HINDCOPPER Aug-Oct 2025 (None in the first run's discovery), so the only expiry in the 4-month span was 2025-07-31 (dte 1); it scored as effectively a near-expiry trade and is inside the 2025 scored line.

