# U1 Bank Nifty — tuning to end in positive

Index OPTIONS only, paper only, no orders, no stocks. Bank Nifty ONLY in this
task; Nifty stays U1 unchanged as control and is not re-tuned here.
Window: 1 Jan – 28 Oct 2026 (203 trading days; October = 1–28 Oct only).
**Real money = ₹0 throughout. Nothing adopted on in-sample alone.**

## Units — read this first

Jan–Sep legs are **spot provisional** (points × 100 shares − ₹40, NOT an
options-lot profit, NOT a futures profit). October legs are **option premiums
per 1 lot** (−50/+90 overlay, ₹220 cost, Bank lot 30). Jan–Oct totals are
therefore **MIXED totals, labelled as such — never a pure premium total**.
A pure-premium Jan–Oct Bank total does not exist in this run and was not
invented.

## Frozen variants — one at a time, each named

Base for all: **U1 Bank** (183 trades, 4.51/week, 26.2% full-target,
−₹158,955 mixed; October 18 trades, +₹11,040 premiums, 55.6% FT).
Prior stage winner: **U1-B1** = U1 Bank with Skill V3 Bank OR-breakout CE
blocked (110 trades, 2.71/week, 32.7% FT, +₹48,095 mixed; October 10 trades,
+₹12,200 premiums, 70.0% FT). B1 drops 73 keys, all Skill-representative CE,
on 73 distinct dates ("blocked dates").

- **U1-B2 (stack, task item 1): U1-B1 + drop Skill-solo ≤09:55.** Start from
  B1, then additionally drop any remaining key where Skill V3 is the sole
  system (n_systems = 1) and entry_time ≤ 09:55. What this actually drops
  from B1: 21 legs, ALL PE (Skill-representative CE is already gone under
  B1, so the stack adds only early solo PE). Those 21 legs sum to
  −₹76,320, including one October leg: 12 Oct PE, Skill-solo 09:55, a
  premium stop −₹1,720 (dropping it is why B2 October net exceeds B1's).
  The stack is NOT identical to either parent: it is B1 minus 21 legs.
- **U1-B3 (task item 2): U1-B1 + Skill V9 pullback as replacement, blocked
  dates only.** V9 definition exactly as frozen in
  `index_options_skill_tuned_oct30_frozen.md` (base S1 + pullback entry,
  CE bearish block RETAINed, pullback bar strictly after the signal bar,
  ≤14:30, room/risk ≥ 1.5). V9 Jan–Sep spot legs were generated from the
  progressive spot cache with that exact definition and validated:
  October generation reproduces the tuned file's 7 Bank V9 legs exactly
  (dates, directions, spot nets, reasons). V9 Jan–Sep standalone: 78 legs,
  −₹37,690 spot, 30.8% FT — V9 itself is not positive Jan–Sep.
  Replacement rule: a V9 leg is added ONLY if its date is one of the 73
  blocked dates AND its (date, direction) key is not already in B1.
  Result: 27 Jan–Sep legs + 3 October legs added (30 total, no collisions).
  October additions are all premium stops: 6 Oct CE, 14 Oct CE, 27 Oct CE,
  each −₹1,720.
- **U1-B4 (task item 3): U1-B1 + (lA) Bank RB widened-band leg, blocked
  dates only.** RB1/RB2 add exactly ONE extra October leg over (lA) base:
  8 Oct re-entry PE, 13:40, premium +₹2,480. 8 Oct is NOT a blocked date
  (blocked October dates are 6, 9, 13, 14, 15, 21, 22, 27 Oct), so under
  the strict "blocked dates only" rule RB adds **0 legs in October**.
  Jan–Sep RB legs were NOT generated: (lA) Jan–Sep legs in the U1 CSV
  carry no entry spot / strike (day_loss/day_green scoring), so a
  from-scratch RB re-entry engine for Jan–Sep would be unverifiable
  against the existing (lA) legs and is not claimed. U1-B4 is therefore
  **identical to U1-B1** on the evidence available — reported, not hidden.
- **U1-B5 (task item 4a): confirmed-only Bank.** Keep only U1 Bank keys
  with n_systems ≥ 2 (multi-system confirmed). Single knob: confirmation.
- **U1-B6 (task item 4b): PE-only Bank.** Keep only U1 Bank PE keys
  (94 trades). Single knob: direction.

Pass bar for "ends in positive" in this task: Jan–Oct mixed net > 0 AND
October premium net > 0 AND full-target above U1 Bank base on BOTH windows
(26.2% Jan–Oct / 55.6% October) AND frequency ≥ 2/week on both windows.

## Results — Bank only

| Variant | Jan–Oct trades | Jan–Oct net mixed | Jan–Oct FT | Jan–Oct /week | Oct trades | Oct net premium | Oct FT | Oct /week | Pass? |
|---|---|---|---|---|---|---|---|---|---|
| U1 Bank base | 183 | −₹158,955 | 26.2% | 4.51 | 18 | +₹11,040 | 55.6% | 5.00 | No |
| U1-B1 (prior) | 110 | +₹48,095 | 32.7% | 2.71 | 10 | +₹12,200 | 70.0% | 2.78 | Yes |
| **U1-B2 (B1 + drop Skill-solo ≤09:55)** | **89** | **+₹124,415** | **36.0%** | **2.19** | **9** | **+₹13,920** | **77.8%** | **2.50** | **YES — best** |
| U1-B3 (B1 + V9 blocked only) | 140 | +₹66,780 | 30.0% | 3.45 | 13 | +₹7,040 | 53.8% | 3.61 | No — Oct FT 53.8% < 55.6% base |
| U1-B4 (B1 + RB blocked only) | 110 | +₹48,095 | 32.7% | 2.71 | 10 | +₹12,200 | 70.0% | 2.78 | Yes — identical to B1, no gain |
| U1-B5 confirmed-only | 55 | +₹82,605 | 34.5% | 1.35 | 5 | +₹4,000 | 60.0% | 1.39 | No — frequency < 2/week |
| U1-B6 PE-only | 94 | +₹33,460 | 36.2% | 2.32 | 8 | +₹7,240 | 62.5% | 2.22 | Yes — passes, but weaker than B2 |

### U1-B2 month-by-month (mixed; October premiums)

| Month | Month net | Cumulative |
|---|---|---|
| Jan | +₹13,830 | +₹13,830 |
| Feb | +₹9,095 | +₹22,925 |
| Mar | +₹97,790 | +₹120,715 |
| Apr | −₹14,375 | +₹106,340 |
| May | +₹68,920 | +₹175,260 |
| Jun | −₹50,510 | +₹124,750 |
| Jul | −₹10,365 | +₹114,385 |
| Aug | −₹26,160 | +₹88,225 |
| Sep | +₹22,270 | +₹110,495 |
| Oct (premiums) | +₹13,920 | **+₹124,415** |

Versus B1: B1 cumulative was negative at three month-ends (Jan −₹17,120,
Feb −₹30,510, Aug −₹9,145). **B2 cumulative is never negative at any
month-end** — that is the "fewer dips" improvement the task asked for.
Monthly declines still occur (Apr, Jun, Jul, Aug are negative months), so
it does not rise every month, but it never goes underwater cumulatively.

### March concentration — stated, not hidden

March (+₹97,790) is 78.6% of B2's Jan–Oct total. That is still a
concentration risk. The mitigating check: **B2 ex-March is still positive
at +₹26,625**, whereas B1 ex-March is −₹62,565. B2 does not need March to
stay positive in sign, even though March dominates its size. November
paper must still show B2 does not need one big month to stay green.

### Why B3 (V9 replacement) fails, and why B5/B6 do not beat B2

- B3: the 27 Jan–Sep V9 replacement legs net +₹23,845 spot but hit only
  6 targets (22.2%), and the 3 October replacements are all stops. Adding
  them lifts B1's Jan–Oct net (+₹48,095 → +₹66,780) but DILUTES
  full-target on both windows (Jan–Oct 32.7% → 30.0%; October 70.0% →
  53.8%, below base). A replacement that adds trades but lowers hit
  quality is not a fix.
- B5 confirmed-only is profitable (+₹82,605) and never cumulative-negative
  either, but at 1.35/week it is not a tradable weekly system under the
  user's 2–3/week requirement.
- B6 PE-only passes every bar but ends at only +₹33,460, below B1, and
  its cumulative dips negative in Jan, Feb and Aug.

### Stacking note (not a candidate)

A further stack, B2 + V9-on-blocked-dates (119 trades, +₹143,100 mixed,
31.9% FT, 2.93/week; October 12 trades, +₹8,760, 58.3% FT), was computed
as a check only. It stacks THREE knobs, worsens March concentration
(March month +₹156,310), and is NOT carried forward as a frozen candidate
under the one-variant-at-a-time discipline. It is mentioned here only so
it is not later quoted as if it were a scored variant.

## Best variant — U1-B2

- **Name: U1-B2** — U1 Bank, with Skill V3 Bank OR-breakout CE blocked
  (U1-B1) AND Skill-solo Bank legs with entry ≤09:55 dropped.
  In plain words: no unconfirmed early Skill Bank trade, in either
  direction, survives. Nifty unchanged (U1 Nifty).
- Trades file: `index_options_U1_B2_bank_trades.csv` (89 Bank legs).
- October B2 legs (9, premiums): 1 Oct CE V5 +₹2,480 target; 5 Oct PE
  Skill +₹2,480 target; 7 Oct PE (lA) −₹1,720 stop; 8 Oct PE Skill
  −₹1,720 stop; 13 Oct PE V5 +₹2,480 target; 21 Oct PE (lA) +₹2,480
  target; 23 Oct PE Skill +₹2,480 target; 26 Oct CE Volrix +₹2,480
  target; 26 Oct PE V5 +₹2,480 target. 7 targets, 2 stops, 77.8% FT.

## What B2 still fails

- Full-target 36.0% Jan–Oct is above base (26.2%) and above B1 (32.7%),
  but still below the 50% bar used elsewhere. October FT (77.8%) passes;
  Jan–Oct FT does not reach 50%.
- March concentration (above) and four negative months (Apr, Jun, Jul,
  Aug) remain, even though cumulative never goes negative.
- Jan–Sep is spot provisional, not premiums — no pure-premium Jan–Oct
  B2 total exists and none is claimed.
- Frequency margin is thin: 2.19/week Jan–Oct, 2.50/week October — just
  above the 2/week floor, not comfortably above it.
- Nifty is untouched by this task and still fails its own FT bar
  (36.3% Jan–Oct) — Bank tuning does not close the Nifty leg.

## Frozen November-paper Bank spec to carry forward

From Mon 2026-11-02, separate Bank log (Nifty = U1 separately), no
scoring or re-tuning during November, month-end review only:

**Bank = U1-B2 exactly:** U1 components ((lA) v2 + V5 v2 + Skill V3 +
Volrix (b) at −1.0%), unique-once per date+direction, with two blocks:
(1) any key whose representative system is Skill V3 and direction is CE
is blocked; (2) any remaining key where Skill V3 is the sole system and
entry ≤ 09:55 is blocked. Log every blocked day and, as in B1, any later
(lA)/V5/Volrix entry on a blocked key separately rather than assuming
no-trade. A November pass needs net > 0 AND full-target improvement AND
frequency ≥ 2/week on Bank premiums, separately from Nifty.

## Verdict

**Bank ends in positive under U1-B2: Jan–Oct +₹124,415 mixed
(89 trades, 36.0% FT, 2.19/week), October +₹13,920 premiums
(9 trades, 77.8% FT, 2.50/week), cumulative never negative at any
month-end, and still positive ex-March (+₹26,625).** That is the best
defensible Bank variant from this task, and the one to carry into frozen
November paper. It is a stage pass, not an adoption: FT Jan–Oct is still
below 50%, March still dominates, and November paper is the validation
step. Index work is closed to that frozen candidate; it is not closed to
an adopted system.
