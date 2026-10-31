# Aggressive Tuning — BANK NIFTY channel (October 2026 premiums first)

**Real money: ₹0 — paper only, no live trades, no orders. Index OPTIONS only, 1 lot (Bank lot 30).**
This file is the Bank channel only. Nifty is in `aggressive_oct_nifty.md`. The two channels are never pooled and there is no combined verdict.

## Why this run exists

Historical proof (real premiums, Jan–Oct): U1-B2 = **+₹18,731.50 over 10 months (~₹1,900/month)** — too thin. User instruction 2026-10-30 14:46 IST: start aggressive tuning, October first. Stacking and wider search ARE allowed in this run (superseding the earlier one-knob discipline for this run only).

## Kept best (baseline, reproduced exactly before scoring)

**U1-B2, October premiums: +₹13,920.00 — 9 trades, 7 targets / 2 stops, 77.8% full-target, 2.50/week.**
Jan–Oct premiums: +₹18,731.50 (89 trades, 43.8% FT, 2.19/week); January month-end closes RED (−₹1,920 cumulative) — the only red month-end.

## Conventions (same as the October premium work)

Entry = open of the 5-min option candle at the leg's entry bar; stop checked before target on every bar including the entry bar; square-off 15:10 close; cost ₹220/trade; net = (exit − entry) × 30 − ₹220. October = 1–28 Oct, 18 trading days = 3.6 weeks. Jan–Oct check weeks = 40.6.
**Method note:** NS1/NS2 add-on legs are re-scored here at their spot entry bar — the same convention as the base legs. Their older file nets used "first candle after signal time", which for rescan legs is a different (earlier) bar; those old nets are NOT used anywhere in this report. Bank add-on legs happen to score identically under both conventions; the difference shows up in the Nifty channel.
**NOT_COMPUTED: 0 in every candidate, both windows.** All 198 missing premium contracts (ITM October strikes + NS Jan–Sep add-ons) were fetched via the script-token browser-fetch route before scoring.

## Frozen candidates (written before scoring)

- **Family 1 — exit geometry on B2 legs:** G0 baseline −50/+90; G1 −50/+120; G2 −50/+150; G3 −65/+90; G4 −65/+120; G5 −65/+150; G6 runner (after +90, stop → entry, second target +150); G7 runner-lock50 (after +90, stop → entry+50, second target +150); G8 partial (50% booked at +90, rest trailed BE→+150 — theoretical fractional-lot, 1 lot cannot actually split; flagged wherever shown).
- **Family 2 — volume (unique-once per date+index+direction, earliest entry):** V1 = B2 + NS1 second legs; V2 = B2 + NS2 afternoon legs; V3 = B2 + both; V4 = V3 with filter (a-NS) on add-ons (add-on kept only if that day's earliest base leg did not exit "stop"; add-ons on base-less days dropped); V5 = V3 with filter (c) on add-ons (add-on kept only if its entry premium is not in the top third of its premium range from day start to entry).
- **Family 3 — entry quality on B2 legs:** E1 premium-momentum gate (entry-bar premium close ≥ open); E2 stronger gate (close − open ≥ 5 pts); E3 premium-VWAP gate (entry ≥ premium VWAP from day start to entry bar); E4 entry delayed one bar.
- **Family 4 — components (representative-system based, as in the U1 diagnosis):** C1 drop weakest October rep (none dropped — all four reps are net-positive in October, so no C1 exists for Bank); C2 every two-rep union; C3 confirmed-only (legs with ≥2 source systems).
- **Family 5 — strike:** F5 = B2 legs re-scored on the 100-pt ITM strike (CE: strike−100, PE: strike+100), same −50/+90 geometry.
- **Stacks:** S1 = V3 pool + best October geometry (G7); S2 = S1 + momentum gate; S3 = top-2-rep union + NS add-ons + best geometry. Supplementary sweep after the main table: pooled V3 legs × every geometry, and drop-Skill-rep subset × runner geometries. Stack geometry was selected on October — that selection is in-sample and is flagged as such.

## October results — ranked (premiums per 1 lot)

| # | Candidate | Trades | /week | Full-target % | Oct net ₹ | Jan–Oct check ₹ (FT%, red month-ends) |
|---|---|---|---|---|---|---|
| 1 | V1 base+NS1second | 12 | 3.33 | 75.0% | **+17,160.00** | +23,703.50 (42.3%, none) |
| 1= | V3 base+NS1+NS2 | 12 | 3.33 | 75.0% | **+17,160.00** | +21,432.50 (41.5%, none) |
| 3 | V5 V3+filter-c | 10 | 2.78 | 80.0% | +16,400.00 | +16,060.50 (42.3%, **Sep red**) |
| 4 | POOL+G3 (−65/+90 on V3 pool) | 12 | 3.33 | 75.0% | +15,810.00 | not checked (below V1 on Oct net and FT) |
| 5 | S1 V3 pool + G7 | 12 | 3.33 | 75.0% | +15,360.00 | not checked (dominated by V1) |
| 6 | G7 runner-lock50 | 9 | 2.50 | 77.8% | +14,520.00 | +22,931.50 (43.8%, none) |
| 7 | **G0 = U1-B2 baseline** | 9 | 2.50 | 77.8% | **+13,920.00** | **+18,731.50 (43.8%, Jan red)** |
| 7= | V2 base+NS2aft | 9 | 2.50 | 77.8% | +13,920.00 | — (identical set: the one NS2 Bank add-on, 21 Oct PE 12:00, is a unique-once duplicate of the 11:20 base leg) |
| 7= | V4 V3+filter-aNS | 9 | 2.50 | 77.8% | +13,920.00 | — (filter dropped all 3 surviving add-ons: 6/12/27 Oct had no base leg that day) |
| 7= | E4 delay-1-bar | 9 | 2.50 | 77.8% | +13,920.00 | — (entries change, barrier outcomes coincide on all 9 legs — verified leg by leg) |
| 11 | S2 S1+mom gate | 6 | 1.67 | 100.0% | +13,680.00 | — |
| 12 | G8 partial+trail (theoretical) | 9 | 2.50 | 77.8% | +13,470.00 | — |
| 13 | G3 −65/+90 | 9 | 2.50 | 77.8% | +13,020.00 | — |
| 13= | G6 runner-BE | 9 | 2.50 | 77.8% | +13,020.00 | — |
| 15 | S3 top2-union+NS+G7 | 10 | 2.78 | 80.0% | +12,800.00 | — |
| 16 | C2 union [Skill V3+V5 v2] | 6 | 1.67 | 83.3% | +10,680.00 | — |
| 17 | G1 −50/+120 | 9 | 2.50 | 55.6% | +10,020.00 | — |
| 18 | E1 mom gate / E2 mom+5 gate | 4 | 1.11 | 100.0% | +9,920.00 | — |
| 18= | C2 union [V5 v2+Volrix (b)] | 4 | 1.11 | 100.0% | +9,920.00 | — |
| 20 | F5 ITM-100 strikes | 9 | 2.50 | 66.7% | +9,720.00 | — |
| 21 | G2 −50/+150 | 9 | 2.50 | 44.4% | +8,520.00 | — |
| 22 | G4 −65/+120 | 9 | 2.50 | 55.6% | +8,220.00 | — |
| 23 | C2 union [(lA) v2+V5 v2] | 5 | 1.39 | 80.0% | +8,200.00 | — |
| 24 | E3 VWAP gate | 6 | 1.67 | 66.7% | +6,480.00 | — |
| 25 | G5 −65/+150 | 9 | 2.50 | 44.4% | +6,270.00 | — |
| 26 | C2 union [Skill V3+Volrix (b)] | 4 | 1.11 | 75.0% | +5,720.00 | — |
| 27 | C2 union [(lA) v2+Skill V3] / C3 confirmed-only | 5 | 1.39 | 60.0% | +4,000.00 | — |
| 29 | C2 union [(lA) v2+Volrix (b)] | 3 | 0.83 | 66.7% | +3,240.00 | — |

(V1 and V3 are the same October set: Bank's only NS2 add-on is duplicate-dropped, so NS2 adds nothing in this channel. The 3 add-ons that survive unique-once in V1/V3 — 6 Oct CE stop −₹1,720, 12 Oct PE target +₹2,480, 27 Oct PE target +₹2,480 — sum +₹3,240 over baseline.)

## Jan–Oct premium check (the anti-overfit column)

| Candidate | Trades | /week | FT% | Jan–Oct net ₹ | Red month-ends | vs B2 baseline |
|---|---|---|---|---|---|---|
| V1 base+NS1second | 130 | 3.20 | 42.3% | **+23,703.50** | **none** (Jan +₹1,398 close) | +₹4,972.00 above baseline; fixes the red January |
| G7 runner-lock50 | 89 | 2.19 | 43.8% | +22,931.50 | **none** (Jan +₹1,680 close) | +₹4,200.00 above baseline; fixes the red January |
| V3 base+NS1+NS2 | 142 | 3.50 | 41.5% | +21,432.50 | none | +₹2,701.00 above baseline |
| G0 = U1-B2 baseline | 89 | 2.19 | 43.8% | +18,731.50 | Jan | — |
| V5 V3+filter-c | 111 | 2.73 | 42.3% | +16,060.50 | **Sep** (cum −₹339.50) | **−₹2,671.00 BELOW baseline**, and breaks September's green close |

## Rejected list (failed leg named)

- **V5 (filter-c pool)** — passes all three October legs (net +₹16,400 > baseline, FT 80.0% ≥ 77.8%, 2.78/wk) but the Jan–Oct check goes **backwards**: total below B2 and a new red month-end (September). **October-fitted. Rejected as a replacement.**
- **G1/G2/G4/G5 (bigger fixed targets)** — FT collapses (44–56%); the +90 target is not the binding constraint in this channel, October premiums rarely travel +120/+150 before reversing. Rejected on FT and net.
- **G3/G6 (wider stop / BE runner)** — identical ₹13,020, below baseline: wider stops rescue nothing in October, BE runner gives back. Rejected on net.
- **G8 partial** — below baseline even as a theoretical fractional-lot. Rejected on net.
- **E1/E2/E3 gates** — perfect or high FT on 4–6 trades but frequency collapses (1.11–1.67/wk) and net falls. Rejected on frequency and net.
- **F5 ITM strikes** — ₹9,720, FT 66.7%: ITM premiums move less per spot point, +90 is harder. Rejected on net and FT.
- **All C2 unions / C3 confirmed-only** — Bank's edge is spread across all four reps; every subset loses more net than it gains in FT, and frequency falls below 2/wk. Rejected on frequency (and net vs baseline).
- **S1/S2/S3 stacks and pooled-geometry sweep** — no stack beats plain V1/V3; stacking the October-best geometry (G7) onto the pool makes it worse (₹15,360 < ₹17,160). Rejected on net.

## Verdict — Bank channel

**U1-B2 stays the kept best. No candidate formally replaces it.**

- The replacement rule needs October net AND full-target beaten, frequency ≥2/week, and a Jan–Oct check that does not go backwards. **Nobody passes all of it.**
- **Closest: V1 (B2 + NS1 second legs)** — best October net at full frequency (**+₹17,160**, 3.33/wk) and the best Jan–Oct check (**+₹23,703.50**, no red month-end — it fixes B2's red January). It fails ONE leg: October FT 75.0% vs B2's 77.8% (the added legs hit 2 of 3 targets; the pool dilutes the rate by 2.8 points). Not October-fitted — its Jan–Oct is proportionally as strong. **Best November-paper watch candidate alongside B2, not a replacement.**
- **Second: G7 (runner-lock50 on B2 legs)** — improves net on BOTH windows (+₹600 October, +₹4,200 Jan–Oct) and fixes the red January, with FT and frequency exactly held (77.8% / 43.8%), not beaten. A genuine small improvement, not a formal pass.
- **October ceiling found by this sweep: +₹17,160.** The user's ₹20,000+/month bar is **not reached** in the Bank channel by any candidate, at any frequency. Even the best Jan–Oct check (V1) averages only ~₹2,370/month — the honest problem is not October, it is that Jan–Sep premiums are thin in this channel no matter how the exits are re-cut.
