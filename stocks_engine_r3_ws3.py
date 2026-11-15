#!/usr/bin/env python3
"""ROUND 3 — WS3 ENTRY TIMING. Two gated candidates:
 R3-03 F4 15-min EXECUTION: measurement frozen (premove @10:00, band
   [0.5,1.0), follow), signals frozen; the ENTRY is deferred to the open
   of the next quarter-hour bar (09:15/09:30/09:45/10:00... start times);
   exits T150/S095 replayed on the 5-min candles from the deferred entry.
 R3-04 INV 15-min EXECUTION: same deferral inside the chain; components
   rebuilt under current law (INV-LONG rounds<=3, entry <11:00, FLAT
   stand-aside; INV-ABOVE rounds<=2, entry <10:30).
Anchors: deferral OFF reproduces the cached populations multiset-exact;
current-law builders on the cached populations reproduce the book's
F4 / INV-LONG / INV-ABOVE exactly. Placebos pre-registered per cycle.
"""
import sys, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r3_lib as R3

g = L.load_machinery(L.FULLHIST, "2026-10-28")
DAYCTX = g["DAYCTX"]
below50, pick, replay_plain = g["below50"], g["pick"], g["replay_plain"]
NS = g["NS"]
SYMBOLS = g["SYMBOLS"]
days25 = sorted({d for (s, d) in DAYCTX if d.startswith("2025")})
days26 = sorted({d for (s, d) in DAYCTX if d.startswith("2026")})
ALLDAYS = days25 + days26
COST = 40.0
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
books = R3.load_books()

def ms(rows):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2)) for t in rows)

def cur(comp, yr):
    return [t for t in books[yr] if t["comp"] == comp]

# ------------------------------------------------------------- anchors ----
f4_cur = R.split_years([t for yr in (2025, 2026) for t in cur("F4", yr)])
f4_anchor = R.f4_rows(cache["f4_1000_T150S095"], 0.5, 1.0)
for yr in (2025, 2026):
    assert ms(f4_anchor[yr]) == ms(cur("F4", yr)), f"F4 anchor {yr}"
il = R.inv_long_rows(cache["inv_pop"], round_max=3, cutoff="11:00")
ia = R.inv_above_rows(cache["inv_pop"])
for yr in (2025, 2026):
    assert ms(il[yr]) == ms(cur("INV-LONG", yr)), f"INV-LONG law anchor {yr}"
    assert ms(ia[yr]) == ms(cur("INV-ABOVE", yr)), f"INV-ABOVE law anchor {yr}"
print("anchors OK: cached pops + current law == book F4 / INV-LONG / INV-ABOVE")

QH = {"00", "15", "30", "45"}

def defer_idx(candles, idx, mode):
    """mode: 'std' -> idx+1; 'bar1' -> idx+2; 'qh' -> first bar after idx
    whose start time is a quarter-hour mark."""
    if mode == "std":
        return idx + 1
    if mode == "bar1":
        return idx + 2
    for j in range(idx + 1, len(candles)):
        if candles[j]["time"][3:5] in QH:
            return j
    return None

def premove_m(candles, meas):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < meas]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

AUDIT = {"trades": 0, "violations": 0}

def build2_t(sym, day, mode, follow=True):
    ctx = DAYCTX.get((sym, day))
    if ctx is None or not below50(day):
        return []
    candles = ctx["candles"]
    pm = premove_m(candles, "10:00")
    if pm is None or pm == 0 or abs(pm) < 0.005 or abs(pm) >= 0.01:
        return []
    want = (1 if pm > 0 else -1) * (1 if follow else -1)
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= "10:00"), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = pick(sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = defer_idx(candles, idx, mode)
        if ei is None or ei >= len(candles):
            break
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = replay_plain(candles, ei, sign, entry, 1.50, 0.95)
        AUDIT["trades"] += 1
        if candles[ei]["time"] < "10:00" or candles[idx]["time"] < "10:00" or ei <= idx:
            AUDIT["violations"] += 1
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 6), "meas_time": "10:00"})
        start = xi
    return trades

def collect_t(mode, follow=True):
    out = []
    for sym in SYMBOLS:
        for day in ALLDAYS:
            out.extend(build2_t(sym, day, mode, follow))
    return out

# F4 std-mode anchor vs cache population
std_pop = collect_t("std")
k = lambda t: (t["date"], t["symbol"], t["dir"], t["entry_time"], round(t["net"], 2))
ref = [t for t in cache["f4_1000_T150S095"]
       if 0.5 <= abs(t["premove_pct"]) < 1.0]
assert Counter(map(k, std_pop)) == Counter(map(k, ref)), "F4 std anchor FAILED"
print(f"F4 std anchor OK ({len(std_pop)} raw rows); audit violations {AUDIT['violations']}")

def chain_t(sym, day, mode):
    ctx = DAYCTX.get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    trades, start = [], 0
    while True:
        chosen = NS["pool_pick"](ctx, NS["v4_head"](ctx, start),
                                 NS["skor_head"](ctx, start))
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        ei = defer_idx(candles, idx, mode)
        if ei is None or ei >= len(candles):
            break
        entry = float(candles[ei]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        er, ep, et, exit_idx, gross = replay_plain(candles, ei, sign, entry, 1.25, 0.5)
        trades.append({"date": day, "stock": sym, "direction": direction,
                       "setup": setup, "round": len(trades) + 1,
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit_price": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event_status": ctx["event_status"]})
        start = exit_idx
    return trades

def collect_chain(mode):
    out = []
    for sym in SYMBOLS:
        for day in ALLDAYS:
            for r in chain_t(sym, day, mode):
                r["adr"] = g["ADR"].get((sym, day))
                out.append({kk: r[kk] for kk in ("date", "stock", "direction",
                            "setup", "round", "entry_time", "entry",
                            "exit_price", "net", "adr", "event_status")})
    return out

std_chain = collect_chain("std")
kc = lambda t: (t["date"], t["stock"], t["direction"], t["round"],
                t["entry_time"], round(t["net"], 2))
assert Counter(map(kc, std_chain)) == Counter(map(kc, cache["inv_pop"])), \
    "INV std chain anchor FAILED"
print(f"INV std chain anchor OK ({len(std_chain)} rows)")

def book_total(bk):
    return round(sum(FLT for yr in (2025, 2026)
                     for FLT in [sum(t["net"] for t in bk[yr]
                                     if t["date"] <= f"{yr}-10-31")]), 2)

import stocks_engine_floor_lib as FL

# ------------------------------------------------------------- R3-03 -----
qh_pop = collect_t("qh")
bar1_pop = collect_t("bar1")
fade_pop = collect_t("qh", follow=False)
var = R.f4_rows(qh_pop, 0.5, 1.0)
pl_fade = R3.swap(books, "F4", R.f4_rows(fade_pop, 0.5, 1.0))
pl_bar1 = R3.swap(books, "F4", R.f4_rows(bar1_pop, 0.5, 1.0))
pl = [book_total(pl_fade), book_total(pl_bar1)]
out = R3.gate(books, R3.swap(books, "F4", var), pl,
              timing_violations=AUDIT["violations"])
R3.record("R3-03", "F4 15-min execution (entries deferred to next "
                   "quarter-hour bar open; meas @10:00, band [0.5,1.0), "
                   "T150/S095 frozen)", out,
          note=f"placebos: quarter-hour FADE book {pl[0]}; one-bar-late "
               f"(5-min) entry book {pl[1]}; audit violations "
               f"{AUDIT['violations']}",
          extra={"standalone": {str(yr): round(sum(t['net'] for t in var[yr]), 2)
                                for yr in var}})
if out["verdict"]:
    books = R3.swap(books, "F4", var)
    R3.save_books(books)
    print("    -> BANKED")

# ------------------------------------------------------------- R3-04 -----
qh_chain = collect_chain("qh")
bar1_chain = collect_chain("bar1")
var_il = R.inv_long_rows(qh_chain, round_max=3, cutoff="11:00")
var_ia = R.inv_above_rows(qh_chain)
var_books = R3.swap(R3.swap(books, "INV-LONG", var_il), "INV-ABOVE", var_ia)
b1_il = R.inv_long_rows(bar1_chain, round_max=3, cutoff="11:00")
b1_ia = R.inv_above_rows(bar1_chain)
pl_bar1_books = R3.swap(R3.swap(books, "INV-LONG", b1_il), "INV-ABOVE", b1_ia)
# mirror placebo: SHORT side of the quarter-hour chain under mirrored gates
# (inv_side_rows returns a flat list of raw chain rows -> split by year here)
mir_il = R.split_years([R.norm("INV-LONG", r["date"], r["stock"], "SHORT",
                               r["entry_time"], r["net"])
                        for r in R.inv_side_rows(qh_chain, "SHORT", True,
                                                 round_max=3, cutoff="11:00")])
mir_ia = R.split_years([R.norm("INV-ABOVE", r["date"], r["stock"], "SHORT",
                               r["entry_time"], r["net"])
                        for r in R.inv_side_rows(qh_chain, "SHORT", False,
                                                 round_max=2, cutoff="10:30",
                                                 flat_aside=False)])
mir_books = {yr: [t for t in books[yr]
                  if t["comp"] not in ("INV-LONG", "INV-ABOVE")]
             + mir_il[yr] + mir_ia[yr]
             for yr in (2025, 2026)}
pl = [book_total(mir_books), book_total(pl_bar1_books)]
out = R3.gate(books, var_books, pl)
R3.record("R3-04", "INV 15-min execution (chain entries deferred to next "
                   "quarter-hour bar open; INV-LONG r<=3 <11:00, INV-ABOVE "
                   "r<=2 <10:30, law frozen)", out,
          note=f"placebos: quarter-hour SHORT-mirror components book "
               f"{pl[0]}; one-bar-late chain book {pl[1]}",
          extra={"standalone": {
              "INV-LONG": {str(yr): round(sum(t['net'] for t in var_il[yr]), 2)
                           for yr in var_il},
              "INV-ABOVE": {str(yr): round(sum(t['net'] for t in var_ia[yr]), 2)
                            for yr in var_ia}}})
if out["verdict"]:
    books = var_books
    R3.save_books(books)
    print("    -> BANKED")
print("WS3 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
