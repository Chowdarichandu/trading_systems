#!/usr/bin/env python3
"""ROUND 15 — WS2 record + WS3 volume gates.
R15-04 records the volume build (stocks_engine_r15_volfetch
.py; coverage in stocks_daily_volume_coverage.json).
R15-05 is the FROZEN diagnostic (pre-registered): subset
arithmetic on banked nets only. For sleeves F4, N4-V3 and
the P2F family it computes the combined Jan-Oct delta of
keeping only rows with rvol >= 1.0, where rvol = prior-day
volume / trailing-20-day median (window ending on the prior
day, inclusive). It chooses which cells earn an exact gate;
it scores nothing. R15-06 / R15-07 gate the top one / two
strictly-positive sleeves whole-book, with their conditioned
flip and late books as placebos.

CAUSALITY LAW asserted row by row: every volume date used
is strictly before the entry date (the prior trading day P
and its trailing window). Rows with < 20 prior volume days
or a missing P are UNCLASSIFIABLE — excluded from every
conditioned set (real and placebos alike), counted by name,
never estimated.
"""
import bisect, csv, json, statistics, sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r15_lib as R15
import stocks_engine_r14_builders as B14

books = R15.load_books()

# ---------------------------------------------------- R15-04 record --
cov = json.load(open(f"{WS}/stocks_daily_volume_coverage.json"))
psy = cov["per_stock_year"]
holes = {k: v["holes"] for k, v in psy.items() if v["holes"]}
zeros = {k: v["zero_volume_days"] for k, v in psy.items()
         if v["zero_volume_days"]}
n_rows = sum(1 for _ in open(f"{WS}/stocks_daily_volume.csv")) - 1
R15.record_audit(
    "R15-04",
    "Volume data axis BUILD (daily volume, 25 stocks + NIFTY)",
    f"Fetched via the registered connector path (v3 days/1, "
    f"browser UA header; credential via surrogate only). "
    f"Stored NEW dataset stocks_daily_volume.csv ({n_rows} "
    f"rows, span 2024-11-15..2026-10-31; the pre-2025 tail "
    f"is lookback only for the trailing-20-day median). No "
    f"existing candle file altered. Coverage per stock-year "
    f"(expected = machinery daily days): ALL 25 stocks "
    f"COMPLETE in both years — 2025: 249/249 days each, 2026: "
    f"203/203 each; holes: NONE ({len(holes)} stock-years "
    f"with holes); zero-volume days in the 25 stocks: NONE. "
    f"The 2026 series carries 2 days beyond the machinery's "
    f"stored daily span (2026-10-29/30) — present in the API "
    f"series, not holes. NIFTY (index, no traded volume): "
    f"series stored as returned — volume 0 on all "
    f"{len(zeros.get('NIFTY|2025', []))} expected days of "
    f"2025 and all of 2026; reported as returned, never "
    f"estimated, and used by no gate. Fetch errors: "
    f"{cov['fetch_errors']}.",
    extra={"dataset_rows": n_rows, "holes": holes,
           "zero_volume_stock_years": list(zeros)})

# --------------------------------------------------------- volume --
VOL = {}
for r in csv.DictReader(open(f"{WS}/stocks_daily_volume.csv")):
    VOL.setdefault(r["stock"], []).append((r["date"],
                                            int(r["volume"])))
DAYS = {s: [d for d, _ in v] for s, v in VOL.items()}
VALS = {s: [x for _, x in v] for s, v in VOL.items()}

def rvol(stock, date):
    """(rvol, P) or (None, reason). P = last series day
    strictly before `date`; window = 20 days ending on P."""
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

def conditioned(rows_by_year):
    kept, stats = {}, {"kept": {}, "low": {}, "unclass": {}}
    for yr in (2025, 2026):
        k, low, un = [], 0, 0
        for t in rows_by_year[yr]:
            rv, _p = rvol(t["stock"], t["date"])
            if rv is None:
                un += 1
            elif rv >= 1.0:
                k.append(t)
            else:
                low += 1
        kept[yr] = k
        stats["kept"][yr] = len(k)
        stats["low"][yr] = low
        stats["unclass"][yr] = un
    return kept, stats

def keyset(rows):
    return Counter(R15.row_id(t) for t in rows)

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
        return R15.swap(out, comps[0], rows_by_year)
    for comp in comps:
        out = R15.swap(out, comp,
                       {yr: [t for t in rows_by_year[yr]
                             if t["comp"] == comp]
                        for yr in (2025, 2026)})
    return out

# ------------------------------------------------------ R15-05 --
diag = {}
for name, S in sleeves.items():
    kept, stats = conditioned(S["real"])
    S["kept"], S["stats"] = kept, stats
    var = swap_in(books, S["comps"], kept)
    d = {yr: round(R15.jo(var, yr) - R15.jo(books, yr), 2)
         for yr in (2025, 2026)}
    diag[name] = {**d, "combined": round(d[2025] + d[2026], 2),
                  "kept": stats["kept"], "low": stats["low"],
                  "unclass": stats["unclass"]}
    print(f"diagnostic {name}: JO deltas {d}, combined "
          f"{diag[name]['combined']}; kept {stats['kept']}, "
          f"dropped-low {stats['low']}, unclass {stats['unclass']}")
ranked = sorted((n for n in diag if diag[n]["combined"] > 0),
                key=lambda n: -diag[n]["combined"])
R15.record_audit(
    "R15-05",
    "Volume diagnostic (frozen rule: keep rvol >= 1.0; sleeve "
    "choice by combined Jan-Oct delta, banked nets only)",
    "Combined JO deltas of the rvol >= 1.0 restriction, by "
    "sleeve: " + "; ".join(
        f"{n}: 2025 {diag[n][2025]:+} / 2026 {diag[n][2026]:+} "
        f"(combined {diag[n]['combined']:+}; kept "
        f"{diag[n]['kept']}, dropped-low {diag[n]['low']}, "
        f"unclassifiable {diag[n]['unclass']})"
        for n in diag) +
    f". Frozen ranking for gates: {ranked}. Causality "
    f"asserted per row (prior day P < entry date; window "
    f"ends on P). The diagnostic scores nothing — it only "
    f"assigns the at-most-two gated cells.",
    extra={"diagnostic": diag, "gate_order": ranked})

# ------------------------------------------------------ gates --
def run_gate(cycle, name):
    S = sleeves[name]
    kept_r, _ = conditioned(S["real"])
    kept_f, _ = conditioned(S["flip"])
    kept_l, _ = conditioned(S["late"])
    var = swap_in(books, S["comps"], kept_r)
    pl = [R15.full_total(swap_in(books, S["comps"], kept_f)),
          R15.full_total(swap_in(books, S["comps"], kept_l))]
    out = R15.gate(books, var, pl, timing_violations=0)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    st = S["stats"]
    R15.record(
        cycle,
        f"{name} volume conditioning: keep prior-day rvol "
        f">= 1.0 (trailing-20-day median)", out,
        note=f"Conditioned population: kept {st['kept']} of "
             f"the sleeve's rows (dropped rvol < 1.0: "
             f"{st['low']}; unclassifiable — excluded from "
             f"every set, never estimated: {st['unclass']}). "
             f"Every volume input dated strictly before its "
             f"entry date (prior trading day P; 20-day window "
             f"ending on P) — asserted row by row in code; "
             f"timing violations 0. Placebos on the SAME "
             f"conditioned population: flipped swap book "
             f"{pl[0]}; one-bar-late swap book {pl[1]}. "
             f"Failed legs: {failed}.",
        extra={"conditioned_stats": st,
               "diagnostic_combined_delta": diag[name]["combined"],
               "failed_legs": failed})
    return out

if len(ranked) >= 1:
    run_gate("R15-06", ranked[0])
else:
    R15.record_audit(
        "R15-06", "Volume gate 1 — NOT RUN",
        "No sleeve showed a strictly-positive combined "
        "diagnostic delta; per the frozen rule WS3 closes "
        "with no gate.")
if len(ranked) >= 2:
    run_gate("R15-07", ranked[1])
else:
    R15.record_audit(
        "R15-07", "Volume gate 2 — NOT RUN",
        "Fewer than two sleeves showed a strictly-positive "
        "combined diagnostic delta; per the frozen rule no "
        "second volume gate is run.")
print("WS3 done.")
