# Stocks EQUITY — Round 8 — Exit sweep on the structured V5 re-entry pools (R5a / M5) — 2026-10-30

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0. No live trades
were placed.**
**Every rupee figure is provisional per 100 shares. Gross = before
the frozen ₹40/trade flat cost; net = gross − ₹40/trade. Spec frozen
before scoring: `stocks_equity_round8_frozen.md`. Pools: P1 = R5a
entries (chain round ≤ 2 + ADR≥3% stock-days), P2 = M5 entries
(round ≤ 2 + entry before 10:30 + ADR≥3%), chains rebuilt per exit
cell from the frozen V5 signal stream, Jan–Oct 2026 (203 days,
October = 1–28 Oct), 25 stocks. N4-V3 and its November spec were
not touched.**

**Validation gate — PASSED exactly.** Rebuilt chains at the two
previously published exits reproduce Round 6/7 pool figures to the
paisa (P1 × T125: 1,421 trades, net −₹19,541.85; P1 × T10: 1,471,
−₹27,493.49; P2 × T125: 918, +₹10,657.81; P2 × T10: 947,
+₹5,772.37 — all provisional per 100 shares). Every number below
is anchored to the published chain machinery.

---

## Verdict first — NO survivor. Exits are not the missing lever.

- Across all **20 cells** (9 target/stop combos + 1 runner per
  pool), **no cell is net-positive in both halves at ₹40/trade**.
  The gross edge does not double under any exit in the grid: the
  best both-halves gross expectancy in the round is ₹32.57/trade
  (P2 × T125/S050 — the same figure Round 7 already had), and the
  best balanced P1 cell reaches only ₹22.34.
- The two pools fail in **opposite, exit-invariant ways**:
  - **P1 (R5a, all-day):** Jan–May gross expectancy is positive in
    9 of 10 cells (up to +₹31.86), but Jun–Oct gross collapses at
    the 0.4% and 0.75% stops (−₹6.40 / −₹0.60) and only the two
    widest-target cells (T200/S050, runner) turn Jun–Oct
    net-positive (+₹1,007.04 / +₹1,118.39) — while their Jan–May
    halves are the pool's worst (−₹20,594.65 / −₹27,148.45).
    Widening the target moves P1's edge from the first half to
    the second; it never holds both.
  - **P2 (M5, morning):** **all 10 cells are Jun–Oct net-positive
    and all 10 are Jan–May net-negative** — identical in shape to
    Round 7. Jun–Oct gross expectancy is very large (₹71–133/
    trade), Jan–May gross is ₹32.57 at best and turns negative at
    wide targets/stops (T200/S075: −₹30.28). The morning + ADR
    edge simply did not exist in Jan–May at any exit; no exit
    rule can manufacture a first-half edge that the entries
    don't have.
- Per the frozen rule, concentration checks are produced only for
  a both-halves pass. **No cell passed, so none are claimed.**

---

## Grid — P1 = R5a entries (all figures provisional per 100 shares)

| Cell | Trades | Win % | Tgt % | Gross exp ₹ | Net Jan–Oct ₹ | Gross exp Jan–May ₹ | Net Jan–May ₹ | Gross exp Jun–Oct ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| T125/S040 | 1,484 | 29.2 | 22.6 | +21.34 | −27,691.90 | +31.16 | −9,686.93 | −6.40 | −18,004.97 | −5,131.60 |
| T125/S050 | 1,421 | 33.5 | 25.1 | +26.25 | −19,541.85 | +29.78 | −10,801.11 | +15.99 | −8,740.74 | +3,975.08 |
| T125/S075 | 1,296 | 41.4 | 29.5 | +12.47 | −35,682.53 | +17.02 | −22,082.98 | −0.60 | −13,599.55 | +3,714.83 |
| T150/S040 | 1,446 | 27.5 | 17.9 | +23.54 | −23,800.34 | +31.86 | −8,713.51 | −0.12 | −15,086.83 | −4,720.09 |
| T150/S050 | 1,379 | 31.3 | 19.7 | +22.67 | −23,893.29 | +22.34 | −18,157.04 | +23.66 | −5,736.25 | +4,917.04 |
| T150/S075 | 1,250 | 39.0 | 23.3 | +4.07 | −44,909.17 | +5.83 | −31,713.36 | −0.98 | −13,195.81 | +5,073.67 |
| T200/S040 | 1,401 | 25.2 | 10.7 | +19.99 | −28,031.02 | +22.77 | −17,845.33 | +12.09 | −10,185.69 | +169.74 |
| T200/S050 | 1,331 | 29.2 | 11.8 | +25.28 | −19,587.61 | +19.22 | −20,594.65 | +42.96 | **+1,007.04** | +11,336.30 |
| T200/S075 | 1,194 | 36.5 | 14.1 | +7.51 | −38,796.26 | +3.49 | −32,311.99 | +19.02 | −6,484.27 | +10,048.08 |
| RUNNER 2.0/1.0-partial/S050 | 1,363 | 37.6 | 10.6 | +20.90 | −26,030.06 | +13.17 | −27,148.45 | +43.19 | **+1,118.39** | +5,189.03 |

P1 reading: the 0.5% stop is the pool's best stop at every target
(0.4% gets chopped in Jun–Oct; 0.75% raises win % to 36–41% but
halves gross expectancy — wider stops lose more per loser than
the extra winners repay). T150/S050 is the most balanced cell
(gross +₹22.34 / +₹23.66 across halves) — and its both-halves
breakeven cost is therefore ₹22.34, still ₹17.66 under the frozen
₹40. The runner behaves like T200/S050 with a worse first half:
banking 50% at +1.0% does not rescue Jan–May.

## Grid — P2 = M5 entries (all figures provisional per 100 shares)

| Cell | Trades | Win % | Tgt % | Gross exp ₹ | Net Jan–Oct ₹ | Gross exp Jan–May ₹ | Net Jan–May ₹ | Gross exp Jun–Oct ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| T125/S040 | 963 | 29.0 | 25.2 | +42.19 | +2,106.33 | +31.35 | −6,135.95 | +72.45 | +8,242.28 | +285.45 |
| T125/S050 | 918 | 33.4 | 28.4 | +51.61 | +10,657.81 | +32.57 | −5,035.50 | +105.39 | +15,693.31 | +8,490.91 |
| T125/S075 | 844 | 41.5 | 33.2 | +31.70 | −7,005.53 | +6.21 | −20,879.86 | +101.39 | +13,874.33 | +7,310.29 |
| T150/S040 | 945 | 26.5 | 20.3 | +36.77 | −3,056.47 | +24.43 | −10,838.04 | +71.25 | +7,781.57 | +1,346.37 |
| T150/S050 | 898 | 30.4 | 22.6 | +38.81 | −1,064.40 | +16.55 | −15,549.74 | +101.64 | +14,485.34 | +10,114.59 |
| T150/S075 | 823 | 38.3 | 26.7 | +11.57 | −23,398.63 | −20.14 | −36,201.92 | +97.93 | +12,803.29 | +9,124.32 |
| T200/S040 | 916 | 23.7 | 12.8 | +30.13 | −9,043.64 | +8.17 | −21,424.54 | +90.95 | +12,380.90 | +6,131.20 |
| T200/S050 | 868 | 27.5 | 14.2 | +35.66 | −3,767.03 | +1.81 | −24,438.60 | +130.66 | +20,671.57 | +16,748.37 |
| T200/S075 | 788 | 35.2 | 17.0 | +14.05 | −20,445.48 | −30.28 | −40,340.37 | +132.97 | +19,894.89 | +14,453.02 |
| RUNNER 2.0/1.0-partial/S050 | 874 | 38.1 | 12.7 | +42.50 | +2,181.80 | +13.62 | −16,989.46 | +123.35 | +19,171.26 | +9,889.97 |

P2 reading: widening the target from 1.25% to 2.0% *increases*
Jun–Oct gross expectancy (₹105 → ₹131–133) and *destroys*
Jan–May (₹32.57 → ₹1.81 / −₹30.28). The two halves want opposite
exits — the signature of a regime difference in the entries, not
an exit-tuning problem. The best both-halves breakeven in P2 is
₹32.57 (T125/S050), unchanged from Round 7; the runner adds
nothing in the first half (+₹13.62 gross) despite its strong
second half.

---

## Cost-realism note (no broker data invented)

The flat ₹40/trade is an approximation, and this section states
what it implies so the user can judge it against his own charges:

- Average entry price in the structured pools (gate-cell chains):
  **P1 ₹852.86, P2 ₹833.49**. One side of a 100-share position is
  therefore worth ≈ **₹85,286 (P1) / ₹83,349 (P2)**; round-trip
  turnover ≈ ₹170,571 / ₹166,698.
- The flat ₹40 equals **0.047% (P1) / 0.048% (P2) of the one-side
  100-share value**, or **0.023% / 0.024% of round-trip
  turnover**. In other words, at these pools' average prices the
  frozen cost behaves like an all-in round-trip charge of about
  **0.024% of turnover**.
- A real all-in intraday equity cost is a mix: a possibly flat
  brokerage per order plus components that scale with turnover
  (sell-side STT on intraday, exchange and regulatory charges,
  GST on the fee components). Because part of it is a % of
  turnover, the flat-₹40 approximation is **price-dependent**: it
  overstates cost for higher-priced shares and understates it for
  lower-priced ones, relative to a % charge. If the user's real
  all-in round-trip cost at ~₹850/share is **above** ~0.024% of
  turnover, his real per-trade cost at 100 shares exceeds ₹40 and
  every net figure in this round is optimistic; if **below**, the
  reverse. No broker's schedule is quoted or assumed here — the
  user's actual charges remain the missing input, as in Rounds
  6–7.
- Scale of the remaining gap: the best both-halves breakevens in
  this round are ₹32.57 (P2 × T125/S050) and ₹22.34 (P1 ×
  T150/S050) per trade at 100 shares. At 100-share size the
  structured pools pass only if the real flat-equivalent cost
  sits below those figures; at larger size with a truly flat
  per-trade charge the same gross edges clear ₹40 more easily
  (Round 6, Part C) — but a % cost component does not shrink
  with size, which is exactly why the % framing above matters.

---

## Verdict

1. **No survivor at the frozen basis.** All 20 cells fail the
   both-halves net rule at ₹40/trade per 100 shares. Nothing is
   adopted, and **no cell earns a frozen November/December paper
   spec from this round** — that flag is reserved for a survivor,
   and there is none. N4-V3's November paper is unaffected.
2. **The exit dimension is now exhausted for the structured
   pools**, on top of the unstructured pool's earlier sweep:
   targets 0.5–2.0%, stops 0.4–0.75%, and a partial-and-trail
   runner have all been run. No exit doubles the gross edge,
   because the binding facts are in the entries and the calendar:
   P1's edge halves swap halves as the target widens, and P2's
   morning edge is a Jun–Oct phenomenon at every exit.
3. **What remains genuinely open** (stated, not resolved here):
   (a) the user's real all-in charges vs the ₹32.57 / ₹22.34
   both-halves breakevens — a fact about his account, not the
   backtest; (b) whether the Jun–Oct concentration of the P2
   edge is a durable regime or a 2026 artefact — only fresh
   (November+) data on a frozen rule could answer it, and under
   this round's survivor rule no rule earned that test.

## Files

- Spec (frozen before scoring): `stocks_equity_round8_frozen.md`
- Engine: `stocks_equity_round8.py`
- Results JSON: `stocks_equity_round8_results.json`
  (includes the 4-cell validation gate and cost-realism inputs)
- Kept-trade dumps: `eq_round8_P1_{cell}.csv`,
  `eq_round8_P2_{cell}.csv` (20 files; cells T125/T150/T200 ×
  S040/S050/S075 plus RUNNER_T200_P100_S050)

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.
