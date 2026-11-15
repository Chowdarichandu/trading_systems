# Movement capacity — Bank Nifty & Nifty, Jan–Oct 2026 (205 days, 5-min spot)

Base rates over ALL anchors (no signal selection): how much room the
market itself offers, to size the hunt (Chandu's spec: initial target
10–20 premium points, then trail). Script: move_analysis_2026-11-03.py
on daily2leg/spot.json filtered to 2026 (205 days, >=74 bars/day).
First pass accidentally included 2025 (454 days) — caught and re-run;
only the 2026 figures below stand.

## Bank Nifty (spot points)
- Full-day range: mean 552 · median 491 · p75 705 · p90 956
- |move| mean/median: 5m 30.1/20.5 · 15m 57.7/41.5 · 30m 82.0/57.8 · 60m 117.2/83.1
- 30m |move| by start: 09:15–10:30 → 97.1 · 10:30–13:00 → 75.2 · 13:00–15:00 → 81.8
- Best one-way run, next 30m: mean 102 · median 79 · p75 130; >=40 pts in 81% of windows, >=60 in 64%, >=100 in 38%
- Best one-way run, next 60m: mean 151 · median 118; >=100 pts in 59%

## Nifty (spot points)
- Full-day range: mean 198 · median 167 · p75 265 · p90 339
- |move| mean/median: 5m 10.7/7.2 · 15m 20.6/14.8 · 30m 29.3/20.8 · 60m 41.7/30.0
- 30m |move| by start: 09:15–10:30 → 35.7 · 10:30–13:00 → 26.5 · 13:00–15:00 → 29.4
- Best one-way run, next 30m: mean 36 · median 28 · p75 45; >=40 pts in 31% of windows
- Best one-way run, next 60m: mean 53 · median 41; >=40 pts in 52%

## Premium translation (ATM delta ~0.5, approximation)
+10/+15/+20 premium points need roughly a 20/30/40-pt spot move in
your direction (a little more late-day with theta).
- Bank: the 20-pt premium target's spot requirement (40 pts) is met by
  a one-way run in 81% of 30-min windows; median 30m run (79 spot)
  leaves ~35-40 premium pts of excursion for the trail.
- Nifty: 10 premium pts (20 spot) is a 30-min-scale target (67%);
  20 premium pts (40 spot) is a 60-min-scale target (52%) — Nifty
  needs the longer hold / wider trail.

Caveat: runs are best-direction (hindsight side) over all anchors —
they prove the ROOM exists, not that an entry captures it. Picking the
side and the moment is the strategy's job, still to be gated.
