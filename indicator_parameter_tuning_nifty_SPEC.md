# DIAL PARAMETER ATLAS — NIFTY · SPEC (frozen 2026-11-14, before scoring)

Owner's order 2026-11-14 15:43: tune the top indicators and their value parameters,
with entry and exit defined, including long term. Programme: DIAL (registry
`dial_programme.md`). Segment: Nifty only. STANDALONE research — signals from spot
candles; nothing running is changed. Buying only, 1 lot (65), ₹220/trade, paper
only, real money ₹0. This run does NOT touch or duplicate the separately running
DIAL-Nifty Round 2 (R-PE seed, `dial_nifty_r2_*`).

## DATA (identical stores to DIAL Round 1)
- Spot 5-min: `data/progressive/NIFTY/spot_5m.csv` (2025-01-01 → 2026-11-13, OHLC,
  no volume). All indicators computed on the CONTINUOUS series, warmed on 2025 bars;
  signals evaluated only inside the window in force.
- Session VWAP (EMA family only): near-month Nifty FUTURES session VWAP from
  `phase3_buildup_data/futures/FUT7_NIFTY_*` (7-field candles), cumulative
  Σ(typical×vol)/Σ(vol) within the session. The side test is BASIS-CONSISTENT —
  futures close vs futures VWAP at the signal bar (≡ spot close vs basis-adjusted
  VWAP), the corrected Round 1 fill. If no futures VWAP exists at the signal bar,
  the event does not qualify (scan continues that day).
- Premium candles: `oi_buildup_data/candles_NIFTY_{strike}{CE|PE}_{expiry}_{day}.json`
  (7-field). Strike = 50-grid strike nearest the SPOT CLOSE of the signal bar.
  Weekly expiry = smallest expiry in the stored expiry calendar ≥ the signal day.

## ENTRY (frozen, all families)
Signal on a COMPLETED 5-min bar's close; entry = OPEN of the next bar of the stored
premium candles. A signal is actionable only if its entry bar starts ≤ 15:15 (signal
bar ≤ 15:10). FIRST QUALIFYING signal per day per configuration: the scan passes
over events that fail a condition (VWAP side / ADX filter) and takes the first event
that satisfies everything. CE for up-signals, PE for down-signals — always BUYING.
A signal is SCORED only if the exact contract-day file exists AND its bars cover the
entry bar through the 15:20 bar contiguously; otherwise NC, counted per family with
reason (`nc_no_file` / `nc_partial` / `late`), never substituted with a neighbour
strike or another expiry. NC never silently shrinks a denominator: every family
card shows signals generated vs scored vs NC.

## INDICATOR FAMILIES + GRIDS (frozen)
All indicators on spot closes unless stated; EMA k = 2/(p+1), seeded at series start;
RSI/ATR/ADX = Wilder smoothing.
1. **EMA cross** — pairs (9,21), (13,34), (20,50). Event: fast EMA crosses slow EMA
   at bar close (up = CE, down = PE), qualifying only if price is on the cross side
   of session VWAP at the signal bar (basis-consistent test above).
2. **Supertrend** — period 7/10/14 × multiplier 2/3/4 (Wilder ATR, standard
   final-band ratchet, as Round 1). Event: direction flip at bar close.
3. **RSI momentum** — period 7/14/21. Event: RSI crosses through 50 (up = CE,
   down = PE).
4. **RSI reversion** — period 7/14/21 × band (25/75), (30/70), (35/65). Event:
   RSI exits the extreme zone turning back — RSI[t−1] ≤ lo and RSI[t] > lo = CE;
   RSI[t−1] ≥ hi and RSI[t] < hi = PE.
5. **MACD** — (8,21,5), (12,26,9), (19,39,9). Event: MACD line crosses its signal
   line at bar close (up = CE, down = PE).
6. **Bollinger breakout** — period 14/20/30 × sd 1.5/2/2.5 (SMA ± sd×sample σ,
   ddof=1). Event: close crosses beyond the band (above upper after ≤ upper = CE
   follow; below lower after ≥ lower = PE follow).
7. **Bollinger reversion** — same grid. Event: previous close beyond the band,
   current close back inside (was above upper, now ≤ upper = PE fade; was below
   lower, now ≥ lower = CE fade).
8. **Donchian breakout** — channel 10/20/55 bars, from the PRIOR N bars (current
   bar excluded). Event: fresh close beyond the channel — close[t] > max high of
   prior N with close[t−1] ≤ that channel = CE; mirror = PE.

## ADX FILTER DIMENSION (frozen)
ADX(14) Wilder on spot. Levels: none / 20 / 25 — a signal qualifies only if
ADX at the signal bar ≥ threshold. Applied ONLY to the trend families:
EMA, Supertrend, MACD, Donchian. (RSI and Bollinger families: no ADX dimension.)

## EXITS (frozen)
Level exits scan the contract's bars from the entry bar through the 15:15 bar:
a bar whose low ≤ stop exits AT the stop level; else a bar whose high ≥ target
exits AT the target level; if both levels fall inside one bar the STOP fills first.
If neither level is touched, square-off = OPEN of the 15:20 bar.
- E1: stop −40 / target +70. E2: stop −50 / target +90. E3: stop −60 / target +120.
- E4 (trend families only — EMA, Supertrend, MACD, Donchian): indicator-flip exit
  with −60 hard stop. Exit = OPEN of the bar following the first OPPOSITE-direction
  event bar of the same family+parameters (raw event, no VWAP/ADX condition) after
  the entry bar, if that event bar starts ≤ 15:15. The −60 hard stop is scanned on
  premium bars from the entry bar through the event bar inclusive; if touched, exit
  at the stop level (stop wins over the flip). If no opposite event by the 15:15
  bar, square-off = OPEN of the 15:20 bar.
Money: net = (exit − entry) × 65 − ₹220. Win iff net > 0.

## WINDOWS + ROBUSTNESS (frozen, anti-overfit)
Discovery = 2026-01-01 → 2026-06-30. Validation = 2026-07-01 → 2026-10-31.
November (Nov 2–13) is counterfactual-only, run AFTER freezing, never for selection.
A configuration is **ROBUST** iff ALL of:
1. Discovery total > 0 AND validation total > 0 (after costs).
2. ≥ 2 one-step neighbours also validation-positive. Neighbours: same family/mode,
   exactly one grid step in exactly one dimension — a numeric indicator parameter
   one step along its grid list, OR exit set one width step (E1↔E2↔E3; E4 has no
   exit neighbour), OR ADX one step (none↔20↔25) where the dimension exists.
3. Validation ex-top-3 > 0.
4. Validation random-entry placebo ≥ 95th percentile (1,000 iterations; same scored
   trade count, validation-window scorable contract-day universe, uniformly random
   feasible entry bars, same exit geometry; for E4 the placebo exits after the same
   number of bars as the positionally matched real trade, with the −60 hard stop
   and the 15:20 cap). Screening order: legs 1,2,3,5,6,7 first; placebos run only
   for screen survivors (if > 12 survive, triage at 300 iterations, then 1,000 for
   those ≥ 90th pct at triage).
5. Validation pace ≥ ₹7,500/mo (validation total / 4).
6. ≤ 1 red month within Jul–Oct.
7. Validation WR ≥ 60%.
A **family PASS** = ≥ 1 ROBUST configuration in the family. A family's parameter
card reports its best ROBUST configuration (highest validation total; ties →
higher validation WR) or **NONE ROBUST**. The single best raw row (highest
validation total across all 306 configurations) is listed separately, labelled
**NOT SELECTED** unless it is itself ROBUST. No cherry-picking: every
configuration's discovery/validation line is in the results JSON + heatmap CSV.
Configuration count (frozen): EMA 3×3 ADX×4 exits = 36 · Supertrend 9×3×4 = 108 ·
RSI-momentum 3×3 exits = 9 · RSI-reversion 9×3 = 27 · MACD 3×3×4 = 36 ·
Bollinger-breakout 9×3 = 27 · Bollinger-reversion 9×3 = 27 · Donchian 3×3×4 = 36 ·
**total 306**.

## LONG-TERM ANNEX (frozen — signal quality only, NOT options P&L)
Daily Nifty spot from `data/progressive/NIFTY/spot_daily.csv` (2025-01-01 →
2026-11-13). Events counted only for signal dates ≥ 2025-07-01 (uniform warm-up;
EMA200 is seeded at the 2025 start, so early values are approximations — stated,
not hidden). Signals (close-based events): EMA(20,50) cross · EMA(50,200) cross ·
RSI(14) cross through 50 · MACD(12,26,9) signal-line cross · Supertrend(10,3) flip.
For each event at day t (known at t's close): directed forward return =
direction × (close[t+k]/close[t] − 1) × 100% for k = 5, 10, 20 trading days;
events lacking t+k are excluded per horizon. Report per signal: event counts
(long/short), mean directed % and win-rate (share > 0) per horizon. Labelled
everywhere: **spot signal study — not a traded book, no costs, no options**.

## DELIVERABLES
`indicator_parameter_tuning_nifty_2026-11-14.md` (parameter card per family) ·
`indicator_parameter_tuning_nifty_results.json` (all 306 configurations) ·
`indicator_parameter_tuning_nifty_heatmap.csv` (one row per configuration).
