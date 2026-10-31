# S2 — Proposed intraday STOCK system (cash, NOT options) — DRAFT FOR APPROVAL, NOT FROZEN, NOT ADOPTED

**Status: DRAFT ONLY, prepared 2026-10-29 evening.**
- This draft is **not** a frozen system, **not** a backtest, **not** an adoption, and **not** a live system.
- **Paper only. No orders. No lot increase.**
- It becomes S2 only when Chandu approves the two changes in §2 (including
  the exact bias-only definition, which is still open — see §2, open question).
  Until then, S1 remains the last frozen stock system, and S1 itself failed
  and was not adopted.
- **Do NOT score S2 on Jan–Oct 2026 to claim a pass.** Any Jan–Oct run after
  freezing is in-sample context only, labelled as such. S2's first real test
  is November 2026 paper, logged daily, with no scoring or re-tuning during
  November — the same discipline as the Cluster 2/3 November log.

**Why this draft exists now:** on 2026-10-29 Chandu confirmed the index lead
is secured on paper (Nifty (lA) +₹71,780 Jan–Oct 2026, 24 trades, 79.2%,
paper-only, not adopted) and that **stocks are now the focus**. S1 cut the
old stock loss to −₹1,876 but failed on strictness/frequency, so S2 is next.
November paper starts **Monday 2026-11-02**, so S2 must be frozen *before*
Monday if it is to be paper-logged in November at all.

**Source:** `new_stock_system_s1.md` (S1 frozen rules, funnel, verdict) and
the 2026-10-29 main-chat S2 approach: loosen room and Nifty confirmation,
keep the rest frozen, restore CE / setup2 / setup4 trades.

---

## 1. What S1 proved (the problem S2 must fix)

From `new_stock_system_s1.md` §4, Jan–Oct 2026, 25 stocks, cash intraday:

- S1 capped: **18 trades, −₹1,875.94, 0.42 trades/week**, full-target rate
  22.2% (tied with V4 stocks 22.7% and Skill stocks 22.4%).
- **All 18 trades were setup3 bounce-rejection PE (short).** No CE trade,
  no setup2/4 trade survived all S1 filters. 14 of 25 stocks had zero S1 trades.
- Filter funnel (5,075 stock-days): 910 signals → 443 second-close →
  **140 finite room** → **38 Nifty confirmation** → 19 target ≥ ₹500 → 18 capped.
  The cap was not the problem (only 1 trade capped out). Room and Nifty
  confirmation together were too strict.

S2 therefore changes **only** those two filters. Everything else is carried
over unchanged from S1 (§3 below), so any November difference is attributable
to those two changes, not to a wholesale re-tune.

## 2. The two proposed S2 changes (approval needed)

| # | S1 (frozen) | S2 proposed | Reason |
|---|---|---|---|
| S2-1 Room | Room to next PD level must be finite AND ≥ 2 × risk | Room must be finite AND **≥ 1.5 × risk**; target stays entry ± 2 × risk | Room ≥ 2 × killed 303 candidates after confirmation. 1.5 × loosens room without removing the finite-room rule (infinite room still fails) and without shrinking the target to a tiny win. |
| S2-2 Nifty confirmation | At confirmation time, Nifty's last closed 5-min candle must be on the same OR side (CE: close > Nifty OR high; PE: close < Nifty OR low); Nifty inside its OR = no trade | **Bias-only confirmation** (not OR-side): the stock trade is allowed unless Nifty's bias for the day opposes it | Nifty OR-side killed 102 candidates. A stock that moves before Nifty leaves its OR should not be blocked for that alone. |

**OPEN QUESTION — do not freeze S2 until Chandu answers this one question:**
"Bias-only" needs one exact definition. Candidate definition, for approval
(not assumed): use the existing S1 bias rule (bearish < 35%, neutral 35–79%,
bullish ≥ 80%, from previous close position in its range) and allow CE when
Nifty bias is bullish or neutral, PE when Nifty bias is bearish or neutral,
and block only the directly opposed direction (CE on a bearish Nifty day,
PE on a bullish Nifty day). If Chandu defines it differently, his definition
replaces this candidate verbatim before freezing.

**Deliberately NOT changed in S2:** second-close confirmation, structural
stop (OR low − 0.1% / OR high + 0.1%), give-back exit (partial 50 at 1 × risk,
rest trail to breakeven), no re-entry, cap (max 3 stock trades/week,
max 1/stock/week, prospective full-target net ≥ ₹500), 100 shares,
₹40/trade, 15:10 square-off, setups 2/3/4 only (Setup 1 skipped, no Red bands
for stocks), short paper-only.

## 3. S2 rules carried over unchanged from S1

- Universe: the same 25 stocks. Nifty is a confirmation filter only, never
  traded in this system and never pooled into a stock total.
- Base signal: old V4 `find_signal` (setups 2/3/4) + bias filter as old.
- OR filter: OR width / prev close in [0.25%, 3.0%], else no-trade.
- Confirmation: candle after signal must close further in direction than
  signal close; entry = open of next candle; no rescan, no re-entry that day.
- Structural stop: CE stop = OR low − 0.1% of prev close; PE stop = OR high
  + 0.1% of prev close. Risk = |entry − stop|.
- Give-back exit: at 1.0 × risk book 50 shares; remaining 50 stop trails to
  breakeven; remaining target 2 × risk; square-off 15:10; bar order stop,
  then partial, then target.
- Cap ranking: prospective target net DESC, then room ratio, then setup rank.
- Win (primary) = net > 0, with full-target rate reported alongside, so
  partial-BE wins (+₹108–₹148 in S1) are visible and not counted as targets.

## 4. November 2026 paper — how S2 is tested (separate from Cluster 2/3 log)

- **Scope:** S2 stock signals only, every trading day in November 2026,
  starting Monday 2026-11-02, logged daily after 15:10. This log is separate
  from `cluster23_forward_paper_log.csv`, which is Nifty-only (Nifty (lA) PE
  + setup4 reclaim CE) and must not be mixed with stock rows.
- **Log every signal, not only trades:** for each stock-day signal, record
  the filter stage it failed at (OR / no-signal / second-close / room /
  Nifty-bias / target-≥₹500 / cap) or, if it traded, entry/stop/target/
  partial/exit/net. No-trade days and filter-killed signals are part of the
  sample — dropping them would hide whether S2 actually restored CE and
  setup2/4 trades.
- **First diagnostic (month-end only):** the same funnel as S1 §4, plus a
  per-stock funnel for the 14 zero-trade S1 stocks (no signal vs
  filter-killed, per stock). Target diagnostic: ~2–3 stock trades/week,
  CE and setup2/4 trades present, without returning to tiny wins or
  infinite-room passes.
- **Adoption bar (unchanged):** adopt only if S2 progresses on net + win
  rate + frequency together on unseen November paper, with cumulative
  profit rising month by month — not on a November total alone, and not
  on any Jan–Oct re-score.
- **No re-tuning during November.** If S2 fails in November, it is logged
  as failed and the next version is frozen after November, not patched
  mid-month.

**Template:** `s2_forward_paper_log.csv` in this directory (empty, header only).

## 5. What this draft does NOT do

- It does not run S2 on Jan–Oct 2026, does not quote an S2 Jan–Oct net,
  win rate, or trade count, and does not claim S2 beats S1.
- It does not change the index paper: Nifty (lA) November paper continues
  separately, and index and stock totals are never pooled.
- It does not book, order, or authorise any trade. Paper only.
