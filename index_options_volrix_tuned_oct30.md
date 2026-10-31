# Index OPTIONS — Volrix tuned, 2026-10-30 (paper only, no orders, no stocks, no other systems)

**Scope:** Volrix ONLY, index OPTIONS only, Nifty and Bank Nifty separately, never
pooled. Paper only, no orders, no futures. October 2026 first (1–28 Oct, 18 trading
days), then a Jan–Oct 2026 spot check for variants that trade in October.
**Nothing is adopted on October / in-sample alone. November 2026 paper from
Mon 2026-11-02 remains validation.**
The old spot-proxy futures nets (Nifty +₹3,37,730 / Bank +₹62,737 over 7 years,
spot proxy, NOT futures) are NOT results for any variant below and are not used
in any total here. No trigger that never fired is counted as a trade.

## 0. Baseline (from the prior Volrix files, read first)

- Volrix original: previous-day underlying close <= -2%, next session 09:16 entry,
  LONG ATM call, monthly expiry 0, 1 lot, no stop/target, 5-session hold,
  10-session cooldown.
- October 2026 at -2%: 0 trades on both indices. Nifty's worst prev-day close in
  October was -1.64% (8 Oct); Bank's was -1.16% (23 Oct). Over 7 years the original
  fired ~4 times/year — by design an occasional overlay, not a daily system.

## 1. Frozen definitions (fixed before premium scoring)

Common to all variants below, unless a variant states otherwise:
- **Instrument:** LONG ATM CALL, 1 lot. Lot Nifty 65 / Bank 30. Cost ₹220/trade
  (assumed, labelled), applied to every premium net.
- **Strike:** ATM nearest 100 to the trigger-day (previous-day) close for (a)/(b);
  for (c-raw) ATM nearest 100 to the confirmation-entry spot (see below).
  This follows the task's "ATM nearest 100" instruction, NOT the prior Nifty
  options report's nearest-50 basis.
- **Expiry:** monthly 27 Oct 2026 for entries 1–27 Oct. (No Volrix-tuned entry falls
  on 28 Oct, so the weekly 3 Nov expiry rule is stated but unexercised.)
- **Premium bars:** Upstox expired-instruments 5-minute candles, fetched
  2026-10-30 via the script-token browser-fetch route (connector returned 401,
  as in prior October premium work; token never printed/logged). Entry premium =
  open of the first 5-min option candle with time > the signal time (the October
  premium convention used in `premium_score_oct.py`). Square-off / exit bar =
  15:10 close. Note: the original Volrix code exits at 15:15; the 15:10 bar is
  used here to match the October premium convention, stated, not hidden.
- **Cooldown:** 10 sessions, kept in EVERY variant (a), (b), (c), (c-raw).
  Cooldown runs concurrently with any hold and is the binding constraint in
  Jan–Oct (see Section 5): entries are at least 10 trading sessions apart.
- **Skip quirk:** the original code's skip-after-monthly-expiry-change quirk was
  NOT simulated in the Jan–Oct spot check. Its October effect is nil (no October
  trigger falls on a skip day: the Sep monthly expiry skip day is 1 Oct, with no
  trigger; the Oct expiry skip day is 29 Oct, outside the window and with no
  trigger). Jan–Oct entry counts are therefore "cooldown + hold" counts, and a
  small number of Jan–Oct entries could additionally be skipped under the exact
  original code — stated as a limitation, not hidden.
- **Full-target definition:** a trade counts as a full target ONLY if it exits at
  its +90 premium target (variant (b) only). Square-off greens are NOT full
  targets. Variants (a)/(c)/(c-raw) have NO target in their primary definition,
  so their full-target rate is "n/a (no target)" — they cannot pass a
  full-target >= 50% leg as defined, by construction, not by outcome.
- **Frequency:** October: trades / 18 days x 5. Jan–Oct: trades / 203 trading
  days x 5.

### (a) Threshold lowered, everything else original
- Trigger: prev-day close <= -1.5% / -1.25% / -1.0% (three separate sub-variants,
  scored separately). Entry next session at the 09:16 evaluation (premium entry =
  09:20 5-min bar open). Hold 5 sessions (entry day = session 1), NO stop, NO
  target. Expiry inside a hold: exit at 15:10 on the expiry day, no roll, trade
  ends there (the prior options-translation rule). This bites Bank in October:
  entry 26 Oct, monthly expiry 27 Oct is session 2, so the Bank (a) trade exits
  27 Oct, NOT on a 5th session.

### (b) Volrix intraday adaptation
- Trigger: same as (a) (three thresholds, scored separately). Entry next session
  (premium entry = 09:20 5-min bar open). Exit SAME DAY 15:10 at the latest.
  **Stop/target FROZEN: stop = entry premium - 50 points, target = entry
  premium + 90 points**, checked on every 5-min bar including the entry bar,
  stop before target on a bar, square-off at the 15:10 bar close if neither
  hits. Cooldown 10 sessions still applies, so a second trigger inside the
  cooldown is still blocked even though the position is closed the same day.

### (c) Volrix + confirmation, primary: TAKEN Skill S1 CE signal
- Trigger: -1.0% (the widest (a) threshold, so the most candidates to confirm
  or reject). Cooldown 10 sessions, 5-session hold, no stop/target, expiry
  rule as in (a).
- **Confirmation FROZEN:** the rebound call is taken ONLY if a TAKEN Skill S1 CE
  signal fires on the entry day — i.e. a raw OR-breakout CE that appears in the
  v2 S1 taken list (not blocked). The (lA) rescan is PE-only, so it cannot
  confirm a CE rebound and is NOT used here; the "morning rescan/OR" leg is the
  Skill OR breakout. A blocked S1 CE (e.g. S1_CE_bearish) is NOT confirmation.
  Entry timing is unchanged from (a) for the filter test (09:20 premium entry);
  a day with no taken S1 CE signal produces NO trade, even if the raw direction
  later breaks out.

### (c-raw) Sensitivity, frozen separately: raw morning OR direction
- Same trigger (-1.0%), cooldown, hold and expiry rule as (c), but confirmation
  is direction-only, ignoring the S1 bias block: **a 5-min spot close above the
  entry-day OR high at or before 11:30** (OR = 09:15–09:55 bars, as in Family B).
  This is a SEPARATE variant, never blended into (c).
- Tradability: because confirmation fires after 09:16, entry is DELAYED to the
  first 5-min option candle after the confirming spot signal (premium entry =
  that bar's open), and the strike is ATM nearest 100 to the entry spot (the
  open of the first 5-min spot bar after the signal). If no close above the OR
  high occurs by 11:30, no trade.

## 2. October trigger scan (before any premium outcome)

Prev-day close % (Upstox daily closes, volrix CSVs):

| Index | Trigger days in October (down %) | Entry days (October-isolated, fresh state 1 Oct) |
|---|---|---|
| Nifty | 8 Oct -1.64%; 19 Oct -1.11% | -1.5%: 9 Oct only. -1.25%: 9 Oct only. -1.0%: 9 Oct only — 21 Oct is BLOCKED by the 10-session cooldown from the 9 Oct entry (cooldown runs to 26 Oct), so the 19 Oct trigger does NOT become a second October trade at any threshold. |
| Bank | 23 Oct -1.16% | -1.5%: none. -1.25%: none (23 Oct -1.16% does not meet either). -1.0%: 26 Oct only. |

October-isolated trade counts (fresh state at 1 Oct, the October-first framing):
(a)/(b) Nifty: 1 trade at -1.5%, 1 at -1.25%, 1 at -1.0% (all the same 9 Oct trade).
(a)/(b) Bank: 0 at -1.5%, 0 at -1.25%, 1 at -1.0% (26 Oct).
(c) primary: 0 on both indices (see Section 4). (c-raw): Nifty 1 (9 Oct),
Bank 0 (raw breakout only at 15:25, after the 11:30 morning window).

**Continuity warning (read before quoting the October-isolated counts):** in a
CONTINUOUS run from September, Nifty at -1.25% and -1.5% has ZERO October trades,
not one: a 25 Sep entry (trigger 24 Sep, -1.63%) is still inside its 10-session
cooldown on 9 Oct (cool = 1 on 9 Oct, 0 only on 12 Oct). The 9 Oct premium for
-1.25%/-1.5% below is therefore an October-isolated score of a trade that, in
continuous trading, would not have fired in October. Nifty -1.0% and Bank -1.0%
are unaffected (their September entries' cooldowns expired before October).

## 3. October premium table (actual traded premiums, 1 lot, -220 cost)

All six contract-days fetched 2026-10-30 (77 5-min bars each). No premium is
estimated or backfilled.

| Variant / index | Entry (strike/expiry, entry premium, entry bar) | Exit (premium, bar, reason) | Premium change | Net / 1 lot |
|---|---|---|---|---|
| (a) -1.0% / -1.25% / -1.5% Nifty (same trade) | 9 Oct, 22200 CE / 27 Oct, 398.00, 09:20 open | 15 Oct, 796.70, 15:10 close, 5th-session square-off | +398.70 | **+₹25,695.50** (398.70 x 65 - 220) |
| (a) -1.0% Bank | 26 Oct, 54300 CE / 27 Oct, 238.55, 09:20 open | 27 Oct, 14.10, 15:10 close, monthly-expiry exit (session 2, no roll) | -224.45 | **-₹6,953.50** (224.45 x 30 + 220) |
| (b) -1.0% / -1.25% / -1.5% Nifty (same trade) | 9 Oct, 22200 CE / 27 Oct, 398.00, 09:20 open; stop 348.00 / target 488.00 | 9 Oct, 488.00, 09:45 bar, TARGET (high 494.15; low never <= stop before it) | +90.00 | **+₹5,630.00** (90 x 65 - 220) |
| (b) -1.0% Bank | 26 Oct, 54300 CE / 27 Oct, 238.55, 09:20 open; stop 188.55 / target 328.55 | 26 Oct, 328.55, 09:55 bar, TARGET (high 390.40; stop checked first on every bar, never hit before it) | +90.00 | **+₹2,480.00** (90 x 30 - 220) |
| (c) primary Nifty / Bank | — | — | — | 0 trades, ₹0 (not a missing fetch) |
| (c-raw) Nifty | 9 Oct, 22500 CE / 27 Oct, 310.30, 10:10 open (after 10:05 confirming close 22482.20 above OR high 22480.45; entry spot 22482.50 -> nearest 100 = 22500) | 15 Oct, 533.05, 15:10 close, 5th-session square-off | +222.75 | **+₹14,258.75** (222.75 x 65 - 220) |
| (c-raw) Bank | — | — | — | 0 trades (first close above OR high 54357.60 is 15:25, after the 11:30 window) |

Notes on the premium bars, for audit:
- Nifty 22200 CE 9 Oct: 09:20 bar open 398.00, day low from 09:20 to 15:10 is
  386.85 (never near the (b) stop 348.00); 15:10 close 534.55 (intraday square-off
  would have been +₹8,655.75, but (b) exits at target, so that figure is NOT
  claimed for (b)).
- Bank 54300 CE 26 Oct: 09:20 bar open 238.55; day low from 09:20 is 171.95,
  which is BELOW the (b) stop 188.55 — but it occurs AFTER the 09:55 target hit,
  so it does not affect (b). It does show the (b) target exit was not a
  comfortable hold: the same contract later fell through the stop level.
- Bank 54300 CE 27 Oct (expiry day): 09:20 open 202.25, 15:10 close 14.10,
  last bar 0.05 — an expiry-day premium collapse, consistent with spot closing
  53974.90, well below the 54300 strike.

## 4. Before / after per track (October, premium, per index separately)

"Working" test (task): net > 0 AND full-target >= 50% AND frequency >= 5/week.
Frequency = trades / 18 x 5. Full-target = target exit only (see Section 1).

| Variant / index | Trades (before -> after) | Premium net / 1 lot (before -> after) | Full-target % | Frequency / week | Passes? Failing leg(s) |
|---|---|---|---|---|---|
| Original -2% Nifty -> (a) -1.5% Nifty | 0 -> 1 (Oct-isolated; 0 continuous) | ₹0 -> +₹25,695.50 | n/a (no target) | 0 -> 0.28 | NO — frequency, and full-target n/a by construction |
| Original -2% Nifty -> (a) -1.25% Nifty | 0 -> 1 (Oct-isolated; 0 continuous) | ₹0 -> +₹25,695.50 | n/a | 0 -> 0.28 | NO — same, plus continuous-run caveat |
| Original -2% Nifty -> (a) -1.0% Nifty | 0 -> 1 | ₹0 -> +₹25,695.50 | n/a | 0 -> 0.28 | NO — frequency; full-target n/a |
| Original -2% Bank -> (a) -1.5% Bank | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade at all |
| Original -2% Bank -> (a) -1.25% Bank | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade at all |
| Original -2% Bank -> (a) -1.0% Bank | 0 -> 1 | ₹0 -> -₹6,953.50 | n/a | 0 -> 0.28 | NO — net negative, frequency, full-target n/a |
| Original Nifty -> (b) Nifty (any threshold) | 0 -> 1 | ₹0 -> +₹5,630.00 | 100% (1/1 target) | 0 -> 0.28 | NO — frequency only (net and full-target pass) |
| Original Bank -> (b) Bank (-1.0% only) | 0 -> 1 | ₹0 -> +₹2,480.00 | 100% (1/1 target) | 0 -> 0.28 | NO — frequency only |
| Original Bank -> (b) Bank (-1.25% / -1.5%) | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade |
| Original Nifty -> (c) primary Nifty | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade. Reason: 9 Oct S1 CE exists (10:05 breakout) but is BLOCKED (S1_CE_bearish), so it is not a taken signal and fails the frozen confirmation. |
| Original Bank -> (c) primary Bank | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade. Reason: no taken S1 CE signal on 26 Oct (raw breakout only at 15:25, with no entry bar after it). |
| Original Nifty -> (c-raw) Nifty | 0 -> 1 | ₹0 -> +₹14,258.75 | n/a (no target) | 0 -> 0.28 | NO — frequency; full-target n/a. Note: (c-raw) net is SMALLER than (a) on the same hold (+₹14,258.75 vs +₹25,695.50) because the delayed 10:10 entry takes the higher 22500 strike instead of 22200. Confirmation cost premium here, it did not add it. |
| Original Bank -> (c-raw) Bank | 0 -> 0 | ₹0 -> ₹0 | — | 0 | NO — no trade (morning window). |

**Closest variant, stated plainly:** (b) intraday is the closest to the working
test — it is the ONLY variant family that passes two legs (net > 0 and
full-target 100%) on both indices — but it still fails frequency by a wide
margin (0.28/week vs 5/week required, i.e. about 1 trade per 18-day month, not
1 per day). No variant is "working" under the task's test.

## 5. Jan–Oct 2026 check (for variants that trade in October)

Method: continuous state machine on Upstox daily closes (volrix CSVs), Jan–Oct
2026 (203 trading days), trigger = prev-day close %, cooldown 10 sessions,
hold blocking as in Section 1 (cooldown is binding; see Section 1 skip-quirk
limitation). **Spot points ONLY** (entry-day open to 5th-session close for (a),
entry-day open to same-day close for (b)). Spot points are NOT converted to
rupees and are NOT an options profit — premium moves are not 1:1 with spot, and
the October premium results above show why (Bank (a) premium -224.45 points on
a spot move that, on the expiry-exit basis, is not the 5-day spot move at all).
**Jan–Oct premiums were NOT scored** (no Jan–Oct option candles were fetched
for these variants; the prior options report's 5 trades are 5-day monthly holds
on the original -2% entries, a different variant, and are not reused here).

| Index / threshold | Entries Jan–Oct (continuous) | October entries in continuous run | Freq / week (trades/203x5) | Spot (a) 5-day points (wins) | Spot (b) 1-day points (wins) |
|---|---|---|---|---|---|
| Nifty -1.0% | 12 | 1 (9 Oct) | 0.30 | +959.85 (7/12) | +618.25 (9/12) |
| Nifty -1.25% | 8 | 0 (Sep 25 entry blocks Oct) | 0.20 | -1,514.20 (3/8) | -45.65 (6/8) |
| Nifty -1.5% | 7 | 0 (Sep 25 entry blocks Oct) | 0.17 | -638.20 (3/7) | +363.80 (6/7) |
| Bank -1.0% | 13 | 1 (26 Oct) | 0.32 | +948.20 on 12 scored (8 wins; 26 Oct 5th session falls outside the 28 Oct CSV, incomplete in spot terms — its premium expiry exit is the October score, Section 3) | +2,148.65 (9/13) |
| Bank -1.25% | 9 | 0 (no October trigger meets -1.25%) | 0.22 | +2,924.30 (7/9) | +3,284.40 (7/9) |
| Bank -1.5% | 7 | 0 (no October trigger meets -1.5%) | 0.17 | -971.00 (4/7) | +1,393.85 (5/7) |

Entry-date lists (continuous run, for audit):
- Nifty -1.0%: 9 Jan, 2 Feb, 16 Feb, 2 Mar, 20 Mar, 27 Apr, 12 May, 1 Jun, 24 Jun,
  9 Jul, 16 Sep, 9 Oct.
- Nifty -1.25%: 21 Jan, 16 Feb, 5 Mar, 20 Mar, 12 May, 1 Jun, 9 Jul, 25 Sep.
- Nifty -1.5%: 2 Feb, 5 Mar, 20 Mar, 13 May, 1 Jun, 9 Jul, 25 Sep.
- Bank -1.0%: 22 Jan, 20 Feb, 9 Mar, 24 Mar, 10 Apr, 29 Apr, 1 Jun, 24 Jun, 9 Jul,
  23 Jul, 2 Sep, 25 Sep, 26 Oct.
- Bank -1.25%: 2 Feb, 20 Feb, 9 Mar, 24 Mar, 10 Apr, 29 Apr, 24 Jun, 9 Jul, 16 Sep.
- Bank -1.5%: 2 Feb, 5 Mar, 20 Mar, 10 Apr, 29 Apr, 9 Jul, 25 Sep.
- (c)/(c-raw) Jan–Oct: NOT scored. Their confirmed counts are bounded above by
  the unconfirmed trigger counts above, but S1/OR confirmation was not rescanned
  for Jan–Oct in this run, so no confirmed Jan–Oct count, spot total or
  frequency is claimed for (c)/(c-raw). Do not quote the (a) counts as (c) counts.

Reading of the Jan–Oct spot check (spot only, not a premium verdict):
- Lowering the threshold does NOT monotonically improve the spot result. On
  Nifty, -1.0% is the only threshold with a positive 5-day spot total; -1.25%
  and -1.5% are deeply negative on the 5-day spot basis despite fewer trades,
  because the entry sets are different (cooldown picks different entries), not
  nested subsets. On Bank, -1.25% looks best on spot, -1.5% negative — again,
  different entry sets, not a threshold curve.
- Frequency on Jan–Oct spot is 0.17–0.32/week at every threshold on both
  indices. Even the widest threshold tested (-1.0%) is roughly 1 trade per
  3 weeks, not 1 per day.

## 6. Verdict

- **No Volrix variant is working under the task's test** (net > 0 AND
  full-target >= 50% AND >= 5/week on October premiums). The frequency leg is
  not close on any variant: best October frequency is 0.28/week, best Jan–Oct
  spot frequency is 0.32/week. The 5/week bar would require roughly 18 trades
  in an 18-day month; Volrix at -1.0% produces 1.
- **Variant that trades most often with positive October premium net:** (b)
  intraday at -1.0% — 1 trade on each index, both target exits, +₹5,630.00
  (Nifty) and +₹2,480.00 (Bank) per 1 lot. That is the variant to carry into
  November paper IF a Volrix variant is carried at all — with its definition
  frozen as in Section 1(b) (trigger -1.0%, cooldown 10, entry 09:20 premium
  bar, stop -50 / target +90, same-day 15:10 square-off) — and with the honest
  label that it is an occasional overlay, not a daily system, and that its
  October evidence is exactly 2 trades.
- **Do NOT force it to 5/week.** Reaching 5/week from Volrix would require a
  fundamentally different (intraday) definition — e.g. dropping the prev-day
  close trigger entirely, or dropping the cooldown — which is no longer Volrix.
  That redefinition is NOT made here and is NOT scored here. If the user wants
  a daily Volrix-derived system, that is a new system to freeze and validate
  separately, not a tuning of this one.
- **(a) is not a rescue either.** Its one big October premium win (Nifty
  +₹25,695.50) is a single 5-day hold on a strong rebound week, paired with a
  Bank expiry wipeout (-₹6,953.50) on the only other October trade. On Jan–Oct
  spot, (a) at -1.25%/-1.5% is negative on Nifty. One trade is not a system.
- **(c) primary adds nothing in October** — it filters both candidates to
  zero. (c-raw) trades once (Nifty) but for LESS premium than the unfiltered
  (a) trade on the same hold, because the delayed entry takes a higher strike.
  Confirmation, on this October evidence, costs rather than adds.
- **Nothing adopted on October/in-sample alone.** November 2026 paper from
  Mon 2026-11-02 remains validation, with any carried variant's definition
  frozen before November (Section 1). A November log for Volrix would need its
  own entries (trigger day, entry premium/bar, stop/target or hold exit,
  expiry handling) — it is NOT covered by the Cluster 2/3 log spec, and no
  November trades are claimed here.

## 7. Trade list (every variant that trades in October, premium)

| Variant | Index | Trigger day (down %) | Entry day | Strike / expiry | Entry premium (bar) | Exit premium (bar, reason) | Net / 1 lot |
|---|---|---|---|---|---|---|---|
| (a) -1.0/-1.25/-1.5% | Nifty | 8 Oct (-1.64%) | 9 Oct | 22200 CE / 27 Oct | 398.00 (09:20) | 796.70 (15 Oct 15:10, 5th-session square-off) | +₹25,695.50 |
| (a) -1.0% | Bank | 23 Oct (-1.16%) | 26 Oct | 54300 CE / 27 Oct | 238.55 (09:20) | 14.10 (27 Oct 15:10, monthly-expiry exit) | -₹6,953.50 |
| (b) -1.0/-1.25/-1.5% | Nifty | 8 Oct (-1.64%) | 9 Oct | 22200 CE / 27 Oct | 398.00 (09:20) | 488.00 (9 Oct 09:45, target) | +₹5,630.00 |
| (b) -1.0% | Bank | 23 Oct (-1.16%) | 26 Oct | 54300 CE / 27 Oct | 238.55 (09:20) | 328.55 (26 Oct 09:55, target) | +₹2,480.00 |
| (c-raw) | Nifty | 8 Oct (-1.64%) | 9 Oct | 22500 CE / 27 Oct | 310.30 (10:10) | 533.05 (15 Oct 15:10, 5th-session square-off) | +₹14,258.75 |

Zero-trade variants (not missing data): (a) Bank -1.25% and -1.5%; (b) Bank
-1.25% and -1.5%; (c) primary both indices; (c-raw) Bank. The 19 Oct Nifty
trigger (-1.11%) at -1.0% is a blocked trigger, not a trade (cooldown from
9 Oct) — it is not counted anywhere above.

## 8. Files

- This report: `index_options_volrix_tuned_oct30.md`
- Fetch script (paper only, no orders): `volrix_tuned_fetch_oct30.py`
- Fetched 5-min premium candles:
  `v4_options_oct_data/candles_premium_NIFTY_22200CE_2026-10-09_2026-10-27.json`,
  `..._2026-10-15_...`, `..._NIFTY_22500CE_2026-10-09_...`,
  `..._2026-10-15_...`, `..._BANKNIFTY_54300CE_2026-10-26_...`,
  `..._2026-10-27_...`
- Daily closes used for triggers: `volrix/nifty_daily_2019_2026.csv`,
  `volrix_banknifty/banknifty_daily_2019_2026.csv`; spot 5-min OR check:
  `data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv`
- Prior Volrix files read first (not re-scored here):
  `volrix_nifty_large_down_rebound_backtest.md`,
  `volrix_nifty_large_down_rebound_options_backtest.md`,
  `volrix_banknifty_large_down_rebound_backtest.md`
