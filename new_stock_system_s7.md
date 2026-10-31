# S7 — Intraday STOCK system (cash, NOT options) — FROZEN, tested in-sample only, NOT adopted

**Paper only, no orders, cash intraday only, no options. Nothing in this
report is adopted, and no November adoption-track log was created for S7.**
Frozen spec (written before scoring): `new_stock_system_s7_frozen.md`.
Engine: `stock_system_s7.py`. Trades: `s7_trades_jan_oct_2026.csv`
(51 trades), uncapped `s7_uncapped_jan_oct_2026.csv` (76),
month JSON `data/progressive/s7_summary_2026-jan-oct.json`.
Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks,
203 trading days, 5,075 stock-days. All Jan–Oct figures are
**in-sample context only**; the real test would be November 2026
paper, which S7 does not qualify for (see judgement below).

## S7 design (one structural change vs S6)

- **CE leg — setup4 pullback ONLY.** No direct reclaim CE and no
  setup2 OR-breakout CE (both are the same reclaim-chasing entry
  S6 showed gets noise-stopped). A reclaim close arms the day
  (first candle 09:30–14:30 with day open < PDC, close > OR high,
  close > PDC, close < PDH, room to next PD above ≥ 200×scale);
  entry triggers only on a later candle dipping toward the
  reclaimed level (|low − OR high| ≤ 40×scale) and closing back
  above it (close > OR high, close > open), with the second-close
  rule on the pullback candle (confirmation close > pullback
  close). Entry = open of the candle after confirmation,
  stop = pullback low, room to next PD above entry finite AND
  ≥ 1.5× risk, target = entry + 2× risk.
- **PE leg — unchanged from S6.** find_signal PE (setup2 breakdown,
  setup3 bounce rejection), second close, retest-hold stop
  (max(signal high, confirmation high)), room to next PD below
  finite AND ≥ 1.5× risk, target = entry − 2× risk.
- Common: OR width / prev close in [0.25%, 3.0%], stock bias
  filter, Nifty bias-only confirmation, prospective full-target
  net ≥ ₹500, give-back exit (50 at 1× risk, rest trailed to
  breakeven), 100 shares, ₹40/trade, square-off 15:10, short
  paper-only. Cap: max 1 valuable stock trade per day,
  1/stock/week retained, ranking target net → room → setup rank.
  One candidate per stock-day (earliest entry, tie → higher
  target net). No forcing: a day with no passing candidate
  trades nothing.

## Results — Jan–Oct 2026, capped

| Series | Trades | Win net>0 | Full-target | Net ₹ | Expectancy | /day | /week |
|---|---|---|---|---|---|---|---|
| **S7** | **51** | **51.0% (26)** | **21.6% (11)** | **+₹722.50** | **+₹14.17** | **0.25** | **1.16** |
| S6 | 53 | 45.3% | 17.0% (9) | −₹3,847.50 | −₹72.59 | 0.26 | 1.20 |
| S2 (best kept before S7) | 61 | 59.0% | 19.7% (12) | −₹785.98 | −₹12.88 | 0.30 | 1.39 |
| S1 | 18 | 50.0% | 22.2% (4) | −₹1,875.94 | −₹104.22 | 0.09 | 0.42 |
| V4 stocks | 132 | — | 22.7% | −₹17,435 | −₹132 | — | ~3.0 |
| Skill stocks | 143 | — | 22.4% | −₹21,835 | −₹153 | — | ~3.3 |

**S7 is the first stock version in this series to be net positive
in-sample — but only just:** +₹722.50 over 10 months, expectancy
+₹14.17/trade after a ₹40 assumed cost. The 51.0% net>0 rate
includes 15 partial-breakeven wins, shown separately and never
counted as targets. Exits (capped): 24 stops, 15 stops-after-
partial-BE, 11 targets-after-partial, 1 square-off.

### Legs

- **CE pullback leg: 5 trades, +₹1,590.00, 60.0% net>0,
  40.0% full targets (2), expectancy +₹318.00.** Trades:
  BDL 2026-05-05 target +₹710, GLENMARK 2026-05-26 target +₹605,
  TVSMOTOR 2026-08-31 partial-BE +₹1,055, OBEROIRLTY 2026-04-22
  stop −₹410, HINDUNILVR 2026-08-06 stop −₹370. Uncapped CE:
  6 trades (the 5 above plus UNITDSPR 2026-07-13 stop −₹420,
  capped out). This is a genuine reversal vs S6's CE leg
  (7 trades, −₹2,980, 0 full targets): the pullback entry
  rescued CE profitability, not just CE presence — on a
  5-trade sample, which is too small to call proven.
- **PE leg: 46 trades, −₹867.50, 50.0% net>0, 19.6% full
  targets (9), expectancy −₹18.86.** Identical to S6's PE leg
  (46 trades, −₹867.50, 9 targets) — the PE path was unchanged
  and reproduces exactly, a useful cross-check. S7's total
  (+₹722.50) is therefore PE (−₹867.50) + CE pullback
  (+₹1,590.00) exactly.
- **Setup/direction split (capped):** setup3 bounce PE 46,
  setup4 pullback CE 5, setup2 0. Uncapped split is the same
  shape: setup3 PE 70, setup4 pullback CE 6, setup2 0.
  **Setup2 is absent at the uncapped stage too, not a cap
  artefact** — find_signal never returns a setup2 candidate
  that survives to the uncapped list in this window (S6
  uncapped was the same: setup3 PE 70, setup4 reclaim CE 8,
  setup2 0). Setup2 remains an open problem, reported
  honestly, not rescued by loosening room.

### Days

- Trading days: 203. Days traded: 51. Days with at least one
  uncapped candidate: 53. Days with a candidate but capped
  out: 2. **Days with no valuable setup: 150.**
- Uncapped 76 → capped 51 (25 trades capped out, mostly on
  days that already traded). The frequency shortfall is
  candidate scarcity, not the 1/day cap — only 2 days were
  lost to the cap. No trades were forced on no-setup days.

### Funnel (as instrumented)

Scanned 5,075 stock-days → OR pass 4,859 → uncapped
candidates 76 → capped 51. The engine's per-stage CE
counters (arming / pullback / second-close) were not wired
into the funnel output in this version and are left at 0 in
the JSON — do not quote them. The uncapped split above
(70 PE + 6 CE) is the reliable stage evidence.

### Month-by-month cumulative (capped)

| Month | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|
| Jan | 5 | +₹2,960.00 | +₹2,960.00 |
| Feb | 8 | −₹1,870.00 | +₹1,090.00 |
| Mar | 6 | −₹1,070.00 | +₹20.00 |
| Apr | 6 | −₹735.00 | −₹715.00 |
| May | 4 | +₹1,150.00 | +₹435.00 |
| Jun | 5 | −₹940.00 | −₹505.00 |
| Jul | 4 | +₹885.00 | +₹380.00 |
| Aug | 8 | +₹1,090.00 | +₹1,470.00 |
| Sep | 3 | −₹445.00 | +₹1,025.00 |
| Oct (1–28) | 2 | −₹302.50 | +₹722.50 |

Ex-March total +₹1,792.50; ex-October total +₹1,025.00.
S7 is not carried by March (March was −₹1,070) or by
October (October was −₹302.50) — but cumulative does NOT
rise month by month: it falls Jan→Apr, recovers, falls
again, and ends barely above zero.

### Per-stock (capped, non-zero only)

GLENMARK 6 trades +₹1,975 (5 wins, 3 targets); ASTRAL 7
+₹1,010; OBEROIRLTY 4 +₹810; HINDALCO 3 +₹530; BDL 9 +₹245;
GODREJCP 3 −₹72.50; HINDUNILVR 2 −₹185; HINDZINC 2 −₹245;
HDFCBANK 1 −₹315; HINDCOPPER 2 −₹685; TVSMOTOR 7 −₹750;
UNITDSPR 5 −₹1,595 (worst). Zero-trade stocks (13):
INDUSTOWER, IRCTC, ITC, KALYANKJIL, NATIONALUM, NHPC,
NTPC, OIL, PFC, RECLTD, TATASTEEL, VEDL, WIPRO.
S1-zero-stock trades: 5, from HDFCBANK, HINDCOPPER,
HINDUNILVR only — the same narrow set as S2–S6.

## Judgement against the user bar (all together)

User bar: 1 valuable STOCK trade per day, index separate;
valuable = convicted, high-return, no tiny wins, no
partial-BE wins counted as wins, no forced trade.

| Leg | Verdict |
|---|---|
| (a) Net positive in-sample | **PASS, barely** — +₹722.50, expectancy +₹14.17 |
| (b) Close to 1 valuable trade/day, no forcing | **FAIL** — 0.25/day, 51 traded days vs 150 no-setup days. No forcing was honoured, which is why frequency is low. |
| (c) CE pullback present AND profitable; setup2 honest | **CE PASS, setup2 FAIL (absent)** — CE pullback 5 trades, +₹1,590, 40% full targets; setup2 0 at uncapped stage too. |
| (d) Full-target rate above S2's 19.7% | **PASS vs S2** — 21.6% (11/51). Still below S1's 22.2%, and 15 of 26 net-positive trades are partial-BE wins. |
| (e) Cumulative rising month by month | **FAIL** — Jan +₹2,960 → Apr −₹715 → Aug +₹1,470 → Oct +₹722.50. Oscillates, never sustains a rise. |

**Overall: S7 does NOT pass all legs together, so S7 is NOT
adopted and does NOT go on an adoption-track November log.**
No `s7_forward_paper_log.csv` was created, deliberately.
Best kept is now S7 on net alone (+₹722.50 vs S2 −₹785.98),
but best-kept on net alone is not adoption: S7 fails
frequency, cumulative progression, and setup2, and its net
is +₹14/trade on a 51-trade sample whose CE leg is only
5 trades. S7 was NOT re-tuned on this window and re-claimed.

## Next design change (S8 sketch only, not implemented or scored)

Frequency, not edge per trade, is now the binding constraint:
150 of 203 days have no valuable setup under S7's filters,
and only 2 days are lost to the cap. Loosening room again
has failed in every direction tried (S2–S6), so S8 must
add valuable setups, not loosen filters:

1. **Widen CE pullback arming beyond gap-down days.** S7 arms
   only when day open < PDC. Test, as a frozen S8 rule,
   arming on any reclaim close above OR high (regardless of
   day open vs PDC) followed by the same OR-high pullback
   + second-close entry. This is the most direct way to
   raise CE candidate count without touching room, stop,
   or target — but it must be frozen before scoring, and
   if it admits reclaim-chasing again it will show up as
   CE stops, not as a frequency win.
2. **Investigate setup2 absence separately, not by loosening.**
   find_signal's setup2 requires OR width ≤ 360×scale,
   t ≤ 11:30, and a close beyond OR with room ≥ 200×scale,
   and it returns the first signal of the day — setup3/4
   may simply never let it surface, or stock ORs may
   rarely satisfy the width cap. Diagnose setup2 on raw
   signals (before any filter) before designing around it.
3. **Do not** re-introduce direct reclaim CE, setup2 CE
   breakout, timing gates, or room < 1.5× as a frequency
   fix — each has already failed or is the exact chasing
   entry S7 was built to avoid.

## Comparison and provenance

- S7 +₹722.50 (51 trades) vs S6 −₹3,847.50 (53) vs S2
  −₹785.98 (61) vs S1 −₹1,875.94 (18) vs V4 stocks
  −₹17,435 (132) vs Skill stocks −₹21,835 (143), same
  Jan–Oct 2026 window, cash intraday only.
- Index totals were never pooled into stock totals; Nifty
  was a bias filter only, never traded in S7. No cash-index
  net in this report is an options profit. No order was
  placed.
