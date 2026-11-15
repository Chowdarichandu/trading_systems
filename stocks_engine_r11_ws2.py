#!/usr/bin/env python3
"""ROUND 11 — WS2: CROSS-FAMILY PAIR.

R11-03: banked book + NE-REV-NU rows (the exact Round-9/10
ingredient build; fails (e) only standalone) + REXP-DOWN rows
at the preferred T100/S065 geometry (fails (c) only
standalone) — two families, two different single-leg failures;
the pair tests whether they cure each other assembled.
Anchors asserted at build: NU standalone +12,596.19 /
+23,744.40 on 200/313 rows; REXP-DOWN T100/S065 Jan-Oct
+10,243.45 / -5,899.72 (the R8-07 record).
Placebos: book + both flipped sets; book + both late sets.
Timing: CERT violations + REXP violations, asserted 0.
R11-04 (conditional, pre-registered trigger): iff R11-03
fails AND its failed legs intersect {c_2026_no_fall,
e_extop3}, gate the single substitution — NOTCHCELL in place
of NU, same REXP rows, same composed placebos. Otherwise
R11-04 closes by statement.
"""
import sys, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r11_lib as R11
import stocks_engine_r9_ingredients as ING
import stocks_engine_r8_builders as B8

books = R11.load_books()
ing = ING.build_all()
cond = ING.build_cond()
viol_c = ing["viol_c"]
assert viol_c == 0, viol_c

nu = cond["notchup"]
nu_sa = {yr: round(sum(t["net"] for t in nu["real"][yr]), 2)
         for yr in (2025, 2026)}
assert nu_sa == {2025: 12596.19, 2026: 23744.40}, nu_sa
assert (len(nu["real"][2025]), len(nu["real"][2026])) == (200, 313)

rexp, rexp_f, rexp_l, viol_r = B8.rexp_geo(
    "SHORT", cells={"DOWN"}, tgt=1.00, stp=0.65)
assert viol_r == 0, viol_r
rx_jo = {yr: round(sum(t["net"] for t in rexp[yr]
                       if t["date"] <= f"{yr}-10-31"), 2)
         for yr in (2025, 2026)}
assert rx_jo == {2025: 10243.45, 2026: -5899.72}, rx_jo
rx_sa = {yr: round(sum(t["net"] for t in rexp[yr]), 2)
         for yr in (2025, 2026)}
print(f"anchors OK: NU {nu_sa}; REXP-DOWN T100/S065 JO {rx_jo} "
      f"(full {rx_sa}, rows {len(rexp[2025])}/{len(rexp[2026])})")

def add2(bk, rows_a, rows_b):
    out = R11.add_comp(bk, rows_a[2025][0]["comp"], rows_a)
    out = R11.add_comp(out, rows_b[2025][0]["comp"], rows_b)
    return out

# ------------------------------------------------------ R11-03 --
var = add2(books, nu["real"], rexp)
pl = [R11.full_total(add2(books, nu["flip"], rexp_f)),
      R11.full_total(add2(books, nu["late"], rexp_l))]
out = R11.gate(books, var, pl, timing_violations=viol_c + viol_r)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R11.record(
    "R11-03",
    "Cross-family pair: NE-REV-NU + REXP-DOWN (T100/S065) on "
    "the banked book", out,
    note=f"NU standalone {nu_sa[2025]} / {nu_sa[2026]} on "
         f"200/313 rows (fails (e) alone standalone, R10-02); "
         f"REXP-DOWN T100/S065 Jan-Oct {rx_jo[2025]} / "
         f"{rx_jo[2026]} on {len(rexp[2025])}/{len(rexp[2026])} "
         f"rows (fails (c) alone standalone, R8-07). Placebos: "
         f"flipped pair book {pl[0]}; late pair book {pl[1]}. "
         f"Timing violations {viol_c + viol_r}. Failed legs: "
         f"{failed}.",
    extra={"nu_standalone": {str(k): v for k, v in nu_sa.items()},
           "rexp_jo": {str(k): v for k, v in rx_jo.items()},
           "rexp_full": {str(k): v for k, v in rx_sa.items()},
           "failed_legs": failed})

# ------------------------------------------------------ R11-04 --
TRIGGER_LEGS = {"c_2026_no_fall", "e_extop3"}
if out["verdict"] or not (set(failed) & TRIGGER_LEGS):
    R11.record_audit(
        "R11-04",
        "NOTCHCELL substitution — closes by statement",
        f"Pre-registered trigger not met: R11-03 "
        f"{'BANKED' if out['verdict'] else 'failed legs ' + str(failed)}"
        f" — the substitution runs only when the pair fails "
        f"with (c) or (e) among the failed legs. No second "
        f"candidate is designed or scored.")
    print("WS2 done (no substitution).")
    sys.exit(0)

# NOTCHCELL rows: the R10-04 construction VERBATIM
# (stocks_engine_r10_ws2.py) — CERT rows admitted iff NOTCH
# passes (ING._state_ok_notch) AND the day's frozen regime
# cell is DOWN or FLAT; state-unknown dates never admitted.
# Anchor: standalone +6,566.49 / +27,213.39 on 181/293 rows.
LABELS = R11.LABELS

def _ok_notchcell(day):
    if LABELS.get(day) not in ("DOWN", "FLAT"):
        return False
    return ING._state_ok_notch(day)     # True / False / None

def _ncell_filt(rows):
    kept = {2025: [], 2026: []}
    for yr in (2025, 2026):
        for t in rows[yr]:
            if _ok_notchcell(t["date"]) is True:
                kept[yr].append(dict(t, comp="NE-REV-NOTCHCELL"))
    return kept

ncell = {"real": _ncell_filt(ing["cert"]),
         "flip": _ncell_filt(ing["cert_f"]),
         "late": _ncell_filt(ing["cert_l"])}
ncell_sa = {yr: round(sum(t["net"] for t in ncell["real"][yr]), 2)
            for yr in (2025, 2026)}
assert ncell_sa == {2025: 6566.49, 2026: 27213.39}, ncell_sa
assert (len(ncell["real"][2025]), len(ncell["real"][2026])) == \
    (181, 293)
print(f"NOTCHCELL anchor OK: {ncell_sa} on 181/293 rows")

var4 = add2(books, ncell["real"], rexp)
pl4 = [R11.full_total(add2(books, ncell["flip"], rexp_f)),
       R11.full_total(add2(books, ncell["late"], rexp_l))]
out4 = R11.gate(books, var4, pl4,
                timing_violations=viol_c + viol_r)
failed4 = [k for k, v in out4["legs"].items()
           if isinstance(v, bool) and not v]
R11.record(
    "R11-04",
    "Substitution: NE-REV-NOTCHCELL + REXP-DOWN (T100/S065) "
    "on the banked book", out4,
    note=f"trigger fired (R11-03 failed legs {failed} "
         f"intersect {{c, e}}). NOTCHCELL standalone "
         f"{ncell_sa[2025]} / {ncell_sa[2026]} on 181/293 "
         f"rows (fails (e) alone standalone, R10-04); same "
         f"REXP-DOWN rows as R11-03. Placebos: flipped book "
         f"{pl4[0]}; late book {pl4[1]}. Timing violations "
         f"{viol_c + viol_r}. Failed legs: {failed4}.",
    extra={"notchcell_standalone": {str(k): v
                                    for k, v in ncell_sa.items()},
           "failed_legs": failed4})
print("WS2 done.")
