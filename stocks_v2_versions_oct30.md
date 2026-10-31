# Stocks v2 versions — NO-NEWS days only, 2026-10-30

Paper only. Cash intraday only, 25 stocks, no options, no orders.
All ₹ figures are **per 100 shares, provisional, NOT a lot profit**
(₹40/trade cost, 100 shares/trade, square-off 15:10 throughout).
Window: **2026-01-01 to 2026-10-28** (203 trading days), from the
progressive cache only — no new fetches. **2026-10-29 is NOT in the
cache, so no 29 Oct trade is claimed anywhere below** (see §6).

## Verdict first — plain

**NO version meets all legs** (1/day, net positive, full-target
> 19.7%, month cumulative rising, no forcing), on no-event days,
individually or combined.

**Closest is (lA) v2, 1/day-capped**: smallest loss (−₹22,093),
best expectancy (−₹126/trade), full-target 24.0% (passes the
19.7% leg), 0.86 trades/day with 28 no-trade days (not forced).
It still **fails net-positive and fails cumulative-rising**
(Jan +₹100, then down to −₹22,093 by October; only April and
October months are green). It is the closest, not a pass, and
nothing here is adopted.

## 1. Frozen definitions (stated before scoring, not re-tuned)

- **V5-stock**: pool of V4-baseline trades + Skill-v2 OR-only trades
  from the same tuning engine (`daytrader_cash_tuning.find_signal`,
  ratio 2, stop scale 1, room 0.0036, bias on for V4). Dedup same
  symbol+date: setup rank wins (setup4=3 > setup3=2 > setup2=1 >
  skill_or=0), then higher prospective full-target net, then
  earlier signal. Filter: prospective full-target net ≥ ₹500.
- **Skill v2 — frozen variant: "Skill-v2 OR-only"** from
  `daytrader_tuning_v5_v2_results.md`: first 5-min close beyond the
  stock OR (09:15–09:30 bars) after 09:30 up to 11:30, no bias, no
  room, no PD check. Entry next bar open, stop = signal-bar
  extreme, target 2× risk, stop-before-target per bar, 15:10
  square-off. Note: this variant passed the Jul–Sep capped check
  in that doc but was **NOT adopted** there (October context
  −₹4,588, cap doing the work). It is frozen here as specified.
- **(lA) v2-stock** (adapted from `DOCUMENTED_V5_LA_BANKNIFTY.md`
  (lA)): Nifty confirms the stock (instead of Bank Nifty
  confirming Nifty); both directions (not PE-only). Morning
  candidate = earliest pooled V4/Skill-v2 signal with signal time
  ≥ Nifty's first OR-break time, ≤ 11:30, same direction as
  Nifty's break. Entry next bar open, stop = signal-bar extreme,
  target 2× risk, stop-before-target, 15:10 square-off.
  Re-entry (max 1/stock-day, only if the morning trade stops):
  rescan after the stop bar, same direction, risk band adapted to
  **relative [0.5×, 1.0×] morning risk** (the original index-point
  band [10, rescan risk] does not scale to rupee stocks);
  morning-phase fails are skipped, first afternoon (>11:30)
  band-fail **ends** the scan (stop-on-first-fail, to 15:05).
- **Volrix v2-stock** (adapted to cash intraday, exit **frozen**):
  trigger = previous trading day's close ≤ −2% vs the day before.
  Next session, **long only, entry 09:15 open, exit 15:10
  square-off, no intraday stop/target**. This exit was frozen
  before scoring and not optimised after seeing results. By
  construction its full-target rate is 0% — that leg cannot pass
  for this version as defined.
- **NO-EVENT day** (per `stock_event_gate_v1_frozen.md` window):
  a stock-day outside **every** event window for that stock, where
  a window = 7th trading day before the event date through the
  7th trading day after the effective reaction date, inclusive.
  Effective reaction = reaction_date if within event_date..
  event_date+7 calendar days, else the event date (this drops the
  2026-01-01 placeholders on 2025 events). All calendar rows
  count (results, large orders, FDA, management, dividends,
  policy, pricing, block deals, corporate actions). Volrix is
  filtered on its **entry** day only; its trigger day may itself
  be an event day.
- **1/day cap** (frozen, no outcome look-ahead): per trading day,
  rank by prospective full-target net desc, setup rank desc,
  signal time asc; top 1. Volrix has no target: in its own cap it
  ranks by |previous-day drop| desc (known at open); in the
  combined ranking it sorts last. Combined = pool all four
  versions' no-event trades, dedup same symbol+date (highest
  prospective wins, Volrix last), then 1/day.
- **Full-target win** = exit_reason = target. **Net>0 win** =
  net_rs > 0 (includes square-off winners). Full-target and
  net>0 are reported separately everywhere below.
- Inputs (all days, before event filter): V4-baseline 938 trades,
  Skill-v2 3,985 trades. Script:
  [stocks_v2_versions_oct30.py](sandbox://workspace/trading/stocks_v2_versions_oct30.py)
  (a first run excluded 0 trades due to a date-type mismatch in
  the window builder; fixed before scoring — exclusion counts
  below are from the corrected run).

## 2. Headline: no-event, 1/day-capped (the task's legs)

203 trading days. Net ₹ per 100 shares, provisional.

| Version | Trades | /day | Net ₹ | Expect. | Net>0 | Full-target | Verdict on legs |
|---|---|---|---|---|---|---|---|
| V5-stock | 202 | 0.995 | −32,850 | −162.62 | 63 (31.2%) | 48 (23.8%) ✓ | Net ✗, cumul. ✗ |
| Skill v2 (OR-only) | 203 | 1.000 | −45,835 | −225.79 | 61 (30.0%) | 47 (23.2%) ✓ | Net ✗, cumul. ✗ |
| (lA) v2 | 175 | 0.862 | −22,093 | −126.25 | 53 (30.3%) | 42 (24.0%) ✓ | Net ✗, cumul. ✗ — **closest** |
| Volrix v2 | 134 | 0.660 | −40,783 | −304.35 | 57 (42.5%) | 0 (0.0%) ✗ | Net ✗, target ✗ by construction, cumul. ✗ |
| **Combined (deduped, 1/day)** | 203 | 1.000 | −45,210 | −222.71 | 62 (30.5%) | 46 (22.7%) ✓ | Net ✗, cumul. ✗ |

1/day is satisfied by construction for the capped series. On
forcing: (lA) v2 has 28 days with no trade and Volrix v2 has 69
days with no trade (genuine no-signal days); V5, Skill v2 and
Combined trade on essentially every day because at least one
no-event signal exists every day — that is signal presence, not
a forced trade, but it is not "1 valuable trade on selected
days" either.

## 3. Uncapped no-event reference (same filter, no 1/day cap)

| Version | Trades | /day | Net ₹ | Expect. | Net>0 | Full-target |
|---|---|---|---|---|---|---|
| V5-stock | 1,116 | 5.498 | −81,166 | −72.73 | 380 (34.1%) | 316 (28.3%) |
| Skill v2 | 2,930 | 14.433 | −190,180 | −64.91 | 952 (32.5%) | 890 (30.4%) |
| (lA) v2 | 1,547 | 7.621 | −71,752 | −46.38 | 489 (31.6%) | 469 (30.3%) |
| Volrix v2 | 501 | 2.468 | −30,411 | −60.70 | 237 (47.3%) | 0 (0.0%) |
| Combined (deduped, uncapped) | 3,053 | 15.039 | −196,687 | −64.42 | 1,002 (32.8%) | 898 (29.4%) |

The cap improves expectancy for V5/Skill/(lA) but every capped
series is still deeply negative — the cap is selecting, not
creating, edge, and the 1/day ranking (prospective net) does not
turn any version green.

## 4. Event-day exclusions (all-days uncapped → no-event uncapped)

| Version | All-days trades | Excluded as event-window | No-event trades |
|---|---|---|---|
| V5-stock | 1,566 | 450 | 1,116 |
| Skill v2 | 3,985 | 1,055 | 2,930 |
| (lA) v2 | 2,112 | 565 | 1,547 |
| Volrix v2 | 656 | 155 | 501 |

The filter removes 24–29% of trades per version, yet no version
flips sign: no-event trading is not better than all-days trading
here (e.g. V5 all-days −₹109,640 → no-event −₹81,166 on fewer
trades; expectancy slightly worse, −₹70.01 → −₹72.73).

## 5. Month cumulative, no-event 1/day-capped (₹ per 100 shares)

Cumulative must rise month by month to pass. **None does.**

| Month | V5 cumul. | Skill v2 cumul. | (lA) v2 cumul. | Volrix v2 cumul. | Combined cumul. |
|---|---|---|---|---|---|
| Jan | +7,970 | +6,980 | +100 | −4,844 | +10,420 |
| Feb | −2,890 | −4,060 | −4,455 | −17,916 | −820 |
| Mar | −7,610 | −13,260 | −5,505 | −37,303 | −10,140 |
| Apr | −5,945 | −9,315 | +1,410 | −40,113 | −6,195 |
| May | −11,205 | −15,685 | −4,380 | −42,473 | −12,565 |
| Jun | −14,395 | −20,065 | −8,800 | −47,105 | −14,545 |
| Jul | −18,980 | −26,785 | −15,731 | −50,406 | −20,730 |
| Aug | −28,000 | −33,915 | −25,768 | −46,906 | −30,930 |
| Sep | −32,150 | −44,325 | −27,223 | −45,263 | −43,700 |
| Oct (1–28) | −32,850 | −45,835 | −22,093 | −40,783 | −45,210 |

Only January starts green for V5/Skill/Combined; (lA) v2's only
returns above its January level are April (+₹1,410 cumulative)
and October's partial recovery. Volrix 1/day never gets above
−₹40,783 after April despite green Aug/Sep/Oct months.

## 6. Setup split, no-event 1/day-capped

- **V5-stock**: skill_or_breakout 93 / −₹24,005; skill_or_breakdown
  83 / −₹3,300; setup3_bounce_rejection 14 / −₹5,220;
  setup4_reclaim 12 / −₹325. The V5 pool's 1/day picks are
  dominated by Skill OR signals; V4 setup4/3 legs are rare and
  roughly flat, not the driver.
- **Skill v2**: skill_or_breakout 121 / −₹36,515;
  skill_or_breakdown 82 / −₹9,320. Breakouts lose ~4× breakdowns.
- **(lA) v2**: skill_or_breakout|morning 80 / −₹19,710;
  skill_or_breakdown|morning 83 / −₹992; setup3|morning 7 / +₹520;
  setup2|morning 3 / −₹1,100; setup4|morning 2 / −₹811.
  **Re-entries: 0 survive the 1/day cap.** Uncapped, the
  re-entry leg is 303 trades / −₹8,276 / 28.1% target — it loses
  too, consistent with the (lA) doc's warning that re-entry is
  where (lA) loses money. Morning-only uncapped: 1,244 trades /
  −₹63,476 / 30.9% target.
- **Volrix v2**: volrix_rebound 134 / −₹40,783, all square-offs.
  Uncapped all-days Volrix is the only near-breakeven number in
  this work (656 trades / −₹9,711 / 49.1% net>0), but it is
  **out of scope** for the verdict: it includes event days, is
  uncapped, and has no target — and its no-event 1/day form is
  the worst expectancy of the four (−₹304/trade).
- **Combined**: skill_or_breakout 107 / −₹38,515;
  skill_or_breakdown 80 / −₹7,100; setup4_reclaim 10 / +₹1,325;
  setup3 6 / −₹920. No Volrix trade survives the combined 1/day
  ranking (Volrix sorts last by construction).

## 7. Separate check: 26–28 Oct 2026 (no-event)

Cache ends 28 Oct. **29 Oct 2026 has no data in the progressive
cache, so no 29 Oct result exists here** — a live-cache check
would be needed for the 29th, and none is claimed.

| Version | Uncapped no-event (trades / net ₹) | 1/day (trades / net ₹ / full-target) |
|---|---|---|
| V5-stock | 15 / −₹2,565 | 3 / −₹1,020 / 1 (33.3%) |
| Skill v2 | 38 / −₹5,744 | 3 / −₹4,210 / 0 |
| (lA) v2 | 17 / −₹2,067 | 3 / −₹1,355 / 0 |
| Volrix v2 | 10 / −₹291 | 3 / −₹100 / 0 (1/3 net>0) |
| Combined (deduped, 1/day) | 39 deduped / −₹6,074 | 3 / −₹4,210 / 0 |

The 3-day check agrees with Jan–Oct: everything except Volrix
uncapped is negative, and 3 days prove nothing on their own.

## 8. What this does NOT show

- No per-stock adoption: CSVs carry the symbol column for
  follow-up, but no per-stock version is claimed here — the task
  asked for versions together and individually (per version),
  and per-stock slicing of 134–203 capped trades would be noise.
- No November claim: November has not happened; nothing here is
  a forward-paper result.
- The (lA) re-entry band ([0.5×, 1.0×] morning risk) and the
  Volrix 15:10 square-off exit are adaptations frozen for this
  run, not Chandu's rules and not previously validated versions.
  In particular, (lA) v2's "closest" status rests on a morning
  leg dominated by Skill OR signals, not on re-entry edge.

## Files

- Report (this file):
  [stocks_v2_versions_oct30.md](sandbox://workspace/trading/stocks_v2_versions_oct30.md)
- Script (frozen definitions + event windows):
  [stocks_v2_versions_oct30.py](sandbox://workspace/trading/stocks_v2_versions_oct30.py)
- Summary JSON:
  [stocks_v2_versions_oct30_summary.json](sandbox://workspace/trading/stocks_v2_versions_oct30_summary.json)
- Trade CSVs (no-event), uncapped + 1/day per version:
  [stocks_v2_v5_stock_noevent_all.csv](sandbox://workspace/trading/stocks_v2_v5_stock_noevent_all.csv),
  [stocks_v2_v5_stock_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_v5_stock_noevent_1day.csv),
  [stocks_v2_skill_v2_noevent_all.csv](sandbox://workspace/trading/stocks_v2_skill_v2_noevent_all.csv),
  [stocks_v2_skill_v2_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_skill_v2_noevent_1day.csv),
  [stocks_v2_la_v2_noevent_all.csv](sandbox://workspace/trading/stocks_v2_la_v2_noevent_all.csv),
  [stocks_v2_la_v2_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_la_v2_noevent_1day.csv),
  [stocks_v2_volrix_v2_noevent_all.csv](sandbox://workspace/trading/stocks_v2_volrix_v2_noevent_all.csv),
  [stocks_v2_volrix_v2_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_volrix_v2_noevent_1day.csv),
  [stocks_v2_combined_noevent_deduped.csv](sandbox://workspace/trading/stocks_v2_combined_noevent_deduped.csv),
  [stocks_v2_combined_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_combined_noevent_1day.csv)
- Oct 26–28 check CSVs + V4-input reference:
  [stocks_v2_combined_oct26_28_noevent_1day.csv](sandbox://workspace/trading/stocks_v2_combined_oct26_28_noevent_1day.csv),
  [stocks_v2_v4input_noevent_all.csv](sandbox://workspace/trading/stocks_v2_v4input_noevent_all.csv)
