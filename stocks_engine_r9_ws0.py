#!/usr/bin/env python3
"""ROUND 9 — WS0 (R9-01, audit): FLIP DECOMPOSITION.

The R8-02 max stack fails leg (f) only: Jan 2025 +2,200.31 ->
-715.46 (delta -2,915.77) and Dec 2025 +1,207.95 -> -99.76
(delta -1,307.71). The four ingredients act on disjoint
components, so each month's stack delta is exactly the sum of
the four per-ingredient deltas. This audit applies each
ingredient ALONE to the starting book (constructions re-anchored
at R8-01 prices by stocks_engine_r9_ingredients) and attributes
every month of 2025/2026 to its ingredient(s). No candidate is
scored here.
"""
import sys, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
books = ing["books"]

APPLIERS = {
    "R2-26 (INV-ABOVE T150/S080 swap)": ING.apply_r226,
    "R5-03-clean (fade>=1.25% swap, INC retired)": ING.apply_r503,
    "R5-07-CERT (NE-REV certified add)": ING.apply_cert,
    "R7-03 (REXP-SHORT DOWN add)": ING.apply_rexp,
}

def months_of(bk, yr):
    out = {}
    for t in bk[yr]:
        out[t["date"][:7]] = round(out.get(t["date"][:7], 0.0)
                                   + t["net"], 2)
    return out

base_m = {yr: months_of(books, yr) for yr in (2025, 2026)}
deltas = {}
for name, fn in APPLIERS.items():
    var = fn(books, ing)
    deltas[name] = {}
    for yr in (2025, 2026):
        vm = months_of(var, yr)
        allm = sorted(set(base_m[yr]) | set(vm))
        deltas[name][yr] = {m: round(vm.get(m, 0.0)
                                     - base_m[yr].get(m, 0.0), 2)
                            for m in allm}

for yr, mo, expect in ((2025, "2025-01", -2915.77),
                       (2025, "2025-12", -1307.71)):
    tot = round(sum(deltas[n][yr][mo] for n in APPLIERS), 2)
    print(f"\n== {mo}: base {base_m[yr][mo]} -> stack "
          f"{round(base_m[yr][mo] + tot, 2)} (delta {tot}, "
          f"expected {expect})")
    assert tot == expect, (mo, tot, expect)
    for n in APPLIERS:
        print(f"   {n}: {deltas[n][yr][mo]}")

print("\n== full-year 2025 per-ingredient month deltas")
hdr = [f"{m:>9}" for m in
       [f"2025-{i:02d}" for i in range(1, 13)]]
print("ingredient".ljust(46), *hdr)
for n in APPLIERS:
    row = [f"{deltas[n][2025].get(f'2025-{i:02d}', 0.0):>9.2f}"
           for i in range(1, 13)]
    print(n.ljust(46), *row)

# Row-level detail for the two flip months, per ingredient slot.
def slot_rows(name, yr, mo):
    """(added_rows, removed_rows) of an ingredient in a month."""
    if name.startswith("R2-26"):
        new = [t for t in ing["above150"][yr]
               if t["date"][:7] == mo]
        old = [t for t in books[yr]
               if t["comp"] == "INV-ABOVE" and t["date"][:7] == mo]
        return new, old
    if name.startswith("R5-03"):
        new = [t for t in ing["sleeve125"][yr]
               if t["date"][:7] == mo]
        old = [t for t in books[yr]
               if t["comp"] in ("GAP-FADE", "GAP-FADE-INC")
               and t["date"][:7] == mo]
        return new, old
    if name.startswith("R5-07"):
        return [t for t in ing["cert_r"][yr]
                if t["date"][:7] == mo], []
    return [t for t in ing["rexp"][yr] if t["date"][:7] == mo], []

detail = {}
for yr, mo in ((2025, "2025-01"), (2025, "2025-12")):
    print(f"\n== row detail {mo}")
    detail[mo] = {}
    for n in APPLIERS:
        new, old = slot_rows(n, yr, mo)
        dn = round(sum(t["net"] for t in new)
                   - sum(t["net"] for t in old), 2)
        detail[mo][n] = {
            "delta": dn,
            "new": [(t["date"], t["stock"], t.get("direction"),
                     t["net"]) for t in new],
            "removed": [(t["date"], t["stock"], t.get("direction"),
                         t["net"]) for t in old]}
        print(f"  {n}: delta {dn} (new {len(new)} rows "
              f"{round(sum(t['net'] for t in new), 2)}, removed "
              f"{len(old)} rows {round(sum(t['net'] for t in old), 2)})")
        for t in new:
            print(f"     + {t['date']} {t['stock']:12} "
                  f"{t.get('direction')} net {t['net']} "
                  f"cell {R9.LABELS.get(t['date'])}")
        for t in old:
            print(f"     - {t['date']} {t['stock']:12} "
                  f"{t.get('direction')} net {t['net']} "
                  f"cell {R9.LABELS.get(t['date'])}")

json.dump({"base_months": {str(y): base_m[y] for y in base_m},
           "deltas": {n: {str(y): deltas[n][y] for y in deltas[n]}
                      for n in deltas},
           "detail": detail},
          open(f"{WS}/r9_ws0_decomp.json", "w"), indent=1)

R9.record_audit(
    "R9-01",
    "WS0 flip decomposition of the R8-02 max stack (audit — no "
    "candidate scored)",
    "per-ingredient month deltas computed by applying each "
    "ingredient alone to the starting book; Jan-2025 and Dec-2025 "
    "sums verified against the R8-02 gate sheet (-2,915.77 / "
    "-1,307.71). Full table + row detail in r9_ws0_decomp.json "
    "and the Round-9 report.",
    extra={"jan_2025_deltas": {n: deltas[n][2025]["2025-01"]
                               for n in APPLIERS},
           "dec_2025_deltas": {n: deltas[n][2025]["2025-12"]
                               for n in APPLIERS}})
print("\nWS0 decomposition done.")
