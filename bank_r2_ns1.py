#!/usr/bin/env python3
"""ROUND 2 Family 2 (Cycles 31-33): NS1 PERMUTATIONS. Second legs regenerated
from spot with the frozen generator's logic (newsetups_score.score_day NS1
block), changing ONLY room_ratio minimum / signal window end / strike rule.
Frozen-construction note: the stored second legs carry entry_time = the spot
replay's exit-bar time (replay() returns the exit bar's time on stop/target)
with strike = ATM(spot entry) - that convention IS the frozen book and is
preserved identically here. Sanity at frozen params must reproduce the book's
NS1 second legs (date, direction, entry_time, strike, expiry) exactly."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import newsetups_score as ns
from newsetups_score import day_info, replay, room_ratio, s1_trade
from aggressive_score import EXPIRIES
from bank_engine_repro import build_v1_legs, base_legs
from bank_engine_cycle import signal_map as frozen_signal_map
from bank_r2_core import build_pool, build_fixed, controls, full_run, V14
import copy

V15 = {"lt400": dict(stop=50.0, trig=105.0, lock=75.0, tgt2=330.0),
       "ge400_warm": dict(stop=50.0, trig=90.0, lock=90.0, tgt2=180.0),
       "ge400_cold": dict(stop=50.0, trig=90.0, lock=None, tgt2=None)}

def expiry_for(date):
    if date > "2026-09-30":
        return "2026-10-27" if date <= "2026-10-27" else "2026-11-03"
    return next(e for e in EXPIRIES if e >= date)

def gen_ns1(room_min, window_end, itm=False):
    legs, sigmap = [], {}
    daily = ns.DATA["BANKNIFTY"][1]
    for raw_date in sorted(set(daily["date"])):
        date = str(raw_date)[:10]
        if not ("2026-01-01" <= date <= "2026-10-28"): continue
        info = day_info("BANKNIFTY", raw_date)
        if info is None: continue
        s1 = s1_trade(info)
        if s1[0] is None: continue
        tr, i, d, _ = s1[0]
        if not (tr["exit_reason"] in ("target", "stop") and tr["exit_time"] <= "13:30"): continue
        bars = info["bars"]
        exit_idx = next(j for j, b in enumerate(bars) if b["time"] == tr["exit_time"])
        for j in range(exit_idx + 1, len(bars)):
            b = bars[j]
            if b["time"] > window_end: break
            prev = bars[j - 1]
            d2 = None
            if b["close"] > info["orh"] and not (prev["close"] > info["orh"]): d2 = "CE"
            elif b["close"] < info["orl"] and not (prev["close"] < info["orl"]): d2 = "PE"
            if d2 is None: continue
            if d2 == "CE" and info["bias"] == "bearish": break
            tr2 = replay(bars, j, d2)
            if tr2 is None: break
            rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
            if rr < room_min: break
            strike = round(tr2["entry"] / 100.0) * 100
            if itm: strike += -100 if d2 == "CE" else 100
            leg = {"date": date, "index": "BANKNIFTY", "direction": d2,
                   "entry_time": tr2["entry_time"], "strike": strike,
                   "expiry": expiry_for(date), "lot": 30,
                   "family": "NS1 (S1 + post-exit re-break)",
                   "rep": "NS1 (S1 + post-exit re-break)"}
            legs.append(leg)
            sigmap[(date, d2, tr2["entry_time"])] = b["time"]
            break
    return legs, sigmap

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sanity"
    if mode == "sanity":
        legs, sigmap = gen_ns1(1.5, "14:30", itm=False)
        mine = sorted((l["date"], l["direction"], l["entry_time"], l["strike"], l["expiry"]) for l in legs)
        book = sorted((l["date"], l["direction"], l["entry_time"], l["strike"], l["expiry"])
                      for l in build_v1_legs()[0] if l["family"].startswith("NS1"))
        print(f"regenerated frozen-param second legs: {len(mine)} | book NS1 legs: {len(book)}")
        print("sets identical:", mine == book)
        if mine != book:
            sm, sb = set(mine), set(book)
            print(" only in regen:", sorted(sm - sb)[:10])
            print(" only in book :", sorted(sb - sm)[:10])
        fsm = frozen_signal_map()
        mism = [(k, sigmap.get(k), fsm.get(k)) for k in sigmap if fsm.get(k) not in (None, sigmap[k])]
        print("signal-time mismatches vs frozen map:", mism[:5], "count", len(mism))

def run_variant(room, window, itm, cyc_name, REF):
    seconds, sigmap = gen_ns1(room, window, itm=itm)
    base = base_legs("BANKNIFTY")
    pool = base + seconds
    holder = {}
    def bf(delay):
        rows, nc, lbk, states, taken, nc0 = build_pool(pool, V15, delay=delay)
        if delay == 0: holder["nc0"] = nc0; holder["taken"] = len(taken)
        return rows, nc, lbk
    c, rows = full_run(bf, REF, cycle_name=cyc_name, signal_map=sigmap)
    c["stream_nc"] = holder.get("nc0")
    return c, rows

def sweep():
    ref_rows, ref_nc, ref_lbk = build_fixed(V15, delay=0)
    ref_prows, ref_pnc, _ = build_fixed(V15, delay=6)
    REF = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
    assert REF["net"] == 105167.00, REF["net"]
    # frozen-param pool build must reproduce the working book exactly
    c0, _ = run_variant(1.5, "14:30", False, None, REF)
    assert c0["net"] == 105167.00 and c0["n"] == 82, (c0["net"], c0["n"])
    print(f"REF v15 via pool builder: net={c0['net']} n={c0['n']} stream_nc={c0['stream_nc']} [frozen-param reproduction OK]")
    out = {}
    cells = [("r2c31_room13", 1.3, "14:30", False), ("r2c31_room14", 1.4, "14:30", False),
             ("r2c31_room16", 1.6, "14:30", False),
             ("r2c32_win1400", 1.5, "14:00", False), ("r2c32_win1500", 1.5, "15:00", False),
             ("r2c33_itm", 1.5, "14:30", True)]
    for name, room, window, itm in cells:
        c, _ = run_variant(room, window, itm, name if False else None, REF)
        out[name] = {k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw", "halves",
                                       "months", "ex_top3_total", "not_computed", "stream_nc",
                                       "gate_pass", "gate_failed_legs")}
        out[name]["placebo_net"] = c["placebo"]["net"]
        print(f"{name}: room={room} win={window} itm={itm} -> n={c['n']} net={c['net']} "
              f"ft90={c['ft90_pct']} pl={c['placebo']['net']} nc={c['not_computed']} snc={c['stream_nc']} "
              f"PASS={c['gate_pass']} fail={c['gate_failed_legs'][:3]}")
    json.dump(out, open("/home/hatch/workspace/trading/bank_r2_ns1_results.json", "w"), indent=1)
    print("saved bank_r2_ns1_results.json")
    return out

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "sweep":
    sweep()
