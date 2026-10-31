# S9 — Intraday STOCK system (cash, NOT options) — FROZEN 2026-10-30, BEFORE SCORING

**Status: FROZEN 2026-10-30, NOT adopted, NOT a live system. Paper only, no orders.**
**Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks, 203 trading days, plus
the week of 26–29 Oct 2026 scored separately (see § Week slice).**
Any Jan–Oct 2026 run of S9 is **in-sample context only**. If S9 passes ALL
legs in-sample, its real test is November 2026 paper starting Mon
2026-11-02, logged daily after 15:10 in `s9_forward_paper_log.csv`,
separate from the Nifty log, with no re-tuning during November.
Adoption only on net + win rate + frequency together on unseen paper.
If S9 fails any leg in-sample, it is NOT re-tuned on the same window
and re-claimed, and no adoption-track November log is created.
This spec was written BEFORE the S9 scoring run on 2026-10-30.
The scoring result is in `s9_result_oct30.md`; it does not change this spec.

## Gate mode frozen — ONE mode, chosen before scoring

**Mode: G-TIERED — S8 price design + Event Gate v1 tiered thresholds.**
This is the mode specified in `stock_event_gate_v1_frozen.md` (frozen
2026-10-30, before S9 scoring) and in the S9 task. It is NOT the draft's
E-ONLY mode (event-window only) and NOT its E-BLOCK mode (event-window
blocked). No E-ONLY / E-BLOCK run was scored for S9, and no mode was
picked by comparing S8 outcomes. The draft's open parameter is closed
by the delivered gate doc, not by peeking at S8 trades: G-TIERED keeps
the S8 price setup as the only trade source and only raises the bar
where the gate doc says the bar should be raised.

## Base design — S8 exactly, unchanged

S8 exactly, as in `new_stock_system_s8_frozen.md`: CE pullback arming on
ANY reclaim close above OR high (regardless of day open vs PDC),
pullback + second-close entry, stop = pullback low, room ≥ 1.5×,
target +2× risk; PE path as in S6/S7/S8 (find_signal PE, second close,
retest-hold stop = max(signal high, confirmation high), room ≥ 1.5×
below, target −2× risk); OR width 0.25–3.0%, stock bias filter, Nifty
bias-only confirmation, prospective full-target net ≥ ₹500 (per 100
shares, provisional — NOT a lot profit), give-back exit (50 shares at
1× risk, rest trailed to breakeven, target stays 2× risk, square-off
15:10, bar order stop, then partial, then target), 100 shares,
₹40/trade, 15:10 square-off, short paper-only, one candidate per
stock-day (earliest entry, tie → higher prospective target net).
No direct reclaim CE, no setup2 CE breakout, no timing gates, no
room < 1.5×, no re-entry, no second trade of the same stock on the
same day. Setup2 remains absent by construction (see S8 report);
S9 does not introduce a new setup2-PE room definition.

## Event gate — exact rules (Gate v1, frozen)

Source calendar: `stock_event_calendar_jan_oct_2026.csv` (115 events:
100 results, 3 management_change, 3 dividend, 3 fda_approval,
2 large_order, 1 sector_policy, 1 pricing, 1 block_deal,
1 corporate_action). The gate is a FILTER on an S8 candidate. It never
creates a trade. Price setup first: no S8 candidate = no trade, event
or not. No forcing.

### Window and phase (per stock, per event)

- Window: from the 7th trading day before the announcement date
  through the 7th trading day after the reaction date, inclusive
  (trading days, not calendar days). Reaction date = first trading
  day after an after-market announcement; for a daytime announcement,
  the announcement day itself if it is a trading day, else the next
  trading day.
- Phases on a trade day D, for an in-window event:
  - `pre_announcement`: window start ≤ D < event_date (outcome not
    yet known; scheduled date only).
  - `announcement_day`: D = event_date. Outcome is NOT known before
    the open on this day for after-market announcements, and is not
    known before the open for daytime announcements either. It is
    therefore NEVER treated as post-reaction.
  - `reaction_or_post`: reaction_date ≤ D ≤ window end (outcome
    known before the open on the reaction day for after-market
    announcements).
- Trading-day list for window reconstruction: the NIFTY daily dates
  in the cache (`~/workspace/trading/data/progressive/`).

### Missing calendar fields — frozen handling (no invention, no peeking)

- If `window_start` is blank, reconstruct it as the 7th trading day
  before the event_date on the trading-day list. If `window_end` is
  blank, reconstruct it as the 7th trading day after the reaction
  date (for the 10 October events this runs past the 28 Oct cache
  end; that does not affect scoring up to 28 Oct, because every
  D ≤ 28 Oct with D ≥ reaction_date is then in-window).
- If `reaction_date` is blank (one event: UNITDSPR results
  2026-10-28, after_market unverified), treat reaction_date =
  event_date, so 2026-10-28 is `announcement_day`, not post-reaction.
- A candidate is in-window for an event iff window_start ≤ D ≤
  window_end under the values above (given, or reconstructed).

### Single-stock news — frozen type list

Single-stock news = exactly these event types: `management_change`,
`large_order`, `fda_approval`, `block_deal`, `sector_policy`.
`dividend`, `pricing`, and `corporate_action` are calendar events but
are NOT in this list: they are treated as ordinary in-window events
(phase decides their tier), never as single-news, and never as
no-event. Results are ordinary in-window events, not single-news.

### Tier, threshold, and priority — frozen (applied to the UNCAPPED pool)

Priority when a stock-day is in-window for several events (highest
applicable tier wins):

1. **single_news** — any in-window single-news event, regardless of
   phase: keep ONLY if room ≥ 2.0× risk. Prospective target net does
   NOT substitute for room here. Rationale (gate doc): these days gap
   and reverse; there is no evidence reaction days on these events
   are safer.
2. **post_reaction** — any in-window event in `reaction_or_post`
   phase (and no single-news event): S8 thresholds unchanged —
   room ≥ 1.5× risk and prospective ≥ ₹500 (already satisfied by
   every S8 candidate, so the gate passes it).
3. **pre_announcement** — any in-window event in `pre_announcement`
   or `announcement_day` phase (and no single-news / post-reaction
   event): NEUTRAL — S8 thresholds unchanged (room ≥ 1.5×,
   prospective ≥ ₹500). Pre-phase outperformance in S7 is NOT used
   to favour these trades, because the outcome is unknown before
   the announcement and S2 contradicts S7 on pre-phase net.
4. **no_event** — no in-window event for that stock-day: STRONGER
   confirmation required — room ≥ 2.0× risk OR prospective
   full-target net ≥ ₹1,000 (per 100 shares, provisional).
   A no-event candidate failing BOTH (room < 2.0× AND prospective
   < ₹1,000) is gate-blocked.

Nearest event recorded for a taken trade: the in-window event that
determined its tier (single-news first, then post-reaction, then
pre/announcement); within that tier, the event with the smallest
|D − event_date|, tie → earliest event_date. For no-event trades,
nearest event fields are blank.

### Cap — gate ranking applied AFTER filtering, not before

Gate-filter the uncapped S8 pool first, then cap-select the survivors:
max 1 valuable stock trade per trading day across all 25 stocks,
max 1 trade per stock per week retained. Ranking (gate doc, with the
one extension the gate doc leaves silent — single-news rank — frozen
here): tier rank post_reaction (4) > single_news (3) >
pre_announcement (2, announcement_day counted in this tier) >
no_event (1); within a tier, S8 ranking (prospective target net DESC,
then room ratio DESC, then setup rank DESC, then date, then symbol).
Cap is a ceiling, NOT a quota: a day with no gate-passing candidate
trades nothing. Capping S8 first and then filtering would waste days
and is NOT what S9 does.

## Week slice — 26–29 Oct 2026, scored separately

The week slice is scored with the IDENTICAL S8 price design + G-TIERED
gate, restricted to dates 2026-10-26 … 2026-10-29, cap 1/day and
1/stock/week within that slice, reported separately and NEVER pooled
into the Jan–Oct total. Data limit, frozen in advance: only the cache
in `~/workspace/trading/data/progressive/` is used, no live token wait.
If a date in 26–29 Oct has no cache data, it is reported as missing
data, not as a zero-trade day by design and not filled from any other
source. (At freeze time the cache is known to end 2026-10-28; the
week-slice result must state exactly which of 26–29 Oct were in cache.)

## What S9 deliberately does NOT do

- No re-tuning of S8's price filters, room, stop, target, exit, OR
  filter, bias, or Nifty confirmation on the Jan–Oct window.
- No E-ONLY / E-BLOCK comparison, no choosing the better-looking mode
  after scoring.
- No new setup2-PE room definition. That remains the family AFTER S9.
- No pooling of index totals into stock totals. Nifty is a bias
  filter only. All rupee totals are per 100 shares, provisional —
  NOT a lot profit.

## Engine and outputs

`stock_system_s9.py` (S8 candidate functions imported unchanged +
gate tagging + gate-filter + gate-ranked cap; `run_s9` for Jan–Oct,
`run_s9_week` for 26–29 Oct). Trade CSV:
`s9_trades_jan_oct_2026.csv`, uncapped gate-passing
`s9_uncapped_jan_oct_2026.csv` (gate survivors before cap; the S8
uncapped pool is `s8_uncapped_jan_oct_2026.csv`), week trades
`s9_trades_oct26_29_2026.csv`, month JSON
`data/progressive/s9_summary_2026-jan-oct.json`, report
`s9_result_oct30.md`. Forward log template (only if S9 passes ALL
legs in-sample): `s9_forward_paper_log.csv` (header only).
