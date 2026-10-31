# LINE R2 — Generalised Follow-Through + Overnight Gap (report)

Equity cash, LONG/SHORT, paper only, real ₹0. Provisional per 100
shares, ₹40/trade cost deducted. Window Jan–Oct 2026 (home Oct =
1–28, 18 trading days, as cached; ext Oct = 1–30, 20 trading days, as
cached). Pooled 50 primary. Cells frozen in `stocks_R2_frozen.md`
BEFORE scoring. Engine: `stocks_R2.py`; raw results:
`stocks_R2_results.json`; per-cell trade dumps:
`stocks_R2_<cell>_trades.csv`.

## Timing audit — CLEAN (ran in the same run as scoring)

Asserted programmatically over **all** trades before any score was
printed: entry timestamp strictly after information-complete
timestamp. **Axis 1: 7,202 trades checked, 0 violations. Axis 2:
5,356 trades checked, 0 violations.**

Samples (qualifier → entry):

Axis 1 (info complete = big-move day close, stamped 15:30; entry =
next trading day 09:15):
- GODREJCP 2026-01-28 SHORT: info 2026-01-27 15:30 → entry 2026-01-28 09:15 (big-move day 2026-01-27 −5.21%)
- GODREJCP 2026-03-04 SHORT: info 2026-03-02 15:30 → entry 2026-03-04 09:15 (big-move day −3.13%; 2026-03-03 was not a cached trading day)
- GODREJCP 2026-03-11 LONG: info 2026-03-10 15:30 → entry 2026-03-11 09:15 (big-move day +2.03%)

Axis 2 (info complete = 09:15 gap print on the entry day; entry =
09:20, the second bar's open):
- GODREJCP 2026-01-07 LONG: info 2026-01-07 09:15 → entry 2026-01-07 09:20 (gap +1.67%, follow)
- GODREJCP 2026-02-02 SHORT: info 2026-02-02 09:15 → entry 2026-02-02 09:20 (gap −1.11%, follow)
- GODREJCP 2026-03-10 LONG: info 2026-03-10 09:15 → entry 2026-03-10 09:20 (gap +2.36%, follow)

Both axes are leak-proof by construction and the audit confirms the
implementation matches the construction.

## Axis 1 — Generalised Follow-Through (P2F without the event restriction)

Verdict up front: **dead, decisively.** Removing the event restriction
from P2F destroys it — every cell is deeply negative in both halves.
The follow-through edge, such as it is, lives in event-driven moves,
not in big moves generally.

| Cell | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Exp/trade ₹ | Win % |
|---|---|---|---|---|---|---|---|---|
| FT-20-T125 | 2,171 | −161,431.64 | −95,843.22 | −65,588.42 | −51,637.46 | 10/50 | −74.36 | 26.5 |
| FT-20-T10 | 2,171 | −186,035.65 | −117,674.79 | −68,360.86 | −37,301.61 | 7/50 | −85.69 | 29.6 |
| FT-25-T125 | 1,430 | −178,121.93 | −90,755.18 | −87,366.75 | −21,942.43 | 8/50 | −124.56 | 25.5 |
| FT-25-T10 | 1,430 | −214,116.75 | −121,531.46 | −92,585.29 | −9,884.89 | 7/50 | −149.73 | 28.4 |

Direction splits (pooled): the LONG side is the hole everywhere —
FT-20-T125 LONG −₹252,522.37 vs SHORT +₹91,090.73; FT-20-T10 LONG
−₹252,599.02 vs SHORT +₹66,563.37; FT-25-T125 LONG −₹189,759.95 vs
SHORT +₹11,638.02; FT-25-T10 LONG −₹203,606.87 vs SHORT −₹10,509.88.
Universe splits are negative on both (e.g. FT-20-T125 home
−₹73,484.81 / ext −₹87,946.83). Diagnostic colour only: continuation
after big DOWN days (the SHORT side at the 2.0% threshold) is positive
in-sample — but it sits inside cells that fail every gate leg, and
this line freezes no rescue variants. Recorded as an observation for
a future pre-declared line, nothing more.

## Axis 2 — Overnight Gap (entry 09:20, exits T125/S050)

Verdict: **no edge.** The best cell is scratch in total and fails on
halves, October and breadth; fading is worse overall.

| Cell | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Exp/trade ₹ | Win % |
|---|---|---|---|---|---|---|---|---|
| GAP-10-FOLLOW | 1,777 | +1,411.15 | +17,967.76 | −16,556.61 | −11,865.94 | 16/50 | +0.79 | 29.9 |
| GAP-10-FADE | 1,777 | −83,762.98 | −68,696.37 | −15,066.61 | +33,955.20 | 21/50 | −47.14 | 31.1 |
| GAP-15-FOLLOW | 901 | −10,036.12 | −7,892.78 | −2,143.34 | −6,546.04 | 15/50 | −11.14 | 29.1 |
| GAP-15-FADE | 901 | −28,934.07 | −24,170.94 | −4,763.13 | +10,808.89 | 22/50 | −32.11 | 30.9 |

Notes: GAP-10-FOLLOW is +₹1,411.15 over ten months pooled — ₹141/month
against a ~₹25k/month target bar — and it flips sign between halves
(Jan–May +, Jun–Oct −) with a negative October; its universe split
also disagrees with itself (home −₹69,209.08 / ext +₹70,620.23). The
FADE cells' positive Octobers (+₹33,955.20 / +₹10,808.89) sit inside
both-halves-negative books — one-month luck, not an edge.

## Gate verdicts

Gate per cell: pooled both halves > 0 AND breadth ≥ 35/50 AND
October > 0 AND audit clean. **All 8 cells FAIL. No candidate is
frozen; no `stocks_R2_candidate_spec.md` exists.**

| Cell | Halves > 0 | Breadth ≥35 | Oct > 0 | Audit | Verdict |
|---|---|---|---|---|---|
| FT-20-T125 | ✗ | ✗ (10) | ✗ | ✓ | FAIL |
| FT-20-T10 | ✗ | ✗ (7) | ✗ | ✓ | FAIL |
| FT-25-T125 | ✗ | ✗ (8) | ✗ | ✓ | FAIL |
| FT-25-T10 | ✗ | ✗ (7) | ✗ | ✓ | FAIL |
| GAP-10-FOLLOW | ✗ | ✗ (16) | ✗ | ✓ | FAIL |
| GAP-10-FADE | ✗ | ✗ (21) | ✓ | ✓ | FAIL |
| GAP-15-FOLLOW | ✗ | ✗ (15) | ✗ | ✓ | FAIL |
| GAP-15-FADE | ✗ | ✗ (22) | ✓ | ✓ | FAIL |

Bottom line: neither leak-proof axis gets anywhere near the target
bar. Generalised follow-through is strongly negative (the P2F effect
does not survive removing the event qualifier), and overnight gaps at
1.0–1.5% carry no tradable continuation or fade edge after ₹40 costs
on this universe and window. Both axes are closed as frozen.
