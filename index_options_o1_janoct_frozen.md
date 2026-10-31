# Index OPTIONS — O1 cross-confirmation persistence, Jan–Oct 2026 — FROZEN before scoring
Paper only, no orders, no stocks, no futures. Index OPTIONS only.
Written BEFORE any Jan–Oct O1 number was computed (2026-10-30).
Window: Jan–Oct 2026, 1 Jan – 28 Oct 2026, 203 trading days in the spot cache
(October = 1–28 Oct only, 18 days, as in cache). Nifty and Bank Nifty separately, never pooled.
Unit: spot provisional = direction points × 100 shares − ₹40 per leg.
This is NOT an options-lot profit and NOT a futures profit.
Premiums: NOT recomputed for Jan–Oct (no option candles in the spot cache; no live fetch
in this subagent run). An October-only premium overlay from the existing v2 CSV is shown
separately and is labelled as October-only, never as a Jan–Oct premium result.

## O1 definition — copied verbatim from October Family C (C1)
From ~/workspace/trading/index_options_familyC_frozen_oct30.md, C1:

> PE breakdown taken only if the confirming index (Bank confirms Nifty, Nifty confirms Bank)
> closes below its own OR low on BOTH the signal bar AND the entry bar (the bar after the
> signal, whose open is the entry). CE trades are out of scope and are kept unchanged;
> the PE-filtered count is reported separately.

Applied here exactly as in October, with these mechanical clarifications (no change of substance):
- Confirmer = the OTHER index: Bank Nifty confirms Nifty PE trades; Nifty confirms Bank Nifty PE trades.
- OR low = the confirmer's own opening-range low that day: minimum low over the confirmer's
  5-min bars with time < 09:30 (09:15 and 09:20 bars, plus 09:25 bar where present in cache).
- Signal bar = the traded symbol's signal bar (clock time T). Entry bar = the next 5-min bar
  after the signal bar on the traded symbol (clock time T+5 min, whose open is the entry price).
- The confirmer is read at the SAME clock times: confirmer close at time T AND confirmer close
  at time T+5 min. BOTH closes must be strictly below the confirmer's OR low. If either
  close is at/above the confirmer's OR low, or if either confirmer bar is missing from the
  cache, the PE trade is filtered out (missing-bar cases are counted and listed, not assumed kept).
- CE handling: CE trades are NEVER filtered by O1, on any track. They are kept unchanged and
  are not counted as "filtered out".
- Filter granularity: O1 removes the WHOLE trade/day. For (lA) v2, where a day net =
  morning leg + re-entry leg where a re-entry fired, filtering removes the whole day net
  (both legs); O1 does not re-score the re-entry leg standalone.
- O1 is a filter only: it creates no new signals, moves no entry/stop/target, and does not
  re-gate room. A kept trade keeps its exact base entry, stop, target, exit and net.
- No cap is re-applied after filtering: O1 is scored on the base set as defined below, and
  filtered-out trades are NOT replaced by the next candidate in that week.

## Base tracks — per version per index, separately
- V4 (uncapped): V4 index candidates from find_signal + run_day per day (setups 1–4;
  Setup 1 skipped — no Red bands supplied), recomputed from the spot cache Jan–Oct.
  This is the October Family C V4 base (uncapped: Nifty 4, Bank 5 in October), extended
  to Jan–Oct. It is NOT the capped V4 series (62 trades Jan–Oct) and must not be quoted as it.
- Skill v2 (S1, uncapped): raw first OR break — first 5-min close beyond the 09:15–09:30 OR
  between 09:30 and 11:30 — with exactly two S1 blocks: (a) a 09:30 PE signal is taken only
  if its close is below PDL; (b) CE on a bearish-bias day (prev-day close position < 35%)
  is blocked. Exit: entry = next bar open, stop = signal high/low, target = 2× risk,
  square-off 15:10, stop checked before target per bar. Recomputed from the spot cache
  Jan–Oct. This is the October Family C Skill base (Nifty 8, Bank 9 in October), extended.
  It is NOT the bias-aligned / room-filtered Skill series used inside the capped V5 pool
  and the triple merge; the two Skill series differ and are never merged here.
- (lA) v2 (L1, uncapped candidates): (lA) PE rescan + L1 extension (rescan cutoff 11:30 →
  13:30 only where the confirmer broke before 11:30), PE only, day net = morning + re-entry
  where a re-entry fired, recomputed Jan–Oct with the L1 engine
  (~/workspace/trading/o1_la_l1.py: confirmer break = first bar 09:30–11:30 closing below
  the confirmer's OR low; rescan = first bar at/after the confirmer break, ≤ cutoff, close
  < own OR low AND < own PDL, OR width ≤ 360×scale, room ≥ 200×scale; re-entry =
  scan_reentry "lA" band [10, morning risk], morning scan-skip to 11:30, afternoon
  stop-on-first-fail to 15:05). Signal time = morning_signal. This is the October Family C
  (lA) base (Nifty 3, Bank 4 in October), extended.
  CORRECTION NOTE (found during the October cross-check, before Jan–Oct (lA) scoring):
  the merged Jan–Oct JSONs (data/progressive/merged_skill_la_summary_2026-MM.json,
  la_candidates) use the BASE 11:30 rescan (rescan_trade) without the L1 extension and
  therefore drop 2 October v2 days — Bank 8 Oct signal 13:15 (−₹8,510) and Nifty 21 Oct
  signal 11:35 (+₹4,940) — so they do NOT reproduce the Family C (lA) base and were NOT
  used. The L1 engine above reproduces October exactly (Nifty 3 / +₹28,020 with signals
  11:25, 11:35, 10:05; Bank 4 / +₹28,275 with signals 09:35, 13:15, 11:15, 09:55).
  Reading pinned by that reproduction: "broke before 11:30" = confirmer break time
  strictly < 11:30. Sensitivity: with ≤ 11:30 instead, exactly one extra Jan–Oct (lA)
  trade appears — Nifty 2026-08-04, signal 12:05, day net −₹1,655 (confirmer break at
  exactly 11:30) — excluded under the strict reading used here.
- V5-v2 (capped pool, by definition): pooled V4 + Skill-filtered candidates (OR-only,
  bias-aligned, room ≥ 200×scale, PD bound — the v2 frozen pool definition), dedup by
  symbol+date, prospective target net ≥ ₹500, cap 3 index trades/ISO week and
  1 trade/symbol/week, applied per calendar month exactly as in capped-v2 Jan–Oct
  (data/progressive/capped_v2_summary_2026-MM.json, unified_capped_trades, index legs only).
  V5-v2 is the ONLY capped base in this run, because its definition includes the cap;
  its O1 delta is measured on that capped set. Signal time for each V5 trade is recovered
  from its origin candidate (V4 signal bar, or Skill-filtered signal bar) recomputed for
  that month; a V5 trade whose origin signal time cannot be recovered is listed as
  UNRESOLVED and excluded from neither base nor O1 (it is reported, not silently dropped
  from the base count — base counts still include it, O1-kept counts exclude it only if
  it is a PE trade, with the reason stated).
- Volrix v2: out of scope for O1 (it is a daily-close overlay with no OR signal bar, so
  the O1 signal/entry-bar test does not apply). Reported as 0 O1 effect by construction,
  not scored.

## Metrics (per track, base vs O1)
- Trades, net (spot provisional ₹), win = net > 0 count and rate, full-target = count and
  rate where full-target means exit_reason = target AND day net > 0 (for (lA), the
  candidate exit_reason "target" already encodes morning-target with no re-entry and a
  positive day net; "day_green" days are wins but NOT full targets).
- Frequency = trades ÷ 203 days × 5 (trades/week over Jan–Oct).
- Filtered-out list per track: every PE trade removed by O1, with date, direction, base
  exit, base net, and whether it was a winner (net > 0) or loser (net ≤ 0) removed.
  October subset is also shown separately per track, so the October keeps can be checked
  against the Jan–Oct result without re-reading Family C.
- Verdict rule (pre-registered, same as Family C): O1 is a "keep as candidate" for a track
  only if, vs that track's base, it improves net AND win/full-target rate together
  without the gain coming only from deleting trades (trades, net, win rate and full-target
  rate all shown). Otherwise "discard + why". Nothing is adopted on Jan–Oct in-sample
  alone; November 2026 paper from 2026-11-02 remains validation, with the definition frozen here.
- October cross-check (must pass before Jan–Oct numbers are trusted): recomputing O1 on
  the October slice of each base must reproduce the Family C C1 October deltas
  (Skill Bank 9→7, +₹8,675→+₹20,790; (lA) Bank 4→3, +₹28,275→+₹35,750; (lA) Nifty 3→2,
  +₹28,020→+₹16,330; V4 Nifty 4→2, +₹2,725→+₹2,755; V4 Bank 5→3, +₹67,690→+₹60,900;
  Skill Nifty 8→4, +₹8,420→+₹15,780; V5 Nifty 3→2, +₹8,195→+₹2,755; V5 Bank 4→2,
  +₹43,630→+₹36,840). Any mismatch is reported as a mismatch, not adjusted to match.

## Data sources (cached only, no live fetch, no orders)
- ~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv and spot_daily.csv.
- (lA) L1 engine: ~/workspace/trading/o1_la_l1.py (see correction note above); the merged
  Jan–Oct JSONs were checked and rejected as the (lA) base for the reason stated.
- ~/workspace/trading/data/progressive/capped_v2_summary_2026-MM.json (V5-v2 capped trades).
- October premium values only: ~/workspace/trading/index_options_v2_october_trades.csv.
- Muse Upstox connector was NOT used (still 401 per task); no missing day was patched.
