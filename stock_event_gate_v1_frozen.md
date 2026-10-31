# Event Gate v1 — FROZEN, 2026-10-30, NOT SCORED, NOT ADOPTED

Paper only. Cash intraday stocks only. This gate is a FILTER on an
existing S7/S8 price setup. It never creates a trade by itself.
It was frozen on 2026-10-30 BEFORE any November scoring, and it
must not be re-tuned on Jan–Oct 2026 and then claimed as a pass.
Validation window: November 2026 paper, from Mon 2026-11-02,
separate from the Nifty log, no re-tuning during November.

## Definitions (fixed)
- Event window, per stock, per event: from the 7th trading day
  before the announcement date through the 7th trading day
  after the reaction date, inclusive (trading days, not
  calendar days). Reaction date = first trading day after an
  after-market announcement; for a daytime announcement, the
  announcement day itself if it is a trading day, else the
  next trading day.
- Phases on a trade day: pre_announcement (window start ..
  announcement day − 1, outcome NOT yet known, date only
  scheduled), announcement_day, reaction_or_post (reaction
  date .. window end, outcome known before the open on the
  reaction day for after-market announcements).
- Known-before-open: results announced after market are
  known before the open ONLY from the reaction day onward,
  never on the announcement day itself. Scheduled board dates
  are known in advance, but the outcome is not — pre-window
  trades are never treated as "news trades".

## Gate rules (exact)
1. A price setup (S7 rules: setups 2/3/4, second-close,
   structural/retest-hold stop, give-back exit) must exist
   first. No setup = no trade, event or not. No forcing.
2. Post-reaction event day (reaction .. +7 trading days):
   keep S7 thresholds unchanged — room ≥ 1.5× risk,
   prospective full-target net ≥ ₹500 (per 100 shares,
   provisional — NOT a lot profit).
3. No-event day: STRONGER confirmation required — room
   ≥ 2.0× risk OR prospective full-target net ≥ ₹1,000
   (per 100 shares, provisional). Rationale: Jan–Oct S7
   losses cluster on no-event days (20 of 25 net ≤ 0
   trades), so the gate raises the bar where there is no
   driver, rather than inventing trades on event days.
4. Single-stock news day (CEO/management change, large
   order/contract, FDA approval, block deal, sector policy):
   room ≥ 2.0× risk, regardless of phase, because these
   days gap and reverse; S7 has only 2 such in-window
   trades, both pre-announcement, so there is NO evidence
   that reaction days on these events are safer.
5. Pre-announcement window: NEUTRAL. No priority, no
   block, thresholds as in rule 2. The S7 pre-phase
   outperformance (+₹2,090 on 8 trades) is NOT used as a
   reason to favour pre-window trades: S2 pre-phase was
   only +₹197 on 9 trades, and the outcome is unknown
   before the announcement.
6. 1/day cap ranking (tie-break only, never creates a
   trade): post-reaction event trade > pre-announcement
   trade > no-event trade; within a tier, S7 ranking
   (target net → room → setup rank).
7. Logging (November, daily after 15:10): for every
   candidate, log stock, date, setup, event_status,
   nearest event type/date/phase, gate tier, taken /
   blocked / deprioritised, and the shadow outcome of
   blocked trades. A gate is only judged on November
   paper + shadow outcomes together.

## What this gate does NOT do
- It does not block no-event trading outright (that would
  remove 37 of 51 S7 trades and destroy the already-low
  frequency).
- It does not claim events explain S7's edge: S2
  contradicts S7 on event-window net, and event windows
  do not raise candidate frequency (see event layer v1).
- It is not adopted, and no November log is created
  for it until the parent confirms the November paper
  track (S8/S9 base + this gate).
