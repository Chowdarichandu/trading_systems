# Line T1 — The Combined Real Book: INV-LONG + N4-V3 + P2F as one book

Computed once, under `stocks_T1_frozen.md` (combination rules frozen
before any combined figure existed). Equity cash intraday, LONG/SHORT.
**Paper only — real money ₹0, no orders.** All figures provisional per
100 shares, ₹40/trade cost already deducted. Jan–Oct 2026
(October = 1–28 Oct). **Home 25 universe only** — no ext pooling
(INV-LONG and P2F both failed transfer to the ext 25).

## Validation — all three components reproduce exactly

| Component | Trades | Recomputed | Published | |
|---|---|---|---|---|
| INV-LONG (T125, LONG rows) | 249 | +₹24,185.73 | +₹24,185.73 | ✅ to the paisa |
| N4-V3 (T125) | 56 | +₹7,990.43 | +₹7,990.43 | ✅ to the paisa |
| P2F (2.5% band) | 39 | +₹15,489.08 | +₹15,489.08 | ✅ to the paisa |

## The combined book

| | |
|---|---|
| Total trades | **344** |
| Combined net | **+₹47,665.24** |
| H1 (Jan–May) | +₹26,609.09 |
| H2 (Jun–Oct) | +₹21,056.15 |
| October | +₹6,845.39 |
| Breadth | **13/25** stocks net-positive (25 traded) |
| Expectancy | +₹138.56 / trade |

### Full month table

| Month | Trades | Net ₹ |
|---|---|---|
| Jan | 53 | +6,682.89 |
| Feb | 57 | −5,533.46 |
| Mar | 62 | +7,283.60 |
| Apr | 42 | +3,339.69 |
| May | 46 | +14,836.37 |
| Jun | 21 | +1,305.20 |
| Jul | 9 | +3,282.63 |
| Aug | 16 | +5,802.73 |
| Sep | 9 | +3,820.20 |
| Oct | 29 | +6,845.39 |

9 of 10 months positive; February is the only losing month
(INV-LONG's known February hole, −₹9,951.91, only partly covered).

### Overlap (pre-declared reporting)

Systems run independently; both trades count on a collision.
**5 same-stock-same-day collisions** across systems, 14 trades
involved, combined net of those trades −₹2,160.55:
INV-LONG × N4-V3: 3 (2026-02-01 BDL, NATIONALUM, VEDL);
INV-LONG × P2F: 2 (2026-02-09 KALYANKJIL, 2026-05-04 VEDL);
N4-V3 × P2F: 0. Overlap is small and slightly negative — the books
are mechanically near-independent. Their dependence is not in the
calendar; it is in the stocks (below).

### Honest monthly run-rate vs the target bar

- Mean: **₹4,766.52/month**; median month ₹4,811.47.
- Target bar: ~₹25,000/month. **The combined real book runs at
  ~19% of the bar** — ₹47.7k over 10 months against the ~₹250k the
  retracted claims implied. Combining the three real systems adds
  them; it does not multiply them.

## Stress battery — the tests that killed the EventBook

EventBook died here: ex-top-3 stocks −₹3,046.87, winsorised H1
−₹1,805.21. Same battery, same definitions:

### 1. Ex-top-3 stocks — **FAILS, both legs**

Top 3 stocks of the combined book: GLENMARK +₹22,748.11,
TVSMOTOR +₹20,514.96, OBEROIRLTY +₹8,120.19 — together
**+₹51,383.26 = 107.8% of the entire combined net**.
Removing them (294 trades remain):

| | Net ₹ |
|---|---|
| Total | **−3,718.02** |
| H1 | **−1,685.06** |
| H2 | **−2,032.96** |
| October | −1,299.73 |

### 2. Winsorised at +₹2,000/stock — **FAILS**

Net **−₹1,274.83**; H1 **−₹585.95** (flips negative, exactly the
EventBook failure mode); H2 +₹2,306.74.

### 3. Ex-top-3 trades — passes

The three largest single trades are one TVSMOTOR trade from *each*
system (+₹4,937.62 INV-LONG 2026-10-15; +₹4,844.50 P2F 2026-07-23;
+₹4,267.87 N4-V3 2026-05-14). Removing them: **+₹33,615.25**,
H1 +₹22,341.22 / H2 +₹11,274.03 — both halves stay positive.
The book is not carried by three lucky trades. It is carried by
two lucky *stocks*.

## Verdict — the combined book FALLS under stress. No candidate.

Under the frozen verdict rule (ex-top-3 stocks: net > 0 AND both
halves > 0), the combined book **fails on both legs**, the same
death as the EventBook. **No `stocks_T1_combined_candidate_spec.md`
is frozen.**

**Which component's concentration does the damage: all three,
through the same two names.** GLENMARK + TVSMOTOR together are
+₹43,263.07 = **90.8% of the combined net**, and they are not an
INV-LONG problem alone:

- GLENMARK is the #1 payer in N4-V3 (+₹9,383.00 — 117% of that
  system's whole net) and in P2F (+₹5,112.24), and #2 in INV-LONG
  (+₹8,252.87).
- TVSMOTOR is the #1 payer in INV-LONG (+₹15,287.54) and #2 in
  P2F (+₹4,844.50).
- Each component's own top-3 stocks equal 59.0% (INV-LONG), 28.0%
  (N4-V3), 29.1% (P2F) of the *combined* net.

Plainly: these are three different entry mechanisms, but on this
watchlist they are substantially **one bet on GLENMARK and
TVSMOTOR behaving well in 2026**. Diversification across systems
did not diversify the payer base. Until a real system pays broadly
across stocks — the breadth gate the invention lines keep failing —
combining real-but-concentrated books cannot reach the target bar
honestly, and any combined figure quoted without this stress would
repeat the EventBook mistake.

What survives this line unchanged: the three components themselves,
on their own frozen terms — N4-V3 faces November as primary, INV1
and P2F as shadows. Their individual verdicts never depended on
this combination.

Files: `stocks_T1_frozen.md` (rules), `stocks_T1.py` (engine),
`stocks_T1_results.json` (full results), this report.
