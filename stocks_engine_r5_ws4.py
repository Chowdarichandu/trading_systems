#!/usr/bin/env python3
"""ROUND 5 — WS4: P2F-R2 REGIME / BAND CONDITIONING.

P2F-R2 is 2025's weakest reaction family (-Rs390.06 on 21 trades in
2025 vs +Rs15,149.33 on 32 in 2026, R3 audit). One condition at a time,
gated whole-book:
  R5-09 keep entry-date regime cell in {DOWN, FLAT} (drop UP entries)
  R5-10 keep entry-date regime cell == DOWN only
  R5-11 keep reaction band [2.5%, 4.0%) only (drop >= 4.0% reactions)
  R5-12 keep reaction band >= 4.0% only (drop [2.5%, 4.0%))
(The brief's 2.0-2.5% band at R+2 is the separate R2-LOWBAND component
— 1 trade in 2025; it cannot carry a conditioning verdict, so the band
axis is applied inside P2F-R2's own >= 2.5% population, split at 4.0%.)

Band source: each book row is joined to the machinery's own scored
lag-2 row (score_lag on reaction_candidates, both calendars) on
(date, stock, dir, net) -> reaction_ret_pct. Unmatched rows fall back
to recomputation from the daily series (R = entry - 2 trading days;
ret = close(R)/close(R-1) - 1); every row's |ret| >= 2.5 is asserted.

Placebos per condition (whole-book combined totals): (i) chrono
removal — drop the chronologically first N P2F-R2 trades instead
(N = the condition's removal count); (ii) complement removal — keep
ONLY the subset the condition drops. Timing: filters on existing
audited rows; no new entries are created -> 0 violations.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r5_lib as R5

books = R5.load_books()
LABELS = R5.LABELS
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E = g["STOCKS_E"]
rc, score_lag = g["reaction_candidates"], g["score_lag"]
CALS = [(f"{WS}/stock_event_calendar_2025.csv", "2025-01-01", "2025-12-31"),
        (f"{WS}/stock_event_calendar_jan_oct_2026.csv", "2026-01-01",
         "2026-12-31")]

band = {}
for cal, lo, hi in CALS:
    for c in rc(cal, lo, hi):
        if abs(c["reaction_ret_pct"]) < 2.5:
            continue
        t = score_lag(c, 2)
        if t is None:
            continue
        band[(t["date"], t["symbol"], t["direction"], t["net_rs"])] = \
            c["reaction_ret_pct"]

def ret_of(t):
    k = (t["date"], t["stock"], t["dir"], t["net"])
    if k in band:
        return band[k], "join"
    spot, daily = STOCKS_E[t["stock"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    ri = didx[t["date"]] - 2
    ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
    return ret, "recomputed"

rows = {yr: [t for t in books[yr] if t["comp"] == "P2F-R2"]
        for yr in (2025, 2026)}
meta = {}
src_count = {"join": 0, "recomputed": 0}
for yr in (2025, 2026):
    for t in rows[yr]:
        ret, src = ret_of(t)
        src_count[src] += 1
        assert abs(ret) >= 2.49, (t, ret)
        meta[(yr, t["date"], t["stock"], t["dir"], t["net"])] = ret
print(f"P2F-R2 rows: {sum(len(v) for v in rows.values())}; band source: "
      f"{src_count}")
for yr in (2025, 2026):
    sub = rows[yr]
    jo = [t for t in sub if t["date"] <= f"{yr}-10-31"]
    print(f"  {yr}: {len(sub)} trades, JO net "
          f"{round(sum(t['net'] for t in jo), 2)}, cells "
          f"{ {c: round(sum(t['net'] for t in jo if LABELS.get(t['date']) == c), 2) for c in ('DOWN','FLAT','UP')} }, "
          f"band[2.5,4) JO {round(sum(t['net'] for t in jo if abs(meta[(yr,t['date'],t['stock'],t['dir'],t['net'])]) < 4.0), 2)}, "
          f"band>=4 JO {round(sum(t['net'] for t in jo if abs(meta[(yr,t['date'],t['stock'],t['dir'],t['net'])]) >= 4.0), 2)}")

def run_condition(cyc, label, keep_fn):
    global books
    kept = {yr: [t for t in books[yr]
                 if t["comp"] != "P2F-R2" or keep_fn(yr, t)]
            for yr in (2025, 2026)}
    removed = {yr: [t for t in books[yr]
                    if t["comp"] == "P2F-R2" and not keep_fn(yr, t)]
               for yr in (2025, 2026)}
    n_removed = sum(len(removed[yr]) for yr in (2025, 2026))
    complement = {yr: [t for t in books[yr] if t["comp"] != "P2F-R2"]
                  + removed[yr] for yr in (2025, 2026)}
    pl = [R.chrono_placebo(books, "P2F-R2", n_removed),
          R5.full_total(complement)]
    out = R5.gate(books, kept, pl, timing_violations=0)
    R5.record(cyc, label, out,
              note=f"removed {n_removed} P2F-R2 trades "
                   f"(2025 JO removed net "
                   f"{round(sum(t['net'] for t in removed[2025] if t['date'] <= '2025-10-31'), 2)}; "
                   f"2026 JO removed net "
                   f"{round(sum(t['net'] for t in removed[2026] if t['date'] <= '2026-10-31'), 2)}); "
                   f"timing: filter on existing audited rows, no new "
                   f"entries -> 0 violations; placebos: chrono-removal "
                   f"book {pl[0]}; complement-removal book {pl[1]}",
              extra={"removed_trades": n_removed})
    if out["verdict"]:
        books = kept
        R5.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

run_condition("R5-09", "P2F-R2 keep DOWN+FLAT entry cells only",
              lambda yr, t: LABELS.get(t["date"]) in ("DOWN", "FLAT"))
run_condition("R5-10", "P2F-R2 keep DOWN entry cells only",
              lambda yr, t: LABELS.get(t["date"]) == "DOWN")
run_condition("R5-11", "P2F-R2 keep reaction band [2.5%, 4.0%) only",
              lambda yr, t: abs(meta[(yr, t["date"], t["stock"],
                                      t["dir"], t["net"])]) < 4.0)
run_condition("R5-12", "P2F-R2 keep reaction band >= 4.0% only",
              lambda yr, t: abs(meta[(yr, t["date"], t["stock"],
                                      t["dir"], t["net"])]) >= 4.0)

print("WS4 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
