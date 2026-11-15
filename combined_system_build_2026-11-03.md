# THE BIG BUILD — ONE COMBINED SYSTEM PER ENGINE
## Evidence pack · built 2026-11-03 · PAPER ONLY — real money ₹0 · NOTHING ARMED

**Status: delivered for the owner's approval under the proof-first rule. This build changes no November primary, no cron, and no live paper book. The SHORT-FOLLOW (R7-M1) paper run remains DISARMED_BY_OWNER. If a forward run of this combined system is approved, it starts only on the owner's word, under the pass/kill pre-registered at the end of this pack.**

**Money bases (never mixed):** Index engines = option premiums per 1 lot (Bank Nifty lot 30, Nifty lot 65), cost ₹220/trade, spot is trigger/levels only. Stocks engine = equity cash, **PROVISIONAL per 100 shares**, cost ₹40/trade (100 shares is a provisional cash-translation unit, never a lot profit). Per-segment accounting and verdicts are separate forever. The single combined figure in this pack — the shared +₹2,000 day ceiling — is an **operational trigger only**, labelled "combined (trigger only)" wherever it appears; it is never a pooled verdict.

**Build dataset (Amendment A):** October 2026 is the tuning window (audited `oct2026_fresh/` set + October slices of the premium/spot stores). Jan–Sep 2026 is printed as an out-of-sample (OOS) read beside every October number — no re-tuning on it. Jan–Oct totals are context. Stocks are judged per year (2025 and 2026 separately).

**How the combined numbers were produced:** one intraday overlay simulator runs the full clubbed book bar-by-bar on 5-minute closes in three arms — **FULL** (everything in the rulebook: segment day-loss caps + the combined ceiling + circuit breakers), **NOCEIL** (caps + breakers, no day-profit ceiling anywhere), **NOGUARD** (no caps, no breakers, no ceilings). Ceiling save/cost per segment = FULL − NOCEIL. Guards' price = NOCEIL vs the standalone books (jointly with removal of the daily pair's own ceiling — stated where used). Simulator validation: with only the daily sleeve loaded it reproduces frozen R7-M1 standalone on **193/193 days, 0 mismatches**; with only the quality layers loaded it reproduces the three adopted books **to the paisa** (Bank +₹83,650.50 · Nifty +₹91,168.50 · Stocks 2026 +₹2,47,178.79). Every component book was independently re-summed before assembly. NOT_COMPUTED is labelled wherever data or machinery is missing; nothing is estimated.

**Denominators:** combined day-metrics (% positive days, worst day, drawdown) are over all calendar trading days in the window (205 days Jan–Oct 2026; 185 Jan–Sep; 20 October) — zero days (paused / no-trade) count as non-positive. Component-book reads quoted from the segment stages use traded days and are labelled as such.

---

## THE SHARED RULEBOOK (all three engines)

**Layers.** Each engine = a **daily layer** (fires every trading day it is computable) + a **quality layer** (the adopted book). Layers may fire on the same day. Positions are accounted per layer and **never netted** across layers. UNIQUE-ONCE applies within a layer. If both layers hold the same contract/side, both positions stand under their own rulebooks, are counted separately, and are listed as overlaps (in Jan–Oct 2026 the index daily layer and quality layers never held the same contract-day: the daily layer trades the front weekly/monthly ATM short; quality legs are dated directional buys — overlap count for the window: **0**).

**Evaluation order at each 5-minute close:** (1) each leg's own exits (stops, targets, trails, square-offs — close-based, gap-through at the bar close; multi-day holds would fill at the next bar's open — no hold variant was adopted, see per-engine hold verdicts); (2) the segment day-loss cap; (3) the combined ceiling.

**Combined day-profit ceiling — "combined (trigger only)":** ONE shared ceiling of **+₹2,000** across all three engines. At any 5-minute close where the combined mark (realised-today + open marks, all engines, each on its own paper sizing above) reaches +₹2,000 — from one engine alone or several together — **every open trade in all engines closes at that close and the day ends: no further entries that day.** Inside this system the shared ceiling **replaces** the daily pair's internal +₹2,000 ceiling; the pair's −₹1,500 day-stop is unchanged.

**Segment day-loss caps (close-based):** Bank −₹3,000 · Nifty −₹3,000 · Stocks −₹1,500 (per-100 unit). At a 5-minute close where a segment's day mark (realised + open) is at or below its cap, all open legs **of that segment** close at that close; the segment takes no new entries that day (other segments continue).

**Circuit breaker (per segment):** 3 consecutive losing combined days → the segment pauses the next 3 trading days. Combined month-to-date ≤ −₹5,000 (index engines) / ≤ −₹3,000 (stocks, per-100) at a day close → the segment pauses for the rest of that calendar month. Pauses block new entries only; held legs continue under their own exits. (No leg is held overnight in the adopted configurations, so the held-leg clause is inert in this build's numbers.)

**Daily layer (both index engines) = R7-M1 "SHORT-FOLLOW-T2", frozen** (`daily2leg/FREEZE.md`, certified under the extended gate incl. bleed legs in Rounds 8/9, `daily2leg/EVIDENCE_PACK_R9.md`):
- 09:15–10:00 reference move on spot; at **10:00** sell the ATM CE if the move is up, sell the ATM PE if down — Bank monthly expiry, Nifty next weekly, 1 lot each, **unconditional** (state picks side only). Zero-move → no leg that index.
- Exits on 5-minute closes: combined day-stop −₹1,500; per-leg T2 trail (arm at +₹1,500 → floor = max(+₹750, peak − ₹750)); runner hard target +₹3,000 per leg; square-off 15:10 bar close. (Its standalone +₹2,000 pair ceiling is replaced by the shared ceiling inside this system.)
- Standalone gated evidence, Jan–Oct 2026 (193 computable days, fires 100% of computable days): **net +₹49,149.25, mean +₹254.66/day** (Bank share +₹41,621.00 · Nifty share +₹7,528.25), win rate 50.3% of days, ceiling-hit 91 days standalone, worst day −₹4,602.75 (2026-07-17), worst 3-day streak −₹8,363.25, max drawdown −₹11,194.10, longest losing streak 5 — inside the owner's bleed limits. Placebos beaten; halves both positive; 8/10 months positive. **Risks carried verbatim from the freeze: NAKED SHORTS — paper only; close-based stops overshoot (worst day −₹4,602.75 vs the −₹1,500 stop).**
- **The small-move note, corrected by Rounds 8/9:** conditioning entries on morning move size is a **closed axis**. Under M1 itself, small-move legs are the book's most profitable cell (Bank small legs +₹52,390 over 129 leg-days at the 0.40% cut); all five small-move replacement variants failed (−₹349…−₹577/day). Nov 2/3 were ordinary losing days in a 50.3%-win-rate book, not a small-move flaw. Round 9's ITM-1 (+₹212.86/day), OTM-1 (+₹143.14) and monthly-Nifty (+₹129.54) variants also pass the gate but are **dominated by M1** — corroboration only. An intrabar circuit breaker at the day-stop is a **proven null** (identical on all 193 days) and is not used.
- **October tuning stage (Amendment A), reported and superseded:** a compact grid (entry 09:45/10:00/10:30 × ATM/OTM-1) was scored with M1 as replica control (reproduced exactly, 193 days, 0 mismatches). October ranking put E1000_OTM first (October: +₹6,012.25 over 8 computable days, mean +₹751.53, 4 ceiling days) — on **8 days only**, and Round 9's full-window gate dominates it (OTM-1 +₹143.14/day < M1 +₹254.66/day), so per the binding Rounds 8/9 update **the daily layer is M1 exactly**; the tuning table is retained as evidence (`combined_build/daily_tuning_results.json`). 09:45 entries are NOT_COMPUTED (premium stores carry no bars before 10:00 — 0 computable days). 10:30 entries fail outright (October mean −₹870.47 ATM; OOS −₹148.80, streak 6). October computable days for the pair: **8 of 20** (12 October days lack the needed contract candles in the stores — the sleeve is NC on those days, never estimated).

**Stocks daily layer: NONE — stated plainly.** No SarvaRitu sleeve passed a gate as an unconditional daily sleeve, and none was fabricated. The stocks engine's busy-ness is intrinsic: the adopted Variant C book trades on 181 of 205 days (2026) at 7.53 trades/day. The system's every-day engine is the index daily layer above.

**Trailing (Amendment: gated per book):** two pre-registered variants per quality book were gated against the incumbent on October (adoption) with the full Jan–Oct gate as supporting evidence. **Result: trailing was NOT adopted in any of the three books** — every variant failed the October net leg, most by wide margins. The incumbent fixed exits stand everywhere; per-engine deltas are in the engine sections. The owner's trailing instruction is therefore implemented as *tested everywhere, adopted nowhere it failed* — the gate, not preference, decided.

**Holding period (open per the owner; decided by gated evidence):** H0 same-day / H1 overnight / H2 ≤5 days / H3 ≤10 days were pre-registered per engine. **H0 stands in all three engines** — in both index engines H1–H3 are NOT_COMPUTED-blocked on the October legs that matter (the actual contracts have no next-day candles in any store), and the one fully-computed hold case in the window *lost* money by carrying (Bank 2026-01-29: +₹1,235.00 same-day → −₹1,720.00 carried overnight). In stocks, H1 was computed for 2026 and failed its placebo leg; H2/H3 are NC-blocked. Details per engine.

---

## ENGINE 1 — NIFTY (options) · ⚠ OOS READ IS NEGATIVE under the full combined rulebook

**Headline:** Quality layer strong (DEC-S1 +₹91,168.50 Jan–Oct; October +₹20,160.50 on 4 legs). But the **combined system as specified** — shared ceiling + breakers — turns Nifty's Jan–Sep out-of-sample read **negative (−₹1,724.60)**. The shared ceiling alone costs this engine −₹70,373.50 out-of-sample: DEC-S1's edge lives in runner legs that run to +175 points (₹11,155), and a +₹2,000 combined trigger amputates them whenever any engine has a good morning. This is the owner's rule implemented exactly; its price on this engine is stated, not hidden.

### Quality layer — adopted pair book DEC-S1 (frozen 2026-11-02), incumbent exits kept
- **A — standing causal book** (35 legs): U1 with C3 confirmation (≥2 distinct U1 systems agree), G7 exits (stop −50; +90 → lock entry+50; target 2 +150; square-off 15:10), monthly expiry.
- **B — gap-fade sleeve** (49 legs): 10:05 entry, fade the overnight gap when |gap| ≥ 0.8%, stop −40 / target +60, square-off 12:30.
- **C — expiry-day sleeve** (13 legs): expiry-day 09:30 PE-short **premium sale** (a different basis from A/B premium points — labelled wherever its legs appear), stop 1.6× / target 0.45× entry premium, square-off 14:30.
- UNIQUE-ONCE, ≤1 leg/sleeve/day, deterministic same-day order A → B → C. Book total Jan–Oct: **97 legs, +₹91,168.50** (regenerated leg-for-leg in this build: 25/25 field checks, 97/97 per-leg nets vs the December freeze). Two gate legs from adoption remain **FAILED-AND-WAIVED** on record (feature-timing 34.0% vs standing book's 34.3%; March flips +₹7,895.00 → −₹11,846.50). The standing causal book (+₹54,102.00) remains the comparison baseline.

### Trailing verdicts — NOT ADOPTED (incumbent G7 kept)
| Variant | Jan–Oct net | Δ vs incumbent | October net (4 legs) | Verdict |
|---|---|---|---|---|
| Incumbent DEC-S1 (lock +60 / tgt2 +175 / arm +50 → BE / sq 15:20 stage clock) | +₹91,168.50 | — | +₹20,160.50 (placebo +₹2,831.50) | stands |
| TR-N1 runner peak-trail (stop2 = max(entry+60, peak2−40)) | +₹85,432.25 | −₹5,736.25 | +₹18,415.25 | FAIL — net leg only, both windows (helps Jun–Oct +₹1,160.25, costs Jan–May −₹6,896.50) |
| TR-N2 pre-target trail (arm +50 → stop = max(entry−50, peak−60)) | +₹69,569.00 | −₹21,599.50 | +₹17,160.75 | FAIL — net leg + feature-timing share falls 34.0% → 27.8% |

### Hold verdict — H0 (same-day)
H1/H2/H3 **NOT_COMPUTED-blocked on October**: both hold-relevant October legs (2026-10-08 22500 PE, 2026-10-09 22400 CE, both exp 2026-10-27) have no next-trading-day candles in any store, so the October gate cannot be passed by any hold variant; full-window NC counts 28 (H1) / 30 (H2/H3) legs. Multi-day machinery itself was validated (H0-mode replay reproduces all 97 legs exactly). **Final configuration: DEC-S1 incumbent × H0.** Jan–Sep OOS of this configuration (component read, traded days): **+₹71,008.00, 93 trades, 84 trading days, worst day −₹5,295.50 (2026-07-14), worst drawdown −₹17,360.00, 48.8% positive days.**

### Combined gate — NIFTY (daily layer share + DEC-S1, per 1 lot, ₹220/trade)
| Window | Arm | Net | ₹/month vs ₹15,000 floor | % positive days | Worst day | Worst 3-day | Worst drawdown | Ex-top-3 days | Trades | Days with ≥1 trade | Paused days |
|---|---|---|---|---|---|---|---|---|---|---|---|
| October (tuned) | **FULL** | **+₹10,651.75** | ₹10,651.75 — below floor | 30.0% | −₹1,029.25 | ₹0.00 | −₹1,029.25 | +₹3,042.75 | 8 | 7/20 (35%) | 2 |
| October | NOCEIL | +₹19,081.00 | above floor | 30.0% | −₹1,464.75 | −₹1,464.75 | −₹1,464.75 | +₹5,068.50 | 10 | 8/20 | 2 |
| Jan–Sep (OOS) | **FULL** | **−₹1,724.60** | **−₹191.62/mo — NEGATIVE** | 37.3% | −₹4,232.75 | −₹8,214.25 | −₹18,380.75 | −₹16,872.35 | 202 | 140/185 (75.7%) | 41 |
| Jan–Sep (OOS) | NOCEIL | +₹68,648.90 | ₹7,627.66/mo — below floor | 33.0% | −₹3,485.25 | −₹7,753.75 | −₹14,973.25 | +₹32,938.40 | 200 | 134/185 | 51 |
| Jan–Oct | **FULL** | **+₹8,927.15** | ₹892.71/mo — below floor | 36.6% | −₹4,232.75 | −₹8,214.25 | −₹18,380.75 | −₹6,220.60 | 210 | 147/205 (71.7%) | 43 |
| Jan–Oct | NOGUARD | +₹102,902.25 | ₹10,290.23/mo — below floor | 43.9% | −₹9,042.75 | −₹12,182.50 | −₹19,691.25 | +₹67,666.25 | 290 | 195/205 | 0 |

- **Ceiling save/cost (FULL − NOCEIL):** October **−₹8,429.25** · Jan–Sep **−₹70,373.50** · Jan–Oct **−₹78,802.75**. The shared ceiling is this engine's single largest cost.
- **Guards' price (NOCEIL vs standalone books +₹98,696.75, jointly with pair-ceiling removal):** −₹10,966.85 Jan–Oct — the breaker pauses this engine 51–53 days across arms; a book built on sparse quality signals loses real trades to streak/month pauses.
- **Busy:** FULL arm fires on 71.7% of days at 1.02 trades/day — busy enough; the binding problem is not activity, it is that the ceiling truncates the winners the book depends on.
- **Day-cap evidence inside the window:** none needed beyond the tables — FULL worst day −₹4,232.75 (cap −₹3,000 close-based; overshoot −₹1,232.75 on the worst day, from close-to-close progression of the short daily leg).

### Nov 2 + Nov 3 counterfactual — NIFTY
- **Daily layer (computable, from the frozen two-day check):** Nov 2 share **−₹1,110.50**, Nov 3 share **−₹363.00** (both days: small up-move → CE sold → day-stop 10:40 / 10:20).
- **Quality layer: NOT_COMPUTED both days** — no DEC-S1 leg can be identified for Nov 2/3 from stored artefacts (the standing book's trade file ends 2026-10-21; the fade builder's calendar is capped 2026-10-28 with the daily spot cache ending the same day; the expiry sleeve's calendar ends 2026-10-31). The November primary's no-trade days (C3 blocked the only signal, a solo Skill CE, both days) were **not** substituted — a different book's record is not evidence for this one.
- **Combined-ceiling trigger:** did **not** fire on either day on the computable index path (peak combined index mark +₹1,799 at 10:15 on Nov 2 — see the ceiling section for the stocks-mark caveat).
- **"Would we still be negative?" — YES on everything computable:** −₹1,110.50 (Nov 2) and −₹363.00 (Nov 3) from the daily layer alone, quality NC. November MTD after Nov 3: −₹1,473.50 — no breaker trigger (limit −₹5,000; losing streak 2 < 3).

---

## ENGINE 2 — BANK NIFTY (options)

**Headline:** The combined FULL system has its **best October of the three arms for this engine (+₹19,488.00, above the ₹15,000 floor)** and the ceiling is roughly free in October (+₹659.00 vs NOCEIL). Out-of-sample the guards and ceiling together cost real money (Jan–Sep FULL +₹53,357.70 = ₹5,928.63/mo, below floor; NOCEIL +₹82,327.50; standalone books +₹1,25,271.50 pace ₹12,527.15/mo — still below floor). Trailing fails this book decisively; the flaw-cycle's conclusion stands: **Bank's problem is entry-side, not exit-side.**

### Quality layer — v21 (causality-audited standing book), incumbent G0 exits kept
U1 pool with frozen B2 adjustments + NS1 second leg (≤1/day, after base exit ≤13:30, room_ratio ≥ 1.5, CE blocked on bearish days); exits **−50 stop / +90 target, no trailing, square-off 15:10**, monthly expiry. Jan–Oct: **99 legs, +₹83,650.50** (reproduced exactly in this build, 0 mismatches). The book's only losing legs are its 47 full −50 stops (−₹80,840 drag against +₹1,64,490.50 of winners): 25 never developed, 22 developed past +30 then faded — and today's flaw cycle proved all three exit-side fixes fail (FC-1 −₹4,204.50, FC-2 −₹39,661.50, FC-3 −₹37,266.00 deltas). Entry-side pre-registrations (NS1-only give-back lock; entry-bar quality conditions on OR breaks) are queued to the evening engine, unchanged by this build.

### Trailing verdicts — NOT ADOPTED (incumbent G0 kept)
| Variant | Jan–Oct net | Δ vs incumbent | October net (9 legs) | Verdict |
|---|---|---|---|---|
| Incumbent v21 × G0 | +₹83,650.50 | — | +₹14,929.50 (placebo −₹3,780.00) | stands |
| TR-B1 post-target peak trail (after +90 trigger: stop = max(entry+50, peak−30)) | +₹66,951.00 | −₹16,699.50 | +₹13,638.00 | FAIL — net leg only, both windows |
| TR-B2 late-arm partial lock (arm +60 → stop entry+25) | +₹48,079.50 | −₹35,571.00 | +₹9,979.50 | FAIL — net + feature-timing legs; the family resemblance to the banned FC-2 lock shows in the delta |

October n is **9 legs** for this book (the 14–17 October trades quoted elsewhere belong to the November *primary's* October reconstruction — a different book; not used here).

### Hold verdict — H0 (same-day)
H1/H2/H3 **NOT_COMPUTED-blocked on October**: the only October leg open at day-end (2026-10-21, 55200 PE exp 2026-10-27, H0 +₹4,389.50) has no 2026-10-22 candles in any store. Across the 94 computable full-window legs, exactly one leg's outcome changes under any hold — 2026-01-29, which flips **+₹1,235.00 → −₹1,720.00** carried overnight (Δ −₹2,955.00): the window's only direct hold evidence is negative. **Final configuration: v21 × G0 × H0.** Jan–Sep OOS of this configuration (component read, traded days): **+₹68,721.00, 90 trades, 83 trading days, worst day −₹1,720.00 (2026-01-28), worst drawdown −₹13,240.00, 50.6% positive days** (68,721.00 + 14,929.50 = 83,650.50 ✓).

### Combined gate — BANK NIFTY (daily layer share + v21, per 1 lot, ₹220/trade)
| Window | Arm | Net | ₹/month vs ₹15,000 floor | % positive days | Worst day | Worst 3-day | Worst drawdown | Ex-top-3 days | Trades | Days with ≥1 trade | Paused days |
|---|---|---|---|---|---|---|---|---|---|---|---|
| October (tuned) | **FULL** | **+₹19,488.00** | **₹19,488.00 — ABOVE FLOOR** | 50.0% | −₹505.00 | ₹0.00 | −₹505.00 | +₹10,348.50 | 15 | 11/20 (55%) | 0 |
| October | NOCEIL | +₹18,829.00 | above floor | 45.0% | −₹2,225.00 | −₹1,526.00 | −₹3,084.00 | +₹7,067.00 | 17 | 12/20 | 0 |
| Jan–Sep (OOS) | **FULL** | **+₹53,357.70** | ₹5,928.63/mo — below floor | 42.7% | −₹4,017.50 | −₹8,442.00 | −₹9,379.00 | +₹40,102.20 | 192 | 145/185 (78.4%) | 39 |
| Jan–Sep (OOS) | NOCEIL | +₹82,327.50 | ₹9,147.50/mo — below floor | 40.0% | −₹4,027.00 | −₹8,139.50 | −₹9,050.50 | +₹58,264.00 | 213 | 145/185 | 40 |
| Jan–Oct | **FULL** | **+₹72,845.70** | ₹7,284.57/mo — below floor | 43.4% | −₹4,017.50 | −₹8,442.00 | −₹9,379.00 | +₹59,590.20 | 207 | 156/205 (76.1%) | 39 |
| Jan–Oct | NOGUARD | +₹1,30,712.00 | ₹13,071.20/mo — below floor | 52.2% | −₹6,828.50 | −₹8,878.50 | −₹16,714.00 | +₹1,05,074.00 | 292 | 197/205 | 0 |

- **Ceiling save/cost (FULL − NOCEIL):** October **+₹659.00** (the ceiling *helped* — it banked combined marks before Bank's own legs faded) · Jan–Sep **−₹28,969.80** · Jan–Oct **−₹28,310.80**.
- **Guards' price (NOCEIL vs standalone books +₹1,25,271.50, jointly with pair-ceiling removal):** −₹24,115.00 Jan–Oct. What the guards buy for it: worst day contained to −₹4,017.50 (vs −₹6,828.50 unguarded), worst drawdown −₹9,379.00 (vs −₹16,714.00).
- **Busy:** FULL fires on 76.1% of days at 1.01 trades/day — the daily layer does its job; October dips to 55% only because the pair is computable on just 8 October days in the stores (NC, not idleness).
- **Day-cap evidence:** the −₹3,000 cap binds in the FULL arm (Jan–Oct worst day −₹4,017.50 is a post-cap close-based overshoot of ₹1,017.50, driven by the short daily leg's close-to-close progression — the same mechanism Round 8 proved an intrabar breaker cannot fix).

### Nov 2 + Nov 3 counterfactual — BANK NIFTY (full combined rulebook applied)
- **Nov 2:** daily leg (CE 58300 sold 10:00 @ ₹415.30) day-stopped 10:40, share **−₹895.00**; quality leg Skill PE 54800 (exp 2026-11-23) entered 10:20 @ ₹681.95, stopped 10:25 → **−₹1,720.00**. Segment cap tested at 10:20: segment mark ≈ −₹1,403.00 > −₹3,000 → **cap does not fire**. Combined ceiling: no (peak +₹1,799, ceiling section). **Combined-system Nov 2 net: −₹2,615.00 — still negative** (vs −₹1,720.00 for the November primary alone; the daily layer added a second loser, as a 50.3%-win-rate sleeve will on half its days).
- **Nov 3:** daily leg (CE 58400 sold 10:00 @ ₹436.10) day-stopped 10:20, share **−₹1,673.50**; quality NS1 second leg CE 55500 entered 10:20 @ ₹867.60, own −50 stop would exit 11:10 → −₹1,720.00 unguarded. **The segment day-cap FIRES first, at 11:05:** realised −₹1,673.50 + quality mark at the 11:05 close −₹1,378.00 = −₹3,051.50 ≤ −₹3,000 → quality leg closes at **−₹1,378.00**, saving ₹342.00. **Combined-system Nov 3 net: −₹3,051.50 — still negative, ₹342 less negative.**
- **Breaker consequence:** Bank November MTD after Nov 3 = −₹2,615.00 + −₹3,051.50 = **−₹5,666.50 ≤ −₹5,000 → the MTD circuit breaker would trigger at the Nov 3 close and pause the Bank engine for the rest of November** under this rulebook. (Streak breaker does not fire: 2 consecutive losing days.) Recorded as a counterfactual consequence, nothing is paused in reality — this system is not running.

---

## ENGINE 3 — STOCKS (equity cash, PROVISIONAL per 100 shares, ₹40/trade) — judged PER YEAR

**Headline:** The only engine whose **combined FULL system clears the ₹15,000/month floor in every 2026 window** (October +₹51,724.51 · Jan–Sep +₹15,367.33/mo · Jan–Oct +₹19,003.04/mo). Two honest qualifications ride with that: (1) the stocks day-loss cap **cannot bind intraday in this backtest** — the adopted book's artefacts carry no exit times or exit prices, so stocks legs are realised at day-end in the overlay and the −₹1,500 cap is a live-run control, not a backtested one; (2) the circuit breaker is **expensive** for this high-frequency book (56 paused days Jan–Sep 2026; a day-granularity 2025 read loses −₹61,619.90 to pauses). 2025 remains below floor on the adopted book itself (+₹11,981.34/mo, gap ₹30,186.56 — pre-existing, unchanged by this build).

### Quality layer — adopted Variant C (frozen 2026-11-02), incumbent exits kept
11 sleeves (F4, INV family, N4-V3, P2F family, GAP-FADE, NE-REV-NU, REXP) on the 25-stock watchlist, regime law = Nifty prior close vs 50DMA. Jan–Oct: **2025 — 1,108 trades, +₹1,19,813.44** · **2026 — 1,363 trades, +₹2,47,178.79** (both re-summed exactly in this build). The build's resimulation machinery **reproduces both books row-for-row, all 11 sleeves** — trailing/hold variants below are therefore real resimulations, not overlays on nets. Variant C's adoption record keeps its qualification: re-gated against the pre-adoption book it passes 8/10 legs; legs (c)/(e) are **FAILED-AND-WAIVED** (2026 −₹10,121.51; combined ex-top-3 −₹16,352.41) — never quote Variant C without it.

### Trailing verdicts — NOT ADOPTED in either year (incumbent fixed exits stand)
October gate (the adoption decision; placebo bar = best of the month's three placebo slices):
| Year · October | Incumbent | Placebo bar | TR-S1 (arm at 60% of target → exit on 40%-of-target retrace) | TR-S2 (arm 60% → lock 25% of target) |
|---|---|---|---|---|
| 2025 (21 trades) | −₹4,042.67 | −₹2,644.51 | −₹5,087.29 (Δ −₹1,044.62) FAIL | −₹4,648.02 (Δ −₹605.35) FAIL |
| 2026 (152 trades) | +₹56,127.37 | **+₹64,610.51** | +₹54,704.60 (Δ −₹1,422.77) FAIL | +₹44,482.02 (Δ −₹11,645.35) FAIL |

Full-year supporting evidence agrees: both variants fail the standing 10-leg gate (Jan–Oct deltas: S1 −₹41,028.79 in 2025 / −₹36,266.02 in 2026; S2 −₹38,499.35 / −₹34,829.77). **Plain note:** in October 2026 the placebo bar (+₹64,610.51, a fade-late slice) sits *above the incumbent itself* — on the tuning month, the adopted book did not beat its toughest placebo slice. Neither OOS read is negative (below), so this is a watch item, not a disqualification — but it is recorded, not smoothed over.

### Hold verdict — H0 in both years
- **2025:** H1/H2/H3 all October-NC-blocked by exactly **one** leg — the book's only NC leg: P2F-R2 WIPRO SHORT 2025-10-21 (WIPRO's 5-minute store for that date holds only 12 bars, 13:45–15:10; the 09:15 entry bar itself is absent).
- **2026:** H1 computed with NC = 0: October +₹57,737.32 (Δ +₹1,609.95 vs H0) but **fails the placebo leg** (bar +₹64,610.51) → not adopted. H2 NC-blocked (21 October legs), H3 NC-blocked (94 legs — hold windows run past 2026-11-02, the last date with bars in any store).
- **Final configuration: Variant C incumbent × H0, both years.** Jan–Sep OOS of this configuration (component read, traded days): **2025 +₹1,23,856.11** (1,043 trades, worst day −₹7,523.14 on 2025-01-30, worst drawdown −₹17,044.80, 55.10% positive days) · **2026 +₹1,91,051.42** (1,211 trades, worst day −₹9,970.41 on 2026-03-04, worst drawdown −₹12,179.31, 59.01% positive days).

### Combined gate — STOCKS 2026 (Variant C + guards + shared ceiling; stocks legs realised at day-end in the overlay — see cap caveat)
| Window | Arm | Net | ₹/month vs ₹15,000 floor | % positive days | Worst day | Worst drawdown | Ex-top-3 days | Trades | Days with ≥1 trade | Paused days |
|---|---|---|---|---|---|---|---|---|---|---|
| October (tuned) | **FULL** | **+₹51,724.51** | **ABOVE FLOOR** | 70.0% | −₹2,122.56 | −₹2,122.56 | +₹15,409.33 | 116 | 19/20 (95%) | 0 |
| October | NOCEIL (= NOGUARD in Oct) | +₹56,127.37 | above floor | 75.0% | −₹2,122.56 | −₹2,122.56 | +₹20,019.24 | 152 | 20/20 | 0 |
| Jan–Sep (OOS) | **FULL** | **+₹1,38,305.93** | **₹15,367.33/mo — ABOVE FLOOR** | 36.8%* | −₹9,970.41 | −₹9,970.41 | +₹89,028.63 | 779 | 119/185 | 48 |
| Jan–Sep (OOS) | NOCEIL | +₹1,14,809.89 | ₹12,756.65/mo — below floor | 36.2%* | −₹9,970.41 | −₹9,970.41 | +₹67,637.57 | 796 | 114/185 | 56 |
| Jan–Oct | **FULL** | **+₹1,90,030.44** | **₹19,003.04/mo — ABOVE FLOOR** | 40.0%* | −₹9,970.41 | −₹9,970.41 | +₹1,40,753.14 | 895 | 138/205 | 48 |
| Jan–Oct | NOGUARD | +₹2,47,178.79 | ₹24,717.88/mo — above floor | 53.7%* | −₹9,970.41 | −₹12,179.31 | +₹1,97,320.84 | 1,363 | 181/205 | 0 |

\* % positive days here is over all calendar days in the window (zero days counted); over traded days the adopted book reads 60.77% (2026).
- **Ceiling save/cost (FULL − NOCEIL):** October **−₹4,402.86** (all of it entry suppression after early triggers — stocks exits are never truncated in this backtest because legs carry no intraday marks) · Jan–Sep **+₹23,496.04** (the same suppression happened to skip losing late entries and shifted breaker paths; treat the sign as path luck, not a ceiling benefit) · Jan–Oct +₹19,093.18.
- **Guards' price:** Jan–Sep **−₹76,241.53** (NOGUARD +₹1,91,051.42 → NOCEIL +₹1,14,809.89) — essentially **all circuit breaker** (56 paused days), since the day-cap cannot bind in-sim. In October the breaker never fired (0 paused days) and cost nothing.
- **2025 breaker read (day granularity, full year incl. Nov–Dec as carried in the adopted CSV):** raw +₹1,21,764.83 → with breaker **+₹60,144.93**, 71 of 186 days paused, **price −₹61,619.90**. The breaker as specified is badly calibrated for a 6–7 trades/day book: it pauses the engine through the recovery days its edge needs.
- **Busy:** the busiest engine by far — FULL arm 895 trades over 138 active days (4.37/calendar day; 6.5/active day), October 116 trades on 19/20 days.

### Nov 2 + Nov 3 counterfactual — STOCKS
- **Variant C, Nov 2: NOT_COMPUTED.** Bars exist (the forward store carries a complete Nov 2 — 75 bars × 25 stocks), but scoring needs three pieces of new, unvalidated construction: a forward-root rebuild of the validated machinery, substituting the live calendar for N4/P2F candidate generation, and extending the NE-REV certified non-event set beyond its frozen Jan–Oct calendar (the NTPC Nov 2 reaction day is not in it, so NE-REV admission cannot be certified). No partial number was estimated. (Kept distinct: the *frozen v2 book's* official Nov 2 log is +₹1,455.27 over 4 trades — that is a different book and is **not** a Variant C counterfactual.)
- **Nov 3: NOT_COMPUTED** — no Nov 3 bars exist in any store available to this build (forward store ends Nov 2; the official EOD log lands 16:35 IST, after this build).

---

## THE COMBINED CEILING — BEHAVIOUR (combined (trigger only) — operational statistic, not a verdict)

- **Trigger days:** 106 of 205 days Jan–Oct 2026 (51.7%) · **14 of 20 October days** (Oct 5, 6, 7, 8, 9, 13, 16, 21, 22, 23, 26, 27, 28, 29). **Mean trigger time 11:42** (October 11:48) — the typical combined day ends before noon.
- **Why so often:** the trigger is *realised + open marks* across three engines. A single Bank quality leg at its +90 target is +₹2,480 — one good leg anywhere ends the day for everyone. The ceiling as specified is, in practice, "the first good morning ends the day."
- **Save/cost per segment (FULL − NOCEIL), Jan–Oct:** Bank **−₹28,310.80** · Nifty **−₹78,802.75** · Stocks **+₹19,093.18** (entry-suppression artefact — stocks exits untruncated in-sim; see Engine 3). October only: Bank +₹659.00 · Nifty −₹8,429.25 · Stocks −₹4,402.86.
- **Nov 2/3:** did **not** trigger on either day on the computable path. Nov 2: the index pair's combined mark peaked at **+₹1,799 at 10:15** while open (both legs exited 10:40) — ₹201 short. Stocks intraday marks for Nov 2 are NOT_COMPUTED (the spot store ends 2026-10-28), so a trigger additionally requiring ≥ +₹201 of open stocks marks at 10:15 can neither be verified nor excluded; Nov 2's known stocks fills were later (09:35–10:05 entries, day-end exits). Nov 3: pair peaked +₹778 at 10:05; after 10:20 the pair was realised at −₹2,036.50 and the Bank quality mark peaked at +₹647 (10:30), so the combined index path stayed ≤ −₹1,389.50, and the day's known stocks records were negative — no trigger.

## WHAT STILL DOESN'T WORK — honest list
1. **The shared +₹2,000 ceiling vs the quality books' geometry.** It is the owner's rule and it is implemented exactly — and on this evidence it is the combined system's biggest single cost (−₹78,802.75 Jan–Oct on Nifty; −₹28,310.80 on Bank), because both index quality books earn through runners (+90/+150 points; +175 on DEC-S1's second target) that a ₹2,000 combined trigger structurally amputates. Under the FULL rulebook **no engine reaches the ₹15,000/month floor on the Jan–Sep OOS read except Stocks**, and Nifty's OOS goes negative. If the owner wants the ceiling kept, the evidence says its level — not the engines — is what stands between the system and the floor out-of-sample. (Reported, not changed: changing it is the owner's call.)
2. **Trailing does not survive the gate anywhere.** Six variants, three books, all fail — Bank by −₹16,699.50 / −₹35,571.00, Nifty by −₹5,736.25 / −₹21,599.50, Stocks by −₹605…−₹41,029 depending on year/variant. "Trail once it's moving" is already priced into these books' fixed geometries (G7's lock, the sleeves' targets); adding more give-back room donates winners' edge. The books' losses are entry-side (Bank flaw cycle: 47 full stops, every exit fix fails) — that is where the remaining edge hunt lives.
3. **The circuit breaker is mis-calibrated for the stocks engine** (−₹76,241.53 Jan–Sep 2026; −₹61,619.90 on the 2025 day-level read; 48–71 paused days). For the index engines it buys genuine drawdown containment (Bank worst drawdown −₹16,714.00 → −₹9,379.00) at a real but smaller price. One breaker shape does not fit both a 1-trade/day book and a 7-trades/day book.
4. **Holding is unproven, not disproven.** Every index hold variant is NC-blocked on the exact October legs that matter (no next-day candles for those contracts in any store), and the single computable hold case lost ₹2,955.00 by carrying. Stocks H1 (2026) gained +₹1,609.95 in October and *still* failed its placebo leg. H0 stands by default of evidence, not by proof of superiority.
5. **Stocks intraday guard granularity.** The adopted book's artefacts carry no exit times/prices, so in backtest the stocks day-cap never binds and stocks legs cannot be marked into the combined ceiling intraday (their day-end nets are exact; the 2025 overlay is day-granularity; Nov 2 Variant C is NC for machinery reasons). A live run removes this limitation — live marks exist tick-by-tick — but the backtested ceiling/cap statistics for stocks must be read with this label attached.
6. **October itself is a thin tuning window for the index quality books** (Bank 9 legs, Nifty 4 legs, daily pair 8 computable days). Every October adoption decision in this build is therefore backed by the full-window gate as supporting evidence — and in all six trailing cases both windows agreed, which is why the incumbent stands everywhere. The daily pair's October NC rate (12 of 20 days missing contract candles) is a data-store gap, not a strategy gap.
7. **Floors vs the combined system as specified:** Bank FULL — October above floor, Jan–Sep ₹5,928.63/mo, Jan–Oct ₹7,284.57/mo (gap to floor pace ₹77,154.30). Nifty FULL — October ₹10,651.75, Jan–Sep **negative**, Jan–Oct ₹892.71/mo. Stocks FULL 2026 — floor met in all windows (cap caveat attached); Stocks 2025 — ₹11,981.34/mo on the adopted book, gap ₹30,186.56, breaker makes it worse. The standing per-segment floor fight continues in the evening engines on November live trades + December judging, unchanged by this build.

## PRE-REGISTERED FORWARD PASS/KILL — per segment, ONLY if the owner approves a run (proof-first)
Run: the FULL combined rulebook above, live paper, 20 trading days, all three engines clubbed (shared ceiling live), per-segment accounting. November primaries untouched; this is a separate book.
- **PASS (per segment):** segment net > ₹0 over the 20 days **and** ≥ 70% of days with ≥ 1 trade (busy) **and** no MTD-breaker trigger during the run.
- **KILL (per segment):** segment net ≤ −₹5,000 (Bank/Nifty) / ≤ −₹3,000 (Stocks, per-100) at any day close, **or** busy < 50% of days, **or** a second MTD-breaker trigger. A killed segment stops; the others continue (segments are judged separately, as always).
- **INCONCLUSIVE** (neither PASS nor KILL): extend once by 10 trading days, then judge on 30.
- Recorded but not gated: combined-ceiling trigger days (in-sample rate 51.7% of days) and mean trigger time (in-sample 11:42).
- Naked-short risk note for the daily layer stands: paper only; any future live thought requires a separate margin/gap review that this pack does not provide.

## ARTEFACTS (all in `~/workspace/trading/combined_build/` unless noted)
- `PREREG.md`, `PREREG_AMENDMENT.md`, `PREREG_AMENDMENT2.md` — pre-registrations (rulebook, October-primary amendment, combined-ceiling rule), filed before scoring.
- `daily_tuning.py` / `daily_tuning_results.json` / `daily_layer_days.csv` — daily-layer tuning stage (M1 replica control 193/193) and the frozen M1 day file.
- `bank_trailing_results.json`, `nifty_trailing_results.json`, `stocks_trailing_results.json` — per-engine gates (October + full window), hold stages, OOS reads; `bank_quality_adopted_trades.csv`, `nifty_quality_adopted_trades.csv`, `stocks_quality_adopted_trades.csv` — final adopted books (re-sum exact).
- `overlay.py` / `combined_overlay_results.json` / `overlay_days_FULL.csv`, `overlay_days_NOCEIL.csv`, `overlay_days_NOGUARD.csv` — the clubbed simulation (validation: daily-only = M1 193/193; quality-only = adopted books to the paisa).
- `counterfactual.py` / `counterfactual_results.json` — Nov 2/3 per segment, incl. the Bank cap firing at 11:05 on Nov 3 and the Bank MTD-breaker consequence.
- `~/workspace/trading/daily2leg/FREEZE.md`, `~/workspace/trading/daily2leg/EVIDENCE_PACK_R9.md`, `~/workspace/trading/flaw_cycle_2026-11-03.md` — the daily layer's freeze + extended-gate certification, and the entry-side flaw evidence this build builds on.
