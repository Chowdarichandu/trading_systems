#!/usr/bin/env python3
"""STOCK ENGINE — TIME-OF-DAY PROFITABILITY MAP (Deliverable 1,
owner order 2026-11-12 07:10 IST: "at which time interval — first
half or second half of the day — entry remains profitable").

For EVERY SarvaRitu component (frozen twins + causal variants where
they exist: F4/F4-C, INV-LONG/INV-LONG-C, INV-ABOVE/INV-ABOVE-C,
N4-V3, P2F, P2F-R2, R2-LOWBAND), bucket trades by ENTRY TIME:
  B1 [09:15-10:30) · B2 [10:30-12:00) · B3 [12:00-13:30) ·
  B4 [13:30-15:10] (+ overflow bucket if any entry falls outside),
plus FIRST HALF (entry <= 12:00) vs SECOND HALF (entry > 12:00)
per the owner's framing (note: a 12:00-exact entry sits in B3 by
the bucket edges but in FIRST HALF by the <= rule — the task's own
definitions; both are reported as specified).
Per bucket: trades, net, win rate, expectancy, ex-top-3 (the three
best STOCKS by net inside the bucket removed — V1.extop3 semantics).

Universes/periods:
  (a) 25-universe full history, Jan-Oct 2026 and Jan-Oct 2025
      separately. Chain comps: the causal3 gate leg-3 canonical
      CSVs (post-law, independently re-summed when written).
      Reaction family: rebuilt here via the gate's own
      build_live4_detailed on the FULLHIST machinery + v2 law,
      cross-checked against the production logger's build_book.
  (b) 1,081-wide window Oct 1 - Nov 11 2026 (27 trading days).
      Frozen twins: sarvasetu_top3_v2 pool CSV (post-law).
      Causal variants: stock_engine_causal3_variant_rows.csv
      (post-law). Reaction family: the v2 pool CSV.

VERDICT RULE (pre-registered, applied to (a) only): a bucket is
PROFITABLE iff trades_2026 >= 15 AND net_2026 > 0 AND
ex-top-3_2026 > 0 AND NOT deeply-negative-2025, where
deeply-negative-2025 := trades_2025 >= 15 AND net_2025 < -Rs5,000
AND ex-top-3_2025 < 0. trades_2026 < 15 -> SPARSE (no verdict).
2026-positive but deeply-negative-2025 -> REJECTED-2025.
Otherwise NOT-PROFITABLE. The S1/S2 session windows are read from
these verdicts by the invention script — the causal variant's OWN
2026 map governs its windows.

Paper only, real money Rs0. Basis: provisional per 100 shares,
Rs40/trade (nets as stored in the source books).
Outputs: stock_engine_timeofday_2026-11-12.csv (all bucket rows),
stock_engine_timeofday_2026-11-12_verdicts.json (per-comp bucket
verdicts + chosen S1/S2 windows), console tables for the report.
"""
import csv, json, sys, time
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stock_engine_causal3_gate as G3
import stocks_sarvaritu_logger as L

COMPS = ["N4-V3", "P2F", "P2F-R2", "R2-LOWBAND",
         "F4", "F4-C", "INV-LONG", "INV-LONG-C", "INV-ABOVE", "INV-ABOVE-C"]
CHAIN_PAIRS = [("F4", "F4-C"), ("INV-LONG", "INV-LONG-C"),
               ("INV-ABOVE", "INV-ABOVE-C")]
BUCKETS = ["09:15-10:30", "10:30-12:00", "12:00-13:30", "13:30-15:10",
           "FIRST-HALF", "SECOND-HALF"]
SPARSE_N = 15
DEEP_NEG = -5000.0


def bucket_of(t):
    if "09:15" <= t < "10:30":
        return "09:15-10:30"
    if "10:30" <= t < "12:00":
        return "10:30-12:00"
    if "12:00" <= t < "13:30":
        return "12:00-13:30"
    if "13:30" <= t <= "15:10":
        return "13:30-15:10"
    return "OUTSIDE"


def half_of(t):
    return "FIRST-HALF" if t <= "12:00" else "SECOND-HALF"


def bstats(rows):
    a = V1.agg(rows)
    ex3, top3 = V1.extop3(rows)
    return {"trades": a["trades"], "net": a["net"],
            "win_rate": a["win_rate"],
            "expectancy": (round(a["net"] / a["trades"], 2)
                           if a["trades"] else 0.0),
            "ex_top3": ex3, "top3_stocks": top3}


def bucket_rows(universe, period, comp, rows):
    out = []
    for b in BUCKETS[:4] + ["OUTSIDE"]:
        br = [r for r in rows if bucket_of(r["entry_time"]) == b]
        if br or b != "OUTSIDE":
            out.append({"universe": universe, "period": period,
                        "comp": comp, "bucket": b, **bstats(br)})
    for h in ("FIRST-HALF", "SECOND-HALF"):
        hr = [r for r in rows if half_of(r["entry_time"]) == h]
        out.append({"universe": universe, "period": period,
                    "comp": comp, "bucket": h, **bstats(hr)})
    out.append({"universe": universe, "period": period, "comp": comp,
                "bucket": "ALL", **bstats(rows)})
    return out


def main():
    t0 = time.time()
    all_rows = []          # map CSV rows
    sets = {}              # (universe, period, comp) -> trade rows

    # ---------- (a) 25-universe history: chain comps from gate CSVs
    for year in ("2025", "2026"):
        for comp in ("F4", "F4-C", "INV-LONG", "INV-LONG-C",
                     "INV-ABOVE", "INV-ABOVE-C"):
            rows = list(csv.DictReader(open(
                f"{WS}/stock_engine_causal3_hist_{comp}_{year}.csv")))
            rows = [{"date": r["date"], "stock": r["stock"],
                     "entry_time": r["entry_time"],
                     "net": float(r["net"])} for r in rows]
            sets[("hist25", year, comp)] = rows

    # ---------- (a) reaction family rebuilt on FULLHIST machinery
    print("loading FULLHIST machinery for reaction family...",
          flush=True)
    g = L.load_machinery(L.FULLHIST, "2026-10-28")
    labels = L.regime_labels(g)
    days_by_year = {
        "2025": [d for d in g["ALL_DAYS"]
                 if d.startswith("2025") and d <= "2025-10-31"],
        "2026": [d for d in g["ALL_DAYS"]
                 if d.startswith("2026") and d <= "2026-10-31"],
    }
    CALS = {"2025": (f"{WS}/stock_event_calendar_2025.csv",
                     "2025-01-01", "2025-12-31"),
            "2026": (f"{WS}/stock_event_calendar_jan_oct_2026.csv",
                     "2026-01-01", "2026-10-28")}
    for year, days in days_by_year.items():
        cal, lo, hi = CALS[year]
        live4 = G3.build_live4_detailed(g, cal, lo, hi, days)
        live4 = L.apply_law(live4, labels)
        live4 = [t for t in live4 if t["date"] in days]
        # cross-check vs production build_book reaction subset
        prod = L.build_book(g, cal, lo, hi, days)
        from collections import Counter
        # both builders spill reaction trades past Oct 31 (late-Oct
        # events reacting in Nov); the Jan-Oct map day-set filter is
        # applied to BOTH sides of the cross-check
        pk = Counter((t["comp"], t["date"], t["stock"], t["dir"],
                      t["entry_time"], round(float(t["net"]), 2))
                     for t in prod
                     if t["comp"] in ("N4-V3", "P2F", "P2F-R2",
                                      "R2-LOWBAND")
                     and t["date"] in days)
        mk = Counter((t["comp"], t["date"], t["stock"], t["dir"],
                      t["entry_time"], round(float(t["net"]), 2))
                     for t in live4)
        assert pk == mk, (f"reaction xcheck FAILED {year}: "
                          f"prod {sum(pk.values())} vs mine "
                          f"{sum(mk.values())}")
        print(f"{year} reaction xcheck OK: {len(live4)} rows "
              f"({time.time()-t0:.0f}s)", flush=True)
        for comp in ("N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"):
            rows = [{"date": t["date"], "stock": t["stock"],
                     "entry_time": t["entry_time"],
                     "net": round(float(t["net"]), 2)}
                    for t in live4 if t["comp"] == comp]
            sets[("hist25", year, comp)] = rows

    # ---------- (b) wide window Oct 1 - Nov 11 2026
    pool = list(csv.DictReader(
        open(f"{WS}/sarvasetu_top3_v2_2026-11-11_pool.csv")))
    for comp in ("N4-V3", "P2F", "P2F-R2", "R2-LOWBAND", "F4",
                 "INV-LONG", "INV-ABOVE"):
        rows = [{"date": r["date"], "stock": r["stock"],
                 "entry_time": r["entry_time"], "net": float(r["net"])}
                for r in pool if r["comp"] == comp]
        sets[("wide1081", "2026-10-01/11-11", comp)] = rows
    varr = list(csv.DictReader(
        open(f"{WS}/stock_engine_causal3_variant_rows.csv")))
    for comp in ("F4-C", "INV-LONG-C", "INV-ABOVE-C"):
        rows = [{"date": r["date"], "stock": r["stock"],
                 "entry_time": r["entry_time"], "net": float(r["net"])}
                for r in varr if r["comp"] == comp]
        sets[("wide1081", "2026-10-01/11-11", comp)] = rows

    # ---------- bucket everything
    for (uni, per, comp), rows in sorted(sets.items()):
        all_rows.extend(bucket_rows(uni, per, comp, rows))

    fields = ["universe", "period", "comp", "bucket", "trades", "net",
              "win_rate", "expectancy", "ex_top3", "top3_stocks"]
    with open(f"{WS}/stock_engine_timeofday_2026-11-12.csv", "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_rows:
            w.writerow({**r, "top3_stocks":
                        ";".join(f"{k}:{v:+.2f}"
                                 for k, v in r["top3_stocks"])})

    # ---------- verdicts from (a): 2026 rule + 2025 guard
    def get(uni, per, comp, b):
        for r in all_rows:
            if (r["universe"], r["period"], r["comp"], r["bucket"]) == \
                    (uni, per, comp, b):
                return r
        return {"trades": 0, "net": 0.0, "ex_top3": 0.0}

    verdicts = {}
    for comp in COMPS:
        verdicts[comp] = {}
        for b in BUCKETS:
            r26 = get("hist25", "2026", comp, b)
            r25 = get("hist25", "2025", comp, b)
            if r26["trades"] < SPARSE_N:
                v = "SPARSE"
            else:
                deep25 = (r25["trades"] >= SPARSE_N
                          and r25["net"] < DEEP_NEG and r25["ex_top3"] < 0)
                if r26["net"] > 0 and r26["ex_top3"] > 0:
                    v = "REJECTED-2025" if deep25 else "PROFITABLE"
                else:
                    v = "NOT-PROFITABLE"
            verdicts[comp][b] = {
                "verdict": v,
                "2026": {k: r26[k] for k in
                         ("trades", "net", "win_rate", "expectancy",
                          "ex_top3")},
                "2025": {k: r25[k] for k in
                         ("trades", "net", "win_rate", "expectancy",
                          "ex_top3")}}
    windows = {}
    for comp in ("F4-C", "INV-LONG-C", "INV-ABOVE-C"):
        windows[comp] = [b for b in BUCKETS[:4]
                         if verdicts[comp][b]["verdict"] == "PROFITABLE"]
    with open(f"{WS}/stock_engine_timeofday_2026-11-12_verdicts.json",
              "w") as f:
        json.dump({"verdicts": verdicts, "s1_windows": windows,
                   "rule": "PROFITABLE iff trades_2026>=15 and "
                           "net_2026>0 and ex_top3_2026>0 and not "
                           "(trades_2025>=15 and net_2025<-5000 and "
                           "ex_top3_2025<0); SPARSE if trades_2026<15",
                   "bucket_edges": "B1 [09:15,10:30) B2 [10:30,12:00) "
                                   "B3 [12:00,13:30) B4 [13:30,15:10]; "
                                   "halves: FH entry<=12:00, SH >12:00"},
                  f, indent=1, default=str)
    print(json.dumps({"s1_windows": windows}, indent=1), flush=True)
    print(f"MAP DONE in {time.time()-t0:.0f}s — "
          f"{len(all_rows)} bucket rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
