# Stocks EQUITY — November 2026 PAPER spec — N4-DEEP V3 (combined event-reaction)

**FROZEN 2026-10-30, before November begins. Paper only, no orders.
Real money: ₹0. NO re-tuning during November — any change to trigger,
entry, exit, or event rules voids the month as a validation.**

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Every rupee figure: provisional per 100 shares,
₹40/trade flat cost.**

## What is being paper-traded, and why this variant

The paper system is **V3 — combined event-reaction momentum**, the
winning variant of the round-5 in-sample deepening
(`stocks_equity_n4deep.md`, spec `stocks_equity_n4deep_frozen.md`):

- V3 at the declared primary exit **T125** (target +1.25% /
  stop −0.5%): 56 trades Jan–Oct 2026, net **+₹7,990.43 provisional
  per 100 shares**, expectancy +₹142.69, with **both halves
  positive** — Jan–May +₹5,155.13 (34 trades) and Jun–Oct +₹2,835.30
  (22 trades) provisional per 100 shares. It was the highest
  Jan–Oct T125 net among the variants that graduated under the
  frozen round-5 rule, and it is also both-halves positive at the
  secondary exit T10 (+₹7,837.42 / +₹746.10 provisional per
  100 shares).
- It beat base N4 at T125 (+₹2,924.79; halves +₹2,727.65 / +₹197.14)
  and V1b (≥1.5% trigger; +₹3,228.65; second half +₹17.32, flat).
- **Honest caveats, part of this spec:** the whole record is
  in-sample; V3's October 2026 slice was NEGATIVE (6 trades,
  −₹530.69 provisional per 100 shares); 52 of its 56 trades are
  results reactions and only 4 are single-news reactions; and a
  labelled diagnostic in round 5 showed the LONG side net-negative
  at T125 (21 trades, −₹973.83) against SHORT +₹8,964.26 — no
  direction filter is applied (that would be hindsight fitting);
  November paper trades BOTH directions exactly as specified.

## The rule — exact

1. **Event set.** Reaction days arising from either:
   - **Results** events (quarterly/half-yearly results), or
   - **Single-news** events: management/CEO change, large order,
     FDA approval, block deal, sector policy, pricing action, or
     corporate action. Dividend declarations on their own are
     mechanical and are NOT single-news events (a results event
     that also declares a dividend is still a results event).
2. **Event source.** The November watchlist
   (`stock_event_watchlist_nov2026.md`) PLUS a **daily
   exchange-filing check** (BSE/NSE announcements for all 25
   stocks) each morning before the open. Events for the nine
   stocks with no confirmed November date at freeze time
   (HDFCBANK, TVSMOTOR, UNITDSPR, OBEROIRLTY, INDUSTOWER, WIPRO,
   HINDCOPPER, ASTRAL, HINDUNILVR) and any single-news event are
   added ONLY through that daily filing check — adding a genuinely
   announced event is applying the rule, not re-tuning it.
3. **Reaction day.** The first trading day on which the outcome is
   known before the open: announcement filed after market hours or
   on a non-trading day → reaction day = next trading day;
   announcement filed before the open on a trading day → reaction
   day = that day; announcement filed intraday → reaction day =
   next trading day (the 09:30 trigger cannot be applied to a move
   already underway).
4. **Trigger.** On the reaction day, move by 09:30 =
   (close of the 09:25 five-minute bar ÷ previous daily close − 1)
   × 100. If **|move| ≥ 1.0%**, the trade direction is the sign of
   the move (trade WITH the reaction). Below 1.0%: no trade.
5. **Entry.** Close of the 09:30 five-minute bar, recorded as entry
   time 09:35. Quantity basis 100 shares.
6. **Exit — primary T125.** Target = entry × (1 ± 1.25%), stop =
   entry × (1 ∓ 0.5%) (+ for LONG, mirrored for SHORT). Exit scan
   starts on the bar after the entry bar; on any bar the **stop is
   checked before the target**; if neither level is touched, exit
   at the close of the 15:10 bar.
7. **Shadow exit — T10.** Every taken trade is ALSO scored at
   target +1.0% / stop −0.5% (same entry, same scan rules) and the
   shadow net is logged in its own column. Shadow results never
   change the primary verdict.
8. **Frequency.** Max **1 trade per stock per event**. Otherwise
   **ALL** qualifying event-reaction trades are taken — there is
   **no portfolio cap** (the user's rule: the minimum-2-valuable/day
   standard is a floor, not a cap). Multiple stocks reacting on the
   same day all trade.

## Known November event map at freeze time (from the watchlist)

Reaction days in parentheses; the daily filing check governs if a
date moves.

- NTPC — results Sat 2026-10-31 → reaction **Mon 2026-11-02**
- ITC — results Mon 2026-11-02 → reaction 2026-11-03 if after-market
- NATIONALUM — results Mon 2026-11-02 (plus interim dividend) →
  reaction 2026-11-03 if after-market
- NHPC — results Wed 2026-11-04 → reaction 2026-11-05 if after-market
- GLENMARK — results Thu 2026-11-05 → reaction 2026-11-06 if after-market
- PFC — results Thu 2026-11-05 → reaction 2026-11-06 if after-market
- HINDALCO — results Fri 2026-11-06 → reaction **Mon 2026-11-09**
- TATASTEEL — results Sat 2026-11-07 → reaction **Mon 2026-11-09**
- KALYANKJIL — results Tue 2026-11-10 → reaction 2026-11-11 if after-market
- OIL — results Thu 2026-11-12 → reaction 2026-11-13 if after-market
- BDL — results Sat 2026-11-14 → reaction **Mon 2026-11-16**
- IRCTC — results 2026-11-17 / 2026-11-18 (two-day range at freeze
  time) → reaction = next trading day after the actual announcement

Late-October reporters (GODREJCP, HINDZINC, RECLTD, VEDL) have no
November reaction day under this rule — only a NEW announcement
found in the daily filing check creates one.

## Logging

One row per taken trade in `stocks_n4_november_paper_log.csv`,
filled the same day after 15:10, plus one row per reaction day
where the trigger did NOT fire (|move| < 1.0%) with exit fields
blank and exit_reason `no_trigger` — so the month's event count is
auditable, not just its trades. No-trade rows carry net 0 and are
excluded from trade statistics. November has no re-tuning, no
skipped trades, and no retroactive edits: a missed trade is logged
as a note in `notes`, not backfilled silently.

## Month-end verdict rule (frozen)

Judged on the primary exit T125, on **net + win rate + trade count
together**, never on net alone:

- Net (provisional per 100 shares) positive AND win rate ≥ 40% AND
  at least 5 taken trades = a positive November.
- **A positive November does NOT adopt this system on its own.**
  V3's Jan–Oct record is in-sample and its halves, while both
  positive at T125, come with a negative October slice and a
  56-trade base; adoption requires the November result to be
  consistent with that record AND a further fresh window — the
  month-end verdict is "continue / stop", not "adopt".
- A negative November, or fewer than 5 taken trades, means the
  event-reaction question is answered negatively or left
  unanswered respectively — reported as such, not re-tuned away.
