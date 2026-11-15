# SMALL TUNES — VWAP x EMA CROSSOVER · NIFTY · SPEC (frozen 2026-11-14, before scoring)

Owner's correction (2026-11-14 15:50): start from the rules traders actually use — buy
above VWAP, EMA crossovers — and tune in SMALL turns, one dial at a time. Plain numbers,
no verdict essays. Research only: no running book, ledger or job is changed. Option
BUYING only, 1 lot (65), Rs220/trade, paper only, real money Rs0. Segment: Nifty only.
This run does NOT redo the parameter atlas; it reuses the DIAL-Nifty data and fill
conventions (dial_nifty_SPEC.md) verbatim where they apply.

## DATA + FILL CONVENTIONS (inherited from DIAL-Nifty, unchanged)

- Spot: `data/progressive/NIFTY/spot_5m.csv` (OHLC, no volume), CONTINUOUS 5-min series;
  indicators computed on the continuous series, warmed up on the 2025 bars in the same
  store; signals evaluated only inside the window in force.
- Session VWAP: spot carries no volume, so VWAP comes from the near-month Nifty FUTURES
  5-min candles (`phase3_buildup_data/futures/FUT7_NIFTY_*`): cumulative
  sum(typical price x volume)/sum(volume) within the session, typical = (H+L+C)/3,
  contract in force = nearest monthly expiry >= the day. BASIS-CONSISTENT TEST (the
  DIAL correction): every VWAP comparison uses the FUTURES close at the bar against the
  FUTURES session VWAP at the same bar. A spot bar whose timestamp has no futures VWAP
  value is not VWAP-evaluable that day.
- EMA(p): k = 2/(p+1), seeded at the series start, on spot closes, continuous.
- Entry: signal completes at a bar close; entry bar = the next bar; entry premium =
  OPEN of the entry bar in the stored premium candles
  (`oi_buildup_data/candles_NIFTY_{strike}{CE|PE}_{expiry}_{day}.json`, 7-field).
  Strike = 50-grid strike nearest the SPOT CLOSE of the final signal bar (the cross bar
  when hold=0, the confirming bar when hold=1). Weekly expiry = smallest expiry in the
  stored expiry calendar >= the signal day. CE for up-signals, PE for down-signals.
- A signal is actionable only if its entry bar starts <= 15:15. A signal is SCORED only
  if the exact contract-day file exists AND its bars cover entry..15:20 contiguously;
  otherwise NC, counted per row (nc_no_file / nc_partial), never substituted. Signals
  whose entry bar would start after 15:15 are counted as `late`, separately from NC.
- Money: net = (exit - entry) x 65 - Rs220. Win iff net > 0.

## THE RULES (practitioner base forms)

State definitions at a bar t (all on completed closes):
- VWAP side with buffer b: UP if fut_close(t) > VWAP(t) x (1+b); DOWN if
  fut_close(t) < VWAP(t) x (1-b); NEUTRAL otherwise. b in {0, 0.0005, 0.001}.
- VWAP cross at t: side(t) is UP and side(t-1) is not UP (cross up), or side(t) is DOWN
  and side(t-1) is not DOWN (cross down), where t-1 is the previous bar OF THE SAME
  SESSION. The first VWAP-evaluable bar of a session cannot be a cross.
- EMA cross at t (pair f,s): fast(t) > slow(t) and fast(t-1) <= slow(t-1) (cross up),
  or mirror (cross down); t-1 is the previous bar of the CONTINUOUS series.

- Rule A (VWAP cross): first VWAP cross of the day. Up = buy CE, down = buy PE.
- Rule B (EMA cross): first EMA cross of the day for the pair in force. Up = CE,
  down = PE. (No VWAP test; hold and buffer dials do not apply to B.)
- Rule C (combined): first EMA cross of the day whose cross bar ALSO closes on the
  matching VWAP side (up-cross needs side = UP at the cross bar, with the buffer in
  force; down-cross needs side = DOWN). A cross that fails the VWAP side test is not
  the day's candidate; a LATER cross the same day may qualify (crosses are scanned in
  order until one passes the side test; that one is the day's candidate).
- Rule C2 (VWAP reclaim with EMA alignment): first VWAP cross of the day at whose
  cross bar the EMA pair is ALREADY aligned the same way (up-cross needs fast > slow
  at the cross bar; down-cross needs fast < slow). A cross without alignment is not
  the candidate; a later aligned cross the same day may qualify.

## THE SMALL TUNES (dials, moved one at a time, in this order)

Base configuration: EMA pair (9,21), hold = 0, buffer = 0, exit = E2.
1. EMA pair: (5,20), (9,21), (13,34), (20,50). [Rules B, C, C2]
2. VWAP hold: 0 = enter after the cross bar; 1 = one extra confirming bar — the bar
   after the cross bar must keep the signal's condition: A/C2: VWAP side still the
   same beyond the buffer; C: EMA fast still on the cross side of slow AND VWAP side
   still matching; C2 also needs EMA alignment to persist. If confirmation fails, the
   candidate is dead (no trade from that candidate; for C/C2 a later qualifying cross
   the same day may still become the candidate). Signal bar for strike/entry timing =
   the confirming bar when hold = 1. [Rules A, C, C2]
3. VWAP buffer: 0, 0.05%, 0.10%. [Rules A, C, C2 — every VWAP side/cross test]
4. Exit:
   - E1: stop -40 / target +70 premium points.
   - E2: stop -50 / target +90.
   - E3: exit at the premium CLOSE of the first bar whose futures close crosses back
     across VWAP to the opposite side (CE: fut_close < VWAP; PE: fut_close > VWAP;
     buffer not applied); hard stop -60.
   - E4: exit at the premium CLOSE of the first bar with an opposite EMA cross (pair
     in force; for Rule A the pair is (9,21)); hard stop -60.
   Level exits (E1/E2, and the -60 hard stops in E3/E4): scanned bar by bar from the
   entry bar through 15:15; a bar whose low <= stop exits AT the stop level; else a
   bar whose high >= target exits AT the target level; if both levels fall inside one
   bar the STOP fills first. In E3/E4 the hard-stop level test is applied within each
   bar BEFORE that bar's close-based exit test. If no exit triggers, square-off =
   OPEN of the 15:20 bar. For E3, a bar with no futures VWAP value cannot trigger the
   close-based exit.

## SCORING + REPORTING (frozen)

- The full small grid is computed (A: hold x buffer x exit = 24 rows; B: pair x exit =
  16; C: pair x hold x buffer x exit = 96; C2: 96). The report presents, per rule, the
  ONE-DIAL-AT-A-TIME PATH from the base configuration (at each step the dial's values
  are scored with the other dials held at the path's current settings; the path keeps
  the value with the best full Jan-Oct net) AND the best full-grid row per rule
  (by full Jan-Oct net).
- Every row shows: Jan-Jun net/trades/WR, Jul-Oct net/trades/WR, full Jan-Oct
  net/trades/WR, November CF net/trades/WR (descriptive), and NC counts (Jan-Oct).
  Windows split at 2026-07-01. November window = 2026-11-02..2026-11-13.
- TIMING AUDIT on the final (best) rows: every scored trade asserts entry bar =
  signal bar + 5 min and entry premium = stored open; plus an independent recomputation
  (separate code path) of EMA fast/slow and the futures VWAP at the first scored
  signal bar of each rule's best row.
- RANDOM-ENTRY PLACEBO only on the best full-year row per rule: 1,000 iterations;
  each rebuilds the row's book with the same number of trades and the same CE/PE mix,
  each trade drawn as a uniformly random scorable contract-day file of the same
  direction from the Jan-Oct availability universe with a uniformly random feasible
  entry bar (entry..15:20 contiguous), the SAME exit rule applied (E3/E4 evaluated on
  the drawn day's own VWAP/EMA series); same cost. Percentile = share of placebo
  totals <= the real total. Reported plainly, no pass/fail language attached.
- Tables are the deliverable. No robustness essay, no gate verdicts.
