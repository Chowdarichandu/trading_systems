#!/usr/bin/env python3
"""BTST-2 ROUND 2 — anatomy of E0-H2 + one frozen NIFTY crash-week filter.
Spec: btst2_r2_SPEC.md (frozen 2026-11-15 before scoring). Research only;
changes no book/ledger/job. Machinery imported verbatim from
hold_programme_build.py. Basis: equity cash, LONG only, frozen 25 names,
per 100 shares PROVISIONAL, Rs40 per completed position, paper only.
"""
import csv, json, os, sys
from collections import defaultdict
from datetime import date

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import hold_programme_build as HB

NAMES, YEARS = HB.NAMES, HB.YEARS

CHECK = {2025: dict(trades=1075, net=98386.0, max_dd=-232796.0),
         2026: dict(trades=1075, net=303058.0, max_dd=-276472.0)}

def iso_key(datestr):
    y, w, _ = date.fromisoformat(datestr).isocalendar()
    return (y, w)

def load_nifty_weeks():
    """ISO week -> last close of that week, from results_data/NIFTY50.csv."""
    wk = {}
    with open(os.path.join(WS, "results_data", "NIFTY50.csv")) as f:
        for r in csv.DictReader(f):
            wk[iso_key(r["date"])] = float(r["close"])  # rows are date-ordered
    return wk

def prior_week_return(wk_closes, week_key, ordered_weeks):
    """Return of the ISO week immediately before week_key, or None."""
    if week_key not in ordered_weeks:
        return None
    i = ordered_weeks.index(week_key)
    if i < 2:
        return None
    prev, prev2 = ordered_weeks[i - 1], ordered_weeks[i - 2]
    return wk_closes[prev] / wk_closes[prev2] - 1.0

def week_groups(trades):
    g = defaultdict(list)
    for t in trades:
        g[iso_key(t["entry_date"])].append(t)
    out = []
    for k in sorted(g):
        ts = g[k]
        out.append(dict(iso_year=k[0], iso_week=k[1],
                        first_entry=min(t["entry_date"] for t in ts),
                        trades=len(ts),
                        net=round(sum(t["net"] for t in ts), 2),
                        deployed=round(sum(t["entry"] * 100.0 for t in ts), 2)))
    return out

def main():
    data = {sym: HB.prep(sym) for sym in NAMES}

    # ---- control: E0-H2 through the imported machinery, exact check
    scored = {}
    for y in YEARS:
        tr = []
        for sym in NAMES:
            tr.extend(HB.score_year(HB.sim(data[sym], "E0", 2), data[sym], y))
        scored[y] = tr
        s = HB.stats(tr)
        for k, v in CHECK[y].items():
            assert s[k] == v, f"CONTROL FAIL {y} {k}: got {s[k]}, published {v}"
    print("CONTROL PASS: E0-H2 reproduces BTST-2 R1 exactly (both years).")

    wk_closes = load_nifty_weeks()
    ordered_weeks = sorted(wk_closes)

    results = {"spec": "btst2_r2_SPEC.md",
               "basis": "per 100 shares PROVISIONAL, Rs40/position",
               "control_check": "E0-H2 reproduces btst2_2026-11-15.md exactly",
               "years": {}}

    for y in YEARS:
        tr = scored[y]
        s = HB.stats(tr)
        weeks = week_groups(tr)

        # months by entry month
        months = defaultdict(lambda: dict(trades=0, net=0.0))
        for t in tr:
            m = months[t["entry_date"][:7]]
            m["trades"] += 1; m["net"] = round(m["net"] + t["net"], 2)
        # halves by entry date
        halves = {}
        for name, lo, hi in [("H1", f"{y}-01-01", f"{y}-05-31"),
                             ("H2", f"{y}-06-01", f"{y}-10-31")]:
            sel = [t for t in tr if lo <= t["entry_date"] <= hi]
            halves[name] = dict(trades=len(sel),
                                net=round(sum(t["net"] for t in sel), 2))
        worst10 = sorted(weeks, key=lambda w: w["net"])[:10]
        total_dep = round(sum(w["deployed"] for w in weeks), 2)
        avg_dep = round(total_dep / len(weeks), 2)
        max_dep = max(w["deployed"] for w in weeks)
        best4 = round(sum(sorted((w["net"] for w in weeks), reverse=True)[:4]), 2)

        anatomy = dict(
            control=dict(trades=s["trades"], net=s["net"], wr=s["wr"],
                         max_dd=s["max_dd"]),
            months={m: months[m] for m in sorted(months)},
            halves=halves,
            n_weeks=len(weeks),
            worst10_weeks=worst10,
            capital=dict(total_deployed=total_dep, avg_week=avg_dep,
                         max_week=max_dep),
            return_on_capital_pct=round(100.0 * s["net"] / total_dep, 2),
            best4_weeks_net=best4,
            best4_share_pct=round(100.0 * best4 / s["net"], 1) if s["net"] else None)

        # ---- Part B: frozen filter
        skipped, kept_weeks, unknown = [], [], 0
        for w in weeks:
            r = prior_week_return(wk_closes, (w["iso_year"], w["iso_week"]),
                                  ordered_weeks)
            if r is None:
                unknown += 1
                kept_weeks.append(w)
            elif r < -0.02:
                skipped.append(dict(iso_year=w["iso_year"], iso_week=w["iso_week"],
                                    first_entry=w["first_entry"],
                                    prior_week_return_pct=round(100.0 * r, 2),
                                    week_net=w["net"]))
            else:
                kept_weeks.append(w)
        skipped_keys = {(w["iso_year"], w["iso_week"]) for w in skipped}
        kept_trades = [t for t in tr
                       if iso_key(t["entry_date"]) not in skipped_keys]
        fs = HB.stats(kept_trades)
        kept_dep = round(sum(w["deployed"] for w in kept_weeks), 2)
        filt = dict(weeks_skipped=len(skipped), skipped=skipped,
                    weeks_unknown_kept=unknown,
                    trades=fs["trades"], net=fs["net"], max_dd=fs["max_dd"],
                    total_deployed=kept_dep,
                    avg_week_deployed=round(kept_dep / len(kept_weeks), 2) if kept_weeks else 0.0,
                    return_on_capital_pct=round(100.0 * fs["net"] / kept_dep, 2) if kept_dep else None)

        results["years"][str(y)] = dict(anatomy=anatomy, filter=filt)
        print(f"{y}: control net {s['net']:+.0f} DD {s['max_dd']:+.0f} | "
              f"weeks {len(weeks)} avg dep {avg_dep:,.0f} max {max_dep:,.0f} | "
              f"filter: skipped {len(skipped)} net {fs['net']:+.0f} DD {fs['max_dd']:+.0f}")

    with open(os.path.join(WS, "btst2_r2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE btst2_r2_results.json")

if __name__ == "__main__":
    main()
