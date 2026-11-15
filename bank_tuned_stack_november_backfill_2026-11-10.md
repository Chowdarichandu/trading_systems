# Bank Nifty TUNED STACK — November backfill (Nov 2–9, 2026)

**RETROSPECTIVE BACKFILL** — scored on 2026-11-10 from stored/served
candles, after the days traded. This is **not a live run and not a
gate**. Paper only, real money ₹0. Basis: option premiums per 1 lot
(lot 30), cost ₹220/trade. Owner ask 2026-11-10: "run the tune stack
from November 1 to November 9th so we can see how it is going."
(Nov 1 was a Sunday; Nov 7–8 weekend; the only November days with
candles are Mon 2, Tue 3, Wed 4, Thu 5, Fri 6, Mon 9.)

## The stack (frozen definition)

SHADOW v22 frame (v21 assembly + EVE-04 NS1 give-back lock + EVE-05
pre-10:30 OR-break PE skip) **+ EVE-06(a) re-entry** (after a v22 leg
stops at full −50: first 5-min spot close back through the
morning-range extreme at/after 12:00 re-enters the same side ATM at
next bar open, G0 exits, max 1/day, skipped if day P&L ≤ −₹3,000)
**+ c4 runner extension** (PLAIN legs, non-expiry: +90 locks +90 and
runs to +180 instead of exiting) **+ v1 NS3/S3 band add-ons**
(band-dropped [400,550) candidates re-admitted UNIQUE-ONCE).
Jan–Oct reference: +₹123,471.50 / 115 legs
(`bank_aggressive_tune_2026-11-04.md`).

## Sanity anchor — PASSED on all 6 days

The v22 intermediate reproduced the written SHADOW v22 November log
exactly (every leg's strike, entry/exit times and premiums, exit
reason and net; Nov 2's EVE-05 skip counted), and the raw assembly
reproduced the SHADOW v21 log exactly. Each day's assembly also
re-asserted the frozen Jan–Oct reproduction (99 legs,
+₹83,650.50) before the day's rows were read.

## Per-day table

| Date | Legs (component · direction · strike · entry → exit) | Day net |
|---|---|---|
| Mon 2026-11-02 | none — the day's only candidate (Skill V3 PE 54800, 10:20 @ 681.95) is EVE-05-skipped inside the v22 frame, so no stack leg exists; with no stopped v22 leg there is no re-entry population, and the day had zero NS3/S3 candidates | ₹0.00 |
| Tue 2026-11-03 | none | ₹0.00 |
| Wed 2026-11-04 | v22 frame · S3-R1 · PE 55800 · 09:55 @ 715.30 → 10:25 @ 805.30 · runner_stop · **+₹2,480.00** | **+₹2,480.00** |
| Thu 2026-11-05 | none | ₹0.00 |
| Fri 2026-11-06 | none | ₹0.00 |
| Mon 2026-11-09 | v22 frame · Skill V3 · PE 58900 · 10:45 @ 815.40 → 10:45 @ 765.40 · stop · **−₹1,720.00** | **−₹1,720.00** |

**November total (Nov 2–9): +₹760.00 on 2 legs.**

## What each stack component contributed in November

| Component | Legs | Net |
|---|---|---|
| v22 frame (EVE-04/05 included) | 2 | +₹760.00 |
| c4 runner extension | 0 changed legs | ₹0.00 |
| EVE-06(a) re-entry | 0 legs | ₹0.00 |
| v1 NS3/S3 band add-ons | 0 legs | ₹0.00 |

Why the extra layers added nothing — each checked, none approximated:

- **c4:** neither November v22 leg is a PLAIN leg — the Nov 4 S3-R1
  leg already carries a lock (runner params), and the Nov 9 Skill
  leg stopped on its entry bar before ever reaching +90. No leg's
  exit changed.
- **EVE-06(a) re-entry:** only Nov 9 had a stopped v22 leg. Its
  trigger scan (from 12:00, PE side: close back below the morning
  low 58,877.85) never fired — the lowest afternoon close was
  59,085.35; spot ran up +835 after the stop instead. Verified
  directly on the day's bars. Nov 2's stopped leg never entered the
  v22 book (EVE-05 skip), so it is outside the registered
  population by construction.
- **v1 add-ons:** no November day produced a band-dropped NS3/S3
  candidate (Nov 2 and Nov 9 had zero NS3/S3 candidates at all;
  Nov 4's S3 leg entered at 715.30, outside the [400,550) band, and
  was admitted by the assembly itself).

## NOT_COMPUTED

None. All 6 days scored; every leg's candles were available. No day
and no leg is estimated.

## Reading

Over the six completed November days the tuned stack is **identical
to plain SHADOW v22: +₹760.00** — the stack's extra machinery never
got a November leg to act on. For comparison over the same days:
frozen primary −₹6,880.00 (4 trades; the stack's frame skips the
Nov 2 primary leg via EVE-05 and never takes Nov 3's NS1 leg),
SHADOW v21 −₹960.00. The stack's Jan–Oct edge (+₹123,471.50) came
from layers that fired rarely; six days is far too small a sample
to judge them — this backfill only shows the stack did no worse
than v22 in November's first week, and that its November number so
far rests entirely on the v22 frame.

Files: `bank_tuned_stack_november_backfill_trades.csv` (the 2 legs,
producible), `bank_tuned_stack_november_backfill.py` (scorer;
anchor-checked assembly replicated from `november_shadow_score.py`,
re-sims via its `replay_overlay`; shadow state loaded read-only,
never saved; no frozen log or spec modified).
