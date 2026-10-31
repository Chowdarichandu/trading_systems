# LINE R1 — THE HONEST MOVER NEIGHBOURHOOD — Report

Workplan frozen in `stocks_R1_frozen.md` BEFORE scoring
(controls-first protocol: leak audit + placebo run in the
same run as first scoring; nothing is quoted that fails
them). Equity cash intraday, LONG/SHORT only, paper only,
real money ₹0. All figures provisional per 100 shares,
net = gross − ₹40/trade. Window Jan–Oct 2026 (Oct = 1–28).
Pooled 50 primary; home (original 25) / ext (new 25) splits
reported. Engine: `stocks_R1.py`; results:
`stocks_R1_results.json`; run log: `stocks_R1_run.log`;
dumps: `moverR1_A_1000/1015`, `moverR1_B_1000/1015`,
`moverR1_C1_1000/1015`, `moverR1_C2_1000/1015`,
`moverR1_PLACEBO_C1_1015` trade CSVs.

**Question.** The retracted Morning-Mover qualified a
stock-day on a ≥1% move by 10:00/10:15 but entered on
signals from earlier in the day — untradable. B5's honest
rebuild (discard the first post-measurement signal, trade
the second) lost money at both measurement times. This line
asks whether any *other* real-time-executable relative —
first signal instead of second, direction-filtered, or no
signals at all — reaches toward the target bar of ~₹25k/month
pooled per 100 shares (≈ +₹250,000 over Jan–Oct).

## Anchor validation — PASS

The B5 honest second-signal machinery reproduced both
anchors to the paisa in-process before any R1 cell was
scored: honest 10:00 → 614 chains / 946 trades /
**−₹117,200.13**; honest 10:15 → 894 chains / 1,299 trades /
**−₹167,156.86**. R1's builders differ from that machinery
by exactly the frozen cell rules (no discard, or no signal
stream).

## Leak audit — CLEAN, zero violations everywhere

Programmatic assertion per cell × measurement × universe:
every trade's `entry_time ≥ measurement time`. Totals
checked: A@10:00 1,007; A@10:15 1,362; B@10:00 926; B@10:15
1,281; C1@10:00 707; C1@10:15 1,014; C2@10:00 707; C2@10:15
1,014; placebo 1,015. **Violations: 0 in all nine books.**
Earliest entries: 10:05 under the 10:00 measurement,
10:20 under 10:15 — exactly the machinery's first possible
entries. Every number below is real-time-executable by
construction, and this time the audit ran in the same run
as the first scoring, not afterwards.

## Cell results — pooled 50

| Cell | Chains | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Exp/trade ₹ | Home ₹ | Ext ₹ | Losing months | Max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **R1-A** first-signal @10:00 | 637 | 1,007 | **−128,595.61** | −79,864.49 | −48,731.12 | −19,252.51 | 19/50 | −201.88 | −127.70 | −56,864.68 | −71,730.93 | 8 | −129,049.85 |
| **R1-A** first-signal @10:15 | 917 | 1,362 | **−180,817.36** | −111,651.96 | −69,165.40 | −14,373.87 | 17/50 | −197.18 | −132.76 | −55,689.92 | −125,127.44 | 7 | −187,022.70 |
| **R1-B** first-signal same-dir @10:00 | 576 | 926 | **−120,162.13** | −75,029.41 | −45,132.72 | −21,652.21 | 20/50 | −208.61 | −129.76 | −52,383.52 | −67,778.61 | 8 | −120,616.37 |
| **R1-B** first-signal same-dir @10:15 | 858 | 1,281 | **−181,485.29** | −113,808.01 | −67,677.28 | −16,560.88 | 19/50 | −211.52 | −141.67 | −48,631.78 | −132,853.51 | 7 | −187,420.63 |
| **R1-C1** fixed-time 0.5%/0.5% @10:00 | 707 | 707 | **−45,058.00** | −25,836.60 | −19,221.40 | +2,444.09 | 10/50 | −63.73 | −63.73 | −60,981.59 | +15,923.59 | 7 | −65,756.71 |
| **R1-C1** fixed-time 0.5%/0.5% @10:15 | 1,014 | 1,014 | **−43,264.78** | −16,204.97 | −27,059.81 | −24,091.36 | 16/50 | −42.67 | −42.67 | −28,140.57 | −15,124.21 | 4 | −61,188.92 |
| **R1-C2** fixed-time 1.0%/0.5% @10:00 | 707 | 707 | **−65,698.72** | −12,359.32 | −53,339.40 | −8,551.09 | 14/50 | −92.93 | −92.93 | −60,500.53 | −5,198.19 | 8 | −83,737.98 |
| **R1-C2** fixed-time 1.0%/0.5% @10:15 | 1,014 | 1,014 | **−162,328.96** | −81,455.76 | −80,873.20 | −28,216.58 | 12/50 | −160.09 | −160.09 | −29,785.91 | −132,543.05 | 9 | −166,679.07 |
| **R1-D** second-signal (B5) @10:00 | 614 | 946 | **−117,200.13** | −74,380.44 | −42,819.69 | −18,487.89 | 15/50 | −190.88 | — | −47,557.10 | −69,643.03 | 9 | −118,351.91 |
| **R1-D** second-signal (B5) @10:15 | 894 | 1,299 | **−167,156.86** | −100,793.47 | −66,363.39 | −29,590.72 | 17/50 | −186.98 | — | −55,615.44 | −111,541.42 | 8 | −174,300.24 |

Notes on the shape:

- **The first signal is not better than the second.**
  R1-A @10:00 (−₹128,595.61) is worse than the D anchor
  (−₹117,200.13); @10:15 it is worse again (−₹180,817.36
  vs −₹167,156.86). The signal stream's first post-measurement
  signal loses just as the second one does — nothing was
  hiding behind the discard.
- **Direction filtering does not rescue it.** R1-B's
  same-direction restriction moves @10:00 by only +₹8,433
  and @10:15 by −₹668 against R1-A. The B-line stack that
  doubled the leaky book adds nothing honest.
- **No signals is the least-bad family, and it is still
  negative.** R1-C1 (0.5% target / 0.5% stop, fixed entry at
  measurement+5 in the pre-move's direction) is the best
  cell in the neighbourhood at both measurements
  (−₹45,058.00 / −₹43,264.78). Its expectancy per trade is
  −₹63.73 @10:00 and −₹42.67 @10:15 — i.e. gross expectancy
  about −₹24 and −₹3 per trade after adding back the ₹40
  cost. At the 10:15 measurement the post-measurement drift
  on ≥1% mover days is, in honest terms, **approximately
  zero before costs** — which is why the cost alone makes
  it negative. The wider-target C2 variant is decisively
  worse at 10:15 (−₹162,328.96): chasing the extra target
  on already-moved stocks loses.
- **Splits never agree.** Every signal cell loses on both
  universes. C1@10:00 is the one split-positive reading in
  the line (ext +₹15,923.59 against home −₹60,981.59) — a
  universe disagreement, not an edge; pooled it stays
  −₹45,058.00.
- **No cell passes even one gate leg except audit.**
  Best breadth is 20/50 (gate needs 35); every cell's both
  halves are negative; only C1@10:00 has a positive October
  (+₹2,444.09) and it fails everything else.

## Placebo — best cell C1@10:15

Best cell by the frozen rule: **R1-C1 @10:15**
(−₹43,264.78). Re-run with qualification and direction
taken from **yesterday's** pre-move (same measurement
window, |pm| ≥ 1%): 1,015 trades, **−₹65,544.41** (Jan–May
−₹40,279.03 / Jun–Oct −₹25,265.38, October +₹13,392.01,
breadth 18/50, max DD −₹88,596.46, leak audit clean).

Read: the real cell "beats" its placebo by ₹22,279.63 —
but both are deeply negative, and the placebo's October is
actually positive while the real cell's is −₹24,091.36.
There is no real effect to certify here: today's qualifier
is merely less-bad than yesterday's, and the gap (₹22 per
trade) is an order of magnitude below the target bar and
inside the noise of a cost-dominated book. The placebo
gate leg is recorded as passed only in the mechanical sense
(placebo net < cell net); it does not make C1@10:15 a
candidate, because the cell fails every other leg.

## Verdict — NO CANDIDATE

**Gate outcome: 0 of 8 cells pass. No
`stocks_R1_candidate_spec.md` is frozen.**

The honest neighbourhood's ceiling is the best cell,
R1-C1 @10:15: **−₹43,264.78 over 10 months =
−₹4,326/month**, against the target bar of +₹25,000/month
— a gap of roughly ₹29k/month, on the wrong side of zero.
The fixed-time drift is ≈ ₹0 gross per trade, so the
entire neighbourhood is decided by the ₹40 cost: even the
best honest mover relative cannot pay for itself.

What this closes: morning-momentum relatives of the
retracted flagship — first signal, direction-filtered
first signal, fixed-time directional entry at two target
sizes, two measurement times — are all honestly negative
on pooled 50, with leak audits clean and a placebo run in
the same run. The user's instruction stands as given ("the
previous fake data to be true" is the target to chase), but
this line's honest answer is that **no real-time-executable
version of the mover rule reproduces the retracted
numbers**: the retracted lakhs were the leak itself, not a
distortion of a real edge that a different entry could
recover. Any future mover idea needs a different mechanism
entirely — not another entry variant on ≥1% morning-move
days, whose honest expectancy this line has now measured
three ways (first signal, second signal, fixed time) and
found negative or zero in all of them.
