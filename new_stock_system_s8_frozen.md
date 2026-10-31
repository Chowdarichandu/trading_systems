# S8 — Intraday STOCK system (cash, NOT options) — FROZEN before scoring

**Status: FROZEN 2026-10-30, NOT adopted, NOT a live system. Paper only, no orders.**
**Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks, 203 trading days.**
Any Jan–Oct 2026 run of S8 is **in-sample context only**. If S8 passes ALL
legs in-sample, its real test is November 2026 paper starting Mon
2026-11-02, logged daily after 15:10 in `s8_forward_paper_log.csv`,
separate from the Nifty log, with no re-tuning during November.
Adoption only on net + win rate + frequency together on unseen paper.
If S8 fails any leg in-sample, it is NOT re-tuned on the same window
and re-claimed, and no adoption-track November log is created.

## Why S8 exists — the S7 finding

S7 was the first stock version net positive in-sample (+₹722.50, 51
trades, +₹14.17/trade, per 100 shares provisional — NOT a lot
profit), and its CE pullback leg reversed S6's CE leg (5 trades,
+₹1,590, 40% full targets vs S6 CE 7 trades, −₹2,980, 0 full
targets). But S7 failed the user bar: only 0.25 trades/day, 150 of
203 days with no valuable setup, only 2 days lost to the cap, and
setup2 absent even uncapped. Frequency, not edge per trade, is now
binding, and loosening room has failed in every direction tried
(S2–S6). S8 therefore ADDS valuable setups without touching room,
stop, or target.

## S8 rules (exact, frozen) — S7 except the ONE change below

- Universe: same 25 stocks. Nifty is a confirmation filter only,
  never traded, never pooled into a stock total. Index paper is
  separate. Cash intraday only, no options.
- OR filter (unchanged): OR width / prev close in [0.25%, 3.0%],
  else no-trade. OR = 09:15–09:30 candles (time < "09:30").
- Bias (unchanged, stock's own day): bearish → PE only, bullish →
  CE only, neutral → both. Bands: bearish <35%, neutral 35–79%,
  bullish ≥80% from previous close position in its daily range.
- Nifty confirmation (unchanged from S2/S6/S7): bias-only — allow
  CE on bullish/neutral Nifty days, PE on bearish/neutral Nifty
  days, block only the directly opposed direction.
- Costs/size (unchanged, PROVISIONAL label): 100 shares per trade,
  ₹40/trade assumed cost, square-off 15:10, short paper-only.
  All rupee totals in S8 are "per 100 shares, provisional — NOT a
  lot profit". Give-back exit (unchanged): at 1.0× risk book 50
  shares; remaining 50 stop trails to breakeven (entry); remaining
  target stays 2× risk; square-off 15:10; bar order stop, then
  partial, then target. Win (primary) = net > 0; full-target rate
  reported alongside — partial-BE wins are NOT full targets.
- Valuable filter (unchanged): prospective full-target net =
  2 × risk × 100 − ₹40 must be ≥ ₹500.
- Cap (unchanged from S6/S7, user bar): max 1 valuable stock
  trade per trading day across all 25 stocks, max 1 trade per
  stock per week retained. Ranking: prospective target net DESC,
  then room ratio DESC, then setup rank DESC, then date, then
  symbol. Cap is a ceiling, NOT a quota: a day with no candidate
  passing every filter trades nothing, reported as a
  no-valuable-setup day.
- One candidate per stock-day (unchanged): earliest entry, tie →
  higher prospective target net. Entry time is a signal-time
  quantity, never a realised outcome.

### THE S8 CHANGE — CE pullback arming widened (only change)

S7 armed a CE pullback day ONLY when day open < PDC (a gap-down
day). S8 arms on ANY reclaim close above OR high, regardless of
day open vs PDC. Everything else in the CE path is identical:

1. **Arming (reclaim close).** First candle at or after 09:30, at
   or before 14:30, satisfying ALL of: close > OR high, close >
   PDC, close < PDH, and room from close to the next PD level
   above ≥ 200 × scale (scale = prev close / 55000). Day open
   vs PDC is NOT a condition in S8. CE must be allowed by the
   stock's own bias. This candle arms the day; it is NOT an entry.
2. **Pullback candle.** A later candle (index > arming index, time
   ≤ 14:30) satisfying ALL of: |low − OR high| ≤ 40 × scale,
   close > OR high, and close > open (green close back above the
   level). First such candle only.
3. **Second close (on the pullback candle).** The candle
   immediately after the pullback candle must close further in
   direction than the pullback close: confirmation close >
   pullback close. If not, no CE trade that day for that stock
   (no rescan for another pullback, no re-entry).
4. **Entry / stop / room / target.** Entry = open of the candle
   after the confirmation candle. Stop = pullback candle low.
   Risk = entry − stop; invalid if risk ≤ 0. Room = distance
   from entry to the next PD level (PDH/PDC/PDL) above entry;
   must be finite AND ≥ 1.5 × risk (UNCHANGED — not loosened).
   Target = entry + 2 × risk. Nifty bias-only and prospective
   ≥₹500 filters then apply, and the give-back replay runs from
   the entry candle.

### PE leg — unchanged from S6/S7

PE trades use the S7 path exactly: base signal from find_signal
restricted to PE directions (setup2 OR breakdown, setup3 bounce
rejection), second-close confirmation (confirmation close <
signal close), entry = open of the candle after confirmation,
stop = max(signal high, confirmation high) (retest-hold stop),
risk = stop − entry, room to the next PD level below entry
finite AND ≥ 1.5 × risk, target = entry − 2 × risk, Nifty
bias-only, prospective ≥₹500, give-back replay as above.

### Setup2 diagnosis — reported, NOT designed around by loosening

Setup2 was 0 even uncapped in S6 and S7. Before any setup2 design
change, S8 reports a raw-signal diagnosis over the same window
(see `setup2_diagnosis_jan_oct_2026.json`): per stock-day, whether
a setup2 close-cross existed at all, whether the OR-width cap
(≤360×scale) blocked it, whether room (≥200×scale) blocked it,
whether the previous-close resistance condition blocked a CE
cross, whether bias blocked it, and whether find_signal returned
an earlier setup (setup4 reclaim/pullback or setup3) on an earlier
candle that day — i.e. precedence masking. Room is NOT loosened
below 1.5×, and setup2 CE breakout is NOT re-introduced, as a
frequency fix in S8.

### What S8 deliberately does NOT change

Give-back exit, target 2× risk, room threshold 1.5×, Nifty
bias-only confirmation, prospective ≥₹500, costs, square-off,
OR filter, second-close concept, pullback tolerance 40×scale,
arming room 200×scale. No direct reclaim CE, no setup2 CE
breakout, no timing gates, no bounce-bar stops, no target-shrink
to tiny wins, no re-entry, no second trade of the same stock on
the same day.

## Engine and outputs

`stock_system_s8.py` (`run_s8` / `cap_select_daily` / `summarise`),
adapted from `stock_system_s7.py` with the arming condition changed
and the CE funnel counters wired (armed / pullback / second-close /
candidate). Trade CSV: `s8_trades_jan_oct_2026.csv`, uncapped
`s8_uncapped_jan_oct_2026.csv`, month JSON
`data/progressive/s8_summary_2026-jan-oct.json`, diagnosis
`setup2_diagnosis_jan_oct_2026.json`.
Forward log template (only if S8 passes ALL legs in-sample):
`s8_forward_paper_log.csv` (header only).
