#!/usr/bin/env python3
"""ROUND 7 — WS1: REXP-SHORT REPAIR (R7-01 audit; R7-02 DOWN+FLAT;
R7-03 DOWN-only). Construction and verdict rule EXACTLY as
pre-registered in stocks_engine_round7_2026-11-02.md.

R7-01 decomposes R6-10's frozen population (rebuilt verbatim and
re-anchored to R6-10's recorded standalone before anything is read)
by regime cell x year and by stock (2026). R7-02 / R7-03 gate the
cell-restricted forms whole-book.
"""
import sys
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r7_lib as R7
import stocks_engine_r7_builders as B

books = R7.load_books()
LABELS = FL.LABELS
COMP = "REXP-SHORT"

def relabel(rows, comp):
    return {yr: [dict(t, comp=comp) for t in rows[yr]] for yr in rows}

def gate_form(cyc, label, real, flipped, late, viol, note_extra):
    real = relabel(real, COMP)
    flipped = relabel(flipped, "REXP-LONG")
    late = relabel(late, COMP)
    present = any(t["comp"] == COMP for yr in (2025, 2026)
                  for t in books[yr])
    var = (R7.swap(books, COMP, real) if present
           else R7.add_comp(books, COMP, real))
    base_wo = {yr: [t for t in books[yr] if t["comp"] != COMP]
               for yr in (2025, 2026)}
    pl = [R7.full_total(R7.add_comp(base_wo, "REXP-LONG", flipped)),
          R7.full_total(R7.add_comp(base_wo, COMP, late))]
    out = R7.gate(books, var, pl, timing_violations=viol)
    n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
    sa = {str(yr): round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    rec = R7.record(
        cyc, label, out,
        note=f"population trades {n}; standalone {sa}; timing audit: "
             f"entry bar (10:20) strictly after the signal bar "
             f"(10:10) on every row, violations counted = {viol}; "
             f"placebos: opposite-direction book {pl[0]}; "
             f"one-bar-late book {pl[1]}. {note_extra}",
        extra={"standalone": sa, "population_trades": n})
    return out, var

# ------------------------------------------------------- anchor build
real, flipped, late, viol = B.rexp_rows("SHORT", cells=None)
assert viol == 0, viol
sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
n_all = len(real[2025]) + len(real[2026])
assert sa == {2025: 14409.54, 2026: -10286.95}, sa
assert n_all == 237, n_all
print(f"R6-10 anchor OK (standalone +14,409.54 / -10,286.95; "
      f"{n_all} trades)")

# ------------------------------------------------------------ R7-01 --
def decomp(rows, yr, jo_only):
    by_cell = defaultdict(lambda: [0, 0.0])
    by_stock = defaultdict(lambda: [0, 0.0])
    for t in rows[yr]:
        if jo_only and t["date"] > f"{yr}-10-31":
            continue
        c = LABELS.get(t["date"])
        by_cell[c][0] += 1
        by_cell[c][1] = round(by_cell[c][1] + t["net"], 2)
        by_stock[t["stock"]][0] += 1
        by_stock[t["stock"]][1] = round(by_stock[t["stock"]][1]
                                        + t["net"], 2)
    return ({k: tuple(v) for k, v in sorted(by_cell.items())},
            {k: tuple(v) for k, v in sorted(
                by_stock.items(), key=lambda kv: kv[1][1])})

d = {}
for yr in (2025, 2026):
    cj, sj = decomp(real, yr, True)
    cf, _ = decomp(real, yr, False)
    d[yr] = {"cells_JO": cj, "cells_full": cf, "stocks_JO": sj}
    print(f"{yr} cells (Jan-Oct): {cj}")
    print(f"{yr} cells (full):    {cf}")
print("2026 stocks (Jan-Oct), worst first:")
for s, (n, v) in list(d[2026]["stocks_JO"].items())[:12]:
    print(f"   {s}: {n} tr, {v}")
print("2025 stocks (Jan-Oct), worst first:")
for s, (n, v) in list(d[2025]["stocks_JO"].items())[:6]:
    print(f"   {s}: {n} tr, {v}")

c26 = d[2026]["cells_JO"]
c25 = d[2025]["cells_JO"]
R7.record_audit(
    "R7-01",
    "REXP-SHORT 2026-damage decomposition (R6-10 population rebuilt "
    "verbatim, anchor exact)",
    f"R6-10 anchor reproduced exactly (standalone +14,409.54 / "
    f"-10,286.95; 237 trades; timing violations 0). 2026 Jan-Oct by "
    f"regime cell: {c26}. 2025 Jan-Oct by cell: {c25}. 2026 by stock "
    f"(worst first): "
    + "; ".join(f"{s} {v} ({n} tr)" for s, (n, v)
                in list(d[2026]["stocks_JO"].items())[:8])
    + ". Decomposition only — no candidate scored in this cycle.",
    extra={"cells_2026_JO": {k: {"trades": v[0], "net": v[1]}
                             for k, v in c26.items()},
           "cells_2025_JO": {k: {"trades": v[0], "net": v[1]}
                             for k, v in c25.items()},
           "stocks_2026_JO": {k: {"trades": v[0], "net": v[1]}
                              for k, v in
                              d[2026]["stocks_JO"].items()}})

# ------------------------------------------------------------ R7-02 --
real_df, flip_df, late_df, viol_df = B.rexp_rows(
    "SHORT", cells={"DOWN", "FLAT"})
assert viol_df == 0, viol_df
out, var = gate_form(
    "R7-02",
    "REXP-SHORT restricted to DOWN+FLAT regime cells (R6-10 repair: "
    "first-hour range >= 2x trailing median, bottom-quartile close, "
    "entry 10:20, T125/S050)", real_df, flip_df, late_df, viol_df,
    "Cell restriction per the R7-01 decomposition; the banked "
    "GAP-FADE sleeves are untouched.")
if out["verdict"]:
    books = var
    R7.save_books(books)
    print("    -> BANKED; incumbent updated")

# ------------------------------------------------------------ R7-03 --
real_d, flip_d, late_d, viol_d = B.rexp_rows("SHORT",
                                             cells={"DOWN"})
assert viol_d == 0, viol_d
out, var = gate_form(
    "R7-03",
    "REXP-SHORT restricted to DOWN regime cells only (R6-10 repair, "
    "narrower form)", real_d, flip_d, late_d, viol_d,
    "Gated as a swap of the REXP-SHORT comp if R7-02 banked, else "
    "as an addition.")
if out["verdict"]:
    books = var
    R7.save_books(books)
    print("    -> BANKED; incumbent updated")

print("WS1 done. Incumbent Jan-Oct:",
      {yr: R7.jo(books, yr) for yr in (2025, 2026)})
