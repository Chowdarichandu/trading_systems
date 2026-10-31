# Results Intelligence Layer v1 — 2026-10-29

Paper only. No orders. Proprietary to Chandu, workspace only, do not publish.
Base: Day Trader skill + V4. Results Intelligence is a CONTEXT GATE only — it
gates a V4/skill setup, it does NOT create a trade alone.

## 1. Results dates (verified, last 4 ANNOUNCED per stock, as of 2026-10-29)
File: `results_dates_v1.csv` — 100 rows, 25 stocks x 4, all verified from
public Moneycontrol / Financial Express board-meeting lists, TipRanks earnings
history, ET/press reports, or company/IR sources (see source + source_url per row).
No date was invented. After-market flag is yes/no only where a source gave a
timestamp; otherwise unverified (not inferred).
Basis: last 4 ANNOUNCED, not scheduled. Scheduled-but-not-yet-announced Q2 FY27
dates excluded: GODREJCP 2026-10-29, ITC 2026-11-02, GLENMARK 2026-11-05,
NTPC 2026-10-31, KALYANKJIL 2026-11-10, NHPC 2026-11-04, PFC 2026-11-05,
IRCTC 2026-11-17/18, NATIONALUM 2026-11-02, HINDALCO 2026-11-06,
TATASTEEL rescheduled to 2026-11-07 (old 2026-10-27 calendars are stale),
BDL 2026-11-14, OIL 2026-11-11. HINDCOPPER Q2 FY27 disputed (6 vs 17 Nov) — excluded.
Stocks already announced Q2 FY27 by 2026-10-29: UNITDSPR 2026-10-28,
OBEROIRLTY 2026-10-16, INDUSTOWER 2026-10-27, RECLTD 2026-10-26,
TVSMOTOR 2026-10-28, HDFCBANK 2026-10-17, WIPRO 2026-10-15, VEDL 2026-10-28,
HINDZINC 2026-10-19, HINDUNILVR 2026-10-28.

## 2. Event study — fixed windows
- T = results announcement calendar date.
- Pre: last 5 trading days with date <= T.
- During: announcement evening -> next trading open gap
  (reaction open / last pre close - 1).
- Post: 5 trading days starting at reaction day
  (reaction = first trading day after T if after_market yes/unverified-assumed-after,
   else T if T is a trading day).
- Lookback: 20 trading days before Pre, for volume median and typical-price mean.
- Measures per event: pre_return %, post_return %, gap %, pre/post volume ratio
  vs 20-day median, range %, excess vs Nifty 50 (same windows),
  close vs 20-day typical-price mean (APPROXIMATE, daily only).
- Accumulation (provisional, NOT Chandu's rule): pre_return > 0 AND
  pre_vol_ratio >= 1.2 — price up + volume up together, not price alone.
- Post direction: continuation if sign(post)==sign(pre) and |post|>1%,
  reversal if sign differs and |post|>1%, else flat.
- Data: Upstox daily candles, 2024-01-01 to 2026-10-28, 701 trading days per
  symbol, in `results_data/` (25 stocks + NIFTY50). Instrument keys verified
  via Upstox search 2026-10-29. No candles fabricated.
- Engine: `results_intelligence.py` (smoke-tested on synthetic data; bug fixed
  in idx_by_date enumeration before any real run).

## 3. Pattern classification — 3/4 rule (REAL RUN, 2026-10-29)
Files: `results_events_v1.csv` (100 events, 94 ok, 6 insufficient_post_data),
`results_patterns_v1.csv` (25 stocks).
- PATTERN (4 stocks): ASTRAL NOACCUM+continuation 3/4, ITC NOACCUM+reversal 3/4,
  PFC NOACCUM+continuation 3/4, TATASTEEL NOACCUM+continuation 3/4.
- NO_PATTERN (15 stocks): BDL, GLENMARK, GODREJCP, HDFCBANK, HINDALCO,
  HINDCOPPER, HINDZINC, IRCTC, KALYANKJIL, NATIONALUM, NHPC, NTPC, OBEROIRLTY,
  OIL, WIPRO — most common signature only 1-2/4.
- INSUFFICIENT_EVENTS (6 stocks, PENDING not no-pattern): HINDUNILVR,
  INDUSTOWER, RECLTD, TVSMOTOR, UNITDSPR, VEDL — their Q2 FY27 events
  (26-28 Oct 2026) have no complete 5-day post window yet in data to 2026-10-28.
  Re-run after early Nov 2026 to complete them; do not classify them yet.
- Aggregate over 94 ok events: pre_return mean +0.93%, post_return mean -2.08%,
  gap mean -0.79%, pre_vol_ratio mean 1.26x, post_vol_ratio mean 2.01x,
  excess vs Nifty pre +0.83%, post -2.11%. Accumulation (pre up + vol >=1.2x)
  in 27/94 events. Post directions: reversal 43, continuation 41, flat 10.
- IMPORTANT reading: pattern is sign-based, not bullish by itself.
  PFC "continuation" is mostly DOWN-continuation (pre -1.03/-3.86/-6.12%,
  post -10.48/-3.73/-1.49%); ITC "reversal" is mostly post-down after mixed pre.
  ASTRAL is the cleanest up case (pre +2.04/+1.83/+1.17%, post +5.53/+5.85/+8.04%).
  TATASTEEL continuation is mixed-sign. Do NOT trade a pattern label alone;
  gate must also check pre sign and post excess, per the V5 gate below.
- A pattern is a gate, not a signal: e.g. ACCUM+continuation -> allow long
  V4/skill setups in pre/post windows, block shorts; ACCUM+reversal -> block
  chasing the pre-run, allow only reversal setups; NO_PATTERN -> results layer
  is neutral, V4/skill runs ungated.

## 4. V5 framework — Day Trader skill + V4 + Results gate
- V5 = V4 setups + Day Trader skill scanner/exit discipline + Results gate above.
- Skill v1 -> v2 iteration is separate from V5: skill entry/exit changes are
  versioned as skill v2, V4-derived entry changes as V5, unified engine as V6
  only after both pass independently.
- Tuning methods (not a single grid):
  1. Walk-forward: expanding and rolling windows, tune on fold N, test on fold N+1.
  2. Purged validation: no overlapping pre/post windows across train/test;
     results events are purged as whole events, never split.
  3. Ablation: remove one layer at a time (Results gate, bias, room, skill flag)
     and measure the change on validation.
  4. Sensitivity: vary accumulation threshold (1.0/1.2/1.5x volume) and post
     threshold (0.5/1.0/2.0%) and report the range, not a single cherry-picked point.
  5. Regime check: results pattern by market regime (Nifty trend / VIX proxy
     from daily data) — a pattern that only works in one regime is flagged.

## 5. Adoption gate — progressing results only (Chandu, 2026-10-29)
X = all three together, on VALIDATION (unseen period), never in-sample alone:
  (1) 2-3 quality trades/week, portfolio total; (2) good net profit; (3) good win rate.
- A V5 / skill v2 version is adopted ONLY if it improves on validation vs the
  previous best on all three, or improves net + win rate with frequency still
  inside 2-3/week. A decreasing result is NOT adopted: keep previous best,
  log the failure, fix, retry.
- When Chandu asks a question, just report status/numbers plainly.

## 6. Continuous loop spec — not a 15:30-only job
- Intraday paper signals: 09:15-15:15 only, closed candles only.
- Daily after close: update pre/post windows, check for moved/announced results
  dates, log flat / gap-up / gap-down, update runbook.
- Weekly: re-score last-4 pattern per stock, flag any pattern that broke.
- Quarterly, after each new result: add new quarter, drop oldest (rolling last 4),
  re-run event study, fix the rule if it failed, log the fix. Never re-trade a
  failed pattern unchanged.
- Loop order: identifying -> learning -> fixing -> identifying again.
- Cron (Muse, already set 2026-10-29): Upstox refresh 03:45 weekdays,
  check 08:00, rescue 08:05 — token only, not a trading signal.

## 7. Limitations (honest)
- Sector excess is NOT yet computed: sector index series per stock were not
  fetched in v1; excess vs Nifty only. Add sector mapping in v2.
- VWAP position is daily typical-price approximation, not intraday VWAP.
- After-market flag: where a source did not state time, assumed after-market
  (Indian results are overwhelmingly evening filings) and flagged as unverified
  for that field, not as verified.
- October 2026 quarter (Q2 FY27) may not yet be announced for some stocks at
  2026-10-29; for those, last 4 = the 4 most recent ANNOUNCED quarters.
- This file, event study, and pattern table are NOT proof of edge and NOT a
  live-trading recommendation. Forward paper on the NEXT results cycle is required.
