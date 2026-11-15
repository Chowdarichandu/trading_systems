# PHASE-3 TUNING — BANK NIFTY · BUILDUP / SPECULATION CONDITIONING · SPEC (FROZEN BEFORE SCORING)

Frozen: 2026-11-14 (IST), before any phase-3 scoring was run.
Owner's order: 2026-11-14 09:02 — tuning does NOT stop until the result is
got; tuning = adjusting parameters in small turns, using the data on hand.
Owner's named surface (his words): long buildup / unwinding and the other
buildup classes, previous-day volume compared with today's, call rates vs
put rates (where the speculation is positioning), and whether our trades go
in the correct direction relative to all that. Research only — no book,
ledger, or job is changed by this run. Buying only, 1 lot, Bank only.

## What this round is (and is not)
This round conditions the EXISTING book's proven legs on the morning
buildup/speculation state. It generates NO new trades and changes NO exits.
It is parameter tuning of TUNED STACK v2: small turns of keep/idle dials.

## Book under test (control)
TUNED STACK v2, Jan–Oct 2026 gated leg store, loaded exactly as phase 2:
- Features store: solid60_programme_2026-11-13_bank_A_stack_features.csv (111 legs)
- Anatomy store: november_books_fix_anatomy_legs.csv, book=BANK_STACK (111 legs)
- Join key: (date, entry_time, entry_premium), 111/111.
- Control to reproduce BEFORE scoring: 111 legs · +₹127,351.50 · WR 59.5% ·
  89 trade-days · ₹1,430.92/trade-day · 60G/29R/116NT of 205 days ·
  H1 +₹83,082.00 / H2 +₹44,269.50 · ex-top-3 +₹100,528.50 · zero red months ·
  independent raw re-sum +₹127,351.50. If the control fails, stop and report.

## Data
- Futures: round5_history/FUT7_<expiry>.json — near-month Bank Nifty futures
  5-min candles, all 7 fields (vol + OI). In-force contract for day d =
  FUT7 file of the expiry carried for d in oi_history/banknifty_daily_oi.csv
  (the same in-force expiry mapping the round-5 options dataset used).
- Options: round5_ioi_data/chunks/ — near-band option 5-min candles, 7 fields.
  That dataset's own completeness: 187 complete / 18 NC_BAND of 205 Jan–Oct
  days (round5_ioi_dataset.csv, 10:55 band). THIS round re-derives its band
  (below) and reports its own coverage; nothing is filled silently.
- Spot (band anchor only): daily2leg/spot.json (Jan–Oct) and
  oi_history/spot_nov_bars.json (November), BANKNIFTY 5-min bars.
- Day sequence: the 205 Jan–Oct trading days from oi_history (in date order),
  extended by the November trading days for the counterfactual.

## Morning state (entry-knowable only)
Two pre-registered reads: R = 10:00 and R = 11:00.
State at read R is computed ONLY from 5-min bars with start time < R
(last state bar starts at R−5 and completes exactly at R). Base = the 09:15
bar. A leg is conditioned by read R iff entry_time >= R; legs entered before
the read are untouched (always kept) by that read's conditioners.

(a) FUTURES BUILDUP CLASS (per day, per read):
  price_chg% = (close of last state bar − close of 09:15 bar) / close of
  09:15 bar × 100. oi_chg% = (OI at last state bar − OI at 09:15 bar) /
  OI at 09:15 bar × 100. Directional OI band: |oi_chg%| > 0.5% counts as
  directional; |oi_chg%| ≤ 0.5% → NEUTRAL. price_chg% == 0 → NEUTRAL.
    price>0, OI up   → LONG_BUILDUP   (bullish)
    price<0, OI up   → SHORT_BUILDUP  (bearish)
    price<0, OI down → LONG_UNWINDING (bearish)
    price>0, OI down → SHORT_COVERING (bullish)
(b) RELATIVE VOLUME (futures): cumulative bar volume over bars 09:15..R−5
  today ÷ the same-clock window on the previous trading day (ratio_prev),
  and ÷ the mean of the same window over the previous 5 trading days
  (ratio_5d). Previous days use their own in-force futures contract.
(c) CALL/PUT SPECULATION (options): band = the 11 strikes nearest the day's
  OPENING spot (close of the spot 09:15 bar), same band both reads, both
  types. ΔOI per type = Σ over band contracts of (OI at last state bar −
  OI at 09:15 bar). Speculation index = (ΔOI_CE − ΔOI_PE) /
  (|ΔOI_CE| + |ΔOI_PE|); denominator 0 → FLAT. Lean: index > +0.15 → LONG,
  index < −0.15 → SHORT, else FLAT.

NC RULES (frozen): if any band contract lacks the 09:15 bar or any state bar
needed, the speculation component is NC for that day-read (NO partial-band
sums). If futures bars are missing, buildup + volume are NC for that
day-read. If the previous-day (or 5-day) window is unavailable, that volume
ratio is NC. An NC component makes the leg UNCONDITIONABLE for grid points
that need it: the leg is KEPT unconditionally and counted as NC-kept
(the same philosophy as "neutral = keep": we idle only on positive evidence).

## Tuning grid (minute turns — all frozen here; per read R ∈ {10:00, 11:00})
Kept set = pre-read legs + NC-kept legs + post-read legs passing the rule.
  A      DIRECTION ALIGNMENT: keep a post-read leg iff the buildup class
         does not oppose its side (bullish class opposes PE; bearish
         opposes CE; NEUTRAL opposes nothing).
  B      A + SPECULATION: additionally the call/put lean must not oppose
         the leg's side (LONG lean opposes PE; SHORT lean opposes CE;
         FLAT opposes nothing).
  C1.0 / C1.1 / C1.25   VOLUME GATE: keep iff ratio_prev ≥ t.
  C5-1.0 / C5-1.1 / C5-1.25  VOLUME GATE on ratio_5d ≥ t (reported variant).
  D1.0 / D1.1           A + volume gate ratio_prev ≥ t.
  E      A + speculation-not-oppose + volume gate ratio_prev ≥ 1.0.
11 grid points per read, 22 total. No other combinations will be scored.

## Scoring per grid point
Kept legs, dropped legs, total, WR, trade-days, ₹/trade-day, green/red/
no-trade days (205-day universe), full month table (months fully idled are
listed, not silently absent), halves (Jan–May / Jun–Oct), ex-top-3,
NC-kept count.

## Placebos + flipped control (per grid point, pre-registered)
- 200 random subsets of the SAME kept size from all 111 legs (seed 42);
  statistic = subset total. Conditioner must beat ≥ 95% of draws
  (kept total > the draws' 95th percentile).
- Direction-flipped control: flipped book = all legs EXCEPT the post-read
  legs the conditioner KEPT (i.e., it keeps exactly the dropped ones).
  Conditioner must beat its flipped book on total. The dropped legs'
  standalone total is also reported.

## Pass bar (pre-registered, NOT to be moved)
A grid point PASSES only if ALL hold: WR ≥ 60% · ₹/trade-day ≥ ₹900 ·
total ≥ 60% of +₹127,351.50 (≥ ₹76,410.90) · both halves positive ·
ex-top-3 positive · placebo percentile ≥ 95 · kept total > flipped total ·
no red month. Any failing leg is named per grid point.

## Distinctness (pre-registered statement)
- IOI-1 / IOI-2 (CLOSED): standalone intraday-OI momentum SIGNALS that
  generated their own entries at a 10:55 read. This round generates no
  entries; it only keeps/idles the stack's own legs.
- FLOW-VOL (CLOSED): standalone futures volume-thrust + basis SIGNAL with
  its own entries and exits. Here volume never generates anything — it is
  only a keep-gate on stack legs, with no basis term, and it must survive
  the dropped-set control FLOW-VOL never faced.
- Day-level OI V1–V3 (CLOSED): standalone signals on previous-day OI
  changes. Here the state is intraday, same-morning, and conditions an
  existing book rather than signalling.
- Phase-2 confidence gating: a per-leg composite of the leg's own features.
  Here the conditioner is market positioning state (futures OI quadrants,
  option OI lean, relative volume) — a different information surface.
If any conditioner collapses into one of the closed mechanisms, it is
dropped and the collapse is stated.

## November counterfactual (descriptive only)
Apply every grid point to the stack's 4 actual November legs
(Nov 4 S3-R1 PE 09:55 +₹2,480 · Nov 9 Skill V3 PE 10:45 −₹1,720 ·
Nov 12 S3-R1 PE 11:30 −₹1,720 · Nov 13 NS3 PE 12:20 −₹1,720; total
−₹2,680), with state computed from November futures/options data
(expiry 2026-11-23). Nov 4 (09:55) is pre-read for both reads → always kept.
Report per grid point which legs are kept/idled and the kept total.
November sets no rule; description only.

## Deliverables
phase3_buildup_bank_2026-11-14.md + phase3_buildup_bank_results.json.
