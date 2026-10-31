# Stocks EQUITY — HYPOTHESIS (frozen, untested) — EVENT BOOK v2.1 × below-50DMA regime gate

**Status: HYPOTHESIS ONLY, frozen 2026-10-31 in tuning loop
LINE 3b (family W3). This document freezes a question for a
future fresh-window test. It adopts NOTHING. No gate is in
force anywhere. November's frozen systems (N4-V3 primary,
P2F shadow, P2-INV1 shadow) are unchanged by this document.**

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**

## The hypothesis

> The Event Book's weak half (Jan–May) is regime-concentrated:
> event trades taken when NIFTY sat ABOVE its 50-day average
> lost money in H1 on both legs, while the same trades taken
> below the 50DMA were the book's best bucket. A book that
> trades ONLY on below-50DMA days might keep the edge and cut
> the H1 damage.

## The frozen gated rule (for the future test — NOT scored in Line 3b)

- **Book:** Event Book v2.1, exactly as frozen in
  `stocks_eventbook_v21_candidate_spec.md` (Leg A = N4-V3 per
  its November spec; Leg B = P2F at the 2.5% reaction band per
  the P2F shadow spec with the band change stated there).
- **Gate:** a leg-trade is taken only if the INV1 condition is
  MET on that trade's own trade date D, computed ex-ante
  exactly as in `stocks_p2inv_november_shadow_spec.md`:
  previous close = last NIFTY daily close dated < D; 50DMA =
  mean of the 50 closes ending at that previous bar; condition
  MET ⇔ previous close ≤ 50DMA. Each leg-trade is judged on
  its own date (leg A on R, leg B on R+1 — the two legs of one
  event can fall on different sides of the gate).
- **No other change:** same triggers, entries, T125 exits,
  ₹40 per leg-trade, all qualifying (gated) events taken, no
  de-duplication, no direction filter.
- **November dependency:** if either November leg verdict
  kills its leg, the underlying book dies and this hypothesis
  dies with it — there is nothing left to gate.

## Hypothesis source (in-sample — the ONLY evidence, and it is not a test)

Line 3 family V6 tagged the v2 book (P2F leg at the **2.0%**
band) trade-by-trade with this condition. That split — a
diagnostic, run knowing the halves — is the entire basis:

| V6 diagnostic (v2 book, 2.0% band) | Trades | Net ₹ | Exp ₹/trade | H1 ₹ (n) | H2 ₹ (n) |
|---|---|---|---|---|---|
| Condition MET | 65 | +16,551.59 | +254.64 | +11,523.16 (39) | +5,028.43 (26) |
| Condition NOT met | 39 | +4,274.72 | +109.61 | **−2,869.93** (24) | +7,144.65 (15) |

Inside the buckets: on MET days both legs were both-halves
positive; on NOT-MET days BOTH legs lost in H1 (N4-V3 −₹849.85;
P2F −₹2,020.08) and both earned in H2. Note honestly what this
source is and is not:

- It is a **split of a scored set**, produced after the book's
  halves were known. Splits like this are how hypotheses are
  born and how overfitting happens; the same data cannot do
  both jobs.
- The split was computed at the **2.0% band**; the frozen
  gated book is the **v2.1 (2.5%) form**. The v2.1 × condition
  split was deliberately NOT computed in Line 3b (family W3 is
  spec-only) — computing it would add in-sample temptation,
  not evidence.
- Line 3b's W1 stress adds a caution that cuts both ways: the
  book's H1 is concentrated in a few stocks, so the NOT-MET
  H1 loss (−₹2,869.93 over 24 trades) may be a handful of
  events, not a regime law.

## Judging rule for the future fresh window (pre-registered, mirrors the INV1 shadow rule)

To be run only if the main thread freezes a fresh window for
the v2.1 book itself, and judged once at that window's end,
on the gated book's T125 net (provisional per 100 shares):

- **Positive window net with ≥ 15 gated trades:** the gated
  book is upgraded to a **candidate** — it earns a further
  frozen decision. It is NOT adopted on one window.
- **Negative window net (with ≥ 15 gated trades):** the gate
  is **killed** — recorded as an in-sample artefact of the V6
  split, no re-test with a different DMA length, no band
  change after the fact.
- **Fewer than 15 gated trades in the window** (including a
  window where the condition rarely triggers): **inconclusive**
  — the test extends to the next window under identical rules,
  judged on the combined sample against the same bar.
- The window report must show the gated book AND the ungated
  v2.1 book over the same window side by side: the gate earns
  its keep only if it beats doing nothing, not merely by being
  positive.

**No parameter changes during the window, and none after a
verdict:** no change to the 50DMA length, the ≤ comparison,
the 2.5% band, the legs, the exits, the cost, or this judging
rule.

## Files

- Book frozen at: `stocks_eventbook_v21_candidate_spec.md`
- Gate definition source: `stocks_p2inv_november_shadow_spec.md`
- Hypothesis source evidence: `stocks_tuning_event_report.md`
  (Line 3, family V6); freeze recorded in
  `stocks_tuning_event_frozen.md` (Line 3b, family W3)
