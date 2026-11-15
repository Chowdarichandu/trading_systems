# Live intraday paper-trading loop — build note (2026-11-02)

Paper only, real money ₹0, no live orders anywhere. All live results are
labelled LIVE-SHADOW and are never mixed into the official EOD paper logs
(`november_paper_bank_log.csv` / `november_paper_nifty_log.csv` /
`stocks_sarvaritu_paper_log.csv`). The EOD log remains the official record
until live proves identical.

Data route (all books): Upstox script token from
`upstox_refresh/.env`; every api.upstox.com request sends the browser
User-Agent header (without it Cloudflare returns 403 — the 2026-11-02 fix).

---

## Bank Nifty — BNF-PAPER-V1 (U1-B2 + NS1 second legs, G0 −50/+90, lot 30)

**Machinery reused.** New producer `live_signal_producer.py` evaluates the
frozen U1 components causally on completed 5-min spot bars, importing the
original code where it exists (V4 candidate via
`daytrader_cash_backtest.find_signal`) and re-implementing the rest
line-for-line from the frozen sources: Skill V3 (`skill_tune_oct30.py`),
(lA) v2 L1 (`o1_la_l1.py`), V5 v2 (`progressive_capped_v2.py`), Volrix (b)
@ −1.0% with the 10-session cooldown, NS1 second leg
(`newsetups_score.py`). Pool assembly mirrors `u1_janoct_merge.py`; the B2
filter is Rule B (drop a merged key iff CE with representative Skill V3, or
Skill-solo with entry ≤ 09:55), verified programmatically beforehand
against all 183 Jan–Oct Bank keys with 0 mismatches. Directives go to
`live_shadow_signals.json`; `live_shadow_runner.py` consumes them, fills at
the live premium, applies G0 exits, squares off 15:10, stops 15:30.

**Control result.**
- Reference (full-day EOD construction) vs frozen files, cached days:
  Oct 23 — MERGE PE MATCH (sources (lA)+Skill, entry 09:50), B2 IN MATCH;
  Oct 26 — MERGE CE Volrix 09:20 MATCH, MERGE PE V5 10:20 MATCH, B2 both
  MATCH; Oct 28 — one merge-level extra key (Skill CE 09:50) that the
  frozen merge file does not list, but B2 drops it on BOTH sides (book
  MATCH). Book-level: 4/4 frozen book keys reproduced, 0 missing, 0 extra.
- Causal replay (bar-by-bar directive stream): Oct 23 PE emitted with
  entry bar 10:00 vs EOD 09:50 — the pre-declared Skill-early rescue-lag
  class (a Skill-solo key with entry ≤ 09:55 must be held pending under
  Rule B; it was emitted when (lA) confirmed). Oct 26 CE 09:20 and PE
  10:20 — exact. Oct 28 — 0 directives (Skill-first CE killed by Rule B),
  matching the book.
- Fri Oct 30 (API bars; no frozen artefact exists for Oct 30 — the frozen
  constructions were never run over Oct 29–30, so this is an internal
  consistency check, not a file match): EOD construction gives Skill PE
  entry 10:35, B2 IN BOOK (solo Skill, entry after 09:55), plus an NS1
  second leg CE signal 11:50, room_ratio 1.98. The causal stream emits
  exactly those two directives (BASE PE 10:35, NS1_SECOND CE 11:55).
  Consistent.

**What is live as of this report.** Producer verified → LIVE today.
Producer loop runs every ~5 min (log `live_producer_log.md`); runner
started 10:36 IST, self-terminates 15:30. Today's own Bank signal (Skill
PE, entry bar 10:20) fired before the producer existed and was logged
MISSED — not back-filled, per the emission rule; it belongs to tonight's
EOD log only. Any Bank signal from now to 15:30 (including an NS1 second
leg) will be emitted live.

**EOD-only remainder.** None for Bank signals. Premium exit tracking is
the runner's (LIVE-SHADOW); the official exit record stays the EOD log.

**Morning start.** Cron `live-loop-morning-start` (Mon–Fri ~09:08 IST,
Nov 2–30 window guard) starts the runner and the producer loop if not
already running and verifies the first evaluation per index.

---

## Nifty — NF-PAPER-C3G7 (C3 confirmed-only + G7 runner-lock50, lot 65)

**Machinery reused.** Same producer, same four U1 components (N1 filter is
a control only and is not run live). C3 emission rule: a key is emitted
when its SECOND distinct source system fires, with all sources known at
that moment; solo keys are never emitted.

**Contract selection — outcome of the expiry check (explicit, per the
follow-up).** The premise that the frozen spec uses the nearest weekly
(e.g. 2026-11-03) is NOT what the frozen record shows. The frozen
NF-PAPER-C3G7 spec mandates "the expiry in force… following the October
convention (monthly expiry of the trade month; trades after that expiry
use the next expiry in force)". October evidence is uniform: every NIFTY
premium leg Oct 5–27 used the monthly 2026-10-27, never the nearer
weeklies; only Oct 28 used weekly 2026-11-03 because the monthly had
passed. Instruments master (checked 2026-11-02): NIFTY November 2026
expiries are 2026-11-03, 2026-11-09, 2026-11-17 and 2026-11-23 (monthly);
December: 2026-12-01, 2026-12-29. BANKNIFTY November: only 2026-11-23;
December: 2026-12-29. So this week's correct Nifty contract is the
**2026-11-23 monthly**, and the runner's `monthly_expiry()` was already
right for Nov 2–23. One genuine defect was found and patched: for trades
after the monthly expiry (Nov 24–30) the old code would have picked
Dec 29 instead of the next expiry in force (Dec 1 weekly for NIFTY).
`live_shadow_runner.py` now has `expiry_in_force()` (monthly of the trade
month while in force; else the earliest expiry ≥ today) and
`monthly_expiry()` delegates to it. Mock-verified: NIFTY 2026-11-02 →
2026-11-23, 11-23 → 11-23, 11-24 → 2026-12-01, 11-30 → 2026-12-01;
BANKNIFTY 11-02 → 2026-11-23, 11-24/11-30 → 2026-12-29; compiles.

**Control result.**
- Reference vs frozen merge file: Oct 23 PE MATCH (sources (lA)+V5,
  entry 10:10, C3 IN); Oct 26 CE MATCH (Skill+V5, entry 09:55, C3 IN);
  Oct 28 PE MATCH (Skill solo, entry 10:20, C3 OUT — solo). 3/3 keys.
- Causal replay: Oct 23 PE entry bar 10:10 — exact (both legs signalled
  10:05). Oct 26 CE emitted at entry bar 10:00 vs EOD 09:55 — the
  pre-declared C3 confirmation-lag class (EOD enters a confirmed key at
  its earliest leg; live can only enter when the confirming leg fires).
  Same key, direction and sources. Oct 28 — 0 directives (solo), correct.
- Fri Oct 30 (API, internal consistency): Skill CE solo → C3 OUT; causal
  stream empty. Consistent.

**What is live as of this report.** Producer verified → LIVE today, same
runner and loop as Bank. Today: Nifty Skill V3 fired solo this morning;
no second source has confirmed, so no directive — correct C3 behaviour.
A confirming second source later today would be emitted live.

**EOD-only remainder.** None for Nifty signals. The known, measured cost
of live C3 is the confirmation lag (one bar on Oct 26); it is reported,
not hidden, and the EOD log stays official.

**Morning start.** Same `live-loop-morning-start` cron as Bank.

---

## Stocks — SarvaRitu (equity cash)

**Machinery built.** `stocks_live_shadow_producer.py` fetches Upstox v3
intraday 5-min bars for all 25 watchlist stocks (script token, browser UA),
evaluates on completed bars only, keeps its own state
(`stocks_sarvaritu_live_shadow_state.json`) and logs every run
(`stocks_sarvaritu_live_shadow_producer.log`). Live trades go to NEW
LIVE-SHADOW logs (`stocks_sarvaritu_live_shadow_log.csv` for the book,
`stocks_sarvaritu_live_shadow_scorecards_log.csv` for scorecards); the
official `stocks_sarvaritu_paper_log.csv` was never written by the live
loop. The frozen event gate is respected exactly as the EOD logger
implements it (live calendar `stocks_sarvaritu_calendar_live.csv`;
reaction returns from the stocks' own daily closes; frozen exclusions and
gates applied).

**Component classification (from the frozen spec/logger, not memory).**
- CAUSAL — LIVE: **N4-V3** (trigger knowable when the 09:30 bar completes;
  entry = 09:30-bar close, labelled 09:35; exits scanned bar-by-bar),
  **P2F**, **P2F-R2**, **R2-LOWBAND** (reaction return fixed at the
  reaction day's close; entries at R+1/R+2 09:15 open; gates use prior
  closes only).
- EOD-ONLY — OFF live, with the specific reason: **F4**, **INV-LONG**,
  **INV-ABOVE** (and the P2-INV1 scorecard) select trades by `pool_pick` —
  the day's first V4 and first skill-OR signals ranked by setup rank
  before time, over the full day. On 39 of 67 October stock-days (F4) and
  49 of 84 (INV chains) where both heads fired, the frozen pick is the
  LATER signal, so the entry cannot be known when the earlier signal
  completes. A first-signal live variant would be an invented rule. These
  stay with the 16:35 EOD logger, which remains their record; nothing of
  the book is lost, only the intraday announcement layer excludes them.

**Control result (replay vs the frozen EOD construction).**
- N4-V3: Oct 30 matched 1/1 exact (GODREJCP SHORT 09:35, net −₹686.36).
  The control caught one real bug — frozen nets use unrounded stop/target
  prices — fixed and re-verified.
- P2F: 0/0 on Oct 30 (no candidate either side); Oct 29: 4/4 exact.
- P2F-R2: Oct 30: 3/3 exact; Oct 29: 1/1 exact.
- R2-LOWBAND: 0/0 on Oct 29/30; positive instances Oct 22 (HDFCBANK
  +₹836.81) and Oct 23 (HINDZINC +₹591.25) both exact.
- F4/INV-LONG diagnostic: a causal-lock simulation happens to reproduce
  Oct 30 exactly (4/4, 1/1 — no supersession that day). They stay OFF:
  one coincident day does not cure a selection rule proven non-causal
  across October.

**Today's two verified cases (2026-11-02) — explicit results.**
1. **NTPC (N4-V3): REPRODUCED — book position OPEN.** Trigger fired
   (09:25-bar close 326.3 vs Friday close 316.25 = +3.18%). Entered LONG
   at the loop's first run (10:31 IST) at the frozen entry: the close of
   the 09:30 bar = **325.30**. Two factual corrections to the case as
   supplied, from the bars themselves: (a) 325.35 is the 09:35 bar's OPEN
   print; the frozen entry in both the book construction and the November
   primary spec is the 09:30-bar close (325.30), so book levels are
   target 330.18 / stop 322.70 (vs 330.23 / 322.75 off 325.35) — the
   producer was NOT changed to a non-frozen entry; (b) the post-entry
   range through 10:25 was actually 323.35–327.50, so while the book
   variant (T150/S080) is untouched and open, the **scorecard variant
   (T125/S050) stop 323.67 WAS hit on the 10:05 bar**: scorecard shows
   ENTRY 325.30 → EXIT stop 323.67 at 10:05, net −₹202.65. "Open under
   both variants" holds only for the book variant.
2. **GODREJCP (P2F shadow): REPRODUCED — entry AND exit surfaced.**
   Reaction return −2.27% sits in the shadow's ≥2.0% band (correctly NOT
   a book-P2F trade — book band is ≥2.5% — and the book loop took no
   GODREJCP entry, as frozen). Live-shadow shows SHORT entry 09:15 @
   813.0 and stop exit @ 817.06, net −₹446.50. One bar-attribution
   correction: the 09:15 entry bar's high (823.0) did cross the stop, but
   the frozen exit engine scans from the bar AFTER the entry bar, so the
   frozen exit fired on the 09:20 bar (high 817.5 ≥ stop 817.065),
   exit_time 09:20 — not inside the first 5 minutes. The substance
   (pre-booked entry, fast stop-out this morning) is exactly as supplied;
   frozen semantics were kept rather than rewritten.

**What is live as of this report.** Producer LIVE today (manual runs
10:31 and ~10:36 IST; NTPC book position open in the live-shadow state).
Cron `stocks-sarvaritu-live-shadow` runs every 5 min, Mon–Fri
09:15–15:35 IST body-guard, November 2026, announcements only in the
stocks chat (a78cf46b-244c-49e9-957c-05159e358301), LIVE-SHADOW labelled,
silent when nothing new. Day-1 honesty note: today's NTPC/GODREJCP
entries were detected when the loop first ran at 10:31 and are recorded
at their true frozen entry times/prices from completed bars — no fitted
or simulated prices. Caveat: the cron's body-guard is November-only; the
forward test runs through December, so extending it is a one-line cron
body edit when wanted. New events still enter only via the EOD process's
calendar maintenance — the live loop invents no events.

---

## Divergence classes (pre-declared, measured by the controls)

1. **C3 confirmation lag** (Nifty): live entry = confirming leg's entry
   bar; EOD entry = earliest leg's. Measured: Oct 26, one bar (09:55 →
   10:00 entry bar).
2. **Skill-early rescue lag** (Bank): a Skill-solo key with entry ≤ 09:55
   is held pending under Rule B and emitted only if a second system joins
   (entry = confirming leg's entry bar). Measured: Oct 23 (09:50 →
   10:00). If no second system joins, the key is correctly never emitted.
3. **V5 supersede / weekly-cap displacement**: named in the design; did
   not occur on the control days (V5 legs matched the frozen files on
   Oct 23/26/28 and Oct 30).

## Files

- Producer: `live_signal_producer.py` (log `live_producer_log.md`,
  state `live_producer_state.json`)
- Runner: `live_shadow_runner.py` (state `live_shadow_state.json`,
  console `live_shadow_runner_console.log`)
- Directives: `live_shadow_signals.json`
- Morning cron: `live-loop-morning-start` (Mon–Fri ~09:08 IST)
