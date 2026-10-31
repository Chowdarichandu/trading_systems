# Stocks EQUITY — Round 5: N4-deep (event-reaction) — FROZEN SPEC (written BEFORE scoring)

**Status: FROZEN 2026-10-30, before any round-5 scoring run. NOT adopted,
NOT a live system. Paper only, no orders.**

**EQUITY CASH intraday only. LONG/SHORT language only — no options, no
premiums anywhere. Real money: ₹0.**
**Every rupee figure: provisional per 100 shares, ₹40/trade flat cost.**

## Why this round exists

Round 4 (`stocks_equity_native4_frozen.md`) tested stock-native entry
families on the 25 screenshot stocks over Jan–Oct 2026. Exactly one
family had a positive full-year net: **N4 results-reaction momentum**
— on a results reaction day, if the stock has moved ≥1% by 09:30 in
one direction, trade THAT direction (entry 09:35). Round-4 N4:
52 trades, **+₹4,319.24 provisional per 100 shares at T10**
(target 1.0% / stop 0.5%), halves Jan–May +₹5,641.88 / Jun–Oct
−₹1,322.64 provisional per 100 shares; at T125 (target 1.25% /
stop 0.5%) the halves were **both positive**: +₹2,727.65 / +₹197.14
provisional per 100 shares (the second half flat within noise).
N4b single-news reaction posted positive halves on only 4 trades —
insufficient sample. Round 4's frozen rule (T10 primary) made N4 a
near-miss, not a survivor. This round deepens ONLY the event-reaction
idea, with the exit choice declared in advance below. No new entry
source is introduced; no V5/Skill/(lA)/Volrix signal is used.

## DECLARED PRIMARY EXIT FOR THIS ROUND — T125 (declared before scoring)

**The primary exit for round 5 is T125: target +1.25% / stop −0.5%.**
Reason, stated before any round-5 run: in round 4, T125 was the only
exit at which N4 was positive in BOTH halves of Jan–Oct
(+₹2,727.65 / +₹197.14 provisional per 100 shares), while at T10 the
second half was negative (−₹1,322.64). If the event-reaction edge is
real, it apparently needs the wider target to pay for the 0.5% stop
on reaction-day volatility. Declaring T125 primary here — before
scoring any round-5 variant — is what makes a both-halves-positive
result at T125 in this round a graduation, rather than the
secondary-exit observation it was in round 4.

**T10 (target +1.0% / stop −0.5%) is scored and reported for every
variant as the secondary exit.** No variant graduates on T10 alone,
on a single half, on October alone, or on any exit other than the
two frozen here. Stop is checked before target on the same candle;
exit scan starts on the bar after the entry bar; 15:10 square-off —
all identical to round 4.

## Universe, window, data (identical to round 4)

- 25 screenshot stocks. Window Jan–Oct 2026 (203 trading days;
  Jan–May = 99, Jun–Oct = 104, October = 1–28 Oct, 18 days; 29 Oct
  missing from cache, stated, not a zero day).
- Data: each stock's `spot_5m.csv` and `spot_daily.csv` in
  `data/progressive/`; NIFTY daily dates are the trading-day list.
- Event source: `stock_event_calendar_jan_oct_2026.csv`, reaction
  dates exactly as round 4 computed them: `reaction_date` when
  present and within [event_date, event_date + 7 days], otherwise
  `event_date`; the reaction date must be a trading day in the
  stock's own daily data and inside the window.
- Results events: event_type = `results`. Single-news events:
  event_type in {management_change, large_order, fda_approval,
  block_deal, sector_policy, pricing, corporate_action} (dividend
  rows excluded as mechanical) — identical to round 4's N4b set.
- **Uncapped portfolio**: every qualifying stock trades; max 1 trade
  per stock per event per variant. The minimum-2-valuable/day rule
  is a floor, not a cap.

## Base rule (round-4 N4, unchanged — reproducibility anchor)

- On a results reaction day: move by 09:30 = (close of the bar
  timestamped 09:25 ÷ previous daily close − 1) × 100.
- If |move| ≥ 1.0%: direction = sign of the move (trade WITH the
  reaction). Entry = close of the bar timestamped 09:30, recorded
  entry_time 09:35; exit scan from the next bar.
- The round-5 engine must reproduce round 4's N4 exactly (52 trades;
  T10 +₹4,319.24; T125 +₹2,924.79 provisional per 100 shares) before
  any variant number is trusted.

## Variants (frozen — one change each from base, unless stated)

- **V1a — trigger ≥0.5%**: identical to base except the 09:30 move
  threshold is |move| ≥ 0.5%. Purpose: bigger sample — does the
  edge survive weaker reactions, or is it concentrated in strong
  moves?
- **V1b — trigger ≥1.5%**: identical to base except |move| ≥ 1.5%.
  Purpose: is the edge concentrated in the strongest reactions?
- **V2 — late entry 10:05**: identical trigger to base (|move| ≥ 1%
  by 09:30, same direction). Entry = close of the bar timestamped
  10:00, recorded entry_time 10:05; exit scan from the next bar.
  If the 10:00 bar is missing, no trade. Purpose: does waiting out
  the first half-hour (reaction-day opening noise) improve the
  trade, on the SAME trigger set?
- **V3 — combined event-reaction (the true event family)**: base
  rule applied to reaction days of results events AND single-news
  events pooled (the round-4 N4 + N4b event sets). Trigger ≥1%,
  entry 09:35, both exits. Max 1 trade per stock per event: if a
  stock-day is a reaction day for both a results and a single-news
  event, it produces ONE trade. Purpose: one event-reaction family
  instead of two fragments, with a usable sample.
- **V4 — second-day follow-through (results only)**: for each base
  N4 reaction day (results, |move| ≥ 1% by 09:30, direction D):
  if the reaction day's own daily close moved in direction D versus
  the previous daily close (LONG: reaction-day close > previous
  close; SHORT: reaction-day close < previous close), then on the
  NEXT trading day (next date on the trading-day list for which the
  stock has data) take direction D with the base intraday mechanics
  (entry = close of the 09:30 bar, recorded 09:35, exit scan from
  the next bar, same exits). No additional intraday trigger on
  day +1 — the day-1 close condition is the whole signal. Reported
  separately; a small sample is expected and will be labelled as
  such. V4 is an observation family: it cannot be the November
  paper primary unless it clears the same graduation rule below on
  an adequate sample (≥10 trades total, ≥3 per half).

## Graduation rule for the November paper spec (frozen)

A variant **graduates** if, at the declared primary exit **T125**:
net (provisional per 100 shares) is positive in **BOTH** halves
(Jan–May AND Jun–Oct), on an adequate sample (≥10 trades total and
≥3 trades in each half). Among graduating variants, the November
paper primary is the one with the highest Jan–Oct net at T125;
ties break toward the simpler rule (base before V1/V2 before V3).
If NO variant graduates, the November paper spec carries the
**base N4 rule (≥1% trigger, 09:35 entry) at T125**, with T10 logged
as shadow — because base N4 is the only family with a positive
full-year net in round 4 and its T125 halves were both positive
there, even though October and the Jun–Oct T10 half counsel
caution. V4 never carries the November spec alone (it is a
day-after observation, and its trades would be logged inside the
base/V3 paper log as a tagged shadow if the chosen primary is
results-based — no, frozen decision: V4 is NOT part of the November
paper spec in any form; it stays an in-sample observation).

## Reporting (frozen)

Every variant × both exits reports: trades, win %, target-hit %,
net provisional per 100 shares, expectancy, trades/day — for
Jan–Oct, Jan–May, Jun–Oct, and October. The both-halves verdict at
the primary exit is stated plainly for each variant. In-sample
only: graduation here means "carried to November paper", never
"adopted".

## What this round does NOT do

- No threshold, timing, or filter fitted from round-5 results.
- No direction split (LONG-only / SHORT-only), no per-stock list,
  no event-type sub-filter claimed from these samples.
- No union with any other family; no re-run of rounds 1–4 families.
- November paper, once specified, is NOT re-tuned during November.
