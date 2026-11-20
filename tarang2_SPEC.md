# TARANG Round 2 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 18:18 IST, before any Round 2 scoring. No Round 2
result exists at the time of writing; no parameter below has been tuned against
any Round 2 result.

**Class:** the EKAM-style tuning family for TARANG. Round 1 (frozen
`tarang_SPEC.md`) scored net positive in both years but **NO PASS** — it failed
only the random-entry placebo in both years, and its own diagnosis showed the
trend∩pullback intersection destroys value (each ingredient alone, in
cap-saturated ungated ablations, earned more than the combination). Round 2
promotes each ingredient to a standalone candidate book and judges each on its
own full gate. **The Round 1 ablation numbers are NOT evidence** — each
candidate stands or falls on its own gated run in this round.

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per 100 shares,
₹40 per completed trade. Paper only, real money ₹0. No stock options (closed
surface). Nothing is armed; no paper run is started; no live book is touched.

## 1. What is unchanged from Round 1 (exact)

- Universe: the frozen 25 names (ASTRAL, BDL, GLENMARK, GODREJCP, HDFCBANK,
  HINDALCO, HINDCOPPER, HINDUNILVR, HINDZINC, INDUSTOWER, IRCTC, ITC,
  KALYANKJIL, NATIONALUM, NHPC, NTPC, OBEROIRLTY, OIL, PFC, RECLTD,
  TATASTEEL, TVSMOTOR, UNITDSPR, VEDL, WIPRO). A labelled TVSMOTOR-excluded
  sensitivity line is reported per candidate; TVSMOTOR is never silently
  dropped.
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` (volume-bearing store, complete
  2025-01-01 → 2026-11-13, OHLC verified identical to the frozen stores).
- Indicators: session VWAP (typical price × volume, cumulative from 09:15),
  EMA-50 on 5-minute closes (SMA-seeded at bar 50, k = 2/51), RSI(7) Wilder on
  5-minute closes (SMA seed) — the Round 1 scorer's disclosed conventions,
  unchanged. All causal, computed on completed bars only.
- Trend state (used by TARANG-B): UPTREND iff close > VWAP and close > EMA-50;
  DOWNTREND iff close < VWAP and close < EMA-50; otherwise no state.
- Exits (first hit wins): target +0.8% / stop −0.5% from entry, evaluated on
  completed bars, **stop first** on a bar whose range spans both; square-off at
  the 15:15 bar close if neither is hit. Net = side × (exit − entry) × 100 −
  ₹40.
- Entry fill: next bar's open after the signal bar; the fill must be in the
  same session, at a bar time ≥ 09:45 and ≤ 15:15 (no entries before 09:45).
- Caps: one open position per name; max 2 entries per name per day; max 10
  entries per day across the book; same-bar contention ordered deepest RSI
  excursion first (TARANG-A); re-entry after an exit allowed subject to each
  candidate's own signal rule.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the November 2026
  slice reported separately, never pooled into one verdict.

## 2. Candidate TARANG-A — pullback-only (no trend condition)

- No trend condition of any kind. Entries from 09:45 (fill window as above).
- LONG: RSI(7) dips to ≤35 on a completed bar (arming), then a later completed
  bar's RSI(7) crosses back above 35 → enter LONG at the next bar's open.
- SHORT: RSI(7) rallies to ≥65 on a completed bar (arming), then a later
  completed bar's RSI(7) crosses back below 65 → enter SHORT at the next bar's
  open.
- A fresh excursion (a new dip to ≤35 / rally to ≥65) is required for each
  entry — no repeated entries off one pullback. Arming state is per name-day
  and resets each session, exactly as the Round 1 pullback state machine.
- Signal depth for the same-bar tie-break: excursion beyond the threshold
  (35 − min RSI for longs, max RSI − 65 for shorts), as Round 1.

## 3. Candidate TARANG-B — trend-only (no pullback wait)

- No RSI condition of any kind.
- A signal fires on the FIRST completed bar of a trend-state episode: the
  first bar whose state is UPTREND after a bar whose state was not UPTREND →
  LONG signal; mirror for DOWNTREND → SHORT signal. Episode tracking is per
  name-day (the state machine resets each session, as in Round 1); the first
  bar of a session carries prior-state "none", so a session opening already in
  a state signals on its first state bar (its fill is still subject to the
  ≥09:45 window).
- After an exit, a new entry in the same name requires the state to have LEFT
  and RE-ESTABLISHED — transition-only signalling gives exactly this: no new
  signal exists inside one continuous state episode, so no immediate re-entry
  is possible within an episode. The per-name 2/day and book 10/day caps still
  apply on top.

## 4. Controls gate (identical bar for both candidates)

Per `tarang_SPEC.md` Section 9–10 and
`~/workspace/custom-skills/backtest_controls_gate/SKILL.md`, run in the same
run, before any verdict:

1. **Timing/leak audit (per candidate):** independent recompute of the
   candidate's signal set (separately written state machine); every trade
   checked — entry after signal, entry exactly at the next bar, fill inside
   the entry window, exit re-simulated bar-by-bar and matched, net recomputed,
   caps (≤2/name/day, ≤10/day), no overlapping positions per name. Plus a
   truncation spot-check (indicators recomputed from bars cut at the signal
   bar must match the engine at that bar). Violations must be 0.
2. **Random-entry placebo (per candidate, 200 seeded draws, seed base
   20261118):** same names, same days, same number of entries per day as the
   candidate took, random eligible bars 09:45–14:45, random side, identical
   exit geometry and caps. The candidate must beat the placebo 90th percentile
   in both years.
3. **Direction-flip placebo (information only):** the candidate's exact
   entries with the side flipped.
4. **Splits and stress:** first-half/second-half per year; full month table;
   ex-top-3 per year; max drawdown (cumulative net ordered by exit time,
   overall and per year); independent re-sum of headline nets from the written
   trades CSV.

## 5. Pass bar (pre-registered, frozen — identical for both candidates)

A candidate PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is reported as
information. Per candidate the report also gives: side split (LONG vs SHORT
nets per year), win rate, trade count, max drawdown, month table, and the
TVSMOTOR-excluded sensitivity line.

## 6. Discipline

- No parameter is tuned in this round (RSI thresholds 35/65, RSI length 7,
  EMA length 50, exits +0.8%/−0.5% all stay at their Round 1 values).
- No Round 3 is designed in this run. If both candidates fail, the report
  diagnoses from the trades what the family has now measured across Rounds
  1+2 — in particular whether any entry-timing edge exists in this family on
  this universe and window, and where it sits if it does.
