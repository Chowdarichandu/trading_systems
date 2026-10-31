# THE SARVARITU ROOF — every stocks strategy, one registry

**User order 2026-10-31 20:59 IST: "All stocks strategies under one roof."**
From that order, **SarvaRitu is the single umbrella for ALL of Chandu's
stocks work** (equity cash intraday, his 25 watchlist stocks, paper only,
real ₹0, provisional per 100 shares, ₹40/trade). Every stocks strategy is
either a component of the SarvaRitu book, a registered scorecard/candidate
feeding it, or closed. Nothing stocks-related runs as a scattered
standalone. Index work (CRACK / ACRACK) is a different house — not here.

## THE REGISTRY RULE (binding)

1. A new stocks strategy joins the roof **only as a SarvaRitu component,
   through the engine gate**: controls + timing/leak audit in the same run
   as its first scoring, scored on BOTH 2025 and 2026 (cross-year gate),
   and — under the current v3 charter — the maximin constraints (no year's
   total falls, no regime cell goes negative, combined total does not
   fall). No exceptions, no side doors.
2. A standalone stocks experiment must be **registered in this file as a
   CANDIDATE before any scoring** (name, one-line rule, frozen spec path).
   An unregistered experiment's numbers do not exist as far as the roof
   is concerned.
3. Anything killed is moved to CLOSED below with its one-line cause.
   Closed lines are not re-opened except on the fresh-evidence condition
   recorded in the lessons (`stocks_engine_lessons.md`).

## A. IN THE BOOK — the SarvaRitu components (7)

The frozen book (post-C24 v2 state) is under FORWARD TEST Nov–Dec 2026:
spec `stocks_sarvaritu_forward_spec.md`, logger
`stocks_sarvaritu_logger.py`, log `stocks_sarvaritu_paper_log.csv`,
daily summary `stocks_sarvaritu_daily_summary.md`, cron
`stocks-sarvaritu-paper-logging` (Mon–Fri ~16:35 IST). Frozen book dumps:
`stocks_engine_v2_c24_book2025_trades.csv` /
`stocks_engine_v2_c24_book2026_trades.csv`.

| # | Component | What it does (one line) | Status |
|---|---|---|---|
| 1 | **F4** | On below-trend days (NIFTY prior close ≤ 50DMA), follows the first morning move of 0.5–1.0% measured by 10:00; exits T150/S095; 12 mechanism-scoped direction exclusions. This IS the M2 state-gated cell (see §C) — inside the book, not a separate candidate. | IN THE BOOK |
| 2 | **INV-LONG** | The INV pool (round ≤ 2, entry < 10:30, ADR ≥ 3.0) bought LONG on below-trend days; T125/S050; excludes BDL/VEDL/HINDZINC/INDUSTOWER/KALYANKJIL + (v2 law) HINDALCO/UNITDSPR/TATASTEEL. | IN THE BOOK |
| 3 | **INV-ABOVE** | The identical INV pool bought LONG on above-trend days (v2 Cycle 22 — the up-market sleeve); T125/S050, same exclusions; stands aside on FLAT days for INV-LONG per C24 law. | IN THE BOOK |
| 4 | **N4-V3** | Results/news reaction day: if the stock has moved ≥ 1% by 09:30, follow it from 09:35; book exits T150/S080; excludes ASTRAL, TVSMOTOR LONG, OIL LONG + v2 deletions. | IN THE BOOK |
| 5 | **P2F** | Big results reaction (≥ 2.5% on reaction day) followed at the next day's (R+1) 09:15 open; T125/S050; excludes ASTRAL, HINDUNILVR, HINDALCO LONG. | IN THE BOOK |
| 6 | **P2F-R2** | The same ≥ 2.5% follow-through, entered two days after the reaction (R+2); T125/S050; no TVSMOTOR LONG + v2 deletions. | IN THE BOOK |
| 7 | **R2-LOWBAND** | Smaller results reactions (2.0–2.5%) followed at R+2; T125/S050; stands aside on UP days (C23 law). | IN THE BOOK |

Book-wide law: **RF-1** (no trades on weekend/special sessions) and the
v2 (component × stock × direction) deletions listed in the forward spec.

## B. FORWARD TEST — component scorecards (November 2026)

These three loggers are scorecards INSIDE the roof for book components.
Their frozen November variants differ from the book versions in exits —
that is deliberate: each is judged by its own frozen spec, on its own log.

| Scorecard | What it is | Book counterpart | Log / spec |
|---|---|---|---|
| **N4-V3 PRIMARY (T125/S050)** | The results-reaction system exactly as originally frozen (56 tr, +₹7,990.43 in-sample, timing-audited clean), run as November's primary paper test. | N4-V3 (book runs T150/S080) | Log `stocks_n4_november_paper_log.csv`; cron `stocks-n4-november-paper-logging` (Mon–Fri ~15:52 IST) |
| **INV1 shadow** | The INV pool in BOTH directions (T125/S050), shadow-logged; the direction split is what the INV-LONG v2 candidate (§C) rests on. | INV-LONG / INV-ABOVE (book is LONG-only) | Log `stocks_p2inv_november_shadow_log.csv`; spec `stocks_p2inv_november_shadow_spec.md`; cron `stocks-p2inv-november-shadow-logging` (~16:52 IST) |
| **P2F shadow** | P2F at the frozen home-25 rule (2.0%/2.5% bands, R+1), shadow-logged; first trade pre-booked: GODREJCP SHORT, Mon 2026-11-02 09:15 open. | P2F (book: 2.5% band only) | Log `stocks_p2f_november_shadow_log.csv`; spec `stocks_p2f_november_shadow_spec.md`; cron `stocks-p2f-november-shadow-logging` (~17:22 IST) |

Judging (frozen, per `stocks_REAL_status.md`): N4-V3 positive November →
stands as primary; INV1 positive + ≥ 20 trades → candidate; P2F T125
positive + ≥ 8 trades → candidate; negatives are killed; thin/zero
samples extend or are inconclusive per each spec. No re-tuning during
November.

## C. CANDIDATES — registered, awaiting December fresh-window judging

| Candidate | What it is | Spec / note |
|---|---|---|
| **INV-LONG v2** | The INV line's v2 candidate: the P2 pool, LONG-only on the inverted (below-trend) condition — the direction restriction suggested by the INV1 direction split. A hypothesis with a frozen shape; verdict requires the fresh window declared in its spec. Does NOT change the November INV1 shadow. | `stocks_inv_v2_candidate_spec.md` (frozen 2026-10-31) |
| **DBL-LONG** | The DBL condition (Line 1's near-miss) with the LONG-only step applied; passed the tuning loop's full pass gate in-sample. DISCLOSED: `stocks_REAL_status.md` records DBL-LONG failing the transfer test to the ext 25 (H2 −₹3,339.63, breadth 5/25) — it survives only as a home-25 December candidate under its frozen spec, judged on fresh December data. | `stocks_dbl_candidate_spec.md` (frozen 2026-10-31) |

(The M2 F4 state-gated cell from `stocks_M2_candidate_spec.md` is **not**
a separate candidate anymore: its rule is the book's F4 component (§A.1),
carried into the SarvaRitu forward test Nov–Dec. The v1 engine's December
candidate spec, `stocks_engine_candidate_spec.md`, froze the same book
for December judging — that judging is now executed as the SarvaRitu
whole-book forward test, Nov + Dec scored separately.)

## D. THE TUNING PROGRAMME — inside the roof

| Programme | What it is | Status |
|---|---|---|
| **Engine v3 — maximin tuning** | Tunes the SarvaRitu book on history (2025 + 2026): raise the WORST month toward ≥ +₹10,000, then toward ₹15,000, under the hard constraints (neither year falls, all regime cells stay positive, combined never falls). The frozen forward test is untouched; anything v3 banks is a NEW version for a later fresh test. | RUNNING — charter: v3 section of `stocks_RECURSIVE_ENGINE.md`; state: `stocks_engine_state.json` (v3 block); lessons: `stocks_engine_lessons.md` |

## E. OUTSIDE THE ROOF — by the user's scope rule

| Strategy | Why outside |
|---|---|
| **T2 P2F 3.0% band** (`stocks_T2_candidate_spec.md`) | Pooled 50-stock universe (his 25 + ext 25). His rule: "Run only on my stocks." It faces its own December judging on the pooled universe, outside SarvaRitu; the 4.0% nested variant cannot upgrade alone. |
| **O2 11:00 fade** (`stocks_O2_candidate_spec.md`) | Ext-25 large caps only — the fade was flat on his 25 (a large-cap phenomenon). Outside by the same scope rule; own December judging (≥ 40 trades). |

## F. CLOSED — dead lines (one line each; evidence in `stocks_REAL_status.md` and `stocks_engine_lessons.md`)

- **Morning-Mover (all versions) + A2/B2/B3** — look-ahead artefact; honest rebuilds negative at every measurement time. Its two November shadow loggers were DISABLED before launch.
- **EventBook (N4-V3 + P2F as one book)** — killed by its own concentration stress (ex-top-3 negative).
- **S-system (S1–S12)** — superseded: built on the wrong instrument assumption (stock options framing); stocks are equity cash only.
- **L1 levels family** — stale placebos beat the real rules in all 18 cells; level events are information-free on his 25 at 5-minute scale.
- **R1 mover neighbourhood / R2 follow-through & gaps / R3 INV→ext transfer** — closed on controlled runs (dead or non-transferring).
- **G1 state-gate transfer, RSI1 (indicator), EXTREME-HUNT, LADDER + volume, SNAP, cross-sectional RS, transplanted index systems (V5 / Day-Trader skill / (lA) as stock entries)** — negative totals or expectancy that flips sign between halves.
- **DBL-LONG on ext** — fails transfer (see §C disclosure); the home-25 candidate survives, the ext line does not.

## Reporting — one report under the roof

The consolidated **SarvaRitu report** is the Friday roll-up of the
`stocks-sarvaritu-paper-logging` cron in the Stocks chat: whole-book week
+ month-to-date vs the user's acceptance band (₹15,000–₹25,000/month for
all SarvaRitu modules combined — his updated standard, 2026-10-31
21:00 IST) and the ₹10k monthly minimum + the three component scorecards
(§B) + one line on v3 tuning status (§D). Month
verdicts land at November-end and after December per the frozen spec.
