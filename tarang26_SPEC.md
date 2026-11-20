# TARANG Design 26 — FORWARD PACK + TWO NAMED WOUNDS — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 26 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run
started, no live book touched, no cron created. **T25-C's
forward paper starts only on the owner's explicit word —
this design prepares the pack; it does not start it.**

## S.0 Why this design

Design 25 produced the programme's first full-gate PASS:
**TARANG-T25-C (GAP-FADE-UP-15)** — net +₹1,51,307.50 /
+₹50,274.68, 9 of 9 legs, placebo percentile 100.0 in
both years. Its Design 26 seed named three workstreams:

1. **WS1 — the forward-paper pack for T25-C** (frozen
   rules + a scorer on the same definitions), prepared
   for the owner's word. Preparation only.
2. **WS2 — a clustered-day guard for the two-sided
   books** (T25-A failed 7/9 on the 2026 LONG side +
   month floor; T25-B failed 5/9 after largest-|gap|
   allocation kept only 12.3% of its 2026 stream gross
   on market-wide clustered days).
3. **WS3 — the capture side of the passing book**
   (T25-C's stop tail: ~57% of trades stop at ~−₹750…
   −₹850 net each against the square-off drift).

## S.1 Basis and universe

Identical to Designs 23–25: equity cash, PROVISIONAL per
100 shares, ₹40/trade cost levy, paper only, real money
₹0. No stock options. Universe: the 127 verified F&O
names of Designs 7–25, 5-min bars from the same stores,
2025-01-01 to 2026-11-13. Years by trade date.

## S.2 WS1 — T25-C forward-paper pack (preparation only)

- `tarang25c_forward_pack.md` states the frozen rules
  exactly as gated in Design 25 (SPEC tarang25_SPEC.md
  S.2–S.4, book TARANG-T25-C): up-gap ≥ +1.5% vs the
  name's previous store day's last close, SHORT at the
  day's first-bar open, −1.0% disaster stop stop-first,
  else 15:15 square-off; caps 10/day, 1/name-day;
  allocation |gap%| DESC, vol_ratio DESC, universe
  order.
- `tarang25c_scorer.py` — given a date, computes that
  day's T25-C signals from the stored bars and scores
  them with the frozen exits, using the same machinery
  (tarang23 prep/day_ctx, tarang24 sig_gapw2, tarang23
  take_trade, tarang25 allocate25/vol_ratio_at).
- **Self-test (mandatory before the pack is reported):**
  the scorer is run on two historical trading days —
  2025-08-18 and 2026-03-24, both cap-bound 10-trade
  days in the published book — and its output must
  reproduce the published Design 25 trades for those
  dates (tarang25_trades_TARANG-T25-C.csv) exactly:
  same taken set, same entry/exit prices, reasons and
  nets. The result is stated in the Design 26 report.
- The pack is NOT scheduled, NOT run as a live book, and
  no cron is created. It waits for the owner's word.

## S.3 WS2 — clustered-day guard (T25-A, T25-B; research)

**Cluster definition (ONE primary, pre-registered):** a
book-day is a **CLUSTER DAY** for a book if that book's
own candidate pool on that day (Design 25 pools, before
caps) contains **≥ 15 candidates**. The count is known at
the open (every candidate is a first-bar gap event), so
the guard is causal. The threshold is 1.5× the 10/day
cap — days where allocation choice binds hardest.

**Variants** (per book; mechanics, exits, ranking frozen
from Design 25 — only the taken set changes):

- **TARANG-T26-A-SKIP / TARANG-T26-B-SKIP:** take NO
  trades on cluster days; all other days exactly as
  Design 25.
- **TARANG-T26-A-CAP3 / TARANG-T26-B-CAP3:** on cluster
  days take at most **3** trades (the same S.4 ranking,
  top 3); all other days exactly as Design 25.

Both variants are pure subsets of the Design 25 taken
sets (the cap-3 set is the top 3 of the same ranking
whose top 10 Design 25 took). Every variant is re-run
under the **full 9-leg gate** (S.5) and reported leg by
leg with the diff vs the unguarded book (trades removed,
net removed, per year).

## S.4 WS3 — T25-C capture side (research; frozen book NOT modified)

Entries are T25-C's exact taken set (1,111 trades,
Design 25). Only the exit changes. For each trade:
entry px = the first-bar open; prev_close = the name's
previous store day's last close; the **half-retrace
level** is **H = (px + prev_close) / 2** (for T25-C's
SHORT up-gap fades, H < px always).

- **TARANG-T26-C-TARGET (gap-half target):** exit at H
  when price retraces to H. Bar scan from the entry bar,
  per bar, in this order: (1) the frozen −1.0% disaster
  stop (stop-first, exactly as exit20 — a bar opening
  through the stop fills at the open, else at the stop);
  (2) the target — LONG: a bar opening ≥ H fills at the
  open, else a bar whose high ≥ H fills at H; SHORT
  mirrored (open ≤ H fills at the open, else low ≤ H
  fills at H); (3) the square-off bar (last bar ≤ 15:15)
  exits at its close. Exit reason "target".
- **TARANG-T26-C-TRAIL (trailing-after-half):** the
  disaster stop starts at the frozen −1.0% level. Once a
  bar's favourable extreme reaches H (LONG high ≥ H;
  SHORT low ≤ H), the stop moves to **breakeven (px)**
  from the NEXT bar onward (arming is evaluated after
  the bar's own stop/square-off checks, so a bar never
  both arms and is stopped by the new level). From then
  on the stop check uses px with the same fill rules
  (open-through fills at the open, else at px); exit
  reason "trailstop" (unarmed stop exits keep "stop").
  Square-off unchanged.

Each variant is re-run under the **full 9-leg gate**
(S.5) as a separate research line, reported against the
frozen book's published legs. The frozen T25-C book is
not modified, re-scored or renamed by this workstream.

**Placebo target convention (pre-registered):** the
random-entry placebo for a WS3 variant uses the variant
exit, with the half level for a random entry defined
from that entry's own name-day: d = 0.5 × |px −
prev_close| of the randomly chosen name-day, H = px +
side × d (the favourable half-retrace of that day's own
gap distance). The direction-flip placebo likewise uses
the variant exit with H defined from the trade's own
name-day gap, favourable to the flipped side.

## S.5 Controls, audits and gate (WS2 + WS3)

1. **EKAM machinery control FIRST** (tarang19_score
   .ekam_control) — exact reproduction required before
   any Design 26 number is quoted.
2. **WS2 subset audit:** every variant trade matches a
   Design 25 taken trade on all economics fields; caps
   verified (≤10/day overall; 0 trades on cluster days
   for SKIP; ≤3 on cluster days for CAP3; ≤1/name-day);
   cluster classification independently recounted from
   the candidate pools.
3. **WS3 exit parity:** every variant trade's exit is
   computed by an engine bar-loop AND an independent
   audit implementation (two-phase for TRAIL); 0
   mismatches on bar, price and reason. Entry, gap and
   net recomputed from the stored bars; H recomputed
   from the name's previous store day.
4. **Truncation spot-check:** 30 sampled trades per
   workstream recomputed from bars truncated at the
   decision point (WS2: previous day + first bar; WS3:
   bars up to the exit bar) must reproduce the trade.
5. **Placebos:** 200-draw random-entry placebo with the
   line's OWN exits and own per-day counts (family
   construction, D25 SPEC S.5.7a; WS3 per S.4's target
   convention); direction-flip placebo (information).
6. **Independent re-sum** — the written
   tarang26_trades.csv re-sums to every reported net per
   line per year to the paisa.
7. **Gate (unmoved — tarang2_score.gate_for):** per line,
   all nine legs: net positive BOTH years · beats the
   random-entry placebo p90 BOTH years · ex-top-3
   positive BOTH years · no month worse than −₹15,000 ·
   November 2026 slice ≥ −₹3,000 · audits clean.

## S.6 Anatomy (reported per line)

Every gate leg; placebo percentiles and p90s; flip
placebo; side splits; win rate; trades and trading days;
max drawdown; month table; top-10 contributors per year;
gross/cost/net per trade; resolution mix (stop / target
/ trailstop / square-off). WS2 additionally: cluster-day
counts per book per year, trades and net removed by the
guard per year. WS3 additionally: how many frozen-book
stops each variant converted, and to what (target /
trailstop / still stop), with the net diff per class.

## S.7 What this design does not do

No new signal, no threshold change, no change to the
frozen T25-C book, no forward run of anything. WS2/WS3
lines are research lines; a variant that passes the gate
is a candidate for the owner's word, nothing more.
