# TRIO-IND — SPEC (frozen before scoring, 2026-11-15)

Owner's question (2026-11-15): if TRIO is used WITH indicators —
specifically EKAM-style vote agreement at the moment of entry — do
the chances / accuracy increase? This build MEASURES the one
conditioning surface not yet tested on TRIO: vote agreement at
entry. Research only — no book, ledger or job is changed.

Prior measured context (stated, not re-argued):
- Indicator conditioning on these books has mostly FAILED: the
  Phase-3 buildup / volume / speculation surfaces all gate-failed
  on the Bank stack and on Nifty TUNED v1 (both directions).
- The one success was the Bank CONFIDENCE score (a composite, not
  indicator agreement): stack WR 59.5% -> 62.5% keeping 96.1% of
  profit; on forward shadow, adoption decided Nov 30. It FAILED
  on Nifty and on Stocks.
- In the SOLID-60 study, agreement was BACKWARDS: the more systems
  agreed, the LOWER the win rate. The DISAGREE row below exists
  because of that finding and is reported as its own row.

## 1. The vote (EKAM-intraday's frozen vote, per segment build)

On 5-min spot bars, per completed bar, directional votes 0/1 each:
1. VWAP side (close vs session VWAP; basis per segment build —
   Bank: spot close vs futures session VWAP mapped to the bar;
   Nifty: futures close vs futures VWAP; Stocks: equal-weighted
   typical-price session VWAP proxy, stores carry no volume).
2. EMA(9,21) trend. 3. Supertrend(7,3) direction.
4. MACD(12,26,9) line vs signal. 5. RSI(14) zone
   (long 50<=RSI<70, short mirror per segment build).
6. ADX(14)>=20 adds +1 to the side leading on votes 1-5 (tie: none).
Final counts L, S, each 0..6. Computed CAUSALLY (indicators are
trailing recursions on bars up to and including the vote bar).
Implementation: each segment's own EKAM-intraday build code,
replicated verbatim (Bank: ekam_intraday_bank_build.py on the
2026-01-01..2026-11-13 filtered series; Nifty:
ekam_intraday_nifty_build.py on its full stored series; Stocks:
ekam_intraday_stocks_build.py build_stock / votes_at on
data/sarvaritu_fwd stores).
VALIDATION (before any TRIO leg is scored): the recomputed votes
must reproduce the stored signal_votes of the EKAM builds' own
trades (Bank results JSON, Nifty trades CSV, Stocks trades CSV)
at their signal bars. Mismatches are counted and reported; a
segment whose validation fails is not scored.

## 2. Legs under test (the REPAIRED TRIO lead lines, stored legs)

- BANK: TUNED STACK v2 + B-FIX-1 kept legs,
  november_books_fix_repair_bank_legs.csv (Jan-Oct 2026) +
  November legs derived from november_shadow_stack_bank_log.csv
  by the frozen B-FIX-1 stand-down (bank_bfix1_score.py logic).
  CONTROL (Jan-Oct kept legs) must reproduce +Rs1,31,510.00
  exactly; November kept legs must total -Rs3,440.00.
- NIFTY: TUNED v1 + N-FIX-1 kept legs,
  november_books_fix_repair_nifty_legs.csv (Jan-Oct) + November
  v1 legs from nifty_nfix1_score.py's derivation with the N-FIX-1
  stand-down applied. CONTROL must reproduce +Rs1,17,170.00
  exactly; November kept legs = 0 (total Rs0).
- STOCKS: the raw Stock Book (adopted Variant C),
  stocks_engine_adoptedC_book2025_trades.csv (Jan-Oct only;
  Nov-Dec 2025 legs are outside the adopted window, excluded) +
  stocks_engine_adoptedC_book2026_trades.csv (Jan-Oct) +
  November from stocks_sarvaritu_paper_log.csv. CONTROLS must
  reproduce the published totals: 2025 +Rs1,19,813.44 (1,064
  trades), 2026 Jan-Oct +Rs2,47,178.79 (1,363), Nov +Rs7,517.94
  (32). Basis: per 100 shares PROVISIONAL, Rs40/trade in nets.

## 3. Vote state per leg

The vote state is taken at the bar JUST BEFORE the leg's entry:
the last completed 5-min bar of the leg's day with bar-start time
< entry_time (entry at 09:55 reads the 09:50 bar). Leg side:
CE/LONG -> own = L, opposite = S; PE/SHORT -> own = S, opp = L.
If no such bar exists, or the vote is undefined at that bar
(warm-up / VWAP unavailable in the stocks build's sense), the leg
is NC for the vote rows: counted, never estimated; it stays in
the ALL control row only.

## 4. Rows (per line, per window)

- ALL — every kept leg (the control).
- AGREE>=4 — own-side votes >= 4 at the pre-entry bar.
- AGREE>=5 — own-side votes >= 5.
- DISAGREE>=4 — OPPOSITE-side votes >= 4 (the SOLID-60 warning
  row; reported on its own, never buried).
Windows: Jan-Oct (primary; halves Jan-Jun / Jul-Oct), November
descriptive. Stocks: per year (2025, 2026) + November.
Per row: legs kept, net, WR (win = net > 0), Rs per trade,
distinct trade-days, Rs per trade-day, halves (net + legs + WR).

## 5. Verdict (per line, frozen)

An agreement row HELPS iff, on the primary window, its WR is
strictly above the ALL row's WR AND its net >= 80% of the ALL
row's net. Stocks: the row must satisfy this in BOTH years.
Report per line: control WR/net, best agreement row WR/net,
verdict — or NONE.

Paper only, real money Rs0. Buying only (all legs are buys).
Outputs: trio_ind_2026-11-15.md + trio_ind_results.json.
Build: trio_ind_build.py. Frozen 2026-11-15, before scoring.
