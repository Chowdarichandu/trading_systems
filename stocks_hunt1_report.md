# Stocks — complete report (Saturday 2026-10-31)

Equity cash intraday only, LONG/SHORT. **Paper only — real money
₹0, no orders placed.** Every figure is **provisional per 100
shares, ₹40/trade cost already deducted**, on Jan–Oct 2026 data
(October = 1–28 Oct, 18 trading days). Detail lives in the linked
reports; this file is the summary.

---

## ⚠️ CORRECTION added 08:50 IST, 2026-10-31 — read this first

**Section 1's flagship is RETRACTED.** Control tests run this
morning (Line B4/B5, `stocks_moverB4_report.md` /
`stocks_moverB5_report.md`) found a look-ahead leak in the
Morning-Mover engine: it qualified a stock-day on the move through
the measurement time, then took entries from earlier in the day —
before that move was knowable. **127% of MOVER-A's profit and 113%
of MOVER-B's sat in those impossible entries**; the honest slices
lose money (A −₹67,908.97, B −₹59,361.39), and an honest rebuild
(signals counted only from the measurement time onward) is
**negative at every measurement time in both halves**. The
Morning-Mover line — including the A2/B2/B3 tuned variants
(+₹406k / +₹812k / +₹1.62M, all the same leak, worse at later
measurement times) — is **dead**. Its two November shadow loggers
have been **disabled** so November is not wasted certifying an
unexecutable rule. Sections 2–5 below stand as written (different
machinery, ex-ante by construction); Section 6's November board
now runs **three** shadows: N4-V3 primary, INV1, P2F.

---

## 1. The flagship: Morning-Mover Second Signal

The rule: if a stock has already moved ≥1% before the measurement
time, ignore its first signal of the day and trade the *next* one
(target +1.25%, stop −0.5%, max 2 entries per stock-day).

- **Home watchlist (25 stocks):** 424 chains, **+₹84,671.74**,
  positive in both halves (+₹52,884.19 / +₹31,787.55), October
  +₹16,825.42, breadth **16/25** stocks positive. It survives
  costs easily — breakeven is **₹161.31 per trade**, four times
  the ₹40 we charge it.
- **It transfers.** Run word-for-word on 25 brand-new large caps
  it was never tuned on (RELIANCE, TCS, INFY…): 199 chains,
  **+₹164,483.29**, both halves positive, breadth **22/25**.
  Pooled across all 50 stocks: **+₹249,155.03**, breadth 38/50.
- **A stronger variant exists (diagnostic, not yet adopted):**
  measuring the move at **10:15 instead of 10:00** — MOVER-B —
  gives +₹295,288.72 on the new 25 with breadth **25/25**, and
  **+₹464,617.03** pooled with breadth **49/50**.

This is the strongest stocks result of the entire programme, and
the only mechanism that is a market-wide behaviour rather than a
quirk of our watchlist. November judges it on fresh data
(Section 6) before anything is adopted.
Sources: `stocks_tuning_vline_report.md`,
`stocks_tuning_universe_report.md`, `stocks_tuning_mover_report.md`.

## 2. Other candidates — and their verdicts

- **DBL-LONG** (below-trend double condition, longs only):
  **+₹24,327.37**, expectancy +₹182.91/trade, breadth 10/25 —
  passes every gate at home, but **FAILS the transfer test** on
  new stocks. Home-universe candidate only.
- **INV-LONG** (below-trend pool, longs only): **+₹24,185.73**,
  both halves positive — but it **stands weakened**: two stocks
  (TVSMOTOR + GLENMARK) are ~97% of the profit; remove both and
  the second half flips negative.
- **EventBook** (N4-V3 + P2F traded as one book): +₹20,826.31 on
  paper — then **killed by its own frozen concentration test**:
  remove the top-3 paying stocks and it goes negative. The book
  is dead; its two legs below survive individually.
- **N4-V3** (results-reaction momentum): **+₹7,990.43**, both
  halves positive at both exits. Alive — it is November's
  primary exam.
- **P2F** (post-reaction follow-through: after a ≥2% results
  reaction day, trade the next morning in the same direction):
  **+₹12,835.88**, both halves positive, expectancy
  +₹267.41/trade, breadth 14/25. Alive as a November shadow —
  with caveats: it is mostly a SHORT-side result in-sample and
  it **fails the transfer test**, so its edge may live in
  specific watchlist names.

Sources: `stocks_tuning_inv_report.md`,
`stocks_tuning_event_report.md`.

## 3. The overnight invention search — all failed

Three brand-new mechanisms were invented and tested across
price, volume and adaptation axes (~136,000 paper trades). None
passed; no paper spec was earned.

- **EXTREME-HUNT** (breakout + trail + re-entry): the hunt works
  mechanically (33+ entries/day) but 42% of entries never reach
  the trail and bleed the stop. Best family −₹283,889.92.
- **LADDER** (0.4% step grid): one positive half only — a regime
  artefact, not a system.
- **SNAP** (fade or follow climax stretches): climax bars carry
  no tradable next-bar information here. Worst breadth (3–4/25).
- **Volume axis:** volume confirmation roughly doubles the gross
  quality of the best pockets (ladder+volume was the strongest
  near-miss: +₹45,413.60 in Jan–May) — but the second half still
  flips negative.
- **Adaptation axis:** trailing-drift gates and relative-strength
  selection **hurt** — the drift flip is a half-year regime
  change that trailing statistics cannot read in time.

Lesson: on this universe, pure price/volume structure has gross
expectancy at or below the ₹40 cost, and the good pockets flip
sign between halves. Source: `stocks_new_strategy_report.md`.

## 4. Event axis + reaction profiles

- **EA1** (strongest pools restricted to event windows): all 6
  families fail. Correction to an earlier observation — event
  proximity is NOT the edge; INV1's money is in its below-trend
  condition (its *no-event* subset is +₹23,161.35, both halves
  positive). The narrow reaction ±2-day window is toxic for
  signal pools.
- **EA2** (pre-results drift): fails — second half negative, and
  one stock (BDL) is bigger than the whole total.
- **EA3** (volume confirmation on N4-V3): fails — the quiet-volume
  trades it would drop carried the second-half profit. **N4-V3
  enters November exactly as frozen.**
- **The dry run caught a real bug before it cost us:** a full
  rehearsal of Monday's logging on Friday's data found that
  short-range Upstox fetches intermittently drop the newest
  trading day, which would have silently skipped stocks. All
  **5 fixes are now written into the November loggers** (wide
  fetch window + DATA_MISSING rule, no Jan–Oct calendar for
  November, fresh long lookbacks, holiday guard, unclassifiable
  row).
- **Reaction profiles** (how each stock behaves around results):
  **OBEROIRLTY** fell on all 4 reaction days and kept falling in
  all 4 post-windows; **BDL** runs up into results (+5.74%
  median) then fell on all 3 reaction days; **ASTRAL**'s big
  reactions faded all 3 times. HINDCOPPER showed the strongest
  pre-results accumulation — and it did not pay.

Sources: `stocks_event_axis_report.md`,
`stock_reaction_profiles.md`.

## 5. October paper table (per 100 shares)

| System | Trades | October net |
|---|---|---|
| INV1 | 39 | **+₹8,490.91** |
| V5 × T10 | 378 | **+₹6,502.57** |
| S12 (superseded line) | 8 | **+₹1,885.00** |
| N4-V3 | 6 | −₹530.69 |
| P2F | 4 | −₹102.83 |

These are five separate paper books — they overlap on the same
stocks and days, so **they cannot be added together** into one
account figure. October flattered the high-frequency books; the
event books (N4-V3, P2F) were quiet — their money was made in
the other nine months.

## 6. November exam board — all self-running from Mon 2 Nov

Every logger reports in this stocks chat on its own schedule.
No re-tuning during November.

- **N4-V3 — PRIMARY** (~15:52): judged on November net + win% +
  trade count together at T125; a positive month alone does not
  adopt it, per its frozen honesty clause.
- **INV1 — SHADOW** (~16:52): positive November with ≥20 trades
  upgrades INV1 to candidate; negative kills it; a month where
  the below-trend condition never triggers is inconclusive.
- **P2F — SHADOW** (~17:22): T125 net positive with ≥8 trades
  → candidate next to N4-V3; negative → dead; fewer than 8
  qualifying events → inconclusive, extends to December. First
  trade already pre-booked: **GODREJCP SHORT on Mon 2 Nov**
  (reaction day −2.27%).
- **Morning-Mover HOME A/B** (~18:12): the flagship (A = 10:00
  measurement) and the 10:15 variant (B) logged side-by-side on
  the home 25, judged independently on fresh data.
- **Morning-Mover EXT A/B** (~19:02): the same A/B test on the
  25 new large caps — the transfer universe gets its own fresh
  verdict, never pooled with home.

## 7. Open items

- **Your actual equity broker charges are still unknown.** They
  decide several near-miss systems whose breakeven sits between
  ₹16 and ₹34 per trade. They do **not** decide the flagship —
  Morning-Mover's breakeven is ₹161.31/trade.
- **Your watchlist is 30 stocks; we hold 25.** The other 5 names
  have not been shared, so nothing has been tested on them.
- **December windows** are reserved for any candidate whose
  November exam comes back inconclusive (too few trades) under
  its pre-registered rule.
