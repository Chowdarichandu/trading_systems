# EKAM-INTRADAY — STOCKS · SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1 (owner's correction 2026-11-14 20:53 — EKAM means INTRADAY
indicators clubbed together, NOT daily; the daily EKAM is a different artefact and is not
this system). Segment: **Stocks**. STANDALONE — it does not condition or filter the Stock
Book; it generates its own intraday signals from the frozen 25 names' candles.
Basis: equity cash intraday · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0.
Frozen 25: ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC
INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL
TVSMOTOR UNITDSPR VEDL WIPRO.
Standard indicators only, clubbed by votes. Identical core across segments (this file is
the Stocks realisation).

## DATA / FILL DETAILS

1. **Store:** `data/sarvaritu_fwd/<SYM>/spot_5m.csv` (same store as DIAL-Stocks; extends to
   2026-11-13 for the November CF). 5-min OHLC bars; signal on a COMPLETED bar's close;
   entry at the NEXT present bar's open within the same session.
2. **No volume exists** in the persisted stock stores, so session VWAP is the
   **equal-weighted cumulative mean of bar typical price (H+L+C)/3**, reset each session —
   "session VWAP (EW proxy)", disclosed wherever the numbers are reported.
3. **Indicator construction (all causal, trailing only; on the continuous per-stock 5-min
   series — state carries across sessions, as on a live chart — except VWAP, per session):**
   - EMA(9), EMA(21): seeded with the SMA of the first `span` closes, then k = 2/(span+1).
   - MACD(12,26,9): EMA(12) − EMA(26) (same seeding); signal = EMA(9) of the MACD line,
     seeded with the SMA of the first 9 MACD values (first MACD value at index 25, first
     signal value at index 33).
   - RSI(14): Wilder, on closes; seeded with the SMA of the first 14 close-changes.
   - Supertrend(7,3): standard ratchet bands; ATR(7) Wilder RMA seeded with the SMA of the
     first 7 true ranges (identical construction to DIAL-Stocks). Direction +1 = uptrend,
     −1 = downtrend, 0 = not yet initialised.
   - ADX(14): Wilder. TR as in the Supertrend construction; +DM = up-move when up-move >
     down-move and > 0 (else 0), −DM mirrored. Smoothed TR/±DM seeded at index 14 with the
     sum of indices 1–14, then s = s − s/14 + value. ±DI = 100 · smoothed±DM / smoothedTR.
     DX = 100 · |+DI − −DI| / (+DI + −DI) (0 if the denominator is 0). ADX seeded at
     index 27 with the SMA of DX[14–27], then ADX = (ADX·13 + DX)/14.
   - Warm-up: no votes on a bar until every indicator is defined AND the continuous series
     has ≥ 60 bars of history including the current bar (binds only at the store's start).
4. **Tradable stock-day:** the day contains the bar stamped 15:10 AND ≥ 30 bars; otherwise
   NC (no trades), counted. (Known NC: 2025-10-21 Muhurat, all 25 names; the 2026-11-08
   Sunday stub in November.)

## VOTES (evaluated at each completed bar's close, bars ≤ t only)

Let L5 = number of LONG conditions 1–5 true, S5 = number of SHORT conditions 1–5 true.

| # | LONG (+1) | SHORT (+1) |
|---|---|---|
| 1 | close > session VWAP (EW proxy) | close < session VWAP (EW proxy) |
| 2 | EMA(9) > EMA(21) | EMA(9) < EMA(21) |
| 3 | Supertrend direction = +1 | Supertrend direction = −1 |
| 4 | MACD line > MACD signal | MACD line < MACD signal |
| 5 | 50 ≤ RSI(14) < 70 | 30 < RSI(14) ≤ 50 |
| 6 | ADX(14) ≥ 20 AND L5 > S5 | ADX(14) ≥ 20 AND S5 > L5 |

Vote 6 is the ADX strength vote: it adds +1 to whichever side leads on votes 1–5 when
ADX ≥ 20; a tie on votes 1–5 earns no vote 6. LONG votes LV ∈ 0–6, SHORT votes SV ∈ 0–6.

## ENTRY

- Per stock per day: the FIRST bar where LV ≥ T (→ LONG) or SV ≥ T (→ SHORT), for the
  row's threshold T ∈ {4, 5}. If both sides reach T on the same bar (arithmetically near-
  impossible under the mirrored definitions), the larger total wins; an exact tie = no
  signal that bar and scanning continues.
- Entry at the next present bar's open in the same session; the entry bar's stamp must be
  ≤ 15:10. A signal on the day's last bar has no entry and is dropped.
- At most 1 trade per stock per day. **At most 5 trades per day across the list:** the
  day's candidate signals (one per stock) are ordered by signal-bar stamp, ties broken
  alphabetically by symbol, and only the first 5 are taken.

## EXITS (entry price E = entry bar's open; bars monitored entry bar → 15:10 bar incl.)

- **X1 (fixed):** LONG target 1.01·E / stop 0.995·E; SHORT mirrored (0.99·E / 1.005·E).
  Within a bar, stop fills first if both levels are inside the range; a gap through a
  level fills at the bar's open. If neither level is hit by the 15:10 bar, square-off at
  the 15:10 bar's CLOSE.
- **X2 (vote-decay):** hard stop only — LONG 0.9925·E, SHORT 1.0075·E — same gap/stop
  fill rules as X1 (checked on each monitored bar before the decay test). Decay test: at
  each monitored bar's close, if the position's own-direction votes (LV for LONG, SV for
  SHORT, computed at that bar) ≤ 2, exit at that bar's CLOSE. If no exit by the 15:10
  bar's close, square-off at the 15:10 bar's CLOSE.
- Net per trade: LONG (exit − E)·100 − 40; SHORT (E − exit)·100 − 40 (per 100 shares
  provisional).

## ROWS (only these four)

T4-X1 · T4-X2 · T5-X1 · T5-X2 (T = vote threshold, X = exit rule).

## REPORTING (frozen)

- Per row, PER YEAR (2025 and 2026 separately, never pooled): windows Jan–Jun
  (entry dates Jan 1–Jun 30), Jul–Oct (Jul 1–Oct 31), full Jan–Oct — trades, net, WR.
  Trades are dated by ENTRY day.
- **Timing audit:** assert entry stamp > signal stamp on every trade; plus a truncated-
  series recompute of the vote counts on a deterministic sample of signal bars (every
  37th candidate signal across the run) — votes recomputed from bars ≤ t only must match.
- **Placebo:** on the best full Jan–Oct row per year (best = highest full-year net for
  that year): 200 draws, fixed seed 20261114. Each draw = the row's real trade count for
  that year; each placebo trade = uniform random tradable stock-day of that year × uniform
  random entry bar (stamps 09:20–15:10 present that day) × uniform random side; exit by
  the row's own exit rule evaluated on that stock-day's real bars (and real vote series
  for X2). Percentile = % of draws whose total is below the real total.
- **November CF (descriptive only):** the frozen rows run over entry dates
  2026-11-02 – 2026-11-13 (the Stock Book's 9 November trading days: Nov 2,3,4,5,6,9,11,
  12,13), with the same 5-per-day cap. The 2026-11-08 stub is NC, excluded.
- Coverage: stock-days and NC stock-days per gate year (Jan–Oct), as in DIAL-Stocks.
