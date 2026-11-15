# November shadow runs — run sheet (owner-directed 2026-11-04 ~06:18 IST)

Standing labels for everything on this page: **paper only · real money ₹0 · 1 lot per leg · no live orders.** The frozen November primaries (Bank BNF-PAPER-V1, Nifty NF-PAPER-C3G7), their specs, logs and cron sections are **not modified** by these runs — all additions are additive and labelled SHADOW. The intraday announcement watcher is **not** extended to shadows; shadows report at the 15:45 daily stats and in the evening segment-engine reports only.

## SHADOW 1 — Bank Nifty "v22" (log: `november_shadow_v22_bank_log.csv`)

**Rules in force** (v22 assembled book, `bank_v22_phase1_2026-11-04.md`; Jan–Oct 2026 evidence +₹91,450.50 over 90 legs, full gate passed; the scorer re-verifies the Jan–Oct assembly — 99 legs / +₹83,650.50 under v21 exits — on every run before writing any November row):

- Entry frame = Bank v21's: B2 causal pool (U1 component legs — Skill V3, (lA) v2, V5 v2, Volrix (b) — with Skill Bank CE blocked and solo legs admitted only causally) + NS1 second leg (≤1/day, after the base trade exits ≤13:30, fresh OR break, room_ratio ≥ 1.5, CE blocked on bearish-bias days) + NS3 gap-class legs (GD/GU sublegs only) + S3A/S3E/S3D state add-ons; UNIQUE-ONCE per (date, direction); entry-premium band 400–550 dropped; NS1 CE dropped (v21 frame rule); segment exit geometry per the v21 book (V15 segments / P21 for NS3 / state geometry for S3), square-off 15:20.
- **Step A — BANK-EVE-04:** NS1 second legs get the FC-2 give-back lock (once a bar's high reaches entry+30, the stop rises to entry for subsequent bars).
- **Step B — BANK-EVE-05:** base rows whose representative system is Skill V3, direction PE, entering before 10:30 are removed (logged as `v22 EVE-05-SKIP` rows with no net — disclosure, not trades).
- Basis: option premiums per 1 lot (lot 30), cost ₹220/trade.

**Frame-difference note (required by the wiring task):** the TUNED SHADOW BOOK v2 designated in `november_rsi_bank_log.md` (from Wed 2026-11-04) is a **genuinely different book** — it runs on the frozen PRIMARY's frame (BNF-PAPER-V1 legs, G0 exits −50/+90, square-off 15:10) with the EVE-05 skip and the EVE-04 NS1 lock applied there. SHADOW v22 runs on the **v21 frame** (different entries, segment geometry, square-off 15:20). They are not the same signals: on 2026-11-02 the primary frame produced a Skill V3 PE trade (the primary's own −₹1,720 leg) while v22's only assembled row that day was that same component leg removed by EVE-05 (v22: no trade); on 2026-11-03 the primary frame's trade was an NS1 CE leg, which the v21 frame drops by rule (NS1 CE dropped). **Resolution: both run, separately labelled** — v2 stays the Bank engine's TUNED SHADOW BOOK; v22 is the additional owner-directed shadow from Chandu's 2026-11-04 direction. The Bank engine's one-shadow-at-a-time rule governs TUNED shadows, not this owner-directed run. Their MTD lines are reported side by side, never merged.

## SHADOW 2 — Nifty "DEC-S1" (log: `november_shadow_decs1_nifty_log.csv`)

**Rules in force** (adopted DEC-S1 spec, `nifty_engine_frozen.md` Round 11 S0–S9; Jan–Oct 2026 evidence +₹91,168.50; two gate legs recorded FAILED-AND-WAIVED at adoption — never quote "no waiver needed"):

- **A** — standing causal book admission over the day's U1 sysmap: a key (date, direction) is admitted when ≥2 systems agree and the 2nd-earliest system entry is ≤ 09:55 (leg enters at that bar), or a solo (lA) v2 leg at its own bar; strike ATM100 at the entry bar's spot open; contract = monthly expiry in force; a leg whose trade date **is** the monthly expiry is excluded (EXP0).
- **B** — gap fade: if |open / prior close − 1| ≥ 0.50%, one leg opposite the gap at the 10:05 bar, ATM100, monthly in force, EXP0, unless A owns the key.
- **C** — weekly-expiry sleeve: on weekly expiry days, U1 pool keys whose sources include Skill V3 are re-struck ATM100 at Skill V3's own entry bar (admitted 09:15–11:00) on the contract expiring that day, unless A or B owns the key.
- UNIQUE-ONCE per (date, direction) across A/B/C. Geometry (all): stop −50 (checked before target, entry bar included); +50 arms breakeven (stop → entry); +90 moves the runner lock to entry+60; target 2 +175; square-off 15:20 close. Entry premium = entry bar's open. Basis: premiums per 1 lot (lot 65), cost ₹220/trade.
- Expiry determination is route-governed (Upstox instruments master): November monthly in force = **2026-11-23** (Tue 2026-11-24 is a holiday — the master lists the monthly at Mon 11-23); November weekly expiry days = **2026-11-03, 2026-11-09, 2026-11-17** (11-09 is the shifted Tue 11-10 weekly).
- **December judging window is unaffected**: DEC-S1's pass/kill is judged on December as pre-registered. November days are extra forward evidence, labelled as such everywhere.

## SHADOW 3 — Bank Nifty "v21" RAW (log: `november_shadow_v21_bank_log.csv`)

**Added 2026-11-05 on Chandu's direct order (09:14 IST):** v21 is the frozen December candidate but had zero November forward days — the other best versions were wired as November shadows on 2026-11-04 and raw v21 was left out. SHADOW v21 fixes that: the December candidate now accrues November forward evidence under its own name.

**Rules in force** — the RAW v21 book, unmodified: the exact Jan–Oct assembly behind `bank_engine_r6_v21_trades.csv` (B2 causal pool + NS1 second leg + NS3 GD/GU legs + S3A/S3E/S3D state add-ons; UNIQUE-ONCE per (date, direction); NS1 CE dropped by the v21 frame rule; v21 segment exit geometry — V15 segments / P21 for NS3 / state geometry for S3 — square-off 15:20). **NO EVE-04 give-back lock, NO EVE-05 skip, NO re-entry, NO add-ons.** Basis: option premiums per 1 lot (lot 30), cost ₹220/trade. The scorer's Jan–Oct guard (99 legs / +₹83,650.50) re-verifies before any November row is written, exactly as for v22 — v21 and v22 rows come from the same single assembly per day; v21 is formatted from the pristine rows before v22's Step A/B are applied.

**How v21 differs from SHADOW v22:** v22 = the v21 frame PLUS Step A (BANK-EVE-04 FC-2 give-back lock on NS1 second legs) PLUS Step B (BANK-EVE-05: Skill V3 PE legs entering before 10:30 removed). v21 = neither step — every assembled leg trades, with v21's own exits. Concrete consequence, 2026-11-02: the day's only assembled leg (Skill V3 PE 54800 @681.95) is a v21 trade (stopped 10:25 → −₹1,720) but only an EVE-05-SKIP disclosure in v22 (no trade). Both books run, separately labelled, never merged; v21's December judging is unaffected — November days are its forward evidence, labelled as such.

## SHADOW 4 — Day Trader Skill standalone, both indices (logs: `november_shadow_skill_bank_log.csv`, `november_shadow_skill_nifty_log.csv`)

**Added 2026-11-05 on Chandu's continuing "run them" direction:** the Day Trader Skill had only one-off scores (Nov 2–4 and October); it now accrues daily November forward evidence under its own name, like the other shadows.

**Rules in force** — the Skill V3 standalone book, unmodified from the one-off runs (`skill_standalone_nov2_4_2026-11-05.md`, `skill_standalone_october_2026-11-05.md`): every Skill V3 key the U1 construction generates on the day (solo legs included — the frozen primaries' B2/C3 blocks are NOT applied; if Skill fired, the leg counts). Strike = ATM nearest 100 to spot at the entry bar; expiry = monthly in force (2026-11-23 for November, both indices); entry premium = open of the entry 5-min premium candle. Exits: Bank **G0** (stop −50 / target +90, stop before target incl. entry bar, square-off 15:10); Nifty **G7** (stop −50; +90 → lock entry+50; target +150; square-off 15:10). Basis: option premiums per 1 lot (Bank 30 / Nifty 65), cost ₹220/trade. The scorer derives the Skill key from the same `live_signal_producer` U1 machinery the EOD logging uses (Skill derivation depends only on the day's spot bars + prev daily, so it is unaffected by the other books' state). A `--skill-only` mode backfills the two Skill logs without touching any other log.

## Scoring route (all shadows)

- Scorer: `~/workspace/trading/november_shadow_score.py` (premium candles via `november_shadow_fetch.py` — live contracts from the instruments master + v3 historical endpoint; expired contracts via the expired-instruments route; browser User-Agent on every Upstox request; HTTP 429 = hard stop). Since 2026-11-05 the same run also writes the SHADOW v21 log (`november_shadow_v21_bank_log.csv`) from the same Bank assembly, and the two SHADOW Skill logs (`november_shadow_skill_bank_log.csv`, `november_shadow_skill_nifty_log.csv`) from the day's Skill V3 keys.
- Cron `november-shadow-scoring` runs Mon–Fri ~15:32 IST: scores today plus any November trading day still missing or NOT_COMPUTED in any shadow log — Bank v22, Bank v21, Nifty DEC-S1, Skill Bank, Skill Nifty (idempotent — a day's rows are replaced on re-score). Silent on routine success; alerts the combined chat on failure or NOT_COMPUTED.
- Every run of the Bank scorer first reproduces the Jan–Oct v21 assembly exactly (99 legs / +₹83,650.50) as a guard; a failed guard writes nothing. Construction machinery was validated before first use: NS1 generator copy = audited original (65/65 legs), NS3 score_day = stored file sample (exact), DEC-S1 Component A admission = standing book (35/35 legs).
- A day whose candles are unavailable is logged **NOT_COMPUTED with the reason and excluded from all totals — never estimated.**

## Where the daily numbers appear

- 15:45 `november-paper-daily-stats` message: labelled lines per index section — Bank "SHADOW v22", "SHADOW v21" and "SHADOW Skill", Nifty "SHADOW DEC-S1" and "SHADOW Skill" — never added to primary figures.
- Evening engines (Bank 17:15 / Nifty 17:32): shadow trades journalled with their SHADOW labels; MTD lines in the reports and in `segment_floor_tracker.md` (Bank: SHADOW v22 beside TUNED SHADOW BOOK v2, SHADOW v21 as its own line; Nifty: DEC-S1 November MTD labelled December-candidate forward evidence).
- The per-shadow logs above are the record of truth.

## Start and first scores

- Live from **Wed 2026-11-04**; Mon 2026-11-02 and Tue 2026-11-03 covered retrospectively from stored candles, labelled **CANDLE-SCORED**.
- **2026-11-02** — Bank v22: no trade (the day's only assembled leg, Skill V3 PE 54800 @681.95, removed by EVE-05; skip row logged). Nifty DEC-S1: 1 trade — B leg PE 23300 (exp 2026-11-23), entry 10:05 @288.00, breakeven-armed then stopped at entry 14:35 @288.00 → **−₹220** (cost only).
- **2026-11-03** — both shadows **NOT_COMPUTED**: index spot 5-minute candles for 2026-11-03 were not served by the v3 historical endpoint at scoring time (empty response; local captures partial — Nifty spot to 13:45 only). The scorer re-runs the day automatically once the full day is served; DEC-S1 is expected to field a Component C leg that day (Skill V3 CE key, weekly expiry 2026-11-03) once scorable.
- Shadow MTD after the first scoring: Bank v22 ₹0 (0 trades, 1 day NC) · Nifty DEC-S1 −₹220 (1 trade, 1 day NC).
- **SHADOW v21 live from Thu 2026-11-05** (owner order 09:14 IST); Mon 2026-11-02 → Wed 2026-11-04 backfilled the same morning from stored/served candles, labelled **CANDLE-SCORED**. Backfill results — **2026-11-02:** 1 trade, Skill V3 PE 54800 (exp 2026-11-23), entry 10:20 @681.95 → stop 10:25 @631.95 → **−₹1,720** (the leg v22 skips under EVE-05; raw v21 takes it). **2026-11-03:** no trade (NS1 generated 1 CE leg, dropped by the v21 frame rule; assembled rows 0). **2026-11-04:** no trade (spot candles served at backfill time; Skill filtered, NS1 CE dropped, 2 S3 candidates not assembled; assembled rows 0). Guard on every backfill day: 99 legs / +₹83,650.50 OK. SHADOW v21 MTD after backfill: **−₹1,720** (1 trade, 0 days NC).

- **SHADOW Skill live from Thu 2026-11-05**; Mon 2026-11-02 → Wed 2026-11-04 backfilled the same morning via `--skill-only`, labelled **CANDLE-SCORED**, and verified leg-for-leg against the one-off run (`skill_standalone_nov2_4_2026-11-05.md`) — exact match, no discrepancy. Backfill results — **Bank:** Nov 2 PE 54800 @681.95 → stop −₹1,720 · Nov 3 CE 55500 @841.85 → stop −₹1,720 · Nov 4 CE 55800 @788.00 → stop (entry bar) −₹1,720 → **MTD −₹5,160 (3 trades)**. **Nifty:** Nov 2 CE 23300 @363.00 → stop −₹3,470 · Nov 3 CE 23600 @355.75 → square-off +₹2,688.75 · Nov 4 no leg → **MTD −₹781.25 (2 trades)**. Thu 2026-11-05 scores at the normal 15:32 run (Nifty Skill fired a solo CE today — signal 09:45, entry 09:50 — and will be caught by that run, not scored early).

This job family ends with November: the scoring cron can be disabled after 2026-11-30.
