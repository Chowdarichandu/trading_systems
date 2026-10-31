# Line M1 — Month-Repair Loop — FROZEN WORKPLAN (Part A: bases, anchors, procedure)

Frozen 2026-10-31 BEFORE any M1 scoring. Equity cash intraday only,
LONG/SHORT language. **Paper only — real money ₹0, no orders.**
Every figure provisional per 100 shares, ₹40/trade already deducted.
Universe: **Chandu's own 25 watchlist stocks ONLY** (home universe,
`data/progressive/`). Window Jan–Oct 2026.

## The user's spec

A strategy where **October is positive and EVERY month Jan–Oct ends
positive**. Method: start from October, take failing months one at a
time (September first if it fails, then backward Aug, Jul, … Jan),
DEBUG why the month fails, FIX with a rule, re-run that month AND
every already-green month. A fix that breaks a green month is
rejected.

## Hard guards (non-negotiable, from the 2026-10-31 fake-data failure)

1. A fix must be an **ex-ante rule** computable at entry time from
   past/current data only. Never a date filter, never a per-month
   parameter, never "skip month X", never a stock blacklist derived
   from the target month alone (a trailing-window performance gate
   computed from data strictly before each trade IS ex-ante).
2. After each accepted fix, re-run ALL months and publish the full
   month table. Every month must stay or become positive.
3. **Activity guard:** under a fix, the target month's trade count
   may not fall by more than 60% vs the base book's count in that
   month. A "fix" that greens a month by barely trading is reported,
   not accepted.
4. If a month cannot be turned green after the pre-listed fix
   families are exhausted (max 4 per month), STOP on that month and
   report the diagnosis + best month table honestly. No invented
   patches.
5. **Timing audit on every scored book:** every trade's entry must
   be strictly after the moment its qualifying information was
   complete. Asserted mechanically wherever the dump fields allow.

## Base 1 — the combined REAL book (home 25)

Traded independently, summed (T1 construction, `stocks_T1_frozen.md`):

- **INV-LONG:** LONG rows of `tuning_inv_T1_T125_S050_trades.csv`.
  Qualifier: Nifty PREVIOUS close ≤ its 50DMA (known before the day
  opens); P2 pool entries from the day's live signal stream.
  Published: 249 trades, +₹24,185.73.
- **N4-V3 (T125):** all rows of `eq_n4deep_v3_trades_T125_janoct.csv`.
  Qualifier: reaction move ≥1% by the 09:30 bar close; entry 09:35.
  Published: 56 trades, +₹7,990.43.
- **P2F (2.5% band):** rows of `stocks_tuning_event_V1_combined_trades.csv`
  with leg = P2F and |reaction_ret_pct| ≥ 2.5. Qualifier: reaction-day
  close; entry next trading day 09:15 open.
  Published: 39 trades, +₹15,489.08.

Published combined anchor (T1, to be reproduced to the paisa):
344 trades, **+₹47,665.24**, October +₹6,845.39, only February
negative (−₹5,533.46). October here = 1–28 Oct (component dumps were
built on the 5-min cache) — reproduced as published, stated openly.

## Base 2 — the 11:00 fade on home 25

Rule (O2 base cell, home slice): stock moves ≥1% from open through
the bar ending 11:00 → enter at the 11:00 bar's open AGAINST the
move; exits T125/S065; one trade per stock-day.
Source: `stocks_O1_P2_1100_1_fade_fixed_T125S065_all_trades.csv`
filtered to the 25 home symbols; cross-checked against
`stocks_O2_results.json` home_control.
Published anchor: 1,073 trades, **+₹4,243.18**, October +₹341.29
(full-month October incl. 29–30 via O1's validated aggregation).

## Base choice (pre-declared)

Working base = the base with **October positive AND fewer failing
months**; tie → the combined book.

## Repair-loop procedure (per failing month, worst first;

September before February if both fail, per the user's order)

1. **DIAGNOSE** the month's losing trades from the dumps: component
   system, direction split, event vs no-event, entry time, setup /
   round, exit reason, stock concentration, day-context fields
   (adr_pct, day_gap_pct), Nifty regime depth that month.
2. **FREEZE the fix families** for that month in Part B of this file
   (≤4 families, listed BEFORE any of them is scored). Each family =
   one ex-ante rule, stated exactly, with the field/data it uses and
   proof the data exists before entry.
3. **SCORE** each family on the FULL Jan–Oct book (the fix applies
   to all months, never only the target month).
4. **ACCEPT** a fix only if ALL hold: (a) target month net > 0;
   (b) every other month stays > 0; (c) activity guard holds in the
   target month; (d) timing audit clean. On accept, the fixed book
   becomes the new working book and the loop moves to the next
   failing month. On reject, revert and try the next family.

## End state

- All 10 months positive → freeze `stocks_M1_candidate_spec.md`
  (full final rule set + December fresh-window judging rule).
- Otherwise → the report names the resisting month(s), the
  diagnosis, every family tried and its full month table.

---

# Part B — February fix families

Frozen 2026-10-31, AFTER the February diagnosis in
`stocks_M1_report.md` Step 3, BEFORE any fix was scored.

Target month: **February** (combined book: 57 trades, −₹5,533.46;
the working base's only failing month — September was checked
first per the user's order and is green on both home bases).
Base February trade count = 57 → activity guard floor = **≥23
February trades** under any fix (drop ≤ 60%).

Diagnosis summary the families derive from: the hole is INV-LONG
(39 trades, −₹9,951.91), concentrated on Feb 1–2 (Budget Sunday
crash −2.16% + next-day whipsaw; 12 trades, 0 wins, −₹9,770.34);
N4-V3 and P2F were green in February and are untouched by MF-1,
MF-3, MF-4.

- **MF-1 — INV-LONG event-window exclusion.** Drop every INV-LONG
  trade whose `event_status` = `event_window` (flag from the
  pre-built event calendar `stock_event_calendar_jan_oct_2026.csv`
  lineage — the stock's event dates are public before the day, so
  the flag is known at entry). Applies to all months. Rationale:
  INV-LONG's entries are generic signal-stream entries, not event
  trades; its Feb event-window slice is −₹8,378.38.
- **MF-2 — Leg swap to DBL-LONG.** Replace the INV-LONG leg with
  the already-frozen DBL-LONG candidate's trades
  (`tuning_inv_L1b_S2_DBL_LONG_T125_S050_trades.csv`: INV1 +
  stock's prev close ≤ own 20DMA, LONG-only, T125/S050 — every
  input from prior-day closes). N4-V3/P2F legs unchanged.
- **MF-3 — INV-LONG exit variant S065.** Replace the INV-LONG leg
  with its frozen T125/S065 tuning-dump trades
  (`tuning_inv_T1_T125_S065_trades.csv`, LONG rows): same entries,
  stop widened −0.5% → −0.65%. Rationale: 29 of 39 Feb INV trades
  stopped out at the −0.5% stop.
- **MF-4 — INV-LONG high-ADR-only.** Keep only INV-LONG trades
  with `adr_pct` ≥ 4.5 (ADR from prior days, field carried in the
  dump; the P2 pool's own range measure). Rationale: Feb's INV
  loss sits in the 3–4.5 ADR band (−₹11,378.77) while its ≥4.5
  slice was green (+₹1,426.86). Expected to strain the activity
  guard — listed so the guard is exercised, not assumed.

**Considered and NOT listed:** a Union-Budget-calendar stand-aside
(no trades on Budget day + next day). It is the mechanically
perfect Feb 1–2 patch, but inside Jan–Oct 2026 it has exactly ONE
instance and is indistinguishable from a date filter; it also
cannot be tested by the December fresh window (no Budget in
December). Guard 1 bars it. Recorded as diagnosis, not a fix.

