#!/usr/bin/env python3
"""N-FIX-1 REPAIRED-LEAD SCORER — Nifty TUNED v1 (from Mon 2026-11-16).

TUNED v1's forward legs are produced from the DEC-S1 shadow ledger
(november_shadow_decs1_nifty_log.csv, scored by the 15:32 shadow
job): v1 = every DEC-S1 row EXCEPT component-B PE rows (the proven
B-PE leak, removed by v1's definition). This scorer makes that
derivation a standing machine and applies the frozen repair:

N-FIX-1 (november_books_fix_2026-11-14.md, GATE PASS 2026-11-14):
a TUNED v1 leg is NOT taken iff side = CE AND the day's overnight
gap% > 0. Jan-Oct gate: repaired +Rs117,170.00 vs standing
+Rs103,050.25; placebo p95 +Rs108,558.31 (repair beats 199/200);
halves both +. November counterfactual: v1 +Rs3,036.50 -> Rs0
(the Nov 3 C CE leg is stood down).

Appends one row per day to november_repaired_nfix1_nifty_log.csv
carrying BOTH the TUNED v1 (original, control) day net and the
repaired-lead day net. The DEC-S1 ledger is never modified.

Gap source (in order): the stored November spot bars
(oi_history/spot_nov_bars.json — today's 09:15 open vs the previous
weekday's last close) -> the persisted progressive spot file.
If no gap can be established and a v1 CE leg exists, the day is
marked NC_GAP and no repaired figure is produced — never estimated.

Usage: python3 nifty_nfix1_score.py [--date YYYY-MM-DD] [--backfill]
Paper only, real money Rs0. Buying only. Lot 65, Rs220/trade inside
the stored DEC-S1 nets.
"""
import csv, json, sys
from datetime import date as ddate
from pathlib import Path

TR = Path.home() / "workspace/trading"
DECS1_LOG = TR / "november_shadow_decs1_nifty_log.csv"
LEDGER = TR / "november_repaired_nfix1_nifty_log.csv"
SPOT_JSON = TR / "oi_history/spot_nov_bars.json"
SPOT = TR / "data/progressive/NIFTY/spot_5m.csv"
FIELDS = ["date", "row_type", "gap_pct", "v1_legs", "v1_net_inr",
          "stood_down", "repaired_net_inr", "notes"]
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]


def gap_pct(day):
    d = json.load(open(SPOT_JSON)).get("NIFTY", {})
    if day in d:
        prev = [x for x in sorted(d) if x < day
                and ddate.fromisoformat(x).weekday() <= 4
                and d[x] and d[x][0][0] == "09:15"]
        if prev:
            p = prev[-1]
            return (float(d[day][0][1]) / float(d[p][-1][4])
                    - 1.0) * 100.0
    days = {}
    for r in csv.DictReader(open(SPOT)):
        days.setdefault(r["timestamp"][:10], []).append(r)
    if day not in days:
        return None
    prev = [x for x in sorted(days) if x < day
            and ddate.fromisoformat(x).weekday() <= 4]
    if not prev:
        return None
    prev = prev[-1]
    return (float(days[day][0]["open"]) / float(days[prev][-1]["close"])
            - 1.0) * 100.0


def v1_legs(day):
    out = []
    if not DECS1_LOG.exists():
        return out
    for r in csv.DictReader(open(DECS1_LOG)):
        if r["date"] != day or not r["net_inr"]:
            continue
        comp = r["system_source"].replace("DEC-S1", "").strip()
        if comp == "B" and r["direction"] == "PE":
            continue  # B-PE is not part of TUNED v1 by definition
        r["_comp"] = comp
        out.append(r)
    return out


def score_day(day, row_type):
    legs = v1_legs(day)
    v1_net = round(sum(float(r["net_inr"]) for r in legs), 2)
    g = gap_pct(day)
    if legs and any(r["direction"] == "CE" for r in legs) and g is None:
        return dict(date=day, row_type=row_type, gap_pct="",
                    v1_legs=len(legs), v1_net_inr=v1_net, stood_down="",
                    repaired_net_inr="",
                    notes="NC_GAP: overnight gap not establishable "
                          "from stored spot; repaired line not scored")
    stood = []
    if g is not None:
        stood = [r for r in legs
                 if r["direction"] == "CE" and g > 0]
    repaired = round(v1_net
                     - sum(float(r["net_inr"]) for r in stood), 2)
    detail = "; ".join(
        f"STOOD DOWN {r['_comp']} {r['direction']} {r['strike']} "
        f"@{r['entry_premium']} net {float(r['net_inr']):+,.2f}"
        for r in stood)
    return dict(date=day, row_type=row_type,
                gap_pct=(round(g, 4) if g is not None else ""),
                v1_legs=len(legs), v1_net_inr=v1_net,
                stood_down=len(stood), repaired_net_inr=repaired,
                notes=detail or "no leg met the N-FIX-1 stand-down")


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
        return (f"N-FIX-1 {row['date']}: NC_GAP — repaired line not "
                f"scored (TUNED v1 net {row['v1_net_inr']:+,.2f} on "
                f"{row['v1_legs']} legs stands as the control)")
    gd = (f"{float(row['gap_pct']):+}%" if row["gap_pct"] != ""
          else "n/a")
    return (f"N-FIX-1 {row['date']} ({row['row_type']}): gap "
            f"{gd} · TUNED v1 {row['v1_legs']} legs "
            f"{row['v1_net_inr']:+,.2f} · stood down "
            f"{row['stood_down']} · REPAIRED LEAD "
            f"{row['repaired_net_inr']:+,.2f}")


def main():
    args = sys.argv[1:]
    if "--backfill" in args:
        tot_v = tot_r = 0.0
        for day in NOV_DAYS:
            row = score_day(day, "BACKFILL_COUNTERFACTUAL")
            upsert(row)
            print(fmt(row))
            tot_v += float(row["v1_net_inr"])
            tot_r += float(row["repaired_net_inr"])
        print(f"BACKFILL Nov 2-13: TUNED v1 {tot_v:+,.2f} -> "
              f"repaired {tot_r:+,.2f}")
        assert round(tot_v, 2) == 3036.50, tot_v
        assert round(tot_r, 2) == 0.00, tot_r
        print("DRY-RUN MATCHES the Phase-2 counterfactual exactly "
              "(TUNED v1 +3,036.50 -> repaired 0.00).")
        return
    day = None
    if "--date" in args:
        day = args[args.index("--date") + 1]
    if day is None:
        day = ddate.today().isoformat()
    if day > "2026-11-30":
        print(f"N-FIX-1 {day}: November window closed 2026-11-30 — "
              "the repaired line's fate is decided at the Nov 30 "
              "verdicts / December adoption. No row written.")
        return
    row = score_day(day, "LIVE")
    upsert(row)
    print(fmt(row))
    rows = [r for r in csv.DictReader(open(LEDGER))
            if r["row_type"] == "LIVE" and r["repaired_net_inr"] != ""]
    mtd = round(sum(float(r["repaired_net_inr"]) for r in rows), 2)
    print(f"N-FIX-1 repaired-lead MTD (live rows from 2026-11-16): "
          f"{mtd:+,.2f} over {len(rows)} scored days. Paper only, "
          f"real money Rs0.")


if __name__ == "__main__":
    main()
