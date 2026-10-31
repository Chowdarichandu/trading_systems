# U1 — Unified-1 — FROZEN before scoring (2026-10-30)

Paper only. No orders. No stocks. Index OPTIONS only; spot is trigger/levels
only, never the traded instrument for index work in the premium leg.
Real money made = ₹0 — no live trades were placed.
Nothing is adopted on this run alone; adoption still needs frozen November
2026 paper from Monday 2026-11-02, separate Nifty/Bank logs, no re-tuning
during November.

## Name and definition

**U1 — Unified-1**: a SINGLE unified index OPTIONS system, not four systems
added together.

- **Components pooled, then deduplicated:** (lA) v2 (L1) + V5 v2 + Tuned
  Skill V3 (CE no-block) + Volrix tuned intraday (b) at −1.0%.
  - (lA) v2 (L1): (lA) rescan re-entry, PE only, rescan cutoff extended
    11:30 → 13:30 only where the confirming index broke before 11:30.
    See `index_options_v2_frozen.md`.
  - V5 v2: pooled V4 + Skill index candidates, dedup by setup rank,
    prospective ≥ ₹500 (provisional cash unit in its own definition).
    See `index_options_v2_frozen.md`.
  - Tuned Skill V3 (CE no-block): Day Trader Skill OR signal, S1 rules,
    with the CE bearish-bias block REMOVED; the 09:30-PE rule (PE taken
    only if its close < PDL) unchanged.
    See `index_options_skill_tuned_oct30_frozen.md`.
  - Volrix tuned intraday (b) at −1.0%: prev-day close ≤ −1.0% → next
    session LONG ATM CALL, 1 lot, same-day exit, stop −50 / target +90
    premium points, square-off 15:10, 10-session cooldown kept.
    See `index_options_volrix_tuned_oct30.md` §1(b).
  - NOT included: Skill V9 pullback, NS1 second legs, NS2 afternoon legs,
    Volrix (a) 5-session hold, Volrix (c)/(c-raw) confirmation, Skill V3's
    Bank 28 Oct CE leg (NOT_COMPUTED, Bank Nov-03 chain gap).
- **Counting: UNIQUE-ONCE only.** Key = (date, index, direction CE/PE).
  Each key counted ONCE, at the EARLIEST entry time among the systems on
  that key. Later signals on the same key are overlaps, not extra trades.
  NO double-counting (the literal sum of system legs is not a U1 total)
  and NO exclusive-deletion (a key signalled by 2+ systems is still one
  trade, not deleted).
- **Window:** 1 January – 28 October 2026. October = 1–28 Oct only;
  29–30 Oct are NOT in any number here. Trading days: 203
  (Jan 20, Feb 21, Mar 19, Apr 20, May 19, Jun 21, Jul 23, Aug 21,
  Sep 21, Oct 18).
- **October scoring (premium, already computed):** entry = open of first
  5-min option candle after the spot signal; stop = entry − 50,
  target = entry + 90 option points, both CE and PE; stop before target
  per bar including the entry bar; square-off 15:10; net per 1 lot =
  (exit − entry) × lot − ₹220 assumed cost; lot Nifty 65 / Bank 30.
  October check to reproduce exactly: Nifty 16 trades +₹14,169.75,
  Bank 18 trades +₹11,040.00, combined +₹25,209.75.
- **Jan–Sep scoring (spot provisional, labelled per leg):** option
  premiums for ~300 Jan–Sep contract-days were NOT fetched in this run
  (volume; see report §1). Each Jan–Sep leg is therefore scored on spot
  provisional rules of its own source engine and labelled
  `spot_provisional` in the trades CSV: net = spot points × 100 shares
  − ₹40 assumed cost. That is NOT an options-lot profit and NOT a
  futures profit. Jan–Sep subtotals, October premium subtotals, and the
  mixed combined total are reported SEPARATELY; the mixed total is
  labelled "mixed (spot Jan–Sep + premium Oct)" and is never presented
  as a pure premium total.
- **Full-target %** = share of trades exiting at target only
  (premium +90 in October; 2× risk in spot-provisional legs, except
  Volrix (b) spot legs which use the +90/−50 spot translation stated
  in the report). Square-off greens are NOT full targets.
- **Frequency** = trades ÷ trading days × 5, per index separately.
- **Verdict rule:** per index separately, never pooled in the verdict.
  Cumulative progression = month-by-month cumulative net, checked for
  profit rising month by month, not just a positive final total.
