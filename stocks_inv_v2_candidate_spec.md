# Stocks EQUITY — INV-LONG — v2 CANDIDATE spec (frozen 2026-10-31)

**CANDIDATE ONLY — not adopted, not a system, no orders. Paper
only, real money ₹0. EQUITY CASH intraday, LONG/SHORT language.
Every rupee figure: provisional per 100 shares, ₹40/trade flat
cost. Source: INV tuning loop, `stocks_tuning_inv_report.md`
(spec `stocks_tuning_inv_frozen.md`, frozen before scoring;
validation gate reproduced Round 8/9/10 figures to the paisa).**

## Status — what this is, and what it does NOT change

The November 2026 INV1 shadow runs **exactly as frozen** in
`stocks_p2inv_november_shadow_spec.md` (both directions,
T125/S050 primary). This candidate changes nothing about
November. It is the INV line's **v2 candidate**: a direction
restriction suggested by Round 10's direction split (A4) and
confirmed through the tuning loop's full pass gate on the same
Jan–Oct data that suggested it — which is why it is a
*hypothesis with a frozen shape*, not a result. Its verdict
requires a fresh window, pre-declared below.

## The rule — exact (delta from the INV1 shadow spec is ONE line)

1. **Entry pool: P2, exactly as Rounds 6–9** — frozen V5
   re-entry signal stream (`stocks_equity_reentry.py`
   `pool_pick` over v4 + skill_or detectors); chain round ≤ 2
   under the exit's own timing; entry_time < 10:30; ADR≥3%
   stock-day (prior-10-day mean (high−low)/close×100, min 5
   prior rows, trade day excluded).
2. **Inverted condition:** Nifty previous close ≤ its 50DMA
   (daily bars strictly before the trade day; 50DMA = mean of
   the 50 closes ending at the previous bar; equality = met).
   If the 50DMA cannot be computed, no trades that day.
3. **DIRECTION: LONG entries only.** SHORT signals in the pool
   are not taken. (This is the only change from INV1.)
4. **Exits: primary T125/S050** — target +1.25% / stop −0.5%,
   stop-first on a same-candle tie, 15:10 square-off.
   **Shadow column T10/S050** (+1.0% / −0.5%) recorded per
   trade; unlike combined INV1, the LONG-only set is
   both-halves positive at T10 as well (see below), so the
   shadow column is a genuine second reading, not a known-bad
   one.
5. All qualifying LONG trades are taken; no portfolio cap, no
   per-stock cap beyond chain round ≤ 2 and one open position
   per stock at a time.

## In-sample record (Jan–Oct 2026 — hypothesis-generation only)

At **T125/S050**: 249 trades, win 36.1%, gross expectancy
+₹137.13/trade, net expectancy +₹97.13/trade, net
**+₹24,185.73** provisional per 100 shares — halves
**Jan–May +₹14,751.12 (200 trades) / Jun–Oct +₹9,434.61
(49 trades)**, October +₹7,691.08 (21 trades). Breadth
**12/25** stocks net-positive; top-3 share 116.2%.
At **T10/S050**: 256 trades, net +₹16,584.48, halves
+₹3,120.30 / +₹13,464.18 — the combined-INV1 T10 Jan–May flip
(−₹517.74) is **cured on the LONG side**; it was entirely a
SHORT-side artefact (SHORT-only at T10: Jan–May −₹3,638.04).
Reference points: combined INV1 at T125 = 694 trades,
+₹22,964.30, expectancy +₹33.09 — the LONG-only subset earns
more in total on 445 fewer trades, with the most balanced
halves of any configuration in the tuning loop.

**Concentration disclosure (must travel with this candidate):**
TVSMOTOR (+₹15,287.54) and GLENMARK (+₹8,252.87) together are
≈97% of the candidate's Jan–Oct net; ASTRAL (+₹4,565.74) is
third. The remaining 22 stocks net ≈ −₹3,920 combined. Breadth
12/25 is real (twelve stocks positive), but the money is
concentrated in two names — exactly the failure mode the
fresh-window test exists to judge.

## Recorded alternates — NOT carried (with reasons)

- **T125_S065 LONG-only** (stop −0.65%): also passes the full
  gate — 237 trades, +₹19,100.60, halves +₹12,331.80 /
  +₹6,768.80, breadth 13/25 (best in the loop). Not carried:
  lower total and weaker Jun–Oct than the primary-exit
  candidate; changing the frozen stop as well as the direction
  would be two changes, and the tie-break favours the single
  change at the November shadow's own exit.
- **T100_S050 LONG-only**: passes (256 trades, +₹16,584.48)
  but its Jan–May is thin (+₹3,120.30) and its Jun–Oct leans
  on October (+₹11,921.50 of +₹13,464.18). Recorded as the
  T10 reading of the carried candidate instead.
- **N20 condition (= INV2, both directions) at T125**: passes
  the gate with the loop's highest totals (563 trades,
  +₹48,437.14, halves +₹24,913.18 / +₹23,523.96, breadth
  11/25, top-3 86.4%) — but this is Round 10's pre-existing
  alternate, not a tuning-loop discovery, and it carries
  Round 10's recorded warning: **March alone is 63.6% of its
  total** and its February is −₹13,940.37. Not carried, for
  the reason recorded in Round 10: choosing the highest
  in-sample net after seeing all variants is the fitting this
  exercise avoids. It remains on record for a future frozen
  decision.
- **DBL condition** (Nifty ≤50DMA AND stock prev close ≤ own
  20DMA) at T125: both halves positive and balanced
  (+₹7,861.57 / +₹8,687.21, 390 trades, October +₹8,916.58)
  but breadth 9/25 — **fails the breadth leg by one stock**.
  Near-miss, recorded.

## Judging rule — fresh window (pre-declared)

- The November shadow log (both directions) lets the LONG
  subset be *read* informatively at November month-end, but
  that reading is NOT this candidate's verdict: November was
  frozen for the combined hypothesis before this candidate
  existed.
- This candidate earns its own frozen fresh-window test
  (window and logging to be set by a separate frozen decision
  after November's judgement — e.g. December 2026), judged on
  the primary exit T125: **positive net with ≥ 20 trades
  upgrades INV-LONG to a second candidate window; negative net
  kills the direction restriction** (the combined INV1
  hypothesis then stands or falls on its own November/
  December record). A window with < 20 qualifying LONG trades
  is inconclusive.
- No re-tuning of this candidate on Jan–Oct data: the pool,
  the condition, the direction restriction and the exits above
  are frozen as of this file.

Stage work only. Nothing here is adopted; nothing here is a
live-trading instruction.
