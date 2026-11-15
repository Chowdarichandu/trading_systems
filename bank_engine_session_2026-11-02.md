# Bank Nifty Recursive Engine — Session 2026-11-02 (floor-target session)

**Objective (Chandu's directive, 2026-11-02):** Bank Nifty alone must reach a **₹15,000/month pace** = ≥ **₹1,50,000 across Jan–Oct 2026** on the gated book (index options premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE counting). Paper only, real money ₹0. The frozen November primary (BNF-PAPER-V1), its spec and its logs were never touched.

**Headline, plainly:** the session improved the book by **+₹27,370.50 (+35.5%)** in 7 cycles — and the floor was **not** reached. Ending book: **+₹104,567.00 Jan–Oct ≈ ₹10,457/month**, leaving a gap of **₹45,433.00 (₹4,543/month)**. This is an in-sample plateau; December fresh data in the Bank channel decides adoption.

---

## Starting point

Incumbent **book v8** (the Run-2 plateau, frozen 2026-10-31): **+₹77,196.50**, 82 trades, FT 53.7%, 2.02/week, no red month-ends. Gap to the floor pace: ₹72,803.50.

One structural fact governed the whole session: the book sits **exactly at the ≥2 trades/week banking-gate floor** (82 legs / 40.6 weeks = 2.02). Dropping even one net leg breaks the gate, so no leg-dropping fix could bank — the session worked exit-side and state-side only.

## Diagnosis before Cycle 21 (exact per-leg replays on book v8)

- **Dead:** the parked Run-1 runner-gate refinement (<250 → G0) = −₹3,600 on v8 (the <250 runner is worth +₹3,600; [250,400) +₹13,500). A state-strength threshold for the ≥400 runner (runner value is positive in *every* state band: warmup ₹0, [0,3k) +₹1,800, [3k,8k) +₹6,300, ≥8k +₹3,600). The no-progress **time-stop family** (the natural attack on the 2026-11-02 homework's quick-stop signature) loses at *every* grid point (best −₹1,359; 15-min/+40 headline −₹33,045) — Bank's eventual +180 runners routinely show MFE < +40 in their first 15 minutes, so at 15 minutes future winners and quick deaths are the same shape.
- **Live:** second target +210 splits by segment (≥400-warm −₹5,850 vs **<400 +₹3,150**); lock +90 on the ≥400-warm segment (its lock curve was never measured) **+₹4,500**; the only negative runner pocket by premium sub-band is ≥400-warm **[550,750) −₹1,800**.
- **Unreachable:** Jun/Jul (−₹15,820 in v8; 13 of 16 legs full stops, PE-dominated, no usable causal state signature — the regime PE bleed of lesson 28) and the expiry-day pocket (−₹2,510): every covering mechanism is leg-dropping and therefore frequency-blocked.

## Per-cycle verdicts

| Cycle | Mechanism (one change, frozen before scoring) | Verdict | Book total (₹) |
|---|---|---|---|
| 21 | Segment-split second target: +210 for <400 legs only (book-wide +210 was rejected in Cycle 19) | **BANKED** (+3,150: 7 legs reach, 1 falls back) | 80,346.50 (v9) |
| 22 | Segment-split lock: +90 for ≥400-warm runner legs only (<400 lock curve peaked at +75; this segment's was unmeasured) | **BANKED** (+4,500: 16 lock exits +450, 1 target leg cut) | 84,846.50 (v10) |
| 23 | Runner-off gate for ≥400-warm legs entered in [550,750) | **REJECTED — exact no-op**: Cycle 22's +90 lock had already closed the pocket (fall-back legs exit at the plain-target value) | 84,846.50 |
| 24 | <400 second target +210 → +240 (curve completion) | **BANKED** (+6,300: 7 of 7 reach, 0 fall back) | 91,146.50 (v11) |
| 25 | <400 second target +240 → +270 (after an independent path-by-path leak check on all 7 legs) | **BANKED** (+6,300: 7 of 7 reach) | 97,446.50 (v12) |
| 26 | <400 second target +270 → +300 (last step the verified paths provably reach; weakest clean maximum +323.3) | **BANKED** (+6,300: 7 of 7 reach) | 103,746.50 (v13) |
| 27 | <400 second target +300 → +330 (the turning step, measured per the peak rule) | **BANKED, thin** (+820.50: 6 reach; the weakest leg misses +330 and exits at its 15:10 close, −₹4,579.50) | **104,567.00 (v14)** |

Diagnosis-closed without a scored cycle (exact deltas on the then-current book): <400 target2 +360 = −₹10,879.50 (**the <400 curve peaks at +330**); ≥400 target2 curve peaked at +180 (+150 −₹1,800, +210 split −₹5,850); <400 lock +90 on the current assembly −₹2,250 (peak +75 stands); ≥400-cold legs given the runner +₹2,700 on exactly one leg (noise); (lA) deep-cold un-skip — the only marginally-cold skipped leg was itself a full stop; trailing-15 state window +₹450 on exactly one leg (noise); the break-hold/confirmation family stays rejected in its scored form (2026-11-02 fix test) and all sibling forms are frequency-blocked on this book.

Every scored cycle ran the **full controls gate in the same run**: sanity reproduction of the incumbent book to the paisa before the variant was read; timing audit on all 82 entry bars (0 violations in every cycle); placebo (identical assembly, entries +30 min) beaten in every cycle (final book's placebo: +₹10,830.70 vs +₹104,567.00); halves; full month table; ex-top-3 stress; independent re-sum from the written trades file (matched to the paisa in every cycle); NOT_COMPUTED = 0 in every cycle. Blocked legs were never scored from spot: the known NOT_COMPUTED add-on legs (NS3 14, NS5a 19, NS5b 17) remain unscored and were not chased — every admitted sample of those families lost on premiums in Runs 1–2.

## Ending book — engine book v14 (frozen verbatim in `bank_engine_frozen.md` as the December candidate)

- **Pool:** V1 = B2 base legs + NS1 second legs, UNIQUE-ONCE (date, direction), earliest entry; NS1 CE second legs blocked; legs with entry premium in [400, 550) blocked.
- **State rule:** skip an (lA) v2 leg when the anchored trailing-10 state is cold (trailing-10 net of book-v4 outcomes known at its entry < 0, ≥10 known legs).
- **Exits** (stop −50, first target +90, stop before target, square-off 15:10):
  - Entry premium < 400 → runner: lock **+75** after the trigger, second target **+330**.
  - Entry premium ≥ 400, warm state → runner: lock **+90**, second target **+180**. Cold state → plain G0.

### Full controlled scorecard (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade)

- **Net: +₹104,567.00** · Trades: **82** · Full-target rate: **53.7%** (44/82) · Frequency: **2.02/week** · Red month-ends: **none**
- Halves: Jan–May **+₹84,980.00** / Jun–Oct **+₹19,587.00** (both ≥ 0)
- Placebo (+30 min): **+₹10,830.70** (beaten by ₹93,736.30) · Ex-top-3: **+₹75,527.00** · Top-3 legs: 21 Jan PE +₹9,680, 23 Jan PE +₹9,680, 19 Feb PE +₹9,680 (the +330 runner targets)
- Timing audit: 0 violations / 82 entry bars · Independent re-sum: matched · NOT_COMPUTED: 0

| Month | Net ₹ | Cumulative ₹ |
|---|---|---|
| Jan | +23,730.00 | +23,730.00 |
| Feb | +23,670.00 | +47,400.00 |
| Mar | +15,880.00 | +63,280.00 |
| Apr | +6,360.00 | +69,640.00 |
| May | +15,340.00 | +84,980.00 |
| Jun | −6,120.00 | +78,860.00 |
| Jul | −9,250.00 | +69,610.00 |
| Aug | +8,499.00 | +78,109.00 |
| Sep | +2,487.50 | +80,596.50 |
| Oct | +23,970.50 | +104,567.00 |

(June and July are negative as individual months; every month-end cumulative close is positive, as the gate requires.)

## Against the floor

| | ₹ Jan–Oct | ₹/month |
|---|---|---|
| Floor pace (Chandu, 2026-11-02) | 1,50,000.00 | 15,000.00 |
| Session start (book v8) | 77,196.50 | 7,719.65 |
| **Session end (book v14)** | **104,567.00** | **10,456.70** |
| **Remaining gap** | **45,433.00** | **4,543.30** |

The session closed **37.6%** of the gap. All of the gain is exit-side value extraction (segment-split runner parameters + the <400 second-target curve measured to its peak) — no new entries, because none exist on premiums.

## Why it stops here (saturation)

Termination follows the engine's own exhaustion standard (the one that closed Run 2): the last paying family (the <400 target curve) has been measured to its peak and closed at +330, and every other remaining family is closed by a scored verdict or an exact path-level diagnosis (census in `bank_engine_log.md`, session termination entry; lessons 35–41). The binding wall is the **frequency floor itself**: at 82 legs = 2.02/week, no losing leg may be dropped, and there is no unscored premium entry family left to add legs with. Further Bank gains require a genuinely new premium-scored entry mechanism (none is currently known — the add-on census is exhaustive and the blocked NS3/NS5 legs have lost in every admitted sample) or fresh-data evidence in December, not more exit tuning.

Files: per-cycle trades `bank_engine_cycle{21..27}_trades.csv` and summaries `bank_engine_cycle{21..27}_summary.json`; definitions frozen in `bank_engine_frozen.md`; log in `bank_engine_log.md`; lessons 35–41 in `bank_engine_lessons.md`; state in `bank_engine_state.json` (best book v14).
