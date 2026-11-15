# Bank Nifty engine — ROUND 3 (targeted techniques), 2026-11-02

Starting book: **v16 = +₹106,517.00** Jan–Oct 2026 (premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0). Floor: ₹1,50,000 (₹15,000/month). Gap at start: ₹43,483.00.
Ending book: **v17 = +₹107,930.00** — ₹10,793.00/month. **Gap at end: ₹42,070.00.** Floor NOT reached.
22 cycles (42–63) across the four mandated workstreams; every candidate premium-scored under the full controls gate in the same run (timing/leak audit, placebo +30 min, halves, month table, ex-top-3, independent re-sum). Definitions were frozen in `bank_engine_frozen.md` (Round-3 appendix) before any Round-3 scoring; one pre-scoring amendment (Setup-4's two documented day-open readings) is recorded there. **NOT_COMPUTED = 0 on every candidate** — 52 contracts fetched this round via the expired-instruments route (browser User-Agent), 0 failures. November primary/spec/logs untouched.

## Workstream 1 — the unscored legs, unblocked (Cycles 42–44)

Census reproduced the parked counts exactly. After fetching 31 contracts, the three families were premium-scored completely for the first time. Completed censuses on book v4 (original Cycles 8/9/10 re-run post-fetch, same frozen definitions):

| Family | Partial sample (Rounds 1–2) | Completed census on v4 | On v16 (banking test) | Verdict |
|---|---|---|---|---|
| NS3 (gap class) | 6 legs, −₹2,127 | 18 admitted, **+₹13,821.00** | 19 admitted, **+₹11,051.00** → book +₹117,568.00 | NOT banked — fails only FT90 (51.5% < 53.7%) |
| NS5a (Skill rescan) | 12 legs, −₹4,047 | 30 admitted, −₹9,792.00 | 35 admitted, −₹17,642.00 → book +₹88,875.00 | Rejected (net, FT90) |
| NS5b (CE mirror) | 8 legs, −₹1,160 | 23 admitted, −₹18,012.50 | 23 admitted, −₹18,012.50 → book +₹88,504.50 | Rejected (net, Sep flip, FT90) |

The NS3 partial-sample verdict **reversed sign** on completion: the family is genuinely positive. Its money comes from runner locks and partials (8/19 full targets; three +₹2,030 runner-stop exits, one +₹5,180 runner target), so it dilutes FT90 in every assembly — the single gate leg it fails, everywhere it was tried (Cycles 42, 58, 63). NS5b's family net is identical under the v4 and v16 assemblies (−₹18,012.50 both) — an independent cross-validation of the Round-3 scorer.

## Workstream 2 — mechanised unbuilt setups (Cycles 45–52)

Signals regenerated mechanically from stored 5-min spot (`bank_r3_setups.py`), frozen definitions; 21 contracts fetched; NC 0.

| Cycle | Family | Admitted | Family net | Book | Failed gate legs |
|---|---|---|---|---|---|
| 45 | S3-A: OR ≥400 (v4 reading), close rejection | 6 | +₹2,280.00 | +₹108,797.00 | FT90 53.4% only |
| 46 | S3-B: OR 350–580, close rejection | 9 | −₹7,080.00 | +₹99,437.00 | net, FT90 |
| 47 | S3-C: OR 400–650, close rejection | 5 | −₹200.00 | +₹106,317.00 | net, FT90 |
| 48 | S3-D: wick rejection (≥1.5× body) | 3 | +₹445.50 | +₹106,962.50 | FT90 52.9% only |
| 49 | S3-E: close back below PDC | 4 | +₹1,520.00 | +₹108,037.00 | FT90 53.5% only |
| 50 | S4 reclaim — spec reading (open < PDC & PDL) | 1 | −₹1,720.00 | +₹104,797.00 | net, FT90 |
| 51 | S4B reclaim — v4 as-coded (open < PDC) | 9 | −₹7,080.00 | +₹99,437.00 | net, Sep flip, FT90 |
| 52 | S1 retest-hold on derived Red bands | 7 | −₹3,176.50 | +₹103,340.50 | net, FT90 |

Readings: the Setup-3 close-rejection family is mildly positive at the document's own band edges (S3-A/E) and negative when the band widens downward (S3-B) — widening the OR band admits weaker rejections. Setup 4's reclaim, under either documented reading, buys the spent point of the trap. The derived Red bands (prior-10-day rejected swing-high clusters) do **not** reproduce the hand-drawn bands' Setup-1 edge — a negative for this derivation, recorded as such.

## Workstream 3 — execution optimisation (Cycles 53–57)

Sanity asserted in-run before any variant was read: the frozen convention (entry-bar open, square-off 15:10) reproduces v16 to the paisa, main and placebo.

| Cycle | Variant | Net | Verdict |
|---|---|---|---|
| 53 | EC-A: enter at the entry bar's CLOSE | +₹42,752.00 | Rejected — net −₹63,765 vs v16, May flips red, FT90 43.9% |
| 54 | EC-B: enter at the NEXT bar's OPEN | +₹41,339.00 | Rejected — net −₹65,178, May flips red, FT90 42.7% |
| 55 | Square-off 14:45 | +₹107,871.50 | **BANKED** vs v16 (+₹1,354.50) |
| 56 | Square-off 15:00 | +₹104,795.00 | Rejected (net) |
| 57 | Square-off 15:20 | +₹107,930.00 | **BANKED** vs v16 (+₹1,413.00) → **book v17** |

Entry delay is the book's most expensive axis: the first 5–10 minutes after the frozen entry carry the edge (same direction as the Day-1 hold-confirmation rejection, larger). Note on Cycles 53–54: the controls' timing audit flags all 82 rows because it checks entry == entry-bar open; for these two variants the entry price is by construction a different real price (the same bar's close / the next bar's open — both causal, no look-ahead, visible in `bank_r3_ws3.py`). The candidates fail on net regardless; no reliance is placed on them. The square-off curve is non-monotonic (14:45 and 15:20 both beat the frozen 15:10; 15:00 dips below it) — 15:20 is the frozen set's peak and becomes v17.

## Workstream 4 — combinations on v17 (Cycles 58–63; gate vs v17)

| Cycle | Stack | Net | n | FT90 | Failed legs |
|---|---|---|---|---|---|
| 58 | v17 + NS3 | +₹122,609.50 | 101 | 52.5% | FT90 only |
| 59 | v17 + S3-A | +₹110,210.00 | 88 | 53.4% | FT90 only (one leg short) |
| 60 | v17 + S3-E | +₹109,450.00 | 86 | 53.5% | FT90 only (one leg short) |
| 61 | v17 + NS5a | +₹93,648.00 | 117 | 45.3% | net, FT90 |
| 62 | v17 + NS5b | +₹91,072.50 | 105 | 45.7% | net, Sep flip, FT90 |
| 63 | v17 + NS3 + S3-A + S3-E (+S3-D: 0 admitted after key consumption) | **+₹127,369.50** | 108 | 52.8% | **FT90 only (57/108; 58 needed)** |

**FLAGGED for Chandu's decision (not banked):** the Cycle-63 stack passes every gate leg except FT90 — net +₹127,369.50 (₹12,736.95/month; floor gap would fall to ₹22,630.50), halves +₹105,741.00 / +₹21,628.50, placebo +₹15,367.50 beaten, ex-top-3 +₹98,329.50, no red month-ends, no month flips, timing clean, NC 0. The FT90 waiver is the owner's call (Nifty CH3-R precedent), not the engine's.

## Ending scorecard — book v17 (December candidate)

+₹107,930.00 · 82 trades · 2.02/week · FT90 53.7% · no red month-ends · months Jan +29,163.00 / Feb +24,120.00 / Mar +15,880.00 / Apr +6,810.00 / May +15,340.00 / Jun −6,120.00 / Jul −13,000.00 / Aug +8,806.50 / Sep +2,321.00 / Oct +24,609.50 · halves +₹91,313.00 / +₹16,617.00 · placebo +₹18,380.50 beaten · ex-top-3 +₹78,890.00 · timing audit 0 violations · NOT_COMPUTED 0 · independent re-sum 82 / +₹107,930.00 ✓. Trades: `bank_engine_r3_v17_trades.csv`. **Pace ₹10,793.00/month vs the ₹15,000 floor — remaining gap ₹42,070.00.**

## What Round 3 established

1. The data wall is gone: every add-on family in the engine's history is now fully premium-scored. One family (NS3) was misjudged for two rounds on a 6-leg sample.
2. The unbuilt setups are built and gated: small real positives in Setup 3's close-rejection readings; negatives for Setup 4 (both readings) and for mechanically derived Red bands.
3. Execution timing is worth +₹1,413 (square-off 15:20) and entry delay is ruinous (−₹64k class) — a hard constraint for any future live-fill design.
4. The remaining ₹42,070 does not live in any space this round was mandated to search. The two live items are Chandu's: the Cycle-63 FT90 waiver decision (worth +₹19,439.50 if adopted), and December fresh data judging v17.
