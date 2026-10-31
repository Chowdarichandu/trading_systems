# Stocks EQUITY — Tuning loop LINE 3: the EVENT BOOK (N4-V3 + P2F) — report

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**
Spec frozen before scoring: `stocks_tuning_event_frozen.md`.
Engine: `stocks_tuning_event.py`. Results:
`stocks_tuning_event_results.json`. Window Jan–Oct 2026
(October = 1–28 Oct). Halves: H1 = trade date ≤ 2026-05-31,
H2 = ≥ 2026-06-01.

**The frozen November specs are untouched by this loop** —
N4-V3 primary and P2F shadow run in November exactly as frozen.
This loop builds the NEXT event-book version, as candidates only.

**Pass gate (frozen):** net positive in BOTH halves at ₹40,
overall expectancy > 0, breadth ≥ 10 of 25 stocks net-positive.

## Anchors — both reproduce EXACTLY

- N4-V3 T125 (published round-5 file): 56 trades, **+₹7,990.43**,
  halves +₹5,155.13 / +₹2,835.30, expectancy +₹142.69. ✓
- P2F T125 (regenerated in-engine from the calendar + caches,
  exact frozen definitions): 48 trades, **+₹12,835.88**, halves
  +₹3,498.10 / +₹9,337.78, win 45.8%, expectancy +₹267.41,
  breadth 14/25, SHORT +₹13,109.45 / LONG −₹273.57. ✓

---

## V1 — COMBINED BOOK (headline family): ✅ PASS

Book = all 56 N4-V3 trades + all 48 P2F trades, no
de-duplication, no change to either leg.

| Combined book T125 | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ (n) | H2 ₹ (n) | Breadth |
|---|---|---|---|---|---|---|---|
| N4-V3 + P2F | 104 | 41.3 | **+20,826.31** | +200.25 | +8,653.23 (63) | +12,173.08 (41) | **13/25** |

**Overlap accounting (as frozen, reported, nothing changed):**
- **Both-fire events: 43.** For 43 of the 48 P2F events, N4-V3
  also traded the same stock on the reaction day R (P2F trades
  R+1). The two legs are NOT independent samples — they are
  mostly the same events traded on consecutive days. V5 below
  prices exactly this.
- **Same-stock same-day overlaps: ZERO.** No (stock, date) pair
  appears as a trade date in both legs — the books never collide
  on the same day, by construction (R vs R+1).

**Concentration warning, in the same breath as the pass:**
GLENMARK alone is +₹14,495.24 of the +₹20,826.31 combined net
(~70%) — its two large N4-V3 single-news targets plus its P2F
trades. Breadth is genuinely 13/25 (OBEROIRLTY +₹4,880.37,
GODREJCP +₹4,497.57, TVSMOTOR +₹3,354.92, BDL +₹1,756.20 behind
it), but the total leans on one stock's event history. Worst
losers: HINDUNILVR −₹3,357.47, ASTRAL −₹3,203.55, UNITDSPR
−₹2,086.65. The combined book's October slice is also negative:
10 trades, −₹633.52 — inherited from both legs' weak Octobers.

**Verdict:** PASS on every frozen leg of the gate — both halves
strongly positive (not flat), expectancy +₹200.25, breadth
13/25. Honest framing: the pass is partly arithmetic — two
both-halves-positive books sum to a both-halves-positive book —
but the combination is not trivially redundant: the legs trade
different days, never collide, and the book's H2 (+₹12,173.08)
is stronger than either leg's H2 alone. **Frozen as the v2
candidate: `stocks_eventbook_v2_candidate_spec.md`.**


---

## V2 — P2F REACTION BANDS: ✅ PASS at all three frozen thresholds

One change only: the minimum |reaction-day return| for a P2F
candidate. Base 2.0% (already scored) shown for reference.

| Band | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ (n) | H2 ₹ (n) | Breadth | Gate |
|---|---|---|---|---|---|---|---|---|
| 2.0% (base) | 48 | 45.8 | +12,835.88 | +267.41 | +3,498.10 (29) | +9,337.78 (19) | 14/25 | — |
| **2.5%** | 39 | 48.7 | **+15,489.08** | **+397.16** | +6,702.84 (23) | +8,786.24 (16) | 12/25 | ✅ PASS |
| 3.0% | 33 | 48.5 | +14,231.75 | +431.27 | +6,720.88 (21) | +7,510.87 (12) | 11/25 | ✅ PASS |
| 4.0% | 22 | 54.5 | +8,399.06 | +381.78 | +7,383.06 (14) | +1,016.00 (8) | 10/25 | ✅ PASS (thin H2) |

**Reading:** raising the bar from 2.0% to 2.5% REMOVES 9 trades
and ADDS ₹2,653.20 of net — the 2.0–2.5% reactions were
net-negative dead weight in BOTH halves (H1 nearly doubles when
they are dropped). The thresholds were pre-declared in the
frozen spec ({2.5, 3.0, 4.0}), so this is not post-hoc
threshold-fishing, and the fact that all three pass says the
P2F result is not knife-edge on the threshold. Picking a
"best" band is still a selection among variants: 2.5% has the
highest net and the most balanced halves; 3.0% the highest
expectancy on a thinner sample; 4.0% concentrates into H1 with
an 8-trade H2. **Recorded passed variant: P2F leg at band 2.5%**
— carried into the supplementary composition check below and
noted in the candidate spec as an option requiring its own
frozen decision before it replaces the 2.0% leg anywhere.

---

## V3 — P2F HOLD VARIANTS

### V3a — TWO-DAY HOLD ⚠ NON-INTRADAY — deviation priced, not adopted

This variant HOLDS POSITIONS OVERNIGHT. It breaks the
intraday-only convention and is labelled NON-INTRADAY in every
file and table. It cannot be adopted as an intraday system.

| V3a NON-INTRADAY | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Two-day hold | 47 | 46.8 | +13,012.87 | +276.87 | +3,225.85 | +9,787.02 | 14/25 |

Mechanics as frozen: T125 levels fixed from entry; day-1
stop/target scan identical to base; positions still open at
15:10 on R+1 (the base engine's 4 square-offs) were held
overnight and exited on R+2 (gap check first — it never
triggered; then the standard scan; 1 final square-off). One
candidate (RECLTD, R 2026-10-27, trade date 2026-10-28) was
dropped by the frozen upfront R+2 check: its R+2 does not
exist in the cache (29 Oct missing). The ₹40 flat cost is kept
for comparability — real overnight charges would differ and
are NOT modelled.

**Exact accounting of the apparent gain:** V3a's +₹176.99
over base P2F is an artefact of that one drop — RECLTD was a
day-1 stop (−₹183.00) in the base, a trade the hold rule
would never have touched. The hold rule's own contribution,
on the 4 trades it actually changed, is **−₹6.01**: those 4
trades netted +₹886.99 held overnight versus +₹893.00 as
15:10 square-offs (two reached target at the R+2 open bar,
one stopped late on R+2 after being positive at the R+1
close, one squared off a day later near flat).

**Verdict:** the numbers pass the gate, and the deviation
buys literally nothing (−₹6.01 on the trades it changed).
**Rejected as a direction** — the overnight risk (gap through
the stop, unmodelled here beyond the open-price gap rule) is
not paid for. The intraday square-off is not the constraint
on this family.

### V3b — CLOSE-EXIT CONTROL (exit at R+1 close, no target/stop)

| V3b control | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Close exit | 48 | 58.3 | +14,757.00 | +307.44 | +12,874.00 | +1,883.00 | 14/25 |

**Reading:** the control's TOTAL (+₹14,757.00) exceeds the
T125 base (+₹12,835.88) — but the shape is wrong: its H1 does
nearly all the work (+₹12,874.00) while its H2 sags to
+₹1,883.00 (expectancy ≈ +₹99/trade) where T125's H2 is
+₹9,337.78. The target/stop structure is not decoration: it
converts H1's raw drift into a both-halves result, mainly by
banking +1.25% targets in H2 conditions where close-exits give
the move back. The control passes the gate arithmetic but is
strictly worse balanced than the frozen T125 form; **no change
to the exit structure is carried forward.**


---

## V4 — P2F DIRECTION SPLIT

| Side | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth | Gate |
|---|---|---|---|---|---|---|---|---|
| SHORT only | 32 | 59.4 | +13,109.45 | +409.67 | +6,712.29 | +6,397.16 | 14/25 | ✅ numbers pass — see warning |
| LONG only | 16 | 18.8 | −273.57 | −17.10 | −3,214.19 | +2,940.62 | 3/25 | ❌ FAIL |

**Hindsight warning (required by the frozen spec):** the SHORT
tilt of P2F was public knowledge before this split was run —
it is printed in the November shadow spec's disclosures. A
SHORT-only variant therefore CANNOT be treated as a discovery;
it is a restatement of a known in-sample asymmetry. Its numbers
are genuinely strong (both halves ≈ +₹6.5k, expectancy
+₹409.67, the highest of this loop), and that is exactly why
it must not be smuggled in as a fresh candidate: adopting it
would be fitting the rule to the sample that suggested it.
**Recorded, not frozen.** If a future fresh window (November
P2F shadow, both directions as frozen) again shows the same
asymmetry, a direction decision can be frozen THEN, on fresh
evidence. LONG-only fails outright: negative overall, H1
−₹3,214.19, 18.8% win rate — in this window, up-reactions did
not follow through; down-reactions did.

---

## V5 — SAME-EVENT CHAIN ACCOUNTING (diagnostic)

43 both-fire events (V1): the same stock-event traded by
N4-V3 on R and by P2F on R+1.

| Chain accounting | Value |
|---|---|
| Chains | 43 |
| Chain net (sum of both legs) | +₹9,494.37 |
| Chain win rate (chain net > 0) | 65.1% |
| Chain expectancy | +₹220.80 per 2-day chain |
| N4-V3 leg expectancy ON CHAIN EVENTS | **−₹23.62** |
| P2F leg expectancy ON CHAIN EVENTS | **+₹244.42** |
| Directions agree | 40 of 43 |

**The finding that matters for sizing:** on the events where
both legs fire, the N4-V3 leg itself is expectancy-NEGATIVE
(−₹23.62/trade) — N4-V3's overall +₹142.69 expectancy is
earned on its OTHER trades (the single-news trades and the
results events P2F does not take). The chain's profit is
carried by the second day: the P2F leg earns +₹244.42 on the
same events. In plain terms: on big-reaction events, the
money is in the FOLLOW-THROUGH day, not the reaction day.
Best chains: GLENMARK (R 2026-02-01) +₹4,823.12, OBEROIRLTY
(2026-01-20) +₹3,803.12, GODREJCP (2026-01-27) +₹2,881.25.
Worst: TVSMOTOR (2026-01-29) −₹3,751.35, HINDUNILVR
(2026-02-13) −₹2,410.60 and (2026-05-04) −₹2,400.00. The 3
direction-disagreement chains (N4 LONG on the 09:30 move, P2F
SHORT on the full-day return — the day reversed after 09:30)
net +₹413.11 combined; disagreement is rare and not itself a
signal. **Sizing implication, recorded only:** if capital is
ever allocated per event, these numbers argue for weighting
the R+1 leg at least equally with the R leg — NO rule change
is made from this diagnostic.

---

## V6 — COMBINED BOOK × INV1-STYLE CONDITION (diagnostic)

Every V1 trade tagged ex-ante: NIFTY previous close ≤ its
50DMA on the trade date (INV1 condition, exact shadow-spec
definition). NO gate is adopted from this split.

| Bucket | Trades | Net ₹ | Exp ₹/trade | H1 ₹ (n) | H2 ₹ (n) |
|---|---|---|---|---|---|
| Condition MET | 65 | +16,551.59 | +254.64 | +11,523.16 (39) | +5,028.43 (26) |
| Condition NOT met | 39 | +4,274.72 | +109.61 | **−2,869.93** (24) | +7,144.65 (15) |

Per leg inside each bucket: on MET days both legs are
both-halves positive (N4-V3: H1 +₹6,004.98 / H2 +₹922.64;
P2F: H1 +₹5,518.18 / H2 +₹4,105.79). On NOT-MET days, BOTH
legs lose in H1 (N4-V3 −₹849.85; P2F −₹2,020.08) and both earn
in H2 (N4-V3 +₹1,912.66; P2F +₹5,231.99).

**Reading (diagnostic only):** the event book's H1 weakness
is regime-concentrated — in Jan–May, event trades taken when
NIFTY sat ABOVE its 50DMA lost money on both legs, while the
same trades below the 50DMA were the book's best bucket.
H2 shows no such split (both buckets positive). This rhymes
with INV1's own in-sample story (the below-trend condition is
where its money was) and is recorded as a hypothesis for a
future frozen test — per the frozen spec, a split alone
adopts nothing, and November's frozen systems are unchanged.

---

## SUPPLEMENTARY composition check (NOT a frozen family)

Run after V1 and V2 were scored, disclosed as such: the V1
combined book with its P2F leg at the passed V2 band of 2.5%.

| Composition | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| N4-V3 + P2F@2.5% | 95 | 42.1 | **+23,479.51** | +247.15 | +11,857.97 | +11,621.54 | 13/25 |

It improves on V1 as scored (+₹20,826.31) with 9 fewer trades
and near-even halves. It is NOT the frozen candidate — the
composition was not a pre-declared family, and freezing it
now would be selecting on results. It is recorded so the
next tuning line can freeze exactly this composition as its
first family and score it as such.

---

## LINE 3 SUMMARY — verdicts

| Family | Verdict |
|---|---|
| **V1 Combined book** | ✅ **PASS** — frozen as v2 candidate (`stocks_eventbook_v2_candidate_spec.md`) |
| V2 Bands 2.5 / 3.0 / 4.0% | ✅ PASS (all three; 2.5% recorded as the leg variant) |
| V3a Two-day hold | ⚠ Numbers pass but NON-INTRADAY — rejected as a direction; deviation buys ~nothing |
| V3b Close-exit control | Control — total higher, H2 much weaker; exit structure kept |
| V4 SHORT-only | Numbers pass, NOT frozen — known in-sample tilt (hindsight), recorded only |
| V4 LONG-only | ❌ FAIL — negative, H1 −₹3,214.19 |
| V5 Chains | Diagnostic — on shared events the R+1 leg carries the profit (N4 leg −₹23.62 exp) |
| V6 INV1 split | Diagnostic — H1 losses concentrate on above-50DMA days; no gate adopted |

**Standing caveats over the whole line:** everything is
in-sample Jan–Oct 2026; the combined book's October is
negative (−₹633.52, 10 trades); GLENMARK is ~70% of the
combined net. The candidate earns a fresh-window test, not
adoption — and November's already-frozen N4-V3 primary and
P2F shadow are the first fresh evidence for its two legs.

## Files

- Frozen spec: `stocks_tuning_event_frozen.md`
- This report: `stocks_tuning_event_report.md`
- Engine: `stocks_tuning_event.py`; results:
  `stocks_tuning_event_results.json`
- Trades: `stocks_tuning_event_V1_combined_trades.csv`,
  `stocks_tuning_event_V3a_NONINTRADAY_trades.csv`,
  `stocks_tuning_event_V3b_trades.csv`,
  `stocks_tuning_event_V5_chains.csv`
- Candidate (on V1 pass): `stocks_eventbook_v2_candidate_spec.md`

---
---

# LINE 3b — STRESS-TEST OF THE EVENT BOOK CANDIDATE

**Appended 2026-10-31. Spec frozen before scoring:
`stocks_tuning_event_frozen.md` (Line 3b section). Engine:
`stocks_tuning_event_3b.py`. Results:
`stocks_tuning_event_3b_results.json`. Same basis throughout:
equity cash, LONG/SHORT, paper only, real ₹0, provisional per
100 shares, ₹40/trade, Jan–Oct 2026 (Oct = 1–28).**

**Purpose:** Line 3 built a candidate; Line 3b tries to break
it. The frozen November specs are untouched. **Anchors
reproduce exactly before anything below is believed:** V1
combined book 104 trades / +₹20,826.31 / halves +₹8,653.23 /
+₹12,173.08 / breadth 13/25 ✓; supplementary composition
(book @2.5%) 95 trades / +₹23,479.51 / halves +₹11,857.97 /
+₹11,621.54 / breadth 13/25 ✓ (re-verified under W2).

## W1 — CONCENTRATION STRESS (base book, P2F leg at 2.0%)

Gate (unchanged): both halves > 0, expectancy > 0, breadth
≥ 10/25. GLENMARK's base-book halves, for reference: H1
+₹7,386.87, H2 +₹7,108.37.

| Stress | Trades | Win % | Net ₹ | Exp ₹/trade | H1 ₹ | H2 ₹ | Breadth | Gate |
|---|---|---|---|---|---|---|---|---|
| Base book (V1) | 104 | 41.3 | +20,826.31 | +200.25 | +8,653.23 | +12,173.08 | 13/25 | ✅ |
| **W1a — ex-GLENMARK** | 97 | 38.1 | +6,331.07 | +65.27 | +1,266.36 | +5,064.71 | 12/25 | ✅ PASS |
| **W1b — ex-top-3** (GLENMARK, OBEROIRLTY, GODREJCP) | 88 | 34.1 | **−3,046.87** | −34.62 | **−7,805.21** | +4,758.34 | 10/25 | ❌ FAIL |
| **W1c — winsorised @ +₹2,000/stock/half** | 104 | — | +4,421.10 | +42.51 | **−1,805.21** | +6,226.31 | 13/25 | ❌ FAIL (H1) |

**Reading:**
- **W1a passes — the book is not literally one stock.** Remove
  GLENMARK entirely and +₹6,331.07 survives, both halves
  positive, breadth 12/25. But look at the shape: expectancy
  falls from +₹200.25 to +₹65.27 (two-thirds of the per-trade
  edge was GLENMARK), and H1 thins to +₹1,266.36.
- **W1b fails outright.** The top-3 payers (GLENMARK
  +₹14,495.24, OBEROIRLTY +₹4,880.37, GODREJCP +₹4,497.57 =
  +₹23,873.18, more than the book's net) ARE the book: without
  them it is −₹3,046.87 with an H1 of −₹7,805.21. H2 stays
  positive (+₹4,758.34) — the dependence is an H1 phenomenon.
- **W1c fails on H1 — the decisive one.** Capping each stock's
  contribution *within each half* at +₹2,000 (an accounting
  stress, not a tradable rule) removes ₹10,458.44 from H1 —
  the excess of just three stocks (GLENMARK +₹5,386.87 over
  cap, OBEROIRLTY +₹3,849.37, GODREJCP +₹1,222.20) — and H1
  flips to **−₹1,805.21**. H2 survives capping (+₹6,226.31;
  caps bind GLENMARK and TVSMOTOR there). So the book's
  Jan–May half — the half that made the combined book look
  balanced — is three stocks' outsized event histories, not a
  broad edge.

**Candidate verdict (frozen W1 rule): the candidate FALLS.**
The frozen rule was written before scoring: stands = all three
stresses pass; stands weakened = W1a + W1c pass, W1b fails;
falls = W1a fails OR W1c fails both-halves. W1c fails
both-halves → **falls**. What falls is the *combined-book
candidate claim* (v2, and by inheritance the family claim):
as a book, its H1 cannot survive its own concentration. What
does NOT fall: the legs. N4-V3 and P2F were frozen for
November on their own evidence and their own judging rules,
and they still face November exactly as frozen — a leg can
pass its own fresh test while this book claim stays dead, and
the book can only be re-proposed afterwards as a new frozen
composition, not revived by this line.

## W2 — v2.1 FORMALISED + VERIFIED

`stocks_eventbook_v21_candidate_spec.md` written, freezing
the composed book (Leg A = N4-V3 as frozen; Leg B = P2F at
the **2.5%** reaction band, all other P2F definitions
unchanged). **Verification: EXACT MATCH, no discrepancy** —
re-scored from the engines: **95 trades / +₹23,479.51 / H1
+₹11,857.97 / H2 +₹11,621.54 / breadth 13/25**, win 42.1%,
expectancy +₹247.15.

Disclosures recomputed for v2.1 (all inside the spec):
- **GLENMARK +₹14,495.24 = 61.7% of the v2.1 net** — the same
  rupees as in v2 (every GLENMARK leg-B trade was a ≥2.5%
  reaction; the share fell from ~70% only because the total
  rose).
- **October slice: 8 trades, −₹845.69** — worse than v2's
  −₹633.52.
- **Leg-B SHORT tilt at 2.5%:** SHORT 28 trades +₹14,740.78
  (exp +₹526.46, win 60.7%) = 95.2% of leg B's net; LONG 11
  trades +₹748.30 (exp +₹68.03, win 18.2%) — LONG is no longer
  negative at this band, but the leg is still SHORT-carried.
- **Overlap:** 34 of leg B's 39 events are also leg-A events.
- The spec carries the W1 stress verdict on its face: v2.1
  inherits the concentration structure of a book form that
  fell its stress test, and any fresh-window run must be read
  with that attached.

## W3 — V6 REGIME HYPOTHESIS FROZEN (spec only, no scoring)

`stocks_eventbook_regime_hypothesis.md` written: the v2.1
book traded only when the INV1 condition (NIFTY prev close ≤
50DMA, ex-ante per trade date) is MET, frozen for a future
fresh-window test with judging language mirroring the INV1
shadow rule (positive with ≥ 15 gated trades upgrades to
candidate; negative kills the gate; < 15 gated trades
inconclusive/extend; the gated book must be reported beside
the ungated book over the same window). Hypothesis source
recorded as-is from the Line 3 V6 diagnostic (2.0% band: MET
65 trades +₹16,551.59 both halves positive; NOT-MET H1
−₹2,869.93). **No new scoring was done — the v2.1 × condition
split was deliberately not computed.** Stated plainly in the
document: hypothesis only, untested on fresh data, no gate
adopted, and it dies if either November leg dies.

## W4 — MONTH-BY-MONTH, v2.1 book

| Month | Trades | Net ₹ | Share of total | Cumulative ₹ |
|---|---|---|---|---|
| 2026-01 | 12 | +3,501.18 | +14.9% | +3,501.18 |
| 2026-02 | 18 | +4,418.45 | +18.8% | +7,919.63 |
| 2026-03 | 1 | +2,563.75 | +10.9% | +10,483.38 |
| 2026-04 | 5 | +43.06 | +0.2% | +10,526.44 |
| 2026-05 | 24 | +1,331.53 | +5.7% | +11,857.97 |
| 2026-06 | 3 | +3,077.52 | +13.1% | +14,935.49 |
| 2026-07 | 9 | +3,282.63 | +14.0% | +18,218.12 |
| 2026-08 | 15 | +6,107.08 | +26.0% | +24,325.20 |
| 2026-09 | 0 | 0.00 | 0.0% | +24,325.20 |
| 2026-10 | 8 | **−845.69** | −3.6% | +23,479.51 |

**Reading:** no month is worse than −₹3,000 — none is close.
**October is the ONLY negative month** (−₹845.69), and
September simply had no qualifying events (results calendar,
not a failure). The carriers: August alone is 26.0% of the
net; Jan+Feb together are 33.7%. Two fragilities the table
exposes: March's +₹2,563.75 is ONE trade, and May — the
busiest month (24 trades) — earns only +₹1,331.53
(+₹55.48/trade): the book's edge is episodic, riding a few
heavy event months, not a steady monthly income shape. The
cumulative never dips negative after January.

## LINE 3b SUMMARY — verdicts

| Family | Verdict |
|---|---|
| **W1 Concentration stress** | ❌ **Candidate FALLS** — W1a passes (ex-GLENMARK +₹6,331.07, both halves +), W1b fails (−₹3,046.87), W1c fails both-halves (H1 −₹1,805.21 capped). Frozen rule: W1c both-halves failure = falls |
| W2 v2.1 formalisation | ✅ Frozen + **verified exactly** (95 / +₹23,479.51 / +₹11,857.97 / +₹11,621.54 / 13/25) — carries the W1 verdict as a disclosure; GLENMARK 61.7% of its net |
| W3 Regime hypothesis | 📄 Frozen, spec-only — untested on fresh data, no gate adopted, no scoring done |
| W4 Month table | No month worse than −₹3,000; October the only negative month; Aug + Jan/Feb carry; March = 1 trade |

**Bottom line of Line 3b:** the Event Book as a *book* does
not survive its own concentration: its first half is three
stocks deep. The honest assets that remain are the two legs
(N4-V3 primary and P2F shadow, both already facing November
on their own frozen terms), the verified v2.1 composition —
frozen with its concentration and the stress verdict printed
on its face, so a future window can be judged with eyes open —
and the frozen regime hypothesis. Nothing in this line changes
any November spec, and nothing here is adopted.

## Line 3b files

- Frozen spec: `stocks_tuning_event_frozen.md` (Line 3b section)
- Engine: `stocks_tuning_event_3b.py`; results:
  `stocks_tuning_event_3b_results.json`; trades:
  `stocks_tuning_event_v21_combined_trades.csv`
- W2: `stocks_eventbook_v21_candidate_spec.md`
- W3: `stocks_eventbook_regime_hypothesis.md`
