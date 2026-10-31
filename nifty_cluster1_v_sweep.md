# NIFTY — Family (v): survival-gated partial (k=1.0, BE) on the OOS window — NO PASS, nothing adopted

## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (u) is done: no pass, nothing adopted. Previous best kept is
still (lA) on Cluster 1 (−₹2,720, 5/8), not adopted. Cluster 3
survival N=10 (3/3, +₹4,589.25, at k=0.9 in the survival sweep)
remains the best scoped result for Cluster 3 only, combined below
baseline — it is **not** re-run or re-claimed here, because (v) is
specified at k=1.0 and its OOS question is the give-back shape, not
Cluster 3.

Pass bar, same as (p)/(q)/(r)/(s)/(t)/(u): **60% green on the
failing set AND total positive AND combined NOT below (lA) on the
same window, winners not collapsed.** Green = net > ₹0.
**No-trade is counted separately from green throughout.**
100 shares equivalent, ₹40/trade, square-off 15:10, stop checked
before target on each bar except where a variant states otherwise.

Variant, defined before results — survival-gated partial,
interpretation B (eligibility, as in the survival sweep):

- PE only (rescan_trade: close below OR low and below previous-day
  low). Entry = next bar open after signal, stop = signal high,
  target = entry − 2×risk.
- Partial level = entry − 1.0×risk (k=1.0). Book 50 shares there,
  trail the remaining 50 to breakeven (entry).
- Gate index = entry-bar index + N, for N = 5, 10, 20. Bars before
  the gate are replayed plain (stop before target, no partial
  checked). A trade stopped or targeted before the gate is
  untouched — full stop or full target.
- At the gate open, if still open and the best favourable extreme
  over the pre-gate bars (minimum low) already reached the partial
  level, book 50 at the partial level immediately (partial time
  recorded as gate bar + "(gate, earned earlier)") and trail the
  rest to BE; the gate bar itself is then replayed with BE as the
  adverse level, so a BE exit can occur on the gate bar (as in the
  survival sweep: Cluster 3 13 Feb BE stop on its gate bar).
- If the partial level was not reached before the gate, arm it from
  the gate bar onward. Per-bar order from the gate onward (survival
  sweep run_bar order): adverse (current stop — original until
  booked, BE once booked) first, then partial trigger, then target,
  then square-off at 15:10. A partial booked on a bar cannot BE-exit
  on that same bar; BE can exit from the next bar onward.
- Re-entry: (lA) scan only, and only if the morning final exit is
  a plain "stop". A breakeven-after-partial, target-after-partial
  or square-off-after-partial morning does **not** re-enter —
  exactly as in (u)'s day_partial, where a breakeven exit likewise
  did not re-enter. No re-entry timing variant is proposed in (v);
  (lA) re-entry is kept as-is (see §3).

Engine: `v_sweep.py`, raw replay `v_sweep_raw.json`, replayed bar
by bar from the Upstox 5-min cache. It reuses `u_sweep.day_lA_plain`
for the (lA) baseline and mirrors `u_sweep.day_partial`'s structure
(morning partial, then (lA) re-entry on a plain stop). The morning
replay itself is new, because `u_sweep.replay_partial_gen` has no
survival gate (its `cutoff` is a time gate, not a survival gate).
One ordering difference from `replay_partial_gen` is documented,
not hidden: after a partial is booked, the survival replay replaces
the original stop with BE (so a later bar's adverse exit is a BE
exit), whereas (u)'s replay checked the original stop first on
every bar. A sensitivity run under (u)'s ordering is reported in
§4 — it changes nothing about the verdict.

## Engine validation — (lA) reproduced exactly, not copied

| Window | (lA) reproduced here | (u)/(q) reference | Match? |
|---|---|---|---|
| Cluster 1 (8) | 5/8 green, 0 no-trade, −₹2,720 | 5/8, −₹2,720 | Yes |
| Winners (14) | 12/14 green, 2 no-trade, +₹83,380 | 12/14, 2 no-trade, +₹83,380 | Yes |
| OOS (92 days) | 74 traded, 18 no-trade, 39 green (52.7%), +₹35,570; (lA)-winners +₹184,820, (lA)-losers −₹149,250 | 74 traded, 18 no-trade, 39 green, +₹35,570 | Yes |

The 2 in-sample winner no-trades (24 Feb, 12 Aug) are rescan
no-signals, identical under (lA) and under every survival variant
— the gate cannot create a trade. The 18 OOS no-trades are likewise
identical across all four runs. Every survival number below is
therefore a difference in exits on the same traded days, not a
difference in which days traded.

## Part 1 — OOS window: the decisive table (92 days, 74 traded)

| Variant | Green / traded | Green rate | Total | vs (lA) OOS +₹35,570 | (lA)-losers converted | (lA)-winner total |
|---|---|---|---|---|---|---|
| (lA) baseline | 39 / 74 | 52.7% | +₹35,570 | — | — | +₹184,820 |
| **Survival N=5, k=1.0 BE** | 45 / 74 | **60.8%** | +₹19,205 | **−₹16,365** | 6 / 35 (17.1%) | +₹116,962.50 (−₹67,857.50) |
| **Survival N=10, k=1.0 BE** | 45 / 74 | **60.8%** | +₹28,827.50 | **−₹6,742.50** | 6 / 35 (17.1%) | +₹126,585 (−₹58,235) |
| **Survival N=20, k=1.0 BE** | 44 / 74 | 59.5% | +₹27,227.50 | **−₹8,342.50** | 5 / 35 (14.3%) | +₹140,087.50 (−₹44,732.50) |

**No variant passes.** N=5 and N=10 pass the overall green-rate
leg (60.8%) and fail the total leg; N=20 fails both legs. And the
green-rate pass at N=5/N=10 is thinner than it looks, for a reason
that must be stated with it: all 39 (lA)-winner days stay green
under every variant (39/39), so the overall green count is carried
by winners that were already green. On the failing set itself —
the 35 (lA)-loser days — conversion is only 6/35 (17.1%) at N=5 and
N=10, and 5/35 (14.3%) at N=20. Under the loser-set reading of the
60% bar, every variant fails the green leg outright. Under either
reading, every variant fails the total leg, so the pass/fail
verdict does not depend on which reading is used.

Decomposition (day-net basis, morning + (lA) re-entry where fired,
as in (u)):

| Variant | (lA)-loser total: −₹149,250 → | Loser saving | (lA)-winner total: +₹184,820 → | Winner tax (net) | Net vs (lA) |
|---|---|---|---|---|---|
| N=5 | −₹97,757.50 | +₹51,492.50 | +₹116,962.50 | −₹67,857.50 | −₹16,365 |
| N=10 | −₹97,757.50 | +₹51,492.50 | +₹126,585 | −₹58,235 | −₹6,742.50 |
| N=20 | −₹112,860 | +₹36,390 | +₹140,087.50 | −₹44,732.50 | −₹8,342.50 |

The same structural trade-off as (u)'s ungated partials, in a
smaller dose: survival gating shrinks the winner tax (from
−₹74,000 to −₹122,000 ungated, to −₹45,000 to −₹68,000 here) but
it shrinks the loser saving even more (only 5–6 of 35 losers
convert, because most (lA) losers stop before any gate or never
reach 1.0×risk while still open). N=10 is the best variant by
total, and it is best for an instructive reason: its loser saving
is identical to N=5's (the same 6 converted days book the same
50×risk − ₹40 BE nets regardless of gate timing), while its
winner tax is smaller (fewer winners survive long enough to be
partialled: 18 winner days taxed at N=10 vs 23 at N=5, 12 at N=20).
N=20 taxes winners least but loses a conversion (2025-01-10) and
so ends below N=10. No gate length escapes the trade-off; moving
the gate later only trades conversions for winner preservation,
one for one, and the total stays below (lA) at every gate.

Converted (lA)-loser days (day net (lA) → survival, morning exit
breakeven-after-partial in every case):

| Converted day | N=5 | N=10 | N=20 |
|---|---|---|---|
| 2025-01-08 (−₹6,430) | +₹3,155 | +₹3,155 | +₹3,155 |
| 2025-01-10 (−₹11,985) | +₹3,117.50 | +₹3,117.50 | not converted (unchanged) |
| 2025-03-03 (−₹7,275) | +₹2,190 | +₹2,190 | +₹2,190 |
| 2025-09-23 (−₹3,525) | +₹1,702.50 | +₹1,702.50 | +₹1,702.50 |
| 2025-12-03 (−₹4,195) | +₹2,037.50 | +₹2,037.50 | +₹2,037.50 |
| 2026-06-03 (−₹3,960) | +₹1,920 | +₹1,920 | +₹1,920 |

No other (lA)-loser day changes at all under any variant — 29 of
35 losers are byte-identical to (lA) at N=5/N=10, 30 of 35 at N=20.
Changed-day counts: N=5: 30 days changed (6 conversions + 23
winner days taxed + 1 winner day improved, 2025-05-20 +₹460 →
+₹2,000, because the survival BE exit avoids a losing (lA)
re-entry that (lA) itself took); N=10: 25 changed (6 + 18 + 1);
N=20: 17 changed (5 + 12 + 0). Full changed-day rows are in
`v_sweep_raw.json` (OOS section, per variant) and in the engine
log; the unchanged days are, by construction, the complement.
No variant flips any (lA)-winner day to a loss (winner green
39/39 throughout) — winners are taxed in value, not collapsed in
count — but the pass bar requires the total too, and the total
fails.

**Part 1 verdict: survival gating does not rescue the give-back
shape OOS.** Its winner tax is smaller than the ungated partials'
tax, exactly as the survival sweep predicted in-sample, but its
loser conversion (17.1% at best) is far below the ungated partials'
(20–54% in (u)) and far below the 60% bar, because a 1.0×risk
partial gated on survival is earned by few losers. The give-back
family is now exhausted on this data in all three shapes:
ungated partials fail total (u), time-gated partials fail green
rate (q)/(u), survival-gated partials fail total at every gate
(and fail green on the loser set at every gate). 13 May stays an
in-sample give-back example, not a validated exit rule — and, as
§2 shows, survival gating could not have converted 13 May itself
in any case.

## Part 2 — In-sample comparison (Cluster 1 + winners, same variants)

| Variant | Cluster 1 (8) | Winners (12 traded / 14) | Combined C1+Winners | vs (lA) combined +₹80,660 |
|---|---|---|---|---|
| (lA) reference | 5/8, 0 no-trade, −₹2,720 | 12/12 green, +₹83,380 | +₹80,660 | — |
| Survival N=5 | 5/8, 0 no-trade, −₹2,720 | 12/12 green, +₹63,167.50 | +₹60,447.50 | −₹20,212.50 |
| Survival N=10 | 5/8, 0 no-trade, −₹2,720 | 12/12 green, +₹69,652.50 | +₹66,932.50 | −₹13,727.50 |
| Survival N=20 | 5/8, 0 no-trade, −₹2,720 | 12/12 green, +₹75,677.50 | +₹72,957.50 | −₹7,702.50 |

Cluster 1 is **identical to (lA) at every gate, day for day**:
no Cluster 1 morning is partialled at any N (partialled list is
empty for Cluster 1 at N=5, N=10 and N=20), because every Cluster 1
morning stops before even the N=5 gate — 13 May stops 09:55,
before its N=5 gate at 10:00; the other seven stop earlier still.
Survival gating therefore cannot be a 13 May fix and cannot be a
Cluster 1 fix, by construction, at k=1.0 just as at k=0.9 in the
survival sweep. In-sample, survival gating only taxes winners:
8 of 12 traded winners partialled at N=5, 4 at N=10, 2 at N=20
(22 Jul and 8 Oct are partialled at all three gates; 24 Apr,
5 May at N=5/N=10; 16 Mar, 27 Aug, 7 Sep, 23 Oct at N=5 only).
Winner green count never collapses (12/12 throughout), but winner
value falls ₹7,702–₹20,212 and combined in-sample falls with it,
so no in-sample variant passes the combined leg either.

## Part 3 — (lA) re-entry check: no new timing variant, working trades untouched

No (lA) re-entry timing variant is proposed in (v). The check the
task requires is therefore run as a no-change check: the three
working (lA) re-entries from (u) must appear unchanged under every
survival variant, and they do — because their mornings stop before
any gate, the morning is untouched, and the (lA) re-entry scan runs
on the identical stop bar with the identical band:

| Working re-entry day | (lA) morning → re-entry → day net | Survival N=5 / N=10 / N=20 (all three) |
|---|---|---|
| 2026-06-29 | −₹4,740 → +₹6,840 → **+₹2,100** | Identical: morning −₹4,740, re-entry +₹6,840, day +₹2,100 |
| 2026-07-08 | −₹1,985 → +₹2,940 → **+₹955** | Identical: morning −₹1,985, re-entry +₹2,940, day +₹955 |
| 2026-08-19 | −₹2,300 → +₹3,970 → **+₹1,670** | Identical: morning −₹2,300, re-entry +₹3,970, day +₹1,670 |

The other Cluster 1 re-entries are likewise identical (9 Jan
+₹6,040 → day +₹2,295; 6 Feb +₹2,930 → day +₹1,120; 2 Apr −₹1,665
→ day −₹3,730; 30 Mar and 13 May no re-entry, days −₹2,055 and
−₹5,075). Any future re-entry timing variant must still be
checked in this same table before it is proposed as a fix for
30 Mar / 2 Apr — and, per (u), a bounce-persistence guard in
either form (U1/U2) is not to be re-proposed, because it deletes
exactly these three trades.

## Part 4 — Ordering sensitivity (does the verdict hinge on bar ordering?)

The one judgement call in the (v) engine is the gate bar: under
survival order, a gate-booked trade whose gate bar touches BE
exits at BE even if that bar also reaches target; under (u)'s
original-stop-first ordering with BE deferred past the booking
bar, that gate bar can reach target instead. Re-running the OOS
window under (u)'s ordering: N=10 and N=20 are **unchanged to the
rupee** (0 differing days, totals +₹28,827.50 and +₹27,227.50);
N=5 differs on exactly 2 days, both upward — 2025-02-11
(+₹945 → +₹2,915, target-after-partial instead of BE) and
2026-08-18 (+₹467.50 → +₹1,482.50) — lifting the N=5 total to
+₹22,190, still ₹13,380 below (lA), with green unchanged at
45/74. The survival ordering used for the headline numbers is the
conservative one (and the one the survival sweep itself used), and
the alternative ordering does not change any pass/fail verdict.
This sensitivity was run on the OOS window only, where the verdict
is decided; in-sample headline numbers use survival ordering
throughout.

## Part 5 — Cluster 2: forward logging format only, no rule, no result

Per the task and per (u) Part 3, no new Cluster 2 entry/exit rule
is proposed, tested, or claimed in (v). Cluster 2 remains recorded
as unfixable on the available 6-trade sample. The only (v) output
for Cluster 2 is this logging format, for forward paper trades as
they accumulate (paper only, no re-fitting on the paper month):

| Field | What to record |
|---|---|
| date | Trade date |
| signal | Reclaim signal time, and the (s)-format scan that produced it |
| L | max(OR high, previous close), frozen at signal time |
| entry / stop / risk / target | Frozen entry, stop, risk and target from the original trade |
| exit / net | Actual paper exit (time, reason, net at 100 shares, ₹40/trade) |
| original_would_have_done | What the original (unmodified) trade would have done on the same day, for comparison |
| notes | Post-signal path only as observation (first close/low below L, MFE) — not a fitted rule |

No forward reclaim trade is claimed in this report: no new reclaim
trade was accumulated or evaluated as part of (v), and no date is
listed here, because listing one would invent it.

## Verdict — family (v) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| 1 — Survival-gated partial, OOS | N=10 | 45/74 green (60.8%), but total +₹28,827.50, ₹6,742.50 below (lA); loser conversion 6/35 (17.1%) | No — fails total, and fails green on the loser set |
| 1 — Survival-gated partial, OOS (other gates) | N=5 | 45/74 (60.8%), +₹19,205, ₹16,365 below (lA); N=20: 44/74 (59.5%), +₹27,227.50 | No |
| 2 — Survival-gated partial, in-sample | N=20 (least winner tax) | Cluster 1 identical to (lA) (−₹2,720); winners +₹75,677.50; combined +₹72,957.50, below (lA) | No — Cluster 1 untouched, combined below (lA) |
| 3 — (lA) re-entry | (lA) as-is | 29 Jun, 8 Jul, 19 Aug working re-entries identical under all variants | No new variant proposed; check passed as no-change |
| 5 — Cluster 2 | Logging format only | No rule, no result claimed | — |

- **No (v) variant passes** the full bar (60% green on the failing
  set AND total positive AND combined NOT below (lA), winners not
  collapsed) as a genuine conversion fix, on either window.
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is not
  adopted. Cluster 3 survival N=10 (k=0.9, prior sweep) remains the
  best scoped result for Cluster 3 only, combined below baseline.
  November paper is NOT frozen for any (v) variant. No (v)
  in-sample result is carried into a whole-month run on the same
  Jan–Oct data.
- **Give-back family exhausted on this data:** ungated partials
  (u), time-gated partials (q)/(u), and now survival-gated
  partials at N=5, 10 and 20 (v) all fail the total leg OOS, and
  survival gating additionally fails the loser-conversion leg at
  every gate. 13 May stays an in-sample give-back example.
- **Dead, do not re-propose without new evidence:** any further
  partial shape as a give-back fix on this data (ungated,
  time-gated, or survival-gated at a new gate length — the gate
  length only trades conversions for winner preservation);
  bounce-persistence re-entry guards U1/U2 (delete the 29 Jun,
  8 Jul and 19 Aug working re-entries); any Cluster 2 entry/exit
  rule on the 6-trade sample.

## Next family (w) — the task continues, not completed

Family (v) closes the give-back question on this data. What remains
open, in the order the evidence points to it:

1. **Cluster 1's morning bar itself, or a re-entry timing variant
   that survives the §3 table.** The waiting families are now
   exhausted for Cluster 1 (timing, second-close, retest, stall,
   survival, and every partial shape all fail to convert it, and
   its mornings stop before any gate). The next family must either
   change the morning entry or its stop in a way not already
   tested to exhaustion, or propose a re-entry timing change that
   is shown, in the §3 table, not to delete the 29 Jun, 8 Jul and
   19 Aug working re-entries — before it is proposed as a fix for
   30 Mar / 2 Apr.
2. **Cluster 2: forward logging only** (§5), until new reclaim
   trades accumulate in forward paper. No entry/exit family until
   then.
3. **Cluster 3: forward validation only.** Its scoped survival
   result (prior sweep, k=0.9) is not re-tested here and is not
   adopted without a validated live discriminator.

Files: engine `v_sweep.py`, raw replay `v_sweep_raw.json`, this
report `nifty_cluster1_v_sweep.md`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task continues
in the parent conversation: family (v) is exhausted, none is
adopted, and the next decision is family (w) — not a whole-month
run of any (v) variant on the same Jan–Oct data.
