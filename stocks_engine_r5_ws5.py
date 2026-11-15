#!/usr/bin/env python3
"""ROUND 5 — WS5: RED-MONTH DIAGNOSIS (Jun/Jul/Oct 2025) on the current
book, with at most ONE conditional candidate.

Diagnosis: decompose the three red months by component x regime cell
(and component x direction for the record), on the Round-4 ending book
(the book WS1-WS4 left unchanged — no Round-5 banking has occurred).

Signature rule (frozen before the scan is read): a (comp x cell) slice
qualifies ONLY if it is negative in EACH of Jun, Jul and Oct 2025,
negative across full-year 2025, and its three-month sum is <=
-Rs3,000. If at least one slice qualifies, the single strongest (most
negative three-month sum) is frozen as candidate R5-14: standing
exclusion of that (comp x cell) slice in BOTH years, gated whole-book
with chrono-removal and complement-removal placebos. If none
qualifies, the diagnosis is recorded and WS5 stops — no candidate is
manufactured.
"""
import sys, json
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r5_lib as R5

books = R5.load_books()
LABELS = R5.LABELS
MONTHS = ("2025-06", "2025-07", "2025-10")
b25 = books[2025]

def agg(rows, keyfn):
    out = defaultdict(lambda: [0.0, 0])
    for t in rows:
        k = keyfn(t)
        out[k][0] += t["net"]
        out[k][1] += 1
    return {"|".join(str(x) for x in k) if isinstance(k, tuple) else k:
            (round(v[0], 2), v[1]) for k, v in sorted(out.items())}

diag = {}
for m in MONTHS:
    rows = [t for t in b25 if t["date"].startswith(m)]
    diag[m] = {
        "total": round(sum(t["net"] for t in rows), 2),
        "trades": len(rows),
        "by_comp": agg(rows, lambda t: t["comp"]),
        "by_comp_cell": agg(rows, lambda t: (t["comp"],
                                             LABELS.get(t["date"]))),
        "by_comp_dir": agg(rows, lambda t: (t["comp"], t["dir"])),
    }
    print(f"{m}: total {diag[m]['total']} on {diag[m]['trades']} trades")
    for k, v in diag[m]["by_comp"].items():
        print(f"    {k:12s} {v[0]:>10}  ({v[1]} tr)")

full_by_cc = agg(b25, lambda t: (t["comp"], LABELS.get(t["date"])))
three = {}
keys = set()
for m in MONTHS:
    keys |= set(diag[m]["by_comp_cell"].keys())
for k in sorted(keys):
    per = {m: diag[m]["by_comp_cell"].get(k, (0.0, 0))[0] for m in MONTHS}
    three[k] = {"months": per, "sum3": round(sum(per.values()), 2),
                "full2025": full_by_cc.get(k, (0.0, 0))[0]}
    print(f"slice {k}: Jun {per['2025-06']} | Jul {per['2025-07']} | "
          f"Oct {per['2025-10']} | sum3 {three[k]['sum3']} | full-2025 "
          f"{three[k]['full2025']}")

qualifying = [k for k, v in three.items()
              if all(v["months"][m] < 0 for m in MONTHS)
              and v["full2025"] < 0 and v["sum3"] <= -3000.0]
print("qualifying (comp x cell) signatures:", qualifying)
json.dump({"months": {m: diag[m] for m in MONTHS},
           "slices": {str(k): v for k, v in three.items()},
           "qualifying": [str(k) for k in qualifying]},
          open(f"{WS}/r5_ws5_diag.json", "w"), indent=1)

worst = {m: sorted(diag[m]["by_comp"].items(), key=lambda kv: kv[1][0])[:3]
         for m in MONTHS}
R5.record_audit(
    "R5-13", "WS5 red-month diagnosis (Jun/Jul/Oct 2025, comp x cell)",
    note=f"Jun total {diag['2025-06']['total']}, Jul "
         f"{diag['2025-07']['total']}, Oct {diag['2025-10']['total']}. "
         f"Worst comps per month: "
         + "; ".join(f"{m}: " + ", ".join(f"{c} {v[0]}" for c, v in w)
                     for m, w in worst.items())
         + f". Frozen signature rule (neg in all 3 months AND neg "
         f"full-2025 AND sum3 <= -3000): qualifying slices = "
         f"{[str(k) for k in qualifying]}. Full table: "
         f"r5_ws5_diag.json.",
    extra={"diag_file": "r5_ws5_diag.json",
           "qualifying": [str(k) for k in qualifying]})

if qualifying:
    comp, cell = min(qualifying, key=lambda k: three[k]["sum3"]).split("|")
    print(f"frozen candidate: exclude ({comp} x {cell})")
    var = {yr: [t for t in books[yr]
                if not (t["comp"] == comp
                        and LABELS.get(t["date"]) == cell)]
           for yr in (2025, 2026)}
    removed_n = sum(len(books[yr]) - len(var[yr]) for yr in (2025, 2026))
    complement = {yr: [t for t in books[yr] if t["comp"] != comp]
                  + [t for t in books[yr]
                     if t["comp"] == comp
                     and LABELS.get(t["date"]) == cell]
                  for yr in (2025, 2026)}
    pl = [R.chrono_placebo(books, comp, removed_n),
          R5.full_total(complement)]
    out = R5.gate(books, var, pl, timing_violations=0)
    sig = three[f"{comp}|{cell}"]
    R5.record("R5-14", f"WS5 conditional: exclude {comp} x {cell}-cell "
                       f"slice (both years)", out,
              note=f"signature frozen from the diagnosis before gating: "
                   f"Jun {sig['months']['2025-06']}, "
                   f"Jul {sig['months']['2025-07']}, "
                   f"Oct {sig['months']['2025-10']}, "
                   f"full-2025 {sig['full2025']}; "
                   f"removed {removed_n} trades; timing: exclusion of "
                   f"existing audited rows -> 0 violations; placebos: "
                   f"chrono-removal book {pl[0]}; complement book "
                   f"{pl[1]}")
    if out["verdict"]:
        books = var
        R5.save_books(books)
        print("    -> BANKED; incumbent updated")
else:
    print("No qualifying signature — WS5 stops at the diagnosis.")

print("WS5 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
