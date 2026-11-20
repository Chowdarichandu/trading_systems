# "DON'T TRADE WHEN THIS OCCURS" GUARD TEST — EKAM INTRADAY CANDIDATES · SPEC
### (frozen 2026-11-17, BEFORE any guard is scored)

**Owner's order (2026-11-17 10:48 IST):** *"Go without fix"* — the first-bar
confirmation fix stays **REJECTED** (lossfix_2026-11-17.md) and is not revived
in any form here — *"and note down the losses' cause, so we don't trade when
this occurs in future."*

**Scope:** paper research only. The frozen live candidates (CAND-T5 /
"EKAM Cand-1", S2 / "EKAM Cand-2") and the November board do NOT change in
this run. A guard that passes the frozen bar below becomes a **proposal for
the owner's word**, nothing more. Basis: equity cash intraday, frozen 25
names, **per 100 shares PROVISIONAL**, ₹40/trade, paper only, real money ₹0.
VWAP = equal-weighted typical-price proxy (stores carry no volume).

## THE HONESTY CONSTRAINT (stated before any number)

The diagnosis in lossfix_2026-11-17.md found **no stable losing cell** across
2025–2026: both books earn on RANGE and on TREND days in both full years;
only November-to-date range days are slightly red (Cand-1 −₹1,172.90 / 30
trades; Cand-2 −₹2,902.40 / 18). The day-type label used there (full-day
high/low/close) is known only **after** the close — it may **not** be used
as a guard input. Every guard below uses only inputs knowable at its
decision time. A guard that merely re-labels hindsight, or that cannot beat
skipping random days, fails — that is what the placebos are for.

## BOOKS / MACHINERY (frozen, verbatim — same engine as the stagger and lossfix tests)

- **CAND-T5 ("EKAM Cand-1")** — R1 `day_candidates` (T=5) + R5 `sel_s0`
  (earliest-5). **S2 ("EKAM Cand-2")** — same candidates, R5 `sel_s2`
  (earliest-3).
- Exits (unchanged in the control and in G1/G3): CAND stack D=3 / S=1.00% /
  C=none — vote-decay exit at own-direction votes ≤ 3, hard stop −1.00%, no
  profit cap, square-off at the 15:10 bar's close (R2 `net_of` verbatim;
  exit detail from the stagger test's instrumented `exit_full`, asserted
  equal to `net_of`'s implied exit on **every** trade, now also returning
  the exit bar index).
- G2 modifies exits only on its trigger days (below); entries and selection
  are untouched.

## CONTROL (must reproduce exactly before anything else is reported)

CAND-T5: 2025 **+₹62,164.57** · 2026 **+₹63,883.60** · Nov (frozen slice)
**+₹24,528.65**
S2:      2025 **+₹45,300.64** · 2026 **+₹72,605.30** · Nov (frozen slice)
**+₹20,662.60**

Checked as full `year_rows` equality (windows, months, ex-top-3, November)
against `ekam_intraday_stocks_r2_results.json` CAND-T5 and the R5 S2 row —
the stagger/lossfix control-check procedure, verbatim. Any mismatch stops
the run. Windows: **2025** = dates in 2025 up to 2025-10-31; **2026** =
dates in 2026 up to 2026-10-31; **November slice** = the frozen 9 dates
2026-11-02,03,04,05,06,09,11,12,13 (R2 `NOV_DATES`).

## NIFTY INPUTS (the only external series any guard may read)

From the local NIFTY store (`data/sarvaritu_fwd/NIFTY/spot_5m.csv`, loaded
via R1 `load_stock("NIFTY")` + `day_segments`): 465 trading dates,
2025-01-01 → 2026-11-16, 75 bars/day stamped 09:15–15:25. Per date D:

- `open(D)` = open of D's first bar; `close(D)` = close of D's last bar;
  `high(D)`, `low(D)` = full-day extremes.
- `prev(D)` = the immediately preceding date in the store's sorted date
  list (the previous trading day in the data). The first store date
  (2025-01-01) has no predecessor: no guard may trigger on it.
- Day-type ratio (diagnosis definition, lossfix): `ratio(D) =
  |close(D) − open(D)| / (high(D) − low(D))`; D is RANGE iff ratio < 0.6.

## THE THREE GUARDS (thresholds frozen here — no tuning after results)

### G1 — FLAT-OPEN SKIP (entry gate, decided at the open)
`gap_pct(D) = open(D) / close(prev(D)) − 1`, in %. **Trigger:** `|gap_pct(D)|
≤ 0.15`. On a trigger day, **all** entries of both books are skipped (the
day contributes no trades). Inputs knowable at 09:15 from the first bar's
open and the prior close.

### G2 — FLAT-FIRST-HOUR EARLY SQUARE-OFF (exit overlay, decided at 10:15)
From D's own NIFTY bars stamped 09:15..10:10 inclusive:
`move_pct(D) = close(10:10 bar) / open(09:15 bar) − 1`, in %;
`range_pct(D) = fh_high / fh_low − 1`, in %, where fh_high / fh_low are the
max high / min low over those bars. **Trigger:** `|move_pct(D)| ≤ 0.10`
**AND** `range_pct(D) < 0.40`. On a trigger day, every position of the book
that is **open at the 10:15 bar** is squared off at **the open of that
stock's own 10:15 bar** instead of riding decay/stop/square-off. A position
is open at 10:15 iff, in that stock's day dict, `entry_li < idx(10:15)` and
its natural (frozen-rule) `exit_li ≥ idx(10:15)`. Positions entered at or
after 10:15, positions already exited before the 10:15 bar, and any trade
on a day whose stock day-dict has no 10:15 bar are **unchanged**. The
overlaid exit is recorded with reason `guard_sq1015`, stamp `10:15`, net via
the frozen `trade_net` (₹40 cost unchanged). Entries, selection, caps and
all non-trigger days are exactly the control.

### G3 — POST-RANGE SKIP (entry gate, decided pre-open)
**Trigger:** `prev(D)` exists and `ratio(prev(D)) < 0.6` — i.e. the prior
trading day was a RANGE day by the diagnosis definition. On a trigger day,
all entries of both books are skipped. Inputs are the prior day's complete
data — knowable before today's open.

## GATE MEASURES (per guard, per book)

For each window (2025 · 2026 · November slice): trades · net · max
drawdown (cumulative trade-net sequence in control ctx order, as in the
stagger test) — for the guard and the control side by side. Plus, per
window: **days skipped/triggered** (guard trigger days inside the window on
the store calendar, and the subset carrying ≥1 control trade of the book)
and **what the guard removes/changes**:
- G1/G3: trades removed and the **net of the removed trades alone**
  (control nets on skipped days).
- G2: positions squared off and the **delta** = Σ (overlaid net − control
  net) over squared positions.

## PLACEBOS (seeded, 200 draws each — `random.Random(20261117)`)

Per guard, per book, per window (2025 · 2026 · November slice):

- **G1/G3:** candidate days = sorted dates in the window carrying ≥1 control
  trade of the book. K = the number of candidate days the real guard skips.
  Each draw samples K candidate days uniformly without replacement; placebo
  net = control window net − Σ control nets on the sampled days.
- **G2:** candidate days = sorted dates in the window carrying ≥1 control
  trade of the book that is open at 10:15 (overlay-eligible). K = the
  number of candidate days on which the real G2 condition triggers. Each
  draw samples K candidate days and applies the 10:15 square-off overlay to
  those days only; placebo net = the resulting window net.
- Reported per cell: the real guard's net, the placebo median, the placebo
  90th-percentile value, and the real guard's **percentile** = 100 ×
  (#draws with placebo net < real net) / 200.

## VERDICT BAR — FROZEN BEFORE SCORING

A guard **PASSES for a book** only if **all four** hold:

1. **2025 net ≥ 95%** of the control's 2025 net **AND 2026 net ≥ 95%** of
   the control's 2026 net for that book, **AND**
2. max drawdown **strictly improves** (less negative) vs control in **both**
   2025 and 2026, **AND**
3. **November-slice net improves** vs control (strictly greater), **AND**
4. the guard **beats its placebo's 90th percentile** in **both** years:
   placebo percentile ≥ 90.0 in 2025 and in 2026.

A guard passing for only one book is reported as passing for that book
only. A passing guard is a **proposal for the owner's word** — nothing live
changes in this run. Failed guards are never retested in identical form,
and the frozen thresholds above are never re-tuned inside this test.

## PART 3 — TODAY + NOVEMBER COUNTERFACTUAL (per guard)

- **Today (2026-11-17):** stock bars fetched and built with the live
  producer's own route (`fetch_today_5m` + `completed_bars` +
  `build_today_stock` from `ekam_intraday_live_producer.py`) — bit-identical
  votes to the live layer, completed bars only. Today's NIFTY bars come
  from the same route (`fetch_today_5m("NIFTY", …)`); today's G1 prior
  close and G3 prior-day ratio come from the store's 2026-11-16. The
  control replay of today must first reproduce the live record
  (`ekam_intraday_live_log.csv`: Cand-1 −₹2,279.25 / 5 trades closed;
  Cand-2 −₹1,005.00 / 3 trades closed) — any mismatch is reported plainly
  and the counterfactual is then computed on the replay's own bars for both
  sides. Per guard: whether it triggers today, which entries it would have
  skipped (G1/G3) or which open positions it would have squared at the
  10:15 open **with prices** (G2), and today's resulting total per book.
  Positions still open at run time are marked at the latest completed bar
  (labelled MARK), never presented as closes.
- **November-to-date:** frozen slice (Nov 2–13) + Nov 16 (full day, frozen
  store — its guard inputs read from the store, prior day = 2026-11-13) +
  Nov 17 (today, as above) — control vs each guard per book, each piece
  shown separately and summed. Nov 16's control is cross-checked against
  the live log (Cand-1 +₹1,340.00 / 5 trades; Cand-2 +₹1,205.00 / 3 trades).

## DELIVERABLES

`guard_SPEC.md` (this file) · the loss-cause note in `ekam_strategy.md` +
one-line pointer in `~/memory/2026-11-17.md` (Part 1, checkpoint) ·
`guard_2026-11-17.md` · `guard_results.json` · `guard_trades.csv`
(control + G1/G2/G3 trades with exit detail, plus today's counterfactual
rows flagged) · `guard_build.py`.
