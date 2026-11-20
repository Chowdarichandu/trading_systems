# SAPTA Round 2 — Frozen Spec (pre-registered BEFORE scoring)

**Frozen at:** 2026-11-17 IST, before any SAPTA2 number was computed.
**Status:** Research only. Nothing is armed, no paper run is started, no live book changes.
**Money basis (labelled everywhere):** equity cash, PROVISIONAL per 100 shares, ₹40 per completed trade. Paper only, real money ₹0. Equity cash ONLY — no stock options in any form.

## What Round 2 is

One mechanically different retest of the SAPTA concept (7 sectoral indices × top-performing stocks; a separate entity — not EKAM, not TRIO, not the Stock Book). Round 1 (spec `sapta_SPEC.md`, report `sapta_2026-11-17.md`) FAILED both sizes: SAPTA-14 2025 −₹88,404 / 2026 +₹1,12,117; SAPTA-21 2025 −₹40,645 / 2026 +₹1,57,893. Diagnosed causes: (1) whipsaw — breakouts taken while the name's own sector index was falling (Apr 2025 −₹50,433 / −₹90,068); (2) ranking weak — random selection from SAPTA's own eligible pools beat the top-performer ranking in 2026 (SAPTA at 77.5th / 81.5th percentile); (3) 2026 profit mostly unrealised marks; DD −₹1,76,660 / −₹2,13,263.

Round 2 changes **EXACTLY two mechanics** vs Round 1 and nothing else. Everything else is identical to Round 1: same 7 indices (Nifty Bank, Nifty IT, Nifty Pharma, Nifty Auto, Nifty Metal, Nifty FMCG, Nifty Realty), same saved current constituent lists (`sapta_constituents/`, fetched 2026-11-17 for Round 1 — reused, not refetched), same ≤₹2,000 owner cap and ₹5-crore median-60-day traded-value liquidity floor at selection, same trailing-126-trading-day ranking metric computed only from closes strictly before the ranking day, same Donchian entry (close > prior 20-day highest close → buy next open) and exit (close < prior 10-day lowest close → sell next open), same one-position-per-name, same max-10-concurrent cap with rank-order fills and skipped-not-queued entries, same re-rank-drop exit at the ranking day's open, same window (entries 2025-01-01 → 2026-11-13), same ₹40/trade cost, same end-of-window marking of open positions at the 2026-11-13 close, same month/half attribution.

## The two changes

### Change 1 — MONTHLY re-rank (was quarterly)
Re-rank on the first trading day of **each month** (master calendar = HDFCBANK sessions in the universe dump), Jan 2025 through Nov 2026 → 23 ranking days. Ranking metric, constraints and pick sizes unchanged (top 2 = SAPTA2-14, top 3 = SAPTA2-21).

### Change 2 — PARENT-INDEX TREND GATE on entries
A name may ENTER only if, at the signal close, its parent sector index's own close is above that index's trailing 100-day simple moving average (SMA computed on the index's daily closes including the signal day; at least 100 index closes through the signal day required, else the gate is closed).

- **Parent index** = the index (or indices) whose current monthly selection contains the name. If a name is selected through more than one of the 7 indices, the gate passes if **any** selecting index is above its 100-day average.
- **Entries only.** A held position is NOT force-exited by the gate; exits remain the 10-day-low rule and the re-rank-drop rule.
- The gate is evaluated with decision-time data only: the signal fires at day d's close, the index close and its SMA through day d are known at that moment, and the fill is at day d+1's open.

### Index series — PROXY (disclosed)
Actual index levels could not be sourced in this run: the niftyindices.com historical-data request was not performed (an approval for the outbound fetch was not answered), and the Yahoo Finance chart route is blocked by policy. Per the pre-agreed fallback, each index's daily series is a **PROXY**: the **equal-weighted average of that index's current constituents' closes** on each master-calendar day (constituents with a bar that day; the proxy is defined on HDFCBANK session days from 2024-01-01 so the 100-day average exists before the window opens). The same current-constituent lists are used, so the proxy carries the same survivorship caveat as Round 1 — disclosed, and partially controlled by the random-selection placebo, which uses the identical proxy gate. **Every gate reference in the report is to this PROXY series, never to the official index level.**

## Placebos under Round 2 mechanics (fairness)
Both placebos are rebuilt under the SAME two changes (200 seeded draws each, seed base 20261117, same as Round 1):
- **(a) Random entries:** same monthly selections; each real trade's entry shifted by a random offset of ±10…±120 trading days; a shifted entry is accepted only on a day when the name is inside its selected periods **and the trend gate is open for that name on the shifted signal day** (same parent rule as the real book); exit rule re-applied from the shifted entry (exits are NOT gated); one-position-per-name and the 10-cap enforced chronologically, shortfall reported.
- **(b) Random selection:** per **month** per index, randomly draw the same number of names from the same constraint-eligible pool; identical strategy **including the trend gate**.

## Controls gate (identical bar to Round 1, same run, before any verdict)
1. **Timing/leak audit (programmatic, every trade):** entry fill = first bar strictly after the signal close; ranking inputs strictly before the ranking day; gate inputs (index proxy closes through the signal day) recomputed independently per trade; exit fills likewise; re-rank exits at the ranking day's open with inputs through R−1. Violation count must be 0.
2. **Placebos:** SAPTA2's net must beat the **90th percentile of BOTH placebos, in BOTH years** (placebo nets computed per entry-year).
3. **Halves split** per year; **full month table**; **ex-top-3 stress** per size per year.
4. **Independent re-sum** of headline nets from the trades CSV by a separate pass; must match to the paisa.

## PASS BAR (pre-registered, per size — do not move after seeing results)
A size PASSES only if ALL hold:
- Net positive in BOTH 2025 and 2026.
- Beats both placebos' 90th percentile in both years.
- Ex-top-3 net positive in both years.
- No single month worse than −₹15,000.
- Timing audit clean (0 violations).

## Round-2-specific report lines (required)
- **Closed-trades-only net per size per year** (trades with a real exit, END_MARK open positions excluded) — Round 1's 2026 profit was mostly open marks; show whether Round 2's is real.
- **Apr 2025 month figure** per size (exit-month attribution, same as Round 1's month table) vs Round 1's −₹50,433 (SAPTA-14) / −₹90,068 (SAPTA-21) — did the trend gate fix the whipsaw month?

## PRE-REGISTERED KILL CONDITION (written before scoring)
If Round 2 also fails the **random-selection placebo** (does not beat its 90th percentile) in **either year**, the conclusion is that top-performer RANKING on these pools carries no edge — **the SAPTA ranking surface is then measured dead**, and that is the final verdict on the concept. (The eligible pool itself may still be noted as an observation, not a strategy.) A failed size is never retested identically; no parameter is tuned after seeing results.

## Known limitation (carried from Round 1, stated prominently)
Current (Nov 2026) constituent lists applied to a 2025–2026 backtest carry constituent look-ahead / survivorship bias, which **flatters** absolute nets. The random-selection placebo shares the same lists, the same constraints and the same proxy gate, so the SAPTA2-vs-placebo comparison is fair even though absolute nets are flattered.
