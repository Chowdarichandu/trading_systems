# NIFTY Cluster 1 Fix — Step 2: FIRST failing case only, day by day

Paper only. No orders placed, no live trading, no live-trading recommendation.
NIFTY index only. Cash intraday, provisional rules (NOT Chandu's live options
rules): 100 shares equivalent (index points × 100), ₹40/trade assumed cost,
stop = signal-candle high (PE) / low (CE), target = 2× stop distance,
square-off 15:10, short signals paper-only.

Source: `nifty_failing_cases_jan_oct_2026.md`, Cluster 1 = Immediate
OR-breakdown PE bear-trap, 8 trades, −₹24,290, Jan–Aug 2026, all
bearish-bias, stop within 1–5 bars, stop inside the OR, 6 of 8 later
reach target.

## Step 2 stopping rule (as instructed)

Sequence: first failing day → second day with the same scenario ONLY if
day 1 turns green/positive → whole month ONLY if both days turn
green/positive. If day 1 does NOT turn green, STOP and do NOT proceed
to day 2 or a whole month. This report stops at day 1, for the reason
below. Day 2 and the whole month were NOT run.

## The ONE tweak chosen (and why)

**Candidate 1 from the source report, highest priority: confirmation
close.**

Exact definition, reproducible:

- Opening range (OR) = 09:15–09:30 bars, OR low = lowest low of those
  bars, OR high = highest high.
- Original rule: enter PE on the first 5-min close below the OR low
  (signal bar), entry = next bar's open, stop = signal bar's high,
  target = entry − 2 × (stop − entry).
- Tweaked rule: require a SECOND consecutive 5-min close below the
  OR low before entry. Entry = open of the bar after that second
  close, stop = that second bar's high, target = entry − 2 ×
  (stop − entry), net = (entry − exit) × 100 − ₹40 for a PE trade,
  with the stop checked intra-bar on the entry bar itself, exactly
  as in the source engine (entry bar is included in the stop check).

Why this one, and not the others, first: it attacks the stated
mechanism directly — the first close below the OR low was the
morning extreme, not a confirmed breakdown — without widening
risk (stop-placement candidate 3b), without a blunt time gate
(candidate 4, which would also kill genuine early breakdowns),
and without inventing a re-entry trade (candidate 5, which is a
new trade, not a fix to the first trade). Signal-distance
(candidate 2) was not chosen first because on day 1 the first
close is only 2.00 points below the OR low, so any distance
threshold would be fitted to that one day's number.

No other candidate was tested, and no cherry-picking across
candidates was done.

## Day 1 — 2026-01-09 — ORIGINAL (verified from the source report)

- OR: low 25,839.15, high 25,940.60 (09:15–09:30).
- Signal bar 09:30: open 25,841.10, high 25,873.10, low 25,820.80,
  close 25,837.15 — first close below the OR low.
- Entry (09:35 open): 25,836.05. Stop: 25,873.10 (signal high).
  Risk: 37.05 points. Target: 25,761.95.
- 09:35 bar: high 25,848.60, below the stop — survives.
- 09:40 bar: high 25,876.70, above the stop — stop hit.
- Original outcome: **−₹3,745** (37.05 × 100 + ₹40 cost).

## Day 1 — 2026-01-09 — TWEAKED (second-close rule, replayed bar by bar)

- First close below OR low: 09:30 close 25,837.15 (< 25,839.15).
- Second close below OR low: 09:35 close 25,830.10 (< 25,839.15,
  and below the first close). Confirmation is met — the tweak
  does NOT keep the trade out entirely on this day.
- Tweaked entry (09:40 open): 25,830.90. Tweaked stop: 25,848.60
  (09:35 bar's high). Tweaked risk: 17.70 points (less than half
  the original 37.05). Tweaked target: 25,795.50
  (25,830.90 − 2 × 17.70). Tweaked target net if hit: +₹3,500.
- 09:40 bar (the entry bar itself): open 25,830.90, high
  25,876.70, low 25,819.60, close 25,876.70. The high
  25,876.70 is above the tweaked stop 25,848.60, so the
  stop is hit on the entry bar.
- Tweaked outcome: **−₹1,810** (17.70 × 100 + ₹40 cost).

## Day 1 verdict — DOES NOT TURN GREEN

- Original: −₹3,745. Tweaked: −₹1,810. Improvement: +₹1,935,
  i.e. the loss is roughly halved because the second close
  moved entry lower and shrank the risk from 37.05 to
  17.70 points.
- But −₹1,810 is still a loss. It is NOT green, NOT positive,
  and NOT a no-trade. The tweak therefore FAILS the day-1
  test as instructed.

Why it failed, in price-action terms: the second close did
confirm direction for one more bar, but the bounce that
killed the original trade was not a one-bar spike — it
ran from the 09:35 low of 25,818.35 all the way to
25,876.70 in the 09:40 bar, through both the original
stop (25,873.10) and the tighter tweaked stop
(25,848.60). A tighter stop from a lower entry cannot
survive a 58-point bounce bar. The direction was
eventually right — price later fell well below both
targets (day low 25,623.00, below the original target
25,761.95 and the tweaked target 25,795.50) — but
that later move is a diagnostic only, exactly as the
source report warns: it is NOT evidence the tweaked
trade would have banked the target, because the
tweaked trade was already stopped out at 09:40.

## Stopping point — what was NOT done

- Day 2 (2026-02-06, original −₹2,275) was NOT tested
  with this tweak, because day 1 did not turn green.
- No whole-month (January 2026) run was done.
- No second tweak candidate was tested in this step.
- No cluster other than Cluster 1 was touched.

## What the parent needs to decide next

The second-close confirmation alone does not fix
Cluster 1's first day. The next decision is which
single candidate to test next on 2026-01-09, in
the source report's order — e.g. signal-distance
below the OR low, stop buffer, OR-low re-entry
stop (with target recomputed), or a time gate —
each tested on day 1 alone first, under the same
stopping rule. Alternatively, the parent may
conclude from this day that Cluster 1 needs a
stop that survives the bounce bar itself (which
necessarily widens risk and recomputes the target),
rather than a tighter confirmation entry.

## Reproducibility

Data: `~/workspace/trading/data/progressive/NIFTY/spot_5m.csv`
(09:15–09:40 bars for 2026-01-09 quoted above),
source report:
`~/workspace/trading/nifty_failing_cases_jan_oct_2026.md`.
All numbers above were recomputed from those
candles, not taken from the "later target"
diagnostic. Paper only, no orders, no fabrication.
