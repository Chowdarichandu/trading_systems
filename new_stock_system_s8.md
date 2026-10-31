# S8 — Intraday STOCK system (cash, NOT options) — FROZEN, tested in-sample only, NOT adopted

**Paper only, no orders, cash intraday only, no options. Nothing in this
report is adopted, and no November adoption-track log was created for S8.**
Frozen spec (written before scoring): `new_stock_system_s8_frozen.md`.
Engine: `stock_system_s8.py`. Trades: `s8_trades_jan_oct_2026.csv`
(54 trades), uncapped `s8_uncapped_jan_oct_2026.csv` (81),
month JSON `data/progressive/s8_summary_2026-jan-oct.json`,
diagnosis `setup2_diagnosis_jan_oct_2026.json`.
Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks,
203 trading days, 5,075 stock-days. All Jan–Oct figures are
**in-sample context only**. All rupee totals are **per 100 shares,
provisional — NOT a lot profit** (100 shares was a provisional
cash-translation unit, never the user's lot rule; index options
use 1 options lot, stocks have no lot). Index totals were never
pooled into stock totals; Nifty was a bias filter only.

## S8 design (ONE change vs S7, frozen before scoring)

- **CE pullback arming widened:** S7 armed only on gap-down days
  (day open < PDC). S8 arms on ANY reclaim close above OR high,
  regardless of day open vs PDC. Same pullback + second-close
  entry after arming: first pullback candle dipping toward OR
  high (|low − OR high| ≤ 40×scale) and closing back above it,
  second close above the pullback close, entry = next open,
  stop = pullback low, room ≥ 1.5× risk to the next PD level
  above, target +2× risk.
- **Everything else unchanged from S7:** PE path (find_signal PE,
  second close, retest-hold stop, room ≥ 1.5× below, target
  −2× risk), OR width 0.25–3.0%, stock bias filter, Nifty
  bias-only confirmation, prospective full-target net ≥ ₹500,
  give-back exit (50 at 1× risk, rest trailed to breakeven),
  100 shares, ₹40/trade, 15:10 square-off, short paper-only,
  cap max 1 valuable stock trade/day, 1/stock/week, ranking
  target net → room → setup rank. No forcing, no direct reclaim
  CE, no setup2 CE breakout, no timing gates, no room < 1.5×.

## Results — Jan–Oct 2026, capped

| Series | Trades | Win net>0 | Full-target | Net ₹ | Expectancy | /day | /week |
|---|---|---|---|---|---|---|---|
| **S8** | **54** | **50.0% (27)** | **22.2% (12)** | **+₹932.50** | **+₹17.27** | **0.27** | **1.23** |
| S7 | 51 | 51.0% (26) | 21.6% (11) | +₹722.50 | +₹14.17 | 0.25 | 1.16 |
| S2 (best kept before S7) | 61 | 59.0% | 19.7% (12) | −₹785.98 | −₹12.88 | 0.30 | 1.39 |
| S1 | 18 | 50.0% | 22.2% (4) | −₹1,875.94 | −₹104.22 | 0.09 | 0.42 |
| V4 stocks | 132 | — | 22.7% | −₹17,435 | −₹132 | — | ~3.0 |
| Skill stocks | 143 | — | 22.4% | −₹21,835 | −₹153 | — | ~3.3 |

S8 improves on S7 on net (+₹210), expectancy, and full-target
rate, but by a small margin on a small sample. Exits (capped):
26 stops, 15 stops-after-partial-BE, 12 targets-after-partial,
1 square-off. The 50.0% net>0 rate includes 15 partial-BE wins,
shown separately and never counted as targets.

### Legs

- **CE pullback leg: 9 trades, +₹1,960.00, 55.6% net>0,
  33.3% full targets (3), expectancy +₹217.78.** Widening arming
  added 4 capped CE trades vs S7 (5 trades, +₹1,590) and kept CE
  profitable: new CE trades TVSMOTOR 2026-08-25 partial-BE
  +₹375, TVSMOTOR 2026-09-30 target +₹965, ASTRAL 2026-05-14
  stop −₹540, GLENMARK 2026-08-07 stop −₹430; the 5 S7 CE trades
  are all retained. Uncapped CE: 11 (vs S7's 6). Reclaim-chasing
  did NOT return as a CE blow-up: CE stops are 4 of 9, CE
  expectancy is strongly positive. CE is now the carrying leg.
- **PE leg: 45 trades, −₹1,027.50, 48.9% net>0, 20.0% full
  targets (9), expectancy −₹22.83.** Slightly worse than S7's
  PE leg (46 trades, −₹867.50) — one PE candidate was displaced
  by a CE candidate under the one-candidate-per-stock-day rule
  (earliest entry), and cap ranking shifted. PE remains the drag:
  S8 total (+₹932.50) = CE (+₹1,960.00) + PE (−₹1,027.50).
- **Setup/direction split (capped):** setup3 bounce PE 45,
  setup4 pullback CE 9, **setup2 0**. Uncapped split: setup3 PE
  70, setup4 pullback CE 11, setup2 0 — setup2 is absent at the
  uncapped stage too.

### Days and funnel (properly instrumented this time)

- Trading days: 203. Days traded: 54. Days with at least one
  uncapped candidate: 56. Days with a candidate but capped
  out: 2. **Days with no valuable setup: 147.**
- Funnel: scanned 5,075 → OR pass 4,859 → CE armed 215 →
  CE pullback 138 → CE second-close 56 → uncapped candidates
  81 → capped 54. The CE funnel shows the widening worked at
  the arming stage (215 armed days) but most armed days still
  die before a candidate: 138 pullbacks, 56 second closes, and
  only 11 survive room / prospective / Nifty / one-per-day to
  uncapped. Frequency is still candidate scarcity, not the cap
  (only 2 days lost to it). No trades were forced.

### Month-by-month cumulative (capped)

| Month | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|
| Jan | 5 | +₹2,960.00 | +₹2,960.00 |
| Feb | 8 | −₹1,870.00 | +₹1,090.00 |
| Mar | 6 | −₹1,070.00 | +₹20.00 |
| Apr | 6 | −₹735.00 | −₹715.00 |
| May | 5 | +₹610.00 | −₹105.00 |
| Jun | 5 | −₹940.00 | −₹1,045.00 |
| Jul | 4 | +₹885.00 | −₹160.00 |
| Aug | 10 | +₹1,035.00 | +₹875.00 |
| Sep | 3 | +₹360.00 | +₹1,235.00 |
| Oct (1–28) | 2 | −₹302.50 | +₹932.50 |

Ex-March total +₹2,002.50; ex-October total +₹1,235.00.
Cumulative does NOT rise month by month: it falls Jan→Jun,
recovers Aug→Sep, and ends barely above zero.

### Per-stock (capped, non-zero only)

GLENMARK 7 trades +₹1,545 (3 targets); TVSMOTOR 9 +₹590;
OBEROIRLTY 3 +₹650; HINDALCO 3 +₹530; ASTRAL 8 +₹470;
BDL 9 +₹245; GODREJCP 3 −₹72.50; HINDUNILVR 2 −₹185;
HINDZINC 2 −₹245; HDFCBANK 1 −₹315; HINDCOPPER 2 −₹685;
UNITDSPR 5 −₹1,595 (worst, 0 targets). Zero-trade stocks (13):
INDUSTOWER, IRCTC, ITC, KALYANKJIL, NATIONALUM, NHPC,
NTPC, OIL, PFC, RECLTD, TATASTEEL, VEDL, WIPRO.
S1-zero-stock trades: 5, from HDFCBANK, HINDCOPPER,
HINDUNILVR only — the same narrow set as S2–S8.

## Setup2 diagnosis — why setup2 is 0 (solved, not a cap artefact)

Diagnosis over the same window (`setup2_diagnosis_jan_oct_2026.json`,
plus a PE-path stage check):

- OR-pass stock-days: 4,859. Raw OR-cross days: CE 1,220, PE
  1,181, any 2,302 — crosses are common.
- **Passing ALL setup2 gates: only 105 days** (CE 13, PE 93,
  1 day both). The dominant blocker is the OR-width cap
  (≤360×scale ≈ 0.65% of prev close, while the OR filter allows
  up to 3.0%): 1,033 cross days blocked by width alone, 1,126
  by multiple gates together; room alone 12, resistance alone
  16, bias alone 10.
- **Precedence masking is NOT the cause:** only 1 pass day was
  masked by an earlier setup (TATASTEEL 2026-05-26, setup4
  reclaim 10:05 before a setup2 CE pass 10:50). 95 of 105 pass
  days ARE returned by find_signal as setup2; the other 9 are
  same-candle setup4 precedence (setup4 is checked before
  setup2 in the same candle loop — e.g. GLENMARK 2026-02-24,
  OBEROIRLTY 2026-02-24, HDFCBANK 2026-10-26).
- **Why 0 survive into S8 uncapped, then?** A PE-path stage
  check on the 95 find_signal setup2 days (92 PE, 3 CE):
  - PE: **47 fail second close**, **45 fail "no room below"**,
    **0 survive all filters**. The no-room failure is
    structural: setup2 PE requires a close below PDL, the
    lowest PD level, so there is no PD level below the entry
    for the room test to measure against — room is undefined,
    and the candidate is rejected by construction.
  - CE: only 3 days, and S8's CE path is pullback-only, so a
    setup2 CE breakout never enters S8 at all.
- Conclusion: setup2 cannot be rescued by loosening room
  (room < 1.5× was already ruled out, and for PE there is no
  room to measure), nor by cap changes. Rescuing setup2 PE
  would need a NEW room definition (e.g. a structural level
  below PDL, or a fixed multiple of OR width) frozen as a
  separate design change and tested as its own version — it
  is NOT done inside S8, and it is not claimed here.

## Judgement against the user bar (all together)

User bar: 1 valuable STOCK trade per day, index separate;
valuable = convicted, high-return, no tiny wins, no
partial-BE wins counted as wins, no forced trade.

| Leg | Verdict |
|---|---|
| (a) Net positive in-sample | **PASS, barely** — +₹932.50, expectancy +₹17.27 |
| (b) Close to 1 valuable trade/day, no forcing | **FAIL** — 0.27/day, 54 traded days vs 147 no-setup days |
| (c) CE pullback present AND profitable; setup2 honest | **CE PASS, setup2 FAIL (absent, now explained)** — CE 9 trades, +₹1,960, 33.3% full targets; setup2 0, structurally blocked (see diagnosis) |
| (d) Full-target rate above S2's 19.7% | **PASS** — 22.2% (12/54), equal to S1's 22.2%; 15 of 27 net-positive trades are partial-BE wins |
| (e) Cumulative rising month by month | **FAIL** — Jan +₹2,960 → Jun −₹1,045 → Oct +₹932.50, oscillates |

**Overall: S8 does NOT pass all legs together, so S8 is NOT
adopted and does NOT go on an adoption-track November log.**
No `s8_forward_paper_log.csv` was created, deliberately.
Best kept on net alone is now S8 (+₹932.50 vs S7 +₹722.50),
but best-kept on net alone is not adoption: S8 fails
frequency and cumulative progression, and its net is
+₹17/trade on a 54-trade in-sample sample.

## Tuning does NOT stop here (standing requirement 2026-10-30)

S8's failure does not close tuning. Until the system is ready
for paper trading for the next one month, tuning continues
family by family, for intraday stocks and intraday options
both. The next family is **S9 — S8 price design + event gate**
(see `new_stock_system_s9_frozen_draft.md`): the S8 design
unchanged, plus a news/results/CEO-change/corporate-action
event gate built from the separate event-layer calendar (not
yet delivered at S8 report time), frozen before any S9
scoring, with November 2026 paper as validation — NOT a
re-tune of S8 on the same window to force a pass. If the
event gate does not fix frequency/cumulative, the family
after S9 is a new setup2-PE room definition (structural level
below PDL), as a separate frozen version.
