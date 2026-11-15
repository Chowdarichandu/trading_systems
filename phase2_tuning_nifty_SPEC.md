# PHASE-2 TUNING — NIFTY · SELECTIVITY (CONFIDENCE-GATING) · SPEC FROZEN BEFORE SCORING

**Frozen:** 2026-11-14 08:56 IST — before any subset was scored. Nothing in
this spec may be edited after the run; deviations are reported, not absorbed.

**Order:** owner's direct order, 2026-11-14 08:54 IST — "the next phase of
tuning to be started now for both entities (Bank Nifty, Nifty)". This spec
covers NIFTY only. Research only: no book, ledger or job is changed.

**Owner's principle driving the phase (his words, 2026-11-14):** if the
system is not confident about a trade, it should keep its hands idle — idle
is better than a marginal trade. This phase therefore tunes SELECTIVITY
only: which of the standing book's legs to stand down. No exit changes, no
new signals, no admission changes. Buying only, 1 lot (65), premiums basis,
cost ₹220/trade already inside every stored net.

## Subject book and leg store

- **Book:** Nifty TUNED v1 (EVE-07) = DEC-S1 − B PE. The standing/lead book
  with the only Nifty November forward record. TUNED v2 is NOT the subject
  (zero forward legs); the subject is not switched mid-run.
- **Store:** `november_books_fix_repair_nifty_legs.csv` — the gated leg
  store the ₹900 verification and the books-fix (N-FIX-1) runs used.
  Columns: date, side, family (A/B/C), rep, entry_time, bucket,
  entry_premium, gap_pct, regime, exit_class, net_inr, stood_down,
  repaired_net_inr. The v1 population is all 74 rows (the file carries no
  B-PE rows — verified); `net_inr` is the v1 leg net.

## Step 0 — Control (gate to everything else)

Reproduce from the store, exactly: **74 legs · total +₹103,050.25 · WR
51.4% (38 wins) · 66 trade-days · ₹1,561.37/trade-day · March 2026
−₹1,216.50 (the only red month)**. Also reproduce the N-FIX-1 anchors from
the same store (8 stood-down legs, −₹14,119.75; repaired total
+₹117,170.00) since the distinctness overlap is computed against them. If
any figure does not reproduce, STOP and report — no scoring.

## Step 1 — Composite confidence score (entry-knowable factors only)

Equal-weight mean of the available factor scores, each in [0.30, 1.00] or
{0.2, 0.5, 1.0} as defined. NO fitted weights. Factor audit:

| Factor | Source field | Knowable at entry bar? | Definition |
|---|---|---|---|
| F_time — entry-time bucket | `bucket` | YES — the entry bar's own clock time | pre-11:00 = 1.00 · 11:00–12:30 = 0.60 · post-12:30 = 0.30 (runway to the +90 target before the 15:20 square-off shrinks through the day) |
| F_gap — signed gap aligned with side | `gap_pct`, `side` | YES — the overnight gap is fixed at the 09:15 open, before every entry | aligned (CE & gap > 0, or PE & gap < 0) = 1.00 · \|gap\| < 0.10% = 0.50 (no overnight information) · counter-aligned = 0.20 |
| F_prem — entry premium vs book median | `entry_premium` | YES, given the frozen constant — the book's median premium ₹213.025 is a fixed statistic of the gated Jan–Oct store, carried as a constant | r = premium / 213.025; F = 1 − 0.7 · min(1, \|ln r\| / ln 4). r = 1 → 1.00; r = 2 or ½ → 0.65; r ≥ 4 or ≤ ¼ → 0.30 (mid-band premiums are the book's home turf under fixed-point geometry; extremes are noise-dominated) |
| F_exp — weekly-expiry-day flag | `date` weekday | YES — the expiry calendar is known in advance | date is a Tuesday (2026 Nifty weekly expiry; cross-check: all 13 family-C legs fall on Tuesdays) AND family ≠ C → 0.70 (pin/theta noise on legs not built for expiry day); otherwise 1.00 (C legs are expiry-native) |
| F_src — agreeing-source count | — | **NOT CARRIED by the store** — `rep` names a single producing source per leg and the frozen r11 dump carries no source list | **DROPPED**, stated here, not approximated |
| F_base — second-leg base outcome | — | **NOT APPLICABLE** — TUNED v1 (DEC-S1 components A/B/C) has no second-leg structure; second legs belong to the NS1 frames | **DROPPED**, stated here |

Composite = (F_time + F_gap + F_prem + F_exp) / 4.

## Step 2 — Threshold grid (pre-registered)

Rank all 74 legs by composite score, descending; ties broken by (date asc,
entry_time asc) — deterministic. Keep the top:
- **T70:** k = round(0.70 × 74) = **52 legs**
- **T60:** k = round(0.60 × 74) = **44 legs**
- **T50:** k = round(0.50 × 74) = **37 legs**

The idled remainder is the stand-down set. Record each threshold's cutoff
score (the k-th leg's score).

Per kept subset, report: total, legs, distinct trade-days, WR (legs),
₹/trade-day, green/red/no-trade days over the 205-day Jan–Oct 2026
calendar (day net > 0 / < 0 / no kept leg; calendar =
`volrix/nifty_daily_2019_2026.csv`), full month table (Jan–Oct nets),
halves (H1 = Jan–May legs, H2 = Jun–Oct legs, totals), ex-top-3 (total
minus the 3 largest leg nets).

## Step 3 — Placebo (pre-registered)

Per threshold: 200 uniform random subsets of exactly k legs drawn without
replacement from the 74 (RNG: Python `random.Random(20261114)`, draws in
threshold order T70, T60, T50). Placebo percentile = fraction of the 200
whose total is strictly below the kept subset's total. Matching random
thinning must not reproduce the kept subset — random selection of the same
size is the null.

## Step 4 — Distinctness (pre-registered)

- N-FIX-1 (already running as the repaired lead) keeps the 66 legs with
  `stood_down` blank and idles the 8 CE-on-gap-up legs. For each threshold:
  report |kept ∩ N-FIX-1 kept|, |kept \ N-FIX-1 kept| (legs this score
  keeps that N-FIX-1 also keeps is expected; the informative numbers are
  the disagreements), and how many of N-FIX-1's 8 idled legs each
  threshold keeps. Note the polarity: F_gap REWARDS gap alignment while
  N-FIX-1 idles one aligned cell — the constructions are mechanically
  different (single-cell rule vs 4-factor rank), and the overlap numbers
  must show it.
- Not a relabel of closed routes: T-N exit variants (exits — untouched
  here), EVE rounds (admission/assembly — untouched), C3-loosening
  (admission — untouched), DEC-S1 B-PE conditioning (= N-FIX-1, measured
  above, not reused as a factor: no factor in Step 1 references the B-PE
  leak or the CE-gap-up cell as such).

## Step 5 — November counterfactual (descriptive only)

v1's actual November = 1 leg: **Nov 3, CE 23600 (family C, weekly sleeve),
entry 09:50 @ ₹75.90, square-off 13:20 @ ₹126.00, +₹3,036.50** (from
`november_shadow_decs1_nifty_log.csv`; overnight gap +0.6034%, from the
books-fix results). Score this leg under the frozen Step-1 formula
(F_time: pre-11:00 = 1.00 · F_gap: CE on +0.6034% = aligned = 1.00 ·
F_prem: r = 75.90/213.025 · F_exp: Nov 3 2026 is a Tuesday but family C =
1.00) and state, per threshold, whether its score clears that threshold's
Jan–Oct cutoff (KEPT) or not (IDLED). One leg sets no rule in either
direction.

## PASS BAR (per threshold, pre-registered, do not move)

ALL of: WR ≥ 60% · ₹/trade-day ≥ ₹900 · total ≥ ₹61,830.15 (60% of the
full book's +₹103,050.25) · H1 > 0 AND H2 > 0 · ex-top-3 > 0 · placebo
percentile ≥ 0.95 · no new red month (subset's red months ⊆ {2026-03},
the baseline's only red month). Any leg failed = FAIL for that threshold,
with the failing leg(s) named.

## Deliverables

`phase2_tuning_nifty_2026-11-14.md` + `phase2_tuning_nifty_results.json`,
produced by `phase2_tuning_nifty_2026-11-14.py`. Whatever the outcome, the
verdict line must state honestly whether confidence-gating earned anything
beyond what trading less (random thinning of the same size) would have
given — that is what the placebo is for.
