# Index OPTIONS — highest-tuned v2, delivered 09:00 IST, Fri 2026-10-30
Paper only, no orders. Frozen spec (written before scoring): [index_options_v2_frozen.md](sandbox://workspace/trading/index_options_v2_frozen.md)
Trades: [index_options_v2_october_trades.csv](sandbox://workspace/trading/index_options_v2_october_trades.csv)
Window: full October 2026, 1–28 Oct (18 trading days). Pilot week 19–23 Oct (4 trading days; 20 Oct Dussehra holiday) is a consistency check only.
Nifty and Bank separately, never pooled, never deduped across versions/indices.

## Unit discipline — read this before any rupee number
- Spot provisional = index points × 100 shares − ₹40/trade. This is **NOT an options-lot profit and NOT a futures profit**. It is the complete scoring unit for (lA) v2 and Skill v2, because their option premiums were not computed for most October days.
- Premium net per 1 lot = (exit premium − entry premium) × lot − ₹220 assumed cost (labelled assumption), lot Nifty 65 / Bank 30, stop −50 / target +90 option points, square-off 15:10. Premium overlay exists only for trades already computed in the V4-options report (21/23/26/28 Oct); every other row is NOT_COMPUTED for premium, never converted from spot.
- V4-options premium lesson stands: spot target ≠ premium target (Nifty 23 Oct spot target, premium square-off loss).

## Ranked table — spot provisional (complete), premium subset noted
Frequency = trades ÷ 18 days × 5 (trades/week equivalent). Target: ≥5/week, net>0, full-target ≥50%.

| Rank | Version / index | Trades | Full-targets | Green (net>0) | Spot prov. net | /week | Premium-known subset |
|---|---|---|---|---|---|---|---|
| **1 (Bank)** | **V5-v2 Bank** | 4 | 3 (75%) | 3 | **+₹43,630** | 1.11 | 2 trades: +₹4,960 (21+26 Oct); 2 NOT_COMPUTED |
| **1 (Nifty)** | **(lA) v2 Nifty** | 3 | 3 targets* | 3 (100%) | **+₹28,020** | 0.83 | 1 trade: −₹1,334.75 (23 Oct premium); 2 NOT_COMPUTED |
| 2 (Bank) | (lA) v2 Bank | 4 | 2 targets | 2 (50%) | +₹28,275 | 1.11 | 2 trades: +₹4,960 (21+23 Oct); 2 NOT_COMPUTED |
| 2 (Nifty) | V5-v2 Nifty | 3 | 2 (67%) | 2 | +₹8,195 | 0.83 | 2 trades: −₹4,804.75 (23+26 Oct); 1 NOT_COMPUTED |
| 3 (Bank) | Skill v2 Bank | 9 taken (7 blocked) | 3 (33%) | 3 | +₹8,675 | 2.50 | 0 computed |
| 3 (Nifty) | Skill v2 Nifty | 8 taken (8 blocked) | 2 (25%) | 3 | +₹8,420 | 2.22 | 1 trade: −₹3,470 premium (28 Oct) vs −₹5,470 cash |
| — | Volrix v2 Nifty | 0 | — | — | ₹0 | 0 | 0 triggers |
| — | Volrix v2 Bank | 0 | — | — | ₹0 | 0 | 0 triggers |

\* (lA) "targets" here = morning target exit on a green day (day_net>0, no re-entry); see trade CSV for morning/re-entry split. (lA) v2 Bank 8 Oct day is a new L1 day (signal 13:15, stop, −₹8,510) — L1 adds a loser as well as a winner.

## Highest tuned — verdict
**NO version meets all legs (≥5/week + net>0 + full-target ≥50%). No version is adopted.**
- **Highest tuned overall: (lA) v2** — 7 trades across its two separate tracks, 5 green, +₹56,295 spot provisional combined (tracks kept separate; that sum is a version total, not a portfolio P&L). Per index it is the hits leader on Nifty (3/3) and second on Bank. It fails frequency only (0.83–1.11/week).
- **Highest tuned per index:**
  - **Nifty: (lA) v2** — 3 trades, 100% green, +₹28,020 provisional, +₹9,340/trade. Skill v2 Nifty has better frequency (2.22/week) but only 25% full targets and its net is driven by one 26 Oct square-off (+₹16,550 provisional, 165.90 pts, target not hit) — not a hits profile.
  - **Bank: V5-v2** — 4 trades, 75% targets, +₹43,630 provisional, +₹10,907/trade, at the same frequency as (lA) v2 Bank. (lA) v2 Bank is second (+₹28,275, 50% green).
- **Frequency leader, hits failure: Skill v2** — 17 taken trades (Nifty 8 + Bank 9), 2.22–2.50/week, the closest to 5/week, but 25–33% full targets and the lowest nets. S1 blocking is heavy: 15 raw signals blocked (8 Nifty, 7 Bank: CE-on-bearish and 09:30-PE-not-below-PDL).
- **Premium-known subset reverses the spot story for V5/Skill/(lA) on the overlapping days:** V5-v2 premium-known Nifty −₹4,804.75 (vs +₹8,195 cash on its full track, different trade sets), Bank +₹4,960; (lA) v2 premium-known Bank +₹4,960, Nifty −₹1,334.75. Premium scoring for the full month is incomplete — do not rank versions on premium alone until it is complete.

## What v2 changed, per version (vs base, October)
- **V5-v2:** base V5 October unchanged as a pool (7 trades, 71.4%, +₹51,825 provisional: Nifty 3/+₹8,195, Bank 4/+₹43,630). V5-v2 adds only the premium overlay above; no new pool rule was scored in the time to 09:00.
- **Skill v2 (S1):** Nifty 8 taken / 8 blocked, net +₹8,420 provisional (targets 6 Oct +₹4,240, 8 Oct +₹5,440; square-off 26 Oct +₹16,550; stops 5/7/12/27/28 Oct). Bank 9 taken / 7 blocked, net +₹8,675 provisional (targets 1 Oct +₹16,640, 5 Oct +₹25,690, 23 Oct +₹14,860). S1 vs raw: raw Skill October (capped variant in earlier reports) was Nifty 2 trades / Bank 1 trade; S1 raw taken is far more frequent but far less selective — the bias block and 09:30-PE block together still admit 17 trades.
- **(lA) v2 (L1):** Nifty 3 days (8 Oct target +₹11,690; **21 Oct NEW L1 target +₹4,940, signal 11:35** — the exact 5-minute window miss from the pilot week, now captured; 23 Oct target +₹11,390), net +₹28,020 vs base (lA) Nifty October 2 trades / +₹23,080. Bank 4 days (7 Oct loss −₹7,475; **8 Oct NEW L1 stop −₹8,510, signal 13:15**; 21 Oct target +₹20,200; 23 Oct target +₹24,060), net +₹28,275 vs base (lA) Bank uncapped 3 trades / +₹36,785. L1 verdict: adds 1 winner (Nifty) and 1 loser (Bank) — net L1 effect −₹3,570 on the two new days combined, before any re-entry effect. L1 is NOT a proven improvement.
- **Volrix v2:** trigger scan, full October: no previous-day close ≤ −2% for either index (Nifty min −1.64% on 8 Oct; Bank min −1.16% on 23 Oct). 0 trades, ₹0, by design — not a failure to run, and not counted toward the daily bar. Its history (~30 entries in ~7 years) means it cannot meet 1/day by construction; it stays an occasional overlay.

## Pilot-week consistency check (19–23 Oct, 4 days)
- (lA) v2: Nifty 2 trades (21 Oct L1 +₹4,940, 23 Oct +₹11,390), Bank 2 trades (21 Oct +₹20,200, 23 Oct +₹24,060) — consistent with base, plus the L1 winner.
- Skill v2: Nifty **0 taken in the pilot week** (21/22 Oct CE blocked as bearish, 23 Oct 09:30 PE blocked as not below PDL) — **discrepancy flagged:** the pilot-week S1 proposal expected S1 to keep the 23 Oct Nifty PE target, but as coded (first OR signal of the day, 09:30, close ≥ PDL) it blocks it. S1's 09:30-PE rule needs re-examination before S1 is used again; do not quote S1 pilot Nifty as a pass.
- Skill v2 Bank pilot: 1 taken (23 Oct target +₹14,860); 21/22 Oct CE blocked as bearish.
- V5-v2 pilot: Nifty 1 (23 Oct), Bank 2 (21+23 Oct) — same as base V5 pilot subset.
- Volrix pilot: 0 triggers (see above).

## Next family (tuning continues, per standing requirement — not closed)
1. **Premium completion first:** fetch option candles for all October (lA) v2 / Skill v2 / V5-v2 trades via the browser-fetch route (script token only), so ranking is on premiums, not spot provisional. Until then, no premium ranking is claimed.
2. **Skill v2 next family:** re-examine the 09:30-PE rule against the 23 Oct Nifty case (signal-bar vs second-close, PDL measured on close vs low) before re-scoring S1; do not loosen room to rescue frequency.
3. **(lA) v2 next family:** L1 is neutral-to-negative on October (1 win, 1 loss); the next family is not a wider window — it is the O1 cross-confirmation persistence family from the pilot week (confirmer still below its OR low on both signal and entry bars), scored on Jan–Oct per track.
4. **Frequency:** no version is close to 5/week (best 2.50/week, Skill v2 Bank). Reaching 1/day with convicted setups only will require new setup definitions, not cap/filter loosening — that is the next design question, not a claim made here.

## Validation still required
Nothing adopted on October alone. Next: full-October premium scoring, then November 2026 paper from Mon 2026-11-02 (separate Nifty/Bank logs, no re-tuning during November). A version is adopted only if it progresses on net + win rate + frequency together on unseen data.
