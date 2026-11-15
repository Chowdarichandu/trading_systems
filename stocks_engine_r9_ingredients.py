#!/usr/bin/env python3
"""ROUND 9 — shared stack-ingredient builds, verbatim from the
Round-8 constructions (stocks_engine_r8_ws0.py / _ws2.py), each
re-anchored to the paisa on the Round-8 book before use:

- R2-26:      INV-ABOVE swap to the cached T150/S080 population.
- R5-03-clean: GAP-FADE swap to the >=1.25% DOWN+FLAT fade-LONG
  sleeve (09:20 entry) AND GAP-FADE-INC retired.
- R5-07-CERT: morning NE-REV LONG rows on the certified population
  (comp NE-REV-CERT), standalone +14,105.64 / +24,112.86, 291/370.
- R7-03:      REXP-SHORT rows restricted to DOWN cells, standalone
  +14,870.39 / -8,399.33, 41/86.
- R8-05 IDX:  NE-REV-CERT rows admitted only when NIFTY's 10:25-bar
  close <= -0.30% vs prior close (kept 201/252 of 291/370 rows).

Every build returns its counted timing violations (asserted 0 by
the callers). Basis: equity cash, home 25, provisional per
100 shares, Rs40/trade, paper only, real Rs0.
"""
import sys, pickle
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B6
import stocks_engine_r7_builders as B7
import stocks_engine_r8_builders as B8
import stocks_engine_r9_lib as R9

_cache = {}

def build_all():
    if _cache:
        return _cache
    books = R9.load_books()

    cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
    POP150 = cache["inv_pop_T150S080"]
    above150 = R.inv_above_rows(POP150)
    above150_short = R.split_years([R.norm(
        "INV-ABOVE", r["date"], r["stock"], r["direction"],
        r["entry_time"], r["net"]) for r in R.inv_side_rows(
            POP150, "SHORT", below=False, flat_aside=False)])

    sleeve125 = B6.gap_rows("fade", 1.25, 1, 1.25, 0.5,
                            only_dir="LONG", cells={"DOWN", "FLAT"})
    sleeve125_mirror = B6.gap_rows("follow", 1.25, 1, 1.25, 0.5,
                                   only_dir="SHORT",
                                   cells={"DOWN", "FLAT"})
    sleeve125_late = B6.gap_rows("fade", 1.25, 2, 1.25, 0.5,
                                 only_dir="LONG",
                                 cells={"DOWN", "FLAT"})
    ss = {yr: round(sum(t["net"] for t in sleeve125[yr]), 2)
          for yr in (2025, 2026)}
    assert ss == {2025: 32064.93, 2026: 4270.42}, ss

    cert_set = B7.certified_exclusions()[0]
    cert, cert_flip, cert_late, viol_c, _ = B7.nerev_gen(
        signal_time="10:25", entry_time="10:35", thr=2.0,
        excl=cert_set)
    assert viol_c == 0, viol_c
    sa = {yr: round(sum(t["net"] for t in cert[yr]), 2)
          for yr in (2025, 2026)}
    assert sa == {2025: 14105.64, 2026: 24112.86}, sa
    assert (len(cert[2025]), len(cert[2026])) == (291, 370)
    cert_r = {yr: [dict(t, comp="NE-REV-CERT") for t in cert[yr]]
              for yr in cert}
    cert_f = {yr: [dict(t, comp="NE-REV-CERT-S") for t in cert_flip[yr]]
              for yr in cert_flip}
    cert_l = {yr: [dict(t, comp="NE-REV-CERT") for t in cert_late[yr]]
              for yr in cert_late}

    rexp, rexp_flip, rexp_late, viol_r = B7.rexp_rows(
        "SHORT", cells={"DOWN"})
    assert viol_r == 0, viol_r
    sa = {yr: round(sum(t["net"] for t in rexp[yr]), 2)
          for yr in (2025, 2026)}
    assert sa == {2025: 14870.39, 2026: -8399.33}, sa
    assert (len(rexp[2025]), len(rexp[2026])) == (41, 86)

    # R8-05 IDX form: day filter on the certified NE-REV rows.
    def idx_filter(rows):
        kept = {2025: [], 2026: []}
        ds = du = 0
        for yr in (2025, 2026):
            for t in rows[yr]:
                mv = B8.nifty_move(t["date"], "10:25")
                if mv is None:
                    du += 1
                elif mv <= -0.30:
                    kept[yr].append(t)
                else:
                    ds += 1
        return kept, ds, du
    idx_r, ds, du = idx_filter(cert)
    idx_f, _, _ = idx_filter(cert_flip)
    idx_l, _, _ = idx_filter(cert_late)
    assert (len(idx_r[2025]), len(idx_r[2026])) == (201, 252), \
        (len(idx_r[2025]), len(idx_r[2026]))
    sa_i = {yr: round(sum(t["net"] for t in idx_r[yr]), 2)
            for yr in (2025, 2026)}
    assert sa_i == {2025: 10055.20, 2026: 31651.93}, sa_i
    idx_rr = {yr: [dict(t, comp="NE-REV-IDX") for t in idx_r[yr]]
              for yr in idx_r}
    idx_ff = {yr: [dict(t, comp="NE-REV-IDX") for t in idx_f[yr]]
              for yr in idx_f}
    idx_ll = {yr: [dict(t, comp="NE-REV-IDX") for t in idx_l[yr]]
              for yr in idx_l}

    _cache.update({
        "books": books, "above150": above150,
        "above150_short": above150_short,
        "sleeve125": sleeve125, "sleeve125_mirror": sleeve125_mirror,
        "sleeve125_late": sleeve125_late,
        "cert": cert, "cert_r": cert_r, "cert_f": cert_f,
        "cert_l": cert_l, "viol_c": viol_c,
        "rexp": rexp, "rexp_flip": rexp_flip, "rexp_late": rexp_late,
        "viol_r": viol_r,
        "idx_r": idx_rr, "idx_f": idx_ff, "idx_l": idx_ll,
        "idx_dropped_state": ds, "idx_dropped_unknown": du,
    })
    print("ingredients anchored: R2-26 / sleeve125 (+32,064.93 / "
          "+4,270.42) / CERT (+14,105.64 / +24,112.86) / REXP-DOWN "
          "(+14,870.39 / -8,399.33) / IDX (+10,055.20 / +31,651.93)")
    return _cache

def _state_ok_notch(day):
    mv = B8.nifty_move(day, "10:25")
    if mv is None:
        return None            # unknown — never guessed
    return not (-0.30 < mv < 0)

def _state_ok_upguard(day):
    if R9.LABELS.get(day) != "UP":
        return True            # condition applies to UP days only
    mv = B8.nifty_move(day, "10:25")
    if mv is None:
        return None
    return mv >= 0

def _filt(rows, okfn):
    kept = {2025: [], 2026: []}
    unknown = 0
    for yr in (2025, 2026):
        for t in rows[yr]:
            ok = okfn(t["date"])
            if ok is None:
                unknown += 1
            elif ok:
                kept[yr].append(t)
    return kept, unknown

def build_cond():
    """Conditioned NE-REV forms frozen in the Round-9
    pre-registration, built by filtering the anchored CERT / IDX
    rows on date-level state (the state depends only on the trade
    date, so real / flipped / late rows filter identically)."""
    if "cond" in _cache:
        return _cache["cond"]
    ing = build_all()
    forms = {}
    defs = {
        "notch": (_state_ok_notch, "NE-REV-NOTCH"),
        "upguard": (_state_ok_upguard, "NE-REV-UPGUARD"),
        "notchup": (lambda d: (_state_ok_notch(d) is True)
                    and (_state_ok_upguard(d) is True),
                    "NE-REV-NU"),
    }
    for name, (okfn, comp) in defs.items():
        out = {}
        for src, key in ((ing["cert"], "real"),
                         (ing["cert_f"], "flip"),
                         (ing["cert_l"], "late")):
            kept, unk = _filt(src, okfn)
            out[key] = {yr: [dict(t, comp=comp) for t in kept[yr]]
                        for yr in kept}
            out[key + "_unknown"] = unk
        forms[name] = out
        sa = {yr: round(sum(t["net"] for t in out["real"][yr]), 2)
              for yr in (2025, 2026)}
        print(f"cond {name}: kept "
              f"{len(out['real'][2025])}/{len(out['real'][2026])} "
              f"rows, standalone {sa}; state-unknown dropped "
              f"{out['real_unknown']}")
    # IDXCELL: IDX rows restricted to DOWN+FLAT regime cells.
    def cell_ok(day):
        return R9.LABELS.get(day) in ("DOWN", "FLAT")
    out = {}
    for src, key in ((ing["idx_r"], "real"), (ing["idx_f"], "flip"),
                     (ing["idx_l"], "late")):
        raw = {yr: [dict(t) for t in src[yr]] for yr in src}
        kept, _ = _filt(raw, cell_ok)
        out[key] = kept        # comp already NE-REV-IDX
        out[key + "_unknown"] = 0
    forms["idxcell"] = out
    sa = {yr: round(sum(t["net"] for t in out["real"][yr]), 2)
          for yr in (2025, 2026)}
    print(f"cond idxcell: kept {len(out['real'][2025])}/"
          f"{len(out['real'][2026])} rows, standalone {sa}")
    _cache["cond"] = forms
    return forms

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

def apply_r226(books, ing):
    return R9.swap(books, "INV-ABOVE", ing["above150"])

def apply_r503(books, ing):
    return without(R9.swap(books, "GAP-FADE", ing["sleeve125"]),
                   "GAP-FADE-INC")

def apply_cert(books, ing):
    return R9.add_comp(books, "NE-REV-CERT", ing["cert_r"])

def apply_rexp(books, ing):
    return R9.add_comp(books, "REXP", ing["rexp"])

def max_stack(books, ing, nerev_key="cert_r", nerev_comp="NE-REV-CERT"):
    """The R8-02 stack with the NE-REV slot parameterised."""
    out = apply_r503(apply_r226(books, ing), ing)
    out = R9.add_comp(out, nerev_comp, ing[nerev_key])
    out = R9.add_comp(out, "REXP", ing["rexp"])
    return out
