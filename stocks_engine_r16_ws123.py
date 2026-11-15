#!/usr/bin/env python3
"""ROUND 16 — R16-01 audit + WS1/WS2 mirror gates + WS3
conditional gate.

The MIRROR of Round 15's frozen volume form: keep a sleeve's
rows whose PRIOR-day relative volume is BELOW its trailing
20-day median (rvol < 1.0), where rvol is exactly the Round-15
frozen feature — P = last trading day strictly before the
entry date in the stock's volume series; rvol = volume(P) /
median(volume over the 20 trading days ending on P,
inclusive), from stocks_daily_volume.csv.

CAUSALITY LAW asserted row by row (unchanged from Round 15):
every volume input is dated strictly before the entry date
(P < entry date; the window ends on P). Rows with < 20 prior
volume days, a missing P, or a non-positive median are
UNCLASSIFIABLE — excluded from every conditioned set (real
and placebos alike), counted by name, never estimated.

Sleeve populations are the banked ones, rebuilt by the
Round-14 builders; each builder's real set must reproduce the
banked comp rows exactly (anchor) before any conditioning.
Placebos per gate (the Round-15 conditioned-population
convention): the mirror-conditioned flip book and the
mirror-conditioned late book, each swapped in whole-book.
"""
import bisect, csv, pickle, statistics, sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r16_lib as R16
import stocks_engine_r14_builders as B14

books = R16.load_books()

# ------------------------------------------------------ R16-01 --
R16.record_audit(
    "R16-01",
    "Starting-book verification (Round-15 ending book)",
    "Books re-summed from stocks_engine_r15_book{2025,2026}"
    "_trades.csv: 2025 JO 105987.24 / full 107589.18 / 1101 "
    "rows; 2026 JO 257300.30 / full 257300.30 / 1352 rows — "
    "exact vs the Round-15 record (asserted in code at load). "
    "Red 2025 Jan-Oct months asserted: Jul -2733.21, Oct "
    "-4152.19. No scoring preceded this audit.")

# --------------------------------------------------------- volume --
VOL = {}
for r in csv.DictReader(open(f"{WS}/stocks_daily_volume.csv")):
    VOL.setdefault(r["stock"], []).append((r["date"],
                                            int(r["volume"])))
DAYS = {s: [d for d, _ in v] for s, v in VOL.items()}
VALS = {s: [x for _, x in v] for s, v in VOL.items()}

def rvol(stock, date):
    """(rvol, P) or (None, reason). P = last series day
    strictly before `date`; window = 20 days ending on P.
    Identical to the Round-15 frozen feature."""
    days = DAYS[stock]
    i = bisect.bisect_left(days, date) - 1
    if i < 0:
        return None, "no_prior_day"
    P = days[i]
    assert P < date, (stock, date, P)  # causality law
    if i < 19:
        return None, "insufficient_history"
    med = statistics.median(VALS[stock][i - 19:i + 1])
    if med <= 0:
        return None, "zero_median"
    return VALS[stock][i] / med, P

def mirror(rows_by_year):
    """Keep rows with rvol < 1.0 (the mirror). Returns
    (kept, stats): kept {yr: rows}; stats counts kept /
    dropped-high (rvol >= 1.0) / unclassifiable per year."""
    kept, stats = {}, {"kept": {}, "high": {}, "unclass": {}}
    for yr in (2025, 2026):
        k, high, un = [], 0, 0
        for t in rows_by_year[yr]:
            rv, _p = rvol(t["stock"], t["date"])
            if rv is None:
                un += 1
            elif rv < 1.0:
                k.append(t)
            else:
                high += 1
        kept[yr] = k
        stats["kept"][yr] = len(k)
        stats["high"][yr] = high
        stats["unclass"][yr] = un
    return kept, stats

def keyset(rows):
    return Counter(R16.row_id(t) for t in rows)

# ------------------------------------------------- sleeve sets --
sleeves = {}

f4bk = B14.comp_rows(books, "F4")
f4r, f4f, f4l, miss = B14.rescore(f4bk, "F4", 1.50, 0.95, "plain")
assert miss == 0
for yr in (2025, 2026):
    assert keyset(f4r[yr]) == keyset(f4bk[yr]), yr
sleeves["F4"] = {"comps": ("F4",), "real": f4r, "flip": f4f,
                 "late": f4l}
print("anchor OK: F4 rescore at T150/S095 'plain' == banked rows")

n4r, n4f, n4l = B14.n4_geo(1.50, 0.80)
n4bk = B14.comp_rows(books, "N4-V3")
for yr in (2025, 2026):
    assert keyset(n4r[yr]) == keyset(n4bk[yr]), yr
sleeves["N4-V3"] = {"comps": ("N4-V3",), "real": n4r,
                    "flip": n4f, "late": n4l}
print("anchor OK: N4 builder at T150/S080 == banked rows")

p2 = {"real": {}, "flip": {}, "late": {}}
for comp in ("P2F", "P2F-R2"):
    bk = B14.comp_rows(books, comp)
    got = None
    for fl in ("plain", "v2"):
        rr, ff, ll, m = B14.rescore(bk, comp, 1.25, 0.50, fl,
                                    open_entry=True)
        if m == 0 and all(keyset(rr[yr]) == keyset(bk[yr])
                          for yr in (2025, 2026)):
            got = (rr, ff, ll)
            break
    assert got is not None, comp
    for name, s in zip(("real", "flip", "late"), got):
        for yr in (2025, 2026):
            p2[name].setdefault(yr, []).extend(
                [{**t, "comp": comp} for t in s[yr]])
    print(f"anchor OK: {comp} rescore at T125/S050 == banked rows")
sleeves["P2F family"] = {"comps": ("P2F", "P2F-R2"),
                         "real": p2["real"], "flip": p2["flip"],
                         "late": p2["late"]}

def swap_in(bk, comps, rows_by_year):
    out = bk
    if len(comps) == 1:
        return R16.swap(out, comps[0], rows_by_year)
    for comp in comps:
        out = R16.swap(out, comp,
                       {yr: [t for t in rows_by_year[yr]
                             if t["comp"] == comp]
                        for yr in (2025, 2026)})
    return out

# ------------------------------------------------------ gates --
derived = {}

def run_gate(cycle, name):
    S = sleeves[name]
    kept_r, st = mirror(S["real"])
    kept_f, _ = mirror(S["flip"])
    kept_l, _ = mirror(S["late"])
    # Each set is conditioned on its own rows: classification
    # is a function of (stock, entry date) only, so a row and
    # its flip/late counterparts share one classification —
    # but a sleeve's flip population is law-filtered for the
    # flipped direction (e.g. N4's direction-scoped law), so
    # the sets' (stock, date) multisets need not be identical
    # and no count equality is asserted.
    var = swap_in(books, S["comps"], kept_r)
    pl = [R16.full_total(swap_in(books, S["comps"], kept_f)),
          R16.full_total(swap_in(books, S["comps"], kept_l))]
    out = R16.gate(books, var, pl, timing_violations=0)
    failed = R16.failed_legs(out)
    rec = R16.record(
        cycle,
        f"{name} volume MIRROR: keep prior-day rvol < 1.0 "
        f"(trailing-20-day median)", out,
        note=f"Mirror-conditioned population: kept "
             f"{st['kept']} of the sleeve's rows (dropped "
             f"rvol >= 1.0: {st['high']}; unclassifiable — "
             f"excluded from every set, never estimated: "
             f"{st['unclass']}). Every volume input dated "
             f"strictly before its entry date (prior trading "
             f"day P; 20-day window ending on P) — asserted "
             f"row by row in code; timing violations 0. "
             f"Placebos on the SAME mirror-conditioned "
             f"population: flipped swap book {pl[0]}; "
             f"one-bar-late swap book {pl[1]}. Failed legs: "
             f"{failed}.",
        extra={"conditioned_stats": st, "failed_legs": failed,
               "placebos": pl})
    derived[name] = {"real": kept_r, "flip": kept_f,
                     "late": kept_l, "stats": st,
                     "rec_var_jo": {yr: rec["var"][str(yr)]["jan_oct"]
                                    for yr in (2025, 2026)},
                     "banked": rec["banked"],
                     "failed_legs": failed}
    return rec

rec_f4 = run_gate("R16-02", "F4")
rec_n4 = run_gate("R16-03", "N4-V3")

# ------------------------------------------------- R16-04 (WS3) --
def single_leg_or_banked(rec):
    return rec["banked"] or len(R16.failed_legs(rec)) == 1

trigger = single_leg_or_banked(rec_f4) or \
    single_leg_or_banked(rec_n4)
if trigger:
    run_gate("R16-04", "P2F family")
else:
    R16.record_audit(
        "R16-04",
        "P2F volume MIRROR — NOT RUN (frozen WS3 condition)",
        "Neither WS1 (F4 mirror) nor WS2 (N4-V3 mirror) "
        "banked or failed on exactly one leg, so per the "
        "condition frozen in this round's pre-registration "
        "the P2F-family mirror gate does not run and no P2F "
        "mirror number is computed.")

with open(f"{WS}/r16_cond.pkl", "wb") as f:
    pickle.dump({k: {"real": v["real"], "flip": v["flip"],
                     "late": v["late"], "stats": v["stats"]}
                 for k, v in derived.items()}, f)
print("WS1-WS3 done; conditioned sets saved to r16_cond.pkl")
