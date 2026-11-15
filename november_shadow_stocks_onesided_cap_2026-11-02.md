# SHADOW SPEC (CORRECTED, PROMOTED) — N4-V3 ONESIDED-CAP3 · Stocks TUNED SHADOW · promoted 2026-11-02, effective Tue 2026-11-03

Status: **PROMOTED by the 2026-11-02 evening Stocks engine (its first action).**
Paper only, real money ₹0. Shadow numbers are labelled shadow and are never mixed
into the frozen book's or the primary scorecard's numbers.

## Correction on record — read first
The draft at `november_shadow_candidate_stocks_2026-11-02.md` specified a SYMMETRIC
cap (skip |move by 09:30| ≥ 3.0%). **That draft is SUPERSEDED and must not be
promoted or scored as written.** The symmetric version passed at standalone-component
level (fix test STOCKS-FIX-02), but the same day's whole-book floor session
(`stocks_engine_session_2026-11-02.md`, cycle FLOOR-1) showed it does NOT transplant
to book level: the surviving in-book ≥3% bucket is −₹1,838.73 in 2025 but
**+₹5,678.23 in 2026** — the book's prior deletions had already harvested the losing
names, and the symmetric cap fails the session gate (combined and 2026 legs).
What BANKED at book level (cycle FLOOR-2, all nine session-gate legs pass) is the
ONE-SIDED cap below. This spec promotes THAT variant, and only that variant.

## Identity
- Book: Stocks — SarvaRitu, N4-V3 component.
- Shadow name: **N4-V3-ONESIDED-CAP3 (Stocks TUNED SHADOW v1)**.
- Incumbent it shadows: the frozen N4-V3 as scored in the November scorecard
  (T125/S050) and in the SarvaRitu whole book (T150/S080).
- Basis: equity cash, provisional per 100 shares, ₹40/trade.

## The one rule diff
At the 09:30 measurement on a reaction day, compute the stock's signed reaction
move by 09:30 exactly as the incumbent N4-V3 pipeline records it.
**If the trade is LONG and the signed move by 09:30 is ≥ +3.0%, take no trade in
that stock that day. SHORT entries are NOT capped** (in-book SHORT ≥3% went 9/10
winners in 2026, +₹7,468.49 — capping them is what killed the symmetric version).
Otherwise the trade is taken identically to the incumbent.

Everything else is unchanged from the incumbent N4-V3: same event/reaction pipeline
and universe, same reaction-day qualification, same 09:35 entry, same exits
(scorecard basis T125/S050; book basis T150/S080 where the whole-book logger applies
it), same frozen component exclusions (ASTRAL; TVSMOTOR LONG; OIL LONG; and the v2
per-stock deletions).

## Gate evidence (in-sample, from the runs that banked it — not re-scored tonight)
- Book level, cycle FLOOR-2 on the v3 C16 book: combined +₹2,59,860.26 →
  +₹2,62,591.33; 2025 Jan–Oct +₹45,985.12 → +₹47,048.67 (ex-top-3 +₹30.76 →
  +₹5,131.62); 2026 +₹2,15,131.13 → +₹2,16,921.39; LONG ≥3% bucket is negative in
  BOTH years (2025 −₹940.81 / 10 tr; 2026 −₹1,790.26 / 4 tr); placebos beaten
  (mirror skip-SHORT +₹2,53,289.69; chronological first-N +₹2,47,989.60); all nine
  session-gate legs pass, cross-year clean.
- Standalone level, STOCKS-FIX-02 (the symmetric form's gate, recorded for the
  bucket diagnosis): book +₹19,977.90 → +₹20,940.28; scorecard +₹7,990.43 →
  +₹10,432.93; timing audit 0 violations. The one-sided form keeps the LONG half of
  that bucket and restores the profitable SHORT half.
In-sample only — forward shadow evidence from 2026-11-03 decides December adoption.

## Logging
- One shadow row per incumbent N4-V3 event day, including days the cap skips the
  trade: fields = date, stock, direction, signed move-by-09:30, cap decision
  (TAKEN / SKIPPED-CAP), and for TAKEN rows the entry/exit/net under both bases,
  labelled `N4-V3-ONESIDED-CAP3-SHADOW`.
- SKIPPED-CAP rows also record what the incumbent primary actually did that day
  (its realised net on both bases), so the cap's saved/cost tally is exact.

## Pre-registered judgement (November window, decided in advance)
Judged on identical event days against the primary N4-V3 November scorecard:
- **Adoption case** (for the December decision): shadow net ≥ primary net on the
  scorecard basis AND shadow ex-top-3 ≥ 0 AND the SKIPPED-CAP set's realised primary
  net ≤ 0.
- **Kill:** shadow net < primary net at month end, OR the SKIPPED-CAP set's realised
  primary net > +₹1,000 (per 100 shares, provisional).
- If November produces fewer than 3 TAKEN shadow trades, the window is declared
  evidence-insufficient rather than passed or failed. (Known in-sample cost of the
  symmetric form was frequency ~5.6 → ~3.0 trades/month; the one-sided form keeps
  SHORT trades, so its frequency cost is smaller.)

## Would-be scoring for 2026-11-02 (pre-promotion, NOT in shadow MTD)
Today's NTPC LONG entry had a signed move by 09:30 of **+3.178%** — under this cap
the shadow would have SKIPPED it. The incumbent took it and lost −₹300.24 (book
basis) / −₹202.65 (scorecard basis). Would-be shadow result today: ₹0 taken,
₹300.24 / ₹202.65 saved vs incumbent — labelled would-be only; shadow MTD starts
2026-11-03 at ₹0 · 0 trades.
