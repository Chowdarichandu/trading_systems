# BTST PROGRAMME — Buy Today, Sell Tomorrow (2026-11-13)

Owner order 2026-11-13 05:35 IST ("work on BTSD — buy today sell tomorrow trades"). Two arms, built, gated and reported **separately, never pooled**. Paper only, real money ₹0. December candidates only; November frozen books untouched. **Bars were frozen before scoring and were not moved.**

## VERDICTS

| Arm | Variant | Jan–Oct 2026 (gated) | Gate | November lens (Nov 2–12) |
|---|---|---|---|---|
| **1 — Bank Nifty options** | V1 full-day-move sign (PRIMARY) | **−₹6,436.00** · 190 trips · WR 43.2% | **FAIL** (4 of 7 legs) | **+₹38,732.50** · 5 trips — lens PASS, not promotable (see §4) |
| **1 — Bank Nifty options** | V2 stack day-direction | **−₹6,317.50** · 88 trips · WR 44.3% | **FAIL** (5 of 7 legs) | **−₹22,218.50** · 2 trips — lens FAIL |
| **2 — Stocks (25 watchlist)** | Strength rule | **−₹289,328.00** · 613 trades · WR 35.4% | **FAIL** (all 5 numeric legs) | **−₹10,297.00** · 35 trades — lens FAIL |

**No BTST book passes. No December candidate arises from this programme.** The one bright cell — Arm 1 V1's November — is 5 trips, two of them gap jackpots, from a variant whose 190-trip gated record is negative with a negative second half. Under the standing rule (gate first, November as lens, bars never moved), it is recorded, not promoted.

---

## 1. FROZEN SPEC (registered before scoring)

**Common:** entry days Jan 1–Oct 29, 2026 (exit day ≤ Oct 30). Trading calendar = full sessions only (≥70 spot bars — this excludes the 14-bar mock session on Sun 2026-11-08 in the November store).

**ARM 1 — Bank Nifty options BTST** (lot 30; **₹220 once per round trip**):
- Decision at 15:15 on day D from Bank spot bars with start ≤ 15:10 only. Contract: monthly expiry in force for an overnight hold = first monthly expiry **strictly after** D (on expiry day the expiring contract cannot be held overnight → next monthly). Strike = nearest 100 to the 15:10 bar close (exact-50 remainder rounds down). Entry fill = close of the **15:15 premium bar**.
- **V1 (PRIMARY) direction — full-day move sign:** spot close(15:10) vs open(09:15): up → buy CE, down → buy PE; |move| < 0.05% → no trade (13 flat-skips in the window).
- **V2 direction — stack day-direction:** side of TUNED STACK v2's first leg that day (gated leg record Jan–Oct; November shadow log for the lens); no stack leg → no trade (89 stack days in the window).
- **Exit (primary EXIT-TS):** next trading day, premium bar closes, bars starting 09:15…10:25: first close ≥ entry+60 → TARGET; first close ≤ entry−40 → STOP; else close of the 10:25 bar (HARD 10:30). Lens EXIT-0920 = exit at the 09:20 bar close.
- Placebos per variant: **P-REV** (opposite side, same day/strike) and **P-RANDDIR** (seeded coin-flip side, seed 20261113).

**ARM 2 — Stocks BTST** (frozen 25 watchlist; provisional per-100-shares; ₹40/trade):
- Signal at day close (fill at the close of the 15:25 bar — the workspace EOD convention): qualifies if **day gain vs previous close ≥ +1.00% AND CS% = (C−L)/(H−L)×100 ≥ 75**. Rank by gain desc (tie → alphabetical), **top 5/day**.
- **Exit (primary EXIT-TS):** next day, closes of bars starting 09:15…10:25: first close ≥ entry×1.010 → TARGET; first close ≤ entry×0.993 → STOP; else 10:25 bar close. Lens EXIT-OPEN = close of the 09:15 bar (the task's open-print proxy).
- Placebos: **P-REV-MIRROR** (gain ≤ −1.00% AND CS% ≤ 25, ranked most-negative first, top 5, bought long, same exits — tests whether *strength selection* specifically carries anything) and **P-RANDSEL** (same per-day pick count as the real book, seeded random watchlist names, same exits).

**PASS bars (per arm/variant, ALL must hold):** G1 total > 0 · G2 H1 (Jan–May entries) > 0 AND H2 (Jun–Oct) > 0 · G3 red months ≤ 3 of 10 · G4 ex-top-3 > 0 · G5 total beats both placebos · G6 timing/leak audit clean · G7 NC share ≤ 10% of eligible. **Owner's lens (separate):** November counterfactual total > 0.

## 2. PRECEDENT CHECK (mandatory) — the dead afternoon-strength pattern

The dead pattern (pattern_engine_afternoon_strength_2026-11-11, verdict **NOT SUPPORTED**): *afternoon strength on index spot — CS% buckets, post-13:00 run buckets, and their combo — predicts a next-day gap-up in spot.* It died on the controls: Bank COMBO mean gap **+0.752% (H1 2026) → −0.141% (H2 2026) → −0.061% (2025)**; gap-up rate barely above base; the next day typically **faded** the gap (plain CS≥80 → next close up only 40.4% for Bank, below base).

How each construction here relates — stated precisely:

- **A CS%-keyed Arm-1 variant was EXCLUDED before scoring.** CS% is the dead pattern's own core measure (and its plain form leaned *reversal*); wrapping it in an option would still be the dead pattern's signal. The precedent check stops that variant, as instructed.
- **V1 differs in construction:** (i) conditioning window is the **full day** (open→15:10), not the afternoon segment the dead study isolated; (ii) the traded quantity is **option premium** (gap + IV + theta), not the spot gap; (iii) the exit is a **target/stop morning rule**, not a gap print or open→close hold. **Adjacency admitted honestly:** it remains a "today's direction continues overnight" claim — which is why the halves test and the reversed placebo were made gate legs. The outcome rhymes with the dead pattern anyway: **H1 +₹38,626 → H2 −₹45,062**, the same half-flip signature that killed it.
- **V2 does not collapse into it at all:** its conditioning variable is a trading system's executed position (multi-system consensus during the day), not any price-strength statistic. It was convicted by its own placebos instead (below).
- **Arm 2 differs:** stock-level idiosyncratic strength with cross-sectional selection and a 5/day cap (the dead study was index-level, afternoon-only, gap-outcome), and an intraday target/stop exit. The fade the dead study documented shows up here in lens form: the selected names' pure-overnight lens (−₹54,581) is **worse** than random names' (−₹20,623).

## 3. DATA AND AUDITS

- **Premium data:** on-disk chain store `data/banknifty-2026-*/option_5m.csv` (185 days) + `daily2leg/prem_bank.json` (all days, 10:00–15:15 window) cover most needs; **126 missing contract-days were fetched** into `btst_data/` via the standing routes (expired-instruments for Jan–Oct expiries; live-key v3 for the 2026-11-23 expiry), browser UA, no 429 encountered. One contract-day is unobtainable (2026-04-28 expiry 50300 PE on 2026-03-30 — API returns no candles) → exactly **1 NC trip in V1 and 1 in V2** (0.5% / 1.1% — G7 passes). Arm 2 uses `data/sarvaritu_fwd/` (full history through Nov 12 for all 25).
- **Timing/leak audits (G6):** Arm 1 — corrupting every spot bar after 15:10 (×3 prices) changes **0** signals/strikes across all days. Arm 2 — corrupting all post-day-D data changes **0** selections on the audit sample. Signals use only data available at their decision points.
- **Cross-store agreement:** 352 overlapping Arm-1 entry bars exist in both premium stores — **352 agree, 0 differ**. Stock store cross-validated against the period stores: 19/19 October days identical O/H/L/C (ASTRAL, HDFCBANK, TATASTEEL).
- **Independent re-sum:** every variant total re-summed from its emitted trades CSV — all match.
- **Raw-drift diagnostic (Arm 2 context):** across all 5,099 stock-days of the universe, the raw overnight move (close → next-day 09:15 bar close) averages **−0.015%** (50.3% up) — the universe does not bleed overnight by itself; the losses below are selection + exit geometry, itemised in §5.

## 4. ARM 1 — BANK NIFTY OPTIONS BTST

### V1 (PRIMARY) — gate FAIL
Total **−₹6,436.00** (−₹643.60/month pace) · 190 trips · WR 43.2% · lens EXIT-0920 −₹2,957.80.
Exits: 80 TARGET / 103 STOP / 7 HARD. Best trip +₹40,772.00 (Mar 6→9, PE 57700, spot gapped +2.88% in its favour); worst −₹17,345.50.

| Month | ₹ | | Month | ₹ |
|---|---|---|---|---|
| Jan | −3,320.50 | | Jun | +4,403.50 |
| Feb | +18,800.50 | | Jul | −10,919.50 |
| Mar | +14,059.50 | | Aug | −11,161.00 |
| Apr | −20,554.00 | | Sep | −1,163.50 |
| May | +29,640.50 | | Oct | −26,221.50 |

H1 **+₹38,626.00** · H2 **−₹45,062.00** · red months **6/10** · ex-top-3 **−₹112,324.00**.
Gate legs: G1 ✗ · G2 ✗ · G3 ✗ · G4 ✗ · **G5 ✓** (beats P-REV −₹69,273.50 and P-RANDDIR −₹26,594.50 — the day's direction *is* better than reversed or chance; it is simply not enough to pay for overnight premium risk after costs) · G6 ✓ · G7 ✓.
Reading: the distribution is a lottery on gap size — three mornings (Feb 2→3, Mar 6→9, Apr 7→8) contribute +₹105,888; without them the book bleeds every month. Direction skill exists but is small against gap variance, and it inverted in H2 — the dead pattern's signature.

### V2 (stack day-direction) — gate FAIL, convicted by its own placebos
Total **−₹6,317.50** (−₹631.75/month) · 88 trips · WR 44.3% · lens EXIT-0920 +₹5,323.70.
H1 +₹31,613.00 · H2 −₹37,930.50 · red months 6/10 · ex-top-3 −₹93,385.00.
Placebos: **P-REV-V2 +₹3,151.00** and **P-RANDDIR-V2 +₹55,805.50** — *both beat the variant it
...[truncated 8189 chars]