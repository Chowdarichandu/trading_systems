# S9 — S8 price design + Event Gate v1 (G-TIERED) — result, 2026-10-30

**Paper only, no orders, cash intraday only, no options. S9 is NOT adopted.**
Frozen spec (written before scoring): `new_stock_system_s9_frozen.md`.
Engine: `stock_system_s9.py`. Trades: `s9_trades_jan_oct_2026.csv`
(50 trades), gate survivors before cap `s9_uncapped_jan_oct_2026.csv`
(69), gate-blocked `s9_gate_blocked_jan_oct_2026.csv` (12),
month JSON `data/progressive/s9_summary_2026-jan-oct.json`.
Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks,
203 trading days, 5,075 stock-days. All Jan–Oct figures are
**in-sample context only**. All rupee totals are **per 100 shares,
provisional — NOT a lot profit** (100 shares was a provisional
cash-translation unit, never the user's lot rule). Index totals were
never pooled into stock totals; Nifty was a bias filter only.
Gate mode was frozen before scoring as **G-TIERED** (the tiered
thresholds in `stock_event_gate_v1_frozen.md`); no E-ONLY / E-BLOCK
run was scored, and no S8 price filter was re-tuned.

## Verdict — plain

**S9 FAILS the user bar overall, so S9 is NOT adopted and no
adoption-track November log is created. No re-tuning on this window
and no re-claim follows.**

| Leg | Verdict |
|---|---|
| (a) Net positive in-sample | **PASS** — +₹1,640.00, expectancy +₹32.80/trade |
| (b) 1 valuable stock trade/day, no forcing | **FAIL** — 0.246/day, 50 traded days vs 147 no-S8-candidate days + 5 gate-blocked-all days + 1 capped-out day = 203 |
| (c) Full-target rate above S2's 19.7% | **PASS** — 26.0% (13/50) |
| (d) Cumulative rising month by month | **FAIL** — Jan +₹2,375 → Jun −₹1,050 (negative May–Jun) → Sep +₹2,160 → Oct +₹1,640 |
| (e) No forcing | **PASS** — nothing was forced; 153 of 203 days traded nothing |

The gate improves S8 on net (+₹1,640.00 vs S8 +₹932.50, +₹707.50)
and on full-target rate (26.0% vs 22.2%), but it does NOT fix the
binding failure: frequency. It trades FEWER days than S8 (50 vs 54)
and its cumulative still falls for five straight months before
recovering. A better in-sample net on 50 trades is not adoption.

## Results — Jan–Oct 2026, capped

| Series | Trades | Win net>0 | Full-target | Net ₹ | Expectancy | /day | /week |
|---|---|---|---|---|---|---|---|
| **S9** | **50** | **50.0% (25)** | **26.0% (13)** | **+₹1,640.00** | **+₹32.80** | **0.246** | **1.14** |
| S8 | 54 | 50.0% (27) | 22.2% (12) | +₹932.50 | +₹17.27 | 0.27 | 1.23 |
| S7 | 51 | 51.0% (26) | 21.6% (11) | +₹722.50 | +₹14.17 | 0.25 | 1.16 |
| S2 (bar for full-target rate) | 61 | 59.0% | 19.7% (12) | −₹785.98 | −₹12.88 | 0.30 | 1.39 |

Win net>0 (25) and full-target (13) are reported separately, as
required: the other 12 net-positive trades are partial-BE wins
(`stop_after_partial_BE`), never counted as targets. Exits (capped):
24 stops, 12 stops-after-partial-BE, 13 targets-after-partial,
1 square-off. The 25 non-wins are the 24 stops plus the square-off.

### Direction / setup split (capped)

- **PE: 41 trades, +₹825.00, 51.2% net>0, 26.8% full targets (11),
  expectancy +₹20.12.** All 41 are setup3 bounce rejection.
- **CE: 9 trades, +₹815.00, 44.4% net>0, 22.2% full targets (2),
  expectancy +₹90.56.** All 9 are setup4 pullback.
- **Setup2: 0.** Unchanged from S8 — S9 introduces no new
  setup2-PE room definition, so setup2 remains absent by
  construction (see S8 report diagnosis).
- CE fell from S8's +₹1,960.00 to +₹815.00 even though the CE trade
  count is the same (9): gate tier ranking displaced BDL's CE trade
  on 2026-05-05 (+₹710.00, no-event) in favour of INDUSTOWER's CE
  trade the same day (−₹435.00, post-reaction). Tier ranking is a
  cost as well as a filter — stated honestly, not hidden.

### Funnel

Scanned 5,075 stock-days → OR pass 4,859 → CE armed 215 →
CE pullback 138 → CE second-close 56 → S8 uncapped candidates 81 →
**gate survivors 69 → gate-blocked 12 → capped 50** (19 gate
survivors capped out). Frequency is still candidate scarcity, not
the cap alone: only 1 day lost to the cap after gating, but 147
days had no S8 candidate at all.

### Gate effect — what the gate actually did

Gate applied to the uncapped S8 pool (81 trades, uncapped net
−₹922.50 — the cap, not the gate, is what makes any of these
versions positive):

| Tier (uncapped) | n | Uncapped net ₹ | Capped n | Capped net ₹ |
|---|---|---|---|---|
| no_event (46 pass, 12 blocked) | 58 | −₹2,172.50 | 30 | −₹885.00 |
| post_reaction | 8 | +₹1,050.00 | 8 | +₹1,050.00 |
| pre_announcement | 12 | −₹635.00 | 9 | +₹640.00 |
| single_news | 3 | +₹835.00 | 3 | +₹835.00 |

- **Blocked (12, all no-event, all PE setup3): net −₹1,802.50
  shadow, 5 net-positive, 1 full target.** Blocking them removed
  net losers on balance, including 7 stops — but it also removed
  a +₹650.00 target (OBEROIRLTY 2026-10-06) and a +₹217.50
  partial-BE win (GODREJCP 2026-10-06). The gate is not a pure
  loser filter.
- **No-event capped trades still lose money: 30 trades,
  −₹885.00.** The stronger no-event bar (room ≥ 2.0× OR
  prospective ≥ ₹1,000) did not make the surviving no-event leg
  profitable; it only shrank it.
- **Post-reaction capped: 8 trades, +₹1,050.00, but only 3 wins
  and 2 full targets** — driven by two January targets (BDL
  2026-01-09 +₹1,955.00, OBEROIRLTY 2026-01-22 +₹1,370.00) against
  5 losers. Small-sample, January-heavy; not a demonstrated edge.
- **Pre-announcement capped: 9 trades, +₹640.00, 5 wins, 3 full
  targets.** Neutral treatment kept these; no claim is made that
  pre-window trading is safer (S2 contradicts S7 on this).
- **Single-news capped: 3 trades, +₹835.00, 3 net-positive,
  1 full target** — GLENMARK FDA-approval pre-window trades
  (2026-08-11 +₹185.00 partial-BE, 2026-08-17 +₹545.00 target)
  and BDL large-order pre-window (2026-09-16 +₹105.00
  partial-BE). All three are PRE-announcement, none is a
  reaction-day trade, and two of the three wins are partial-BE
  wins, not targets. The single-news rule (room ≥ 2.0× any phase)
  was never tested on a reaction day in this window.
- **Announcement_day branch: never triggered** — no S8 uncapped
  candidate fell on an announcement day. That frozen branch is
  untested in-sample.
- **Reconciliation S8 → S9:** S8 capped +₹932.50; gate-blocked 7
  S8 capped trades (net −₹1,447.50 among the dropped set's
  components — see trade CSVs); tier ranking displaced 2 more S8
  capped trades (BDL CE 2026-05-05 +₹710.00, HINDUNILVR
  2026-01-16 +₹185.00); 5 new trades entered under gate ranking
  (+₹155.00 net). Net change +₹707.50 = +₹155.00 − (−₹552.50
  dropped total). Capped-out gate survivors (19) net −₹760.00
  shadow; gate survivors uncapped net +₹880.00 = capped
  +₹1,640.00 + capped-out −₹760.00.

### Days

- Trading days: 203. Days traded: 50. Days with an S8 candidate:
  56. Days with a gate-passing candidate: 51. Days with a
  candidate but capped out: 1. **Days with no S8 candidate: 147.
  Days where every candidate was gate-blocked: 5.** 147 + 5 + 1
  + 50 = 203. No day was forced.

### Month-by-month cumulative (capped)

| Month | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|
| Jan | 5 | +₹2,375.00 | +₹2,375.00 |
| Feb | 6 | −₹520.00 | +₹1,855.00 |
| Mar | 5 | −₹645.00 | +₹1,210.00 |
| Apr | 6 | −₹785.00 | +₹425.00 |
| May | 5 | −₹535.00 | −₹110.00 |
| Jun | 5 | −₹940.00 | −₹1,050.00 |
| Jul | 4 | +₹1,815.00 | +₹765.00 |
| Aug | 10 | +₹1,035.00 | +₹1,800.00 |
| Sep | 3 | +₹360.00 | +₹2,160.00 |
| Oct (1–28) | 1 | −₹520.00 | +₹1,640.00 |

Ex-March total +₹2,285.00; ex-October total +₹2,160.00. Neither
exclusion changes the verdict: cumulative falls Jan→Jun, goes
negative, recovers Jul→Sep, and falls again in October. It does
NOT rise month by month. October's single capped trade is ASTRAL
2026-10-12, a stop at −₹520.00 (no-event, room 2.875×, so it
passed the gate and still stopped out); S8's other October capped
trade (GODREJCP 2026-10-06, +₹217.50) was gate-blocked, and no S8
candidate exists after 2026-10-12 in this window at all.

### Per-stock (capped, non-zero only)

GLENMARK 7 trades +₹1,545.00 (3 targets); HINDALCO 2 +₹955.00
(2 targets); ASTRAL 8 +₹720.00 (3 targets); OBEROIRLTY 5
+₹660.00 (2 targets); TVSMOTOR 9 +₹590.00 (2 targets); BDL 6
+₹575.00 (1 target); GODREJCP 1 +₹200.00 (partial-BE win);
HINDUNILVR 2 −₹230.00; HINDZINC 1 −₹345.00; HDFCBANK 1
−₹315.00; INDUSTOWER 1 −₹435.00; HINDCOPPER 2 −₹685.00;
UNITDSPR 5 −₹1,595.00 (worst, 0 targets).
Zero-trade stocks (12): IRCTC, ITC, KALYANKJIL, NATIONALUM,
NHPC, NTPC, OIL, PFC, RECLTD, TATASTEEL, VEDL, WIPRO.

## Week slice — 26–29 Oct 2026, separately, NOT pooled

Identical S8 price design + G-TIERED gate, cap 1/day and
1/stock/week within the slice, cache only, no live token wait:

- **Trading days in cache: 3 — 2026-10-26, 2026-10-27,
  2026-10-28. 2026-10-29 has NO cache data** (cache ends
  2026-10-28) and is reported as missing data, not as a
  zero-trade day and not filled from any other source.
- S8 uncapped candidates 26–28 Oct: **0**. Gate survivors: 0.
  Gate-blocked: 0. Capped S9 trades: **0**. Net ₹0.00 on 0 trades
  is an empty slice, not a result.
- This is consistent with the Jan–Oct pool: the last S8 candidate
  in October is 2026-10-12; 13–28 Oct produced no S8 candidate
  for any of the 25 stocks, so the gate had nothing to filter
  that week. Week files `s9_trades_oct26_29_2026.csv` /
  `s9_uncapped_oct26_29_2026.csv` are header-only for that reason.

## Caveats (do not over-read S9)

- In-sample only, 50 capped trades. The net improvement over S8
  (+₹707.50) is smaller than the two January post-reaction
  targets that carry the post leg, and the no-event leg that the
  gate was meant to fix is still negative when capped.
- Calendar gaps were handled only by the frozen reconstruction
  rule in the spec (blank window_start = 7th trading day before
  the event; blank window_end = 7th trading day after reaction,
  open-ended past the cache; blank reaction for UNITDSPR
  2026-10-28 = event date). No calendar field was edited to
  change an outcome.
- `dividend`, `pricing`, and `corporate_action` events were
  treated as ordinary in-window events (phase tier), not as
  single-news and not as no-event, per the frozen type list.
  No capped S9 trade depended on that choice changing its tier
  to single-news (the three single-news capped trades are
  fda_approval / large_order, as listed above).

## Next step (standing requirement: tuning does NOT stop)

S9 fails frequency and cumulative progression, so tuning continues
family by family. The family after S9, per the S8 report, is a new
setup2-PE room definition (structural level below PDL), frozen as
its own version — not a re-tune of S9 on this window. No
`s9_forward_paper_log.csv` was created, deliberately.
