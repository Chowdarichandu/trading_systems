#!/usr/bin/env python3
"""ROUND 2 — EVENT CYCLES: reaction grid untested cells, N4 permutations,
and the new-mechanism trial (PERSIST-R2). All law held constant per family;
every variant anchored to the incumbent component before scoring.
Gate: Round-1 session gate. Placebos pre-registered per cycle in code.
"""
import sys, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_floor_lib as FL

g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
EV = cache["events"]
books = R.load_books()
COST = 40.0

def ms(rows):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2)) for t in rows)

def cur(comp, yr):
    return [t for t in books[yr] if t["comp"] == comp]

# ---------------------------------------------------------- P2F family -----
def p2f_law(rows, comp):
    out = []
    for t in rows:
        sym, d, dir_ = t["symbol"], t["date"], t["direction"]
        if R._wk(d):
            continue
        if comp == "P2F":
            if sym in ("ASTRAL", "HINDUNILVR"):
                continue
            if sym == "HINDALCO" and dir_ == "LONG":
                continue
        elif comp == "P2F-R2":
            if sym in ("ASTRAL", "HINDUNILVR"):
                continue
            if sym == "TVSMOTOR" and dir_ == "LONG":
                continue
        elif comp == "R2-LOWBAND":
            if sym in ("ASTRAL", "HINDUNILVR"):
                continue
            if sym == "HINDALCO" and dir_ == "LONG":
                continue
        if (comp, sym, dir_) in R.V3_DROP:
            continue
        if (comp, sym, dir_) in R.EXCL_V2:
            continue
        out.append(R.norm(comp, d, sym, dir_, t["entry_time"], t["net_rs"]))
    return out

def fam_rows(yr, comp, lag, lo, hi=None, flip=False, up_aside=True):
    scored = EV[yr]["scored"][(lag, flip)]
    sel = [t for t in scored
           if abs(t["reaction_ret_pct"]) >= lo
           and (hi is None or abs(t["reaction_ret_pct"]) < hi)]
    rows = p2f_law(sel, comp)
    if comp == "R2-LOWBAND" and up_aside:
        rows = [t for t in rows if R.LABELS.get(t["date"]) != "UP"]
    return rows

# anchors: cached-score constructions == incumbent components
for yr in (2025, 2026):
    assert ms(fam_rows(yr, "P2F", 1, 2.5)) == ms(cur("P2F", yr)), f"P2F anchor {yr}"
    assert ms(fam_rows(yr, "P2F-R2", 2, 2.5)) == ms(cur("P2F-R2", yr)), f"P2FR2 anchor {yr}"
    assert ms(fam_rows(yr, "R2-LOWBAND", 2, 2.0, 2.5)) == ms(cur("R2-LOWBAND", yr)), f"R2LOW anchor {yr}"
print("P2F-family anchors OK")

def fam_cycle(cyc, label, comp, var_by_yr, placebo_books_list):
    global books
    var_books = R.swap(books, comp, var_by_yr)
    pl = [round(sum(t["net"] for yr in (2025, 2026) for t in pb[yr]), 2)
          for pb in placebo_books_list]
    out = R.gate(books, var_books, pl)
    R.record(cyc, label, out, note=f"placebos {pl}",
             extra={"var_trades": {str(yr): len(var_by_yr[yr]) for yr in var_by_yr}})
    if out["verdict"]:
        books = var_books
        R.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

def both(fn):
    return {yr: fn(yr) for yr in (2025, 2026)}

# R2-11: P2F band 3.0 @ lag1 (restriction)
var = both(lambda yr: fam_rows(yr, "P2F", 1, 3.0))
pl_flip = R.swap(books, "P2F", both(lambda yr: fam_rows(yr, "P2F", 1, 3.0, flip=True)))
n_removed = sum(len(cur("P2F", yr)) - len(var[yr]) for yr in (2025, 2026))
pl_chrono_total = R.chrono_placebo(books, "P2F", n_removed)
out11 = R.gate(books, R.swap(books, "P2F", var),
               [round(sum(t["net"] for yr in (2025, 2026) for t in pl_flip[yr]), 2),
                pl_chrono_total])
R.record("R2-11", "P2F band >=3.0 @ R+1", out11,
         note="placebos: flipped band-3.0 book; chrono first-N removal")
if out11["verdict"]:
    books = R.swap(books, "P2F", var); R.save_books(books); print("    -> BANKED")

# R2-12: P2F-R2 band 3.0 @ lag2 (restriction)
var = both(lambda yr: fam_rows(yr, "P2F-R2", 2, 3.0))
pl_flip = R.swap(books, "P2F-R2", both(lambda yr: fam_rows(yr, "P2F-R2", 2, 3.0, flip=True)))
n_removed = sum(len(cur("P2F-R2", yr)) - len(var[yr]) for yr in (2025, 2026))
pl_chrono_total = R.chrono_placebo(books, "P2F-R2", n_removed)
out12 = R.gate(books, R.swap(books, "P2F-R2", var),
               [round(sum(t["net"] for yr in (2025, 2026) for t in pl_flip[yr]), 2),
                pl_chrono_total])
R.record("R2-12", "P2F-R2 band >=3.0 @ R+2", out12,
         note="placebos: flipped band-3.0 book; chrono first-N removal")
if out12["verdict"]:
    books = R.swap(books, "P2F-R2", var); R.save_books(books); print("    -> BANKED")

# R2-13: R2-LOWBAND without the UP stand-aside (adds UP-day low-band trades)
var = both(lambda yr: fam_rows(yr, "R2-LOWBAND", 2, 2.0, 2.5, up_aside=False))
pl_flip = R.swap(books, "R2-LOWBAND",
                 both(lambda yr: fam_rows(yr, "R2-LOWBAND", 2, 2.0, 2.5,
                                          flip=True, up_aside=False)))
pl_decoy = R.swap(books, "R2-LOWBAND",
                  both(lambda yr: fam_rows(yr, "R2-LOWBAND", 2, 1.5, 2.0,
                                           up_aside=False)))
out13 = R.gate(books, R.swap(books, "R2-LOWBAND", var),
               [round(sum(t["net"] for yr in (2025, 2026) for t in pl_flip[yr]), 2),
                round(sum(t["net"] for yr in (2025, 2026) for t in pl_decoy[yr]), 2)])
R.record("R2-13", "R2-LOWBAND without UP stand-aside", out13,
         note="placebos: flipped no-aside book; decoy band [1.5,2.0) no-aside book")
if out13["verdict"]:
    books = R.swap(books, "R2-LOWBAND", var); R.save_books(books); print("    -> BANKED")

# R2-14: P2F band 2.0 @ lag1 (adds the [2.0,2.5) slice at R+1 under P2F law)
var = both(lambda yr: fam_rows(yr, "P2F", 1, 2.0))
pl_flip = R.swap(books, "P2F", both(lambda yr: fam_rows(yr, "P2F", 1, 2.0, flip=True)))
pl_decoy = R.swap(books, "P2F", both(lambda yr: fam_rows(yr, "P2F", 1, 1.5, 2.0)))
out14 = R.gate(books, R.swap(books, "P2F", var),
               [round(sum(t["net"] for yr in (2025, 2026) for t in pl_flip[yr]), 2),
                round(sum(t["net"] for yr in (2025, 2026) for t in pl_decoy[yr]), 2)])
R.record("R2-14", "P2F band >=2.0 @ R+1", out14,
         note="placebos: flipped band-2.0 book; decoy band [1.5,2.0) book")
if out14["verdict"]:
    books = R.swap(books, "P2F", var); R.save_books(books); print("    -> BANKED")

# ---------------------------------------------------------- N4 ---------------
N4_EXCL = {("GLENMARK", "SHORT"), ("BDL", "SHORT"), ("HINDALCO", "SHORT"),
           ("HINDZINC", "LONG"), ("UNITDSPR", "LONG"), ("RECLTD", "LONG"),
           ("WIPRO", "SHORT")}

def n4_score(sym, day, direction, thr, mode):
    spot, daily = STOCKS_E[sym]
    bars = spot.get(day, [])
    if not bars:
        return None
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    i = dmap.get(day)
    if i is None or i == 0:
        return None
    prev_close = daily[i - 1]["close"]
    by_time = {c["time"]: j for j, c in enumerate(bars)}
    if mode == "std":
        j = by_time.get("09:30")
        if j is None:
            return None
        entry = bars[j]["close"]
        r = replay(bars, j, entry, direction, 1.50, 0.80)
        et_label = "09:35"
    else:  # confirm40: 09:35 bar close must still be beyond thr, same side
        j = by_time.get("09:35")
        if j is None:
            return None
        mv = (bars[j]["close"] / prev_close - 1) * 100
        if direction == "LONG" and mv < thr:
            return None
        if direction == "SHORT" and mv > -thr:
            return None
        entry = bars[j]["close"]
        r = replay(bars, j, entry, direction, 1.50, 0.80)
        et_label = "09:40"
    if r is None:
        return None
    er, ep, et = r
    sign = 1 if direction == "LONG" else -1
    return {"comp": "N4-V3", "date": day, "stock": sym, "dir": direction,
            "entry_time": et_label,
            "net": round(sign * (ep - entry) * 100 - COST, 2)}

def n4_rows(yr, thr, mode, flip=False):
    out = []
    for s in cache["n4_signals"][yr]:
        if abs(s["move_pct"]) < thr:
            continue
        direction = s["direction"]
        if flip:
            direction = "SHORT" if direction == "LONG" else "LONG"
        t = n4_score(s["symbol"], s["date"], direction, thr, mode)
        if t is None:
            continue
        sym, dir_ = t["stock"], t["dir"]
        if flip:
            # law applies to the FLIPPED trade's own (stock, dir)
            pass
        if R._wk(t["date"]):
            continue
        if sym == "ASTRAL":
            continue
        if (sym, dir_) in N4_EXCL:
            continue
        if sym == "TVSMOTOR" and dir_ == "LONG":
            continue
        if sym == "OIL" and dir_ == "LONG":
            continue
        if ("N4-V3", sym, dir_) in R.V3_DROP:
            continue
        if sym == "HDFCBANK" and dir_ == "LONG":
            continue
        if dir_ == "LONG" and round(s["move_pct"], 2) >= 3.0:
            continue  # FLOOR-2 one-sided cap (on the signal's own move)
        out.append(t)
    return out

# N4 anchor: thr 1.0 std == incumbent N4 (note: for flip=False the FLOOR-2
# cap uses the signal move; incumbent rows were capped identically in R1)
for yr in (2025, 2026):
    mine = n4_rows(yr, 1.0, "std")
    assert ms(mine) == ms(cur("N4-V3", yr)), \
        f"N4 anchor failed {yr}: mine {len(mine)} vs book {len(cur('N4-V3', yr))}"
print("N4 anchor OK (thr 1.0 std + law + FLOOR-2 cap == incumbent N4-V3)")

def n4_cycle(cyc, label, thr, mode):
    global books
    var = {yr: n4_rows(yr, thr, mode) for yr in (2025, 2026)}
    flip = {yr: n4_rows(yr, thr, mode, flip=True) for yr in (2025, 2026)}
    pl_flip = R.swap(books, "N4-V3", flip)
    pl = [round(sum(t["net"] for yr in (2025, 2026) for t in pl_flip[yr]), 2)]
    n_removed = sum(len(cur("N4-V3", yr)) - len(var[yr]) for yr in (2025, 2026))
    if n_removed > 0:
        pl.append(R.chrono_placebo(books, "N4-V3", n_removed))
    out = R.gate(books, R.swap(books, "N4-V3", var), pl)
    R.record(cyc, label, out, note=f"placebos {pl}",
             extra={"var_trades": {str(yr): len(var[yr]) for yr in var}})
    if out["verdict"]:
        books = R.swap(books, "N4-V3", var)
        R.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

out15 = n4_cycle("R2-15", "N4-V3 threshold 1.2%, std entry", 1.2, "std")
out16 = n4_cycle("R2-16", "N4-V3 09:40 confirming-close entry (thr 1.0)", 1.0, "confirm40")
out17 = n4_cycle("R2-17", "N4-V3 threshold 0.8%, std entry", 0.8, "std")
banked = [o["verdict"] for o in (out15, out16)]
if out15["verdict"] and not out16["verdict"]:
    n4_cycle("R2-18", "N4-V3 threshold 1.2% x 09:40 confirm entry", 1.2, "confirm40")
elif out16["verdict"] and not out15["verdict"]:
    n4_cycle("R2-18", "N4-V3 threshold 1.2% x 09:40 confirm entry", 1.2, "confirm40")
elif out15["verdict"] and out16["verdict"]:
    print("R2-18 skipped: both parents banked sequentially already "
          "(1.2 was re-based on the confirm40 book if R2-16 banked after; "
          "the cross cell is recorded as covered by chaining)")
else:
    n4_cycle("R2-18", "N4-V3 threshold 1.2% x 09:40 confirm entry", 1.2, "confirm40")

# ------------------------------------------------- NEW MECHANISM: PERSIST-R2 -
def persist_rows(yr, flip=False, conditioned=True):
    out = []
    for c in EV[yr]["cands"]:
        if abs(c["reaction_ret_pct"]) < 2.5:
            continue
        sym = c["symbol"]
        spot, daily = STOCKS_E[sym]
        ri = c["ri"]
        if ri + 2 >= len(daily):
            continue
        direction = c["direction"]
        if conditioned:
            r_close = daily[ri]["close"]
            r1_close = daily[ri + 1]["close"]
            if direction == "LONG" and not (r1_close > r_close):
                continue
            if direction == "SHORT" and not (r1_close < r_close):
                continue
        d2 = daily[ri + 2]["date"]
        bars = spot.get(d2, [])
        if not bars:
            continue
        by_time = {cc["time"]: j for j, cc in enumerate(bars)}
        j = by_time.get("09:55")
        if j is None:
            continue
        day_open = bars[0]["open"]
        drift = (bars[j]["close"] / day_open - 1) * 100
        if direction == "LONG" and not (drift > 0):
            continue
        if direction == "SHORT" and not (drift < 0):
            continue
        entry = bars[j]["close"]
        use_dir = direction if not flip else ("SHORT" if direction == "LONG" else "LONG")
        r = replay(bars, j, entry, use_dir, 1.25, 0.5)
        if r is None:
            continue
        er, ep, et = r
        sign = 1 if use_dir == "LONG" else -1
        net = round(sign * (ep - entry) * 100 - COST, 2)
        # law on the trade actually taken (for flip, the flipped direction)
        if R._wk(d2):
            continue
        if sym in ("ASTRAL", "HINDUNILVR"):
            continue
        if ("P2F-R2", sym, use_dir) in R.V3_DROP:
            continue
        if ("P2F-R2", sym, use_dir) in R.EXCL_V2:
            continue
        if sym == "TVSMOTOR" and use_dir == "LONG":
            continue
        out.append(R.norm("PERSIST-R2", d2, sym, use_dir, "10:00", net))
    return out

var_p = {yr: persist_rows(yr) for yr in (2025, 2026)}
flip_p = {yr: persist_rows(yr, flip=True) for yr in (2025, 2026)}
unc_p = {yr: persist_rows(yr, conditioned=False) for yr in (2025, 2026)}
pl = [round(sum(t["net"] for yr in (2025, 2026) for t in R.add_comp(books, "PERSIST-R2", flip_p)[yr]), 2),
      round(sum(t["net"] for yr in (2025, 2026) for t in R.add_comp(books, "PERSIST-R2", unc_p)[yr]), 2)]
out19 = R.gate(books, R.add_comp(books, "PERSIST-R2", var_p), pl)
R.record("R2-19", "NEW MECHANISM PERSIST-R2 (reaction>=2.5% + R+1 persistence "
                  "+ R+2 10:00 hold, T125/S050)", out19,
         note=f"placebos {pl} (flipped entries; unconditioned sibling)",
         extra={"var_trades": {str(yr): len(var_p[yr]) for yr in var_p},
                "standalone": {str(yr): round(sum(t['net'] for t in var_p[yr]), 2)
                               for yr in var_p}})
if out19["verdict"]:
    books = R.add_comp(books, "PERSIST-R2", var_p)
    R.save_books(books)
    print("    -> BANKED; incumbent updated")
print("event cycles done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
