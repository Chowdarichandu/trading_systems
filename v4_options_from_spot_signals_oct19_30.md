# V4 options, computed from V4 spot signals — Oct 19–23 pilot week + Oct 26–29 this week

Paper only. No orders. No live trading. **Options only for index** — no futures
trade, no futures total anywhere in this report.

## 0. What the user clarified (2026-10-30 07:29 IST), and what this report does

1. **Volrix futures entry = options entry.** If Volrix gives a futures entry
   (previous-day underlying close down ≥2%, next session 09:16, 5-session
   hold, 10-session cooldown), use **the same entry for options** — buy the
   underlying's ATM CALL option instead of the futures contract. That is the
   already-frozen Volrix options translation (LONG ATM CALL, monthly expiry 0,
   1 lot, no stop/target). It is confirmed here, not re-invented, and no
   spot-proxy futures total is presented as an options result.
2. **V4 for options: use V4 spot signals to compute options outcomes** —
   because, per the user, we have options data. And "or else let's try this
   week data which you have" — so this report does **not** wait for a perfect
   premium route. It uses the data already available first, and marks what
   it cannot fetch as NOT_COMPUTED instead of converting spot points into
   option points.
3. **Skill + (lA) are already good per the user** — they are NOT re-tuned
   here. Their spot signals are reported alongside V4 options for comparison
   only, separately, never pooled.

## 1. Method — read this before the numbers

- **Spot signals** are taken from the cache
  (`~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv` +
  `spot_daily.csv`, ends 2026-10-28), the pilot-week report
  (`index_options_pilot_week_oct19_23.md` + its trade CSV, reproduced
  exactly for pilot-week signals), the October (lA)+Skill report, and for
  Bank Nifty 29 Oct the intraday file
  (`~/workspace/goals/3-blue-line-bank-nifty-backtest/hidden_files/oct29_spot_5m.csv`,
  75 bars). Nifty 29 Oct has **daily OHLC only** (open 22690.65, high 22961.95,
  low 22656.75, close 22936.75, public close data) — no 5-minute bars — so
  its V4/Skill/(lA) signals are **undetermined**, not assumed.
- **Strike:** ATM = nearest 100 to entry spot. Lot sizes from the contracts
  themselves: Nifty 65, Bank Nifty 30. Expiry: next monthly expiry
  **Tue 27 Oct 2026** for trades on/before 27 Oct; for the 28 Oct Nifty trade
  the next weekly expiry **Tue 3 Nov 2026** (live option chain, see §5).
  None of 21/23/26 Oct is a monthly-expiry day, so the 100-point-ITM
  expiry-day rule does not apply to those trades.
- **Entry premium:** open of the first 5-minute option candle **after** the
  spot signal time (matching the spot entry = next open). **Stop = entry −50
  option points, target = entry +90 option points**, checked bar by bar
  (high ≥ target or low ≤ stop) on the option's own 5-minute candles.
  If neither is hit, square-off at the **15:10 close** (the square-off time
  used throughout the other backtests). Net per 1 lot =
  (exit premium − entry premium) × lot − **₹220 assumed cost** (labelled
  assumption, not actual Upstox charges).
- **Book-20 rule, honestly limited:** the original rule also says "book 20
  points before the overhead line". That line is a **spot** level, and there
  is no premium equivalent without a delta for that contract on that day,
  so it is **not** applied in the premium walk. The pure −50/+90 result
  below may therefore hold longer than the original rule would have on a
  day where spot approached an overhead line. This is stated, not hidden.
- **What is NOT done:** spot points are never converted into option points.
  A spot target hit does not mean an option target hit (see Nifty 23 Oct,
  §3 — the clearest example in this report).

## 2. P0 section — did browser-fetch supply option candles? YES, for the 27-Oct expiry + Nov-03 Nifty

- **Direct script-token API calls returned 403** in the pilot week (that was
  the P0 blocker). **Browser-fetch through the localhost CONNECT forwarder
  (127.0.0.1:8899, in `auto_token_refresh.py`) returned 200** — the same
  Option-B pattern that succeeded for token exchange at 07:06 IST on
  2026-10-30. Profile check via browser-fetch: HTTP 200.
- **Expired-instruments route (works):** `GET /v2/expired-instruments/option/contract`
  for expiry 2026-10-27 returned 322 Bank Nifty contracts and 288 Nifty
  contracts, and `GET /v2/expired-instruments/historical-candle/{key}/5minute/{day}/{day}`
  returned **77 five-minute candles per contract-day** for all five
  27-Oct-expiry targets below. Fetch script (no credentials in it):
  `v4_options_browser_fetch.py`; raw JSON in
  `v4_options_oct_data/` (contracts + candles).
- **Live chain route (works for Nifty, not for Bank):** `GET /v2/option/chain`
  for Nifty expiry 2026-11-03 returned a full chain, giving Nifty 22500 PE
  (Nov-03) for the 28 Oct trade, whose 5-minute candles were then fetched
  via `GET /v3/historical-candle/{key}/minutes/5/2026-10-28/2026-10-28`
  (77 candles, HTTP 200).
- **Remaining block, Bank post-27-Oct contracts:** the Bank option chain
  returned **0 rows for every expiry scanned** (2, 6, 12, 13, 19, 20, 24, 26,
  27, 30 Nov 2026), although the same endpoint returns a full Nifty chain.
  The Bank 29 Oct contract key therefore could not be located via this
  route, and the expired route does not apply (a 29 Oct trade's expiry is
  in the future at that date). That one row is NOT_COMPUTED (§4), with this
  reason — not guessed, not filled from spot.
- **Token store note:** all fetches used the **script token store**
  (`~/workspace/trading/upstox_refresh/.env`, live 2026-10-30 07:06 IST).
  The Muse connector is separate and still 401 — it was not used and is
  not claimed to work. No credential, token, auth code, or login URL is
  recorded in this report or its CSV.

## 3. V4 options — computed results (6 trades with real premiums)

| Date | Index | Setup | Dir | Strike / expiry | Lot | Entry premium (time) | Stop / target | Exit | Net per 1 lot |
|---|---|---|---|---|---|---|---|---|---|
| 21 Oct | BANKNIFTY | setup2 OR breakdown | PE | 55200 PE / 27 Oct | 30 | 379.95 (11:20) | 329.95 / 469.95 | **target 11:35** @ 469.95 | **+₹2,480.00** |
| 23 Oct | BANKNIFTY | setup2 OR breakdown | PE | 54400 PE / 27 Oct | 30 | 321.55 (10:00) | 271.55 / 411.55 | **target 10:05** @ 411.55 | **+₹2,480.00** |
| 23 Oct | NIFTY | setup2 OR breakdown | PE | 22500 PE / 27 Oct | 65 | 125.85 (10:10) | 75.85 / 215.85 | square-off 15:10 @ 108.70 | **−₹1,334.75** |
| 26 Oct | NIFTY | setup4 reclaim | CE | 22600 CE / 27 Oct | 65 | 197.55 (10:00) | 147.55 / 287.55 | **stop 11:05** @ 147.55 | **−₹3,470.00** |
| 26 Oct | BANKNIFTY | setup3 bounce rejection | PE | 54300 PE / 27 Oct | 30 | 275.15 (10:20) | 225.15 / 365.15 | **target 10:35** @ 365.15 | **+₹2,480.00** |
| 28 Oct | NIFTY | setup2 OR breakdown | PE | 22500 PE / 3 Nov | 65 | 200.95 (10:20) | 150.95 / 290.95 | **stop 11:00** @ 150.95 | **−₹3,470.00** |

- **Totals, computed trades only (6): 3 targets, 2 stops, 1 square-off,
  net −₹834.75 per 1 lot (separate tracks, not a portfolio — Nifty and
  Bank are never pooled).**
- **Pilot week subset (21 + 23 Oct, 3 trades): 2 targets, 1 square-off,
  net +₹3,625.25.**
- **This-week subset (26 + 28 Oct, 3 trades): 1 target, 2 stops,
  net −₹4,460.00.**
- Entry spot for reference (spot trigger only, never the P&L): Bank 21 Oct
  55,249.15; Bank 23 Oct 54,444.05; Nifty 23 Oct 22,526.25; Nifty 26 Oct
  22,635.70; Bank 26 Oct 54,275.20; Nifty 28 Oct 22,519.95.

### The lesson in these six rows — spot ≠ options

**Nifty 23 Oct is the proof.** On spot, that signal was a target
(+114.30 spot points, exit 10:35). On premium, the 22500 PE opened at
125.85, never reached the +90 target (215.85; highest premium after entry
was 182.00), never hit the −50 stop either (lowest 78.00 vs stop 75.85 —
2.15 points away), and squared off at 15:10 at 108.70 for **−₹1,334.75**.
Reporting the spot target as an options profit would have been bluff on that
one trade (spot provisional +₹11,390 per 100 shares vs options −₹1,334.75
per 1 lot — different units, which is exactly why the units must never be
mixed).

The other five rows agree with their spot direction (Bank targets hit
fast on premium too — 11:35, 10:05, 10:35 — while both Nifty stops hit on
premium at 11:05 and 11:00), but agreement on five rows does not make spot
a proxy for premium. The Nifty 23 Oct row is why V4 options must be scored
on premiums, as done here.

## 4. NOT_COMPUTED rows — stated, not filled

| Date | Index | Setup | Reason |
|---|---|---|---|
| 29 Oct | BANKNIFTY | setup2 OR breakout CE (spot signal 09:35, entry spot 09:40 open 54,416.10, ATM strike 54400 CE) | Bank option chain returned 0 rows for all 10 expiries scanned (§2); contract key not locatable via browser-fetch chain route; expired route does not apply (expiry future at 29 Oct). Premium outcome NOT_COMPUTED. **Note:** this signal was NOT in the 29 Oct paper playbook (which covered Setup 3/Setup 4 only) — it is a generic V4 setup2 signal from the 29 Oct intraday file, reported here for completeness, not as a playbook trade. |
| 29 Oct | NIFTY | V4 / Skill / (lA) — undetermined | No Nifty 5-minute data for 29 Oct (daily OHLC only, §1). No signal is assumed. |
| 27 Oct | Both | — | No V4 spot signal in cache for either index (27 Oct was monthly-expiry day; both indices no-trade on the V4 spot engine). |
| 19, 22 Oct | Both | — | No V4 spot signal in cache/pilot week for either index. |
| 26–28 Oct | BANKNIFTY 27/28 Oct | — | No V4 spot signal in cache (Bank 27 Oct bullish bias no-trade; Bank 28 Oct bearish bias no-trade). |

## 5. Volrix options entry check — same entry as futures, 0 trades in both weeks

**Rule confirmed (user clarification 2026-10-30 07:29 IST):** Volrix futures
entry = options entry. Trigger = previous-day underlying close down ≥2%;
entry = next session 09:16; instrument = underlying's ATM CALL option
(monthly expiry 0 in the frozen translation, 1 lot, no stop/target,
5-session hold, 10-session cooldown). No spot-proxy futures total is used.

**Trigger scan — previous-day close %:**

| Entry day | Nifty prev-day % | Bank prev-day % | Trigger ≤ −2%? |
|---|---|---|---|
| 19 Oct | +0.65% | +0.06% | No / No |
| 21 Oct | −1.11% | −0.64% | No / No |
| 22 Oct | −0.34% | −0.92% | No / No |
| 23 Oct | −0.54% | −0.09% | No / No |
| 26 Oct | −0.39% | −1.16% | No / No |
| 27 Oct | +0.68% | +0.15% | No / No |
| 28 Oct | −0.02% | −0.72% | No / No |
| 29 Oct | −0.22% | +0.54% | No / No |

**Result: 0 Volrix options trades in either week, by design, not by failure
to run.** Cooldown blocks nothing (last Volrix entry in the old list was
9 Jul 2026). Volrix's history is ~30 entries in ~7 years (~4/year) — it
cannot meet a 1/day or 5/week bar by construction, and it is not counted
toward the daily versions' bar. Its correct role remains an occasional
rebound overlay: when it fires, an extra trade that week, scored on
premium at that time, never merged into (lA)/Skill/V4 totals.

## 6. Skill + (lA) alongside — comparison only, NOT re-tuned, never pooled

**Pilot week (from the pilot-week report, spot-trigger only, premium NOT
computed for these rows):**
- (lA) Nifty: 1 trade (23 Oct PE target, +114.30 spot pts).
  (lA) Bank: 2 trades (21 + 23 Oct PE targets, +443.40 spot pts).
- Skill raw Nifty: 3 trades (21 Oct CE stop, 22 Oct CE stop, 23 Oct PE
  target, −18.45 spot pts). Skill raw Bank: 3 trades (21 Oct CE stop,
  22 Oct CE target, 23 Oct PE target, +372.15 spot pts).
- Capped Skill variant: 0 trades this week (filters out all 6 raw signals).

**This week (spot signals, from cache + Bank 29 Oct intraday file):**
- (lA): no (lA) PE trade on 26, 27, or 28 Oct for either index; Bank 29 Oct
  has no (lA) PE rescan trade (price rose all day); Nifty 29 Oct
  undetermined (no 5-minute data).
- Skill: 26 Oct both indices 0; 27 Oct both 0; 28 Oct Skill Nifty PE stop
  (−54.30 spot pts, same spot signal as the V4 28 Oct trade, provisional
  cash −₹5,470 per 100 shares — NOT an options result), Skill Bank 0;
  29 Oct Skill Bank raw OR breakout CE spot signal 09:35 (entry spot
  09:40 open 54,416.10; spot cash target would be 54,534.00, hit 10:10 on
  spot — reported as a **spot signal only**, premium NOT computed, same
  Bank-chain reason as §4).
- **Comparison, plainly:** V4 options (6 computed trades, net −₹834.75)
  is the only version in this report scored on real premiums. (lA) and
  Skill spot signals look cleaner on spot (especially (lA) Bank, 2/2
  targets in the pilot week), but their options outcomes are **not**
  computed here — and Nifty 23 Oct shows why their spot targets must not
  be read as options profits.

## 7. Verdict — nothing adopted on these two weeks alone

- V4 options, computed on premiums: **6 trades, 3 targets / 2 stops /
  1 square-off, net −₹834.75 per 1 lot** (pilot week +₹3,625.25, this
  week −₹4,460.00). It does **not** meet the 5/week = 1/day bar in either
  week (3 V4 spot signals in each 4-day / 3-day window, and only 6
  premium-computed trades across 8 days) and it is net negative across
  the two weeks together, despite a positive pilot week.
- Volrix options: 0 trades — not a daily version, overlay only.
- Skill + (lA): already good per the user on spot signals, but their
  options P&L is not established by this report.
- **Next steps, in order:** (1) resolve the Bank option-chain gap (§2) so
  the 29 Oct Bank CE row can be computed instead of left NOT_COMPUTED;
  (2) run V4 options on premiums for the **full October** (1–28 Oct, 18
  days) using this same browser-fetch route — that is the real 5/week
  test; (3) November 2026 paper (from Mon 2026-11-02, separate Nifty/Bank
  logs, no re-tuning during November) before any adoption claim.
  **Nothing in this report is adopted.**

## 8. Files

- This report: `v4_options_from_spot_signals_oct19_30.md`
- Trade CSV: `v4_options_from_spot_signals_oct19_30_trades.csv`
- Fetch script: `v4_options_browser_fetch.py`
- Raw option data: `v4_options_oct_data/` (contracts + candles JSON)
- Sources: cache `data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv` +
  `spot_daily.csv`; `index_options_pilot_week_oct19_23.md` + CSV;
  `october_2026_la_and_skill_nifty_bank.md`; Bank 29 Oct intraday
  `oct29_spot_5m.csv`; Nifty 29 Oct daily OHLC (public close data);
  Upstox expired-instruments + live option-chain + historical-candle APIs
  via browser-fetch (script token store only, Muse connector not used).
