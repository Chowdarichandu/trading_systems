# Historical proof — Nifty — U1-N1 — PREMIUMS ONLY, Jan–Oct 2026

**Real money: ₹0 — paper proof only. No live trades were placed.**

This file covers **Nifty only**, in its own channel. It is not pooled with the other index and no combined verdict is made.

![Cumulative equity curve — Nifty U1-N1, premiums only](sandbox://workspace/trading/historical_proof_nifty_N1_chart.png)

## What was done

Every Jan–Sep 2026 leg of the frozen U1-N1 (which had only been scored as spot provisional: spot points × 100 shares − ₹40) was re-scored on its **actual option premium candles** fetched from Upstox expired-instruments data (script-token browser-fetch route; the Muse connector was not used). October legs were already premium-scored in the frozen run and are carried in unchanged — the scoring code was re-validated against them and reproduces them exactly (e.g. Nifty 8 Oct 22500 PE target +₹5,630.00; Nifty 23 Oct 22500 PE square-off −₹1,334.75).

- Scoring (identical to the October overlay): entry premium = open of the 5-min option candle at the leg's entry bar; stop = entry − 50 premium points, checked **before** target = entry + 90 on every bar including the entry bar; square-off at the 15:10 bar close; cost ₹220/trade; net per 1 lot = (exit − entry) × lot − ₹220.
- Strike: ATM nearest 100 to spot at the entry bar (spot from the leg file, or from cached 5-min spot candles at the entry bar where the leg file carried no spot value — source noted per leg in the working file).
- Expiry: the monthly expiry applicable to the trade date — the first monthly expiry on or after the trade date. Monthly expiries in 2026 (both indices, verified from expired-contract data): 27 Jan, 24 Feb, 30 Mar, 28 Apr, 26 May, 30 Jun, 28 Jul, 25 Aug, 29 Sep, 27 Oct. The expiry used is stated per trade in the trades CSV.
- **Lot size, verified from the contract data for every monthly expiry Jan–Oct 2026: Nifty 65 — constant all year.** Not assumed from October; each month's contracts were read and all show the same lot size.
- Completeness: **108 of 108 legs COMPUTED, 0 NOT_COMPUTED.** Every Jan–Sep premium candle fetch returned data; no leg was substituted with spot points and nothing was invented.

## Month by month — premiums only, per 1 lot

| Month | Trades | Targets | Stops | Square-offs | Full-target % | Net (₹) | Month-end cumulative (₹) | Month-end |
|---|---|---|---|---|---|---|---|---|
| Jan 2026 | 13 | 4 | 5 | 4 | 30.8% | ₹6,896.50 | ₹6,896.50 | ✅ green |
| Feb 2026 | 13 | 3 | 5 | 5 | 23.1% | ₹6,565.00 | ₹13,461.50 | ✅ green |
| Mar 2026 | 11 | 4 | 6 | 1 | 36.4% | ₹1,460.50 | ₹14,922.00 | ✅ green |
| Apr 2026 | 11 | 4 | 3 | 4 | 36.4% | ₹12,981.75 | ₹27,903.75 | ✅ green |
| May 2026 | 7 | 1 | 6 | 0 | 14.3% | ₹-15,190.00 | ₹12,713.75 | ✅ green |
| Jun 2026 | 9 | 2 | 3 | 4 | 22.2% | ₹1,162.75 | ₹13,876.50 | ✅ green |
| Jul 2026 | 12 | 2 | 5 | 5 | 16.7% | ₹-7,596.25 | ₹6,280.25 | ✅ green |
| Aug 2026 | 11 | 2 | 1 | 8 | 18.2% | ₹778.00 | ₹7,058.25 | ✅ green |
| Sep 2026 | 13 | 2 | 1 | 10 | 15.4% | ₹7,325.50 | ₹14,383.75 | ✅ green |
| Oct 2026 | 8 | 4 | 3 | 1 | 50.0% | ₹10,775.25 | ₹25,159.00 | ✅ green |
| **Jan–Oct total** | **108** | **28** | **38** | **42** | **25.9%** | **₹25,159.00** | — | — |

- **Jan–Oct premium-only total (Nifty alone): ₹25,159.00 per 1 lot**
- Trades/week: **2.66** (108 trades over 203 trading days)
- Full-target %: **25.9%**

## Old mixed basis vs new premium-only basis

| Basis | Jan–Sep | October | Jan–Oct |
|---|---|---|---|
| Old (spot provisional Jan–Sep + premiums Oct, "mixed") | ₹157,365.00 (spot points × 100 shares − ₹40 — not an options profit) | ₹10,775.25 (premiums) | ₹168,140.25 |
| **New (premiums only)** | **₹14,383.75** | **₹10,775.25** | **₹25,159.00** |

The premium-only Jan–Oct total is **₹142,981.25 lower** than the mixed figure. October does not change at all — the entire difference is Jan–Sep, where the spot-provisional unit (spot points × 100 shares) systematically overstated what the option premium actually did: spot moves of +150 to +230 points that scored as ₹15,000–₹23,000 spot "wins" were often only worth a premium stop or a small square-off, because the premium does not move 1:1 with spot and decays while the spot move develops. **36 of the 100 Jan–Sep legs change sign** between the two bases. Biggest disagreements:

- **2026-02-02 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-3,470.00 (premium exit: stop; swing ₹-12,430.00)
- **2026-03-02 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-3,470.00 (premium exit: stop; swing ₹-12,430.00)
- **2026-03-16 PE ((lA) v2)**: spot provisional ₹8,940.00 → premium ₹-3,470.00 (premium exit: stop; swing ₹-12,410.00)
- **2026-07-09 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-2,712.75 (premium exit: square_off; swing ₹-11,672.75)
- **2026-03-17 CE (Skill V3)**: spot provisional ₹6,100.00 → premium ₹-3,470.00 (premium exit: stop; swing ₹-9,570.00)
- **2026-04-07 CE (Skill V3)**: spot provisional ₹-3,555.00 → premium ₹5,630.00 (premium exit: target; swing ₹9,185.00)

## Honest verdict — Nifty alone

- Ends positive on premiums alone: **YES — ₹25,159.00 per 1 lot over Jan–Oct 2026.** The system is not a fiction; the premium history is green.
- But it is **far smaller** than the mixed-basis ₹168,140.25 suggested — the mixed figure must not be quoted as this system's premium performance again.
- Every month-end green cumulatively: **YES** — all ten month-ends close green.
- Worst month: **May 2026, ₹-15,190.00**.
- Max drawdown of the cumulative premium curve (trade by trade): **₹28,231.50**.
- Best month: Apr 2026, ₹12,981.75 — **51.6% of the entire Jan–Oct premium total** comes from that single month.
- Every month-end closes green cumulatively — that part of the mixed-basis story survives. But the cushion is thin: after May's −₹15,190.00 month the cumulative halved, and the curve's max drawdown of ₹28,231.50 is larger than the entire final total of ₹25,159.00. Hit quality is the weakness: only 25.9% of legs reached the +90 premium target and 42 of 108 legs ended as square-offs — spot moves that the premium never converted into a target.
- Nothing was re-tuned in this task. U1-N1 remains a frozen candidate; November 2026 paper (from Mon 2026-11-02, this index's own log) is still the validation step, and it should be judged against these premium-only numbers, not the mixed ones.

Trade-by-trade detail: `historical_proof_nifty_N1_trades.csv` (entry/exit premium, exit reason, net per leg; October legs flagged in the note column).
