# Stocks EQUITY — CANDIDATE SPEC — T2-A POOLED (P2F magnitude bands, 50 stocks)

**FROZEN 2026-10-31 from Line T2 (`stocks_T2_frozen.md`,
`stocks_T2_report.md`, engine `stocks_T2.py`). CANDIDATE ONLY —
not adopted. Judged on FRESH December 2026 data under the rule
below. November's frozen systems (N4-V3 primary, P2F shadow at
2.0% / R+1 / home 25) are NOT changed by this spec.**

**EQUITY CASH intraday only. LONG/SHORT language only — no
options, no premiums. Paper only, no orders. Real money: ₹0.
Every rupee figure: provisional per 100 shares, ₹40/trade
flat cost.**

## The rule — exact

Identical to the frozen P2F rule
(`stocks_p2f_november_shadow_spec.md`) with exactly two
changes: **universe = 50 stocks** (HOME 25 watchlist + EXT 25
large caps) and **reaction threshold = 3.0%** (primary
variant) / **4.0%** (co-frozen nested variant).

1. **Event population — RESULTS EVENTS ONLY**, from the event
   calendars (December: built from exchange filings the same
   way as the Jan–Oct calendars; only an actual results
   announcement creates an event).
2. **Reaction day R:** the calendar `reaction_date` when
   announcement ≤ reaction_date ≤ announcement + 7 days,
   otherwise the announcement date. After-hours / weekend
   announcements react on the next trading day.
3. **Reaction return:** close(R) / close(previous trading
   day) − 1, %, rounded to 2 dp. Candidate iff
   **|return| ≥ 3.00%** (primary) / **≥ 4.00%** (variant) AND
   R+1 exists.
4. **Direction:** sign of the reaction return (LONG if
   positive, SHORT if negative).
5. **Entry:** open of the 09:15 bar of R+1. One trade per
   qualifying event; no caps, no filters, no re-entry.
6. **Exits T125:** target +1.25% / stop −0.5% from entry
   (mirrored for SHORT); exit scan starts on the bar after
   the entry bar; stop checked before target within a bar;
   else exit at the close of the 15:10 bar (or last bar
   ≤ 15:10). Net = sign × (exit − entry) × 100 − ₹40.
7. **Corporate-action artefacts** are traded and flagged, not
   excluded (verbatim P2F rule).

The 4.0% variant's population is a strict subset of the 3.0%
population. They are **nested variants, not two discoveries**;
the 3.0% variant is the primary candidate and is judged
first.

## In-sample evidence (Jan–Oct 2026, discovery — not proof)

| Variant | Universe | Trades | Net ₹ | Exp ₹ | H1 ₹ | H2 ₹ | Oct ₹ | Breadth | Top-3 |
|---|---|---|---|---|---|---|---|---|---|
| 3.0% | POOLED 50 | 66 | +31,719.61 | +480.60 | +17,391.09 | +14,328.52 | +2,547.21 | 24/50 | 50.1% |
| 4.0% | POOLED 50 | 45 | +17,374.45 | +386.10 | +13,779.22 | +3,595.23 | +4,356.38 | 19/50 | 75.0% |
| 3.0% | HOME 25 | 33 | +14,231.75 | +431.27 | +6,720.88 | +7,510.87 | **−315.00 (2 trades)** | 11/25 | 97.5% |
| 4.0% | HOME 25 | 22 | +8,399.06 | +381.78 | +7,383.06 | +1,016.00 | **−132.00 (1 trade)** | 10/25 | 112.8% |

### Mandatory disclosures

- **Selection history:** the 3.0%/4.0% thresholds were
  pre-declared in Line 3 (V2) and already known to pass on
  HOME before T2 ran. The POOLED scoring (EXT 25 events) is
  new evidence; the threshold choice was not blind.
- **HOME fails the T2 gate at both bands** — on October
  samples of 2 and 1 trades. The pooled pass leans on EXT
  names (EICHERMOT is the pooled top payer at 3.0%). A
  home-only December reading is part of the judging record.
- The pooled 4.0% expectancy (+₹386.10) sits **below** the
  base P2F-2.5% home expectancy (+₹397.16); the frozen T2
  gate did not apply the expectancy leg to pooled cells.
  Recorded, not hidden.
- In-sample the SHORT tilt persists on HOME but pooled both
  directions pay at 3.0% (LONG +₹16,032.35 / SHORT
  +₹15,687.26). The rule trades both directions; no
  direction split may be applied after the fact.

## December 2026 judging rule — pre-registered

Judged once, after the last December trading day, per variant
(3.0% primary first), on the pooled-50 December sample at
T125, with an entry-timing audit (every entry's information —
the reaction-day close — complete before the entry) run in
the same pass:

- **December net positive with ≥ 8 trades and a clean audit:**
  the variant is a **confirmed candidate** — it earns a
  further frozen decision (e.g. a second fresh window or a
  combined event-book composition test). It is NOT adopted
  on one fresh month.
- **December net negative with ≥ 8 trades:** the variant is
  **killed** — recorded as a Jan–Oct in-sample artefact, no
  re-tuning, no threshold change after the fact.
- **Fewer than 8 qualifying events in December:** inconclusive
  — the test extends to January 2027 under these same frozen
  rules, judged on the combined sample against the same bar.
- **Net exactly ₹0 with ≥ 8 trades:** inconclusive, extends
  as above.
- If the 3.0% variant is killed and the 4.0% variant passes,
  the 4.0% result is recorded but **cannot upgrade alone** —
  a nested subset outliving its parent on one month is a
  selection pattern, not evidence; it extends one more window
  before any confirmation.

**No parameter changes during December.** Observations may be
logged; they change nothing until the month-end judgement.
