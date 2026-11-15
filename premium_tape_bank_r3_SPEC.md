# PREMIUM-TAPE — BANK NIFTY · ROUND 3: WIDEN THE RETEST · SPEC · FROZEN BEFORE SCORING · 2026-11-14

Round-2 result: P-RET-X1 is the first intraday index row of the day
positive in BOTH windows — 46 trades, +Rs12,132.50, WR 47.8%
(Jan–Jun +Rs5,724.50 / Jul–Oct +Rs6,408.00), placebo 98.9th pct.
But it is SMALL: of 199 gate break events only 49 completed a retest
inside the 60-minute watch (120 events died at the window end, 30 on
a close below VWAP), and the 49 contract retests became 46 day
trades. **The turn: widen the net in two separate small steps and
see whether the edge survives at higher frequency.**

Research only. Nothing running is changed. Option BUYING only,
1 lot (30), Rs220/trade, paper only, real money Rs0.

## Data, contract selection, indicators — IDENTICAL to Rounds 1–2

- `premium_tape_bank_r2_SPEC.md` and `premium_tape_bank_SPEC.md`
  govern unchanged: same spot store (09:15 strike selection only),
  same in-force expiry map with the November 2026-11-23 override,
  same CE and PE of the strike nearest spot at 09:15 (100-step,
  exact half rounds up), same premium-store priority, same
  completeness test (all bars labelled 09:15..15:20; a missing side
  is NC, counted, never substituted), same premium VWAP
  (volume-weighted typical price where volume is carried; the
  equal-weighted proxy only on a no-volume source), and same premium
  opening-range high (bars labelled 09:15..09:45, 7 bars).
- Exits in this round are X1 ONLY (stop −50 checked before target
  +90 on each bar, fills AT the level; entry bar can trigger; if
  neither is hit through the 15:20 bar, exit at the 15:20 close).
  X2 is NOT carried — it failed in Round 2 (−Rs5,996.50).
- Net per trade = (exit − entry) × 30 − Rs220. Win = net > 0.
  Rs/trade-day = total / distinct trade days (the house convention;
  Steps B/C can hold 2 trades on one day, so trade-days can be
  fewer than trades there).

## CONTROL (must reproduce before any step is scored)

- The Round-2 P-RET-X1 book, rebuilt with the identical Round-2
  machinery (60-minute watch = 12 watch bars, retest capped at the
  14:25 bar, one trade per day): **46 trades, full Jan–Oct net
  +Rs12,132.50, WR 47.8%** (Jan–Jun 28 trades / +Rs5,724.50;
  Jul–Oct 18 trades / +Rs6,408.00). If the control does not
  reproduce exactly, the run stops and reports the mismatch — no
  step is scored.

## P-RET base rule (Round 2, restated)

Per scoreable contract-day: the BREAK EVENT is the first bar i
labelled in 09:50..14:20 whose premium close > premium
opening-range high AND close > premium VWAP at bar i. WATCH bars
j = i+1 onward: RETEST HOLD at the first j with low[j] <= VWAP[j]
AND close[j] > VWAP[j]; FAIL (event expires, `close_below_vwap`) at
the first j with close[j] <= VWAP[j] and no hold; if the watch ends
with no hold, the event expires (`window_end`). The day trade is
the earliest completed retest across the two contracts (same-bar
tie: larger touch depth VWAP[j] − low[j] first, then CE before PE);
entry = open of bar j+1.

## STEP A — WIDEN THE WINDOW

Identical to the control except the watch is **24 bars (120
minutes)**: j = i+1 .. min(i+24, the 14:25 bar). The 14:25 retest
cap (entry by 14:30) is unchanged, so late events gain nothing.
One trade per day, X1 exits.

## STEP B — ALLOW A SECOND TRADE

Identical to the control (60-minute watch, one trade per day
machinery) except: after the first trade's position has closed, a
SECOND trade is allowed the same day, at most 2 trades/day.

- The second search starts at the bar AFTER the first trade's exit
  bar (exit_i + 1). Per contract, the second BREAK EVENT is the
  first bar k in [exit_i + 1, the 14:20 bar] with close > premium
  opening-range high AND close > premium VWAP at bar k — a NEW
  event occurring after the close, regardless of that contract's
  earlier event history. The same contract may be traded twice.
- The second event's watch is the control's: j = k+1 ..
  min(k+12, the 14:25 bar), same hold / fail / expiry semantics.
- The second day trade is the earliest completed second retest
  across the two contracts (same tie-breaks); entry = open of
  bar j+1; X1 exits.
- If no second event completes a retest, the day keeps 1 trade.
  A first trade exiting at the 15:20 square-off leaves no room
  for a second trade by construction.

## STEP C — A + B COMBINED (labelled combined-after-steps)

Step A's 120-minute watch (24 bars) for BOTH the first and the
second trade's watches, plus Step B's second-trade rule (second
search from exit_i + 1, max 2 trades/day). X1 exits.

## Reporting

- Gate: the 203 stored days 2026-01-01..2026-10-31; windows
  Jan–Jun (<= 2026-06-30), Jul–Oct (>= 2026-07-01), full Jan–Oct.
  Per step (A / B / C): trades, net, WR, Rs/trade-day per window.
- **Selectivity per step**: break events vs completed retests
  (contract-days, gate and November separately) with expiry
  reasons; Steps B/C additionally report the second pass: days
  with a first trade, post-exit second events, completed second
  retests, second trades taken.
- NC counts (gate + November), identical accounting to Rounds 1–2.
- November CF (descriptive): Nov 2,3,4,5,6,9,11,12,13, per step.
- Timing audit: every completed retest used by the control or any
  step (first or second pass) re-checked — premium opening-range
  high and premium VWAP recomputed from the contract-day series
  truncated at the event / retest bars by an independent code
  path; the event asserted as the first eligible break inside its
  search range; no fail and no earlier hold inside the watch; the
  step's watch-length bound and the 14:25 cap asserted; every
  scored trade's entry = retest bar + 5 min at that bar's stored
  open; Steps B/C additionally assert each second event bar is
  strictly after its day's first-trade exit bar.
- Random-entry placebo on EACH step row: 1,000 draws × the row's
  trade count, fresh RNG seed 20261114 per row; each trade = a
  uniform random scoreable gate day, a uniform random scoreable
  side of that day, a uniform random entry bar 09:20..15:15, X1
  exit; percentile = % of draw totals strictly below the real
  total (the Rounds 1–2 Bank convention).

## DESIRED-RESULT BAR (stated before scoring)

A step IS the channel only if ALL of: full Jan–Oct net positive in
BOTH windows (Jan–Jun > 0 AND Jul–Oct > 0) AND its placebo
percentile >= 95th AND its full-year net is ABOVE the control's
+Rs12,132.50. Otherwise the step is reported as measured and the
control stands.

No parameter is tuned after scoring begins; Steps A, B, C as
defined here are the whole test.

Frozen 2026-11-14, before scoring. Build: premium_tape_bank_r3_build.py.
Outputs: premium_tape_bank_r3_2026-11-14.md +
premium_tape_bank_r3_results.json (+ premium_tape_bank_r3_trades.csv).
