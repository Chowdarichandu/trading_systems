# Historical proof — Bank Nifty — U1-B2 — PREMIUMS ONLY, Jan–Oct 2026

**Real money: ₹0 — paper proof only. No live trades were placed.**

This file covers **Bank Nifty only**, in its own channel. It is not pooled with the other index and no combined verdict is made.

![Cumulative equity curve — Bank Nifty U1-B2, premiums only](sandbox://workspace/trading/historical_proof_bank_B2_chart.png)

## What was done

Every Jan–Sep 2026 leg of the frozen U1-B2 (which had only been scored as spot provisional: spot points × 100 shares − ₹40) was re-scored on its **actual option premium candles** fetched from Upstox expired-instruments data (script-token browser-fetch route; the Muse connector was not used). October legs were already premium-scored in the frozen run and are carried in unchanged — the scoring code was re-validated against them and reproduces them exactly (e.g. Bank 1 Oct 54900 CE target +₹2,480.00; Bank 13 Oct PE target +₹2,480.00).

- Scoring (identical to the October overlay): entry premium = open of the 5-min option candle at the leg's entry bar; stop = entry − 50 premium points, checked **before** target = entry + 90 on every bar including the entry bar; square-off at the 15:10 bar close; cost ₹220/trade; net per 1 lot = (exit − entry) × lot − ₹220.
- Strike: ATM nearest 100 to spot at the entry bar (spot from the leg file, or from cached 5-min spot candles at the entry bar where the leg file carried no spot value — source noted per leg in the working file).
- Expiry: the monthly expiry applicable to the trade date — the first monthly expiry on or after the trade date. Monthly expiries in 2026 (both indices, verified from expired-contract data): 27 Jan, 24 Feb, 30 Mar, 28 Apr, 26 May, 30 Jun, 28 Jul, 25 Aug, 29 Sep, 27 Oct. The expiry used is stated per trade in the trades CSV.
- **Lot size, verified from the contract data for every monthly expiry Jan–Oct 2026: Bank Nifty 30 — constant all year.** Not assumed from October; each month's contracts were read and all show the same lot size.
- Completeness: **89 of 89 legs COMPUTED, 0 NOT_COMPUTED.** Every Jan–Sep premium candle fetch returned data; no leg was substituted with spot points and nothing was invented.

## Month by month — premiums only, per 1 lot

| Month | Trades | Targets | Stops | Square-offs | Full-target % | Net (₹) | Month-end cumulative (₹) | Month-end |
|---|---|---|---|---|---|---|---|---|
| Jan 2026 | 6 | 2 | 4 | 0 | 33.3% | ₹-1,920.00 | ₹-1,920.00 | 🔴 RED |
| Feb 2026 | 10 | 7 | 2 | 1 | 70.0% | ₹15,377.00 | ₹13,457.00 | ✅ green |
| Mar 2026 | 9 | 6 | 3 | 0 | 66.7% | ₹9,720.00 | ₹23,177.00 | ✅ green |
| Apr 2026 | 11 | 5 | 6 | 0 | 45.5% | ₹2,080.00 | ₹25,257.00 | ✅ green |
| May 2026 | 8 | 5 | 3 | 0 | 62.5% | ₹7,240.00 | ₹32,497.00 | ✅ green |
| Jun 2026 | 8 | 1 | 7 | 0 | 12.5% | ₹-9,560.00 | ₹22,937.00 | ✅ green |
| Jul 2026 | 10 | 2 | 8 | 0 | 20.0% | ₹-8,800.00 | ₹14,137.00 | ✅ green |
| Aug 2026 | 11 | 2 | 8 | 1 | 18.2% | ₹-7,301.00 | ₹6,836.00 | ✅ green |
| Sep 2026 | 7 | 2 | 4 | 1 | 28.6% | ₹-2,024.50 | ₹4,811.50 | ✅ green |
| Oct 2026 | 9 | 7 | 2 | 0 | 77.8% | ₹13,920.00 | ₹18,731.50 | ✅ green |
| **Jan–Oct total** | **89** | **39** | **47** | **3** | **43.8%** | **₹18,731.50** | — | — |

- **Jan–Oct premium-only total (Bank Nifty alone): ₹18,731.50 per 1 lot**
- Trades/week: **2.19** (89 trades over 203 trading days)
- Full-target %: **43.8%**

## Old mixed basis vs new premium-only basis

| Basis | Jan–Sep | October | Jan–Oct |
|---|---|---|---|
| Old (spot provisional Jan–Sep + premiums Oct, "mixed") | ₹110,495.00 (spot points × 100 shares − ₹40 — not an options profit) | ₹13,920.00 (premiums) | ₹124,415.00 |
| **New (premiums only)** | **₹4,811.50** | **₹13,920.00** | **₹18,731.50** |

The premium-only Jan–Oct total is **₹105,683.50 lower** than the mixed figure. October does not change at all — the entire difference is Jan–Sep, where the spot-provisional unit (spot points × 100 shares) systematically overstated what the option premium actually did: spot moves of +150 to +230 points that scored as ₹15,000–₹23,000 spot "wins" were often only worth a premium stop or a small square-off, because the premium does not move 1:1 with spot and decays while the spot move develops. **16 of the 80 Jan–Sep legs change sign** between the two bases. Biggest disagreements:

- **2026-07-14 PE (Skill V3)**: spot provisional ₹23,410.00 → premium ₹-1,720.00 (premium exit: stop; swing ₹-25,130.00)
- **2026-05-06 PE (Skill V3)**: spot provisional ₹21,370.00 → premium ₹-1,720.00 (premium exit: stop; swing ₹-23,090.00)
- **2026-06-24 PE (V5 v2)**: spot provisional ₹-8,625.00 → premium ₹2,480.00 (premium exit: target; swing ₹11,105.00)
- **2026-04-29 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-1,720.00 (premium exit: stop; swing ₹-10,680.00)
- **2026-06-24 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-1,720.00 (premium exit: stop; swing ₹-10,680.00)
- **2026-07-23 CE (Volrix (b))**: spot provisional ₹8,960.00 → premium ₹-1,720.00 (premium exit: stop; swing ₹-10,680.00)

## Honest verdict — Bank Nifty alone

- Ends positive on premiums alone: **YES — ₹18,731.50 per 1 lot over Jan–Oct 2026.** The system is not a fiction; the premium history is green.
- But it is **far smaller** than the mixed-basis ₹124,415.00 suggested — the mixed figure must not be quoted as this system's premium performance again.
- Every month-end green cumulatively: **NO** — red closes: Jan.
- Worst month: **Jun 2026, ₹-9,560.00**.
- Max drawdown of the cumulative premium curve (trade by trade): **₹28,645.50**.
- Best month: Feb 2026, ₹15,377.00 — **82.1% of the entire Jan–Oct premium total** comes from that single month.
- January closes RED (cumulative −₹1,920.00) — the mixed-basis claim of a green close at every month-end does **not** survive on premiums. February recovers it and every later month-end is green. The drawdown is the story: after peaking at ₹32,497.00 at May month-end, the curve fell for four straight months (Jun–Sep all negative months) before October's +₹13,920.00.
- Nothing was re-tuned in this task. U1-B2 remains a frozen candidate; November 2026 paper (from Mon 2026-11-02, this index's own log) is still the validation step, and it should be judged against these premium-only numbers, not the mixed ones.

Trade-by-trade detail: `historical_proof_bank_B2_trades.csv` (entry/exit premium, exit reason, net per leg; October legs flagged in the note column).
