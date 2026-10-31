# MOVER-B5 — Leak Audit + Honest Rebuild Report (Line B5)

Workplan frozen in `stocks_moverB5_frozen.md` BEFORE scoring.
Equity cash intraday, LONG/SHORT only, paper only, real
money ₹0. All figures provisional per 100 shares,
net = gross − ₹40/trade. Window Jan–Oct 2026 (Oct = 1–28).
Pooled 50 primary; home (original 25) / ext (new 25) splits
reported. Engine: `stocks_moverB5.py`; results:
`stocks_moverB5_results.json`; dumps: `moverB5_AUDIT_A_trades.csv`,
`moverB5_AUDIT_B_trades.csv` (with `slice` column),
`moverB5_HONEST_1000/1015/1030/1130_trades.csv`,
`moverB5_STACK_trades.csv`.

**Purpose.** Line B4 proved the B3 candidate (11:30
measurement) earned 99.3% of its net from entries placed
before the measurement that qualified the day — a look-ahead
structure inherited from the mover machinery (qualify on the
pre-move through the measurement time; search the whole
day's signal stream from 09:15). This line answers two
questions about the FROZEN flagship configurations:

1. **How much of MOVER-A (10:00) and MOVER-B (10:15) was
   untradable?** (Part 1 — audit of the frozen books, no rule
   changes.)
2. **What survives when the machinery is rebuilt honestly**
   — signal search starting at the first bar at/after the
   measurement time? (Part 2.)

## Validation gate — PASS

`build_b5` with honest=False (the original whole-day search)
reproduced every published anchor to the paisa before any
B5 number was scored: MOVER-A pooled 623 chains / 998 trades
/ **+₹249,155.03** (home +₹84,671.74, ext +₹164,483.29);
MOVER-B pooled 917 chains / 1,422 trades / **+₹464,617.03**
(home +₹169,328.31, ext +₹295,288.72), including halves,
October, breadth on all six universe cells and B's pooled
max drawdown of −₹17,471.45. The honest switch therefore
differs from the flagship machinery by exactly one thing:
where the signal search starts.

## Part 1 — Leak audit of the frozen configurations

Every trade of the frozen books, split by entry time against
its own configuration's measurement time (pre = entry_time <
measurement; post = entry_time ≥ measurement). Slice chains =
distinct stock-days contributing to the slice.

### MOVER-A (measure 10:00) — pooled 50

| Slice | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth* |
|---|---|---|---|---|---|---|---|
| Full book | 623 | 998 | **+249,155.03** | +126,026.74 | +123,128.29 | +56,809.97 | 38 pos |
| **Pre-measurement** | 430 | 480 | **+317,064.00** | +175,933.45 | +141,130.55 | +57,757.66 | 45 pos |
| **At/after measurement** | 430 | 518 | **−67,908.97** | −49,906.71 | −18,002.26 | −947.69 | 23 pos |

\* slice breadth counts positive stocks among the stocks that
traded in that slice (49 stocks traded at all in A pooled).

Chain classes (by the entry times inside each chain):
all-pre 193 chains **+₹120,013.56**; all-post 193 chains
**−₹41,445.72**; mixed 237 chains +₹170,587.19 (a mixed
chain's post trade exists only because its pre trade was
taken and exited first).

Splits — home: full +₹84,671.74 = pre **+₹101,466.46**
(119.8%) + post **−₹16,794.72** (post halves −₹11,435.91 /
−₹5,358.81). Ext: full +₹164,483.29 = pre **+₹215,597.54**
(131.1%) + post **−₹51,114.25** (post halves −₹38,470.80 /
−₹12,643.45).

### MOVER-B (measure 10:15) — pooled 50

| Slice | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth* |
|---|---|---|---|---|---|---|---|
| Full book | 917 | 1,422 | **+464,617.03** | +243,806.97 | +220,810.06 | +118,748.54 | 49 pos |
| **Pre-measurement** | 741 | 910 | **+523,978.42** | +265,263.17 | +258,715.25 | +129,208.22 | 48 pos |
| **At/after measurement** | 456 | 512 | **−59,361.39** | −21,456.20 | −37,905.19 | −10,459.68 | 18 pos |

Chain classes: all-pre 461 chains **+₹276,348.18**; all-post
176 chains **−₹8,126.61**; mixed 280 chains +₹196,395.46.

Splits — home: full +₹169,328.31 = pre **+₹179,182.09**
(105.8%) + post **−₹9,853.78**. Ext: full +₹295,288.72 = pre
**+₹344,796.33** (116.8%) + post **−₹49,507.61**.

### The plain statement

**More than the entire flagship profit was untradable.**
The pre-measurement slice is **127.3%** of MOVER-A's pooled
net and **112.8%** of MOVER-B's: the leaky books earn more
than their headline totals from trades entered before the
qualifying move was knowable, and the trades entered at or
after the measurement — the only ones a live trader could
even in principle have taken — **lose money in aggregate for
both configurations, on both universes, in both halves**
(the single exception anywhere is B-home's post Jun–Oct at
+₹1,116.48, scratch). And even that losing post slice is an
upper bound, not the honest rule: in mixed chains the post
trade depends on a pre trade having happened, and the honest
discard is the first signal *after* measurement, not the
day's first signal. Part 2 prices the honest rule itself.

The leak is not subtle or rare: 480 of A's 998 pooled trades
(48%) and 910 of B's 1,422 (64%) entered before their
measurement completed. It is also visible inside the frozen
November shadow spec's own worked examples — under MOVER-A
the validated 2026-10-28 BDL trade entered at **09:50**,
before the 10:00 measurement existed; under MOVER-B the
GLENMARK trade entered at **10:00**, before the 10:15
measurement existed.

## Part 2 — Honest rebuild

Machinery identical, except the signal search starts at the
first bar at/after the measurement time: the discarded first
signal is the first signal at/after measurement, the traded
signal is the next one at/after it, re-entries proceed from
the previous exit as before. Threshold 1.0%, T125 exits,
cap 2, any direction — all frozen.

### Pooled 50

| Honest cell | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Max DD ₹ | Losing months |
|---|---|---|---|---|---|---|---|---|---|---|
| 10:00 | 614 | 946 | **−117,200.13** | −74,380.44 | −42,819.69 | −18,487.89 | 15/50 | −190.88 | −118,351.91 | 9 of 10 |
| 10:15 | 894 | 1,299 | **−167,156.86** | −100,793.47 | −66,363.39 | −29,590.72 | 17/50 | −186.98 | −174,300.24 | 8 of 10 |
| 10:30 | 1,186 | 1,618 | **−65,834.30** | −49,521.89 | −16,312.41 | −24,790.89 | 20/50 | −55.51 | −90,230.81 | 6 of 10 |
| 11:30 | 146 | 188 | **−66,681.94** | −32,031.49 | −34,650.45 | −1,390.77 | 13/50 | −456.73 | −68,480.52 | 8 of 10 |

Splits (net ₹): 10:00 — home −₹47,557.10 (breadth 6/25),
ext −₹69,643.03 (9/25). 10:15 — home −₹55,615.44 (8/25),
ext −₹111,541.42 (9/25). 10:30 — home −₹31,192.05 (7/25),
ext −₹34,642.25 (13/25). 11:30 — home −₹12,301.74 (6/25),
ext −₹54,380.20 (7/25). Every split of every cell is
negative in total; the only positive half in any pooled cell
is none — both halves are negative in all four. (Two
universe-level exceptions, both small: honest 10:15 home
Jun–Oct +₹5,218.40 and October +₹4,529.99; honest 10:30 home
October +₹9,087.36. Neither rescues its cell.)

Month tables (pooled net ₹) — 10:00: Jan −29,272.75,
Feb −16,806.03, Mar −2,758.99, Apr +22,982.77, May −48,525.44,
Jun −12,731.79, Jul −2,452.09, Aug −7,387.78, Sep −1,760.14,
Oct −18,487.89. 10:15: Jan −32,926.26, Feb −30,414.99,
Mar −2,536.47, Apr −11,103.31, May −23,812.44, Jun −34,987.27,
Jul −11,818.00, Aug +2,404.83, Sep +7,627.77, Oct −29,590.72.
10:30: Jan −39,032.44, Feb −26,442.28, Mar +16,233.88,
Apr +7,851.23, May −8,132.28, Jun −1,857.16, Jul +3,034.04,
Aug −2,686.50, Sep +9,988.10, Oct −24,790.89. 11:30:
Jan −14,392.44, Feb −14,055.62, Mar −5,921.75, Apr +2,422.42,
May −84.10, Jun −11,900.06, Jul −7,193.40, Aug −14,933.77,
Sep +767.55, Oct −1,390.77.

Notes on shape: honest chain counts stay close to the leaky
books at 10:00/10:15 (614 vs 623; 894 vs 917) — the honest
rule trades *different signals* on mostly the same qualifying
days, and those signals lose. At 11:30 the honest book
collapses to 146 chains (two post-11:30 signals on a
qualifying day are rare) with the worst expectancy of any
cell (−₹456.73/chain): late honest entries chase
already-extended moves. The leaky slope that rose with
measurement time (B2/B3) inverts into uniformly negative
honest books at every measurement time.

### Stack cell (B3 stack, honestly rebuilt)

Best honest base by the frozen selection rule = 10:30
(highest pooled net — i.e. least negative). Same-direction
ON, cap 1, exits T125/S065, honest search: 1,107 chains,
**−₹77,570.58** (Jan–May −₹65,981.78 / Jun–Oct −₹11,588.80,
October −₹22,799.52, breadth 21/50, max DD −₹106,766.07) —
**worse than its own base cell**. The stack that doubled the
leaky B3 book subtracts money from the honest one.

## Part 3 — Verdict

The frozen gate (pooled: both halves positive, breadth
≥ 35/50, October positive): **no honest configuration
passes — and no honest configuration passes even one single
leg of the gate.** All four base cells and the stack fail
Jan–May, fail Jun–Oct, fail breadth (best 21/50), and fail
October.

**The Morning-Mover line is dead in honest form.** Stated
plainly:

- The flagship's in-sample profits (+₹249,155.03 for A,
  +₹464,617.03 for B, pooled) were a look-ahead artefact:
  127.3% / 112.8% of them sat in entries placed before the
  qualifying measurement existed.
- Rebuilt so that every decision uses only information
  available at the moment it is made, the same rule loses
  money at every measurement time, on both universes, in
  both halves, after the frozen ₹40 cost. There is no
  honest configuration to freeze: **no
  `stocks_mover_honest_candidate_spec.md` is created.**
- The A2 (+₹406,054.73), B2 (+₹812,204.86) and B3
  (+₹1,623,905.15) candidates all inherit the identical
  whole-day search and fall with the flagship; their
  December fresh-window judging rules would judge after-close
  reconstructions of the same leak and cannot validate
  anything tradable. They should be recorded as dead with
  this line, not carried forward.
- **What remains:** nothing tradable from this construction.
  The one true fact the line established is that the
  post-measurement V5 second-signal stream, traded honestly
  on ≥1% morning-mover days, has negative expectancy after
  costs (−₹55 to −₹457 per chain across cells). B4's
  fixed-time control already showed the qualifying days
  themselves do not drift profitably after the measurement;
  this line shows the signal machinery adds nothing on top.
  Any future morning-momentum idea needs a different entry
  mechanism, its own frozen line, and — first — a
  leak-audit of exactly this kind before its numbers are
  quoted.

## What this means for the November shadow specs

Both frozen November Morning-Mover shadow specs —
`stocks_morningmover_november_shadow_spec.md` (home) and
`stocks_morningmover_ext_november_shadow_spec.md` (ext) —
specify generation by this same machinery: their rule text
calls the pre-move test "ex-ante, known at the measurement
time", but the discard-first construction they freeze
searches the day's signal stream from 09:15, and their own
validation sections log pre-measurement entries (09:50 under
the 10:00 variant; 10:00 under the 10:15 variant). The
November loggers run after the close, so as frozen they will
faithfully reconstruct the leaky books on fresh data.

Consequences, grounded in Part 1: in-sample, the leaky books'
pre-measurement slices carried +₹317,064.00 (A) and
+₹523,978.42 (B) of pooled profit while the real-time-knowable
slices lost money. A November run as frozen is therefore
expected to *look* healthy and to pass its ≥40-chain /
positive-net judging bar — while certifying a rule no live
trader can execute. A pass would promote an untradable rule;
a kill would say nothing about the honest rule either (Part 2
has already killed that in-sample, at both shadow measurement
times, on both universes).

**Recommendation: re-freeze both shadow specs to the honest
construction before the Mon 2026-11-02 launch** — signal
search starting at the first bar at/after the measurement
time, discard = first signal at/after measurement — and go
in with eyes open: the honest in-sample books at 10:00 and
10:15 are negative on both universes (pooled −₹117,200.13
and −₹167,156.86), so an honest November shadow tests a rule
that is already negative in-sample, and the parent may
reasonably decide it does not merit the slot at all. If the
leaky variants are run at all, run them only as explicitly
labelled controls (e.g. MOVER-A-LEAKY-CONTROL) whose verdicts
can never upgrade anything, kept purely to document the
reconstruction gap on fresh data. The alternative — running
November exactly as frozen and judging it as a hypothesis
test — is not recommended: its verdicts are uninterpretable
for any adoption decision. Re-freezing costs nothing today:
the launch is Monday 2026-11-02 and no November rows exist
yet. This line has edited no November spec and no November
log; the decision belongs to the parent.

## Files

- Freeze: `stocks_moverB5_frozen.md`
- Engine / results: `stocks_moverB5.py`,
  `stocks_moverB5_results.json`
- Dumps: `moverB5_AUDIT_A_trades.csv`,
  `moverB5_AUDIT_B_trades.csv`, `moverB5_HONEST_1000_trades.csv`,
  `moverB5_HONEST_1015_trades.csv`, `moverB5_HONEST_1030_trades.csv`,
  `moverB5_HONEST_1130_trades.csv`, `moverB5_STACK_trades.csv`
- No honest candidate spec — the Part 3 gate did not pass.
