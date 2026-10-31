# Cluster 2 / Cluster 3 — Forward paper log spec, November 2026

## Status: preparation only

This is a **log spec and an empty template only**. It is **not** a new tweak
family, **not** a backtest, **not** a tuning run, and **not** an adoption.

- **Paper only. No orders. No live trading. No lot increase.**
- **No November result is claimed.** November 2026 has not happened.
  The first trading day in scope is **Monday, 2026-11-02**.
- **No thresholds are frozen as a candidate in this spec.**
- **No rule is adopted by this spec.**
- **No re-fitting on the November month is permitted.** November data are
  for logging and for a month-end count only (see "Month-end review").
- Do **not** re-tune c2-A, survival N, flip triggers, or any other
  previously tested rule on the basis of this log while November is
  in progress.

Context for why only logging is justified now: family (y) is done and
the direction-flip idea is discarded; no further 5-minute PE parameter
family is proposed. Cluster 2 was recorded as unfixable on the available
reclaim sample, and Cluster 3 survival N=10 remains only a scoped,
in-sample result — not an adopted rule. The previous best kept for
Cluster 1 remains (lA) (5/8, −₹2,720, winners intact), and (lA) itself
is **not** adopted.

## What must be logged

Log **two universes**, every trading day in November 2026:

1. **Every Nifty PE trade under (lA).**
   - Log every (lA) PE trade, **not only trades later classified as
     Cluster 3**. Cluster 3 (slow PE give-back) is only knowable
     post-hoc — from MFE and bars-to-stop after the trade — so
     filtering at log time to "likely Cluster 3" days would bias
     the sample.
   - (lA) here means the reference rule already used in the
     long-horizon sweeps: the BN-confirmed rescan morning, with the
     band-filtered re-entry scan and the afternoon
     stop-on-first-fail rule, as previously defined. This spec does
     not change (lA); it only records what (lA) produced that day.
   - If (lA) produces no PE trade on a day, record one no-trade row
     for that day (date, trade type, and reason in `notes`), so the
     November universe is auditable and no-trade days are not
     silently dropped.

2. **Every setup4 reclaim CE trade (the Cluster 2 universe).**
   - A reclaim CE trade is a day opening below the previous close
     whose signal close is above BOTH the opening-range high and the
     previous close, and below the previous-day high, with the
     room condition as previously defined.
   - Reclaimed level `L = max(OR high, previous close)`.
   - Log every such trade, win or loss, whether or not it later
     looks like a Cluster 2 failure. Do not filter reclaim trades
     by outcome at log time.

No other instruments, no stocks, and no Bank Nifty trades are in
scope for this log. Nifty only.

## Fields — one row per trade (plus one no-trade row per no-trade day)

The CSV template is `cluster23_forward_paper_log.csv` in the same
directory. Its header is the field list. Every field must be filled
where it applies; use an empty value only where the field genuinely
does not apply (for example, re-entry fields when there was no
re-entry, or `reclaim_L` for a PE trade).

- `date` — trading date, YYYY-MM-DD.
- `trade_type` — `PE_lA`, `reclaim_CE`, or `no_trade`.
- `signal_time` — time label of the signal bar (5-minute bar label).
- `signal_mode` — `v4` or `skill`, as used for that signal.
- `or_low`, `or_high` — opening-range low / high for the day.
- `pdl` — previous-day low.
- `prev_close` — previous trading day's close.
- `reclaim_L` — for reclaim CE trades only: `max(OR high, previous close)`.
  Leave empty for PE trades.
- `entry`, `stop`, `risk_points`, `target` — the **frozen (lA) /
  original reclaim trade actually logged that day**: entry price,
  stop price, risk in index points (`stop − entry` for PE;
  `entry − stop` for CE), and target price at 2× risk from entry.
  These are the prices the paper trade used that day, not a
  re-computed or re-tuned alternative.
- `exit_time`, `exit_type` — when and how the morning trade exited:
  `target`, `stop`, `trail_exit` (only if a trail rule was part of
  the logged trade — otherwise do not invent one), `square_off`,
  or `no_trade`.
- `net_rs` — morning-trade net in rupees, on the provisional paper
  basis used throughout this work: **100 shares, ₹40/trade cost**.
  This is a paper-comparison basis, not actual brokerage.
- `reentry_entry`, `reentry_stop`, `reentry_risk_points`,
  `reentry_target`, `reentry_exit_time`, `reentry_exit_type`,
  `reentry_net_rs` — the (lA) re-entry for that day, if any, on the
  same basis. Leave empty if there was no re-entry. The re-entry
  is part of the day's (lA) result; do not log a re-entry that (lA)
  would not have taken.
- `day_net_rs` — morning net + re-entry net for that day (or the
  morning net alone if there was no re-entry).
- `plain_entry`, `plain_stop`, `plain_risk_points`, `plain_target`,
  `plain_exit_time`, `plain_exit_type`, `plain_net_rs` — what the
  **original (plain) trade would have done** on the same day:
  entry = next-bar open after the original signal, stop = signal
  high (PE) / signal low (CE), target = entry ∓ 2× risk,
  square-off 15:10, 100 shares, ₹40/trade. This is a reference
  column for comparison at month-end; it is not a second live
  candidate and it does not change the (lA) day result.
- `mfe_pct_of_target` — **for Cluster 3 candidates (PE trades)**:
  maximum favourable excursion as a percentage of the full target
  distance, measured bar by bar before exit. Record it for every
  PE trade, so slow give-back can be classified later without
  re-fitting a definition during November.
- `bars_to_stop` — **for Cluster 3 candidates (PE trades)**: number
  of bars from entry to the stop bar, if the trade stopped;
  otherwise empty (or the bars to exit, noted as such in `notes`).
- `second_close` — **for reclaim CE trades only**: the close of the
  bar after the signal bar.
- `second_close_vs_L` — **for reclaim CE trades only**: `above`,
  `below`, or `equal`, comparing `second_close` with `reclaim_L`.
- `hold_observation` — **for reclaim CE trades only, observation
  only**: what the 2026-style second-close hold would have shown
  (for example, "second close above L" / "second close below L").
  This is **not** a rule, **not** a filter, and **not** a candidate.
  It must not change the logged trade, its entry, or its exit.
  c2-A was discarded on held-out data and is not revived by
  recording this observation.
- `posthoc_cluster_label` — **leave empty during November**.
  Fill only at the month-end review, from the logged MFE /
  bars-to-stop / exit fields, for classification and counting only.
  Do not fill it day by day to steer later November logging.
- `notes` — anything needed to reproduce the row: no-trade reason,
  re-entry scan outcome, square-off detail, or data-source note.
  Do not put a new rule, threshold, or adoption claim in `notes`.

## Daily log cadence

- Log **after the 15:10 square-off** on each November trading day,
  once that day's paper trades are complete.
- For a day in progress, use the **Upstox intraday endpoint** for
  that day's 5-minute candles. The historical-candle endpoint
  returns completed days only and is empty for a day still in
  progress — that is a data-route fact from the October work, not
  a reason to delay or to guess a close.
- One row per trade, plus one no-trade row per no-trade day.
  Do not backfill a day from memory, do not estimate a close, and
  do not log a trade that did not occur under (lA) / the reclaim
  definition above.
- Do not score, rank, or re-tune anything from the log during
  November. Logging is the work; interpretation waits for the
  month-end review.

## Month-end review rule

Only **after the last November trading day has been logged**:

1. Count how many new Cluster 2 (reclaim CE) trades and how many
   new Cluster 3-classifiable PE trades (by the logged MFE /
   bars-to-stop fields) actually accumulated in November.
2. Report those counts, with the (lA) totals and the plain-trade
   reference totals for the same days, separately for PE and
   reclaim CE. Do not merge index and stock results, and do not
   present a November total as an adoption.
3. Decide only whether any new family is **even justified** by the
   sample size. The small-N verdict on Cluster 2 stands unless
   the sample grows materially; a single new reclaim trade, or a
   handful of PE trades, does not by itself justify a new family.
   No numeric threshold is frozen as a candidate in this spec,
   and no rule is adopted at the review on the basis of November
   alone.
4. If a new family is later proposed, its definition must be
   frozen **before** it is scored on any window it was not fitted
   on. November must not be re-fitted and then re-claimed as a
   pass.

## What this spec deliberately does not do

- No November trades are run by writing this spec — November has
  not happened, and no November row exists yet.
- No backtest of a new rule.
- No re-tuning of c2-A, survival N, flip triggers, partials,
  targets, stops, or re-entry guards.
- No candidate thresholds, no adoption, no live-trading
  recommendation, no lot change.

## Files

- Spec: `cluster23_forward_paper_log_spec.md` (this file).
- Empty log template: `cluster23_forward_paper_log.csv` — header
  row only, no data rows, no November result.
