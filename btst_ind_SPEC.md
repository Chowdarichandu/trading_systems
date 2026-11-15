# BTST-IND — BTST DECIDED BY INTRADAY INDICATORS · SPEC (frozen 2026-11-15, before scoring)

Programme: BTST-IND v1 — owner's order 2026-11-15: "BTST use indicators, use
different approach." The original BTST programme (2026-11-13) FAILED both arms
and stays CLOSED; this is a different entry decision, not a retest of it: the
day's EKAM intraday indicator-vote state near the close decides the overnight
hold. Research only — arms nothing, changes no book, ledger or job.
BUYING ONLY: index arm = bought options, never sold; stocks arm = cash
long/short per the Stock Book convention (shorts labelled SHORT-CASH).

## OVERNIGHT GAP RISK (read first)

An overnight hold carries unhedgeable gap risk. In the CLOSED BTST programme
the worst single night was **−Rs17,125.50 on 1 Bank lot (2026-03-18 → 19,
Arm 1 V1)**. Any BTST-IND row's worst trade must be read against that number.

## VOTE (frozen, identical to EKAM-INTRADAY)

EKAM-INTRADAY's frozen 6-vote system on 5-min bars, causal, each segment's own
frozen EKAM instance (ekam_intraday_{stocks,bank,nifty}_SPEC.md):
VWAP side · EMA(9,21) · Supertrend(7,3) · MACD(12,26,9) · RSI(14) zone
(long 50≤RSI<70, short mirror) · ADX(14)≥20 adds +1 to the side leading on
votes 1–5. LV/SV ∈ 0–6 per completed bar.
Stocks VWAP = equal-weighted typical-price proxy (stock stores carry no
volume — EKAM-Stocks basis). Index VWAP = futures session VWAP (EKAM-Bank /
EKAM-Nifty basis, each segment keeps its own frozen convention).

## DECISION / FILL TIMES (frozen interpretation, start-stamped bars)

- **Vote bar:** the bar stamped **15:00** on entry day D (votes evaluated on
  that completed bar, EKAM convention).
- **Fill:** the **close of the bar stamped 15:15** on D (house BTST
  convention: the closed programme's entry fill was the close of the 15:15
  premium bar).
- Timing audit: fill stamp (15:15) > vote stamp (15:00) asserted on every
  trade; plus a truncated-series recompute of the 15:00-bar votes on every
  37th scored trade per arm (series truncated at that bar must reproduce the
  full-series votes exactly).

## STOCKS ARM

- Universe: frozen 25 Stock Book names; store data/sarvaritu_fwd/<SYM>/
  spot_5m.csv. Basis: equity cash, **per 100 shares PROVISIONAL**,
  Rs40/position, paper only.
- Scoreable stock-day D: ≥ 30 bars, stamps 15:00 and 15:15 present, EKAM
  votes defined at the 15:00 bar. Next day D+1 = the stock's next stored
  day; exit (i) needs its 09:15 bar, exit (ii) needs ≥ 1 bar. Missing →
  NC for that exit row, counted, never substituted.
- Rows (decision at D's 15:00 bar):
  - **L5** — LV ≥ 5 → LONG. **L4** — LV ≥ 4 → LONG. **S5** — SV ≥ 5 →
    SHORT (cash short, labelled).
- Exits on D+1 (two rows per entry row): **X0920** = close of the 09:15 bar
  (the first bar, completing 09:20); **XCLOSE** = close of D+1's last bar.
- Cap: max **5 entries/day per row**, ordered by the day's first-hit stamp
  (first bar where that side's votes first reach the row threshold), ties
  alphabetical by symbol (EKAM convention).
- Net: LONG (exit − entry)·100 − 40; SHORT (entry − exit)·100 − 40.
- Windows: entry dates Jan 1–Oct 31, **2025 and 2026 separately**; halves
  Jan–Jun / Jul–Oct.

## INDEX ARM (Bank Nifty and Nifty separately)

- Basis: bought options, **1 lot** (Bank 30, Nifty 65), **Rs220/trade**,
  paper only. Spot stores: data/progressive/{BANKNIFTY,NIFTY}/spot_5m.csv
  (Jan–Oct 2026 window — the index premium stores' window; stated wherever
  index numbers appear).
- Book signals (stored legs, november_books_fix_anatomy_legs.csv):
  Bank = BANK_STACK (TUNED STACK v2, 111 legs); Nifty = NIFTY_TUNED_V1
  (74 legs). A day's signal sides = the sides of its legs that day; the
  day's FIRST side = the side of its earliest-entry leg.
- Vote side on D: LV ≥ 5 → long (CE); SV ≥ 5 → short (PE). (Both ≥ 5 is
  arithmetically impossible: LV + SV ≤ 6.)
- Rows (at most 1 trade/day/index/row):
  - **BOTH** — vote side ≥ 5 AND that side is among the day's book-signal
    sides.
  - **VOTES** — vote side ≥ 5 alone.
  - **SIGNAL** — a book signal exists that day; direction = the day's
    FIRST side. CONTROL row: approximates the closed programme's V2
    (stack-direction overnight) — labelled as such everywhere.
- Contract: strike = step nearest (Bank 100, Nifty 50; exact half rounds
  up) the spot close of D's 15:10 bar, on the vote/signal side. Expiry =
  in-force expiry on D (Bank: oi_history/banknifty_daily_oi.csv map;
  Nifty: first expiry ≥ D in the oi_buildup_data calendar); if that expiry
  ≤ D, the next expiry after D (a contract expiring on D cannot be held
  overnight).
- Entry fill = close of the contract's premium bar stamped 15:15 on D
  (premium resolution = the EKAM index builds' house order). Exit fill =
  close of the same contract's premium bar stamped **09:30** on the next
  trading day in the spot series. Missing entry or exit bar → NC, counted.
- Net = (exit − entry) × lot − 220.
- Window: entry dates Jan 1–Oct 31 2026; halves Jan–Jun / Jul–Oct.

## REPORTING (frozen)

- Per row: trades, net, WR (win = net > 0), worst trade, halves
  (net + trades per half). Stocks rows reported per year, never pooled.
- **Placebo:** best row per arm (stocks: highest combined two-year net —
  run per year with that year's real count; index: best row per index by
  net). Random entry days, same counts and sides, same fill/exit rules on
  the drawn day's real bars. Stocks: 200 draws, seed 20261115. Index: 500
  iterations, seed 20261115, NC draws redrawn ≤ 50 times then dropped
  (drops counted). Percentile = % of draw totals below the real total.
- Counts reported: candidates, capped-out, NC by reason, audit result.

Frozen 2026-11-15, before scoring. Build: btst_ind_build.py.
Outputs: btst_ind_2026-11-15.md + btst_ind_results.json (+ trades CSV).
