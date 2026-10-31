# S9 — Intraday STOCK system (cash, NOT options) — FROZEN DRAFT, NOT YET SCORED

**Status: DRAFT 2026-10-30, carried forward from S8's failure. NOT
adopted, NOT scored, NOT a live system. Paper only, no orders.**
This draft exists so tuning does NOT stop at S8. It becomes a
frozen spec the moment the event-layer calendar lands, and NO S9
scoring happens before that freeze is complete.

## Base design (frozen, identical to S8)

S8 exactly: CE pullback arming on ANY reclaim close above OR
high (regardless of day open vs PDC), pullback + second-close
entry, stop = pullback low, room ≥ 1.5×, target +2× risk;
PE path as in S6/S7/S8; OR width 0.25–3.0%, stock bias filter,
Nifty bias-only confirmation, prospective ≥ ₹500 (per 100
shares, provisional — NOT a lot profit), give-back exit,
100 shares, ₹40/trade, 15:10 square-off, cap max 1 valuable
stock trade/day, 1/stock/week. No direct reclaim CE, no setup2
CE breakout, no timing gates, no room < 1.5×.

## The S9 change — event gate (ONE open parameter, to be frozen)

A separate event-layer agent is building a news/results/
CEO-change calendar for the 25 stocks: results announcement
dates (reaction day = next trading day after after-market
announcements, window ±7 days as established in results
intelligence v1), CEO/management changes, major news, and
corporate actions. S9 = S8 candidates filtered by that
calendar, in ONE of the following modes — the mode is the
single parameter left open in this draft, and it MUST be
frozen, with its window definitions, BEFORE any S9 run is
scored:

- **Mode E-ONLY (event-window only):** a candidate trades only
  if its stock-day falls inside an event window for that
  stock. Rationale: stock entries are not random; news and
  results drive the moves S8's price levels are trying to
  catch, so restricting to event windows should raise
  frequency quality, not just frequency.
- **Mode E-BLOCK (event-window blocked):** a candidate trades
  only if its stock-day falls OUTSIDE every event window for
  that stock. Rationale: event days are the noisy, gap-driven
  days where price setups get stopped; excluding them should
  raise win quality on ordinary days.

The mode is NOT chosen by peeking at S8's Jan–Oct outcomes
(that would be re-tuning S8 on the same window). It is chosen
at calendar delivery from the calendar's coverage and the
standing results-intelligence finding (post-results volume
~2×, post return mean −2.08% in v1), recorded here as a
frozen amendment, and only then is S9 run on Jan–Oct 2026
as in-sample context, judged on the same user bar (net
positive, ~1 valuable trade/day, full-target above S2's
19.7%, cumulative rising month by month, no forced trades,
setup2 reported honestly). If S9 passes ALL legs in-sample,
it is still NOT adopted — it goes to November 2026 paper
from Mon 2026-11-02, logged daily after 15:10 in
`s9_forward_paper_log.csv`, separate from the Nifty log,
with no re-tuning during November.

## What S9 deliberately does NOT do

- No re-tuning of S8's price filters on the Jan–Oct window
  to force a pass. S8's numbers stand as reported in
  `new_stock_system_s8.md`.
- No new setup2-PE room definition inside S9. That is the
  family AFTER S9 (structural level below PDL, frozen as its
  own version), because S8's diagnosis showed setup2 PE has
  no room to measure under the current definition.

## Deliverables when frozen and scored

Frozen spec (this draft + mode amendment), engine
`stock_system_s9.py`, report `new_stock_system_s9.md`,
trade CSVs `s9_trades_jan_oct_2026.csv` /
`s9_uncapped_jan_oct_2026.csv`, month JSON
`data/progressive/s9_summary_2026-jan-oct.json`, and — only
if S9 passes all legs in-sample — header-only
`s9_forward_paper_log.csv`.
