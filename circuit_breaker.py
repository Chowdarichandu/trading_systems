#!/usr/bin/env python3
"""CIRCUIT BREAKER — the owner's bleed-control rule (2026-11-03),
one deterministic implementation shared by the Jan-Oct / November
replays, the worst-window stress test, and the forward daily
record for TUNED STACK v2 (circuit_breaker_stack.py).

THE RULE (index books; it binds the shadow/December layer, never
the frozen primaries):
  - 3 consecutive losing days  -> pause the next 3 trading days;
  - month-to-date net <= -Rs5,000 -> pause the rest of the month.

SEMANTICS (fixed here, matching the tracker's day-sign accounting
that fired the legacy line on 2026-11-05 after Nov 2/3/4):
  - A "losing day" is a trading day whose realised day net < 0.
    A no-trade day (net 0) is not a losing day and resets the
    streak — this is why the stack's November (losses Nov 9/12/13
    with a no-trade Nov 11 between) never trips.
  - The streak counts consecutive trading days, across month
    boundaries; MTD is per calendar month and resets monthly.
  - Trips are evaluated at the close of a traded (non-paused) day:
    the MTD leg is checked first (it dominates — rest of month);
    the streak leg then pauses exactly the next 3 trading days and
    the streak resets to 0.
  - On a paused day the book does not trade: realised net = 0, the
    day's hypothetical net is recorded as suppressed, MTD and the
    streak do not move.

OPTIONAL THIRD LEG — ROLL10 (frozen 2026-11-14 in
scenario_proofing_2026-11-14.md, "BREAKER GAP" section; DISABLED
by default so every Item 3 caller reproduces its replay exactly;
the December-layer runner enables it only if the frozen adoption
criteria pass):
  - At the close of a non-paused day, if the sum of the book's
    realised day-nets over the trailing `roll10_window` (10)
    calendar trading days including today (paused days contribute
    their realised 0; the window spans month boundaries) is
    <= `roll10_floor` (-Rs5,000), the leg trips and pauses the
    next `roll10_pause` (3) trading days.
  - Evaluation order at a close: MTD -> ROLL10 -> STREAK; at most
    one trip per close. Pauses never stack or extend (trips are
    evaluated only on non-paused days). On a ROLL10 trip the
    losing streak resets to 0 (the streak leg's own convention);
    MTD is untouched. After the pause, evaluation resumes on the
    trailing window as it stands — no immunity period.
OPTIONAL FOURTH LEG — HWM-DD (frozen 2026-11-14 in
scenario_proofing_2026-11-14.md, "BREAKER GAP — HWM-DD LEG:
FREEZE"; DISABLED by default so every Item 3 / ROLL10 caller
reproduces its replay exactly; the December-layer runner enables
it only if the frozen adoption criteria pass):
  - Within a calendar month, HWM is the highest realised MTD
    reached at any prior close this month, floored at the
    month-start baseline 0 (HWM >= 0 always; it resets to 0 with
    MTD at each month start and does not move on paused days).
    At the close of a non-paused day, if HWM - MTD >=
    `hwmdd_drop` (Rs5,000) the leg trips. When HWM = 0 the
    condition is exactly MTD <= -Rs5,000 — the leg reduces to the
    MTD leg, which is checked first and takes the trip label.
  - Action: pause the rest of the calendar month — exactly the
    MTD leg's pause shape. The losing streak is NOT reset by an
    HWM-DD trip and does not move on paused days (exactly the
    MTD leg's streak treatment).
  - Evaluation order at a close: MTD -> HWM-DD -> ROLL10 ->
    STREAK; at most one trip per close. Pauses never stack or
    extend (trips are evaluated only on non-paused days).
Paper only. Pure functions; no I/O, no API.
"""

STREAK_N = 3
STREAK_PAUSE_DAYS = 3
MTD_FLOOR = -5000.0
ROLL10_FLOOR = -5000.0
ROLL10_WINDOW = 10
ROLL10_PAUSE_DAYS = 3
HWMDD_DROP = 5000.0


def simulate(days, hypothetical, roll10_floor=None,
             roll10_window=ROLL10_WINDOW,
             roll10_pause=ROLL10_PAUSE_DAYS,
             hwmdd_drop=None):
    """days: ordered list of trading-day strings (YYYY-MM-DD).
    hypothetical: {date: day net the book would have made with no
    breaker} (missing date = 0.0). Returns (records, summary).
    Each record: date, hypothetical_net, realised_net, paused,
    pause_kind ('' / 'STREAK' / 'ROLL10' / 'MTD' / 'HWMDD'),
    mtd_realised (after the day), streak (after the day), trip
    ('' / 'STREAK' / 'ROLL10' / 'MTD' / 'HWMDD'), roll10_sum
    (trailing realised window sum at the day's close, None until
    the window is complete). With the HWM-DD leg enabled, records
    also carry hwm (the month's high-water mark after the day)
    and hwm_dd (HWM - MTD measured at the day's close, from
    prior-close HWM on non-paused days).
    roll10_floor=None disables the ROLL10 leg and hwmdd_drop=None
    disables the HWM-DD leg (both off = Item 3 behaviour,
    byte-identical)."""
    records = []
    streak = 0
    mtd = 0.0
    pause_left = 0
    pause_src = ""
    mtd_paused = False
    rom_src = ""
    hwm = 0.0
    cur_month = None
    trips = []
    realised_hist = []

    def roll10_sum():
        if len(realised_hist) < roll10_window:
            return None
        return round(sum(realised_hist[-roll10_window:]), 2)

    for day in days:
        month = day[:7]
        if month != cur_month:
            cur_month = month
            mtd = 0.0
            mtd_paused = False
            rom_src = ""
            hwm = 0.0
        hyp = round(float(hypothetical.get(day, 0.0)), 2)
        paused = mtd_paused or pause_left > 0
        if paused:
            kind = rom_src if mtd_paused else (pause_src or "STREAK")
            if pause_left > 0 and not mtd_paused:
                pause_left -= 1
            realised_hist.append(0.0)
            rec = dict(date=day, hypothetical_net=hyp,
                       realised_net=0.0, paused=True,
                       pause_kind=kind, mtd_realised=round(mtd, 2),
                       streak=streak, trip="",
                       roll10_sum=roll10_sum())
            if hwmdd_drop is not None:
                rec["hwm"] = round(hwm, 2)
                rec["hwm_dd"] = round(hwm - mtd, 2)
            records.append(rec)
            continue
        realised = hyp
        realised_hist.append(realised)
        mtd = round(mtd + realised, 2)
        streak = streak + 1 if realised < 0 else 0
        trip = ""
        r10 = roll10_sum()
        dd = round(hwm - mtd, 2)
        if mtd <= MTD_FLOOR:
            trip = "MTD"
            mtd_paused = True
            rom_src = "MTD"
            trips.append(dict(date=day, kind="MTD", mtd=mtd))
        elif hwmdd_drop is not None and dd >= hwmdd_drop:
            trip = "HWMDD"
            mtd_paused = True
            rom_src = "HWMDD"
            trips.append(dict(date=day, kind="HWMDD", mtd=mtd,
                              hwm=round(hwm, 2), drop=dd))
        elif (roll10_floor is not None and r10 is not None
              and r10 <= roll10_floor):
            trip = "ROLL10"
            pause_left = roll10_pause
            pause_src = "ROLL10"
            streak = 0
            trips.append(dict(date=day, kind="ROLL10", mtd=mtd,
                              roll10=r10))
        elif streak >= STREAK_N:
            trip = "STREAK"
            pause_left = STREAK_PAUSE_DAYS
            pause_src = "STREAK"
            streak = 0
            trips.append(dict(date=day, kind="STREAK", mtd=mtd))
        if mtd > hwm:
            hwm = mtd
        rec = dict(date=day, hypothetical_net=hyp,
                   realised_net=realised, paused=False,
                   pause_kind="", mtd_realised=mtd,
                   streak=streak, trip=trip,
                   roll10_sum=r10)
        if hwmdd_drop is not None:
            rec["hwm"] = round(hwm, 2)
            rec["hwm_dd"] = dd
        records.append(rec)
    tot_h = round(sum(r["hypothetical_net"] for r in records), 2)
    tot_r = round(sum(r["realised_net"] for r in records), 2)
    suppressed = round(sum(r["hypothetical_net"] for r in records
                           if r["paused"]), 2)
    summary = dict(days=len(records), total_hypothetical=tot_h,
                   total_realised=tot_r,
                   breaker_effect=round(tot_r - tot_h, 2),
                   suppressed_hypothetical=suppressed,
                   paused_days=sum(1 for r in records if r["paused"]),
                   roll10_enabled=roll10_floor is not None,
                   hwmdd_enabled=hwmdd_drop is not None,
                   trips=trips)
    return records, summary
