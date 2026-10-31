# MOVER-B3 — CANDIDATE SPEC (frozen 2026-10-31)

**Status: CANDIDATE for a fresh window. NOT adopted. In-sample
tuned (Jan–Oct 2026) under the frozen family list in
`stocks_moverB3_frozen.md`; full results in
`stocks_moverB3_report.md`. Supersedes the MOVER-B2 candidate
(`stocks_moverB2_candidate_spec.md`) as the line's reference
configuration, per the B3 frozen gate: it passed every gate leg
against each configuration it modifies.**

Equity cash intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders, real money ₹0. Every rupee
figure provisional per 100 shares; net = gross − ₹40/trade flat.

## The rule (complete — this spec is self-contained)

Universe: the pooled 50 stocks (25 home watchlist + 25 ext
large caps), each scored on its own 5-min candles.

For each stock, each trading day:

1. **Pre-move measurement at 11:30.** Pre-move = (close of the
   last 5-min bar before 11:30) ÷ (open of the day's first bar)
   − 1. If |pre-move| < 1.0%, the stock-day does not qualify —
   no trades.
2. On a qualifying stock-day, take the frozen V5 re-entry signal
   stream for that stock-day (home: `stocks_equity_reentry.py`
   heads; ext: `stocks_equity_reentry_ext.py` heads). **Discard
   the first signal of the day entirely** — no trade, no cost.
3. Trade the **next** signal **only if its direction agrees
   with the pre-move's direction** (pre-move up → LONG signals
   only; pre-move down → SHORT signals only). A signal in the
   opposite direction is skipped — no trade, no cost — and the
   search restarts at that signal bar + 1. Entry = the open of
   the bar after the signal bar.
4. Exits (**T125/S065**): target **+1.25%**, stop **−0.65%**,
   stop checked before target within a bar, otherwise
   square-off at the 15:10 bar's close.
5. **One trade maximum per stock-day** (chain cap 1 — no
   re-entry leg). After the trade exits, the stock-day is done.
6. No ADR, event, timing or per-stock filters beyond steps
   1–5. Net per trade = gross − ₹40, per 100 shares. The
   tradable unit is the stock-day **chain** (here: the single
   trade).

Differences from the MOVER-B2 candidate: measurement **11:30**
instead of 10:30; step 3's **same-direction** restriction;
step 5's **cap 1** instead of cap 2; stop **−0.65%** instead
of −0.5%. Target unchanged at +1.25%.

## In-sample record (Jan–Oct 2026, Oct = 1–28) — tuned, NOT fresh

- Pooled 50: **1,694 chains, 1,694 trades, net +₹1,623,905.15**,
  expectancy **+₹958.62/chain**, chain win 71.1%.
- Halves: Jan–May **+₹951,573.84** / Jun–Oct **+₹672,331.31**.
- Splits: home 837 chains / **+₹489,399.84** (breadth 24/25);
  ext 857 chains / **+₹1,134,505.31** (breadth 25/25).
- October (1–28): **+₹190,471.72**.
- Breadth **49/50** — only NHPC negative (−₹97.91 over
  39 chains). Top-3 share 33.3%; largest contributor
  ULTRACEMCO +₹208,590.55.
- Max drawdown (daily-aggregated, risk-card method):
  **−₹11,557.03**.
- **No losing month**; weakest month May +₹86,294.15,
  strongest Mar +₹262,658.41. Full month table in
  `stocks_moverB3_report.md`.
- Gate record (frozen B3 gate): net greater than the B2
  candidate (+₹812,204.86) ✓ and greater than the B3-3
  configuration it modifies (+₹1,570,930.17) ✓, both halves
  positive ✓, breadth ≥ 47/50 ✓, max DD ≥ −₹25,000 ✓,
  no losing month ✓ — **PASS**.

## Disclosures (read before judging any fresh result)

1. **In-sample, heavily selected.** This configuration sits at
   the end of a selection chain (measurement slope scored at
   six points, stacks, exit check) all on the same Jan–Oct
   2026 window. Treat +₹1,623,905.15 as an **upper-bound
   estimate** until fresh data judges it; expect regression.
2. **The measurement slope never turned.** Net rose at every
   scored step through 11:30, the last point the frozen list
   allowed. 11:30 is the best *tested* point, NOT a proven
   peak; later measurement times are untested.
3. **Intermediate drawdowns.** The 10:45 and 11:00 plain cells
   failed the gate on drawdown alone (−₹25,759.71 /
   −₹26,464.55); the candidate's shallow −₹11,557.03 depends
   on the combined stack + wider stop, not on the measurement
   time alone.
4. November's frozen A/B shadows (home + ext, 10:00 vs 10:15)
   are **untouched** by this spec and proceed as scheduled.

## Fresh-window judging rule (pre-registered)

Window: **December 2026** (the next full fresh month after the
November exams), pooled 50, rules exactly as above, ₹40/trade,
paper only.

- December net positive at T125/S065 accounting with
  **≥ 80 chains** → B3 is confirmed as a candidate alongside
  the November survivors, for an adoption decision on the
  combined evidence.
- December net negative with ≥ 80 chains → **B3 is killed**;
  the MOVER-B2 candidate (10:30 plain) remains the line's
  reference configuration.
- Fewer than 80 chains, or net exactly ₹0 → inconclusive;
  extend one month under identical rules.

No parameter of this spec may be changed during the fresh
window.
