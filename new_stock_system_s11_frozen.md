# S11 — Intraday STOCK system (cash, NOT options) — FROZEN 2026-10-30, BEFORE SCORING — **NOT SCORED**

**Status: FROZEN 2026-10-30, before any S11 scoring run. NOT scored in
the session that froze it. NOT adopted, NOT a live system. Paper only,
no orders.**
**Window when scored: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks,
203 trading days.** Scoring is a separate, later step; this file only
freezes the definition. Any Jan–Oct run of S11 is in-sample context
only; adoption requires net + win rate + frequency together on unseen
November 2026 paper, separate from the index logs.

## Base design — S9 exactly, ONE change only

S11 = S9 exactly (`new_stock_system_s9_frozen.md`, G-TIERED event gate
included), with the single change below. S10's setup2-PE room change
is NOT part of S11: S10 failed its adoption test (see
`stocks_resume_s10.md`), so S11 is built on the S9 base, not stacked
on a rejected version.

## Diagnosis this fixes — S9's no-event leg (from S9's own capped trades)

S9 capped no_event tier: **30 trades, −₹885 provisional per 100
shares**, despite the stronger no-event bar. Breakdown of those 30:

- By setup/direction: the loss is one leg — **setup3 bounce-rejection
  PE: 26 trades, −₹2,870**. Setup4 CE no-event: 4 trades, +₹1,985.
- By how the candidate passed the no-event bar (the gate's OR rule —
  room ≥ 2.0× **OR** prospective full-target net ≥ ₹1,000):
  - room-only (room ≥ 2.0×, prospective < ₹1,000): **18 trades,
    −₹1,855**, 4 full targets
  - prospective-only (prospective ≥ ₹1,000, room < 2.0×): **3 trades,
    −₹1,050**, 1 full target
  - **both bars passed: 9 trades, +₹2,020**, 2 full targets
- Losers vs winners inside the tier: median room ratio 2.41 (losers)
  vs 3.60 (winners); median prospective ₹790 (losers) vs ₹1,060
  (winners). The single-bar passes are exactly the weak half.
- The gate is not useless here: the 12 no-event candidates it already
  blocks would have lost −₹1,802.50. The leak is the OR, not the bar.

## THE S11 CHANGE — no-event tier: AND instead of OR (only change)

In the Event Gate v1 G-TIERED tier 4 (`no_event`), replace:

> keep ONLY if room ≥ 2.0× risk **OR** prospective full-target net
> ≥ ₹1,000 (per 100 shares, provisional)

with:

> keep ONLY if room ≥ 2.0× risk **AND** prospective full-target net
> ≥ ₹1,000 (per 100 shares, provisional). A no-event candidate
> failing either bar is gate-blocked.

### What does NOT change

- All other tiers (single_news room ≥ 2.0×; post_reaction and
  pre_announcement at S8 thresholds) are unchanged.
- S8/S9 price design, stop, target, give-back exit, cap, gate ranking
  (tier rank, then prospective, then room, then setup rank), costs
  (100 shares, ₹40/trade, provisional label), square-off: unchanged.
- The change is a FILTER tightening only. It creates no trades; on
  in-sample S9 numbers it can only remove no-event trades (the capped
  set may backfill from other gate survivors under the unchanged cap
  ranking — that backfill is part of the design when scored, not a
  second change).

## Pre-registered expectation (stated before scoring, not a result)

If the AND rule had applied to S9's capped set with no backfill, the
no-event tier would have been 9 trades / +₹2,020 instead of
30 / −₹885. The scored S11 result will differ because of cap
backfill; it must be reported as scored, not as this arithmetic.
S11 is a watch candidate only if, when scored, it progresses vs S9 on
net + win rate + frequency together — noting the known tension: this
fix REMOVES trades, so frequency will likely fall further below the
1-valuable/day standard, and that leg must be reported honestly
rather than the fix being claimed as a frequency improvement.
