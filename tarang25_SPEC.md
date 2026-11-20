# TARANG Design 25 — THE GAP-FADE BOOK, FULL GATE — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 25 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run
started, no live book touched. **A gate pass earns forward
paper only on the owner's explicit word.**

## S.0 Why this design

Designs 23–24 surveyed raw signal streams on stream gross
alone (the Design 22 seed's method: no family earns a book
until its raw stream clears the ₹40/trade levy in BOTH
years). Three gap-fade streams passed — the first survey
pass in twenty-four designs:

| Stream | 2025 g/t | 2026 g/t | Trades |
|---|---|---|---|
| GAP-FADE-15 (\|gap\| ≥ 1.5%) | +469.36 | +65.20 | 4,111 |
| GAP-FADE-20 (\|gap\| ≥ 2.0%) | +621.15 | +149.67 | 2,408 |
| GAP-FADE-UP-15 (up ≥ 1.5%) | +220.25 | +74.10 | 2,181 |

The threshold ladder is monotonic in both years: the
money is in the LARGE gaps; small gaps dilute (and invert
the down side at 1%). Design 25 builds the book the survey
earned: the three streams as three books, mechanics frozen
from the survey, with the one layer the survey
deliberately omitted — caps and allocation — added under
pre-registration (S.4), and the programme's full unmoved
9-leg gate (S.6) as the only verdict.

## S.1 Basis and universe

Identical to Designs 23–24: equity cash, PROVISIONAL per
100 shares, ₹40/trade cost levy, paper only, real money
₹0. No stock options. Universe: the 127 verified F&O
names of Designs 7–24, 5-min bars from the same stores
(`tarang6_score.load_name6` via `tarang23_score.prep`),
2025-01-01 to 2026-11-13. Years by trade date; 2026 runs
to the store's end (2026-11-13).

## S.2 Signal — frozen from D23 S.3.4 / D24 S.3

Bars are 5-minute bars timestamped by bar start. For each
name-day after the name's first store day:

**gap% = (today's first-bar open / previous trading day's
last bar close) − 1**, the previous trading day being that
name's previous day in the store. A name's first store day
has no previous day and produces no candidate (counted).

The fade direction: gap up → SHORT, gap down → LONG.
There is exactly ONE candidate per qualifying name-day
(the gap is a day-level event; the survey's
first-signal-per-name-day rule is structural here).

## S.3 The three books — mechanics frozen from the survey

- **TARANG-T25-A (primary)** — GAP-FADE-15: |gap%| ≥ 0.015,
  both sides.
- **TARANG-T25-B** — GAP-FADE-20: |gap%| ≥ 0.020, both
  sides.
- **TARANG-T25-C** — GAP-FADE-UP-15: gap% ≥ +0.015 only,
  SHORT only.

**Entry:** the day's first-bar open (bar local 0 — the gap
is known at the open). **Exit — the survey's ONE standard
exit, unchanged** (`tarang20_score.exit20_engine`):
disaster stop at entry × 0.99 (LONG) / entry × 1.01
(SHORT), stop-first, a bar that opens through the stop
fills at the bar's open, otherwise exit at the CLOSE of
the square-off bar (the day's last bar with timestamp
≤ 15:15). The exit scan starts at the entry bar itself.

**Money:** gross = (exit − entry) × side × 100 shares;
net = gross − ₹40. Win rate = share of trades with
net > 0.

## S.4 Caps and allocation — the layer the survey omitted

- **Caps:** at most **10 taken trades per book-day**; at
  most **1 per name-day** (structural, S.2). No other
  caps. A candidate not taken is simply not taken — it
  does not defer or regenerate (each name-day's candidate
  is a standalone trade whose entry/exit do not interact
  with any other name's, so the taken set is a pure
  subset of the survey stream).
- **Allocation:** on a day whose candidates exceed the
  slots, rank candidates by:
  1. **|gap%| DESC** (exact float — the threshold ladder
     says gap size is the quality axis);
  2. **vol_ratio DESC** — the family formula at the
     signal bar: the signal bar is the day's first bar
     (global index g in the name's series);
     vol_ratio = vol[g] / mean(vol[g−19..g]), 0 if the
     mean is 0;
  3. **chronology** — the candidate's position in the
     verified-universe list order, ASC.
  Take the top 10.
- **Disclosure (pre-registered):** key 1 is causal at the
  open. Key 2 uses the first bar's completed volume and
  can bind only on an exact-float |gap%| tie. The audit
  (S.5.4) counts the cap-boundary decisions key 2 actually
  decided and re-runs the allocation with key 2 removed;
  any taken-set difference is reported, not hidden.

## S.5 Controls and audits (any failure aborts or fails
the audit leg)

1. **EKAM machinery control FIRST** —
   `tarang19_score.ekam_control()`: EKAM's own imported
   machinery on the frozen 25 must reproduce the
   published CAND-T5 (+₹62,164.57 / +₹63,883.60) and S2
   (+₹45,300.64 / +₹72,605.30) Jan–Oct lines exactly,
   before any Design 25 number is quoted.
2. **Candidate-pool parity (two independent checks):**
   (a) each book's candidate set (sym, date, side) equals
   the corresponding stream's set in the independent
   pandas-path validator (`tarang24_score.
   validator_sigset`, GAPW2 mode) exactly; (b) every
   candidate's standalone trade (entry, exit, reason,
   gross, net) matches the published Design 24 survey
   trade for that (stream, sym, date) in
   `tarang24_trades_GAPW2.csv` exactly — the capped book
   must be a pure subset of the audited survey stream,
   with identical per-trade economics.
3. **Exit parity** — every taken trade's exit
   re-simulated by the independent audit exit
   (`tarang20_score.exit20_audit`); 0 mismatches on bar,
   price and reason.
4. **Allocation audit** — an independent rebuild of each
   book's taken set from the validated candidate pool
   (fresh ranking implementation of S.4) matched
   trade-for-trade; caps verified (≤10/day,
   ≤1/name-day); the S.4 key-2 decisiveness count and
   the no-key-2 sensitivity re-run reported.
5. **Timing/leak audit** over every taken trade: entry
   local == 0 and entry price == the day's first-bar
   open; gap% recomputed from the stored bars (today's
   first open, the name's previous store day's last
   close) matches the candidate's; no trade on a name's
   first store day; exit re-simulation (S.5.3); net
   recompute.
6. **Truncation spot-check** — 30 sampled taken trades:
   the signal recomputed from the previous day's bars
   plus today's first bar only must reproduce the
   candidate with identical side (no look-ahead — the
   gap uses nothing beyond the first open).
7. **Placebos:** (a) 200-draw random-entry placebo with
   the book's OWN exits (the family's standing
   construction, D15 S.5.3 / D22 S.5.5a): same dates and
   the book's own entries-per-day counts, random names
   from the 127, random eligible bars in the family
   placebo window [09:45, 14:45], random side, exit by
   `exit20_audit` (the book's flat −1% stop form —
   no range term exists in this book), caps identical
   (≤1 entry per name-day, no same-name overlap).
   Percentile of the real net within the draws, per
   year; the gate leg reads the draws' p90.
   (b) Direction-flip placebo (information): the taken
   trades with sides flipped, exits re-simulated.
8. **Independent re-sum** — the written
   `tarang25_trades.csv` re-sums to every reported net
   per book per year to the paisa.

## S.6 Gate (unmoved — `tarang2_score.gate_for`)

Per book, all nine legs: net positive BOTH years · beats
the random-entry placebo p90 BOTH years · ex-top-3
positive BOTH years · no month worse than −₹15,000 ·
November 2026 slice (Nov 1–13) ≥ −₹3,000 · audits clean
(S.5.2–S.5.6 all zero). PASS requires all nine.

## S.7 Anatomy (reported per book)

Every gate leg; placebo percentiles and p90s; flip
placebo; side splits (trades and net, LONG/SHORT, per
year; gross/trade by side); win rate; trades and trading
days (the family is episodic — also candidate days and
days the cap bound); max drawdown; month table; top-10
contributors per year; gross/cost/net per trade
(`tarang9_score.cost_anatomy`); resolution mix (stop /
square-off counts, nets, per-trade, per year); and the
**capped-vs-survey comparison** per book per year: survey
stream trades / gross / gross-per-trade (Design 24
published) vs the capped book's, the share of stream
trades taken and the share of stream gross kept. The
question Design 25 answers: **does the first stream in
the programme that pays for itself survive contact with
a book — caps, allocation, concentration, placebo,
November — under the full unmoved gate?**

## S.8 What this design does not do

No new signal, no exit variant, no threshold change, no
per-name tuning. The three books differ only in their
pre-registered survey streams. Nothing is armed; no
paper run is started by this design under any outcome.
