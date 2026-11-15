# Volrix — October 2026, clean standalone run (paper only, real money ₹0)

**Scope:** Volrix only, index OPTIONS only, Nifty and Bank Nifty reported separately, never pooled. 1 lot (Nifty 65 / Bank 30), cost ₹220/trade inside every net. Frozen definitions per `index_options_volrix_tuned_oct30.md` and the `volrix/` / `volrix_banknifty/` / `volrix_options/` / `volrix_banknifty_options/` files — nothing re-tuned.

**Data & method:** daily spot closes from `volrix/nifty_daily_2019_2026.csv` and `volrix_banknifty/banknifty_daily_2019_2026.csv` (extended through Nov 3). Trigger state is a CONTINUOUS run (cooldown/hold carried in from September, per the Oct 30 report's continuity rule — not an October-isolated fresh start). The continuous machine used here reproduces the Oct 30 report's published Jan–Oct entry lists exactly on both indices at −1.0% (Nifty 12 entries, Bank 13), which validates the state handling. Premium scoring from the stored 5-min expired-contract candles in `v4_options_oct_data/` (fetched 2026-10-30); entry premium = open of the 09:20 bar; square-off bar = 15:10 close (the frozen October premium convention). The original code's skip-after-expiry-change quirk has nil October effect (no trigger falls on the 1 Oct or 29 Oct skip entry-days) — same finding as the Oct 30 report. No leg lacked premium bars; there are **no NOT_COMPUTED legs** in this run.

**October trigger scan (prev-day close):** Nifty ≤ −1.0% on **8 Oct (−1.64%)** and **19 Oct (−1.11%)**; Bank Nifty ≤ −1.0% on **23 Oct (−1.16%)** only. Nothing in October reaches −2.00% on either index (worst: Nifty −1.64%, Bank −1.16%). The 19 Oct Nifty trigger does **not** become a trade at −1.0%: the 10-session cooldown from the 9 Oct entry blocks it (cooldown runs to 26 Oct).

---

## (a) ORIGINAL rebound — frozen options translation

Definition: prev-day ≤ −2.00% → buy ATM call next session 09:16 (premium entry = 09:20 bar open), monthly expiry 0, 1 lot, no stop/target, 5-session hold, 10-session cooldown, expiry-skip quirk.

**Nifty — 0 October entries, 0 carried in. Total ₹0.**
**Bank Nifty — 0 October entries, 0 carried in. Total ₹0.**

No October day closes ≤ −2.00% on either index, and no earlier position is open into October: the last original-rebound entries on both indices were **2026-07-09** (trigger 2026-07-08), exited 2026-07-15 on the 5th session — confirmed in `volrix/positions_daily.json`, `volrix_banknifty/positions_daily.json` and the frozen options translations `volrix_options/options_trades.json` (30 lifetime positions) and `volrix_banknifty_options/options_trades.json` (48 lifetime positions), none dated after July 2026.

## (b) Intraday variant at −1.0%

Definition: prev-day ≤ −1.0% → entry next session (09:20 bar open), ATM call nearest 100 to the trigger-day close, monthly expiry 27 Oct 2026, stop −50 / target +90 checked on every 5-min bar including the entry bar (stop before target within a bar), square-off 15:10, 10-session cooldown.

### Nifty — 1 trade, +₹5,630.00

| Trigger | Entry | Contract | Entry premium | Exit | Exit reason | Net ₹ |
|---|---|---|---|---|---|---|
| Thu 8 Oct (−1.64%) | Fri 9 Oct 09:20 | 22200 CE / 27 Oct | 398.00 | 9 Oct 09:45 @ 488.00 | target (+90) | **+5,630.00** |

(90.00 × 65 − 220 = 5,630.00. The day low from entry, 386.85, never approached the 348.00 stop before the target bar.)

### Bank Nifty — 1 trade, +₹2,480.00

| Trigger | Entry | Contract | Entry premium | Exit | Exit reason | Net ₹ |
|---|---|---|---|---|---|---|
| Fri 23 Oct (−1.16%) | Mon 26 Oct 09:20 | 54300 CE / 27 Oct | 238.55 | 26 Oct 09:55 @ 328.55 | target (+90) | **+2,480.00** |

(90.00 × 30 − 220 = 2,480.00. The contract's day low of 171.95 falls below the 188.55 stop level only *after* the 09:55 target exit, so it does not change the result.)

## (c) 5-session hold at −1.0% (the Oct 30 report's variant (a) at −1.0%)

Definition: as (b) for trigger/cooldown/entry, but NO stop and NO target; hold 5 sessions (entry day = session 1), exit at the 15:10 close of the 5th session — except that a monthly expiry falling inside the hold ends the trade at that day's 15:10 close, no roll.

### Nifty — 1 trade, +₹25,695.50

| Trigger | Entry | Contract | Entry premium | Exit | Exit reason | Net ₹ |
|---|---|---|---|---|---|---|
| Thu 8 Oct (−1.64%) | Fri 9 Oct 09:20 | 22200 CE / 27 Oct | 398.00 | Thu 15 Oct 15:10 @ 796.70 | 5th-session square-off | **+25,695.50** |

(398.70 × 65 − 220 = 25,695.50. Sessions: 9, 12, 13, 14, 15 Oct.)

### Bank Nifty — 1 trade, −₹6,953.50

| Trigger | Entry | Contract | Entry premium | Exit | Exit reason | Net ₹ |
|---|---|---|---|---|---|---|
| Fri 23 Oct (−1.16%) | Mon 26 Oct 09:20 | 54300 CE / 27 Oct | 238.55 | Tue 27 Oct 15:10 @ 14.10 | monthly-expiry exit (session 2, no roll) | **−6,953.50** |

(−224.45 × 30 − 220 = −6,953.50. The 27 Oct monthly expiry falls inside the hold, so the trade ends there — spot closed 27 Oct at 53,974.90, below the 54300 strike, and the expiry-day premium collapsed.)

---

## Reconciliation against the Oct 30 recorded figures

| Recorded (Oct 30) | This run | Verdict |
|---|---|---|
| (a) original: 0 October trades, both indices | 0 entries, 0 carried in, ₹0 / ₹0 | **Reproduced exactly** |
| (b) Nifty: 1 trade, +₹5,630 | 1 trade, +₹5,630.00 | **Reproduced exactly** |
| (b) Bank: 1 trade, +₹2,480 | 1 trade, +₹2,480.00 | **Reproduced exactly** |
| (c) [Oct-30 (a) @ −1.0%] Nifty: +₹25,695.50 | +₹25,695.50 | **Reproduced exactly** |
| (c) [Oct-30 (a) @ −1.0%] Bank: −₹6,953.50 | −₹6,953.50 | **Reproduced exactly** |

No differences to reconcile: every recorded figure is reproduced from the stored daily closes and premium candles under the frozen definitions. October totals by variant — (a) ₹0 / ₹0 · (b) Nifty +₹5,630.00, Bank +₹2,480.00 · (c) Nifty +₹25,695.50, Bank −₹6,953.50 (indices never pooled). One trade per index in (b) and (c) — an occasional overlay's evidence, not a daily system.
