# TARANG Design 24 — STREAM-GROSS SURVEY, WAVE 2 — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 24 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run,
NO BOOK is built in this design.

## S.0 Why wave 2

Design 23's survey (tarang23_2026-11-17.md S.10) passed no
family, but it located the survey's only large economics:
the overnight gap. GAP-FADE grossed +₹335.73/trade in 2025
(the largest stream figure the programme has ever measured)
and failed only in 2026 (+₹11.59), and the failure was
located, not diffuse — the UP-gap fade held both years
(+₹166.68 / +₹39.31) while the DOWN-gap fade inverted
(+₹571.27 → −₹20.09). Two further streams had one side
positive in both years at meaningful size: FH-MOM's shorts
(+₹28.10 / +₹28.31) and ORB-30's shorts (+₹31.66 /
+₹28.98). Wave 2 surveys those located slices as fresh,
pre-registered streams under the IDENTICAL protocol and
the IDENTICAL unmoved bar. A wave-2 pass earns a Design 25
book under the full gate; a wave-2 fail completes the
survey's verdict — no raw single-signal stream on this
universe reaches the levy — and the programme's next move
is on the cost/capture side, not a ninth signal.

## S.1 Basis and universe

Identical to Design 23 (tarang23_SPEC.md S.1): equity
cash, PROVISIONAL per 100 shares, ₹40/trade cost levy,
paper only, real money ₹0. No stock options. Universe: the
127 verified F&O names of Designs 7–23, 5-min bars from
the same stores, 2025-01-01 to 2026-11-13, loaded by
`tarang6_score.load_name6`. Years by trade date; 2026 runs
to the store's end (2026-11-13).

## S.2 Common survey protocol (identical to D23 S.2)

- **Stream**: every signal the family's rule produces, at
  most ONE trade per name-day per family — the FIRST
  qualifying signal of the day. No caps, no allocation,
  no filters, no ranking.
- **Entry**: the open of the bar AFTER the signal bar,
  except the families whose signal is defined at a session
  boundary (all GAP families: entry is the day's first-bar
  open, the gap being known at the open; FHMOM-SHORT:
  entry is the open of the 10:15 bar). An entry that would
  fall after the square-off bar is not taken (counted as
  unfilled and disclosed).
- **Exit — ONE standard exit** (the drift form, unchanged):
  disaster stop at entry × 0.99 (LONG) / entry × 1.01
  (SHORT), stop-first, a bar that opens through the stop
  fills at the bar's open, otherwise exit at the CLOSE of
  the square-off bar (the day's last bar with timestamp
  ≤ 15:15). The exit scan starts at the entry bar itself.
  Implementation: `tarang20_score.exit20_engine`, unchanged.
- **Money**: gross = (exit − entry) × side × 100 shares.
  net = gross − ₹40. Win rate = share of trades with
  net > 0.
- **Score per family per year**: trades taken (and raw
  signals / unfilled count), gross ₹, gross/trade, net ₹,
  net/trade, win rate, LONG gross/trade and SHORT
  gross/trade (side split), stop share, square-off mean
  gross/trade.
- **SURVEY PASS**: gross/trade STRICTLY greater than
  ₹40.00 in BOTH 2025 and 2026. Anything else is a survey
  fail, whatever its net, win rate or single-year figure.

## S.3 The six families (exact signal definitions)

Bars are 5-minute bars timestamped by bar start. gap% is
defined exactly as in D23 S.3.4: (today's first-bar open /
previous trading day's last bar close) − 1, the previous
trading day being that name's previous day in the store.
A name's first store day has no previous day and is
skipped (counted).

1. **GAP-FADE-UP** — gap% ≥ +0.010 → SHORT, entered at the
   day's first-bar open. (The up-gap half of D23's
   GAP-FADE, the side that held both years.)
2. **GAP-FADE-UP-15** — gap% ≥ +0.015 → SHORT, entered at
   the day's first-bar open.
3. **GAP-FADE-15** — |gap%| ≥ 0.015 → fade: up-gap SHORT,
   down-gap LONG, entered at the day's first-bar open.
4. **GAP-FADE-20** — |gap%| ≥ 0.020 → fade, as family 3.
5. **FHMOM-SHORT** — the D23 FH-MOM rule (S.3.6 of the
   D23 SPEC: first-hour return = close of the 10:10 bar /
   open of the 09:15 bar − 1; a day missing the 09:15,
   10:10 or 10:15 bar is skipped, counted), restricted to
   days whose first-hour return is < 0 → SHORT, entered
   at the open of the 10:15 bar. Return = 0 → no trade.
   The signal bar is the 10:10 bar, as in D23.
6. **ORB30-SHORT** — the D23 ORB-30 rule (S.3.1 of the
   D23 SPEC: opening range = high/low over the bars
   timestamped 09:15…09:40; a day missing any of those
   six bars, or the 09:45 bar, is skipped, counted),
   restricted to the SHORT outcome: the first bar from
   09:45 whose close is below the range low, provided no
   earlier bar from 09:45 closed above the range high
   (first break of the day wins, as in D23 — a day whose
   first break is upward produces no ORB30-SHORT signal).
   Entry at the next bar's open.

## S.4 Controls (identical to D23 S.4, run in the same order)

1. **EKAM machinery control FIRST** —
   `tarang19_score.ekam_control()`: EKAM's own imported
   machinery on the frozen 25 must reproduce the published
   CAND-T5 (+₹62,164.57 / +₹63,883.60) and S2
   (+₹45,300.64 / +₹72,605.30) Jan–Oct lines exactly. If
   it fails, no Design 24 number is quoted.
2. **Signal parity** — every family's signal set is
   re-derived by an independent second implementation
   (pandas groupby/rolling path over the raw frames) and
   must match the engine's set exactly (name, date,
   stream, side, signal bar) on all 127 names.
3. **Exit parity** — every taken trade's exit is
   re-simulated by the independent audit exit
   (`tarang20_score.exit20_audit`) and must match on bar,
   price and reason.
4. **Truncation spot-check** — 30 sampled trades: the
   signal is recomputed from bars cut at the signal bar
   and must be present and identical (no look-ahead).
5. **Independent re-sum** — the written
   `tarang24_trades.csv` re-sums to the reported gross and
   net per family per year to the paisa.
6. **Subset cross-check (new in wave 2, arithmetic only)**
   — GAP-FADE-UP must reproduce D23 GAP-FADE's SHORT-side
   figures, FHMOM-SHORT must reproduce D23 FH-MOM's SHORT
   side, and ORB30-SHORT must reproduce D23 ORB-30's
   SHORT side, since each is exactly that side's trade
   set under the identical protocol. Any mismatch is a
   machinery fault, disclosed and fixed before reporting.

## S.5 What this design does not do

No gate table, no placebo, no per-entity tuning, no
November slice verdict (identical to D23 S.5). The
survey's only verdict per family is PASS (gross/trade
> ₹40 both years) or FAIL, with the anatomy reported
either way. A passing family earns a Design 25 book under
the full unmoved gate — the survey pass alone arms
nothing and starts no paper run.
