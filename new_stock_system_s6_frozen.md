# S6 — Intraday STOCK system (cash, NOT options) — FROZEN before scoring

**Status: FROZEN 2026-10-29, NOT adopted, NOT a live system. Paper only, no orders.**
**Window for any run below: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks.**
Any Jan–Oct 2026 run of S6 is **in-sample context only**. S6's real test, if it
passes in-sample, is November 2026 paper starting Mon 2026-11-02, logged daily
after 15:10 in `s6_forward_paper_log.csv`, separate from the Nifty Cluster 2/3 log,
with no re-tuning during November. Adoption only on net + win rate + frequency
together on unseen paper. If S6 fails in-sample, it is NOT re-tuned on the same
window and re-claimed; the next design (S7) is frozen after this report.

## Why S6 exists — the CE structural problem (S1–S5 finding)

S1–S5 all used the same structural stop: CE stop = OR low − 0.1% of prev close,
PE stop = OR high + 0.1%. That stop is direction-asymmetric in practice:

- A CE reclaim / OR-breakout trade enters near the OR high, so its structural
  risk is ≈ the whole OR width (0.25–3.0% of price).
- A setup3 PE bounce trade enters near the OR high, so its structural risk is
  tiny (entry is already at the stop level).

The room filter (room to the next PD level ≥ 1.25–1.5× risk) therefore
systematically favours PE bounces and systematically filters out CE trades,
however good the CE direction was. Result across S2–S5: S2 had 0 CE trades out
of 61; S3–S5 had 1 CE trade each. Loosening room only admitted more PE trades.
That is a design flaw in the stop definition, not a filter-tuning problem, so
S6 changes the stop definition itself. This is the one structural change in S6;
it is not a re-use of any dead Nifty-sweep trick (no timing gates, no OR-high
stop as a standalone rule, no bounce-bar stops, no target-shrink).

## S6 rules (exact, frozen)

- Universe: same 25 stocks. Nifty is a confirmation filter only, never traded,
  never pooled into a stock total. Index paper (Nifty (lA) / Bank V4) is separate.
- Base signal: old V4 `find_signal` (setups 2/3/4 only; Setup 1 skipped, no Red
  bands) + bias filter as old (bearish → PE only, bullish → CE only, neutral → both).
- OR filter: OR width / prev close in [0.25%, 3.0%], else no-trade.
- Confirmation (second close, unchanged): candle after signal must close further
  in direction than signal close (CE: conf > sig close; PE: conf < sig close).
  Entry = open of the next candle after confirmation. No rescan, no re-entry
  that day for that stock.
- **STOP — NEW, direction-symmetric retest-hold stop (the S6 change):**
  - CE: stop = min(signal candle low, confirmation candle low).
  - PE: stop = max(signal candle high, confirmation candle high).
  - Risk = |entry − stop|; invalid if risk ≤ 0.
  - Rationale: this is the level whose breach invalidates the signal under the
    original Filter 4 (Retest Hold Confirmation) — a CE reclaim fails if price
    trades back below the signal/confirmation lows; a PE rejection fails if price
    trades back above the signal/confirmation highs. It makes CE risk comparable
    to PE risk (both are one signal-formation wide, not OR-width wide), instead
    of penalising CE trades for entering near the OR high. It is NOT the old
    signal-candle-only stop from the original cash `run_day` (which used the
    signal candle alone and no confirmation candle), and it is NOT the
    OR-boundary stop used in S1–S5.
- Target: entry ± 2 × risk (unchanged). Give-back exit (unchanged): at 1.0 × risk
  book 50 shares; remaining 50 stop trails to breakeven (entry); remaining target
  stays 2 × risk; square-off 15:10; bar order stop, then partial, then target.
- Room (unchanged threshold, recomputed on the NEW risk): room to the next PD
  level (PDH/PDC/PDL) in direction must be finite AND ≥ 1.5 × risk. Infinite
  room (no PD level beyond entry) fails. Target is NOT shrunk to room.
- Nifty confirmation (unchanged from S2): bias-only — allow CE on bullish/neutral
  Nifty days, PE on bearish/neutral Nifty days, block only the directly opposed
  direction (CE on bearish, PE on bullish); bands bearish <35%, neutral 35–79%,
  bullish ≥80% from previous close position in its range.
- **Valuable filter (unchanged threshold, now the daily bar):** prospective
  full-target net = 2 × risk × 100 − ₹40 must be ≥ ₹500. A setup that cannot
  prospectively make ₹500 net is not valuable and never trades, however many
  signals that day produce.
- **Cap — CHANGED to fit the user bar (1 valuable stock trade per day):**
  max **1 stock trade per trading day** across all 25 stocks, max 1 trade per
  stock per week retained. Ranking: prospective target net DESC, then room
  ratio DESC, then setup rank DESC, then date, then symbol. This cap is a
  ceiling, NOT a quota: a day with no candidate passing every filter above
  trades nothing that day, and that day is reported as a no-valuable-setup day.
- Costs/size: 100 shares, ₹40/trade, square-off 15:10, short paper-only.
  Win (primary) = net > 0; full-target rate reported alongside — partial-BE
  wins (partial 50 at 1× risk, rest stopped at breakeven) are NOT full targets
  and are shown separately, never counted as targets.

## What S6 deliberately does NOT change

Second-close confirmation, give-back exit, target 2× risk, room threshold 1.5×,
Nifty bias-only confirmation, prospective ≥₹500, costs, square-off time, setups
2/3/4 only. No timing gates, no bounce-bar stops, no target-shrink to tiny wins,
no re-entry, no second trade of the same stock on the same day.

## Engine

`stock_system_s6.py` (`run_s6` / `cap_select_daily` / `summarise_s6`).
Trade CSV: `s6_trades_jan_oct_2026.csv`, uncapped `s6_uncapped_jan_oct_2026.csv`,
month JSON `data/progressive/s6_summary_2026-jan-oct.json`.
Forward log template (only if S6 passes in-sample): `s6_forward_paper_log.csv`.
