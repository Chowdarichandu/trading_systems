# Index OPTIONS v2 — frozen before scoring (2026-10-30, deadline 09:00 IST)
Paper only, no orders. Index = options only; no futures trades/totals.
Nifty and Bank Nifty separately, never pooled, never deduped across versions/indices.
Window: full October 2026, 1–28 Oct (18 trading days); pilot week 19–23 Oct (4 trading days, 20 Oct Dussehra holiday) as consistency check only.
Target per version per index: ≥5 trades/week = 1/day, decent return, decent hits (full targets, not partials). No forcing.

## V5-v2 (pooled V4+Skill, options)
- Pool = V4 index candidates + Skill index candidates (OR-only, bias-aligned, room ≥200×scale, PD bound), dedup same symbol+date by setup rank (setup4>setup3>setup2>skill OR), then prospective net, bias-strong, room ratio. Filter prospective target net ≥₹500 (provisional cash unit, labelled).
- V5-v2 change vs V5: scored on option premiums where candles exist (entry = first 5-min option candle open after spot signal, stop −50 / target +90 option points, 1 lot: Nifty 65 / Bank 30, cost ₹220 assumed, labelled; square-off 15:10). Where premiums unavailable, spot points + provisional per-100-shares are shown and labelled NOT an options profit, with the gap stated. Cap: max 1 trade/symbol/week per version track (the attainable index cap with 2 symbols), prospective ≥₹500.
- Base V5 October (from frozen v5_index_summary_2026-10.json): 7 trades, 71.4%, +₹51,825 provisional.

## Skill v2 (S1 family)
- Base = Day Trader skill OR signal per day (find_skill_signal, OR only), outcome via skill_or_outcome (entry next open, stop signal high/low, target 2× risk, square-off 15:10).
- S1 change, frozen: (a) a 09:30 signal bar is taken for PE ONLY when its close is below PDL; a 09:30 PE signal closing at/above PDL is blocked; (b) CE on a bearish-bias day (prev close position <35%) is blocked; (c) all other raw OR signals kept. No other filter change. Scored on spot provisional + premiums where available (see V4 premium overlay); capped variant (bias-aligned + room filters) shown side by side, not merged.

## (lA) v2 (L1 family)
- Base = (lA): BN-confirmed rescan morning (Nifty) / Nifty-confirmed mirror (Bank, provisional), PE only, rescan = first bar ≥ confirmer break, ≤11:30, close < OR low AND < PDL, OR width ≤360×scale, room ≥200×scale, target 2× risk, re-entry risk in [10, rescan risk], morning scan-skip to 11:30, afternoon stop-on-first-fail to 15:05.
- L1 change, frozen: rescan cutoff extended 11:30 → 13:30 ONLY where the confirming index broke before 11:30. All else unchanged (including confirmer-break window, OR-width, room, re-entry rules). No re-entry rule change.

## Volrix v2 (overlay, not a daily version)
- Frozen translation: previous-day underlying close down ≥2% → next session 09:16, LONG ATM CALL, monthly expiry 0, 1 lot, no stop/target, 5-session hold, 10-session cooldown. Futures entry = options entry. By construction ~30 entries in ~7 years; it cannot meet 1/day and is never counted toward the daily bar. Trigger scan for October + premium outcome if any trigger fires in October; otherwise 0 trades, reported as 0, not as a failure to run.

## Ranking (highest tuned)
Rank per index, then overall, by net + win/full-target rate + frequency TOGETHER, not net alone. A version meeting all three legs (≥5/week, net>0, full-target ≥50% on its track) outranks a higher-net version failing frequency or hits. Nothing adopted on October alone; November 2026 paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November) is validation.
