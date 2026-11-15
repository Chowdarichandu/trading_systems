# DIAL — NIFTY · ROUND 2: THE R-PE SEED · SPEC (frozen 2026-11-14, before scoring)

Programme: DIAL (registry `dial_programme.md`). Segment: Nifty only. Research only:
no existing book, ledger, or job is changed; Round 1 artifacts are read-only inputs.
Buying only (puts), 1 lot (65), paper only, real money ₹0.

## Why this run exists
In DIAL Round 1 (`dial_nifty_2026-11-14.md`, gate FAIL on all eight legs), DIAL-R's
two sides split: the LONG-reversion side (buy CE at RSI ≤ 30) lost −₹70,179.00 while
the SHORT-reversion side (buy PE at RSI ≥ 70) made **+₹32,513.50**. Round 1 recorded
that split as an observation only — a hypothesis seed, not a finding. This run tests
that side ALONE, frozen fresh, under the owner's standing order (tuning does not stop
until the result is got; each failure rolls into the next tune from its diagnosis).
If the seed fails this gate, the seed is dead and DIAL-Nifty closes.

## THE SEED (the only change from Round 1)
The seed book = the put-buying subset of Round 1's computed DIAL-R signal set:
signals with direction −1 (SHORT-reversion → buy PE). LONG-reversion signals are
NOT taken. Everything else is IDENTICAL to Round 1 (`dial_nifty_SPEC.md` + the
basis-consistent VWAP fill correction, which affects DIAL-T only):
- Signal: at a COMPLETED 5-min bar's close, RSI(14) ≥ 70 AND Bollinger %B ≥ 0.95
  AND EMA50 slope over the last 6 bars < +0.1% (%), all on the continuous spot
  series exactly as computed in Round 1 (Wilder RSI; Bollinger 20-bar SMA ± 2σ,
  σ = sample stdev ddof=1, %B := 0.5 if upper == lower; EMA50 k = 2/51 seeded at
  series start; warmed up on the 2025 bars in the same store).
- First-R-signal-of-the-day logic UNCHANGED: Round 1's generator stops at the
  first R signal of a day of either side. A day whose first R signal was LONG
  contributes NO seed trade (its later bars were never in Round 1's set). The seed
  is a subset of the computed set, not a re-generation with different logic.
- Entry: next bar after the signal bar; actionable only if the entry bar starts
  ≤ 15:15. Strike = 50-grid strike nearest the spot close of the signal bar.
  Weekly expiry = smallest expiry in the stored expiry calendar ≥ the signal day.
- Fill: entry premium = open of the entry bar in the stored premium candles
  (`oi_buildup_data/candles_NIFTY_{strike}PE_{expiry}_{day}.json`, 7-field). A
  signal is SCORED only if that exact file exists AND its bars cover the entry
  bar through the 15:20 bar contiguously; otherwise NC (counted, never
  substituted).
- Exits: scan from the entry bar (included) through the 15:15 bar — a bar whose
  low ≤ entry − 50 exits AT entry − 50 (stop); else a bar whose high ≥ entry + 90
  exits AT entry + 90 (target); if both levels fall inside one bar the STOP fills
  first. If neither is touched, square-off = OPEN of the 15:20 bar.
- Money: net = (exit − entry) × 65 − ₹220. Win iff net > 0.

## CONTROL (before any gating)
The full Round 1 set is regenerated with Round 1's own code path and must
reproduce the published figures EXACTLY before the seed is gated:
combined 205 trades / −₹89,487.20 · T 112 / −₹51,821.70 · R 93 / −₹37,665.50 ·
R-CE 47 / −₹70,179.00 · **R-PE 46 / +₹32,513.50, 22 wins (WR 47.8%)**.
Any mismatch stops the run and is reported instead of a gate verdict.

## METRICS (seed book alone)
- Trade-day = a day with ≥ 1 scored seed trade. ₹/trade-day = seed total / seed
  trade-days. Monthly pace = seed Jan–Oct total / 10.
- Halves: H1 = trades dated before 2026-06-01; H2 = on/after.
- Ex-top-3 = seed total − the 3 largest seed trade nets.
- Red month = a calendar month (Jan–Oct) whose seed net < 0 (a month with no
  seed trades nets ₹0 and is not red).
- Timing audit: for every scored seed trade, entry bar timestamp = signal bar
  timestamp + 5 min AND entry premium = the stored open of the entry bar.

## GATE (same run, frozen)
1. RANDOM-ENTRY PLACEBO: 1,000 iterations (RNG seed 20261114, programme
   convention). Each iteration rebuilds a book of the same seed trade count;
   each trade is drawn as a uniformly random file from the PE-ONLY scorable
   universe (stored PE contract-day files with day in Jan–Oct 2026 having ≥ 1
   feasible entry bar — an entry bar whose stored bars cover it through 15:20
   contiguously, entry start ≤ 15:15), with a uniformly random feasible entry
   bar in it; same exits and cost (this is the same PE-buying geometry).
   Percentile = share of placebo totals ≤ the seed total. Bar: ≥ 0.95.
2. +30-MIN SHIFT PLACEBO: every scored seed entry moved 6 bars later the same
   day, same contract; trades whose shifted entry bar does not exist, starts
   after 15:15, or loses contiguous coverage are dropped (counted). The seed
   total must EXCEED the shifted book's total.
3. Halves both positive.
4. Ex-top-3 positive.
5. ₹/trade-day ≥ 900.
6. WR ≥ 60%.
7. Monthly pace ≥ ₹7,500.
8. Red months ≤ 2.
PASS = all eight legs. Failing legs are named. No leg is moved, waived or
re-weighted after scoring.

## NOVEMBER CF (descriptive, not gated)
The identical frozen seed over 2026-11-02 → 2026-11-13: report the FULL seed
signal set (every SHORT-reversion signal, scored or NC, with the NC reason;
Round 1's scored R Nov 4 PE 23850 −₹3,470.00 is one member) and the seed's
November net.

## Deliverables
`dial_nifty_r2_2026-11-14.md` + `dial_nifty_r2_results.json` (+ seed trades CSV).
