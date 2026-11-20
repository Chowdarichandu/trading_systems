# FORWARD-PAPER PACK — the four gated candidates (live from 2026-11-18)

**Status: LIVE — owner-approved.** The owner approved forward
paper for these four lines on **2026-11-18 ~07:12 IST**
("can we wire them today for paper tray" — wired the same
day). Score-only: no orders, no position-taking, paper only,
real money ₹0. Basis: equity cash, PROVISIONAL per 100
shares, ₹40/trade. No stock options.

**Start date: 2026-11-18.** First real run: the
`forward-candidates-daily` cron, Mon–Fri ~20:10 IST, first
fire Wed 2026-11-18 after the close. Forward tallies count
only runs from 2026-11-18 onward; historical dry runs and
self-tests are machinery checks and never count.

## The four lines (frozen rules — no tuning, ever)

| Line | Book | Scorer | Gate record |
|---|---|---|---|
| TARANG-C1 | T25-C frozen (GAP-FADE-UP-15) | `tarang25c_scorer.py` | Design 25 PASS 9/9: +₹1,51,307.50 / +₹50,274.68 |
| TARANG-C2 | T25-C+TRAIL | `tarang25c_trail_scorer.py` | Design 26 WS3 PASS 9/9: +₹1,58,473.60 / +₹74,939.33 |
| SAPTA-C1 | Design 16 UNION (UP-15 ∪ FADE-20, TRAIL) | `sapta_forward_scorer.py --book SAPTA-C1` | Design 16 PASS 4/4: +₹1,36,826 / +₹24,894 |
| SAPTA-C2 | Design 13 GAPFADE-TRAIL | `sapta_forward_scorer.py --book SAPTA-C2` | Design 13 PASS 4/4: +₹70,322 / +₹21,826 |

Frozen rule sources: `tarang25c_forward_pack.md`,
`tarang25c_trail_forward_pack.md`, `sapta_d16_SPEC.md` §2,
`sapta_d13_SPEC.md` §3. Shared shape: gap-fade entries at the
first-bar open, caps 10/day and 1/name-day, allocation
|gap%| DESC → vol_ratio DESC → universe/quarter order ASC;
TARANG-C1 exits −1% stop / 15:15 square-off, the other three
exit by TRAIL (breakeven after half the gap retraces).
SAPTA forward dates past the stored window (2026-11-13) keep
the last stored quarter (Q4 2026) in force until the next
ranking date — the frozen construction's own continuation.

## Machinery

- **Runner:** `forward_candidates_runner.py` — refreshes the
  day's 5-min bars into the family stores via the established
  Upstox v3 route (browser User-Agent; token read at runtime
  from `upstox_refresh/.env`, never printed), runs the four
  scorers, appends taken trades to the ledgers, prints
  per-line day results + running forward totals. **HTTP 429 =
  hard stop:** nothing scored, all lines NC for the day, the
  next run catches up. Same-day scoring before 15:35 IST is
  refused (incomplete bars).
- **Cron:** `forward-candidates-daily`, Mon–Fri 20:10 IST,
  reports to the Bank + Nifty — Combined View chat.
- **Ledgers** (idempotent, trade key `LINE|date|sym`):
  `forward_tarang_c1_log.csv` · `forward_tarang_c2_log.csv` ·
  `forward_sapta_c1_log.csv` · `forward_sapta_c2_log.csv`.

## Verification at wiring (2026-11-18)

- **Self-tests — all PASS, exact matches:** TARANG-C1 and
  TARANG-C2 on the pre-registered anchor days 2025-08-18 and
  2026-03-24 (10/10 trades each day, every field). SAPTA-C1
  and SAPTA-C2 on their cap-bound anchor days 2025-04-15 and
  2026-03-24 (10/10 trades each day, every field) against
  `sapta_d16_trades.csv` / `sapta_d13_trades.csv`.
- **Runner dry run 2025-04-15** (machinery check, no ledger
  writes): TARANG-C1 10 taken +₹2,833.78 · TARANG-C2 10
  taken +₹4,481.66 · SAPTA-C1 10 taken −₹945.00 · SAPTA-C2
  10 taken −₹945.00 — all identical to the published books.

## Honest limits (carried from the gate reports)

Gate passes are not sizing claims: TARANG's 2026 pace is
below the ₹15,000/month segment floor and its per-year
drawdowns are large; SAPTA's books do not meet the EKAM
power bar in 2026 (SAPTA-C1 +₹24,894 vs EKAM Cand-1
+₹63,884). Forward paper exists to test exactly that,
live, one day at a time.
