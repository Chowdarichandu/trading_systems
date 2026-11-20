# COMPENSATOR CANDIDATE — PRE-REGISTERED SPEC
### Improvement audit 2026-11-17, Thread 2(c). Written BEFORE any offset scoring was run.

**Trigger (measured, Thread 2a):** the board has a real joint-red gap —
24 days in Jan–Oct 2026 where ≥3 books traded and every one was ≤ 0
(worst combined day −₹10,336.75, 2026-02-05), and the two EKAM books
bleed together (daily ρ = +0.91). One compensator candidate is therefore
admitted for testing. Exactly one. No second candidate will be scored
under this audit whatever the result.

**Candidate:** BTST-IND Bank VOTES — the frozen `btst_ind_SPEC.md`
overnight Bank Nifty line: on days the Bank vote engine closes with a
≥5-vote side, buy that side's near option at the close, exit next
morning (frozen fills per its own build). Option BUYING only, 1 lot
(30), ₹220/trade basis as per its own record. It already runs as a
score-only shadow; this test asks only whether it COMPENSATES the
board. Its standalone record is already published
(`btst_ind_results.json`): 104 trades, +₹98,630.50, WR 50.0%,
halves +₹39,016.00 / +₹59,614.50, placebo 97.8th pct (500 draws),
worst single night −₹17,036.50, ex-top-3 +₹9,290.50. **Known at
registration time:** its data covers 2026 only (2026-01-02 →
2026-10-27) — no 2025 window exists in its record.

**Attribution:** candidate net is attributed to its ENTRY date (the
evening the overnight position joins the board). Window: Jan–Oct 2026,
the same 214-day calendar as Thread 2(a).

**Gate — the candidate PASSES as a compensator only if ALL hold:**
- C1 (frozen-gate coverage): standalone net positive in BOTH 2025 and
  2026 Jan–Oct windows, halves positive, placebo ≥ 90th pct.
- C2 (independence): daily correlation with EKAM Cand-1 < +0.20.
- C3 (aimed offset): candidate's average daily net on EKAM Cand-1's
  worst-decile days (the same 20 days as Thread 2a) > ₹0.
- C4 (board effect): the seven-line combined max drawdown (Jan–Oct
  2026, six Thread-2(a) lines + candidate) is strictly better
  (shallower) than the six-line combined max DD of −₹27,222.98.
- C5 (no new tail): candidate's worst single day is no worse than
  1.5× the board's worst combined day (1.5 × −₹10,336.75 = −₹15,505.13).

Any leg fails → verdict NO PASS, reported plainly with the numbers.
A PASS would still only make it a candidate for the owner's approval —
nothing is armed by this audit.
