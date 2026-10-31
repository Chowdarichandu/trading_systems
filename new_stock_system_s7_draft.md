# S7 — Intraday STOCK system (cash, NOT options) — DRAFT, not frozen, not scored

**Status: DRAFT 2026-10-29, NOT frozen, NOT adopted, NOT a live system. Paper only, no orders.**
**Source:** the S7 design sketch in §5 of `new_stock_system_s6.md` (2026-10-29), written
after S6 was scored and found worse than S2. This draft turns that sketch into a
freezable spec. Nothing here has been scored on Jan–Oct 2026, and no S7 result
is claimed. If this draft is approved (with the two questions in §3 answered),
it becomes the frozen S7 spec and only then is it scored in-sample; if it passes
in-sample, its real test is November 2026 paper, with no re-tuning during November.

## Why S7 exists — what S6 proved

- S6 fixed the stop asymmetry in presence, not in profit: CE trades went from
  0 in S2 to 7 capped in S6, but the CE leg lost ₹2,980 with 0 full targets.
- The remaining layer is reclaim-chasing: entering at the open after a reclaim
  confirmation starts at the top of the reclaim move with almost no pullback
  room, so any normal pullback stops it out (5 of 8 CE candidates stopped).
- S7 therefore changes the CE entry, not another filter. Loosening room has
  already failed in S2–S6 in every direction tried and is not reused here.

## S7 rules — S6 carried over, one change

Everything from S6 (`new_stock_system_s6_frozen.md`) is unchanged except the
setup4 CE entry below: same 25 stocks, setups 2/3/4 only, OR width 0.25–3.0%
of previous close, second-close confirmation for non-CE trades, target entry
± 2 × risk, give-back exit (50 shares at 1 × risk, rest trailed to breakeven),
square-off 15:10, room to the next PD level finite AND ≥ 1.5 × risk (target
NOT shrunk to room), Nifty bias-only confirmation (bearish <35%, neutral
35–79%, bullish ≥80%; block only the directly opposed direction), prospective
full-target net (2 × risk × 100 − ₹40) ≥ ₹500, cap max 1 stock trade per
trading day and max 1 trade per stock per week (a ceiling, not a quota —
no-valuable-setup days trade nothing), 100 shares, ₹40/trade, cash intraday
only, Nifty as filter only and never pooled into a stock total.

**THE S7 CHANGE — setup4 CE only via a pullback entry (sketch, verbatim):**
(i) a setup4 reclaim close (as in `find_signal`) marks the day as
reclaim-armed; (ii) the entry triggers only on a later candle that dips
toward the reclaimed level (OR high, within the existing 40 × scale tolerance
used for setup4 pullback) and then closes back above it, with the second-close
rule applied to that pullback candle; (iii) entry = open of the next candle;
stop = pullback candle low; room = distance from entry to the next PD level
above, ≥ 1.5 × pullback risk; target = entry + 2 × risk; give-back exit
unchanged.

**PE trades in S7 keep the S6 retest-hold stop** (CE: min of signal and
confirmation lows; PE: max of signal and confirmation highs), since the S6 PE
leg was near breakeven (46 trades, −₹867.50, 9 full targets) and was not the
damaged leg. Setup2 remains a separate open problem: if setup2 still yields
zero candidates under S7, it is reported as absent rather than rescued by
loosening room.

## Questions that must be answered before this draft is frozen

1. **Pullback level — OR high or PDC/PDL?** The S7 sketch says the dip is
   toward the reclaimed level (OR high). The existing `find_signal`
   setup4_pullback instead dips to PDC/PDL within 40 × scale. These are not
   the same level. Freezing must pick one verbatim; this draft does not pick.
2. **Second-close on the pullback candle — what exactly?** S6 confirmation
   means the candle after the signal closes further in direction than the
   signal close. For a pullback entry, the candidate reading is: the candle
   after the pullback candle must close above the pullback candle's close
   before entry at the next open. If that reading differs from the intended
   rule, it replaces it verbatim before freezing.

## Judging legs (same bar as S6, plus the user's daily bar)

Judged on Jan–Oct 2026 in-sample only, then — only if it passes — on
November paper from Mon 2026-11-02, logged daily after 15:10, separate from
the Nifty Cluster 2/3 log, with no re-tuning during November:
- Net positive (S2 best kept is −₹785.98; S6 is −₹3,847.50)
- Close to 1 valuable stock trade per trading day, with no forced trade on a
  no-setup day (S6: 0.26/day; S2: 0.30/day on the old weekly framing)
- CE AND setup2/4 present (S6: CE present, setup2 absent, pullback 0)
- Full-target rate above S2 (19.7%) and S1 (22.2%) — partial-breakeven wins
  shown separately, never counted as targets
- Cumulative profit rising month by month, not carried by one month
  (ex-March and ex-October checks, as in S6)

Even a pass in-sample is NOT adoption. Adoption needs net + win rate +
frequency together on unseen November paper.

## November consequence if this draft is not frozen

No November adoption-track stock log is created from S7, and S6 must not be
logged in its place. The only existing stock template remains the
diagnostic-only `s2_forward_paper_log.csv` (S2, best kept, itself not adopted).
