# Round 5 — Track B: November Forensic + Green-Day Counts (2026-11-14)

Owner's simple criterion (2026-11-14): *"November till now is red — at least more than half days green."*
This file is **descriptive arithmetic only** — no new rules invented, nothing fitted to November, nothing armed.
Paper history throughout; Bank Nifty option premiums per 1 lot (30), cost ₹220/trade inside all nets.

**Sources (stored files only):** stack legs `solid60_programme_2026-11-13_bank_A_stack_features.csv` (the file the
₹900-build anchors on: 111 legs) · OI-V3 legs `oi_buildup_trades.csv` (variant V3, mode=real) + `oi_buildup_results.json`
(merge §) · VIX-B1 legs `round2_trades.csv` (variant B1, mode=real) + `new_data_round2_results.json` (merge §) ·
R4-D1 legs `round4_trades.csv` (family D1, mode=real) + `new_data_round4_results.json` (merge §) · November stack
`november_shadow_stack_bank_log.csv`, cross-checked against `bank_900_tradeday_results.json` (identical day map) ·
205-day Jan–Oct calendar from `oi_history/banknifty_daily_oi.csv`.

**Method:** an increment = the fragment's real legs that fall on stack-idle days only (exactly as each round
computed it). A day is GREEN if its net > 0, RED if < 0, NO-TRADE if the configuration took no leg that day.

**Verification — every union re-summed independently from the leg files, all four match the published round totals to the paisa:**
STACK ₹127,351.50 ✓ · STACK+OI-V3 ₹130,711.50 ✓ · STACK+VIX-B1 ₹131,911.50 ✓ · STACK+R4-D1 ₹136,324.50 ✓ ·
merged trade-days also match (131 / 101 / 116) and ₹/trade-day matches (997.80 / 1,306.05 / 1,175.21). No mismatch found.

---

## 1. November day by day (Nov 2–13, 9 trading days; Nov 10 = Diwali holiday)

| Date | Stack net | Mark | +V3 incr | +V3 merged | +B1 incr | +B1 merged | +D1 incr | +D1 merged |
|---|---|---|---|---|---|---|---|---|
| Nov 02 | 0 | NO-TRADE | **+2,480** | **+2,480 GREEN** | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE |
| Nov 03 | 0 | NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE |
| Nov 04 | +2,480 | GREEN | 0 | +2,480 GREEN | 0 | +2,480 GREEN | 0 | +2,480 GREEN |
| Nov 05 | 0 | NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE |
| Nov 06 | 0 | NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE |
| Nov 09 | −1,720 | RED | 0 | −1,720 RED | 0 | −1,720 RED | 0 | −1,720 RED |
| Nov 11 | 0 | NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE | 0 | 0 NO-TRADE |
| Nov 12 | −1,720 | RED | 0 | −1,720 RED | 0 | −1,720 RED | 0 † | −1,720 RED |
| Nov 13 | −1,720 | RED | 0 | −1,720 RED | 0 | −1,720 RED | 0 | −1,720 RED |
| **Total** | **−2,680** | **1 G / 3 R / 5 NT** | **+2,480** | **−200 · 2 G / 3 R / 4 NT** | **0** | **−2,680 · 1 G / 3 R / 5 NT** | **0** | **−2,680 · 1 G / 3 R / 5 NT** |

† R4-D1's family *did* fire on Nov 12 (PE 61300, target +₹2,480) — but the stack also traded that day, so under the
rounds' increment rule it is **not** an increment leg and the merged November is unchanged. VIX-B1 fired no November
legs at all. OI-V3's single increment leg (Nov 02, PE 55000 target +₹2,480) is the only fragment leg that lands in
any merged November line.

**November reading:** no merged configuration is green-day majority in November. The best is STACK+OI-V3
(2 green / 3 red / 4 no-trade, −₹200) — one extra green day vs the stack alone (1 / 3 / 5, −₹2,680).

---

## 2. Jan–Oct 2026 green-day rates (205 trading days)

| Configuration | Total ₹ | Trade-days | Green | Red | No-trade | Green share of trade-days | Green share of all 205 days | ₹ / trade-day |
|---|---|---|---|---|---|---|---|---|
| STACK alone | +127,351.50 | 89 | 60 | 29 | 116 | **67.4%** | 29.3% | 1,430.92 |
| STACK + OI-V3 | +130,711.50 | 131 | 78 | 53 | 74 | 59.5% | **38.0%** | 997.80 |
| STACK + VIX-B1 | +131,911.50 | 101 | 66 | 35 | 104 | **65.3%** | 32.2% | 1,306.05 |
| STACK + R4-D1 | +136,324.50 | 116 | 73 | 43 | 89 | 62.9% | 35.6% | 1,175.21 |

## 3. The answer, in the owner's terms

- **Highest green-day share among the merged configurations: STACK + VIX-B1 — 65.3% of its trade-days are green**
  (66 of 101). Its November counterfactual day-count is **1 green / 3 red / 5 no-trade** (B1 added no November legs;
  merged November = the stack's −₹2,680).
- Two honest qualifiers, same table: the **stack alone** has a higher trade-day green share (67.4%, 60 of 89) than any
  merged configuration — every fragment dilutes the share even while adding money. And on the **all-205-days**
  denominator the leader is **STACK + OI-V3 (38.0%, the most green days outright: 78)**, which also owns the best
  November line (2 green / 3 red / 4 no-trade, −₹200).
- **No configuration is green on more than half of ALL days** — no-trade days dominate every line (74–116 of 205).
  Green-day majority exists only inside trade-days. Any "more than half of all days green" outcome requires a book
  that trades most days — none of the four configurations here does (43–64% of days traded).
- Status reminder: all three fragments remain **unpromoted merge-only evidence** (each passed its round's registered
  numeric merge legs; each standalone gate FAILED). These counts describe history; they promote nothing.

**Day-level data:** `round5_forensic_greenday_days_2026-11-14.csv` — 856 rows: every Jan–Oct day (205) and every
November day (9) for each of the four configurations, with stack net, increment net, merged net and day mark;
totals re-summed from that CSV reproduce every figure above.
