# EKAM-2b — SPEC (FROZEN 2026-11-14, before scoring)

Programme: EKAM (registry `ekam_strategy.md`). A small turn on EKAM-2, from the
diagnosis in `ekam_2026-11-14.md`: in EKAM-2 S0, 215 of 245 merged positions
exited on the Bollinger middle-band rule at ~13 days, and merged 2025
(+₹26,282.50) sits below RSI-REV standalone TIME60 (+₹63,575.50), with 2025
ex-top-3 −₹19,032.00. Research only — no book, ledger or job is touched.
Basis: equity cash · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR (2025,
2026), never pooled.

## 0. Base book — EKAM-2 S0, exactly as built

Everything is `ekam_SPEC.md` / `ekam_build.py` verbatim: same component
definitions (BB-REV-D BASE + RSI-REV TIME60, imported from the atlas build via
the EKAM build), same merge rules (one open position per name; entry-day firing
set tags the position `BB`, `RSI` or `BOTH`; entry signals in a held name are
ignored), same fill conventions, S0 = no stop. The stop question is settled by
the EKAM run and is NOT reopened: no stop form is scored here.

## 1. CONTROL (mandatory, before the variant)

(a) Run the EKAM engine's EKAM-2 S0 book and check its per-year lines against
the published anchors (`ekam_2026-11-14.md` / `ekam_results.json`):
2025 — 86 trades · +₹26,282.50 · WR 70.9% · avg hold 14.8 · ex-top-3
−₹19,032.00 · max DD −₹59,451.00 · worst −₹41,345.00 · peak 18.
2026 — 117 trades · +₹1,31,791.90 · WR 60.7% · avg hold 14.9 · ex-top-3
+₹85,110.90 · max DD −₹29,805.00 · worst −₹10,840.00 · peak 19.
Full stats-dict equality with `ekam_results.json` is required, not just the
headline lines.
(b) Cross-tabulate the control book's exit kinds by position tag (a measurement
of the EKAM record, reported whatever it shows).
Any mismatch in (a) = stop and report it; no EKAM-2b numbers are produced.

## 2. THE ONE CHANGE — exit ownership

The exit stack of a position is built ONLY from the component(s) that entered
it:
- Tag `BB` → only the BB rule: first close ≥ middle band → exit at next day's
  open (FORCED at the last close if the signal fires on the last data day or
  the position is still open at data end).
- Tag `RSI` → only the RSI stack, priority: (1) TIME60 at the open of the
  first day i with i − entry_index ≥ 60 (i > entry_index); (2) CAP intraday
  +10% from entry (gap-through at the open, else at the level); (3) first
  close with RSI ≥ 70 → exit at next day's open (FORCED as above).
- Tag `BOTH` → UNCHANGED from EKAM-2: the first trigger among both components'
  exit rules, with EKAM-2's priority (TIME60 → CAP → close signals, BB
  checked before RSI on the same day).
Entries, merge rules, fills, costs: unchanged. (Exit dates feed the state
machine, so later entries follow from the changed exits by the same rules —
"same entries" means same entry RULES.)

## 3. Reporting (per year — 2025 and 2026 separately)

Side by side, EKAM-2b vs EKAM-2 S0 (with the difference): trades · total · WR ·
avg hold · month table (net and trades by entry month, Jan–Oct) · halves
(H1 = entries Jan–Jun, H2 = entries Jul–Oct) · ex-top-3 · equity-curve max
drawdown (same ordering rule as EKAM) · worst trade · peak concurrent
positions. Year attribution: entry date in Jan 1 – Oct 31 of the year.
Plus: the full trade-list diff between the two books (count and identity of
any trades that differ), and the exit-kind × tag cross-tab for both books.

## 4. PLACEBO

Same random-entry design as the EKAM run, verbatim (`ekam_build.placebo`,
seed 20261114, 200 draws): per year, N = the book's trade count that year;
each draw sums N independent trades — name uniform from the 25, signal day
uniform from that name's Jan 1 – Oct 31 days of the year with a next day, entry
at next day's open, 100 shares. Exit stack: the EKAM placebo stack (TIME60 →
middle-band rule) — this IS the ownership-consistent stack for a tag-less
random entry, because it is exactly the BOTH-tag stack, the one stack
EKAM-2b leaves unchanged; a random entry has no entering component to own it.
As a determinism check, the placebo run against the CONTROL book must
reproduce EKAM's published S0 percentiles (2025: 53.5 · 2026: 99.0) and draw
means (+₹17,363.94 · +₹43,274.12) exactly; the EKAM-2b percentiles are then
read off the same draws against the EKAM-2b totals.

## 5. NOVEMBER (descriptive only)

From the EKAM-2b trade list and event log: every position with entry date in
2026-11-02 – 2026-11-13 (signal date shown), and every position entered
earlier still open at 2026-11-13. Positions still open at 2026-11-13 are
marked at the 2026-11-13 close and labelled **OPEN/MARKED** — never counted
in any closed total. Also count: component signals firing on 2026-11-02 –
2026-11-13 that produced no entry (name already held, or signal on the last
data day with no next day).

## 6. Diagnostic (labelled, not a variant)

From the EKAM-2b run's event log: entry signals ignored because the name was
already held, counted by the ignored signal's component and by the holding
position's tag. This measures the entry-side interaction between the
components; it changes no rule and produces no extra book.

## 7. Standing

EKAM-2b arms nothing and replaces nothing. Adoption needs forward evidence +
the owner's explicit word.
