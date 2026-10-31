# Index OPTIONS — New Setup Definitions for Frequency (NS1–NS6) — Report 2026-10-30

Paper only, no orders, no stocks. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
This report does NOT edit `index_options_progressive_tuning.md` (parent merges).

## Verdict up front — plainly
**NO family passes ALL legs together (net > 0 AND full-target >= 50% AND frequency >= 5/week = 1/day)
on BOTH the Jan–Oct 2026 window AND the October 2026 premium window, on either index.**
There is therefore **no final in-sample candidate and nothing is adopted** on this run.
November 2026 paper from 2026-11-02 remains validation, and no family earns adoption from
in-sample numbers alone.

**Closest version: NS1 (second convicted signal per day).** It is the only family that comes near
the frequency leg — Jan–Oct 4.95/week (Nifty) and 4.80/week (Bank) — with net > 0 on both indices
in Jan–Oct spot AND in October premiums. It still fails, and fails clearly, because its
full-target rate fails on every window and every index: Jan–Oct 35.8% (Nifty) / 31.8% (Bank),
October spot 38.5% / 42.9%, October premium 23.1% / 42.9% — all below 50% — and its October
frequency (3.61 / 3.89 per week) is also below 5/week. Frequency was nearly fixed; hit quality
was not. NS1 is the only family whose November paper (frozen as-is) would be informative.
Every other family fails on net or frequency as well as on hits, and is discarded below with
its reason. No family was re-tuned on its window to force a pass.

## Frozen definitions (written BEFORE any NS number was computed)
- [NS1 second signal](sandbox://workspace/trading/index_options_newsetup_ns1_second_frozen.md)
- [NS2 afternoon rescan](sandbox://workspace/trading/index_options_newsetup_ns2_afternoon_rescan_frozen.md)
- [NS3 gap-class](sandbox://workspace/trading/index_options_newsetup_ns3_gapclass_frozen.md)
- [NS4 OR re-break](sandbox://workspace/trading/index_options_newsetup_ns4_or_rebreak_frozen.md)
- [NS5 cross-legs (5a + 5b, scored separately)](sandbox://workspace/trading/index_options_newsetup_ns5_crossleg_frozen.md)
- [NS6 session-range breakout](sandbox://workspace/trading/index_options_newsetup_ns6_session_range_frozen.md)

Common frozen rules (all families): OR = 09:15–09:25 bars; PDH/PDC/PDL = previous day; bias
bearish < 35% / neutral 35–79% / bullish >= 80%; spot entry = next 5-min open, stop = signal-bar
low/high, target = 2x risk, stop before target per bar, square-off 15:10; room_ratio >= 1.5
to the next PD level in direction, never below 1.5x; full-target = target exit only (square-off
greens, partials and break-evens never count); no direct reclaim CE re-introduced (NS4/NS5b CE
legs require a full inside close + fresh break + confirmer break, or a close above PDH +
confirmer break — see the frozen files); no forced trades on no-setup days.
Implementation notes (readings fixed in the scorer, not re-tuned): for NS2/NS4/NS6 the trade
candidate is the first bar satisfying trigger AND cross-confirmation together; a bias or room
failure on that candidate ends the day (no later candidate is sought). For NS5a the confirmer's
FIRST break (either direction, <= 11:30) fixes the direction; only a rescan at/after that bar
counts. NS2's track total includes its morning leg; NS6's track counts its afternoon legs
only (morning legs are excluded by construction — the two tracks are not counted the same way).

## Scoring method and verification
- Spot: cached 5-min spot + daily, Jan–Oct 2026 (203 trading days per index = 40.6 weeks) and
  October 2026 (18 days), scored by [newsetups_score.py](sandbox://workspace/trading/newsetups_score.py).
  Spot provisional net = direction points x 100 shares - Rs 40/leg. This is NOT an options-lot
  profit and NOT a futures profit.
- Verification (exact, before trusting any NS number): the scorer reproduces the October bases
  exactly — Skill S1 Nifty 8 trades / +Rs 8,420 / 2 targets, Bank 9 / +Rs 8,675 / 3 targets;
  V4 uncapped Nifty 4 / +Rs 2,725 / 2 targets, Bank 5 / +Rs 67,690 / 4 targets.
- Premiums (October only): entry = open of the first 5-min option candle after the signal,
  stop = entry - 50, target = entry + 90 option points, square-off 15:10, cost Rs 220/trade,
  1 lot (Nifty 65, Bank 30), ATM nearest 100 to entry spot, expiry monthly 2026-10-27 for
  1–27 Oct and weekly 2026-11-03 for 28 Oct. The Muse connector was NOT used (401, as briefed).
  20 of 38 October NS contracts were already cached; the other 18 were fetched successfully
  via the existing browser-fetch script-token route ([newsetup_premium_fetch.py](sandbox://workspace/trading/newsetup_premium_fetch.py),
  profile 200, all 18 returned 200 with 77 candles each), so **all 84 October NS legs are
  COMPUTED on premiums — zero NOT_COMPUTED**. Premium scorer:
  [newsetup_premium_score.py](sandbox://workspace/trading/newsetup_premium_score.py).
  Premium validation: NS1/NS2 morning legs reproduce the v2 Skill S1 premium file to the rupee
  (Nifty +Rs 3,394.50 / 2 targets; Bank -Rs 2,880 / 3 targets).
- The -50/+90 premium rule is the V5-v2 options overlay, not Skill's/(lA)'s native spot rule
  (stop = signal high/low, target = 2x spot risk). Spot and premium nets are reported side by
  side and never converted into each other.

## Before / after — Jan–Oct 2026 spot (203 days, 40.6 weeks)
Frequency = trades / 203 x 5. Green = legs with net > 0. FT = full-target legs.

| Track | Nifty: trades / FT / green / net prov. / wk | Bank: trades / FT / green / net prov. / wk |
|---|---|---|
| BEFORE Skill S1 | 125 / 48 (38.4%) / 49 / +Rs 47,265 / 3.08 | 130 / 36 (27.7%) / 39 / -Rs 157,750 / 3.20 |
| BEFORE V4 uncapped | 46 / 21 (45.7%) / 21 / +Rs 33,130 / 1.13 | 46 / 14 (30.4%) / 14 / -Rs 28,635 / 1.13 |
| NS1 (base + second) | 201 / 72 (35.8%) / 74 / +Rs 56,760 / 4.95 | 195 / 62 (31.8%) / 66 / +Rs 14,130 / 4.80 |
| NS1 second legs only | 76 / 24 (31.6%) / 25 / +Rs 9,495 / 1.87 | 65 / 26 (40.0%) / 27 / +Rs 171,880 / 1.60 |
| NS2 (morning + aft.) | 152 / 59 (38.8%) / 60 / +Rs 63,400 / 3.74 | 146 / 44 (30.1%) / 47 / -Rs 120,970 / 3.60 |
| NS2 afternoon legs only | 27 / 11 (40.7%) / 11 / +Rs 16,135 / 0.67 | 16 / 8 (50.0%) / 8 / +Rs 36,780 / 0.39 |
| NS3 gap-class | 73 / 21 (28.8%) / 21 / -Rs 49,380 / 1.80 | 58 / 22 (37.9%) / 23 / +Rs 82,295 / 1.43 |
| NS4 OR re-break | 60 / 17 (28.3%) / 17 / -Rs 19,440 / 1.48 | 60 / 25 (41.7%) / 25 / +Rs 98,750 / 1.48 |
| NS5a Skill rescan | 95 / 39 (41.1%) / 39 / +Rs 34,085 / 2.34 | 90 / 27 (30.0%) / 29 / -Rs 52,235 / 2.22 |
| NS5b CE mirror | 29 / 6 (20.7%) / 6 / -Rs 20,770 / 0.71 | 28 / 5 (17.9%) / 7 / -Rs 95,040 / 0.69 |
| NS6 session range | 15 / 2 (13.3%) / 3 / -Rs 14,975 / 0.37 | 12 / 4 (33.3%) / 4 / +Rs 6,835 / 0.30 |

Reading: NS1 is the only family that lifts frequency materially on both indices (S1 base
3.08/3.20 -> 4.95/4.80 per week) — it breaks the old October uncapped ceiling of 9 candidates
by construction, since second legs are new trades, not loosened filters. But it does so by
adding mostly non-target legs: NS1's FT rate is BELOW its S1 base on Nifty (35.8% vs 38.4%)
and only slightly above on Bank (31.8% vs 27.7%). Bank's NS1 total (+Rs 14,130) is entirely a
rescue: base S1 Bank is -Rs 157,750 over Jan–Oct and second legs add +Rs 171,880, concentrated
in January (+Rs 72,270, 8 legs) and March (+Rs 57,495, 5 legs) with June -Rs 38,350 — a
concentrated, not steady, contribution. NS2's afternoon legs are genuinely positive on both
indices over Jan–Oct (+Rs 16,135 Nifty, +Rs 36,780 Bank) but add only 0.67/0.39 per week, so
the track still fails frequency. NS4 Bank (+Rs 98,750) is the largest single-family Bank net
after NS1's second legs, but at 41.7% FT and 1.48/week it fails two legs.

## Before / after — October 2026 spot (18 days) and October premiums (1 lot)
Premium FT = premium target exits. Premium /wk counts computed legs (all 84 computed).

| Track | Oct spot Nifty: n / FT / net prov. / wk | Oct spot Bank: n / FT / net prov. / wk | Oct premium Nifty: net / FT / wk | Oct premium Bank: net / FT / wk |
|---|---|---|---|---|
| BEFORE Skill S1 | 8 / 2 (25.0%) / +Rs 8,420 / 2.22 | 9 / 3 (33.3%) / +Rs 8,675 / 2.50 | +Rs 3,394.50 / 2 of 8 / 2.22 | -Rs 2,880 / 3 of 9 / 2.50 |
| NS1 | 13 / 5 (38.5%) / +Rs 21,045 / 3.61 | 14 / 6 (42.9%) / +Rs 36,055 / 3.89 | +Rs 1,696.50 / 3 of 13 (23.1%) / 3.61 | +Rs 1,120.00 / 6 of 14 (42.9%) / 3.89 |
| NS2 | 12 / 4 (33.3%) / +Rs 20,100 / 3.33 | 10 / 4 (40.0%) / +Rs 21,765 / 2.78 | -Rs 1,050.75 / 3 of 12 (25.0%) / 3.33 | -Rs 400.00 / 4 of 10 (40.0%) / 2.78 |
| NS3 | 5 / 1 (20.0%) / -Rs 12,055 / 1.39 | 3 / 1 (33.3%) / -Rs 8,420 / 0.83 | -Rs 4,395.50 / 0 of 5 / 1.39 | -Rs 960.00 / 1 of 3 (33.3%) / 0.83 |
| NS4 | 3 / 2 (66.7%) / +Rs 7,780 / 0.83 | 5 / 3 (60.0%) / +Rs 23,870 / 1.39 | +Rs 2,885.75 / 1 of 3 (33.3%) / 0.83 | +Rs 4,000.00 / 3 of 5 (60.0%) / 1.39 |
| NS5a | 7 / 4 (57.1%) / +Rs 20,075 / 1.94 | 6 / 1 (16.7%) / -Rs 12,715 / 1.67 | +Rs 8,710.50 / 1 of 7 (14.3%) / 1.94 | -Rs 6,120.00 / 1 of 6 (16.7%) / 1.67 |
| NS5b | 2 / 1 (50.0%) / +Rs 1,450 / 0.56 | 2 / 0 (0%) / -Rs 21,220 / 0.56 | -Rs 1,668.50 / 0 of 2 / 0.56 | -Rs 3,440.00 / 0 of 2 / 0.56 |
| NS6 | 2 / 0 (0%) / -Rs 7,170 / 0.56 | 0 / — / Rs 0 / 0.00 | -Rs 6,940.00 / 0 of 2 / 0.56 | 0 trades |

October premium leg splits that matter: NS1 Nifty's premium net (+Rs 1,696.50) is base
+Rs 3,394.50 dragged by second legs -Rs 1,698.00 (1 of 5 targets); NS1 Bank's (+Rs 1,120.00)
is base -Rs 2,880 rescued by second legs +Rs 4,000.00 (3 of 5 targets) — the same second-leg
mechanic helps one index and hurts the other in October. NS2 afternoon legs on October
premiums: Nifty 4 legs -Rs 4,445.25 (1 target) — the afternoon rescan actively hurts Nifty
on premiums even though its Jan–Oct spot afternoon legs were positive; Bank 1 leg +Rs 2,480
(target) cannot offset its -Rs 2,880 morning base. NS5a is the sharpest spot-to-premium
reversal: October spot FT 57.1% (Nifty) collapses to 14.3% on premiums, while its premium net
stays positive (+Rs 8,710.50) only through square-off greens — square-offs are not full
targets, so the FT leg still fails.

## Per-family verdicts (ALL legs together, Jan–Oct AND October premiums)
- **NS1 second signal — FAILS, closest.** Jan–Oct: net passes both indices, frequency
  4.95/4.80 (just under 5), FT fails both (35.8%/31.8%). October premiums: net passes both,
  FT fails both (23.1%/42.9%), frequency fails both (3.61/3.89). Discard as an adopted system;
  keep only as the closest November-paper watch candidate, frozen as-is.
- **NS2 afternoon rescan — FAILS.** Jan–Oct: Nifty net passes but FT (38.8%) and frequency
  (3.74) fail; Bank net fails outright (-Rs 120,970) despite positive afternoon legs, because
  the morning base is deeply negative. October premiums: net fails both indices. Discard.
- **NS3 gap-class — FAILS.** Jan–Oct: Nifty net fails (-Rs 49,380); Bank net passes but FT
  (37.9%) and frequency (1.43) fail. October: spot and premium both fail on both indices
  (premium FT 0% Nifty, 33.3% Bank). The gap/width regime split does not create a convicted
  edge. Discard.
- **NS4 OR re-break — FAILS.** Jan–Oct: Nifty net fails; Bank net passes (+Rs 98,750) but FT
  (41.7%) and frequency (1.48) fail. October premiums: Bank passes net AND FT (60%) but
  frequency is 1.39/week — one leg short of a pass, and the Jan–Oct FT failure already blocks
  it. Discard. (Note: NS4's October spot FT of 66.7%/60.0% does not survive to premiums on
  Nifty, 33.3%, or to Jan–Oct on either index.)
- **NS5a Skill rescan — FAILS.** Jan–Oct: Nifty net passes but FT (41.1%) and frequency (2.34)
  fail; Bank net fails (-Rs 52,235). October premiums: Nifty net passes but FT collapses to
  14.3%; Bank net fails. The confirmer-first gate removes trades without fixing hit quality.
  Discard.
- **NS5b CE mirror — FAILS.** Negative on both indices over Jan–Oct (-Rs 20,770 / -Rs 95,040)
  with FT 20.7%/17.9% and frequency 0.71/0.69; October premiums negative with 0 targets on
  both indices. The PDH-break CE mirror has no edge in this window. Discard.
- **NS6 session-range breakout — FAILS.** Fewest trades of any family (Jan–Oct 15/12 legs),
  Nifty negative, FT 13.3%/33.3%, frequency 0.37/0.30; October Bank has zero trades and Nifty
  premiums are -Rs 6,940 with 0 targets. The session-range level is too wide to fire and too
  late to pay when it does. Discard.

## What this means for the frequency blocker
Families A–D failed because the candidate ceiling was binding (October uncapped ceiling:
9 candidates). NS1 proves the ceiling can be broken by construction — second legs lift Jan–Oct
frequency to ~4.9/week — but the added legs dilute hit quality below 50% on every window, and
October frequency still falls short (3.61/3.89) because second legs need a morning exit by
13:30, which many October days do not produce. The remaining problem is therefore no longer
"no new trades exist": it is "new trades exist but do not hit full targets at a 50% rate."
Further work should target hit quality of second/afternoon legs specifically (e.g. why NS1
second legs hit only 31.6%/40.0% over Jan–Oct, and why NS5a's spot targets do not become
premium targets), not another family that merely adds more legs. No such quality fix was
attempted here, by design: each family was frozen, scored once, and discarded on failure
rather than re-tuned on the same window.

## Caveats
1. All spot rupees are provisional (points x 100 shares - Rs 40/leg) and are NOT options-lot
   profits. All premium rupees are per 1 lot with the assumed Rs 220 cost and the -50/+90
   overlay; they are comparable across versions but are not any version's native exit rule.
2. October is 18 days; several October premium cells rest on 2–5 legs (NS5b, NS6, NS3 Bank)
   and must not be over-read. The Jan–Oct window (203 days) is the weight-bearing window;
   October premiums are the translation check, and they mostly make NS families look worse,
   not better, than spot.
3. (lA) Jan–Oct was not recomputed here (it needs the full re-entry engine); the October
   (lA)/V5-v2 premium baselines from the brief (V5-v2 Bank 4 trades, 100%, +Rs 9,920/1 lot;
   (lA) v2 Nifty 3 trades, +Rs 6,678.50/1 lot) are carried as context, not re-derived. NS
   pass/fail does not depend on them: NS families were judged on their own legs.
4. Nothing in this report is a live-trading recommendation. No orders were placed, no
   positions exist, and no family is adopted on in-sample results.

## Files delivered
- Frozen definitions (6 files, listed above).
- [NS1 trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns1_trades_jan_oct_2026.csv)
- [NS2 trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns2_trades_jan_oct_2026.csv)
- [NS3 trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns3_trades_jan_oct_2026.csv)
- [NS4 trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns4_trades_jan_oct_2026.csv)
- [NS5a trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns5a_trades_jan_oct_2026.csv)
- [NS5b trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns5b_trades_jan_oct_2026.csv)
- [NS6 trades Jan–Oct](sandbox://workspace/trading/index_options_newsetup_ns6_trades_jan_oct_2026.csv)
- [October premium trades, all families](sandbox://workspace/trading/index_options_newsetup_premium_october_trades.csv)
- [October contract list (cached vs fetched)](sandbox://workspace/trading/index_options_newsetup_oct_contracts.csv)
- Base comparison files:
  [Skill S1 Jan–Oct](sandbox://workspace/trading/index_options_newsetup_base_s1_trades_jan_oct_2026.csv),
  [V4 Jan–Oct](sandbox://workspace/trading/index_options_newsetup_base_v4_trades_jan_oct_2026.csv)
- Scripts (not deliverables for merging, kept for audit):
  [newsetups_score.py](sandbox://workspace/trading/newsetups_score.py),
  [newsetup_premium_fetch.py](sandbox://workspace/trading/newsetup_premium_fetch.py),
  [newsetup_premium_score.py](sandbox://workspace/trading/newsetup_premium_score.py)
- `index_options_progressive_tuning.md` was NOT edited, as instructed.
