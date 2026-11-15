#!/usr/bin/env python3
"""SHORT-FOLLOW-T2 (R7-M1) — FORWARD paper deployment, window from Fri 2026-11-13.

Owner directive 2026-11-12 19:21 IST (daily shape specified by the owner
himself: 1 Bank Nifty trade + 1 Nifty trade every day, no idle days) arms
the FREEZE's pre-registered 20-trading-day forward paper run. Paper only,
real money ₹0, no live orders.

This wrapper does NOT re-implement the strategy. It imports the frozen
runner `daily2leg/daily2leg_paper_runner.py` — whose exit engine is a
verbatim port of the gated score_r7.simulate(..., "T2") and whose spec is
daily2leg/FREEZE.md (frozen 2026-11-03, full controls gate PASS, audit
clean) — and re-points ONLY its file globals and window start:

  RUN_START       2026-11-04  ->  2026-11-13 (the Nov-4 window never ran:
                  the owner disarmed it the same day it was frozen; its
                  state/killswitch files are left untouched as that
                  record)
  STATE_FILE      -> ~/workspace/trading/november_shortfollow_state.json
  LOG_CSV         -> ~/workspace/trading/november_shortfollow_log.csv
                     (NEW dedicated forward log — never mixed into any
                     primary or shadow log)
  JOURNAL         -> ~/workspace/trading/november_journal_shortfollow.md
  KILLSWITCH_FILE -> ~/workspace/trading/november_shortfollow_KILLSWITCH
                     (absent = armed; create the file to square off and
                     stop entries, exactly as the frozen runner defines)

Modes (all except --init/--dry-run delegate to the frozen runner's own
commands, unchanged):
  --init           create the forward state (ARMED, run_start 2026-11-13),
                   journal header and log header if missing. No API calls.
  --arm            readiness check (frozen runner's cmd_arm): token route,
                   instruments master, expiries + ATM key band for the
                   next trading day.
  --tick           one intraday evaluation for today (10:00 entries from
                   the 09:55 spot bar; exit scan on completed 5-min bars).
  --wrap [--date]  EOD finalisation: full-candle replay, one row appended
                   to the forward log, journal summary, pass/kill judge.
  --drain          print queued chat messages (JSON array), mark delivered.
  --status         run tally vs the FREEZE pass/kill lines.
  --dry-run DATE   full pipeline on a PAST day (DATE < 2026-11-13 only —
                   enforced, so the forward record can never be backfilled).
                   Read-only wrt state/log/journal; the runner writes its
                   scratch report to daily2leg/dryrun_<DATE>.md.
"""
import sys
import urllib.error
from datetime import date as ddate, datetime, timedelta
from pathlib import Path

TR = Path.home() / "workspace" / "trading"
D2L = TR / "daily2leg"
sys.path.insert(0, str(D2L))

import daily2leg_paper_runner as R  # frozen engine — do not modify that file

WINDOW_START = ddate(2026, 11, 13)

# --- re-point the frozen runner's file globals (strategy code untouched) ---
R.RUN_START = WINDOW_START
R.STATE_FILE = TR / "november_shortfollow_state.json"
R.LOG_CSV = TR / "november_shortfollow_log.csv"
R.JOURNAL = TR / "november_journal_shortfollow.md"
R.KILLSWITCH_FILE = TR / "november_shortfollow_KILLSWITCH"

JOURNAL_HEADER = (
    "# SHORT-FOLLOW-T2 — live paper journal (R7-M1, frozen 2026-11-03)\n\n"
    "Paper only, real money ₹0. Basis: premiums per 1 lot per index "
    "(Bank lot 30, Nifty lot 65), cost ₹220/trade, day = both legs. "
    "Spec: FREEZE.md in this folder. Every entry shows its basis; "
    "every losing day names its failure cause.\n"
    "\nFORWARD RUN armed by owner directive 2026-11-12 19:21 IST — "
    "window Fri 2026-11-13 → Thu 2026-12-10 (20 trading days), judged on "
    "the FREEZE pass/kill lines. Forward log: november_shortfollow_log.csv.\n")


class _ArmApi(R.Api):
    """Arm-check-only Api (data resolution, NOT strategy).

    Repair 2026-11-13: the frozen runner's cmd_arm takes its ATM reference
    close from api.spot_intraday() — TODAY's intraday series. Pre-open that
    series is empty (0 bars), so the 09:05 arm check found "no reference
    close" and resolved 0 keys, even though the same check passed the
    previous evening (when "today" was the completed Nov 12). The reference
    close must be the LAST COMPLETED trading day's close at any hour: if
    today's intraday series is empty, fall back to the dated bars of the
    most recent earlier day that has any (walking back over weekends /
    holidays). The patch is installed ONLY around the --arm call below —
    the --tick process never sees it, and the tick's live entry path
    (today's 09:15→09:55 bars) is untouched. A 429 is never swallowed.
    """

    def spot_intraday(self, idx):
        bars = super().spot_intraday(idx)
        if bars:
            return bars
        day = datetime.now(R.IST).date() - timedelta(days=1)
        for _ in range(10):
            try:
                past = super().spot_day(idx, day)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    raise
                past = {}
            if past:
                return past
            day -= timedelta(days=1)
        return bars


def cmd_init():
    if not R.STATE_FILE.exists():
        R.save_state(R.fresh_state())
    if not R.JOURNAL.exists():
        R.journal(JOURNAL_HEADER)
    if not R.LOG_CSV.exists():
        R.LOG_CSV.write_text(R.CSV_HEADER)
    st = R.load_state()
    print(f"init: state={R.STATE_FILE.name} status={st['status']} "
          f"run_start={st['run_start']} target_days={st['target_days']} "
          f"counted={len(st['counted'])}")
    print(f"init: log={R.LOG_CSV.name} journal={R.JOURNAL.name} "
          f"killswitch={'PRESENT (disarmed)' if R.KILLSWITCH_FILE.exists() else 'absent (armed)'}")
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--arm", action="store_true")
    ap.add_argument("--tick", action="store_true")
    ap.add_argument("--wrap", action="store_true")
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--dry-run", metavar="DATE")
    ap.add_argument("--date", metavar="DATE",
                    help="explicit day for --wrap (default today)")
    a = ap.parse_args()
    if a.init:
        return cmd_init()
    if a.arm:
        orig_api = R.Api
        R.Api = _ArmApi
        try:
            return R.cmd_arm()
        finally:
            R.Api = orig_api
    if a.tick:
        return R.cmd_tick()
    if a.wrap:
        return R.cmd_wrap(ddate.fromisoformat(a.date) if a.date else None)
    if a.drain:
        return R.cmd_drain()
    if a.status:
        return R.cmd_status()
    if a.dry_run:
        day = ddate.fromisoformat(a.dry_run)
        if day >= WINDOW_START:
            print(f"dry-run refused: {day} is inside the forward window "
                  f"(>= {WINDOW_START}); the forward record is never backfilled")
            return 2
        return R.cmd_dry_run(day)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
