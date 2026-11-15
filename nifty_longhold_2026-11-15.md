# Monthly Long Holds — Nifty + Bank Nifty (2026-11-15)

Owner's order: "buy today and hold for two months in Nifty, seeing the projection
for the long months" + extension 10:45 — "monthly holding of options, Nifty or
Bank Nifty." Spec: `nifty_longhold_SPEC.md` (frozen before scoring).
**Research only — nothing armed. Option BUYING only.**

## The rule
At each month-end close, trend from daily spot: UP = close > 50-DMA and
50-DMA > 200-DMA; DOWN = mirror; else FLAT (no trade). On the next month's first
trading day, buy that month's MONTHLY-expiry ATM contract on the trend side at
the open. **HOLD-1M** exits at the expiry close. **HOLD-2M** recomputes the
trend at the first expiry — FLAT stops the position; otherwise it rolls into
the next monthly ATM on the same side and exits at the second expiry close.
No stops of any kind inside a hold.

## Money basis (labelled)
- Nifty 1 lot = 65, Bank Nifty 1 lot = 30. Net per round trip =
  (exit − entry) × lot − **₹220**. HOLD-1M = ₹220 costs; a full HOLD-2M roll =
  ₹440; a FLAT-stopped HOLD-2M = ₹220.
- **Worst case per position = the full premium paid + costs. A monthly option
  held to expiry can and does expire worthless** — in this run, 21 of the 33
  distinct legs exited at ₹0.05–₹0.25, i.e. effectively zero.

## Premium window achieved
Expired-instruments route (Upstox), contract lists verified for every monthly
expiry **Jan 2025 – Oct 2026** for both indices (no holiday step-backs were
needed). Scored entries **2025-02-01 → 2026-10-01**, exits to **2026-10-27**.
**NC = 4**, all one cause: the Nov 2026 monthly expiry (2026-11-23) has not
expired yet, so its premiums do not exist — the Oct-2026-signal positions
(both indices, 1M) and the Sep-2026-signal positions' second legs (2M) are
unscored, counted, never estimated. (Data note: the stored Upstox token had
expired Sat 22:00; the owner's own refresh job was run off-schedule to restore
the feed, same as the Sat 2026-11-14 precedent.)

## Results — NIFTY (1 lot 65)

| Hold | Year | Positions | Net (₹) | WR | Best | Worst | Worst DD |
|---|---|---|---|---|---|---|---|
| 1M | 2025 | 5 | **−45,589.25** | 20.0% | +39,166.75 | −30,113.50 | −84,756.00 |
| 1M | 2026 | 6 | **−36,686.50** | 16.7% | +75,960.00 | −33,015.75 | −93,024.00 |
| 2M | 2025 | 5 | **−112,276.25** | 20.0% | +19,908.25 | −55,027.00 | −132,184.50 |
| 2M | 2026 | 5 | **−56,513.75** | 20.0% | +58,060.00 | −54,565.50 | −114,573.75 |

Halves (net ₹): 1M 2025 — Jan–Jun entries +24,975.00 / Jul–Dec −70,564.25 ·
1M 2026 — Jan–Jun −93,024.00 / Jul–Dec +56,337.50 · 2M 2025 — +5,716.50 /
−117,992.75 · 2M 2026 — −114,573.75 / +58,060.00.
Two-year totals (this index only): **1M −₹82,275.75 (11 positions) ·
2M −₹1,68,790.00 (10 positions).**

## Results — BANK NIFTY (1 lot 30)

| Hold | Year | Positions | Net (₹) | WR | Best | Worst | Worst DD |
|---|---|---|---|---|---|---|---|
| 1M | 2025 | 5 | **−65,271.20** | 40.0% | +9,834.50 | −30,515.50 | −65,271.20 |
| 1M | 2026 | 7 | **−113,027.50** | 14.3% | +11,120.00 | −29,426.50 | −113,027.50 |
| 2M | 2025 | 5 | **−136,468.70** | 0.0% | −12,938.00 | −55,115.00 | −136,468.70 |
| 2M | 2026 | 6 | **−178,730.00** | 0.0% | −20,153.50 | −53,513.00 | −178,730.00 |

Halves (net ₹): 1M 2025 — Jan–Jun −9,184.70 / Jul–Dec −56,086.50 · 1M 2026 —
Jan–Jun −91,805.00 / Jul–Dec −21,222.50 · 2M 2025 — −37,900.20 / −98,568.50 ·
2M 2026 — −125,217.00 / −53,513.00.
Two-year totals (this index only): **1M −₹1,78,298.70 (12 positions) ·
2M −₹3,15,198.70 (11 positions). Bank HOLD-2M lost on all 11 positions.**

## Annex — the long-months projection (SPOT signal study, NOT option money)
Direction-signed forward spot returns per signal month, Aug 2019 onward
(a DOWN signal "wins" when spot falls). No premiums, no costs.

| Index | Horizon | Events | Avg signed return | Win share |
|---|---|---|---|---|
| Nifty | +20d | 47 | +1.230% | 61.7% |
| Nifty | +40d | 46 | **+1.328%** | **65.2%** |
| Nifty | +60d | 45 | +0.671% | 51.1% |
| Bank Nifty | +20d | 50 | −0.256% | 44.0% |
| Bank Nifty | +40d | 49 | **−1.833%** | **42.9%** |
| Bank Nifty | +60d | 48 | −2.714% | 39.6% |

## Reading (plain)
- The Nifty spot projection is mildly real (+40d average +1.33%, 65% win) —
  and the option book still loses in both years at both holds. A ~1.3% average
  spot drift does not pay for a full month of ATM premium held to expiry;
  most months the contract dies at ₹0.05.
- Bank Nifty's projection itself points the wrong way (negative at every
  horizon), and its option book is worse again. HOLD-2M is worse than HOLD-1M
  in all four index-years: the second month's premium usually dies too.
- Files: `nifty_longhold_trades.csv` (every position, both holds, both
  indices), `nifty_longhold_results.json` (summary + annex + NC list),
  build `nifty_longhold_build.py`, cache `nifty_longhold_data/`.
