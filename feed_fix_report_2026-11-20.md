# Feed-lag fix report — 2026-11-20

Owner authority granted 2026-11-20. Two defects, both the Upstox
one-day publication lag family. Diagnosis of record:
ekam_daily_feed_diagnosis_2026-11-18.md (not redone).

## State found at start (2026-11-20, before any fix)

- EKAM Daily: ledger has UNSCORED day rows for 2026-11-16, 17, 18, 19.
  fwd cache holds daily candles through 2026-11-18 for all 25 names
  (each day's candle lands in time for the NEXT run, never its own).
- Forward candidates: all four ledgers header-only. 5-min stores
  (data/tarang_vol) already hold bars through 2026-11-18 — the
  Nov 19 runner refresh DID land Nov 18 bars via the range route,
  i.e. the range route serves day D only from day D+1.

## FIX 2 — forward runner fetch route (diagnosis)

- The runner's refresh() fetches the RUN DATE's 5-min bars via the
  v3 historical RANGE route
  (/v3/historical-candle/{key}/minutes/5/{target}/{from}) — the
  route that lags one day for the newest date. Hence Nov 18 run:
  0/136 names with Nov 18 bars; Nov 19 run: 0 with Nov 19 bars.
- forward_live_producer.py instead fetches the current day via the
  v3 INTRADAY route (/v3/historical-candle/intraday/{key}/minutes/5),
  which serves same-day bars live — that is why it traded on
  Nov 18–20 while the EOD runner scored nothing.
- Fix (data route only, no rule changes): in refresh(), after the
  range-route fetch, if the target date is TODAY (IST) and no bars
  for the target date landed, fetch the target day via the intraday
  route (same call shape as the live producer) and merge. Past
  dates keep the range route (it serves them correctly one day on).

## FIX 1 — EKAM Daily scorer (plan)

- (a) Catch-up: main() first scores any earlier day in
  [START, today) whose ledger DAY row is UNSCORED (or missing),
  in date order, using the published daily candles (which have
  since landed). DAY-row notes state the day was scored one day
  late (catch-up). Position rows are recomputed deterministically
  each pass, so the final write carries the latest state.
- (b) Today: if the published daily candle for today is still
  absent at run time, build today's bar per name from the v3
  intraday route (5-min candles aggregated to OHLC) and score
  with it; DAY-row notes mark the day intraday-built.
- (c) Verification: built bars are recorded in
  ekam_daily_intraday_built.json; the NEXT run compares each
  built bar against the then-published daily candle and appends
  the result to ekam_daily_bar_verify_log.csv (and prints it).

## Results

(filled in as the work proceeds)
