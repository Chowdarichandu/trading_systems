# STAGGERED-ENTRY TEST — EKAM INTRADAY CANDIDATES · SPEC
### (frozen 2026-11-17, BEFORE any variant scoring)

**Owner's question (2026-11-17 10:12 IST):** today (Tue 2026-11-17) all 8 live EKAM
entries fired at 09:20 off the same 09:15 bar, and three stopped/decayed together
within the hour. *"What if we take positions in different time intervals? How would
they impact our loss proportion? Can you do that?"*

**What this test does:** change ONLY the entry timing of the two frozen EKAM
intraday candidates and measure whether staggering decorrelates the losses or
merely trades less. Paper research only; nothing live is mutated; the frozen live
candidates stay exactly as they are.

## BOOKS (frozen, verbatim machinery)

- **CAND-T5 ("EKAM Cand-1")** — pre-cap candidates = each stock-day's first ≥5-of-6-vote
  signal (R1 `day_candidates`, T=5); day cap 5 via earliest-(signal_stamp, sym)
  selection (R5 `sel_s0`).
- **S2 ("EKAM Cand-2")** — same candidates; day cap 3, earliest first (R5 `sel_s2`).
- Exits (both books, unchanged in every variant): CAND stack D=3 / S=1.00% / C=none —
  vote-decay exit at own-direction votes ≤ 3, hard stop −1.00%, no profit cap,
  square-off at the 15:10 bar's close (R2 `net_of` / `exit_x2p` verbatim).
- Basis: equity cash intraday, frozen 25 names, **per 100 shares PROVISIONAL**,
  ₹40/trade, paper only, real money ₹0. VWAP = equal-weighted typical-price proxy
  (stores carry no volume). Windows: 2025 Jan–Oct and 2026 Jan–Oct judged
  separately, never pooled; November slice = the 9 frozen dates
  (2026-11-02,03,04,05,06,09,11,12,13), reported separately, NOT part of the bar.

## CONTROL (must reproduce exactly before any variant number is reported)

CAND-T5: 2025 **+₹62,164.57** · 2026 **+₹63,883.60** · Nov **+₹24,528.65**
S2:      2025 **+₹45,300.64** · 2026 **+₹72,605.30** · Nov **+₹20,662.60**

Checked as full `year_rows` equality (windows, months, ex-top-3, November) against
`ekam_intraday_stocks_r2_results.json` CAND-T5 and the R5 S2 selection. Any mismatch
stops the run — no variant numbers on a failed control. An instrumented copy of the
exit loop (identical fill order) additionally returns exit price + reason + bar; its
exit price is asserted equal to `net_of`'s on **every** trade of every row.

## VARIANTS (change ONLY entry timing; selection ranking basis, caps, exits, stops unchanged)

- **SLOT30** — at most ONE new entry per 30-minute slot. Slot entry stamps:
  09:20, 09:50, 10:20, 10:50, 11:20, 11:50, 12:20, 12:50, 13:20, 13:50, 14:20.
  At each slot τ, the qualifying set = every stock with a tradable day whose bar
  stamped τ−5min (the latest completed bar) shows ≥5 votes on one side (LV≠SV),
  whose next bar is stamped τ, and which has not traded today. Ranking within the
  slot (frozen): **votes descending, then symbol A→Z**. Take the single
  highest-ranked qualifier, if the book's daily cap (5 / 3) is not yet filled.
  Qualification is re-evaluated fresh at every slot — a stock passed over at one
  slot may be taken at a later slot if it still qualifies there; a stock taken is
  out for the day. An empty slot stays empty (no carry-over, never two in a slot).
- **SLOT60** — identical, one entry per 60-minute slot: 09:20, 10:20, 11:20,
  12:20, 13:20, 14:20.
- **LATE** — no entries before 10:35. The control's candidate scan runs unchanged
  except that any signal whose ENTRY stamp is < 10:35 is passed over and scanning
  continues; each stock-day's candidate is its first qualifying signal with entry
  stamp ≥ 10:35 (i.e. signal stamp ≥ 10:30). Day selection then exactly as the
  control: earliest (signal_stamp, sym), first 5 (Cand-1) / first 3 (Cand-2).

## MEASURES (per book × variant × window: 2025, 2026, November)

Trades · net · WR · **losing-trade share %** (trades with net < 0 ÷ trades) ·
average loss (mean net of losing trades) · worst single day (minimum day-net) ·
max drawdown (cumulative trade-net sequence in (date, entry_stamp, sym) order,
peak-to-trough, as in `wide100_ekam.max_drawdown`) · ex-top-3 · **cluster measure**:
number of days with ≥3 trades exiting by stop or gap_stop, and the total booked on
those cluster days (sum of ALL the book's nets on those days; the stopped trades'
own sum reported alongside). Exit reasons come from the instrumented exit loop:
gap_stop (bar opens through the stop → fill at open), stop (stop touched in range
→ fill at stop), decay (own votes ≤3 at a bar close → fill at close), squareoff
(15:10 close).

## VERDICT BAR — FROZEN BEFORE SCORING

A variant **PASSES for a book** only if, in **BOTH** 2025 and 2026:
1. net ≥ 75% of the control's net for that book-year, **AND**
2. max drawdown ≤ 70% of the control's max drawdown for that book-year
   (drawdowns are negative: variant DD must be ≥ 0.70 × control DD), **AND**
3. losing-trade share **strictly lower** than the control's for that book-year.

November is reported for information only and is not part of the bar. Any variant
that passes gets a halves table (Jan–Jun vs Jul–Oct, both years). Failed variants
are never retested in identical form.
