# Toward the weekly target — index OPTIONS, October 2026

**User requirement, 2026-10-30 12:27 IST:** not the exclusive-only ₹5,654 total, and not 8 trades for ₹5,000. He wants 2–3 quality trades per week with a meaningful monthly total — in the range he was interested in, roughly ₹20,000–₹38,000 on a unique-counted basis. The ₹38,048 literal sum was double-counted and is NOT the target to chase by double-counting.

**Counting rule for this task — UNIQUE-ONCE:** each date + index + direction signal counted ONCE (earliest entry). Duplicates are NOT deleted (that was the rejected exclusive-only rule) and NOT counted twice (that was the literal sum).

**Scope:** index OPTIONS only, paper only, no orders, no stocks, no live trading. October 2026, 1–28 Oct, 18 trading days = 3.6 weeks. Overlay for all variants: stop entry −50, target entry +90 option points, square-off 15:10, ₹220 cost per trade, Nifty lot 65, Bank lot 30. Real money = ₹0.

**Target bar, per index separately, never pooled in the verdict:** frequency 2–3 trades/week (read in the tables both as a strict band and as a minimum ≥2/week, because the base already exceeds 3/week), full-target ≥50%, net > 0, and combined unique-once total ≥ ₹20,000 for October as a checkpoint.

**Systems in the unified base:** (lA) v2 + V5 v2 + Skill V3 (CE no-block) + Volrix intraday (b) at −1.0%. V9 is NOT merged into Skill (merging V3 + V9 would double-count Skill itself).

## Variant 1 — single unified system (earliest signal per key)

Source: `index_options_toward_20k_variant1.md`, verified from the CSVs (44 legs fed in, 10 duplicate legs removed, literal sum ₹38,048.25, double-counting removed ₹12,838.50).

| Index | Trades | Trades/week | Full-target | Net / 1 lot |
|---|---|---|---|---|
| Nifty | 16 | 4.44 | 6/16 = 37.5% | +₹14,169.75 |
| Bank | 18 | 5.00 | 10/18 = 55.6% | +₹11,040.00 |
| Combined (arithmetic sum only) | 34 | — | 16/34 = 47.1% | +₹25,209.75 |

Verdict V1: combined clears ₹20,000 by ₹5,209.75, and frequency clears the ≥2/week minimum on both indices, but Nifty fails full-target (37.5% < 50%), so there is no clean all-legs pass. Under the strict 2–3/week band, both indices are also above the band (4.44 and 5.00) — frequency is already too high, not too low.

Caveat: the earliest-entry rule matters. On 26 Oct Nifty CE it picks the Skill V3 target (+₹5,630) over the later V5 stop (−₹3,470) on the same key — a ₹9,100 swing if the rule changed.

## Variant 2 — unified base + NS1 second legs (second signal/day)

Source: `index_options_toward_20k_variant23.md`. NS1 second legs alone: Nifty 5 trades, 1 target, −₹1,698.00; Bank 5 trades, 3 targets, +₹4,000.00. All 10 count (each differs from the base leg that day).

| Index | Trades | Trades/week | Full-target | Net / 1 lot |
|---|---|---|---|---|
| Nifty | 21 | 5.83 | 7/21 = 33.3% | +₹12,471.75 |
| Bank | 23 | 6.39 | 13/23 = 56.5% | +₹15,040.00 |
| Combined | 44 | — | 20/44 = 45.5% | +₹27,511.75 |

Verdict V2: Bank meets all four checks (frequency minimum, FT, net, combined). Nifty does NOT — FT falls to 33.3%. Adding second legs raises count and Bank net, but dilutes Nifty hit quality. Not a pass on both indices.

## Variant 3 — Variant 2 + NS2 afternoon legs

Source: `index_options_toward_20k_variant23.md`. Added legs: Nifty 01 Oct PE −₹3,135.25 (square-off), 14 Oct PE −₹3,470 (stop), 23 Oct PE −₹3,470 (stop); Bank 21 Oct PE +₹2,480 (target). Added alone: Nifty 3 trades, 0 targets, −₹10,075.25; Bank 1 trade, 1 target, +₹2,480.00.

Excluded double-count (NOT in the numbers): NS2 Nifty 21 Oct PE — signal 11:35, strike 22800, 151.30 → 241.30 target, +₹5,630.00 — identical in signal time, strike, direction, premiums and exit to base leg (lA) v2 Nifty 21 Oct PE. Wrongly adding it would give Nifty +₹8,026.50 and combined +₹25,546.50, flipping the combined check on a double-count alone.

| Index | Trades | Trades/week | Full-target | Net / 1 lot |
|---|---|---|---|---|
| Nifty | 24 | 6.67 | 7/24 = 29.2% | +₹2,396.50 |
| Bank | 24 | 6.67 | 14/24 = 58.3% | +₹17,520.00 |
| Combined | 48 | — | 21/48 = 43.8% | +₹19,916.50 |

Verdict V3: worse than V2 and worse than the base on combined net, despite the most trades. Nifty fails FT (29.2%) and the combined total fails ₹20,000 by ₹83.50. Afternoon legs hurt Nifty badly and help Bank only slightly. V3 is rejected.

## Variant 4 — hit-quality filters on NS1 second / NS2 afternoon legs

Source: `index_options_toward_20k_variant4.md`, legs in `index_options_toward_20k_variant4_legs.csv`, frozen scoring script `variant4_score.py`.

Note on base: Variant 4's base (V4B) counts all 15 extra legs (NS1 second + NS2 afternoon) without deduping the NS2 Nifty 21 Oct duplicate, so it is Nifty 25 / Bank 24 = 49 legs, not Variant 3's 48. Its filter verdicts are therefore reported against V4B, not against V3, and the two bases must not be mixed.

V4B unfiltered: Nifty 25 trades, 6.94/week, FT 8/25 = 32.0%, +₹8,026.50; Bank 24 trades, 6.67/week, FT 14/24 = 58.3%, +₹17,520.00. Extra legs unfiltered: Nifty 9 legs, FT 22.2%, −₹6,143.25; Bank 6 legs, FT 66.7%, +₹6,480.00.

Filters, each frozen before scoring, one at a time (full track = unified untouched + filtered extra legs):

- **(a-NS) first leg not a stop (NS-track reading):** Nifty keeps 1 extra leg (12 Oct target, +₹5,630) → full 17 trades, 4.72/week, FT 41.2%, +₹19,799.75. Bank keeps 1 extra leg (1 Oct stop, −₹1,720) → full 19 trades, 5.28/week, FT 52.6%, +₹9,320.00. Closest on Nifty, still below 50%, built on one leg, and it hurts Bank net by ₹8,200 vs base. Fail.
- **(a-T) first leg a target only:** Nifty keeps 0 extra legs → full = unified alone. Bank keeps the same 1 Oct stop leg → +₹9,320.00. Fail.
- **(b) spot room_ratio ≥ 2.0:** Nifty keeps 7 extra legs, FT 28.6%, −₹5,755.25 → full 23 trades, 6.39/week, FT 34.8%, +₹8,414.50. Bank keeps 4 extra legs, FT 75.0%, +₹5,720.00 → full 22 trades, 6.11/week, FT 59.1%, +₹16,760.00. Nearly inert; it drops a Bank target to save a stop, so Bank net falls below base. Fail.
- **(c) premium extension — keep iff entry premium ≤ 0.67 of the contract's premium range so far that day:** Nifty keeps 0 extra legs → full = unified alone. Bank keeps 1 leg (27 Oct PE target, +₹2,480) → full 19 trades, 5.28/week, FT 57.9%, +₹13,520.00. 14 of 15 entries sit above 0.67 (positions 0.717–0.990), so the gate is close to a ban on second/afternoon legs. Fail on frequency and, on Bank, on net.

Verdict V4: **no filter lifts FT to ≥50% while keeping net at or above base and frequency at or above 2/week on either index.** On Nifty no filter reaches 50% full-track FT (best 41.2%); on Bank the unfiltered base already passes FT and every filter that keeps FT above 50% drops net below base. No filter is adopted. At most, (a-NS) as frozen could be logged in November paper alongside the unfiltered track — that is not a claim.

Why second/afternoon legs hit poorly (consistent with Jan–Oct spot evidence: NS1 second legs 31.6% Nifty / 40.0% Bank): the extra legs are mostly late, extended entries — under filter (c), 14 of 15 sit in the top third of the day's premium range. The problem is entry quality, not count.

## Jan–Oct sanity check

No variant passes the bar on both indices on October premiums, so the task's condition for a Jan–Oct check (October passer first) is not met and no variant is put forward for adoption. The standing Jan–Oct spot picture for the extra legs (NS1 second legs 31.6% / 40.0%) already points the same way as October: second legs dilute Nifty hit rate. No Jan–Oct premium total is claimed here.

## Plain verdict

- **Frequency is NOT the problem.** The unified base already gives 4.44 (Nifty) and 5.00 (Bank) trades/week — above the user's 2–3/week, not below it. Adding NS1 second and NS2 afternoon legs pushes it to 5.83–6.67/week and makes Nifty worse.
- **Net in the user's range IS reachable on the unique-once basis, without double-counting:** Variant 1 combined +₹25,209.75, Variant 2 combined +₹27,511.75 — both in the ₹20,000+ range he was interested in, and both well above the rejected exclusive-only ₹5,654.50.
- **What is still short is Nifty hit quality.** Nifty full-target is 37.5% (base), 33.3% (V2), 29.2% (V3) — short of 50% by 12.5, 16.7 and 20.8 points respectively. Bank passes FT in every variant (55.6% / 56.5% / 58.3%).
- **Best variant by the bar: Variant 2 on Bank only, Variant 1 overall.** Neither passes on both indices. Nothing is adopted on October alone; the next step is frozen November paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November), with (a-NS) at most as a shadow log alongside the unfiltered track.
- **Do NOT re-deliver the exclusive-only ₹5,654.50 as the answer** — the user rejected that counting rule. The honest October checkpoint numbers are +₹25,209.75 (unified, unique-once) and +₹27,511.75 (unified + NS1 second legs), paper only, real money ₹0.
