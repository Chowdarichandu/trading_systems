# THE RECURSIVE ENGINE — Nifty ONLY (built 2026-10-31)

Built for the same reason as the Bank engine: Chandu asked for the recursive system on the index work (2026-10-31 13:15 IST), and then set the target (13:17 IST): **₹50,000/month including Nifty and Bank Nifty together.** The Bank engine (`bank_RECURSIVE_ENGINE.md`) and this engine are a matched pair — same loop, same controls, separate indexes, separate files, separate verdicts.

## Scope — hard boundaries
- **Nifty ONLY.** This engine never touches Bank Nifty, never touches stocks. Its files, logs, charts and verdicts are Nifty-only. Nothing is pooled with any other index.
- **Index OPTIONS only, 1 lot (Nifty lot 65), premiums only.** Spot is trigger/levels only, never the traded instrument. No futures numbers in an options report.
- **Paper only. Real money = ₹0. No live orders.**
- **November paper is FROZEN and untouched.** NF-PAPER-C3G7 (`november_paper_nifty_C3G7_frozen.md`, log `november_paper_nifty_log.csv`) runs Nov 2026-11-02 → 2026-11-30 exactly as frozen, with no re-tuning during November. This engine builds a *next* candidate on Jan–Oct 2026 history; its candidate is judged later on fresh data (December), never adopted on in-sample results alone.

## Incumbent (the book to beat)
**C3+G7 = confirmed-only legs (≥2 source systems agree on the (date, index, direction) key) + runner-lock50 exit** (after +90, stop → entry+50, second target +150; initial stop −50; stop before target on every bar incl. entry bar; square-off 15:10). UNIQUE-ONCE per (date, index, direction), earliest entry. Cost ₹220/trade. Net = (exit − entry premium) × 65 − ₹220. Entry premium = open of the 5-min option candle at the entry bar. Strike ATM nearest 100.

Reference (premiums, Jan–Oct 2026, from `aggressive_oct_nifty.md` / `november_paper_nifty_C3G7_frozen.md`):
- Jan–Oct: **+₹66,619.25**, 56 trades, 37.5% full-target (G7 definition: premium reached +90 at any point), **no red month-ends**, 1.38 trades/week
- October: **+₹18,805.25**, 4 trades, 75.0% FT, 1.11/week
- Months: Jan +16,643.75; Feb +11,264.00; Mar +8,210.00; Apr +4,240.75; May −5,793.00; Jun +9,131.00; Jul +10,809.00; Aug −4,129.25; Sep −2,562.25; Oct +18,805.25 — three negative individual months (May, Aug, Sep), every month-end cumulative green.
- Baseline underneath it, U1-N1 alone: Jan–Oct +₹25,159.00 (108 trades, 25.9% FT, 2.66/week).
- **Known weakness: frequency.** C3+G7's confirmed-only rule trades only ~1.38/week. For November paper Chandu delegated and accepted that trade (money over frequency, November only). For this engine, frequency is a live problem to fix, not a settled acceptance: a challenger that lifts frequency toward ≥2/week *without* giving back the net is the highest-value direction — but net + FT + no-red-month-end must hold together (see gate).

## Goal (Chandu, 2026-10-31 13:17 IST)
- **Target: ₹50,000/month across the two index systems together — Nifty + Bank Nifty — on premiums per 1 lot each = ₹500,000 over Jan–Oct 2026 as the combined aspiration.**
- Reporting rules unchanged: each index in its own section with its own numbers; no joint adoption verdict; the combined target counts for nothing if one index is negative or closes a month-end red (his standing rule).
- This engine maximises the **Nifty contribution** under the gate below, until saturation — no solo threshold at which it may stop early. Starting pace: Nifty ~₹6,662/month; Bank incumbent ~₹2,370/month; combined ~₹9,032/month vs the ₹50,000 line (gap ~₹40,968/month). Report the plateau honestly against that line, with the gap and the untried families named.

## Success gate for any cycle (Nifty alone, all must hold)
Total rises vs the incumbent book AND no red month-end is created AND full-target rate does not collapse. Frequency: a cycle that raises frequency toward ≥2/week while holding the other three is preferred; a cycle that *cuts* frequency further must raise the total by enough to be reported as an explicit quality-for-frequency trade for Chandu to judge — it is not silently banked as a plain win. UNIQUE-ONCE counting only.

## Month order (his method)
**October first**, then September, then August … January. Diagnose the target month, fix with ONE ex-ante rule, apply to all months, re-check all previously secured months; a fix that un-secures one is rejected. Note the known diagnosis order inside this book: May/Aug/Sep are the negative individual months, and October's +₹18,805 came from only 4 trades — concentration is a standing warning (see lessons).

## The loop (one cycle — minutes, back-to-back, no waiting, no approval waits)
1. **IDENTIFY** — read `nifty_engine_state.json` and `nifty_engine_lessons.md` first. Diagnose the target month from the working book's trades, with numbers.
2. **FIX** — ONE rule-fix, ex-ante, applies to all months, never a date/month filter, not in the tried registry. Freeze it in `nifty_engine_frozen.md` BEFORE scoring.
3. **APPLY + CONTROLS IN THE SAME RUN** — timing audit on EVERY trade (entry ≥ when its qualifying information existed; count violations); placebo on the same qualifying days; halves split (Jan–May / Jun–Oct); full month table with month-end cumulative closes; ex-top-3-trades stress; independent re-sum to the paisa. **No number is quoted to Chandu before these controls pass.**
4. **DECIDE (banking rule)** — BANK if it improves the target month and breaks nothing (gate above), even partially. REJECT if it breaks something or does not improve the target; record it in the rejected list with the leg it failed. Append to `nifty_engine_log.md`, add lessons to `nifty_engine_lessons.md`, update `nifty_engine_state.json`.
5. **RECURSE immediately.** A ~15-minute watchdog exists only to restart a stalled chain; it checks `cycle_lock` and skips if a fresh cycle is running.

## Challenger rule (Recursive Self Improvement)
When a target stalls (2 consecutive no-bank cycles) or every 3rd cycle, BUILD A CHALLENGER system from the lessons — a new assembly/mechanism consistent with every lesson (e.g. a frequency-lifting confirmation variant, a state gate, a second-leg mechanism that is NOT the NS add-ons this channel has already rejected) — frozen before scoring, full controls, replaces the incumbent only on the gate.

## Saturation / termination
- No fixed cycle count. Run until saturation: peak = the last cycle before one fails to beat the best; confirm with 3 consecutive no-beat cycles, then report the full climb and the plateau against the ₹50,000/month combined line (Nifty contribution stated separately).
- **SUCCESS (this engine's part):** a frozen Nifty book, together with the Bank engine's frozen book at the same date, reaches ≥₹500,000 Jan–Oct across the two (each reported separately) with no red Nifty month-end and the gate held → freeze as `nifty_engine_candidate_spec.md` for fresh-data (December) judging.
- **BREAK-EVEN / EXHAUSTED:** as in the Bank protocol — reported honestly, naming the resisting month/family.
- Chandu saying stop ends it at any time.

## Reporting (in this combined-view chat)
- Nifty results in a **Nifty section only**: real money ₹0 first, premiums per 1 lot (65) labelled in the same sentence, UNIQUE-ONCE stated, ₹220/trade cost stated.
- Never add Nifty and Bank into one pooled total as a success claim, and no joint verdict. Any adoption verdict for a Nifty candidate belongs to the Nifty channel (chat 202c2254-5191-4e09-927a-263bc8ab5100) after fresh-data judging.

## RUN 2 — added 2026-10-31 13:54 IST (target lowered by Chandu)
Chandu: "Now 20k since 50k is hard." The combined target is now **₹20,000/month (₹200,000 Jan–Oct)** across Nifty + Bank, replacing the ₹50,000 line everywhere in this protocol. Run 1 terminated SATURATED at the Cycle-8 book (+₹92,437.75); that plateau stands as Run 2's starting book. Run 2 is **challenger-only**: every cycle must be a NEW mechanism consistent with the lessons registry — re-trying a closed family (geometry/lock/arm sizes, early exits, SA2D, RATCHET150, NS add-ons) is not a valid cycle. The CH3 flagged variant remains flagged and NOT banked unless Chandu explicitly decides it — Run 2 does not bank it by itself. Termination: SUCCESS (combined ₹200,000 reached with the Bank book at the same date, gates intact) or saturation again after 3 consecutive no-beat Run-2 cycles, reported against the ₹20,000/month line.
