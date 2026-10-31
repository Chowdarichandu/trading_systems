# Aggressive Tuning — NIFTY channel (October 2026 premiums first)

**Real money: ₹0 — paper only, no live trades, no orders. Index OPTIONS only, 1 lot (Nifty lot 65).**
This file is the Nifty channel only. Bank Nifty is in `aggressive_oct_bank.md`. The two channels are never pooled and there is no combined verdict.

## Why this run exists

Historical proof (real premiums, Jan–Oct): U1-N1 = **+₹25,159.00 over 10 months (~₹2,500/month)** — too thin, and only 25.9% of its Jan–Oct legs ever reached the +90 premium target (42 of 108 drifted to square-off). User instruction 2026-10-30 14:46 IST: start aggressive tuning, October first. Stacking and wider search ARE allowed in this run (superseding the earlier one-knob discipline for this run only).

## Kept best (baseline, reproduced exactly before scoring)

**U1-N1, October premiums: +₹10,775.25 — 8 trades, 4 targets / 3 stops / 1 square-off, 50.0% full-target, 2.22/week.**
Jan–Oct premiums: +₹25,159.00 (108 trades, 25.9% FT, 2.66/week); every month-end cumulative closes green.

## Conventions (same as the October premium work)

Entry = open of the 5-min option candle at the leg's entry bar; stop checked before target on every bar including the entry bar; square-off 15:10 close; cost ₹220/trade; net = (exit − entry) × 65 − ₹220. October = 1–28 Oct, 18 trading days = 3.6 weeks. Jan–Oct check weeks = 40.6.
**Method note:** NS1/NS2 add-on legs are re-scored here at their spot entry bar — the same convention as the base legs. Their older file nets used "first candle after signal time", which for rescan legs is a much earlier bar (e.g. the 5 Oct NS1 second leg: old file +₹345.50 entered 10:25; at its actual spot entry bar 12:05 it is a −₹3,470 stop). Those old nets are NOT used anywhere in this report. This convention change is most of why the pooled Nifty numbers here are worse than the toward-20k variant numbers quoted earlier — the earlier pool mixed two entry conventions.
**NOT_COMPUTED: 0 in every candidate, both windows.** All 198 missing premium contracts (ITM October strikes + NS Jan–Sep add-ons) were fetched via the script-token browser-fetch route before scoring.

## Frozen candidates (written before scoring)

- **Family 1 — exit geometry on N1 legs:** G0 baseline −50/+90; G1 −50/+120; G2 −50/+150; G3 −65/+90; G4 −65/+120; G5 −65/+150; G6 runner (after +90, stop → entry, second target +150); G7 runner-lock50 (after +90, stop → entry+50, second target +150); G8 partial (50% booked at +90, rest trailed BE→+150 — theoretical fractional-lot, 1 lot cannot actually split; flagged wherever shown).
- **Family 2 — volume (unique-once per date+index+direction, earliest entry):** V1 = N1 + NS1 second legs; V2 = N1 + NS2 afternoon legs; V3 = N1 + both; V4 = V3 with filter (a-NS) on add-ons (add-on kept only if that day's earliest base leg did not exit "stop"; add-ons on base-less days dropped); V5 = V3 with filter (c) on add-ons (add-on kept only if its entry premium is not in the top third of its premium range from day start to entry).
- **Family 3 — entry quality on N1 legs:** E1 premium-momentum gate (entry-bar premium close ≥ open); E2 stronger gate (close − open ≥ 5 pts); E3 premium-VWAP gate (entry ≥ premium VWAP from day start to entry bar); E4 entry delayed one bar.
- **Family 4 — components (representative-system based, as in the U1 diagnosis):** C1 drop weakest October rep (Skill V3: its 4 October legs sum −₹4,780); C2 every two-rep union; C3 confirmed-only (legs with ≥2 source systems). In October, C1 and C3 keep the **same 4 legs** (the dropped Skill legs are exactly the solo ones); they differ Jan–Oct.
- **Family 5 — strike:** F5 = N1 legs re-scored on the 100-pt ITM strike (CE: strike−100, PE: strike+100), same −50/+90 geometry.
- **Stacks:** S1 = V3 pool + best October geometry (G2); S2 = S1 + momentum gate; S3 = top-2-rep union + NS add-ons + best geometry. Supplementary sweep after the main table: pooled V3 legs × every geometry (all worse than the plain pool — none above −₹1,369.50 except G7-pool −₹2,334.75; omitted from the ranking except S1), and confirmed/solo-filtered subsets × runner geometries (C3+G7, C3+G2, C1+G7 — these produced the channel's biggest October numbers and were Jan–Oct checked). Stack geometry was selected on October — that selection is in-sample and is flagged as such.

## October results — ranked (premiums per 1 lot)

| # | Candidate | Trades | /week | Full-target % | Oct net ₹ | Jan–Oct check ₹ (FT%, red month-ends) |
|---|---|---|---|---|---|---|
| 1 | C3+G2 (confirmed-only, target +150) | 4 | 1.11 | 25.0% | +20,414.00 | +65,488.25 (10.7%, none) |
| 2 | C3+G7 (confirmed-only + runner-lock50) | 4 | 1.11 | 75.0% | **+18,805.25** | **+66,619.25 (37.5%, none)** |
| 2= | C1+G7 (drop-Skill + runner-lock50) | 4 | 1.11 | 75.0% | +18,805.25 | +40,072.50 (30.8%, none) |
| 4 | C1+G6 / C1+G2 | 4 | 1.11 | 75.0% / 25.0% | +18,161.75 | +30,478.50 / +35,444.50 (none) |
| 6 | C1 drop-Skill / C3 confirmed-only | 4 | 1.11 | 75.0% | +15,555.25 | C1 +33,354.75 (30.8%, none); C3 +55,939.75 (37.5%, none) |
| 8 | G2 −50/+150 | 8 | 2.22 | 12.5% | +12,390.50 | +27,196.75 (5.6%, none) |
| 9 | G7 runner-lock50 | 8 | 2.22 | 50.0% | +11,425.25 | +26,442.75 (25.9%, none) |
| 10 | **G0 = U1-N1 baseline** | 8 | 2.22 | 50.0% | **+₹10,775.25** | **+25,159.00 (25.9%, none)** |
| 10= | V4 V3+filter-aNS | 8 | 2.22 | 50.0% | +10,775.25 | — (filter dropped every surviving add-on) |
| 10= | E3 VWAP gate | 8 | 2.22 | 50.0% | +10,775.25 | — (gate kept all 8 legs — inert on N1's October) |
| 13 | G1 −50/+120 | 8 | 2.22 | 25.0% | +10,440.50 | — |
| 14 | E1 mom gate | 3 | 0.83 | 66.7% | +9,925.25 | — |
| 14= | C2 unions [(lA)+V5], [(lA)+Volrix] | 3 | 0.83 | 66.7% | +9,925.25 | — |
| 16 | G5 −65/+150 | 8 | 2.22 | 12.5% | +9,465.50 | — |
| 17 | G8 partial+trail (theoretical) | 8 | 2.22 | 50.0% | +9,153.50 | — |
| 18 | F5 ITM-100 strikes | 8 | 2.22 | 50.0% | +8,640.00 | — |
| 19 | G3 −65/+90 | 8 | 2.22 | 50.0% | +7,850.25 | — |
| 20 | G6 runner-BE | 8 | 2.22 | 50.0% | +7,531.75 | — |
| 21 | G4 −65/+120 | 8 | 2.22 | 25.0% | +7,515.50 | — |
| 22 | V5 V3+filter-c | 9 | 2.50 | 44.4% | +7,305.25 | — |
| 23 | V2 base+NS2aft | 10 | 2.78 | 40.0% | +5,320.50 | — |
| 24 | V1 base+NS1second | 13 | 3.61 | 30.8% | +2,470.00 | — |
| 25 | S3 top2-union+NS+G2 | 11 | 3.06 | 9.1% | +1,506.00 | — |
| 26 | C2 unions [Skill+V5], [Skill+Volrix] | 5 | 1.39 | 40.0% | +850.00 | — |
| 28 | C2 union [(lA)+Skill] | 6 | 1.67 | 33.3% | −484.75 | — |
| 29 | S1 V3 pool + G2 | 15 | 4.17 | 6.7% | −1,369.50 | — |
| 30 | V3 base+NS1+NS2 | 15 | 4.17 | 26.7% | −2,984.75 | — |
| 31 | S2 S1+mom gate | 6 | 1.67 | 0.0% | −3,019.75 | — |
| 32 | E4 delay-1-bar | 8 | 2.22 | 25.0% | −4,272.25 | — |

(What kills the pooled tracks: under the consistent entry-bar convention the surviving NS add-ons sum **−₹13,760** against the N1 base in October — NS1 second legs −₹8,305.25, NS2 afternoon legs −₹5,454.75 after unique-once. In the Bank channel the same add-ons are positive; in this channel they are a drag at any geometry.)

## Jan–Oct premium check (the anti-overfit column)

| Candidate | Trades | /week | FT% | Jan–Oct net ₹ | Red month-ends | vs N1 baseline |
|---|---|---|---|---|---|---|
| **C3+G7 confirmed-only + runner-lock50** | 56 | 1.38 | 37.5% | **+66,619.25** | none | **+₹41,460.25 above baseline (2.6×)** |
| C3+G2 confirmed-only, +150 target | 56 | 1.38 | 10.7% | +65,488.25 | none | +₹40,329.25 above baseline — but FT collapses; the money is square-off drift, not targets |
| C3 confirmed-only (baseline geometry) | 56 | 1.38 | 37.5% | +55,939.75 | none | +₹30,780.75 above baseline |
| C1+G7 drop-Skill + runner-lock50 | 52 | 1.28 | 30.8% | +40,072.50 | none | +₹14,913.50 above baseline |
| C1 drop-Skill (baseline geometry) | 52 | 1.28 | 30.8% | +33,354.75 | none | +₹8,195.75 above baseline |
| G2 −50/+150 | 108 | 2.66 | 5.6% | +27,196.75 | none | +₹2,037.75 above baseline, FT destroyed |
| G7 runner-lock50 | 108 | 2.66 | 25.9% | +26,442.75 | none | +₹1,283.75 above baseline, FT held not beaten |
| G0 = U1-N1 baseline | 108 | 2.66 | 25.9% | +25,159.00 | none | — |

C3+G7 month-by-month (net → cumulative): Jan +16,643.75 → 16,643.75; Feb +11,264 → 27,907.75; Mar +8,210 → 36,117.75; Apr +4,240.75 → 40,358.50; May −5,793 → 34,565.50; Jun +9,131 → 43,696.50; Jul +10,809 → 54,505.50; Aug −4,129.25 → 50,376.25; Sep −2,562.25 → 47,814.00; Oct +18,805.25 → **66,619.25**. Every month-end green; three negative individual months (May, Aug, Sep).

## Rejected list (failed leg named)

- **C3+G2** — highest October net in the channel (+₹20,414) but FT 25.0% in October and **10.7% Jan–Oct**: with a +150 target almost nothing "hits target"; profits are 15:10 square-off drift. Rejected on FT in both windows, and on frequency (1.11/wk).
- **Every volume candidate (V1/V2/V3/V5, S1/S2/S3)** — Nifty NS add-ons are net-negative under the consistent entry convention; pooling drags the base down, V3 turns the month negative. Rejected on net. (Filter (a-NS) V4 = baseline exactly: it deletes the whole add-on set, which is the correct instinct, but adds nothing.)
- **G2/G1/G5 (bigger fixed targets)** — October net rises slightly (G2) only through square-offs; FT falls to 12.5–25%. Rejected on FT.
- **G3/G4/G6/G8** — wider stops and BE runner all score below baseline on net. Rejected on net.
- **E1/E2 gates** — E1 keeps 3 legs (+₹9,925.25, 0.83/wk); E2 keeps 2. Rejected on frequency and net. **E4 delay** — destroys the channel (−₹4,272.25): Nifty entries are timing-sensitive in the wrong direction. Rejected on net.
- **F5 ITM strikes** — ₹8,640, below baseline. Rejected on net.
- **C2 unions containing Skill V3** — all ≤ +₹850 or negative in October. Any union that keeps solo Skill legs keeps the channel's weakest part. Rejected on net.

## Verdict — Nifty channel

**U1-N1 stays the kept best. No candidate formally replaces it.**

- The replacement rule needs October net AND full-target beaten, frequency ≥2/week, and a Jan–Oct check that does not go backwards. **Nobody passes all of it** — every October improver fails FT or frequency.
- **The standout is C3+G7 (confirmed-only legs + runner-lock50): October +₹18,805.25, Jan–Oct +₹66,619.25 (~₹6,660/month, 2.6× N1), FT 37.5% Jan–Oct (vs N1's 25.9%), no red month-end in either window.** It is **not October-fitted** — its Jan–Oct is proportionally stronger than its October. What it fails is frequency, decisively: 1.11/week in October, 1.38/week Jan–Oct, against the ≥2/week leg. Confirmed-only means waiting for ≥2 systems to agree, and that simply does not happen 2+ times a week in this channel. It is a quality-for-frequency trade, and under the frozen rule it cannot be named the new best. **It is the channel's best November-paper watch candidate alongside N1** if the user accepts ~1 trade/week in this channel.
- **G7 on the full N1 set** is a small genuine improvement (net up on both windows, +₹650 / +₹1,283.75) with FT held, not beaten — same borderline class as the Bank channel's G7.
- **October ceiling:** at ≥2/week, +₹12,390.50 (G2, with FT destroyed at 12.5% — unusable); the best balanced October is C3+G7's +₹18,805.25 at 1.11/week. The user's ₹20,000+/month bar is reached in this channel only by C3+G2 (+₹20,414), whose 10.7% Jan–Oct FT makes it untradeable as a "quality" system. On a Jan–Oct average, even the best track (C3+G7) makes ~₹6,660/month — better than N1's ~₹2,500, still far from ₹20,000/month.
