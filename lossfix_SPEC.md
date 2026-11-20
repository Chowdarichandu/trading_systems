# LOSS-FLAW DIAGNOSIS + ONE FIX — EKAM INTRADAY CANDIDATES · SPEC
### (frozen 2026-11-17, BEFORE any diagnosis table or fix scoring)

**Owner's order (2026-11-17 10:31 IST):** *"work on the losses and how we can
address in future."* Trigger: today (Tue 2026-11-17) every EKAM entry was a LONG
off the first bar (09:15 signal, 09:20 entry) on a range morning — HDFCBANK
decayed on the next bar (−₹330), GODREJCP stopped −1% (−₹944.25), GLENMARK
decayed at 10:10 (−₹1,480 in BOTH books); ASTRAL/BDL still open at the time of
writing.

**Scope:** paper research only. The frozen live candidates and the November
board do NOT change. Any passing fix becomes a **December candidate proposal
only**. Basis: equity cash intraday, frozen 25 names, **per 100 shares
PROVISIONAL**, ₹40/trade, paper only, real money ₹0. VWAP = equal-weighted
typical-price proxy (stores carry no volume).

## BOOKS (frozen, verbatim machinery — same engine as this morning's stagger test)

- **CAND-T5 ("EKAM Cand-1")** — pre-cap candidates = each stock-day's first
  ≥5-of-6-vote signal (R1 `day_candidates`, T=5); day cap 5 via
  earliest-(signal_stamp, sym) selection (R5 `sel_s0`).
- **S2 ("EKAM Cand-2")** — same candidates; day cap 3, earliest first
  (R5 `sel_s2`).
- Exits (both books, unchanged everywhere in this test): CAND stack
  D=3 / S=1.00% / C=none — vote-decay exit at own-direction votes ≤ 3, hard
  stop −1.00%, no profit cap, square-off at the 15:10 bar's close
  (R2 `net_of` / `exit_x2p` verbatim). Exit detail (price + reason + bar) from
  the stagger test's instrumented copy of the exit loop, asserted equal to
  `net_of`'s implied exit on **every** trade before any stat is trusted.

## CONTROL (must reproduce exactly before anything else is reported)

CAND-T5: 2025 **+₹62,164.57** · 2026 **+₹63,883.60** · Nov (frozen slice)
**+₹24,528.65**
S2:      2025 **+₹45,300.64** · 2026 **+₹72,605.30** · Nov (frozen slice)
**+₹20,662.60**

Checked as full `year_rows` equality (windows, months, ex-top-3, November)
against `ekam_intraday_stocks_r2_results.json` CAND-T5 and the R5 S2 row —
the stagger test's control-check procedure, verbatim. Any mismatch stops the
run. The frozen November slice = the 9 dates 2026-11-02,03,04,05,06,09,11,12,13
(R2 `NOV_DATES`).

## STAGE 1 — DIAGNOSIS (computed and read BEFORE any fix is scored)

Windows, per book, never pooled: **2025 Jan–Oct**, **2026 Jan–Oct**,
**November-to-date** = the engine-scored November days in the frozen store,
2026-11-02..2026-11-16 (10 trading days; the frozen Nov 2–13 subtotal is also
shown). 2026-11-17 is a partial live day and is diagnosed separately in
Stage 3, not here.

Every control trade is split four ways. Each cell reports: trades · net · WR ·
avg win · avg loss.

- **(a) Signal-bar time.** FIRST BAR = the trade's `signal_stamp` is `09:15`
  (the day's first bar). LATER = any other signal stamp.
- **(b) Day type (NIFTY).** From the local NIFTY store
  (`data/sarvaritu_fwd/NIFTY/spot_5m.csv`), per date: O = open of the day's
  first bar, H = max high, L = min low, C = close of the day's last bar.
  **TREND** iff (H−L) > 0 and |C−O| / (H−L) ≥ 0.6; otherwise **RANGE**.
  A date absent from the NIFTY store is UNCLASSIFIED — excluded from split
  (b) only, and the count is reported. The classification is computed once,
  mechanically, before any trade is assigned.
- **(c) Side.** LONG vs SHORT.
- **(d) Exit reason** (instrumented exit loop): `decay` · stop family
  (`stop` + `gap_stop`, also shown separately) · `squareoff`. Split (d)
  additionally reports each reason's share of the book's gross losses
  (sum of negative nets) in that window.

**Diagnosis statement:** the measured flaw is stated in one sentence with
numbers, naming the concentrated cell(s) if any. If the losses are evenly
spread with no concentrated cell, the diagnosis is recorded as *"today is
variance inside a positive book"* and Stage 2 proceeds with the first-bar fix
explicitly as **the owner's live hypothesis**, not as a diagnosis-led fix.

## STAGE 2 — ONE FIX (pre-registered here, before scoring)

**FIRST-BAR CONFIRMATION.** Everything frozen except the treatment of a
candidate whose signal is on the day's first bar:

- A candidate with `signal_stamp == "09:15"` does **not** enter at 09:20.
  It is **confirmed** iff at the **09:25 bar** (signal_li + 2) the
  own-direction votes are **≥ 5** and strictly greater than the other side's
  votes. If confirmed, it enters at the **09:30 bar's open**
  (entry_li = signal_li + 3, entry_stamp `09:30`), keeping
  `signal_stamp = "09:15"` for day-cap selection order.
- If confirmation fails (own votes < 5, tie/loss of the lead, or the bars do
  not exist), the candidate is **void** — that stock does not trade that day.
  Scanning does **not** resume for a later signal for that stock (the first
  signal is the stock-day's candidate; it either enters late or not at all).
- Candidates with any other signal stamp behave **exactly as the control**.
- Day-cap selection is unchanged: surviving candidates sorted by
  (signal_stamp, sym), first 5 (Cand-1) / first 3 (Cand-2). Caps, 1 trade
  per stock per day, −1% stop, decay exit, 15:10 square-off — all frozen.

**PLACEBO — CONFIRM-0920.** The identical mechanic shifted one bar later, to
separate *"the first bar is special"* from *"any delay helps/hurts"* (this
morning's stagger test already showed generic delay costs money): a candidate
with `signal_stamp == "09:20"` does not enter at 09:25; it is confirmed iff
own-direction votes ≥ 5 (and own > other) at the **09:30 bar**, entering at
the **09:35 bar's open**; failure voids the candidate. 09:15 signals and all
other signals behave exactly as the control. Same selection, same exits.

**First-bar cohort (for the verdict bar):** control cohort = control trades
with `signal_stamp == "09:15"`. Fix cohort = fix trades whose originating
signal was `09:15` (i.e. confirmed entries at 09:30). The number of first-bar
candidates voided by failed confirmation is reported per book-year. For the
placebo, the treated cohort is the 09:20-signal trades, reported the same way.

**Gate measures** (fix and placebo, per book): per year — net and % of
control · halves (Jan–Jun vs Jul–Oct) · month table · ex-top-3 · losing-trade
share % · max drawdown (cumulative trade-net sequence in (date, entry_stamp,
sym) order, as in the stagger test) · cluster days (days with ≥ 3 trades
exiting by stop or gap_stop, with the day-total booked on those days) ·
first-bar cohort net vs control. November slice (frozen Nov 2–13) reported
separately, not part of the bar.

## VERDICT BAR — FROZEN BEFORE SCORING

The fix **PASSES for a book** only if, in **BOTH** 2025 and 2026:

1. net ≥ **85%** of the control's net for that book-year, **AND**
2. max drawdown ≤ the control's max drawdown for that book-year
   (drawdowns are negative: fix DD must be ≥ control DD), **AND**
3. losing-trade share **strictly lower** than the control's, **AND**
4. the first-bar cohort's net **improves** vs the control's first-bar cohort
   net for that book-year.

The placebo is not subject to the bar; it is reported beside the fix so the
fix's effect can be attributed. A passing fix is a December candidate
proposal only — nothing live changes. Failed variants are never retested in
identical form.

## STAGE 3 — COUNTERFACTUAL ON TODAY (2026-11-17) + NOVEMBER-TO-DATE

Today's bars: fetched and built with the live producer's own route
(`fetch_today_5m` + `completed_bars` + `build_today_stock` from
`ekam_intraday_live_producer.py`) — bit-identical votes to the live layer,
completed bars only, at the moment of the run.

- **Control replay of today** must first reproduce the live record
  (`ekam_intraday_live_log.csv` / state): Cand-1 closed HDFCBANK −₹330.00
  (decay), GODREJCP −₹944.25 (stop), GLENMARK −₹1,480.00 (decay), open
  ASTRAL/BDL; Cand-2 closed GLENMARK −₹1,480.00, open ASTRAL/BDL. Any
  mismatch is reported plainly and the counterfactual is then computed on
  the replay's own bars for both sides (control and fix on identical bars).
- **Fix on today:** which of today's actual entries the fix would have
  skipped (confirmation failed) or delayed (confirmed → 09:30 entry, with
  the resulting exit/mark), including any replacement candidate the freed
  cap slot pulls in. Positions still open are **marked** at the latest
  completed bar's close (as-if-exited net incl. ₹40, labelled MARK) —
  never presented as closes.
- **November-to-date counterfactual:** Nov 2–13 (frozen slice, full days)
  + Nov 16 (full day, frozen store) + Nov 17 (today so far, marks) —
  control vs fix per book, each piece shown separately and summed.
  Nov 16's control is cross-checked against the live log
  (Cand-1 +₹1,340.00 / 5 trades; Cand-2 +₹1,205.00 / 3 trades) and any
  difference is stated, not smoothed over.

## DELIVERABLES

`lossfix_SPEC.md` (this file) · `lossfix_2026-11-17.md` (diagnosis table,
fix results, gate, today counterfactual) · `lossfix_results.json` ·
`lossfix_trades.csv` (control + fix + placebo trades with exit detail, plus
today's counterfactual rows flagged). Checkpoint after Stage 1: the
diagnosis table and the one-sentence flaw are produced and read before
Stage 2 is scored.
