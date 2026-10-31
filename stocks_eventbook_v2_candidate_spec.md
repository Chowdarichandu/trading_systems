# Stocks EQUITY — CANDIDATE spec — EVENT BOOK v2 (N4-V3 + P2F combined)

**Status: CANDIDATE, frozen 2026-10-31 from tuning loop LINE 3
family V1, which PASSED the frozen gate in-sample. A candidate
is NOT an adopted system. It earns a fresh-window paper test,
judged there, and nothing more.**

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**

**Relationship to November:** the November paper tests already
frozen — N4-V3 primary (`stocks_n4_november_paper_spec.md`)
and P2F shadow (`stocks_p2f_november_shadow_spec.md`) — are
UNCHANGED and run as-is. This candidate combines their two
legs into one book for the NEXT window (December, or as the
main thread decides), and November's per-leg verdicts are the
first fresh evidence about it. If either leg is killed by its
November judging rule, this candidate dies with it.

## The candidate rule — exactly as scored in V1

The Event Book v2 is a two-leg book. Both legs are taken on
every qualifying event; there is no de-duplication, no
portfolio cap, no direction filter, and the legs never share a
trade date for the same event (leg A trades the reaction day,
leg B trades the next day).

**Leg A — N4-V3 (reaction day), exactly per
`stocks_n4_november_paper_spec.md`:** results + single-news
events; reaction day R per that spec; trigger |close of 09:25
bar ÷ previous close − 1| ≥ 1.0%; direction = sign of the
move; entry = close of the 09:30 bar (recorded 09:35); exit
T125 (target +1.25% / stop −0.5%, stop before target, scan
from the next bar, 15:10 square-off).

**Leg B — P2F (follow-through day), exactly per
`stocks_p2f_november_shadow_spec.md`:** RESULTS events only;
|reaction-day return| ≥ 2.00% (close(R)/close(prev trading
day) − 1, rounded to 2 dp); direction = sign of the reaction
return; entry = open of the 09:15 bar on R+1; exit T125 as
above. Corporate-action artefact days are traded and flagged,
per that spec — no silent exclusions.

**Book accounting:** each leg's trade is a trade of the book
(₹40 per leg-trade). Book net = sum of leg nets. Max 1 trade
per stock per event per leg; all qualifying events taken.

## In-sample evidence (Jan–Oct 2026 — discovery, not proof)

Scored in `stocks_tuning_event_report.md` (family V1), anchors
reproduced exactly before scoring:

| Event Book v2 (T125) | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Leg A (N4-V3) | 56 | 37.5 | +7,990.43 | +142.69 | +5,155.13 | +2,835.30 | — |
| Leg B (P2F) | 48 | 45.8 | +12,835.88 | +267.41 | +3,498.10 | +9,337.78 | — |
| **Book** | **104** | **41.3** | **+20,826.31** | **+200.25** | **+8,653.23** | **+12,173.08** | **13/25** |

Mandatory disclosures (part of this freeze):

- **43 of leg B's 48 events are also leg-A events** — the legs
  are consecutive-day trades on mostly the SAME events, not
  independent samples. On those shared events the leg-A trade
  is expectancy −₹23.62 and the leg-B trade +₹244.42 (V5
  chain accounting): the book's engine is the follow-through
  day; leg A contributes mainly through its non-shared trades.
- **Concentration:** GLENMARK is +₹14,495.24 of the book's
  +₹20,826.31 (~70%). Breadth 13/25 is real, the total is not
  evenly earned.
- **The book's October slice is negative:** 10 trades,
  −₹633.52.
- Both legs are SHORT-tilted in-sample (disclosed in their own
  specs). The frozen book trades both directions anyway.

## Judging proposal for the fresh window (for the main thread to freeze)

- Run the book as ONE log for the fresh window, legs tagged,
  same frozen rules, no parameter changes during the window.
- Judge at window end on book net at T125, win %, and trade
  count together, alongside the two legs' separate verdicts.
  A positive window upgrades the book to a further frozen
  decision; a negative window kills the book (legs revert to
  their own separate judgements).

## Recorded passed variants — NOT part of the candidate rules

These were scored in the same loop and are recorded so a
future line can freeze them properly. None of them changes
this candidate:

- **P2F leg at reaction band 2.5%** (V2: 39 trades,
  +₹15,489.08, halves +₹6,702.84 / +₹8,786.24, expectancy
  +₹397.16, breadth 12/25 — passes). A supplementary
  composition check (book with leg B at 2.5%: 95 trades,
  +₹23,479.51, halves +₹11,857.97 / +₹11,621.54, breadth
  13/25) was run AFTER the families and is disclosed as a
  composition check, not a frozen family. Adopting the 2.5%
  band into the book requires its own frozen decision.
- **P2F SHORT-only** (V4: numbers pass — +₹13,109.45, both
  halves ≈ +₹6.5k) is NOT frozen and must not be treated as a
  candidate: the SHORT tilt was known before the split was
  run, so a direction-only variant now would be hindsight
  fitting.
- **V6 diagnostic:** the book's H1 losses concentrate on days
  when NIFTY closed above its 50DMA the prior day (NOT-MET
  bucket H1 −₹2,869.93 across both legs; MET bucket H1
  +₹11,523.16). A regime gate is a hypothesis for a future
  frozen test only — no gate is in this candidate.
- **Rejected in this loop:** two-day hold (NON-INTRADAY,
  buys −₹6.01 on the trades it changed), close-exit control
  (H2 collapses), P2F LONG-only (fails).

## Files

- Evidence: `stocks_tuning_event_report.md`,
  `stocks_tuning_event_results.json`,
  `stocks_tuning_event_V1_combined_trades.csv`
- Loop spec: `stocks_tuning_event_frozen.md`; engine:
  `stocks_tuning_event.py`
- Leg specs (unchanged, in force for November):
  `stocks_n4_november_paper_spec.md`,
  `stocks_p2f_november_shadow_spec.md`
