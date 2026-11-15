# SMALL TUNES — VWAP x EMA CROSSOVER · BANK NIFTY · SPEC (frozen before scoring, 2026-11-14)

Owner's correction 2026-11-14 15:50: start from the rules traders
actually use — buy above VWAP, EMA crossovers — and tune in SMALL
turns, one dial at a time. Research only — no book, ledger or job
changed. Buying only, 1 lot (30), Rs220/trade, paper only.

## Basis (copied from dial_bank_SPEC.md, unchanged)
- Spot: data/progressive/BANKNIFTY/spot_5m.csv, continuous 5-min
  series 2026-01-01 → 2026-11-13. Gate days = stored days ≤
  2026-10-31 (203 full 75-bar days; Oct 29–30 absent from the store,
  outside the basis). November CF days: Nov 2,3,4,5,6,9,11,12,13.
- Session VWAP = session VWAP of the in-force Bank Nifty FUTURES
  contract (round5_history/FUT7_{expiry}.json), cumulative
  typical-price x volume / volume, mapped to each spot bar as the
  last futures bar at or before the spot bar's time (dial build's
  day_vwap). Spot closes are tested against that VWAP. If VWAP is
  undefined at a bar, no VWAP test can pass at that bar.
- Expiry: in-force expiry from oi_history/banknifty_daily_oi.csv;
  November override 2026-11-23. Strike step 100, strike = step
  nearest the decision bar's spot close (exact half rounds up).
  CE for up-signals, PE for down-signals.
- Premium resolution (house order): round5_history C5 files →
  daily2leg/prem_bank.json → per-day candle files in btst_data,
  november_shadow_data, nifty_weekly_expiry_chain, oi_buildup_data.
  Missing everywhere → NC (counted, never substituted).
- EMA: continuous series across days, k = 2/(p+1), seeded with the
  SMA of the first p closes (dial build's ema_series). EMA value at
  bar i uses closes ≤ i only.
- Entry: NEXT bar's open after the decision bar (see hold rule).
  Signal/decision bars must be ≤ 15:10; entry bar ≤ 15:15.
- Money: net = (exit − entry) x 30 − Rs220. Win = net > 0.

## The rules (practitioner base forms)
Notation at bar i: C = spot close, VW = session VWAP at i,
F/S = fast/slow EMA at i, buf = buffer fraction.
Buffered VWAP lines: up-line = VW x (1+buf), down-line = VW x (1−buf).

- VWAP cross up at i (needs i−1 in the SAME session, VW defined at
  i−1 and i): C[i−1] ≤ VW[i−1] x (1+buf) AND C[i] > VW[i] x (1+buf).
  Cross down mirrors: C[i−1] ≥ VW[i−1] x (1−buf) AND
  C[i] < VW[i] x (1−buf). With buf = 0 this is the plain cross.
- EMA cross up at i (continuous series, i ≥ 1, EMAs defined):
  F[i−1] ≤ S[i−1] AND F[i] > S[i]. Cross down mirrors.
- Rule A (VWAP cross): first VWAP cross of the day → CE on up,
  PE on down.
- Rule B (EMA cross): first EMA cross of the day → CE on up,
  PE on down.
- Rule C (combined): first EMA cross of the day whose cross bar
  ALSO closes on the matching buffered VWAP side (up-cross with
  C[i] > VW[i] x (1+buf); down-cross with C[i] < VW[i] x (1−buf)).
- Rule C2 (VWAP reclaim with EMA alignment): first VWAP cross of
  the day at a bar where the EMAs are already aligned (up-cross
  with F[i] > S[i]; down-cross with F[i] < S[i]).

## Hold dial (confirmation)
- hold = 0: decision bar = the cross bar; entry at the next bar.
- hold = 1: the cross counts only if the NEXT bar (the confirm
  bar, must be ≤ 15:10) still sits on the signal side:
  - A: C[confirm] beyond the buffered VWAP line on the signal side.
  - B: F[confirm] still on the crossed side of S[confirm].
  - C and C2: BOTH tests (EMA relation persists AND close still
    on the buffered VWAP side).
  Decision bar = confirm bar; entry at the bar after it.
  A cross whose confirmation FAILS does not consume the day —
  scanning continues for a later cross. A confirmed signal whose
  entry bar is missing or past 15:15 is counted LATE and consumes
  the day. A first cross after 15:10 is counted LATE, no trade.

## Exit sets (walk premium bars from the entry bar, 5-min steps;
every bar from entry through exit must be present, else NC)
- E1: stop −40 / target +70 (per bar: stop checked before target,
  fills at the level).
- E2: stop −50 / target +90 (same mechanics — the house geometry).
- E3: exit when a spot bar closes back across raw session VWAP
  against the trade (CE trade: spot close < VW at that bar; PE
  trade: spot close > VW), filled at that bar's premium close;
  hard stop −60 (level fill, checked before the close test).
- E4: exit when the opposite EMA cross occurs at a spot bar
  (CE trade: EMA cross down; PE trade: EMA cross up), filled at
  that bar's premium close; hard stop −60 (checked first). E4
  uses the rule's own EMA pair; Rule A (no pair) uses (9,21).
- All exits: square-off at the 15:20 bar's premium close if nothing
  fired earlier (for E1/E2 the 15:20 bar is level-checked first).
  The entry bar itself can trigger an exit. Buffer applies to
  entries only; E3 tests raw VWAP.

## Small tunes — one dial at a time, in this order
Base settings: EMA pair (9,21) · hold 0 · buffer 0 · exit E2.
Each step is scored before the next dial moves. At each step the
carried setting = the one with the highest full Jan–Oct net
(tie → the earlier-listed setting). All rows are reported
regardless of the carry.
- Dial 1 — EMA pair: (5,20), (9,21), (13,34), (20,50).
  Scored for B, C, C2 (hold 0, buffer 0, exit E2). Rule A has no
  pair: its base row (hold 0, buffer 0, E2) is scored once here.
- Dial 2 — VWAP hold: 0 vs 1 extra confirming bar (pair carried).
  Scored for A, B, C, C2 (the B form is the EMA-persistence
  analogue defined above).
- Dial 3 — VWAP buffer: 0, 0.05%, 0.10% (pair + hold carried).
  Scored for A, C, C2. Rule B has no VWAP test; its carried row
  stands.
- Dial 4 — Exit: E1, E2, E3, E4 (pair + hold + buffer carried).
  Scored for A, B, C, C2.

## Reporting (frozen)
- Every scored row: Jan–Jun, Jul–Oct, full Jan–Oct and November CF
  (Nov 2–13, descriptive) — trades, net Rs, WR% per window.
- Timing audit on the FINAL rows (the best full-year row per rule
  across all its scored rows): EMA and futures-VWAP values at every
  decision bar recomputed from truncated series; entry bar =
  decision bar + 1 verified.
- Random-entry placebo ONLY on the single best full-year row per
  rule: 500 iterations, seed 20261114; per real trade, a random
  gate day + random entry bar 09:20–15:15, same side, strike from
  the close of the bar before the drawn entry bar, same exit set;
  NC draws redrawn up to 50 times then dropped (drops counted).
  Percentile = % of iteration totals strictly below the real total.
- NC taxonomy: NC_premium (contract/entry/exit bars missing or
  non-contiguous), LATE (defined above), VWAP-undefined bars
  (no VWAP test possible).

Frozen 2026-11-14, before scoring. Build:
vwap_ema_smalltunes_bank_build.py. Outputs:
vwap_ema_smalltunes_bank_2026-11-14.md +
vwap_ema_smalltunes_bank_results.json.
