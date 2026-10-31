# MOVER-A → A2 TUNING — REPORT

Spec frozen BEFORE scoring: `stocks_moverA2_frozen.md`.
Engine: `stocks_moverA2.py` (Line 5 machinery verbatim + cap/flank
knobs). Results JSON: `stocks_moverA2_results.json`. Trade dumps:
`moverA2_<family>_trades.csv`.

Equity cash intraday, LONG/SHORT, paper only, real ₹0. All figures
provisional per 100 shares, ₹40/trade flat. Window Jan–Oct 2026
(Oct 1–28). Primary book: pooled 50 (home 25 + ext 25); home/ext
splits reported per family.

**Improver gate (pooled 50):** net > +₹249,155.03 (base) AND
Jan–May > 0 AND Jun–Oct > 0 AND breadth ≥ 35/50 AND losing months
≤ 3 AND October > 0. A pass is frozen as an A2 candidate for a
fresh window — in-sample only, not adoption. November's frozen
shadows are untouched.

## Validation (anchors before scoring)

**ALL PASS, to the paisa**, before any family was scored:

- Home: 424 chains, 698 trades, net +₹84,671.74 (JM +₹52,884.19 /
  JO +₹31,787.55; Oct +₹16,825.42; breadth 16/25) ✓
- Ext: 199 chains, 300 trades, net +₹164,483.29 (JM +₹73,142.55 /
  JO +₹91,340.74; Oct +₹39,984.55; breadth 22/25) ✓
- Pooled 50: 623 chains, 998 trades, net **+₹249,155.03** (JM
  +₹126,026.74 / JO +₹123,128.29; Oct +₹56,809.97; breadth 38/50;
  top-3 34.1%) ✓
- Home legs: direct 424 trades +₹93,575.31; re-entry 274 trades
  −₹8,903.57 ✓
- Pooled losing months exactly Jan / Feb / May (3) ✓
- Field-by-field diff of the A2 builder's base trades vs the
  published Line 5 dumps (`mover_A_old_trades.csv` 698 rows,
  `mover_A_ext_trades.csv` 300 rows): **IDENTICAL** ✓

## A2-1 — DIRECT-ONLY (chain cap 1, re-entry leg dropped)

**Pooled 50: 623 chains, 623 trades, net +₹275,795.51** —
JM +₹150,504.40 / JO +₹125,291.11; October +₹49,777.01; chain win
47.4%; expectancy +₹442.69/chain; breadth **42/50**; top-3 28.1%.
Home +₹93,575.31 (= the base direct leg exactly — the discarded
re-entry leg was worth −₹8,903.57 there); ext +₹182,220.20.
Pooled months (chains / net): Jan 74 / −₹6,593.95; Feb 69 /
−₹77.79; Mar 105 / +₹74,776.66; Apr 73 / +₹58,817.01; May 77 /
+₹23,582.47; Jun 39 / +₹42,028.98; Jul 51 / +₹9,444.76; Aug 33 /
−₹1,763.77; Sep 26 / +₹25,804.13; Oct 76 / +₹49,777.01.
Losing months: Jan, Feb, Aug (3 — same count as base, different
third month: May is cured, August appears).
**GATE: PASS** (net > base ✓, both halves ✓, breadth 42 ≥ 35 ✓,
losing months 3 ≤ 3 ✓, October ✓). Dropping the re-entry leg is
worth +₹26,640.48 over base on 375 fewer trades.

## A2-2 — SAME-DIRECTION

**Pooled 50: 571 chains, 923 trades, net +₹261,069.37** —
JM +₹136,035.93 / JO +₹125,033.44; October +₹55,768.00; chain win
58.3%; expectancy +₹457.21/chain; breadth **41/50**; top-3 32.6%.
Home +₹92,923.38 (identical to the Line 2b R5a / Line 5 anchor —
cross-validated); ext +₹168,145.99.
Pooled months: Jan 68 / −₹5,791.34; Feb 63 / +₹3,879.21; Mar 96 /
+₹68,983.55; Apr 68 / +₹70,481.33; May 74 / −₹1,516.82; Jun 35 /
+₹41,285.51; Jul 46 / +₹1,683.69; Aug 25 / +₹3,872.57; Sep 24 /
+₹22,423.67; Oct 72 / +₹55,768.00.
Losing months: Jan, May (2).
**GATE: PASS** — the smallest net gain of the five (+₹11,914.34
over base): the same-direction filter's benefit is mostly offset
by the re-entry leg it retains (pooled re-entry legs under this
filter: home −₹9,446.15, ext −₹19,568.09).

## A2-3 — DIRECT-ONLY + SAME-DIRECTION

**Pooled 50: 571 chains, 571 trades, net +₹290,083.61** —
JM +₹160,391.80 / JO +₹129,691.81; October +₹48,735.04; chain win
49.7%; expectancy **+₹508.03/chain**; breadth **43/50**; top-3
27.4% (lowest concentration so far). Home +₹102,369.53; ext
+₹187,714.08 — each exactly its universe's same-direction direct
leg.
Pooled months: Jan 68 / −₹2,020.51; Feb 63 / +₹5,525.96; Mar 96 /
+₹73,773.25; Apr 68 / +₹59,460.99; May 74 / +₹23,652.11; Jun 35 /
+₹44,412.73; Jul 46 / +₹7,362.48; Aug 25 / +₹2,408.33; Sep 24 /
+₹26,773.23; Oct 72 / +₹48,735.04.
Losing months: **Jan only (1)**.
**GATE: PASS** — the two A2-1/A2-2 changes stack: +₹40,928.58
over base, fewest losing months of the cap/direction families.

## A2-4 — MEASUREMENT MICRO-STEPS (10:05 / 10:10)

### A2-4a — measure to < 10:05
**Pooled 50: 751 chains, 1,191 trades, net +₹332,476.95** —
JM +₹184,162.96 / JO +₹148,313.99; October +₹86,270.43; chain win
56.6%; expectancy +₹442.71/chain; breadth **46/50**; top-3 37.7%.
Home +₹135,682.16 (no losing month at home); ext +₹196,794.79.
Pooled months: Jan 90 / +₹5,815.56; Feb 78 / +₹27,008.39; Mar 122
/ +₹59,183.90; Apr 87 / +₹63,946.00; May 88 / +₹28,209.11; Jun 58
/ +₹44,940.37; Jul 57 / −₹6,565.71; Aug 37 / −₹681.64; Sep 28 /
+₹24,350.54; Oct 106 / +₹86,270.43.
Losing months: Jul, Aug (2) — the base's Jan/Feb/May holes are
all cured; the cost is a soft Jul–Aug.
**GATE: PASS** (+₹83,321.92 over base).

### A2-4b — measure to < 10:10
**Pooled 50: 812 chains, 1,280 trades, net +₹406,054.73** —
JM +₹202,495.77 / JO +₹203,558.96 (near-perfectly balanced
halves); October +₹103,883.51; chain win 59.6%; expectancy
+₹500.07/chain; breadth **47/50**; top-3 30.2%.
Home +₹163,227.51 (no losing month); ext +₹242,827.22 (breadth
25/25).
Pooled months: Jan 90 / +₹19,752.98; Feb 85 / +₹19,712.05; Mar
133 / +₹77,893.47; Apr 95 / +₹57,944.16; May 88 / +₹27,193.11;
Jun 69 / +₹58,162.97; Jul 60 / +₹5,062.76; Aug 40 / +₹15,572.15;
Sep 32 / +₹20,877.57; Oct 120 / +₹103,883.51.
Losing months: **none (0)**.
**GATE: PASS** — +₹156,899.70 over base, the best of A2-1..4 by
pooled net (and by breadth). The A→B measurement slope continues
through 10:05 and 10:10 without flattening. Per the frozen spec,
A2-5 exit variants are applied to this family's configuration
(window < 10:10, cap 2, any-direction, T125 base exits).

## A2-5 — EXIT VARIANTS on the best of A2-1..4 (= A2-4b, 10:10 config)

### A2-5a — target +1.5% / stop −0.5%
**Pooled 50: 812 chains, 1,210 trades, net +₹322,897.36** —
JM +₹185,485.55 / JO +₹137,411.81; October +₹75,574.39; chain win
56.3%; expectancy +₹397.66/chain; breadth 45/50; top-3 33.6%;
losing months: none. Home +₹147,438.08; ext +₹175,459.28.
Pooled months: Jan +₹23,522.51; Feb +₹22,252.55; Mar +₹68,576.41;
Apr +₹51,795.46; May +₹19,338.62; Jun +₹27,265.42; Jul +₹6,614.56;
Aug +₹14,863.09; Sep +₹13,094.35; Oct +₹75,574.39.
**GATE vs base: PASS — but −₹83,157.37 BELOW its own basis
(A2-4b).** The wider target gives back expectancy everywhere
(fewer target hits, more square-offs); rejected as an exit change.

### A2-5b — target +1.25% / stop −0.65%
**Pooled 50: 812 chains, 1,205 trades, net +₹397,758.28** —
JM +₹195,422.20 / JO +₹202,336.08; October +₹103,404.29; chain win
61.9% (best recorded); expectancy +₹489.85/chain; breadth 47/50;
top-3 26.6% (lowest of all families); losing months: none.
Home +₹178,825.18; ext +₹218,933.10.
Pooled months: Jan +₹17,476.27; Feb +₹17,577.28; Mar +₹71,577.72;
Apr +₹62,452.12; May +₹26,338.81; Jun +₹48,347.49; Jul
+₹13,471.77; Aug +₹16,915.68; Sep +₹20,196.85; Oct +₹103,404.29.
**GATE vs base: PASS — but −₹8,296.45 BELOW its own basis
(A2-4b).** The wider stop raises win rate and cuts concentration
yet still nets slightly less than the frozen −0.5% stop. Rejected
as an exit change; the frozen T125 exits stand.

## A2-6 — FLANK RULE (mover-UP days: same-direction only; mover-DOWN: unchanged)

**Pooled 50: 580 chains, 937 trades, net +₹260,880.35** —
JM +₹134,186.91 / JO +₹126,693.44; October +₹55,768.00; chain win
58.1%; expectancy +₹449.79/chain; breadth 41/50; top-3 33.2%.
Home +₹92,352.58; ext +₹168,527.77.
Pooled months: Jan 69 / −₹6,345.00; Feb 64 / +₹4,792.56; Mar 98 /
+₹68,983.42; Apr 71 / +₹69,559.98; May 75 / −₹2,804.05; Jun 35 /
+₹41,285.51; Jul 47 / +₹3,343.69; Aug 25 / +₹3,872.57; Sep 24 /
+₹22,423.67; Oct 72 / +₹55,768.00.
Losing months: Jan, May (2).
**GATE: PASS** — but the gain over base is only +₹11,725.32, the
smallest of all families, and the pooled result is statistically
the A2-2 result (October identical at +₹55,768.00): restricting
only the up-flank captures nearly all of what full same-direction
captures, and the thin up-flank was never the pooled book's real
problem. Recorded; not the candidate.

## Loop summary — A2 ranking (pooled 50, Jan–Oct 2026)

| Family | Change | Chains | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Losing mo | Gate |
|---|---|---|---|---|---|---|---|---|---|
| Base A | — | 623 | +249,155.03 | +126,026.74 | +123,128.29 | +56,809.97 | 38/50 | 3 | — |
| A2-6 | flank rule | 580 | +260,880.35 | +134,186.91 | +126,693.44 | +55,768.00 | 41/50 | 2 | PASS |
| A2-2 | same-direction | 571 | +261,069.37 | +136,035.93 | +125,033.44 | +55,768.00 | 41/50 | 2 | PASS |
| A2-1 | direct-only | 623 | +275,795.51 | +150,504.40 | +125,291.11 | +49,777.01 | 42/50 | 3 | PASS |
| A2-3 | direct + same-dir | 571 | +290,083.61 | +160,391.80 | +129,691.81 | +48,735.04 | 43/50 | 1 | PASS |
| A2-5a | 10:10 + T150/S050 | 812 | +322,897.36 | +185,485.55 | +137,411.81 | +75,574.39 | 45/50 | 0 | PASS* |
| A2-4a | measure 10:05 | 751 | +332,476.95 | +184,162.96 | +148,313.99 | +86,270.43 | 46/50 | 2 | PASS |
| A2-5b | 10:10 + T125/S065 | 812 | +397,758.28 | +195,422.20 | +202,336.08 | +103,404.29 | 47/50 | 0 | PASS* |
| **A2-4b** | **measure 10:10** | **812** | **+406,054.73** | **+202,495.77** | **+203,558.96** | **+103,883.51** | **47/50** | **0** | **PASS** |

\* A2-5a/5b pass the gate against the BASE but score below their
own basis (A2-4b); as exit changes they are rejected — the A2
candidate keeps the frozen T125 exits.

Findings, in order of size:
1. **Measurement time is the dominant lever.** Moving the
   pre-move measurement from < 10:00 to < 10:10 adds +₹156,899.70
   pooled, lifts breadth 38 → 47/50, and removes every losing
   month. The slope toward MOVER-B's 10:15 continues through both
   micro-steps (10:05: +₹332,476.95; 10:10: +₹406,054.73; Line 5's
   10:15 pooled: +₹464,617.03) — A2-4b is an interior point of
   that slope, not a peak.
2. **The re-entry leg is a drag at both measurements, split by
   universe.** Direct-only (A2-1) beats base by +₹26,640.48 at
   the 10:00 measurement. At 10:10 the re-entry leg is +₹11,403.01
   at home but −₹24,840.95 on ext (pooled −₹13,437.94), so it
   remains a pooled drag inside the winning A2-4b configuration
   too. A direct-only variant at 10:10 was NOT among the frozen
   families and is not scored here — it is a new hypothesis for a
   future spec, not a result.
3. **Exit widening does not help.** Neither the 1.5% target nor
   the 0.65% stop beats frozen T125 on the best configuration.
4. **Direction filters help modestly and stack** (A2-3 is the
   best of the 10:00-measurement families), but they are worth
   ~+₹41k where measurement time is worth ~+₹157k.

**A2 CANDIDATE: A2-4b** — frozen in
`stocks_moverA2_candidate_spec.md` (primary rule verbatim + the
other gate-passers recorded as alternates). In-sample only: the
candidate earns a fresh-window test, nothing more. November's
frozen shadows are untouched.
