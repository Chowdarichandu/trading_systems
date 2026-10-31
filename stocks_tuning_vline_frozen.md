# Stocks EQUITY — Tuning LINE 2 (V-line) — FROZEN SPEC — written BEFORE any scoring in this line

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0.**
**Every rupee figure is provisional per 100 shares. Net = gross −
₹40/trade flat (frozen cost), unless a family explicitly states a
different cost (U6 sensitivity only). Window: Jan–Oct 2026
(October = 1–28 Oct), 203 trading days, 25 watchlist stocks.**

## Pass gates (frozen, apply to every family)

A family/cell is a **candidate** only if ALL hold at ₹40/trade:
1. Net positive in Jan–May AND net positive in Jun–Oct.
2. Breadth: ≥10 of 25 stocks net-positive (on the cell's own
   trade set; for direction-restricted cells, breadth is counted
   on that direction's trades alone).
3. Gross expectancy > 0 in both halves (implied by 1 at ₹40, but
   reported explicitly).

One structural change at a time. No hindsight per-trade filters.
Rejected cells are reported, not hidden. A pass freezes
`stocks_vline_v2_candidate_spec.md` and is flagged — November's
frozen exams (N4-V3 primary, INV1 + P2F shadows) are NOT touched
by anything in this line.

## Base mechanisms (definitions inherited, not re-invented)

- **V3** = LADDER L-c (0.4% log-step grid from the day anchor =
  first bar's open; seed band extremes from bars before 09:45;
  entries from 09:45 when the close crosses into a new band;
  entry at the signal bar's close; cap 6 entries/stock-day; last
  entry 15:05; exit = −1.0% disaster stop, else hold to the 15:10
  bar's close) **plus the volume gate**: the signal bar's volume
  must be ≥1.5× the rolling median of the prior 20 bars of the
  same day (volume cache `data/progressive_vol/`). Published V3:
  3,275 trades, Jan–May **+₹45,413.60**, Jun–Oct **−₹61,697.60**,
  total −₹16,284.00, breadth 10/25; direction split (diagnosis):
  LONG +₹43,171 (Jan–May) → −₹52,032 (Jun–Oct). Engine:
  `stocks_new_strategy_vol.py::sim_v3`. **Validation gate: the
  generalised engine in this line must reproduce V3 exactly
  (trades, both halves, total) before any family is scored.**
- **V5 re-entry stream** = the frozen signal stream of
  `stocks_equity_reentry.py` (pool_pick over v4_head/skor_head),
  chained exactly as in `stocks_equity_round8.py::run_chain`
  (entry = next bar's open after the signal; next search starts
  at the previous exit bar). **Validation gate for U5: chains
  with both trades at T125 and cap 2 must reproduce Round 6's
  R1a/R2 row (5,689 trades, net −₹143,903.56) before U5 scoring.**
- Exit replay for V5-stream trades = round8 `replay_plain`
  (scan starts at the entry bar; within a bar the stop is checked
  before the target; 15:10 square-off at that bar's close).

## Direction-block semantics (applies to U1–U4)

In a direction-restricted cell, a signal of the blocked direction
is treated exactly like a volume-gate block in the base engine:
the band extreme is consumed (bhi/blo already updated), no entry
is taken, scanning continues. The cap counts taken trades only.

## U1 — V3 direction split cure

V3 exactly as frozen, three cells: **U1-BOTH** (base, = V3
reproduction), **U1-LONG** (LONG entries only), **U1-SHORT**
(SHORT entries only). Hold-to-close + −1.0% stop unchanged.
Question: is one direction both-halves positive on its own?

**"Best direction" selection rule (used by U3/U4):** the
single-direction U1 cell (LONG-only or SHORT-only) with the
higher Jan–Oct net; if both are negative, the less negative one.
Mechanical, no discretion.

## U2 — V3 stop structure

V3 with the disaster stop changed to: **−0.75%**, **−1.25%**, and
**NONE** (no intraday stop at all; every trade rides to the
15:10 close — included per the brief's "a wider stop than the
excursion, or none"). Each stop × three direction modes
(both / LONG-only / SHORT-only) = 9 cells. Everything else
(step 0.4%, volume gate, hold-to-close) unchanged. The base
−1.0% stop is covered by U1's three cells.

## U3 — V3 time exit

V3 (stop −1.0% unchanged) with the terminal exit moved from the
15:10 close to the close of the first bar at or after **13:00**,
and separately **14:30**. If the disaster stop is touched in any
bar up to and including the exit-time bar, the stop fills first
(base fill rule); otherwise the exit is that bar's close. A trade
still open at 15:10 (no bar ≥ exit time found) squares off per
base. Cells: {13:00, 14:30} × {both directions, best direction
from U1} = 4 cells.

## U4 — V3 step size

Ladder step ∈ {**0.3%**, **0.5%**, **0.6%**} (0.4% is the frozen
base, covered by U1), volume gate and hold-to-close + −1.0% stop
unchanged, direction = best direction from U1 only. 3 cells.

## U5 — Round-2 emphasis on the V5 re-entry stream (NOT the
P2-structured pools; no ADR filter, no morning filter)

**U5a PROBE-CHAIN.** Every stock-day with ≥1 V5-stream signal:
- Trade 1 (the probe) uses the tight exit **target +0.5% /
  stop −0.35%**.
- If a second signal occurs after the probe exits, Trade 2 uses
  **T125 (target +1.25% / stop −0.5%)**. Chain cap = 2 trades.
- **The tradable unit is the stock-day chain.** Primary score =
  chain-total net summed over ALL initiated chains (a chain that
  ends after the probe alone still books the probe's result —
  that is what running this rule live would actually produce).
  Secondary (diagnostic): chains where Trade 2 fired vs
  probe-only chains, reported separately.
- Halves and October by chain date. Breadth = stocks whose
  chain-total net is positive / 25. Expectancy reported per
  chain and per trade.

**U5b SKIP-PROBE.** Identical to U5a EXCEPT on stock-days where
the stock has already moved ≥1% before 10:00 — defined ex-ante
as |close of the last bar with time < 10:00 ÷ day open − 1| ≥
1.0%, day open = first bar's open. On those days the first
signal is discarded entirely (no probe, no cost) and the chain
is: the next signal (the would-be second signal) at T125, plus
one further T125 re-entry if a third signal occurs after it
exits (cap 2 trades). Non-qualifying days are traded exactly as
U5a. Primary score identical in form to U5a (all initiated
chains). The qualifying-day subset is also reported separately
(diagnostic).

## U6 — Cost reality check (sensitivity, NOT a pass at lower cost)

On the best cell of U1–U5 — selected mechanically as the cell
with the highest min(Jan–May net, Jun–Oct net) at ₹40; if
several cells pass both halves, among passers the highest
Jan–Oct net — report: net at ₹25/trade and at ₹60/trade (both
halves + total), and the breakeven flat cost per trade
(= gross expectancy per trade, overall and per half). This is a
sensitivity statement only; the pass gate stays at ₹40.

## Reporting

`stocks_tuning_vline_report.md`, written incrementally per
family: trades, win %, gross expectancy, net (all / Jan–May /
Jun–Oct / October), per-direction split where applicable,
breadth (positive stocks /25, best/worst stocks, top-3 share
when the total is positive), verdict per cell against the
frozen gates. Trade dumps per cell as CSV.

---

## Line 2b — Robustness battery on the frozen v2 candidate
## (DIAGNOSTIC — appended 2026-10-31 BEFORE any Line 2b scoring)

Everything in Line 2b is **diagnostic on/around the frozen
rule** in `stocks_vline_v2_candidate_spec.md`. No result in
this battery may be claimed as a pass; the candidate spec is
NOT edited by this line. If a variant looks better than the
frozen rule, it is recorded as a named observation only.

**Base (frozen rule, verbatim):** a stock-day qualifies iff
|close of the last bar with time < window_end ÷ first bar's
open − 1| ≥ threshold, frozen window_end = **10:00**,
threshold = **1.0%**. Non-qualifying days: no trades.
Qualifying days: discard the first V5-stream signal of the
day entirely; trade the next signal(s) at **T125**, entry at
the next bar's open, exit replay = round8 `replay_plain`,
chain cap **2 trades/stock-day**.

**Validation gate (before any battery cell):** the battery
engine at frozen parameters must reproduce the published
subset exactly — 424 chains, 698 trades, net +₹84,671.74,
Jan–May +₹52,884.19 (272 chains), Jun–Oct +₹31,787.55
(152 chains), October +₹16,825.42, chain win 55.0%, breadth
16/25, direct leg 424 trades +₹93,575.31, re-entry leg
274 trades −₹8,903.57.

**Direction-block semantics for R2/R5** (same convention as
this file's ladder families): the first-signal discard is
the first signal of the day regardless of direction and
happens first; thereafter a blocked-direction signal is
consumed (search continues from signal bar + 1), takes no
entry, pays no cost, and does not count toward the cap.

- **R1 THRESHOLD NEIGHBOURHOOD:** threshold ∈ {0.75%, 1.0%
  (frozen = validation row), 1.25%, 1.5%}, window frozen.
  Per threshold: chains, trades, net, both halves, October,
  breadth. Question: cliff edge or plateau at 1.0%?
- **R2 DIRECTION SPLIT** at frozen parameters: (i) LONG-only
  chains and SHORT-only chains under the direction-block
  semantics above; (ii) trade-level LONG/SHORT split of the
  frozen chains' legs; (iii) partition of the frozen chains
  by the SIGN of the pre-10:00 move — mover-up days
  (pre-move ≥ +1%) vs mover-down days (≤ −1%) — chains, net,
  halves, breadth per side.
- **R3 CONCENTRATION** on the frozen chains: per-stock chain
  nets; top-3 stocks' share of net; net excluding the top-3
  payers (total and both halves, top-3 ranked on the full
  window); winsorised total with each stock's net capped at
  +₹2,000 (negative stocks unchanged); month-by-month table
  (chains, trades, net, cumulative net); worst month named.
- **R4 TIME NEIGHBOURHOOD:** window_end ∈ {09:45, 10:00
  (frozen = validation row), 10:15} at the frozen threshold;
  pre-close = close of the last bar with time < window_end;
  qualification only — entry/discard/exit logic unchanged.
- **R5 SIGNAL DEFINITION CHECK:** (b) ANY-direction next
  signal = the frozen base (to be confirmed from the engine:
  `build_chain` applies no direction filter after the
  discard). (a) SAME-direction variant: after the discard,
  only signals whose direction equals the sign of the
  pre-10:00 move are traded; other signals are consumed per
  the direction-block semantics.
- **R6 COST SENSITIVITY:** the frozen rule re-costed at
  ₹25 and ₹60 per trade (net = gross − cost × trades):
  total, both halves, October, plus the breakeven flat cost.

**Reporting:** appended to `stocks_tuning_vline_report.md`
as the Line 2b section, ending in a robustness verdict —
**robust / fragile / cliff-edge** — with the evidence. No
pass is claimed for any cell. Engine:
`stocks_tuning_vline2b.py`; results:
`stocks_tuning_vline2b_results.json`.
