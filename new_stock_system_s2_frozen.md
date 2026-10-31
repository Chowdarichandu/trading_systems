# S2 — Intraday STOCK system (cash, NOT options) — FROZEN for November paper

**Status: FROZEN 2026-10-29, NOT adopted, NOT a live system. Paper only, no orders.**
- Frozen by delegation: the user said "continue until you feel satisfied" on 2026-10-29
  evening, delegating continuation to the assistant. The candidate bias-only definition
  from the draft is therefore adopted verbatim as written below — it is no longer an
  open question for freezing purposes, but it remains a provisional rule, not Chandu's rule.
- Any Jan–Oct 2026 run of S2 in the continuation report is **in-sample context only**.
  S2's real test is November 2026 paper, starting Mon 2026-11-02, logged daily after
  15:10 in `s2_forward_paper_log.csv`, separate from the Nifty Cluster 2/3 log, with
  no re-tuning during November. Adoption only on net + win rate + frequency together
  on unseen paper.
- If S2 fails the in-sample satisfaction bar in the continuation report, S3/S4/S5 are
  frozen in their own files before scoring; S2 remains the November candidate only if
  it passes, otherwise the passing candidate (if any) replaces it for November.

## S2 rules (exact, frozen)

Carried over unchanged from S1 (`new_stock_system_s1.md` §3), except the two changes
in S2-1 and S2-2:

- Universe: same 25 stocks. Nifty is a confirmation filter only, never traded, never pooled.
- Base signal: old V4 `find_signal` (setups 2/3/4 only; Setup 1 skipped, no Red bands) + bias filter as old (bearish→PE only, bullish→CE only, neutral→both).
- OR filter: OR width / prev close in [0.25%, 3.0%], else no-trade.
- Confirmation (second close): candle after signal must close further in direction than signal close (CE: conf > sig close; PE: conf < sig close). Entry = open of next candle. No rescan, no re-entry that day.
- Structural stop: CE stop = OR low − 0.1% of prev close; PE stop = OR high + 0.1% of prev close. Risk = |entry − stop|; invalid if risk ≤ 0.
- Target: entry ± 2 × risk. Give-back exit: at 1.0 × risk book 50 shares; remaining 50 stop trails to breakeven (entry); remaining target stays 2 × risk; square-off 15:10; bar order stop, then partial, then target.
- No re-entry: one signal, one trade per stock/day.
- Convicted cap: max 3 stock trades/week, max 1/stock/week, prospective full-target net ≥ ₹500 (2 × risk × 100 − 40 ≥ 500). Cap ranking: prospective target net DESC, then room ratio, then setup rank.
- Costs/size: 100 shares, ₹40/trade, square-off 15:10, short paper-only. Win (primary) = net > 0; full-target rate reported alongside, partial-BE wins are NOT full targets.

### S2-1 Room (changed from S1)
Room to the next PD level in direction (PDH/PDC/PDL) must be **finite AND ≥ 1.5 × risk**.
If no PD level lies beyond entry, room fails (infinite room is never a pass).
Target stays entry ± 2 × risk — the target is NOT shrunk to 1.5 × risk.

### S2-2 Nifty confirmation — bias-only (changed from S1, candidate definition adopted verbatim)
At confirmation time, the stock trade is allowed unless Nifty's bias for the day opposes it.
Nifty bias uses the existing bias rule from previous close position in its range:
bearish < 35%, neutral 35–79%, bullish ≥ 80%.
- Allow CE when Nifty bias is bullish or neutral.
- Allow PE when Nifty bias is bearish or neutral.
- Block only the directly opposed direction: CE on a bearish Nifty day, PE on a bullish Nifty day.
Nifty inside its OR no longer blocks a trade by itself.

## Deliberately NOT changed in S2
Second-close confirmation, structural stop, give-back exit, target 2 × risk, no re-entry,
cap, costs. No timing gates, no OR-high stop, no bounce-bar stops, no target-shrink to tiny wins,
no dead Nifty-sweep tricks.

## Engine
`stock_system_continued.py` (function `run_version` with `room_min=1.5`, `nifty_mode='bias_only'`,
`cap_rank='target'` for S2). Trade CSV: `s2_trades_jan_oct_2026.csv`, uncapped `s2_uncapped_jan_oct_2026.csv`.
