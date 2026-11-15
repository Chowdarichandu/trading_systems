# DIAL — one roof, one name (owner's order 2026-11-14 15:37)

The owner's tuning programme under a single name: **DIAL** (his radio rule — tune in small turns until the channel is found, then listen). The roof holds the standalone indicator system only. (The morning's repaired-books programme is a separate strategy named TRIO — see trio_strategy.md. Do not merge the two identities.) Segments are always reported separately, never pooled.

## Members

### 1. DIAL standalone indicator system (NEW — building 2026-11-14)
Standalone — NOT a filter on any existing book. Signals from spot candles only. Two frozen components, identical core in all three segments:
- **DIAL-T (trend):** Supertrend(7,3) flip on 5-min spot + price on the same side of session VWAP. First qualifying signal per day (per stock for stocks).
- **DIAL-R (reversion):** RSI(14) extreme + Bollinger %B extreme together, EMA50 slope not strongly against. First qualifying signal per day (per stock for stocks).
- Segments: Bank Nifty (options, buy only, 1 lot 30) · Nifty (options, buy only, 1 lot 65) · Stocks (equity cash, frozen 25 watchlist, per 100 shares provisional).
- Status: Jan–Oct gate runs launched 2026-11-14 (dial_bank / dial_nifty / dial_stocks). Nothing arms without a gate pass + forward evidence + the owner's word.

## Standing rules inside the roof
- Buying only (options). 1 lot. Paper only; real money ₹0 until the owner says otherwise.
- Every candidate: spec frozen before scoring; full gate in the same run (placebos, halves, ex-top-3, month table, dropped-set control where applicable); no number quoted before the gate.
- Tuning does not stop until the result is got (owner, 2026-11-14); a failed variant changes the dial, never ends the tuning — and never moves the pass bar.

## Round 1 verdicts (2026-11-14)
- **DIAL-Nifty: FAIL, all eight legs** — combined 205 trades −₹89,487.20, WR 36.6%, worse than random (11th pct). Seed found: DIAL-R put-side +₹32,513.50 vs long side −₹70,179.00 → **Round 2 (R-PE only) running.**
- **DIAL-Stocks: FAIL, both years, every leg** — combined 2025 −₹193,637.97 / 2026 −₹292,761.31 (per 100 shares provisional); November CF −₹20,466.44 vs Stock Book +₹7,517.94. Diagnosis: signals beat the random median in 5 of 6 series-years but ~27 trades/day churn in a +1.0%/−0.5% frame loses on any dose of it → **Round 2 (one most-extreme signal per component per day) running.**
- DIAL-Bank: Round 1 running at the time of this entry.

## Parameter Atlas (owner's order 2026-11-14 15:43)
Owner: tune the TOP INDICATORS and their VALUE PARAMETERS, with ENTRY and EXIT defined, even for long term. Launched 2026-11-14 for all three segments (specs indicator_parameter_tuning_{bank,nifty,stocks}_SPEC.md, frozen before scoring):
- Families: EMA cross, Supertrend, RSI (momentum + reversion modes), MACD, Bollinger (breakout + reversion modes), Donchian; ADX as a filter dimension. Exit sets tuned alongside entries.
- Anti-overfit law: Discovery Jan-Jun vs Validation Jul-Oct; a parameter set counts only as a ROBUST PLATEAU (>=2 one-step neighbours also validation-positive), never a lone best row; placebo >=95th on validation; November never used for selection.
- Long term included: daily-candle systems for stocks (EMA 50/100/200, golden cross, RSI, MACD, Supertrend, Bollinger reversion, ATR trailing exits) judged positive in BOTH years; daily spot signal annexes for Bank/Nifty (signal quality only, not options P&L).
- **DIAL-Nifty Round 2 (R-PE seed): FAIL 6 of 8 legs — SEED DEAD, DIAL-Nifty standalone core CLOSED.** The seed made +₹32,513.50 (46 trades) but its own +30-min shift made MORE (+₹34,264.90) — the moment is not the edge; WR 47.8%, ₹706.82/TD, pace ₹3,251/mo, placebo 93.9th pct. November CF −₹3,470. Indicator work on Nifty continues ONLY through the Parameter Atlas (owner's 15:43 order).
- **DIAL-Stocks Round 2 (frequency test): FAIL both years — frequency was NOT the poison.** At 1/16th the dose (414/410 trades) losses shrank ~93% but loss PER TRADE rose (−₹28.94→−₹33.15 in 2025; −₹43.44→−₹55.21 in 2026) and WR fell; the +1.0%/−0.5% frame loses per trade at any dose; November CF −₹2,210.27. **DIAL-Stocks standalone core CLOSED** — the segment's channel is TRIO's Stock Book. Stocks indicator work continues only via the Parameter Atlas (intraday with frequency discipline + daily long-term systems).
- **Parameter Atlas BANK: COMPLETE — ZERO robust rows in any family** (306 variants; 26 both-window-positive rows, all failed a frozen leg). One real structure, NOT SELECTED: Supertrend 7 x4 + ADX>=25 + flip-ride exit — +Rs37,579.70 discovery / +Rs29,791.50 validation, plateau 4/4, ex-top-3 barely positive, but WR 33.3% and pace Rs7,447.88/mo (misses by Rs208.50) — payoff-shaped, fails the owner's 60% WR standard. November CF +Rs1,459.50 (3 trades). RSI momentum/reversion, MACD, Bollinger reversion, Donchian: dead at every value (several flip sign between windows). **Long-term annex: daily EMA(20,50) cross = +0.816% average over next 20 days, 58.3% win, 36 events (2019-2026 spot)** — the one measurable long-term Bank signal; EMA(50,200) thin second (8 events).
