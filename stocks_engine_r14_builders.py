#!/usr/bin/env python3
"""ROUND 14 shared builders — pre-registered in
stocks_engine_round14_2026-11-02.md before any scoring.

Every builder re-scores ONE sleeve's population at a parameterised
exit geometry (tgt, stp); populations, admissions and entries are
the banked ones. Callers assert the anchor first: at the book
geometry each builder must reproduce the banked rows exactly
(multiset identity on date/stock/dir/entry_time/net).

- rescore(): generic entry-bar re-score (F4, P2F family). Two
  replay flavours exist in the machinery — "plain"
  (replay_plain: scan from the entry bar, gross returned) and
  "v2" (replay: scan from the bar after the entry bar). The
  anchor identifies which flavour a sleeve's book rows carry;
  it is never assumed.
- inv_long_geo() / inv_above_geo(): chain populations re-formed
  by run_chain at the candidate geometry (picks never read exit
  outcomes, so later rounds re-form causally), filtered by the
  current law; INV-ABOVE also re-applies the R12-02 hard-dip
  exclusion. Placebo = the chain's SHORT side under the same
  law (R2-25/26 precedent).
- fade_geo(): GAP-FADE + GAP-FADE-INC via gap_rows at the
  candidate geometry; mirror (follow) and one-bar-late sets
  per the R4/R6 convention.
- n4_geo(): the R2-events N4 population (thr 0.8%, std entry,
  full law + FLOOR-2 cap) with the geometry parameterised,
  minus the four R6-11 voided signals in every set. Late =
  entry at the 09:35 bar's close, no confirmation condition.
All entries are strictly after every input is knowable;
violations are counted per construction and returned, never
defaulted. Basis: equity cash, home 25, provisional per 100
shares, Rs40/trade, paper only, real Rs0.
"""
import sys, pickle, os
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B6
import stocks_engine_r8_builders as B8
import stocks_engine_r14_lib as R14

COST = 40.0
DF = {"DOWN", "FLAT"}

def machinery():
    return B6.machinery()

_fwd = None

def machinery_fwd():
    """The forward-collection root's machinery — the only place
    the 2026-10-29/30 bars live (the R6-L4 audit found 8 F4 book
    rows there). Used ONLY as a fallback for (stock, date) pairs
    the full-history root has no bars for."""
    global _fwd
    if _fwd is None:
        import stocks_sarvaritu_logger as L
        _fwd = L.load_machinery(f"{WS}/data/sarvaritu_fwd",
                                "2026-10-28")
    return _fwd

def bars_of(stock, day):
    g = machinery()
    bars = g["STOCKS_E"][stock][0].get(day, [])
    if bars:
        return bars
    return machinery_fwd()["STOCKS_E"][stock][0].get(day, [])

# ---------------------------------------------------------- rescore ---
def rescore(rows_by_year, comp, tgt, stp, flavour,
            open_entry=False):
    """Re-score fixed entry rows at (tgt, stp). Returns
    (real, flipped, late, missing): flipped = opposite direction
    on the identical entry bar; late = same direction one bar
    later; missing counts rows whose bars/entry bar are absent
    (must be 0 at the anchor). open_entry (the P2F family's
    convention — entry at the session's opening print): if the
    nominal 09:15 bar does not exist (the 2025-10-21 Muhurat
    special session, whose first bar is 13:45), the entry bar
    is the day's first bar — the convention the sleeve's own
    lineage scored that row by, verified by the anchor."""
    g = machinery()
    STOCKS_E = g["STOCKS_E"]

    def one(t, ei_off, flip):
        bars = bars_of(t["stock"], t["date"])
        idx = {b["time"]: k for k, b in enumerate(bars)}
        fell_back = False
        if t["entry_time"] not in idx:
            if not (open_entry and bars):
                return None
            base = 0
            fell_back = True
        else:
            base = idx[t["entry_time"]]
        ei = base + ei_off
        if ei >= len(bars):
            return None
        entry = float(bars[ei]["open"])
        d = t["dir"]
        if flip:
            d = "SHORT" if d == "LONG" else "LONG"
        sign = 1 if d == "LONG" else -1
        if flavour == "plain":
            er, ep, et, xi, gross = g["replay_plain"](
                bars, ei, sign, entry, tgt, stp)
            net = round(gross - COST, 2)
        else:
            r = g["replay"](bars, ei, entry, d, tgt, stp)
            if r is None:
                return None
            er, ep, et = r
            net = round(sign * (ep - entry) * 100 - COST, 2)
        label = (t["entry_time"] if (fell_back and ei_off == 0)
                 else bars[ei]["time"])
        return R.norm(comp, t["date"], t["stock"], d,
                      label, net)

    out = {}
    missing = 0
    for name, off, flip in (("real", 0, False),
                            ("flip", 0, True),
                            ("late", 1, False)):
        by = {}
        for yr in (2025, 2026):
            rows = []
            for t in rows_by_year[yr]:
                r = one(t, off, flip)
                if r is None:
                    missing += 1
                    continue
                rows.append(r)
            by[yr] = rows
        out[name] = by
    return out["real"], out["flip"], out["late"], missing

def comp_rows(books, comp):
    return {yr: [t for t in books[yr] if t["comp"] == comp]
            for yr in (2025, 2026)}

def f4_geo(books, tgt, stp, flavour):
    return rescore(comp_rows(books, "F4"), "F4", tgt, stp,
                   flavour)

def p2f_geo(books, tgt, stp, flavour):
    return {comp: rescore(comp_rows(books, comp), comp,
                          tgt, stp, flavour)
            for comp in ("P2F", "P2F-R2")}

# -------------------------------------------------------------- INV ---
_r14cache_path = f"{WS}/r14_cache.pkl"

def _load_r14cache():
    if os.path.exists(_r14cache_path):
        return pickle.load(open(_r14cache_path, "rb"))
    return {}

def inv_pop(tgt, stp):
    """Chain population at (tgt, stp). (1.25, 0.50) reuses the
    Round-2 cache pop; any other geometry is captured fresh by
    run_chain (the r2_cells method) and cached."""
    if (tgt, stp) == (1.25, 0.50):
        c = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
        return c["inv_pop"]
    cache = _load_r14cache()
    key = f"inv_pop_T{int(tgt*100):03d}S{int(stp*100):03d}"
    if key in cache:
        return cache[key]
    g = machinery()
    ALLDAYS = sorted({d for (_, d) in g["DAYCTX"]})
    rows = []
    for sym in g["SYMBOLS"]:
        for day in ALLDAYS:
            rs = g["run_chain"](sym, day, ("PLAIN", tgt, stp))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [{kk: r[kk] for kk in ("date", "stock", "direction",
                                 "setup", "round", "entry_time",
                                 "entry", "exit_price", "net",
                                 "adr", "event_status")}
           for r in rows]
    cache[key] = pop
    pickle.dump(cache, open(_r14cache_path, "wb"))
    return pop

def _prev_bar(t):
    hh, mm = map(int, t.split(":"))
    m = hh * 60 + mm - 5
    return f"{m // 60:02d}:{m % 60:02d}"

def _bucket_of(row):
    """The frozen R10-05/R12 index-state bucket of a row:
    NIFTY move at the bar completing at the row's entry
    instant; hard <= -0.30 / shallow (-0.30, 0) / up >= 0."""
    et = row.get("entry_time") or ""
    if len(et) != 5:
        return "unknown"
    mv = B8.nifty_move(row["date"], _prev_bar(et))
    if mv is None:
        return "unknown"
    if mv <= -0.30:
        return "hard"
    if mv < 0:
        return "shallow"
    return "up"

def _side_split(comp, rows):
    return R.split_years([R.norm(comp, r["date"], r["stock"],
                                 r["direction"], r["entry_time"],
                                 r["net"]) for r in rows])

def inv_long_geo(tgt, stp):
    pop = inv_pop(tgt, stp)
    real = R.inv_long_rows(pop, adr_min=3.0, round_max=3,
                           cutoff="11:00")
    side = _side_split("INV-LONG", R.inv_side_rows(
        pop, "SHORT", below=True, adr_min=3.0, round_max=3,
        cutoff="11:00"))
    return real, side

def inv_above_geo(tgt, stp):
    pop = inv_pop(tgt, stp)
    real0 = R.inv_above_rows(pop)
    real = {yr: [t for t in real0[yr]
                 if _bucket_of(t) != "hard"]
            for yr in (2025, 2026)}
    dropped = {yr: len(real0[yr]) - len(real[yr])
               for yr in (2025, 2026)}
    side = _side_split("INV-ABOVE", R.inv_side_rows(
        pop, "SHORT", below=False, flat_aside=False))
    return real, side, dropped

# ------------------------------------------------------------- FADE ---
def fade_geo(tgt, stp):
    def one(mode, thr, eb, only_dir, comp, band=None,
            entry_time=None):
        return B6.gap_rows(mode, thr, eb, tgt, stp,
                           only_dir=only_dir, cells=DF,
                           comp_name=comp, band=band,
                           entry_time=entry_time)
    out = {}
    out["GAP-FADE"] = {
        "real": one("fade", 1.5, 1, "LONG", "GAP-FADE"),
        "flip": one("follow", 1.5, 1, "SHORT", "GAP-FADE"),
        "late": one("fade", 1.5, 2, "LONG", "GAP-FADE"),
    }
    out["GAP-FADE-INC"] = {
        "real": one("fade", 1.25, 1, "LONG", "GAP-FADE-INC",
                    band=(1.25, 1.5), entry_time="09:40"),
        "flip": one("follow", 1.25, 1, "SHORT", "GAP-FADE-INC",
                    band=(1.25, 1.5), entry_time="09:40"),
        "late": one("fade", 1.25, 1, "LONG", "GAP-FADE-INC",
                    band=(1.25, 1.5), entry_time="09:45"),
    }
    return out

# --------------------------------------------------------------- N4 ---
N4_EXCL = {("GLENMARK", "SHORT"), ("BDL", "SHORT"),
           ("HINDALCO", "SHORT"), ("HINDZINC", "LONG"),
           ("UNITDSPR", "LONG"), ("RECLTD", "LONG"),
           ("WIPRO", "SHORT")}
VOID_KEYS = {("2025-01-16", "BDL"), ("2026-07-24", "HINDZINC"),
             ("2026-10-28", "HINDUNILVR"), ("2026-10-28", "VEDL")}

def _n4_score(sym, day, direction, tgt, stp, late=False):
    g = machinery()
    STOCKS_E, replay = g["STOCKS_E"], g["replay"]
    spot, daily = STOCKS_E[sym]
    bars = spot.get(day, [])
    if not bars:
        return None
    by_time = {c["time"]: j for j, c in enumerate(bars)}
    j = by_time.get("09:35" if late else "09:30")
    if j is None:
        return None
    entry = bars[j]["close"]
    r = replay(bars, j, entry, direction, tgt, stp)
    if r is None:
        return None
    er, ep, et = r
    sign = 1 if direction == "LONG" else -1
    return {"comp": "N4-V3", "date": day, "stock": sym,
            "dir": direction,
            "entry_time": "09:40" if late else "09:35",
            "net": round(sign * (ep - entry) * 100 - COST, 2)}

def _n4_law(t, s, dir_):
    sym = t["stock"]
    if R._wk(t["date"]):
        return False
    if sym == "ASTRAL":
        return False
    if (sym, dir_) in N4_EXCL:
        return False
    if sym == "TVSMOTOR" and dir_ == "LONG":
        return False
    if sym == "OIL" and dir_ == "LONG":
        return False
    if ("N4-V3", sym, dir_) in R.V3_DROP:
        return False
    if sym == "HDFCBANK" and dir_ == "LONG":
        return False
    if dir_ == "LONG" and round(s["move_pct"], 2) >= 3.0:
        return False  # FLOOR-2 one-sided cap (signal's own move)
    return True

def n4_geo(tgt, stp):
    cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
    signals = cache["n4_signals"]
    out = {"real": {2025: [], 2026: []},
           "flip": {2025: [], 2026: []},
           "late": {2025: [], 2026: []}}
    for yr in (2025, 2026):
        for s in signals[yr]:
            if abs(s["move_pct"]) < 0.8:
                continue
            if (s["date"], s["symbol"]) in VOID_KEYS:
                continue  # R6-11 voided signal: void in all sets
            d0 = s["direction"]
            for name, d, late in (
                    ("real", d0, False),
                    ("flip", "SHORT" if d0 == "LONG" else "LONG",
                     False),
                    ("late", d0, True)):
                t = _n4_score(s["symbol"], s["date"], d,
                              tgt, stp, late=late)
                if t is None:
                    continue
                if not _n4_law(t, s, d):
                    continue
                out[name][yr].append(t)
    return out["real"], out["flip"], out["late"]
