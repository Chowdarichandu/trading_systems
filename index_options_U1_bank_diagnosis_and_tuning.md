# U1 Bank Nifty — why it was negative, and tuning to close index work

Index OPTIONS only, paper only, no orders, no stocks. Nifty shown only as control.
Window: 1 Jan – 28 Oct 2026 (203 trading days; October = 1–28 Oct only).
**Real money = ₹0 throughout. Nothing adopted on in-sample alone.**
Units warning: Jan–Sep legs are **spot provisional** (points × 100 shares − ₹40, NOT an options-lot profit, NOT a futures profit);
October legs are **option premiums per 1 lot** (−50/+90 overlay, ₹220 cost, Bank lot 30, Nifty lot 65).
Jan–Oct totals below are therefore **MIXED totals, labelled as such — never a pure premium total**.
Source: `index_options_U1_janoct_trades.csv` (362 unique U1 keys), `index_options_U1_skillV3_jansep_spot.csv`,
`index_options_skill_tuned_oct30_trades.csv` (October premiums).

## PART 1 — DIAGNOSIS: why U1 Bank is negative

### Headline — verified, and the earlier hint was right, but understated
- U1 Bank Jan–Oct: **183 trades, 4.51/week, 26.2% full-target, −₹158,955 mixed**
  - Jan–Sep spot: 165 trades, −₹169,995, 23.0% FT
  - October premiums: 18 trades, +₹11,040, 55.6% FT — October is the outlier, not the norm.
- U1 Nifty (control): 179 trades, 4.41/week, 36.3% FT, +₹109,320 mixed — Bank is not a whole-U1 failure, it is a Bank-specific failure.
- **Verdict: it is ONE bad component, in ONE direction, concentrated in solo (unconfirmed) legs — not broad.**
  It is not (lA), V5, or Volrix failing, and it is not PE failing. It is Skill V3 Bank CE.

### By representative component (U1 Bank, Jan–Oct mixed)
| Representative | Trades | Net mixed | Full-target |
|---|---|---|---|
| Skill V3 | 128 | −₹170,750 | — |
| V5 v2 | 21 | −₹19,680 | — |
| (lA) v2 | 21 | +₹5,475 | — |
| Volrix (b) | 13 | +₹26,000 | 0* |
| **Total** | **183** | **−₹158,955** | **26.2%** |

\* Volrix (b) spot legs use day_green/day_loss exits in the Jan–Sep spot file, so its full-target flag is 0 even on winning legs — its FT is not comparable. Its net is what matters: positive.
Jan–Sep alone, representative: Skill V3 −₹171,110 (116 trades), V5 −₹27,120 (18), (lA) +₹4,715 (19), Volrix +₹23,520 (12).
So Skill V3 representative alone (−₹171,110) is larger than the whole Bank loss — (lA)+Volrix (+₹28,235 Jan–Sep) partly offset it, V5 adds a smaller loss. The earlier "−₹171,110 representative" hint is **verified**.

### By direction (U1 Bank, Jan–Oct mixed)
| Direction | Trades | Net mixed | Full-target |
|---|---|---|---|
| CE | 89 | −₹192,415 | 9 targets (10.1%) |
| PE | 94 | +₹33,460 | 29 targets (30.9%) |

CE loses almost 6× the total Bank loss; PE is positive. **Direction is the split, not a general Bank weakness.**

### Skill V3 standalone (Jan–Sep spot, 150 Bank legs) — the smoking gun
| Skill V3 Bank | Trades | Net spot | Full-target |
|---|---|---|---|
| CE (OR breakout) | 74 | −₹150,390 | 12 (16.2%) |
| PE (OR breakdown) | 76 | −₹8,480 | 26 (34.2%) |
| **All** | **150** | **−₹158,870** | **38 (25.3%)** |

Skill V3 Bank CE alone is −₹150,390 — 95% of its standalone loss, on half its trades.
By entry time (Skill V3 standalone):
- CE early (entry ≤09:55): 51 trades, −₹161,635. CE late (≥10:00): 23 trades, +₹11,245.
- PE early: 43 trades, −₹47,830. PE late: 33 trades, +₹39,350.
- All early (≤09:55): 94 trades, −₹209,465, 19 FT. All late (≥10:00): 56 trades, +₹50,595, 19 FT.
So the losing Skill leg is specifically **early-morning OR-breakout CE** — the first close above the opening range, taken at 09:35–09:55, which then stops out. That is a setup + timing failure, not "Bank Nifty doesn't work".

### Solo vs confirmed — the second split
U1 Bank legs by source (Jan–Sep):
- Skill V3 **solo** (no other system gave the same key): 101 trades, **−₹252,115**.
- Multi-system (confirmed) keys: 50 trades, **+₹78,605** (Jan–Sep; +₹82,120 in the solo-drop variant including October effects — see Part 2).
- Non-Skill keys: 15 trades, +₹27,735.
In other words: **when Skill V3 Bank is alone, it loses badly; when another system confirms the same date+direction, the key wins.** October repeats this pattern in miniature: Skill-solo Bank legs −₹400 (10 legs), multi legs +₹4,000, non-Skill legs +₹9,920.

### By month (U1 Bank, mixed)
Jan −₹65,870 · Feb −₹37,685 · Mar +₹52,490 · Apr −₹41,930 · May +₹47,150 · Jun −₹66,725 · Jul −₹46,995 · Aug −₹46,815 · Sep +₹36,385 · Oct +₹11,040 (premiums).
Only Mar, May, Sep, Oct are green months; cumulative is negative at every month-end except none — it never turns positive Jan–Oct. Skill V3 Bank standalone by month: Jan −₹90,030 (worst), Jul −₹44,800, Aug −₹53,375 are the deep holes; Mar +₹24,350, May +₹19,150, Sep +₹25,375 are its only green months.

### Exit profile (U1 Bank, Jan–Oct)
Stops: 107 legs, −₹830,985 gross. Targets: 54 legs, +₹696,140 gross. Square-offs: 8 legs, +₹63,455.
Day_loss (Volrix/(lA) spot day exits): 11 legs, −₹97,445. Day_green: 3 legs, +₹9,880.
It is a stop-heavy system on Bank: 58% of legs stop out, and the average stop is larger than the average target in spot points (Bank spot moves are large; the provisional spot scale exaggerates this vs option lots — another reason Jan–Sep spot rupees must not be read as option-lot rupees).

### Largest losing U1 Bank legs (mixed; all spot except October)
1. 2026-06-29 PE, (lA)+Skill+V5, day_loss, −₹24,935
2. 2026-03-16 CE, Skill solo, stop, −₹24,160
3. 2026-04-01 PE, Skill+V5, stop, −₹23,515
4. 2026-09-17 CE, Skill solo, stop, −₹20,190
5. 2026-04-09 PE, Skill solo, stop, −₹17,400
6. 2026-01-27 CE, Skill solo, stop, −₹17,145
7. 2026-02-03 PE, Skill solo, stop, −₹16,805
8. 2026-05-13 PE, Skill solo, stop, −₹16,580
9. 2026-06-04 CE, Skill solo, stop, −₹16,285
10. 2026-03-20 CE, Skill solo, stop, −₹15,690
No single leg explains the loss — it is ~100 losing Skill-solo legs, mostly stops, not one blow-up. (The 29 Jun day_loss leg is the largest single leg but is a confirmed key, not a Skill-solo leg.)

### Plain diagnosis
**Bank is negative because Skill V3 Bank OR-breakout CE, taken early (09:35–09:55) and unconfirmed by any other system, loses repeatedly and stops out.**
(lA) Bank and Volrix Bank are positive; PE is positive; confirmed keys are positive; October is positive. Remove the unconfirmed early Skill CE leg and Bank flips positive — that is exactly what Part 2 tests, frozen, one knob at a time.

## PART 2 — TUNING, frozen before scoring, one knob at a time

Frozen definitions (all Bank-only; Nifty stays U1 unchanged in every variant):
- **(a-strict)** U1 Bank with NO leg that has Skill V3 in its source at all.
- **(a-solo)** U1 Bank with Skill-V3-solo legs removed; confirmed (multi-source) legs kept.
- **(b) = U1-B1** U1 Bank with Skill-V3-representative CE legs blocked (the losing setup: Skill OR-breakout CE).
  A key is dropped whole when Skill V3 was its earliest (representative) system and direction is CE.
  Caveat (conservative): if (lA)/V5/Volrix also signalled the same key later, that later entry is NOT in the U1 CSV and is NOT scored here — November paper must log the actual later entry if one fires, so (b) may understate November frequency/net.
- **(c1)** Setup filter = (b): for Skill, direction IS setup (CE = OR breakout, PE = OR breakdown), so dropping the losing setup is identical to (b) — shown to prove convergence, not as a separate claim.
- **(c2-time)** Timing filter: drop Skill-representative legs with entry ≤09:55. **(c2-time-solo)**: drop Skill-solo legs with entry ≤09:55 only.
- **(d)** Replacement leg — NOT scored Jan–Sep, because (b)/(c2) already pass the stage bar (see below) and the task orders (d) only if (a)–(c) fail.
  For reference, October premiums only: Skill V9 Bank pullback = 7 legs, +₹4,760, 57.1% FT (4 targets); (lA) Bank RB widened band (RB1/RB2) October = +₹4,000, 60% FT, 1.39/week. Either could be a future single frozen replacement variant, but neither is claimed as a Jan–Oct fix here.

Stage pass rule (frozen): Bank Jan–Oct mixed net > ₹0 AND October premium net > ₹0 AND full-target improves vs U1 Bank (26.2% Jan–Oct / 55.6% Oct) WITHOUT frequency collapsing below 2/week.

### Results — Bank only (Jan–Oct mixed + October premiums alone)

| Variant | Jan–Oct trades | Jan–Oct net mixed | Jan–Oct FT | Jan–Oct /week | Oct trades | Oct net premium | Oct FT | Oct /week | Pass? |
|---|---|---|---|---|---|---|---|---|---|
| U1 Bank base | 183 | −₹158,955 | 26.2% | 4.51 | 18 | +₹11,040 | 55.6% | 5.00 | No (net) |
| (a-strict) no Skill in source | 19 | +₹37,655 | 36.8% | 0.47 | 4 | +₹9,920 | 100% | 1.11 | **No — frequency collapses** |
| (a-solo) drop Skill-solo only | 72 | +₹93,560 | 33.3% | 1.77 | 8 | +₹11,440 | 75.0% | 2.22 | **No — Jan–Oct frequency 1.77 < 2** |
| **(b) U1-B1: block Skill-rep CE** | **110** | **+₹48,095** | **32.7%** | **2.71** | **10** | **+₹12,200** | **70.0%** | **2.78** | **YES — passes all stage bars** |
| (b2) block Skill-solo CE only | 111 | +₹40,545 | 32.4% | 2.73 | 10 | +₹12,200 | 70.0% | 2.78 | Yes (near-identical to (b)) |
| (c1) setup = (b) | 110 | +₹48,095 | 32.7% | 2.71 | 10 | +₹12,200 | 70.0% | 2.78 | Yes (same as (b)) |
| (c2-time-solo) drop Skill-solo ≤09:55 | 111 | +₹87,120 | 32.4% | 2.73 | 10 | +₹16,400 | 80.0% | 2.78 | Yes — highest net, timing-based |
| (c2-time) drop Skill-rep ≤09:55 | 100 | +₹28,055 | 30.0% | 2.46 | 9 | +₹13,920 | 77.8% | 2.50 | Yes |

Reading: (a-strict) proves confirmed legs alone are profitable (+₹37,655) but far too few (0.47/week) — confirmation alone is not a system. (a-solo) proves the solo-leg problem (+₹93,560 without them) but still thins frequency below 2/week Jan–Oct. (b) is the first variant that keeps frequency (2.71/week) while flipping net and lifting FT on both windows.

### U1-B1 month-by-month (mixed; October premiums)
Jan −₹17,120 · Feb −₹13,390 · Mar +₹110,660 · Apr −₹41,095 · May +₹52,340 · Jun −₹35,805 · Jul −₹38,575 · Aug −₹26,160 · Sep +₹45,040 · Oct +₹12,200 (premiums).
Cumulative: Jan −₹17,120 → Feb −₹30,510 → Mar +₹80,150 → Apr +₹39,055 → May +₹91,395 → Jun +₹55,590 → Jul +₹17,015 → Aug −₹9,145 → Sep +₹35,895 → Oct +₹48,095.
**Warning, plainly:** U1-B1 passes the stage bar but does NOT rise month by month — it dips negative again in August, and March (+₹110,660, a single month larger than the whole Jan–Oct total) dominates it. It is a stage pass, not a proven system. The March concentration and the August dip are exactly what November paper must disprove.

### Best variant — U1-B1 (Bank) + U1 (Nifty)
- **Name: U1-B1** — U1 with Skill V3 Bank OR-breakout CE blocked. Nifty component unchanged (U1 Nifty: 179 trades, 36.3% FT, +₹109,320 mixed — still fails FT/progression on its own, see U1 report; Bank tuning does not fix Nifty).
- Trades file: `index_options_U1_B1_bank_trades.csv` (110 Bank legs; Nifty legs are the unchanged U1 Nifty legs in `index_options_U1_janoct_trades.csv`).
- **Do NOT stack (b) + (c2-time-solo)** — that combination was not scored and must not be quoted. If it is wanted, it is a new frozen variant, scored separately.

## FINAL VERDICT — can index work be closed?

**No — not closed to adoption, but closed to a frozen November-paper candidate, which is the next step.**
- Why Bank was negative: **Skill V3 Bank early OR-breakout CE, unconfirmed — verified, not a guess** (−₹150,390 standalone CE; early CE −₹161,635; solo legs −₹252,115 Jan–Sep).
- What fixes it at stage level: **U1-B1 (block Skill Bank CE)** — Bank Jan–Oct +₹48,095 mixed, October +₹12,200 premiums, FT 32.7% / 70.0%, 2.71 / 2.78 per week. A timing alternative (c2-time-solo, +₹87,120 / +₹16,400) also passes but is a different knob — pick one for November, not both. Recommended: **U1-B1**, because it follows the diagnosis (setup/direction), not just the clock.
- What remains open before any adoption claim:
  1. U1-B1's March concentration and August dip — November paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November) must show it does not need one big month.
  2. The conservative-drop caveat: November logging must record later (lA)/V5/Volrix entries on Skill-CE-blocked days, not assume no-trade.
  3. Nifty hit quality (36.3% Jan–Oct) is still short of 50% — Bank tuning does not close the Nifty leg.
  4. Jan–Sep is spot provisional, not premiums — a pure-premium Jan–Oct U1-B1 total does not exist yet and must not be invented.
- **November paper spec (frozen for this handoff):** Bank = U1-B1 exactly as defined above; Nifty = U1 exactly; log every signal, blocked Skill-CE day, and later-entry replacement separately; no scoring/re-tuning during November; month-end review only. Only a November pass on net + full-target + frequency together, per index separately, can move U1-B1 toward adoption.
