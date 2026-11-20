# TARANG Design 22 — SPEC (pre-registered 2026-11-17, before any Design 22 scoring)

**Programme status:** CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Design 21's diagnosis (tarang21_2026-11-17.md
S.6) is this design's seed. Design 21 closed the vote
family's entry side: transitions at |V| ≥ 4 (D19/D20),
survival holds (D20), unanimity (D21-A — the poorest slice,
+₹3.11 / −₹4.01 stream gross), and three allocation rules
(chronological-volume, quiet, strength-priority — the last
inverting the taken-slice gap by year) are all measured.
The family's taken books have never grossed above +₹26.08
per trade in any year against the ₹40 levy. One dial has
not moved since Design 19: **the exit's stop distance.**
In every vote-family book the flat −1.0% stop fires on
35–41% of positions at −₹784…−₹853 each — the exact
counterweight to the drift (+₹504.14 per square-off in
T20-A). The continuation family already showed a stop
ruler is a real, measurable dial: in Design 15 the
range-scaled stop (1.5 × the signal bar's own range)
cheapened each stop by ~₹260 (−₹593.05 vs the flat −1%'s
−₹852.56) — on excursion entries. It has never been tried
on vote entries. Design 22 tries exactly that, and
nothing else.

**Basis:** equity cash, PROVISIONAL per 100 shares,
₹40/trade, paper only, real money ₹0. No stock options.
Research only — nothing armed, no paper run started, no
live book touched.

**Universe / data:** the 127 Round-6-verified F&O names
(`tarang6_verify.json` verified_universe), via
`tarang6_score.load_name6` (the Design 19/20/21 route);
missing volume prints count as 0 (the family's standing
convention). Data runs 2025-01-01 → 2026-11-13.

## S.1 Vote state and transitions — frozen as Designs 19/20/21

The six-vote state V (RSI(14) zone, MACD hist sign,
Supertrend(7, 3.0), ADX(14) trend sign vs EMA-50, EMA 9/21
alignment, Bollinger %B side, net in −6..+6) is computed
**exactly** as in `tarang19_SPEC.md` S.1, including
Amendments A1/A2. The Design 19 scorer's engine and
validator indicator stacks are imported unchanged; no vote
definition moves in this design.

A **LONG transition** fires at bar g if V(g) and V(g−1)
are both defined, V(g−1) < +4 and V(g) ≥ +4. A **SHORT
transition** fires if V(g−1) > −4 and V(g) ≤ −4. Each
transition carries **strength** = |V(g)| ∈ {4, 5, 6} and
**vol_ratio** at the signal bar = vol[g] /
mean(vol[g−19..g]) (0 if the mean is 0) — both exactly as
Design 20 SPEC S.2.

## S.2 Candidate generation — frozen as T20-A

Candidate generation is the family's per-name chronological
simulation (Design 20 SPEC S.2, T20-A form): the name
starts flat; while flat, the first actionable transition
opens a position; while a position is open, transitions
are ignored; after an exit whose fill bar is f, scanning
resumes at bar f. The entry fills at the **open of bar
g+1**, which must be in the same session and stamped in
**[09:30, 14:30]**; a transition whose entry bar falls
outside the window is a non-event (the name stays flat,
scanning continues). Re-entry on a fresh transition after
a close is part of the design. No survival pre-filter, no
strength gate. Because exits change in this design (S.3),
the blocking structure — and therefore the candidate set —
differs from T20-A's; that is expected and is part of what
is measured.

## S.3 Exits — ONE change vs T20-A: the stop distance

No vote-decay. Evaluated bar by bar from the entry bar e
to the day's square-off bar sq (the last bar stamped
≤ 15:15, the family `day_maps` construction), in this
order at each bar j:

1. **Disaster stop — RANGE-SCALED (the change):** the stop
   distance is **dist = 1.5 × rng**, where **rng** is the
   transition bar's own range, rng = high(g) − low(g) at
   the signal bar g, **rounded to 4 decimals at the
   source** (prices are 2-decimal; Design 15's disclosed
   float-dust fix — an exact touch is a fill under the
   family's ≤ convention). Stop level = entry − dist
   (LONG) / entry + dist (SHORT), measured from the entry
   price. If the bar's open is beyond the stop, fill at
   the open; else if the bar's range touches the stop
   (low ≤ stop for LONG, high ≥ stop for SHORT), fill at
   the stop. Reason `stop`. (Fill mechanics are T20-A's,
   unchanged; only the level moves.)
2. **Square-off:** if j = sq, fill at close(sq). Reason
   `squareoff`.

Net per trade = side × (exit − entry) × 100 − ₹40.

## S.4 The book — ONE book, everything else frozen

**TARANG-T22** = T20-A with the S.3 stop. Caps: **1 open
position per name** (no overlap of taken [entry, exit]
bar spans for a name), **2 entries per name-day**,
**10 entries per book-day**; a skipped candidate does not
regenerate later candidates. Allocation — **A4
volume-priority (frozen)**: the family's greedy
chronological allocator (Design 19 SPEC S.4): sort key
(date, entry_time, vol_ratio DESC, strength DESC,
signal_time, sym).

## S.5 Controls (all pre-registered; any failure aborts or fails the audit leg)

1. **EKAM machinery control (reported FIRST, before any
   D22 number):** EKAM's own vote machinery (imported
   `ekam_intraday_stocks_build` +
   `ekam_intraday_stocks_r2_build.exit_x2p`, via the Design
   19 scorer's control) run on the frozen 25 under EKAM's
   09:15 configuration must reproduce the published
   **CAND-T5** Jan–Oct lines **+₹62,164.57 (2025) /
   +₹63,883.60 (2026)** and **S2** lines **+₹45,300.64 /
   +₹72,605.30**, exact to ±₹0.05 per line. If either line
   misses, no D22 number is quoted. Companion parity: the
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
   transition set with matching V values; **the stored
   transition-bar range re-derived from the day's bars and
   matched**; exit re-simulated on the trade's own day by
   an independent exit implementation (with the range
   re-derived, not read from the trade) and matched on
   bar, price and reason; square-off price = close(sq);
   net recompute; caps (≤2/name/day, ≤10/day, no same-name
   overlap); a full independent allocator rebuild
   (validator transitions + audit exits + A4 allocation)
   matched trade-for-trade.
4. **Truncation spot-check:** 30 sampled taken trades;
   indicators and V recomputed from the series truncated
   at the signal bar must reproduce V(g) and V(g−1)
   exactly (the Design 19 check, unchanged).
5. **Placebos:** (a) 200-draw random-entry placebo with
   the book's OWN exits (S.3) — same names/days, the
   book's own entries-per-day counts, random eligible bars
   in [09:45, 14:45] (the family's standing placebo
   window), random side, identical caps. **A random entry
   has no transition bar; its range-scaled stop uses its
   ENTRY bar's own range × 1.5 — the causal analogue,
   exactly as pre-registered in Design 15 S.5.3.**
   Percentile of the real net within the draws, per year.
   (b) Direction-flip placebo (information): the taken
   trades with sides flipped and exits re-simulated (each
   flipped trade keeps its own transition bar's range).
6. **Independent re-sum** of the written trades CSV
   against the engine nets, to the paisa.

## S.6 Gate (unmoved — `tarang2_score.gate_for`)

Net positive BOTH years · beats the random-entry placebo
p90 BOTH years · ex-top-3 positive BOTH years · no month
worse than −₹15,000 · November 2026 slice (Nov 1–13) ≥
−₹3,000 · audits clean (S.5.2–S.5.4 all zero). Nine legs.

## S.7 Anatomy (the seed's questions)

Report: every gate leg; placebo percentiles; side splits;
halves; win rate; max drawdown; month table; top-10
contributors; gross/cost/net per trade
(`tarang9_score.cost_anatomy`); the RAW candidate stream
under this book's own entry/exit rules (trades, gross ₹,
gross/trade) beside the taken book's; and the **stop
anatomy head-to-head vs T20-A** (published: stop share
41.2% — 1,911 stops at −₹813.52 each, net −₹15,54,645.34;
square-off 58.8% — 2,725 at +₹504.14 each, net
+₹13,73,777.00; book nets −₹34,649.28 / −₹1,46,219.06;
percentiles 92.0 / 3.5; worst month Jun 2025 −₹49,558.95):
stop count/share, per-stop net, square-off count/share
and per-trade net, plus the stop-distance distribution
(dist as % of entry price: mean, median, share of taken
trades where the ruler is tighter than the flat 1% vs
wider). The question Design 22 answers: **does the
range-scaled ruler cheapen vote-entry stops the way it
cheapened excursion stops in Design 15 — and does the
cheapening survive to the book's net, or does the wider
tail (stops beyond 1%) tax the drift as Design 16's
window-range ruler did?** If the ruler also fails, the
vote family joins the excursion family as
measured-exhausted, and Design 23's seed (S.8) applies.

## S.8 Design-23 seed (pre-registered fork)

If T22 fails the gate: the next family is chosen by
**stream gross first** — a survey of candidate signal
families scored on RAW STREAM GROSS ONLY (uncapped
candidate stream, per-trade gross vs the ₹40 levy, both
years) before any book, filter, gate or allocator is
built on any of them. No family gets a book until its raw
stream clears ₹40 in both years.
