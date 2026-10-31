# Stocks EQUITY — LINE U1 FREEZE — 11:00 Fade, broad universe, last 60 trading days

**FROZEN 2026-10-31, before any U1 data was fetched or scored.
Paper only, no orders. Real money: ₹0. This is a breadth /
robustness read of an already-frozen rule — NOT a tuning run.
No parameter of the rule may change anywhere in this line.**

**EQUITY CASH intraday only. LONG/SHORT language only — no
options, no premiums. Every rupee figure: provisional per 100
shares, ₹40/trade flat cost.**

## Why this line exists

The user asked (2026-10-31): run the frozen 11:00 fade on ALL
stocks — not only his 25, not only the 25 large caps — for the
last 60 days. U1 answers exactly that: does the candidate rule
(`stocks_O2_candidate_spec.md`) survive contact with the whole
market over the most recent 60 trading days?

## The rule — VERBATIM from the frozen candidate (engine-faithful)

Machinery: Line O1's fixed-mode builder (`stocks_O1.build_cell`)
over the shared exit engine (`stocks_tuning_universe.replay_plain`)
and the shared measurement (`stocks_tuning_mover.premove`) — the
identical code path that produced the O2 candidate's anchors.

1. **Candles:** the day's 5-min bars with time ≥ 09:30, in time
   order (the DAYCTX convention of every prior line).
2. **Measurement (11:00):** pre-move = (close of the last bar
   with time < 11:00) / (open of the first bar ≥ 09:30) − 1.
3. **Qualification:** |pre-move| ≥ **1.0%** on that stock-day.
4. **Direction: FADE** — pre-move positive → **SHORT**;
   pre-move negative → **LONG**.
5. **Entry:** the open of the first bar with time ≥ 11:00 (the
   11:00 bar's open — strictly after the measurement completes).
   **One trade per qualifying stock-day.** No re-entry, no
   signal confirmation, no context filter (all days).
6. **Exits:** target **+1.25%** / stop **−0.65%** from entry
   (mirrored for SHORT), stop checked before target within a
   bar; if neither is touched, exit at the close of the 15:10
   bar (or the last bar at or before 15:10).
7. **Net per trade** = sign × (exit − entry) × 100 shares
   − **₹40** flat cost.

## Universe — declared before the build

- **Target:** the **Nifty 500** constituent list as published by
  NSE (the "Download List of Nifty 500 Stocks (.csv)" file
  linked from NSE's Nifty 500 index page), retrieved
  2026-10-31. Instrument key per name = `NSE_EQ|<ISIN Code>`
  from that same CSV.
- **Achieved universe** = target names whose instrument returns
  at least one usable day of 5-min data inside the window
  (a usable day = bars present from 09:15 through 15:10, so the
  09:30+ candle list and the 15:10 square-off both exist).
- Every target name not in the achieved universe is **dropped
  and counted**, with the reason class recorded (no data /
  fetch error / partial data only). The report's first line
  states target vs achieved. No silent shrinkage.
- If the Nifty 500 build cannot be completed in full, the
  fallback declared here is: **complete Nifty 200 fully rather
  than 500 partially**, and say so in the report's first line.

## Window — declared before the build

- **The last 60 trading days ending Fri 2026-10-30.**
- Fetch span: 2026-08-01 → 2026-10-30 (5-min bars, Upstox v3
  historical-candle, the same endpoint family as all prior
  lines), then the window is the last 60 dates ≤ 2026-10-30 on
  which at least half of the achieved universe has a usable
  day. The exact start date is whatever those 60 days give;
  it is stated in the report.
- Days inside the window on which an individual stock has no
  usable day are simply absent for that stock (suspension /
  holiday / listing mid-window) — never zero-filled.

## Controls — same run, mandatory

1. **Timing audit:** the builder's built-in audit (every entry
   bar time ≥ 11:00) **plus** an independent re-derivation of
   every trade's qualifier, direction, and entry bar from the
   raw fetched bars (the O2 method). Violations must be 0.
2. **FOLLOW control:** the identical qualifying stock-day set
   traded in the pre-move's OWN direction (follow instead of
   fade), same entry and exits. The fade must beat follow
   decisively on the broad universe too, or the verdict says so.

## Reporting — declared

Total trades and net; per-calendar-month split inside the
window; first-30-trading-days vs last-30-trading-days halves;
breadth (net-positive stocks / achieved universe); expectancy
per trade; top-3 and top-10 stock share of net; worst stock;
the **October-only slice** of the broad run, placed next to the
ext-25 October anchor (+₹98,153.17, 104 trades); and the
**ext-25 subset inside this broad run** as a consistency check
against the O2 record for the overlapping months. Monthly
run-rate over the 60 days = net / 3 (60 trading days ≈ 3
months), stated as such.

## What this line may NOT do

No threshold, measurement-time, exit, direction, or cost
variants. No per-stock exclusions after seeing results. No
context filters. If the fade fails on the broad universe, the
verdict says it failed — the December candidate's own frozen
test is a separate matter and is not edited by this line.
