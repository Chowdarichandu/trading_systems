#!/usr/bin/env python3
"""ROUND 13 — R13-01 audit + WS1: the new sweep mechanism.

R13-01: starting books re-verified from the Round-12 CSVs
(the R13 lib asserts JO / full / row counts at load; the two
red 2025 months are asserted here).
R13-02: SWEEP-RECLAIM LONG (prior-day-low sweep + reclaim)
added to the banked book, gated whole-book.
R13-03: SWEEP-REJECT SHORT (prior-day-high sweep + rejection,
the pre-registered symmetric variant), same treatment.
Placebos per candidate: the flipped book and the one-bar-late
book (combined totals), the engine convention.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r13_lib as R13
import stocks_engine_r13_builders as B13

books = R13.load_books()

# ------------------------------------------------------ R13-01 --
jul = R13.month_net(books[2025], "2025-07")
oct_ = R13.month_net(books[2025], "2025-10")
assert jul == -2101.93, jul
assert oct_ == -3751.28, oct_
R13.record_audit(
    "R13-01",
    "Starting-book verification (Round-12 ending book)",
    f"Books re-summed from stocks_engine_r12_book{{2025,2026}}"
    f"_trades.csv: 2025 JO {R13.JO_BASE[2025]} / full "
    f"{R13.FULL_BASE[2025]} / {R13.ROWS_BASE[2025]} rows; 2026 "
    f"JO {R13.JO_BASE[2026]} / full {R13.FULL_BASE[2026]} / "
    f"{R13.ROWS_BASE[2026]} rows — exact vs the Round-12 "
    f"record. Red 2025 Jan-Oct months asserted: Jul {jul}, "
    f"Oct {oct_} (decomposed in R12; no separator; not "
    f"re-tested).",
    extra={"jul_2025": jul, "oct_2025": oct_})
print("R13-01 audit OK")

# ---------------------------------------------------- WS1 gates --
def gate_sweep(cycle, mode):
    real, flip, late, viol, stats = B13.sweep_rows(mode)
    assert viol == 0, viol
    comp = real[2025][0]["comp"] if real[2025] else \
        real[2026][0]["comp"]
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    rows = {yr: len(real[yr]) for yr in (2025, 2026)}
    var = R13.add_comp(books, comp, real)
    pl = [R13.full_total(R13.add_comp(books, comp, flip)),
          R13.full_total(R13.add_comp(books, comp, late))]
    out = R13.gate(books, var, pl, timing_violations=viol)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    desc = ("prior-day-low sweep + reclaim, LONG"
            if mode == "reclaim" else
            "prior-day-high sweep + rejection, SHORT")
    R13.record(
        cycle,
        f"New mechanism {comp} ({desc}), T125/S050, added "
        f"to the banked book", out,
        note=f"Standalone {sa[2025]} / {sa[2026]} on "
             f"{rows[2025]}/{rows[2026]} rows. Population "
             f"{stats['population_days']} stock-days, sweeps "
             f"{stats['sweep_days']}, signals "
             f"{stats['signal_days']} (no reclaim "
             f"{stats['no_reclaim']}, no entry bar "
             f"{stats['no_entry_bar']}). Placebos: flipped book "
             f"{pl[0]}; late book {pl[1]}. Timing violations "
             f"{viol}. Failed legs: {failed}.",
        extra={"standalone": {str(k): v for k, v in sa.items()},
               "rows": {str(k): v for k, v in rows.items()},
               "stats": stats, "failed_legs": failed})
    return out

gate_sweep("R13-02", "reclaim")
gate_sweep("R13-03", "reject")
print("WS1 done.")
