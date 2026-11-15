# VIX PROGRAMME — SPEC (FROZEN 2026-11-15, before any scoring)

Owner's order 2026-11-15: work on VIX-related strategies. Research only;
arm nothing. OPTION BUYING ONLY. Paper only, real money Rs0.

## Data

- **India VIX daily close:** `round2_history/india_vix_daily.csv` — the
  Round-2 dataset (source: Yahoo Finance `^INDIAVIX` published daily
  closes, as documented in `new_data_round2_2026-11-13.md`). Coverage:
  2025-12-22 → 2026-11-11; 203 of 205 Jan–Oct 2026 trading days carry a
  close. Missing: 2026-01-01 and 2026-02-01. Missing is never filled —
  any read needing a missing VIX close emits no signal / counts NC.
- **Spot:** stored 5-min spot series (`daily2leg/spot.json`, both
  indices, 2025-01-01 → 2026-10-30). Daily close = last bar's close.
  Trading calendar = days present for both indices.
- **Premium bars:** the programme's stored series plus the expired-
  instruments fetch route, via the frozen Round-1/Round-2 machinery
  (`oi_buildup_score.py` + the full-day repair from `round2_score.py`),
  imported unmodified. On HTTP 429: hard stop, partials saved, flagged.
- **Stored legs (Part A):** Bank TUNED STACK v2 =
  `solid60_programme_2026-11-13_bank_A_stack_ALL_X-1_trades.csv`
  (111 legs, +Rs127,351.50 — re-verified at load); Nifty TUNED v1 =
  `solid60_programme_2026-11-13_nifty_v1_ALL_X-1_trades.csv`
  (74 legs, +Rs103,050.25 — re-verified at load).

## Common Part-B construction (both rules, both indices)

Signal at the close of day D from data knowable at D's close only.
Trade on the next trading day D+1 (the next day on the spot calendar).
Entry = OPEN of the 09:20 5-min bar of the premium series on D+1.
Strike = ATM (nearest step: Bank 100 / Nifty 50) to the 09:20 spot
bar's open on D+1. Contract = in-force expiry of the trade day (Bank
monthly / Nifty weekly-front, from the OI dataset's expiry column).
Exits (frozen by the task): stop −50 checked BEFORE target +90 on
every bar including the entry bar, fills at the level; square-off at
the 15:20 bar close (if the series ends earlier, the last bar's
close). 1 lot (Bank 30 / Nifty 65). Cost Rs220/trade. Buying only.
A signal whose trade cannot be constructed (no spot bar, no premium
candles, replay impossible) is NC — counted, never estimated.

## PART A — ANATOMY (descriptive; no new book)

Split the stored Jan–Oct legs of Bank TUNED STACK v2 and Nifty TUNED
v1 by the PRIOR trading day's India VIX close band:
<12 / 12–14 / 14–17 / 17–20 / >20 (band edges: [12,14), [14,17),
[17,20) — a close of exactly 14.00 sits in 14–17).
Per band per book: legs, net, WR (net > 0), Rs per trade-day where
trade-days = distinct leg dates inside the band. Legs whose prior
day's VIX close is missing are counted separately as NC.

## PART B — TWO FROZEN STANDALONE RULES

### V1 — LOW-VIX TREND BUY
At close of D: VIX close of D < 12 AND spot close of D above its
20-day average (mean of the closes of D and the 19 prior trading
days, spot calendar). If both hold → buy CE on D+1. Long-trend only:
if spot is below the 20-DMA there is no trade (no PE leg exists in
V1). One trade per day max (the rule fires at most once per day by
construction).

### V2 — VIX-SPIKE FADE
At close of D: VIX close of D is ≥ +15% versus the prior trading
day's VIX close AND the spot change on D is ≤ −1% (close vs prior
close). If both hold → buy CE on D+1 (reversal bet). One trade per
spike event: a day qualifies only if the prior trading day did not
itself satisfy both spike conditions (an event is the first day of a
spike run).

## GATE-LITE (per rule per index)

Trades dated Jan–Oct 2026 only. Report: trades, net, WR, halves
(Jan–May / Jun–Oct by trade date), ex-top-3 (total minus the three
largest trade nets), month table (net + trades per month), and a
random-entry placebo: 200 draws; each draw takes the same number of
trades on uniformly random distinct Jan–Oct trade days (same
direction — CE for both rules — same ATM/first-bar construction and
exits; a drawn day that cannot be constructed is resampled to another
unused day); percentile = share of draws whose total is ≤ the rule's
total.
**PASS only if: total > 0 AND both halves > 0 AND ex-top-3 > 0 AND
placebo percentile ≥ 95. Otherwise FAIL, naming the failing legs.**
No parameter of V1/V2 may be adjusted after scoring; a failed rule is
not retested in this programme.

## Deliverables

`vix_programme_2026-11-15.md` + `vix_programme_results.json`
(+ `vix_programme_trades.csv` with every scored Part-B trade).
