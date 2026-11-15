# PHASE-3 TUNING — NIFTY · BUILDUP / SPECULATION STATE CONDITIONING ON TUNED v1 · SPEC FROZEN BEFORE SCORING

**Frozen:** 2026-11-14 09:09 IST — before any phase-3 subset was scored.
Nothing in this spec may be edited after the run; deviations are reported,
not absorbed. (The data-completion fetch `phase3_fetch.py` is a data
build, upstream of scoring: it computes no leg outcome and no state.)

**Order:** owner's standing order of 2026-11-14 09:02 IST — tuning does
not stop until the result is got; tuning = adjusting parameters in small
turns, on the data on hand. His named surface: long buildup / unwinding
and the other buildup classes, previous-day volume compared with
today's, call rates vs put rates (where the speculation is positioning),
and whether our trades go in the correct direction relative to all that.
Research only: no book, ledger or job is changed. Buying only, 1 lot
(65), premiums basis, cost ₹220/trade already inside every stored net.

**What this round is, and is not.** It conditions TUNED v1's OWN
pre-existing legs on the morning buildup/speculation state — it fires no
trade of its own. It is NOT another confidence score: phase 2 / 2B closed
that dial for Nifty with measured reasons (global and family-wise) and no
factor, percentile or composite from those runs appears here. It is NOT
a standalone signal: IOI-1/IOI-2 (closed) generated their own entries
from band-option quadrants; FLOW-VOL (closed) generated entries from a
volume thrust; day-level OI V1–V3 (closed) generated next-day entries.
If any rule below collapses into one of those mechanisms, it is dropped
and the collapse is stated.

## Subject book and leg store

**Nifty TUNED v1 (EVE-07) = DEC-S1 − B PE**, store
`november_books_fix_repair_nifty_legs.csv` (74 rows, no B-PE rows) —
the same store phases 2/2B used. Columns include `family` (A/B/C),
`rep`, `side`, `entry_time`, `gap_pct`, `net_inr`.

## Step 0 — Control (gate to everything else)

Reproduce from the store, exactly as phases 2/2B did: **74 legs · total
+₹103,050.25 · WR 51.4% (38 wins) · 66 trade-days · ₹1,561.37/trade-day ·
March 2026 −₹1,216.50 (the only red month)**; N-FIX-1 anchors (8
stood-down legs, −₹14,119.75; repaired total +₹117,170.00); median
premium ₹213.025. Day profile over the 205-day Jan–Oct 2026 calendar
(`volrix/nifty_daily_2019_2026.csv`): 37 green / 29 red / 139 no-trade.
If any figure does not reproduce, STOP and report — no scoring.

## Step 1 — Morning state (pre-registered; entry-knowable only)

For each trading day D and each read R ∈ {**10:00, 11:00**}: the read
uses only bars that start at or before R−5 min (last bar 09:55 for the
10:00 read, 10:55 for the 11:00 read — its fields are known when the
read's clock strikes). The baseline bar is 09:15. A leg is **conditioned
by read R iff entry_time ≥ R** (its entry bar opens at or after the
read, so the state precedes the entry bar — the house timing
convention, identical to the IOI gate's 10:55-bar read for an 11:00
entry). Legs with entry_time < R pass through unconditioned.

Data: NIFTY futures 5-min 7-field candles (in-force monthly contract =
earliest monthly expiry ≥ D; Nov 2026 → 2026-11-23), fetched into
`phase3_buildup_data/futures/`; near-band option 5-min 7-field candles
in the shared cache `oi_buildup_data/` (completed for the leg-days by
`phase3_fetch.py`); spot from `data/progressive/NIFTY/spot_5m.csv`.

**(a) Futures buildup class.** dP% = (futures close at last read bar /
futures close at 09:15 bar − 1) × 100; dOI% likewise on the futures OI
field. Dead-band: **NEUTRAL if |dP%| < 0.05 or |dOI%| < 0.50**. Else by
signs: dP>0, dOI>0 → **LONG_BUILDUP**; dP>0, dOI<0 →
**SHORT_COVERING**; dP<0, dOI>0 → **SHORT_BUILDUP**; dP<0, dOI<0 →
**LONG_UNWINDING**. Positioning direction: **BULL** = {LONG_BUILDUP,
SHORT_COVERING}; **BEAR** = {SHORT_BUILDUP, LONG_UNWINDING};
**NONE** = NEUTRAL.

**(b) Relative volume.** cumVol(R) = Σ futures bar volumes from 09:15
through the last read bar. **RELVOL** = cumVol_D(R) / cumVol_prev(R),
prev = the previous trading day (spot calendar). **RELVOL5** =
cumVol_D(R) / mean of cumVol(R) over the previous 5 trading days.

**(c) Call/put speculation.** Band(R) = the 11 strikes nearest the spot
close of the last read bar (step 50; ATM = round(spot/50)×50), in-force
monthly expiry. doi_S = Σ over band (OI_S at last read bar − OI_S at
09:15 bar), S ∈ {CE, PE}. **SPEC_IDX** = (doi_CE − doi_PE) /
(OI0915_CE + OI0915_PE) × 100, where OI0915_S = Σ band OI_S at 09:15.
**CROWD = LONG if SPEC_IDX ≥ +0.25 · SHORT if SPEC_IDX ≤ −0.25 ·
FLAT otherwise.**

**NC rules (never filled, never estimated).** Component (a)/(b) is NC
for (D, R) if the futures 09:15 bar or last read bar is missing.
Component (c) is NC if ANY band contract lacks its 09:15 bar or its
last-read bar. A leg whose conditioning component is NC is **not
dropped**: it is kept, flagged NC, and counted per grid point. NC is a
data verdict, not a signal.

## Step 2 — Tuning grid (frozen; evaluated in this order)

At each read R ∈ {10:00, 11:00}, nine rules — 18 grid points. "Kept"
below applies to conditioned, non-NC legs; unconditioned and NC legs
are always kept.

| # | Rule | Keep condition (conditioned legs) |
|---|---|---|
| 1 | ALIGN | (CE and buildup BULL) or (PE and buildup BEAR); NEUTRAL drops |
| 2 | ALIGN+SPEC | ALIGN passes AND crowd agrees (CE↔LONG, PE↔SHORT); FLAT drops |
| 3 | VOL-1.0 | RELVOL ≥ 1.00 |
| 4 | VOL-1.1 | RELVOL ≥ 1.10 |
| 5 | VOL-1.25 | RELVOL ≥ 1.25 |
| 6 | VOL5-1.1 | RELVOL5 ≥ 1.10 |
| 7 | PF-ALIGN | ALIGN applied to families A and C only; family B ungated |
| 8 | PF-ALIGN+SPEC | ALIGN+SPEC applied to families A and C only; family B ungated |
| 9 | FB-ONLY | Only family B conditioned, INVERTED (below); A and C ungated |
| 10 | FB-COMBO | Families A/C under ALIGN; family B under the INVERTED rule |

(Ten rules × two reads = **20 grid points**; the table lists 10 rows —
rows 1–10 evaluated at R10 then R11, in this order, which is also the
placebo RNG consumption order.)

**Family-B INVERTED rule (pre-registered, from the phase-2B
diagnosis):** family B (R8-GAP-FADE) earns against the morning
direction, so for a B leg the test is whether fading *crowded*
speculation hurts: **drop a B leg iff the buildup AGREES with the
leg's own side** — (CE leg and buildup BULL) or (PE leg and buildup
BEAR) — i.e. the crowd is already positioned for the move the fade is
betting on. **Keep if the buildup opposes the leg's side or is
NEUTRAL.**

Per grid point, report: kept legs, total, WR (legs), distinct
trade-days, ₹/trade-day, green/red/no-trade days over the 205-day
calendar, full month table (Jan–Oct), halves (H1 = Jan–May legs,
H2 = Jun–Oct legs), ex-top-3 (total − 3 largest kept leg nets);
dropped population (count, total, mean net); NC-kept leg count.

## Step 3 — Placebos and the dropped-set control (pre-registered)

Per grid point: **200 draws**. Each draw keeps every unconditioned and
NC leg (structural keeps) and samples uniformly without replacement,
from that point's conditioned non-NC population, exactly as many legs
as the rule kept from that population. Placebo percentile = fraction
of the 200 draw-totals strictly below the grid book's total. RNG:
Python `random.Random(20261114)`, one stream, draws consumed in the
frozen grid order (R10 rules 1–10, then R11 rules 1–10).

**Dropped-set control:** the conditioner must beat the legs it drops —
PASS iff mean net of kept conditioned legs > mean net of dropped
conditioned legs (same grid point, conditioned non-NC population).
Both means and the dropped total are reported regardless.

## Step 4 — Diagnostics (reported, not gated)

At R10 (the read with the larger conditioned population): mean net of
v1 legs by buildup class, pooled and per family; family-B legs split
by buildup agrees / opposes / neutral (count, total, mean); legs by
crowd class; RELVOL terciles vs mean net. These describe whether the
state knows anything about this book's legs even where no grid point
passes.

## Step 5 — November counterfactual (descriptive only)

v1's one November leg: **Nov 3, CE 23600 (weekly), family C, entry
09:50 @ ₹75.90, +₹3,036.50**, overnight gap +0.6034%. It entered
BEFORE both reads, so it is unconditioned and **kept at all 20 grid
points by construction**. Report Nov 3's morning state at both reads
(buildup class, RELVOL, RELVOL5, crowd) and, descriptively, what each
rule would have said had the leg entered after the read. One leg sets
no rule in either direction. If Nov 3's state is NC in any component,
say so — never estimate it.

## PASS BAR (per grid point, pre-registered — do not move)

ALL of: WR ≥ 60% · ₹/trade-day ≥ ₹900 · total ≥ ₹61,830.15 (60% of
the full book's +₹103,050.25) · H1 > 0 AND H2 > 0 · ex-top-3 > 0 ·
placebo percentile ≥ 0.95 · dropped-set control PASS · no new red
month (the book's red months ⊆ {2026-03}, the baseline's only red
month). Any leg failed = FAIL for that grid point, with the failing
leg(s) named.

## Deliverables

`phase3_buildup_nifty_2026-11-14.md` + `phase3_buildup_nifty_results.json`,
produced by `phase3_buildup_nifty_score.py`. The verdict must state
honestly whether the buildup/speculation state knows anything about
this book's legs, and through which dial — or that it does not.
