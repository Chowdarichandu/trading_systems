# MOVER-B3 — Tuning Report (Line B3)

Families frozen in `stocks_moverB3_frozen.md` BEFORE scoring.
Equity cash intraday, LONG/SHORT only, paper only, real money ₹0.
All figures provisional per 100 shares, net = gross − ₹40/trade.
Window Jan–Oct 2026 (Oct = 1–28). Pooled 50 primary; home/ext
splits reported per cell. Engine: `stocks_moverB3.py` (B2
machinery reused verbatim); results: `stocks_moverB3_results.json`.

## Anchor validation — PASS

The B2 candidate configuration (measurement 10:30, threshold
1.0%, any direction, cap 2, T125) reproduced exactly before any
B3 cell was scored: pooled 1,212 chains / 1,835 trades /
**+₹812,204.86**, halves +₹448,461.50 / +₹363,743.36, October
+₹144,167.85, breadth 48/50, expectancy +₹670.14/chain, max DD
−₹18,493.11, no losing month; home +₹270,069.11 (24/25),
ext +₹542,135.75 (24/25).

## Reference slope (from the B-line, pooled net)

| Measurement | Chains | Net ₹ | Max DD ₹ |
|---|---|---|---|
| 10:00 (MOVER-A) | 623 | +249,155.03 | −33,440.10 |
| 10:15 (MOVER-B) | 917 | +464,617.03 | −17,471.45 |
| 10:20 (B2-4a) | — | +606,005.93 | — |
| 10:30 (B2 candidate) | 1,212 | +812,204.86 | −18,493.11 |

B3-1 tests whether the slope continues past 10:30.

## B3-1 — Measurement extension: the slope does NOT peak inside the frozen range

| Cell | Meas. | Chains | Trades | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Max DD ₹ | Losing months | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B2 cand. | 10:30 | 1,212 | 1,835 | +812,204.86 | +448,461.50 | +363,743.36 | +144,167.85 | 48/50 | +670.14 | −18,493.11 | none | — |
| B3-1a | 10:45 | 1,417 | 2,128 | +937,163.76 | +522,289.63 | +414,874.13 | +151,163.54 | 49/50 | +661.37 | −25,759.71 | none | FAIL (DD leg only, by ₹759.71) |
| B3-1b | 11:00 | 1,615 | 2,411 | +1,094,120.71 | +618,715.89 | +475,404.82 | +155,108.08 | 49/50 | +677.47 | −26,464.55 | none | FAIL (DD leg only) |
| B3-1c | 11:30 | 1,788 | 2,675 | **+1,442,985.71** | +864,626.10 | +578,359.61 | +172,253.96 | 49/50 | +807.04 | −16,115.66 | none | **PASS** |

Splits — B3-1a: home +₹331,264.77 (24/25), ext +₹605,898.99
(25/25). B3-1b: home +₹355,566.34 (24/25), ext +₹738,554.37
(25/25). B3-1c: home +₹457,950.50 (24/25), ext +₹985,035.21
(25/25).

Month tables (pooled net ₹, all ten months positive in every
cell): B3-1a weakest month Sep +33,331.54; B3-1b weakest May
+37,644.36; B3-1c weakest Sep +66,662.49, strongest Mar
+246,774.48. Full month tables are in
`stocks_moverB3_results.json`.

**Read:** net rises at every step 10:30 → 10:45 → 11:00 → 11:30
(+15.4%, +16.7%, +31.9% step-over-step) and expectancy/chain
jumps at 11:30 (+807.04). The slope has NOT turned inside the
frozen range — 11:30 is the best *tested* point, not a proven
peak; the frozen list stops here by design and no later time
was tried. The two intermediate cells fail the candidate gate
on the drawdown leg alone (−₹25,759.71 and −₹26,464.55 vs the
−₹25,000 floor); their drawdowns arrive with the larger chain
counts. At 11:30 the drawdown instead *improves* to −₹16,115.66,
better than the B2 candidate's −₹18,493.11, and B3-1c passes
every gate leg against the B2 candidate. Per the frozen list,
11:30 is "the peak" for B3-3 purposes (best B3-1 cell).
Only NHPC is net-negative at 11:30 (−₹470.85 over 40 chains).

## B3-2 — Stack on 10:30

| Cell | Config | Chains | Trades | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Max DD ₹ | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | plain 10:30 | 1,212 | 1,835 | +812,204.86 | +448,461.50 | +363,743.36 | +144,167.85 | 48/50 | +670.14 | −18,493.11 | — |
| B3-2a | + direct-only (cap 1) | 1,212 | 1,212 | +764,385.44 | +450,587.49 | +313,797.95 | +100,931.09 | 48/50 | +630.68 | −10,758.30 | FAIL (net) |
| B3-2b | + same-direction | 1,127 | 1,694 | **+855,301.87** | +452,788.81 | +402,513.06 | +168,972.51 | 48/50 | +758.92 | −16,008.81 | **PASS** |
| B3-2c | + combined | 1,127 | 1,127 | +813,234.13 | +459,800.04 | +353,434.09 | +123,463.65 | 49/50 | +721.59 | −10,758.30 | PASS (net leg by only +₹1,029.27) |

Splits — B3-2a: home +₹224,822.39 (23/25), ext +₹539,563.05
(25/25). B3-2b: home +₹293,842.79 (24/25), ext +₹561,459.08
(24/25). B3-2c: home +₹246,882.51 (24/25), ext +₹566,351.62
(25/25). No losing month in any cell.

**Read:** the 10:15 stack behaviour does NOT repeat at 10:30.
Direct-only now *subtracts* ₹47,819.42 — at 10:30 the re-entry
leg is profitable (the base's round-2 trades earn), whereas at
10:15 it was a drag. Same-direction still adds, +₹43,097.01,
and passes the full gate. The combination keeps only the
same-direction gain on the direct leg and lands +₹1,029.27
above base — a gate pass on paper, not "clearly better".
Both remain far below the plain 11:30 cell (+₹1,442,985.71).

## B3-3 — Stack on the peak (11:30 + combined: cap 1 + same-direction)

| Config | Chains | Trades | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Max DD ₹ | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| plain 11:30 (B3-1c) | 1,788 | 2,675 | +1,442,985.71 | +864,626.10 | +578,359.61 | +172,253.96 | 49/50 | +807.04 | −16,115.66 | — |
| **11:30 + combined** | 1,694 | 1,694 | **+1,570,930.17** | +926,820.20 | +644,109.97 | +174,518.22 | 49/50 | **+927.35** | **−8,957.16** | **PASS** |

Splits: home +₹440,758.67 (24/25), ext +₹1,130,171.50 (25/25).
No losing month. Top-3 share 36.3%.

**Read:** unlike at 10:30, at 11:30 the combined stack adds
real money: +₹127,944.46 over plain 11:30 with 981 fewer trades,
expectancy/chain up to +₹927.35, and the max drawdown *halves*
to −₹8,957.16 — the shallowest of any configuration in the
B-line. Both restrictions earn at 11:30: the pre-move is more
informative later (same-direction filters better) and the
re-entry leg that paid at 11:30 plain was concentrated in
counter-direction chains. This is the best configuration
overall and the base for B3-4.

## B3-4 — Exit check on the best configuration (B3-3: 11:30 + combined)

| Cell | Exits | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Win % | Max DD ₹ | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| B3-3 | T125/S050 | +1,570,930.17 | +926,820.20 | +644,109.97 | +174,518.22 | 49/50 | +927.35 | 66.0 | −8,957.16 | — |
| B3-4a | T150/S050 | +1,518,848.92 | +906,652.66 | +612,196.26 | +171,392.27 | 49/50 | +896.61 | — | −17,363.45 | FAIL (net) |
| B3-4b | **T125/S065** | **+1,623,905.15** | +951,573.84 | +672,331.31 | +190,471.72 | 49/50 | **+958.62** | 71.1 | −11,557.03 | **PASS** |

Splits — B3-4a: home +₹463,383.46 (24/25), ext +₹1,055,465.46
(25/25). B3-4b: home +₹489,399.84 (24/25), ext +₹1,134,505.31
(25/25). No losing month in either cell; chains/trades 1,694
in both (exit parameters do not change chain formation).

**Read:** the wider target subtracts (−₹52,081.25 vs B3-3);
the wider stop adds (+₹52,974.98) and lifts win rate to
71.1% — at 11:30 with direction-confirmed entries, trades
that dip 0.5–0.65% before running are worth keeping. B3-4b
passes the full gate against B3-3, the configuration it
modifies.

## Final verdict — B3 candidate frozen

The best configuration overall, passing every gate leg, is
**B3-4b: measurement 11:30, threshold 1.0%, combined stack
(direct-only cap 1 + same-direction), exits T125/S065**:

- Pooled 50: **1,694 chains / 1,694 trades, net +₹1,623,905.15**
  — exactly **2.00×** the B2 candidate's +₹812,204.86.
- Halves: Jan–May **+₹951,573.84** / Jun–Oct **+₹672,331.31**.
- October (1–28): **+₹190,471.72**.
- Breadth **49/50** — only NHPC negative (−₹97.91 over
  39 chains, i.e. scratch). Top-3 share 33.3%
  (ULTRACEMCO +₹208,590.55, MARUTI +₹194,200.95,
  EICHERMOT +₹137,272.96).
- Expectancy **+₹958.62/chain**, chain win 71.1%.
- Max drawdown **−₹11,557.03** — shallower than the B2
  candidate's −₹18,493.11 despite double the profit.
- **No losing month** — weakest month May +₹86,294.15;
  strongest Mar +₹262,658.41. Top-2 months (Mar + Oct)
  = 27.9% of the total.

### Full pooled month table — B3 candidate (B3-4b)

| Month | Chains | Net ₹ | Cumulative ₹ |
|---|---|---|---|
| Jan | 203 | +201,106.80 | +201,106.80 |
| Feb | 179 | +208,095.62 | +409,202.42 |
| Mar | 228 | +262,658.41 | +671,860.83 |
| Apr | 186 | +193,418.86 | +865,279.69 |
| May | 146 | +86,294.15 | +951,573.84 |
| Jun | 155 | +184,327.17 | +1,135,901.01 |
| Jul | 166 | +124,061.82 | +1,259,962.83 |
| Aug | 108 | +88,134.83 | +1,348,097.66 |
| Sep | 98 | +85,335.77 | +1,433,433.43 |
| Oct (1–28) | 225 | +190,471.72 | +1,623,905.15 |
| **Total** | **1,694** | **+1,623,905.15** | — |

### Slope summary (pooled net, plain rule unless noted)

10:00 +₹249,155.03 → 10:15 +₹464,617.03 → 10:20 +₹606,005.93
→ 10:30 +₹812,204.86 → 10:45 +₹937,163.76 → 11:00
+₹1,094,120.71 → 11:30 +₹1,442,985.71 → 11:30 + combined
+₹1,570,930.17 → 11:30 + combined + S065 **+₹1,623,905.15**.

**Where the slope peaks:** it does not turn inside the frozen
range. Net is still rising at 11:30, the last point the frozen
list allowed. Calling 11:30 "the peak" would be wrong — it is
the best *tested* point; the true peak is untested beyond
11:30 and finding it is a question for a future frozen line,
not something this line may reach for after the fact.

Frozen as `stocks_moverB3_candidate_spec.md` (December 2026
fresh-window judging, ≥ 80 chains). The B2 candidate is
superseded as the line's reference by this gate pass, under
the frozen rule that a B3 configuration replaces it only on a
full gate pass against the configuration it modifies.
In-sample warnings from the B2 spec apply with full force:
this configuration was selected on the same Jan–Oct window,
through more selection steps, so its in-sample net is an
upper-bound estimate until December judges it.
