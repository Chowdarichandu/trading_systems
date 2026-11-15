#!/usr/bin/env python3
"""ROUND 14 — WS4: P2F family geometry neighbour (R14-07):
P2F + P2F-R2, T125/S050 -> T150/S050 (target step only, one
family swap; the incumbent stop is kept so the family's
two-axis history — Lesson 33 — is decomposed: the 2025 bleed
is attributed to the target or the stop by this one cell).

Anchor first: entry-bar re-scoring at the book cell
reproduces each comp's banked rows exactly — the replay
flavour is identified per comp by the anchor, not assumed.
Placebos: flipped / one-bar-late sets at the candidate
geometry for both comps (R13 swap convention).
"""
import sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r14_lib as R14
import stocks_engine_r14_builders as B14

books = R14.load_books()
COMPS = ("P2F", "P2F-R2")

def keyset(rows):
    return Counter(R14.row_id(t) for t in rows)

# ------------------------------------------------------- anchors --
flavours, cand = {}, {}
for comp in COMPS:
    bk = B14.comp_rows(books, comp)
    for fl in ("plain", "v2"):
        real, _f, _l, miss = B14.rescore(bk, comp, 1.25, 0.50,
                                         fl, open_entry=True)
        if miss == 0 and all(keyset(real[yr]) == keyset(bk[yr])
                             for yr in (2025, 2026)):
            flavours[comp] = fl
            break
    assert comp in flavours, f"no flavour reproduces {comp}"
    cand[comp] = B14.rescore(bk, comp, 1.50, 0.50,
                             flavours[comp], open_entry=True)
    assert cand[comp][3] == 0, (comp, cand[comp][3])
    print(f"anchor OK: {comp} book rows are "
          f"'{flavours[comp]}'-replay rows (re-score at "
          f"T125/S050 exact, 0 missing)")

# ------------------------------------------------------ R14-07 --
def swap2(bk, kind_idx):
    out = bk
    for comp in COMPS:
        out = R14.swap(out, comp, cand[comp][kind_idx])
    return out

var = swap2(books, 0)
pl = [R14.full_total(swap2(books, 1)),
      R14.full_total(swap2(books, 2))]
out = R14.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
sa, base_sa = {}, {}
for comp in COMPS:
    sa[comp] = {yr: round(sum(t["net"]
                              for t in cand[comp][0][yr]), 2)
                for yr in (2025, 2026)}
    base_sa[comp] = {yr: round(sum(t["net"] for t in
                                   B14.comp_rows(books,
                                                 comp)[yr]), 2)
                     for yr in (2025, 2026)}
R14.record(
    "R14-07",
    "P2F family geometry swap T125/S050 -> T150/S050 (target "
    "step only, P2F + P2F-R2)", out,
    note=f"Sleeve standalone: P2F {sa['P2F'][2025]} / "
         f"{sa['P2F'][2026]} (banked cell "
         f"{base_sa['P2F'][2025]} / {base_sa['P2F'][2026]}); "
         f"P2F-R2 {sa['P2F-R2'][2025]} / "
         f"{sa['P2F-R2'][2026]} (banked cell "
         f"{base_sa['P2F-R2'][2025]} / "
         f"{base_sa['P2F-R2'][2026]}). Stated reason (frozen "
         f"in the pre-registration): both prior family tests "
         f"moved target and stop together (T150/S080), so the "
         f"2025 bleed was unattributable; this cell isolates "
         f"the target at the incumbent stop. One P2F-R2 row "
         f"(WIPRO 2025-10-21, the Muhurat special session) "
         f"carries the nominal 09:15 label on a day whose "
         f"first bar is 13:45; it is scored from the "
         f"session's opening bar — the convention its own "
         f"lineage used, and the anchor reproduces its "
         f"banked net (-59.0) exactly. Placebos: flipped "
         f"swap book {pl[0]}; one-bar-late swap book "
         f"{pl[1]}. Timing violations 0 — entries are the "
         f"banked ones; exits only. Failed legs: {failed}.",
    extra={"sleeve_standalone": sa, "failed_legs": failed})
print("WS4 done.")
