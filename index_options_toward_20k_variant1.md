# Variant 1 — SINGLE unified index OPTIONS system, October 2026

**Paper only. No orders. No stocks. Real money made = ₹0 — no live trades were placed.**
**No adoption claim on October alone.** November 2026 paper (from Monday 2026-11-02) remains validation.

## Frozen definition (as tasked)

- **Systems pooled, then deduplicated:** (lA) v2 + V5 v2 + Tuned Skill V3 (CE no-block) + Volrix intraday (b) at −1.0%.
- **Counting: UNIQUE-ONCE.** Key = (date, index, direction CE/PE). Each key counted **once**, at the **earliest entry time** among the systems on that key. Later signals on the same key are overlaps, not extra trades.
- **NOT exclusive-only, NOT literal sum.** A key signalled by two or three systems is still one trade; the literal sum of all system legs is not the Variant 1 total.
- **Overlay (uniform, from source files):** stop = entry premium − 50 points, target = entry premium + 90 points, checked per 5-min bar including the entry bar, square-off 15:10; net per 1 lot = (exit − entry) × lot − ₹220 cost. Lot: Nifty 65, Bank Nifty 30.
- **Window:** 1–28 October 2026 = 18 trading days = 3.6 weeks (18 ÷ 5).
- **Full-target %** = share of trades exiting at the +90 target only. Square-off greens are NOT full targets.
- **Excluded:** Skill V3 Bank 28 Oct CE (54000, 3 Nov expiry) — premium_status NOT_COMPUTED (Bank post-October chain gap). If it were counted, Bank would have 19 unique trades, not 18. Volrix (a) 5-session hold and (c-raw) are NOT included — only (b) intraday at −1.0%.

## Verification from the CSVs (not invented)

Legs fed in: **44** = 7 (lA) v2 + 7 V5 v2 + 28 Skill V3 computed + 2 Volrix (b).

| System | Nifty legs / net | Bank legs / net | Total net |
|---|---|---|---|
| (lA) v2 | 3 / +₹6,678.50 | 4 / +₹1,520.00 | +₹8,198.50 |
| V5 v2 | 3 / +₹825.25 | 4 / +₹9,920.00 | +₹10,745.25 |
| Tuned Skill V3 (computed only) | 14 / +₹9,874.50 | 14 / +₹1,120.00 | +₹10,994.50 |
| Volrix intraday (b) −1.0% | 1 / +₹5,630.00 | 1 / +₹2,480.00 | +₹8,110.00 |
| **Literal sum (double-counted)** | | | **+₹38,048.25** |

- Skill v2 (S1) base rows in the premium CSV were **not** fed separately: they are the same Skill system as V3, and every base key is already covered by V3.
- Unique keys: **34**. Duplicate legs removed: **10** (44 − 34).
- Double-counting removed: ₹38,048.25 − ₹25,209.75 = **₹12,838.50**.
- Every representative net was re-checked as (exit − entry) × lot − ₹220; all 44 legs reconcile.
- This recount reproduces `index_options_october_UNIQUE_trades.md` exactly (same 34 keys, same representatives, same per-index nets).

Two earliest-entry sensitivities, stated so the total is reproducible:
- **26 Oct Nifty CE:** earliest is Skill V3 09:55, target +₹5,630; the later V5 v2 10:00 leg on the same key was a stop (−₹3,470) and is NOT counted. Under a latest-entry rule this key alone would change the total by ₹9,100.
- **9 Oct Nifty CE:** earliest is Volrix (b) 09:20, 22200 CE, 398.00 → 488.00 target +₹5,630; the later Skill V3 09:35 leg (22400 CE, 318.15 → 408.15) is also a target +₹5,630, so the net is unchanged but the strike/entry differ. Volrix (b) adds one genuinely new key that no other system has: **Bank 26 Oct CE** (54300 CE, target +₹2,480).

## Result — per index separately (never pooled in the verdict)

| Index | Unique trades | Trades/week (÷ 3.6) | Full targets | Stops | Square-offs | Full-target % | Net-positive trades | Net / 1 lot |
|---|---|---|---|---|---|---|---|---|
| **Nifty** | **16** | **4.44** | 6 | 7 | 3 | **37.5%** (6/16) | 8/16 (50.0%) | **+₹14,169.75** |
| **Bank Nifty** | **18** | **5.00** | 10 | 8 | 0 | **55.6%** (10/18) | 10/18 (55.6%) | **+₹11,040.00** |

Notes on the two percentages:
- Nifty full-target % (37.5%) is lower than its net-positive rate (50.0%) because two square-off exits were green but are not full targets: 6 Oct CE +₹1,801.50 and 12 Oct PE +₹4,213.00. The third Nifty square-off (23 Oct PE, −₹1,334.75) was a loss.
- Bank has no square-offs, so its full-target % and net-positive rate coincide at 55.6%.

### Combined unique-once total (arithmetic sum only, not a pooled verdict)

- **34 unique trades, combined net +₹25,209.75 per 1 lot each index** (Nifty +₹14,169.75 + Bank +₹11,040.00).
- Combined full-target rate, for reference only: 16/34 = **47.1%**. Combined trades/week arithmetic: 34 ÷ 3.6 = 9.44 — this is two separate 1-lot books added together, not a single-system frequency, and is not used in the per-index verdict below.

## Does Variant 1 meet the four checks?

| Check | Nifty | Bank Nifty | Combined |
|---|---|---|---|
| **2–3 trades/week** (strict band) | **NO — 4.44, above the band** | **NO — 5.00, above the band** | n/a (not pooled) |
| 2–3 trades/week (read as minimum ≥ 2/week) | YES — clears the minimum | YES — clears the minimum | — |
| **Full-target ≥ 50%** | **NO — 37.5%** | **YES — 55.6%** | NO — 47.1% (reference only) |
| **Net > 0** | **YES — +₹14,169.75** | **YES — +₹11,040.00** | YES — +₹25,209.75 |
| **Combined ≥ ₹20,000** | — (portfolio-level check) | — (portfolio-level check) | **YES — +₹25,209.75, exceeds by ₹5,209.75** |

**Overall verdict:**
- **Variant 1 does NOT meet all four checks together on either index under the strict 2–3/week band.** Nifty fails full-target and sits above the frequency band; Bank passes full-target and net but also sits above the frequency band.
- Under the looser "at least 2/week" reading of frequency, Bank passes its own legs (frequency minimum, full-target, net) and the combined total clears ₹20,000 — but Nifty still fails full-target (37.5%), so there is still no clean all-legs pass on both indices.
- Neither index alone reaches ₹20,000 (Nifty +₹14,169.75; Bank +₹11,040.00); the ₹20,000 bar is cleared only by adding the two separate 1-lot books together.
- **No adoption claim on October alone.** This is an in-sample, deduplicated October total under a frozen earliest-entry rule, not a live system result. November 2026 paper from 2026-11-02, with the definition frozen, remains the validation step.

## Unique trade list — all 34 (representative = earliest entry on each key)

| # | Date | Index | Dir | Strike | Expiry | Entry | Entry prem | Exit | Exit prem | Reason | Net / 1 lot |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-01 | BANKNIFTY | CE | 54900 | 2026-10-27 | 10:00 | 999.15 | 10:30 | 1089.15 | target | +₹2,480.00 |
| 2 | 2026-10-01 | NIFTY | CE | 22600 | 2026-10-27 | 10:05 | 360.35 | 12:10 | 310.35 | stop | −₹3,470.00 |
| 3 | 2026-10-05 | BANKNIFTY | PE | 54700 | 2026-10-27 | 10:55 | 755.00 | 11:50 | 845.00 | target | +₹2,480.00 |
| 4 | 2026-10-05 | NIFTY | CE | 22600 | 2026-10-27 | 09:35 | 364.05 | 10:25 | 314.05 | stop | −₹3,470.00 |
| 5 | 2026-10-06 | BANKNIFTY | CE | 55000 | 2026-10-27 | 09:45 | 941.10 | 10:05 | 891.10 | stop | −₹1,720.00 |
| 6 | 2026-10-06 | NIFTY | CE | 22600 | 2026-10-27 | 09:50 | 359.90 | 15:10 | 391.00 | square_off | +₹1,801.50 |
| 7 | 2026-10-07 | BANKNIFTY | PE | 54700 | 2026-10-27 | 09:40 | 736.90 | 09:40 | 686.90 | stop | −₹1,720.00 |
| 8 | 2026-10-07 | NIFTY | PE | 22600 | 2026-10-27 | 09:40 | 268.45 | 10:20 | 218.45 | stop | −₹3,470.00 |
| 9 | 2026-10-08 | BANKNIFTY | PE | 54800 | 2026-10-27 | 11:30 | 717.65 | 11:45 | 667.65 | stop | −₹1,720.00 |
| 10 | 2026-10-08 | NIFTY | PE | 22500 | 2026-10-27 | 09:45 | 270.00 | 12:20 | 360.00 | target | +₹5,630.00 |
| 11 | 2026-10-09 | BANKNIFTY | CE | 55100 | 2026-10-27 | 09:35 | 849.35 | 10:10 | 939.35 | target | +₹2,480.00 |
| 12 | 2026-10-09 | NIFTY | CE | 22200 | 2026-10-27 | 09:20 | 398.00 | 09:45 | 488.00 | target | +₹5,630.00 |
| 13 | 2026-10-12 | BANKNIFTY | PE | 55000 | 2026-10-27 | 09:55 | 609.00 | 09:55 | 559.00 | stop | −₹1,720.00 |
| 14 | 2026-10-12 | NIFTY | PE | 22500 | 2026-10-27 | 09:55 | 250.80 | 15:10 | 319.00 | square_off | +₹4,213.00 |
| 15 | 2026-10-13 | BANKNIFTY | CE | 55200 | 2026-10-27 | 09:40 | 756.65 | 11:45 | 706.65 | stop | −₹1,720.00 |
| 16 | 2026-10-13 | BANKNIFTY | PE | 55200 | 2026-10-27 | 10:40 | 547.35 | 11:45 | 637.35 | target | +₹2,480.00 |
| 17 | 2026-10-13 | NIFTY | CE | 22500 | 2026-10-27 | 09:35 | 288.60 | 14:35 | 378.60 | target | +₹5,630.00 |
| 18 | 2026-10-14 | BANKNIFTY | CE | 55500 | 2026-10-27 | 09:35 | 728.00 | 10:05 | 678.00 | stop | −₹1,720.00 |
| 19 | 2026-10-15 | BANKNIFTY | CE | 55600 | 2026-10-27 | 09:55 | 669.95 | 10:15 | 759.95 | target | +₹2,480.00 |
| 20 | 2026-10-15 | NIFTY | CE | 22800 | 2026-10-27 | 09:35 | 213.30 | 10:15 | 303.30 | target | +₹5,630.00 |
| 21 | 2026-10-21 | BANKNIFTY | CE | 55800 | 2026-10-27 | 09:35 | 489.80 | 09:45 | 439.80 | stop | −₹1,720.00 |
| 22 | 2026-10-21 | BANKNIFTY | PE | 55200 | 2026-10-27 | 11:20 | 379.95 | 11:35 | 469.95 | target | +₹2,480.00 |
| 23 | 2026-10-21 | NIFTY | CE | 23100 | 2026-10-27 | 09:35 | 183.10 | 10:00 | 133.10 | stop | −₹3,470.00 |
| 24 | 2026-10-21 | NIFTY | PE | 22800 | 2026-10-27 | 11:40 | 151.30 | 14:45 | 241.30 | target | +₹5,630.00 |
| 25 | 2026-10-22 | BANKNIFTY | CE | 54800 | 2026-10-27 | 10:15 | 499.00 | 10:20 | 589.00 | target | +₹2,480.00 |
| 26 | 2026-10-22 | NIFTY | CE | 22700 | 2026-10-27 | 10:25 | 190.45 | 11:45 | 140.45 | stop | −₹3,470.00 |
| 27 | 2026-10-23 | BANKNIFTY | PE | 54600 | 2026-10-27 | 09:50 | 322.70 | 10:00 | 412.70 | target | +₹2,480.00 |
| 28 | 2026-10-23 | NIFTY | PE | 22500 | 2026-10-27 | 10:10 | 125.85 | 15:10 | 108.70 | square_off | −₹1,334.75 |
| 29 | 2026-10-26 | BANKNIFTY | CE | 54300 | 2026-10-27 | 09:20 | 238.55 | 09:55 | 328.55 | target | +₹2,480.00 |
| 30 | 2026-10-26 | BANKNIFTY | PE | 54300 | 2026-10-27 | 10:20 | 275.15 | 10:35 | 365.15 | target | +₹2,480.00 |
| 31 | 2026-10-26 | NIFTY | CE | 22600 | 2026-10-27 | 09:55 | 132.05 | 10:05 | 222.05 | target | +₹5,630.00 |
| 32 | 2026-10-27 | BANKNIFTY | CE | 54500 | 2026-10-27 | 09:40 | 222.00 | 10:20 | 172.00 | stop | −₹1,720.00 |
| 33 | 2026-10-27 | NIFTY | CE | 22800 | 2026-10-27 | 09:45 | 65.00 | 13:10 | 15.00 | stop | −₹3,470.00 |
| 34 | 2026-10-28 | NIFTY | PE | 22500 | 2026-11-03 | 10:20 | 200.95 | 11:00 | 150.95 | stop | −₹3,470.00 |

## Sources

- `~/workspace/trading/index_options_october_UNIQUE_trades.md` — reproduced exactly by the independent recount above.
- `~/workspace/trading/index_options_premium_october_trades.csv` — (lA) v2 and V5 v2 legs only (Skill v2 base rows excluded as duplicates of Skill V3).
- `~/workspace/trading/index_options_skill_tuned_oct30_trades.csv` — Skill V3, COMPUTED legs only (29th leg, Bank 28 Oct CE, NOT_COMPUTED, excluded).
- `~/workspace/trading/index_options_volrix_tuned_oct30.md` — Volrix intraday (b) at −1.0% only (Nifty 9 Oct, Bank 26 Oct; both target exits).
