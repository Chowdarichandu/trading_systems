# STOCKS ENGINE — FLOOR SESSION, 2026-11-02

**Directive:** Stocks (SarvaRitu, equity cash intraday, Chandu's 25, paper, real ₹0,
provisional per 100 shares, ₹40/trade) must reach a **₹15,000/month pace in EACH year
separately** — ≥ ₹1,50,000 across Jan–Oct 2026 AND ≥ ₹1,50,000 across Jan–Oct 2025.
A strong year may not subsidise a weak one.

**Incumbent adopted:** the v3 C16 book — the reigning banked candidate line for
December adoption — because it dominates the brief's reference book (frozen v2 C24)
under the cross-year gate in both years (2025 +₹44,729.13 vs +₹27,479.24; 2026
+₹215,131.13 vs +₹211,588.10). The frozen v2 book and its Nov–Dec forward test were
not touched. All baselines independently re-summed to the paisa; REGIME-CLASSIFIER-1
labels replicated exactly against both books' published cells; N4 move-by-09:30
recomputation matched the recorded 2026 standalone moves 56/56 and the in-book join
34/34 (`stocks_engine_floor_baseline.py`).

**Session gate (frozen before scoring, all legs, same run):** combined rises ·
2025 total and Jan–Oct do not fall · 2026 does not fall · every regime cell × year
stays positive · ex-top-3 per year ≥ 0 and combined ex-top-3 does not fall · no green
month flips red · no Jan–Oct half flips positive→negative · beats both pre-registered
placebos · timing audit 0 violations and re-sum exact.

## Starting position (v3 C16 book)
| Year | Jan–Oct | Pace/month | vs ₹15,000 floor |
|---|---|---|---|
| 2025 | +₹45,985.12 | ₹4,598.51 | **gap ₹1,04,014.88** |
| 2026 | +₹2,15,131.13 | ₹21,513.11 | **MET (+₹65,131.13)** |

## Cycles

### FLOOR-1 — N4-V3 symmetric over-extension cap (|move by 09:30| ≥ 3.0%) → **REJECTED**
The brief's starting asset, re-gated at whole-book level on both years. The transplant
failed: the book's own prior deletions (v2/v3 law) had already harvested the standalone
file's losing ≥3% names, so the surviving **in-book** ≥3% bucket has the opposite sign
split — 2025 −₹1,838.73 (17 tr) but **2026 +₹5,678.23 (14 tr)**. The cap would have
lifted 2025 (total → +₹46,567.86; ex-top-3 +₹30.76 → +₹8,860.54) and cut 2026
(→ +₹2,09,452.90). Combined +₹2,59,860.26 → +₹2,56,020.76. **Gate legs (a) combined and
(c) 2026 fail**; all other legs pass, both placebos beaten. A year-scoped version
(2025-only) is a date filter and was not entertained. Evidence:
`stocks_engine_floor_c1_result.json`.

### FLOOR-2 — N4-V3 LONG over-extension cap (signed move ≥ +3.0%) → **BANKED**
Diagnosis split Cycle 1's bucket by direction: LONG ≥3% is negative in BOTH years
(2025 −₹940.81 / 10 tr / 2 W; 2026 −₹1,790.26 / 4 tr / 1 W), while SHORT ≥3% carries
2026's earners (10 tr, 9 W, +₹7,468.49). The one-sided cap drops 14 trades:
- Combined **+₹2,59,860.26 → +₹2,62,591.33 (+₹2,731.07)**
- 2025 total +₹44,729.13 → +₹45,669.94 · **Jan–Oct +₹45,985.12 → +₹47,048.67** ·
  ex-top-3 **+₹30.76 → +₹5,131.62** (the concentration razor is repaired)
- 2026 +₹2,15,131.13 → +₹2,16,921.39 · ex-top-3 +₹85,611.99 → +₹87,402.25
- All nine legs pass; placebos: mirror (skip SHORT ≥3%) +₹2,53,289.69, chronological
  first-N +₹2,47,989.60 — both beaten clearly. Cells stay positive in both years.
- Disclosed inside the win: one dropped trade was a winner (OBEROIRLTY, 2025-10-16,
  +₹2,455.85) — October 2025 deepened (−₹3,020.72 → −₹4,624.53 by session end) while
  the bucket and the year improved. The gate judges the rule, not the anecdote.
Books: `stocks_engine_floor_c2_book2025_trades.csv` / `...2026...`.

### FLOOR-3 — Challenger: P2F-family reaction-size cap → **REFUSED AT DIAGNOSIS**
Challenger slot (cadence: every 3rd cycle). Hypothesis: cap the P2F family the way
Cycle 2 capped N4. The diagnosis killed it before any scoring: reaction_ret was
reconstructed for all 114 in-book family trades (0 band-consistency violations) and
expectancy **rises** with reaction size in both years — 2026 buckets: 2.5–4% +₹384/tr,
4–6% +₹865/tr, 6–8% +₹85/tr, ≥8% +₹695/tr; 2025 all buckets positive too. There is no
over-extension region to cut. Second kill in the same cycle: F4 × regime-cell is
cross-year locked in both cells (DOWN: 2025 −₹2,369.54 / 2026 +₹1,06,005.51; FLAT:
2025 +₹2,460.68 / 2026 −₹2,949.58) — neither side is deletable under the gate.
No-bank (refusal with evidence, the v3 C18 precedent class).

### FLOOR-4 — Deletion: N4-V3 × HDFCBANK × LONG → **BANKED**
Registry re-derived at the C2 book under the gate-accurate bar (the C2 diagnostic's
both-years-negative bar was the stricter v2 bar; v3's banks were mostly of the
one-sided class: < 0 in one year, ≤ 0 in the other, combined ≤ −₹500). Exactly one
qualifying row book-wide: N4-V3 × HDFCBANK × LONG — 3 trades, all 2025, −₹836.12
(Apr −₹814.08, Jul +₹830.00, Oct −₹852.04), zero 2026 presence.
- Combined **+₹2,62,591.33 → +₹2,63,427.45 (+₹836.12)**; 2025 total → +₹46,506.06 ·
  **Jan–Oct +₹47,048.67 → +₹47,884.79** · ex-top-3 → +₹5,967.74; 2026 untouched.
- All nine legs pass; placebos (chrono first-3; largest-|move| 3) beaten.
- Disclosed cost, as frozen: the slice's July leg was positive — deleting it deepens
  the worst month (Jul 2025 → −₹5,664.05). Accepted under the per-year floor
  objective; v3's maximin would have refused. Thin sample (3 trades) on the record.
Books: `stocks_engine_floor_c4_book2025_trades.csv` / `...2026...`.

### FLOOR-5 — Whole-stock axis: two rows over the bar → **REFUSED (aggregation)**
Re-derivation at the C4 book: (comp × stock × dir) and (comp × cell) axes empty.
The coarser (comp × stock) axis shows two rows — P2F-R2 × RECLTD (−₹690.73) and
N4-V3 × PFC (−₹561.82) — and both are refused: each is a sum of direction slices
that individually fail the −₹500 quality bar (RECLTD: LONG −₹252.73 in 2025 /
SHORT −₹438.00 in 2026; PFC: LONG −₹399.96 / SHORT −₹161.86, the SHORT slice
carrying a +₹568.78 winning trade in 2026 that the whole-stock cut would delete).
Aggregating sub-bar slices to clear the bar is the mirror image of slicing thinner
to find one (SAT-30): the bar binds in both directions. No-bank.

### FLOOR-6 — F4 entry-hour axis → **NO-BANK (axis empty)**
Final scan axis: F4 is the only component with a time axis in the dumps (N4 all
09:35, P2F family all 09:15, INV earliness closed in v2). F4's population is
~94% concentrated in the 10:00 hour in both years, and that hour is the same
cross-year lock as everything else in F4 (−₹2,703.03 in 2025 / +₹89,051.14 in
2026); every other hour is positive in both years. No slice qualifies. No-bank.
Session ends on the brief's cycle-count stop (6 cycles). The consecutive no-bank
streak at close is 2 (FLOOR-5, FLOOR-6) — the protocol's 3-cycle saturation rule
is not formally triggered, but every axis the protocol enumerates has been scanned
at the final book state and is empty, refused, or closed (see below).

## Ending book — FLOOR-C4 (the December candidate line, updated)

**Combined +₹2,63,427.45** (session lift +₹3,567.19 over the C16 incumbent, from two
banked cycles; no rejected variant is in the book). Trades 718 (2025) + 632 (2026).

### 2025 — pace ₹4,788.48/month vs the ₹15,000 floor: **GAP ₹1,02,115.21**
- Jan–Oct **+₹47,884.79** (31.9% of the ₹1,50,000 floor) · full year +₹46,506.06
- Halves (Jan–Oct): H1 Jan–May +₹40,672.50 · H2 Jun–Oct +₹7,212.29 — both positive
- Ex-top-3 +₹5,967.74 (was +₹30.76 at session start — the session's banks materially
  de-concentrated 2025) · Top-3 stocks carry the rest, as before
- Regime cells: DOWN +₹32,605.74 · UP +₹11,017.75 · FLAT +₹2,882.57 — all positive
- Months Jan–Oct: Jan +6,147.74 · Feb +11,073.79 · Mar +1,687.03 · Apr +21,096.20 ·
  May +667.74 · **Jun −955.92 · Jul −5,664.05** · Aug +12,846.15 · Sep +5,610.64 ·
  **Oct −4,624.53** (Nov −2,586.68 · Dec +1,207.95 outside the floor window)
- By component (full year): P2F +15,884.42 · INV-LONG +12,605.23 · INV-ABOVE
  +8,281.25 · N4-V3 +5,712.13 · INV-R3 +4,438.70 · F4 **+91.14** · P2F-R2 −390.06 ·
  R2-LOWBAND −116.75

### 2026 — pace ₹21,692.14/month vs the ₹15,000 floor: **MET (+₹66,921.39)**
- Jan–Oct **+₹2,16,921.39** · Halves: H1 +₹1,20,674.05 · H2 +₹96,247.34
- Ex-top-3 +₹87,402.25 · Cells: DOWN +₹1,93,697.00 · UP +₹16,161.49 · FLAT +₹7,062.90
- All ten months green; worst month Jul +₹8,486.54
- By component: F4 +1,03,055.93 · INV-LONG +44,062.10 · N4-V3 +27,678.40 ·
  P2F +20,116.78 · P2F-R2 +15,149.33 · INV-ABOVE +3,349.21 · INV-R3 +2,226.28 ·
  R2-LOWBAND +1,283.36

## What the gap is, plainly
The remaining 2025 gap (₹1,02,115.21 of Jan–Oct pace) is **not a slice problem any
more**. Every deletion axis — (component × stock × direction), (component × stock),
(component × regime-cell), entry-hour — has been re-derived at the final book and is
exhausted at the standing quality bar; the two over-bar aggregations were refused on
principle, not arithmetic. The gap's anatomy is a **year effect**: F4, the book's
largest earner, made +₹91.14 across 246 trades in 2025 against +₹1,03,055.93 in 2026,
with an identical population (same band, same hour concentration, same direction mix)
— the joint state (below-trend × moderate move × follow) was simply inert in 2025's
tape, and no ex-ante sub-population separates the years. The weak months are thin,
not rotten (Jun 2025: one trade all month). Families remaining open: **none in-sample**
— the reaction (band × lag) grid is closed, both F4 exit ladders are closed, the
R-ladder ends at R+2, the deletion registry is empty on all axes, and the challenger
axes attempted this session (P2F size cap, F4 hour) are refused/empty on evidence.

**Reopening conditions (unchanged from the v3 termination, now re-confirmed):**
(1) bulk/block-deal data access (sourcing failed from this environment, Lesson 39);
(2) fresh data — the frozen SarvaRitu forward test is already collecting Nov–Dec 2026,
and December judging will score this session's ending book family on it;
(3) a genuinely new mechanism class not derived from the F4/INV/N4/P2F families.
Loosening the gate or re-defining the floor are not reopenings.

**Book law added this session:** N4-V3 takes no entry with signed move by 09:30
≥ +3.0% (FLOOR-2) · N4-V3 takes no HDFCBANK LONG signals (FLOOR-4). Ending books of
record: `stocks_engine_floor_c4_book2025_trades.csv` /
`stocks_engine_floor_c4_book2026_trades.csv`. The frozen SarvaRitu forward test
(v2 book) ran untouched throughout.
