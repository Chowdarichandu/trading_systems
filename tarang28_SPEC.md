# TARANG Design 28 — A-ASYM-25 (LONG THRESHOLD 2.5%) — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 28 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run
started, no live book touched, no cron created. **No
forward paper — frozen T25-C or TRAIL — starts without
the owner's explicit word; this design is a research
line only.**

## S.0 Why this design

Design 27's A-ASYM (SHORT up-gaps ≥ 1.5% frozen; LONG
down-gaps ≥ 2.0%) reached 8 of 9: it repaired T25-A's
month floor outright (Jan 2026 −₹15,840.99 →
−₹12,933.89) and narrowed the surviving deficit by 74%
(2026 ex-top-3 −₹11,205.18 → −₹2,914.55). The one leg
still failing is 2026 ex-top-3, and the wound is
located: the ≥ 2% down-gap longs the capped book
actually takes are themselves gross-negative in 2026
(−₹23.43/trade, LONG net −₹22,011.15), while the SHORT
side pays +₹51,886.60. Design 27's seed named the
direct test: raise the LONG threshold one more rung,
to ≥ 2.5%, SHORT frozen — does any down-gap threshold
make the two-sided book's 2026 ex-top-3 positive?

**Closure clause (pre-registered, from the D27 seed):**
if A-ASYM-25 fails the same leg (2026 ex-top-3), the
two-sided line is declared concentration-bound in 2026
and CLOSES — no further threshold rungs — and TARANG's
gated books are then the two T25-C packs (frozen and
TRAIL) awaiting the owner's word. The Design 29 seed
is written accordingly.

## S.1 Basis and universe

Identical to Designs 23–27: equity cash, PROVISIONAL
per 100 shares, ₹40/trade cost levy, paper only, real
money ₹0. No stock options. Universe: the 127 verified
F&O names of Designs 7–27, 5-min bars from the same
stores, 2025-01-01 to 2026-11-13. Years by trade date.

## S.2 The book — TARANG-T28-A-ASYM-25 (ONE book)

Candidate pool = the union of two sub-pools, built on
the family's engine path (tarang23 day_ctx/take_trade;
membership decided on the UNROUNDED gap = first-bar
open / previous store day's last close − 1, the same
quantity tarang24 sig_gapw2 thresholds):

- **SHORT sub-pool (FROZEN, exactly A-ASYM's):**
  up-gap ≥ +1.5% → SHORT — the GAP-FADE-UP-15
  candidates, unchanged in membership and in every
  standalone trade.
- **LONG sub-pool (the single change):** down-gap
  ≤ −2.5% → LONG (raised from A-ASYM's −2.0%). Stream
  label "GAP-FADE-25". Each member's standalone trade
  is the family's standard trade for that name-day
  (identical to its GAP-FADE-20 candidate trade —
  the threshold selects membership only).

A name-day gaps in one direction only, so the
sub-pools are disjoint by construction. Each candidate
carries the survey's standalone trade under the
family's one standard exit (exit20: −1.0% disaster
stop stop-first, else 15:15 square-off) plus the
Design 25 allocation keys (gap_pct, vol_ratio,
universe order).

**Entries, exits, caps and allocation exactly as
T25-A / A-ASYM:** entry at the day's first-bar open;
exit20 exits; caps 10 taken trades/day, 1 per
name-day; allocation by |gap%| DESC, vol_ratio DESC,
universe order ASC (tarang25 allocate25) over the
union pool.

## S.3 Gate (unmoved — tarang2_score.gate_for)

All nine legs: net positive BOTH years · beats the
200-draw random-entry placebo p90 BOTH years (placebo
with the book's OWN exits and per-day counts, family
construction, D28 seed base 20261128) · ex-top-3
positive BOTH years · no month worse than −₹15,000 ·
November 2026 slice ≥ −₹3,000 · audits clean.

## S.4 Controls and audits

In run order, mirroring Designs 25–27:

1. **EKAM machinery control FIRST**
   (tarang19_score.ekam_control) — exact reproduction
   of CAND-T5 (+₹62,164.57 / +₹63,883.60) and S2
   (+₹45,300.64 / +₹72,605.30) required before any
   Design 28 number is quoted.
2. **Candidate-pool parity:**
   (a) independent pandas-path validator sigsets for
   both D28 rules (SHORT ≥ +1.5%; LONG ≤ −2.5%)
   equal the engine sets exactly;
   (b) the SHORT sub-pool equals the published Design
   25 GAP-FADE-UP-15 pool (tarang25 gen_candidates)
   member-for-member, standalone trades identical;
   (c) the LONG-25 sub-pool is a strict subset of the
   GAP-FADE-20 LONG pool, standalone trades identical
   to the corresponding GAP-FADE-20 candidates;
   (d) all union candidates' standalone trades match
   the published Design 24 survey trades
   trade-for-trade (LONG-25 members under their
   GAP-FADE-20 survey row);
   (e) disjointness of the union verified.
3. **Exit parity + timing/leak audit** (tarang25
   audit_book on the union pool): exit re-simulation
   0 mismatches, entry at the first-bar open, gap
   recomputed from stored bars, no first-store-day
   trades, net recompute, caps (≤10/day, ≤1/name-day),
   independent allocation rebuild.
4. **Truncation spot-check:** 30 sampled taken trades
   recomputed from the previous day's bars plus
   today's first bar only must reproduce the signal:
   SHORT iff recomputed gap ≥ +1.5% (and sig_gapw2
   emits GAP-FADE-UP-15, side −1); LONG iff
   recomputed gap ≤ −2.5% (and sig_gapw2 emits
   GAP-FADE-20, side +1).
5. **Placebos:** 200-draw random-entry placebo with
   the book's own exits and per-day counts;
   direction-flip placebo (information).
6. **Independent re-sum** — the written
   tarang28_trades.csv re-sums to the reported net
   per year to the paisa.

## S.5 Anatomy (reported)

Every gate leg; placebo percentiles and p90s; flip
placebo; side splits (trades, net, gross/trade by side
by year) with the LONG side compared directly to
A-ASYM's (2026 LONG net −₹22,011.15, gross/trade
−₹23.43; 2025 LONG net +₹1,34,171.97); win rate;
trades and trading days; max drawdown (book and by
year); month table; top-10 contributors per year —
with TORNTPHARM's trades, net and share of the 2026
net stated explicitly (and the same figures recomputed
for A-ASYM from its published CSV); gross/cost/net
per trade; resolution mix (stop / square-off);
capped-vs-stream note; **the removed-band diff**: the
2.0–2.5% down-gap LONG candidates removed vs A-ASYM
(count, standalone net by year, band membership
verified on recomputed gaps) and the net of the
A-ASYM taken trades inside that band, by year; the
named failed-leg comparison (2026 ex-top-3: T25-A
−₹11,205.18 → A-ASYM −₹2,914.55 → A-ASYM-25 ?).

## S.6 What this design does not do

No change to the frozen T25-C book, either forward
pack, or the TRAIL research line's definitions; no
forward run of anything; no new signal; no third
threshold rung beyond this one — the closure clause
in S.0 binds.
