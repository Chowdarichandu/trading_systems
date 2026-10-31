# N1-plus upgrade tuning — NIFTY CHANNEL ONLY

**SEPARATE CHANNEL: NIFTY ONLY.** No Bank figures, no combined total, no
combined verdict anywhere in this file. Index OPTIONS only, paper only,
no orders, no stocks. **Real money = ₹0. Nothing adopted** — any passer
would still need frozen November paper from Mon 2026-11-02; as it turns
out, there is no passer (see verdict).

Previous best kept: **U1-N1** — drop solo + early (≤09:55) keys from U1.
Pass bar for replacement (all together): net progresses vs N1 AND
full-target % progresses vs N1 AND frequency ≥ 2/week AND month-end
cumulative green at every month-end Jan–Oct — on October premiums and on
Jan–Oct mixed, separately judged.

Units: October = option premiums per 1 lot (Nifty lot 65, stop −50 /
target +90 premium points, ₹220 cost). Jan–Sep = spot provisional per leg
(points × 100 shares − ₹40, **per 100 shares, provisional — NOT an
options-lot profit, NOT a futures profit**). Jan–Oct totals are **MIXED,
labelled as such — never a pure premium total**. Scorer:
`nifty_N1plus_score.py`; premium replay uses the cached 5-min premium
candles in `v4_options_oct_data/`.

## 0. Baseline reproduction — EXACT

Replaying −50/+90 on the cached premium candles reproduces all 8 N1
October legs exactly (net, exit reason and exit time, 8/8):

| Date | Dir | Violent? | Entry prem | Exit | Net ₹ |
|---|---|---|---|---|---|
| 2026-10-01 | CE | yes | 360.35 | stop 12:10 | −3,470.00 |
| 2026-10-08 | PE | yes | 270.00 | target 12:20 | +5,630.00 |
| 2026-10-09 | CE | no | 398.00 | target 09:45 | +5,630.00 |
| 2026-10-21 | PE | yes | 151.30 | target 14:45 | +5,630.00 |
| 2026-10-22 | CE | no | 190.45 | stop 11:45 | −3,470.00 |
| 2026-10-23 | PE | yes | 125.85 | square_off 15:10 | −1,334.75 |
| 2026-10-26 | CE | yes | 132.05 | target 10:05 | +5,630.00 |
| 2026-10-28 | PE | no | 200.95 | stop 11:00 | −3,470.00 |

- **October premiums: 8 trades, +₹10,775.25 per 1 lot, 50.0% FT
  (4/8), 2.22/week** — matches N1 exactly.
- **Jan–Oct mixed: 108 trades, +₹168,140.25 mixed, 41.7% FT (45/108),
  2.66/week** (Jan–Sep legs are spot provisional per leg, labelled
  above) — matches N1 exactly.
- Month-end cumulative green at every month-end Jan–Oct; lowest close
  Jan +₹8,710; May is a negative individual month (−₹9,235) inside a
  green cumulative close, as in the N1 file.

## 1. VIOLENT-DAY definition — frozen from spot data BEFORE scoring any variant outcome

**VIOLENT-DAY = Nifty spot daily range (daily high − low) ≥ 300 points**
(`data/progressive/NIFTY/spot_daily.csv`). Chosen from the range
distribution of N1 trade dates only (median ≈ 218 pts; ≥300 is roughly
the top third), before any variant was scored.

- Qualifies: **34 of 108 N1 legs Jan–Oct**; **5 of 8 October legs**
  (1, 8, 21, 23, 26 Oct).
- Caveat stated: a full-day range is known only ex-post. It is a tuning
  classification here; a November-paper version would need a live
  proxy (e.g. first-hour range) frozen separately — no variant passed,
  so that step is not needed.

## 2. RUNNER family — REJECTED

Frozen rule (one rule): violent days only. After premium +90 is hit,
do not exit: stop moves to entry premium, second target = entry +150
premium points, otherwise exit at the breakeven stop or the 15:10
close, whichever comes first (continuation scanned from the bar after
the +90 bar; stop checked before target). Non-violent legs unchanged.
Full-target counted as reaching +90, as in baseline.

October premiums (per 1 lot):

| Leg | Baseline | Runner | Change |
|---|---|---|---|
| 08 Oct PE (V) | +5,630 target | +7,580 runner square_off 15:10 | +1,950.00 |
| 21 Oct PE (V) | +5,630 target | +2,386.50 runner square_off 15:10 | −3,243.50 |
| 26 Oct CE (V) | +5,630 target | −220 runner breakeven stop 11:15 | −5,850.00 |
| Other 5 legs | unchanged | unchanged | 0 |
| **October total** | **+₹10,775.25** | **+₹3,631.75** | **−₹7,143.50** |

October: 8 trades, 50.0% FT (unchanged), 2.22/week (unchanged),
net **falls** by ₹7,143.50. No runner leg reached the +150 second
target; one gave back the entire +90 to breakeven.

Jan–Sep spot translation (labelled provisional, per 100 shares):
applies to violent-day target-exit legs only — continue after the
original exit for one more favourable leg equal to the original
target distance, breakeven stop at entry spot, else 15:10 close.
9 legs computed: **+₹34,890 provisional extra** (16 Feb Volrix +₹9,000;
11 Mar Skill +₹7,200; 1 Jun Skill +₹9,690; 24 Jun Volrix +₹9,000;
5 legs breakeven-stopped at +₹0). **10 violent target legs are
NOT_COMPUTED** — (lA)/V5 representative legs whose source CSV carries
no entry/exit spot or exit time; they were kept at baseline, so the
Jan–Sep runner figure is a partial, lower-coverage number, not a
complete re-score.

Jan–Oct mixed (with that partial translation): 108 trades,
**+₹195,886.75 mixed**, 41.7% FT, 2.66/week, month-end cumulative
green at every month-end (Jan +₹8,710 … Oct +₹195,886.75; May still a
negative individual month, cumulative green).

**Verdict: REJECTED.** It fails the October-premium net leg — the only
pure-premium window gets worse by ₹7,143.50 — and full-target does not
progress on either window (50.0% / 41.7%, both unchanged). The
Jan–Oct mixed improvement rests on spot-provisional translation with
10 of 19 eligible legs NOT_COMPUTED and cannot override the premium
failure.

## 3. VOLATILE-STOP family — REJECTED (both variants)

Frozen rule: violent days only, premium stop widened, target +90
unchanged, everything else as N1. Extra risk per trade at lot 65:
**−65 stop = +15 pts = ₹975/lot extra risk; −75 stop = +25 pts =
₹1,625/lot extra risk.** Jan–Sep legs carry native signal-bar spot
stops, not a −50 premium stop, so there is nothing to widen in that
window: Jan–Sep is unchanged by construction and labelled as such —
the Jan–Oct mixed figures below are baseline Jan–Sep plus the new
October, nothing more.

October premiums: only one violent leg is a baseline stop (1 Oct CE).

| Variant | 1 Oct CE | October total | vs N1 Oct | FT | Freq |
|---|---|---|---|---|---|
| N1 baseline (−50) | −₹3,470 stop 12:10 | +₹10,775.25 | — | 50.0% | 2.22/wk |
| VS65 (−65) | −₹4,445 stop 12:25 | +₹9,800.25 | −₹975.00 | 50.0% | 2.22/wk |
| VS75 (−75) | −₹5,095 stop 12:40 | +₹9,150.25 | −₹1,625.00 | 50.0% | 2.22/wk |

The wider stop rescued **nothing**: 1 Oct still stopped, just later
and for exactly the extra risk. No other violent leg changes (targets
and the 23 Oct square-off are unaffected by the stop level).

Jan–Oct mixed: VS65 **+₹167,165.25 mixed**, VS75 **+₹166,515.25
mixed** (both 108 trades, 41.7% FT, 2.66/week, month-end cumulative
green every month-end — inherited from baseline Jan–Sep).

**Verdict: REJECTED (both).** Net falls on October and on Jan–Oct,
full-target does not progress on either window. Frequency and
green-close legs pass but are not enough — all legs must progress
together.

## 4. PREMIUM-CONVERSION family — diagnosis, then one gate — REJECTED

### Diagnosis: spot hit target, premium did not (all 16 U1 October Nifty legs examined)

Exactly two such legs exist in the underlying U1 October legs:

| Leg | Spot result (component leg) | Premium result | In N1? |
|---|---|---|---|
| **23 Oct PE, (lA) v2 / V5 v2** | **target, +₹11,390 spot provisional (V5 leg)** | **square_off 15:10, −₹1,334.75 premium** | **YES — remains in N1** (confirmed, entry 10:10, not solo-early) |
| 06 Oct CE, Skill V3 | target, +₹4,240 spot provisional | square_off, +₹1,801.50 premium (green, but never hit +90) | No — dropped by N1 (solo + early 09:50); diagnosis only, not re-added |

The 23 Oct type case therefore **does remain in N1** — it is N1's
only non-stop, non-target October loss. (Reverse cases also exist —
e.g. 12 Oct PE: spot stop, premium square-off +₹4,213 — but that leg
is dropped by N1 and is not this family.)

### The one frozen gate tested

**Gate: take the spot signal only if the entry premium bar (the bar
whose open is the entry premium) closes ≥ its open** — a
premium-momentum confirmation on the entry bar itself. October
premiums only; premium candles were actually cached for all 8 N1
legs, so nothing here is NOT_COMPUTED.

Entry-bar evidence (open → close): 1 Oct 360.35→348.55 down (stop
leg); 8 Oct 270.00→268.00 down (**target leg, +₹5,630, would be
blocked**); 9 Oct 398.00→392.60 down (**target leg, +₹5,630, would
be blocked**); 21 Oct 151.30→160.15 up (kept, target); 22 Oct
190.45→180.10 down (stop leg, blocked); 23 Oct 125.85→129.40 up
(**kept — the gate does not fix the type case**); 26 Oct
132.05→197.60 up (kept, target); 28 Oct 200.95→200.35 down (stop
leg, blocked).

October premiums after gate: **3 trades, +₹9,925.25, 66.7% FT (2/3),
0.83/week**. Net **falls** ₹850.00 vs N1 (the gate blocks three stop
legs worth −₹10,410 but also two target legs worth +₹11,260), and
frequency collapses below the 2/week floor.
Jan–Oct (gate is an October-premium rule; Jan–Sep unchanged):
103 trades, +₹167,290.25 mixed, 41.7% FT (43/103 — no progress vs
41.7%), 2.54/week, month-end cumulative green every month-end.

**Verdict: REJECTED.** Fails October net, fails October frequency
(0.83 < 2/week), full-target does not progress Jan–Oct, and it does
not even remove the 23 Oct conversion loss it was aimed at.

## Summary table — NIFTY ONLY

| Variant | Oct premiums (trades / net / FT / wk) | Jan–Oct mixed (trades / net / FT / wk) | Red month-end closes | Failed leg(s) |
|---|---|---|---|---|
| **U1-N1 (kept)** | 8 / **+₹10,775.25** / 50.0% / 2.22 | 108 / **+₹168,140.25 mixed** / 41.7% / 2.66 | None | — |
| RUNNER | 8 / +₹3,631.75 / 50.0% / 2.22 | 108 / +₹195,886.75 mixed* / 41.7% / 2.66 | None | Oct net ↓ ₹7,143.50; FT no progress either window |
| VS65 | 8 / +₹9,800.25 / 50.0% / 2.22 | 108 / +₹167,165.25 mixed / 41.7% / 2.66 | None | Net ↓ both windows; FT no progress |
| VS75 | 8 / +₹9,150.25 / 50.0% / 2.22 | 108 / +₹166,515.25 mixed / 41.7% / 2.66 | None | Net ↓ both windows; FT no progress |
| GATE | 3 / +₹9,925.25 / 66.7% / **0.83** | 103 / +₹167,290.25 mixed / 41.7% / 2.54 | None | Oct net ↓ ₹850; Oct frequency < 2; Jan–Oct FT no progress; 23 Oct leg kept |

\* Runner Jan–Oct mixed includes the partial spot translation of
§2 (10 of 19 eligible Jan–Sep legs NOT_COMPUTED, kept at baseline) —
labelled, not a complete re-score and not a pure premium total.

## Verdict — NIFTY ONLY

**No upgrade beats U1-N1. U1-N1 is kept** (October +₹10,775.25
premiums per 1 lot, 8 trades, 50.0% FT, 2.22/week; Jan–Oct
+₹168,140.25 mixed, 108 trades, 41.7% FT, 2.66/week, month-end
cumulative green at every month-end). RUNNER, VS65, VS75 and the
premium-momentum GATE are all logged as rejected above, each with
the leg it failed. No variant trades CSV is produced, because no
variant passed. **Nothing adopted**: the frozen November paper spec
from Mon 2026-11-02 remains **Nifty = U1-N1 exactly**, unchanged by
this tuning round. Real money = ₹0.
