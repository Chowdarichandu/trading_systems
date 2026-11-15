# FREEZE — ADOPTED BOOK: VARIANT C STACK (SarvaRitu), for DECEMBER 2026 judging
**Adopted:** 2026-11-02, by owner direction (Chandu, 16:48 IST —
"You apply the fix and run again"). **Status:** this book
SUPERSEDES the banked book of
`stocks_engine_banked_book_FREEZE_dec2026.md` as the December
2026 candidate. The pre-adoption (Round-16) book stays on
record as the comparison baseline; it is no longer the book
judged in December.
**Construction:** the frozen R9-04 stack — R2-26 INV-ABOVE
swap + R5-03-clean GAP-FADE swap (GAP-FADE-INC retired) +
NE-REV-NOTCH+UPGUARD (NE-REV-NU) slot + R7-03 REXP add —
applied to the Round-16 ending book by the generalised
construction used for every stack restatement since R12
(the book's NE-REV*/REXP rows are stripped first: they are
alternative forms of the same sleeves, replaced — never
doubled — by the stack forms).
**Basis:** equity cash intraday · Chandu's 25 watchlist
stocks · provisional per 100 shares · Rs40/trade · paper
only, real money Rs0 · same-day re-entry allowed · no
volume features.

## The frozen (adopted) book — regeneration-verified at adoption
Built 2026-11-02 by `stocks_engine_adoptC_verify.py` and
verified three ways in the same run (see "Regeneration
verification" below):

| Year | Trades (full) | Full total | Jan-Oct | Jan-Oct trades | Ex-top-3 (full) |
|---|---|---|---|---|---|
| 2025 | 1,108 | Rs121,764.83 | Rs119,813.44 | 1,064 | Rs46,266.80 |
| 2026 | 1,363 | Rs247,178.79 | Rs247,178.79 | 1,363 | Rs55,557.16 |

2025 months: {'2025-01': 4476.9, '2025-02': 25913.57, '2025-03': 8412.63, '2025-04': 53220.39, '2025-05': 6518.38, '2025-06': 1802.59, '2025-07': -660.91, '2025-08': 13486.06, '2025-09': 10686.5, '2025-10': -4042.67, '2025-11': 4.51, '2025-12': 1946.88}
2026 months: {'2026-01': 28021.1, '2026-02': 12576.14, '2026-03': 18225.72, '2026-04': 46744.31, '2026-05': 43842.74, '2026-06': 6756.75, '2026-07': 10284.46, '2026-08': 10106.06, '2026-09': 14494.14, '2026-10': 56127.37}
2025 halves (Jan-Oct): H1 Rs98,541.87 / H2 Rs21,271.57 · 2026 halves: H1 Rs149,410.01 / H2 Rs97,768.78
Regime cells 2025 (full): {'DOWN': 66566.97, 'FLAT': 30787.4, 'UP': 24410.46} · 2026: {'DOWN': 219008.9, 'FLAT': 11915.35, 'UP': 16254.54}
Top-3 stocks 2025: [('OBEROIRLTY', 39542.99), ('ASTRAL', 22268.52), ('GODREJCP', 13686.52)] · 2026: [('TVSMOTOR', 101522.89), ('OBEROIRLTY', 47976.08), ('ASTRAL', 42122.66)]
Floor status of this book: 2025 Jan-Oct Rs119,813.44 =
**Rs11,981.34/month — floor NOT met, gap Rs30,186.56** ·
2026 Jan-Oct Rs247,178.79 = **Rs24,717.88/month — floor
MET** (Rs97,178.79 above the line).
Exports: `stocks_engine_adoptedC_book2025_trades.csv`,
`stocks_engine_adoptedC_book2026_trades.csv` (independently
re-summed at export, exact).

## Universe (25, frozen)
GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR

## Regime law (frozen — REGIME-CLASSIFIER-1)
From NIFTY daily closes through the PRIOR session: UP = prior
close > 50DMA and the 5-day 50DMA slope >= 0; DOWN = prior
close <= 50DMA and slope <= 0; else FLAT. "Below-trend" = prior
close <= 50DMA (the SarvaRitu law governing F4 / INV-LONG).

## Components (frozen constructions; builders are the operative definition)
Sleeves marked UNCHANGED are row-identical to the pre-adoption
book (verified in the adoption run). Sleeves marked STACK FORM
replace the corresponding pre-adoption sleeve wholesale.

| Component | Admission (all knowable at the decision bar) | Entry | Exits |
|---|---|---|---|
| F4 (UNCHANGED) | Below-trend day; the stock's first morning move in [0.5%, 1.0%) by the 10:00 bar; follow that direction; frozen exclusion set incl. the direction-scoped slices banked in the saturation run | First bar after 10:00 | T150 / S095 |
| INV-LONG (UNCHANGED) | Below-trend pool days (prior close <= 50DMA); frozen pool machinery (stocks_engine_r2_lib), rounds <= 3, 11:00 cutoff (Round-2 banking); mechanism-scoped exclusions (BDL, VEDL, HINDZINC, KALYANKJIL, INDUSTOWER) | Per frozen pool machinery, strictly after the signal bar | T125 / S050 |
| INV-R3 (UNCHANGED) | Below-trend pool days; the Round-2 INV pool's R3 sub-form (stocks_engine_r2_lib) | Per frozen pool machinery | T125 / S050 |
| N4-V3 (UNCHANGED) | CERTIFIED results-reaction day only (R6-11 standard, below); signed move by 09:30 >= +1.0% or <= -1.0% -> follow, at the population carried from the Round-2 ending book (the R2-17 threshold banking and the FLOOR-2 cap are inside the carried rows); FLOOR-2: no LONG entry when the signed move by 09:30 >= +3.0%; FLOOR-4: no HDFCBANK LONG | 09:35 bar | T150 / S080 |
| P2F (UNCHANGED) | Results reaction >= 2.5% (certified set); follow at R+1; exclusions ASTRAL, HINDUNILVR (mechanism-scoped) | R+1 session, frozen machinery | T125 / S050 |
| P2F-R2 (UNCHANGED) | Same reaction set and exclusions, followed at R+2 | R+2 session | T125 / S050 |
| R2-LOWBAND (UNCHANGED) | Reactions in [2.0%, 2.5%) at R+2; stands aside on UP-regime days | R+2 session | T125 / S050 |
| INV-ABOVE (STACK FORM — R2-26) | Above-trend pool days; the ANCHORED Round-2 population (r2_cache `inv_pop_T150S080`, via the frozen INV pool machinery), re-exited at the R2-26 cell. This population does NOT carry the pre-adoption book's R12-02 hard-dip exclusion or the R14-04 geometry — the stack form replaces that sleeve wholesale (131 rows 2025 / 31 rows 2026; sleeve full-period +Rs17,248.75 / +Rs7,471.54 in this book) | Per frozen pool machinery, strictly after the signal bar | T150 / S080 |
| GAP-FADE (STACK FORM — R5-03-clean) | Overnight gap <= -1.25% (open vs prior close); fade LONG; regime cells DOWN + FLAT only (112 rows 2025 / 292 rows 2026; sleeve +Rs32,064.93 / +Rs4,270.42). The pre-adoption book's >=1.5% sleeve and its R14-05 S065 geometry are replaced by this frozen cell | 09:20 bar | T125 / S050 |
| GAP-FADE-INC | **RETIRED — not in this book** (its [-1.5%, -1.25%) band is inside the R5-03-clean sleeve's >=1.25% population) | — | — |
| NE-REV-NU (STACK SLOT) | CERTIFIED non-event population (R6-11 standard): a stock-day with no certified results event; the stock's morning fall >= 2.0% at the 10:25 signal bar -> LONG reversal. Admission requires BOTH state conditions on NIFTY's 10:25-bar move vs prior close: NOTCH — the move is NOT in the open band (-0.30%, 0); UPGUARD — on UP-regime days only, the move is >= 0. A row whose state is unknown is NOT admitted (counted; 0 unknown in both years at build). 200 rows 2025 / 313 rows 2026; standalone +Rs12,596.19 / +Rs23,744.40 | 10:35 bar (signal 10:25) | T100 / S065 |
| REXP (STACK ADD — R7-03 form) | Range-expansion SHORT, DOWN regime cells only (41 rows 2025 / 86 rows 2026; standalone +Rs14,870.39 / -Rs8,399.33) | 10:20 bar | T125 / S050 |

## Timing certification (every admission feature)
| Feature | Knowable at | Why it is causal |
|---|---|---|
| Prior close, 50DMA, 50DMA slope, regime label, below/above-trend | Before the session opens | Daily closes through the prior session only |
| Results-reaction-day status / certified non-event status | Before the reaction session | Certified set (R6-11): the filing must be timestamped before the reaction day; a same-day intraday announcement NEVER qualifies its own day (4 rows voided on exactly this in the R6-11 audit; the certified book carries none) |
| Signed move by 09:30 (N4-V3, FLOOR-2) | 09:30 | Close of the 09:25 bar vs prior close; entry is the 09:35 bar |
| Overnight gap (GAP-FADE clean sleeve) | 09:15 | The day's open print vs prior close; entry is the 09:20 bar |
| First morning move (F4) | 10:00 | Bars through the 10:00 bar; entries strictly after |
| INV pool signals (INV-LONG / INV-R3 / INV-ABOVE R2-26 population) | The signal bar | Entries strictly after the signal bar by construction (frozen cached populations, audited in their rounds and re-anchored at R8-01 / R9) |
| NE-REV-NU signal + state | 10:30 | The stock's fall is measured at the 10:25 bar; both state conditions read NIFTY's 10:25-bar close vs prior close — that bar completes at 10:30, strictly before every 10:35 entry. Counted timing violations at build: 0 |
| REXP signal state | The bar before entry | Range-expansion state complete before the 10:20 entry; counted timing violations at build (R7/R8 builders): 0 |
| Exits (targets/stops) | The exit bar | First-passage on bars at/after entry; no exit uses a later bar |

## Gate record at adoption (both sheets, verbatim — see the adoption report)
- **Frozen construction gate (R9-04, vs its birth baseline):**
  PASSES ALL TEN LEGS — reproduced EXACTLY in the adoption
  run (legs, sums Rs306,737.52 -> Rs368,943.62, scorecards,
  placebos P1 Rs174,662.47 / P2 Rs344,925.15 / P3
  Rs322,968.45; timing violations 0).
- **Re-gate vs the pre-adoption (Round-16) book, same run:**
  8 of 10 legs pass — combined rises (+Rs4,054.14), 2025
  rises on both measures, no month flips, no half flips,
  cells positive, placebos beaten, timing clean, leg (x)
  holds. Legs **(c)** and **(e)** FAIL on this comparison:
  2026 Jan-Oct Rs247,178.79 vs the pre-adoption book's
  Rs257,300.30 (-Rs10,121.51), and combined ex-top-3
  Rs101,823.96 vs Rs118,176.37 (-Rs16,352.41) — the
  pre-adoption book's post-R9 bankings (the pair at
  T100/S050, the INV-ABOVE target step, the fade stop step)
  out-earn the stack's frozen forms in 2026. These two legs
  stand as **failed-and-waived by the owner's direction**
  (the direction was given with C's adoption values vs the
  current book — +Rs13,826.20 / -Rs10,121.51 — already on
  record since Round 13). Nothing is edited or hidden.

## Regeneration verification (adoption run, 2026-11-02)
Chain: Round-16 CSVs (themselves regeneration-verified
through the R8->R16 chain in the banked-book freeze) ->
strip NE-REV*/REXP rows -> R2-26 swap (anchored population)
-> R5-03-clean swap (anchored sleeve) with GAP-FADE-INC
retired -> NE-REV-NU slot (anchored conditioned rows) ->
REXP add (anchored rows). Verified in
`stocks_engine_adoptC_verify.py` (evidence:
`stocks_adoption_variantC_results.json`):
1. Jan-Oct totals reproduce the expected prices EXACTLY:
   2025 Rs119,813.44 / 2026 Rs247,178.79.
2. The book built from the Round-16 baseline is
   ROW-FOR-ROW IDENTICAL (multiset on comp/date/stock/dir/
   entry_time/net) to the book built on the construction's
   birth baseline — i.e. this freeze's spec reproduces the
   R9-04 gated book exactly.
3. Exported CSVs independently re-summed: exact, both years.

## December 2026 — PRE-REGISTERED pass / kill lines (re-registered for THIS book)
Judged on December 2026 live paper under this exact spec,
same basis (per 100 shares, Rs40/trade):
- **PASS:** December net > Rs0 AND no ISO week of December
  worse than -Rs15,000 AND >= 20 trades.
- **FLOOR LINE (reported separately):** December net >=
  Rs15,000 = one month at the segment floor pace.
- **KILL:** December net <= Rs0 — the book is judged
  in-sample fit and the floor claim for this book is
  withdrawn.
- **EXTEND:** fewer than 20 December trades -> judging
  extends to January 2027 under the same lines, cumulatively.
- **No parameter changes in December.** Any change voids
  this freeze and starts a new candidate.
