# Index OPTIONS — October EXCLUSIVE trades only

**User correction applied (2026-10-30 12:08 IST): "If the trade is given by all the same engines that means that's duplicate. You want only one. That means one trade which was not given with other stuff. So show me that."**

**Correct definition used here — EXCLUSIVE only:**
A trade counts ONLY if it was given by exactly ONE of the 4 systems, and by NO other system.
Trades given by 2, 3, or 4 systems are duplicates and are EXCLUDED entirely — not counted once, not merged.
This is NOT the previous deduplicated-once list. That definition was wrong and is not used here.

Index OPTIONS only, paper only, no orders, no stocks, no futures.
Window: October 2026, 1–28 Oct, 18 trading days. 29–30 Oct are NOT included.
Real money made in October = **₹0** — no live trades were placed. All nets below are paper, per 1 lot, after ₹220 assumed cost.
Lot: Nifty 65, Bank Nifty 30. Premium rule (uniform V4-overlay): entry = open of first 5-min option candle after the spot signal; stop = entry − 50, target = entry + 90 option points, both CE and PE; stop before target per bar including the entry bar; square-off 15:10.

## The 4 systems

- (lA) v2 — from `index_options_premium_october_trades.csv`
- V5 v2 — from `index_options_premium_october_trades.csv`
- Tuned Skill V3 (CE no-block) — from `index_options_skill_tuned_oct30_trades.csv`, variant V3 only. V9 is NOT merged in.
- Volrix tuned intraday (b) at −1.0% — from `index_options_volrix_tuned_oct30.md`: Nifty 9 Oct 22200 CE, entry 398.00 → target 488.00 at 09:45, +₹5,630; Bank 26 Oct 54300 CE, entry 238.55 → target 328.55 at 09:55, +₹2,480.

## Matching key for "same trade"

**Date + index + direction (CE/PE).** If two systems give the same date + index + direction, that trade is a duplicate and is excluded from the exclusive list, even if strike or entry time differ slightly. Overlaps are shown only in the duplicates-excluded summary below, not in the exclusive list.

## Exclusive trades — the only list that counts here

Sorted by date, then index. Running total is per index (Nifty running total counts Nifty exclusive trades only; Bank running total counts Bank exclusive trades only).

| Date | Index | Direction | Single system that gave it | Strike | Expiry | Entry time | Entry premium | Exit time | Exit premium | Exit reason | Net / 1 lot | Running total (per index) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | NIFTY | CE | Tuned Skill V3 | 22600 | 2026-10-27 | 10:05 | 360.35 | 12:10 | 310.35 | stop | −₹3,470.00 | Nifty −₹3,470.00 |
| 2026-10-05 | BANKNIFTY | PE | Tuned Skill V3 | 54700 | 2026-10-27 | 10:55 | 755.00 | 11:50 | 845.00 | target | +₹2,480.00 | Bank +₹2,480.00 |
| 2026-10-05 | NIFTY | CE | Tuned Skill V3 | 22600 | 2026-10-27 | 09:35 | 364.05 | 10:25 | 314.05 | stop | −₹3,470.00 | Nifty −₹6,940.00 |
| 2026-10-06 | BANKNIFTY | CE | Tuned Skill V3 | 55000 | 2026-10-27 | 09:45 | 941.10 | 10:05 | 891.10 | stop | −₹1,720.00 | Bank +₹760.00 |
| 2026-10-06 | NIFTY | CE | Tuned Skill V3 | 22600 | 2026-10-27 | 09:50 | 359.90 | 15:10 | 391.00 | square-off | +₹1,801.50 | Nifty −₹5,138.50 |
| 2026-10-07 | NIFTY | PE | Tuned Skill V3 | 22600 | 2026-10-27 | 09:40 | 268.45 | 10:20 | 218.45 | stop | −₹3,470.00 | Nifty −₹8,608.50 |
| 2026-10-09 | BANKNIFTY | CE | Tuned Skill V3 | 55100 | 2026-10-27 | 09:35 | 849.35 | 10:10 | 939.35 | target | +₹2,480.00 | Bank +₹3,240.00 |
| 2026-10-12 | BANKNIFTY | PE | Tuned Skill V3 | 55000 | 2026-10-27 | 09:55 | 609.00 | 09:55 | 559.00 | stop | −₹1,720.00 | Bank +₹1,520.00 |
| 2026-10-12 | NIFTY | PE | Tuned Skill V3 | 22500 | 2026-10-27 | 09:55 | 250.80 | 15:10 | 319.00 | square-off | +₹4,213.00 | Nifty −₹4,395.50 |
| 2026-10-13 | BANKNIFTY | CE | Tuned Skill V3 | 55200 | 2026-10-27 | 09:40 | 756.65 | 11:45 | 706.65 | stop | −₹1,720.00 | Bank −₹200.00 |
| 2026-10-13 | BANKNIFTY | PE | V5 v2 | 55200 | 2026-10-27 | 10:40 | 547.35 | 11:45 | 637.35 | target | +₹2,480.00 | Bank +₹2,280.00 |
| 2026-10-13 | NIFTY | CE | Tuned Skill V3 | 22500 | 2026-10-27 | 09:35 | 288.60 | 14:35 | 378.60 | target | +₹5,630.00 | Nifty +₹1,234.50 |
| 2026-10-14 | BANKNIFTY | CE | Tuned Skill V3 | 55500 | 2026-10-27 | 09:35 | 728.00 | 10:05 | 678.00 | stop | −₹1,720.00 | Bank +₹560.00 |
| 2026-10-15 | BANKNIFTY | CE | Tuned Skill V3 | 55600 | 2026-10-27 | 09:55 | 669.95 | 10:15 | 759.95 | target | +₹2,480.00 | Bank +₹3,040.00 |
| 2026-10-15 | NIFTY | CE | Tuned Skill V3 | 22800 | 2026-10-27 | 09:35 | 213.30 | 10:15 | 303.30 | target | +₹5,630.00 | Nifty +₹6,864.50 |
| 2026-10-21 | BANKNIFTY | CE | Tuned Skill V3 | 55800 | 2026-10-27 | 09:35 | 489.80 | 09:45 | 439.80 | stop | −₹1,720.00 | Bank +₹1,320.00 |
| 2026-10-21 | NIFTY | CE | Tuned Skill V3 | 23100 | 2026-10-27 | 09:35 | 183.10 | 10:00 | 133.10 | stop | −₹3,470.00 | Nifty +₹3,394.50 |
| 2026-10-21 | NIFTY | PE | (lA) v2 | 22800 | 2026-10-27 | 11:40 | 151.30 | 14:45 | 241.30 | target | +₹5,630.00 | Nifty +₹9,024.50 |
| 2026-10-22 | BANKNIFTY | CE | Tuned Skill V3 | 54800 | 2026-10-27 | 10:15 | 499.00 | 10:20 | 589.00 | target | +₹2,480.00 | Bank +₹3,800.00 |
| 2026-10-22 | NIFTY | CE | Tuned Skill V3 | 22700 | 2026-10-27 | 10:25 | 190.45 | 11:45 | 140.45 | stop | −₹3,470.00 | Nifty +₹5,554.50 |
| 2026-10-26 | BANKNIFTY | CE | Volrix tuned (b) −1.0% | 54300 | 2026-10-27 | 09:20 | 238.55 | 09:55 | 328.55 | target | +₹2,480.00 | Bank +₹6,280.00 |
| 2026-10-26 | BANKNIFTY | PE | V5 v2 | 54300 | 2026-10-27 | 10:20 | 275.15 | 10:35 | 365.15 | target | +₹2,480.00 | Bank +₹8,760.00 |
| 2026-10-27 | BANKNIFTY | CE | Tuned Skill V3 | 54500 | 2026-10-27 | 09:40 | 222.00 | 10:20 | 172.00 | stop | −₹1,720.00 | Bank +₹7,040.00 |
| 2026-10-27 | NIFTY | CE | Tuned Skill V3 | 22800 | 2026-10-27 | 09:45 | 65.00 | 13:10 | 15.00 | stop | −₹3,470.00 | Nifty +₹2,084.50 |
| 2026-10-28 | NIFTY | PE | Tuned Skill V3 | 22500 | 2026-11-03 | 10:20 | 200.95 | 11:00 | 150.95 | stop | −₹3,470.00 | Nifty −₹1,385.50 |

**Note on the two Bank 26 Oct rows:** Bank 26 Oct CE (Volrix) and Bank 26 Oct PE (V5) are DIFFERENT trades under the key (direction differs), so both are exclusive. They are not duplicates of each other.

**Note on Nifty 21 Oct:** Nifty 21 Oct CE (Skill V3) and Nifty 21 Oct PE ((lA) v2) are different directions, so both are exclusive.

## Exclusive totals

| System | Nifty exclusive trades / net | Bank exclusive trades / net | System exclusive total |
|---|---|---|---|
| (lA) v2 | 1 / +₹5,630.00 | 0 / ₹0 | +₹5,630.00 |
| V5 v2 | 0 / ₹0 | 2 / +₹4,960.00 | +₹4,960.00 |
| Tuned Skill V3 | 11 / −₹7,015.50 | 10 / −₹400.00 | −₹7,415.50 |
| Volrix tuned (b) −1.0% | 0 / ₹0 | 1 / +₹2,480.00 | +₹2,480.00 |
| **Total exclusive** | **12 / −₹1,385.50** | **13 / +₹7,040.00** | **25 trades / +₹5,654.50 paper** |

**Combined exclusive total: +₹5,654.50 paper, 1 lot each — NOT real money (real = ₹0).**
Nifty exclusive alone is negative (−₹1,385.50); Bank exclusive alone is positive (+₹7,040.00). The combined positive total comes entirely from Bank.

## Duplicates excluded — summary only (not in the exclusive list)

9 duplicate keys (date + index + direction given by 2–3 systems), covering 19 system-legs, totalling +₹32,393.75 of leg nets that were removed by excluding duplicates entirely:

| Duplicate key | Systems that gave it | Leg nets |
|---|---|---|
| 2026-10-01 BANKNIFTY CE | V5 v2, Tuned Skill V3 | +₹2,480 + ₹2,480 = +₹4,960.00 |
| 2026-10-07 BANKNIFTY PE | (lA) v2, Tuned Skill V3 | −₹1,720 − ₹1,720 = −₹3,440.00 |
| 2026-10-08 BANKNIFTY PE | (lA) v2, Tuned Skill V3 | −₹1,720 − ₹1,720 = −₹3,440.00 |
| 2026-10-08 NIFTY PE | (lA) v2, V5 v2, Tuned Skill V3 | +₹2,383.25 + ₹5,630 + ₹5,630 = +₹13,643.25 |
| 2026-10-09 NIFTY CE | Tuned Skill V3, Volrix tuned (b) | +₹5,630 + ₹5,630 = +₹11,260.00 |
| 2026-10-21 BANKNIFTY PE | (lA) v2, V5 v2 | +₹2,480 + ₹2,480 = +₹4,960.00 |
| 2026-10-23 BANKNIFTY PE | (lA) v2, Tuned Skill V3 | +₹2,480 + ₹2,480 = +₹4,960.00 |
| 2026-10-23 NIFTY PE | (lA) v2, V5 v2 | −₹1,334.75 − ₹1,334.75 = −₹2,669.50 |
| 2026-10-26 NIFTY CE | V5 v2, Tuned Skill V3 | −₹3,470 + ₹5,630 = +₹2,160.00 |

Reconciliation, verified from the CSVs:
- Total system-legs across the 4 systems: 44 ((lA) v2: 7, V5 v2: 7, Tuned Skill V3 computed: 28, Volrix (b): 2).
- Literal sum of all 44 legs: +₹38,048.25 ((lA) +₹8,198.50 + V5 +₹10,745.25 + Skill V3 +₹10,994.50 + Volrix (b) +₹8,110.00).
- Exclusive legs: 25, totalling +₹5,654.50.
- Duplicate legs removed: 19, totalling +₹32,393.75.
- Check: +₹5,654.50 + ₹32,393.75 = +₹38,048.25. ✓
- Distinct date+index+direction keys: 34 (25 exclusive keys + 9 duplicate keys).
- Excluded from the count entirely: Tuned Skill V3 Bank 28 Oct CE (54000, Nov-03 expiry) — NOT_COMPUTED in the Skill file (Bank Nov-03 chain gap), so it is neither exclusive nor duplicate; it cannot change the exclusive total.

## What this means, plainly

- Almost all of the "big" October systems total (+₹38,048.25) was duplicates: ₹32,393.75 of it came from trades given by 2–3 engines at once.
- What is left, exclusive-only, is much smaller: **+₹5,654.50**, and it is Bank-only in net terms (Nifty exclusive is a loss).
- Most exclusive trades come from Tuned Skill V3 (21 of 25) — and on its own, its exclusive set is negative (−₹7,415.50). The exclusive winners are the few (lA)/V5/Volrix trades that no other engine also gave: (lA) Nifty 21 Oct PE +₹5,630, V5 Bank 13 Oct PE +₹2,480 and 26 Oct PE +₹2,480, Volrix Bank 26 Oct CE +₹2,480.
- Nothing is adopted on October alone. November 2026 paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November) remains validation.
