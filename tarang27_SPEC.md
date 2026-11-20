# TARANG Design 27 — TRAIL FORWARD PACK + ASYMMETRIC THRESHOLDS — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 27 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run
started, no live book touched, no cron created. **No
forward paper — frozen or TRAIL — starts without the
owner's explicit word; this design prepares packs and
runs research lines only.**

## S.0 Why this design

Design 26 produced two gate passes on T25-C's entries
(the frozen book's own pass was Design 25): the WS3
TRAIL exit variant passed 9 of 9 AND beat the frozen
book in both years (+₹1,58,473.60 / +₹74,939.33 vs
frozen +₹1,51,307.50 / +₹50,274.68, drawdown reduced in
both years). Design 26's seed named two moves, and this
design runs both:

1. **WS1 — the TRAIL forward-paper pack** beside the
   frozen pack (same preparation standard as Design 26
   WS1: frozen definitions, a scorer on the same
   machinery, a mandatory self-test), so the owner's
   forward-paper decision is a choice between two ready
   packs.
2. **WS2 — T25-A with asymmetric thresholds.** T25-A
   (two-sided GAP-FADE-15) failed 7 of 9 on two legs
   with one address: the 2026 down-gap (LONG) fade —
   2026 ex-top-3 −₹11,205.18 and Jan 2026 −₹15,840.99
   (month floor). The LONG side netted −₹27,227.78 in
   2026 (543 trades, gross/trade −₹10.14) while the
   SHORT side netted +₹48,812.60; in 2025 the LONG side
   paid +₹1,53,920.81. The threshold ladder (Designs
   23–24) priced both sides at 1.5% and 2.0% together
   but never priced the sides separately. WS2 raises
   the LONG side's threshold to ≥ 2.0% and freezes the
   SHORT side at ≥ 1.5% — the one construction the
   ladder has not yet priced.

## S.1 Basis and universe

Identical to Designs 23–26: equity cash, PROVISIONAL
per 100 shares, ₹40/trade cost levy, paper only, real
money ₹0. No stock options. Universe: the 127 verified
F&O names of Designs 7–26, 5-min bars from the same
stores, 2025-01-01 to 2026-11-13. Years by trade date.

## S.2 WS1 — TRAIL forward-paper pack (preparation only)

- `tarang25c_trail_forward_pack.md` states the TRAIL
  rules exactly as gated in Design 26 WS3
  (tarang26_SPEC.md S.4, line TARANG-T26-C-TRAIL):
  entries are T25-C's frozen entries (up-gap ≥ +1.5%
  vs the name's previous store day's last close, SHORT
  at the day's first-bar open; caps 10/day, 1/name-day;
  allocation |gap%| DESC, vol_ratio DESC, universe
  order); the exit is the frozen −1.0% disaster stop
  UNTIL a bar's favourable extreme reaches the
  half-retrace level H = (entry + prev_close) / 2 —
  from the NEXT bar onward the stop is breakeven
  (entry), with the same fill rules; arming is
  evaluated after the bar's own stop / square-off
  checks; otherwise the 15:15 square-off at the close
  of the last bar ≤ 15:15. Exit reasons: "stop" /
  "trailstop" / "squareoff".
- `tarang25c_trail_scorer.py` — given a date, computes
  that day's T25-C entries through the same family
  machinery (tarang23 prep/day_ctx, tarang24 sig_gapw2,
  tarang25 allocate25/vol_ratio_at) and scores them
  with the TRAIL exit (tarang26 exit26_trail_engine),
  so a forward day is scored by the identical
  definitions that passed the Design 26 gate.
- **Self-test (mandatory before the pack is
  reported):** the scorer is run on the same two
  pre-registered historical days as the frozen pack —
  2025-08-18 and 2026-03-24, both cap-bound 10-trade
  days — and its output must reproduce the published
  Design 26 TRAIL trades for those dates
  (tarang26_trades.csv, line TARANG-T26-C-TRAIL)
  exactly: same taken set, same entry/exit prices,
  reasons and nets. The result is stated in the
  Design 27 report.
- The pack is NOT scheduled, NOT run as a live book,
  and no cron is created. It waits for the owner's
  word, beside the frozen pack.

## S.3 WS2 — A-ASYM (research only; ONE book)

**Book TARANG-T27-A-ASYM.** Candidate pool = the union
of two frozen sub-pools, both from the family's engine
path (tarang24 sig_gapw2 + tarang23 take_trade, the
Design 25 candidate construction):

- **SHORT sub-pool:** GAP-FADE-UP-15 candidates —
  up-gap ≥ +1.5% → SHORT (exactly T25-A's short side,
  threshold frozen at 1.5%).
- **LONG sub-pool:** GAP-FADE-20 candidates with
  side +1 — down-gap ≤ −2.0% → LONG (the LONG side's
  threshold raised from 1.5% to 2.0%).

A name-day gaps in one direction only, so the
sub-pools are disjoint by construction. Each candidate
is the survey's standalone trade under the family's
one standard exit (exit20: −1.0% disaster stop
stop-first, else 15:15 square-off), plus the Design 25
allocation keys (gap_pct, vol_ratio, universe order).

**Entries, exits, caps and allocation exactly as
T25-A:** entry at the day's first-bar open; exit20
exits; caps 10 taken trades/day, 1 per name-day;
allocation by |gap%| DESC, vol_ratio DESC, universe
order ASC (tarang25 allocate25) over the union pool.

**Gate (unmoved — tarang2_score.gate_for):** all nine
legs: net positive BOTH years · beats the 200-draw
random-entry placebo p90 BOTH years (placebo with the
book's OWN exits and per-day counts, family
construction, D27 seed base 20261127) · ex-top-3
positive BOTH years · no month worse than −₹15,000 ·
November 2026 slice ≥ −₹3,000 · audits clean.

**Reported specifically** (the legs and side this
design exists to answer): the two legs T25-A failed in
Design 25 — 2026 ex-top-3 (was −₹11,205.18) and the
worst month (was Jan 2026 −₹15,840.99; Sep 2026
−₹15,733.29 also breached) — and the LONG side's net
by year vs T25-A's LONG side (2025 +₹1,53,920.81 /
2026 −₹27,227.78, recomputed from the published
Design 25 CSV), plus full side splits for A-ASYM.

## S.4 Controls and audits (WS2)

In run order, mirroring Design 25 S.5:

1. **EKAM machinery control FIRST**
   (tarang19_score.ekam_control) — exact reproduction
   required before any Design 27 number is quoted.
2. **Candidate-pool parity:** the union pool's two
   sub-pools equal the Design 25 candidate pools for
   GAP-FADE-UP-15 and the LONG side of GAP-FADE-20
   (rebuilt via tarang25 gen_candidates); disjointness
   verified (no shared (sym, date)).
3. **Exit parity + timing/leak audit** (tarang25
   audit_book on the union pool): exit re-simulation
   0 mismatches, entry at the first-bar open, gap
   recomputed from stored bars, no first-store-day
   trades, net recompute, caps (≤10/day, ≤1/name-day),
   independent allocation rebuild.
4. **Truncation spot-check:** 30 sampled taken trades
   recomputed from the previous day's bars plus
   today's first bar only must reproduce the signal
   and side (each sampled trade's sub-pool signal).
5. **Placebos:** 200-draw random-entry placebo with
   the book's own exits and per-day counts;
   direction-flip placebo (information).
6. **Independent re-sum** — the written
   tarang27_trades.csv re-sums to the reported net per
   year to the paisa. The gate's audit leg is settled
   with the real spot-check in the audit step, as in
   Designs 25–26.

## S.5 Anatomy (reported for A-ASYM)

Every gate leg; placebo percentiles and p90s; flip
placebo; side splits (trades, gross/trade, net by side
by year); win rate; trades and trading days; max
drawdown; month table; top-10 contributors per year;
gross/cost/net per trade; resolution mix (stop /
square-off); capped-vs-stream note (candidates vs
taken per year); the S.3 named comparisons vs T25-A.

## S.6 What this design does not do

No change to the frozen T25-C book, its forward pack,
or the TRAIL research line's definitions; no forward
run of anything; no new signal. WS2's book is a
research line: if it passes the gate it is a candidate
for the owner's word, nothing more.
