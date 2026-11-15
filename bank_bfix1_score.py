#!/usr/bin/env python3
"""B-FIX-1 REPAIRED-LEAD SCORER — Bank Nifty (from Mon 2026-11-16).

Frozen repair (november_books_fix_2026-11-14.md, GATE PASS 2026-11-14):
a TUNED STACK v2 leg is NOT taken iff side = PE AND the day's
overnight gap% < 0 AND entry premium in [Rs500, Rs800].
Jan-Oct gate: repaired +Rs131,510.00 vs standing +Rs127,351.50;
placebo p95 +Rs124,715.98 (repair beats 200/200); halves both +.

This scorer reads the day's stack legs from the stack's own ledger
(november_shadow_stack_bank_log.csv — written by the existing chain,
NEVER modified here), applies the stand-down, and appends one row to
the repaired-line ledger november_repaired_bfix1_bank_log.csv.
The original stack keeps scoring untouched as the control line.

Gap source (in order): the frozen November regime-classification
file (Nov 2026 days) -> the persisted progressive spot file (today's
09:15 open vs the previous weekday's last close). If no gap can be
established the day is marked NC_GAP and no repaired figure is
produced — never estimated.

Usage: python3 bank_bfix1_score.py [--date YYYY-MM-DD] [--backfill]
Paper only, real money Rs0. Buying only. Lot 30, Rs220/trade inside
the stored stack nets.
"""
import csv, sys
from datetime import date as ddate
from pathlib import Path

TR = Path.home() / "workspace/trading"
STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
LEDGER = TR / "november_repaired_bfix1_bank_log.csv"
REGIME = TR / "november_regime_days_bank.csv"
SPOT = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
FIELDS = ["date", "row_type", "gap_pct", "stack_legs", "stack_net_inr",
          "stood_down", "repaired_net_inr", "notes"]
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]


def gap_pct(day):
    for r in csv.DictReader(open(REGIME)):
        if r["date"] == day and r["gap_pct"]:
            return float(r["gap_pct"])
    days = {}
    for r in csv.DictReader(open(SPOT)):
        days.setdefault(r["timestamp"][:10], []).append(r)
    if day not in days:
        return None
    prev = [d for d in sorted(days) if d < day
            and ddate.fromisoformat(d).weekday() <= 4]
    if not prev:
        return None
    prev = prev[-1]
    return (float(days[day][0]["open"]) / float(days[prev][-1]["close"])
            - 1.0) * 100.0


def stack_legs(day):
    out = []
    if not STACK_LOG.exists():
        return out
    for r in csv.DictReader(open(STACK_LOG)):
        if r["date"] == day and r["net_inr"]:
            out.append(r)
    return out


def score_day(day, row_type):
    legs = stack_legs(day)
    stack_net = round(sum(float(r["net_inr"]) for r in legs), 2)
    g = gap_pct(day)
    if legs and g is None:
        return dict(date=day, row_type=row_type, gap_pct="",
                    stack_legs=len(legs), stack_net_inr=stack_net,
                    stood_down="", repaired_net_inr="",
                    notes="NC_GAP: overnight gap not establishable "
                          "from stored spot; repaired line not scored")
    stood = []
    if g is not None:
        for r in legs:
            prem = float(r["entry_premium"])
            if (r["direction"] == "PE" and g < 0
                    and 500.0 <= prem <= 800.0):
                stood.append(r)
    repaired = round(stack_net
                     - sum(float(r["net_inr"]) for r in stood), 2)
    detail = "; ".join(
        f"STOOD DOWN {r['direction']} {r['strike']} @{r['entry_premium']} "
        f"net {float(r['net_inr']):+,.2f}" for r in stood)
    return dict(date=day, row_type=row_type,
                gap_pct=(round(g, 4) if g is not None else ""),
                stack_legs=len(legs), stack_net_inr=stack_net,
                stood_down=len(stood), repaired_net_inr=repaired,
                notes=detail or "no leg met the B-FIX-1 stand-down")


def upsert(row):
    rows = []
    if LEDGER.exists():
        rows = [r for r in csv.DictReader(open(LEDGER))
                if r["date"] != row["date"]]
    rows.append(row)
    rows.sort(key=lambda r: r["date"])
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def fmt(row):
    if row["repaired_net_inr"] == "":
        return (f"B-FIX-1 {row['date']}: NC_GAP — repaired line not "
                f"scored (stack net {row['stack_net_inr']:+,.2f} on "
                f"{row['stack_legs']} legs stands as the control)")
    gd = (f"{float(row['gap_pct']):+}%" if row["gap_pct"] != ""
          else "n/a")
    return (f"B-FIX-1 {row['date']} ({row['row_type']}): gap "
            f"{gd} · stack {row['stack_legs']} legs "
            f"{row['stack_net_inr']:+,.2f} · stood down "
            f"{row['stood_down']} · REPAIRED LEAD "
            f"{row['repaired_net_inr']:+,.2f}")


def main():
    args = sys.argv[1:]
    if "--backfill" in args:
        tot_s = tot_r = 0.0
        for day in NOV_DAYS:
            row = score_day(day, "BACKFILL_COUNTERFACTUAL")
            upsert(row)
            print(fmt(row))
            tot_s += float(row["stack_net_inr"])
            tot_r += float(row["repaired_net_inr"])
        print(f"BACKFILL Nov 2-13: stack {tot_s:+,.2f} -> repaired "
              f"{tot_r:+,.2f}")
        assert round(tot_s, 2) == -2680.00, tot_s
        assert round(tot_r, 2) == -3440.00, tot_r
        print("DRY-RUN MATCHES the Phase-2 counterfactual exactly "
              "(stack -2,680.00 -> repaired -3,440.00).")
        return
    day = None
    if "--date" in args:
        day = args[args.index("--date") + 1]
    if day is None:
        day = ddate.today().isoformat()
    if day > "2026-11-30":
        print(f"B-FIX-1 {day}: November window closed 2026-11-30 — "
              "the repaired line's fate is decided at the Nov 30 "
              "verdicts / December adoption. No row written.")
        return
    row = score_day(day, "LIVE")
    upsert(row)
    print(fmt(row))
    rows = [r for r in csv.DictReader(open(LEDGER))
            if r["row_type"] == "LIVE" and r["repaired_net_inr"] != ""]
    mtd = round(sum(float(r["repaired_net_inr"]) for r in rows), 2)
    print(f"B-FIX-1 repaired-lead MTD (live rows from 2026-11-16): "
          f"{mtd:+,.2f} over {len(rows)} scored days. Paper only, "
          f"real money Rs0.")


if __name__ == "__main__":
    main()
