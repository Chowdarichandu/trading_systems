# TARANG — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 17:58 IST, before any scoring.
**Status at pre-registration:** NOT SCORED — the spec's own data stop-condition (Section 3) triggered on first inspection. See `tarang_2026-11-17.md`. No parameter in this spec has been tuned against any result; no result exists.

**Class:** brand-new indicator-based stocks strategy, in the class of EKAM and TRIO but mechanically distinct from both. Family: **intraday trend-pullback** — trade WITH the day's established trend, buying the pullback dips inside it. (EKAM intraday is a first-bar vote *fade*; TRIO is index options + event/EOD stock setups; SAPTA's ranking approach is dead and is not used here.)

**Basis (labelled everywhere):** equity cash only, PROVISIONAL per 100 shares, ₹40 per completed trade. Paper only, real money ₹0. No stock options (closed surface).

## 1. Universe

The frozen 25 names: ASTRAL, BDL, GLENMARK, GODREJCP, HDFCBANK, HINDALCO, HINDCOPPER, HINDUNILVR, HINDZINC, INDUSTOWER, IRCTC, ITC, KALYANKJIL, NATIONALUM, NHPC, NTPC, OBEROIRLTY, OIL, PFC, RECLTD, TATASTEEL, TVSMOTOR, UNITDSPR, VEDL, WIPRO.

PRIMARY run: all 25 (the frozen universe as it stands; the owner's ≤₹2,000 grandfathering decision is still open — TVSMOTOR at ₹4,495 is the only incumbent above the cap). A labelled sensitivity line — the same book with TVSMOTOR excluded — is reported alongside. TVSMOTOR is never silently dropped.

## 2. Window

Entries 2025-01-01 → 2026-11-13. Report 2025, 2026, and the November 2026 slice separately. Segments/years never pooled into a single verdict.

## 3. Data — AND THE STOP CONDITION

5-minute bars from the programme's stores: `data/sarvaritu_fwd/<SYM>/spot_5m.csv` (the same stores EKAM intraday uses). If a store's bars are insufficient for a name, say so per name rather than substituting data.

**STOP CONDITION (frozen):** intraday VWAP must be session-anchored and cumulative from 09:15 **using bar volume**. If the stores lack volume, STOP and report that VWAP cannot be computed. A price average (typical-price or any other proxy) must NOT be substituted for VWAP.

## 4. Indicators (all causal, computed on completed bars only)

- Intraday VWAP: session-anchored, cumulative from 09:15, Σ(typical price × volume) / Σ(volume) over completed bars of the session.
- EMA-50 on 5-minute closes.
- RSI(7) on 5-minute closes.

## 5. Trend state (per name, per bar, decision-time only)

- UPTREND: close > VWAP **and** close > EMA-50.
- DOWNTREND: close < VWAP **and** close < EMA-50.
- Otherwise: NO TRADE state.

## 6. Entry

- No entries before 09:45 (the trend must establish; this also keeps TARANG out of EKAM's first-bar territory).
- LONG: in UPTREND, when RSI(7) has dipped to ≤35 on a completed bar (the pullback) and a later completed bar's RSI(7) crosses back above 35 while the trend state is still UPTREND → enter LONG at the next bar's open.
- SHORT: mirror in DOWNTREND — RSI(7) rallies to ≥65 on a completed bar, then a later completed bar's RSI(7) crosses back below 65 while still DOWNTREND → enter SHORT at the next bar's open.
- A fresh dip/rally is required for each entry — no repeated entries off one pullback.

## 7. Exits (first hit wins)

- Target +0.8% from entry / stop −0.5% from entry, evaluated on completed bars. If a single bar's range spans both target and stop, the conservative order applies: **stop first**.
- Square-off at the 15:15 bar close if neither is hit.
- Net per trade = (exit − entry) × 100 shares (sign by side) − ₹40.

## 8. Caps

- One open position per name at a time.
- Max 2 entries per name per day.
- Max 10 entries per day across the book; if more signals fire on the same bar, take them deepest-pullback first (largest RSI excursion beyond the threshold).
- Re-entry after an exit is allowed (owner's stocks rule).

## 9. Controls gate (same run, before any verdict)

Per `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`:

1. **Timing/leak audit:** VWAP/EMA/RSI use only completed bars up to the signal bar; entries fill at the NEXT bar's open. Audited programmatically over every trade; violations must be 0.
2. **Placebos (200 seeded draws):** (a) random entries — same names, same days, same number of entries per day, random eligible bars (09:45–14:45), same exit geometry; (b) direction-flip — TARANG's exact entries with the side flipped (information only).
3. **Splits and stress:** first-half/second-half per year; full month table; ex-top-3 per year; independent re-sum of headline nets from the trades CSV.
4. **Ablations (information, not gate legs):** pullback-only (trend filter removed); trend-only (pullback removed, trend-break entries).

## 10. Pass bar (pre-registered, frozen)

TARANG PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats the random-entry placebo 90th percentile in **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations);
- November 2026 slice not worse than −₹3,000.

Monthly pace per year vs the ₹15,000/month stocks floor is reported as information. If NO PASS, the report must diagnose the failure cause from the trades (trend-state distribution, pullback depth, exit geometry, time-of-day, side) as the input to a possible Round 2 — which is a separate, separately-authorised run.
