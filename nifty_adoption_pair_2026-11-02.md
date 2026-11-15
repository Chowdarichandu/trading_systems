# NIFTY — ADOPTION OF THE FLAGGED PAIR (DEC-S1) — 2026-11-02 16:48 IST

**Segment:** Nifty only. Premiums per 1 lot (65), UNIQUE-ONCE, cost ₹220/trade. Paper only, real money ₹0.
**Direction:** Chandu, 2026-11-02 16:48 IST — "You apply the fix and run again."
**Effect:** the flagged pair (fade-10:05 sleeve + expiry-day sleeve — the DEC-S1 construction) is applied as the Nifty candidate book, effective now. DEC-S1 is re-designated from a labelled December SHADOW candidate to the **adopted December CANDIDATE**.
**Not affected:** the November primary NF-PAPER-C3G7 is UNCHANGED — this adoption governs the candidate/December book only. The standing causal book (+₹54,102.00 Jan–Oct) remains on record as the comparison baseline and is not rewritten.

---

## 1. Verification re-check (run immediately before the adoption was written)

The Cycle-168 regeneration (`nifty_engine_r11_verify.py`) was re-run from the frozen DEC-S1 specification alone (frozen.md ROUND 11, S1–S5), full controls gate in the same run:

- **26/26 pre-registered field checks MATCH** — verdict: **VERIFIED** (again; Round 11 verified the same 26/26).
- Total **+₹91,168.50** Jan–Oct — to the paisa. Legs **97** (A standing 35 · B fade-10:05 49 · C expiry in-pair 13).
- **FT 34.0%** (33/97 full targets). Frequency 2.39/wk.
- **Month table identical to the Cycle-152 record** — Jan +19,211.25 · Feb +5,038.75 · **Mar −11,846.50** · Apr +28,416.00 · May +4,574.00 · Jun −1,331.00 · Jul +5,839.00 · Aug +841.25 · Sep +20,265.25 · Oct +20,160.50.
- Halves +₹45,393.50 / +₹45,775.00 · placebo +₹52,867.25 beaten · ex-top-3 +₹57,703.50 · timing audit 97/0 · NC 0.
- Independent checks by this run, separate from the script's own comparisons: the regenerated leg list (`nifty_engine_r11_decs1_legs.json`) is **identical** to the frozen leg list from Round 11; an **independent re-sum of the month table reproduces +₹91,168.50 exactly**; the pair identity holds — 54,102.00 (A) + 33,624.75 (B standalone) + 3,441.75 (C in-pair) = **91,168.50**.

**No mismatch was found. Nothing was patched.**

## 2. Adoption record (as recorded in `nifty_engine_frozen.md` ADOPTION section and `nifty_engine_state.json` → `adoption_pair`)

Adopted by owner direction, 2026-11-02 16:48 IST, exactly as the CH3-R adoption was recorded (2026-11-02 ~12:46 IST precedent): an owner's adoption over the engine's flag. Under the engine's own rules this book was **NOT BANKED** — the Round 9 Cycle-152 verdict stands, unedited.

**The two failed gate legs, recorded FAILED-AND-WAIVED (waived by the adoption direction; not recorded as passed):**

1. **FT leg — FAILED, waived.** FT **34.0%** vs the standing book's **34.3%** (relative dilution of 0.3 points).
2. **March no-flip leg — FAILED, waived.** March flips from the standing book's **+₹7,895.00** to the pair's **−₹11,846.50** (green → red).

No other gate leg is waived: net, frequency (2.39/wk vs 0.86/wk), halves, placebo, ex-top-3, timing audit, NC and re-sum all passed in full.

## 3. December designation

- DEC-S1 is now the **adopted December CANDIDATE**. Its specification is unchanged (frozen.md S0–S9).
- Its pre-registered December pass/kill **stands as registered in S9**, judged on December 2026 data alone (2026-12-01…12-31): **PASS** iff Dec net > ₹0 AND timing audit clean AND NC = 0 · **KILL** iff Dec net ≤ −₹3,470.00 OR any timing violation · **INCONCLUSIVE** otherwise · NC > 0 → PROVISIONAL, never a pass. Floor-pace context printed beside, never as the test: December ≥ +₹15,000.
- The standing book's December freeze (rules 1–9, of record since Round 10) remains on file as the **comparison**, judged in December in parallel, labelled; neither verdict alters the other.

## 4. Restated position

| Measure | Before (standing book) | After (adopted pair, DEC-S1) |
|---|---|---|
| Jan–Oct 2026 total | +₹54,102.00 | **+₹91,168.50** |
| Monthly pace | ₹5,410.20 | **₹9,116.85** |
| Remaining gap to ₹1,50,000 | ₹95,898.00 | **₹58,831.50** |
| Trades / FT / frequency | 35 / 34.3% / 0.86/wk | 97 / 34.0% / 2.39/wk |

Adoption value over the standing baseline: **+₹37,066.50** (₹210.00 less than the sum of the two flags — two UNIQUE-ONCE key collisions, lesson 72).

**Superseded:** the fade-only alternative (standing + fade-10:05 alone = +₹87,726.75 Jan–Oct) is superseded by this pair adoption and is no longer a live adoption option; its flag record stands unedited in the frozen file and state.
