# NOVEMBER FAILURE AUDIT — 2026-11-13

**Scope:** all November lines, Nov 2–12 (8 trading days; Nov 10 = Diwali holiday), against their Jan–Oct 2026 gated records. Bank stack v2 (primary), Bank legacy BNF-PAPER-V1, Nifty primary NF-PAPER-C3G7, DEC-S1, TUNED v1, TUNED v2, Stock Book, Stock Engine. SHORT-FOLLOW: n/a (starts Nov 13). **Diagnosis only — no book, filter, or parameter was changed.** Paper only, real money ₹0. Index figures = option premiums per 1 lot, net after ₹220/trade; stocks = provisional per 100 shares, net after ₹40/trade. Segments never pooled.

**Method / data limits (stated once, apply throughout):** every Jan–Oct anchor was re-summed from its leg file and matched exactly (stack +₹127,351.50/111 · v21 frame +₹83,650.50/99 · DEC-S1 +₹91,168.50/97 · TUNED v1 +₹103,050.25/74 · TUNED v2 +₹115,950.75/59 · Stock Book 2026 +₹2,47,178.79/1,363). Bank spot regime stats are computed from the stored 5-minute spot series (203 full sessions Jan–Oct + all 8 November days; a 14-bar 2026-11-08 fragment in the November spot file was excluded — not a session). **Nifty November intraday spot bars were fetched nightly by the live chain and not persisted**, so Nifty November regime detail is partial (see H2). The Stock Book leg file carries no exit-time field, so H3 is index-only.

## November final standings (the thing being explained)

| Line | Nov 2–12 net ₹ | Legs | Note |
|---|---|---|---|
| Bank stack v2 (primary) | **−960** (live-only −1,720) | 3 | live record = 1 leg, Nov 12 |
| Bank legacy | **−1,920** | 6 | 2 PE base −3,440 · 4 NS1 +1,520 |
| Bank shadows v21 / v22 / Skill | −2,680 / −960 / −1,160 | 4 / 3 / 8 | |
| Nifty primary C3G7 | **−3,470** | 1 | 1 trade in 8 days |
| DEC-S1 (shadow) | **−443.50** | 5 | gross was **+656.50** before costs |
| TUNED v1 (shadow) | **+3,036.50** | 1 | only positive Nifty line |
| TUNED v2 (shadow) | **0** | 0 | no leg fired |
| Stock Book | **+7,965.74** | 30 | Nov 6 alone = +6,577.68 (83%) |
| Stock Engine | **+265.06 live** | 3 | 1 live day; the Nov 2–11 "+6,764.38" is retrospective sim, not forward evidence |

---

## H1 — EXECUTION / CHAIN: did the machinery lose or mis-score real trades?

**Verdict: incidents CONFIRMED — as a cause of the losses, REJECTED.** The machinery delayed numbers on Nov 11–12; it did not create, lose, or mis-price a single trade. After recovery, every book has a complete 8-day record, and the recovered figures moved in *both* directions.

Incidents, verified and quantified:

1. **Stack scorer abort (daily-bar lag) — CONFIRMED.** On Nov 11 the v21-frame assembly (which the stack's scoring anchors on) aborted on its own guard: the scorer builds its day list from the Upstox daily-bar endpoint, which at scoring time still ended at 2026-11-09 (journal, 2026-11-11 NC entry; the scorer's own code comments describe the same lag). Nov 11 was excluded that night — never estimated — and catch-up scored it the next day as a **no-trade day**. So the stack's "₹0 / 0 legs live" at the Nov 12 15:45 compile was *unscored*, not *flat*; the recovered live record is Nov 11 no-trade + Nov 12 −₹1,720. **No stack P&L figure was ever revised — there was no hidden Nov 11 trade.**
2. **Nov 12 rows unscored at first compile (DEC-S1, v21, v22) — CONFIRMED, all recovered the same evening.** Numbers that changed after recovery: DEC-S1's Nov 11 leg was scored on Nov 12 → a **+₹3,680 win** landed late (MTD −4,123.50/4 trades → **−443.50/5**); v21 and v22 each gained a Nov 12 −₹1,720 leg (v21 −960 → **−2,680**; v22 +760 → **−960**). Recovery helped one line and hurt two — the signature of a *timing* defect, not a bias.
3. **Nov 4 SHADOW v22 NOT_COMPUTED — CONFIRMED, recovered.** The day's spot path was absent from the stored record that night (journal), so v22 (and the EVE-06(a) counterfactual) were NC; the +₹2,480 Nov 4 row is in the final log.
4. **Nov 2 live-producer miss — CONFIRMED, announcement layer only.** The live producer flagged the Bank entry MISSED at 10:34 (first poll after the entry bar), so one entry was not announced live. All November books are officially EOD-constructed; the EOD row exists and is the log of record. P&L impact: zero.
5. **Nov 4 circuit-breaker state — fired, on the record, working as designed.** Legacy posted 3 consecutive losing days (Nov 2/3/4) and MTD −₹5,160 crossed the ≤ −₹5,000 leg on Nov 4 — both bleed triggers fired. By the standing rule the breaker binds the shadow/December layer; the frozen primary was never paused (it traded Nov 9/11/12). The TUNED SHADOW line's own MTD leg fired Nov 9 (−₹5,160) and cleared Nov 12 (−₹2,900). No line is in breach tonight.
6. **Token chain — no failure on any of the 8 days.** Zero token incidents in the journals; every day's EOD construction completed on full 74–75-bar spot days; Nov 10's NO MARKET DATA line is the exchange holiday, correctly identified as such at the time.
7. Minor, P&L-neutral: the Stock Book's Nov 12 figure moved from the +₹265.06 live-layer estimate to the final **−₹425.54** when the EOD sleeves landed at 16:35 (ASTRAL INV-ABOVE −₹690.60) — scheduled completion, not a correction. A Nov 9 TATASTEEL book-vs-scorecard divergence (Muhurat prior-close) was recorded, not adjusted.

**NC count:** stack 2 day-incidents (Nov 11, Nov 12), DEC-S1 1 (Nov 11, scored next day), v21 1, v22 2 (Nov 4, Nov 12) — **all recovered; zero trades lost; zero final figures wrong.**

## H2 — MARKET REGIME: was November an outlier patch?

**Verdict: CONFIRMED as a contributing condition (Bank, full data) — a hostile patch inside the historical distribution, not a new regime. For Nifty November intraday detail: INSUFFICIENT DATA (bars not persisted).**

Bank Nifty spot, Jan–Oct (203 sessions) vs Nov 2–12 (8 sessions), computed from stored 5-minute bars:

| Metric | Jan–Oct | November | Reading |
|---|---|---|---|
| Median daily range | 1.151% | **1.406%** (65th pctile of Jan–Oct days) | bigger days, not extreme days |
| Median \|gap\| | 0.303% | **0.508%** (87th pctile) | a large-gap patch (Nov 5: +2.13%, Nov 2: +1.05%, Nov 11: +1.31%) |
| Trend days (close–open ≥ 50% of range) | 49.3% | **62.5%** (5/8) | trend-heavy |
| **Post-11:00 reversal days** (spot moves ≥0.7% against the morning direction after 11:00) | **21.7%** | **50.0%** (4/8: Nov 5, 6, 9, 11) | the hostile part |

The combination is what hurt: trend afternoons the morning-signal books cannot participate in (H3/coverage), *and* reversal days that ran against the morning PE legs. No single November day sits outside the Jan–Oct daily distribution — this is a bad draw of ordinary days, concentrated.

Nifty: Jan–Oct baseline — median range 0.880%, median |gap| 0.262%, trend share 46.8%, reversal share 18.2%. November intraday bars were not persisted, so the reversal/range table cannot be computed for Nifty November; what is recoverable points the same way (Nov 5 gap **+1.74%** vs a 0.26% median, followed by an all-day uptrend; the other recorded gaps are ordinary: Nov 4 −0.29%, Nov 6 +0.01%, Nov 9 +0.36%, Nov 12 −0.16%).

## H3 — ENTRY-BAR / STOP STRUCTURE and the missed moves

**Verdict: CONFIRMED as November's Bank loss shape (small sample, stated); NOT a Nifty pattern. A proven remedy does not exist — see fixes.**

Deduped Bank index stop-outs in November (the same trade counted once): Nov 2 PE 54800 — stopped **1 bar** after entry; Nov 9 PE 58900 — stopped **on the entry bar**; Nov 12 PE 61200 — stopped **1 bar** after entry; Nov 3 CE (10 bars) and Nov 4 CE (4 bars). **3 of 5 stops died within a bar of entry**, vs a Jan–Oct quick-stop share of **35.0%** (stack, 14/40 stops) and **36.2%** (v21 frame, 17/47). Per line, November quick-stop shares: legacy 2/4, stack 2/2, v21 3/3, Skill Bank 3/5.

What spot did in the 60 minutes after each deduped Bank stop (stored bars):

| Stopped leg | Adverse next 60m | Favourable next 60m |
|---|---|---|
| Nov 2 PE 54800 | +120.2 pts | 67.0 |
| Nov 3 CE 55500 | 51.6 | 123.3 (recovered — premium was ≈ +₹977 by 14:10) |
| Nov 4 CE 55900 | 40.2 | 195.9 |
| **Nov 9 PE 58900** | **+593.8 pts** | **18.6** |
| Nov 12 PE 61200 | 25.2 | 178.2 (spot fell back — the stop was near the extreme) |

One day is the catastrophe: **Nov 9** — an entry-bar stop, then spot ran +835.10 pts to close at its high (missed-move Bank #4). Nov 12 cuts the other way (the quick stop was well-placed). So the pattern is real but concentrated, not systematic: widening these stops is exactly what the Nov 12 tuning tested (T-B2a/T-B2b) — both failed the Jan–Oct gate, T-B2b by ₹1,060, because wider PE stops enlarge losses across the ten months. The flaw is documented; the fix has been tried and refused by the evidence.

Missed moves: **Bank ×4** (Nov 3 post-stop run +279.5 pts · Nov 5 flat book, afternoon +547.30 pts · Nov 6 flat book, afternoon extension +1,094.25 pts on a 3.05%-range day · Nov 9 post-stop +835.10) and **Nifty ×3** (Nov 5, Nov 6, Nov 11 — all flat-book days; the primary was C3-blocked on a solo morning key and no system fired again). Structural root, measured on 2026-11-12: of 509 U1 system signals Jan–Oct, exactly **1** occurs at/after 13:30 — the books have no afternoon signal source to re-enter with. Two of Bank's four missed moves and all three of Nifty's happened while the book was *flat*, not stopped out. This is a coverage property of the frozen constructions, priced into their Jan–Oct records (which include the same flat afternoons), not a November malfunction.

Nifty stops show no quick-stop pattern at all: DEC-S1's November stops took 41–42 bars (Jan–Oct quick-stop share for the whole DEC-S1 family: **0.0%** — its BE-arm/runner geometry holds legs for hours by design), and the primary's only stop took 8 bars.

## H4 — SIDE ASYMMETRY: PE vs CE

**Verdict: CONFIRMED — November's index losses are PE-side losses, inverting the structure that made the books profitable.**

Jan–Oct, PE is the profit engine of every index book: stack PE **+₹97,066.50** (90 legs) vs CE +₹30,285.00 (21); v21 frame PE **+₹56,825.50** (80) vs CE +₹26,825.00 (19); DEC-S1 PE +₹58,562.50 (56) vs CE +₹32,606.00 (41); TUNED v1/v2 PE +₹70,444.25.

November, deduped Bank trades: PE went **1W/3L** (Nov 4 S3-R1 runner +2,480; Nov 2/9/12 stops −1,720 each), while Bank CE legs *made* money (legacy CE net +₹1,520; Skill Bank CE +₹2,280). Per line: legacy PE −3,440 vs CE +1,520 · stack PE −960 (all 3 legs PE) · v21 PE −2,680 · Skill Bank PE −3,440 vs CE +2,280. On the reversal-heavy patch of H2, the books kept expressing their (normally correct) downside/PE bias into mornings that reversed up.

Nifty adds the known, specific case: DEC-S1's **B-PE leak fired again, exactly as pre-diagnosed** — November B legs 4, net **−₹3,480** (1 win), the same class that lost −₹11,881.75 across Jan–Oct while B-CE made +₹45,506.50. DEC-S1's November PE total −₹3,480 vs CE +₹3,036.50. TUNED v1 — DEC-S1 with B-PE removed — is November's only positive Nifty line (+₹3,036.50) *because* the removal works. The Nifty primary's single leg was also PE (Nov 9, the same breakdown morning as Bank's entry-bar stop).

## H5 — NORMAL VARIANCE: is November outside the books' own history?

**Verdict: REJECTED. At the matched 8-trading-day horizon, November is an unremarkable draw for every book individually. The "everything failed at once" impression is a counting artefact (H5b).**

Full-month distributions Jan–Oct: stack — 0 red months, worst +₹2,059.50, mean +₹12,735.15 · TUNED v2 — 0 red, worst +₹1,911.75 · TUNED v1 — 1 red (Mar −₹1,216.50) · DEC-S1 — 2 red (Mar **−₹11,846.50**, Jun −₹1,331.00), mean +₹9,116.85 · v21 frame — 3 red (Apr −90, Jul −3,680, Aug −873.50) · Stock Book — 0 red, worst +₹6,756.75. Red months and bad patches are already in every Nifty book's record and in the Bank legacy frame's.

But November has only 8 trading days, so the honest test is the rolling 8-trading-day window over Jan–Oct (196 windows per book):

| Book | Worst Jan–Oct 8-day window | Mean 8-day window | % of 8-day windows negative | November's 8 days | November percentile |
|---|---|---|---|---|---|
| Stack v2 | −6,880.00 | +4,951.44 | 23.0% | −960 | 15th |
| v21 frame (legacy) | −8,600.00 | +3,200.38 | 33.7% | −1,920 | 21st |
| DEC-S1 | −17,360.00 | +3,650.89 | 30.1% | −443.50 | 29th |
| TUNED v1 | −13,670.00 | +4,135.86 | 26.0% | +3,036.50 | 45th |
| TUNED v2 | −6,730.00 | +4,630.46 | 19.4% | 0 | 25th |
| Stock Book | −5,782.80 | +9,332.73 | 16.3% | +7,965.74 | 58th |

Roughly **one in four** Jan–Oct 8-day windows was negative for each index book. November sits between the 15th and 58th percentile everywhere — below average, nowhere near the tail.

**H5b — why it *looked* simultaneous:** the lines are not independent draws. November's 37 index leg-instances across the audited lines reduce to **25 distinct trades**; the single Nov 9 Bank PE 58900 leg appears in **5 lines at once** (legacy, its control, v21, v22, stack backfill), Nov 2 PE in 3, Nov 4 PE in 3, Nov 12 PE in 3, the Nov 9 Nifty PE in 2. All index books draw on the same four U1 systems over the same 8 days, 5 of which were trend/reversal days. One bad patch, counted many times — and two lines (Stock Book, TUNED v1) didn't dip at all.

**Exception — the Nifty primary itself: INSUFFICIENT DATA.** C3G7 was never scored over Jan–Oct (read-only by rule; only a comparison baseline exists, +₹54,102, which is not its score). Its November (1 trade, −₹3,470) therefore *cannot* be placed in its own distribution. "The primary failed in November" and "the primary is a very low-frequency construction" cannot be separated with the records that exist. That is an auditability gap in the programme, recorded here as a finding.

## H6 — COSTS / FREQUENCY

**Verdict: REJECTED as a cause; CONFIRMED as an amplifier.** Per-leg costs are unchanged (₹220 index / ₹40 stocks) and activity ran at or above Jan–Oct pace on the active lines — legacy traded 6 of 8 days (Jan–Oct v21 frame: 92/203 days, 0.49 legs/day; November legacy 0.75 legs/day), DEC-S1 5 legs in 8 days vs 97 in 203, Skill lines traded every day. There was no frequency collapse to explain the losses.

What costs did do: in a near-zero-gross month, the fixed ₹220/leg toll is the P&L. November gross (pre-cost) vs net — legacy **−600 → −1,920** (costs ₹1,320) · stack **−300 → −960** (₹660) · DEC-S1 **+656.50 → −443.50** (₹1,100 — costs alone flipped DEC-S1's month negative) · v21 −1,800 → −2,680. In Jan–Oct the same toll ran at 16–21% of gross (stack 16.1%, DEC-S1 19.0%, v21 frame 20.7%). Nothing about costs changed; gross edge was simply absent for 8 days, so the toll shows.

The one genuinely idle line is by construction: C3G7 took 1 trade because on 6 of 8 days its only key was a solo Skill CE (C3 requires ≥2 systems) and on Nov 4 no system fired at all. The shadow that *did* take those blocked keys (Skill Nifty) lost **−₹2,966.75** in November — in this patch, the primary's idleness was net-protective, whatever it costs in better months (unmeasurable — see H5 exception). TUNED v2's zero legs are likewise construction: the only November candidate class that fired was B-PE, which v2 excludes.

---

## WHAT IS ACTUALLY WRONG (confirmed items only)

1. **A PE-side drawdown on a reversal patch (H2 + H4).** November's Bank patch — median |gap| at the 87th percentile, 4 of 8 days reversing ≥0.7% against the morning direction after 11:00 — hit the side that carries every index book (PE = ₹57–97k of each book's Jan–Oct profit). Deduped Bank PE trades went 1W/3L. This is a market-vs-book interaction on an ordinary-but-hostile patch, not a defect in any book's code or rules.
2. **Session coverage (H3).** The books are structurally absent from afternoon moves: 7 missed-move days in 8 (Bank 4, Nifty 3), with 1 of 509 Jan–Oct U1 signals occurring after 13:30. November's trend afternoons (Bank Nov 5 +547 pts, Nov 6 +1,094 pts of extension) made a known, gate-priced limitation expensive. It cannot be tuned away with the existing signal sources.
3. **DEC-S1 still carries the proven B-PE leak (H4).** It fired again (4 legs, −₹3,480), as it did for −₹11,881.75 across Jan–Oct. The cure already exists and is already ranked above it (TUNED v1 — which is positive in November precisely because the leak is removed). DEC-S1 itself remains FAILED-AND-WAIVED stock.
4. **Scoring-chain fragility (H1).** The shadow/stack scorer's dependence on the Upstox daily-bar endpoint delayed four lines' scoring across Nov 11–12, and the live producer missed announcing one entry (Nov 2). All recovered; worth zero rupees of the losses; still a real process defect — November's numbers were *late*, twice, at exactly the moments the owner was asking for them.
5. **The Nifty primary is unauditable (H5 exception).** C3G7 has no Jan–Oct record of its own, so no November verdict on it — good or bad — can be evidence-based. A primary that cannot be benchmarked is a programme defect, independent of its P&L.

## WHAT IS NOT WRONG

- **No trades were lost, invented, or mis-scored.** Every November figure in the final record is complete and re-summed; recovery moved figures in both directions (+3,680 to DEC-S1, −1,720 each to v21/v22).
- **No token or data-chain outage** on any of the 8 days; the Nov 10 gap is the exchange holiday.
- **Costs did not change** and activity did not collapse (H6) — the toll only became visible because gross was ~zero.
- **November is not outside any book's own history** at the matched horizon (H5): 15th–58th percentile of each book's Jan–Oct 8-day windows; ~1 in 4 such windows was negative all year.
- **Not everything failed:** the Stock Book is +₹7,965.74 (a 58th-percentile, ordinary-good window) and TUNED v1 is +₹3,036.50. "October good / November bad" is also partly the calendar: October was the Stock Book's best month of the year (+₹56,127.37) and a top-quartile month for the index books — some of the contrast is regression from an exceptional month, measured here rather than asserted.

## PROPOSED FIXES (evidence-labelled — NONE applied)

1. **Decouple the shadow/stack scorer from the daily-bar endpoint** — build its day list and prior-day levels from the intraday spot store (the workaround pattern already present in its own prep code), and **persist Nifty intraday spot bars nightly**. *Evidence: H1 incidents 1–3; the journal's 2026-11-11 NC entry; this audit's INSUFFICIENT DATA on Nifty November regime (H2).* Fixes lateness and future auditability; changes no P&L.
2. **Live-producer entry-announcement check** — reconcile the 1-minute watcher's flagged entries against the EOD construction nightly and report any MISSED flag the same evening. *Evidence: H1 incident 4 (Nov 2).* Announcement layer only.
3. **Retire DEC-S1 as a standalone December candidate; let TUNED v1 carry the slot** (it is already ranked first). *Evidence: H4 — the B-PE leak is now proven in both directions of time: −₹11,881.75 Jan–Oct and −₹3,480 in November, while the leak-free v1 is November's only positive Nifty line.* Stops spending forward days re-proving a proven leak.
4. **Give the Nifty primary a benchmark or replace the label** — either a one-time owner-approved historical scoring of the C3G7 construction, or formally designating a benchmarked book as primary. *Evidence: H5 exception.* Without this, every future month repeats this audit's dead end on the primary line.
5. **Explicitly NO exit/filter fix is proposed from November's evidence.** Wider PE stops (T-B2a/T-B2b), afternoon-capture sleeves (5 constructions), and the base-load fallback were all gated on Jan–Oct within the last 48 hours and failed; November's 5 deduped Bank stops and 8 days do not outweigh 203 days of gate evidence. *Evidence: H3 + the 2026-11-12 tuning programmes.* The standing remedy for a below-average 8-day patch inside normal variance is the already-running forward evidence: the rest of November, judged at full-month scale on Nov 30, and SHORT-FOLLOW's 20-day run from Nov 13.

*Computation: `november_failure_audit_compute.py` (read-only over the November logs, gated leg files, and stored spot series); all figures in this report are reproducible from it plus the cited journal/log entries.*
