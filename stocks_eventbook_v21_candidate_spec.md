# Stocks EQUITY — CANDIDATE spec — EVENT BOOK v2.1 (N4-V3 + P2F@2.5% combined)

**Status: CANDIDATE, frozen 2026-10-31 in tuning loop LINE 3b
(family W2). A candidate is NOT an adopted system. It earns a
fresh-window paper test, judged there, and nothing more.**

**⚠ STRESS VERDICT ATTACHED (Line 3b, family W1):** the
base-form book (Event Book v2, P2F leg at the 2.0% band) was
stress-tested in the same line and **FELL** its frozen
concentration rule — capping each stock's per-half contribution
at +₹2,000 turns its Jan–May half negative (−₹1,805.21), and
removing its top-3 payer stocks turns the whole book negative
(−₹3,046.87). The stress was scored on the 2.0% form, as the
frozen Line 3b spec prescribed; this 2.5% composition was NOT
separately re-stressed, and it inherits the same concentration
structure (GLENMARK is 61.7% of this book's net — see
disclosures). Any fresh-window run of v2.1 must be read with
that verdict attached. Full stress tables:
`stocks_tuning_event_report.md`, Line 3b.

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**

**Relationship to November:** the November paper tests already
frozen — N4-V3 primary (`stocks_n4_november_paper_spec.md`)
and P2F shadow (`stocks_p2f_november_shadow_spec.md`, at the
2.0% band) — are UNCHANGED and run as-is. This candidate is
for the NEXT window (December, or as the main thread decides).
If either leg is killed by its November judging rule, this
candidate dies with it.

## The candidate rule — exactly as scored

The Event Book v2.1 is a two-leg book. Both legs are taken on
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

**Leg B — P2F at the 2.5% reaction band (follow-through day),
exactly per `stocks_p2f_november_shadow_spec.md` with ONE
change — the reaction threshold is 2.50%, not 2.00%:** RESULTS
events only; |reaction-day return| ≥ 2.50% (reaction return =
close(R)/close(prev trading day) − 1, rounded to 2 dp, the
threshold test uses the rounded value); direction = sign of
the reaction return; entry = open of the 09:15 bar on R+1;
exit T125 as above. Corporate-action artefact days are traded
and flagged, per that spec — no silent exclusions.

**Book accounting:** each leg's trade is a trade of the book
(₹40 per leg-trade). Book net = sum of leg nets. Max 1 trade
per stock per event per leg; all qualifying events taken.

## In-sample evidence (Jan–Oct 2026 — discovery, not proof)

Scored in `stocks_tuning_event_report.md` (Line 3 families V1
and V2, and the Line 3 supplementary composition check);
re-scored and verified in Line 3b family W2 — **exact
reproduction: 95 trades / +₹23,479.51 / H1 +₹11,857.97 /
H2 +₹11,621.54 / breadth 13/25. No discrepancy.**

| Event Book v2.1 (T125) | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Leg A (N4-V3) | 56 | 37.5 | +7,990.43 | +142.69 | +5,155.13 | +2,835.30 | — |
| Leg B (P2F@2.5%) | 39 | 48.7 | +15,489.08 | +397.16 | +6,702.84 | +8,786.24 | 12/25 |
| **Book** | **95** | **42.1** | **+23,479.51** | **+247.15** | **+11,857.97** | **+11,621.54** | **13/25** |

Mandatory disclosures (part of this freeze):

- **Composition history — read this first.** This exact
  composition was NOT a pre-declared Line 3 family. It was run
  in Line 3 as a *supplementary composition check*, AFTER the
  frozen families V1 and V2 were scored, and disclosed as such
  there. It is frozen as a candidate only now, in Line 3b,
  under a spec written before the Line 3b verification
  re-score. That is a cleaner provenance than a silently
  selected best-variant, but it is still a composition chosen
  knowing both legs' in-sample results — the fresh-window test
  is the only unbiased evidence this book will ever get.
- **Concentration — GLENMARK is +₹14,495.24 of the book's
  +₹23,479.51 = 61.7%.** The rupee figure is IDENTICAL to its
  share of the v2 (2.0%) book: every GLENMARK leg-B trade was
  a ≥2.5% reaction, so the band change removed none of them;
  the share fell from ~70% only because the total rose.
  Breadth 13/25 is real, the total is not evenly earned. (See
  the stress verdict at the top of this spec.)
- **34 of leg B's 39 events are also leg-A events** — the legs
  are consecutive-day trades on mostly the SAME events, not
  independent samples. On the shared events of the 2.0% book,
  the leg-A trade was expectancy −₹23.62 and the leg-B trade
  +₹244.42 (Line 3, V5 chain accounting): the book's engine is
  the follow-through day; leg A contributes mainly through its
  non-shared trades.
- **Leg B remains SHORT-carried at the 2.5% band.** SHORT:
  28 trades, win 60.7%, **+₹14,740.78**, expectancy +₹526.46 —
  95.2% of leg B's net. LONG: 11 trades, win 18.2%, +₹748.30,
  expectancy +₹68.03 — no longer negative (it was −₹273.57 at
  the 2.0% band) but thin and low-win-rate. The frozen book
  trades both directions anyway; a direction-only variant
  would be hindsight fitting (the tilt was known before any
  split was run) and is NOT part of this candidate.
- **The book's October slice is negative, and worse than the
  v2 book's:** 8 trades, **−₹845.69** (v2: 10 trades,
  −₹633.52) — inherited from both legs' weak Octobers.
- **Month shape (Line 3b, W4):** no month is worse than
  −₹3,000; October (−₹845.69) is the ONLY negative month;
  September had no qualifying trades. The carriers are August
  (+₹6,107.08, 26.0% of net), February (+₹4,418.45) and
  January (+₹3,501.18). March's +₹2,563.75 is a single trade.
- Both legs are SHORT-tilted in-sample (disclosed in their own
  specs). The frozen book trades both directions anyway.

## Judging proposal for the fresh window (for the main thread to freeze)

- Run the book as ONE log for the fresh window, legs tagged,
  same frozen rules, no parameter changes during the window.
- Judge at window end on book net at T125, win %, and trade
  count together, alongside the two legs' separate verdicts —
  AND alongside the Line 3b stress verdict: a positive window
  for a book this concentrated is weaker evidence than the same
  net from a broad book, and the window report should state
  the window's own per-stock concentration, not just the net.
  A positive window upgrades the book to a further frozen
  decision; a negative window kills the book (legs revert to
  their own separate judgements).

## Files

- Evidence: `stocks_tuning_event_report.md` (Line 3 + Line
  3b), `stocks_tuning_event_results.json`,
  `stocks_tuning_event_3b_results.json`,
  `stocks_tuning_event_v21_combined_trades.csv`
- Loop specs: `stocks_tuning_event_frozen.md` (Line 3 + Line
  3b sections); engines: `stocks_tuning_event.py`,
  `stocks_tuning_event_3b.py`
- Sibling candidate (base form, stress-fallen):
  `stocks_eventbook_v2_candidate_spec.md`
- Leg specs (unchanged, in force for November):
  `stocks_n4_november_paper_spec.md`,
  `stocks_p2f_november_shadow_spec.md`
