# EKAM-INTRADAY — STOCKS · TRAILING-STOP VARIANT — SPEC (FROZEN 2026-11-16, before scoring)

Owner-ordered test (2026-11-16): one trailing-stop variant of the two standing
EKAM-INTRADAY Stocks candidates. Research only — paper, real money ₹0. Changes no
book, ledger, live job, or frozen file.

## Candidates under test (frozen, unchanged entries)

Entries are generated VERBATIM by the frozen machinery — `ekam_intraday_stocks_build.py`
(R1: data, votes, `day_candidates`), `ekam_intraday_stocks_r2_build.py` (R2: exit stack),
`ekam_intraday_stocks_r5_build.py` (R5: day-cap selection + contexts). No entry is
rebuilt any other way.

- **Cand-1 = CAND-T5**: R5 row S0 (EARLIEST-5/day), exit params D=3, S=0.0100, C=None.
- **Cand-2 = S2**: R5 row S2 (EARLIEST-3/day), exit params D=3, S=0.0100, C=None.

Entry rule (frozen): 6 standard indicators clubbed as votes on completed 5-min bars
(VWAP side — equal-weighted typical-price proxy, stores carry no volume · EMA(9,21) ·
Supertrend(7,3) · MACD(12,26,9) · RSI(14) momentum zone · ADX(14) ≥ 20 adds +1 to the
leading side); first signal of the day at ≥5 of 6 votes; entry at next bar's open;
≤1 trade per stock per day; day cap per candidate above.

## Control (mandatory, scored first)

The standing candidates with the frozen exit stack (`exit_x2p`, D=3, S=0.0100, C=None:
hard stop −1.00%, vote-decay exit at a bar's close when own-direction votes ≤ 3,
square-off at the 15:10 bar's close). The control MUST reproduce, to the paisa:

- Cand-1: 2025 +₹62,164.57 · 2026 Jan–Oct +₹63,883.60 · Nov 2–13 +₹24,528.65
- Cand-2: 2025 +₹45,300.64 · 2026 Jan–Oct +₹72,605.30 · Nov 2–13 +₹20,662.60

If the control does not reproduce, the run STOPS and scores nothing.
Additionally, the reason-annotated exit replica used for the variant (trail disabled)
must match `net_of` trade-by-trade on every context of both candidates.

## The one change — trailing stop added on top of the frozen exits

Vote-decay and square-off are unchanged. The −1.00% hard stop remains in force until
the trail arms; once armed, the trail governs (for every grid point the armed trail
sits strictly above the hard stop: min (1+A)(1−TD) = 1.005 × 0.9925 = 0.99746 > 0.99).

- **Peak tracking (completed bars only).** LONG: peak = highest high over bars that
  have completed without producing an exit, starting with the entry bar. SHORT:
  trough = lowest low, mirrored. The peak updates only after a bar completes
  without breaching (and without any other exit on that bar).
- **Activation.** At a bar's completion, if peak ≥ entry × (1 + A) (LONG) /
  trough ≤ entry × (1 − A) (SHORT), the trail is armed from the NEXT bar on.
- **Trail level for a bar** is computed from PRIOR bars' peak only (no intrabar
  look-ahead): LONG trail = peak × (1 − TD); SHORT trail = trough × (1 + TD).
- **Per-bar order** (mirrors the frozen exit order, trail inserted as governing stop):
  1. Open gap: if armed and open ≤ trail (LONG) → exit at the open (`trail_gap`);
     if not armed and open ≤ hard stop → exit at the open (`gap_stop`, frozen).
  2. In range: if armed and low ≤ trail (LONG) → exit at the trail price (`trail`);
     if not armed and low ≤ hard stop → exit at the stop (`stop`, frozen).
     SHORT mirrored on the bar's high.
  3. Decay at close (unchanged): own-direction votes at that bar ≤ 3 → exit at
     that bar's close (`decay`).
  4. No exit → the bar completes; peak/trough updates.
  Square-off: no exit through the 15:10 bar → exit at its close (`squareoff`, frozen).
  On the entry bar no trail can be armed (no prior completed bars).

## Grid

A ∈ {+0.50%, +0.75%, +1.00%} × TD ∈ {0.40%, 0.50%, 0.75%} = 9 points × 2 candidates.
(A = activation gain; TD = trail distance below peak / above trough. The frozen decay
threshold is also named D in the R2 code; here it stays fixed at 3 and is not a grid axis.)

## Windows, basis, outputs

- Windows per candidate per point: 2025 Jan–Oct and 2026 Jan–Oct (with Jan–Jun vs
  Jul–Oct splits), November counterfactual = the 9 trading days 2026-11-02…13
  (the frozen `NOV_DATES` list).
- Basis: equity cash intraday, per 100 shares PROVISIONAL, ₹40/trade (`trade_net`),
  paper only. Data = local stores `data/sarvaritu_fwd/<SYM>/spot_5m.csv` only;
  no network fetch.
- Reported per point: total, trades, expectancy, WR per year; ex-top-3 per year;
  worst single trade (per year and November); November total.
- Verdicts stated plainly: grid points beating the control total in BOTH years;
  points beating the control in November; whether any point beats the control on
  expectancy in both years.
- Outputs: `ekam_intraday_trailing_results.json`, `ekam_intraday_trailing_trades.csv`,
  `ekam_intraday_trailing_2026-11-16.md`.
