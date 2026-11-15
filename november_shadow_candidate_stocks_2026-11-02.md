# SHADOW SPEC (DRAFT) — N4-V3-CAP3 · Stocks book · drafted 2026-11-02

**⚠️ SUPERSEDED 2026-11-02 (evening engine): this draft specifies the SYMMETRIC cap
(|move| ≥ 3.0%), which FAILED at whole-book level in the same day's floor session
(cycle FLOOR-1). Do NOT promote or score it as written. The promoted corrected spec
(one-sided LONG-only cap, cycle FLOOR-2) is
`november_shadow_stocks_onesided_cap_2026-11-02.md`.**

Status: **spec only — not wired, not promoted.** Drafted because the candidate passed
the full controls gate in `november_rsi_fix_tests_2026-11-02.md` (Candidate 3).
Formal promotion is the 17:15 RSI engine's step. Paper only, real money ₹0.
Shadow numbers are labelled shadow and are never mixed into primary numbers.

## Identity
- Book: Stocks — SarvaRitu, N4-V3 component.
- Shadow name: **N4-V3-CAP3**.
- Incumbent it shadows: the frozen N4-V3 as scored in the November scorecard
  (T125/S050) and in the SarvaRitu whole book (T150/S080).
- Basis: equity cash, provisional per 100 shares, ₹40/trade.

## The one rule diff
At the 09:30 measurement on a reaction day, compute the stock's reaction move by
09:30 exactly as the incumbent N4-V3 pipeline records it. **If |move by 09:30| ≥ 3.0%,
take no trade in that stock that day.** Otherwise the trade is taken identically to
the incumbent.

Everything else is unchanged from the incumbent N4-V3: same event/reaction pipeline
and universe, same reaction-day qualification (≥1% by 09:30 for the trade set this
cap applies to), same 09:35 entry, same exits (scorecard basis T125/S050; book basis
T150/S080 where the whole-book logger applies it), same frozen component exclusions
(ASTRAL; TVSMOTOR LONG; OIL LONG; and the v2 per-stock deletions).

## Logging
- One shadow row per incumbent N4-V3 event day, including days the cap skips the
  trade: fields = date, stock, direction, move-by-09:30, cap decision (TAKEN /
  SKIPPED-CAP), and for TAKEN rows the entry/exit/net under both bases, labelled
  `N4-V3-CAP3-SHADOW`.
- SKIPPED-CAP rows also record what the incumbent primary actually did that day
  (its realised net on both bases), so the cap's saved/cost tally is exact, not
  reconstructed later.

## Pre-registered judgement (November window, decided in advance)
Judged on identical event days against the primary N4-V3 November scorecard:
- **Adoption case** (for the December decision): shadow net ≥ primary net on the
  scorecard basis AND shadow ex-top-3 ≥ 0 AND the SKIPPED-CAP set's realised primary
  net ≤ 0 (the cap must not have skipped more profit than it saved).
- **Kill:** shadow net < primary net at month end, OR the SKIPPED-CAP set's realised
  primary net > +₹1,000 (per 100 shares, provisional) — i.e., in November the cap
  cost more than it saved.
- Frequency is reported, not gated (the in-sample cost is known: ~5.6 → ~3.0
  trades/month); if November produces fewer than 3 TAKEN shadow trades, the window
  is declared evidence-insufficient rather than passed or failed.

## Gate evidence (in-sample, Jan–Oct 2026, from the 2026-11-02 fix test)
Baseline → variant, per 100 shares provisional: book +₹19,977.90 → +₹20,940.28;
scorecard +₹7,990.43 → +₹10,432.93; both halves ≥ 0 on both bases (baseline book H2
was −₹1,750.10); ex-top-3 book +₹6,844.63 / scorecard +₹658.96; beats both placebos
(skip-1–2%-bucket +₹8,873.80; size-matched chronological skip +₹3,955.06, book basis);
no green month flips red; timing audit 0 violations. Full evidence:
`november_rsi_fix_tests_2026-11-02.md`. In-sample only — this spec exists so November
forward data can judge it.
