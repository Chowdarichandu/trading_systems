# MOVER-B3 — FROZEN FAMILY LIST (frozen 2026-10-31, BEFORE scoring)

Equity cash intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders, real money ₹0. Every rupee
figure provisional per 100 shares; net = gross − ₹40/trade flat.
Window Jan–Oct 2026 (Oct = 1–28). Scoring on POOLED 50 primary;
home/ext splits reported for every cell.

## Base and anchor (validate first, before any family is believed)

**B2 candidate** (`stocks_moverB2_candidate_spec.md`): Morning-Mover
measured at **10:30**, threshold |pre-move| ≥ 1.0%, discard first
signal of the day, trade the next signal in any direction, chain
cap 2, exits T125 (target +1.25% / stop −0.5%, stop before target,
square-off 15:10). Machinery: `stocks_moverB2.py build()` (Line 5
`build_batt` semantics + cap parameter), frozen V5 re-entry signal
heads, pooled 50 (25 home + 25 ext).

Anchor to reproduce exactly before scoring anything:
pooled 1,212 chains / 1,835 trades / net **+₹812,204.86**,
halves Jan–May **+₹448,461.50** / Jun–Oct **+₹363,743.36**,
October **+₹144,167.85**, breadth **48/50**, expectancy
+₹670.14/chain, max DD **−₹18,493.11** (daily-aggregated,
risk-card method), no losing month.

Context: the measurement slope rose at every scored step
10:00 → 10:15 → 10:20 → 10:30 and was never tested beyond 10:30.
At 10:15, direct-only and same-direction each added profit and
their combination scored +₹511,937.80 vs +₹464,617.03 base; those
stacks were NOT re-tested on the 10:30 base. This line finds the
peak and re-stacks.

## Families (score in this order; one structural change at a time)

- **B3-1 MEASUREMENT EXTENSION** — base rule with measurement
  time only changed: **10:45**, **11:00**, **11:30** (three cells).
  Full read per cell: chains, trades, net, halves, month table
  with losing months flagged, October, breadth, expectancy/chain,
  max DD, home/ext splits. Question: where does the slope peak
  and turn?
- **B3-2 STACK ON 10:30** — on the B2 candidate configuration:
  (a) **direct-only** (chain cap 1); (b) **same-direction**
  (only signals in the pre-move's direction are traded, cap 2);
  (c) **both** (cap 1 + same-direction).
- **B3-3 STACK ON THE PEAK** — only if B3-1 finds a measurement
  time with pooled net above the 10:30 base: apply the combined
  stack (direct-only + same-direction) at that peak time.
  If no B3-1 cell beats 10:30, B3-3 is not run and the report
  says so.
- **B3-4 EXIT CHECK** — on the best configuration overall by
  pooled net among {B2 candidate, B3-1 cells, B3-2 cells,
  B3-3 if run}: two cells, (a) **T150/S050** (target +1.5% /
  stop −0.5%), (b) **T125/S065** (target +1.25% / stop −0.65%).
  Everything else identical to that configuration.

## Gate for a B3 candidate

A configuration replaces the B2 candidate only if ALL hold on
the pooled 50:

1. pooled net **greater than the configuration it modifies**
   (for B3-1/B3-2 cells: greater than the B2 candidate's
   +₹812,204.86; for B3-3: greater than the plain peak-time
   configuration AND greater than +₹812,204.86; for B3-4:
   greater than the best configuration it is applied to);
2. both halves (Jan–May, Jun–Oct) net positive;
3. breadth ≥ **47/50**;
4. max DD ≥ **−₹25,000**;
5. **no losing month** (all ten months Jan–Oct net ≥ 0).

If a B3 configuration passes, freeze
`stocks_moverB3_candidate_spec.md` with the December 2026
fresh-window judging rule mirrored from the B2 candidate spec
(December net positive with ≥ 80 chains → confirmed as candidate;
negative with ≥ 80 chains → killed; fewer than 80 chains or net
exactly ₹0 → inconclusive, extend one month). If nothing passes,
the report states plainly that the B2 candidate stands.

November's frozen A/B shadows are untouched by this line.
No parameter outside the frozen cells above may be tried.
