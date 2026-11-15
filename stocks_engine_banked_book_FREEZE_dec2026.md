# FREEZE — BANKED BOOK (SarvaRitu), for DECEMBER 2026 judging
**Frozen:** 2026-11-02, Round 11 (R11-07). **Status:** the banked
book ONLY — no flagged form (max stack, Variant C, standalone
NE-REV forms, R2-26, R5-03, REXP flags) is part of this freeze;
an adopted form gets its own freeze.
**Basis:** equity cash intraday · Chandu's 25 watchlist stocks ·
provisional per 100 shares · Rs40/trade · paper only, real
money Rs0 · same-day re-entry allowed · no volume features.

## The frozen book (regeneration-verified at freeze time)
Regenerated through the documented chain (Round-8 ending CSVs
-> Round-9/10 identity chain) and matched row-for-row and to
the paisa against `stocks_engine_r10_book{2025,2026}_trades.csv`:

| Year | Trades (full) | Full total | Jan-Oct | Jan-Oct trades | Ex-top-3 (full) |
|---|---|---|---|---|---|
| 2025 | 887 | Rs77,041.31 | Rs78,420.04 | 842 | Rs23,708.10 |
| 2026 | 969 | Rs229,696.21 | Rs229,696.21 | 969 | Rs77,473.77 |

2025 months: {'2025-01': 2200.31, '2025-02': 20242.66, '2025-03': 8953.57, '2025-04': 39749.43, '2025-05': 2498.99, '2025-06': -955.92, '2025-07': -7083.39, '2025-08': 11173.48, '2025-09': 5585.44, '2025-10': -3944.53, '2025-11': -2586.68, '2025-12': 1207.95}
2026 months: {'2026-01': 29518.32, '2026-02': 14600.92, '2026-03': 11183.36, '2026-04': 29054.66, '2026-05': 40992.57, '2026-06': 5677.99, '2026-07': 8887.87, '2026-08': 10540.02, '2026-09': 15499.6, '2026-10': 63740.9}
2025 halves (Jan-Oct): H1 Rs73,644.96 /
H2 Rs4,775.08 · 2026 halves: H1
Rs125,349.83 / H2
Rs104,346.38
Regime cells 2025: {'DOWN': 42941.63, 'FLAT': 21250.68, 'UP': 12849.0} · 2026: {'DOWN': 210264.94, 'FLAT': 2909.78, 'UP': 16521.49}
Top-3 stocks 2025: [('OBEROIRLTY', 30748.68), ('ASTRAL', 14260.02), ('GLENMARK', 8324.51)] · 2026:
[('TVSMOTOR', 82776.4), ('ASTRAL', 37313.35), ('OBEROIRLTY', 32132.69)]

## Universe (25, frozen)
GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR

## Regime law (frozen — REGIME-CLASSIFIER-1)
From NIFTY daily closes through the PRIOR session: UP = prior
close > 50DMA and the 5-day 50DMA slope >= 0; DOWN = prior
close <= 50DMA and slope <= 0; else FLAT. "Below-trend" = prior
close <= 50DMA (the SarvaRitu law governing F4 / INV-LONG).

## Components (frozen constructions; builders are the operative definition)
| Component | Admission (all knowable at the decision bar) | Entry | Exits |
|---|---|---|---|
| F4 | Below-trend day; the stock's first morning move in [0.5%, 1.0%) by the 10:00 bar; follow that direction; frozen exclusion set incl. the direction-scoped slices banked in the saturation run | First bar after 10:00 | T150 / S095 |
| INV-LONG | Below-trend pool days (prior close <= 50DMA); frozen pool machinery (stocks_engine_r2_lib), rounds <= 3, 11:00 cutoff (Round-2 banking); mechanism-scoped exclusions (BDL, VEDL, HINDZINC, KALYANKJIL, INDUSTOWER) | Per frozen pool machinery, strictly after the signal bar | T125 / S050 |
| INV-ABOVE | Above-trend pool days (prior close > 50DMA); same frozen pool machinery | Per frozen pool machinery | T125 / S050 (the T150/S080 swap is FLAGGED R2-26 — NOT in this book) |
| INV-R3 | Below-trend pool days; the Round-2 INV pool's R3 sub-form (stocks_engine_r2_lib) | Per frozen pool machinery | T125 / S050 |
| N4-V3 | CERTIFIED results-reaction day only (R6-11 standard, below); signed move by 09:30 >= +1.0% or <= -1.0% -> follow; FLOOR-2: no LONG entry when the signed move by 09:30 >= +3.0%; FLOOR-4: no HDFCBANK LONG | 09:35 bar | T150 / S080 |
| P2F | Results reaction >= 2.5% (certified set); follow at R+1; exclusions ASTRAL, HINDUNILVR (mechanism-scoped) | R+1 session, frozen machinery | T125 / S050 |
| P2F-R2 | Same reaction set and exclusions, followed at R+2 | R+2 session | T125 / S050 |
| R2-LOWBAND | Reactions in [2.0%, 2.5%) at R+2; stands aside on UP-regime days | R+2 session | T125 / S050 |
| GAP-FADE | Overnight gap <= -1.5% (open vs prior close); fade LONG; regime cells DOWN + FLAT only | 09:20 bar | T125 / S050 |
| GAP-FADE-INC | Overnight gap in [-1.5%, -1.25%); fade LONG; DOWN + FLAT only | 09:40 bar | T125 / S050 |

Component census in the frozen book (rows / net):
- F4 2025: 246 rows, Rs91.14
- GAP-FADE 2025: 81 rows, Rs21,470.27
- GAP-FADE-INC 2025: 31 rows, Rs2,305.22
- INV-ABOVE 2025: 151 rows, Rs8,281.25
- INV-LONG 2025: 291 rows, Rs23,894.61
- INV-R3 2025: 4 rows, Rs-230.42
- N4-V3 2025: 35 rows, Rs5,851.63
- P2F 2025: 26 rows, Rs15,884.42
- P2F-R2 2025: 21 rows, Rs-390.06
- R2-LOWBAND 2025: 1 rows, Rs-116.75
- F4 2026: 355 rows, Rs103,055.93
- GAP-FADE 2026: 219 rows, Rs1,492.21
- GAP-FADE-INC 2026: 73 rows, Rs4,763.03
- INV-ABOVE 2026: 36 rows, Rs3,349.21
- INV-LONG 2026: 182 rows, Rs50,160.09
- INV-R3 2026: 4 rows, Rs763.95
- N4-V3 2026: 34 rows, Rs29,562.32
- P2F 2026: 31 rows, Rs20,116.78
- P2F-R2 2026: 32 rows, Rs15,149.33
- R2-LOWBAND 2026: 3 rows, Rs1,283.36

## Timing certification (every admission feature)
| Feature | Knowable at | Why it is causal |
|---|---|---|
| Prior close, 50DMA, 50DMA slope, regime label, below/above-trend | Before the session opens | Daily closes through the prior session only |
| Results-reaction-day status | Before the reaction session | Certified set (R6-11): the filing must be timestamped before the reaction day; a same-day intraday announcement NEVER qualifies its own day (4 rows voided on exactly this in the R6-11 audit; the certified book carries none) |
| Signed move by 09:30 (N4-V3, FLOOR-2) | 09:30 | Close of the 09:25 bar vs prior close; entry is the 09:35 bar |
| Overnight gap (GAP-FADE family) | 09:15 | The day's open print vs prior close; entries are the 09:20 / 09:40 bars |
| First morning move (F4) | 10:00 | Bars through the 10:00 bar; entries strictly after |
| INV pool signals | The signal bar | Entries strictly after the signal bar by construction (frozen cached populations, audited in their rounds) |
| Exits (targets/stops) | The exit bar | First-passage on bars at/after entry; no exit uses a later bar |

## December 2026 — PRE-REGISTERED pass / kill lines
Judged on December 2026 live paper under this exact spec, same
basis (per 100 shares, Rs40/trade):
- **PASS:** December net > Rs0 AND no ISO week of December
  worse than -Rs15,000 AND >= 20 trades.
- **FLOOR LINE (reported separately):** December net >=
  Rs15,000 = one month at the segment floor pace.
- **KILL:** December net <= Rs0 — the book is judged in-sample
  fit and the floor claim for this book is withdrawn.
- **EXTEND:** fewer than 20 December trades -> judging extends
  to January 2027 under the same lines, cumulatively.
- **No parameter changes in December.** Any change voids the
  freeze and starts a new candidate.

## ADDENDUM (R11-08, same day) — the ending book
After this freeze was cut, Round 11 banked the cross-family pair (R11-03): the book judged in December is the frozen book above PLUS two frozen constructions — NE-REV-NU (NOTCH+UPGUARD conditioned NE-REV LONG, signal 10:25 / entry 10:35, thr 2.0%, T100/S065, certified non-event population) and REXP-DOWN (range-expansion SHORT in DOWN regime cells, entry 10:20, T100/S065) — both reproduced from their Round-8/9 anchored builders at banking time with 0 timing violations. Ending book: 2025 Jan-Oct 99363.06 on 1128 rows; 2026 Jan-Oct 247540.89 on 1368 rows. The December pass/kill lines above apply to the ending book as a whole.

## ADDENDUM (R12-09, same day) — the ending book after Round 12
Round 12 banked one further change (R12-02): the INV-ABOVE hard-dip exclusion — INV-ABOVE rows whose index state at the entry instant (close of the last 5-min NIFTY bar completing at entry vs prior close) is a hard dip (<= -0.30%) are not traded (23 rows removed in 2025, 16 in 2026; the state is knowable at the entry instant by construction — the bucketed bar completes exactly at entry). The book judged in December is the R11-08 ending book PLUS this exclusion. Ending book: 2025 Jan-Oct 101114.78 on 1105 rows; 2026 Jan-Oct 251553.07 on 1352 rows. Regeneration verification PASSED (R12-09): rebuilt from the Round-11 CSVs by fresh code, the book matches the exported Round-12 CSVs row-for-row and to the paisa in both years. The December pass/kill lines above apply to the ending book as a whole.

## ADDENDUM (R13-08, same day) — the ending book after Round 13
Round 13 banked one further change (R13-05): the REXP-DOWN sleeve's exit geometry moves from T100/S065 to **T100/S050** — the sleeve's population, admission and entry (SHORT, DOWN regime cells, 10:20 entry) are unchanged; only the stop tightens from 0.65% to 0.50% (41 rows in 2025, 86 in 2026; sleeve Jan-Oct +10,243.45 / -5,899.72 at T100/S065 -> +12,486.11 / -4,384.34 at T100/S050). Exit geometry carries no admission information, so the freeze's timing argument is unaffected. The book judged in December is the R12-09 ending book PLUS this geometry change. Ending book: 2025 Jan-Oct 103357.44 on 1105 rows; 2026 Jan-Oct 253068.45 on 1352 rows. Regeneration verification PASSED (R13-08): rebuilt from the Round-12 CSVs by fresh code, the book matches the exported Round-13 CSVs row-for-row and to the paisa in both years. The December pass/kill lines above apply to the ending book as a whole.

## ADDENDUM (R14-08, same day) — the ending book after Round 14
Round 14 banked two further exit-geometry changes, both whole-sleeve swaps gated on the Round-13 ending book: (1) R14-04 — the INV-ABOVE sleeve's exit geometry moves from T125/S050 to **T150/S050** (target step only; population re-formed by the chain at the new geometry under the incumbent law — ADR >= 3.0, rounds <= 2, entry < 10:30 — with the R12-02 hard-dip exclusion re-applied to the new rows, dropping 22 / 15 rows; sleeve Jan-Oct +10,463.16 / +7,361.39 at the old cell -> +12,513.28 / +10,114.82 at T150/S050). (2) R14-05 — the GAP-FADE family's exit geometry moves from T125/S050 to **T125/S065** (stop step only, both GAP-FADE and GAP-FADE-INC; populations, bands, cells and entries unchanged; family Jan-Oct +23,775.49 / +6,255.24 at the old cell -> +24,355.17 / +7,733.66 at T125/S065). Exit geometry carries no admission information, so the freeze's timing argument is unaffected. The book judged in December is the R13-08 ending book PLUS these two geometry changes. Ending book: 2025 Jan-Oct 105987.24 on 1101 rows; 2026 Jan-Oct 257300.3 on 1352 rows. Regeneration verification PASSED (R14-08): rebuilt from the Round-13 CSVs by fresh code, the book matches the exported Round-14 CSVs row-for-row and to the paisa in both years. The December pass/kill lines above apply to the ending book as a whole.

## ADDENDUM (R15-08, same day) — Round 15: the frozen book is UNCHANGED
Round 15 banked nothing, so the book judged in December is exactly the Round-14 ending book (the R13-08 book with INV-ABOVE at T150/S050 and the GAP-FADE family at T125/S065), at 2025 Jan-Oct 105987.24 on 1101 rows and 2026 Jan-Oct 257300.3 on 1352 rows. Round 15's tested cells are NOT in the frozen book: INV-ABOVE T175/S050 (rejected on leg (c) only; flagged for the owner — adoption from the ending book: 2025 JO +92.57 / 2026 JO -1,198.29), the GAP-FADE family at T125/S080 (rejected on four legs; the family's stop axis is closed at S065), and NO volume-conditioned form (the volume data axis was built this round — stocks_daily_volume.csv — under the causality law that a day's volume may condition only later days' decisions; the frozen rvol >= 1.0 diagnostic was negative on F4, N4-V3 and the P2F family, so no volume gate ran and no volume rule is frozen). Regeneration verification PASSED (R15-08): the exported Round-15 CSVs match a fresh load of the Round-14 CSVs row-for-row and to the paisa in both years. The December pass/kill lines above apply to the book as a whole, unchanged.

## ADDENDUM (R16-06, same day) — Round 16: the frozen book is UNCHANGED
Round 16 banked nothing, so the book judged in December is exactly the Round-15 ending book (the Round-14 book: INV-ABOVE at T150/S050, the GAP-FADE family at T125/S065), at 2025 Jan-Oct 105987.24 on 1101 rows and 2026 Jan-Oct 257300.3 on 1352 rows. Round 16's tested cells are NOT in the frozen book: the volume MIRROR forms (keep prior-day relative volume < 1.0 vs the trailing-20-day median, the exact complement of Round 15's frozen feature, under the same causality law — a day's volume conditions only later days' decisions) were gated whole-book and refused: F4 mirror rejected on legs (a) + (b) + (c) + (e) + (f) (2025 JO -2,064.08 / 2026 JO -53,727.42; March 2026 flips), N4-V3 mirror rejected on (a) + (b) + (c) + (e) (2025 JO -3,937.27 / 2026 JO -24,363.08); the P2F-family mirror was not run (the pre-registered condition — a banking or a single-leg near-miss in WS1/WS2 — was not met). The frozen band's volume axis is now measured in BOTH directions on the two largest sleeves and separates nothing: no volume rule is frozen. Regeneration verification PASSED (R16-06): the exported Round-16 CSVs match a fresh load of the Round-15 CSVs row-for-row and to the paisa in both years. The December pass/kill lines above apply to the book as a whole, unchanged.

## ADDENDUM (ADOPTION, 2026-11-02 16:48 IST) — this freeze is SUPERSEDED as the December candidate
By owner direction (Chandu, 2026-11-02 16:48 IST — "You apply the fix and run again"), **Variant C (the NE-REV-NOTCH+UPGUARD stack, R9-04 form) is adopted as the Stocks candidate book, effective now.** The book judged in December 2026 is the ADOPTED book, frozen in its own document: `stocks_engine_adopted_variantC_FREEZE_dec2026.md`, with its own December pass/kill lines re-registered there (same structure: PASS net > Rs0 + no ISO week < -Rs15,000 + >= 20 trades; FLOOR LINE net >= Rs15,000; KILL net <= Rs0). The book frozen in THIS document (the Round-16 ending book: 2025 Jan-Oct Rs105,987.24 on 1,101 rows; 2026 Jan-Oct Rs257,300.30 on 1,352 rows) stays on record as the **comparison baseline** — it is no longer the December candidate, and the pass/kill lines above no longer apply to it.
Adoption verification (same run, `stocks_engine_adoptC_verify.py`; evidence `stocks_adoption_variantC_results.json`): the Variant C book rebuilt from the Round-16 ending book reproduces the expected totals EXACTLY — **2025 Jan-Oct Rs119,813.44 (Rs11,981.34/month; gap to floor Rs30,186.56)** and **2026 Jan-Oct Rs247,178.79 (Rs24,717.88/month; floor MET)** — and is row-for-row identical to the R9-04 gated book. The construction's frozen gate sheet (R9-04, vs its birth baseline) passes all ten legs and was reproduced exactly in the adoption run (placebos Rs174,662.47 / Rs344,925.15 / Rs322,968.45). Re-gated against THIS book (the pre-adoption baseline), the adopted book passes 8 of 10 legs; legs (c) 2026-no-fall (-Rs10,121.51) and (e) combined ex-top-3 (-Rs16,352.41) fail on that comparison and stand as **failed-and-waived by the owner's direction**, recorded in full in the adopted book's freeze and in `stocks_adoption_variantC_2026-11-02.md`. Nothing in this document's frozen spec was edited; the November SarvaRitu book, scorecards, loggers, specs and logs are untouched by the adoption.
