# Index OPTIONS pilot week — Oct 19–23, 2026 (Mon–Fri)

Paper only. No orders. No live trading. Options only for index — no futures
trade, no futures total anywhere in this report. Spot index is trigger/levels
only, never the traded instrument.

## 0. The week is 4 trading days, not 5 — read the bar correctly

**Tue 2026-10-20 was Dussehra, an NSE/BSE trading holiday** (NSE 2026 holiday
calendar; cache confirms it: no 5-min bars for 20 Oct for either index).
Trading days in this "week" are therefore **Mon 19, Wed 21, Thu 22, Fri 23 Oct
— 4 days**.

Consequence, stated before any verdict: **5 trades in this week is
mathematically impossible for a 1-trade-per-day version** (max 4). The user
bar "5 trades per week = 1 per day" is judged here as **1 per trading day
(4/4)**, and the full-October run (18 trading days) is the proper 5/week
test. Any report claiming 5 pilot-week trades for a 1/day version would be
forcing a second trade on a day or inventing a holiday trade.

## 1. Option-premium data gap — stated plainly, not papered over

- Cache (`~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/`) contains
  **spot 5-min + spot daily only**. No option candles are in it.
- Attempted this run, via the script token store (separate from the Muse
  connector, which is still 401): direct API calls with the script token to
  the expired-instruments expiries endpoint and to the profile endpoint
  both returned **HTTP 403**. (The browser-fetch route proved at 07:06 IST
  on 2026-10-30 returned 200 for profile; the direct route does not. That
  discrepancy is itself a blocker to resolve before premium P&L.)
- **Therefore NO option-premium P&L is computed in this report.** The trade
  CSV's premium columns are `NOT_AVAILABLE` and net per 1 lot is
  `NOT_COMPUTED` for every row. Spot points are reported first, and rupees
  only as "per 100 shares, provisional cash translation — NOT an options-lot
  profit and NOT a futures profit" (₹40/trade assumed cost for the
  spot-trigger legs).
- In particular, **V4 options cannot be scored from spot points**: the V4
  rule is stop −50 / target +90 **option points**, and an option premium
  does not move 1:1 with spot. Converting a +114.30 spot move into an
  options-lot profit would be bluff, so it is not done here.
- Lot sizes used for strike identification only (not for any P&L):
  Nifty 65 (2026 chains, per the Volrix options reports), Bank Nifty 30
  (Jan 2026+ expiries, per the Volrix Bank report). Strikes below are ATM
  (nearest 100 to entry spot); none of 21/23 Oct is a monthly-expiry day
  (monthly expiry Tue 27 Oct 2026), so the 100-point-ITM expiry-day rule
  does not apply to any pilot-week trade.

## 2. Versions run separately, never pooled, never deduped

| Version | Definition used here |
|---|---|
| (lA) | BN-confirmed rescan morning + band-filtered re-entry, from `DOCUMENTED_V5_LA_BANKNIFTY.md` and `october_2026_la_and_skill_nifty_bank.md` (morning + re-entry = one candidate per symbol+date). Bank leg is the mirror (Nifty confirms Bank). |
| Skill | Day Trader skill **OR entries only, raw** — first 5-min close beyond OR high (CE) or below OR low (PE). No V4-style filters. The capped Skill variant (bias/room filters from the October report) is reported alongside as a contrast, because it changes the result to zero. |
| V4 options | Original V4 setups 1–4 on spot triggers (setups 2/3/4 on PD/OR levels here; Setup 1 needs user-supplied Red bands, none supplied for this week, so it is skipped). Spot signals only; premium outcome NOT computed (§1). |
| Volrix | Post Large Down Day Rebound, options translation as previously frozen: LONG ATM CALL, monthly expiry 0, 1 lot, no stop/target, trigger = previous day close down ≥2%, 10-session cooldown, skip-after-expiry-change quirk embodied in the entry list. Spot-proxy totals from the old reports are NOT reused here. |

## 3. Pilot-week results — per version, per index, separately

Spot points first. Provisional rupees = points × 100 − ₹40/trade, labelled
provisional, NOT an options-lot profit.

### (lA) — uncapped signals

| Track | Trades | Days traded / 4 | Full targets | Spot points | Provisional net |
|---|---|---|---|---|---|
| (lA) Nifty | 1 | 1 (23 Oct) | 1 | +114.30 | +₹11,390 |
| (lA) Bank | 2 | 2 (21, 23 Oct) | 2 | +443.40 | +₹44,260 |

Capped (1/week per column, as in the October report): (lA) Nifty 1
(+₹11,390), (lA) Bank 1 (21 Oct only, +₹20,200; 23 Oct +₹24,060 capped out
in W43). The cap, not the signal, is what removes the second Bank trade.

Trades: 21 Oct Bank PE signal 11:15, entry 55,249.15, stop 55,350.35,
target 55,046.75, exit 11:40 target; 23 Oct Bank PE signal 09:55, entry
54,444.05, stop 54,564.55, target 54,203.05, exit 10:10 target; 23 Oct Nifty
PE signal 10:05, entry 22,526.25, stop 22,583.40, target 22,411.95, exit
10:35 target. **Zero (lA) failures this week — all targets.**

### Skill — raw OR

| Track | Trades | Days traded / 4 | Full targets | Spot points | Provisional net |
|---|---|---|---|---|---|
| Skill Nifty | 3 | 3 (21, 22, 23 Oct) | 1 | −18.45 | −₹1,965 |
| Skill Bank | 3 | 3 (21, 22, 23 Oct) | 2 | +372.15 | +₹37,095 |

Trades: Nifty CE 21 Oct signal 09:30, entry 23,117.35, stop 23,069.20 hit
09:45 (−₹4,855); Nifty CE 22 Oct signal 10:20, entry 22,727.05, stop
22,658.15 hit 11:45 (−₹6,930); Nifty PE 23 Oct signal 09:30, entry
22,683.70, target 22,585.10 hit 10:00 (+₹9,820). Bank CE 21 Oct signal
09:30, entry 55,821.65, stop 55,746.80 hit 09:45 (−₹7,525); Bank CE 22 Oct
signal 10:10, entry 54,789.20, target 55,087.20 hit 10:30 (+₹29,760);
Bank PE 23 Oct signal 09:45, entry 54,612.80, target 54,463.80 hit 09:55
(+₹14,860).

**Contrast that matters:** the capped Skill variant (bias-aligned +
room ≥200×scale + signal-close filters) gives **0 trades this week** —
it filters out all 6 raw signals. The two CE losers on Nifty were
bearish-bias days, so the bias filter correctly blocked losers; but it
also blocked the two Bank winners (22 Oct CE target, 23 Oct PE target)
and the Nifty 23 Oct PE target (09:30 signal bar). The filter is not
purely protective — it is also the frequency killer.

### V4 — spot signals (options outcome NOT computed)

| Track | Trades (spot signals) | Days traded / 4 | Spot targets | Spot points |
|---|---|---|---|---|
| V4 Nifty | 1 (23 Oct, setup2 PE) | 1 | 1 | +114.30 |
| V4 Bank | 2 (21 Oct, 23 Oct, setup2 PE) | 2 | 2 | +443.40 |

These are the **same spot signals as (lA) this week** (overlap, not
deduped, not pooled). Identified strikes (ATM, not expiry day): Nifty
23 Oct 22500 PE (lot 65), Bank 21 Oct 55200 PE (lot 30), Bank 23 Oct
54400 PE (lot 30). Under the V4 options rule the trade would carry stop
−50 / target +90 **option points** with a book-20-before-overhead exit —
**none of that is scored here**, because no premium series was available
(§1). A V4-options verdict for this week is therefore **not computable**,
and claiming one from spot points would be bluff.

### Volrix — 0 trades, by design, not by failure to run

Trigger check, previous-day close % (spot daily, cache):

| Entry day | Nifty prev-day % | Bank prev-day % | Trigger (≤ −2%)? |
|---|---|---|---|
| 19 Oct (prev 16 Oct) | +0.65% | +0.06% | No / No |
| 21 Oct (prev 19 Oct) | −1.11% | −0.64% | No / No |
| 22 Oct (prev 21 Oct) | −0.34% | −0.92% | No / No |
| 23 Oct (prev 22 Oct) | −0.54% | −0.09% | No / No |

Cooldown does not block anything (last Volrix entry in the old list was
9 Jul 2026, far beyond the 10-session cooldown). The trigger simply
never fires. Volrix's own history is ~30 entries in ~7 years (~4/year);
**it cannot meet a 1/day or 5/week bar by construction**. Its correct
role is an occasional large-rebound overlay — when it fires, it is an
extra trade that week, never counted toward the daily versions' 1/day.

## 4. Verdict vs the bar (1 per trading day, decent hits)

| Version / track | Trades / 4 days | 1/day? | Decent hits? | Verdict |
|---|---|---|---|---|
| (lA) Nifty | 1 | No | Yes (1/1 target) | Misses frequency; hits clean |
| (lA) Bank | 2 | No | Yes (2/2 targets) | Misses frequency; hits clean |
| Skill Nifty (raw) | 3 | No (3/4) | No (1/3 targets, net negative) | Closest on frequency, fails hits + net |
| Skill Bank (raw) | 3 | No (3/4) | Yes (2/3 targets) | Closest on frequency, hits decent |
| Skill (capped variant) | 0 | No | — | Filters kill the week entirely |
| V4 options | 3 spot signals | No | **Not computable** (no premiums) | No verdict possible on options P&L |
| Volrix | 0 | No — by design | — | Cannot be a daily version |

**No version meets 5/week in this week, and no version could** — the
week has 4 trading days. The honest pilot-week finding is narrower:
(lA) hits are clean but rare (1–2 days); raw Skill is frequent (3/4
days) but Nifty-negative; V4 options is unscored for want of premiums;
Volrix is not a daily system at all.

## 5. Failing / no-setup days diagnosed first (before any tweak)

- **19 Oct, both indices, all versions:** Nifty fell −1.11% but its
  below-PDL close came only at 13:15, after the (lA) 11:30 rescan window;
  Bank never closed below its OR low (day low = OR low 55,331.10 exactly),
  so there was no Bank confirmation for Nifty (lA) and no Bank breakdown
  for V4/Skill. No raw Skill signal either. Diagnosis: late, unconfirmed
  breakdown — not a missed signal, a genuinely unconfirmed day.
- **21 Oct, Nifty (lA):** Nifty first closed below OR low at 10:05 and
  below PDL only at 11:35 — **5 minutes after the 11:30 rescan cutoff**,
  with Bank confirmation present (Bank below OR low 09:55). A 5-minute
  window miss, not a level miss. (Bank (lA)/V4 fired the same day.)
- **22 Oct, both indices, (lA)/V4:** neither index ever closed below its
  OR low (Nifty OR low 22,557.95 = near day low 22,554.85, price recovered
  inside the range; Bank OR low 54,459.35 = day low, price recovered).
  Gap-down reclaim days, not breakdown days. Raw Skill CE signals fired
  (Nifty stop, Bank target) — the only version with a 22 Oct trade.
- **23 Oct:** all versions fired (overlap day). No diagnosis needed.

## 6. Next tuning family per version that missed — proposed, NOT run

Tuning does not stop (standing requirement 2026-10-30), but nothing here
is re-tuned on this week and re-claimed:

- **(lA) — family L1, rescan-window extension (frozen proposal):** extend
  the rescan cutoff from 11:30 to 13:30 for days where the confirming
  index broke before 11:30 (the 21 Oct Nifty case: confirmer 09:55, rescan
  11:35). All else unchanged (OR width, room, stop/target, re-entry).
  Judge on Jan–Oct per track: does L1 add more winning days than losing
  days, and does it preserve the pilot week's 3/3 targets? If it adds
  losers faster than winners, discard it — do not keep widening.
- **Skill — family S1, 09:30-bar + bias re-check (frozen proposal):**
  allow the 09:30 signal bar (currently excluded by the capped variant)
  for PE only when the signal close is below PDL, and keep the bias
  block on CE on bearish days (it correctly blocked two Nifty CE losers
  this week). Judge on Jan–Oct: raw vs S1 vs capped, side by side, per
  track — S1 passes only if it keeps Bank's winners and Nifty's 23 Oct
  PE target without re-admitting the 21/22 Oct CE stops.
- **V4 options — family P0, premium route first (no signal tweak yet):**
  resolve the premium-data blocker before any V4 tuning: (a) why direct
  script-token API calls return 403 while browser-fetch returned 200, and
  (b) whether expired-instruments candles via the browser-fetch route
  (the Option-B exchange pattern) can supply weekly/monthly option
  candles for 21/23 Oct. Until premiums exist, V4 options tuning is
  blind and is not attempted.
- **Volrix — no daily tuning family:** it stays a separate overlay.
  Next step for Volrix is not frequency tuning but the full-October
  trigger scan (did any ≥2% down day occur in October at all, and would
  its 5-session hold have paid in premium?) — reported separately, never
  merged into (lA)/Skill/V4 totals.

## 7. Proceeds to full October? — yes, with conditions

- **(lA), Skill (raw + capped side by side), V4 spot signals:** proceed
  to the full October run (1–28 Oct, 18 days), per version per index
  separately, with L1 and S1 as frozen proposals to be scored there
  (not on this week alone). The full-October bar is the real 5/week test
  (18 days ≈ 3.6 weeks).
- **V4 options P&L and Volrix premium P&L:** do NOT proceed to a full
  October P&L claim until the premium route (P0) is resolved. Their full
  October output, until then, is spot-trigger signals + trigger scan
  only, labelled as such.
- **Nothing is adopted on this pilot week alone.** Adoption requires
  full October, then November 2026 paper (from Mon 2026-11-02, separate
  Nifty/Bank logs, no re-tuning during November).

## 8. Files

- This report: `index_options_pilot_week_oct19_23.md`
- Trade CSV (spot-trigger rows; premium columns NOT_AVAILABLE):
  `index_options_pilot_week_oct19_23_trades.csv`
- Sources: cache `data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv` +
  `spot_daily.csv`; `october_2026_la_and_skill_nifty_bank.md` + its trade
  CSV (reproduced exactly for (lA) trades); `DOCUMENTED_V5_LA_BANKNIFTY.md`;
  Volrix options reports (`volrix_nifty_large_down_rebound_options_backtest.md`,
  `volrix_banknifty_large_down_rebound_backtest.md` §options translation);
  NSE holiday calendar for 20 Oct Dussehra (search, 2026-10-30).
