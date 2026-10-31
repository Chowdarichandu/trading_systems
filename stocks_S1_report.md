# LINE S1 — The Short-Side Continuation Book — Report
Equity cash, SHORT entries, paper only, real Rs 0. Provisional per
100 shares, Rs 40/trade, Jan-Oct 2026, pooled 50 primary.
Cells frozen in stocks_S1_frozen.md BEFORE scoring. Controls-first:
anchor validations + timing audit run in the same run as scoring,
before any score is quoted.

## Protocol log
- Frozen spec written (stocks_S1_frozen.md) before the engine ran.
- Anchors to verify in-run: (1) S1-A must equal R2's published
  FT-20-T125 SHORT block exactly (same construction); (2) S1-E home
  must equal the published P2F SHORT subset: 32 trades / +Rs 13,109.45.
- Timing audit: entry_dt > info_complete asserted over every trade
  in every cell plus the placebo (qualifier = a completed day's
  15:30 close; entry = next session 09:15).

## Results
(to be appended from the audited run — nothing is a result until
the audit prints CLEAN)

## Validations (run first, same run as scoring)
- ANCHOR S1-A vs R2 FT-20-T125 SHORT block: 1,100 trades /
  +Rs 91,090.73 vs 1,100 / +Rs 91,090.73 -> PASS (exact).
- ANCHOR S1-E home vs published P2F SHORT subset: 32 trades /
  +Rs 13,109.45 vs 32 / +Rs 13,109.45 -> PASS (exact). S1-E IS the
  P2F-short core; its pooled verdict below is a true re-judgement.
- TIMING AUDIT: 5,143 trades checked (all cells + placebo),
  violations = 0 -> CLEAN. Every entry is the 09:15 open of the
  session after the qualifier day's 15:30 close (placebo: +2
  sessions).

## Scores — pooled 50 (home / ext splits alongside)
| Cell | Trades | Net Rs | Jan-May | Jun-Oct | Oct | Breadth | Exp/trade | Top-3 | Home (br) | Ext (br) | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1-A down-cont 2.0, T125 | 1,100 | +91,090.73 | +54,580.31 | +36,510.42 | -25,380.02 | 18/50 | +82.81 | 213.4% | +11,661.18 (9/25) | +79,429.55 (9/25) | FAIL |
| S1-B down-cont 2.5, T125 | 715 | +11,638.02 | +16,495.79 | -4,857.77 | -21,692.67 | 18/50 | +16.28 | 946.5% | +2,535.63 (9/25) | +9,102.39 (9/25) | FAIL |
| S1-C = A with T10 | 1,100 | +66,563.37 | +25,577.71 | +40,985.66 | -10,705.65 | 15/50 | +60.51 | 243.5% | -4,071.30 (7/25) | +70,634.67 (8/25) | FAIL |
| S1-D up-fade 2.0, T125 | 1,071 | +62,436.03 | +30,344.89 | +32,091.14 | -35,981.08 | 30/50 | +58.30 | 115.1% | +20,820.13 (16/25) | +41,615.90 (14/25) | FAIL |
| S1-E event-only down-cont | 59 | +6,071.84 | +197.56 | +5,874.28 | +1,046.70 | 22/50 | +102.91 | 201.0% | +13,109.45 (14/25) | -7,037.61 (8/25) | FAIL |

Every cell fails the frozen gate. Failure legs: breadth < 35/50 in
all five (best S1-D 30/50); October negative in A-D; S1-B also
fails both-halves; the best cell S1-A also fails the placebo leg
(below). S1-E's home half is exactly the verified P2F-short profit,
but the ext universe is NEGATIVE (-Rs 7,037.61): pooled, the
P2F-short core shrinks to +Rs 6,071.84 over 10 months — the same
transfer failure P2F already showed, now isolated to its short leg.

## Placebo (frozen control, mirrors best cell S1-A, 2-day lag)
1,098 trades, net +Rs 154,902.69 — HIGHER than S1-A itself
(+Rs 91,090.73). PLACEBO NOT BEATEN. The placebo's own splits (from
its frozen dump): Jan-May +Rs 170,662.38 / Jun-Oct -Rs 15,759.69,
October +Rs 21,068.20, breadth 25/50 — it would fail the gate too.
Read, stated plainly: shorting after a big down day is not a
next-day effect. The qualifier mostly marks stocks inside multi-day
declines / weak regimes (the money concentrates in Mar-Apr in both
books, and reverses hard in other months — placebo July
-Rs 54,772.37; S1-A October -Rs 25,380.02). It is a regime
phenomenon with unstable sign, not a tradable continuation edge.

## Month table — best cell S1-A
Jan +38,315.04 (98) · Feb -880.67 (117) · Mar +55,104.26 (231) ·
Apr -20,580.20 (89) · May -17,378.12 (88) · Jun +21,828.52 (131) ·
Jul +20,506.36 (67) · Aug -9,811.41 (63) · Sep +29,366.97 (113) ·
Oct -25,380.02 (103). Five losing months; Mar alone is 60% of the
net — concentration in time, matching the 213.4% top-3 share in
stocks.

## Verdict
NO CANDIDATE. No stocks_S1_candidate_spec.md is frozen. The
short-side continuation hypothesis, judged on its own frozen gate
with a clean timing audit and both anchors exact, FAILS: too few
stocks carry it, October reverses it, and the 2-day-lag placebo
earning more than the book itself removes the "next-day
continuation" mechanism the book was built on. Against the
programme's ~Rs 25k/month aspiration, the best cell's +Rs 91,090.73
over 10 months (~Rs 9.1k/month, pooled, unstable) does not reach
the bar either — and it is not a candidate at any size because the
gate, not the size, is what it failed.

Files: stocks_S1_frozen.md · stocks_S1.py · stocks_S1_results.json ·
stocks_S1_{S1-A,S1-B,S1-C,S1-D,S1-E,S1-A-PLACEBO}_trades.csv
