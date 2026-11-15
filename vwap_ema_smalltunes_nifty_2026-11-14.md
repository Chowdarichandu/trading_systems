# SMALL TUNES — VWAP x EMA CROSSOVER · NIFTY · 2026-11-14

Spec: `vwap_ema_smalltunes_nifty_SPEC.md` (frozen before scoring). Build: `vwap_ema_smalltunes_nifty_build.py`. Numbers: `vwap_ema_smalltunes_nifty_results.json`.
Basis: option buying only, 1 lot (65), Rs220/trade, paper. Entry = next bar open at the stored weekly nearest-strike contract; missing contract = NC, counted, never substituted. Windows: Jan-Jun / Jul-Oct split at 2026-07-01; November CF = Nov 2-13, descriptive. 232 grid rows scored (A 24, B 16, C 96, C2 96).

## Best row per rule (full Jan-Oct net)

| Rule | Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC | Placebo pct |
|---|---|---|---|---|---|---|---|
| A — VWAP cross | — · hold 1 · buf 0.00% · E4 | +21,311.25 (40 tr, WR 30.0%) | +3,874.10 (30 tr, WR 26.7%) | +25,185.35 (70 tr, WR 28.6%) | -408.50 (1 tr, WR 0.0%) | 54 | 84.8 |
| B — EMA cross | EMA 20/50 · — · — · E2 | +50,397.50 (42 tr, WR 61.9%) | -26,310.50 (34 tr, WR 26.5%) | +24,087.00 (76 tr, WR 46.1%) | -3,470.00 (1 tr, WR 0.0%) | 71 | 91.6 |
| C — EMA cross + VWAP side | EMA 9/21 · hold 0 · buf 0.10% · E4 | +46,352.00 (46 tr, WR 30.4%) | +227.50 (26 tr, WR 34.6%) | +46,579.50 (72 tr, WR 31.9%) | -1,919.75 (1 tr, WR 0.0%) | 68 | 95.0 |
| C2 — VWAP cross + EMA aligned | EMA 20/50 · hold 1 · buf 0.00% · E1 | +1,872.75 (56 tr, WR 44.6%) | -21,699.50 (43 tr, WR 34.9%) | -19,826.75 (99 tr, WR 40.4%) | -453.00 (2 tr, WR 50.0%) | 74 | 49.7 |

Placebo: 1,000 random-entry rebuilds of the best row (same trade count, same CE/PE mix, same exit rule). Percentile = share of random totals <= the real total.
- A — VWAP cross: real +25,185.35 · random mean -2,671.53 · random p95 +44,739.95 · percentile 84.8
- B — EMA cross: real +24,087.00 · random mean -12,036.32 · random p95 +31,638.57 · percentile 91.6
- C — EMA cross + VWAP side: real +46,579.50 · random mean -2,756.15 · random p95 +45,977.37 · percentile 95.0
- C2 — VWAP cross + EMA aligned: real -19,826.75 · random mean -20,398.08 · random p95 +23,671.70 · percentile 49.7

Timing audit on the four best rows: entry bar = signal bar + 5 min and entry premium = stored open on every scored trade — PASS (all four rules). Independent recomputation of EMA fast/slow and futures VWAP at each best row's first signal bar matched the main path to 0.001 — PASS (all four rules).

## Rule A — VWAP cross

Signals Jan-Oct: 124 · scored 70 · NC no-file 54 · NC partial 0 · late 0.

One-dial-at-a-time path from base (EMA 9/21 · hold 0 · buf 0.00% · E2):

**Base**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| — · hold 0 · buf 0.00% · E2 | -16,862.25 (67 tr, WR 38.8%) | -22,225.25 (60 tr, WR 36.7%) | -39,087.50 (127 tr, WR 37.8%) | -3,839.50 (2 tr, WR 0.0%) | 67 |

**Dial 2 — VWAP hold**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| — · hold 0 · buf 0.00% · E2 | -16,862.25 (67 tr, WR 38.8%) | -22,225.25 (60 tr, WR 36.7%) | -39,087.50 (127 tr, WR 37.8%) | -3,839.50 (2 tr, WR 0.0%) | 67 |
| — · hold 1 · buf 0.00% · E2 | -18,797.00 (40 tr, WR 40.0%) | -6,041.00 (30 tr, WR 33.3%) | -24,838.00 (70 tr, WR 37.1%) | -3,470.00 (1 tr, WR 0.0%) | 54 |

**Dial 3 — VWAP buffer**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| — · hold 1 · buf 0.00% · E2 | -18,797.00 (40 tr, WR 40.0%) | -6,041.00 (30 tr, WR 33.3%) | -24,838.00 (70 tr, WR 37.1%) | -3,470.00 (1 tr, WR 0.0%) | 54 |
| — · hold 1 · buf 0.05% · E2 | -3,769.25 (30 tr, WR 43.3%) | +2,976.50 (32 tr, WR 40.6%) | -792.75 (62 tr, WR 41.9%) | -7,862.00 (3 tr, WR 0.0%) | 68 |
| — · hold 1 · buf 0.10% · E2 | +8,839.00 (25 tr, WR 48.0%) | -21,377.00 (21 tr, WR 28.6%) | -12,538.00 (46 tr, WR 39.1%) | -11,425.25 (5 tr, WR 20.0%) | 72 |

**Dial 4 — Exit**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| — · hold 1 · buf 0.05% · E1 | +377.75 (30 tr, WR 43.3%) | -4,810.50 (32 tr, WR 40.6%) | -4,432.75 (62 tr, WR 41.9%) | -6,562.00 (3 tr, WR 0.0%) | 68 |
| — · hold 1 · buf 0.05% · E2 | -3,769.25 (30 tr, WR 43.3%) | +2,976.50 (32 tr, WR 40.6%) | -792.75 (62 tr, WR 41.9%) | -7,862.00 (3 tr, WR 0.0%) | 68 |
| — · hold 1 · buf 0.05% · E3 | +1,241.60 (30 tr, WR 23.3%) | -1,762.00 (32 tr, WR 18.8%) | -520.40 (62 tr, WR 21.0%) | -4,644.50 (3 tr, WR 0.0%) | 68 |
| — · hold 1 · buf 0.05% · E4 | -7,552.90 (30 tr, WR 30.0%) | +4,071.10 (32 tr, WR 31.2%) | -3,481.80 (62 tr, WR 30.6%) | -2,801.75 (3 tr, WR 33.3%) | 68 |

Path end: — · hold 1 · buf 0.05% · E3 — full -520.40 (62 tr, WR 21.0%).
Best full-grid row: — · hold 1 · buf 0.00% · E4 — full +25,185.35 (70 tr, WR 28.6%) · placebo percentile 84.8.

## Rule B — EMA cross

Signals Jan-Oct: 152 · scored 76 · NC no-file 71 · NC partial 0 · late 5.

One-dial-at-a-time path from base (EMA 9/21 · hold 0 · buf 0.00% · E2):

**Base**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 9/21 · — · — · E2 | +1,228.65 (71 tr, WR 39.4%) | -25,680.85 (52 tr, WR 34.6%) | -24,452.20 (123 tr, WR 37.4%) | -6,940.00 (2 tr, WR 0.0%) | 68 |

**Dial 1 — EMA pair**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 5/20 · — · — · E2 | -15,154.00 (82 tr, WR 37.8%) | -29,051.60 (58 tr, WR 37.9%) | -44,205.60 (140 tr, WR 37.9%) | -10,410.00 (3 tr, WR 0.0%) | 60 |
| EMA 9/21 · — · — · E2 | +1,228.65 (71 tr, WR 39.4%) | -25,680.85 (52 tr, WR 34.6%) | -24,452.20 (123 tr, WR 37.4%) | -6,940.00 (2 tr, WR 0.0%) | 68 |
| EMA 13/34 · — · — · E2 | -4,964.25 (57 tr, WR 43.9%) | -34,895.35 (48 tr, WR 33.3%) | -39,859.60 (105 tr, WR 39.0%) | -3,470.00 (1 tr, WR 0.0%) | 67 |
| EMA 20/50 · — · — · E2 | +50,397.50 (42 tr, WR 61.9%) | -26,310.50 (34 tr, WR 26.5%) | +24,087.00 (76 tr, WR 46.1%) | -3,470.00 (1 tr, WR 0.0%) | 71 |

**Dial 4 — Exit**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · — · — · E1 | +40,377.75 (42 tr, WR 57.1%) | -23,200.25 (34 tr, WR 26.5%) | +17,177.50 (76 tr, WR 43.4%) | -2,820.00 (1 tr, WR 0.0%) | 71 |
| EMA 20/50 · — · — · E2 | +50,397.50 (42 tr, WR 61.9%) | -26,310.50 (34 tr, WR 26.5%) | +24,087.00 (76 tr, WR 46.1%) | -3,470.00 (1 tr, WR 0.0%) | 71 |
| EMA 20/50 · — · — · E3 | +30,890.35 (42 tr, WR 45.2%) | -18,221.25 (34 tr, WR 20.6%) | +12,669.10 (76 tr, WR 34.2%) | -2,079.00 (1 tr, WR 0.0%) | 71 |
| EMA 20/50 · — · — · E4 | +52,201.25 (42 tr, WR 52.4%) | -32,134.50 (34 tr, WR 23.5%) | +20,066.75 (76 tr, WR 39.5%) | -4,120.00 (1 tr, WR 0.0%) | 71 |

Path end: EMA 20/50 · — · — · E2 — full +24,087.00 (76 tr, WR 46.1%).
Best full-grid row: EMA 20/50 · — · — · E2 — full +24,087.00 (76 tr, WR 46.1%) · placebo percentile 91.6.

## Rule C — EMA cross + VWAP side

Signals Jan-Oct: 141 · scored 72 · NC no-file 68 · NC partial 0 · late 1.

One-dial-at-a-time path from base (EMA 9/21 · hold 0 · buf 0.00% · E2):

**Base**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 9/21 · hold 0 · buf 0.00% · E2 | +3,929.15 (61 tr, WR 41.0%) | -19,760.10 (48 tr, WR 37.5%) | -15,830.95 (109 tr, WR 39.4%) | -3,470.00 (1 tr, WR 0.0%) | 73 |

**Dial 1 — EMA pair**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 5/20 · hold 0 · buf 0.00% · E2 | -10,576.50 (77 tr, WR 37.7%) | -25,516.60 (57 tr, WR 38.6%) | -36,093.10 (134 tr, WR 38.1%) | -6,940.00 (2 tr, WR 0.0%) | 60 |
| EMA 9/21 · hold 0 · buf 0.00% · E2 | +3,929.15 (61 tr, WR 41.0%) | -19,760.10 (48 tr, WR 37.5%) | -15,830.95 (109 tr, WR 39.4%) | -3,470.00 (1 tr, WR 0.0%) | 73 |
| EMA 13/34 · hold 0 · buf 0.00% · E2 | -6,785.00 (53 tr, WR 43.4%) | -33,972.10 (45 tr, WR 33.3%) | -40,757.10 (98 tr, WR 38.8%) | -3,470.00 (1 tr, WR 0.0%) | 69 |
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +44,767.50 (41 tr, WR 61.0%) | -18,718.00 (28 tr, WR 25.0%) | +26,049.50 (69 tr, WR 46.4%) | -3,470.00 (1 tr, WR 0.0%) | 73 |

**Dial 2 — VWAP hold**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +44,767.50 (41 tr, WR 61.0%) | -18,718.00 (28 tr, WR 25.0%) | +26,049.50 (69 tr, WR 46.4%) | -3,470.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 1 · buf 0.00% · E2 | +14,842.65 (35 tr, WR 51.4%) | -26,851.50 (26 tr, WR 23.1%) | -12,008.85 (61 tr, WR 39.3%) | -3,470.00 (1 tr, WR 0.0%) | 75 |

**Dial 3 — VWAP buffer**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +44,767.50 (41 tr, WR 61.0%) | -18,718.00 (28 tr, WR 25.0%) | +26,049.50 (69 tr, WR 46.4%) | -3,470.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 0 · buf 0.05% · E2 | +43,530.50 (39 tr, WR 61.5%) | -9,872.25 (24 tr, WR 33.3%) | +33,658.25 (63 tr, WR 50.8%) | -3,470.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 0 · buf 0.10% · E2 | +16,131.50 (31 tr, WR 51.6%) | -6,564.25 (17 tr, WR 29.4%) | +9,567.25 (48 tr, WR 43.8%) | -3,470.00 (1 tr, WR 0.0%) | 68 |

**Dial 4 — Exit**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.05% · E1 | +34,537.75 (39 tr, WR 56.4%) | -11,211.25 (24 tr, WR 33.3%) | +23,326.50 (63 tr, WR 47.6%) | -2,820.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 0 · buf 0.05% · E2 | +43,530.50 (39 tr, WR 61.5%) | -9,872.25 (24 tr, WR 33.3%) | +33,658.25 (63 tr, WR 50.8%) | -3,470.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 0 · buf 0.05% · E3 | +22,638.85 (39 tr, WR 43.6%) | -14,718.00 (24 tr, WR 29.2%) | +7,920.85 (63 tr, WR 38.1%) | -2,079.00 (1 tr, WR 0.0%) | 73 |
| EMA 20/50 · hold 0 · buf 0.05% · E4 | +52,763.75 (39 tr, WR 53.8%) | -17,259.50 (24 tr, WR 29.2%) | +35,504.25 (63 tr, WR 44.4%) | -4,120.00 (1 tr, WR 0.0%) | 73 |

Path end: EMA 20/50 · hold 0 · buf 0.05% · E4 — full +35,504.25 (63 tr, WR 44.4%).
Best full-grid row: EMA 9/21 · hold 0 · buf 0.10% · E4 — full +46,579.50 (72 tr, WR 31.9%) · placebo percentile 95.0.

## Rule C2 — VWAP cross + EMA aligned

Signals Jan-Oct: 173 · scored 99 · NC no-file 74 · NC partial 0 · late 0.

One-dial-at-a-time path from base (EMA 9/21 · hold 0 · buf 0.00% · E2):

**Base**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 9/21 · hold 0 · buf 0.00% · E2 | -11,005.50 (64 tr, WR 40.6%) | -40,304.25 (51 tr, WR 37.3%) | -51,309.75 (115 tr, WR 39.1%) | +4,566.00 (3 tr, WR 66.7%) | 67 |

**Dial 1 — EMA pair**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 5/20 · hold 0 · buf 0.00% · E2 | +5,884.50 (67 tr, WR 43.3%) | -45,792.50 (52 tr, WR 34.6%) | -39,908.00 (119 tr, WR 39.5%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 9/21 · hold 0 · buf 0.00% · E2 | -11,005.50 (64 tr, WR 40.6%) | -40,304.25 (51 tr, WR 37.3%) | -51,309.75 (115 tr, WR 39.1%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 13/34 · hold 0 · buf 0.00% · E2 | +3,310.75 (64 tr, WR 43.8%) | -49,490.75 (49 tr, WR 36.7%) | -46,180.00 (113 tr, WR 40.7%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +8,958.25 (63 tr, WR 46.0%) | -37,955.50 (50 tr, WR 40.0%) | -28,997.25 (113 tr, WR 43.4%) | +4,566.00 (3 tr, WR 66.7%) | 67 |

**Dial 2 — VWAP hold**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +8,958.25 (63 tr, WR 46.0%) | -37,955.50 (50 tr, WR 40.0%) | -28,997.25 (113 tr, WR 43.4%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 20/50 · hold 1 · buf 0.00% · E2 | -38,703.50 (56 tr, WR 35.7%) | -25,781.50 (43 tr, WR 34.9%) | -64,485.00 (99 tr, WR 35.4%) | -1,103.00 (2 tr, WR 50.0%) | 74 |

**Dial 3 — VWAP buffer**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +8,958.25 (63 tr, WR 46.0%) | -37,955.50 (50 tr, WR 40.0%) | -28,997.25 (113 tr, WR 43.4%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 20/50 · hold 0 · buf 0.05% · E2 | -11,805.75 (60 tr, WR 46.7%) | -40,848.75 (46 tr, WR 30.4%) | -52,654.50 (106 tr, WR 39.6%) | +13,256.50 (3 tr, WR 100.0%) | 79 |
| EMA 20/50 · hold 0 · buf 0.10% · E2 | -16,267.35 (47 tr, WR 40.4%) | -27,821.00 (38 tr, WR 31.6%) | -44,088.35 (85 tr, WR 36.5%) | +6,911.25 (5 tr, WR 80.0%) | 100 |

**Dial 4 — Exit**

| Config | Jan-Jun | Jul-Oct | Full Jan-Oct | Nov CF | NC |
|---|---|---|---|---|---|
| EMA 20/50 · hold 0 · buf 0.00% · E1 | +4,541.50 (63 tr, WR 42.9%) | -33,694.75 (50 tr, WR 40.0%) | -29,153.25 (113 tr, WR 41.6%) | +3,916.00 (3 tr, WR 66.7%) | 67 |
| EMA 20/50 · hold 0 · buf 0.00% · E2 | +8,958.25 (63 tr, WR 46.0%) | -37,955.50 (50 tr, WR 40.0%) | -28,997.25 (113 tr, WR 43.4%) | +4,566.00 (3 tr, WR 66.7%) | 67 |
| EMA 20/50 · hold 0 · buf 0.00% · E3 | -35,340.55 (63 tr, WR 17.5%) | -30,285.50 (50 tr, WR 10.0%) | -65,626.05 (113 tr, WR 14.2%) | +1,030.00 (3 tr, WR 33.3%) | 67 |
| EMA 20/50 · hold 0 · buf 0.00% · E4 | -33,158.50 (63 tr, WR 33.3%) | -35,696.75 (50 tr, WR 28.0%) | -68,855.25 (113 tr, WR 31.0%) | +6,834.50 (3 tr, WR 66.7%) | 67 |

Path end: EMA 20/50 · hold 0 · buf 0.00% · E2 — full -28,997.25 (113 tr, WR 43.4%).
Best full-grid row: EMA 20/50 · hold 1 · buf 0.00% · E1 — full -19,826.75 (99 tr, WR 40.4%) · placebo percentile 49.7.
