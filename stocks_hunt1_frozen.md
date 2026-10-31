# HUNT-1 — a NEW intraday STOCK strategy (equity cash, NOT options) — FROZEN 2026-10-30 (late night), BEFORE SCORING

**Status: invented from the user's own hunting description, frozen before
any HUNT-1 scoring run. NOT adopted, NOT a live system. Paper only,
no orders, real money ₹0.**
**Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks, 203 trading days.**
All rupee figures provisional per 100 shares, ₹40/trade cost — NOT a lot
profit, NOT premiums. LONG = bullish breakout bought in equity;
SHORT = bearish breakdown sold in equity (paper short, intraday square-off).
A family survives ONLY if net (after ₹40) is positive in BOTH halves
(Jan–May AND Jun–Oct). October shown separately. No hindsight filters.

## Design source — the user's words (2026-10-30 23:27 IST)

> "Invent a new strategy… for example HDFC — there is a breakout at
> 10 o'clock, it met 0.5% or 1% target and we trail and we got 1%, and
> later we hit stop loss. And again we got one more entry, and again
> the stock fell, we got one more entry — in a day we can get four
> trades [on one stock]. We can hunt in stocks rather than options."

HUNT-1 encodes exactly that loop: rolling breakout → trail the winner
(0.5% becomes 1%+) → exit → the stock goes back on watch → the next
breakout is traded again, up to 4 entries on one stock in one day.

## Core rules (identical for all families unless a family says otherwise)

- **Data**: `data/progressive/<SYM>/spot_5m.csv`, candles labelled by
  start time (09:15 … 15:25), daily bars from `spot_daily.csv`.
  Trading days = NIFTY daily dates in window. A stock-day with
  missing/partial candles is skipped, not filled.
- **Day-so-far extremes**: running high/low computed from the 09:15 bar
  onward, updated with every completed candle's high/low. Trigger
  candles are those starting at or after **09:45** (the 09:15–09:40
  bars only seed the extremes).
- **Trigger A (base)**: a 5-min candle whose CLOSE is above the
  day-so-far high computed from all candles BEFORE it → **LONG**,
  entry at that close. Close below the day-so-far low → **SHORT**,
  entry at that close. One open position per stock at a time.
- **Trail exit (primary, the user's exit)**: initial stop = entry ∓ 0.5%.
  Track best price (highest high for LONG / lowest low for SHORT) from
  the candle AFTER entry. Trail activates once best reaches entry ± 0.5%
  in favour; trail stop then sits 0.35% behind best. Effective stop =
  max(initial, trail) for LONG (mirror for SHORT). Per candle, in order:
  (1) stop check against the stop computed BEFORE this candle — if the
  candle's low (LONG) touches it, exit at the stop, or at the candle
  open if the open is already through the stop; (2) only then update
  best with this candle's high/low. Square-off at the close of the
  15:10 candle if still open. No new entries after the 15:05 candle.
- **Fixed-exit controls**: target/stop checked from the candle after
  entry, stop first on a candle touching both; exit at target/stop or
  the open if already through; square-off 15:10 close.
- **Re-entry (the hunt)**: after any exit on exit-candle k, scanning
  resumes at candle k+1. Extremes keep updating all day regardless of
  position, so the next entry needs a NEW day-so-far extreme close.
  Chain round = entry sequence number within the stock-day (1st, 2nd…).
- **Costs**: ₹40 per completed trade, 100 shares. Net = (exit−entry)·sign·100 − 40.

## Families (frozen iteration order; one change each)

- **F0 base**: Trigger A + trail exit + chain cap 4/stock/day.
- **F1**: F0 but fixed exit target +1.0% / stop −0.5%.
- **F2**: F0 but fixed exit target +0.5% / stop −0.5%.
- **F3**: Trigger B + trail + cap 4. Trigger B: close above the highest
  high / below the lowest low of the trailing 12 completed candles
  (60 min, excluding the trigger candle); active from the 10:15 candle.
- **F4**: F0 but chain uncapped.
- **F5**: F0 + stock-day stop-out: after 2 consecutive stop exits on a
  stock, no more entries on that stock that day.
- **F6**: F0 + only stock-days whose prior-10-trading-day average daily
  range ((high−low)/close from daily bars strictly before today) ≥ 2%.
- **F7**: F0 + no entries on trigger candles starting at/after 14:30.
- **F8**: F0 + reclaim re-entries: after a LONG exit at price X on
  candle k, if a later candle's low ≤ X·(1−0.5%) and a still later
  candle closes back above the previous trade's trigger level (the
  day-so-far extreme that triggered it) without that close itself
  being a Trigger-A breakout, enter LONG at that close (trail exit,
  counts toward cap 4 and chain round). Mirror for SHORT (high ≥
  X·(1+0.5%), close back below trigger level).
- **F9+**: diagnosis-driven families only, each defined in the report
  BEFORE its run, one change from the then-best family.

## Reporting (frozen)

Every family: trades, win%, full-… n/a — report net ₹ provisional per
100 shares, expectancy/trade, trades/day, both halves, October alone,
chain-round expectancy table (rounds 1,2,3,4,5+), LONG/SHORT split,
top/bottom 5 stocks. Event-window tag per trade from
`stock_event_calendar_jan_oct_2026.csv` (±7 trading days around
event/reaction, the standing window) reported as a split, never a gate
in F0–F8.
