#!/usr/bin/env python3
"""CIRCUIT BREAKER — daily record for TUNED STACK v2 (scoring
layer; implemented 2026-11-14 under scenario-proofing Item 3).

WHY THIS EXISTS: until today the bleed rule (3 consecutive losing
days -> pause 3; MTD <= -Rs5,000 -> pause rest of month) was
tracked only in the segment engines' evening narratives — no code
computed or recorded it for the stack. This runner is that code.

THIRD LEG — HWM-DD, ENABLED HERE (adopted 2026-11-14 under the
frozen criteria in scenario_proofing_2026-11-14.md, "BREAKER
GAP — HWM-DD LEG"): within a calendar month, HWM is the highest
realised MTD reached at any prior close (floored at the
month-start 0 baseline); HWM - MTD >= Rs5,000 at a non-paused
close trips a rest-of-month pause — the MTD leg anchored to the
month's peak instead of zero, closing the Item 4 gap (bleeds
that begin from a profitable month-to-date). This runner passes
hwmdd_drop=CB.HWMDD_DROP (default ON for the December-layer
record); circuit_breaker.simulate itself keeps the leg optional
and off by default so the Item 3 / ROLL10 replays reproduce
exactly. On the November record the leg trips at the 2026-11-13
close (HWM +Rs2,480, MTD -Rs2,680, drop Rs5,160): the stack
stands paused for the rest of November under this layer.
It changes NO book logic and places NO trades: it reads the
stack's own ledger (november_shadow_stack_bank_log.csv, read-only)
and the persisted spot store (the trading calendar), recomputes
the breaker day by day with circuit_breaker.simulate (the same
implementation the Jan-Oct and November replays were verified
with), and writes:
  - circuit_breaker_stack_log.csv  (one row per trading day)
  - breaker_state_stack.json       (current state + trip history)
Recompute-from-ledger on every run: deterministic, idempotent,
self-healing. A day whose ledger rows are NOT_COMPUTED (no net)
halts the record at the previous day and is reported — the state
never advances on an unknown day (the r4d1 shadow convention).

The breaker binds the shadow/December layer only; the frozen
primaries run untouched regardless of what this record says.

Usage: python3 circuit_breaker_stack.py [--dry-run]
Paper only, real money Rs0.
"""
import argparse, csv, json, sys
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import circuit_breaker as CB

STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
RECORD = TR / "circuit_breaker_stack_log.csv"
STATE = TR / "breaker_state_stack.json"
WINDOW_START = "2026-11-01"
MIN_DAY_BARS = 70

FIELDS = ["date", "day_net_inr", "realised_net_inr", "paused",
          "pause_kind", "mtd_inr", "losing_streak", "trip", "notes"]


def trading_calendar():
    """Trading days >= WINDOW_START proven by the persisted spot
    stores (complete days only, >= 70 five-minute bars)."""
    days = defaultdict(int)
    for fn in (TR / "data/banknifty-2026-11/spot_5m.csv",
               TR / "data/progressive/BANKNIFTY/spot_5m.csv"):
        if not fn.exists():
            continue
        with open(fn) as f:
            for r in csv.DictReader(f):
                d = r["timestamp"][:10]
                if d >= WINDOW_START:
                    days[d] += 1
    # a day present in both stores is counted once per store; a
    # complete day has >= 70 bars in at least one store
    out = set()
    for fn in (TR / "data/banknifty-2026-11/spot_5m.csv",
               TR / "data/progressive/BANKNIFTY/spot_5m.csv"):
        if not fn.exists():
            continue
        per = defaultdict(int)
        with open(fn) as f:
            for r in csv.DictReader(f):
                d = r["timestamp"][:10]
                if d >= WINDOW_START:
                    per[d] += 1
        out |= {d for d, n in per.items() if n >= MIN_DAY_BARS}
    return sorted(out)


def stack_day_nets():
    """({date: net}, {date: 'NOT_COMPUTED'}) from the stack ledger."""
    nets = defaultdict(float)
    seen = set()
    nc = {}
    if not STACK_LOG.exists():
        return {}, {}
    with open(STACK_LOG) as f:
        for r in csv.DictReader(f):
            d = r["date"]
            seen.add(d)
            if r.get("net_inr"):
                nets[d] += float(r["net_inr"])
            elif "NOT_COMPUTED" in (r.get("notes") or ""):
                nc[d] = "stack_not_computed"
    return {d: round(nets.get(d, 0.0), 2) for d in seen}, nc


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    cal = trading_calendar()
    nets, nc = stack_day_nets()
    halted = None
    usable = []
    for d in cal:
        if d in nc:
            halted = (d, nc[d])
            break
        usable.append(d)
    hyp = {d: nets.get(d, 0.0) for d in usable}
    records, summary = CB.simulate(usable, hyp,
                                   hwmdd_drop=CB.HWMDD_DROP)
    rows = []
    for r in records:
        rows.append({
            "date": r["date"],
            "day_net_inr": f"{r['hypothetical_net']:.2f}",
            "realised_net_inr": f"{r['realised_net']:.2f}",
            "paused": "YES" if r["paused"] else "",
            "pause_kind": r["pause_kind"],
            "mtd_inr": f"{r['mtd_realised']:.2f}",
            "losing_streak": str(r["streak"]),
            "trip": r["trip"],
            "notes": ("no-trade day" if r["hypothetical_net"] == 0
                      and not r["paused"] else
                      "suppressed by breaker" if r["paused"] else ""),
        })
    last = records[-1] if records else None
    state = dict(book="TUNED STACK v2", layer="shadow/December",
                 last_date=last["date"] if last else None,
                 mtd_inr=last["mtd_realised"] if last else 0.0,
                 hwm_inr=last.get("hwm") if last else None,
                 hwm_dd_inr=last.get("hwm_dd") if last else None,
                 losing_streak=last["streak"] if last else 0,
                 currently_paused=bool(last and last["paused"]),
                 trips=summary["trips"],
                 total_hypothetical=summary["total_hypothetical"],
                 total_realised=summary["total_realised"],
                 halted_on_nc=halted[0] if halted else None)
    if not a.dry_run:
        with open(RECORD, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        STATE.write_text(json.dumps(state, indent=1))
    print(f"CIRCUIT BREAKER (stack) through {state['last_date']}: "
          f"MTD={state['mtd_inr']:+.2f} streak={state['losing_streak']} "
          f"trips={len(summary['trips'])} paused_days="
          f"{summary['paused_days']} total={summary['total_realised']:+.2f}"
          f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    if halted:
        print(f"HALTED: {halted[0]} is {halted[1]} in the stack "
              f"ledger — record stops at the previous day.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
