# Round 7 — Morning re-entry filters on the V5 re-entry pool — FROZEN 2026-10-30, BEFORE SCORING

**Status: FROZEN 2026-10-30, before any Round 7 scoring. Paper only,
no orders. Equity cash, LONG/SHORT, no options language.**
**Basis: provisional per 100 shares. Gross = before the frozen
₹40/trade flat cost; net = gross − ₹40/trade. Pool: the frozen V5
re-entry trade CSVs (T10, T125), Jan–Oct 2026, Oct = 1–28 Oct,
25 stocks. N4-V3 and its November spec are NOT touched.**

## Input diagnostic (Round 6 Part A, unscored as a filter until now)

Re-entries (chain round ≥ 2) entered before 10:30 were the strongest
gross pocket in Round 6 Part A: gross expectancy ≈ +₹70 provisional
per 100 shares per trade in BOTH halves at both exits (T10: +₹59.63
Jan–May / +₹58.18 Jun–Oct; T125: +₹70.85 / +₹70.06) and net-positive
Jan–Oct at ₹40 on their own. Round 6 scored this as a diagnostic
only; this round scores it as proper filters, defined below ex ante.

## Definitions (frozen)

- Chain `round` = the entry's sequence number within its stock-day,
  as recorded in the frozen re-entry CSVs.
- "Before 10:30" = `entry_time` < "10:30" (entry_time is the recorded
  5-minute bar time, zero-padded HH:MM).
- ADR≥3% stock-day = Round 3/6 formula, unchanged: prior-10-trading-day
  mean of (high−low)/close×100 from spot_daily.csv, minimum 5 prior
  rows, trade day excluded; stock-days with no ADR value are excluded
  from ADR-filtered variants.
- Filters are post-filters on the recorded chains: skipping a trade
  does not alter later signal prices in this engine (same convention
  as Round 6 R3).
- Halves: Jan–May 2026 / Jun–Oct 2026. October shown separately.

## Variants (each scored at T10 and T125)

- **M1 — re-entries before 10:30 only:** keep every round-1 entry
  (any time) plus any round ≥ 2 entry with entry_time < 10:30.
  No chain cap.
- **M2 — morning system:** keep entries with round ≤ 2 (chain cap 2)
  AND entry_time < 10:30. Nothing at or after 10:30, any round.
- **M3 — round-2-only:** keep only trades with round == 2. (Round 1
  and rounds ≥ 3 are skipped. This is scored as the diagnostic
  implies, knowing a live chain cannot reach round 2 without a
  round-1 trade — it is reported as a pool statistic, and that
  caveat is stated wherever M3 is reported.)
- **M4 — M1 on the R5a pool:** first restrict to R5a (round ≤ 2 AND
  ADR≥3% stock-day), then apply M1's rule within that pool (all
  round-1 entries of ADR stock-days, plus round-2 entries before
  10:30).
- **M5 — M2 + ADR≥3%:** round ≤ 2 AND entry_time < 10:30 AND
  ADR≥3% stock-day.

## Scoring and survivor rule (frozen)

- Every variant × exit: trades, win %, gross total and gross
  expectancy, net total and net expectancy at ₹40 — for Jan–Oct,
  Jan–May, Jun–Oct, and October.
- **Survivor rule (unchanged): NET positive at ₹40 in BOTH halves.**
- Each variant's breakeven flat cost per trade at 100 shares is
  reported overall and per half (breakeven = gross expectancy; the
  both-halves breakeven is the smaller half's breakeven).
- Any variant passing both halves additionally gets: a per-month
  table (Jan–Oct), its full October trade list, and concentration
  checks — largest single month's share of Jan–Oct net, and largest
  single trade's share of Jan–Oct net. A pass carried by one month
  (largest month > 50% of Jan–Oct net) or one trade is flagged as
  concentrated, not celebrated.

## What this round does NOT do

- No new entry signals, no exit changes, no per-stock whitelist,
  no cost other than the frozen ₹40 (breakevens are reported, not
  assumed).
- No November-paper change: N4-V3 stays as frozen. If a variant
  survives, it is flagged as needing its OWN frozen November paper
  spec — this round does not create one.
