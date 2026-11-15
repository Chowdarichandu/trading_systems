# BANK NIFTY ENGINE — ROUND 2 — 2026-11-02

**Mandate (Chandu, 2026-11-02):** no saturation conclusions; work different use cases, combinations and permutations until the goal is achievable. Goal: **≥ ₹1,50,000 Jan–Oct 2026 gated pace (₹15,000/month)**. Basis: index-options premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0. November primary/spec/logs untouched (read-only).

**Result: book v14 +₹104,567.00 → book v16 +₹106,517.00** (82 trades, FT90 53.7%, 2.02/week). Two ingredients banked under the full controls gate: Cycle 28 grid cell (+₹600.00) and Cycle 39 expiry-day pocket (+₹1,350.00). Ending pace **₹10,651.70/month**; remaining gap to the floor pace **₹43,483.00 (₹4,348.30/month)**. 14 cycles run (28–41); the enumerated Round-2 space is exhausted: 108/108 exit-grid cells, 24/24 NS1 cross cells, both (lA) cutoffs, both bias variants, expiry-day strike + 3 expiry geometries, 3 bleed-pocket geometries, the standalone setup3 family, and the combination stack — every cell gated, every verdict below.

## Method and sanity (all before any variant was read)
- A generalised exit replay (`bank_r2_core.py`) reproduces book v14 (+₹104,567.00, placebo +₹10,830.70, ex-top-3 +₹75,527.00, halves +₹84,980/+₹19,587, months exact) and book v8 (+₹77,196.50) to the paisa through the new code path.
- NS1 regeneration (`bank_r2_ns1.py`, the frozen generator's logic with parameterised room/window): at frozen parameters it reproduces all 41 pooled book NS1 second legs exactly (date, direction, entry time, strike, expiry; signal times match the frozen map, 0 mismatches); the 24 regenerated legs absent from the pool are each explained by an earlier base leg on the same key. Frozen-construction note: stored second legs carry entry_time = the spot replay's exit-bar time (`replay()` returns the exit bar's time on stop/target) with strike = ATM(spot entry) — that convention is the frozen book and is preserved identically in every variant.
- Entry-side re-pool (`bank_r2_entry.py`) from stored component candidates reproduces the 89-leg B2 base exactly (date, direction, entry time, strike, expiry, representative system). The B2 Skill filters were measured to operate post-pool (73 Skill-rep CE legs and 21 Skill-solo PE legs ≤09:55 dropped, keys do not survive) and are applied that way.
- Data completion: 22 expired contracts whose candles were missing were fetched from the Upstox expired-instruments API (browser User-Agent header) into `historical_proof_data/` — 16 for the NS1 cells (the room-1.3/1.4 leg 2026-01-07 PE 59900, the window-15:00 leg 2026-09-03 PE 57500, 14 ITM second legs over 13 contracts) and 6 expiry-day ITM contracts. No number below rests on a NOT_COMPUTED exclusion: every taken book has NOT_COMPUTED = 0 (a few ITM cross cells carry named stream-level NOT_COMPUTED legs, counted where they occur).

## Family 1 — exit-geometry grid (Cycles 28–30): 108 cells vs book v14
Stop {40, 50, 60} × trigger {75, 90, 105} × lock {none, 50, 75, 90}; second targets frozen (330 <400 / 180 ≥400). Mode A = <400 segment only; B = ≥400 segments (warm runner + cold plain S/T); AB = all segments. Exactly **one cell passes the full gate**: A / stop 50 / trigger 105 / lock 75 → **+₹105,167.00 (+₹600.00), BANKED as book v15**. Its two changed legs: 2026-01-20 PE runner_stop +₹2,030 → square-off +₹6,380; 2026-07-27 PE runner_stop +₹2,030 → stop −₹1,720. Every other cell fails the gate: all 107 score at or below v14's net (45 fail on the net leg alone; the rest on net plus FT90 or another leg). Full table (net = Jan–Oct ₹, FT90 = % of legs touching +90, placebo = +30-min delayed twin):

| Mode | Stop | Trig | Lock | Net ₹ | FT90 % | Placebo ₹ | Ex-top-3 ₹ | Verdict |
|---|---|---|---|---|---|---|---|---|
| A | 40 | 75 | none | 88,143.50 | 51.2 | 8,928.70 | 59,103.50 | fail |
| A | 40 | 75 | 50 | 81,317.00 | 43.9 | 15,366.70 | 52,277.00 | fail |
| A | 40 | 75 | 75 | 74,646.50 | 37.8 | 15,216.70 | 45,606.50 | fail |
| A | 40 | 75 | 90 | 58,896.50 | 35.4 | 20,166.70 | 43,356.50 | fail |
| A | 40 | 90 | none | 88,143.50 | 51.2 | 8,928.70 | 59,103.50 | fail |
| A | 40 | 90 | 50 | 98,117.00 | 51.2 | 17,475.70 | 69,077.00 | fail |
| A | 40 | 90 | 75 | 99,767.00 | 51.2 | 10,980.70 | 70,727.00 | fail |
| A | 40 | 90 | 90 | 89,417.00 | 51.2 | 14,580.70 | 60,377.00 | fail |
| A | 40 | 105 | none | 88,143.50 | 51.2 | 8,928.70 | 59,103.50 | fail |
| A | 40 | 105 | 50 | 92,717.00 | 51.2 | 17,475.70 | 63,677.00 | fail |
| A | 40 | 105 | 75 | 97,217.00 | 51.2 | 18,630.70 | 68,177.00 | fail |
| A | 40 | 105 | 90 | 81,617.00 | 51.2 | 21,780.70 | 52,577.00 | fail |
| A | 50 | 75 | none | 83,643.50 | 53.7 | 3,528.70 | 54,603.50 | fail |
| A | 50 | 75 | 50 | 84,617.00 | 46.3 | 14,766.70 | 55,577.00 | fail |
| A | 50 | 75 | 75 | 79,446.50 | 40.2 | 15,366.70 | 50,406.50 | fail |
| A | 50 | 75 | 90 | 64,596.50 | 37.8 | 20,766.70 | 49,056.50 | fail |
| A | 50 | 90 | none | 83,643.50 | 53.7 | 3,528.70 | 54,603.50 | fail |
| A | 50 | 90 | 50 | 101,417.00 | 53.7 | 16,575.70 | 72,377.00 | fail |
| A | 50 | 90 | 75 | 104,567.00 | 53.7 | 10,830.70 | 75,527.00 | fail |
| A | 50 | 90 | 90 | 95,117.00 | 53.7 | 14,880.70 | 66,077.00 | fail |
| A | 50 | 105 | none | 83,643.50 | 53.7 | 3,528.70 | 54,603.50 | fail |
| A | 50 | 105 | 50 | 98,417.00 | 53.7 | 16,575.70 | 69,377.00 | fail |
| A | 50 | 105 | 75 | 105,167.00 | 53.7 | 18,480.70 | 76,127.00 | **PASS — BANKED (v15)** |
| A | 50 | 105 | 90 | 90,917.00 | 53.7 | 22,080.70 | 61,877.00 | fail |
| A | 60 | 75 | none | 80,654.00 | 53.7 | 13,134.70 | 51,614.00 | fail |
| A | 60 | 75 | 50 | 83,475.50 | 46.3 | 23,166.70 | 54,435.50 | fail |
| A | 60 | 75 | 75 | 78,305.00 | 40.2 | 16,116.70 | 49,265.00 | fail |
| A | 60 | 75 | 90 | 63,455.00 | 37.8 | 21,966.70 | 47,915.00 | fail |
| A | 60 | 90 | none | 80,654.00 | 53.7 | 13,134.70 | 51,614.00 | fail |
| A | 60 | 90 | 50 | 100,275.50 | 53.7 | 24,675.70 | 71,235.50 | fail |
| A | 60 | 90 | 75 | 103,425.50 | 53.7 | 11,280.70 | 74,385.50 | fail |
| A | 60 | 90 | 90 | 93,975.50 | 53.7 | 15,780.70 | 64,935.50 | fail |
| A | 60 | 105 | none | 80,654.00 | 53.7 | 13,134.70 | 51,614.00 | fail |
| A | 60 | 105 | 50 | 97,527.50 | 53.7 | 24,675.70 | 68,487.50 | fail |
| A | 60 | 105 | 75 | 104,277.50 | 53.7 | 18,930.70 | 75,237.50 | fail |
| A | 60 | 105 | 90 | 90,027.50 | 53.7 | 22,980.70 | 60,987.50 | fail |
| B | 40 | 75 | none | 92,745.50 | 45.1 | 7,110.70 | 63,705.50 | fail |
| B | 40 | 75 | 50 | 91,298.00 | 40.2 | 8,580.70 | 62,258.00 | fail |
| B | 40 | 75 | 75 | 88,448.00 | 35.4 | 7,530.70 | 59,408.00 | fail |
| B | 40 | 75 | 90 | 96,098.00 | 35.4 | 11,580.70 | 67,058.00 | fail |
| B | 40 | 90 | none | 86,214.50 | 47.6 | 4,260.70 | 57,174.50 | fail |
| B | 40 | 90 | 50 | 89,867.00 | 47.6 | 1,860.70 | 60,827.00 | fail |
| B | 40 | 90 | 75 | 87,917.00 | 47.6 | 1,710.70 | 58,877.00 | fail |
| B | 40 | 90 | 90 | 91,067.00 | 47.6 | 930.70 | 62,027.00 | fail |
| B | 40 | 105 | none | 87,114.50 | 47.6 | 6,336.70 | 58,074.50 | fail |
| B | 40 | 105 | 50 | 85,367.00 | 47.6 | 5,136.70 | 56,327.00 | fail |
| B | 40 | 105 | 75 | 81,917.00 | 47.6 | 3,486.70 | 52,877.00 | fail |
| B | 40 | 105 | 90 | 84,167.00 | 47.6 | 1,806.70 | 55,127.00 | fail |
| B | 50 | 75 | none | 95,445.50 | 50.0 | 11,010.70 | 66,405.50 | fail |
| B | 50 | 75 | 50 | 97,898.00 | 43.9 | 13,680.70 | 68,858.00 | fail |
| B | 50 | 75 | 75 | 97,298.00 | 39.0 | 12,630.70 | 68,258.00 | fail |
| B | 50 | 75 | 90 | 103,598.00 | 37.8 | 16,680.70 | 74,558.00 | fail |
| B | 50 | 90 | none | 92,514.50 | 53.7 | 13,560.70 | 63,474.50 | fail |
| B | 50 | 90 | 50 | 99,767.00 | 53.7 | 11,760.70 | 70,727.00 | fail |
| B | 50 | 90 | 75 | 100,067.00 | 53.7 | 11,610.70 | 71,027.00 | fail |
| B | 50 | 90 | 90 | 104,567.00 | 53.7 | 10,830.70 | 75,527.00 | fail |
| B | 50 | 105 | none | 93,864.50 | 53.7 | 10,680.70 | 64,824.50 | fail |
| B | 50 | 105 | 50 | 95,117.00 | 53.7 | 9,780.70 | 66,077.00 | fail |
| B | 50 | 105 | 75 | 93,917.00 | 53.7 | 8,130.70 | 64,877.00 | fail |
| B | 50 | 105 | 90 | 97,517.00 | 53.7 | 6,450.70 | 68,477.00 | fail |
| B | 60 | 75 | none | 84,945.50 | 50.0 | 16,149.70 | 55,905.50 | fail |
| B | 60 | 75 | 50 | 89,798.00 | 43.9 | 16,119.70 | 60,758.00 | fail |
| B | 60 | 75 | 75 | 89,198.00 | 39.0 | 15,819.70 | 60,158.00 | fail |
| B | 60 | 75 | 90 | 95,498.00 | 37.8 | 17,619.70 | 66,458.00 | fail |
| B | 60 | 90 | none | 81,714.50 | 53.7 | 18,399.70 | 52,674.50 | fail |
| B | 60 | 90 | 50 | 91,067.00 | 53.7 | 13,299.70 | 62,027.00 | fail |
| B | 60 | 90 | 75 | 91,367.00 | 53.7 | 13,899.70 | 62,327.00 | fail |
| B | 60 | 90 | 90 | 95,867.00 | 53.7 | 10,869.70 | 66,827.00 | fail |
| B | 60 | 105 | none | 83,064.50 | 53.7 | 15,219.70 | 54,024.50 | fail |
| B | 60 | 105 | 50 | 85,817.00 | 53.7 | 10,719.70 | 56,777.00 | fail |
| B | 60 | 105 | 75 | 84,617.00 | 53.7 | 9,819.70 | 55,577.00 | fail |
| B | 60 | 105 | 90 | 88,217.00 | 53.7 | 5,889.70 | 59,177.00 | fail |
| AB | 40 | 75 | none | 76,322.00 | 42.7 | 5,208.70 | 47,282.00 | fail |
| AB | 40 | 75 | 50 | 68,048.00 | 30.5 | 13,116.70 | 39,008.00 | fail |
| AB | 40 | 75 | 75 | 58,527.50 | 19.5 | 11,916.70 | 29,487.50 | fail |
| AB | 40 | 75 | 90 | 50,427.50 | 17.1 | 20,916.70 | 34,887.50 | fail |
| AB | 40 | 90 | none | 69,791.00 | 45.1 | 2,358.70 | 40,751.00 | fail |
| AB | 40 | 90 | 50 | 83,417.00 | 45.1 | 8,505.70 | 54,377.00 | fail |
| AB | 40 | 90 | 75 | 83,117.00 | 45.1 | 1,860.70 | 54,077.00 | fail |
| AB | 40 | 90 | 90 | 75,917.00 | 45.1 | 4,680.70 | 46,877.00 | fail |
| AB | 40 | 105 | none | 70,691.00 | 45.1 | 4,434.70 | 41,651.00 | fail |
| AB | 40 | 105 | 50 | 73,517.00 | 45.1 | 11,781.70 | 44,477.00 | fail |
| AB | 40 | 105 | 75 | 74,567.00 | 45.1 | 11,286.70 | 45,527.00 | fail |
| AB | 40 | 105 | 90 | 61,217.00 | 45.1 | 12,756.70 | 32,177.00 | fail |
| AB | 50 | 75 | none | 74,522.00 | 50.0 | 3,708.70 | 45,482.00 | fail |
| AB | 50 | 75 | 50 | 77,948.00 | 36.6 | 17,616.70 | 48,908.00 | fail |
| AB | 50 | 75 | 75 | 72,177.50 | 25.6 | 17,166.70 | 43,137.50 | fail |
| AB | 50 | 75 | 90 | 63,627.50 | 22.0 | 26,616.70 | 48,087.50 | fail |
| AB | 50 | 90 | none | 71,591.00 | 53.7 | 6,258.70 | 42,551.00 | fail |
| AB | 50 | 90 | 50 | 96,617.00 | 53.7 | 17,505.70 | 67,577.00 | fail |
| AB | 50 | 90 | 75 | 100,067.00 | 53.7 | 11,610.70 | 71,027.00 | fail |
| AB | 50 | 90 | 90 | 95,117.00 | 53.7 | 14,880.70 | 66,077.00 | fail |
| AB | 50 | 105 | none | 72,941.00 | 53.7 | 3,378.70 | 43,901.00 | fail |
| AB | 50 | 105 | 50 | 88,967.00 | 53.7 | 15,525.70 | 59,927.00 | fail |
| AB | 50 | 105 | 75 | 94,517.00 | 53.7 | 15,780.70 | 65,477.00 | fail |
| AB | 50 | 105 | 90 | 83,867.00 | 53.7 | 17,700.70 | 54,827.00 | fail |
| AB | 60 | 75 | none | 61,032.50 | 50.0 | 18,453.70 | 31,992.50 | fail |
| AB | 60 | 75 | 50 | 68,706.50 | 36.6 | 28,455.70 | 39,666.50 | fail |
| AB | 60 | 75 | 75 | 62,936.00 | 25.6 | 21,105.70 | 33,896.00 | fail |
| AB | 60 | 75 | 90 | 54,386.00 | 22.0 | 28,755.70 | 38,846.00 | fail |
| AB | 60 | 90 | none | 57,801.50 | 53.7 | 20,703.70 | 28,761.50 | fail |
| AB | 60 | 90 | 50 | 86,775.50 | 53.7 | 27,144.70 | 57,735.50 | fail |
| AB | 60 | 90 | 75 | 90,225.50 | 53.7 | 14,349.70 | 61,185.50 | fail |
| AB | 60 | 90 | 90 | 85,275.50 | 53.7 | 15,819.70 | 56,235.50 | fail |
| AB | 60 | 105 | none | 59,151.50 | 53.7 | 17,523.70 | 30,111.50 | fail |
| AB | 60 | 105 | 50 | 78,777.50 | 53.7 | 24,564.70 | 49,737.50 | fail |
| AB | 60 | 105 | 75 | 84,327.50 | 53.7 | 17,919.70 | 55,287.50 | fail |
| AB | 60 | 105 | 90 | 73,677.50 | 53.7 | 18,039.70 | 44,637.50 | fail |

## Family 2 — NS1 permutations (Cycles 31–33 + Cycle 41 cross): 24 cells, no pass
Pool rebuilt per cell (B2 base + regenerated second legs → UNIQUE-ONCE → NS1-CE block → premium band [400,550) block → rebuilt anchored states → cold-(lA) skip → working exits). Axis cells gated vs v15; the 17 cross cells gated vs v16 with the v16 assembly.

| Cell | Taken | Net ₹ | Verdict |
|---|---|---|---|
| room 1.3 (win 14:30, ATM) | 82 | 105,167.00 | fail book identical to working book |
| room 1.4 | 82 | 105,167.00 | fail book identical to working book |
| room 1.6 | 82 | 105,167.00 | fail book identical to working book |
| window 14:00 (room 1.5, ATM) | 82 | 105,167.00 | fail book identical to working book |
| window 15:00 | 83 | 104,842.00 | fail  |
| strike 100 ITM (room 1.5, 14:30) | 80 | 96,809.50 | fail  |
| window 15:00 detail | 83 | 104,842.00 | the one added leg (2026-09-03 PE, entry premium 588.0) scores −₹325.00 square-off |
| room 1.3/1.4 detail | — | — | their only newly admitted leg (2026-01-07 PE, entry premium 445.85) falls inside the blocked premium band [400,550) — the room axis cannot bite |
| cross room1.3_win14:00_itm0 | 82 | 106,517.00 | fail |
| cross room1.3_win14:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |
| cross room1.3_win14:30_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |
| cross room1.3_win15:00_itm0 | 83 | 106,192.00 | fail |
| cross room1.3_win15:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 2 named) |
| cross room1.4_win14:00_itm0 | 82 | 106,517.00 | fail |
| cross room1.4_win14:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |
| cross room1.4_win14:30_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |
| cross room1.4_win15:00_itm0 | 83 | 106,192.00 | fail |
| cross room1.4_win15:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 2 named) |
| cross room1.5_win14:00_itm1 | 80 | 98,159.50 | fail |
| cross room1.5_win15:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |
| cross room1.6_win14:00_itm0 | 82 | 106,517.00 | fail |
| cross room1.6_win14:00_itm1 | 80 | 98,159.50 | fail |
| cross room1.6_win14:30_itm1 | 80 | 98,159.50 | fail |
| cross room1.6_win15:00_itm0 | 83 | 106,192.00 | fail |
| cross room1.6_win15:00_itm1 | 80 | 98,159.50 | fail (stream NOT_COMPUTED 1 named) |

## Family 3 — entry-side permutations (Cycles 34–37)
- **(lA) rescan cutoff 11:30 (C34):** 80 taken, +₹104,857.00 — REJECTED (net −₹310.00 vs v15; frequency 1.9704/week < 2.0).
- **(lA) rescan cutoff 12:30 (C35):** 80 taken, +₹104,857.00 — REJECTED (same legs lost; frequency 1.9704/week). Mechanism, measured: cutting the rescan removes the pooled (lA) winners on 2026-02-24 (and, at 11:30, 2026-09-08's candidacy), and on 2026-04-16 / 2026-06-30 the surviving 09:45 Skill legs lose their second source system and fall under the B2 Skill-solo ≤09:55 drop — a pipeline interaction, recorded not hidden. The frozen 13:30 cutoff is worth +₹310.00 to the book.
- **Bias thresholds ±5 (C36):** (40, 85) and (30, 75) each remove **zero** stored V5-v2 winners — no winner sits on a flip band (CE winners on prev-day closing strength ∈ [35,40): none; PE winners on [75,80): none). Both cells are exact no-ops on the stored book; the admission side (legs a looser gate would have generated) does not exist in stored candidates and was not invented.
- **Expiry-day strike 100 ITM (C37):** +₹101,417.00 — REJECTED (−₹3,750.00). Only 1 of the 8 expiry-day legs changes outcome at the ITM strike (2026-02-24 PE +₹2,030 → −₹1,720); level-relative exits make the other 7 identical.

## Family 4 — use-case pockets (Cycles 38–40)
- **Jun/Jul PE bleed (C38).** Diagnosis first (v16 book, 69 PE legs): Jun/Jul PE = 14 legs / −₹15,680.00 / 12 losers; the mechanical signature frozen after diagnosis and before scoring — **PE leg with anchored state cold** — covers 10 of the 14 (−₹13,000.00); prev-day-return and gap signatures do not isolate it. Conditional geometries on the 17 signature legs, all REJECTED: plain (−50/+90) +₹103,967.00; plain (−60/+90) +₹101,925.50; plain (−40/+90) +₹103,067.00. The bleed is not an exit-geometry problem: the cold-PE legs that run earn more under the standard assembly than any tested variant recovers from the losers.
- **Expiry-day pocket (C39).** Expiry-day legs (8) under plain G0 (−50/+90) regardless of segment/state: **+₹106,517.00 (+₹1,350.00) — full gate PASS, BANKED as book v16**. Variants rejected: (−40/+90) +₹104,117.00; (−50/+75) +₹105,167.00. Expiry-day paths do better without the runner: no lock give-back on expiry-day theta paths.
- **Wide-candle rejection standalone (C40).** Blue-Line setup3 legs admitted on unused keys under the frozen admission rules: exactly **1 leg** in Jan–Oct (2026-07-06 PE, entry premium 683.5), scoring −₹1,720.00 → combined +₹104,797.00 — REJECTED. The book's pool already covers nearly every setup3 day.

## Family 5 — combinations (Cycle 41)
- Passing ingredients from Families 1–4: exactly two — the Cycle-28 grid cell (lt400 trigger 105) and the Cycle-39 expiry-day plain geometry. Families 2, 3 and the other pockets produced no passing ingredient, so no further stack exists to form. The two-ingredient stack was re-gated formally against the Round-2 starting book: **book v16 vs v14 — gate PASS** (net +₹106,517.00 vs +₹104,567.00; FT90 53.7 both; no red month-ends; no green month flips; halves ≥ 0; placebo beaten; timing audit 0 violations; independent re-sum matched).

## Ending book v16 — controlled scorecard
- Jan–Oct 2026: **+₹106,517.00**, 82 trades, FT 52.4% (FT90 53.7%), 2.0197/week, premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE. Pace ₹10,651.70/month vs the ₹15,000 floor → **gap ₹43,483.00**.
- Months: 01 28,080.00 · 02 24,120.00 · 03 15,880.00 · 04 6,810.00 · 05 15,340.00 · 06 -6,120.00 · 07 -13,000.00 · 08 8,499.00 · 09 2,487.50 · 10 24,420.50. Red month-ends: none.
- Halves: Jan–May +₹90,230.00 · Jun–Oct +₹16,287.00. Placebo (+30 min): +₹18,365.20 (beaten). Ex-top-3: +₹77,477.00. Timing audit: 0 violations / 82 entry bars. NOT_COMPUTED: 0. Independent re-sum: `bank_engine_r2c41_stack_trades.csv` — 82 trades / +₹106,517.00, matched.
- Definition (frozen in `bank_engine_frozen.md`): pool V1 (B2 + NS1 second legs) → NS1 CE blocked → entry premium [400,550) blocked → anchored trailing-10 state → cold (lA) stand-aside; exits: entry premium <400 → runner stop −50, trigger +105, lock +75, second target +330; ≥400 warm → runner stop −50, trigger +90, lock +90, second target +180; ≥400 cold → plain −50/+90; **expiry-day legs (date == expiry) → plain −50/+90 regardless of segment/state**; square-off 15:10.

## Cycle index (Round 2)
28–30 exit grid (108 cells, 1 banked → v15) · 31 NS1 room · 32 NS1 window · 33 NS1 strike ITM · 34 (lA) cutoff 11:30 · 35 (lA) cutoff 12:30 · 36 bias ±5 (zero-effect, proven) · 37 expiry-day strike ITM · 38 bleed pocket (3 geometries) · 39 expiry-day pocket (3 geometries, 1 banked → v16) · 40 setup3 standalone · 41 NS1 cross-grid (17 cells) + combination stack re-gate.

Artefacts: `bank_r2_core.py`, `bank_r2_grid.py` + `bank_r2_grid_results.json`, `bank_r2_ns1.py` + `bank_r2_ns1_results.json` + `bank_r2_ns1_cross_results.json`, `bank_r2_entry.py` + `bank_r2_entry_results.json`, `bank_r2_expiry.py` + `bank_r2_expiry_results.json`, `bank_r2_bleed.py` + `bank_r2_bleed_results.json`, `bank_r2_blue.py` + `bank_r2_blue_results.json`, `bank_r2_combine.py`, `bank_r2_fetch_missing.py`; trades: `bank_engine_r2c28_gridA_t105_trades.csv` (v15), `bank_engine_r2c39_exp_plain_trades.csv` and `bank_engine_r2c41_stack_trades.csv` (v16).
