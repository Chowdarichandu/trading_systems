# BREAK → TREND probability study — Bank Nifty & Nifty (2026-11-08)

**Descriptive probabilities on index spot only. Every "points" figure below is SPOT POINTS, NOT OPTION MONEY.** No premium scoring, no system, nothing armed. Definitions were pre-registered before scoring and were not altered after seeing results (opening range = 09:15–09:30 bars; break = first 5-min CLOSE beyond the range at/after 09:30; "failure close" = first later close back inside the range; extension-before-failure excludes the failure bar's own high/low).

**Data:** `daily2leg/spot.json`, 5-min spot. Jan–Oct 2026: 205 days per index, all complete. Jan–Oct 2025: 208 days per index, one excluded (2025-10-21, only 12 bars — Diwali session), 207 used. Windows always reported separately, never pooled.

---

## Headline probabilities — UP-breaks (first close above the opening-range high)

| Measure | Bank 2026 (n=129) | Bank 2025 (n=130) | Nifty 2026 (n=129) | Nifty 2025 (n=132) |
|---|---|---|---|---|
| Days with an up-break | 62.9% | 62.8% | 62.9% | 63.8% |
| Failure close within 30 min | 60.5% | 54.6% | 62.0% | 56.1% |
| Failure close within 60 min | 69.0% | 68.5% | 72.1% | 65.2% |
| P(run ≥ small* before failure) | 25.6% | 22.3% | 27.1% | 31.1% |
| P(run ≥ mid* before failure) | 16.3% | 8.5% | 15.5% | 15.2% |
| P(run ≥ large* before failure) | 7.0% | 3.8% | 7.0% | 4.5% |
| P(full-day run ≥ small*) | 53.5% | 47.7% | 59.7% | 56.8% |
| P(full-day run ≥ mid*) | 34.9% | 20.8% | 31.0% | 31.1% |
| P(full-day run ≥ large*) | 16.3% | 6.2% | 16.3% | 11.4% |
| **P(clean trend)** (no failure close + full-day run ≥ mid) | **14.7%** | **8.5%** | **14.0%** | **10.6%** |
| Median run before failure | 55.2 pts | 55.4 pts | 20.8 pts | 23.1 pts |
| Median full-day run | 165.8 pts | 139.9 pts | 61.8 pts | 60.9 pts |
| Median minutes to reach small* (of those that do, pre-failure) | 30 (n=33) | 35 (n=29) | 20 (n=35) | 25 (n=41) |

*Bank thresholds: small +150 / mid +300 / large +500. Nifty: +50 / +100 / +175, all beyond the break price.

**The one-sentence read:** a morning-range break is common (about 63% of days) but usually dies fast — roughly 2 in 3 breaks close back inside the range within the hour, and only about 1 in 7 (2026) to 1 in 10 (2025) becomes a clean, never-failing trend. Yet the full day's run reaches the small threshold about half the time — i.e., **much of the day's real move typically happens only after a first failure close**. Friday 6 Nov was that majority shape, not an exception.

Base rates (both directions): down-breaks occur on 63–69% of days; days with neither break: Bank 3.9%/3.4%, Nifty 0.0%/2.4%; days where the opposite break also occurs later: ~30–32%.

## The HOLD-60 contrast — the conditioning that actually changes the odds

Subset: breaks still above/below the range 60 minutes after the break bar (no failure close in the first hour). This is conditioning on survival — it can only be known at +60 min, not at the break.

| Up-breaks | Bank 2026 | Bank 2025 | Nifty 2026 | Nifty 2025 |
|---|---|---|---|---|
| HOLD-60 subset size | 40 of 129 (31%) | 41 of 130 (32%) | 36 of 129 (28%) | 46 of 132 (35%) |
| P(clean trend) — all breaks | 14.7% | 8.5% | 14.0% | 10.6% |
| **P(clean trend \| HOLD-60)** | **47.5%** | **26.8%** | **50.0%** | **30.4%** |
| P(run ≥ small before failure \| HOLD-60) | 75.0% | 65.9% | 77.8% | 80.4% |
| P(run ≥ mid before failure \| HOLD-60) | 52.5% | 26.8% | 52.8% | 43.5% |
| P(run ≥ large before failure \| HOLD-60) | 22.5% | 12.2% | 25.0% | 13.0% |

Surviving the first hour roughly **triples** the clean-trend probability in every index/window. Note Friday was *not* a HOLD-60 day (see Friday check) — its trend came from a second act after the first break had already failed.

## Break-time buckets (up-breaks)

| Bucket | n (Bank 26/25, Nifty 26/25) | P(clean) Bank 26/25 · Nifty 26/25 | Failure ≤60m | Note |
|---|---|---|---|---|
| ≤10:00 | 64/72 · 69/80 | 14.1%/11.1% · 15.9%/12.5% | 68–75% | The typical break; dies most often |
| 10:05–12:00 | 34/37 · 30/34 | 11.8%/5.4% · 10.0%/8.8% | 59–83% | **Worst bucket** — hold-to-close capture means negative in 3 of 4 index-windows (see below) |
| ≥12:05 | 31/21 · 30/18† | 19.4%/4.8% · 13.3%/5.6% | 57–67% | Best 2026 clean rate (Bank 19.4%), but 2025 does not confirm it; †Nifty 2025 n=18 is thin (<20) |

## Capture arithmetic — entry at break price (SPOT POINTS, NOT OPTION MONEY)

| Up-breaks | Bank 2026 | Bank 2025 | Nifty 2026 | Nifty 2025 |
|---|---|---|---|---|
| (a) Hold to day close: mean / median / win% | +1.3 / +3.9 / 50.4% | −6.6 / −6.3 / 48.5% | −2.2 / +9.2 / 52.7% | +2.3 / +7.2 / 53.0% |
| (b) Exit at failure close: mean / median / win% | +22.8 / −36.2 / 21.7% | −0.7 / −44.0 / 18.5% | +1.3 / −14.8 / 18.6% | −2.5 / −14.5 / 20.5% |
| (a) within HOLD-60 only: mean | +159.6 | +126.7 | +34.9 | +29.8 |
| (b) within HOLD-60 only: mean | +202.0 | +127.9 | +58.2 | +39.3 |
| (a) midday breaks only (10:05–12:00): mean | −79.7 | −46.1 | −37.0 | −12.9 |

Reading: **buying the raw break and holding is a coin toss worth ~zero spot points on average** — the average is carried entirely by the minority of trend days. Exit-at-failure-close wins only ~1 time in 5, but its positive mean (Bank 2026) comes from the no-failure days that ride to the close; the typical (median) failure-exit trade loses ~15–44 points. Within HOLD-60, both exits are strongly positive — the money is in the *survived* breaks, not the breaks themselves.

## Down-breaks (mirror, brief)

Same shape: P(clean trend) Bank 12.9%/10.5%, Nifty 12.0%/13.7%; failure within 60 min 61–69%; P(clean | HOLD-60) 39.5%/34.1% (Bank), 38.6%/35.3% (Nifty). Hold-to-close means: Bank −10.0/−18.0 pts, Nifty −3.5/+3.9 pts — no free lunch on the short side either. Full tables in `break_trend_days.csv` / script output.

## Friday check (machinery sanity)

2026-11-06 Bank Nifty, from the intraday spot file: ORH **57,812.90** ✓, ORL 57,320.80, first close above on the **09:45 bar at 57,821.25** ✓, first failure close at **+50 min** (10:35 bar), extension before failure **+170.50** (small threshold only), full-day extension **+1,264.75**, day close 59,086 ✓. **Classification under the pre-registered definitions: NOT a clean trend, NOT HOLD-60, bucket ≤10:00** — the break failed late-morning and the trend was a second act from ~12:10. Hold-to-close capture on Friday would have been +1,264.75 spot points; exit-at-failure-close would have been **−13.00** points.

## Sanity

- Reconciliation: break-day counts sum exactly to day counts in all four index-windows (e.g. Bank 2026: 129 up + 132 down − 64 both + 8 neither = 205 ✓; CSV rows match day counts per direction exactly, 1,058 rows).
- Three random break days recomputed with an independent loop — all matched (NIFTY 2026-06-12 down, NIFTY 2025-05-30 down, BANKNIFTY 2025-08-07 up; raw bars printed in the script run).

## What capturing this would mechanically require (from the numbers only)

1. **The break alone is not the signal.** Unconditioned, it fails within the hour ~2 times in 3, and holding it averages ~0 spot points. Any capture mechanism keyed on the break itself inherits those odds.
2. **Survival is the ingredient the numbers support.** Conditioning on "still outside the range after 60 minutes" lifts clean-trend probability ~3× (to 27–50%) and turns both capture rules strongly positive. Mechanically that means the entry decision that matters happens *after* the chop window, not at the break — or the position must be sized/structured to survive a ~65–72% chance of a failure close in the first hour.
3. **Big days usually need a second act.** The full-day run reaches the small threshold ~48–60% of the time, but the pre-failure run only ~22–31% — Friday (+170 before failure, +1,265 by close) is the typical big-day shape. A mechanism that exits permanently at the first failure close structurally forfeits most of the day's move; capture requires either holding through the failure or a re-entry after failure.
4. **Midday first breaks (10:05–12:00) are the worst population** by capture mean in both indices — if anything is filtered, the numbers point there first. Late breaks looked best in 2026 but 2025 does not confirm, and counts are thin.
5. **The failure-close exit keeps the tail, drops the middle.** Its positive Bank-2026 mean is entirely the no-failure days; its median trade loses. It is a trend-harvesting rule, not a consistency rule — win rate ~17–22%.

Files: `break_trend_probability_2026-11-08.py` · `break_trend_days.csv` (one row per break, all measured fields).
