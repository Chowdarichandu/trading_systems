#!/usr/bin/env python3
"""ROUND 11 — WS3: LEG-(e) ANATOMY OF NE-REV-NU STANDALONE.

R11-05 (audit): recompute the R10-02 construction (banked
book + NU rows) and decompose its leg-(e) failure exactly,
per year, under the gate's own definition (full-year totals;
each book judged against its OWN top-3 stock set):
  Dex-top-3 = NU profit in names outside the variant top-3
            + base profit in names LEAVING the top-3
            - base profit in names ENTERING the top-3.
Per-stock NU table and the largest NU trades inside the
variant's top-3 names go to r11_nu_anatomy.json.
Separator test (frozen): state slices of the NU population
only — (a) regime cell of the trade day (DOWN/FLAT/UP);
(b) the 10:25 index-state bucket (hard / shallow / up;
shallow must be empty — NOTCH inadmissible — verified, not
searched). A slice qualifies iff (i) combined NU net < 0,
(ii) NU net < 0 in EACH year, (iii) |combined| >= 50% of
the R11-05 combined ex-top-3 shortfall.
R11-06 (conditional): iff exactly one slice qualifies, gate
NU-minus-slice standalone (placebos: flipped / late NU rows
minus the same slice — date-level state filters all three
row sets identically). Otherwise closes by statement.
"""
import sys, json
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r11_lib as R11
import stocks_engine_r9_ingredients as ING
import stocks_engine_r8_builders as B8
import stocks_engine_floor_lib as FL

books = R11.load_books()
ing = ING.build_all()
cond = ING.build_cond()
viol = ing["viol_c"]
assert viol == 0, viol
nu = cond["notchup"]
LABELS = R11.LABELS

var = R11.add_comp(books, "NE-REV-NU", nu["real"])

def by_stock(rows):
    d = defaultdict(float)
    for t in rows:
        d[t["stock"]] += t["net"]
    return {k: round(v, 2) for k, v in d.items()}

anat = {}
shortfall = 0.0
for yr in (2025, 2026):
    sb = FL.scorecard(books[yr], yr)
    sv = FL.scorecard(var[yr], yr)
    bs_b, bs_v = by_stock(books[yr]), by_stock(var[yr])
    t_b = {s for s, _ in sb["top3_stocks"]}
    t_v = {s for s, _ in sv["top3_stocks"]}
    nu_out = round(sum(t["net"] for t in nu["real"][yr]
                       if t["stock"] not in t_v), 2)
    nu_in = round(sum(t["net"] for t in nu["real"][yr]
                      if t["stock"] in t_v), 2)
    leaving = round(sum(bs_b[s] for s in t_b - t_v), 2)
    entering = round(sum(bs_b[s] for s in t_v - t_b), 2)
    delta = round(sv["ex_top3_stocks"] - sb["ex_top3_stocks"], 2)
    assert delta == round(nu_out + leaving - entering, 2), \
        (yr, delta, nu_out, leaving, entering)
    shortfall += -delta if delta < 0 else 0.0
    nu_by_stock = by_stock(nu["real"][yr])
    big_in = sorted((t for t in nu["real"][yr]
                     if t["stock"] in t_v),
                    key=lambda t: -t["net"])[:5]
    anat[yr] = {
        "base_ex_top3": sb["ex_top3_stocks"],
        "var_ex_top3": sv["ex_top3_stocks"],
        "delta": delta,
        "base_top3": sb["top3_stocks"],
        "var_top3": sv["top3_stocks"],
        "nu_profit_outside_var_top3": nu_out,
        "nu_profit_inside_var_top3": nu_in,
        "base_profit_leaving_top3": leaving,
        "base_profit_entering_top3": entering,
        "nu_by_stock": dict(sorted(nu_by_stock.items(),
                                   key=lambda kv: -kv[1])),
        "largest_nu_trades_in_var_top3": [
            {k: t[k] for k in ("date", "stock", "dir",
                               "entry_time", "net")}
            for t in big_in],
    }
    print(f"{yr}: ex3 {sb['ex_top3_stocks']} -> "
          f"{sv['ex_top3_stocks']} (delta {delta}) = NU-out "
          f"{nu_out} + leaving {leaving} - entering {entering}; "
          f"NU inside top-3 {nu_in}; top3 {sorted(t_b)} -> "
          f"{sorted(t_v)}")
base_ex3 = round(sum(anat[yr]["base_ex_top3"] for yr in anat), 2)
var_ex3 = round(sum(anat[yr]["var_ex_top3"] for yr in anat), 2)
shortfall = round(base_ex3 - var_ex3, 2)
assert shortfall > 0
print(f"combined ex-top-3 {base_ex3} -> {var_ex3}; "
      f"shortfall {shortfall}")

# ------------------------------------------- separator test --
def bucket1025(day):
    mv = B8.nifty_move(day, "10:25")
    if mv is None:
        return "unknown"
    if mv <= -0.30:
        return "hard"
    if mv < 0:
        return "shallow"
    return "up"

slices = {}
for fam, keyfn in (("cell", lambda t: LABELS.get(t["date"])),
                   ("bucket1025", lambda t: bucket1025(t["date"]))):
    vals = defaultdict(lambda: {2025: 0.0, 2026: 0.0,
                                "n25": 0, "n26": 0})
    for yr in (2025, 2026):
        for t in nu["real"][yr]:
            k = keyfn(t)
            vals[k][yr] = round(vals[k][yr] + t["net"], 2)
            vals[k]["n25" if yr == 2025 else "n26"] += 1
    for k, v in vals.items():
        slices[f"{fam}:{k}"] = v
# NOTCH inadmissibility of the shallow bucket — verified
assert slices.get("bucket1025:shallow", {}).get("n25", 0) == 0
assert slices.get("bucket1025:shallow", {}).get("n26", 0) == 0
thr = round(0.5 * shortfall, 2)
qual = []
for name, v in slices.items():
    comb = round(v[2025] + v[2026], 2)
    ok = comb < 0 and v[2025] < 0 and v[2026] < 0 \
        and abs(comb) >= thr
    print(f"slice {name}: 2025 {v[2025]} / 2026 {v[2026]} / "
          f"combined {comb} — qualifies {ok}")
    if ok:
        qual.append(name)
json.dump({"anatomy": {str(k): v for k, v in anat.items()},
           "base_ex_top3_combined": base_ex3,
           "var_ex_top3_combined": var_ex3,
           "shortfall": shortfall,
           "separator_threshold": thr,
           "slices": slices, "qualifying": qual},
          open(f"{WS}/r11_nu_anatomy.json", "w"), indent=1)

top_d = "; ".join(
    f"{yr}: NU profit inside the variant top-3 "
    f"{anat[yr]['nu_profit_inside_var_top3']} of "
    f"{round(sum(t['net'] for t in nu['real'][yr]), 2)} "
    f"standalone; delta {anat[yr]['delta']} = outside "
    f"{anat[yr]['nu_profit_outside_var_top3']} + leaving "
    f"{anat[yr]['base_profit_leaving_top3']} - entering "
    f"{anat[yr]['base_profit_entering_top3']}"
    for yr in (2025, 2026))
R11.record_audit(
    "R11-05",
    "Leg-(e) anatomy of NE-REV-NU standalone (audit — no "
    "candidate scored)",
    f"Combined ex-top-3 {base_ex3} -> {var_ex3}: shortfall "
    f"{shortfall}. Decomposition (exact, asserted in code): "
    f"{top_d}. The failure is a 2026 phenomenon — NU's 2026 "
    f"profit lands inside the variant's own top-3 names, "
    f"where leg (e) cannot see it, while 2025 ex-top-3 "
    f"actually rises. Separator test over the frozen state "
    f"slices (regime cell x 10:25 bucket; shallow bucket "
    f"verified empty in NU): threshold |combined| >= {thr}; "
    f"qualifying slices = {qual}. Full tables in "
    f"r11_nu_anatomy.json.",
    extra={"shortfall": shortfall, "threshold": thr,
           "qualifying_slices": qual,
           "slices": slices})

# ------------------------------------------------------ R11-06 --
if len(qual) != 1:
    R11.record_audit(
        "R11-06",
        "Conditioned NE-REV-NU variant — closes by statement",
        f"Separator test produced {len(qual)} qualifying "
        f"slices ({qual}); the frozen rule requires exactly "
        f"one. No candidate is designed or scored — WS3 "
        f"closes with the anatomy as its result.")
    print("WS3 done (no candidate).")
    sys.exit(0)

SL = qual[0]
fam, val = SL.split(":", 1)
keyfn = (lambda t: LABELS.get(t["date"])) if fam == "cell" \
    else (lambda t: bucket1025(t["date"]))

def minus_slice(rows):
    return {yr: [t for t in rows[yr] if keyfn(t) != val]
            for yr in (2025, 2026)}

var6 = R11.add_comp(books, "NE-REV-NU", minus_slice(nu["real"]))
pl6 = [R11.full_total(R11.add_comp(books, "NE-REV-NU",
                                   minus_slice(nu["flip"]))),
       R11.full_total(R11.add_comp(books, "NE-REV-NU",
                                   minus_slice(nu["late"])))]
out6 = R11.gate(books, var6, pl6, timing_violations=viol)
failed6 = [k for k, v in out6["legs"].items()
           if isinstance(v, bool) and not v]
R11.record(
    "R11-06",
    f"NE-REV-NU minus the {SL} slice (the unique separator "
    f"qualifier), standalone", out6,
    note=f"slice {SL} is the unique qualifier under the "
         f"frozen test: combined {round(slices[SL][2025] + slices[SL][2026], 2)} "
         f"(2025 {slices[SL][2025]} / 2026 {slices[SL][2026]}), "
         f"|combined| >= {thr} = 50% of the R11-05 shortfall "
         f"{shortfall}. Placebos: flipped-minus-slice book "
         f"{pl6[0]}; late-minus-slice book {pl6[1]}. Timing "
         f"violations {viol}. Failed legs: {failed6}.",
    extra={"slice": SL, "failed_legs": failed6})
print("WS3 done.")
