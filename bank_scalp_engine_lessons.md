# Bank Scalp Engine — Lessons

(Numbered, appended every cycle. Read before proposing any new cycle.)

0. **Inherited (from the 5-min feasibility study, 2026-10-31):** at 5-min bars, S1
   OR-burst gross edge ≈ ₹0 (the entire −₹75,275 was ₹75,020 of cost over 341 trades);
   S2 level-reject and S3 impulse were negative BEFORE cost and beaten by their lag
   placebos. Lesson 34 of the Bank engine: no scalping re-proposal without a genuinely
   new mechanism. This engine's new element is the TIMEFRAME (1-min/3-min decisions,
   ≤5-min holds) plus premium-space triggers — any cycle that cannot say what the
   finer timeframe changes about the 5-min death cause is not a valid cycle.
1. **Cost is the scalp killer, arithmetically.** ₹220/trade on a 1-lot (30) premium
   trade = 7.33 premium points of gross expectancy needed per trade just to break
   even. A mechanism averaging < ~10 points gross/trade cannot survive its own
   frequency. Per-day caps are cost controls, not risk decoration.
2. **Data integrity is non-negotiable.** 1-min scoring only on genuine 1-min candles
   fetched from the API. Splitting 5-min bars into fake 1-min bars is fabrication —
   the exact failure the user caught once before ("you faked me with fake data").
   Missing series = NOT_COMPUTED, counted, never estimated.
3. **Spot VWAP does not exist.** Index 1-min candles carry volume = 0. Any VWAP
   mechanism must live in premium space or be dropped.
4. **(Cycle 1, OR1)** Retiming a dead signal does not revive it: the 1-min OR break
   has the same ~zero gross edge as the 5-min version (−₹892.50 gross over 541
   trades). At 1-min, 63% of trades resolve inside the entry bar, and the tight
   stop loses the intra-bar race (298 stops vs 216 targets at +12/−9) because the
   premium spikes on the break bar and retraces within the entry minute. Any future
   breakout-style trigger must answer this entry-bar reversion, not just fire faster.
5. **(Cycle 2, PV1)** Premium-space triggers are not magic either: premium velocity
   ≥10 pts/2 min grossed +0.08 pts/trade over 768 trades (≈ zero), despite beating
   both placebos by wide margins — at 1-min, lag/random entries are simply terrible,
   so "beats placebo" is a weak bar; the binding bar is gross ≥ 7.33 pts/trade.
   Placebo dominance without gross is a rejection, full stop.
6. **(Charter Cycles 3–4, OR ladder)** The +2.5 rung cannot win a single trade
   after cost (max net −₹145) and is gross-negative too — small rungs die on
   arithmetic, exactly as the mandate's open cost warning said. OR gross grows
   with target size (drift is real but slow); 1-min decisions beat 3-min at
   every rung for breakouts.
7. **(Charter Cycles 5–6+8, level-rejection)** DEAD everywhere: negative gross on
   1-min and 3-min ladders, beaten by random/lag placebos, worst in Red-band
   months (H2). Rejection-at-a-level is anti-predictive at scalp horizons in
   Bank Nifty premiums — do not re-propose without a new mechanism.
8. **(Charter Cycle 7, trailing)** The trailing stop is the first exit that
   manufactures real gross from a weak signal: +2.91 pts/trade on OR1 vs +0.97
   for the best fixed rung (402 trail exits averaging +15.05 pts). But diffuse
   edges don't filter: no OR1-TRAIL sub-population (break size, OR width,
   ordinal, time, premium band) reaches the 7.33-pt breakeven — the edge is a
   property of the whole population, so selection filters are curve-fitting.
   The binding constraint is now purely: gross/trade 2.91 vs cost 7.33.
9. **(Cycles 9–11, trail ridge)** Trail distance has a peaked, decelerating ridge:
   7 → +₹65,091 · 5 → +₹75,009 · 4 → +₹80,796 · 3 → +₹84,185 gross. Tighter banks
   the fast-decaying peaks better, but the whole ridge sits at ~45% of the cost
   load. When the best family's gross ceiling is ~2.2× below its cost at traded
   frequency AND gross/trade is flat across all selectable subsets, the correct
   verdict is arithmetic saturation — stop, don't keep tuning.
10. **(Engine final)** Across 31 controlled variants (192 days, genuine 1-min),
    NO sub-5-minute Bank Nifty premium scalp reaches the 7.33-pt/trade cost
    breakeven. Best: OR-break + tight trailing exit, +3.27 pts/trade gross.
    Any future revival needs a structurally different cost basis or a mechanism
    whose gross/trade is >2× anything measured here — not another parameter.
