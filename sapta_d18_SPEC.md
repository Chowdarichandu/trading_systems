# SAPTA Design 18 — SPEC (pre-registered)

**Pre-registered:** 2026-11-18, before any Design 18 scoring.
**Authority:** the owner REJECTED the programme's resting state
(2026-11-18 ~06:28 IST): *"Don't stop — results should be equal
or more than EKAM. Different approaches, different entry points,
different timings — it's your wish."* The target is explicit: a
SAPTA book that meets or beats EKAM in BOTH years (Cand-1
+₹62,165/+₹63,884 · Cand-2 +₹45,301/+₹72,605, per 100 shares).
**Class:** research only. Nothing armed, no paper run started,
no live book touched. Paper only, real money ₹0.
**Basis (unmoved):** equity cash, PROVISIONAL per 100 shares,
₹40 per completed trade. No stock options (closed surface).

## 0. Why this design (diagnosis carried in)

SAPTA holds three gated books (D13 GAPFADE-TRAIL +₹70,322/
+₹21,826 · D16 GAPFADE-UNION +₹1,36,826/+₹24,894 · D17
GAPFADE-FOCUS +₹25,150/+₹21,841) — all pass the 4-leg gate, all
fall short of EKAM in 2026. The shared geometry is the intraday
gap-fade square-off; 2026's thinness (gross/trade ₹144–₹187 vs
2025's ₹581–₹922) is the wound. The EKAM-shell transplant and
the Daily line are CLOSED and are not reopened. Following the
TARANG Design 23 method — and the owner's own words (different
approaches, different entry points, different timings) — this
design is a **STREAM-GROSS SURVEY**: seven new streams on
SAPTA's rotating universe, raw and uncapped. **No book is
built in this design.** A stream that passes the survey bar
earns a Design 19 book under the full unmoved gate; a stream
that fails is closed at survey cost.

## 1. Universe and window (unmoved)

- Selection layer: `sapta_owner_SPEC.md` + Amendments A1–A4;
  stored selections in `sapta_owner_selections.json` (quarterly
  top-7 indices by trailing 126-day PROXY return; top-3 picks
  per index under the Nifty 100 ∪ Midcap 150 membership, F&O,
  liquidity ≥ ₹5 cr and ₹2,000 constraints). Disclosed proxy
  series and the F&O + ₹2,000 filters are unchanged.
- A stream may enter a name ONLY on that name's **active days**
  (the days it sits in the current quarter's stored selection —
  the rotating active map of Designs 12–17). Names with no
  verified 5-min store, or excluded by the standing OHLC check
  (>5% mismatch), do not trade — the same tradable set as
  Design 16.
- Entries window 2025-01-01 → 2026-11-13. A trade's year is
  its ENTRY year (family convention). The overnight streams'
  exits may land on store days after the entry day; the store
  ends 2026-11-13, so an entry whose full holding window
  (§3) does not exist in the store is **not taken** and is
  counted (`no_exit_day`).
- **KNOWN LIMITATION (carried):** current (Nov 2026)
  constituent lists applied to a 2025–2026 backtest carry
  constituent look-ahead / survivorship bias; index series
  are constituent-average PROXY series.

## 2. Survey protocol (every stream, no exceptions)

- **Stream:** every signal the stream's rule produces on
  active name-days, at most ONE trade per name-day per stream
  — the FIRST qualifying signal of the day. No caps, no
  allocation, no filters, no ranking.
- **Money:** gross = (exit − entry) × side × 100 shares;
  net = gross − ₹40. Win rate = share of trades with net > 0
  (family convention).
- **Stop convention** (where a stream carries the −1.0% stop):
  the family's `exit20` convention — stop-first; a bar that
  OPENS through the stop fills at the bar's open, otherwise
  the fill is the stop price. For a SHORT the stop is
  entry × 1.01.
- **Score per stream per year:** trades taken (and raw signals
  / skip counts by reason), gross ₹, gross/trade, net ₹,
  net/trade, win rate, LONG and SHORT gross/trade, stop share,
  exit-reason mix. Plus the stream's **full-period net**
  (2025 + 2026) against the EKAM pair's full-period nets —
  Cand-1 +₹1,26,048.17, Cand-2 +₹1,17,905.94 — and per-year
  nets against the EKAM per-year lines.
- **SURVEY PASS BAR (pre-registered):** stream gross/trade
  STRICTLY greater than ₹40.00 in BOTH 2025 and 2026 **AND**
  stream net positive in both years. Anything else is a
  survey fail, whatever its single-year figure.

## 3. The seven streams (exact definitions)

Gap streams share one signal: on an active name-day with a
previous store day, gap% = first-bar open / previous store
day's last-bar close − 1. **Up-gap ≥ +1.5% → SHORT.** The
half-gap level is H = (first-bar open + prev_close) / 2 (the
family's convention). All five gap streams fire on the same
qualifying name-days; they differ only in entry point, exit
and timing, as tasked.

1. **GF-ON1** — Entry at the first-bar open, SHORT. −1.0% stop
   live from the entry bar through the next trading day. Exit
   at the **next trading day's close** (the close of that
   day's last bar) if the stop never fires. Requires the
   T+1 store day to exist.
2. **GF-ON2** — As GF-ON1, exit at the **T+2 close**; stop
   live across T, T+1, T+2. Requires the T+2 store day.
3. **GF-FILL3** — Entry at the first-bar open, SHORT. Exit at
   the **50% gap retrace** (price reaching H) or the **T+3
   close**, whichever first; −1.0% stop throughout. Per-bar
   resolution order: stop first (open-through → open fill,
   else stop price), then retrace (a bar opening at/below H
   fills at its open, else a bar whose low ≤ H fills at H).
   Scan runs from the entry bar through the last bar of T+3.
   Requires the T+3 store day.
4. **GF-BAR2** — Entry at the **second 5-min bar's open**
   (day-local bar 1; normally 09:20) instead of the first
   bar's — isolating the entry-point change against T25-C
   geometry. −1.0% stop, 15:15 square-off (`exit20_engine`
   from the entry bar). A day with no second bar, or whose
   second bar falls after the square-off bar, is unfilled
   (counted).
5. **GF-LATE** — Entry at **13:00**: the first bar timestamped
   ≥ 13:00, at its open — taken ONLY if the gap has **not
   already retraced 50%** before that bar (no bar in
   [first bar, entry bar) with low ≤ H; a retraced day is
   skipped and counted `skipped_retraced`). −1.0% stop from
   the actual entry price, 15:15 square-off (`exit20_engine`
   from the entry bar). A day with no ≥13:00 bar is unfilled
   (counted).
6. **ORB30-SHORT** — The family's frozen definition
   (`tarang24_score.sig_orb30short`): D23's ORB-30 signal —
   opening range = high/low of the 09:15–09:40 bars; from the
   09:45 bar, the first close beyond the range is the day's
   signal — keeping ONLY the SHORT side (a day whose first
   break is LONG produces no trade in this stream). Entry at
   the next bar's open; −1.0% stop + 15:15 square-off
   (`tarang23_score.take_trade` / `exit20_engine`).
7. **VOLSHOCK** — The D23 definition imported EXACTLY
   (`tarang23_score.sig_volshock`; tarang23_SPEC §3.7): for a
   bar j at day-local position ≥ 20, the window is the 20
   bars immediately before j in the same session; a shock
   requires volume[j] ≥ 3 × mean window volume; close[j]
   above the window's maximum high → LONG, below its minimum
   low → SHORT; first shock of the day only. Entry at the
   next bar's open; −1.0% stop + 15:15 square-off
   (`take_trade` / `exit20_engine`).

## 4. Controls (mandatory, before any survey number is quoted)

- **C-12a — EKAM machinery control**
  (`tarang19_score.ekam_control`): CAND-T5 (+₹62,164.57 /
  +₹63,883.60) and S2 (+₹45,300.64 / +₹72,605.30) reproduced
  exactly.
- **C-18a — Imported-machinery verification on TARANG's 127:**
  `tarang23_score.run_family` on the 127-name universe must
  reproduce the published D23 stream figures — ORB30: 28,058
  trades / gross +₹7,50,127.89 (2025), 24,077 / +₹2,74,968.75
  (2026); VOLSHOCK: 18,353 / +₹1,99,327.19 (2025), 16,655 /
  +₹4,02,078.96 (2026) — and the ORB30 SHORT-side subset must
  reproduce D24's published ORB30-SHORT: 15,251 trades /
  +₹4,82,882.09 (2025), 13,003 / +₹3,76,773.11 (2026).
- **C-18b — Design 16 anchor:** Design 16's full union
  pipeline (union candidates → `allocate25` → TRAIL re-exit)
  re-run inside this run reproduces SAPTA's gated union book
  exactly: **424 taken trades**, the taken (sym, date) set
  identical to `sapta_d16_trades.csv` (book GAPFADE-UNION),
  nets **+₹1,36,826.29 (2025) / +₹24,893.52 (2026)**, re-TRAIL
  parity counters at zero.

Any control failure aborts the run before survey scoring.

## 5. Audit (independent path — `sapta_d18_audit.py`)

Separately written from the scorer; shares no code path with
it beyond the frozen data stores and the stored selections
file. Bars loaded via `sapta_owner_engine.load_5m` (a
different loader than the scorer's prep); the active map
rebuilt independently from `sapta_owner_selections.json` +
the RELIANCE calendar. Every survey trade's signal, entry,
exit and net re-derived (overnight exits resolved on
concatenated multi-day arrays; same-day exits via the
family's audit exit `exit20_audit`); the written
`sapta_d18_trades.csv` re-summed per stream per year against
`sapta_d18_results.json`. The audit's counters are reported
in the report's Audit section.

## 6. What this design does not do

No book, no book gate, no placebo (a stream has no allocation
to placebo-test; timing proof belongs to the Design 19 book
if a stream earns one), no per-entity tuning, no November
slice verdict (November days sit inside the 2026 stream like
any other days). No Daily line (closed in Design 14). No
EKAM-shell reopening (measured-exhausted, Designs 3–11). No
threshold change to any frozen stream. Nothing is armed; no
paper run is started by this design under any outcome.
