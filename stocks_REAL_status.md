# Stocks hunt — REAL status (verified 2026-10-31, ~08:55 IST)

Equity cash intraday only, LONG/SHORT. **Paper only — real money ₹0, no
orders.** All figures provisional per 100 shares, ₹40/trade cost deducted,
Jan–Oct 2026 (October = 1–28 Oct in the 5-min work). Every total below was
**re-summed from its trade dump by script on 2026-10-31** and every system's
entry timing was audited against the moment its qualifying information
becomes complete. That audit is what killed the Morning-Mover (see Dead
list) — the three systems below pass both checks.

---

## Surviving systems — verified

### 1. INV-LONG — RE-SUM ✅ · TIMING ✅ CLEAN
- Dump: `tuning_inv_T1_T125_S050_trades.csv` (LONG rows; identical LONG
  subset also in `eq_round10_INV1_trades_T125.csv` and
  `tuning_inv_T4_T125_S050_INV1_trades.csv`).
- Re-sum: **249 trades, +₹24,185.73 — reproduces the claimed total to the
  paisa.**
- Halves: Jan–May **+₹14,751.12** (200 trades) / Jun–Oct **+₹9,434.61**
  (49 trades). October **+₹7,691.08**.
- Timing audit: qualifying information = INV1 condition, *Nifty previous
  close ≤ its 50DMA* (frozen spec: "daily bars strictly before the trade
  day") — complete **before the trade day opens**. Entries come from the
  day's own signal stream in time order (sampled entries 09:35–10:05, all
  on the trade day, after the open). Entry strictly after information
  complete → **CLEAN**.
- Standing weakness (unchanged): TVSMOTOR + GLENMARK ≈ 97% of the net;
  ex-both, Jun–Oct flips negative. Frozen candidate
  (`stocks_inv_v2_candidate_spec.md`); INV1 (both directions) runs as the
  November shadow.

### 2. N4-V3 at T125 — RE-SUM ✅ · TIMING ✅ CLEAN
- Dump: `eq_n4deep_v3_trades_T125_janoct.csv` (cross-checked:
  `eq_eventaxis_EA3_T125_trades.csv` sums identically).
- Re-sum: **56 trades, +₹7,990.43 — reproduces to the paisa.**
- Halves: Jan–May **+₹5,155.13** (34 trades) / Jun–Oct **+₹2,835.30**
  (22 trades). October **−₹530.69**.
- Timing audit: qualifying information = reaction-day move ≥1% measured
  by the **09:30 bar close** — complete at 09:30. **Every one of the 56
  entries is at 09:35**, the next bar. Entry strictly after information
  complete → **CLEAN**.
- November PRIMARY, runs exactly as frozen from Mon 2026-11-02.

### 3. P2F — RE-SUM ✅ (both bands) · TIMING ✅ CLEAN
- Dump: `stocks_tuning_event_V1_combined_trades.csv` (leg = P2F;
  2.5% band = the |reaction_ret_pct| ≥ 2.5 subset of the same dump).
- Re-sum: 2.0% band **48 trades, +₹12,835.88 — to the paisa**;
  2.5% band **39 trades, +₹15,489.08 — to the paisa**.
- Halves: 2.0% → Jan–May **+₹3,498.10** (29) / Jun–Oct **+₹9,337.78**
  (19), October **−₹102.83**. 2.5% → Jan–May **+₹6,702.84** (26) /
  Jun–Oct **+₹8,786.24** (13), October **−₹315.00**.
- Timing audit: qualifying information = the reaction day's close
  (reaction return known only after that day's close). **Every entry is
  at 09:15 on the following trading day** (sampled rows show trade date
  = R + 1 trading day). Entry strictly after information complete →
  **CLEAN**.
- November shadow as frozen (first trade pre-booked: GODREJCP SHORT,
  Mon 2 Nov 09:15 open). Note: P2F **failed the transfer test** on the
  new-25 universe (H1 −₹196.26 there) — it survives as a home-universe
  shadow only, not as a proven candidate.

---

## Dead list — one-line causes

- **Morning-Mover, ALL versions (10:00 / 10:15 / 10:30 / 11:30)** —
  look-ahead leak: days were qualified on a move measured later in the
  day while entries were taken from earlier signals; honest rebuild
  (signals only after the measurement) is negative at every time.
  All headline totals (+₹84k / +₹249k / +₹465k …) **retracted**.
- **A2 / B2 / B3 tuned variants** — same leaky engine; their
  +₹406k / +₹812k / +₹1.62M were the leak compounding. Dead with it.
- **EventBook (N4-V3 + P2F as one book)** — killed by its own frozen
  concentration stress: ex-top-3 payers it is negative (−₹3,046.87).
  (Its two legs survive individually, above.)
- **DBL-LONG** — passes at home (+₹24,327.37) but **fails transfer** to
  the new 25 large caps (H2 −₹3,339.63, breadth 5/25). Dead.
- **LADDER + volume, SNAP, EXTREME-HUNT, cross-sectional RS, transplanted
  index systems (V5/Skill/(lA) as stock entries)** — negative totals or
  expectancy that flips sign between the Jan–May and Jun–Oct halves.
  Dead.

## November board — as it now stands (from Mon 2026-11-02)

1. **N4-V3 — PRIMARY** paper logging, Mon–Fri ~15:52 IST
   (`stocks_n4_november_paper_log.csv`).
2. **INV1 — shadow** (both directions, as frozen), ~16:52 IST.
3. **P2F — shadow**, ~17:22 IST.
4. **Morning-Mover loggers (home + ext) — DISABLED 2026-10-31** before
   launch; they would have certified an unexecutable rule.

No re-tuning during November. Month-end verdicts per the frozen judging
rules in each spec.
