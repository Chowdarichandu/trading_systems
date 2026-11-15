# NIFTY TUNING PROGRAMME — 2026-11-12 (owner order 16:23 IST: "tuning all 3")

Segment: Nifty only. Frozen November primary (NF-PAPER-C3G7) untouched;
outputs are December candidates only. Paper, real ₹0, premiums per 1 lot
(65), cost ₹220/trade, UNIQUE-ONCE. Full controls gate in-run for every
scored variant: timing audit (`audit_exact`), admission/feature-timing
(drop-only filters and exit-geometry only — no admission feature is read
from post-entry data), shift30 placebo, halves, full month table,
ex-top-3 legs **and** days, independent re-sum asserted. Bars unmoved.
Computation: `tuning_nifty_2026-11-12.py` → `tuning_nifty_2026-11-12_results.json`.

**Gate rule (project standard): FAIL if total ≤ incumbent, any
incumbent-green month flips red, H1 or H2 < incumbent, ex-top-3 legs or
days ≤ incumbent, or the shift30 placebo is not beaten. Hygiene: NC = 0,
re-sum exact, timing audit clean — all held in every battery below.**

## VERDICT — NOTHING PASSED

No variant in this programme passes the full gate. One near-miss is
recorded exactly as it fell (T-N1a, below). The December ranking therefore
stands on the already-gated TUNED line, ordered by November forward
evidence.

## ANCHORS — reproduced exactly before any variant was scored

| Book | Legs | Total | H1 (Jan–May) | H2 (Jun–Oct) | Ex-top-3 | FT |
|---|---|---|---|---|---|---|
| DEC-S1 (base) | 97 | +₹91,168.50 | +₹45,393.50 | +₹45,775.00 | +₹57,703.50 | 34.0% |
| **TUNED v1** (EVE-07: DEC-S1 − B PE) | 74 | **+₹103,050.25** | +₹52,319.25 | +₹50,731.00 | +₹69,585.25 | 37.8% |
| **TUNED v2** (EVE-11: − B PE, A CE, C CE) | 59 | **+₹115,950.75** | +₹67,064.25 | +₹48,886.50 | +₹82,485.75 | 44.1% |

v1's only red month is Mar (−₹1,216.50); v2 has no red month. Excluded
classes at incumbent geometry (Jan–Oct, from the DEC-S1 scoring):
B PE 23 legs **−₹11,881.75** · A CE 10 legs −₹2,560.75 · C CE 5 legs
−₹10,339.75.

## T-N1 — TUNED v1 EXIT-GEOMETRY VARIANTS (74 legs, geometry only)

Incumbent geometry: stop −50 · BE arm +50 → entry · tgt1 +90 → lock
**+60** · tgt2 **+175** · SQ 15:20.

**T-N1a — lock +60 → +50 → GATE FAIL, by one leg (H2, −₹351.00).**
Total **+₹109,709.50** (Δ **+₹6,659.25** vs v1) · FT 37.8% · H1
+₹59,329.50 ✓ · **H2 +₹50,380.00 vs incumbent +₹50,731.00 ✗ (−₹351.00)** ·
ex-top-3 legs +₹76,244.50 ✓ · ex-top-3 days +₹76,244.50 ✓ · placebo
+₹71,271.75, beaten ✓ · no month flips (its table has **no red month at
all** — Mar improves −₹1,216.50 → +₹5,608.50) · NC 0, re-sum exact, audit
clean. Six of seven gate legs pass; the H2 leg fails by ₹351.00 and the
bar is not moved. November counterfactual: **+₹3,036.50** — identical to
v1's (direct candle replay of the Nov 3 C CE leg under all three
geometries: square_off 13:20 @ 126.00 in each; the leg never entered the
runner branch, so lock/tgt2 cannot bind). Recorded as the programme's
nearest miss: adoptable only on the owner's explicit waiver (the EVE-16 /
DEC-S1 failed-and-waived precedent), never as a gate pass.

**T-N1b — tgt2 +175 → +150 → GATE FAIL (3 legs).**
Total **+₹99,676.75** (Δ −₹3,373.50) · H1 +₹50,570.75 ✗ · H2 +₹49,106.00
✗ · ex-top-3 +₹71,086.75 ✓ · placebo +₹59,955.25 beaten ✓ · no flips.
Capping the runner at +150 gives back more than it protects — the +175
tail is worth money in this book. November counterfactual +₹3,036.50
(same replay proof as T-N1a).

## T-N2 — TUNED v1 + A-LEG ADMISSION CONDITIONING → SKIPPED, by design

Field inventory of the scored DEC-S1 store (the only fields that exist at
admission): `date, direction, entry_time, strike, expiry, component`
(+ the merged source key). Every one is unavailable as a fresh angle:

- **component / direction** — fully consumed by EVE-07/09/10/11 (the
  A CE / A PE split *is* EVE-10).
- **entry_time** — the axis is closed: NIFTY-EVE-14 (standing book − A PE
  ≥10:30), EVE-15 (TUNED v2 − A PE ≥10:30) and EVE-16 (≥11:00 form) all
  GATE FAILED on 2026-11-09/10; the dropped late A PE legs are earners
  (+₹11,317.00 / 7 legs). Any new threshold on this axis is a retest of a
  refuted family, not a fresh angle.
- **source composition** — EVE-18's ground: the stored pool merges
  sources into one key per (date, direction); NOT TESTABLE from stored
  data, and every C3-loosening route is closed.
- **strike** — present, but a raw strike level is not an honest admission
  property: no spot/prior-close reference exists in the store, and Nifty's
  level ranged across the year, so any strike band is a disguised date
  filter — fitting, which this programme does not do.
- **expiry** — no variation to condition on: A legs carry the monthly
  expiry by construction (the weekly sleeve is Component C).

No variant was registered or scored for T-N2. Stated, not fitted.

## T-N3 — MAKING TUNED v2 TRADE: EXCLUSION ACCOUNTING + ONE GATED RELAXATION

**v2's Jan–Oct frequency** (59 legs, every month active, no red month):
Jan 4 · Feb 6 · Mar 9 · Apr 6 · May 8 · Jun 4 · Jul 8 · Aug 4 · Sep 7 ·
Oct 3 legs. v2's inactivity is a November fact, not a construction fact:
November's DEC-S1 population contained only B PE ×4 and C CE ×1.

**What each v2 exclusion cost in November** (DEC-S1 shadow log,
candle-scored): **B PE — 4 legs** (net −₹3,480: −220 / −3,470 / −3,470 /
+3,680) — the costliest, and **not relaxable**: the leak is proven on
Jan–Oct (−₹11,881.75 / 23 legs vs B CE +₹45,506.50 / 26 legs).
**C CE — 1 leg**, and it is November's only winner (+₹3,036.50).
**A CE — 0 legs** (no November A CE existed). The registered relaxation
is therefore C CE, the next-costliest after B PE.

**T-N3 — TUNED v2 + C CE restored (DEC-S1 − B PE − A CE, 64 legs) →
GATE FAIL vs v2 (5 legs).**
Total **+₹105,611.00** (Δ **−₹10,339.75** vs v2 — exactly the C CE class's
Jan–Oct worth) · FT 40.6% · H1 +₹58,855.50 ✗ · H2 +₹46,755.50 ✗ ·
ex-top-3 legs/days +₹72,146.00 ✗ · placebo +₹73,575.75 beaten ✓ · no
month flips, no red month-ends · mirror placebo (v2 + A CE instead:
+₹113,390.00) **not beaten** ✗. Provenance stated plainly: this leg set
is EVE-10's construction, gated on 2026-11-05 against the *v1* frame
(PASS there, Δ +₹2,560.75 vs v1 — reproduced in this run to the paisa);
gated here, as pre-registered, against the *v2* frame it fails, because
restoring November's one winning sleeve means re-admitting a class that
lost ₹10,339.75 across Jan–Oct. November counterfactual: **+₹3,036.50 /
1 leg** vs v2's ₹0 / 0 legs — the activity is real, and the gate's price
for it is also real. The gate refuses the trade.

## DECEMBER RANKING — NIFTY

1. **TUNED v1** — the only book with both proofs: gate PASS
   (+₹103,050.25 Jan–Oct) *and* the line's only positive November forward
   record (**+₹3,036.50**, 1 leg). Its known weakness is one red month
   (Mar −₹1,216.50) and the shallowest gate total of the tuned pair.
2. **TUNED v2** — the strongest gate on record (+₹115,950.75, no red
   month, FT 44.1%, ex-top-3 +₹82,485.75) but **zero November forward
   trades**; T-N3 shows the only activity-restoring relaxation fails the
   gate, so v2 enters December, if chosen, on gate evidence alone —
   exactly the distinction the 2026-11-10 decision note required.
3. **T-N1a (v1 @ lock +50)** — not a passer: best v1-frame total
   (+₹109,709.50) and a no-red-month table, failed by the single H2 leg
   (−₹351.00). Ranked above DEC-S1 on numbers, promotable only by the
   owner's explicit waiver, never by this gate.
4. **DEC-S1** — November −₹443.50 (5 legs) and carries the proven B-PE
   leak (−₹11,881.75 Jan–Oct; −₹3,480 November). The frozen candidate is
   dominated by its own tuned children on both evidence sets. The C3G7
   primary (−₹3,470, 1 trade in 8 days) is not a December candidate.

*Caveats: all Jan–Oct figures are in-sample gate evidence (ceilings, not
proof) — the same record the EVE-07/09/10/11 promotions rest on; November
forward evidence is 5 candle-scored DEC-S1 legs, from which the v1/v2/T-N3
records are drop-only derivations. T-N1's November counterfactual is a
direct candle replay, not a derivation. Nothing here touches the frozen
November primary, and no failed variant may be retested identically.*
