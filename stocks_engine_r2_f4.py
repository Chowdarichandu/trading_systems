#!/usr/bin/env python3
"""ROUND 2 — F4 CYCLES (band x measurement-time cross + exclusions toggle).
Grid: bands [0.5,1.0) frozen / [0.4,0.9) / [0.6,1.2) x meas {10:00, 09:45},
then EXCL_DIR off at the frozen cell. Placebos per cell (pre-registered):
mirror-direction population in the same cell; decoy band [1.5,2.0) follow
population at the same measurement time. Gate: Round-1 session gate.
Banked cells update the incumbent book immediately (sequential chaining).
"""
import sys, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R

g = L.load_machinery(L.FULLHIST, "2026-10-28")
DAYCTX = g["DAYCTX"]
below50, pick, replay_plain = g["below50"], g["pick"], g["replay_plain"]
ALLDAYS = sorted({d for (s, d) in DAYCTX})
COST = 40.0
AUDIT = {"violations": 0}

def premove_m(candles, meas):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < meas]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

def build2_x(sym, day, lo, hi, meas, TP, SP, follow=1, pm_override=None):
    ctx = DAYCTX.get((sym, day))
    if ctx is None:
        return []
    if not below50(day):
        return []
    candles = ctx["candles"]
    pm = pm_override if pm_override is not None else premove_m(candles, meas)
    if pm is None or pm == 0 or abs(pm) < lo:
        return []
    if hi is not None and abs(pm) >= hi:
        return []
    want = (1 if pm > 0 else -1) * follow
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= meas), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = pick(sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = replay_plain(candles, ei, sign, entry, TP, SP)
        if candles[ei]["time"] < meas or candles[idx]["time"] < meas or ei <= idx:
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
                       "premove_pct": round(100 * pm, 6), "meas_time": meas})
        start = xi
    return trades

def collect_x(days, lo, hi, meas, TP, SP, follow=1, lag=False):
    prev_of = {d: ALLDAYS[i - 1] for i, d in enumerate(ALLDAYS) if i > 0}
    out = []
    for sym in g["SYMBOLS"]:
        for day in days:
            pm_o = None
            if lag:
                pd = prev_of.get(day)
                pctx = DAYCTX.get((sym, pd)) if pd else None
                if pctx is None:
                    continue
                pm_o = premove_m(pctx["candles"], meas)
                if pm_o is None:
                    continue
            out.extend(build2_x(sym, day, lo, hi, meas, TP, SP,
                                follow=follow, pm_override=pm_o))
    return out

# anchor: build2_x defaults reproduce collect2 raw exactly
raw_ref = g["collect2"](ALLDAYS, g["F4_CFG"], 1.50, 0.95)
raw_mine = collect_x(ALLDAYS, 0.005, 0.01, "10:00", 1.50, 0.95)
k = lambda t: (t["date"], t["symbol"], t["dir"], t["entry_time"], round(t["net"], 2))
assert Counter(map(k, raw_ref)) == Counter(map(k, raw_mine)), "build2_x anchor FAILED"
print("build2_x anchor OK")

cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
if "f4_mirror_1000" not in cache:
    cache["f4_mirror_1000"] = collect_x(ALLDAYS, 0.0, None, "10:00", 1.50, 0.95, follow=-1)
    cache["f4_mirror_0945"] = collect_x(ALLDAYS, 0.0, None, "09:45", 1.50, 0.95, follow=-1)
    cache["f4_lag_1000_T150S095"] = collect_x(ALLDAYS, 0.005, 0.01, "10:00", 1.50, 0.95, lag=True)
    cache["f4_lag_1000_T125S065"] = collect_x(ALLDAYS, 0.005, 0.01, "10:00", 1.25, 0.65, lag=True)
    cache["f4_lag_1000_T175S095"] = collect_x(ALLDAYS, 0.005, 0.01, "10:00", 1.75, 0.95, lag=True)
    pickle.dump(cache, open(f"{WS}/r2_cache.pkl", "wb"))
    print("mirror/lag populations captured")
print("audit violations (mirror/lag builds):", AUDIT["violations"])

books = R.load_books()

# lib-level anchor: f4_rows at the frozen cell == incumbent F4 rows
def ms(rows):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2)) for t in rows)
inc = R.f4_rows(cache["f4_1000_T150S095"], 0.5, 1.0, excl_dir=True)
for yr in (2025, 2026):
    cur = [t for t in books[yr] if t["comp"] == "F4"]
    assert ms(inc[yr]) == ms(cur), f"lib F4 anchor failed {yr}"
print("lib F4 frozen-cell anchor OK (== FLOOR-C4 F4, both years)")

POP = {"10:00": cache["f4_1000_T150S095"], "09:45": cache["f4_0945_T150S095"]}
MIR = {"10:00": cache["f4_mirror_1000"], "09:45": cache["f4_mirror_0945"]}

def cell(meas, lo, hi, excl=True, mirror=False):
    pop = MIR[meas] if mirror else POP[meas]
    return R.f4_rows(pop, lo, hi, excl_dir=excl)

def run_cycle(cyc, label, meas, lo, hi, excl=True):
    global books
    var_rows = cell(meas, lo, hi, excl)
    mir_rows = cell(meas, lo, hi, excl, mirror=True)
    dec_rows = cell(meas, 1.5, 2.0, excl)
    p_mirror = R.gate(books, R.swap(books, "F4", mir_rows), [])["sums"]["variant_combined"]
    p_decoy = R.gate(books, R.swap(books, "F4", dec_rows), [])["sums"]["variant_combined"]
    var_books = R.swap(books, "F4", var_rows)
    out = R.gate(books, var_books, [p_mirror, p_decoy],
                 timing_violations=AUDIT["violations"])
    R.record(cyc, label, out,
             note=f"placebos: mirror {p_mirror}, decoy-band {p_decoy}",
             extra={"cell": {"meas": meas, "lo": lo, "hi": hi, "excl": excl},
                    "var_f4_trades": {str(yr): len(var_rows[yr]) for yr in var_rows}})
    if out["verdict"]:
        books = var_books
        R.save_books(books)
        print(f"    -> BANKED; incumbent updated")

run_cycle("R2-01", "F4 band [0.4,0.9) @10:00", "10:00", 0.4, 0.9)
run_cycle("R2-02", "F4 band [0.6,1.2) @10:00", "10:00", 0.6, 1.2)
run_cycle("R2-03", "F4 band [0.5,1.0) @09:45", "09:45", 0.5, 1.0)
run_cycle("R2-04", "F4 band [0.4,0.9) @09:45", "09:45", 0.4, 0.9)
run_cycle("R2-05", "F4 band [0.6,1.2) @09:45", "09:45", 0.6, 1.2)
run_cycle("R2-06", "F4 EXCL_DIR off, band [0.5,1.0) @10:00", "10:00", 0.5, 1.0, excl=False)
print("F4 cycles done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
