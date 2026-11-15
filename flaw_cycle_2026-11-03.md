# FLAW-CYCLE — 2026-11-03 (special run, ordered by Chandu ~11:43 IST)

Paper only, real money ₹0. November primaries untouched; nothing here
mutates any frozen book, cron, or rule. Basis: Bank premiums per 1 lot
(30), cost ₹220/trade, UNIQUE-ONCE. Incumbent reproduced through the
audited pipeline and verified leg-for-leg against
`bank_engine_r8_v21_regen_trades.csv` (99 legs, 0 field mismatches,
+₹83,650.50) before any variant was scored.

## VERDICT BOX — his exact question, answered first

**"Under the fix, would yesterday and today still be negative?"**

- **Nov 2 (Skill PE 54800, −₹1,720 actual): YES — still −₹1,720 under
  every fix.** The premium never developed (best excursion +13.25 pts)
  and hit the full stop on the very next bar (10:25), before any
  close-based exit rule can act. No exit-side fix changes this day.
- **Nov 3 (NS1 CE 55500, −₹1,720 actual): still negative, but only
  −₹220 under the give-back lock (FC-2/FC-3)** — the trade developed
  to +33.4 by 10:30, the lock armed at breakeven, and it would have
  exited 10:35 @ ₹867.60 instead of riding to the full stop at 11:10.
- **BUT the fix is REJECTED.** FC-2 fails the full controls gate on the
  Jan–Oct 2026 book: it would have cost **−₹39,661.50** against v21.
  The same dip-through-entry that killed Nov 3 happens in 22 winning
  trades that go on to target — the lock saves ₹33,000 on losers and
  destroys ₹72,661.50 of winners. It is not promoted, not shadowed.
  Shipping it because it fixes today would be fitting to two days —
  exactly the fake-fit failure mode banned by standing orders.

## 1. THE FLAW — one precise paragraph

The Bank book's OR-family entries (base pool + NS1 second legs) are
paid for in full −50 premium stops: in the causal Jan–Oct 2026 book
(v21), **47 of 99 legs (47.5%) exit at the full stop, every one netting
exactly −₹1,720 — a combined drag of −₹80,840 against a book net of
+₹83,650.50**, i.e. the book earns back its entire stop bill and only
then starts profiting. The drag splits into two shapes: **25 legs
(−₹43,000) never developed at all** (best excursion before the stop
< +30 premium points — dead on arrival, 17 of all 47 stops inside
10 minutes, 22 inside 15), and **22 legs (−₹37,840) developed past
+30 and then faded all the way back through the full stop** (the
Nov 3 shape). Both live November days are textbook instances, one of
each shape, at the identical −₹1,720.

### Counts — v21 book (Jan–Oct 2026)

| Scope | Legs | Full stops | Drag | Never developed (<+30) | Developed→stop |
|---|---|---|---|---|---|
| All legs | 99 | 47 | −₹80,840 | 25 (−₹43,000) | 22 (−₹37,840) |
| OR-family (BASE + NS1) | 77 | 36 | −₹61,920 | 20 (−₹34,400) | 16 (−₹27,520) |
| Add-on sleeves (NS3 + S3) | 22 | 11 | −₹18,920 | 5 (−₹8,600) | 6 (−₹10,320) |

- Full stops by direction: PE 40 of 47, CE 7. By entry hour: <10:00 →
  17, 10:00–10:59 → 20, 11:00–11:59 → 8, ≥12:00 → 2. Never-developed
  stops by entry hour: <10:00 → 10, 10:xx → 8, 11:xx → 5, ≥12:00 → 2
  (18 of 25 are morning entries before 11:00).
- October 2026 fresh re-score (PRIMARY, 14 legs incl. Oct 29–30
  extension): 4 full stops (−₹6,880), of which 3 never-developed
  (−₹5,160) and 1 developed→stop. The flaw is present even in the
  book's best month, at a lower rate (3 of 14 legs).
- Live November: Nov 2 = never-developed instance (MFE +13.25);
  Nov 3 = developed→stop instance (MFE +39.2 through the exit bar).
  2 of 2 live Bank trades so far are this flaw, −₹3,440 combined.

## 2. CANDIDATES — pre-registered before scoring

Full text: `flaw_cycle_candidates_2026-11-03.md` (written before the
scorer ran). All three are exit overlays on the frozen v21 legs —
admissions, segments and each leg's frozen parameters unchanged. The
rejected 2026-11-02 break-hold confirmation was NOT retested.

- **FC-1 NODEV-CUT** (attacks never-developed): if by the close of the
  2nd bar after entry the running max high is still < entry+15, exit
  at that close.
- **FC-2 GIVEBACK-LOCK** (attacks developed→stop): once a bar
  completes with high ≥ entry+30, the stop for subsequent bars rises
  to entry+0 (breakeven premium).
- **FC-3** = FC-1 + FC-2 combined.

## 3. GATE RESULTS — all three FAIL (same run, full controls)

Incumbent v21 controls in-run: net +₹83,650.50 · FT90 49.5% · halves
+₹61,938.00 / +₹21,712.50 · ex-top-3 +₹54,610.50 · no red month-ends ·
placebo (delay-6) beaten · NC 0 · re-sum exact. (Placebo construction
note: this run's delay-6 twin holds each leg's frozen segment/params —
incumbent placebo −₹343.50 here vs −₹4,313.50 in the pipeline's
stream-rebuilt construction; no verdict turns on it — every candidate
beat both placebo figures, and no candidate failed on the placebo leg.)

| Candidate | Net (Δ vs v21) | Legs changed | FT90 | Verdict | Deciding gate legs |
|---|---|---|---|---|---|
| FC-1 nodev-cut | ₹79,446.00 (−₹4,204.50) | 7 | 46.5% | **FAIL** | net < incumbent; FT90 < 49.5% |
| FC-2 giveback-lock | ₹43,989.00 (−₹39,661.50) | 44 | 30.3% | **FAIL** | net < incumbent; FT90 < 49.5% |
| FC-3 combined | ₹46,384.50 (−₹37,266.00) | 47 | 30.3% | **FAIL** | net < incumbent; FT90 < 49.5% |

All other gate legs passed for all three (no red month-ends, no green
month flipped red, halves both ≥ 0, own placebo beaten — FC-1 −₹8,751,
FC-2 −₹3,630, FC-3 −₹15,253.50 — timing violations 0, NC 0, re-sums
exact, ex-top-3 ≥ 0). The failures are purely economic, and the
anatomy is unambiguous:

- **FC-2** improves all 22 developed→stop legs by exactly +₹1,500
  each (**+₹33,000 saved**) — and scratches **22 incumbent winners**
  that touched +30, dipped back through entry, then ran to
  target/runner (**−₹72,661.50 destroyed**). The give-back shape is
  symmetric in this book: 22 losers and 22 winners share it. A
  breakeven lock cannot tell them apart at the moment it must act.
- **FC-1** fires on only 7 legs all year: saves +₹4,081.50 on 4 stops
  but cuts 3 legs that were merely slow, not dead — they recovered to
  winners worth −₹8,286. "No +15 by bar 3" does not separate dead
  breaks from slow ones either.

**Conclusion of the gate: the flaw is real, quantified, and NOT
exit-fixable by either mechanism.** It lives in entry quality (which
breaks are real), not in exit geometry. The one entry-side candidate
that ever caught the never-developed class — EVE-02 (skip Skill-solo
base legs) — already failed the gate on 2026-11-02 (H2 −₹12,605.50).

## 4. COUNTERFACTUALS — the two live days, candle by candle

November primary's own frozen geometry (PLAIN −50/+90, square-off
15:10). Incumbent replays reproduce both live records to the paisa
before any overlay is applied (entry = open of the 10:20 bar in both).

**Nov 2 — Skill V3 PE 54800 (expiry 2026-11-23), entry 10:20 @ ₹681.95**
Entry bar: H 695.20 (MFE +13.25) / L 640.85. Next bar 10:25: L 622.75
through the ₹631.95 stop.

| Rule | Exit | Net |
|---|---|---|
| Actual / incumbent | 10:25 @ ₹631.95 (stop) | **−₹1,720** |
| FC-1 | identical — stop hits a bar before the check bar | −₹1,720 |
| FC-2 | identical — never reached +30, lock never armed | −₹1,720 |
| FC-3 | identical | −₹1,720 |

**Would Nov 2 still be negative under the fix? YES — fully, −₹1,720.**
Nothing that waits for even one completed bar can act on a trade that
is stopped on the bar after entry; the only levers for this shape are
entry-side (skip/delay — delay already gate-failed on 2026-11-02) or a
narrower stop, which shrinks the loss but cannot change its sign.

**Nov 3 — NS1 second-leg CE 55500 (expiry 2026-11-23), entry 10:20 @ ₹867.60**
Path: 10:20 H 893.40 · 10:25 H 896.00 · 10:30 H 901.00 (+33.4 → lock
arms at that bar's close) · 10:35 L 852.00 (through breakeven) ·
premium faded on to the stop, 11:10 L 811.05 → exit @ ₹817.60.

| Rule | Exit | Net |
|---|---|---|
| Actual / incumbent | 11:10 @ ₹817.60 (stop) | **−₹1,720** |
| FC-1 | identical — developed past +15 by the check bar, no cut | −₹1,720 |
| FC-2 | 10:35 @ ₹867.60 (lock_stop, breakeven premium) | **−₹220** |
| FC-3 | 10:35 @ ₹867.60 (lock_stop) | **−₹220** |

**Would Nov 3 still be negative under the fix? YES — but −₹220
(costs only) instead of −₹1,720, a ₹1,500 improvement on the day.**
And per §3, adopting that fix book-wide would have cost ₹39,661.50
across Jan–Oct. A fix that wins today and loses the year is not a fix.

## 5. EVE-03 TUNED SHADOW vs today's NS1 leg

EVE-03 (promoted 2026-11-02 evening, live from today; registry
`november_rsi_candidates.md`): skip B2 **BASE** legs whose sources
include **Skill V3**, direction **PE**, entry **< 10:00**; NS1 second
legs explicitly unchanged; exits are the primary's own.

Today's leg (intraday state file: "Bank NS1_SECOND 55500 CE"): family
**NS1 second leg** (not BASE), direction **CE** (not PE), entry
**10:20** (not < 10:00) — three independent non-matches. **Verdict:
the shadow TOOK the leg identically and would have scored the same
−₹1,720** (exit 11:10 @ ₹817.60). The shadow does not cover the NS1
give-back shape at all. (Same for Nov 2: registry already records
EVE-03's would-be as the kept −₹1,720 — entry 10:20 fails its <10:00
condition: EVE-03 catches the pre-10:00 PE slice of this flaw, not
either live instance.)

## 6. STOCKS — parallel count (separate; PROVISIONAL per 100 shares)

The same micro-shape barely exists inside the frozen SarvaRitu book:
October 2026 book (91 trades, +₹52,696.68): 19 stops totalling
−₹10,957.55 (F4 12, INV-LONG 4, P2F 2, N4-V3 1) — **zero stops within
5 minutes, only 2 within 15 minutes (both P2F, −₹315 combined)**.
The 5-minute stop-outs Chandu saw are real but live in the 09:15-open
reaction layer, not the frozen book's core: Nov 2 GODREJCP −₹446.50
was a P2F *shadow* row (2.0% band; the book's 2.5% band took no
trade), Nov 3 NTPC −₹201.50 is a scorecard row, and the one genuine
book instance is Nov 3 GODREJCP R2-LOWBAND SHORT 09:15 → stop 09:20,
−₹451.85 (live-shadow record; official EOD log lands 16:35). Nov 2's
book stop (NTPC) took 135 minutes — not this shape. **No gated
candidate is run for stocks**: the shape is one book trade in two
days, an exit cut cannot act before a first-bar stop, and the one
entry-side fix for this family (skip the opening bar, STOCKS-FIX-01)
was already gated on 2026-11-02 and FAILED (delay cost ₹21,272.50 on
the reaction family). Running a variant on one instance would be
fitting, not fixing.

## 7. RECOMMENDATION

1. **Promote nothing.** FC-1, FC-2, FC-3 are REJECTED — deciding legs:
   net-vs-incumbent and FT90, for all three. No shadow, no December
   candidate from this cycle. The November primary stays exactly as
   frozen.
2. **What the cycle DID establish** (the recursive asset): the flaw is
   certified entry-side, with the two exit mechanisms now permanently
   closed with numbers — a breakeven give-back lock and a bar-3
   no-development cut each destroy more winners than the losers they
   save, because both shapes (dead break, give-back dip) are shared
   by winners. Any future candidate aimed at this flaw must separate
   the break ITSELF at entry time using information available at the
   entry bar — not exits, not delays.
3. **Hand-off to tonight's Bank evening engine** (as new
   pre-registered hypotheses for its own gate — NOT scored here, and
   not fitted to these two days): (a) an NS1-only give-back lock
   (today's shape is NS1; the book-wide FC-2 damage came mostly from
   base-pool runners — the engine can test whether the NS1 sleeve
   alone separates); (b) entry-bar-range quality conditions on OR
   breaks (e.g. entry-bar close position within its range) — the
   follow-through class the pre-registration named but the delay ban
   pushed out. If both fail, the flaw stands as the known cost of the
   frozen design — and it is literally the book's ONLY loss source:
   the 99 legs split into +₹164,490.50 of winners and the 47 full
   stops (−₹80,840), with not one other losing leg. The floor fight
   continues on other axes.
4. **Direct answer to keep**: yesterday stays −₹1,720 under every
   honest fix; today would have been −₹220 under the lock — and the
   lock is rejected because it loses ₹39,661.50 across the year. The
   scenario WILL recur (47 instances in 10 months); the protection
   that exists today is EVE-03's pre-10:00 PE slice (shadow, live) —
   neither live instance was in it.

## Artefacts
- Pre-registration: `flaw_cycle_candidates_2026-11-03.md`
- Scorer: `flaw_cycle_run.py` · results: `flaw_cycle_results_2026-11-03.json`
- Trades: `flaw_cycle_incumbent_trades.csv`, `flaw_cycle_fc1_trades.csv`,
  `flaw_cycle_fc2_trades.csv`, `flaw_cycle_fc3_trades.csv` (all re-summed exact)
- Counterfactuals: `flaw_cycle_counterfactual.py`,
  `flaw_cycle_counterfactual_2026-11-03.json`
- Candles: `flaw_cycle_candles_2026-11-02_54800PE.json` (Upstox v3,
  key NSE_FO|62152, fetched today); Nov 3 path from the worker's
  completed-bar snapshot `prem_bank_55500CE_2026-11-03_1115.json`
  (goal hidden_files). NOT_COMPUTED: none — every leg and both live
  days computed from real candles.
