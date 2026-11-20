# TARANG Design 21 — SPEC (pre-registered 2026-11-17, before any Design 21 scoring)

**Programme status:** CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Design 20's diagnosis (tarang20_2026-11-17.md
S.6) is this design's seed. Design 20 measured: drift exits
are worth real money (+₹46,127 / +₹61,472 over Design 19 on
identical entries) but the two engines cancel — 58.8% of
positions reach the close at +₹504.14 each (+₹13,73,777)
while the −1% stop fires on 41.2% at −₹813.52 each
(−₹15,54,645), netting ~+₹1 gross per trade against the ₹40
levy. The survival pre-filter enriches the raw STREAM in
both years (+₹22.91 / +₹8.54 gross per trade — the first
pre-filter with a positive stream sign in both years), yet
the TAKEN book grosses below its own stream in 3 of 4
book-years (T20-A 2026: stream −₹0.16, taken −₹28.14;
T20-B 2026: stream +₹8.54, taken −₹13.39), because the
greedy chronological allocator spends the 10 daily slots on
each day's EARLIEST transitions. Two dials remain
unmeasured on this family, and Design 21 measures exactly
those two — strength and allocation — with entries and
exits otherwise frozen.

**Basis:** equity cash, PROVISIONAL per 100 shares,
₹40/trade, paper only, real money ₹0. No stock options.
Research only — nothing armed, no paper run started, no
live book touched.

**Universe / data:** the 127 Round-6-verified F&O names
(`tarang6_verify.json` verified_universe), via
`tarang6_score.load_name6` (the Design 19/20 route);
missing volume prints count as 0 (the family's standing
convention). Data runs 2025-01-01 → 2026-11-13.

## S.1 Vote state and transitions — frozen as Designs 19/20

The six-vote state V (RSI(14) zone, MACD hist sign,
Supertrend(7, 3.0), ADX(14) trend sign vs EMA-50, EMA 9/21
alignment, Bollinger %B side, net in −6..+6) is computed
**exactly** as in `tarang19_SPEC.md` S.1, including
Amendments A1/A2. The Design 19 scorer's engine and
validator indicator stacks are imported unchanged; no vote
definition moves in this design.

A **LONG transition** fires at bar g if V(g) and V(g−1) are
both defined, V(g−1) < +4 and V(g) ≥ +4. A **SHORT
transition** fires if V(g−1) > −4 and V(g) ≤ −4. Each
transition carries **strength** = |V(g)| ∈ {4, 5, 6} and
**vol_ratio** at the signal bar = vol[g] /
mean(vol[g−19..g]) (0 if the mean is 0) — both exactly as
Design 20 SPEC S.2.

## S.2 Candidate generation — frozen construction, one gate

Candidate generation is the family's per-name chronological
simulation (Design 20 SPEC S.2, T20-A form): the name
starts flat; while flat, the first actionable transition
opens a position; while a position is open, transitions are
ignored; after an exit whose fill bar is f, scanning
resumes at bar f. The entry fills at the **open of bar
g+1**, which must be in the same session and stamped in
**[09:30, 14:30]**; a transition whose entry bar falls
outside the window is a non-event (the name stays flat,
scanning continues). Re-entry on a fresh transition after
a close is part of the design. No survival pre-filter in
either Design 21 book.

- **T21-A (strength gate):** inside the same simulation, a
  transition is actionable **only if |V(g)| = 6** (a
  unanimous six-vote transition). A transition with
  |V(g)| ∈ {4, 5} is a non-event: the name stays flat and
  scanning continues at the next bar. This is a gated
  simulation, **not** a post-hoc filter of the T20-A
  stream — the blocking structure differs (a strength-4/5
  trade in T20-A can block a later strength-6 transition;
  in T21-A it cannot), and the stream is generated with
  the gate inside the loop.
- **T21-B:** the full |V| ≥ 4 stream, identical candidate
  generation to T20-A (same simulation, no gate).

## S.3 Exits — frozen as T20-A (the drift form)

No vote-decay. Evaluated bar by bar from the entry bar e
to the day's square-off bar sq (the last bar stamped
≤ 15:15, the family `day_maps` construction), in this
order at each bar j:

1. **Disaster stop −1.0% (stop-first):** stop level =
   entry × 0.99 (LONG) / × 1.01 (SHORT). If the bar's open
   is beyond the stop, fill at the open; else if the bar's
   range touches the stop (low ≤ stop for LONG, high ≥
   stop for SHORT), fill at the stop. Reason `stop`.
2. **Square-off:** if j = sq, fill at close(sq). Reason
   `squareoff`.

Net per trade = side × (exit − entry) × 100 − ₹40.

## S.4 Books — the two unmeasured dials

Caps for both books: **1 open position per name** (no
overlap of taken [entry, exit] bar spans for a name),
**2 entries per name-day**, **10 entries per book-day**;
a skipped candidate does not regenerate later candidates.

- **T21-A allocation — A4 volume-priority (frozen):** the
  family's greedy chronological allocator (Design 19 SPEC
  S.4): sort key (date, entry_time, vol_ratio DESC,
  strength DESC, signal_time, sym). Strength is constant
  6 in this book, so the effective ranking is vol_ratio.
- **T21-B allocation — STRENGTH-PRIORITY (the repair):**
  the day's candidates are ranked **by strength DESC,
  then vol_ratio DESC, then chronology** (entry_time,
  then signal_time, then sym), IGNORING arrival order for
  the strength/volume ranks: sort key (date, −strength,
  −vol_ratio, entry_time, signal_time, sym), processed in
  that order under the same caps. The 10 daily slots go
  to the day's strongest transitions. Because per-name
  candidates are sequential and non-overlapping by
  construction (S.2), the no-overlap cap is enforced as
  an interval check over taken spans — the allocator and
  its independent rebuild use the identical predicate
  (candidate [entry, exit] overlaps a taken span iff NOT
  (exit < span_entry OR entry > span_exit)).

## S.5 Controls (all pre-registered; any failure aborts or fails the audit leg)

1. **EKAM machinery control (reported FIRST, before any
   D21 number):** EKAM's own vote machinery (imported
   `ekam_intraday_stocks_build` +
   `ekam_intraday_stocks_r2_build.exit_x2p`, via the Design
   19 scorer's control) run on the frozen 25 under EKAM's
   09:15 configuration must reproduce the published
   **CAND-T5** Jan–Oct lines **+₹62,164.57 (2025) /
   +₹63,883.60 (2026)** and **S2** lines **+₹45,300.64 /
   +₹72,605.30**, exact to ±₹0.05 per line. If either line
   misses, no D21 number is quoted. Companion parity: the
   Design 19 scorer's indicator stack vs EKAM's indicator
   functions (as in Design 19 S.5.1).
2. **Engine/validator parity:** the vote series and the
   transition sets are computed twice — the Design 19
   engine (loop-based indicators) and its independent
   validator (pandas ewm/rolling) — and must agree on
   every name: identical transition sets, V equal at every
   defined bar. Any mismatch is an audit violation.
3. **Timing/leak audit** over every taken trade: entry
   after signal; entry exactly at signal + 1; entry inside
   [09:30, 14:30]; signal present in the validator's
   transition set with matching V values; **for T21-A,
   every taken trade's strength = 6 re-verified**; exit
   re-simulated on the trade's own day by an independent
   exit implementation and matched on bar, price and
   reason; square-off price = close(sq); net recompute;
   caps (≤2/name/day, ≤10/day, no same-name overlap); a
   full independent allocator rebuild (validator
   transitions + the book's candidate rule + audit exits
   + the book's allocation rule) matched trade-for-trade.
4. **Truncation spot-check:** 30 sampled taken trades;
   indicators and V recomputed from the series truncated
   at the signal bar must reproduce V(g) and V(g−1)
   exactly (the Design 19 check, unchanged).
5. **Placebos:** (a) 200-draw random-entry placebo per
   book with the book's OWN exits (S.3) — same names/days,
   the book's own entries-per-day counts, random eligible
   bars in [09:45, 14:45] (the family's standing placebo
   window), random side, identical caps. Percentile of the
   real net within the draws, per year. (b)
   Direction-flip placebo (information): the taken trades
   with sides flipped and exits re-simulated.
6. **Independent re-sum** of the written trades CSV
   against the engine nets, to the paisa.

## S.6 Gate (unmoved, per book — `tarang2_score.gate_for`)

Net positive BOTH years · beats the random-entry placebo
p90 BOTH years · ex-top-3 positive BOTH years · no month
worse than −₹15,000 · November 2026 slice (Nov 1–13) ≥
−₹3,000 · audits clean (S.5.2–S.5.4 all zero). Nine legs.

## S.7 Anatomy (the seed's questions)

Report, per book and year: every gate leg; placebo
percentiles; side splits; halves; win rate; max drawdown;
month table; top-10 contributors; gross/cost/net per
trade (`tarang9_score.cost_anatomy`); the resolution mix
(stop / square-off counts, nets, shares, per-trade nets)
against Design 20's; and the **stream-vs-taken gross
table**: the RAW candidate stream under the book's own
entry/exit rules (every candidate scored standalone,
before allocation) — trades, gross ₹, gross/trade — beside
the TAKEN book's gross/trade, against the ₹40 levy and
against Design 20's measured pairs (T20-A stream
+₹19.67 / −₹0.16, taken +₹26.08 / −₹28.14; T20-B stream
+₹22.91 / +₹8.54, taken +₹5.84 / −₹13.39). The questions
Design 21 answers: **does the unanimous slice clear the
levy at a lower count (T21-A), and does strength-priority
allocation close the taken-slice gap — taken gross at or
above stream gross — that Designs 19 and 20 both
measured (T21-B)?**
