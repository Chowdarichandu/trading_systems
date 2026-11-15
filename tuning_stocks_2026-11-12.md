# STOCKS TUNING PROGRAMME — 2026-11-12

Owner order 2026-11-12 16:23 IST: "I need tuning all 3." This is the
Stocks package (Bank and Nifty packages run separately). Two stocks
lines: (A) the frozen 25-stock **Stock Book** (November +₹8,391.28
through Nov 11, 26 trades 14W/12L; Nov 12 live layer +₹265.06) —
frozen for November, all tuning is December candidates; (B) **Stock
Engine**, the wide live system (1,081 NSE names, 4 live components;
27-day simulation +₹8,724.39, ex-top-3 −₹3,256.65; first live day
Nov 12 +₹265.06).

Standing controls gate applied in full to every variant, same run:
timing/causality audits, placebos where applicable, halves/months,
ex-top-3, independent re-sum. Bars unmoved. Basis: provisional per
100 shares (₹40/trade) primary; ₹25,000 fixed-capital lens (fc_net)
secondary. Paper only, real money ₹0.

---

## T-S1 — S1 session windows × T2 slot reservation (Stock Engine)

**VERDICT: GATE FAIL — the 9th and last configuration of the causal
chain family. Nothing wired; the live 4-component engine stands.**

The one combination not covered by the 8 failed configurations
(causal-3 raw gate, T1–T5, S1, S2): S1's session windows (F4-C →
[10:30–12:00], INV-LONG-C → [09:15–10:30], INV-ABOVE-C excluded)
applied as a rep-level eligibility filter INSIDE T2's slot
reservation (chain ≤ 2 of 6 daily slots, chain decided at a single
13:30 decision point, chain floor 90, price cap ₹5,000). Implemented
as the tuning chassis (`derive_day_tuned`) verbatim plus the window
step; rep semantics preserved (earliest row per stock-comp is the
rep; an out-of-window rep sits out, later rows are not promoted).

### Harness validations — all passed before T-S1 was scored
| Check | Required | Got |
|---|---|---|
| (a) Live-4 baseline via SIM.derive_day | 39 tr / +₹8,724.39 / ex3 −₹3,256.65 | exact |
| (b) TS1 chassis, windows OFF, stream, no cap = failed-gate combined | 162 tr / −₹4,267.84 / ex3 −₹18,321.31 | exact |
| (c) TS1 chassis, windows OFF, 13:30 + cap 2 = T2 | 93 tr / +₹3,023.65 / ex3 −₹8,957.39 (Oct ex3 −₹14,228.64, Nov ex3 −₹1,879.38) | exact |
| (d) TS1 chassis, windows ON, stream, no cap = S1 | 131 tr / +₹11,673.55 / ex3 −₹1,762.49 | exact |

### Result (162-trade combined frame, Oct 1 – Nov 11)
| | Trades | Net | Ex-top-3 | Oct ex3 | Nov ex3 | ₹25k lens |
|---|---|---|---|---|---|---|
| Live-4 baseline | 39 | +₹8,724.39 | −₹3,256.65 | −₹6,897.97 | −₹1,352.29 | — |
| **T-S1** | **81** | **+₹7,381.08** | **−₹4,599.96** | **−₹10,786.67** | **−₹914.04** | +₹540.63 |
| Placebo-TS1 (same cfg, placebo windows) | 40 | +₹8,332.37 | −₹3,648.67 | −₹7,289.99 | −₹1,352.29 | +₹358.87 |
| S1 (windows, stream) — closed | 131 | +₹11,673.55 | −₹1,762.49 | −₹7,734.08 | −₹1,490.21 | — |
| T2 (reservation, no windows) — closed | 93 | +₹3,023.65 | −₹8,957.39 | −₹14,228.64 | −₹1,879.38 | — |

T-S1 detail: WR 39.5%, expectancy +₹91.12/trade. Chain attribution:
F4-C 27 picks +₹2,400.15 · INV-LONG-C 15 picks −₹3,743.46 ·
INV-ABOVE-C 0 (window-excluded). Reaction family + N4-V3: 39 picks
+₹8,724.39 — the baseline set, untouched. Month nets: October
+₹178.45 (headline carried entirely by its top-3 stocks), November
+₹7,202.63.

### Gate legs (pre-registered, unmoved)
- Combined ex-top-3 > baseline (−₹3,256.65): **FAIL** (−₹4,599.96)
- Headline improvement (> +₹8,724.39): **FAIL** (+₹7,381.08)
- October not worse (ex3 ≥ −₹6,897.97): **FAIL** (−₹10,786.67)
- November not worse (ex3 ≥ −₹1,352.29): **PASS** (−₹914.04 — the
  best November ex-top-3 of any chain-including configuration)
- Beats placebo on ex-top-3: **FAIL** (placebo −₹3,648.67; the
  placebo takes almost no chain picks — F4-C 1, INV 0 — i.e. a
  near-no-chain book beat the combination on both headline and ex3)
- Truncation spot-proof (2026-10-16, 2026-11-11 × slices
  10:30/12:00/13:30/15:00): **PASS 8/8**
- Independent re-sum of the written picks CSVs: **exact** (TS1 and
  placebo)

### Reading
The windows genuinely improve T2 (T-S1 beats T2 on every leg), but
the reservation mechanism subtracts more than the windows add:
T-S1 is dominated by S1 alone on headline and ex-top-3, sits below
the live-4 baseline, and loses to its own placebo. With this, every
causal selection form of the chain sleeves has been tested —
stream, ranked, capped, reserved, windowed, deferred, and
windowed+reserved — and none earns slots against the live 4
components. **The causal-chain family is closed.** T-S1 is never to
be retested identically.

Evidence: `tuning_stocks_ts1_2026-11-12.py`,
`tuning_stocks_2026-11-12_ts1_summary.json`,
`tuning_stocks_2026-11-12_picks_TS1.csv` / `_picks_PTS1.csv`.

---

## T-S2 — N4-V3 threshold reconciliation: 0.8% vs 1.0%

**VERDICT: the evidence supports 1.0%. The discrepancy is settled —
no threshold change for December.**

First, the premise, corrected on the record: the frozen November
book, its frozen spec (§4 of `stocks_sarvaritu_forward_spec.md`)
and the live producer ALL use |move by 09:30| ≥ 1.0% (09:25-bar
close vs prior close). The 0.8% figure exists only as the adopted
Variant C December axis (engine log, 2026-11-03: NATIONALUM −0.869%
"crosses the 0.8% threshold used elsewhere (adopted Variant C
axis)"). So the live question was whether the book's N4-V3 should
move to 0.8% for December. Scored from the book's own machinery
(`stocks_sarvaritu_logger.load_machinery` → the v2_build `n4_raw`
construction with the threshold parameterised; `n4_book` filters +
the v2 law's EXCL_V2 deletions exactly as `build_book` applies
them). The book has no cross-component slot competition, so the
component delta below is the book delta.

### Validation anchors — all passed before any comparison was read
At 1.0% the runs reproduce, trade-for-trade (date, stock, dir,
entry_time, net): the post-C24 frozen dump's N4-V3 rows for 2026
(35/35), the 2025 dump's Jan–Oct rows (43/43), and the November
paper log's N4-V3 rows (5/5). Superset property asserted: lowering
the threshold only ADDS the [0.8%, 1.0%) band — every 1.0% trade
reappears at 0.8% with an identical net.

### Scores (per 100 shares, ₹40/trade)
| Window | Threshold | Trades | Net | WR | Expectancy | Ex-top-3 |
|---|---|---|---|---|---|---|
| Jan–Oct 2026 | 1.0% | 35 | +₹25,271.54 | 65.7% | +₹722.04 | +₹6,638.41 |
| Jan–Oct 2026 | 0.8% | 42 | +₹25,515.62 | 61.9% | +₹607.51 | +₹8,364.73 |
| Jan–Oct 2025 | 1.0% | 43 | +₹4,671.64 | 32.6% | +₹108.64 | −₹8,414.85 |
| Jan–Oct 2025 | 0.8% | 45 | +₹7,091.69 | 35.6% | +₹157.59 | −₹5,994.80 |
| Nov 2–11 fwd | 1.0% | 5 | +₹1,244.00 | 60.0% | +₹248.80 | −₹405.27 |
| Nov 2–11 fwd | 0.8% | 6 | +₹1,689.48 | 66.7% | +₹281.58 | −₹164.07 |

### The marginal [0.8%, 1.0%) band — the decisive evidence
- **2026: 7 trades, +₹244.08** — and that is one trade carrying the
  rest: OBEROIRLTY 2026-05-11 SHORT (−0.891%) +₹2,483.45; the other
  six net **−₹2,239.37**. The band dilutes 2026 expectancy from
  +₹722.04 to +₹607.51 and flips October 2026 green→red at
  component level (+₹1,089.77 → −₹1,773.03; both October band
  trades lost: OBEROIRLTY −₹1,380.56, HINDUNILVR −₹1,482.24).
- **2025: 2 trades, +₹2,420.05** (GODREJCP SHORT +₹1,831.25, OIL
  SHORT +₹588.80) — both winners, but two trades.
- **November: 1 trade, +₹445.48** — NATIONALUM SHORT on Nov 3
  (−0.869%): the near-miss the Nov 3 log recorded but deliberately
  did not score. Scored now, from the book's machinery: it won.
  One trade.
- All windows combined: 10 band trades, +₹3,109.61, of which the
  single largest is +₹2,483.45 — ex-top-1 the band earns
  +₹626.16 over 9 trades (≈ +₹70/trade).

### Reading
2025 and November lean toward 0.8% on a combined 3 band trades;
the primary window (2026, 7 band trades) says the band is
break-even noise that dilutes a strong component (expectancy
−16%) and breaks a month. That does not overturn 1.0%. **December
keeps the 1.0% trigger; the 0.8% Variant-C axis is not vindicated
at component level and is closed as a threshold question.**
Nov 12 is threshold-neutral: the day's only N4 signal, HINDCOPPER
LONG at +3.88% by 09:30, qualifies identically under both
thresholds (book −₹404.32 either way); the fwd-root candles for
Nov 12 land with tonight's logger run and cannot change this
comparison.

Evidence: `tuning_stocks_ts2_2026-11-12.py`,
`tuning_stocks_2026-11-12_ts2_summary.json`,
`tuning_stocks_2026-11-12_ts2_trades_<2026|2025|nov>_<thr100|thr080>.csv`.

---

## T-S3 — Stock Book December evidence pack (no new variant)

Forward records of the two TUNED SHADOWs, compiled from
`november_rsi_stocks_log.md` and `segment_floor_tracker.md`
(scored through Nov 11; Nov 12 items are marked pending — both
shadows are scored by the evening engine run).

### TUNED SHADOW v1 — N4-V3 one-sided cap (EVE-19 lineage; live from Tue 2026-11-03)
Rule: skip N4-V3 LONG entries whose signed move by 09:30 is
≥ +3.0%; SHORTs uncapped. Gate record (FLOOR-2, in-sample):
combined book +₹2,59,860.26 → +₹2,62,591.33, all nine legs pass;
the LONG ≥ +3% bucket is negative in both years (2025 −₹940.81 /
10 tr; 2026 −₹1,790.26 / 4 tr).

November forward record (identical event days from Nov 3):
| Day | Event | Shadow outcome |
|---|---|---|
| Nov 3 | no N4 signal (both names below 1.0% trigger) | ₹0 |
| Nov 4 | no N4 signal | ₹0 |
| Nov 5 | NHPC LONG +3.937% **SKIPPED-CAP** | saved −₹105.03 book / −₹80.65 scorecard |
| Nov 5 | PFC LONG +1.039% taken | +₹448.77 book / −₹202.93 scorecard |
| Nov 6 | ASTRAL SHORT −10.000% taken (uncapped) | +₹1,834.00 book / +₹1,521.50 scorecard |
| Nov 9 | TATASTEEL SHORT taken (book basis); HINDALCO SHORT taken (scorecard basis) | +₹241.20 book / −₹508.20 scorecard |
| Nov 10 | holiday | — |
| Nov 11 | KALYANKJIL LONG +8.658% **SKIPPED-CAP** | forgone +₹959.30 book / +₹792.75 scorecard |
| Nov 12 | HINDUNILVR/HINDCOPPER day — HINDCOPPER LONG +3.88% by 09:30 is a would-be SKIPPED-CAP (book lost −₹404.32) | **pending tonight's scoring** |

**MTD: book basis +₹2,523.97 · scorecard basis +₹810.37 — 3 taken,
2 skipped on each basis.** Pre-registered judgement (spec
`november_shadow_stocks_onesided_cap_2026-11-02.md`), status
through Nov 11:
- Adoption leg 1 (shadow net ≥ primary, scorecard): **FAILS** —
  shadow +₹810.37 vs primary +₹1,522.47; the shadow TRAILS by
  ₹712.10.
- Adoption leg 2 (shadow ex-top-3 ≥ 0): not separately published
  in the log; the taken set is 3 trades on the scorecard basis.
- Adoption leg 3 (SKIPPED-CAP set's realised primary net ≤ 0):
  **FAILS** — the skipped set nets **+₹712.10 scorecard /
  +₹854.27 book** (NHPC −₹80.65 saved, KALYANKJIL +₹792.75
  forgone, scorecard basis).
- Kill leg 1 (shadow net < primary at month end): currently met
  on the running record; judged at month end, not before.
- Kill leg 2 (skipped set > +₹1,000): not met (+₹712.10).
- Evidence floor (≥ 3 taken): met exactly (3).
- Counterweight on record: STOCKS-EVE-21 (2026-11-11) tested
  exempting ≥ +6% moves from the cap and GATE-FAILED — the
  historical ≥ +6% LONG bucket nets −₹351.14 scorecard /
  −₹722.95 book (2 trades), so history still backs the cap that
  November is currently charging for. Both facts go to December
  judging as they stand.

### TUNED SHADOW v2 — EVE-20 (live from Wed 2026-11-11)
Rule: drop INV-ABOVE entries when the stock's prior trading day
moved ≥ +4.0% close-to-close. Gate record (2026-11-10, GATE PASS,
all legs): drops 13 trades (2025: 11 tr −₹1,990.17; 2026: 2 tr
−₹203.35 — incl. GLENMARK 2025-07-14 −₹1,134.05 after a +13.35%
day); component after filter 2025 +₹7,199.88 / 2026 +₹3,552.56;
book ₹29,469.41 / ₹2,11,791.45; chronological placebos beaten in
both years; the mirror filter (drop after ≤ −4.0% days) worsens
both years; book ex-top-3 improves in both years; no month or
half flips. Gate counterfactual (pre-promotion, NOT forward
record): on Nov 9, GLENMARK's prior-day move was +4.36%, so v2
would have dropped both Nov-9 INV-ABOVE rounds and saved the full
−₹2,734.40.

November forward record: **₹0 · 0 trades.** Nov 11 (first live
day): no INV-ABOVE trades — nothing to drop or take. Nov 12:
INV-ABOVE is EOD-determined; **pending tonight's scoring.** v2
has no forward evidence yet; December is its first real evidence
window. It passed on uniform non-degradation, not size
(+₹2,193.52 over two years on 13 dropped trades) — a rare-
configuration rule, judged on whether December produces the
configuration at all.

---

## December note — Stocks

1. **Stock Book (frozen 25):** the November primary is untouched
   and green (+₹8,391.28 through Nov 11; +₹265.06 live layer on
   Nov 12, EOD pending). Nothing in this programme changes it.
2. **N4 threshold: settled at 1.0%** (T-S2). The 0.8% question,
   open since Nov 3, is closed; December's N4-V3 keeps the frozen
   trigger.
3. **TUNED SHADOW v1** goes to December judging with its November
   forward record running AGAINST adoption (trails the primary by
   ₹712.10 on the pre-registered scorecard comparison; skipped
   set positive) and its historical gate record FOR it (EVE-21
   confirmed the cap's bucket logic). If tonight's scoring
   confirms the HINDCOPPER would-be skip, the skip saved ₹404.32
   on the book basis but the skipped set stays positive on both
   bases — the adoption legs still fail; the kill legs are judged
   at month end per the pre-registration.
4. **TUNED SHADOW v2** carries a clean gate pass and zero forward
   evidence; it continues into December as the segment's live
   shadow, and December data is its verdict window.
5. **Stock Engine:** stays on the 4 live components (P2F family +
   N4-V3). T-S1's failure closes the causal-chain family in all
   nine configurations — no chain variant is carried into
   December. The engine is judged on its November forward record
   from Nov 12 (first live day +₹265.06). Operational note: the
   engine job's November-only month guard needs its December
   amendment before Dec 1.
6. Nothing in this programme passed that requires wiring. The
   two-of-three mandate is unaffected on the Stocks side: the
   Stock Book remains the green segment.

*Scripts: `tuning_stocks_ts1_2026-11-12.py`,
`tuning_stocks_ts2_2026-11-12.py`. All figures paper, per 100
shares unless labelled; real money ₹0.*
