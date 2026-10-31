# Stock Event Layer v1 — intraday stocks are NOT random entry/exit

Paper only, no orders, cash intraday stocks only, no options.
Index totals are never pooled with stock totals. Rupees are
ONLY "per 100 shares, provisional — NOT a lot profit"
(100 shares was never the user's lot rule; it is a cash
translation unit, labelled every time here).

Standing requirement (user, 2026-10-30): until ready for
paper trading for the next one month, tuning does NOT stop
— intraday stocks and intraday options both keep being
tuned — and stock entries must be explained by real events
(results, CEO/management changes, major news, corporate
actions), not by random signals alone.

## 1. Event calendar — what was built, and what it is NOT

Files:
- [stock_event_calendar_jan_oct_2026.csv](sandbox://workspace/trading/stock_event_calendar_jan_oct_2026.csv)
  — 115 events: 100 results + 15 curated non-results.
- Frozen gate (not scored): [stock_event_gate_v1_frozen.md](sandbox://workspace/trading/stock_event_gate_v1_frozen.md)
- Tagged trades: `s7_event_tagged.csv`, `s2_event_tagged.csv`
  (in ~/workspace/trading/).

### Results layer — complete for the 25 stocks
Taken unchanged from `results_dates_v1.csv` (100 rows =
25 stocks × 4 announced quarters, verified from
Moneycontrol / Financial Express board-meeting lists,
TipRanks, ET/press, company sources, with source + URL
per row). No date was invented, none was silently
replaced. After-market flag is yes/unverified only where
a source gave a timestamp; otherwise unverified, not
inferred. Reaction day = next trading day after an
after-market announcement (user's rule: most results are
after market, reaction day is the next trading day).

### Non-results layer — curated, NOT exhaustive (honest limit)
15 events found by public search on 2026-10-30, each with
a source + URL in the calendar:
- Large orders: BDL 2026-09-23 MoD SAT-SAAW ₹810.79cr;
  BDL 2026-10-15 Navy heavyweight torpedoes ~₹1,307cr.
- Management: WIPRO 2026-04-01 AI-Native unit +
  leadership reshuffle; WIPRO 2026-05-03 Americas-2 CEO
  exit; TATASTEEL 2026-08-27 CIO change announced
  (effective 2026-11-01).
- Dividends (ex-dates): HDFCBANK 2026-06-19 ₹13;
  ITC 2026-02-04 ₹6.50 interim, 2026-05-27 ₹8 final.
- Sector policy: ITC 2026-02-01 cigarette GST 40% +
  additional excise (weighted tax +28–30%).
- Pricing: ITC 2026-09-23 Gold Flake Premium hike ~8%.
- Block deal: ITC 2026-10-08 GQG ~₹9,395cr sale.
- FDA: GLENMARK 2026-03-04 inhaler, 2026-07-21
  Ryaltris children, 2026-08-20 nasal spray.
- Corporate action: TVSMOTOR 2026-10-28 consumer
  finance demerger approval (same day as Q2 results).

What is missing: a full Reg-30 filing sweep for all
25 stocks was NOT done in this pass. Any CEO change,
order, or dividend not listed above is "not in this
calendar", not "did not happen". November paper must
log events from exchange filings daily, or the gate
will silently miss drivers. Sector news (e.g. metals,
power, banking policy) is only represented where it
touches a named stock above.

### Reconciliation — results_dates_v1.csv vs results_dates.csv
The earlier clubbed agent's `results_dates.csv` has only
5 rows (4 verified + 1 unverified): ITC Q1 FY27
2026-07-31, ITC Q2 FY27 2026-11-02 (scheduled, future —
correctly NOT an announced result), HDFCBANK Q4 FY26
2026-04-18, WIPRO Q4 FY26 2026-04-16, TATASTEEL Q4 FY26
2026-05-15. All four verified dates MATCH
`results_dates_v1.csv` exactly (ITC 2026-07-31,
HDFCBANK 2026-04-18, WIPRO 2026-04-16, TATASTEEL
2026-05-15). The discrepancy is coverage, not conflict:
the clubbed file was a 4-date sample, v1 is the full
100-date calendar. Do NOT use the 5-row file as a gate.
The 6 PENDING stocks from v1 (HINDUNILVR, INDUSTOWER,
RECLTD, TVSMOTOR, UNITDSPR, VEDL — Q2 FY27 events
26–28 Oct 2026 with no complete 5-day post window in
data to 2026-10-28) complete in early November 2026.

### Window definition (fixed, used for all tagging below)
Per stock, per event: 7th trading day before the
announcement date through the 7th trading day after
the reaction date, inclusive. This is the user's
"week before and week after" rule, in trading days.
Known-before-open: for after-market results, only from
the reaction day onward; on pre-announcement days the
scheduled date is known but the outcome is not.

## 2. Test — do events explain S7's trades?

Window: Jan–Oct 2026 (Oct 1–28), 203 trading days,
5,075 stock-days. Event windows cover 1,250 stock-days
(24.6%). Tagged files: `s7_event_tagged.csv`,
`s2_event_tagged.csv`.

### S7 capped (51 trades, +₹722.50 provisional)

| Bucket | Trades | Win net>0 | Full-target | Net ₹ | Expectancy ₹ |
|---|---|---|---|---|---|
| In event window | 14 | 64.3% (9) | 35.7% (5) | +₹2,235.00 | +₹159.64 |
| No event | 37 | 45.9% (17) | 16.2% (6) | −₹1,512.50 | −₹40.88 |
| **Total** | **51** | **51.0% (26)** | **21.6% (11)** | **+₹722.50** | **+₹14.17** |

Phases (in-window only): pre-announcement 8 trades,
75.0% win, +₹2,090.00; reaction_or_post 6 trades,
50.0% win, +₹145.00. By nearest event type: results
12 trades, 58.3% win, +₹1,585.00; FDA 1 trade +₹545;
large order 1 trade +₹105.
Losses: in-window 5, no-event 20 — S7's losses DO
cluster on no-news days, but that is also where most
trades are (37/51).
In-window S7 trades (for checking): TVSMOTOR 15 Jul
+₹1,550 target (results 21 Jul, pre), OBEROIRLTY
22 Jan +₹1,370 target (results 19 Jan, post),
GLENMARK 26 May +₹605 target (results 29 May, pre),
GLENMARK 17 Aug +₹545 target (FDA 20 Aug, pre),
HINDALCO 4 Feb +₹515 target (results 11 Feb, pre),
BDL 16 Sep +₹105 partial-BE (order 23 Sep, pre).

### S2 capped, for comparison (61 trades, −₹785.98 provisional)

| Bucket | Trades | Win net>0 | Full-target | Net ₹ |
|---|---|---|---|---|
| In event window | 15 | 53.3% (8) | 20.0% (3) | −₹951.40 |
| No event | 46 | 60.9% (28) | 19.6% (9) | +₹165.42 |

S2 CONTRADICTS S7: event-window trades lose, no-event
trades are (barely) positive. An event edge that flips
sign between two price systems on the same window is
not a proven edge — it is, at best, a hypothesis with
14–15 trades per bucket.

### Frequency — events do NOT create more setups
- Uncapped candidates per 100 stock-days: in-window
  1.44 (18/1,250), out-of-window 1.52 (58/3,825) —
  essentially identical. Expected in-window capped
  trades if random: 12.6; actual: 14.
- Calendar days: 191 of 203 trading days have at
  least one of the 25 stocks in an event window, so
  "today is an event day" at portfolio level is
  meaningless. The gate must be per-stock, never
  per-day.
- S7's 150 no-setup days are not explained by "no
  news": most of those days some stock was in a
  window, but that stock had no passing price setup.
  Events do not fix candidate scarcity by themselves.

### Verdict on the user's question
Events do NOT explain the moves cleanly in-sample.
What the data supports, narrowly, is:
(a) S7 trades taken inside a stock's event window
performed better than S7 trades outside one, driven
by pre-announcement trades (outcome unknown at
trade time — so this cannot be read as "trade the
news"); (b) S2 shows the opposite sign, so (a) is
not system-independent; (c) events do not raise
candidate frequency at all. Claiming "events drive
the edge" on this evidence would be bluff. The
honest use of events is as a gate that raises the
bar on no-driver days (where S7's losses sit) and
demands stronger room on gap-prone single-stock
news days — which is exactly what the frozen gate
does, without claiming an event edge.

## 3. Frozen event gate — for S8/S9, NOT scored here

Full text: [stock_event_gate_v1_frozen.md](sandbox://workspace/trading/stock_event_gate_v1_frozen.md).
Summary (frozen 2026-10-30, before any scoring):
1. Price setup first (S7 rules). No setup = no trade.
2. Post-reaction event day: S7 thresholds unchanged
   (room ≥1.5×, prospective ≥₹500 provisional).
3. No-event day: stronger confirmation — room ≥2.0×
   OR prospective ≥₹1,000 provisional.
4. Single-stock news day (CEO change, large order,
   FDA, block deal, sector policy): room ≥2.0×,
   any phase.
5. Pre-announcement window: neutral — no priority,
   no block (S7 pre-phase gain is not used to favour
   pre-window trades).
6. 1/day cap ranking (tie-break only): post-reaction
   > pre-announcement > no-event.
7. November logging: every candidate tagged with
   event status/type/date/phase, gate tier, taken /
   blocked / deprioritised, plus shadow outcome of
   blocked trades. Judged on November paper + shadow
   outcomes together, never on Jan–Oct re-scoring.

Nothing here is adopted. November 2026 paper
(from Mon 2026-11-02) is the validation window,
separate from the Nifty log, with no re-tuning
during November.

## 4. November event watchlist (scheduled / completing)
- Completing early Nov: the 6 PENDING Q2 FY27 post
  windows — HINDUNILVR, INDUSTOWER, RECLTD,
  TVSMOTOR, UNITDSPR, VEDL (announced 26–28 Oct).
- Scheduled (from v1 §1, excluded from v1 as not yet
  announced at 2026-10-29): GODREJCP 2026-10-29,
  NTPC 2026-10-31, ITC + NATIONALUM 2026-11-02,
  NHPC 2026-11-04, GLENMARK + PFC 2026-11-05,
  HINDALCO 2026-11-06, TATASTEEL 2026-11-07
  (rescheduled), KALYANKJIL 2026-11-10, OIL
  2026-11-11, BDL 2026-11-14, IRCTC 2026-11-17/18.
  HINDUNILVR/HINDCOPPER Q2 FY27 dates disputed —
  verify from filings before tagging, do not assume.
- Daily November task: check exchange filings for
  each of the 25 stocks for CEO/management changes,
  orders, FDA/regulatory, dividends/splits/bonus, and
  block deals, and append them to the calendar the
  same day — otherwise the gate runs on a stale
  calendar and the "no-event" tier is mislabelled.
