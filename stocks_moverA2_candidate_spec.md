# MOVER-A2 CANDIDATE — Morning-Mover, 10:10 measurement — FROZEN 2026-10-31

**STATUS: IN-SAMPLE GATE PASSER — candidate for a FRESH-WINDOW
test only. NOT adopted.** This configuration was found by tuning
on Jan–Oct 2026 (spec frozen in `stocks_moverA2_frozen.md` before
scoring; full record in `stocks_moverA2_report.md`). Its in-sample
figures are evidence for testing it, not evidence it works.
November 2026's frozen exams (N4-V3 primary; INV1, P2F and the
Morning-Mover home/ext A/B shadows) are already running and are
NOT modified by this spec — this candidate's first possible
window is the next one after those judgements (December 2026),
under a separately created logging schedule, if the parent thread
decides to run it.

**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders.
Real money ₹0. All figures provisional per 100 shares,
₹40/trade flat.**

## The rule (MOVER-A2, primary candidate = family A2-4b)

Universe: pooled 50 — the 25 watchlist stocks (signal stream
`stocks_equity_reentry.py`) + the 25 large-cap extension stocks
(signal stream `stocks_equity_reentry_ext.py`). Signal stream =
the frozen V5 re-entry stream (pool_pick over v4_head/skor_head;
entry = next bar's open after the signal; next search starts at
the previous exit bar).

For each stock-day:
1. **Pre-move test (known at 10:10):** day open = the first 5-min
   bar's open; pre-close = the close of the last bar with time
   < 10:10. The day qualifies iff |pre-close / day open − 1|
   ≥ 1.0%.
2. **Non-qualifying days: NO TRADES AT ALL under this rule.**
3. **Qualifying days:** discard the first V5-stream signal of
   the day entirely (no trade, no cost). Trade the next signal
   at **T125 (target +1.25% / stop −0.5%)**, entry at the next
   bar's open, exit replay per the frozen convention (scan from
   the entry bar; stop checked before target within a bar;
   15:10 square-off at that bar's close). After that trade
   exits, ONE further re-entry is allowed if another signal
   occurs (also T125). **Chain cap = 2 trades per stock-day.**
4. If a qualifying day has a first signal but no second signal,
   no trade is taken that day.
5. Traded signals may be in EITHER direction (any-direction),
   regardless of the pre-move's sign. No ADR filter, no
   morning-entry cutoff, no event filter, no per-stock
   exclusions.

**The ONLY difference from MOVER-A is step 1: the pre-move is
measured to the last bar before 10:10 instead of before 10:00.**

## In-sample record (Jan–Oct 2026, reported, NOT a pass claim)

Pooled 50: **812 chains, 1,280 trades, net +₹406,054.73**
provisional per 100 shares. Jan–May +₹202,495.77 (491 chains);
Jun–Oct +₹203,558.96 (321 chains); October +₹103,883.51 (120
chains). Chain win rate 59.6%, chain expectancy +₹500.07.
Breadth **47/50** stocks net-positive by chain total; top-3
share of net 30.2%.

Splits: home 25 — 532 chains, 863 trades, +₹163,227.51
(JM +₹92,063.87 / JO +₹71,163.64; Oct +₹41,999.89; breadth
22/25; no losing month). Ext 25 — 280 chains, 417 trades,
+₹242,827.22 (JM +₹110,431.90 / JO +₹132,395.32; Oct
+₹61,883.62; breadth 25/25).

### Full month table — pooled 50 (chains / trades / net ₹)

| Month | Chains | Trades | Net |
|---|---|---|---|
| Jan 2026 | 90 | 145 | +19,752.98 |
| Feb 2026 | 85 | 136 | +19,712.05 |
| Mar 2026 | 133 | 204 | +77,893.47 |
| Apr 2026 | 95 | 153 | +57,944.16 |
| May 2026 | 88 | 137 | +27,193.11 |
| Jun 2026 | 69 | 105 | +58,162.97 |
| Jul 2026 | 60 | 99 | +5,062.76 |
| Aug 2026 | 40 | 68 | +15,572.15 |
| Sep 2026 | 32 | 44 | +20,877.57 |
| Oct 2026 | 120 | 189 | +103,883.51 |
| **Total** | **812** | **1,280** | **+406,054.73** |

**Losing months: none.** Base MOVER-A, same
window: 623 chains, +₹249,155.03, losing months Jan/Feb/May —
the candidate is +₹156,899.70 over base.

### Improver-gate record (frozen gate, pooled 50)

Net > base ✓ (+₹406,054.73 > +₹249,155.03) · Jan–May > 0 ✓ ·
Jun–Oct > 0 ✓ · breadth 47 ≥ 35 ✓ · losing months 0 ≤ 3 ✓ ·
October > 0 ✓ — **all six legs pass.**

## Gate-passing alternates (scored, NOT the primary candidate)

All in-sample, pooled 50, same window and gate:

| Family | Rule difference vs MOVER-A | Chains | Net ₹ | Breadth | Losing mo |
|---|---|---|---|---|---|
| A2-4a | measure < 10:05 | 751 | +332,476.95 | 46/50 | 2 |
| A2-5b | A2-4b + stop −0.65% | 812 | +397,758.28 | 47/50 | 0 |
| A2-5a | A2-4b + target +1.5% | 812 | +322,897.36 | 45/50 | 0 |
| A2-3 | direct-only + same-direction (10:00) | 571 | +290,083.61 | 43/50 | 1 |
| A2-1 | direct-only (10:00) | 623 | +275,795.51 | 42/50 | 3 |
| A2-2 | same-direction (10:00) | 571 | +261,069.37 | 41/50 | 2 |
| A2-6 | flank rule (10:00) | 580 | +260,880.35 | 41/50 | 2 |

A2-5a/A2-5b pass the gate against the base but score BELOW the
primary candidate, so as exit changes they are rejected — the
candidate keeps the frozen T125 exits. A2-3 is the strongest
10:00-measurement alternate (fewest trades, lowest top-3 share
27.4%, expectancy +₹508.03/chain) if a simpler cap-1 rule is ever
preferred for a fresh window. Exactly ONE configuration should
be run as the A2 candidate in a fresh window; the rest stay as
this written record.

## Pre-registered judging rule for the fresh window

To be fixed when a logging schedule is created, and stated here
so it cannot drift: over the fresh window, the candidate is
**upgraded** only if its chain-total net at T125 accounting
(₹40/trade, per 100 shares, pooled universe as logged) is
positive AND it produced ≥40 qualifying chains; **killed** if
the net is negative; **inconclusive** (extend one more window,
identical rules) if positive but fewer than 40 qualifying
chains. No parameter changes during the window.

## Honesty clauses

- In-sample only. Jan–Oct 2026 was used to discover MOVER-A and
  to tune this variant; the +₹406,054.73 is evidence for testing
  it, not evidence it works.
- This candidate sits on a measurement-time slope: pooled nets
  rise monotonically 10:00 (+₹249,155.03) → 10:05 (+₹332,476.95)
  → 10:10 (+₹406,054.73) → 10:15 (+₹464,617.03, Line 5's MOVER-B
  diagnostic). 10:10 is an interior point, not a discovered peak;
  MOVER-B (10:15) remains a separate line with its own frozen
  November shadow, and nothing here edits it.
- The re-entry leg inside this configuration is still a pooled
  drag (home +₹11,403.01 / ext −₹24,840.95 in-sample); the rule
  keeps it exactly as frozen because a direct-only variant at
  10:10 was not among the pre-registered A2 families — testing
  one requires its own frozen spec.
- Concentration is moderate: top-3 stocks ≈ 30.2% of the
  candidate's net (base A: 34.1%).
