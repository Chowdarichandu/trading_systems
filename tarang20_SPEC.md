# TARANG Design 20 — SPEC (pre-registered 2026-11-17, before any Design 20 scoring)

**Programme status:** CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Design 19's diagnosis (tarang19_2026-11-17.md
S.6) is this design's seed: the vote-transition stream is
real but small (raw gross **+₹6.21 / +₹5.49** per trade
against the ₹40 levy), and the transplanted vote-decay exit
amputated it — decay fired on ~94% of trades at −₹60/−₹76
each, while the ~2% of positions left to the close netted
**+₹1,799 / +₹1,920** each: the drift signature at maximum
strength. Design 20 keeps Design 19's entries **frozen** and
changes only the exit (T20-A) and one entry pre-filter
(T20-B). Quiet allocation is NOT carried in: it hurt this
family in both years (Design 19) — pre-filters do not
transfer across families.

**Basis:** equity cash, PROVISIONAL per 100 shares,
₹40/trade, paper only, real money ₹0. No stock options.
Research only — nothing armed, no paper run started, no
live book touched.

**Universe / data:** the 127 Round-6-verified F&O names
(`tarang6_verify.json` verified_universe), stores
`data/tarang_vol/<SYM>/spot_5m_vol.csv` (incumbents) and
`data/tarang_wide_vol/<SYM>/spot_5m_vol.csv` (wide names)
via `tarang6_score.load_name6`; missing volume prints count
as 0 (the family's standing convention). Data runs
2025-01-01 → 2026-11-13.

## S.1 Vote state — frozen as Design 19

The six-vote state V (RSI(14) zone, MACD hist sign,
Supertrend(7, 3.0), ADX(14) trend sign vs EMA-50, EMA 9/21
alignment, Bollinger %B side, net in −6..+6) is computed
**exactly** as in `tarang19_SPEC.md` S.1, including
Amendment A1 (the 1e-9 %B tie band) and Amendment A2 (the
two-pass Bollinger numerics). The Design 19 scorer's engine
and validator indicator stacks are imported unchanged; no
vote definition moves in this design.

A **LONG transition** fires at bar g if V(g) and V(g−1) are
both defined, V(g−1) < +4 and V(g) ≥ +4. A **SHORT
transition** fires if V(g−1) > −4 and V(g) ≤ −4 (Design 19
SPEC S.2, unchanged).

## S.2 Entries

Candidate generation is a per-name chronological
simulation, independent of the day cap (the family
construction): the name starts flat; while flat, the first
actionable transition opens a position; while a position is
open, transitions are ignored; after an exit whose fill bar
is f, scanning resumes at bar f. A fresh transition after a
close is a fresh candidate — re-entry is part of the design.
Each candidate carries: sym, date, side, signal bar g (and
its stamp), entry bar e, entry price = open(e), **vol_ratio**
at the signal bar = vol[g] / mean(vol[g−19..g]) (0 if the
mean is 0), **strength** = |V(g)| ∈ {4, 5, 6}.

- **T20-A:** the entry fills at the **open of bar g+1**,
  which must be in the same session and stamped in
  **[09:30, 14:30]**.
- **T20-B (survival pre-filter):** a transition becomes an
  entry only if V **holds at or beyond the ±4 threshold for
  the next 3 bars** after the transition bar: V(g+1),
  V(g+2), V(g+3) all defined, all in the same session as g,
  and all ≥ +4 (LONG) / ≤ −4 (SHORT). The entry then fills
  at the **open of bar g+4**, which must be in the same
  session and stamped in **[09:30, 14:30]** (a setup
  completing after 14:30 is skipped). A transition that
  fails the hold never opens a position; the name stays
  flat and scanning continues at the next bar.

## S.3 Exits — the drift form (both books)

No vote-decay. Evaluated bar by bar from the entry bar e to
the day's square-off bar sq (the last bar stamped ≤ 15:15,
the family `day_maps` construction), in this order at each
bar j:

1. **Disaster stop −1.0% (stop-first):** stop level =
   entry × 0.99 (LONG) / × 1.01 (SHORT). If the bar's open
   is beyond the stop, fill at the open; else if the bar's
   range touches the stop (low ≤ stop for LONG, high ≥ stop
   for SHORT), fill at the stop. Reason `stop`.
2. **Square-off:** if j = sq, fill at close(sq). Reason
   `squareoff`.

Net per trade = side × (exit − entry) × 100 − ₹40.

## S.4 Books — one allocation (A4) for both

Candidates from S.2 are assembled chronologically with the
family's greedy allocator: sort key (date, entry_time,
**ranking key**, signal_time, sym); caps **1 open position
per name** (busy-until the taken trade's exit bar), **2
entries per name-day**, **10 entries per book-day**; a
skipped candidate does not regenerate later candidates.

- **Ranking key (both books) — A4 volume-priority:**
  vol_ratio DESC, then strength DESC.
- **T20-A:** S.2-A entries + S.3 exits.
- **T20-B:** S.2-B entries (survival pre-filter) + S.3 exits.

## S.5 Controls (all pre-registered; any failure aborts or fails the audit leg)

1. **EKAM machinery control (reported FIRST, before any
   D20 number):** EKAM's own vote machinery (imported
   `ekam_intraday_stocks_build` +
   `ekam_intraday_stocks_r2_build.exit_x2p`, via the Design
   19 scorer's control) run on the frozen 25 under EKAM's
   09:15 configuration must reproduce the published
   **CAND-T5** Jan–Oct lines **+₹62,164.57 (2025) /
   +₹63,883.60 (2026)** and **S2** lines **+₹45,300.64 /
   +₹72,605.30**, exact to ±₹0.05 per line. If either line
   misses, no D20 number is quoted. Companion parity: the
   Design 19 scorer's indicator stack vs EKAM's indicator
   functions (as in Design 19 S.5.1).
2. **Engine/validator parity:** the vote series and the
   transition sets are computed twice — the Design 19
   engine (loop-based indicators) and its independent
   validator (pandas ewm/rolling) — and must agree on every
   name: identical transition sets, V equal at every defined
   bar. Any mismatch is an audit violation.
3. **Timing/leak audit** over every taken trade: entry
   after signal; entry exactly at signal + 1 (T20-A) /
   signal + 4 (T20-B); entry inside [09:30, 14:30]; signal
   present in the validator's transition set with matching V
   values; **for T20-B, the survival hold re-verified from
   the vote series** (V at g+1..g+3 defined and beyond the
   threshold); exit re-simulated on the trade's own day by
   an independent exit implementation and matched on bar,
   price and reason; square-off price = close(sq); net
   recompute; caps (≤2/name/day, ≤10/day, no same-name
   overlap); a full independent allocator rebuild (validator
   transitions + the book's entry rule + audit exits)
   matched trade-for-trade.
4. **Truncation spot-check:** 30 sampled taken trades;
   indicators and V recomputed from the series truncated at
   the signal bar must reproduce V(g) and V(g−1) exactly
   (the Design 19 check, unchanged — it is exit-independent).
5. **Placebos:** (a) 200-draw random-entry placebo per book
   with the book's OWN exits (S.3) — same names/days, the
   book's own entries-per-day counts, random eligible bars
   in [09:45, 14:45] (the family's standing placebo window),
   random side, identical caps. (The survival pre-filter is
   a property of the signal stream; random entries have no
   signal to filter — as in Design 19, the placebo tests the
   exit stack and the day/count structure against random
   timing.) Percentile of the real net within the draws, per
   year. (b) Direction-flip placebo (information): the taken
   trades with sides flipped and exits re-simulated.
6. **Independent re-sum** of the written trades CSV against
   the engine nets, to the paisa.

## S.6 Gate (unmoved, per book — `tarang2_score.gate_for`)

Net positive BOTH years · beats the random-entry placebo
p90 BOTH years · ex-top-3 positive BOTH years · no month
worse than −₹15,000 · November 2026 slice (Nov 1–13) ≥
−₹3,000 · audits clean (S.5.2–S.5.4 all zero). Nine legs.

## S.7 Anatomy (the seed's questions)

Report, per book and year: every gate leg; placebo
percentiles; side splits; halves; win rate; max drawdown;
month table; top-10 contributors; gross/cost/net per trade
(`tarang9_score.cost_anatomy`); the resolution mix (stop /
square-off counts, nets, shares, per-trade nets) **against
Design 19's** (decay 93–95% of trades at −₹60/−₹76;
square-off ~2% at +₹1,799/+₹1,920); and the RAW candidate
stream under the book's own entry/exit rules (every
candidate scored standalone, before allocation) — trades,
gross ₹, gross/trade — against the ₹40 levy and against
Design 19's raw stream (+₹6.21 / +₹5.49). The questions
Design 20 answers: **does removing the decay churn let the
drift carry the book, and does the survival hold — the
natural repair for the allocation slice — lift the taken
stream's gross toward the levy?**
