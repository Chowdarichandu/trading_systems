# October 2026 — UNIQUE combined trades across 4 systems (deduplicated)

Index OPTIONS only, paper only, no orders, no stocks. Window: 1–28 October 2026 (18 trading days).
**Real money made = ₹0** — no live trades were placed. All nets below are paper, per 1 lot, after ₹220 assumed cost per trade.

## Dedup rule — frozen before counting

- **Unique key = (date, index, direction CE/PE).** If multiple systems signal the same date + index + direction, count it **ONCE**.
- **Representative trade = the earliest entry time** among the systems on that key. Its strike, entry premium, exit and net are the ones counted. Later signals on the same key are listed under "Systems overlapping" but their nets are NOT added again.
- Do NOT dedup across indices, and do NOT dedup CE vs PE on the same day — those are different trades and both count (e.g. Bank 13 Oct CE and Bank 13 Oct PE are both in the list; Bank 26 Oct CE and PE are both in the list).
- No trades invented, no spot points converted to premiums.

## Systems included (4 only)

1. **(lA) v2** — from `index_options_premium_october_trades.csv` (7 trades)
2. **V5 v2** — from the same file (7 trades)
3. **Tuned Skill = V3 (CE no-block)** — from `index_options_skill_tuned_oct30_trades.csv`, variant V3 only (29 legs, 28 COMPUTED + 1 NOT_COMPUTED). Skill base rows in the premium file were NOT counted separately — they are the same Skill system, and every Skill-base key is already covered by V3.
4. **Volrix tuned = intraday (b) at −1.0%** — from `index_options_volrix_tuned_oct30.md` (2 trades: Nifty 9 Oct, Bank 26 Oct). Volrix (a) 5-session hold and (c-raw) are NOT included — using them as well would double-count Volrix itself.

Excluded, not counted as a win or a loss: Skill V3 Bank 28 Oct CE (54000, Nov-03 expiry) — premium_status NOT_COMPUTED (Bank Nov-03 chain returns 0 strikes, the known Bank post-October chain gap). If it were counted, Bank would have 19 unique trades, not 18.

Premium method (uniform overlay in all source files): entry = open of first 5-min option candle after the spot signal; stop = entry − 50, target = entry + 90 option points, both CE and PE; stop before target per bar including the entry bar; square-off 15:10; net per 1 lot = (exit − entry) × lot − ₹220; lot Nifty 65 / Bank 30; strike ATM nearest 100; expiry monthly 27 Oct 2026 for 1–27 Oct, weekly 3 Nov 2026 for 28 Oct trades. Volrix (b) entry is the 09:20 open on the entry day, with the same −50/+90 stop/target.

## UNIQUE trade list — all 34, in date order

| # | Date | Index | Dir | Strike | Expiry | Entry time | Entry prem | Exit time | Exit prem | Exit reason | Net / 1 lot | Running total (that index) | Systems overlapping on this key |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-01 | BANKNIFTY | CE | 54900 | 2026-10-27 | 10:00 | 999.15 | 10:30 | 1089.15 | target | +₹2,480.00 | +₹2,480.00 | Skill V3 + V5 v2 |
| 2 | 2026-10-01 | NIFTY | CE | 22600 | 2026-10-27 | 10:05 | 360.35 | 12:10 | 310.35 | stop | −₹3,470.00 | −₹3,470.00 | Skill V3 |
| 3 | 2026-10-05 | BANKNIFTY | PE | 54700 | 2026-10-27 | 10:55 | 755.00 | 11:50 | 845.00 | target | +₹2,480.00 | +₹4,960.00 | Skill V3 + V5 v2 |
| 4 | 2026-10-05 | NIFTY | CE | 22600 | 2026-10-27 | 09:35 | 364.05 | 10:25 | 314.05 | stop | −₹3,470.00 | −₹6,940.00 | Skill V3 + V5 v2 |
| 5 | 2026-10-06 | BANKNIFTY | CE | 55000 | 2026-10-27 | 09:45 | 941.10 | 10:05 | 891.10 | stop | −₹1,720.00 | +₹3,240.00 | Skill V3 + V5 v2 |
| 6 | 2026-10-06 | NIFTY | CE | 22600 | 2026-10-27 | 09:50 | 359.90 | 15:10 | 391.00 | square_off | +₹1,801.50 | −₹5,138.50 | Skill V3 + V5 v2 |
| 7 | 2026-10-07 | BANKNIFTY | PE | 54700 | 2026-10-27 | 09:40 | 736.90 | 09:40 | 686.90 | stop | −₹1,720.00 | +₹1,520.00 | (lA) v2 + Skill V3 + V5 v2 |
| 8 | 2026-10-07 | NIFTY | PE | 22600 | 2026-10-27 | 09:40 | 268.45 | 10:20 | 218.45 | stop | −₹3,470.00 | −₹8,608.50 | Skill V3 + V5 v2 |
| 9 | 2026-10-08 | BANKNIFTY | PE | 54800 | 2026-10-27 | 11:30 | 717.65 | 11:45 | 667.65 | stop | −₹1,720.00 | −₹200.00 | (lA) v2 (13:20, later) + Skill V3 + V5 v2 |
| 10 | 2026-10-08 | NIFTY | PE | 22500 | 2026-10-27 | 09:45 | 270.00 | 12:20 | 360.00 | target | +₹5,630.00 | −₹2,978.50 | (lA) v2 (11:30, later) + Skill V3 + V5 v2 |
| 11 | 2026-10-09 | BANKNIFTY | CE | 55100 | 2026-10-27 | 09:35 | 849.35 | 10:10 | 939.35 | target | +₹2,480.00 | +₹2,280.00 | Skill V3 |
| 12 | 2026-10-09 | NIFTY | CE | 22200 | 2026-10-27 | 09:20 | 398.00 | 09:45 | 488.00 | target | +₹5,630.00 | +₹2,651.50 | Skill V3 (09:35, later) + Volrix (b) |
| 13 | 2026-10-12 | BANKNIFTY | PE | 55000 | 2026-10-27 | 09:55 | 609.00 | 09:55 | 559.00 | stop | −₹1,720.00 | +₹560.00 | Skill V3 + V5 v2 |
| 14 | 2026-10-12 | NIFTY | PE | 22500 | 2026-10-27 | 09:55 | 250.80 | 15:10 | 319.00 | square_off | +₹4,213.00 | +₹6,864.50 | Skill V3 + V5 v2 |
| 15 | 2026-10-13 | BANKNIFTY | CE | 55200 | 2026-10-27 | 09:40 | 756.65 | 11:45 | 706.65 | stop | −₹1,720.00 | −₹1,160.00 | Skill V3 |
| 16 | 2026-10-13 | BANKNIFTY | PE | 55200 | 2026-10-27 | 10:40 | 547.35 | 11:45 | 637.35 | target | +₹2,480.00 | +₹1,320.00 | V5 v2 |
| 17 | 2026-10-13 | NIFTY | CE | 22500 | 2026-10-27 | 09:35 | 288.60 | 14:35 | 378.60 | target | +₹5,630.00 | +₹12,494.50 | Skill V3 |
| 18 | 2026-10-14 | BANKNIFTY | CE | 55500 | 2026-10-27 | 09:35 | 728.00 | 10:05 | 678.00 | stop | −₹1,720.00 | −₹400.00 | Skill V3 + V5 v2 |
| 19 | 2026-10-15 | BANKNIFTY | CE | 55600 | 2026-10-27 | 09:55 | 669.95 | 10:15 | 759.95 | target | +₹2,480.00 | +₹2,080.00 | Skill V3 |
| 20 | 2026-10-15 | NIFTY | CE | 22800 | 2026-10-27 | 09:35 | 213.30 | 10:15 | 303.30 | target | +₹5,630.00 | +₹18,124.50 | Skill V3 |
| 21 | 2026-10-21 | BANKNIFTY | CE | 55800 | 2026-10-27 | 09:35 | 489.80 | 09:45 | 439.80 | stop | −₹1,720.00 | +₹360.00 | Skill V3 |
| 22 | 2026-10-21 | BANKNIFTY | PE | 55200 | 2026-10-27 | 11:20 | 379.95 | 11:35 | 469.95 | target | +₹2,480.00 | +₹2,840.00 | (lA) v2 + V5 v2 |
| 23 | 2026-10-21 | NIFTY | CE | 23100 | 2026-10-27 | 09:35 | 183.10 | 10:00 | 133.10 | stop | −₹3,470.00 | +₹14,654.50 | Skill V3 |
| 24 | 2026-10-21 | NIFTY | PE | 22800 | 2026-10-27 | 11:40 | 151.30 | 14:45 | 241.30 | target | +₹5,630.00 | +₹20,284.50 | (lA) v2 |
| 25 | 2026-10-22 | BANKNIFTY | CE | 54800 | 2026-10-27 | 10:15 | 499.00 | 10:20 | 589.00 | target | +₹2,480.00 | +₹5,320.00 | Skill V3 |
| 26 | 2026-10-22 | NIFTY | CE | 22700 | 2026-10-27 | 10:25 | 190.45 | 11:45 | 140.45 | stop | −₹3,470.00 | +₹16,814.50 | Skill V3 |
| 27 | 2026-10-23 | BANKNIFTY | PE | 54600 | 2026-10-27 | 09:50 | 322.70 | 10:00 | 412.70 | target | +₹2,480.00 | +₹7,800.00 | (lA) v2 (10:00, later) + Skill V3 + V5 v2 |
| 28 | 2026-10-23 | NIFTY | PE | 22500 | 2026-10-27 | 10:10 | 125.85 | 15:10 | 108.70 | square_off | −₹1,334.75 | +₹15,479.75 | (lA) v2 + V5 v2 |
| 29 | 2026-10-26 | BANKNIFTY | CE | 54300 | 2026-10-27 | 09:20 | 238.55 | 09:55 | 328.55 | target | +₹2,480.00 | +₹10,280.00 | Volrix (b) |
| 30 | 2026-10-26 | BANKNIFTY | PE | 54300 | 2026-10-27 | 10:20 | 275.15 | 10:35 | 365.15 | target | +₹2,480.00 | +₹12,760.00 | V5 v2 |
| 31 | 2026-10-26 | NIFTY | CE | 22600 | 2026-10-27 | 09:55 | 132.05 | 10:05 | 222.05 | target | +₹5,630.00 | +₹21,109.75 | Skill V3 + V5 v2 (10:00, later, stop leg −₹3,470 NOT counted) |
| 32 | 2026-10-27 | BANKNIFTY | CE | 54500 | 2026-10-27 | 09:40 | 222.00 | 10:20 | 172.00 | stop | −₹1,720.00 | +₹11,040.00 | Skill V3 + V5 v2 |
| 33 | 2026-10-27 | NIFTY | CE | 22800 | 2026-10-27 | 09:45 | 65.00 | 13:10 | 15.00 | stop | −₹3,470.00 | +₹17,639.75 | Skill V3 + V5 v2 |
| 34 | 2026-10-28 | NIFTY | PE | 22500 | 2026-11-03 | 10:20 | 200.95 | 11:00 | 150.95 | stop | −₹3,470.00 | +₹14,169.75 | Skill V3 + V5 v2 |

## Totals — unique, deduplicated

| Index | Unique trades | Targets | Stops | Square-offs | Unique premium net / 1 lot |
|---|---|---|---|---|---|
| NIFTY | 16 | 6 | 7 | 3 | **+₹14,169.75** |
| BANKNIFTY | 18 | 10 | 8 | 0 | **+₹11,040.00** |
| **Combined (Nifty + Bank, 1 lot each)** | **34** | **16** | **15** | **3** | **+₹25,209.75 paper, NOT real money** |

## Reconciliation vs the literal sum

Verified from the CSVs, system by system (premium nets, 1 lot):

| System | Nifty | Bank | Total |
|---|---|---|---|
| (lA) v2 | +₹6,678.50 | +₹1,520.00 | +₹8,198.50 |
| V5 v2 | +₹825.25 | +₹9,920.00 | +₹10,745.25 |
| Tuned Skill V3 (computed legs only) | +₹9,874.50 | +₹1,120.00 | +₹10,994.50 |
| Volrix tuned (b) | +₹5,630.00 | +₹2,480.00 | +₹8,110.00 |
| **Literal sum (double-counted)** | | | **+₹38,048.25** |

- Legs fed in: 44 = 7 (lA) + 7 (V5) + 28 Skill V3 computed + 2 Volrix (b). (Skill V3's 29th leg, Bank 28 Oct CE, is NOT_COMPUTED and excluded from both counts.)
- Unique trades: 34. Duplicate legs removed: 10.
- **Double-counting removed: ₹38,048.25 − ₹25,209.75 = ₹12,838.50.** That ₹12,838.50 is the same trades counted a second (or third) time by overlapping systems — it is not extra profit.
- Note on the largest single dedup effect: on 26 Oct Nifty CE, the earliest-entry rule picks the Skill V3 target (+₹5,630) and drops the later V5 stop leg (−₹3,470) on the same key. Under a different dedup rule (e.g. latest entry, or system priority) that key's net would change by ₹9,100 — the rule is stated above so the number is reproducible, not hidden.

## V9 note — does tuned Skill V9 change the unique set?

No. V9 (pullback) has 12 legs, and all 12 fall on (date, index, direction) keys already in the unique list above (e.g. Nifty 6 Oct CE, 8 Oct PE, 12 Oct PE, 26 Oct CE, 28 Oct PE; Bank 1 Oct CE, 5 Oct PE, 6 Oct CE, 8 Oct PE, 12 Oct PE, 14 Oct CE, 27 Oct CE). V9 was NOT merged with V3 — merging them would double-count Skill itself. V9's own entry times and premiums on those keys differ (later pullback entries), so if V9 were used as the tuned Skill system instead of V3, the unique list's representative trades on those 12 keys would change and the total would differ — but under the frozen rule in this task (V3 = tuned Skill, earliest entry wins), V9 adds zero new unique trades.

## What this unique total is, and is not

- It IS the October premium total if you traded each unique date+index+direction signal once, 1 lot, taking the earliest system's entry on overlapping days.
- It is NOT a single system's result, NOT a portfolio P&L from running all 4 systems live (that would reintroduce the overlaps), and NOT real money — real money in October = ₹0, no live trades placed.
- Nothing is adopted on October alone. November 2026 paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November) remains validation.
