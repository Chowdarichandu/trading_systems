# CAPPED V2 — Jan 2025 to 28 Oct 2026 (IN PROGRESS, Jan-Mar 2025 done)
Paper only, no orders, no live trading. Proprietary to Chandu, workspace only.
New cap rule 2026-10-29 09:20 IST: 3 index + 3 stock = 6 trades/week total,
separate caps, max 1/symbol/week, convicted high-return setups only.
Provisional implementation: prospective net target >= ₹500, ranking
setup > bias-strong > room > prospective target net. See
progressive_capped_v2_jan2025_oct2026_progress.md for month detail.
V1 files are NOT overwritten.

## Jan-Mar 2025 summary (verified from capped_v2_summary_2025-01/02/03.json)
| Series | Jan | Feb | Mar | Cumulative to Mar | Trades | Win |
|---|---|---|---|---|---|---|
| V2-V4 total | -₹62,185 | +₹61,830 | -₹10,285 | -₹10,640 | 57 | 33.3% |
| V2-V4 stocks-only | -₹1,740 | +₹180 | +₹3,915 | +₹2,355 | 57 | — |
| V2-Skill total | -₹59,570 | +₹36,370 | -₹1,055 | -₹24,255 | 51 | 33.3% |
| V2-Skill stocks-only | -₹1,225 | -₹6,425 | +₹6,035 | -₹1,615 | 51 | — |
| V2-Unified total | -₹63,200 | +₹60,060 | -₹10,285 | -₹13,425 | 59 | 32.2% |
| V2-Unified stocks-only | -₹2,755 | -₹1,590 | +₹3,915 | -₹430 | 59 | — |

Counts: 16-23 trades/month total (3.25-4.6/week), NOT 500+.
Structural note: index leg maxes at 2/week (only NIFTY + BANKNIFTY under
1/symbol/week), so 6/week as stated is unattainable as written; attainable
max is 5/week. Needs Chandu's confirmation, not a silent rule change.

High-return check: prospective target size DOES rise vs v1's ₹300 small wins
(stocks avg ₹936-₹2,268/month; index avg ₹10,558-₹23,218), but realised net
does not follow — Jan index leg alone is -₹60,445 (V4), Feb +₹61,650, Mar
-₹14,200. Bigger target = bigger stop at 100 shares x index points.
Sensitivity ₹1000 does not fix Jan, and improves Skill stocks only in Mar alone.

X verdict to Mar: frequency passes on count, net progression FAILS in total
for all series and in stocks-only for Skill/Unified. NO V2 ADOPTION yet.
Next: Apr 2025 onward to 28 Oct 2026, same V2 rules.
