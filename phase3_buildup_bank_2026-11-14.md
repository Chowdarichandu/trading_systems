# PHASE-3 TUNING — BANK NIFTY · BUILDUP / SPECULATION CONDITIONING ON TUNED STACK v2 · 2026-11-14

Spec: `phase3_buildup_bank_SPEC.md` (frozen before scoring). Numbers: `phase3_buildup_bank_results.json`.
Script: `phase3_buildup_bank_build.py`. Research only — no book, ledger, or job changed.
Basis: paper, 1 lot, costs as in the gated store. Owner's surface: futures buildup classes
(long buildup / short buildup / long unwinding / short covering), today's volume vs previous
days, call-vs-put OI speculation — used to condition the stack's own legs, never to signal.

## Control (reproduced before any scoring)
Full book Jan–Oct from the gated store: **111 legs · +₹127,351.50 · WR 59.5% · 89 trade-days ·
₹1,430.92/trade-day · 60G/29R/116NT of 205 · H1 +₹83,082.00 / H2 +₹44,269.50 · ex-top-3
+₹100,528.50 · zero red months** — exact match, plus an independent raw re-sum (+₹127,351.50).
Control OK.

## Dataset coverage (NC counted, never filled)
- **Futures state (buildup class + relative volume): COMPLETE — 205/205 Jan–Oct days at both
  reads** (FUT7 near-month series; the only NC is the ratios on 2026-01-01, which has no
  previous day — its legs, if any, are NC-kept).
- **Speculation state (call/put OI lean): complete on 116/205 days** under this round's causal
  band (11 strikes around the OPENING spot). On 89 days at least one band strike was never
  fetched into the chunk store at all (whole-contract absence — the round-5 fetch was anchored
  to the 10:55 band; verified by hand on samples, e.g. 2026-03-02 missing 60400CE/60500CE
  entirely), so those days are NC for the speculation component. Consequence, stated plainly:
  grid points B and E could actually condition only **44 of 76** post-read legs at the 10:00
  read and **27 of 42** at the 11:00 read; the rest were NC-kept. In November the speculation
  state is NC on **all 4 leg days**, so B and E never fired there at all (see CF below).
- Post-read legs: 76 (entered ≥ 10:00) · 42 (entered ≥ 11:00); pre-read legs are untouched
  by construction at each read.

## Results — every grid point FAILS the frozen pass bar

Pass bar (unmoved): WR ≥ 60% · ₹/trade-day ≥ ₹900 · total ≥ ₹76,410.90 (60% of book) · both
halves > 0 · ex-top-3 > 0 · placebo ≥ 95th pct · kept total > flipped total · no red month.

### Read 10:00 (76 post-read legs conditionable on futures; 44 on speculation)
| Point | Kept | Dropped (₹) | Total | WR | ₹/TD | Placebo | Flipped | Verdict — failing legs |
|---|---|---|---|---|---|---|---|---|
| A align | 93 | 18 (+24,603.00) | +₹102,748.50 | 58.1% | 1,388.49 | 39.0 | +₹51,253.00 | FAIL — WR, placebo |
| B align+spec | 82 | 29 (+33,056.50) | +₹94,295.00 | 58.5% | 1,407.39 | 48.0 | +₹122,845.50 | FAIL — WR, placebo, flipped |
| C1.0 vol≥1.0 | 55 | 56 (+53,717.50) | +₹73,634.00 | 60.0% | 1,534.04 | 79.0 | +₹80,367.50 | FAIL — total, placebo, flipped, red Aug |
| C1.1 vol≥1.1 | 49 | 62 (+77,147.50) | +₹50,204.00 | 55.1% | 1,195.33 | 35.5 | +₹103,797.50 | FAIL — WR, total, placebo, flipped, red Aug |
| C1.25 vol≥1.25 | 47 | 64 (+79,407.50) | +₹47,944.00 | 55.3% | 1,198.60 | 34.0 | +₹106,057.50 | FAIL — WR, total, placebo, flipped, red Aug |
| C5-1.0 vol5≥1.0 | 54 | 57 (+75,847.50) | +₹51,504.00 | 55.6% | 1,119.65 | 23.5 | +₹103,777.50 | FAIL — WR, total, placebo, flipped, red Aug |
| C5-1.1 vol5≥1.1 | 48 | 63 (+82,327.50) | +₹45,024.00 | 54.2% | 1,098.15 | 19.5 | +₹110,257.50 | FAIL — WR, total, placebo, flipped, red Jun+Aug |
| C5-1.25 vol5≥1.25 | 43 | 68 (+87,509.50) | +₹39,842.00 | 53.5% | 1,076.81 | 26.0 | +₹115,439.50 | FAIL — WR, total, placebo, flipped, red Aug |
| D1.0 align+vol1.0 | 45 | 66 (+68,317.50) | +₹59,034.00 | 57.8% | 1,475.85 | 70.0 | +₹94,967.50 | FAIL — WR, total, placebo, flipped, red Aug |
| D1.1 align+vol1.1 | 43 | 68 (+80,477.50) | +₹46,874.00 | 55.8% | 1,233.53 | 46.0 | +₹107,127.50 | FAIL — WR, total, placebo, flipped, red Aug |
| E all three | 68 | 43 (+35,082.50) | +₹92,269.00 | 60.3% | 1,590.84 | 83.0 | +₹124,871.50 | FAIL — placebo, flipped, red Aug |

### Read 11:00 (42 post-read legs conditionable on futures; 27 on speculation)
| Point | Kept | Dropped (₹) | Total | WR | ₹/TD | Placebo | Flipped | Verdict — failing legs |
|---|---|---|---|---|---|---|---|---|
| A align | 100 | 11 (+13,469.50) | +₹113,882.00 | 58.0% | 1,355.74 | 47.5 | +₹99,298.00 | FAIL — WR, placebo |
| B align+spec | 94 | 17 (+17,549.50) | +₹109,802.00 | 58.5% | 1,389.90 | 50.5 | +₹134,630.50 | FAIL — WR, placebo, flipped, red Jun+Aug |
| C1.0 vol≥1.0 | 76 | 35 (+29,051.50) | +₹98,300.00 | 60.5% | 1,467.16 | 81.0 | +₹114,880.00 | FAIL — placebo, flipped |
| C1.1 vol≥1.1 | 75 | 36 (+31,531.50) | +₹95,820.00 | 60.0% | 1,451.82 | 76.0 | +₹117,360.00 | FAIL — placebo, flipped |
| C1.25 vol≥1.25 | 73 | 38 (+32,291.50) | +₹95,060.00 | 60.3% | 1,462.46 | 85.5 | +₹118,120.00 | FAIL — placebo, flipped, red Jun |
| C5-1.0 vol5≥1.0 | 77 | 34 (+27,771.50) | +₹99,580.00 | 61.0% | 1,464.41 | 84.0 | +₹114,880.00 | FAIL — placebo, flipped |
| C5-1.1 vol5≥1.1 | 75 | 36 (+28,531.50) | +₹98,820.00 | 61.3% | 1,453.24 | 86.0 | +₹115,640.00 | FAIL — placebo, flipped |
| C5-1.25 vol5≥1.25 | 73 | 38 (+35,401.00) | +₹91,950.50 | 60.3% | 1,393.19 | 72.0 | +₹122,509.50 | FAIL — placebo, flipped, red Jun |
| D1.0 align+vol1.0 | 75 | 36 (+31,531.50) | +₹95,820.00 | 60.0% | 1,430.15 | 76.5 | +₹117,360.00 | FAIL — placebo, flipped |
| D1.1 align+vol1.1 | 74 | 37 (+34,011.50) | +₹93,340.00 | 59.5% | 1,414.24 | 69.5 | +₹119,840.00 | FAIL — WR, placebo, flipped |
| E all three | 85 | 26 (+11,990.50) | +₹115,361.00 | 61.2% | 1,580.29 | 92.5 | +₹129,071.50 | FAIL — placebo, flipped, red Jun+Aug |

Halves and ex-top-3 were positive at **every** grid point (weakest: C5-1.25 @10:00 halves
+₹18,062/+₹21,780, ex-top-3 +₹20,702) — no grid point failed on those two legs. No month was
fully idled at any grid point. Month tables for the headline points:

- A @10:00: Jan +21,998 · Feb +12,044 · Mar +5,320 · Apr +9,810 · May +11,880 · Jun +3,040 ·
  Jul +8,641 · Aug +2,059.50 · Sep +15,056.50 · Oct +12,899.50 (no red month — it fails on
  WR and placebo, not on shape)
- A @11:00: Jan +24,028 · Feb +12,804 · Mar +6,080 · Apr +7,330 · May +22,920 · Jun +560 ·
  Jul +5,941 · Aug +2,059.50 · Sep +14,750 · Oct +17,409.50
- E @11:00 (nearest miss): Jan +22,748 · Feb +14,524 · Mar +9,520 · Apr +9,050 · May +20,360 ·
  Jun **−1,920** · Jul +5,900 · Aug **−420.50** · Sep +16,470 · Oct +19,129.50
- C1.0 @11:00: Jan +12,020 · Feb +14,524 · Mar +8,760 · Apr +6,570 · May +16,080 · Jun +560 ·
  Jul +4,100 · Aug +2,566.50 · Sep +16,470 · Oct +16,649.50

### What each dial actually did
- **Alignment (A):** the direction dial is a coin flip per leg. The 18 legs it drops at 10:00
  netted **+₹24,603** (avg +₹1,367/leg) vs +₹1,312 avg for the post-read legs it keeps; the
  kept total sits at the **39th–47.5th percentile of random same-size subsets** — worse than
  random thinning. It "beats flipped" only because it keeps more legs, not better ones.
  WR falls (59.5% → 58.0–58.1%). The futures buildup class does not know whether a stack
  leg is pointing the right way.
- **Speculation (B, E):** where it could be tested at all, the call/put lean points the
  **wrong way**: B's flipped book beats its kept book at both reads (+₹122,845.50 vs +₹94,295
  @10:00; +₹134,630.50 vs +₹109,802 @11:00). At 11:00 the 10 legs B actually kept netted
  **−₹7,279** while the 17 it dropped made +₹17,549.50. E @11:00 is the round's nearest miss
  (WR 61.2%, ₹1,580.29/TD, placebo 92.5) — but that is inherited from keeping 85 of 111 legs;
  its speculation component never helps anywhere it is testable, and it still fails placebo,
  flipped, and two red months.
- **Volume (C, C5, D):** the most destructive dial, and it is **inverted**: the book earns on
  its quiet mornings. Gating on volume ≥ previous day amputates earners — at 10:00 the
  dropped sets are worth +₹53,717.50 (≥1.0) rising to +₹87,509.50 (5-day ≥1.25), win rate
  collapses to 53.5–55.6%, and August goes red at almost every 10:00 volume point. At 11:00
  the cuts are milder but the dropped sets still earn +₹27,771.50 to +₹35,401.
  *Post-hoc warning, stated and NOT acted on:* a "keep only low-relative-volume" gate would
  look strong in this window precisely because these dropped sets are positive. That inversion
  was not pre-registered; flipping a failed conditioner into its opposite after seeing the
  result is a new hypothesis, not a finding of this run, and nothing here adopts it.

## November counterfactual (descriptive only — November sets no rule)
Actual November: **−₹2,680** (Nov 4 S3-R1 PE 09:55 +₹2,480 pre-read everywhere; Nov 9 Skill
V3 PE 10:45 −₹1,720; Nov 12 S3-R1 PE 11:30 −₹1,720; Nov 13 NS3 PE 12:20 −₹1,720).
- **10:00 read — A, all C, all C5, both D: +₹2,480.** All three losers are PE legs taken into
  LONG_BUILDUP futures mornings (direction-opposed) with relative volume 0.59–0.99 (below
  every gate) — every futures-based dial idles all three.
- **11:00 read — A, all C, all C5, both D: +₹760.** Nov 9 (entered 10:45) is pre-read at
  11:00 and kept (−₹1,720); Nov 12 and Nov 13 are idled.
- **B and E at both reads: −₹2,680 = actual.** The speculation state is NC on all four
  November days, so every conditioned leg was NC-kept — **B and E never fired in November.**
November's shape flatters the alignment/volume dials, but November is 4 legs; Jan–Oct's 111
legs vote the same dials down (placebo 39–86th pct, flipped losses). The counterfactual is
reported, not believed.

## Distinctness (as pre-registered)
No conditioner collapsed into a closed route: nothing here generates entries (vs IOI-1/IOI-2
and day-level OI V1–V3 standalone signals), the volume gate carries no basis term and faced
a dropped-set control (vs FLOW-VOL's standalone thrust signal), and the conditioner is market
positioning state, not a per-leg feature composite (vs phase-2 confidence gating).

## Honest bottom line
**The buildup/speculation state knows nothing usable about this book's legs — through any of
the three dials.** Alignment is random per leg (placebo 39–47.5th percentile, WR falls);
the call/put speculation lean, on the 116 days and 44/27 legs where it is testable at all,
selects *against* the book (its flipped books win at both reads); and the volume dial runs
backwards — the stack earns on quiet mornings, so "trade only when volume confirms" deletes
its living. All 22 grid points FAIL; TUNED STACK v2 stands unchanged, and this surface joins
the closed list for conditioning this book. The one genuinely new fact the round produced is
the inversion itself (dropped sets +₹28k…+₹88k on the volume gates) — recorded here as an
observation for a possible future pre-registered hypothesis, worth nothing until it is one.
