# Stocks EQUITY — INV family TUNING spec — FROZEN before scoring (2026-10-31)

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0.**
**Every rupee figure: provisional per 100 shares. Gross = before
the frozen ₹40/trade flat cost; net = gross − ₹40/trade.
Window: Jan–Oct 2026 (October = 1–28 Oct), 25 watchlist stocks.**

## What this is — and what it is NOT

This is the INV-line tuning loop (v2 candidates). It does **NOT**
touch the frozen November shadow: INV1 runs in November exactly
as frozen in `stocks_p2inv_november_shadow_spec.md`. Anything
that passes here is a **v2 candidate only**, earning a further
frozen decision later — never adoption, never a November change.

**Base definition (unchanged from Rounds 8–10):**
- **Signal stream:** frozen V5 re-entry stream of
  `stocks_equity_reentry.py` (`pool_pick` over v4 + skill_or
  detectors), chains rebuilt per exit specification exactly as
  `stocks_equity_round8.py: run_chain` does (next signal search
  starts at the previous trade's exit candle; one open position
  per stock at a time; chain `round` = sequence number within
  the stock-day under that exit's own timing).
- **P2 pool filters:** chain round ≤ 2; entry_time < 10:30;
  ADR≥3% stock-day (ADR = prior-10-trading-day mean of
  (high−low)/close×100, min 5 prior rows, trade day excluded —
  Round 8 `adr_map`, verbatim).
- **INV1 condition:** Nifty previous close ≤ its 50DMA, where
  previous close and 50DMA use Nifty daily bars strictly before
  the trade day (50DMA = mean of the 50 closes ending at the
  previous bar; Round 9 `regime_maps` convention). Equality =
  condition met.
- **Baseline exits:** T125/S050 (target +1.25% / stop −0.5%)
  primary; T10/S050 secondary. Plain-exit replay: stop-first on
  a same-candle tie, else 15:10 square-off at candle close
  (Round 8 `replay_plain`, verbatim).

**Validation gate (must pass before any family is scored):**
rebuilt machinery must reproduce, to the paisa —
- P2 pool at T125/S050: 918 trades, net +₹10,657.81.
- INV1 at T125/S050: 694 trades, net +₹22,964.30, halves
  Jan–May +₹7,255.01 / Jun–Oct +₹15,709.29.
- INV1 at T10/S050: 721 trades, net +₹19,232.08, halves
  −₹517.74 / +₹19,749.82.
- INV2-condition subset at T125/S050: 563 trades, net
  +₹48,437.14, halves +₹24,913.18 / +₹23,523.96.
If the gate fails, scoring stops and the failure is reported.

**Pass gate for a v2 candidate (all must hold):** net > 0 in
BOTH halves at ₹40/trade **and** breadth ≥ 10 of 25 stocks
net-positive over Jan–Oct **and** positive net expectancy
(net/trade > 0). Breadth reported for every configuration as:
count of net-positive stocks (of 25) and top-3 share = sum of
the three largest positive per-stock nets ÷ Jan–Oct total net
×100 (can exceed 100% when the remaining stocks are net-negative
in aggregate; reported as-is).
Baseline INV1/T125 breadth for reference: 10/25, top-3 share
141.0% (TVSMOTOR, BDL, ASTRAL).

**Discipline:** one structural change per family; every
configuration scored on the full Jan–Oct window with halves
reported; no per-trade hindsight filters; rejected variants are
reported with their numbers, not hidden. Direction splits and
condition variants are row filters on chains built under the
stated exit (the Round 9/10 methodology) — chains are never
rebuilt direction-only.

---

## Family T1 — EXIT LADDER on INV1

Chains rebuilt per cell; INV1 condition and P2 filters unchanged.
Grid: targets {1.0, 1.25, 1.5, 1.75, 2.0}% × stops
{0.5, 0.65, 0.8}%, plain replay, stop-first, 15:10 square-off.
All 15 cells reported (trades, win%, gross exp, net expectancy,
net Jan–May / Jun–Oct / Jan–Oct / Oct, breadth). Cells ranked by
the weaker half's net (min-half), tie-break total net; best 3
carried to T3/T4. Question: does any cell keep both halves
positive with better balance than T125/S050?

## Family T2 — TRAIL EXIT on INV1

Two trailing variants, no fixed target, initial stop −0.5%,
15:10 square-off, P2 filters + INV1 condition unchanged:
- **TR-A:** activate +0.75%, trail 0.4%.
- **TR-B:** activate +1.0%, trail 0.5%.
Frozen trail mechanics (no intra-candle look-ahead): candles
processed in order starting at the entry candle. On each
candle, FIRST check the stop in force at the start of that
candle (initial stop until the trail is armed; thereafter the
trailing level) — LONG: candle low ≤ stop → exit at the stop
level (`stop` if initial, `trail_stop` if trailing);
SHORT mirrored on the high. THEN update the running favourable
extreme with this candle's extreme (high for LONG, low for
SHORT); if the extreme has reached the activation level, the
trailing stop for SUBSEQUENT candles becomes extreme ×
(1 − trail%) for LONG / extreme × (1 + trail%) for SHORT,
ratcheting only in the favourable direction. If no stop is hit
on the 15:10 candle, square off at its close.

## Family T3 — DIRECTION split

INV1 LONG-only and INV1 SHORT-only (row subsets of the same
chains — Round 10 A4 methodology), scored at: T125/S050, plus
the best 3 cells of T1 (deduplicated if T125/S050 is among
them). Question: does LONG-only cure the T10 Jan–May flip
(INV1 T10 Jan–May = −₹517.74) and what does each direction do
across the ladder's best cells?

## Family T4 — CONDITION VARIANTS

Applied to the P2 pool (row filters), each at T125/S050 and at
T1's best cell (by min-half net):
- **(a) N20:** Nifty previous close ≤ its 20DMA (the INV2
  condition, now also re-scored at the best ladder cell).
- **(b) DBL:** Nifty previous close ≤ its 50DMA AND the traded
  stock's own previous close ≤ its own 20DMA (direction-neutral,
  both computed from bars strictly before the trade day).
- **(c) BAND:** Nifty previous close ≤ its 50DMA AND Nifty is
  no more than 3% below it: (50DMA − prev close)/50DMA ≤ 0.03
  (below-trend but not in freefall).

## Family T5 — FEBRUARY DIAGNOSIS (report only, NO filter built)

INV1 February 2026 trades at T125/S050 (known going in: 124
trades, net −₹21,123.92 — LONG 39 / −₹9,951.91, SHORT 85 /
−₹11,172.01). Decompose and compare against INV1's other
Jan–May months and its Jun–Oct trades, in numbers: direction
split, chain-round split, entry-gap distribution (day open vs
previous close, signed %), ADR distribution, per-stock table,
win% / gross expectancy per cut, exit-reason mix. State what
distinguishes February. **No February filter is built** — a
pattern feeds T6 only if it is an ex-ante feature (knowable
before the trade), and any such use must be declared.

## Family T6 — CHAIN / ENTRY STRUCTURE

On INV1 at T125/S050: chain cap {1, 2, 3} × entry cutoff
{10:30, 11:30} — row filters on the full uncapped T125 chain
(round ≤ cap, entry_time < cutoff), ADR≥3% and INV1 condition
unchanged. 6 cells, both halves + breadth each. (Cap/cutoff
filtering of the uncapped chain is identical to building with
the cap, because signal search depends only on exit timing —
the Round 8 `pools` methodology.)

---

---

## Line 1b — STRESS-TEST of INV-LONG + DBL near-miss (appended 2026-10-31, frozen before scoring)

Same basis, same pass gate, same machinery as Line 1. Row operations
only on the cached chains (`tuning_inv_cache/`); no chain is rebuilt,
no parameter of any Line 1 configuration is changed. INV-LONG below
means exactly the Line 1 T3 configuration: INV1 condition + P2 pool +
LONG-only rows of the T125/S050 chains (249 trades, +₹24,185.73,
halves +₹14,751.12 / +₹9,434.61, breadth 12/25). Anchor checks before
scoring: the script must reproduce those INV-LONG figures and the
Line 1 T4 DBL figures (390 trades, +₹16,548.78, halves +₹7,861.57 /
+₹8,687.21, breadth 9/25) to the paisa, or Line 1b stops.

### Family S1 — INV-LONG concentration stress (accounting only, no new trades)

- **(a)** INV-LONG excluding all TVSMOTOR rows.
- **(b)** INV-LONG excluding all GLENMARK rows.
- **(c)** INV-LONG excluding both TVSMOTOR and GLENMARK rows.
- **(d)** Winsorised: each stock's Jan–Oct net contribution capped
  at +₹2,000 (per-stock nets above +₹2,000 counted as +₹2,000;
  negative per-stock nets unchanged). Headline winsorised total
  = Σ over 25 stocks of min(per-stock net, +₹2,000). Winsorised
  halves computed the same way per half (Σ over stocks of
  min(per-stock half net, +₹2,000)); capped halves need not sum
  exactly to the capped total — reported as computed. Breadth
  under (d) is unchanged by construction (a positive cap cannot
  change a stock's sign) and is reported as such.
- Each variant reported with: trades, win%, net expectancy, net
  Jan–May / Jun–Oct / Jan–Oct / Oct, breadth (positive-stock count;
  denominator 25 throughout, exclusions noted), top-3 share.
- **Pre-declared S1 verdict rule:** the candidate **stands** if
  (c) AND (d) both keep both halves net-positive with positive
  expectancy; **stands weakened** if (c) and (d) totals stay
  positive but any half is ≤ 0; **falls** if (c) or (d) total
  is ≤ 0.

### Family S2 — DBL LONG-only

DBL condition (Line 1 T4 definition, unchanged) + P2 pool +
LONG-only rows. Primary exit T125/S050; shadow exit T100/S050
(row filter on that cell's chains). Full gate report each
(trades, win%, expectancy, halves, October, breadth, top-3
share, pass gate). This is the one structural step from the
recorded DBL near-miss that Line 1 itself proved on INV1
(LONG-only cured INV1's T10 flip); no other change.

### Family S3 — DBL both-directions at friendlier exits

DBL condition + P2 pool, both directions, at T100/S050 and at
T125/S065 (the two other cells that passed for INV-LONG in
Line 1 T3). Full gate report each. Question: does either cell
lift DBL's breadth to ≥ 10/25 while keeping both halves
net-positive — i.e. pass the full gate?

### Family S4 — INV-LONG month table

INV-LONG rows grouped by calendar month Jan–Oct 2026: trades
and net per month, cumulative net. Flag any month with net
< −₹3,000. Report the top-2 months' share = sum of the two
largest monthly nets ÷ Jan–Oct total net × 100 (as-is, can
exceed 100% if other months are net-negative in aggregate).

### Line 1b outputs

- Report section appended to `stocks_tuning_inv_report.md`;
  numbers merged into `stocks_tuning_inv_results.json` under
  `families.L1b`; trade CSVs dumped for S2/S3 configurations
  (`tuning_inv_L1b_<label>_trades.csv`).
- If (and only if) S2 or S3 passes the full pass gate:
  `stocks_dbl_candidate_spec.md` freezing the passing
  configuration as an additional v2 candidate, with per-stock
  concentration disclosures. Otherwise no DBL spec is written.
- The November INV1 shadow is unaffected either way.

## Outputs

- This frozen spec: `stocks_tuning_inv_frozen.md`
- Report (written incrementally per family):
  `stocks_tuning_inv_report.md`
- Engine: `stocks_tuning_inv.py`; results:
  `stocks_tuning_inv_results.json`; chain cache:
  `tuning_inv_cache/`; trade CSVs for any passing
  configuration: `tuning_inv_<label>_trades.csv`
- If (and only if) a configuration passes the pass gate:
  `stocks_inv_v2_candidate_spec.md` freezing it as a v2
  candidate. The November INV1 shadow is unaffected either way.

Stage work only. Nothing here is adopted; nothing here is a
live-trading instruction.
