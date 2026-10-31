# NIFTY — Family (q): out-of-sample validation of (p) passing variants — FAILS, (p) joins (o) as in-sample only
## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion, and (p) is NOT adopted.

## Task and frozen definitions (no re-tuning on this window)

Family (p) passed in-sample (Jan–Oct 2026, Cluster 1 + 14 PE winners) with
(p5) time0945 highBE: Cluster 1 6/8, +₹4,832.50, winners +₹82,422.50,
combined +₹87,255 (+₹6,595 vs (lA)); (p4) time1000 highBE: 6/8, +₹4,832.50,
winners +₹78,847.50, combined +₹83,680; (p8) time1000 closeMid: 6/8,
+₹6,091.25, winners +₹78,847.50, combined +₹84,938.75.
Reference (lA) in-sample combined: +₹80,660 (Cluster 1 −₹2,720 + winners
+₹83,380). Nothing was adopted on that in-sample pass: cutoffs came from
a small pre-defined set (09:45 / 10:00 / 10:30) after partial trigger times
were visible, and (p5) is in substance a near-no-partial rule (only
13 May + 29 Sep partialled in-sample).

(q) runs (p5), (p4), (p8) EXACTLY as defined in
`nifty_cluster1_morning_partial_p_sweep.md`, cutoffs FROZEN, on unseen
data — no cutoff, trail, or partial change was made on this window:
- (p5): partial50 at 1.0×risk, trail = entry on intra-bar high, ONLY if
  the partial trigger bar time < 09:45; later partials are plain trades.
- (p4): same highBE trail, cutoff < 10:00.
- (p8): partial50 at 1.0×risk, trail = entry − 0.5×risk on 5-min CLOSE,
  cutoff < 10:00.
Morning in all variants = (k) BN-confirmed rescan morning as in (p);
re-entry, if any, is the (lA) plain re-entry scan, and runs ONLY if the
morning final exit is a stop — exactly as in (p). Entry = next bar open,
stop = signal high, target = entry − 2×risk, square-off 15:10,
100 shares equivalent, ₹40/trade. Green = net > ₹0. No-trade counted
separately from green throughout.

## Out-of-sample window — what it is, and what it is not

Window: `morning_bar_universe.json`, `in_sample == False` — 92 Nifty PE
days, replayed bar by bar from the Upstox 5-min cache with the (p)
engine (`q_outofsample_sweep.py`, raw `q_outofsample_sweep_raw.json`).
65 days in 2025, 27 days in 2026, none of them in the Cluster 1 (8 days)
or winners (14 days) in-sample set. Mode per day is the universe mode
(v4, or skill where the universe says skill).

This window is held-out for the (p) cutoffs — the cutoffs were not fitted
on these 92 days — but it is NOT forward-in-time: 65 of the days pre-date
the Jan–Oct 2026 fitting window. It is therefore a genuine unseen-data
test of the cutoff rule, but it does not replace a forward November 2026
paper run for any future candidate. November 2026 has not happened;
no November results are claimed anywhere in this report, and no
November spec is frozen for (p) — see below.

## Pass bar, translated to a unified OOS window

In-sample the bar was Cluster 1 green ≥60% AND Cluster 1 total positive
AND combined NOT below (lA) on the same window, winners not collapsed.
On this OOS window there is no Cluster 1 / winner split — the 92 days
are all PE days — so the bar is applied to the whole traded set, with
the winner/loser split taken under (lA) itself:
1. Green ≥60% of TRADED days (no-trade separate, not counted as green).
2. Total positive.
3. Total NOT below (lA) total on the same 92 days.
4. (lA)-winners not collapsed: (lA)-green days stay green in count,
   and their total does not collapse.
A variant must pass ALL four legs. Passing total alone is not a pass.

## Headline — (q) FAILS for all three variants. (p) is in-sample only.

| Variant (frozen) | Traded / no-trade | Green | Green rate (traded) | Total (₹) | vs (lA) total | Pass? |
|---|---|---|---|---|---|---|
| (lA) baseline, same window | 74 / 18 | 39 | 52.7% | +35,570 | — | — |
| **(p5) time0945 highBE** | 74 / 18 | 39 | 52.7% | +34,685 | −₹885 | **NO — green <60%, total below (lA)** |
| **(p4) time1000 highBE** | 74 / 18 | 41 | 55.4% | +47,952.50 | +₹12,382.50 | **NO — green <60%** |
| **(p8) time1000 closeMid** | 74 / 18 | 41 | 55.4% | +51,546.25 | +₹15,976.25 | **NO — green <60%** |

On the stricter denominator (all 92 days, no-trade counted as not green)
the rates are lower still: (lA) 42.4%, (p5) 42.4%, (p4)/(p8) 44.6%.
No variant is anywhere near 60% on either denominator.

The more damning framing, in the task's own terms (failing trades turned
green): under (lA) there are 35 traded losing days on this window.
- (p5) converts **0/35** losers to green.
- (p4) converts **2/35 (5.7%)** losers to green.
- (p8) converts **2/35 (5.7%)** losers to green.
The in-sample Cluster 1 conversion (6/8, via one day, 13 May) does not
generalise: out-of-sample, the time-gated partial almost never rescues
a losing day.

## Why each variant fails, day by day

### (p5) — the near-no-partial rule stays near-no-partial, and helps nobody
Partialled exactly **2 mornings** out of 74 traded days — the same
narrowness as in-sample (2 mornings there too):
- 2025-09-26, partial 09:35: (lA) day +₹690 → (p5) +₹630 (Δ −₹60).
- 2026-09-28, partial 09:35: (lA) day +₹3,260 → (p5) +₹2,435 (Δ −₹825).
Both partialled mornings were ALREADY green under (lA); both shrink.
No losing day is partialled, no losing day converts, and the total
falls ₹885 below (lA). (p5)'s in-sample gain (+₹6,595) was 13 May's
+₹7,552.50 swing minus 29 Sep's −₹957.50 shrinkage; out-of-sample there
is no 13 May, so there is no gain at all. (p5) fails legs 1 and 3.

### (p4) — total passes, green does not; the gain is two days, not a conversion
Partialled 10 mornings. Changed days vs (lA) (all 10):
- Conversions (loser → green): 2025-01-10, partial 09:55, (lA) −₹11,985
  → (p4) +₹3,117.50 (Δ +₹15,102.50); 2026-06-30, partial 09:45,
  (lA) −₹1,155 → (p4) +₹517.50 (Δ +₹1,672.50).
  - 2025-01-10 is the only large conversion, and its mechanism matters:
    under (lA) the morning stopped (−₹6,355) and the re-entry also
    stopped (−₹5,630); under (p4) the morning partialled and exited at
    breakeven, so the day closed and no re-entry ran. The partial did
    not fix an entry — it avoided a second loss by closing the day.
- Loss shrunk but still a loss: 2026-04-09, partial 09:55,
  (lA) −₹2,045 → (p4) −₹40 (Δ +₹2,005) — still not green.
- Winner shrinkage (already green, now smaller): 2025-02-12
  +₹9,960 → +₹7,460 (Δ −₹2,500); 2025-04-25 +₹5,640 → +₹4,220
  (Δ −₹1,420); 2026-02-27 +₹3,340 → +₹2,495 (Δ −₹845);
  2026-08-11 +₹3,010 → +₹722.50 (Δ −₹2,287.50); 2026-09-28
  +₹3,260 → +₹2,435 (Δ −₹825).
- One winner improved: 2025-05-20 +₹460 → +₹2,000 (Δ +₹1,540).
  The remaining partialled day, 2025-09-26, shrinks like (p5):
  +₹690 → +₹630 (Δ −₹60).
Net: +₹12,382.50 over (lA), but 33 of 35 (lA)-losers still lose, and
green rises only 39 → 41. (p4) passes legs 2 and 3, fails leg 1.

### (p8) — best total, same green failure
Partialled the same 10 mornings as (p4) (same cutoff, closeMid trail
instead of highBE). Differences vs (p4):
- 2025-01-10: +₹4,696.25 (Δ +₹16,681.25 vs (lA)) — mid-close pays more
  than BE on the same conversion.
- 2025-05-20: +₹3,020 (Δ +₹2,560); 2025-09-26: +₹965 (Δ +₹275, the only
  partialled winner that improves under closeMid); 2026-06-30: +₹796.25
  (Δ +₹1,951.25); 2026-08-11: +₹1,103.75 (Δ −₹1,906.25, less shrinkage
  than (p4)'s −₹2,287.50).
- All other partialled days identical to (p4).
Net: +₹15,976.25 over (lA), green still 41/74 (55.4%). (p8) passes legs
2 and 3, fails leg 1 — same verdict as (p4), with a larger total driven
by the same single large day (2025-01-10).

## Winners not collapsed — in count, not in value

Split by (lA) outcome on the same window (traded days only):
- (lA)-winners: 39 days, (lA) total +₹184,820.
  - (p5): 39/39 stay green, total +₹183,935 (Δ −₹885).
  - (p4): 39/39 stay green, total +₹178,422.50 (Δ −₹6,397.50).
  - (p8): 39/39 stay green, total +₹180,158.75 (Δ −₹4,661.25).
  No winner flips to a loss under any (p) variant — leg 4 passes in
  count — but every (p) variant shrinks the winner total, because every
  partialled winner except 2025-05-20 / 2025-09-26 (p8) pays the
  50×risk target shrinkage. The winner side is not rescued by (p);
  it is taxed by it, and the tax is only outweighed when a large
  loser-conversion happens to occur (2025-01-10).
- (lA)-losers: 35 days, (lA) total −₹149,250.
  - (p5): total −₹149,250 (unchanged), 0 green.
  - (p4): total −₹130,470, 2 green.
  - (p8): total −₹128,612.50, 2 green.

## Split by year (for the record, not a new pass bar)

| Window | (lA) green / traded, total | (p5) | (p4) | (p8) |
|---|---|---|---|---|
| 2025 (54 traded) | 26, +₹7,420 | 26, +₹7,360 | 27, +₹20,082.50 | 27, +₹23,016.25 |
| 2026 OOS (20 traded) | 13, +₹28,150 | 13, +₹27,325 | 14, +₹27,870 | 14, +₹28,530 |

The 2026 OOS subset alone is 14/20 = 70% green under (p4)/(p8), but
that is 20 traded days, its total is barely above (lA) (+₹380 for
(p8)), and it does not change the full-window verdict — splitting
after the fact to find a passing subset would be exactly the
in-sample selection error (q) exists to prevent. It is reported here
only so it is not later quoted out of context.

## Guardrails checked

- Single-trade share: the largest single day total on this window is
  2025-02-14, +₹15,690 (a plain target, untouched by any partial).
  That is 44.1% of the (lA) total, 45.2% of (p5), 32.7% of (p4),
  30.4% of (p8) — under the 50% guardrail in every variant, so the
  guardrail does not fail any variant; the green leg fails them.
- No-trade count is identical (18) across (lA), (p5), (p4), (p8):
  the partial rule does not create or remove rescan trades, it only
  changes exits on traded days. No-trade is never counted as green.
- No cutoff was moved, no trail was changed, and no day was dropped
  to improve a variant's numbers. (p7) was not re-run out-of-sample:
  it was identical to (p4) in-sample, and (q)'s brief names (p5),
  (p4), (p8) as the variants to validate; (p7) would add nothing
  beyond (p4) on this data's logic, and re-running it to hunt a
  passing variant would be re-tuning by selection.

## November 2026 paper — NOT frozen for (p)

Because (q) fails, (p) is NOT frozen into a November paper spec.
The existing preparation-only spec
(`nifty_november2026_paper_spec_combined.md`) remains preparation
only, and (p5)/(p4)/(p8) must NOT be added to it as candidates.
If a November paper run is later prepared for a NEW family, it must
be written into that spec BEFORE its first November trade is scored,
with the new family's thresholds frozen at that point — not carried
over from (p)'s in-sample cutoffs. November has not happened; no
November day, trade, or result is claimed in this report.

## Verdict and next step — task continues, not completed

- **(p5): FAIL out-of-sample** — 52.7% green, total below (lA),
  0/35 losers converted. Joins (o) as in-sample only.
- **(p4): FAIL out-of-sample** — 55.4% green, total above (lA),
  2/35 losers converted. Joins (o) as in-sample only.
- **(p8): FAIL out-of-sample** — 55.4% green, total above (lA),
  2/35 losers converted. Joins (o) as in-sample only.
- Previous best kept is still (lA) on Cluster 1 economics
  (−₹2,720, 5/8) with winners intact — and (lA) itself is not
  adopted either.
- Next family, as instructed in (p): return to the two untouched
  Cluster 1 days (30 Mar, 2 Apr — no partial, re-entry unchanged,
  in every (o) and (p) variant) and to Clusters 2/3 on their own
  terms (reclaim confirmation for Cluster 2, trail/partial exit
  for Cluster 3) — WITHOUT claiming Cluster 1 is fixed, and
  without re-running (p) cutoffs on a new window to hunt a pass.

Files: engine `q_outofsample_sweep.py`, raw replay
`q_outofsample_sweep_raw.json`, this report
`nifty_cluster1_p_outofsample_sweep.md`. Paper only throughout;
no orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: family (q) is exhausted
(all three (p) passing variants fail out-of-sample), none is
adopted, and the next decision is the untouched-days /
Clusters 2/3 family — not a whole-month run of (p5) on any data.
