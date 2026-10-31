# Family 2 (progressive tuning) — Volrix-for-stocks — FROZEN 2026-10-30, NOT SCORED YET

Paper only, cash intraday stocks only, 25 stocks, no options, no orders.
Frozen BEFORE scoring, so its outcome cannot re-tune its definition.

## Rationale
Volrix (index) = previous-day underlying close down ≥2%, next session
entry, 5-session hold, 10-session cooldown, no stop/target. Adapted to
intraday stocks, the 5-session hold cannot be an intraday rule, so this
family uses a same-day square-off instead (stated, not hidden). It is
tested BOTH individually and as an overlay on S8/S9 candidates — but
scored as its own track first, never pooled with S8/S9 totals.

## Frozen rules
- Trigger: stock's previous trading day close ≤ -2.00% vs the close
  before it (daily closes from spot_daily.csv, cache only).
- Entry: next trading day, first 5-min candle open (09:15 open).
  No OR/bias/second-close filter — the trigger IS the entry.
- Exit: 15:10 square-off close, same day. No stop, no target, no
  give-back exit (Volrix has none). Net per 100 shares, provisional,
  minus ₹40/trade assumed cost.
- Cooldown: after a Volrix entry for a stock, no new Volrix entry
  for that stock for the next 10 trading sessions (skip those days
  even if the trigger fires again).
- Cap (same user bar): max 1 valuable stock trade/day across all
  stocks, 1/stock/week retained. Ranking for the cap: largest
  previous-day drop first (most oversold first), tie → symbol.
  Cap is a ceiling, not a quota: a day with no trigger trades nothing.
- Event/sentiment tagging: every Volrix trade tagged with the same
  event-window tag as S9 (post/pre/no-event/single-news) and with
  the global sentiment tag for that day (risk-on / risk-off / mixed /
  no influencing news found), with source + date. Tagging does NOT
  filter this family — it is diagnostic only, so the trigger's
  standalone value can be judged.

## Scoring (to be run after Family 1)
- Window: Jan–Oct 2026 (Oct 1–28), 25 stocks, from cache only.
- Separate check: this week Oct 26–29 (cache + Bank/Nifty context only;
  no 5-min stock data for Oct 29 in cache, so Oct 29 is reported as
  undetermined, not assumed).
- Report: trades, win net>0, net per 100 shares provisional, expectancy,
  trades/day, days traded vs trigger days vs cooldown-blocked days,
  month-by-month cumulative, ex-March / ex-October, per-stock, and
  event-phase / sentiment breakdown.
- Verdict against the user bar (net positive, 1/day, full-target N/A
  for a no-target system — report win rate and expectancy instead,
  cumulative rising, no forcing). A no-target system cannot pass the
  full-target leg; that leg is reported as N/A, not fudged.

## What this family deliberately does NOT do
- No stop/target added to "improve" Volrix after seeing its outcome
  in this run — that would be a new family, frozen separately.
- No pooling with S8/S9, V5, Skill v2, or (lA) v2 totals.
