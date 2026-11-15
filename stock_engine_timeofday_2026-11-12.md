# Stock Engine — TIME-OF-DAY PROFITABILITY MAP (2026-11-12)

Owner order 2026-11-12 07:10 IST: *"at which time interval — first half or second half of the day — entry remains profitable… I don't want to lose this, that's the main motto."* Paper only, real money ₹0. Basis: provisional per 100 shares, ₹40/trade (nets as stored in the source books). Code: `stock_engine_timeofday_2026-11-12.py`; full bucket table: `stock_engine_timeofday_2026-11-12.csv` (210 rows); verdicts + chosen windows: `stock_engine_timeofday_2026-11-12_verdicts.json`.

## The answer first

**The whole SarvaRitu book is a first-half book — in fact, almost everything enters before 10:30.** On the 25-universe Jan–Oct history (2025 and 2026) and at 1,081 width (Oct 1 – Nov 11 2026), the INV sleeves and the entire reaction family have **zero entries after 10:30** — that is a construction fact, not a market fact: the INV pool population is filtered to entries before 10:30, and the reaction family enters at the 09:15 open / 09:35. Only F4 (and its causal variant) ever enters after 10:30, via chained second legs — and **its second-half entries bleed**: frozen F4 second half at width = 52 trades · **−₹20,176.73** (B3 −₹11,247.89, B4 −₹8,965.85); on the 25-history the second half is nearly empty (4 trades in 2026).

Per component, where the money is (25-universe history):

| Component | Earning bucket(s) 2026 | Bleeding / dead zones |
|---|---|---|
| N4-V3 | B1 only (its only bucket): 35 tr · +₹25,271.54 · ex3 +₹6,638.41 (2025: +₹4,671.64, ex3 −₹8,414.85 — headline carried by top names in 2025) | no entries exist after 10:30 |
| P2F | B1: 32 tr · +₹19,416.63 · ex3 +₹5,543.27 (2025 +₹14,430.12 · ex3 +₹2,013.94 — the cleanest two-year bucket in the book) | — |
| P2F-R2 | B1: 32 tr · +₹15,149.33 · ex3 +₹5,750.96 (2025: −₹4,988.80 — a 2026-regime bucket) | — |
| R2-LOWBAND | B1 SPARSE (3 tr 2026) — no verdict | — |
| F4 (frozen) | B1: 296 tr · +₹69,348.45 · ex3 +₹19,627.02; B2: 46 tr · +₹24,973.36 · ex3 +₹3,699.53 (2025: B1 −₹507.00, B2 +₹529.14 — thin in 2025) | B3/B4 sparse on 25; at width B3/B4 bleed (−₹11,247.89 / −₹8,965.85) |
| **F4-C** | B1 2026: 355 tr · +₹34,060.88 but **ex3 −₹2,826.74 → NOT profitable** (top-3-carried); **B2: 49 tr · +₹21,694.63 · ex3 +₹2,846.49 → PROFITABLE** (2025 B2 −₹4,528.07, above the −₹5,000 deep-negative line) | first half overall REJECTED-2025 (2025 FH −₹18,721.98 · ex3 −₹23,820.34) |
| INV-LONG (frozen) | B1: 133 tr · +₹44,062.10 · ex3 +₹9,830.00 (2025 +₹12,605.23) | no entries after 10:30 exist |
| **INV-LONG-C** | **B1: 165 tr · +₹41,981.25 · ex3 +₹3,179.46 → PROFITABLE** (2025 −₹1,415.04, not deep) | no entries after 10:30 exist |
| INV-ABOVE (frozen) | B1 2026: +₹3,349.21 but ex3 −₹746.48 → NOT profitable | — |
| **INV-ABOVE-C** | B1 2026: 47 tr · **−₹149.17 · ex3 −₹2,638.93 → NOT profitable** (2025 −₹8,287.73) | **no profitable bucket anywhere → sits out the invention** |

**First half vs second half (the owner's framing):** first half is profitable for N4-V3, P2F, P2F-R2, F4, INV-LONG, INV-LONG-C on 2026 (verdict table); second half has no verdict anywhere — it is empty (INV/reaction) or sparse-and-bleeding (F4 at width). There is no second-half strategy hiding in this book; the only genuine *intra-day timing* signal in the whole map is **F4-C: its 09:15–10:30 entries are top-3-carried (ex3 negative) while its 10:30–12:00 entries are the profitable ones** — on the 25-history. One honest divergence, flagged before the screen judges it: at 1,081 width over Oct–Nov, F4-C's B2 bucket is **negative** (608 tr · −₹21,839.19 · ex3 −₹53,939.69) even though it is the profitable bucket on the 25-history. The windows below are chosen by the pre-registered rule (25-universe 2026 history); the wide Stage-1 screen is where that choice is judged.

## Method

Buckets by entry time: B1 [09:15–10:30) · B2 [10:30–12:00) · B3 [12:00–13:30) · B4 [13:30–15:10]; halves: FIRST = entry ≤ 12:00, SECOND = entry > 12:00 (a 12:00-exact entry sits in B3 by bucket edges but FIRST by the ≤ rule — the owner's definitions, both reported as specified). Per bucket: trades, net, win rate, expectancy, ex-top-3 (three best stocks by net inside the bucket removed). Sources: (a) 25-universe Jan–Oct 2025 + 2026 — chain comps from the causal3 gate's leg-3 canonical CSVs (post-law, re-summed at write); reaction family rebuilt with the gate's own `build_live4_detailed` on the FULLHIST machinery + v2 law, **cross-checked trade-for-trade against the production logger's `build_book`** (equal after the shared Jan–Oct day-set filter; both builders spill late-Oct events into November reaction days, excluded from a Jan–Oct map on both sides). (b) 1,081-wide Oct 1 – Nov 11 2026 — frozen twins from the Sarvasetu v2 pool CSV, causal variants from the causal3 variant-rows CSV (both post-law).

**Verdict rule (pre-registered):** PROFITABLE iff 2026 trades ≥ 15 AND 2026 net > 0 AND 2026 ex-top-3 > 0 AND NOT deeply-negative-2025 (2025 trades ≥ 15 AND 2025 net < −₹5,000 AND 2025 ex-top-3 < 0). 2026 trades < 15 → SPARSE, no verdict. 2026-positive but deeply-negative-2025 → REJECTED-2025.

## (a) 25-universe history — bucket detail

### 2026 (Jan–Oct)

| Comp | B1 09:15–10:30 | B2 10:30–12:00 | B3 12:00–13:30 | B4 13:30–15:10 | FIRST | SECOND |
|---|---|---|---|---|---|---|
| N4-V3 | 35 · +25,271.54 · ex3 +6,638.41 | 0 | 0 | 0 | = B1 | 0 |
| P2F | 32 · +19,416.63 · ex3 +5,543.27 | 0 | 0 | 0 | = B1 | 0 |
| P2F-R2 | 32 · +15,149.33 · ex3 +5,750.96 | 0 | 0 | 0 | = B1 | 0 |
| R2-LOWBAND | 3 · +1,283.36 (SPARSE) | 0 | 0 | 0 | = B1 | 0 |
| F4 | 296 · +69,348.45 · ex3 +19,627.02 | 46 · +24,973.36 · ex3 +3,699.53 | 3 · +4,388.50 (SPARSE) | 2 · +25.00 (SPARSE) | 343 · +94,381.81 · ex3 +24,756.54 | 4 · +4,353.50 (SPARSE) |
| F4-C | 355 · +34,060.88 · ex3 **−2,826.74** | 49 · +21,694.63 · ex3 +2,846.49 | 0 | 0 | 404 · +55,755.51 · ex3 +362.81 | 0 |
| INV-LONG | 133 · +44,062.10 · ex3 +9,830.00 | 0 | 0 | 0 | = B1 | 0 |
| INV-LONG-C | 165 · +41,981.25 · ex3 +3,179.46 | 0 | 0 | 0 | = B1 | 0 |
| INV-ABOVE | 36 · +3,349.21 · ex3 −746.48 | 0 | 0 | 0 | = B1 | 0 |
| INV-ABOVE-C | 47 · −149.17 · ex3 −2,638.93 | 0 | 0 | 0 | = B1 | 0 |

### 2025 (Jan–Oct) — the guard year

| Comp | B1 | B2 | FIRST HALF |
|---|---|---|---|
| N4-V3 | 43 · +4,671.64 · ex3 −8,414.85 | 0 | = B1 |
| P2F | 22 · +14,430.12 · ex3 +2,013.94 | 0 | = B1 |
| P2F-R2 | 21 · −4,988.80 · ex3 −6,475.95 | 0 | = B1 |
| R2-LOWBAND | 2 · −1,632.25 (SPARSE) | 0 | = B1 |
| F4 | 216 · −507.00 · ex3 −9,015.55 | 28 · +529.14 · ex3 −2,874.86 | 244 · +22.14 · ex3 −9,859.86 |
| F4-C | 245 · −14,193.91 · ex3 −20,454.59 | 28 · −4,528.07 · ex3 −6,727.25 | 273 · −18,721.98 · ex3 −23,820.34 |
| INV-LONG | 220 · +12,605.23 · ex3 −2,495.54 | 0 | = B1 |
| INV-LONG-C | 257 · −1,415.04 · ex3 −12,022.81 | 0 | = B1 |
| INV-ABOVE | 140 · +5,639.90 · ex3 −5,805.42 | 0 | = B1 |
| INV-ABOVE-C | 201 · −8,287.73 · ex3 −18,510.12 | 0 | = B1 |

## (b) 1,081-wide window (Oct 1 – Nov 11 2026, 27 days) — bucket detail

| Comp | B1 | B2 | B3 | B4 | SECOND HALF |
|---|---|---|---|---|---|
| N4-V3 | 24 · −1,978.86 · ex3 −11,570.31 | 0 | 0 | 0 | 0 |
| P2F | 18 · +1,372.38 · ex3 −5,708.74 | 0 | 0 | 0 | 0 |
| P2F-R2 | 15 · +3,140.28 · ex3 −4,300.84 | 0 | 0 | 0 | 0 |
| R2-LOWBAND | 5 · +841.21 · ex3 −651.85 | 0 | 0 | 0 | 0 |
| F4 | 2,584 · +574,374.31 · ex3 +453,944.81 | 598 · +92,224.26 · ex3 +43,854.01 | 36 · **−11,247.89** | 18 · **−8,965.85** | 52 · **−20,176.73** |
| F4-C | 3,109 · +446,764.68 · ex3 +293,135.93 | 608 · **−21,839.19** · ex3 −53,939.69 | 13 · +4,929.56 (ex3 −2,437.09) | 15 · −6,685.88 | 27 · −1,887.47 |
| INV-LONG | 4,116 · +361,328.17 · ex3 +198,131.42 | 0 | 0 | 0 | 0 |
| INV-LONG-C | 5,618 · +3,291.82 · ex3 **−148,421.43** | 0 | 0 | 0 | 0 |
| INV-ABOVE | 2,289 · +484,876.65 · ex3 +249,679.90 | 0 | 0 | 0 | 0 |
| INV-ABOVE-C | 2,760 · +350,274.29 · ex3 +115,196.29 | 0 | 0 | 0 | 0 |

## Session windows chosen for the invention (pre-registered rule — the causal variant's OWN 2026 25-history map)

- **F4-C → [10:30–12:00]** (its only PROFITABLE bucket; its B1 is top-3-carried)
- **INV-LONG-C → [09:15–10:30]** (its only bucket, PROFITABLE)
- **INV-ABOVE-C → none** (no PROFITABLE bucket — sits out S1/S2 entirely, per the rule)
