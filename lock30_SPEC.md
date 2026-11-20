# LOCK30 TEST — SPEC (frozen 2026-11-16, before any scoring)

Owner follow-up (2026-11-16 18:59 IST) to today's small-target test:
why don't we keep a FIRST target at +30 points? Two forms of that idea
are already measured and dead, and they are NOT what is tested here:

- **The 2026-11-03 ladder** (v21 Bank legs): spot-stage ratchets —
  premium locks +5/+15/+25 keyed to spot stages +30/+58/+82/+100,
  with the hard stop tightened to **−20 from the start**. Scored
  +₹16,777.50 vs +₹83,650.50 plain; WR fell to 46.5%. It failed
  mainly via the tight −20 stop (legs stopped before they could
  travel) and the ratchet locks whipsawing.
- **S30** (small-target test, 2026-11-16): the WHOLE position exits
  at +30. Failed on all three streams — it sells the runner tail
  (median max run +52..+93 pts) at +30.

The two forms below are mechanically distinct from both: nothing is
sold at +30 in LOCK30 (only the stop moves), the hard stop stays at
the leg's own frozen stop (−50 in these books) until the touch, and
there are no ratchet stages. Paper research only. No frozen book,
ledger or live job is touched.

## Streams (entries identical; controls must reproduce EXACTLY first)

Same assembly, leg sets and anchors as small_target_SPEC.md (the
build reuses that run's machinery verbatim; every control assertion
in it must pass again before any variant is scored):

1. **BANK-STACK** — TUNED STACK v2, Jan–Oct: **+₹127,351.50 / 111**.
2. **BANK-LEGACY** — legacy v21, Jan–Oct: **+₹83,650.50 / 99**.
3. **NIFTY-V1** — TUNED v1 (EVE-07), Jan–Oct: **+₹103,050.25 / 74**.

Lots: Bank 30, Nifty 65. Cost ₹220/leg. If any control misses, the
run STOPS and reports the discrepancy.

## LOCK30 (primary variant — executable on 1 lot)

Each leg keeps its OWN frozen exit geometry (its params, its arms,
its runner stages, its square-off) with ONE modification — a stop
floor:

- Until the touch: everything is the original geometry, including
  the hard stop (the leg's own frozen stop, −50 in these books) and
  any original arm (Bank NS1_second arm30 → entry+0; Nifty arm50 →
  entry+0).
- **Touch**: a completed 5-min bar (entry bar onward) whose high
  reaches entry + 30. The touch registers at that bar's close — the
  books' own arm convention (the same point where replay_mod /
  replay_r5 register their arms, after that bar's stop and target
  checks). On the touch bar itself the original stop still governs.
- From the NEXT bar onward, the effective stop is
  **max(original effective stop, entry + 5)**. One move only — no
  further ratchets, no T2/T3 stages. The floor never lowers a stop
  the original geometry sets: once the +90 trigger fires, the
  original runner geometry (lock / tgt2) governs untouched (its stop,
  entry+90 Bank / entry+60 Nifty, is above +5 anyway). On legs whose
  own arm would set entry+0 after the same touch (NS1_second, Nifty
  arm50), the floor takes the max — the stop is entry+5, not entry.

### Fill discipline (identical to the small-target run)

- Stop fills at the effective stop level — unless the bar opens
  beyond it (below the level), then at the bar's open.
- Terminal target fills at the level — or at the bar's open on a
  gap-through above. Runner stop / runner target fills likewise.
- Square-off fills unchanged (the square-off bar's close; Bank
  re-entry legs keep their source terminal rule: stop/target on bars
  ≤ 15:05, terminal = 15:10 bar open if present, else the close of
  the last bar ≤ 15:05).
- Disclosed difference, same as the small-target run: the frozen
  books fill stops/targets at the level even on gap-through bars;
  the variant fills at the open. Applied uniformly, in advance.

## HALF30 (arithmetic reference — NOT executable on 1 lot)

**Every output labels HALF30 as requiring 2 lots to execute
literally; on this 1-lot record it is a points blend.**

- Walk the leg's own premium path over its CONTROL holding window
  (entry bar through the control exit bar inclusive). The first bar
  whose high reaches entry + 30 is the touch — except that on the
  control exit bar itself a stop-family exit (stop / lock_stop /
  be_stop / runner_stop) fires first by the books' stop-before-target
  convention, so no touch is counted on that bar (for armed and
  runner stops the touch necessarily occurred on an earlier bar and
  is counted there). For Bank re-entry legs whose control exit is
  the 15:10 terminal open, only bars before 15:10 are scanned (the
  exit happens at that bar's open, before its high exists).
- Touch fill: entry + 30 — or the touch bar's open on a gap-through
  above (the small-target run's discipline).
- If touched: net = ( 0.5 × (touch fill − entry)
  + 0.5 × (control exit premium − entry) ) × lot − ₹220.
  **One ₹220 cost per leg, not two.** The riding half's exit is the
  recorded control exit, untouched.
- If never touched: net = the control net, unchanged.

## Gate (full, same run, per stream per variant)

- Timing/leak audit on the new fills: exit time ≥ entry time; every
  exit fill is the exit bar's own binding level / open / close (no
  future bar is ever read); entry fill equals the recorded entry
  premium on every leg; no exit after the stream's square-off.
  Internal mirror audit: the variant walk with the LOCK30 floor
  disabled and level fills must reproduce every leg's recorded
  control exit (time / premium / reason) — a divergence stops the
  run for that stream.
- Placebo: the same legs with entries shifted +30 minutes (6 bars)
  on the leg's own series, scored under the SAME variant. For
  LOCK30 the shifted entry is walked under LOCK30. For HALF30 the
  shifted entry's original exit is the frozen replay from the
  shifted entry (replay_mod delay=6 / replay_r5 delay_bars=6 /
  sim_g0), and the touch scan + blend apply to that path. Legs with
  no valid shifted entry are dropped from the placebo and counted.
  The variant must beat its shifted twin's total.
- Halves: Jan–May vs Jun–Oct nets.
- Full month table (Jan–Oct), red months named.
- Ex-top-3 (total minus the three largest leg nets).
- Win rate and ₹/trade-day (trade-day = a date with ≥1 leg;
  identical leg set ⇒ identical trade-days across control and
  variants).
- Independent re-sum of the written trades file, to the paisa.
- November counterfactual: Nov 2–16 legs as stored (Bank stack log,
  Bank legacy PRIMARY log, Nifty TUNED v1 legs = DEC-S1 shadow log
  minus component-B PE rows), shown separately, NEVER used to
  select. LOCK30 geometry for the CF legs: Bank stack legs use the
  frozen stack form (runner lock 90 / tgt2 180, arm30 iff family =
  NS1_second; all four CF legs' dates ≠ their expiry); Bank legacy
  legs use the log's own plain geometry (stop −50, target +90
  terminal, per the log's stop/target columns); the Nifty leg uses
  TUNED v1 geometry (lock 60 / tgt2 175 / arm 50 / SQ 15:20, per
  the DEC-S1 log's stated geometry). HALF30 CF needs no geometry —
  the touch scan runs against the recorded control exit. Terminal
  for CF walks = 15:20 close (last bar ≤ 15:20), on the
  november_shadow_data premium candles (the small-target run's
  loader, exact-tag files outranking globs).

## VERDICT RULE (frozen)

A variant is a **PASS** for its stream only if ALL of:
1. its Jan–Oct total beats the control total, AND
2. it keeps **zero red months**, AND
3. it beats its placebo (shifted-entry twin).

If a variant loses on total but beats the control on win rate,
worst month or drawdown, the report states exactly that trade-off
in plain numbers — no PASS label. (Note, stated in advance: the
Bank legacy control itself has 3 red months — Apr, Jul, Aug — so
rule 2 is an absolute bar, as in the small-target run.) Halves,
ex-top-3 and the November counterfactual are reported in full for
every variant regardless of the label.

## If LOCK30 PASSes on a stream

Build its score-only forward-shadow scorer + seeded ledger for that
stream (Nov 2–16 counterfactual rows labelled
BACKFILL_COUNTERFACTUAL) and report the cron line for the parent to
add (21:20 IST slot). The build does NOT create the cron. HALF30
never gets a shadow (it is an arithmetic reference, not an
executable 1-lot book).

## Deliverables

lock30_SPEC.md (this file) · lock30_build.py ·
lock30_2026-11-16.md · lock30_results.json · lock30_trades.csv
(284 Jan–Oct legs × control + 2 variants, plus the 12 November CF
legs). Data: local stores only; no fetch is expected to be needed —
any Upstox fetch would use the browser User-Agent and hard-stop
the run on a 429.
