# Round 2 Family J — CANDIDATE SOURCES — FROZEN 2026-10-30, BEFORE SCORING

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade — NOT premiums, NOT a lot profit.

Funnel justification (diagnosed before freezing): the S12 B8-PE pool has
only 16 October candidates on 8 of 18 trading days; the gate blocks only
2 October candidates (both losers, −₹685 provisional per 100 shares
shadow) and the cap drops 6 (net −₹2,200 provisional per 100 shares
shadow). Candidate GENERATION is the binding wall, so this family tests
one new source:

J — SECOND-SIGNAL RESCAN. For each stock-day, after the first PE signal
candle returned by find_signal (whether or not it passed the B8 filters),
restart find_signal on the same day with its state reset, using only the
pre-09:30 OR candles plus candles AFTER the first signal candle. A second
PE signal is converted to a candidate under the exact B8 rules
(prospective ≥ ₹250, PD-level room ≥ 1.25×, OR width 0.15–4.0%, no
second close — entry at next candle open, stop = signal-candle high,
Nifty bullish-day PE block on). At most ONE rescan candidate per
stock-day. Rescan candidates join the B8-PE pool, are gate-filtered and
re-scored at the S12 (E4, 3R) exit exactly like first candidates.

- J1: rescan pool + S12 cap (1/day, 1/stock/week).
- J2: rescan pool + G1 cap (2/day, 1/stock/week).

Setup2 note (task caveat): the setup2-PE family was closed on the S9
pool in S10 (rescued leg −₹272.50, 0 full targets). In the B8-timing
pool the funnel shows ZERO setup2 candidates in Jan–Oct (all 209 pool
candidates are setup3 bounce-rejection), so there is no B8-pool setup2
pool to test — J does not revive it; this absence is reported, not
worked around.

Winner rule (task): beat S12 on October net + win + frequency together
AND Jan–Sep net not worse AND Jan–Sep maxDD not deeper.

Cross-family combo (pre-registered): at most two individually
non-October-worsening, non-Jan–Sep-worsening single changes from
G/H/I/J may be stacked as X1 and scored; X1 must still pass the full
winner rule to be named S13.
