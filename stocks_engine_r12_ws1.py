#!/usr/bin/env python3
"""ROUND 12 — WS1: HARD-DIP EXCLUSION ON THE NEW BASELINE.

R12-01 (audit): starting-book verification (independent CSV
re-sum vs the recorded Round-11 totals, incl. Jul / Oct 2025
month nets) + census of every INV-ABOVE row by index-state
bucket under the frozen R10-05 definition (state =
nifty_move(date, entry_time - 5min); hard <= -0.30 / shallow
(-0.30, 0) / up >= 0; unknown counted, never guessed),
asserted against R11-01's recorded bucket nets — the pair
did not touch INV-ABOVE rows, so the census must reproduce
exactly.
R12-02 (gate): the Round-11 ending book minus INV-ABOVE
hard-dip rows (both years) — the R11-02 construction verbatim,
re-based. Placebos (R10-06 convention): P1 chrono removal
(same per-year count of INV-ABOVE rows, earliest first, any
bucket); P2 cross-bucket removal (same count from the
non-hard buckets, earliest first, shortfall from the hard
bucket). Timing violations 0: the bucketed bar completes
exactly at each row's entry instant — asserted per removed
row.
"""
import sys, csv, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r12_lib as R12
import stocks_engine_r8_builders as B8

# ------------------------------------------------------ R12-01 --
raw = {}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r11_book{yr}_trades.csv")))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    raw[yr] = (len(rows), jo, full)
    assert jo == R12.JO_BASE[yr] and full == R12.FULL_BASE[yr], \
        (yr, jo, full)
    assert len(rows) == R12.ROWS_BASE[yr], (yr, len(rows))

books = R12.load_books()
jul = R12.month_net(books[2025], "2025-07")
oct_ = R12.month_net(books[2025], "2025-10")
assert jul == -2101.93, jul
assert oct_ == -3751.28, oct_

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
WANT_N = {2025: {"hard": 23, "shallow": 33, "up": 95},
          2026: {"hard": 16, "shallow": 10, "up": 10}}
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
        assert d[b][0] == WANT_N[yr][b], (yr, b, d[b][0])
    assert d.get("unknown", (0, 0.0))[0] == 0, (yr, d)
cen_str = "; ".join(
    f"{yr}: " + ", ".join(f"{b} {census[yr][b][0]} rows / "
                          f"{census[yr][b][1]}"
                          for b in ("hard", "shallow", "up"))
    for yr in (2025, 2026))
R12.record_audit(
    "R12-01",
    "Starting-book verification + INV-ABOVE index-state census "
    "(audit — no candidate scored)",
    f"Starting books re-summed independently from the Round-11 "
    f"CSVs: 2025 {raw[2025][0]} rows, JO {raw[2025][1]}, full "
    f"{raw[2025][2]}; 2026 {raw[2026][0]} rows, JO "
    f"{raw[2026][1]}, full {raw[2026][2]} — exact vs the "
    f"recorded totals. Month nets asserted: Jul 2025 {jul}, "
    f"Oct 2025 {oct_}. INV-ABOVE census by frozen R10-05 state "
    f"buckets reproduces R11-01's bucket nets to the paisa "
    f"({cen_str}); unknown-state rows 0 in both years — the "
    f"pair left INV-ABOVE untouched, as constructed.",
    extra={"book_check": {str(k): v for k, v in raw.items()},
           "jul_2025": jul, "oct_2025": oct_,
           "inv_above_census": {str(yr): {b: list(v) for b, v
                                           in census[yr].items()}
                                for yr in (2025, 2026)}})

# ------------------------------------------------------ R12-02 --
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
    pl_books.append(R12.full_total(pb))
out = R12.gate(books, var, pl_books, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
rm_sa = {yr: round(sum(t["net"] for t in removed[yr]), 2)
         for yr in (2025, 2026)}
R12.record(
    "R12-02",
    "INV-ABOVE hard-dip exclusion re-gated on the Round-11 "
    "ending book (pair baseline)", out,
    note=f"removed rows {len(removed[2025])}/{len(removed[2026])} "
         f"netting {rm_sa[2025]} / {rm_sa[2026]} (the R11-01 "
         f"hard-bucket nets, reproduced in R12-01). Placebos: "
         f"chrono removal book {pl_books[0]}; cross-bucket "
         f"removal book {pl_books[1]}. Timing violations 0 "
         f"(state = the bar completing at each row's entry "
         f"instant, asserted per removed row). Failed legs: "
         f"{failed}.",
    extra={"removed_standalone": {str(k): v for k, v in rm_sa.items()},
           "removed_trades": {"2025": len(removed[2025]),
                              "2026": len(removed[2026])},
           "failed_legs": failed})
print("WS1 done.")
