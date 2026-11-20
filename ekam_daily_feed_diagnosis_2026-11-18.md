# EKAM-Daily UNSCORED diagnosis — 2026-11-18

**Root cause: Upstox v3 historical daily candles are published with a one-day lag. The scorer is not broken; today's candle does not exist on the route yet when it runs (15:35 IST).**

## What the script requests
`fetch_forward()` in `ekam_daily_paper_score.py` calls, per stock:
`GET https://api.upstox.com/v3/historical-candle/{instrument_key}/days/1/{today}/{2026-11-14}`
with instrument keys from `universe_daily/universe.csv` (e.g. ASTRAL = `NSE_EQ|INE006I01046`), the token from `upstox_refresh/.env`, and the Chrome/130 browser User-Agent. Request format, keys, and auth are all correct.

## Evidence
- Live test today (ASTRAL + HDFCBANK, script's exact window and a wider 2026-11-01→18 window): HTTP 200 both times, candles returned only through **2026-11-17**. No 2026-11-18 candle exists on the endpoint yet.
- The ledger's own UNSCORED notes show the same one-day lag every run, source `fetched_v3` (fetch succeeded, data simply ends one day early): Nov 16 run → last bar 2026-11-13; Nov 17 run → last bar 2026-11-16; Nov 18 run → last bar 2026-11-17.
- `ekam_daily_fwd_cache.json` now holds 2026-11-16 and 2026-11-17 for all 25 names — each day's candle arrived in time for the *next* day's run, never its own.
- The scorer's gate requires a bar dated exactly today (`present` check); with today absent from every stock, the whole day is UNSCORED. It also only ever scores the single run date, so the missed days are never caught up even after their candles land.

## Fix options (none applied)
1. **Run later** — move the run to the evening (after Upstox publishes the day candle) or next morning. Cost: breaks the owner's 15:35 same-day-results timing.
2. **Catch-up mode** — each run also scores any earlier UNSCORED day whose candle has since landed. Days land one day late instead of never; 15:35 run still reports "today pending".
3. **Build today's bar from the v3 intraday route** at 15:35 (intraday candles are live same-day) and merge it as the daily candle. Keeps the timing; changes the data route — needs owner approval and a consistency check against the next day's published daily candle.

Not recommended: relaxing the `present` gate to score on yesterday's bar labelled as today — that would mislabel marks.
