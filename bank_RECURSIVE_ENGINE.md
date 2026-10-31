# THE RECURSIVE ENGINE — Bank Nifty ONLY (built 2026-10-31, at Chandu's request in the combined-view chat)

His words (2026-10-31 13:15 IST): do the same recursive system for Bank Nifty as for stocks — build a strategy, apply it, if it fails learn from the mistake, fix it, and iterate in multiple cycles until the goal is achieved.

## Scope — hard boundaries
- **Bank Nifty ONLY.** This engine never touches Nifty, never touches stocks. Its files, logs, charts and verdicts are Bank-only. Nothing is pooled with any other index.
- **Index OPTIONS only, 1 lot (Bank lot 30), premiums only.** Spot is trigger/levels only, never the traded instrument. No futures numbers in an options report.
- **Paper only. Real money = ₹0. No live orders.**
- **November paper is FROZEN and untouched.** BNF-PAPER-V1 (`november_paper_bank_V1_frozen.md`, log `november_paper_bank_log.csv`) runs Nov 2026-11-02 → 2026-11-30 exactly as frozen, with no re-tuning during November. This engine builds a *next* candidate on Jan–Oct 2026 history; it does not change, re-score or interfere with November paper. Its candidate is judged later on fresh data (December), never adopted on in-sample results alone.

## Incumbent (the book to beat)
**V1 = B2 + NS1 second legs**, UNIQUE-ONCE per (date, index, direction), earliest entry. G0 exits: stop −50 / target +90 premium points, stop checked before target, square-off 15:10. Cost ₹220/trade. Net = (exit − entry premium) × 30 − ₹220. Entry premium = open of the 5-min option candle at the entry bar. Strike ATM nearest 100.

Reference (premiums, Jan–Oct 2026, from `aggressive_oct_bank.md` / `november_paper_bank_V1_frozen.md`):
- Jan–Oct: **+₹23,703.50**, 130 trades, 42.3% full-target, **no red month-ends**, ~3.20 trades/week
- October: **+₹17,160.00**, 12 trades, 75.0% full-target, 3.33/week
- Baseline underneath it, U1-B2 alone: Jan–Oct +₹18,731.50, 89 trades, 43.8% FT — with a RED January month-end close (−₹1,920.00) and a weak Jun–Sep stretch (Jun −₹9,560, Jul −₹8,800, Aug −₹7,301, Sep −₹2,024.50 as individual B2 months).

## Goal for this engine (updated 2026-10-31 13:17 IST by Chandu)
- **Target: ₹50,000/month across the two index systems together — Bank Nifty + Nifty — on premiums per 1 lot each = ₹500,000 over Jan–Oct 2026 as the combined aspiration.** Chandu set this combined target in the combined-view chat; it supersedes the earlier Bank-only ₹20,000/month bar for goal-tracking. It does NOT change the reporting rules: each index is always reported in its own section with its own numbers, and there is no joint adoption verdict — a combined target is not a pooled success claim, and it counts for nothing if one index is negative or closes a month-end red (his standing rule).
- This engine's job is therefore to **maximise the Bank contribution** under the success gate below, until saturation — there is no solo Bank threshold at which it may stop early. Starting pace (premiums, Jan–Oct averages): Bank V1 ~₹2,370/month; the Nifty incumbent (its own engine) ~₹6,662/month — so the combined starting pace is ~₹9,032/month against the ₹50,000 line, a gap of ~₹40,968/month. Report the plateau honestly against that line. Do not import the stocks ₹75k/month goal into this channel.
- **Success gate for any cycle** (all must hold, Bank alone): total rises vs the incumbent book AND no red month-end is created AND frequency stays ≥2 trades/week AND full-target rate does not collapse (no adoption-style pass on net alone — net + FT + frequency move together, per the standing replacement rule).
- Quality over quantity still applies: 2–3 quality trades/week with a meaningful monthly total beats many trades for a small total. UNIQUE-ONCE counting only — never double-count the same date+direction.

## Month order (his method, same as stocks)
**October first**, then September, then August … January. Each month in turn is the target: diagnose why it is weak, fix with ONE ex-ante rule, apply to all months, and move on only when it is secured. Every later fix is re-checked against all previously secured months — a fix that un-secures a secured month is rejected. Note: V1's October is already its strongest month (+₹17,160); October-first here means first *try to lift October toward ₹20,000 without breaking Jan–Sep*, then work the weak Jun–Sep stretch, which is where Jan–Oct is actually lost.

## The loop (one cycle — minutes, back-to-back, no waiting, no approval waits)
1. **IDENTIFY** — read `bank_engine_state.json` and `bank_engine_lessons.md` first. Target = the current month in the order. Diagnose its weakness from the working book's trades, with numbers (which component / direction / exit reason / time band loses, and how much).
2. **FIX** — ONE rule-fix from the diagnosis: ex-ante, applies to all months, never a date filter or per-month parameter, not in the tried-families registry. Freeze the exact rule in `bank_engine_frozen.md` BEFORE scoring.
3. **APPLY + CONTROLS IN THE SAME RUN** (controls gate — non-negotiable, from the 2026-10-31 fake-data failure):
   - Timing audit on EVERY trade: entry time ≥ the moment its qualifying information existed; count violations, do not sample.
   - Placebo control on the same qualifying days (shifted entry or opposite direction); the real rule must beat it clearly.
   - Halves split (Jan–May / Jun–Oct) and full month table with month-end cumulative closes.
   - Ex-top-3-trades stress: remove the top 3 contributing trades and re-score; a book that turns negative without them is flagged, not headlined.
   - Re-sum the trade file independently; totals must match to the paisa before anything is reported.
   - **No number is quoted to Chandu before these controls pass.**
4. **DECIDE (banking rule)** — BANK the fix if it improves the target month AND breaks nothing (no secured month un-secured, no new red month-end, total does not fall, FT and frequency hold the gate above, audit clean) — even if the improvement is partial. REJECT if it breaks something or does not improve the target; record it in the rejected list with the leg it failed. Append the cycle to `bank_engine_log.md`, add any new lesson to `bank_engine_lessons.md`, update `bank_engine_state.json`.
5. **RECURSE immediately** — next cycle starts from the new state at once. Cycles complete in minutes, never on a 2-hour cadence. A ~15-minute watchdog schedule exists only to restart the chain if it stalls; it must check `cycle_lock` in the state and skip if a fresh cycle is already running.

## Challenger rule (Recursive Self Improvement — his meaning of "RSI")
The engine does not only patch V1. When a target month stalls (2 consecutive cycles bank nothing on it) — or every 3rd cycle, whichever comes first — the cycle must **BUILD A CHALLENGER SYSTEM** from the lessons: a new assembly or mechanism consistent with every lesson in `bank_engine_lessons.md` and contradicted by none (e.g. a new component family, a state-gated variant, a second-leg mechanism), frozen before scoring and scored under the full controls above. A challenger replaces the incumbent only on the success gate (total, no red month-end, FT, frequency — together). Otherwise it is recorded as a rejected version with its lesson.

## Saturation / termination
- **No fixed cycle count.** Run until saturation: the first cycle whose best attempt fails to beat the running best is evidence the peak was the previous cycle — confirm with 3 consecutive no-beat cycles, then stop and report the full climb and the plateau against the ₹20,000/month line.
- **SUCCESS (for this engine's part):** a frozen Bank book, together with the Nifty engine's frozen book at the same date, reaches the ₹50,000/month combined pace (≥₹500,000 Jan–Oct across the two, each index reported separately) with no red month-end in Bank, FT and frequency gates held → freeze it as `bank_engine_candidate_spec.md` for fresh-data (December) judging, terminated = "SUCCESS". Short of that, the engine runs to saturation — it does not stop at any smaller solo number.
- **BREAK-EVEN / EXHAUSTED:** all months' cumulative closes ≥0 with no total-raising fix in 2 cycles, or 3 no-bank cycles with a target still resisting → final report naming the resisting month/family and every diagnosis. A plateau is reported honestly, never dressed up.
- Chandu saying stop ends it at any time.

## Reporting (in this combined-view chat)
- Bank results are reported in a **Bank Nifty section only**, real money ₹0 first, premiums per 1 lot (30) labelled in the same sentence, UNIQUE-ONCE counting stated, costs ₹220/trade stated.
- Never add Bank and Nifty into one pooled total, and no joint verdict. Any adoption verdict for a Bank candidate belongs to the Bank channel (chat e1c1e00e-144d-458a-8b5c-2c66db778095) after fresh-data judging — this engine only discovers and freezes candidates.

## RUN 2 — added 2026-10-31 13:54 IST (target lowered by Chandu)
Chandu: "Now 20k since 50k is hard." The combined target is now **₹20,000/month (₹200,000 Jan–Oct)** across Bank + Nifty, replacing the ₹50,000 line everywhere in this protocol. Run 1 terminated SATURATED/EXHAUSTED at book v4 (+₹46,476.50); that plateau stands as Run 2's starting book. Run 2 is **challenger-only**: every cycle must be a NEW mechanism consistent with the lessons registry — re-trying a closed family (exit geometry, target/stop size, NS add-on families, entry gates already tested) is not a valid cycle. Termination: SUCCESS (combined ₹200,000 reached with the Nifty book at the same date, gates intact) or saturation again after 3 consecutive no-beat Run-2 cycles, reported against the ₹20,000/month line.
