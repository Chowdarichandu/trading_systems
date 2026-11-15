# Day Trader Skill (Skill V3) — STANDALONE TUNING, 2026-11-05

Chandu's direction (2026-11-05): tune the Day Trader Skill as a standalone book — it fires nearly every day; the suspicion was that its problem is exits, not presence. **Paper only, real money ₹0, no live orders. Nothing is armed by this run** — a passer would have been reported as a candidate for Chandu's go; there is no passer. Tuning data = **Jan–Oct 2026 only** (203 trading days, 2026-01-01 → 2026-10-28). Nov 2–4 were never tuned on and never enter any tuning total; they are quoted once at the end as the untuned book's untouched forward record.

Indices tuned and reported **separately, never pooled**. Money: Bank lot 30 / Nifty lot 65, cost ₹220/trade, UNIQUE-ONCE (Skill fires at most one signal per day, so the key set is unique by construction — audited).

## The coverage fact — read this before any number below

The premium stores (`daily2leg/prem_bank.json`, `prem_nifty.json`, monthly series) were built from 10:00 onward: **10,169 of ~10,246 Bank contract-days and 8,641 of ~8,744 Nifty contract-days in the stores have no bars before 10:00** (only the ~59–96 backfilled contract-days start at 09:15). Skill's entries cluster at 09:35–09:55. Result:

- **Bank: 79 of 165 legs scorable (86 NOT_COMPUTED — every one "entry bar absent", every one an entry at 09:35–09:55).**
- **Nifty: 96 of 165 legs scorable (69 NOT_COMPUTED — 68 entry-bar-absent at 09:35–09:55, 1 no-expiry on 2026-10-28).**

Every tuning number in this report therefore describes **the ≥10:00-entry subset of Skill's book**, not the whole book. The early-entry majority is untestable from the stored archive — its exits are neither proven nor disproven here. No leg was estimated; NC legs are counted per variant in the results JSON.

## Validation (before any tuning number)

- Signal enumeration reproduces the stored Jan–Sep Skill V3 spot CSV **exactly** (Bank 150/150, Nifty 151/151 legs — 0 missing, 0 extra) and covers **all** U1 Jan–Oct Skill-source keys (Bank 164/164, Nifty 165/165; the 165th Bank leg is a key U1's pool attributed to another representative). Enumeration: 165 signal days per index out of 203 trading days (81% of days — the presence Chandu saw is real: Bank 30 no-signal + 8 blocked-09:30-PE days; Nifty 22 + 16).
- Timing/feature audit on every variant: PASS (OR from bars < 09:30 only; signal = first close beyond OR in 09:30–11:30; PDL = previous trading day's low; entry = the bar immediately after the signal bar; entry premium = that premium bar's open, re-verified per row; all exits within [entry, 15:10]; no November date anywhere).
- Independent re-sum from the written CSVs: PASS on every variant. Two legs hand-verified end-to-end from raw store bars (Bank 2026-01-12 PE 59000 stop 12:15; Nifty 2026-10-01 CE 22600 stop 12:10 — both reproduce to the paisa).
- Baseline geometries replicate `aggressive_score.replay` verbatim — the exact code that scored the Nov 2–4 standalone record (Bank plain −50/+90; Nifty runner_lock50 = G7).

**Gate (identical for every run):** PASS requires net > baseline net AND timing audit clean AND re-sum exact AND halves both ≥ −₹2,000 AND ≤ 3 negative months AND ex-top-3 > 0 AND net above all three placebos (flipped-direction, +30-min shifted, random matched count/month, seed 20261105). Shifted/random placebos score on their own scorable subsets (a +30-min shift moves early entries into the store's coverage, so shifted n can exceed the book's n — counts are in the JSON).

---

## BANK NIFTY — Skill standalone (G0 baseline; scored subset 79 legs)

**Baseline: −₹10,532.50** · win 39.2% · FT 34.2% · H1 +₹574.50 / H2 −₹11,107.00 · 6 negative months · ex-top-3 −₹17,972.50 · worst drawdown −₹28,692.50 · pace **−₹1,053.25/month**. Gate: halves FAIL, months FAIL, ex-top-3 FAIL (placebos beaten: flipped −₹15,154.50, shifted −₹68,481.30, random −₹68,348.50 — the entry timing is real; the book still loses).

| Family | Net ₹ | Legs | Win / FT % | H1 / H2 ₹ | Neg mo | Ex-top-3 ₹ | Verdict |
|---|---|---|---|---|---|---|---|
| F1 trailing (arm +40, trail 25, cap +150) | −15,305.50 | 79 | 43.0 / 8.9 | −4,162.50 / −11,143.00 | 5 | −30,680.50 | FAIL — worse than baseline; flipped placebo (−3,850.50) beats it |
| F2 premium ladder (+30/+58/+82 locks, +100 exit) | −34,084.30 | 79 | 31.6 / 15.2 | −17,016.30 / −17,068.00 | 8 | −47,299.30 | FAIL — worst exit variant; random placebo beats it |
| F3 tighter stop −35/+90 | −25,697.50 | 79 | 26.6 / 24.1 | −10,471.50 / −15,226.00 | 9 | −33,137.50 | FAIL — the −35 stop just gets hit more |
| F4 drop entries after 11:30 | −13,012.50 | 78 | 38.5 / 33.3 | +574.50 / −13,587.00 | 6 | −20,452.50 | FAIL — the filter removed exactly one scored leg: an August 11:35 entry worth +₹2,480 |
| F5 CE-only | −11,688.50 | 32 | 34.4 / 28.1 | −8,282.50 / −3,406.00 | 8 | −19,128.50 | FAIL — anatomy only |
| F5 PE-only | **+1,156.00** | 47 | 42.6 / 38.3 | +8,857.00 / −7,701.00 | 6 | −6,284.00 | FAIL — the only positive Bank book, but H2 is −₹7,701 and ex-top-3 is negative |

Month table (baseline): Jan −3,131.00 · Feb +8,697.00 · Mar −2,880.00 · Apr −400.00 · May +560.00 · Jun −2,271.50 · Jul −8,800.00 · Aug −6,341.00 · Sep +34.00 · Oct +4,000.00.

**Bank anatomy in one line:** every exit re-geometry made it worse; the only split that separates money from bleed is direction — PE legs +₹1,156.00 vs CE legs −₹11,688.50 — and even the PE book is an H1 story that reverses in H2.

## NIFTY — Skill standalone (G7 baseline; scored subset 96 legs)

**Baseline: −₹4,606.75** · win 42.7% · FT 22.9% · H1 −₹20,943.50 / H2 +₹16,336.75 · 6 negative months · ex-top-3 −₹33,196.75 · worst drawdown −₹31,596.25 · pace **−₹460.68/month**. Gate: halves FAIL, months FAIL, ex-top-3 FAIL, and the **flipped placebo makes +₹22,981.50** — on the scorable subset, taking the *opposite* side of Skill's Nifty signals beat taking Skill's side.

| Family | Net ₹ | Legs | Win / FT % | H1 / H2 ₹ | Neg mo | Ex-top-3 ₹ | Verdict |
|---|---|---|---|---|---|---|---|
| F1 trailing | −5,497.25 | 96 | 47.9 / 3.1 | −13,774.00 / +8,276.75 | 5 | −37,912.50 | FAIL — flipped placebo +₹43,313.50 |
| F2 premium ladder | −28,474.75 | 96 | 34.4 / 9.4 | −33,865.50 / +5,390.75 | 6 | −51,400.00 | FAIL |
| F3 tighter stop −35 (G7 shape) | −10,798.00 | 96 | 35.4 / 19.8 | −18,831.00 / +8,033.00 | 4 | −39,388.00 | FAIL |
| F4 drop entries after 11:30 | −5,293.50 | 95 | 42.1 / 23.2 | −20,943.50 / +15,650.00 | 6 | −33,883.50 | FAIL — one late leg removed, no rescue |
| F5 CE-only | −23,025.50 | 43 | 32.6 / 20.9 | −14,909.00 / −8,116.50 | 7 | −45,911.75 | FAIL — the bleed lives here |
| F5 PE-only | **+18,418.75** | 53 | 50.9 / 24.5 | −6,034.50 / +24,453.25 | 4 | −10,171.25 | FAIL — see below |

Month table (baseline): Jan −513.25 · Feb −2,683.25 · Mar −5,469.50 · Apr −3,156.75 · May −16,269.00 · Jun +7,148.25 · Jul −3,758.00 · Aug +214.75 · Sep +14,585.00 · Oct +5,295.00.

**Why F5 PE-only is NOT a pass despite +₹18,418.75:** its own +30-minute shifted placebo makes **+₹28,626.00 — more than the book itself**, so the entry timing carries no edge; H1 is −₹6,034.50 (the entire profit is H2, with May alone −₹13,880.00 inside H1's PE set); ex-top-3 is −₹10,171.25 (the total rests on its three biggest legs). Three gate legs fail. It is recorded as anatomy, not a candidate.

## Combination step

**Not run — the pre-registered condition (two or more families passing on the same index) was met on neither index. Zero families passed.** Combining failed variants would be exactly the re-shopping the registration forbids.

## Closing lines

- **Bank Nifty:** best Skill book found = F5 PE-only, **+₹1,156.00 over Jan–Oct = +₹115.60/month pace — ₹14,884.40/month short of the ₹15,000 floor**, and it failed the gate, so it is not a candidate. The untuned book's untouched forward record, Nov 2–4: **−₹5,160.00** (3 trades, 3 stops).
- **Nifty:** best Skill book found = F5 PE-only, **+₹18,418.75 over Jan–Oct = +₹1,841.88/month pace — ₹13,158.12/month short of the floor**, gate-failed on halves, ex-top-3 and its shifted placebo. Forward record Nov 2–4 (untuned): **−₹781.25** (2 trades).
- **The direct answer to the hypothesis:** on the scorable subset, Skill's problem is **not its exits** — trailing (F1), the ladder (F2) and the tighter stop (F3) all made both indices *worse*, and the late-entry filter (F4) removed a winner. What separates profit from bleed is **direction**: PE legs positive on both indices, CE legs deeply negative on both (−₹11,688.50 Bank, −₹23,025.50 Nifty), and on Nifty the flipped book beat the real one. But no direction book survives the gate either — the PE strength flips sign between halves on both indices. And the majority of Skill's legs (the 09:35–09:55 entries) remain untested either way: the archive simply does not hold their premium bars.

## Files

- Scorer: `skill_tuning_score.py` (pre-registered family definitions in its header)
- Results: `skill_tuning_results.json` (full gate output, placebo counts, NC detail per variant)
- Trades: `skill_tuning_bank_{baseline,F1,F2,F3,F4,F5CE,F5PE}_trades.csv`, `skill_tuning_nifty_{baseline,F1,F2,F3,F4,F5CE,F5PE}_trades.csv`
- No primary, shadow, log or frozen file was touched; no cron changed; nothing armed.
