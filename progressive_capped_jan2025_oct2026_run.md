# Capped progressive backtest — FINAL summary, Jan 2025 to 28 Oct 2026

Paper only, no orders, no live trading. Proprietary to Chandu, workspace only.
Provisional cash rules (NOT Chandu's rules): 100 shares, ₹40/trade, stop = signal-candle low/high, target = 2× stop distance, square-off 15:10, short paper-only, Setup 1 skipped. Indices vs stocks reported separately throughout — index figures are point-scaled cash-equivalents (100 shares × index points), never portfolio rupees, and are never mixed into a stocks verdict.

## Capped rules (fixed in advance, signal-time only)
- Instruments: Nifty, Bank Nifty, 25 stocks (GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR).
- Skill pool OR-only; skill OR passes only if V4-style filters pass (bias-aligned, room ≥ 200×scale to next PD level, PD bound).
- Ranking by setup quality, then room ratio (capped 5.0, unbounded scored 1.0), then bias-strong, then results-gate pass. Results gate stayed NEUTRAL (0) for the whole series — no gate rule was adopted from the v1 patterns in this series.
- Portfolio cap: max 3 trades per ISO week TOTAL per series, max 1 trade per symbol per week.
- Engine: progressive_capped.py, reading ~/workspace/trading/data/progressive/ (Upstox 5-min cache, fetched fresh month by month, Oct 2026 fetched 2026-10-01 to 2026-10-28 only).

## Why this series exists
The raw progressive run gave 621 skill trades in July 2025 (27 instruments × 23 days, 1 per instrument per day, no filter) — too many for stocks, and not progression. Chandu's correction 2026-10-29 08:28 IST stopped the raw run and replaced it with this capped run. Progression, per Chandu, means cumulative profit rising month by month — not another month of losses, and not a total propped up by one index trade.

## Final cumulative results — verified by summing all 22 capped_summary JSONs
| Series | Total net to 28 Oct 2026 | Stocks-only net | Trades | Targets | Win rate |
|---|---|---|---|---|---|
| Capped-V4 | +₹9,014 | −₹33,391 | 320 | 83 | 25.9% |
| Capped-Skill | −₹46,790 | −₹15,070 | 317 | 94 | 29.7% |
| Unified | +₹8,639 | −₹33,766 | 321 | 83 | 25.9% |

Month-by-month nets and splits are in progressive_capped_jan2025_oct2026_progress.md and in capped_summary_YYYY-MM.json (22 files, 2025-01 to 2026-10).

## October 2026 (partial, 1–28 Oct, 18 trading days)
- Capped-V4: 15 trades, 26.7% win, +₹11,242 total (indices +₹16,640, stocks −₹5,398).
- Capped-Skill: 15 trades, 40.0% win, +₹14,389 total (indices +₹16,640, stocks −₹2,251).
- Unified: 15 trades, same as capped-V4 (+₹11,242).
- The entire positive total in all three series is one BANKNIFTY target on 2026-10-01, +₹16,640. Without it, V4 Oct is −₹5,398 and Skill Oct is −₹2,251. Latest capped trade date is 2026-10-26: Oct 27–28 candidates ranked out because the ISO-week cap (W44) was already filled — cap behaviour, not missing data.
- One V4 "target" (NHPC 2026-10-06) nets −₹8 after the ₹40 cost — a target smaller than cost.

## X verdict — FINAL
- Frequency: PASS — 3.0/week, 12–15 trades/month, never 500+. The only X leg that passes consistently.
- Good net profit: FAILS on stocks-only for every series (V4 −₹33,391, Skill −₹15,070, Unified −₹33,766). V4/Unified totals are positive only because of single index trades (Jun 2025 Nifty +₹22,260, Jul 2026 Bank Nifty +₹15,680, Oct 2026 Bank Nifty +₹16,640, May 2025 Bank Nifty net).
- Good win rate: FAILS as proof — 25.9% / 29.7% / 25.9% over 317–321 trades, and Oct's 40.0% skill win rate still lost on stocks.
- **No version hits all three X legs together in this series. NO V5 / skill v2 adopted.** Previous best kept: capped-V4 / capped-Skill as separate series, paper only.
- Candidate fix to test (not adopted): exclude index point-scaled trades from the portfolio cap ranking, or cap index stop/target size, so single Bank Nifty/Nifty trades cannot dominate a month in either direction. A V5 candidate must beat these capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression.

## Corrections to the Sep-2026 brief (found while verifying the final sums)
- Skill trades to Sep 2026 are 302 in the JSONs, not 301 (targets 88, so win 29.1% to Sep, not 29.2%).
- Unified total to Sep 2026 is −₹2,603, not −₹2,228, because Mar 2026 unified (−₹2,854) differs from capped-V4 (−₹2,479); the Sep brief carried V4's total into the unified row. Unified stocks-only to Sep (−₹28,368) was correct.
- Final figures in this file use the verified JSON sums, not the brief's rounded rows.

## Next
This backtest series is COMPLETE (Jan 2025 to 28 Oct 2026). Forward work is November 2026 paper validation of a candidate version under the same cap, paper only — not a continuation of this backtest, and no live order or lot increase until a version is positive on fresh data.
