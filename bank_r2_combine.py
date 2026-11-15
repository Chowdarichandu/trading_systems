#!/usr/bin/env python3
"""ROUND 2 Cycle 41 (Family 5 + Family-2 completion):
(a) NS1 full cross-grid remainder: room {1.3,1.4,1.6} x window {14:00,15:00}
    x strike {ATM, ITM} + room {1.3,1.4,1.6} x ITM at 14:30 + window x ITM at
    1.5 - every cell not already scored in Cycles 31-33, gated vs book v16
    with the v16 assembly (v15 segments + expiry-day plain override).
(b) Formal stack re-gate: v16 (= C28 grid cell x C39 expiry plain, the two
    banked Round-2 ingredients) vs the Round-2 starting book v14."""
import sys, json, itertools
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import controls, gate, gen_replay, seg_of, write_trades
from bank_r2_ns1 import gen_ns1, V15
from bank_r2_expiry import build_geo
from bank_engine_repro import base_legs
from bank_engine_cycle import _entry_premium, signal_map as frozen_signal_map, FILTERS
from aggressive_score import unique_once, candles
from bank_engine_run2 import score_all, trailing_state

def build_pool_v16(pool, delay=0):
    pooled = FILTERS["drop_ns1_ce"](unique_once(pool))
    pooled = FILTERS["drop_prem_400_550"](pooled)
    lbk = {(l["date"], l["direction"], l["entry_time"]): l for l in pooled}
    scored, nc0 = score_all(pooled, delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    states, taken = {}, []
    for row in stream:
        n, net, _ = trailing_state(stream, row)
        states[row["leg_key"]] = (n, net)
        if not (n >= 10 and net < 0 and row["rep"] == "(lA) v2"):
            taken.append(row["leg_key"])
    out, nc = [], 0
    for key in taken:
        l = lbk[key]
        ep = _entry_premium(l)
        seg = seg_of(ep, *states.get(key, (0, 0.0)))
        if l["date"] == l["expiry"]:
            p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
        else:
            p = V15[seg]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = gen_replay(cs, l["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        out.append({**r, "date": l["date"], "direction": l["direction"],
                    "family": l["family"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "leg_key": key, "segment": seg})
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc, lbk, nc0

if __name__ == "__main__":
    ref_rows, ref_nc, ref_lbk = build_geo((50.0, 90.0), 0)
    ref_prows, ref_pnc, _ = build_geo((50.0, 90.0), 6)
    REF16 = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
    assert REF16["net"] == 106517.00
    # sanity: frozen-param pool through the v16 builder reproduces v16
    secs, _ = gen_ns1(1.5, "14:30")
    rows, nc, lbk, nc0 = build_pool_v16(base_legs("BANKNIFTY") + secs, delay=0)
    assert abs(sum(r["net"] for r in rows) - 106517.00) < 0.005 and len(rows) == 82, \
        (len(rows), sum(r["net"] for r in rows))
    print("v16 pool-builder sanity OK (82 legs, 106517.00)")
    base = base_legs("BANKNIFTY")
    cells = []
    for room in (1.3, 1.4, 1.6):
        for window in ("14:00", "15:00"):
            for itm in (False, True):
                cells.append((room, window, itm))
    for room in (1.3, 1.4, 1.6):
        cells.append((room, "14:30", True))
    for window in ("14:00", "15:00"):
        cells.append((1.5, window, True))
    out = {}
    for room, window, itm in cells:
        secs, sigmap = gen_ns1(room, window, itm=itm)
        pool = base + secs
        r0, nc_a, lbk_a, snc_a = build_pool_v16(pool, delay=0)
        r6, nc_b, _, snc_b = build_pool_v16(pool, delay=6)
        c = controls(r0, nc_a, lbk_a, r6, nc_b, signal_map=sigmap)
        ok, failed = gate(c, REF16)
        if snc_a: ok, failed = False, failed + [f"stream NOT_COMPUTED {snc_a}"]
        name = f"room{room}_win{window}_itm{int(itm)}"
        out[name] = {k: c[k] for k in ("n", "net", "ft90_pct", "per_week_raw", "not_computed")
                     } | {"gate_pass": ok, "placebo_net": c["placebo"]["net"],
                          "stream_nc": snc_a, "gate_failed": failed}
        print(f"{name}: n={c['n']} net={c['net']} pl={c['placebo']['net']} snc={snc_a} "
              f"PASS={ok} fail={failed[:2]}")
    json.dump(out, open("/home/hatch/workspace/trading/bank_r2_ns1_cross_results.json", "w"), indent=1)
    print("saved bank_r2_ns1_cross_results.json")
    # (b) formal stack re-gate: v16 vs v14
    from bank_r2_core import build_fixed, V14
    v14_rows, v14_nc, v14_lbk = build_fixed(V14, delay=0)
    v14_prows, v14_pnc, _ = build_fixed(V14, delay=6)
    REF14 = controls(v14_rows, v14_nc, v14_lbk, v14_prows, v14_pnc)
    resum = write_trades(ref_rows, "bank_engine_r2c41_stack_trades.csv")
    ok, failed = gate(REF16, REF14, resum=resum)
    print(f"STACK (C28 x C39) = v16 vs v14: net {REF16['net']} vs {REF14['net']} "
          f"PASS={ok} fail={failed}")
