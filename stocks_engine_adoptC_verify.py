#!/usr/bin/env python3
"""ADOPTION VERIFICATION — Variant C (NE-REV-NOTCH+UPGUARD stack,
R9-04 form), owner direction 2026-11-02 16:48 IST ("You apply
the fix and run again").

Three computations, all behind the frozen nine-leg gate + leg
(x) in the same run (stocks_engine_r3_lib.gate):

A. CONSTRUCTION IDENTITY — rebuild Variant C on its birth
   baseline (the Round-8/9 book inside the ingredients module)
   with the exact R9-WS1 recipe and gate it: the sheet must
   reproduce r9_results.json R9-04 EXACTLY (legs, sums,
   scorecards, placebo totals P1/P2/P3).

B. ADOPTED BOOK — rebuild Variant C from the CURRENT ending
   book (Round-16 CSVs) by the generalised construction the
   engine used for every restatement since R12 (strip the
   book's NE-REV*/REXP rows — alternative forms of the same
   sleeves — then R2-26 swap, R5-03-clean swap with
   GAP-FADE-INC retired, NE-REV-NU slot, R7-03 REXP add).
   Expected Jan-Oct: 2025 Rs1,19,813.44 / 2026 Rs2,47,178.79.
   The adopted book must equal the R9-04 book row-for-row.

C. ADOPTION GATE — the adopted book gated against the
   pre-adoption (Round-16) book with the R9-shaped placebos
   rebuilt on that baseline. Reported verbatim, whatever it
   says.

Plus: alternative stack forms rebuilt on the R16 book (totals
asserted against the recorded prices) for the restated
decision list, and sleeve-identity checks for the flagged
geometry swaps whose deltas are sleeve-local.

Basis: equity cash, home 25, provisional per 100 shares,
Rs40/trade, paper only, real Rs0. Timing violations = the
ingredients' own counted violations (NE-REV 0 + REXP 0,
asserted at build); the state conditions read the 10:25
NIFTY bar (completes 10:30), strictly before every 10:35
NE-REV entry, and add none.
"""
import sys, csv, json
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_floor_lib as FL
import stocks_engine_r3_lib as R3
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
cond = ING.build_cond()
viol = ing["viol_c"] + ing["viol_r"]
assert viol == 0, viol
NU = cond["notchup"]

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

def full(bk, yr):
    return round(sum(t["net"] for t in bk[yr]), 2)

def full_total(bk):
    return round(full(bk, 2025) + full(bk, 2026), 2)

def strip_families(bk):
    return {yr: [t for t in bk[yr]
                 if not t["comp"].startswith("NE-REV")
                 and t["comp"] != "REXP"]
            for yr in (2025, 2026)}

def build(base, slot_rows, strip=False, fade_late=False,
          slot_rows_override=None):
    """The frozen stack construction (R9-WS1 recipe; strip is
    the identity adaptation for baselines that already carry
    NE-REV/REXP rows in other forms)."""
    b = strip_families(base) if strip else base
    out = ING.apply_r226(b, ing)
    if fade_late:
        out = ING.without(
            R3.swap(out, "GAP-FADE", ing["sleeve125_late"]),
            "GAP-FADE-INC")
    else:
        out = ING.apply_r503(out, ing)
    rows = slot_rows if slot_rows_override is None else \
        slot_rows_override
    out = R3.add_comp(out, rows[2025][0]["comp"], rows)
    out = R3.add_comp(out, "REXP", ing["rexp"])
    return out

def build_p1(base, flip_rows, strip=False):
    b = strip_families(base) if strip else base
    p = ING.without(b, "GAP-FADE-INC")
    p = R3.swap(p, "INV-ABOVE", ing["above150_short"])
    p = R3.swap(p, "GAP-FADE", ing["sleeve125_mirror"])
    p = R3.add_comp(p, flip_rows[2025][0]["comp"], flip_rows)
    p = R3.add_comp(p, "REXP", ing["rexp_flip"])
    return p

def multiset(bk, yr):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2))
                   for t in bk[yr])

out = {}

# ---------------- baseline: Round-16 ending book -------------
r16 = {yr: FL.load(f"stocks_engine_r16_book{yr}_trades.csv")
       for yr in (2025, 2026)}
assert {yr: jo(r16, yr) for yr in (2025, 2026)} == \
    {2025: 105987.24, 2026: 257300.30}
assert (len(r16[2025]), len(r16[2026])) == (1101, 1352)
print("R16 baseline verified: JO 105987.24 / 257300.30, "
      "rows 1101 / 1352")
out["baseline_r16"] = {
    "jan_oct": {str(yr): jo(r16, yr) for yr in (2025, 2026)},
    "full": {str(yr): full(r16, yr) for yr in (2025, 2026)},
    "rows": {str(yr): len(r16[yr]) for yr in (2025, 2026)}}
print("R16 comps 2025:", Counter(t["comp"] for t in r16[2025]))
print("R16 comps 2026:", Counter(t["comp"] for t in r16[2026]))

# ------------- A. construction identity vs R9-04 -------------
books9 = ing["books"]
assert not any(t["comp"].startswith("NE-REV") or
               t["comp"] == "REXP"
               for yr in (2025, 2026) for t in books9[yr]), \
    "birth baseline unexpectedly carries NE-REV/REXP rows"
varA = build(books9, NU["real"])
pA = [full_total(build_p1(books9, NU["flip"])),
      full_total(build(books9, NU["late"])),
      full_total(build(books9, NU["real"], fade_late=True))]
gateA = R3.gate(books9, varA, pA, timing_violations=viol)
rec9 = {r["cycle"]: r for r in json.load(
    open(f"{WS}/r9_results.json"))}["R9-04"]
assert gateA["legs"] == rec9["legs"], (gateA["legs"],
                                       rec9["legs"])
assert gateA["sums"] == rec9["sums"], gateA["sums"]
assert gateA["var"] == rec9["var"], gateA["var"]
assert gateA["base"] == rec9["base"], gateA["base"]
assert pA == [174662.47, 344925.15, 322968.45], pA
print("A. R9-04 reproduction EXACT: legs all ten pass, sums "
      f"{gateA['sums']}, placebos {pA}")
out["checkA_r9_reproduction"] = {
    "legs": gateA["legs"], "sums": gateA["sums"],
    "placebos": pA, "var": gateA["var"]}

# ------------- B. adopted book from the R16 book -------------
adopted = build(r16, NU["real"], strip=True)
exp_jo = {2025: 119813.44, 2026: 247178.79}
got_jo = {yr: jo(adopted, yr) for yr in (2025, 2026)}
print(f"B. adopted JO from R16 build: {got_jo} "
      f"(expected {exp_jo})")
assert got_jo == exp_jo, (got_jo, exp_jo)
for yr in (2025, 2026):
    assert multiset(adopted, yr) == multiset(varA, yr), \
        (yr, "adopted book != R9-04 book row-for-row")
print("B. adopted book == R9-04 book ROW-FOR-ROW both years; "
      f"full totals {{2025: {full(adopted, 2025)}, "
      f"2026: {full(adopted, 2026)}}}, rows "
      f"{len(adopted[2025])} / {len(adopted[2026])}")
out["adopted"] = {
    "jan_oct": {str(yr): got_jo[yr] for yr in (2025, 2026)},
    "full": {str(yr): full(adopted, yr) for yr in (2025, 2026)},
    "rows": {str(yr): len(adopted[yr]) for yr in (2025, 2026)},
    "row_for_row_vs_r9_04": True}

# ------------- C. adoption gate vs the R16 book --------------
pB = [full_total(build_p1(r16, NU["flip"], strip=True)),
      full_total(build(r16, NU["late"], strip=True)),
      full_total(build(r16, NU["real"], strip=True,
                       fade_late=True))]
gateC = R3.gate(r16, adopted, pB, timing_violations=viol)
failedC = [k for k, v in gateC["legs"].items()
           if isinstance(v, bool) and not v]
print(f"C. gate vs R16 book: verdict {gateC['verdict']}; "
      f"failed legs {failedC}; flips "
      f"{gateC['legs']['flip_detail']}; placebos {pB}; sums "
      f"{gateC['sums']}")
out["checkC_gate_vs_r16"] = {
    "verdict": gateC["verdict"], "legs": gateC["legs"],
    "sums": gateC["sums"], "placebos": pB,
    "base": gateC["base"], "var": gateC["var"],
    "base_cells": gateC["base_cells"],
    "var_cells": gateC["var_cells"],
    "failed_legs": failedC}

# ------------- alternative stack forms on the R16 book -------
alts = {}
for name, rows, want in (
        ("unconditioned_R8-02", ing["cert_r"],
         {2025: 123231.11, 2026: 247547.25}),
        ("A_NOTCH_R9-02", cond["notch"]["real"],
         {2025: 127134.02, 2026: 244461.23}),
        ("IDXCELL_R9-08", cond["idxcell"]["real"],
         {2025: 113146.38, 2026: 257803.88})):
    bk = build(r16, rows, strip=True)
    j = {yr: jo(bk, yr) for yr in (2025, 2026)}
    assert j == want, (name, j, want)
    alts[name] = {
        "jan_oct": {str(yr): j[yr] for yr in (2025, 2026)},
        "delta_vs_adopted": {
            str(yr): round(j[yr] - got_jo[yr], 2)
            for yr in (2025, 2026)}}
    print(f"alt {name}: JO {j} == recorded {want}; delta vs "
          f"adopted {alts[name]['delta_vs_adopted']}")
out["alternative_stacks"] = alts

# ------------- sleeve-identity checks (carried flags) --------
def comp_multiset(bk, yr, comp):
    return Counter((t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2))
                   for t in bk[yr] if t["comp"] == comp)

ident = {}
for comp in ("F4", "INV-LONG", "N4-V3", "P2F", "P2F-R2",
             "R2-LOWBAND", "INV-R3"):
    ident[comp] = all(comp_multiset(adopted, yr, comp) ==
                      comp_multiset(r16, yr, comp)
                      for yr in (2025, 2026))
nu_same = all(comp_multiset(adopted, yr, "NE-REV-NU") ==
              comp_multiset(r16, yr, "NE-REV-NU")
              for yr in (2025, 2026))
ident["NE-REV-NU_vs_r16_pair_rows"] = nu_same
print(f"sleeve identity adopted vs R16: {ident}")
out["sleeve_identity"] = ident

# ------------- export the adopted book + re-sum -------------
FIELDS = ["comp", "date", "stock", "dir", "entry_time", "net"]
for yr in (2025, 2026):
    path = f"{WS}/stocks_engine_adoptedC_book{yr}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for t in adopted[yr]:
            w.writerow({k: t[k] for k in FIELDS})
    rows = list(csv.DictReader(open(path)))
    j = round(sum(float(r["net"]) for r in rows
                  if r["date"] <= f"{yr}-10-31"), 2)
    fu = round(sum(float(r["net"]) for r in rows), 2)
    assert j == exp_jo[yr] and len(rows) == len(adopted[yr])
    print(f"exported adopted {yr}: {len(rows)} rows, JO {j}, "
          f"full {fu} — independent re-sum OK")

# ------------- scorecards for the report ---------------------
sc = {yr: FL.scorecard(adopted[yr], yr) for yr in (2025, 2026)}
scb = {yr: FL.scorecard(r16[yr], yr) for yr in (2025, 2026)}
out["adopted_scorecard"] = {
    str(yr): {"months": sc[yr]["months"],
              "jan_oct": sc[yr]["jan_oct_total"],
              "jan_oct_trades": sc[yr]["jan_oct_trades"],
              "h1": sc[yr]["jan_oct_H1_jan_may"],
              "h2": sc[yr]["jan_oct_H2_jun_oct"],
              "ex_top3_full": sc[yr]["ex_top3_stocks"],
              "top3": sc[yr]["top3_stocks"],
              "by_comp": sc[yr]["by_comp"]}
    for yr in (2025, 2026)}
out["baseline_scorecard"] = {
    str(yr): {"months": scb[yr]["months"],
              "jan_oct": scb[yr]["jan_oct_total"],
              "ex_top3_full": scb[yr]["ex_top3_stocks"]}
    for yr in (2025, 2026)}
cen = {}
for yr in (2025, 2026):
    c = Counter(t["comp"] for t in adopted[yr])
    cen[str(yr)] = {k: [v, round(sum(t["net"] for t in
                       adopted[yr] if t["comp"] == k), 2)]
                    for k, v in sorted(c.items())}
out["adopted_comp_census"] = cen
print("adopted 2025 months:", sc[2025]["months"])
print("adopted 2026 months:", sc[2026]["months"])
print("adopted census:", cen)

json.dump(out, open(f"{WS}/stocks_adoption_variantC_results"
                    ".json", "w"), indent=1)
print("evidence -> stocks_adoption_variantC_results.json")
print("ADOPTION VERIFICATION COMPLETE")
