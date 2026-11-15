# EKAM — SPEC (FROZEN 2026-11-14, before scoring)

Programme: EKAM (registry `ekam_strategy.md`). Owner's order 2026-11-14 17:41 — adopt
the indicators that tested good (Bollinger Bands, RSI) and make them ONE strategy,
like TRIO. Research only — no book, ledger or job is touched.
Basis: equity cash · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR (2025, 2026),
never pooled into one verdict.

## 0. Source components (definitions are the atlas's, verbatim)

Data: `data/sarvaritu_fwd/<SYM>/spot_daily.csv` (2024-10-01 → 2026-11-13; Oct–Dec 2024
is warm-up). Indicators computed with the atlas build's own functions
(`indicator_parameter_tuning_stocks_build.py`, importing Round 1 constructions from
`dial_stocks_build.py`): Bollinger = window mean ± k·population-SD on closes;
RSI = Wilder. LONG only. One open position per name. ₹40 per completed trade.
Net = round((exit − entry) × 100 − 40, 2). Hold = exit index − entry index in the
name's own series.

- **BB-REV-D (BASE form)** — Entry signal at day t: close[t−1] < lower[t−1] AND
  close[t] ≥ lower[t], lower = Bollinger(20,2) lower band, lower[t] defined.
  Exit signal: first close ≥ middle band → exit at next day's open.
- **RSI-REV (TIME60 form)** — Entry signal at day t: RSI(14) crosses back up through
  30 (RSI[t−1] ≤ 30 < RSI[t], both defined). Exit stack, priority order: (1) TIME60 —
  at the open of the first day i with i − entry_index ≥ 60 (i > entry_index);
  (2) CAP — intraday +10% from entry price (gap-through at the open, else at the
  level); (3) first close with RSI ≥ 70 → exit at next day's open.
- **MACD-D (BASE form)** — MACD(12,26,9): entry signal on signal-line cross up;
  exit on cross down → next day's open. (EKAM-3 comparison only.)

Shared fill conventions (atlas `run_swing`, verbatim): signal at day t close → entry
at day t+1 open (requires t+1 to exist). Close-signal exits at day t → exit at day
t+1 open; if t is the last data day, exit at close[t], flagged FORCED. A position
still open at the data end is closed at the last close, flagged FORCED. After an
exit on day x (the exit-price day), scanning for new entries resumes at day x's
close. Exit checks run from the entry day itself for price-level and close-signal
exits; TIME60 requires i > entry_index.

## 1. CONTROL (mandatory, before combining)

(a) Re-run the atlas build's `part_b()` and check the rows (BB-REV-D, BASE),
(RSI-REV, TIME60), (MACD-D, BASE) against the published anchors in
`indicator_parameter_tuning_stocks_results.json` / the atlas report — trades, total,
WR, avg hold, worst, forced, combined max DD, per year.
(b) Run the EKAM engine in single-component mode (BB only / RSI only / MACD only,
no stop) and check its trade lists equal the atlas `part_b()` trade lists exactly
(entry/exit dates, prices, net, hold, exit kind).
Any mismatch = stop and report it; no EKAM numbers are produced.

## 2. EKAM-2 — the strategy (BB-REV-D + RSI-REV(TIME60) merged into ONE book)

Per name, one state machine over the merged signal union:
- When flat at day t: collect the components whose entry signal fires at t.
  If the set is non-empty and t+1 exists → ONE position entered at t+1 open,
  tagged by the firing set: `BB`, `RSI`, or `BOTH`.
- When a position is open, ALL entry signals in that name are ignored
  (no adding, no pyramiding, no tag changes).
- The position's exit stack is the union of its tagged components' exit rules,
  evaluated per day i from the entry day, priority: (1) TIME60 at the open —
  only if RSI ∈ tag; (2) hard stop (stop forms only, §3) intraday; (3) CAP +10%
  intraday — only if RSI ∈ tag; (4) close-signal exits at day i's close (BB:
  close ≥ middle band, if BB ∈ tag; RSI: close with RSI ≥ 70, if RSI ∈ tag) →
  exit at day i+1 open (FORCED at close[i] if i is the last day).
  First trigger wins; the exit kind records which rule fired (TIME / STOP / CAP /
  SIGNAL-BB / SIGNAL-RSI / FORCED).

## 3. STOP small-tune on EKAM-2 (components natively carry no downside stop)

Three forms, all other rules identical:
- **S0** — no stop (native).
- **S1** — hard stop at entry price × (1 − 0.08), fixed for the trade's life.
- **S2** — hard stop at entry price × (1 − 0.12), fixed for the trade's life.
Stop fill (intraday, day i ≥ entry day): if low[i] ≤ level → exit at open[i] if
open[i] ≤ level (gap-through), else at the level. Kind = STOP.

## 4. EKAM-3 — comparison row only

EKAM-2 + MACD-D under the identical merge rules (tag set can include MACD; a MACD
position's exit rule is the cross-down close signal; TIME60/CAP apply only if RSI ∈
tag; the hard stop applies book-wide per form). Scored at S0, S1, S2; reported as
one summary line per year per form.

## 5. Reporting (per form, per year — 2025 and 2026 separately)

Year attribution (atlas rule): a trade belongs to year Y iff its ENTRY date falls
in Jan 1 – Oct 31 of Y. Report: trades · total · WR · avg hold days · month table
(net and trades by entry month, Jan–Oct) · halves (H1 = entries Jan–Jun, H2 =
entries Jul–Oct: trades and net) · ex-top-3 (total minus the sum of the
min(3, trades) largest nets) · equity-curve max drawdown (that year's trades
ordered by exit date, ties by entry date then symbol; cumulative net from 0;
DD = min(equity − running peak)) · worst trade · peak concurrent positions
(maximum over days of the number of that year's positions simultaneously open,
entry day through exit day inclusive).

## 6. PLACEBO (EKAM-2 only)

For S0 and for the BEST stop form — best = argmax over {S1, S2} of
(total_2025 + total_2026), tie → S1; the choice is made by this rule, not by eye.
Per year: N = EKAM-2's trade count in that form and year. Each of 200 draws
(seed 20261114) sums N independent placebo trades: name drawn uniformly from the
25; signal day drawn uniformly from that name's days whose date is in
Jan 1 – Oct 31 of the year and which have a next day; entry at next day's open,
100 shares. Exit stack mirrors the form under test, frozen: (1) TIME60 at the
open of the first day i with i − entry ≥ 60; (2) the form's hard stop intraday
(S1/S2 only), same fill rule as §3; (3) BB middle-band rule — first close ≥
middle band → next day's open (FORCED at the last close if still open at data
end or if the signal fires on the last day). Net per trade = (exit − entry) ×
100 − 40. Report: the percentile of the real total among the 200 draw totals
(100 × share of draws ≤ real total), plus draw mean and median.

## 7. NOVEMBER (descriptive only)

From the EKAM-2 trade lists at S0 and at the best stop form: every position with
entry date in 2026-11-02 – 2026-11-13 (signal date shown), and every position
entered earlier still open at 2026-11-13. Positions still open at 2026-11-13 are
marked at the 2026-11-13 close and labelled **OPEN/MARKED** — their marked net
is shown for information and is NEVER counted in any closed total. Also count:
component signals firing on 2026-11-02 – 2026-11-13 that produced no entry
(name already held, or signal on 2026-11-13 with no next data day).

## 8. Standing

EKAM arms nothing and replaces nothing. Adoption needs forward evidence + the
owner's explicit word.
