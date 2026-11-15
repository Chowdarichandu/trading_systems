# Engine 1 — Afternoon Strength → Next-Day: pattern study (2026-11-11)

**Owner's observation:** when the market rises from the afternoon onwards and closes strong, the next session gaps up / continues. Instances he cited: Fri 2026-11-06 (both indices closed at their highs) → Mon 11-09 gap up; Mon 11-09 Bank ran into the close → Wed 11-11 gap up (Tue 11-10 was a holiday).

**RESEARCH ONLY — nothing is armed, no trading rules change, no cron touched.** Paper/research only, real money ₹0.

Data: `daily2leg/spot.json` — 5-min spot bars, both indices, full sessions. Windows: Jan–Oct 2026 (204 scored signal days per index) and Jan–Oct 2025 (206 per index, out-of-sample check). Indices always separate, never pooled.

---

## STEP 0 — His instances, verified against Upstox candles

**Fri 2026-11-06 — VERIFIED, exactly as he said.** Both indices closed AT their day highs:

| | Open | High | Low | Close | CS% | Afternoon run (13:00→close) | Post-13:00 up-bars |
|---|---|---|---|---|---|---|---|
| Bank Nifty | 57,812.90 | 59,086.00 | 57,320.80 | **59,086.00** | 100% | **+829.35 (+1.42%)** | 70% |
| Nifty | 24,538.20 | 25,030.35 | 24,388.05 | **25,030.35** | 100% | **+351.25 (+1.42%)** | 67% |

**Mon 2026-11-09 opens — gap up VERIFIED, but modest:** Bank opened 59,219.95 (**+133.95, +0.23%**), Nifty opened 25,076.40 (**+46.05, +0.18%**).

**Mon 2026-11-09 closes:** Bank O 59,219.95 · H 59,741.25 · L 58,877.85 · **C 59,741.25 — closed AT its high again**, CS 100%, afternoon run from the 13:00 level **+513.75 (+0.87%)**, 63% up-bars. (His "+835 into the close" is the run from the late-morning stop zone ~58,906; from 13:00 it is +513.75, and low→close is +863.40 — same move, different start points.) Nifty Mon: C 25,044.65 vs H 25,084.05 — strong but NOT at the high (CS 83.9%), afternoon run **+120.15 (+0.48%)**.

**Wed 2026-11-11 opens (Tue = holiday) — gap up VERIFIED, large:**
- Bank opened **60,524.70 → gap +783.45 pts (+1.31%)** vs Mon's close. (Open-to-open Mon→Wed is +1,304.75 — the source of his "~1,300 points"; the standard prev-close gap is +783.45.)
- Nifty opened **25,337.80 → gap +293.15 pts (+1.17%)** vs Mon's close. (His "~130" matches the ~1.2–1.3% zone, not points.)

So the two instances are real. The question the study answers: how often does this pattern actually precede a gap-up across 410 index-days — and is it stable enough to identify tomorrow?

---

## Method — measures and pre-registered buckets

Knowable at each close: **afternoon run** = close − 13:00 level (pts, % of the 13:00 level, % of day range); **post-13:00 up-bar share**; **closing strength CS%** = (C−L)/(H−L)×100; **distance of close from the day high**. Outcomes next trading day: gap (pts/%), open→close %, full-day change %, higher-high Y/N.

Buckets fixed before outcomes were computed:
- **B_CS80** CS ≥ 80 · **B_AFT30** afternoon run ≥ +0.30% · **B_TOPQ** afternoon run (as % of day range) in the window's top quartile (threshold in-sample by construction — flagged) · **B_COMBO** CS ≥ 80 AND afternoon run ≥ +0.30%
- Mirrors: **M_CS20** CS ≤ 20 · **M_AFT30** afternoon run ≤ −0.30%

Controls: mirror buckets must show the opposite (or nothing); Jan–May vs Jun–Oct halves must agree in sign; 2025 as out-of-sample.

**Base rates (all days):**

| Window | n | Mean gap % | Gap-up % | Next close up % | Mean next-day change % | Next-day higher high % |
|---|---|---|---|---|---|---|
| Bank 2026 | 204 | −0.052 | 45.6 | 48.0 | −0.036 | 47.5 |
| Bank 2025 | 206 | +0.030 | 54.4 | 53.9 | +0.067 | 51.5 |
| Nifty 2026 | 204 | −0.010 | 49.0 | 46.1 | −0.057 | 47.1 |
| Nifty 2025 | 206 | +0.037 | 56.8 | 49.0 | +0.042 | 49.5 |

---

## Results — Jan–Oct 2026 (primary window)

**Bank Nifty** (mean gap in pts in brackets):

| Bucket | n | Mean gap % | Gap-up % | Next close up % | Mean next-day % | Higher high % |
|---|---|---|---|---|---|---|
| B_CS80 | 52 | +0.139 (+77) | 50.0 | **40.4** | +0.022 | 71.2 |
| B_AFT30 | 42 | +0.134 (+73) | 50.0 | **42.9** | +0.006 | 66.7 |
| B_TOPQ | 52 | +0.150 (+84) | 48.1 | 48.1 | +0.063 | 69.2 |
| B_COMBO | 27 | **+0.388 (+217)** | 51.9 | 44.4 | +0.176 | **81.5** |
| M_CS20 | 48 | −0.197 | 33.3 | 52.1 | −0.112 | 20.8 |
| M_AFT30 | 45 | −0.202 | 40.0 | 55.6 | +0.017 | 33.3 |

**Nifty:**

| Bucket | n | Mean gap % | Gap-up % | Next close up % | Mean next-day % | Higher high % |
|---|---|---|---|---|---|---|
| B_CS80 | 53 | +0.091 (+23) | 47.2 | **34.0** | −0.053 | 69.8 |
| B_AFT30 | 38 | +0.243 (+58) | 55.3 | 55.3 | +0.186 | 68.4 |
| B_TOPQ | 52 | +0.127 (+31) | 46.2 | 44.2 | −0.011 | 61.5 |
| B_COMBO | 26 | **+0.399 (+97)** | 53.8 | 50.0 | +0.295 | **80.8** |
| M_CS20 | 43 | −0.184 | 37.2 | 48.8 | −0.124 | 16.3 |
| M_AFT30 | 42 | −0.188 | 45.2 | 57.1 | −0.033 | 26.2 |

First read: the gap effect is real on average in 2026 — mirrors are properly negative (it's not market drift), COMBO shows the biggest mean gaps, and next-day higher highs jump to ~81%. **But** the gap-up *rate* barely moves (51.9% / 53.8% vs bases 45.6% / 49.0%) — the signal is in gap *size*, not frequency — and the next day typically **fades the gap**: open→close averages −0.21% (Bank COMBO) and −0.10% (Nifty COMBO), with next-close-up rates at or below base. "Gap up" and "continues all day" are two different claims; 2026 supports the first weakly and the second not at all.

## Controls — where the pattern dies

**Halves (Jan–May vs Jun–Oct 2026), mean next-day gap %:**

| | Bank H1 | Bank H2 | Nifty H1 | Nifty H2 |
|---|---|---|---|---|
| B_CS80 | +0.367 | **−0.148** | +0.309 | **−0.119** |
| B_AFT30 | +0.299 | **−0.107** | +0.397 | +0.052 |
| B_COMBO | +0.752 | **−0.141** | +0.644 | +0.065 |

Bank: **every strength bucket flips sign** — the whole 2026 effect is a Jan–May phenomenon; in Jun–Oct the same signal preceded gap-*downs* on average (COMBO gap-up rate 27.3%). Nifty CS80 flips too. Nifty AFT30/COMBO keep the sign but collapse in H2 (COMBO gap-up rate 66.7% → 36.4%).

**2025 out-of-sample (mean gap % vs base):**

| | Bank 2025 | Nifty 2025 |
|---|---|---|
| Base | +0.030 | +0.037 |
| B_CS80 | +0.069 | +0.097 |
| B_AFT30 | **−0.038** | +0.037 (= base, no edge) |
| B_COMBO | **−0.061** | +0.089 |

Bank's afternoon-run effect **fails outright in 2025** (negative vs a positive base) — and inside 2025 it sat in H2 (−0.102 H1 → +0.096 H2), the opposite half from 2026. The effect migrates between halves from year to year: that is regime noise, not a pattern. Nifty's COMBO is the least-bad (positive both years, +0.399 / +0.089), but its H2-2026 gap-up rate is 36.4% and its 2025 sample is n=22.

**What survives every control — the higher-high regularity.** After COMBO days, the next day trades above the signal day's high **81.5% / 88.9% (Bank 2026 / 2025)** and **80.8% / 77.3% (Nifty 2026 / 2025)**, vs ~47–52% base; mirror days manage only 10–33%. Part of this is mechanical (a close at the high needs only a small uptick), but the mirror asymmetry shows it is not *only* mechanical. It is a levels fact, not a direction signal: the next day usually *visits* above today's high, then — per the open→close numbers — usually gives the gap back.

---

## Reconciliation with the 24-day Closing Strength study (Sep 30–Nov 4, Bank)

That study (plain CS regimes, 23 signal days, 5 Strict Bullish) leaned **reversal**: Strict Bullish averaged −0.12% next day, next day up only 1/5. This study:

- **Confirms it on its own slice.** The overlapping window inside this data (Sep 30–Oct 29 signals) has 4 Bank CS≥80 days: mean next-day change **−0.389%**, next close up **0/4**, mean gap −0.082%. Nifty's 6 such days: −0.195%, up 2/6. Same lean, same direction.
- **Confirms it in general for plain CS judged on the close.** Across all of Jan–Oct 2026, after CS≥80 days the next day closed up only **40.4% (Bank)** and **34.0% (Nifty)** — *below* base rates. Plain closing strength, on its own, is closer to a fade signal than a continuation signal.
- **Narrows it in two ways.** (1) *Measure:* the owner's pattern is afternoon-specific, and the afternoon-run buckets (AFT30/COMBO) — which the workbook never isolated — do show a positive **gap** tilt in 2026 that plain CS alone doesn't. (2) *Outcome split:* the workbook judged one next-day %; separated here, gap and close lean opposite ways in 2026 (gap tilts up, day fades). The 24-day study's window also sits inside the Jun–Oct regime where even the gap effect is absent for Bank — with n=5 it could not have seen the Jan–May effect, and with the full sample we can see its reversal lean is regime-local, not a law either.

Net: neither "strong close → continuation" nor "strong close → reversal" survives as a stable rule. What the full sample supports: **strong afternoon close → next day probably trades above today's high and gaps slightly positive on average in some regimes — and then usually fades.**

---

## Identification rule — VERDICT: NOT SUPPORTED

No end-of-day rule clears all three controls on either index:

- **Bank — killed by the halves and by 2025.** COMBO's +0.388% mean gap (2026) is +0.752% in Jan–May and **−0.141% in Jun–Oct**, and **−0.061% across 2025**. A flag that worked in one half of one year is not an identifier.
- **Nifty — killed by 2025 and by frequency.** AFT30 matches the 2025 base rate exactly (+0.037% vs base +0.037%, gap-up 56.7% vs 56.8% — no edge). COMBO is positive in both years but its gap-up rate collapses to 36.4% in H2 2026.

**The numbers that kill it, in one line:** Bank COMBO — gap-up 68.8% (H1 2026) → 27.3% (H2 2026) → 44.4% (2025). No honest hit rate exists for this flag; quoting the full-2026 51.9% would be averaging two opposite regimes.

**Daily-usable output (what to compute at each close, and what it would have said):**
At 15:30 compute, per index: (1) CS% = (C−L)/(H−L)×100; (2) afternoon run % = (C − 13:00 level)/13:00 level ×100; (3) whether price traded above today's high the next day (recorded next morning). FLAG = CS ≥ 80 AND afternoon run ≥ +0.30%.
- **Fri 2026-11-06: FLAG on both** (Bank CS 100, +1.42% · Nifty CS 100, +1.42%) → Mon gapped +0.23% / +0.18%. ✔
- **Mon 2026-11-09: FLAG on both** (Bank CS 100, +0.87% · Nifty CS 83.9, +0.48%) → Wed gapped +1.31% / +1.17%. ✔
- 2-for-2 — and still not evidence: n=2 anecdotes, drawn from the same Jun–Nov stretch where the 204-day backtest gives this flag **no dependable edge** (Bank H2: −0.141% mean gap). If the flag is used at all, use it only for the one statistic that survived every control — **expect the next day to trade above today's high (~4 times in 5)** — as a levels/expectation note, never as a buy signal.

---

## Files
- Scorer: `pattern_engine_afternoon_strength_2026-11-11.py`
- Full results (all buckets, halves, mirrors, sub-checks, Step-0 candles): `pattern_engine_afternoon_strength_2026-11-11_results.json`
- Signal-day table (410 index-days with measures + outcomes): `pattern_engine_afternoon_strength_2026-11-11_days.csv`
