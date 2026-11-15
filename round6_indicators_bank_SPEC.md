# ROUND 6 — INDICATOR TUNING, BANK NIFTY · SPEC (FROZEN BEFORE SCORING)

Frozen: 2026-11-14 10:07 IST (system clock at freeze). No grid point, threshold, or
definition below may be altered after any scoring output exists. Research only —
no book, ledger, or job is changed by this run.

Owner order: 2026-11-14 15:35 IST, "work on new with indicators" (voice note;
build proceeded under the standing tuning orders). Buying only, 1 lot, Bank only.

## Subject and control
TUNED STACK v2 legs from the gated stores (`november_books_fix_anatomy_legs.csv`
BANK_STACK rows joined exactly as Phase 2). Control MUST reproduce before any
scoring: 111 legs · +₹127,351.50 · WR 59.5% · 89 trade-days · ₹1,430.92/TD ·
60G/29R/116NT of 205 · H1 +₹83,082.00 / H2 +₹44,269.50 · ex-top-3 +₹100,528.50 ·
zero red months · independent re-sum vs the solid60 store. Failure = stop.

## Verification of the premise (indicator state never used on this book)
Checked before freezing: `november_paper_MAP.md` (book construction notes),
`bank_tuned_stack_live_score.py` + `november_shadow_score.py` (the scoring path),
`daily2leg/*.py` (member signal code), `DOCUMENTED_V5_LA_BANKNIFTY.md`, and the
day-trader skill doc. NONE of RSI, ADX, Bollinger, VWAP, EMA or ATR appears as an
entry rule anywhere in the stack's construction. Member families are: Skill V3
(opening-range / prior-day structure), V5 v2 (pooled V4+Skill structure signals),
(lA) v2 (range-break confirmer), Volrix (b) (prior-day % change), NS1 second legs,
NS3 gap-class legs, S3-R1 / S3-PDC, EVE06 re-entries. **No member family IS one of
the six indicators' rule, so no self-conditioning exclusion applies** — stated as
required; if scoring later reveals a family whose rule is one of these in
substance, its legs are flagged in the report, not silently kept.

## Data and knowability audit (per indicator)
- Spot 5-min bars: `daily2leg/spot.json` BANKNIFTY — 205/205 Jan–Oct days × 75
  bars [time, O, H, L, C]. November: `data/banknifty-2026-11/spot_5m.csv`
  (75 bars on each of Nov 4/9/12/13). This is the persisted spot store the gated
  runs used.
- Futures 5-min bars (VWAP only): `round5_history/FUT7_<in-force expiry>.json`,
  rows [date, time, O, H, L, C, volume, OI]; the persisted spot store carries NO
  volume, so VWAP is the in-force FUTURES contract's VWAP and the distance is
  futures close vs futures VWAP (internally consistent; stated wherever used).
- ENTRY-KNOWABILITY: every indicator at a leg uses ONLY bars with bar-start
  time < the leg's entry_time (the entry premium is the open of the entry bar,
  so the last completed bar is the one ending at entry_time). RSI/EMA/ADX/
  Bollinger/ATR run on the CONTINUOUS series across consecutive trading days
  (standard platform behaviour; prior days from the same spot store, which
  extends through 2025 for warm-up). VWAP is intraday-only by definition
  (session reset), futures bars of the same day before entry.
- NC: a leg whose needed state cannot be computed (missing day/bars) is NC,
  is KEPT by that conditioner (a dial that cannot judge does not idle — the
  Phase-3B convention), is counted per indicator, and is never filled/estimated.

## Indicator state at entry (definitions frozen)
- RSI(14): Wilder, closes, continuous series.
- VWAP state: futures cumulative VWAP from 09:15 to the last completed bar;
  dist% = (futures close − VWAP)/VWAP × 100; side = sign of dist%.
- EMA trend: EMA50 (closes, continuous); price-side = close vs EMA50;
  EMA20 slope sign = EMA20(last completed) − EMA20(5 bars earlier).
- ADX(14): Wilder, continuous series.
- Bollinger %B: 20-period SMA ± 2σ on closes (continuous); %B = (C−lower)/(upper−lower).
- ATR%: ATR(14) Wilder / last close × 100. Tercile cuts are computed on the
  Jan–Oct leg-entry ATR% values and printed in the results (same-window
  descriptive statistic, same status as Phase 2's frozen ₹692.50 median premium:
  Jan–Oct is the tuning window, so a PASS is a tuning result, not forward proof).

## The grid (15 points, frozen; CE = call legs, PE = put legs)
Singles:
1. RSI-ALIGN — keep CE if RSI ≥ 50; keep PE if RSI < 50.
2. RSI-BAND — drop CE if RSI ≥ 70; drop PE if RSI ≤ 30; keep all else.
3. VWAP-ALIGN — keep CE if futures close > VWAP; keep PE if below.
4. EMA50-SIDE — keep CE if close > EMA50; keep PE if close < EMA50.
5. EMA-ALIGN — keep CE if close > EMA50 AND EMA20 slope > 0;
   keep PE if close < EMA50 AND slope < 0; drop all else.
6. ADX20 — keep legs with ADX ≥ 20 (both sides).
7. ADX25 — keep legs with ADX ≥ 25 (both sides).
8. BB-ALIGN — keep CE if %B ≥ 0.5; keep PE if %B < 0.5.
9. BB-BAND — drop CE if %B ≥ 1.0; drop PE if %B ≤ 0.0; keep all else.
10. ATR-LOW — keep legs whose ATR% is in the lowest tercile.
11. ATR-HIGH — keep legs whose ATR% is in the highest tercile.
12. ATR-MIDHIGH — keep legs NOT in the lowest tercile (second honest volume-of-
    volatility reading: avoid only the deadest tape).
Pairs (only these):
13. P1-EMA+ADX — EMA-ALIGN AND ADX ≥ 20.
14. P2-VWAP+RSIBAND — VWAP-ALIGN AND RSI-BAND.
15. P3-EMA+VWAP — EMA50-SIDE AND VWAP-ALIGN.

## Scoring and controls (identical conventions to Phases 2/3)
Per point: kept legs, total, WR, ₹/trade-day, G/R/NT days of 205, full month
table, halves (H1 = Jan–May, H2 = Jun–Oct), ex-top-3.
Controls per point: (a) 200 random same-size subsets of the 111 legs
(seed 20261114) — kept total must sit at ≥ the 95th percentile; (b) dropped-set
control — kept total must exceed the dropped legs' total.
November CF: the stack's 4 actual November legs (Nov 4 +₹2,480 · Nov 9 −₹1,720 ·
Nov 12 −₹1,720 · Nov 13 −₹1,720) per point — kept/idled and the filtered total.
Descriptive only; November sets no rule.

## Pass bar (unmoved)
WR ≥ 60% AND ₹/TD ≥ ₹900 AND total ≥ 60% of +₹127,351.50 (₹76,410.90) AND both
halves positive AND ex-top-3 positive AND placebo ≥ 95th pct AND dropped-set
beaten AND no red month. Any leg failed = FAIL for that point, failing leg named.

Deliverables: round6_indicators_bank_2026-11-14.md + round6_indicators_bank_results.json.
