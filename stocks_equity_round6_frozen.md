# Round 6 — V5 re-entry chain filters + cost/size sensitivity — FROZEN 2026-10-30, BEFORE PART B SCORING

**Status: Part A (diagnostic, no new rules) is complete and is the
input to this spec. Part B/C are NOT scored at freeze time.
Paper only, no orders. Equity cash, LONG/SHORT, no options language.**
**Basis: provisional per 100 shares unless a table says otherwise.
Gross = before the frozen ₹40/trade flat cost; net = gross − ₹40/trade.
Pool: the frozen re-entry V5 trade CSVs (T10, T125), Jan–Oct 2026,
Oct = 1–28 Oct, 25 stocks. Skill/(lA) are out of this round
(gross-negative under re-entry).**

## Part A break — stated before Part B scoring (from stocks_equity_round6_partA.json)

- Round 1 (first entry of a stock-day): gross expectancy ≈ ₹0 at both
  exits (T10 −₹1.86, T125 +₹2.14 per trade). No gross edge.
- **Round 2 is the only round with a strong gross edge at both exits
  and in both halves** (T10 gross exp +₹66.01 Jan–May / +₹38.09
  Jun–Oct; T125 +₹73.51 / +₹13.63).
- Rounds 3 and 4 are gross-negative at both exits in aggregate
  (T10 rounds 3+ combined ≈ −₹28.6k gross; T125 rounds 3+ ≈ −₹3.1k
  gross, with round 5+ positive only on small, half-inconsistent
  samples — treated as noise, not a break).
- **Clean break: the gross edge lives in rounds 1–2, concentrated in
  round 2; rounds ≥3 destroy it.** This break selects the
  break-informed chain cap in R2.
- Secondary diagnostics (NOT scored as filters this round):
  re-entries entered 09:35–10:30 are gross-strong in both halves at
  both exits; re-entries after a target exit are gross-positive only
  in Jun–Oct (Jan–May gross-negative at both exits), after a stop
  exit the mirror image — neither prev-exit split is both-halves
  clean on its own.

## Part B — filters (each judged on gross expectancy/trade AND net at ₹40, both halves, October shown)

- **R1a — chain cap 2:** keep rounds 1–2 of each stock-day chain only.
- **R1b — chain cap 3:** keep rounds 1–3 only.
- **R2 — break-informed cap:** Part A's break (above) selects cap = 2.
  R2 is therefore the same trade set as R1a by construction; it is
  scored once and labelled R1a/R2. No separate R2 numbers will be
  invented.
- **R3 — re-entry only after a target exit (walk rule):** walk each
  stock-day chain in round order. Round 1 is always taken. A later
  signal is taken only if the most recent TAKEN trade in that chain
  exited `target`; a taken trade exiting `stop` or `square_off`
  ends that stock's chain for the day. Skipped signals do not change
  the last-taken exit. Applied as a post-filter on the recorded
  chain (signals are price-generated; skipping a trade does not
  alter later signal prices in this engine).
- **R4 — ADR≥3% stock-days only:** keep all rounds of stock-days
  whose prior-10-day average daily range ≥ 3.0% of close, using
  Round 3's exact formula (mean of (high−low)/close×100 over the
  prior 10 daily rows excluding the trade day, minimum 5 rows;
  stock-days with no ADR value are excluded). Day-level property —
  chains stay intact.
- **R5 — conditional stacks, defined ex ante:** at each exit,
  R5a = R1a + R4 if R4 is gross-positive in both halves at that exit;
  R5b = R1a + R3 if R3 is gross-positive in both halves at that exit;
  R5c = R1a + R3 + R4 if both qualify. If neither R3 nor R4 qualifies
  at an exit, R5 is skipped at that exit and the skip is stated.

**Survivor rule (unchanged): NET positive in BOTH halves at ₹40/trade
cost.** A filter that is gross-strong but net-negative at ₹40 goes
to Part C, not the bin, and not to a survivor claim.

## Part C — cost & size sensitivity

For the best Part B variant (highest net Jan–Oct; ties → higher gross
expectancy) and for unfiltered V5 × T125 re-entry:
- Net Jan–Oct and both halves at flat costs ₹40 / ₹30 / ₹20 / ₹10
  per trade (per 100 shares basis).
- Breakeven flat cost per trade at 100 shares (= gross expectancy).
- Size sensitivity at 200 and 500 shares assuming the flat cost
  stays ₹40 per TRADE regardless of size (stated simplification:
  some real charges scale with size/turnover; intraday equity has
  no STT-on-delivery, but brokerage/GST/exchange charges partly
  scale — the user's actual broker charges are UNKNOWN and are not
  invented here). Also breakeven position size at ₹40 flat.

## What this round does NOT do

- No new entry signals, no exit changes, no per-stock whitelist, no
  time-of-day filter (Part A's time split is a diagnostic for a
  later round, not scored here).
- No November-paper change: N4-V3 stays as frozen; any Round 6
  survivor would still need its own forward paper test.
