#!/usr/bin/env python3
"""ROUND 8 — WS0: MAX-STACK GATE (R8-01 anchors audit; R8-02 gate).

R8-01: each stack ingredient applied ALONE to the starting book
must reproduce its flagged-list price on this book (no combination
scored). R8-02: R2-26 + R5-03 (clean form — GAP-FADE swapped for
the >=1.25% DOWN+FLAT sleeve AND GAP-FADE-INC retired) + R5-07-CERT
+ R7-03 gated as ONE whole-book candidate, force_no_bank —
adoption is Chandu's. Placebos frozen in the Round-8
pre-registration (P1 all-placebo, P2 swaps + sleeves late,
P3 R2-26 + sleeve late + real sleeves).
"""
import sys, pickle
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B6
import stocks_engine_r7_builders as B7
import stocks_engine_r8_lib as R8

books = R8.load_books()
JO = {yr: R8.jo(books, yr) for yr in (2025, 2026)}
assert JO == R8.JO_BASE, JO

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

# ---------------------------------------------------------- ingredients
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
POP150 = cache["inv_pop_T150S080"]
above150 = R.inv_above_rows(POP150)
above150_short = R.split_years([R.norm(
    "INV-ABOVE", r["date"], r["stock"], r["direction"], r["entry_time"],
    r["net"]) for r in R.inv_side_rows(POP150, "SHORT", below=False,
                                       flat_aside=False)])

sleeve125 = B6.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                        cells={"DOWN", "FLAT"})
sleeve125_mirror = B6.gap_rows("follow", 1.25, 1, 1.25, 0.5,
                               only_dir="SHORT",
                               cells={"DOWN", "FLAT"})
sleeve125_late = B6.gap_rows("fade", 1.25, 2, 1.25, 0.5,
                             only_dir="LONG", cells={"DOWN", "FLAT"})
ss = {yr: round(sum(t["net"] for t in sleeve125[yr]), 2)
      for yr in (2025, 2026)}
assert ss == {2025: 32064.93, 2026: 4270.42}, ss
print("gap sleeve125 anchor OK (standalone +32,064.93 / +4,270.42)")

cert_set = B7.certified_exclusions()[0]
cert, cert_flip, cert_late, viol_c, stats_c = B7.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.0, excl=cert_set)
assert viol_c == 0, viol_c
sa = {yr: round(sum(t["net"] for t in cert[yr]), 2) for yr in (2025, 2026)}
assert sa == {2025: 14105.64, 2026: 24112.86}, sa
assert (len(cert[2025]), len(cert[2026])) == (291, 370)
cert_r = {yr: [dict(t, comp="NE-REV-CERT") for t in cert[yr]]
          for yr in cert}
cert_f = {yr: [dict(t, comp="NE-REV-CERT-S") for t in cert_flip[yr]]
          for yr in cert_flip}
cert_l = {yr: [dict(t, comp="NE-REV-CERT") for t in cert_late[yr]]
          for yr in cert_late}
print("NE-REV-CERT anchor OK (standalone +14,105.64 / +24,112.86; "
      "291/370 rows)")

rexp, rexp_flip, rexp_late, viol_r = B7.rexp_rows(
    "SHORT", cells={"DOWN"})
assert viol_r == 0, viol_r
sa = {yr: round(sum(t["net"] for t in rexp[yr]), 2) for yr in (2025, 2026)}
assert sa == {2025: 14870.39, 2026: -8399.33}, sa
assert (len(rexp[2025]), len(rexp[2026])) == (41, 86)
print("R7-03 anchor OK (standalone +14,870.39 / -8,399.33; 41/86 rows)")

# ------------------------------------------------------------- R8-01 -
anchors = {}
var226 = R8.swap(books, "INV-ABOVE", above150)
anchors["R2-26"] = (R8.jo(var226, 2025), R8.jo(var226, 2026))
assert anchors["R2-26"] == (85954.04, 233818.54), anchors["R2-26"]

var503 = without(R8.swap(books, "GAP-FADE", sleeve125), "GAP-FADE-INC")
anchors["R5-03-clean"] = (R8.jo(var503, 2025), R8.jo(var503, 2026))
assert anchors["R5-03-clean"] == (86709.48, 227711.39), \
    anchors["R5-03-clean"]

varCERT = R8.add_comp(books, "NE-REV-CERT", cert_r)
anchors["R5-07-CERT"] = (R8.jo(varCERT, 2025), R8.jo(varCERT, 2026))
assert anchors["R5-07-CERT"] == (92537.28, 253809.07), \
    anchors["R5-07-CERT"]

var703 = R8.add_comp(books, "REXP", rexp)
anchors["R7-03"] = (R8.jo(var703, 2025), R8.jo(var703, 2026))
assert anchors["R7-03"] == (93290.43, 221296.88), anchors["R7-03"]

R8.record_audit(
    "R8-01",
    "WS0 ingredient anchors on the starting book (audit — no "
    "combination scored)",
    f"all four stack ingredients reproduce their flagged-list "
    f"prices on the Round-7 book exactly: R2-26 -> JO "
    f"{anchors['R2-26']}; R5-03-clean (swap + GAP-FADE-INC retired) "
    f"-> {anchors['R5-03-clean']}; R5-07-CERT -> "
    f"{anchors['R5-07-CERT']}; R7-03 -> {anchors['R7-03']}. "
    f"Construction anchors inside the ingredients also exact: gap "
    f"sleeve125 standalone +32,064.93 / +4,270.42; NE-REV-CERT "
    f"+14,105.64 / +24,112.86 (291/370 rows); REXP DOWN "
    f"+14,870.39 / -8,399.33 (41/86 rows). Timing violations "
    f"counted: NE-REV {viol_c}, REXP {viol_r}.",
    extra={"anchors_jo": {k: list(v) for k, v in anchors.items()}})

# ------------------------------------------------------------- R8-02 -
combo = without(R8.swap(var226, "GAP-FADE", sleeve125), "GAP-FADE-INC")
combo = R8.add_comp(combo, "NE-REV-CERT", cert_r)
combo = R8.add_comp(combo, "REXP", rexp)

p1 = without(R8.swap(books, "INV-ABOVE", above150_short),
             "GAP-FADE-INC")
p1 = R8.swap(p1, "GAP-FADE", sleeve125_mirror)
p1 = R8.add_comp(p1, "NE-REV-CERT-S", cert_f)
p1 = R8.add_comp(p1, "REXP", rexp_flip)

p2 = without(R8.swap(var226, "GAP-FADE", sleeve125), "GAP-FADE-INC")
p2 = R8.add_comp(p2, "NE-REV-CERT", cert_l)
p2 = R8.add_comp(p2, "REXP", rexp_late)

p3 = without(R8.swap(var226, "GAP-FADE", sleeve125_late),
             "GAP-FADE-INC")
p3 = R8.add_comp(p3, "NE-REV-CERT", cert_r)
p3 = R8.add_comp(p3, "REXP", rexp)

pl = [R8.full_total(p1), R8.full_total(p2), R8.full_total(p3)]
viol = viol_c + viol_r
out = R8.gate(books, combo, pl, timing_violations=viol)
got25, got26 = R8.jo(combo, 2025), R8.jo(combo, 2026)
exp25 = round(78420.04 + 7534.00 + 8289.44 + 14117.24 + 14870.39, 2)
exp26 = round(229696.21 + 4122.33 - 1984.82 + 24112.86 - 8399.33, 2)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R8.record(
    "R8-02",
    "DECISION SUPPORT: MAX STACK — R2-26 + R5-03 (clean) + "
    "R5-07-CERT + R7-03, gated as ONE whole-book candidate — NOT "
    "a banking", out,
    note=f"ingredients re-anchored to the paisa on this base at "
         f"R8-01 before scoring. Purely-additive expectation: 2025 "
         f"JO {exp25} / 2026 JO {exp26}; actual: {got25} / {got26} "
         f"(exactly additive: {got25 == exp25 and got26 == exp26} "
         f"— the four ingredients act on disjoint components). "
         f"2025 pace if adopted: Rs{round(got25/10, 2)}/month; gap "
         f"would fall to Rs{round(150000 - got25, 2)}. Failing "
         f"legs: {failed}; flips: {out['legs']['flip_detail']}. "
         f"Placebos: P1 all-placebo {pl[0]}; P2 swaps + sleeves "
         f"late {pl[1]}; P3 R2-26 + sleeve late + real sleeves "
         f"{pl[2]}. Timing violations {viol} (NE-REV entries 10:35 "
         f"strictly after the 10:25 signal bar; REXP entries 10:20 "
         f"strictly after the 10:10 signal bar; gap entries at bar "
         f">= 1 after the bar-0 print; all counted in code). "
         f"Adoption is Chandu's; nothing banked here regardless of "
         f"verdict.",
    extra={"expected_if_additive": {"2025_JO": exp25,
                                    "2026_JO": exp26},
           "actual": {"2025_JO": got25, "2026_JO": got26},
           "failed_legs": failed},
    force_no_bank=True)
print("WS0 done. Max stack 2025 JO:", got25, "| 2026 JO:", got26,
      "| pace 2025:", round(got25 / 10, 2), "/mo | gap:",
      round(150000 - got25, 2), "| failed legs:", failed)
