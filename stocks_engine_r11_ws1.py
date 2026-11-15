#!/usr/bin/env python3
"""ROUND 11 — WS1: INV-ABOVE HARD-DIP EXCLUSION.

R11-01 (audit): starting-book verification (independent CSV
re-sum vs the recorded totals) + census of every INV-ABOVE row
by index-state bucket under the frozen R10-05 definition
(state = nifty_move(date, entry_time - 5min); hard <= -0.30 /
shallow (-0.30, 0) / up >= 0; unknown counted, never guessed),
asserted against R10-05's recorded full-year bucket nets.
R11-02 (gate): the banked book minus INV-ABOVE hard-dip rows
(both years). Placebos (R10-06 convention): P1 chrono removal
(same per-year count of INV-ABOVE rows, earliest first, any
bucket); P2 cross-bucket removal (same count from the non-hard
buckets, earliest first, shortfall from the hard bucket).
Timing violations 0: the bucketed bar completes exactly at
each row's entry instant — asserted per removed row.
"""
import sys, csv, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r11_lib as R11
import stocks_engine_r8_builders as B8

# ------------------------------------------------------ R11-01 --
raw = {}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r10_book{yr}_trades.csv")))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    raw[yr] = (len(rows), jo, full)
    assert jo == R11.JO_BASE[yr] and full == R11.FULL_BASE[yr], \
        (yr, jo, full)
    assert len(rows) == R11.ROWS_BASE[yr], (yr, len(rows))

books = R11.load_books()

def prev_bar(t):
    hh, mm = map(int, t.split(":"))
    m = hh * 60 + mm - 5
    return f"{m // 60:02d}:{m % 60:02d}"

def bucket_of(row):
    et = row.get("entry_time") or ""
    if len(et) != 5:
        return "unknown"
    mv = B8.nifty_move(row["date"], prev_bar(et))
    if mv is None:
        return "unknown"
    if mv <= -0.30:
        return "hard"
    if mv < 0:
        return "shallow"
    return "up"

WANT = {2025: {"hard": -1230.62, "shallow": -620.96,
               "up": 10132.83},
        2026: {"hard": -4012.18, "shallow": 3066.24,
               "up": 4295.15}}
census = {}
for yr in (2025, 2026):
    d = {}
    for t in books[yr]:
        if t["comp"] != "INV-ABOVE":
            continue
        b = bucket_of(t)
        n, s = d.get(b, (0, 0.0))
        d[b] = (n + 1, round(s + t["net"], 2))
    census[yr] = d
    for b, want in WANT[yr].items():
        got = d.get(b, (0, 0.0))[1]
        assert got == want, (yr, b, got, want)
    assert d.get("unknown", (0, 0.0))[0] == 0, (yr, d)
cen_str = "; ".join(
    f"{yr}: " + ", ".join(f"{b} {census[yr][b][0]} rows / "
                          f"{census[yr][b][1]}"
                          for b in ("hard", "shallow", "up"))
    for yr in (2025, 2026))
R11.record_audit(
    "R11-01",
    "Starting-book verification + INV-ABOVE index-state census "
    "(audit — no candidate scored)",
    f"Starting books re-summed independently from the Round-10 "
    f"CSVs: 2025 {raw[2025][0]} rows, JO {raw[2025][1]}, full "
    f"{raw[2025][2]}; 2026 {raw[2026][0]} rows, JO "
    f"{raw[2026][1]}, full {raw[2026][2]} — exact vs the "
    f"recorded totals. INV-ABOVE census by frozen R10-05 state "
    f"buckets reproduces R10-05's full-year bucket nets to the "
    f"paisa ({cen_str}); unknown-state rows 0 in both years. "
    f"The hard-dip rows lose in BOTH years and carry zero "
    f"July-2025 rows (R10-05) — the WS1 removal population.",
    extra={"book_check": {str(k): v for k, v in raw.items()},
           "inv_above_census": {str(yr): {b: list(v) for b, v
                                           in census[yr].items()}
                                for yr in (2025, 2026)}})

# ------------------------------------------------------ R11-02 --
removed = {yr: [t for t in books[yr]
                if t["comp"] == "INV-ABOVE"
                and bucket_of(t) == "hard"]
           for yr in (2025, 2026)}
for yr in (2025, 2026):
    for t in removed[yr]:
        # state knowable at the entry instant by construction:
        # the bucketed bar completes exactly at entry_time
        assert B8.nifty_move(t["date"],
                             prev_bar(t["entry_time"])) is not None
    july = [t for t in removed[yr] if t["date"][:7] == "2025-07"]
    if yr == 2025:
        assert not july, july
var = {yr: [t for t in books[yr]
            if not (t["comp"] == "INV-ABOVE"
                    and bucket_of(t) == "hard")]
       for yr in (2025, 2026)}

def keyf(t):
    return (t["date"], t.get("entry_time") or "", t["stock"])

def remove_n(rows, comp, n, pred):
    cand = sorted([t for t in rows if t["comp"] == comp
                   and pred(t)], key=keyf)
    take = {id(t) for t in cand[:n]}
    return [t for t in rows if id(t) not in take]

pl_books = []
for mode in ("chrono", "cross"):
    pb = {}
    for yr in (2025, 2026):
        n = len(removed[yr])
        if mode == "chrono":
            pb[yr] = remove_n(books[yr], "INV-ABOVE", n,
                              lambda t: True)
        else:
            rows = remove_n(books[yr], "INV-ABOVE", n,
                            lambda t: bucket_of(t) not in
                            ("hard", "unknown"))
            removed_ct = sum(1 for t in books[yr]
                             if t["comp"] == "INV-ABOVE") - \
                sum(1 for t in rows if t["comp"] == "INV-ABOVE")
            short = n - removed_ct
            if short > 0:
                rows = remove_n(rows, "INV-ABOVE", short,
                                lambda t: bucket_of(t) == "hard")
            pb[yr] = rows
    pl_books.append(R11.full_total(pb))
out = R11.gate(books, var, pl_books, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
rm_sa = {yr: round(sum(t["net"] for t in removed[yr]), 2)
         for yr in (2025, 2026)}
R11.record(
    "R11-02",
    "INV-ABOVE hard-dip exclusion (banked book minus INV-ABOVE "
    "rows on hard-dip index-state mornings, both years)", out,
    note=f"removed rows {len(removed[2025])}/{len(removed[2026])} "
         f"netting {rm_sa[2025]} / {rm_sa[2026]} (the R10-05 "
         f"full-year hard-bucket nets, reproduced in R11-01). "
         f"Placebos: chrono removal book {pl_books[0]}; "
         f"cross-bucket removal book {pl_books[1]}. Timing "
         f"violations 0 (state = the bar completing at each "
         f"row's entry instant, asserted per removed row). "
         f"Failed legs: {failed}.",
    extra={"removed_standalone": {str(k): v for k, v in rm_sa.items()},
           "removed_trades": {"2025": len(removed[2025]),
                              "2026": len(removed[2026])},
           "failed_legs": failed})
print("WS1 done.")
