# Index OPTIONS — October FINAL Outcome (1–28 October 2026)

**Paper only. No live order was placed. Real money made in October = ₹0 (no live trades were placed).**

All figures below are paper simulation, 1 lot per trade, after an assumed cost of ₹220 per trade.
Premium rule (uniform V4-overlay, as in the premium-completion file): entry premium = open of the first
5-minute option candle after the spot signal; stop = entry − 50 option points; target = entry + 90 option
points, for both CE and PE; stop checked before target on every bar including the entry bar;
square-off at 15:10. Lot: Bank Nifty 30, Nifty 65. Strike: ATM nearest 100 to entry spot.
Expiry: monthly 27 October 2026 for all trades below (all are dated 1–26 October).

Source: `index_options_premium_october_trades.csv` — taken directly, no spot points converted into premiums,
no other versions' trades added.

## Final totals — the two best October tracks only

| Track | Final version kept | Trades | Targets | Stops | Square-offs | Full-target | Frequency / week | **Paper net, 1 lot** |
|---|---|---|---|---|---|---|---|---|
| Bank Nifty | V5-v2 (base, capped) | 4 | 4 | 0 | 0 | 100% | 1.11 | **+₹9,920.00** |
| Nifty | (lA) v2 (L1) (base) | 3 | 1 | 0 | 2 | 33.3% | 0.83 | **+₹6,678.50** |
| **Two best tracks together** (labelled only — two separate systems, not one portfolio P&L) | — | 7 | 5 | 0 | 2 | — | — | **+₹16,598.50 paper, 1 lot each, NOT real money** |

## Final tune — one small frozen pass per track, October only

- **Bank V5-v2, no-cap vs 1/week cap — considered from existing evidence, NOT kept as the final version.**
  On spot, no-cap Bank was 5 trades / +₹67,690 vs capped 4 / +₹43,630, because the cap drops the
  23 October winner. On premiums that dropped trade would add one more +₹2,480 target (+₹12,400 total),
  but frequency would still be only 1.39/week — nowhere near 5/week — and it would break the frozen
  V5 definition that was validated across both indices (the same cap helps Nifty). Discarded as a final
  change; base capped V5 kept.
- **Bank V5-v2, stop 1.25× — NOT applied.** That sensitivity was flagged for (lA) Bank only
  (a single-day 8 October flip), not for V5 Bank. Applying it here would be mixing tracks.
- **Nifty (lA) v2, 1-minute fragility check on 8 October only — warning kept, grid NOT switched.**
  On the 1-minute replay the 8 October (lA) Nifty spot target collapses to a stop, and on premiums
  the same trade never came near its +90 target (premium rose only +40.05, from 247.05 to 287.10,
  and squared off). The 5-minute base trade is kept as scored, but the 8 October result is fragile —
  it depends on the wider 5-minute stop, not on a premium target being reached. The 1-minute grid
  itself was already discarded in Family D; it is not adopted here.
- **Room was not loosened below 1.5×, no forced trades were added, no other tune was run.**
  Neither track improves net AND full-target AND frequency together under any tune tried, so
  **base is kept for both tracks.** Neither track passes all three legs (see Closed section).

## Bank Nifty — V5-v2, final trades (1 lot = 30)

| Date | Setup | Direction | Strike | Expiry | Signal | Entry time | Entry premium | Stop premium | Target premium | Exit time | Exit premium | Exit reason | Net / 1 lot | Running total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Thu 2026-10-01 | setup4 reclaim | CE | 54900 | 2026-10-27 | 09:55 | 10:00 | 999.15 | 949.15 | 1089.15 | 10:30 | 1089.15 | target | +₹2,480.00 | +₹2,480.00 |
| Tue 2026-10-13 | setup3 bounce rejection | PE | 55200 | 2026-10-27 | 10:35 | 10:40 | 547.35 | 497.35 | 637.35 | 11:45 | 637.35 | target | +₹2,480.00 | +₹4,960.00 |
| Wed 2026-10-21 | setup2 OR breakdown | PE | 55200 | 2026-10-27 | 11:15 | 11:20 | 379.95 | 329.95 | 469.95 | 11:35 | 469.95 | target | +₹2,480.00 | +₹7,440.00 |
| Mon 2026-10-26 | setup3 bounce rejection | PE | 54300 | 2026-10-27 | 10:15 | 10:20 | 275.15 | 225.15 | 365.15 | 10:35 | 365.15 | target | +₹2,480.00 | **+₹9,920.00** |

Bank V5-v2 no-trade days (18 trading days in window, 4 traded): 2026-10-05, 2026-10-06,
2026-10-07, 2026-10-08, 2026-10-09, 2026-10-12, 2026-10-14, 2026-10-15, 2026-10-16,
2026-10-19, 2026-10-22, 2026-10-23, 2026-10-27, 2026-10-28.

## Nifty — (lA) v2 (L1), final trades (1 lot = 65)

| Date | Setup | Direction | Strike | Expiry | Signal | Entry time | Entry premium | Stop premium | Target premium | Exit time | Exit premium | Exit reason | Net / 1 lot | Running total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Thu 2026-10-08 | (lA) PE rescan re-entry (L1) | PE | 22300 | 2026-10-27 | 11:25 | 11:30 | 247.05 | 197.05 | 337.05 | 15:10 | 287.10 | square-off 15:10 | +₹2,383.25 | +₹2,383.25 |
| Wed 2026-10-21 | (lA) PE rescan re-entry (L1) | PE | 22800 | 2026-10-27 | 11:35 | 11:40 | 151.30 | 101.30 | 241.30 | 14:45 | 241.30 | target | +₹5,630.00 | +₹8,013.25 |
| Fri 2026-10-23 | (lA) PE rescan re-entry (L1) | PE | 22500 | 2026-10-27 | 10:05 | 10:10 | 125.85 | 75.85 | 215.85 | 15:10 | 108.70 | square-off 15:10 | −₹1,334.75 | **+₹6,678.50** |

Note on 2026-10-23 Nifty: on spot this was a target, on premium it was not — the premium
never reached target 215.85 and never touched stop 75.85, so it squared off at a loss.
That is why premium numbers, not spot numbers, are the final October record.

Nifty (lA) v2 no-trade days (18 trading days in window, 3 traded): 2026-10-01, 2026-10-05,
2026-10-06, 2026-10-07, 2026-10-09, 2026-10-12, 2026-10-13, 2026-10-14, 2026-10-15,
2026-10-16, 2026-10-19, 2026-10-22, 2026-10-26, 2026-10-27, 2026-10-28.

## Scope — what "October" means here

October = 1–28 October 2026, 18 trading days (2 October and 20 October are market holidays
and are not trading days). 29 and 30 October are NOT in this outcome: 29 October has no
complete 5-minute cache (Bank intraday file only, Nifty daily OHLC only) and 30 October
had not closed when the October files were scored. Any 29–30 October result must be a
separate, later addition, never backfilled into these numbers.

## Closed

- **October is closed.** The two best October tracks, final and unchanged from base, are:
  Bank V5-v2 +₹9,920.00 (4 trades, 100% targets, 1.11/week) and Nifty (lA) v2 +₹6,678.50
  (3 trades, 33.3% full-target, 0.83/week); together +₹16,598.50 paper, 1 lot each, NOT real money.
- **Nothing is adopted on October alone.** Neither track passes all three legs together
  (net > 0 AND full-target ≥ 50% AND frequency ≥ 5/week): Bank passes net and full-target
  but fails frequency; Nifty passes net only.
- **Next step (not started in this task):** November paper from Monday 2026-11-02, with
  separate Nifty and Bank logs, no re-tuning during November — or stocks, if the user says so.
  No November work and no stocks work were started here.
