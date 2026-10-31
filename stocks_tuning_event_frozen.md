# Stocks EQUITY — Tuning loop LINE 3: the EVENT BOOK (N4-V3 + P2F) — FROZEN SPEC

**FROZEN before scoring. Families scored in order V1→V6, one
structural change at a time. No hindsight filters; rejects are
reported, not buried.**

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**

**Scope note:** the frozen November specs — N4-V3 primary
(`stocks_n4_november_paper_spec.md`) and P2F shadow
(`stocks_p2f_november_shadow_spec.md`) — are NOT changed by
anything here. This loop builds the NEXT event-book version as
candidates only.

## Common ground (frozen)

- Window: Jan–Oct 2026 (October = 1–28 Oct; 29 Oct absent from the
  cache, never a zero day). Halves by each trade's own trade date:
  H1 = trade date ≤ 2026-05-31, H2 = trade date ≥ 2026-06-01.
- Exit engine: the round-5 N4 engine (identical in
  `stocks_reaction_profiles.py`): exit scan starts on the bar
  AFTER the entry bar; within a bar the stop is checked before
  the target; else exit at the close of the 15:10 bar (or the
  last bar at/before 15:10). Primary exit **T125** (target
  +1.25% / stop −0.5%, mirrored for SHORT). Net per trade =
  sign × (exit − entry) × 100 − ₹40.
- **Anchors that must reproduce before any family is believed:**
  - N4-V3 T125 (from `eq_n4deep_v3_trades_T125_janoct.csv`):
    56 trades, net **+₹7,990.43**, halves +₹5,155.13 / +₹2,835.30.
  - P2F T125 regenerated in-engine from the calendar + caches
    using the exact frozen P2F definitions
    (`stocks_p2f_november_shadow_spec.md`): 48 trades, net
    **+₹12,835.88**, halves +₹3,498.10 / +₹9,337.78, breadth
    14/25, SHORT +₹13,109.45 / LONG −₹273.57.
- **Pass gate for every family** (at the family's declared form):
  net positive in BOTH halves at ₹40, overall expectancy > 0,
  and breadth ≥ 10 of 25 stocks net-positive (universe basis —
  untraded stocks count as not positive). A family that passes
  gets frozen as `stocks_eventbook_v2_candidate_spec.md`.
  Diagnostics (V5, V6) cannot pass or fail — they inform only.

## V1 — COMBINED BOOK (headline family)

- Book = all 56 N4-V3 T125 trades + all 48 P2F T125 trades,
  taken together, NO de-duplication, NO changes to either leg.
- Report: trades, net both halves, win %, expectancy, breadth,
  per-stock nets.
- Overlap accounting (must be reported, changes nothing):
  (a) **both-fire events** — same stock, N4-V3 trade date equals
  the P2F trade's reaction date R (P2F trades the next day, R+1);
  (b) **same-stock same-day overlaps** — any (stock, date) pair
  appearing in both legs' trade dates.

## V2 — P2F REACTION BANDS

- P2F regenerated candidates (results events, |reaction-day
  return| ≥ 2.00%, reaction return = close(R)/close(prev trading
  day) − 1 rounded to 2 dp; entry R+1 open; direction = sign of
  reaction return; T125 exits) filtered at thresholds
  |return| ≥ **2.5%**, **3.0%**, **4.0%**. Base 2.0% is the
  already-scored P2F. One change only: the threshold.
- Report per band: trades, net both halves, expectancy, breadth.

## V3 — P2F HOLD VARIANTS — ⚠ NON-INTRADAY, labelled

These variants BREAK the intraday-only convention (a position is
held overnight). They are scored ONLY so the deviation is priced
honestly; they are labelled NON-INTRADAY everywhere they appear
and cannot be adopted as an intraday system.

- **V3a two-day hold:** P2F base entries (band 2.0%). Target/stop
  prices fixed from entry (T125 levels). Scan R+1 bars after the
  entry bar with the standard engine; if no exit by the last
  R+1 bar, the position is held overnight. On R+2: first, a gap
  check on the R+2 opening bar — if its open is through the stop
  (LONG: open ≤ stop; SHORT: open ≥ stop) exit AT THE OPEN
  (`gap_stop`); if through the target (LONG: open ≥ target;
  SHORT: open ≤ target) exit AT THE OPEN (`gap_target`). Then
  scan R+2 bars with the standard stop-before-target logic;
  square-off at the 15:10 close on R+2. Cost ₹40 flat kept for
  comparability (real overnight charges would differ — flagged,
  not modelled). Candidates whose R+2 does not exist in the data
  are dropped and counted.
- **V3b control:** P2F base entries, exit at the R+1 close
  regardless (close of the 15:10 bar, else last bar ≤ 15:10) —
  no target, no stop. Intraday; the "does the exit structure add
  anything over just holding the day?" control.

## V4 — P2F DIRECTION SPLIT

- P2F base T125 trades split SHORT-only and LONG-only. Each side
  reported with trades, net both halves, expectancy, breadth
  (of that side). This is a split of a scored set, not a new
  rule — reported as a family because the user asked, and any
  direction-only candidate frozen from it must carry the
  in-sample hindsight warning (the SHORT tilt was known before
  this split was run).

## V5 — SAME-EVENT CHAIN ACCOUNTING (diagnostic)

- For every both-fire event (V1 definition (a)): the N4-V3 leg
  (trade date R), the P2F leg (trade date R+1), directions of
  each leg (they can disagree — N4 keys off the 09:30 move, P2F
  off the full-day return), each leg's net, and the 2-day chain
  net. Aggregate: chain count, chain net, chain win rate, chain
  expectancy vs each leg's expectancy over the same events.
  Informs future position sizing only — NO rule change.

## V6 — COMBINED BOOK × INV1-STYLE CONDITION (diagnostic)

- Every V1 combined-book trade is tagged by the INV1 condition
  on its own trade date D, computed ex-ante exactly as in
  `stocks_p2inv_november_shadow_spec.md`: previous close = last
  NIFTY daily close dated < D; 50DMA = mean of the 50 closes
  ending at that previous bar; condition MET ⇔ prev close ≤
  50DMA. Source: `data/progressive/NIFTY/spot_daily.csv`.
- Report the combined book split MET vs NOT-MET: trades, net
  both halves, expectancy, per leg (N4-V3 / P2F) within each
  bucket if counts allow. Diagnostic only — NO gate is adopted
  from a split alone, whatever it shows.

## Deliverables

- This frozen spec: `stocks_tuning_event_frozen.md`
- Engine: `stocks_tuning_event.py`; results:
  `stocks_tuning_event_results.json`; trade CSVs per family.
- Report, written incrementally per family:
  `stocks_tuning_event_report.md`
- On a pass only: `stocks_eventbook_v2_candidate_spec.md`.

---

# LINE 3b — STRESS-TEST OF THE EVENT BOOK CANDIDATE (appended 2026-10-31, FROZEN before scoring)

**Same common ground as Line 3** (window, halves, exit engine,
₹40/trade, provisional per 100 shares, equity cash LONG/SHORT,
paper only, real ₹0). The frozen November specs are untouched.
Line 3b does not search for a better book — it tries to BREAK
the Line 3 candidate. Families in order W1→W4. **Anchors must
reproduce first:** V1 combined book 104 trades / +₹20,826.31 /
halves +₹8,653.23 / +₹12,173.08 / breadth 13/25; supplementary
composition (book with P2F leg at 2.5%) 95 trades / +₹23,479.51
/ halves +₹11,857.97 / +₹11,621.54 / breadth 13/25.

**Pass gate (unchanged):** net positive in BOTH halves at ₹40,
overall expectancy > 0, breadth ≥ 10/25.

## W1 — CONCENTRATION STRESS (on the V1 base book, P2F leg at 2.0%)

Three accounting stresses on the SAME 104 scored trades. No
trade is re-scored; contributions are removed or capped.

- **W1a — exclude GLENMARK entirely:** drop every GLENMARK
  trade from both legs. Report trades, net both halves, win %,
  expectancy, breadth.
- **W1b — exclude the top-3 payer stocks:** the top-3 stocks by
  per-stock net in the V1 combined book (as scored in Line 3:
  GLENMARK, OBEROIRLTY, GODREJCP — the engine recomputes the
  ranking and the names actually dropped are reported). Drop
  all their trades from both legs. Same reporting as W1a.
- **W1c — winsorised contributions:** per stock PER HALF, the
  stock's net contribution within that half is capped at
  **+₹2,000** (if the stock's half-net exceeds +₹2,000 it counts
  as +₹2,000; losses and smaller gains are untouched). Totals =
  sum of the capped halves. Breadth = stocks whose capped
  full-period net is > 0. This is an accounting stress, NOT a
  trading rule — no rule could cap a stock's realised net.

**Verdict rule for the candidate (frozen):**
- **Stands:** all three stresses pass the gate.
- **Stands weakened:** W1a and W1c pass but W1b fails — the
  book is not one stock, but it IS a few-stocks book; the
  candidate survives only with that disclosure upgraded to a
  headline property.
- **Falls:** W1a fails the gate — remove one stock and the
  candidate is gone; or W1c fails both-halves — the positive
  halves are carried by uncapped winners.

## W2 — FORMALISE v2.1 (freeze + verification, no new search)

Write `stocks_eventbook_v21_candidate_spec.md` freezing the
composed book: **Leg A = N4-V3 exactly as frozen**
(`stocks_n4_november_paper_spec.md`); **Leg B = P2F at the
2.5% reaction band**, every other P2F definition unchanged from
`stocks_p2f_november_shadow_spec.md` (results events only,
reaction return = close(R)/close(prev trading day) − 1 rounded
to 2 dp, entry R+1 open, direction = sign of reaction return,
T125 exits, corporate-action artefacts traded and flagged).
Book accounting as in the v2 candidate (each leg-trade a book
trade at ₹40, no de-duplication, no cap).

The spec must carry full disclosures: in-sample composition
(this book was composed AFTER the V1/V2 families were scored —
disclosed in Line 3 as a supplementary check, frozen as a
candidate only now, in Line 3b); GLENMARK's share of the v2.1
net recomputed; the v2.1 October slice; the P2F leg's SHORT
tilt at the 2.5% band recomputed; the 43-event overlap property
recomputed for the 2.5% leg; the same fresh-window judging
proposal and the same kill-dependency (if either November leg
verdict kills its leg, the book dies with it).

**Verification (must hold exactly, else reported as a
discrepancy, not rounded away):** re-scored from the engines,
v2.1 = **95 trades / +₹23,479.51 / H1 +₹11,857.97 / H2
+₹11,621.54 / breadth 13/25**.

## W3 — V6 REGIME HYPOTHESIS FREEZE (spec only, NO scoring)

Write `stocks_eventbook_regime_hypothesis.md` freezing, for a
future fresh-window test only: **the v2.1 book traded only on
days when the INV1 condition is MET on the trade date** (NIFTY
previous close ≤ its 50DMA, exact definition as in
`stocks_p2inv_november_shadow_spec.md`, computed ex-ante per
trade date; each leg-trade judged on its own trade date).
Recorded hypothesis source (in-sample, Line 3 V6 diagnostic at
the 2.0% band): MET bucket 65 trades +₹16,551.59, both halves
positive (H1 +₹11,523.16 / H2 +₹5,028.43); NOT-MET bucket H1
−₹2,869.93. Judging language mirrors the INV1 shadow rule
(positive fresh window with a pre-set minimum trade count
upgrades the gated book to a candidate; negative kills the
gate; a window where the condition rarely triggers is
inconclusive). The document must state plainly: **hypothesis
only, untested on fresh data, no gate is adopted, November's
frozen systems are unchanged.** NO new scoring is done for W3
in this line — the v2.1 × condition split is NOT computed here.

## W4 — MONTH-BY-MONTH TABLE (v2.1 book)

Net per calendar month Jan–Oct 2026 for the v2.1 book (trade
date basis), with trade counts and a running cumulative.
Report: which months carry the book (share of total net),
**any month worse than −₹3,000** flagged by name, and the
count of negative months.

## Line 3b deliverables

- This frozen section (above).
- Engine: `stocks_tuning_event_3b.py`; results:
  `stocks_tuning_event_3b_results.json`; trades:
  `stocks_tuning_event_v21_combined_trades.csv`.
- `stocks_eventbook_v21_candidate_spec.md` (W2),
  `stocks_eventbook_regime_hypothesis.md` (W3).
- Report appended to `stocks_tuning_event_report.md` as
  Line 3b, with the candidate verdict (stands / stands
  weakened / falls) per the frozen W1 verdict rule.
