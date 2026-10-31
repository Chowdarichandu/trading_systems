# Stocks EQUITY — Tuning LINE 2 (V-line): V5 re-entry pools + LADDER+VOLUME (V3) — 2026-10-31

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0. No live trades
were placed.**
**Every rupee figure is provisional per 100 shares. Net = gross −
₹40/trade flat (frozen cost) unless a family states otherwise.
Window Jan–Oct 2026 (October = 1–28 Oct), 203 days, 25 stocks.
Spec frozen before scoring: `stocks_tuning_vline_frozen.md`.
Engine: `stocks_tuning_vline.py`. Results JSON:
`stocks_tuning_vline_results.json`. Trade dumps: `vline_<CELL>_trades.csv`.**

**Validation gates — BOTH PASSED exactly.**
- The generalised ladder engine reproduces published V3 to the
  paisa: 3,275 trades, Jan–May +₹45,413.60, Jun–Oct −₹61,697.60,
  total −₹16,284.00, breadth 10/25.
- (U5 chain gate reported in the U5 section.)

**Pass gates (frozen):** net positive in BOTH halves at ₹40 +
breadth ≥10/25 stocks net-positive + gross expectancy > 0 in
both halves.

---

## U1 — V3 direction split cure

V3 exactly as frozen (0.4% step, volume ≥1.5×, −1.0% stop,
hold-to-close), split by direction. Blocked-direction signals
consume the band extreme, per the frozen semantics — so the
split cells are true standalone systems, not subsets of the
base chain (trade counts 1,595 + 1,716 ≠ 3,275 for that reason).

| Cell | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| U1-BOTH (= V3) | 3,275 | 43.2 | +35.03 | −16,284.00 | **+45,413.60** | −61,697.60 | −25,724.35 | 10/25 |
| U1-LONG | 1,595 | 41.9 | +37.12 | −4,593.75 | **+45,574.87** | −50,168.62 | −19,238.89 | 12/25 |
| U1-SHORT | 1,716 | 43.9 | +33.82 | −10,602.16 | **+216.02** | −10,818.18 | −7,015.46 | 10/25 |

(All figures provisional per 100 shares.)

Per-half gross expectancy tells the story:
- **LONG:** Jan–May gross exp **+₹97.40**/trade — the strongest
  first half anywhere in this search — then Jun–Oct gross exp
  **−₹22.63**: the second half is gross-negative, so no cost
  level can save it. The Part 2 diagnosis (LONGs +₹43,171 →
  −₹52,032) survives the split unchanged; isolating LONGs does
  not cure the flip, it concentrates it.
- **SHORT:** gross-positive in BOTH halves (+₹40.27 / +₹28.05) —
  the only V3 cell with that property — but both are under the
  ₹40 cost in Jun–Oct and barely above it in Jan–May, so the net
  is +₹216.02 / −₹10,818.18. Its both-halves breakeven cost is
  **₹28.05/trade**. Close in structure, short on expectancy.
- Breadth: LONG-only reaches **12/25** (best breadth recorded in
  the V3 line), SHORT-only 10/25. Top-3 share is not meaningful
  (all totals negative). Worst stock in every cell: TVSMOTOR
  (−₹31,641.60 both / −₹18,930.90 LONG / −₹11,290.70 SHORT,
  provisional per 100 shares).

**Verdict U1: NO PASS.** The direction split does not cure V3.
LONG is a first-half-only system with a gross-negative second
half; SHORT is both-halves gross-positive but below cost.
Per the frozen selection rule, **best direction = LONG**
(higher Jan–Oct net, −₹4,593.75 vs −₹10,602.16) — U3 and U4
use LONG.

---

## U2 — V3 stop structure (−0.75% / −1.25% / none × both / LONG / SHORT)

Base stop is −1.0% (U1). Everything else unchanged.

| Cell | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| U2-S075-BOTH | 3,366 | 40.7 | +29.85 | −34,181.39 | +18,190.23 | −52,371.62 | −24,266.92 | 10/25 |
| U2-S075-LONG | 1,624 | 39.5 | +36.45 | −5,770.95 | +23,758.80 | −29,529.75 | −13,925.24 | 9/25 |
| U2-S075-SHORT | 1,754 | 41.6 | +23.76 | −28,484.05 | −7,383.77 | −21,100.28 | −10,416.68 | 10/25 |
| U2-S125-BOTH | 3,238 | 43.8 | +25.21 | −47,903.79 | +34,520.23 | −82,424.02 | −33,520.19 | 10/25 |
| U2-S125-LONG | 1,583 | 42.5 | +25.55 | −22,879.46 | +40,347.88 | −63,227.34 | −23,839.79 | 10/25 |
| U2-S125-SHORT | 1,710 | 44.6 | +24.68 | −26,194.88 | −7,266.77 | −18,928.11 | −10,410.40 | 11/25 |
| U2-SNONE-BOTH | 3,138 | 44.3 | +30.37 | −30,208.00 | +35,211.00 | −65,419.00 | −12,422.00 | 10/25 |
| U2-SNONE-LONG | 1,569 | 43.3 | +27.66 | −19,357.00 | +37,672.00 | −57,029.00 | −11,280.00 | 9/25 |
| U2-SNONE-SHORT | 1,704 | 45.1 | +24.39 | −26,598.00 | −12,868.00 | −13,730.00 | −7,109.00 | 11/25 |

(All figures provisional per 100 shares.)

Reading:
- **Tightening hurts.** −0.75% cuts Jan–May (BOTH +45,413.60 →
  +18,190.23 vs base) — the ~1% adverse excursions are normal
  for these entries, and a tighter stop converts more of them
  into realised losses — and Jun–Oct stays deeply negative.
  It also breaks U1-SHORT's one virtue: SHORT at −0.75% is
  Jan–May net-negative (−₹7,383.77).
- **Widening hurts more.** −1.25% makes Jun–Oct the worst in the
  family (BOTH −₹82,424.02; LONG Jun–Oct gross exp −₹39.33).
  The losing trades are not being cut too early — left longer,
  they lose more.
- **No stop is not the answer either.** With no stop at all,
  Jun–Oct gross expectancy for BOTH is **−₹0.46/trade** — the
  raw Jun–Oct drift-to-close of these entries is zero. The
  −1.0% stop actually *adds* a little second-half gross
  (+₹3.36 in U1-BOTH) by truncating the worst excursions.
- The base −1.0% stop is the best of the four settings on the
  both-directions cell (highest Jan–May, least-bad Jun–Oct).
  **The stop is not the lever.** Jun–Oct is negative at every
  stop width and with no stop — the failure is in the second
  half's entry drift, not in exit truncation.

**Verdict U2: NO PASS (0/9).** Rejected: all nine cells, each
failing the both-halves net gate (SHORT cells at −1.25% / none
also fail Jan–May).

---

## U3 — V3 time exit (13:00 / 14:30 instead of 15:10 close)

Stop −1.0% unchanged; only the terminal exit moves earlier.

| Cell | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| U3-1300-BOTH | 4,629 | 33.2 | −1.85 | −193,722.56 | −99,530.32 | −94,192.24 | −15,873.31 | 2/25 |
| U3-1300-LONG | 2,262 | 32.8 | −14.79 | −123,927.73 | −50,790.26 | −73,137.47 | −20,340.19 | 4/25 |
| U3-1430-BOTH | 3,847 | 38.4 | +9.66 | −116,718.70 | −56,558.31 | −60,160.39 | −1,741.55 | 6/25 |
| U3-1430-LONG | 1,880 | 37.9 | +15.72 | −45,650.90 | −5,452.83 | −40,198.07 | −14,025.49 | 7/25 |

(All figures provisional per 100 shares.)

Reading: **the time exit destroys the mechanism.** The ladder's
entire gross edge is the drift accumulated by holding to the
close; ending the day at 13:00 collapses gross expectancy to
−₹1.85/trade (BOTH) and at 14:30 to +₹9.66 — versus +₹35.03
holding to 15:10. Earlier exits also free slots sooner, so the
machine takes *more* entries (4,629 at 13:00 vs 3,275 base) of
*worsening* quality and pays ₹40 on each: both halves go
net-negative at both exit times, in both direction modes.
Breadth collapses to 2/25 at 13:00. This also retro-explains
Part 1's L-c diagnosis: the value in this entry set lives in
the last part of the session's drift, and any exit that
truncates the hold truncates the edge with it.

**Verdict U3: NO PASS (0/4).** Rejected: all four cells, both
halves net-negative at 13:00, both halves net-negative at 14:30.

---

## U4 — V3 step size (0.3% / 0.5% / 0.6%, LONG = best direction from U1)

Volume gate, −1.0% stop, hold-to-close unchanged. Base step
0.4% LONG is U1-LONG (net −₹4,593.75; JM +₹45,574.87 /
JO −₹50,168.62; breadth 12/25).

| Cell | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| U4-S003-LONG (0.3%) | 1,722 | 41.6 | +42.39 | **+4,122.61** | +41,806.55 | −37,683.94 | −22,187.05 | 10/25 |
| U4-S005-LONG (0.5%) | 1,457 | 41.9 | +40.94 | **+1,363.20** | +24,704.39 | −23,341.19 | −2,775.80 | 10/25 |
| U4-S006-LONG (0.6%) | 1,352 | 42.1 | +51.14 | **+15,060.21** | +38,256.63 | −23,196.42 | −20,518.94 | 9/25 |

(All figures provisional per 100 shares.)

Reading: step size is the first V-line lever that moves the
*total* — all three LONG variants are Jan–Oct net-positive
(the 0.6% step's +₹15,060.21 is the best total in the V3 line),
and widening the step roughly halves the Jun–Oct loss versus
the 0.4% base (−₹50,168.62 → ≈−₹23,200). But the split does not
cure: **Jun–Oct stays net-negative at every step**, and at the
0.3% step its gross expectancy is negative (−₹3.57); at 0.5% /
0.6% Jun–Oct gross is only +₹8.24 / +₹5.12 — the wider grid
takes fewer, later entries, which dilutes the second-half
damage rather than removing it. October is negative in all
three cells. Breadth 9–10/25.

**Verdict U4: NO PASS (0/3).** Rejected: all three cells fail
the Jun–Oct net gate. Recorded as the V3 line's best totals,
not as candidates.

---

## U5 — Round-2 emphasis on the V5 re-entry stream

**Chain gate PASSED exactly:** the chain builder at T125
uncapped reproduces Round 6's unfiltered V5 × T125 totals —
6,625 trades, net −₹184,394.90. All figures provisional per
100 shares; the tradable unit is the stock-day chain (frozen
spec), ₹40/trade on every leg.

| Variant | Chains | Trades | Chain net Jan–Oct ₹ | Exp/chain ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| U5a PROBE-CHAIN | 4,111 | 6,973 | −208,073.21 | −50.61 | −57,907.32 | −150,165.89 | −17,526.51 | 5/25 |
| U5b SKIP-PROBE | 4,096 | 6,831 | −224,988.58 | −54.93 | −75,392.06 | −149,596.52 | −23,234.11 | 3/25 |

**U5a reading — the probe destroys the round-2 edge it was
meant to unlock.** Round 6 found round 2 gross-positive *after
a full T125 round 1*. Replacing round 1 with a cheap probe
(target +0.5% / stop −0.35%) changes the round-2 population:
the probe exits fast, the signal search restarts earlier, and
a second signal fires on 2,862 stock-days instead of 1,578 —
and those extra second trades are not the Round 6 round 2.
Chains with a round 2 net −₹45,495.44; probe-only chains net
−₹162,577.77 (1,249 chains — the tight probe itself is a
losing trade: 0.5% target against a 0.35% stop at these prices
does not cover ₹40 + the stop-heavy exit mix). Total is worse
than the plain cap-2 T125 chain (−₹143,903.56, Round 6). The
round-2 edge is **not separable** from the full-size round-1
trade that precedes it.

**U5b reading — as a whole, worse; inside it, the strongest
diagnostic of this entire line.** Skipping the probe on
pre-moved days does not rescue the non-pre-moved majority, and
U5b's total (−₹224,988.58, breadth 3/25) is the worst in the
family. (15 pre-moved stock-days had a first signal but no
second, so U5b initiated 4,096 chains vs U5a's 4,111.)

### Diagnostic (pre-declared in the frozen spec, reported as
### diagnosis — NOT a scored family, NOT a pass)

The U5b qualifying-day subset — stock-days where the stock had
already moved ≥1% before 10:00 (ex-ante: last pre-10:00 close
vs day open), first signal discarded, next signal traded at
T125, one further T125 re-entry allowed (cap 2):

| Subset | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Pre-moved chains | 424 | 698 | **+84,671.74** | **+52,884.19** | **+31,787.55** | **+16,825.42** | **16/25** |

Chain win rate 55.0%, expectancy +₹199.70/chain. Leg split:
the direct entry (the would-be second signal) = 424 trades,
**+₹93,575.31** (net exp +₹220.70/trade); the further re-entry
leg = 274 trades, −₹8,903.57 — inside these chains the money
is in the single direct entry, and the extra re-entry gives
some back. Best stocks: GLENMARK +₹24,621.20, BDL +₹15,870.19,
TVSMOTOR +₹10,867.44; worst only −₹3,985.46 (KALYANKJIL) —
this is broad, not concentrated (top-3 ≈ 61% of the subset net,
worst-5 small).

**Status, stated plainly:** this subset was defined ex-ante
and pre-declared for reporting in the frozen spec, and it is
both-halves positive with the best breadth seen anywhere in
this search (16/25). It is still a *subset of a failed family,
identified by reading scored output* — under this line's
discipline it is **not** declared a scored pass. What it earns
is exactly what it gets: the rule is frozen verbatim as a
candidate spec (`stocks_vline_v2_candidate_spec.md`) for a
**fresh-window** test, with no further Jan–Oct fitting. The
leg-split observation (re-entry leg negative inside these
chains) is recorded here as a diagnostic for that future test
to judge — it is NOT written into the frozen rule.

**Verdict U5: NO PASS for U5a and U5b as frozen.** Rejected:
both variants, both halves net-negative. One diagnostic
candidate frozen for fresh data (below).

---

## U6 — Cost reality check (sensitivity only — the gate stays ₹40)

Best cell by the frozen selection rule (highest
min(Jan–May, Jun–Oct) net at ₹40 across U1–U5): **U1-SHORT**
(V3, SHORT entries only) — 1,716 trades, net at ₹40:
−₹10,602.16 (+₹216.02 / −₹10,818.18).

| Flat cost/trade | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ |
|---|---|---|---|
| ₹25 | **+15,137.84** | +12,381.02 | +2,756.82 |
| ₹40 (frozen) | −10,602.16 | +216.02 | −10,818.18 |
| ₹60 | −44,922.16 | −16,003.98 | −28,918.18 |

**Breakeven flat cost: ₹33.82/trade overall — ₹40.27 in
Jan–May, ₹28.05 in Jun–Oct** (= gross expectancy). So U1-SHORT
would pass both halves only if the user's real flat-equivalent
cost were below ≈₹28/trade at 100 shares. That is a statement
about the user's broker charges — which remain unknown and are
not invented here — **not a pass**: at the frozen ₹40 the cell
fails, and U6 changes no verdict.

---

## Line 2 verdict

1. **No scored family passes.** U1 (0/3), U2 (0/9), U3 (0/4),
   U4 (0/3), U5 (0/2) — every cell fails the both-halves net
   gate at ₹40. The V3 mechanism is now thoroughly mapped:
   its edge is a Jan–May, hold-to-close, LONG-drift phenomenon;
   direction splits, four stop widths (including none), two
   earlier exit times, and three step sizes all fail to carry
   it into Jun–Oct. The exit/stop/step dimensions are
   exhausted for V3, as they already were for the structured
   V5 pools (Round 8). Nothing from U1–U4 or U5-as-frozen is
   adopted, and November's frozen exams are untouched.
2. **One diagnostic candidate frozen for fresh data:** the
   pre-moved skip-first-signal rule from U5b's pre-declared
   subset (+₹84,671.74 in-sample, both halves positive,
   breadth 16/25) — frozen verbatim in
   `stocks_vline_v2_candidate_spec.md` for the next window,
   labelled diagnostic-derived, with no further Jan–Oct
   fitting permitted.
3. **Cost remains a live unknown, not a rescue:** the closest
   structured cell (U1-SHORT) breaks even at ₹33.82 overall /
   ₹28.05 in its weaker half. If the user's real charges are
   ever supplied, U1-SHORT is the first cell to re-judge —
   on the recorded numbers, without re-running anything.

## Files

- Spec (frozen before scoring): `stocks_tuning_vline_frozen.md`
- Engine: `stocks_tuning_vline.py` (modes gate_v3, u1–u6, gate_u5)
- Results JSON: `stocks_tuning_vline_results.json`
- State (best direction / best cell): `stocks_tuning_vline_state.json`
- Trade dumps: `vline_U1-*`, `vline_U2-*`, `vline_U3-*`,
  `vline_U4-*`, `vline_U5a-PROBE_trades.csv`,
  `vline_U5b-SKIP_trades.csv`
- Candidate (diagnostic-derived, fresh-window only):
  `stocks_vline_v2_candidate_spec.md`

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.

---

## Line 2b — Robustness battery on the frozen v2 candidate
## (DIAGNOSTIC — everything below is diagnosis, NOT a pass)

Battery list frozen in `stocks_tuning_vline_frozen.md`
(Line 2b section) BEFORE scoring. The candidate spec
(`stocks_vline_v2_candidate_spec.md`) is **not** edited by
this battery; anything that looks better than the frozen
rule is recorded as a named observation only. All figures
provisional per 100 shares, ₹40/trade unless a cell states
another cost (R6). Engine: `stocks_tuning_vline2b.py`.

**Validation gate PASSED exactly.** The battery engine at
the frozen parameters (threshold 1.0%, window < 10:00, ANY
direction, cap 2) reproduces the published subset to the
paisa: 424 chains, 698 trades, net +₹84,671.74, Jan–May
+₹52,884.19 (272 chains), Jun–Oct +₹31,787.55 (152 chains),
October +₹16,825.42, chain win 55.0%, breadth 16/25, direct
leg 424 trades +₹93,575.31, re-entry leg 274 trades
−₹8,903.57. All battery cells below are anchored to this
reproduction.

### R1 — Threshold neighbourhood: PLATEAU, not a cliff

| Threshold | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|
| 0.75% | 746 | 1,175 | +123,874.00 | +166.05 | +75,516.44 | +48,357.56 | +34,413.24 | 17/25 |
| **1.0% (frozen)** | **424** | **698** | **+84,671.74** | **+199.70** | **+52,884.19** | **+31,787.55** | **+16,825.42** | **16/25** |
| 1.25% | 238 | 407 | +59,425.91 | +249.69 | +37,865.63 | +21,560.28 | +15,180.82 | 19/25 |
| 1.5% | 131 | 234 | +43,671.22 | +333.37 | +31,623.98 | +12,047.24 | +7,370.31 | 19/25 |

Every threshold in the neighbourhood is net-positive in
**both halves** with breadth ≥16/25. The response is a
smooth gradient, not a spike at 1.0%: lowering the threshold
adds chains and total but dilutes per-chain expectancy;
raising it does the opposite, monotonically. The frozen
1.0% is an interior point of a working region — the subset
is not balanced on a knife-edge parameter.

### R2 — Direction splits

Chain-restricted variants (frozen discard first, then
blocked-direction signals consumed without entry/cost/cap —
chain counts differ from 424 because the search path
changes; these are variant chains, not partitions):

| Variant | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| LONG-only | 182 | 305 | +33,616.07 | +24,608.71 | +9,007.36 | +2,463.11 | 15/25 |
| SHORT-only | 253 | 403 | +52,368.42 | +28,463.89 | +23,904.53 | +14,362.31 | 17/25 |

Both directions stand on their own in both halves. At trade
level inside the frozen chains the same picture holds:
LONG 299 trades +₹32,490.18 (exp +₹108.66/trade), SHORT
399 trades +₹52,181.56 (exp +₹130.78/trade).

Partition of the frozen 424 chains by the SIGN of the
pre-10:00 move:

| Side | Chains | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Mover-UP days | 203 | +25,858.86 | +127.38 | +22,684.55 | +3,174.31 | +2,403.48 | 13/25 |
| Mover-DOWN days | 221 | +58,812.88 | +266.12 | +30,199.64 | +28,613.24 | +14,421.94 | 19/25 |

The edge is materially stronger after a morning move DOWN
(2.3× the net, balanced halves, breadth 19/25). The leg
split locates the frozen rule's known weakness precisely:
on mover-down chains the direct leg is +₹58,467.45 and the
re-entry leg is ≈breakeven (+₹345.43); on mover-up chains
the direct leg is +₹35,107.86 but the re-entry leg is
−₹9,249.00 — **the entire negative re-entry leg of the
frozen rule lives in mover-up chains**, and mover-up
Jun–Oct is thin (+₹3,174.31 over 87 chains, ≈+₹36/chain).
Recorded as diagnosis; the frozen rule is unchanged.

### R3 — Concentration: survives the stress

Per-stock chain nets (top/bottom): GLENMARK +₹24,621.20,
BDL +₹15,870.19, TVSMOTOR +₹10,867.44, HINDUNILVR
+₹10,441.54, ASTRAL +₹6,635.21 … worst KALYANKJIL
−₹3,985.46, VEDL −₹2,594.49, HINDCOPPER −₹1,441.51. The
nine negative stocks sum to only ≈−₹10,380 against
≈+₹95,052 from the sixteen positive ones — the left tail
is shallow.

- **Top-3 share:** GLENMARK + BDL + TVSMOTOR = +₹51,358.83
  = **60.7%** of the net (as disclosed in the candidate
  spec).
- **Excluding the top-3 payers entirely:** total
  **+₹33,312.91**, Jan–May +₹21,263.11, Jun–Oct
  +₹12,049.80 — still positive in both halves on the
  remaining 22 stocks. Unlike the EventBook (Line 3b),
  this candidate does **not** die when its payers are
  removed.
- **Winsorised at +₹2,000/stock** (each stock's net capped
  at +₹2,000, negatives unchanged): total **+₹15,622.16**.
  Under the stricter per-half cap the halves also hold:
  Jan–May +₹13,687.15, Jun–Oct +₹13,344.26.

Month-by-month (chains / net / cumulative):

| Month | Chains | Net ₹ | Cum ₹ |
|---|---|---|---|
| Jan | 56 | −216.47 | −216.47 |
| Feb | 49 | +3,786.64 | +3,570.17 |
| Mar | 62 | +20,654.87 | +24,225.04 |
| Apr | 52 | +25,718.06 | +49,943.10 |
| May | 53 | +2,941.09 | +52,884.19 |
| Jun | 27 | +7,710.64 | +60,594.83 |
| Jul | 32 | +7,399.23 | +67,994.06 |
| Aug | 28 | +2,124.34 | +70,118.40 |
| Sep | 17 | **−2,272.08** | +67,846.32 |
| Oct | 48 | +16,825.42 | +84,671.74 |

Only two negative months, both small; **worst month =
September, −₹2,272.08** (also the thinnest month, 17
chains). April is the largest month (+₹25,718.06 ≈ 30% of
the net) — a time-concentration note, not a disqualifier:
no single month carries the result (removing April still
leaves +₹58,953.68, both halves positive).

### R4 — Time neighbourhood: one-sided sensitivity

| Window end | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| 09:45 | 160 | 278 | +10,355.89 | +11,892.33 | **−1,536.44** | +817.79 | 9/25 |
| **10:00 (frozen)** | **424** | **698** | **+84,671.74** | **+52,884.19** | **+31,787.55** | **+16,825.42** | **16/25** |
| 10:15 | 589 | 941 | +169,328.31 | +92,266.39 | +77,061.92 | +36,815.02 | 24/25 |

Measuring the pre-move at **09:45 breaks the rule**
(Jun–Oct flips negative, breadth falls to 9/25): a 30-minute
move is not yet the same information as the full pre-10:00
move. Measuring at **10:15 strengthens everything** — net
doubles, breadth 24/25, and uniquely among all variants its
re-entry leg turns positive (+₹10,642.17 on 352 trades).
The frozen 10:00 is therefore not a local peak; it sits on
a rising slope toward 10:15, and one step the other way it
degrades. **Named observation OBS-2b-1 (NOT adopted, NOT
written into the candidate spec):** the 10:15 measurement
window is the strongest single variation in this battery;
it would need its own frozen spec and its own fresh window
before it could be claimed as anything.

### R5 — Signal definition check

**The frozen rule is the ANY-direction definition.**
Confirmed from the engine: `build_chain` (mode U5b) applies
no direction filter after the discard — the next signal is
traded whatever direction `pool_pick` returns. Variant (a),
SAME-direction only (post-discard signals must match the
sign of the pre-10:00 move; others consumed):

| Variant | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| ANY (frozen) | 424 | 698 | +84,671.74 | +52,884.19 | +31,787.55 | +16,825.42 | 16/25 |
| SAME-direction | 385 | 639 | +92,923.38 | +58,622.78 | +34,300.60 | +16,885.05 | 18/25 |

The same-direction variant is modestly better on total,
expectancy (+₹241.36 vs +₹199.70/chain) and breadth, with
the same October. **Named observation OBS-2b-2 (NOT
adopted):** restricting the second signal to the pre-move's
direction does not hurt and slightly helps in-sample; the
frozen ANY-direction rule stays as frozen for its fresh
test. (Its re-entry leg is still negative, −₹9,446.15.)

For completeness, **OBS-2b-3 (NOT adopted):** the R1 0.75%
threshold totals +₹123,874.00 (breadth 17/25) — more money,
thinner expectancy (+₹166.05/chain).

### R6 — Cost sensitivity: not cost-fragile

| Cost/trade | Total ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ |
|---|---|---|---|---|
| ₹25 | +95,141.74 | +59,769.19 | +35,372.55 | +17,980.42 |
| ₹40 (frozen) | +84,671.74 | +52,884.19 | +31,787.55 | +16,825.42 |
| ₹60 | +70,711.74 | +43,704.19 | +27,007.55 | +15,285.42 |

**Breakeven flat cost: ₹161.31/trade** (Jan–May ₹155.22,
Jun–Oct ₹173.00). Unlike the V3/U1-SHORT line, whose best
cell breaks even at ₹33.82, this candidate's in-sample
result does not hinge on the unknown real broker charges:
it survives a ₹60 cost with both halves comfortably
positive.

### Line 2b verdict — ROBUST (plateau, not cliff-edge),
### with two recorded soft spots

Evidence for robust: the 1.0% threshold is an interior
point of a both-halves-positive, breadth-≥16 neighbourhood
(R1); both directions and both move-signs are positive,
with the weaker side still net-positive in both halves
(R2); the result survives removal of its top-3 payers and
a harsh +₹2,000/stock winsorisation (R3); only 2 of 10
months are negative and both are small (R3); and the
breakeven cost of ₹161/trade is 4× the frozen assumption
(R6). Nothing in this battery shows the frozen point to be
a fitted spike.

Soft spots, recorded honestly: (1) the **mover-up flank**
— Jun–Oct mover-up chains earn only ≈+₹36/chain and carry
the rule's entire negative re-entry leg; if the candidate
ever weakens on fresh data, this is the flank to inspect
first. (2) **Measurement-time is one-sided sensitive** —
09:45 breaks it, so the rule genuinely needs the move to
be measured over the full morning window it was frozen
with; 10:15 is stronger still (OBS-2b-1).

**No pass is claimed by this battery.** The candidate
remains exactly as frozen in
`stocks_vline_v2_candidate_spec.md` — unedited — and still
earns only its fresh-window test. OBS-2b-1/2/3 are named
observations for a possible future line, nothing more.

## Line 2b files

- Battery spec (frozen before scoring):
  `stocks_tuning_vline_frozen.md`, Line 2b section
- Engine: `stocks_tuning_vline2b.py` (modes validate, all)
- Results JSON: `stocks_tuning_vline2b_results.json`
- Trade dumps: `vline2b_FROZEN_trades.csv`,
  `vline2b_R1-T075_trades.csv`, `vline2b_R1-T125_trades.csv`,
  `vline2b_R1-T150_trades.csv`, `vline2b_R2-LONG_trades.csv`,
  `vline2b_R2-SHORT_trades.csv`, `vline2b_R4-W0945_trades.csv`,
  `vline2b_R4-W1015_trades.csv`,
  `vline2b_R5a-SAMEDIR_trades.csv`

Stage results only. Nothing here is adopted; nothing here is
a live-trading instruction.
