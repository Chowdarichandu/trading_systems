# Stocks EQUITY — small-target systems run — FROZEN 2026-10-30, BEFORE SCORING

**Direction set by the user 2026-10-30 19:09 IST, superseding the
S1–S12 standalone-system direction. STOCKS ARE EQUITY CASH intraday.
NOT options. No premiums anywhere. A bullish signal = LONG equity;
a bearish signal = SHORT equity (paper short, intraday square-off).
All reporting uses LONG/SHORT language only. Paper only, no orders.
Real money: ₹0.**

Window: October 2026 = 1–28 Oct in cache, 18 trading days
(29 Oct missing from cache — stated, not a zero-trade day).
Universe: 25 screenshot stocks, data `data/progressive/`.
Basis: per 100 shares, provisional, ₹40/trade flat cost, labelled in
every figure sentence.

## Systems leveraged (existing index systems, stock adaptations as
## already frozen in this workspace — no new standalone system)

- **V5-stock** (per `stocks_v2_versions_oct30.py` frozen definition):
  pool of V4 signals (`daytrader_cash_tuning.find_signal`, BASE params:
  setups 2/3/4 on PD/OR levels, bias filter, room 0.36% of close,
  Setup 1 skipped — no Red bands for stocks) + Skill-v2 OR-only
  signals; dedup same stock+day by setup rank (setup4=3 > setup3=2 >
  setup2=1 > skill_or=0), then prospective net, then earlier signal.
- **Skill** (Day Trader Skill's own entries,
  `daytrader_skill_run.find_skill_signal`, patterns or+flag+oversold,
  earliest signal of the day): OR breakout/breakdown to 11:30, flag
  breakout/breakdown, oversold RSI bounce (LONG only by construction).
- **(lA)-stock** (per `stocks_v2_versions_oct30.py` frozen adaptation
  of DOCUMENTED_V5_LA_BANKNIFTY (lA)): NIFTY confirms the stock —
  Nifty's first OR break of the day (OR = 09:15–09:30 bars, break =
  first close beyond OR after 09:30); the stock's morning candidate =
  earliest pooled V4 / Skill-v2 signal for that stock-day with signal
  time ≥ Nifty break time and ≤ 11:30, in the SAME direction as
  Nifty's break. Adaptation stated: the (lA) re-entry leg is NOT run
  in this pass because its trigger (a morning stop) depends on which
  exit variant is being scored; morning legs only.
- **Volrix-stock** (per frozen Volrix adaptation): trigger = the
  stock's own previous trading day close ≤ −2.0% vs the day before;
  entry next session 09:15 open, LONG only; 10-trading-session
  cooldown per stock after an entry. Adaptation stated: the original
  Volrix exit was a plain 15:10 square-off with no intraday
  stop/target; in this run the frozen % exits below are overlaid, as
  the task requires every system × every exit variant.

Signal → entry (all intraday systems): entry = open of the next
5-min candle after the signal candle. One signal per system per
stock per day (earliest). Direction mapping: CE-type signal = LONG,
PE-type signal = SHORT.

## Exits — frozen (the user's small-target design)

- **T05:** target = entry ± 0.5%, stop = entry ∓ 0.5%.
- **T10:** target = entry ± 1.0%, stop = entry ∓ 0.5%.
- **TSYS:** target = entry ± 1.0%, stop = signal-candle low (LONG) /
  high (SHORT), capped at −1.0% from entry (if the signal-candle
  stop is wider than 1.0%, the stop is 1.0%); a signal whose system
  stop is not beyond entry is skipped as invalid.
- First hit wins on 5-min candles; if stop and target are both hit
  in the same candle, STOP first (conservative). Otherwise square
  off at the 15:10 candle close (last candle if 15:10 absent).
  Volrix replay starts on its 09:15 entry candle; other systems
  replay from the entry candle onward.
- Net per trade (provisional per 100 shares) = direction ×
  (exit − entry) × 100 − ₹40. Average % captured per trade is also
  reported: mean of direction × (exit − entry) / entry × 100.

## Caps and ranking (frozen, signal-time information only)

- Uncapped view: max 1 trade per stock per day per system (by
  construction); unified uncapped dedups same stock+day+direction
  across systems (earliest entry kept, contributing systems listed).
- Portfolio capped view: max 1 trade per trading day across all 25
  stocks. Ranking = the system's own priority: setup rank desc
  (setup4=3, setup3=2, setup2=1, skill patterns=0, Volrix=−1 in
  unified; within Skill: or=2, flag=1, oversold=0), then prospective
  T10 target net desc (1.0% × entry × 100 − ₹40, known at entry),
  then entry time asc. Volrix's own capped view ranks by
  |previous-day drop| desc (its frozen priority, known at open).

## Events first

Every trade tagged from `stock_event_calendar_jan_oct_2026.csv`
using the frozen gate-v1 window (±7 trading days around the event /
effective reaction date, as coded in `stocks_v2_versions_oct30.py`):
`event_window` or `no_event`. Results are reported for ALL days and
for the NO-EVENT subset separately (the user's rule: the systems
apply where there is no influencing news; event days are reported
separately, never silently mixed).

## Reference line only

S12 October (old standalone S-family, 2R/3R design the user has now
dropped): 8 trades, +₹1,885 provisional per 100 shares. Shown only
as a reference; it is not part of this run's systems.

## Verdict rule

Per system, the best variant is judged on net + win% + frequency
together (uncapped and capped views both shown). Nothing is adopted
on October in-sample; November 2026 paper is the validation step.
If small targets lose after costs on a system, that is reported
with the cost drag shown, not hidden.
