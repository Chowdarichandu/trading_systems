# NIFTY — Family (s): frozen c2-A validation + pure thin-signal no-trade — NO PASS, nothing adopted

## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (r) is done: no pass, nothing adopted. Its best scoped results were
(lA) on Cluster 1 (−₹2,720, 5/8 day-green, winners intact — (lA) itself
NOT adopted), c2-A on Cluster 2 (1/2 green, 1 no-trade, +₹3,510 — 50% < 60%,
in-sample on 3 reclaim trades), and survival N=10 on Cluster 3 (3/3,
+₹4,589.25, combined below baseline). Family (s) tests the two leads (r)
left, and nothing else for the untouched days: no third/fourth re-entry,
no wider band, no signal-low trigger, no direction flip on 2 Apr.

Pass bar, same as (p)/(q)/(r): **60% green AND total positive AND combined
NOT below (lA) on the same window, winners not collapsed.** Green =
net > ₹0. **No-trade is counted separately from green throughout — a
no-trade is never a green, and a total improved only by avoiding trades
is reported as avoidance, not conversion.** 100 shares equivalent,
₹40/trade, square-off 15:10, stop checked before target on each bar.

Engine: `s_sweep.py`, raw replay `s_sweep_raw.json`, replayed bar by bar
from the Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv`,
`spot_daily.csv`, Jan 2025–28 Oct 2026). Nothing fabricated.

**c2-A FROZEN definition (from (r), not re-fitted here):** reclaim level
L = max(OR high, previous close). Entry = open after the second close
above L, stop = second-bar low, target = entry + 2× new risk, CE. If the
second close is ≤ L: no-trade. No stronger hold (c2-E) is substituted —
(r) already showed c2-E collapses on 0.15 points on 26 Oct 2026.

**Thin-signal NO-TRADE definition (pure, as instructed):** a PE signal
whose close sits within <5 points below the OR low (0 < ORlow − close < 5)
makes the **whole day a no-trade** — no rescan, no scan to a later signal,
no re-entry. A second, diagnostic variant adds the narrow-range feature
the untouched days share: thin AND signal range < 40 points. Both are
reported; neither is allowed to claim a later signal's result as its own.

## Part 1 — Freeze c2-A and validate it on held-out reclaim trades: FAILS, DISCARD

### Held-out set: 2025, a different year from the 2026 fit — exactly 3 trades

Scanning every 2025 day with the same `find_signal` logic (first signal
per day, setup4_reclaim only) gives exactly 3 reclaim trades in 2025 —
the same small N as the fitted set, which is itself a warning about how
rare this setup is. No setup4_pullback first-signal occurs in 2025 or
2026 in this scan, so nothing was hidden by that exclusion.

| Date | Signal / L / above L | Original (entry, stop, risk, net) | Second close / above L | c2-A frozen (entry, stop, risk, net) |
|---|---|---|---|---|
| 2025-02-20 | 13:50 / 22,914.40 / +2.10 | 22,917.30, 22,905.55, 11.75, **−₹1,215 stop** | 22,909.75 / −4.65 | **no-trade** (hold fails) |
| 2025-06-06 | 10:05 / 24,763.35 / +31.25 | 24,793.70, 24,682.20, 111.50, **+₹22,260 target** | 24,750.60 / −12.75 | **no-trade** (hold fails) |
| 2025-08-01 | 10:30 / 24,765.60 / +12.50 | 24,778.95, 24,756.25, 22.70, **−₹2,310 stop** | 24,771.30 / +5.70 | 24,771.10, 24,769.30, 1.80, **−₹220 stop 10:40** |

Held-out totals:

| Scope | Green | No-trade | Still loss | Total |
|---|---|---|---|---|
| 2025 original reclaim set | 1/3 (the 6 Jun winner) | 0 | 2 | **+₹18,735** |
| 2025 c2-A frozen | **0/3** | 2 | 1 | **−₹220** (traded only; no-trades = ₹0) |

On the held-out **failing set** (the 2 losers, 20 Feb and 1 Aug):
c2-A converts **0/2 = 0% to green** — far below the 60% bar. 20 Feb is
avoidance (a loss removed, not a green). 1 Aug is still a loss, shrunk
from −₹2,310 to −₹220 only because the recomputed risk is a knife-edge
1.80 points (target 3.60 points, cost ₹40 alone is most of the loss) —
a 1.80-point stop is not a tradeable confirmation, it is a rounding
artefact of a second bar whose low almost equals the next open.

On the **winner side**, c2-A fails in the opposite direction: it kills
the held-out set's only winner. 6 Jun 2025 (+₹22,260 original, the
largest single reclaim trade in either year) becomes a no-trade because
its second close (24,750.60) sits 12.75 points below L. Hold confirmation
therefore does **not** separate losers from winners out-of-sample:
in 2025, the hold-passing trade still loses (1 Aug), a hold-failing
trade is a loser avoided (20 Feb), and a hold-failing trade is the
big winner killed (6 Jun).

Combined, c2-A collapses the reclaim set from +₹18,735 to −₹220 —
a −₹18,955 swing, driven almost entirely by removing the winner.
It fails **all three** legs of the pass bar: 0% green (< 60%),
total negative, combined far below the original on the same window.

### Reproduction check: 2026 fitted set (must match (r) exactly — it does)

| Date | Original | c2-A |
|---|---|---|
| 2026-01-14 | −₹2,785 | no-trade (second close 25,737.50 < L) |
| 2026-07-01 (winner) | +₹4,240 | +₹3,890 (preserved, −₹350) |
| 2026-10-26 | −₹8,635 | +₹3,510 (risk 17.75 vs 85.95) |
| **Total** | −₹7,180 | **+₹7,400** (1/2 green on losers, 1 no-trade) |

The engine reproduces (r) exactly, so the 2025 failure is not an
engine change — it is the rule failing on data it was not fitted on.

### Part 1 verdict: DISCARD c2-A

**c2-A is discarded. Do NOT re-fit it to a stronger hold, do NOT freeze
it for November paper as a candidate, and do NOT carry its 2026
+₹3,510 into any adoption claim.** Its in-sample 50% was already below
the bar; out-of-sample it is 0% green on losers and it kills its
winner. The correct reading is that second-close hold is not a
reclaim discriminator on the available data (3 + 3 trades total) —
not that a slightly different hold threshold would fix it, since (r)
already showed the stronger hold collapses on 0.15 points.

### Forward-paper preparation (for the record, NOT a c2-A candidate)

Because the different-year test already answers Part 1, no forward
paper run is claimed for c2-A and no future result is stated. If the
parent conversation ever wants a reclaim rule watched forward, the
frozen log format to use for a *future, separately validated* rule is:
date, signal time, L, signal close above L, second close above L
(yes/no + points), frozen entry/stop/risk/target, exit, net, and
whether the original (unconfirmed) trade would have done — recorded
daily, paper only, with no re-fitting on the paper month. That format
is a template only; it does not revive c2-A.

## Part 2 — Pure thin-signal no-trade for the untouched shape: NO CONVERSION

### What "thin" actually looks like, before any rule is applied

Plain Cluster 1 signal distances below the OR low (ORlow − signal close)
and signal ranges (high − low):

| Date | Signal | Dist. below OR low | Signal range | Plain net | (lA) signal dist. / range | (lA) day net |
|---|---|---|---|---|---|---|
| 2026-01-09 | 09:30 | **2.00** | 52.30 | −₹3,745 | 2.00 / 52.30 (same bar) | +₹2,295 (green via re-entry) |
| 2026-02-06 | 09:35 | 9.25 | 31.60 | −₹2,275 | 37.75 / 28.90 (rescan 10:10) | +₹1,120 |
| 2026-03-30 (untouched) | 11:25 | **1.95** | **22.45** | −₹2,055 | 1.95 / 22.45 (same bar) | −₹2,055 |
| 2026-04-02 (untouched) | 09:55 | **2.65** | **22.00** | −₹2,115 | 2.80 / 35.65 (rescan 10:45) | −₹3,730 (morning + re-entry) |
| 2026-05-13 | 09:30 | 24.50 | 51.95 | −₹5,075 | 24.50 / 51.95 | −₹5,075 |
| 2026-06-29 | 09:30 | 15.25 | 48.90 | −₹4,740 | 15.25 / 48.90 | +₹2,100 |
| 2026-07-08 | 09:30 | 9.85 | 25.60 | −₹1,985 | 9.85 / 25.60 | +₹955 |
| 2026-08-19 | 09:30 | 19.20 | 27.25 | −₹2,300 | 19.20 / 27.25 | +₹1,670 |

Two facts matter before the rule is judged. First, thinness is **not
unique to the untouched days**: 9 Jan is also thin (2.00 points) in
both scopes, and in the (lA) scope 9 Jan is a green day (via re-entry),
so a pure thin no-trade kills a green there. Second, the (lA) rescan
changes the signal bar for some days (6 Feb, 2 Apr, and several
winners below), so thin status is **scope-sensitive** — a rule judged
on plain signals does not automatically transfer to (lA) signals, and
vice versa. Both scopes are reported below, separately.

### Plain scope: Cluster 1 (8) + PE winners (14)

| Variant | Cluster 1 green / no-trade / total | Winners green / no-trade / total | Combined | vs plain baseline +₹66,980 | Pass? |
|---|---|---|---|---|---|
| Plain baseline | 0/8 / 0 / −₹24,290 | 14/14 / 0 / +₹91,270 | +₹66,980 | — | — |
| **Thin <5, pure no-trade** | 0/8 / 3 / −₹16,375 | 10/14 / 4 / +₹76,050 | +₹59,675 | −₹7,305 | **No — 0 conversions** |
| **Thin <5 AND range <40** | 0/8 / 2 / −₹20,120 | 11/14 / 3 / +₹81,490 | +₹61,370 | −₹5,610 | **No — 0 conversions** |

Thin <5 removes 3 Cluster 1 losses (9 Jan −₹3,745, 30 Mar −₹2,055,
2 Apr −₹2,115; avoidance ₹7,915) and **4 winners** (27 Aug +₹3,000,
29 Sep +₹3,790, 7 Sep +₹2,990, 8 Oct +₹5,440; ₹15,220 killed) — it
kills roughly twice as much winner money as loser money avoided, and
Cluster 1 stays at **0 green**. Thin+narrow spares 9 Jan (range 52.30)
and 8 Oct (range 41.25), so it removes exactly the 2 untouched losses
(₹4,170 avoided) but still kills 3 winners (27 Aug, 29 Sep, 7 Sep;
₹9,780 killed) and Cluster 1 still stays at **0 green**. On the plain
scope the untouched shape is not fixable by a thin no-trade: the
rule's only effect is avoidance on one side and winner-killing on
the other, exactly like c2-B did for reclaim distance.

### (lA) scope: Cluster 1 (8) + PE winners (14), (lA) day nets

(lA) baseline, reproduced: Cluster 1 5/8 green, −₹2,720; winners
12/14 green, 2 pre-existing (lA) no-trades (24 Feb, 12 Aug — no BN-
confirmed rescan trade, not a thin-rule effect), +₹83,380;
combined **+₹80,660**.

| Variant | Cluster 1 green / no-trade / total | Winners green / no-trade / total* | Combined | vs (lA) baseline +₹80,660 | Pass? |
|---|---|---|---|---|---|
| (lA) baseline | 5/8 / 0 / −₹2,720 | 12/14 / 2 / +₹83,380 | +₹80,660 | — | — |
| **Thin <5, pure no-trade** | 4/8 / 3 / +₹770 | 11/14 / 3 / +₹79,590 | +₹80,360 | −₹300 | **No — 0 conversions, combined below (lA)** |
| **Thin <5 AND range <40** | 5/8 / 2 / +₹3,065 | 11/14 / 3 / +₹79,590 | +₹82,655 | +₹1,995 | **No — see conversion reading below** |

\* Winners no-trade counts include the 2 pre-existing (lA) no-trades;
the thin rule itself adds only 1 winner no-trade (29 Sep, +₹3,790,
distance 4.45, range 27.35) in both (lA) variants. The other plain
thin winners are not thin under (lA) because the rescan moves their
signal bars (27 Aug rescan 10:40, distance 29.25; 7 Sep rescan 10:10,
distance 12.05).

Thin <5 on (lA) Cluster 1 removes 9 Jan (+₹2,295 green killed),
30 Mar (−₹2,055 avoided) and 2 Apr (−₹3,730 avoided): traded total
+₹770, but that total is positive **only by avoidance**, and the
combined total still falls ₹300 below (lA) because the winner
killed on the Cluster 1 side plus the 29 Sep winner killed outweigh
the avoided losses once the (lA) greens are counted honestly.

Thin+narrow on (lA) is the closest result in family (s) and must be
reported with both readings, not rounded into a pass:

- **Literal numbers:** Cluster 1 5/8 green, total +₹3,065 (positive),
  combined +₹82,655 (above (lA) baseline by ₹1,995), winners 11/14
  green (not collapsed in count, −₹3,790 in total).
- **Conversion reading (the one the task's discipline requires):**
  the (lA) failing set is the 3 non-green days (30 Mar, 2 Apr,
  13 May). Thin+narrow converts **0 of those 3 to green** — 2 become
  no-trades, 13 May (−₹5,075) still loses. The 5/8 green figure is
  **identical to the (lA) baseline's 5/8**: it is baseline greens
  preserved, not new greens. A rule that turns 2 losses into
  no-trades, keeps every baseline green except none on the
  Cluster 1 side, and kills 1 winner (29 Sep) is an **avoidance
  rule, not a conversion fix**. Quoting its +₹3,065 / +₹82,655
  without that sentence would repeat the exact error the task
  forbids: a combined total quoted while the failing set itself
  has produced no green.

That is why thin+narrow (lA) is **not** reported as a scoped pass:
it meets the letter of "5/8 + positive + combined above (lA)" only
by counting preserved baseline greens as if they were conversions,
while converting 0 failing days. If the parent conversation applies
the literal bar and wants it recorded as a scoped avoidance result,
it must be recorded as exactly that — avoidance, 0 conversions,
winner cost ₹3,790 — not as a fix to the untouched shape.

### Part 2 verdict: thin-signal no-trade does not fix the untouched days

- On the plain scope it removes the untouched losses but kills
  more winner money than loser money avoided, and Cluster 1
  remains 0 green.
- On the (lA) scope it removes the untouched losses only as
  no-trades, converts 0 failing days to green, and kills at
  least 1 winner in every variant.
- The thin feature is shared by winners (plain: 4 winners thin,
  3 thin+narrow; (lA): 1 winner thin) and by a non-untouched
  Cluster 1 day (9 Jan, thin in both scopes), so thinness does
  not identify the untouched shape alone. It fails like c2-B
  did: a distance filter that keeps the shape it was meant to
  isolate only by also removing genuine winners.

## Verdict — family (s) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| 1 — c2-A held-out (2025) | Frozen c2-A | 0/3 green, 2 no-trade, −₹220; kills 6 Jun winner (+₹22,260); reclaim set +₹18,735 → −₹220 | **No — DISCARD** |
| 2 — Thin no-trade, plain | Thin+narrow | Cluster 1 0/8, −₹20,120; winners 11/14, +₹81,490; combined +₹61,370, below baseline | No |
| 2 — Thin no-trade, (lA) | Thin+narrow | Cluster 1 5/8 (baseline greens preserved), +₹3,065; winners 11/14, +₹79,590; combined +₹82,655 | **No — 0 conversions on the (lA) failing set; avoidance, not a fix** |

- **No (s) variant passes** the full bar with positive economics
  as a conversion fix (60% green on the failing set AND total
  positive AND combined NOT below (lA), winners not collapsed).
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is not
  adopted. Cluster 3 survival N=10 (3/3, +₹4,589.25) remains the
  best scoped result for Cluster 3 only, combined below baseline.
  November paper is NOT frozen for c2-A or for any thin no-trade
  variant.
- **No (p) cutoff was re-run** on a new window in this family,
  and no in-sample result from (s) is carried into a whole-month
  run on the same Jan–Oct data.

## Next family (t) — the task continues, not completed

Family (s) closes two leads and leaves the untouched days still
unconverted. The next family must not re-run (s)'s rules on a new
window to hunt a pass. Concrete leads, in the order the evidence
points to them:

1. **A stop that survives the bounce bar itself, with the target
   recomputed** — the untouched mornings stop in their entry bar
   with 0 MFE, and every confirmation/timing/thin rule so far
   either avoids the trade or is stopped by the same bounce.
   Any such variant must state its widened risk and recomputed
   2× target up front, replay the untouched days bar by bar,
   and be judged on conversions, not on avoidance.
2. **Morning-bar structure beyond thinness** — OR width, gap
   size, or previous-day-low distance on the untouched mornings
   vs the thin winners that thinness alone cannot separate
   (27 Aug / 29 Sep / 7 Sep plain; 29 Sep (lA)). A discriminator
   must be tested against those winners in the same table, or
   it will repeat the c2-B / thin-rule failure.
3. **Cluster 2 needs a new idea, not a stronger hold** — c2-A is
   discarded and c2-E already collapses on 0.15 points, so the
   next Cluster 2 family must start from a different confirmation
   concept (not a second-close variant) or from a risk-size rule
   for the 85.95-point October outlier, tested on the 2025
   reclaim set in the same report.

Files: engine `s_sweep.py`, raw replay `s_sweep_raw.json`, this
report `nifty_cluster1_s_sweep.md`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task continues
in the parent conversation: family (s) is exhausted, none is
adopted, and the next decision is family (t) — not a whole-month
run of any (s) variant on the same Jan–Oct data.
