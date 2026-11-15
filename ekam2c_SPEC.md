# EKAM-2c — SPEC (FROZEN 2026-11-14, before scoring)

Programme: EKAM (registry `ekam_strategy.md`). The RSI-upgrade turn, from the
diagnosis in `ekam2b_2026-11-14.md`: exit ownership changed nothing (EKAM-2
already exits every single-tag position by its own component's rules); the
merged-vs-standalone gap is ENTRY-side — 79 pure RSI signals were ignored
while a Bollinger position held the name, vs 29 BB signals blocked by RSI
holds; and all 19 BOTH positions were cut at the middle band, combined
−₹20,243.00. Research only — no book, ledger or job is touched.
Basis: equity cash · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR
(2025, 2026), never pooled.

## 0. Base book — EKAM-2 S0, exactly as built

Everything is `ekam_SPEC.md` / `ekam_build.py` verbatim, imported, not
re-implemented: same component definitions (BB-REV-D BASE + RSI-REV TIME60),
same merge rules (one open position per name; entry-day firing set tags the
position `BB`, `RSI` or `BOTH`; entry signals in a held name are ignored),
same fill conventions, S0 = no stop. The stop question is settled and is NOT
reopened.

## 1. CONTROL (mandatory, before the variant)

(a) Run the EKAM engine's EKAM-2 S0 book and check its per-year stats dicts
against `ekam_results.json` (`EKAM2.S0`) with FULL stats-dict equality, both
years. Headline anchors: 2025 — 86 trades · +₹26,282.50 · WR 70.9% · max DD
−₹59,451.00 · 2026 — 117 trades · +₹1,31,791.90 · WR 60.7% · max DD
−₹29,805.00.
(b) Determinism check: the EKAM placebo run against the control book must
reproduce the published S0 percentiles, draw means and draw medians exactly
(2025: 53.5 · +₹17,363.94 · +₹23,433.00 · 2026: 99.0 · +₹43,274.12 ·
+₹49,755.00).
Any mismatch in (a) or (b) = stop and report it; no EKAM-2c numbers are
produced.

## 2. THE ONE CHANGE — RSI upgrade of a BB-held position

Applies ONLY to a position whose entry tag is exactly `BB` (a pure
Bollinger-entered position). Everything else is EKAM-2 S0 verbatim.

- **Trigger.** On any day t while the BB position is open (t ≥ entry day),
  an RSI entry signal fires for that name — i.e. RSI ∈ the day's entry-signal
  set (the event EKAM-2 logs as IGNORED_HELD; the set may also contain BB).
  First trigger only; later RSI signals during the same hold do nothing.
- **Conversion.** From day t, the position's exit governance is the RSI exit
  stack ONLY. The Bollinger middle-band exit no longer applies to it —
  including day t's own close evaluation.
- **The RSI stack, as converted (EKAM priority):**
  1. TIME60 — at the open of the first governed day i with i − entry_index
     ≥ 60 (i > entry_index); the 60 days are counted from ENTRY, unchanged.
  2. CAP — intraday +10% from ENTRY price (gap-through at the open, else at
     the level).
  3. RSI ≥ 70 close — first governed close with RSI(14) ≥ 70 → exit at next
     day's open (FORCED at the last close if the signal fires on the last
     data day; a position still open at data end is FORCED at the last
     close, as in EKAM-2).
- **Causality carve-out (fill convention, not a rule change).** The trigger
  is a close-of-day-t signal, so on day t itself only the close-signal leg
  (leg 3) is evaluated under the new governance — no exit may fill at day
  t's open (TIME60) or intraday (CAP) on information known at day t's close.
  Legs 1–2 apply from day t+1 onward. (On a cross-up-through-30 day,
  RSI ≥ 70 is in practice false; leg 3 is evaluated anyway.)
- **What does NOT change.** Entries are unchanged: the triggering RSI signal
  does NOT open a second position, and no position is added or re-tagged for
  entry purposes (the position's entry tag stays `BB`; it is flagged
  `UPGRADED` with its upgrade date in the trade list). BB or RSI signals
  firing during an upgraded hold change nothing (no revert, no re-trigger).
  Positions tagged `RSI` are unchanged (already RSI-governed). Positions
  tagged `BOTH` are unchanged (EKAM-2 union stack). No stop (S0).
- **Counting an upgrade.** An upgrade is counted for a position iff the
  trigger fired and the position's exit-price day is AFTER day t (i.e. the
  position actually continued under RSI governance). A trigger on the last
  data day, where the position is FORCED at that same close, is not counted.

## 3. Reporting (per year — 2025 and 2026 separately)

Side by side, EKAM-2c vs EKAM-2 S0 (with the difference): trades · total ·
WR · avg hold · month table (net and trades by entry month, Jan–Oct) ·
halves (H1 = entries Jan–Jun, H2 = entries Jul–Oct) · ex-top-3 ·
equity-curve max drawdown (same ordering rule as EKAM) · worst trade ·
peak concurrent positions. Year attribution: entry date in Jan 1 – Oct 31
of the year (the EKAM `stats` rule).
Plus, the upgrade account: number of counted upgrades per year (same entry-
year attribution); their combined net in EKAM-2c vs the combined net of the
SAME positions in EKAM-2 S0 — matched on (symbol, signal date, entry date,
entry price) — and the difference; any upgraded position with no S0 match is
listed separately, not silently dropped. Per-position detail (symbol, entry
date, upgrade date, S0 exit date/net, 2c exit date/net) goes in the results
JSON and the report.
Plus: the full trade-list diff between the two books (counts of trades only
in one book).

## 4. PLACEBO

Same random-entry design as the EKAM run, verbatim (`ekam_build.placebo`,
seed 20261114, 200 draws): per year, N = EKAM-2c's trade count that year;
percentile of EKAM-2c's real total among the draw totals, plus draw mean and
median. (The placebo exit stack is the EKAM S0 stack — TIME60 → middle-band —
exactly as in the EKAM and EKAM-2b runs.)

## 5. NOVEMBER (descriptive only)

From the EKAM-2c trade list and event log: every position with entry date in
2026-11-02 – 2026-11-13 (signal date shown), and every position entered
earlier still open at 2026-11-13. Positions still open at 2026-11-13 are
marked at the 2026-11-13 close and labelled **OPEN/MARKED** — never counted
in any closed total. Also count: component signals firing on 2026-11-02 –
2026-11-13 that produced no entry (name already held, or signal on the last
data day with no next day), and any upgrade triggers in the November window
or on a position open in November.

## 6. Standing

EKAM-2c arms nothing and replaces nothing. Adoption needs forward evidence +
the owner's explicit word.
