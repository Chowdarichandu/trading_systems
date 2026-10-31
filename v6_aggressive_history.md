# V6 Aggressive Tuning — History First (Jan–Oct 2026, index only)

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday only, provisional rules (NOT Chandu's live options rules):
100 shares equivalent (index points × 100), ₹40/trade assumed cost,
signal-candle stop, 2× target, square-off 15:10, short paper-only.
Index nets are point-scaled cash-equivalents, NOT portfolio rupees.

## Request

Chandu, 2026-10-29 10:48 IST: "Tune more aggressively, then test on
November paper and history first." Order: history first, November paper
second. November has not happened yet, so November paper is prepared
in `v6_november_paper_spec.md` — it is NOT run here, and no November
data is fabricated.

V5 is NOT adopted (see `v5_index_banknifty_nifty_jan_oct_2026.md`:
72 trades, 41.7% win, +₹64,380, below V4 index +₹68,770 / 43.5%).
V6 is a new candidate, not a rename of V5.

## V6 definition (provisional choices labelled, NOT Chandu's rule)

Chandu only said: tune aggressively, Nifty first, history first.
Everything below that is not in his words is provisional and labelled:

- Pool: V5 index pool — V4 index + Skill index candidates, deduped by
  symbol+date keeping higher conviction, NIFTY and BANKNIFTY only,
  NO stocks, Jan 2026 to 28 Oct 2026 (Oct = 1–28 Oct, 29 Oct excluded).
- Conviction only: setup_rank ≥ 2 — setup4 reclaim/pullback (=3) and
  setup3 bounce rejection (=2) only. setup2 OR breakout/breakdown (=1)
  and skill OR (=0) are DROPPED.
- Nifty first: in pooled variants, Nifty candidates rank before Bank
  Nifty candidates at the same setup rank.
- Higher prospective target filter: ≥ ₹1,000 or ≥ ₹1,500 on the ORIGINAL
  2×-risk target (net of ₹40 cost), vs V5 ₹500.
- Cap: max 3 index trades/ISO week, max 1 trade/symbol/week
  (2/week practical max with 2 symbols, as in V5).
- Stop-cap sensitivity: losing trades floored at −₹5,040
  (50 points × 100 shares + ₹40 cost). This is an UPPER-BOUND
  sensitivity only: it keeps original target wins and only truncates
  losses. A true 50-point stop would also shrink targets to 100 points
  (₹9,960 max) and change exit timing, so floored numbers must NOT be
  read as a real backtest of a 50-point stop rule.
- Walk-forward: tune Jan–Jun 2026, validate Jul–Oct 2026 unseen.
  A variant that only looks good on Jan–Oct tuned together is NOT
  a progression.
- Engine: `v6_index.py`. Month JSONs:
  `data/progressive/v6_index_summary_2026-MM.json` (MM = 01–10).

## Variants tested

| Variant | Scope | Target filter | Stop floor |
|---|---|---|---|
| V6-A | Nifty only | ≥ ₹1,000 | No |
| V6-B | Pooled, Nifty first | ≥ ₹1,000 | No |
| V6-C | Pooled, Nifty first | ≥ ₹1,500 | No |
| V6-D | Nifty only | ≥ ₹1,500 | No |
| V6-E | Pooled, Nifty first | ≥ ₹1,000 | Yes (upper bound only) |
| V6-F | Nifty only | ≥ ₹1,000 | Yes (upper bound only) |

Threshold note: ₹1,000 vs ₹1,500 give IDENTICAL picks in every month
(V6-B = V6-C, V6-A = V6-D). Every conviction trade that passes ₹1,000
also passes ₹1,500 in this pool, so the threshold choice is not a
tuning lever here — do not present ₹1,500 as an improvement.

## Headline finding — aggressive conviction-only collapses frequency

Dedup pool Jan–Oct 2026: 114 candidate days.
Conviction pool (setup4/3 only): 15 days.
- Jan 1, Feb 1, Mar 0, Apr 2, May 1, Jun 2, Jul 3, Aug 1, Sep 0, Oct 4.
- March 2026 and September 2026 have ZERO conviction trades.
  V5's March profit (+₹99,805) came entirely from setup2/OR trades
  that V6 drops — so V6 cannot reproduce March, by construction.
- Nifty-only conviction pool Jan–Oct: 3 trades total (Jan 1, Jul 1,
  Oct 1). Nifty-first + conviction-only, on this pool, is effectively
  a no-trade system for Nifty.

## Month by month — V6-B pooled, Nifty first, ≥ ₹1,000, no floor (candidate)

| Month | Trades / win / net | Bank Nifty | Nifty |
|---|---|---|---|
| Jan 2026 | 1 / 0.0% / −₹2,785 | 0 / ₹0 | 1 / −₹2,785 |
| Feb 2026 | 1 / 0.0% / −₹10,655 | 1 / −₹10,655 | 0 / ₹0 |
| Mar 2026 | 0 / — / ₹0 | 0 / ₹0 | 0 / ₹0 |
| Apr 2026 | 2 / 0.0% / −₹32,920 | 2 / −₹32,920 | 0 / ₹0 |
| May 2026 | 1 / 100.0% / +₹15,660 | 1 / +₹15,660 | 0 / ₹0 |
| Jun 2026 | 2 / 0.0% / −₹12,540 | 2 / −₹12,540 | 0 / ₹0 |
| Jul 2026 | 3 / 66.7% / +₹15,360 | 2 / +₹11,120 | 1 / +₹4,240 |
| Aug 2026 | 1 / 0.0% / −₹7,455 | 1 / −₹7,455 | 0 / ₹0 |
| Sep 2026 | 0 / — / ₹0 | 0 / ₹0 | 0 / ₹0 |
| Oct 2026 (1–28) | 4 / 50.0% / +₹14,795 | 3 / +₹23,430 | 1 / −₹8,635 |

## Walk-forward: tune Jan–Jun vs validate Jul–Oct

| Variant | Tune Jan–Jun: trades / win / net | Validate Jul–Oct: trades / win / net | Full Jan–Oct: trades / win / net |
|---|---|---|---|
| V6-A Nifty only ≥1000 | 1 / 0.0% / −₹2,785 (NF only) | 2 / 50.0% / −₹4,395 (NF only) | 3 / 33.3% / −₹7,180 |
| V6-B pooled ≥1000 | 7 / 14.3% / −₹43,240 (BN −₹40,455, NF −₹2,785) | 8 / 50.0% / +₹22,700 (BN +₹27,095, NF −₹4,395) | 15 / 33.3% / −₹20,540 (BN −₹13,360, NF −₹7,180) |
| V6-C pooled ≥1500 | identical to V6-B in all periods | identical to V6-B | identical to V6-B |
| V6-D Nifty only ≥1500 | identical to V6-A | identical to V6-A | identical to V6-A |
| V6-E pooled ≥1000, stop floor (upper bound) | 7 / 14.3% / −₹11,200 floored (raw −₹43,240, saving ₹32,040) | 8 / 50.0% / +₹28,710 floored (raw +₹22,700, saving ₹6,010) | 15 / 33.3% / +₹17,510 floored (raw −₹20,540, saving ₹38,050) |
| V6-F Nifty only ≥1000, stop floor (upper bound) | 1 / 0.0% / −₹2,785 floored (no saving) | 2 / 50.0% / −₹800 floored (raw −₹4,395, saving ₹3,595) | 3 / 33.3% / −₹3,585 floored (raw −₹7,180, saving ₹3,595) |

## Large stops — what the stop cap actually blocks

Conviction pool, trades with net below −₹5,040 (before cap, before
target filter is irrelevant here — all are in the conviction pool):
- Jan–Jun: 4 trades, all Bank Nifty, net sum −₹52,200.
  (Feb Bank Nifty −₹10,655; Apr two Bank Nifty stops totalling
  −₹32,920; Jun one Bank Nifty stop −₹8,625 in the pool.)
- Jul–Oct: 2 trades, Bank Nifty 1, Nifty 1, net sum −₹16,090.
- Jan–Oct: 6 trades, Bank Nifty 5, Nifty 1, net sum −₹68,290.
- In the capped V6-B picks, the floor saves ₹38,050 over Jan–Oct
  (Jan–Jun ₹32,040, Jul–Oct ₹6,010) — but even floored, the tune
  period (Jan–Jun) is still −₹11,200, so the floor does not turn the
  tune period positive. It is not a fix on its own, and as noted it
  is optimistic because a true 50-point stop would shrink targets.

## Comparison to V5 and V4 index (same window, index only)

| Series | Jan–Jun: trades / win / net | Jul–Oct: trades / win / net | Jan–Oct: trades / win / net |
|---|---|---|---|
| V5 index | 44 / 38.6% / +₹41,610 | 28 / 46.4% / +₹22,770 | 72 / 41.7% / +₹64,380 |
| V4 index (capped-v2 leg) | — | — | 62 / 43.5% / +₹68,770 |
| Skill index (capped-v2 leg) | — | — | 58 / 43.1% / +₹40,240 |
| V6-B pooled (candidate) | 7 / 14.3% / −₹43,240 | 8 / 50.0% / +₹22,700 | 15 / 33.3% / −₹20,540 |
| V6-A Nifty only | 1 / 0.0% / −₹2,785 | 2 / 50.0% / −₹4,395 | 3 / 33.3% / −₹7,180 |

Frequency: V6-B = 15 trades in 10 months = ~0.35/week, vs V5
1.47/week. V6-A = 3 trades in 10 months = ~0.07/week. Both fail any
reasonable frequency leg — a system that trades 3 times in 10 months
cannot be judged on win rate, and cannot be a progression on
frequency.

## Verdict — NO V6 variant progresses, NO version adopted

- Net: FAILS. Best non-floor variant (V6-B) is −₹20,540 Jan–Oct,
  negative on tune (−₹43,240) and positive only on validation
  (+₹22,700 on 8 trades) — and validation's +₹22,700 is itself
  July (+₹15,360) plus October (+₹14,795) minus August (−₹7,455)
  and a zero-trade September. That is not a stable progression.
- Win rate: FAILS vs inputs. V6-B 33.3% Jan–Oct is below V5 41.7%,
  V4 index 43.5%, and Skill index 43.1%. Validation win 50.0% is on
  8 trades only.
- Frequency: FAILS badly. 15 trades (pooled) / 3 trades (Nifty only)
  in 10 months vs V5 72 trades. Aggressive filtering did not
  improve quality per trade enough to compensate — it removed the
  trades that made V5's total, including all of March.
- Nifty first, on this pool: does NOT help. Nifty-only conviction
  gives 3 trades and −₹7,180. Nifty's Jan–Oct advantage inside V5
  (+₹47,965 on 32 trades, vs Bank Nifty +₹16,415 on 40) came from
  setup2/OR Nifty trades that conviction-only drops. "Nifty first"
  as a ranking priority inside the pooled variant does not change
  the picks much either — Bank Nifty still dominates V6-B
  (12 of 15 trades, −₹13,360), because Nifty conviction candidates
  barely exist in this pool.
- Stop floor: does NOT rescue V6. Even floored (upper bound),
  V6-B Jan–Oct is only +₹17,510, tune period still negative, and
  the floor is optimistic for the reason stated above.
- Therefore: NO V6 variant is adopted. Previous best kept for
  index: V4 index as a separate series, paper only. V6-B is carried
  forward ONLY as the November paper candidate (see spec), so that
  November can falsify or support it on unseen data — not as an
  adopted version.

## What aggressive tuning actually revealed (for the parent to put to Chandu)

1. Conviction (setup4/3) is rare in the index pool after dedup:
   15 of 114 days. The index edge in V5, such as it was, lived in
   setup2/OR breakouts — including all of March.
2. Nifty-first cannot be tested properly on a conviction-only pool
   because Nifty conviction trades almost do not occur (3 in 10
   months). If Chandu wants Nifty first, it needs a Nifty pool that
   is not conviction-only, or a different Nifty setup definition —
   that is a new definition to ask him for, not something to invent.
3. The large-stop problem is real but concentrated: 6 conviction
   stops below −₹5,040, 5 of them Bank Nifty, totalling −₹68,290.
   A true capped-stop re-run (50-point stop, 100-point target,
   re-evaluated bar by bar) is still untested and is the honest
   next test if the stop cap is to be pursued — the floor numbers
   here are not that test.
