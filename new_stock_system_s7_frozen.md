# S7 — Intraday STOCK system (cash, NOT options) — FROZEN before scoring

**Status: FROZEN 2026-10-30, NOT adopted, NOT a live system. Paper only, no orders.**
**Window for any run below: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks.**
Any Jan–Oct 2026 run of S7 is **in-sample context only**. If S7 passes in-sample,
its real test is November 2026 paper starting Mon 2026-11-02, logged daily
after 15:10 in `s7_forward_paper_log.csv`, separate from the Nifty Cluster 2/3
log and separate from any stock log, with no re-tuning during November.
Adoption only on net + win rate + frequency together on unseen paper.
If S7 fails in-sample, it is NOT re-tuned on the same window and re-claimed.

## Why S7 exists — the S6 finding, two layers

S6 fixed CE stop asymmetry (retest-hold stop) and CE trades appeared
(7 trades vs 0 in S2), but the CE leg lost −₹2,980 with 0 full targets.
The remaining layer is reclaim-chasing: entering at the open after a
reclaim close gets noise-stopped on any normal pullback, because the
stop (just below the reclaim candles) is close to a price that has
already run up to reclaim. S7 therefore does not enter on the reclaim
itself at all. It waits for the market to come back to the reclaimed
level and prove it holds, then enters.

## S7 rules (exact, frozen)

- Universe: same 25 stocks. Nifty is a confirmation filter only, never
  traded, never pooled into a stock total. Index paper is separate.
- OR filter (unchanged): OR width / prev close in [0.25%, 3.0%], else
  no-trade. OR = 09:15–09:30 candles (time < "09:30").
- Bias (unchanged, stock's own day): bearish → PE only, bullish → CE
  only, neutral → both. Bands: bearish <35%, neutral 35–79%,
  bullish ≥80% from previous close position in its daily range.
- Nifty confirmation (unchanged from S2/S6): bias-only — allow CE on
  bullish/neutral Nifty days, PE on bearish/neutral Nifty days, block
  only the directly opposed direction.
- Costs/size (unchanged): 100 shares, ₹40/trade, square-off 15:10,
  short paper-only. Give-back exit (unchanged): at 1.0× risk book
  50 shares; remaining 50 stop trails to breakeven (entry); remaining
  target stays 2× risk; square-off 15:10; bar order stop, then
  partial, then target. Win (primary) = net > 0; full-target rate
  reported alongside — partial-BE wins are NOT full targets.
- Valuable filter (unchanged): prospective full-target net =
  2 × risk × 100 − ₹40 must be ≥ ₹500.
- Cap (unchanged from S6, user bar): max 1 valuable stock trade per
  trading day across all 25 stocks, max 1 trade per stock per week
  retained. Ranking: prospective target net DESC, then room ratio
  DESC, then setup rank DESC, then date, then symbol. Cap is a
  ceiling, NOT a quota: a day with no candidate passing every filter
  trades nothing, reported as a no-valuable-setup day.

### CE leg — setup4 pullback ONLY (the S7 change)

No direct reclaim CE trade and no setup2 OR-breakout CE trade in S7.
Both are the same reclaim-chasing entry (open after a breakout/
reclaim close) that S6 showed gets noise-stopped, so both are
excluded. The only CE trade in S7 is:

1. **Arming (reclaim close).** First candle at or after 09:30, at or
   before 14:30, satisfying ALL of: day open < PDC, close > OR high,
   close > PDC, close < PDH, and room from close to the next PD
   level above ≥ 200 × scale (scale = prev close / 55000, the same
   scaling used in find_signal). CE must be allowed by the stock's
   own bias. This candle arms the day; it is NOT an entry.
2. **Pullback candle.** A later candle (index > arming index, time
   ≤ 14:30) satisfying ALL of: |low − OR high| ≤ 40 × scale (the
   existing 40×scale tolerance, here applied to the reclaimed
   level, OR high), close > OR high, and close > open (green close
   back above the level). This is the dip toward the reclaimed
   level and the close back above it.
3. **Second close (on the pullback candle).** The candle immediately
   after the pullback candle must close further in direction than
   the pullback close: confirmation close > pullback close. If not,
   no trade that day for that stock (no rescan for another
   pullback, no re-entry — the first pullback candidate is the
   only CE candidate that day).
4. **Entry / stop / room / target.** Entry = open of the candle
   after the confirmation candle. Stop = pullback candle low.
   Risk = entry − stop; invalid if risk ≤ 0. Room = distance from
   entry to the next PD level (PDH/PDC/PDL) above entry; must be
   finite AND ≥ 1.5 × risk. Target = entry + 2 × risk.
   Nifty bias-only and prospective ≥₹500 filters then apply as
   above, and the give-back replay runs from the entry candle.

### PE leg — unchanged from S6

PE trades use the S6 path exactly: base signal from find_signal
restricted to PE directions (setup2 OR breakdown, setup3 bounce
rejection), second-close confirmation (confirmation close <
signal close), entry = open of the candle after confirmation,
stop = max(signal high, confirmation high) (S6 retest-hold stop),
risk = stop − entry, room to the next PD level below entry finite
AND ≥ 1.5 × risk, target = entry − 2 × risk, Nifty bias-only,
prospective ≥₹500, give-back replay as above.

### One candidate per stock-day

A stock-day may produce both a PE candidate and a CE pullback
candidate. At most one candidate per stock-day is carried into
the cap: the candidate whose entry candle is earliest; if entry
times tie, the higher prospective target net wins. Entry time is
a signal-time quantity, never a realised outcome, so this choice
cannot cherry-pick winners.

### What S7 deliberately does NOT change

Give-back exit, target 2× risk, room threshold 1.5×, Nifty
bias-only confirmation, prospective ≥₹500, costs, square-off,
OR filter, second-close concept. No timing gates, no bounce-bar
stops, no target-shrink to tiny wins, no re-entry, no second
trade of the same stock on the same day, no loosening of room
to rescue setup2 — if setup2 yields zero candidates, it is
reported as absent, not rescued.

## Engine

`stock_system_s7.py` (`run_s7` / `cap_select_daily` / `summarise_s7`).
Trade CSV: `s7_trades_jan_oct_2026.csv`, uncapped
`s7_uncapped_jan_oct_2026.csv`, month JSON
`data/progressive/s7_summary_2026-jan-oct.json`.
Forward log template (only if S7 passes in-sample):
`s7_forward_paper_log.csv`.
