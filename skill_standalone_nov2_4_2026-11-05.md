# Day Trader Skill (Skill V3) — STANDALONE record, Mon 2026-11-02 → Wed 2026-11-04

Scored 2026-11-05 on Chandu's order, for the Nov 2–4 systems scoreboard. **Paper only, real money ₹0, no live orders.** 1 lot (Bank 30 / Nifty 65), cost ₹220/trade.

**Definition:** every Skill V3 key the U1 construction generated on the day — INCLUDING the solo/early legs the frozen primaries blocked (Bank B2 blocks Skill CE and drops solo ≤09:55 keys; Nifty C3 drops solo keys). Here nothing is blocked: if Skill fired, the leg counts. Each leg was re-derived from the day's real spot bars with the frozen U1 machinery (`live_signal_producer.evaluate_legs`) — every known key from the official logs was reproduced exactly, and no additional Skill leg was found on any day. Strike = ATM nearest 100 to spot at the entry bar; expiry = monthly **2026-11-23** both indices (the series the November logs use); entry premium = open of the entry 5-min premium candle. Exits: Bank **G0** (stop −50 / target +90, stop before target incl. entry bar, square-off 15:10); Nifty **G7** (stop −50; +90 → lock entry+50; target +150; square-off 15:10).

## Bank Nifty — Skill standalone

| Date | Leg | Signal → Entry | Entry @ | Exit | Exit @ | Reason | Net ₹ |
|---|---|---|---|---|---|---|---|
| Mon 2026-11-02 | PE 54800 | 10:15 → 10:20 | 681.95 | 10:25 | 631.95 | stop | −1,720.00 |
| Tue 2026-11-03 | CE 55500 | 09:55 → 10:00 | 841.85 | 11:30 | 791.85 | stop | −1,720.00 |
| Wed 2026-11-04 | CE 55800 | 09:30 → 09:35 | 788.00 | 09:35 | 738.00 | stop (entry bar) | −1,720.00 |

Day totals: Nov 2 **−₹1,720.00** · Nov 3 **−₹1,720.00** · Nov 4 **−₹1,720.00**
**3-day total (Bank): 3 trades, 0 targets, −₹5,160.00**

Notes: Nov 2 is the same leg the Bank primary took (B2 kept it — PE, entry after 09:55). Nov 3 and Nov 4 are CE legs the primary blocked under B2; standalone, both stopped for the same −₹1,720.

## Nifty — Skill standalone

| Date | Leg | Signal → Entry | Entry @ | Exit | Exit @ | Reason | Net ₹ |
|---|---|---|---|---|---|---|---|
| Mon 2026-11-02 | CE 23300 | 09:35 → 09:40 | 363.00 | 13:05 | 313.00 | stop | −3,470.00 |
| Tue 2026-11-03 | CE 23600 | 09:45 → 09:50 | 355.75 | 15:10 | 400.50 | square_off | +2,688.75 |
| Wed 2026-11-04 | — | no Skill leg (no OR break 09:30–11:30) | — | — | — | — | ₹0 |

Day totals: Nov 2 **−₹3,470.00** · Nov 3 **+₹2,688.75** · Nov 4 **₹0 (no leg)**
**3-day total (Nifty): 2 trades, −₹781.25**

Notes: both Nifty legs are solo keys the C3 primary dropped by rule. Nov 3 never reached +90 (445.75) and never hit the −50 stop (305.75); it rode to the 15:10 square-off in profit.

## Cross-check

**Bank Nov 2 reproduces the official primary log exactly:** PE 54800, entry 10:20 @ 681.95 → stop 10:25 @ 631.95, **net −₹1,720.00** — identical to `november_paper_bank_log.csv` (PRIMARY and CONTROL rows). No discrepancy.

## Data integrity note

All five legs were scored on full-day monthly-expiry premium series (77 × 5-min bars, 09:15–15:35). A first pass on the Nifty Nov 3 leg picked up a truncated weekly-expiry file (50 bars ending 13:20) from a cache glob and produced +₹3,036.50 — **discarded**; the leg was re-scored on the fetched monthly 2026-11-23 series (entry @ 355.75), giving the +₹2,688.75 above. No leg is NOT_COMPUTED; no premium was estimated. No primary/shadow log or other system's files were modified.
