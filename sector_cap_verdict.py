#!/usr/bin/env python3
"""SECTOR-CAP RETEST — verdict assembly. Loads the three book runs
(sector_cap_ekam_results.json, sector_cap_daily_results.json,
sector_cap_stockbook_results.json) + Stage 1 (sector_cap_stage1.json),
applies the FROZEN verdict bar from sector_coverage_2026-11-17.md's
SPEC ADDENDUM (identical to the additions test):
  IMPROVES — net above control, max DD not worse than 1.5x control
  HOLDS    — net within 10% below control, max DD not worse than 1.5x
  DEGRADES — net worse by >10% OR max DD worse than 1.5x
FIT TO JOIN LIVE requires no DEGRADES in any book-year.
Writes sector_cap_results.json + sector_cap_trades.csv."""
import csv, json

WS = "/home/hatch/workspace/trading"
NOV_DATES = {"2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
             "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
             "2026-11-13"}


def verdict(ctl_net, ctl_dd, net, dd):
    dd_ratio = (abs(dd) / abs(ctl_dd)) if ctl_dd else float("inf")
    net_ok = net >= 0.9 * ctl_net
    dd_ok = dd_ratio <= 1.5
    if not (net_ok and dd_ok):
        why = []
        if not net_ok:
            why.append("net")
        if not dd_ok:
            why.append("DD")
        return "DEGRADES", "+".join(why), round(dd_ratio, 2)
    if net > ctl_net:
        return "IMPROVES", "", round(dd_ratio, 2)
    return "HOLDS", "", round(dd_ratio, 2)


def window_of(date):
    if date in NOV_DATES:
        return "november"
    y = date[:4]
    return f"{y}_jan_oct" if date <= f"{y}-10-31" else f"{y}_post_oct"


def main():
    s1 = json.load(open(f"{WS}/sector_cap_stage1.json"))
    ek = json.load(open(f"{WS}/sector_cap_ekam_results.json"))
    dy = json.load(open(f"{WS}/sector_cap_daily_results.json"))
    sb = json.load(open(f"{WS}/sector_cap_stockbook_results.json"))

    cells = []  # book, year, ctl stats, capped stats, added, blocked

    for book in ("CAND-T5", "S2"):
        label = f"EKAM {book}"
        for y in (2025, 2026):
            ctl = ek["control25"][book]["years"][str(y)]["stats"]
            cap = ek["enlarged37_capped"][book]["years"][str(y)]
            cells.append(dict(book=label, year=y, control=ctl,
                              capped=cap["stats"], added=cap["added"],
                              blocked=ek["blocked"][str(y)][book]))
    for wname, y in (("2025_jan_oct", 2025), ("2026_jan_oct", 2026)):
        ctl = sb["control25w"][wname]
        cap = sb["windows"][wname]
        cells.append(dict(book="Stock Book", year=y,
                          control={k: ctl[k] for k in
                                   ("trades", "net", "wr", "ex_top3",
                                    "max_drawdown")},
                          capped={k: cap["capped"][k] for k in
                                  ("trades", "net", "wr", "ex_top3",
                                   "max_drawdown")},
                          added=cap["added"], blocked=cap["blocked"]))
    for y in (2025, 2026):
        ctl = dy["control25_screened"]["years"][str(y)]["stats"]
        cap = dy["enlarged37_capped"]["years"][str(y)]
        cells.append(dict(book="EKAM-Daily", year=y, control=ctl,
                          capped=cap["stats"], added=cap["added"],
                          blocked=dy["blocked"][str(y)]))

    table = []
    for c in cells:
        v, why, ratio = verdict(c["control"]["net"],
                                c["control"]["max_drawdown"],
                                c["capped"]["net"],
                                c["capped"]["max_drawdown"])
        row = dict(book=c["book"], year=c["year"],
                   control_net=c["control"]["net"],
                   capped_net=c["capped"]["net"],
                   delta_net_pct=(round(100.0 * (c["capped"]["net"]
                                                 / c["control"]["net"] - 1), 1)
                                  if c["control"]["net"] else None),
                   control_dd=c["control"]["max_drawdown"],
                   capped_dd=c["capped"]["max_drawdown"],
                   dd_ratio=ratio,
                   control_trades=c["control"]["trades"],
                   capped_trades=c["capped"]["trades"],
                   capped_wr=c["capped"]["wr"],
                   capped_ex_top3=c["capped"]["ex_top3"],
                   verdict=v, degraded_on=why,
                   added=c["added"], blocked=c["blocked"])
        table.append(row)
        print(f"{c['book']:12s} {c['year']}: ctl {c['control']['net']:+11.2f} "
              f"-> capped {c['capped']['net']:+11.2f} "
              f"({row['delta_net_pct']:+.1f}%) | DD {c['control']['max_drawdown']:.2f} "
              f"-> {c['capped']['max_drawdown']:.2f} ({ratio}x) | {v}"
              f"{' (' + why + ')' if why else ''}", flush=True)

    fit = all(r["verdict"] != "DEGRADES" for r in table)
    n_deg = sum(1 for r in table if r["verdict"] == "DEGRADES")
    print(f"\nFIT TO JOIN LIVE: {fit} ({n_deg} of 8 book-years DEGRADES)")

    # November slices (descriptive)
    nov = {
        "EKAM CAND-T5": dict(
            control=ek["control25"]["CAND-T5"]["november"]["stats"],
            capped=ek["enlarged37_capped"]["CAND-T5"]["november"]["stats"],
            added=ek["enlarged37_capped"]["CAND-T5"]["november"]["added"],
            blocked=ek["blocked"]["november"]["CAND-T5"]),
        "EKAM S2": dict(
            control=ek["control25"]["S2"]["november"]["stats"],
            capped=ek["enlarged37_capped"]["S2"]["november"]["stats"],
            added=ek["enlarged37_capped"]["S2"]["november"]["added"],
            blocked=ek["blocked"]["november"]["S2"]),
        "Stock Book": dict(
            control={k: sb["control25w"]["november"][k] for k in
                     ("trades", "net", "wr", "ex_top3", "max_drawdown")},
            capped={k: sb["windows"]["november"]["capped"][k] for k in
                    ("trades", "net", "wr", "ex_top3", "max_drawdown")},
            added=sb["windows"]["november"]["added"],
            blocked=sb["windows"]["november"]["blocked"]),
        "EKAM-Daily": dy["enlarged37_capped"]["november"],
        "EKAM-Daily control": dy["control25_screened"]["november"],
        "EKAM-Daily blocked": dy["blocked"]["november"],
    }

    out = {
        "rule": "owner 2026-11-17 07:43 IST: no stock priced above Rs3,000 "
                "is traded (entry price <= Rs3,000, all names)",
        "cap": 3000.0,
        "stage1": {
            "additions12": s1["additions12"],
            "replacements": s1["replacements"],
            "final_capped_additions": s1["final_capped_additions"],
            "incumbents_above_cap": {
                s: m for s, m in s1["incumbents25"].items()
                if m["above_cap"]},
            "incumbents25": s1["incumbents25"],
        },
        "controls": "identical to the additions test (EKAM published 25; "
                    "Stock Book sector25w within-machinery; EKAM-Daily "
                    "official-close screened 25) — all control checks PASS",
        "verdict_table": table,
        "fit_to_join_live": fit,
        "degrades_count": n_deg,
        "november_slices": nov,
        "ekam_gate": {
            "candidate_days_total": ek["candidate_days_total"],
            "candidate_days_disqualified": ek["candidate_days_disqualified"],
            "disqualified_by_sym": ek["disqualified_by_sym"]},
        "stockbook_entry_validation": {
            k: sb["entry_validation"][k] for k in
            ("checked", "match_entry_open", "match_prev_close", "unmatched")},
        "data_fetch": "AMBUJACEM + ASIANPAINT 5-min bars fetched via the "
                      "programme's Upstox route into data/wide100 "
                      "(34,676 bars each, 2025-01-01..2026-11-13, no 429); "
                      "fetched daily closes match the independent parquet "
                      "dump on all 526 common days for both names",
    }
    json.dump(out, open(f"{WS}/sector_cap_results.json", "w"), indent=1)

    # ---- combined capped trades CSV
    rows = []
    for t in ek["trades"]:
        rows.append(dict(book=t["book"], window=window_of(t["date"]),
                         date=t["date"], sym=t["sym"], side=t["side"],
                         entry=t["entry"], exit="", net=t["net"],
                         added=t["added"]))
    for t in dy["trades"]:
        rows.append(dict(book=t["book"],
                         window=window_of(t["entry_date"]),
                         date=t["entry_date"], sym=t["sym"], side="LONG",
                         entry=t["entry"], exit=t["exit"], net=t["net"],
                         added=t["added"]))
    for t in sb["trades"]:
        rows.append(dict(book=t["book"], window=t["window"],
                         date=t["date"], sym=t["sym"], side=t["side"],
                         entry=t["entry"], exit=t["exit"], net=t["net"],
                         added=t["added"]))
    rows.sort(key=lambda r: (r["book"], r["date"], r["sym"]))
    with open(f"{WS}/sector_cap_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["book", "window", "date", "sym",
                                          "side", "entry", "exit", "net",
                                          "added"])
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE sector_cap_results.json + sector_cap_trades.csv "
          f"({len(rows)} capped trades)")


if __name__ == "__main__":
    main()
