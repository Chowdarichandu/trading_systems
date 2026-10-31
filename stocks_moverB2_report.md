# Stocks EQUITY — MOVER-B2 Tuning (MOVER-B → its next version)

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money ₹0.**
**Every rupee figure is provisional per 100 shares. Net = gross −
₹40/trade flat. Window Jan–Oct 2026 (October = 1–28 Oct).**

Families frozen BEFORE scoring in `stocks_moverB2_frozen.md`
(B2-1 … B2-6, in order). Engine: `stocks_moverB2.py`. Results
JSON: `stocks_moverB2_results.json`. Trade dumps:
`moverB2_<FAMILY>_trades.csv`. Primary score = POOLED 50; home /
ext splits reported for every family.

**IMPROVER GATE (pooled):** net > +₹464,617.03 (base MOVER-B) AND
both halves positive AND breadth ≥ 45/50 AND max drawdown no worse
than −₹25,000 (daily-aggregated, risk-card method) AND no losing
month pooled. A family passing all five legs is frozen as the B2
candidate for a FRESH window — November's frozen A/B shadows are
not touched by this line.

**BASE MOVER-B recap:** pre-move |close of last bar before 10:15 ÷
day open − 1| ≥ 1.0% → discard the day's first V5-stream signal,
trade the next (any direction), one re-entry (cap 2), T125 exits
(+1.25% / −0.5%, stop-first, 15:10 square-off).

---
## Anchor validation — **ALL PASS to the paisa**

| Book | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Home-B | 589 | 941 | +169,328.31 | +92,266.39 | +77,061.92 | +36,815.02 | 24/25 |
| Ext-B | 328 | 481 | +295,288.72 | +151,540.58 | +143,748.14 | +81,933.52 | 25/25 |
| **Pooled-B (base)** | **917** | **1,422** | **+464,617.03** | **+243,806.97** | **+220,810.06** | **+118,748.54** | **49/50** |

Pooled max drawdown by the risk-card method reproduces exactly:
**−₹17,471.45**. Pooled top-3 share 29.0%, expectancy +₹506.67/
chain, no losing month (Jan +20,654.74 · Feb +18,593.73 · Mar
+113,901.46 · Apr +56,999.06 · May +33,657.98 · Jun +49,709.85 ·
Jul +9,747.90 · Aug +12,887.79 · Sep +29,715.98 · Oct
+118,748.54). Base leg split (context for B2-1): on ext, the
re-entry leg is −₹16,671.52 while the direct leg carries the book;
pooled re-entry leg is only −₹6,029.35 on 505 trades.

Every B2 number below is anchored to this reproduction.

---
## B2-1 — DIRECT-ONLY (chain cap 1) — **PASSES THE IMPROVER GATE**

The re-entry leg is dropped entirely; every chain is its direct
trade only (917 chains = 917 trades, vs base 1,422 trades).

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 589 | 589 | +158,686.14 | +269.42 | +99,412.92 | +59,273.22 | +30,413.67 | 23/25 | 45.5% | −6,128.99 |
| Ext | 328 | 328 | +311,960.24 | +951.10 | +184,656.20 | +127,304.04 | +46,837.89 | 25/25 | 43.9% | −12,356.57 |
| **Pooled** | **917** | **917** | **+470,646.38** | **+513.25** | **+284,069.12** | **+186,577.26** | **+77,251.56** | **48/50** | 30.7% | **−9,484.99** |

Pooled months (₹): Jan +25,000.64 · Feb +24,189.07 · Mar
+125,219.75 · Apr +58,654.81 · May +51,004.85 · Jun +60,634.51 ·
Jul +18,995.69 · Aug +7,897.03 · Sep +21,798.47 · Oct +77,251.56
— **no losing month**.

Gate legs: net +₹470,646.38 > base +₹464,617.03 ✓ (the delta is
exactly the pooled re-entry leg's −₹6,029.35, removed) · both
halves positive ✓ · breadth 48/50 ≥ 45 ✓ · max DD −₹9,484.99,
*better* than base −₹17,471.45 and inside −₹25,000 ✓ · no losing
month ✓. **GATE: PASS.**

Reading: direct-only improves the total and halves the drawdown,
and Jan–May strengthens sharply (+₹284,069.12 vs base
+₹243,806.97), but Jun–Oct and October give money back versus
base (+₹186,577.26 vs +₹220,810.06; Oct +₹77,251.56 vs
+₹118,748.54) — the re-entry leg was a drag on the year and a
contributor in the autumn. Home alone falls slightly vs base-B
(+₹158,686.14 vs +₹169,328.31, breadth 23/25); ext alone rises
(+₹311,960.24 vs +₹295,288.72).

**Verdict B2-1: PASS — first B2 candidate-eligible family
(candidate is decided after B2-6; highest pooled net among
passing families wins).**

---
## B2-2 — SAME-DIRECTION (cap 2) — **PASSES THE IMPROVER GATE**

Post-discard signals must match the pre-10:15 move's sign;
non-matching signals are consumed without entry, cost or cap.
56 base chains disappear entirely (their post-discard signals
never align) — 861 chains remain.

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 552 | 880 | +188,924.33 | +342.25 | +102,723.52 | +86,200.81 | +37,278.71 | 24/25 | 44.8% | −7,220.54 |
| Ext | 309 | 451 | +313,068.31 | +1,013.17 | +149,162.04 | +163,906.27 | +100,309.75 | 25/25 | 49.0% | −22,656.60 |
| **Pooled** | **861** | **1,331** | **+501,992.64** | **+583.03** | **+251,885.56** | **+250,107.08** | **+137,588.46** | **49/50** | 30.5% | **−19,860.59** |

Pooled months (₹): Jan +25,372.22 · Feb +17,878.91 · Mar
+115,090.35 · Apr +61,501.27 · May +32,042.81 · Jun +53,509.10 ·
Jul +13,811.17 · Aug +14,989.68 · Sep +30,208.67 · Oct
+137,588.46 — **no losing month pooled** (ext alone has one
small losing month, Jul −₹1,761.62; home covers it).

Gate legs: net +₹501,992.64 > base ✓ (+₹37,375.61 over base) ·
both halves positive and near-balanced ✓ · breadth 49/50 ✓ ·
max DD −₹19,860.59 inside −₹25,000 ✓ (worse than base's
−₹17,471.45 — the same-direction book is lumpier day-to-day) ·
no losing month ✓. **GATE: PASS.**

Reading: the same-direction restriction — a modest help at the
10:00 measurement on both universes (Line 5 M3 / OBS-5-4) — is a
large help at 10:15: expectancy per chain rises +15.1% pooled
(+₹583.03 vs +₹506.67) and both universes improve. Its re-entry
leg, however, is still negative pooled (−₹9,945.16) — which is
exactly what B2-3 removes.

**Verdict B2-2: PASS.**

---
## B2-3 — COMBINED (cap 1 + same-direction) — **PASSES THE IMPROVER GATE**

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 552 | 552 | +180,038.59 | +326.16 | +111,904.10 | +68,134.49 | +30,877.36 | 24/25 | 44.3% | −5,939.62 |
| Ext | 309 | 309 | +331,899.21 | +1,074.11 | +186,251.34 | +145,647.87 | +64,543.52 | 25/25 | 46.8% | −13,916.07 |
| **Pooled** | **861** | **861** | **+511,937.80** | **+594.59** | **+298,155.44** | **+213,782.36** | **+95,420.88** | **49/50** | 32.2% | **−9,234.94** |

Pooled months (₹): Jan +30,023.44 · Feb +26,845.44 · Mar
+126,273.62 · Apr +64,360.08 · May +50,652.86 · Jun +61,898.16 ·
Jul +18,842.46 · Aug +12,785.92 · Sep +24,834.94 · Oct +95,420.88
— **no losing month** (none in either universe separately
either).

Gate legs: net +₹511,937.80 > base ✓ (+₹47,320.77 over base,
+₹9,945.16 over B2-2 — exactly B2-2's negative re-entry leg,
removed) · both halves positive ✓ · breadth 49/50 ✓ · max DD
−₹9,234.94, the shallowest of any book so far ✓ · no losing
month ✓. **GATE: PASS — the current B2 leader.**

Reading: the two restrictions compose cleanly. Same-direction
selects better chains; direct-only deletes the leg that leaks
in almost every cell of this programme. Internal consistency
check: B2-3's total equals B2-2's direct leg to the paisa
(+₹511,937.80), as it must. The trade-off versus B2-2 is the
same shape as B2-1's: Jun–Oct and October are lower than the
cap-2 same-direction book (the re-entry leg earns in the
autumn) while Jan–May is much stronger (+₹298,155.44, the best
first half of any family so far).

**Verdict B2-3: PASS — highest pooled net among passing
families to date.**

---
## B2-4 — MEASUREMENT MICRO-STEPS — **BOTH PASS; 10:15 IS NOT THE PEAK**

### B2-4a — measurement 10:20 — **PASSES THE IMPROVER GATE**

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 649 | 1,021 | +201,197.04 | +310.01 | +105,871.34 | +95,325.70 | +42,428.99 | 24/25 | 50.1% | −6,710.97 |
| Ext | 374 | 553 | +361,317.74 | +966.09 | +203,067.95 | +158,249.79 | +64,818.75 | 25/25 | 47.6% | −18,527.18 |
| **Pooled** | **1,023** | **1,574** | **+562,514.78** | **+549.87** | **+308,939.29** | **+253,575.49** | **+107,247.74** | **49/50** | 32.4% | **−15,957.42** |

Pooled months (₹): Jan +39,183.36 · Feb +22,076.57 · Mar
+123,638.86 · Apr +89,888.28 · May +34,152.22 · Jun +78,794.38 ·
Jul +20,275.49 · Aug +21,852.90 · Sep +25,404.98 · Oct
+107,247.74 — no losing month. Gate legs all ✓ (net
+₹562,514.78, +₹97,897.75 over base; max DD −₹15,957.42 also
better than base). **GATE: PASS.**

### B2-4b — measurement 10:30 — **PASSES THE IMPROVER GATE, BY A LOT**

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 743 | 1,160 | +270,069.11 | +363.48 | +161,134.69 | +108,934.42 | +46,285.36 | 24/25 | 47.7% | −6,255.42 |
| Ext | 469 | 675 | +542,135.75 | +1,155.94 | +287,326.81 | +254,808.94 | +97,882.49 | 24/25 | 49.5% | −14,252.94 |
| **Pooled** | **1,212** | **1,835** | **+812,204.86** | **+670.14** | **+448,461.50** | **+363,743.36** | **+144,167.85** | **48/50** | 34.0% | **−18,493.11** |

Pooled months (₹): Jan +74,526.64 · Feb +50,328.52 · Mar
+174,633.57 · Apr +99,112.98 · May +49,859.79 · Jun +104,933.64 ·
Jul +50,068.85 · Aug +22,901.63 · Sep +41,671.39 · Oct
+144,167.85 — **no losing month; the weakest month (Aug
+₹22,901.63) is stronger than base B's weakest.** Gate legs all
✓ (net +₹812,204.86 = base + ₹347,587.83, +74.8%; both halves
roughly double base; breadth 48/50; max DD −₹18,493.11 inside
−₹25,000). **GATE: PASS — the runaway B2 leader, and the base
configuration for B2-6.**

Reading: the measurement slope that Line 2b found between 09:45
(broken) → 10:00 → 10:15 keeps rising through 10:20 and 10:30.
Each later measurement admits more qualifying stock-days (917 →
1,023 → 1,212 chains) and they are *better*, not diluted —
expectancy per chain rises at every step (+₹506.67 → +₹549.87 →
+₹670.14). Waiting for the morning move to declare itself more
fully before discarding the first signal is the single strongest
lever found in this programme. Honest caveat: this micro-step
family was three points on one slope (10:15/10:20/10:30) scored
on the same in-sample window; the frozen list did not include
10:45 or 11:00, and nothing beyond 10:30 may be claimed from
this line. The peak, if there is one, is at or beyond 10:30 —
untested here by design.

**Verdict B2-4: PASS (both cells); B2-4b is the best of
B2-1..B2-5.**

---
## B2-5 — THRESHOLD (0.75% / 1.25% at 10:15) — **BOTH FAIL THE GATE**

### B2-5a — threshold 0.75% — FAILS on drawdown alone

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 1,013 | 1,521 | +151,494.76 | +149.55 | +82,035.23 | +69,459.53 | +26,468.61 | 23/25 | 43.0% | −13,179.10 |
| Ext | 650 | 912 | +536,209.86 | +824.94 | +337,100.77 | +199,109.09 | +90,439.65 | 25/25 | 52.5% | −43,820.57 |
| **Pooled** | **1,663** | **2,433** | **+687,704.62** | **+413.53** | **+419,136.00** | **+268,568.62** | **+116,908.26** | **48/50** | 40.9% | **−37,391.86** |

Pooled months: no losing month (Jul is a scratch +₹1,077.29;
ext alone loses May −₹271.95 and Jul −₹5,379.65). Gate legs:
net ✓ (+₹687,704.62 > base — the second-highest net of the
line) · halves ✓ · breadth ✓ · **max DD −₹37,391.86 worse than
−₹25,000 ✗** · months ✓. **GATE: FAIL** — diluting the
qualification to 0.75% buys total at the cost of expectancy
(+₹413.53/chain) and a drawdown more than double base B's; the
gate's risk leg exists precisely for this cell.

### B2-5b — threshold 1.25% — FAILS on net and on a losing month

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 347 | 580 | +128,915.35 | +371.51 | +74,032.32 | +54,883.03 | +39,160.69 | 24/25 | 54.4% | −5,949.32 |
| Ext | 168 | 270 | +219,543.63 | +1,306.81 | +105,471.98 | +114,071.65 | +79,931.09 | 24/25 | 61.2% | −16,740.10 |
| **Pooled** | **515** | **850** | **+348,458.98** | **+676.62** | **+179,504.30** | **+168,954.68** | **+119,091.78** | **48/50** | 42.1% | **−19,285.57** |

Pooled months (₹): Jan +25,821.10 · Feb +7,651.02 · Mar
+83,816.67 · Apr +46,440.00 · May +15,775.51 · Jun +37,308.91 ·
**Jul −6,377.76** · Aug +10,114.40 · Sep +8,817.35 · Oct
+119,091.78. Gate legs: **net +₹348,458.98 < base ✗** · halves
✓ · breadth ✓ · DD ✓ · **losing month (Jul) ✗**. **GATE:
FAIL.** Per-chain expectancy is the line's second-highest
(+₹676.62) but the rule starves (515 chains) — consistent with
Line 5 OBS-5-3: on this universe the usable band is
0.75–1.0%, and at the frozen 1.0% the total peaks.

**Verdict B2-5: FAIL (both cells, on different legs) — the
frozen 1.0% threshold stands.**

---
## B2-6 — EXIT VARIANTS on the best of B2-1..B2-5 (B2-4b, 10:30)

Best of B2-1..B2-5 by pooled net = **B2-4b** (+₹812,204.86).
Both cells rebuild the 10:30 configuration with a changed exit;
chains re-form (1212 chains in both, fewer trades — wider
targets/stops resolve later and restart the search later).

### B2-6a — target +1.5% / stop −0.5% — FAILS on drawdown

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 743 | 1,101 | +261,652.29 | +352.16 | +176,820.98 | +84,831.31 | +43,059.10 | 24/25 | 43.1% | −8,177.58 |
| Ext | 469 | 632 | +481,838.95 | +1,027.38 | +281,512.24 | +200,326.71 | +69,330.85 | 24/25 | 48.4% | −24,118.30 |
| **Pooled** | **1,212** | **1,733** | **+743,491.24** | **+613.44** | **+458,333.22** | **+285,158.02** | **+112,389.95** | **48/50** | 33.7% | **−28,603.98** |

No losing month pooled. Gate legs: net ✓ vs base B but BELOW
its own base configuration (−₹68,713.62 vs B2-4b) · halves ✓ ·
breadth ✓ · **max DD −₹28,603.98 worse than −₹25,000 ✗** ·
months ✓. **GATE: FAIL.** The wider target's extra room is paid
for in Jun–Oct (+₹285,158.02 vs +₹363,743.36) and in drawdown.

### B2-6b — target +1.25% / stop −0.65% — **PASSES THE GATE, but below B2-4b**

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Home | 743 | 1,109 | +279,389.97 | +376.03 | +170,477.82 | +108,912.15 | +51,007.02 | 24/25 | 45.9% | −5,570.00 |
| Ext | 469 | 639 | +496,206.30 | +1,058.01 | +264,039.99 | +232,166.31 | +84,817.28 | 25/25 | 44.5% | −15,243.96 |
| **Pooled** | **1,212** | **1,748** | **+775,596.27** | **+639.93** | **+434,517.81** | **+341,078.46** | **+135,824.30** | **49/50** | 30.6% | **−20,604.15** |

Pooled months (₹): Jan +63,021.75 · Feb +44,336.28 · Mar
+166,159.71 · Apr +107,193.68 · May +53,806.39 · Jun +91,991.73 ·
Jul +53,991.09 · Aug +21,733.24 · Sep +37,538.10 · Oct
+135,824.30 — no losing month. Gate legs all ✓. **GATE: PASS**
— but at +₹775,596.27 it earns *less* than the unmodified
B2-4b (+₹812,204.86, −₹36,608.59): the wider stop rescues some
trades and taxes the rest, net negative. Recorded as a passing
alternate, not the candidate.

**Verdict B2-6: neither exit variant improves on B2-4b's frozen
T125 exits (+1.25% / −0.5%). The exit dimension, at the 10:30
measurement, prefers the original target/stop — the improvement
in B2 lives in the measurement time, not the exit.**

---
## Line summary — MOVER-B2

| Family | Configuration | Pooled net ₹ | Δ vs base B | Halves (JM / JO) ₹ | Breadth | Max DD ₹ | Losing months | Gate |
|---|---|---|---|---|---|---|---|---|
| Base B | 10:15, 1.0%, cap 2, ANY, T125 | +464,617.03 | — | +243,806.97 / +220,810.06 | 49/50 | −17,471.45 | none | (base) |
| B2-1 | direct-only | +470,646.38 | +6,029.35 | +284,069.12 / +186,577.26 | 48/50 | −9,484.99 | none | **PASS** |
| B2-2 | same-direction | +501,992.64 | +37,375.61 | +251,885.56 / +250,107.08 | 49/50 | −19,860.59 | none | **PASS** |
| B2-3 | cap 1 + same-dir | +511,937.80 | +47,320.77 | +298,155.44 / +213,782.36 | 49/50 | −9,234.94 | none | **PASS** |
| B2-4a | measure 10:20 | +562,514.78 | +97,897.75 | +308,939.29 / +253,575.49 | 49/50 | −15,957.42 | none | **PASS** |
| **B2-4b** | **measure 10:30** | **+812,204.86** | **+347,587.83** | **+448,461.50 / +363,743.36** | **48/50** | **−18,493.11** | **none** | **PASS — CANDIDATE** |
| B2-5a | threshold 0.75% | +687,704.62 | +223,087.59 | +419,136.00 / +268,568.62 | 48/50 | −37,391.86 | none | FAIL (drawdown) |
| B2-5b | threshold 1.25% | +348,458.98 | −116,158.05 | +179,504.30 / +168,954.68 | 48/50 | −19,285.57 | Jul | FAIL (net, month) |
| B2-6a | 10:30 + target 1.5% | +743,491.24 | +278,874.21 | +458,333.22 / +285,158.02 | 48/50 | −28,603.98 | none | FAIL (drawdown) |
| B2-6b | 10:30 + stop 0.65% | +775,596.27 | +310,979.24 | +434,517.81 / +341,078.46 | 49/50 | −20,604.15 | none | **PASS** (alternate) |

**B2 CANDIDATE = the B2-4b configuration**, frozen in
`stocks_moverB2_candidate_spec.md`: measurement at **10:30**,
everything else exactly as MOVER-B (1.0% pre-move threshold, any
direction, chain cap 2, T125 exits). In-sample: 1,212 chains,
1,835 trades, **+₹812,204.86** provisional per 100 shares (+74.8%
over base B), halves +₹448,461.50 / +₹363,743.36, October
+₹144,167.85, chain win 62.2%, expectancy +₹670.14/chain,
breadth 48/50 (only SBIN −₹48.95 and NHPC −₹908.48 negative),
top-3 share 34.0% (MARUTI +₹130,810.75 the largest single
contributor, 16.1%), max drawdown −₹18,493.11, no losing month
(weakest: Aug +₹22,901.63; top-2 months Mar + Oct = 39.3% of
the total).

Disclosures that travel with the candidate:
1. This is IN-SAMPLE tuning on the same Jan–Oct window that
   produced MOVER-B. The 10:15 → 10:20 → 10:30 slope was scored
   at three points of one pre-frozen family; the candidate
   earns only a FRESH window, exactly as MOVER-B did.
2. The measurement slope is untested beyond 10:30 — this
   line's frozen list stopped there. Whether 10:45/11:00 is
   higher still is unknown, and no later point may be claimed
   from this data without its own frozen family and, ideally,
   fresh data.
3. The restrictions that helped at 10:15 (direct-only,
   same-direction) were NOT re-tested on top of 10:30 within
   this frozen list — B2-6 spent its cells on exits. The
   candidate is the plain 10:30 configuration, not a stack.
4. November's frozen A/B shadows (home + ext) are untouched
   and proceed as scheduled; B2's fresh window is the next
   window after theirs (December), under the judging rule in
   the candidate spec.

Files: this report; frozen spec `stocks_moverB2_frozen.md`;
candidate `stocks_moverB2_candidate_spec.md`; engine
`stocks_moverB2.py`; results `stocks_moverB2_results.json`;
dumps `moverB2_BASE_trades.csv`, `moverB2_B2-1_trades.csv`, …,
`moverB2_B2-6b_trades.csv`.

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.
